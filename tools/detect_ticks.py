#!/usr/bin/env python3
"""
detect_ticks.py — Programmatically detect "tick" events (visual state transitions)
in a sub-region of a source recording.

Designed for the tail-cut zoom technique: when a video shows a progress
checklist, status sidebar, or similar UI element that ticks through discrete
states (item 1 active → item 1 checked → item 2 active → ...), this tool
identifies the precise timestamps of each visual transition.

Pipeline integration (Phase 5.5 helper):
  1. After scrub.py produces the canonical scrubbed file
  2. Before authoring tail-cut ffmpeg ranges around tick events
  3. Run this tool to get precise tick timestamps
  4. Pipe the output into the ffmpeg trim+concat filter graph

Why this exists:
  Eyeballing tick timestamps from sampled frames is error-prone — sampling at
  1s intervals gives ±1s precision, which produces visible asymmetry in the
  output (one tail-cut feels longer than another because the tick isn't
  precisely centered in its window). Detecting the actual frame-of-change
  programmatically eliminates that error.

  Companion to tools/measure_highlight.py — same discipline: "measured, not
  eyeballed" (Hard Rule #10 in video-production-workflow).

Detection method:
  1. Sample frames at high rate (default 30fps) in the search region.
  2. For each consecutive frame pair, compute the mean absolute pixel
     difference within a configurable sub-region.
  3. Find the top-N peaks (with non-maximum suppression so two adjacent
     frames don't both count as separate ticks).
  4. Output the timestamp of each peak — that's the tick moment.

Limitations:
  - Detects N largest visual change events. If the recording has more visual
    activity than N actual ticks (e.g., cursor movement, chat thread firing),
    those can register as false positives. Narrow the region_pct to just the
    progress-bar area to minimize this.
  - For SIMULTANEOUS ticks (e.g., V1.2 steps 2 + 3 tick at the same instant),
    the tool detects ONE peak — the simultaneous moment — not two. Set
    --expected-ticks to the count of distinct *moments*, not lines.

Usage:
  python tools/detect_ticks.py SCRUBBED.mp4 \\
      --time-range 19:46 \\
      --region-pct "80,0,20,30" \\
      --expected-ticks 3 \\
      --tail-seconds 1.0 \\
      --output ticks.json
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def get_video_dims(video: Path) -> tuple[int, int]:
    """Return (width, height) of the video file via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0", str(video),
    ]
    out = subprocess.check_output(cmd).decode().strip()
    w, h = out.split(",")
    return int(w), int(h)


def get_video_duration(video: Path) -> float:
    """Return duration in seconds."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0", str(video),
    ]
    return float(subprocess.check_output(cmd).decode().strip())


def extract_region_frames(
    video: Path,
    t_start: float,
    t_end: float,
    fps_sample: int,
    region_pct: tuple[float, float, float, float],
) -> list[tuple[float, np.ndarray]]:
    """Extract frames from `video` cropped to `region_pct` at `fps_sample` fps.

    Returns a list of (timestamp_seconds, RGB array of shape (h, w, 3)).
    """
    src_w, src_h = get_video_dims(video)
    x, y, w, h = region_pct
    px = max(0, int(x * src_w / 100))
    py = max(0, int(y * src_h / 100))
    pw = max(1, int(w * src_w / 100))
    ph = max(1, int(h * src_h / 100))
    # Ensure even dims (libx264 / rawvideo requirement)
    pw = pw - (pw % 2)
    ph = ph - (ph % 2)

    cmd = [
        "ffmpeg", "-loglevel", "error",
        "-ss", f"{t_start:.3f}", "-to", f"{t_end:.3f}",
        "-i", str(video),
        "-vf", f"crop={pw}:{ph}:{px}:{py},fps={fps_sample}",
        "-f", "image2pipe", "-vcodec", "rawvideo", "-pix_fmt", "rgb24", "-",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    frame_size = pw * ph * 3
    frames: list[tuple[float, np.ndarray]] = []
    t = t_start
    dt = 1.0 / fps_sample
    while True:
        data = proc.stdout.read(frame_size)
        if len(data) < frame_size:
            break
        arr = np.frombuffer(data, dtype=np.uint8).reshape((ph, pw, 3))
        frames.append((t, arr.copy()))
        t += dt
    proc.wait()
    if proc.returncode != 0:
        stderr = proc.stderr.read().decode(errors="ignore") if proc.stderr else ""
        print(f"[detect-ticks] ffmpeg returned {proc.returncode}: {stderr}", file=sys.stderr)
    return frames


def detect_tick_peaks(
    frames: list[tuple[float, np.ndarray]],
    expected_ticks: int,
    suppress_seconds: float = 0.8,
    fps_sample: int = 30,
) -> list[tuple[float, float]]:
    """Return the top `expected_ticks` peak (timestamp, magnitude) tuples,
    sorted by timestamp ascending.

    Detection: frame-to-frame mean absolute pixel diff. Peaks are picked by
    descending magnitude with non-maximum suppression (no two peaks within
    `suppress_seconds` of each other).
    """
    if len(frames) < 2:
        return []
    timestamps = [t for t, _ in frames]
    arrays = [a for _, a in frames]

    # Compute mean absolute frame-to-frame diff
    diffs = np.empty(len(arrays) - 1, dtype=np.float64)
    for i in range(1, len(arrays)):
        d = arrays[i].astype(np.int32) - arrays[i - 1].astype(np.int32)
        diffs[i - 1] = np.abs(d).mean()

    # Non-maximum suppression: take top peaks, separated by suppress_seconds
    suppress_frames = max(1, int(round(suppress_seconds * fps_sample)))
    used = np.zeros(len(diffs), dtype=bool)
    sorted_idx = np.argsort(diffs)[::-1]

    peaks: list[tuple[float, float]] = []
    for idx in sorted_idx:
        if used[idx]:
            continue
        # Timestamp of the *after* frame in the diff pair
        peak_t = timestamps[idx + 1]
        peaks.append((peak_t, float(diffs[idx])))
        # Suppress neighbors within suppress_frames in either direction
        lo = max(0, idx - suppress_frames)
        hi = min(len(diffs), idx + suppress_frames + 1)
        used[lo:hi] = True
        if len(peaks) >= expected_ticks:
            break

    peaks.sort(key=lambda p: p[0])
    return peaks


def compute_keep_ranges(
    t_start: float,
    t_end: float,
    tick_timestamps: list[float],
    compress_threshold: float = 2.0,
    margin: float = 1.0,
) -> list[tuple[float, float]]:
    """Apply the gap-cut rule to a tick window — V1's ±margin pattern.

    For each dead segment (pre-first-tick, between consecutive ticks, post-last-tick):
      - If the dead-segment duration > compress_threshold, compress by keeping `margin`
        seconds adjacent to each boundary tick.
      - Otherwise, leave at natural playback (keep the full segment).

    Compression layout (margin defaults to 1.0s, matching V1):
      - Pre-first-tick: keep [t1 - margin, t1].
      - Between ticks (ti, ti+1): keep [ti, ti + margin] + [ti+1 - margin, ti+1].
        That's `margin` seconds after the prior tick + `margin` seconds before the next
        tick, with a jump-cut between them. Total natural-rate breathing between
        consecutive ticks = 2 × margin (when compressed).
      - Post-last-tick: keep [tN, tN + margin].

    Adjacent / overlapping kept ranges are merged.

    Per workflow Hard Rule #23 + decisions/2026-05-23-tick-window-compression-moves-to-phase-3.md
    + decisions/2026-05-24-v1-tick-spacing-pattern.md.
    """
    if not tick_timestamps:
        return [(t_start, t_end)]

    keep: list[tuple[float, float]] = []

    # Pre-first-tick segment
    t1 = tick_timestamps[0]
    if (t1 - t_start) > compress_threshold:
        keep.append((max(t_start, t1 - margin), t1))
    else:
        keep.append((t_start, t1))

    # Between-tick segments
    for i in range(len(tick_timestamps) - 1):
        t_a = tick_timestamps[i]
        t_b = tick_timestamps[i + 1]
        gap = t_b - t_a
        if gap > compress_threshold:
            keep.append((t_a, t_a + margin))
            keep.append((t_b - margin, t_b))
        else:
            keep.append((t_a, t_b))

    # Post-last-tick segment
    tN = tick_timestamps[-1]
    if (t_end - tN) > compress_threshold:
        keep.append((tN, min(t_end, tN + margin)))
    else:
        keep.append((tN, t_end))

    # Merge adjacent/overlapping ranges
    keep.sort()
    merged: list[tuple[float, float]] = [keep[0]]
    for s, e in keep[1:]:
        ls, le = merged[-1]
        if s <= le + 1e-6:
            merged[-1] = (ls, max(le, e))
        else:
            merged.append((s, e))

    # Round to ms precision
    return [(round(s, 3), round(e, 3)) for s, e in merged]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect tick events (visual transitions) in a video region."
    )
    parser.add_argument("video", type=Path, help="Source video file")
    parser.add_argument(
        "--time-range", required=True,
        help='Time range to search, "start:end" in seconds (e.g. "19:46")',
    )
    parser.add_argument(
        "--region-pct", required=True,
        help='Search region as "x,y,w,h" in % of source frame (e.g. "80,0,20,30")',
    )
    parser.add_argument(
        "--expected-ticks", type=int, required=True,
        help="Number of distinct tick moments to detect. For simultaneous "
             "ticks (e.g. two lines tick at the same instant), count as ONE moment.",
    )
    parser.add_argument(
        "--fps-sample", type=int, default=30,
        help="Sample rate in fps (default 30). Higher = more precise, more memory.",
    )
    parser.add_argument(
        "--suppress-seconds", type=float, default=0.8,
        help="Minimum seconds between detected peaks (non-maximum suppression). "
             "Default 0.8 — peaks closer than this are merged.",
    )
    parser.add_argument(
        "--tail-seconds", type=float, default=1.0,
        help="LEGACY (kept for backwards-compat). Seconds of source to keep on each side "
             "of each tick. Was used for the V1-era ±tail-seconds tail-cut. Superseded by "
             "the gap-cut rule (see --compress-threshold + --target-gap). Default 1.0.",
    )
    parser.add_argument(
        "--compress-threshold", type=float, default=2.0,
        help="Gap-cut rule threshold (per Hard Rule #23). Dead segments LONGER than this "
             "(in seconds) get compressed to --target-gap. Shorter segments are left at "
             "natural playback. Default 2.0.",
    )
    parser.add_argument(
        "--margin", type=float, default=1.0,
        help="Gap-cut rule per-side margin (per Hard Rule #23, V1 pattern). When a dead "
             "segment is compressed, keep `margin` seconds of source adjacent to each boundary "
             "tick. Pre-first-tick: keep margin before T1. Between-tick: keep margin after T_a "
             "+ margin before T_b. Post-last-tick: keep margin after T_N. Default 1.0 (V1 pattern: "
             "1s anticipation + 1s settling around each tick).",
    )
    parser.add_argument(
        "--target-gap", type=float, default=None,
        help="DEPRECATED — use --margin instead. (Old semantic: total compressed gap between "
             "ticks; new semantic: per-side margin.) If provided, treated as 2× --margin for "
             "backward compatibility.",
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="JSON output path. If omitted, prints to stdout.",
    )
    parser.add_argument(
        "--ffmpeg-ranges", action="store_true",
        help="In addition to JSON, print ffmpeg-ready trim ranges to stderr.",
    )
    args = parser.parse_args()

    if not args.video.exists():
        print(f"error: {args.video} does not exist", file=sys.stderr)
        return 1

    try:
        t_start, t_end = (float(x) for x in args.time_range.split(":"))
    except ValueError:
        print(f'error: --time-range must be "start:end" in seconds', file=sys.stderr)
        return 1
    if t_end <= t_start:
        print(f"error: t_end ({t_end}) must be > t_start ({t_start})", file=sys.stderr)
        return 1

    try:
        region_pct = tuple(float(x) for x in args.region_pct.split(","))
    except ValueError:
        print(f'error: --region-pct must be "x,y,w,h" in %', file=sys.stderr)
        return 1
    if len(region_pct) != 4:
        print(f"error: --region-pct must have 4 values", file=sys.stderr)
        return 1

    print(
        f"[detect-ticks] {args.video.name}: sampling {args.fps_sample}fps "
        f"from {t_start:.2f}s to {t_end:.2f}s, region {region_pct}%, "
        f"expecting {args.expected_ticks} ticks...",
        file=sys.stderr,
    )

    frames = extract_region_frames(
        args.video, t_start, t_end, args.fps_sample, region_pct
    )
    print(f"[detect-ticks] {len(frames)} frames extracted", file=sys.stderr)
    if len(frames) < 2:
        print("error: not enough frames extracted (region too small? time range too short?)", file=sys.stderr)
        return 2

    peaks = detect_tick_peaks(
        frames,
        expected_ticks=args.expected_ticks,
        suppress_seconds=args.suppress_seconds,
        fps_sample=args.fps_sample,
    )
    print(f"[detect-ticks] detected {len(peaks)} ticks", file=sys.stderr)

    # Apply gap-cut rule (per workflow Hard Rule #23 + decisions/2026-05-23 + 2026-05-24):
    # for each dead segment (pre-first-tick, between ticks, post-last-tick), if gap > compress_threshold
    # then keep `margin` seconds adjacent to each boundary tick; else keep natural.
    # Backward-compat: --target-gap (deprecated) is treated as 2× margin.
    if args.target_gap is not None:
        effective_margin = args.target_gap / 2.0
    else:
        effective_margin = args.margin
    tick_times = [round(t, 3) for t, _ in peaks]
    keep_ranges = compute_keep_ranges(
        t_start=t_start,
        t_end=t_end,
        tick_timestamps=tick_times,
        compress_threshold=args.compress_threshold,
        margin=effective_margin,
    )

    result = {
        "video": str(args.video),
        "time_range": [t_start, t_end],
        "region_pct": list(region_pct),
        "expected_ticks": args.expected_ticks,
        "fps_sample": args.fps_sample,
        "suppress_seconds": args.suppress_seconds,
        "tail_seconds": args.tail_seconds,
        "compress_threshold": args.compress_threshold,
        "margin": effective_margin,
        "ticks": [
            {
                "index": i,
                "t_tick": round(t, 3),
                "magnitude": round(mag, 2),
                "tail_start": round(t - args.tail_seconds, 3),
                "tail_end": round(t + args.tail_seconds, 3),
            }
            for i, (t, mag) in enumerate(peaks)
        ],
        # Gap-cut keep-ranges: paste these into the ffmpeg trim+concat that builds
        # the tick-compressed segment of the scrubbed file (Phase 3, not Phase 5.5).
        "ffmpeg_keep_ranges": [
            f"{s:.3f}:{e:.3f}" for (s, e) in keep_ranges
        ],
        # Legacy field — ±tail_seconds windows. Kept for backwards-compat but superseded
        # by ffmpeg_keep_ranges per the 2026-05-23 architecture move.
        "ffmpeg_trim_ranges": [
            f"{t - args.tail_seconds:.3f}:{t + args.tail_seconds:.3f}"
            for t, _ in peaks
        ],
    }

    output_json = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(output_json + "\n")
        print(f"[detect-ticks] wrote {args.output}", file=sys.stderr)
    else:
        print(output_json)

    if args.ffmpeg_ranges:
        print("\nffmpeg keep ranges (gap-cut rule):", file=sys.stderr)
        for r in result["ffmpeg_keep_ranges"]:
            print(f"  {r}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
