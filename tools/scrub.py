#!/usr/bin/env python3
"""
tools/scrub.py — Tapered scrub of dead loading time in screen recordings.

Detects "freeze" segments (frames not changing for > N seconds) and applies a
treatment based on length:
  - Short freezes (5s up to cut-threshold): uniform 2x speedup.
  - Long freezes (>= cut-threshold): keep the front 2s and back 2s at 2x speed,
    cut the middle entirely.
The 2s anchors preserve the "loading begins -> result lands" transition so
cuts feel real, not janky. Maximum speedup applied anywhere is 2x.

Threshold default: -45dB, tuned against V1 (Cowork plugin chrome with the
spinner + text-highlight-wave loading state). Empirical sweep found -60dB too
conservative (misses spinner-only loading), -40dB too aggressive (collapses
real content reveals). Re-tune the default if a future Parallax video has a
visually different loading pattern. Override per-recording via --diff-threshold.

Usage:
    python tools/scrub.py "screen recordings/V5/vid5.mp4"

Outputs (written alongside the input — i.e., inside the same per-video folder):
    <name>_scrubbed.mp4
    <name>_scrub_report.json
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


def get_video_duration(video_path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def detect_freezes(video_path: Path, noise_threshold: str,
                   min_dead_seconds: float) -> list[dict]:
    cmd = [
        "ffmpeg", "-hide_banner",
        "-i", str(video_path),
        "-vf", f"freezedetect=n={noise_threshold}:d={min_dead_seconds}",
        "-map", "0:v", "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    freezes: list[dict] = []
    current_start: Optional[float] = None
    current_duration: Optional[float] = None

    for line in result.stderr.split("\n"):
        m = re.search(r"freezedetect\.freeze_start:\s*([\d.]+)", line)
        if m:
            current_start = float(m.group(1))
            continue
        m = re.search(r"freezedetect\.freeze_duration:\s*([\d.]+)", line)
        if m:
            current_duration = float(m.group(1))
            continue
        m = re.search(r"freezedetect\.freeze_end:\s*([\d.]+)", line)
        if m and current_start is not None and current_duration is not None:
            freezes.append({
                "start": current_start,
                "end": float(m.group(1)),
                "duration": current_duration,
            })
            current_start = None
            current_duration = None
    return freezes


def cursor_moved_across_freeze(
    video_path: Path,
    freeze_start: float,
    freeze_end: float,
    *,
    pixel_threshold: int = 30,
    min_diff_pixels: int = 100,
    grid: int = 20,
    cursor_max_active_cells: int = 6,
    min_pixels_per_cell: int = 5,
) -> bool:
    """
    Compare frame at freeze_start to frame at freeze_end. Decide if the cursor
    moved across the span — distinguished from generic content evolution by
    spatial localization.

    Approach: compute per-cell pixel-change density on a `grid`×`grid` mesh.
    - If active cells <= cursor_max_active_cells: motion is localized (cursor)
      → return True.
    - If active cells > cursor_max_active_cells: motion is distributed across
      the frame (chat content, sidebar, brief reveal) → return False (content
      evolution, not cursor motion; safe to anchor-cut).

    This catches slow cursor drift below per-sample-pair detection threshold
    without false-positiving on content reveals during LLM-compute freezes.
    """
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return False

    if freeze_end - freeze_start < 1.0:
        return False

    with tempfile.TemporaryDirectory() as tmpdir:
        for label, t in [("start", freeze_start + 0.05), ("end", freeze_end - 0.05)]:
            cmd = [
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-ss", f"{t:.3f}",
                "-i", str(video_path),
                "-frames:v", "1",
                "-vf", "scale=480:-1,format=gray",
                f"{tmpdir}/{label}.png",
            ]
            subprocess.run(cmd, capture_output=True, check=False)

        start_path = os.path.join(tmpdir, "start.png")
        end_path = os.path.join(tmpdir, "end.png")
        if not (os.path.exists(start_path) and os.path.exists(end_path)):
            return False

        start_frame = np.array(Image.open(start_path), dtype=np.int16)
        end_frame = np.array(Image.open(end_path), dtype=np.int16)

    diff = np.abs(end_frame - start_frame)
    mask = (diff > pixel_threshold).astype(np.int32)
    total_changed = int(mask.sum())
    if total_changed < min_diff_pixels:
        return False  # no meaningful change

    # Spatial localization check via grid-cell density
    H, W = mask.shape
    cell_h, cell_w = max(H // grid, 1), max(W // grid, 1)
    h_used, w_used = cell_h * grid, cell_w * grid
    cell_counts = (
        mask[:h_used, :w_used]
        .reshape(grid, cell_h, grid, cell_w)
        .sum(axis=(1, 3))
    )
    active_cells = int((cell_counts > min_pixels_per_cell).sum())
    return 0 < active_cells <= cursor_max_active_cells


def detect_cursor_motion_in_freeze(
    video_path: Path,
    freeze_start: float,
    freeze_end: float,
    *,
    sample_fps: float = 4.0,
    pixel_threshold: int = 25,
    min_motion_pixels: int = 8,
    max_motion_pixels: int = 4000,
    motion_pad: float = 0.5,
    merge_gap: float = 0.7,
) -> list[tuple[float, float]]:
    """
    Within a detected freeze, find sub-windows where the cursor is moving.

    freezedetect uses whole-frame MSE, which is blind to cursor motion (cursor
    is ~0.01% of pixel area in a 3420x2146 frame). This function samples frames
    at sample_fps inside the freeze, computes inter-frame pixel diff, and flags
    intervals where a *small* number of pixels changed (cursor-sized) but not
    so many that it's a real content reveal.

    Pixel-diff math:
      - Frames downsampled to 480p grayscale for speed.
      - Pixels exceeding `pixel_threshold` (0-255) count as "changed".
      - If count is in [min_motion_pixels, max_motion_pixels], that's localized
        motion (likely cursor). Above max = real content reveal (shouldn't be
        inside a freeze; means freezedetect was too lenient). Below min = noise.

    Returns: list of (start, end) tuples in absolute video timestamps for
    motion windows, each padded by `motion_pad` on both sides and merged when
    closer than `merge_gap`. Empty list if no cursor motion detected.
    """
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return []

    if freeze_end - freeze_start < 1.0:
        return []

    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-ss", f"{freeze_start:.3f}",
            "-i", str(video_path),
            "-t", f"{freeze_end - freeze_start + 0.1:.3f}",
            "-vf", f"fps={sample_fps},scale=480:-1,format=gray",
            f"{tmpdir}/f%05d.png",
        ]
        subprocess.run(cmd, capture_output=True, check=False)

        files = sorted(os.listdir(tmpdir))
        if len(files) < 2:
            return []

        frames = [np.array(Image.open(os.path.join(tmpdir, f)), dtype=np.int16)
                  for f in files]

    motion_events: list[float] = []
    for i in range(1, len(frames)):
        diff = np.abs(frames[i] - frames[i - 1])
        changed = int((diff > pixel_threshold).sum())
        if min_motion_pixels <= changed <= max_motion_pixels:
            t_mid = freeze_start + (i - 0.5) / sample_fps
            motion_events.append(t_mid)

    if not motion_events:
        return []

    windows: list[tuple[float, float]] = []
    cur_start = motion_events[0] - motion_pad
    cur_end = motion_events[0] + motion_pad
    for t in motion_events[1:]:
        if t - motion_pad <= cur_end + merge_gap:
            cur_end = t + motion_pad
        else:
            windows.append((max(cur_start, freeze_start), min(cur_end, freeze_end)))
            cur_start = t - motion_pad
            cur_end = t + motion_pad
    windows.append((max(cur_start, freeze_start), min(cur_end, freeze_end)))

    return windows


def split_freezes_around_motion(
    freezes: list[dict],
    motion_windows_per_freeze: list[list[tuple[float, float]]],
    min_dead_seconds: float,
) -> list[dict]:
    """
    For each freeze that contains cursor-motion windows, split it into static
    sub-segments. Motion windows are removed from the freeze list entirely —
    they will play at 1x as non-freeze content. Static sub-segments shorter
    than min_dead_seconds are also dropped (not worth scrubbing).
    """
    expanded: list[dict] = []
    for freeze, motion_windows in zip(freezes, motion_windows_per_freeze):
        if not motion_windows:
            expanded.append(freeze)
            continue

        cursor = freeze["start"]
        for m_start, m_end in motion_windows:
            if m_start - cursor >= min_dead_seconds:
                expanded.append({
                    "start": cursor,
                    "end": m_start,
                    "duration": m_start - cursor,
                })
            cursor = m_end
        if freeze["end"] - cursor >= min_dead_seconds:
            expanded.append({
                "start": cursor,
                "end": freeze["end"],
                "duration": freeze["end"] - cursor,
            })
    return expanded


def get_freeze_effective_speed(
    freeze: dict,
    *,
    anchor_speed: float,
    force_speed_ranges: list[tuple[float, float, float]],
    multiply_speed_ranges: list[tuple[float, float, float]],
    min_speed_ranges: list[tuple[float, float, float]],
) -> float:
    """
    Predict the playback speed a freeze's segments will run at after all
    speed-modifying flags are applied. Used by plan_treatment to compute
    raw cut_threshold and anchor_seconds from their scrub-time counterparts.

    force-speed-range overrides everything (replaces the timeline section).
    multiply-speed-range multiplies the base speed.
    min-speed-range floors the speed.
    """
    fs = freeze["start"]
    fe = freeze["end"]
    for rstart, rend, force_speed in force_speed_ranges:
        if fs >= rstart and fe <= rend:
            return force_speed
    speed = anchor_speed
    for rstart, rend, multiplier in multiply_speed_ranges:
        if fs >= rstart and fe <= rend:
            speed *= multiplier
    for rstart, rend, min_sp in min_speed_ranges:
        if fs >= rstart and fe <= rend:
            speed = max(speed, min_sp)
    return speed


def plan_treatment(freeze: dict, *, anchor_seconds: float, anchor_speed: float,
                   cut_threshold: float, force_uniform: bool = False,
                   drop: bool = False) -> dict:
    duration = freeze["duration"]
    start = freeze["start"]
    end = freeze["end"]

    if drop:
        # Hard drop — no anchor, no speedup, freeze region removed entirely.
        # Use when visual state is identical before/after the freeze (cursor
        # in same position, same UI), so a hard cut is invisible.
        return {"kind": "drop", "segments": []}

    if duration < cut_threshold or force_uniform:
        # Short enough that uniform 2x speedup compresses without feeling weird
        return {
            "kind": "uniform_speedup",
            "segments": [{"start": start, "end": end, "speed": anchor_speed}],
        }

    # Long enough that even at 2x there'd still be too much middle — cut it,
    # keep just the natural front and back transitions
    front_end = start + anchor_seconds
    back_start = end - anchor_seconds
    return {
        "kind": "tapered_with_cut",
        "segments": [
            {"start": start, "end": front_end, "speed": anchor_speed},
            {"start": back_start, "end": end, "speed": anchor_speed},
        ],
    }


def build_timeline(total_duration: float, freezes: list[dict],
                   plans: list[dict]) -> list[dict]:
    timeline = []
    cursor = 0.0
    for freeze, plan in zip(freezes, plans):
        if freeze["start"] > cursor:
            timeline.append({"start": cursor, "end": freeze["start"], "speed": 1.0})
        for seg in plan["segments"]:
            timeline.append(dict(seg))
        cursor = freeze["end"]
    if cursor < total_duration:
        timeline.append({"start": cursor, "end": total_duration, "speed": 1.0})
    return timeline


def build_filter_graph(timeline: list[dict]) -> str:
    parts = []
    labels = []
    for i, seg in enumerate(timeline):
        label = f"[v{i}]"
        labels.append(label)
        speed_factor = 1.0 / seg["speed"]
        parts.append(
            f"[0:v]trim={seg['start']:.6f}:{seg['end']:.6f},"
            f"setpts=(PTS-STARTPTS)*{speed_factor:.6f}{label}"
        )
    n = len(labels)
    concat = "".join(labels) + f"concat=n={n}:v=1:a=0[outv]"
    return ";".join(parts) + ";" + concat


def render(video_path: Path, output_path: Path, filter_graph: str) -> bool:
    # -g 60 -keyint_min 60: force keyframe every 60 frames (= 1s at 60fps source).
    # Prevents Hyperframes' renderer from freezing on seeks to non-keyframe positions.
    # -movflags +faststart: moov atom at the start so the player doesn't have to
    # download the whole file before seeking.
    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-i", str(video_path),
        "-filter_complex", filter_graph,
        "-map", "[outv]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-g", "60", "-keyint_min", "60",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ffmpeg error tail:", result.stderr[-2000:], file=sys.stderr)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Tapered scrub of dead loading time.")
    parser.add_argument("video", type=Path, help="Input video file")
    parser.add_argument("--diff-threshold", default="-45dB",
                        help="freezedetect noise threshold (default: -45dB, tuned against V1's Cowork plugin loading visuals)")
    parser.add_argument("--min-dead-seconds", type=float, default=5.0,
                        help="minimum freeze length to bother processing")
    parser.add_argument("--cut-threshold-scrub", type=float, default=4.0,
                        help="scrub-time threshold for anchor-cut decision (default 4.0s). A freeze "
                             "is cut if its predicted scrub duration (raw / effective_speed) exceeds "
                             "this. Adapts to per-freeze speed: at 2× an 8s raw freeze produces 4s "
                             "scrub (borderline); at 3× a 12s raw freeze produces 4s scrub (borderline).")
    parser.add_argument("--anchor-seconds-scrub", type=float, default=1.5,
                        help="scrub-time anchor length PER SIDE (default 1.5s). Anchor cut produces "
                             "this much scrub on each side of the cut, so total anchor output = 2× "
                             "this value (default 3s scrub). Raw anchor seconds = this × effective_speed.")
    parser.add_argument("--cut-threshold", type=float, default=None,
                        help="DEPRECATED: raw-seconds cut threshold. Overrides --cut-threshold-scrub "
                             "if passed.")
    parser.add_argument("--anchor-seconds", type=float, default=None,
                        help="DEPRECATED: raw-seconds anchor per side. Overrides --anchor-seconds-scrub "
                             "if passed.")
    parser.add_argument("--anchor-speed", type=float, default=2.0,
                        help="default playback speed for freezes (the speed used when no "
                             "--min-speed-range, --force-speed-range, or --multiply-speed-range applies). "
                             "Max practical: 2.0.")
    parser.add_argument("--max-speed", type=float, default=2.0,
                        help="hard cap on any segment's playback speed (default 2.0). Enforces the "
                             "video-production-workflow Hard Rule that content speedup max is 1.5–2× — "
                             "anything faster reads as comedic. Applied as a final pass on the timeline. "
                             "Pass a higher value (e.g. 3.0) to allow super-fast playback for specific "
                             "videos with explicit reason.")
    parser.add_argument("--force-uniform-starts", default="",
                        help="comma-separated raw start-timestamps (seconds) of freezes that should "
                             "always use uniform 2x speedup, never anchor-cut. Tolerance ±0.5s. "
                             "Opt-in escape hatch for recordings where a specific freeze spans active "
                             "cursor/scroll motion (anchor-cut would jump). Default: empty (no overrides).")
    parser.add_argument("--clip-freeze-end", default="",
                        help="comma-separated 'start:new_end' pairs (seconds) — truncate the end of "
                             "a detected freeze. Tolerance ±0.5s on matching start. The portion "
                             "between new_end and the original detected end becomes non-freeze "
                             "content (1x playback). Use when freezedetect's end overshoots into "
                             "real motion (e.g. cursor moves at tail of long static window). Opt-in.")
    parser.add_argument("--drop-starts", default="",
                        help="comma-separated raw start-timestamps (seconds) of freezes to drop "
                             "entirely — no anchor, no speedup, region removed from timeline. "
                             "Tolerance ±0.5s. Use when visual state is identical before and after "
                             "the freeze (cursor in same position, same UI), so a hard cut is "
                             "invisible. Stacks with --clip-freeze-end (clip first, then drop).")
    parser.add_argument("--drop-ranges", default="",
                        help="comma-separated raw 'start:end' pairs (seconds) — drop arbitrary raw "
                             "time ranges from the timeline, independent of freeze detection. "
                             "Applied AFTER freeze-based scrub planning, can split segments. Use "
                             "for surgical cuts of dead time that freezedetect aggregated with "
                             "real content evolution. Visual state must be identical on both sides "
                             "of the drop range for the cut to be invisible.")
    parser.add_argument("--cursor-aware", action="store_true",
                        help="enable cursor-motion-aware freeze splitting. After freezedetect, "
                             "scan inside each detected freeze for localized pixel motion (cursor-"
                             "sized) that whole-frame MSE missed. Split freezes around cursor-motion "
                             "windows so those play at 1x instead of being collapsed by anchor-cut. "
                             "Requires numpy and PIL. Adds ~10-30s wall-clock per recording.")
    parser.add_argument("--cursor-sample-fps", type=float, default=4.0,
                        help="sample rate (fps) for cursor motion detection inside freezes")
    parser.add_argument("--cursor-pixel-threshold", type=int, default=25,
                        help="per-pixel intensity delta (0-255) to count as 'changed'")
    parser.add_argument("--cursor-min-px", type=int, default=8,
                        help="minimum changed pixels per sample pair to register motion (noise floor)")
    parser.add_argument("--cursor-max-px", type=int, default=4000,
                        help="maximum changed pixels per sample pair — above this is real content motion, not cursor")
    parser.add_argument("--cursor-endpoint-threshold", type=int, default=30,
                        help="per-pixel intensity delta (0-255) for the endpoint check (start vs end "
                             "of a sub-segment). Lower than --cursor-pixel-threshold because cumulative "
                             "drift over many seconds is gentler per-pixel than instant cursor motion.")
    parser.add_argument("--cursor-endpoint-min-px", type=int, default=100,
                        help="minimum changed pixels between sub-segment start and end frames to mark "
                             "force_uniform. No upper bound (large content evolution also requires uniform).")
    parser.add_argument("--force-speed-range", default="",
                        help="comma-separated 'raw_start:raw_end:speed' triples — override the timeline "
                             "to play the specified raw range as one continuous segment at the given "
                             "speed multiplier. Eliminates anchor cuts and 1x motion windows inside the "
                             "range. Use to force a section (e.g. 'loading segment') to one uniform "
                             "pace. Example: '7.2:193.8:2.0' plays raw 7.2-193.8 at 2x continuously.")
    parser.add_argument("--multiply-speed-range", default="",
                        help="comma-separated 'raw_start:raw_end:multiplier' triples — multiply the "
                             "speed of all existing timeline segments within the range by the multiplier. "
                             "KEEPS the existing cut structure (anchor cuts, motion windows, uniform "
                             "speedups) — only changes how fast each segment plays. Example: "
                             "'7.2:193.8:2.0' makes anchor cuts that were 2× become 4×, motion windows "
                             "that were 1× become 2×, etc. — entire loading section plays twice as fast "
                             "while preserving cut structure.")
    parser.add_argument("--min-speed-range", default="",
                        help="comma-separated 'raw_start:raw_end:min_speed' triples — ensure every "
                             "timeline segment within the range plays at AT LEAST the specified speed. "
                             "Keeps cut structure intact. Segments already at or above min_speed are "
                             "left unchanged. Example: '7.2:193.8:2.0' brings 1× motion windows up to "
                             "2× while leaving existing 2× anchor cuts unchanged — entire loading section "
                             "plays at min 2× pace.")
    args = parser.parse_args()

    force_starts = [float(s.strip()) for s in args.force_uniform_starts.split(",") if s.strip()]
    drop_starts = [float(s.strip()) for s in args.drop_starts.split(",") if s.strip()]
    drop_ranges = []
    for pair in args.drop_ranges.split(","):
        pair = pair.strip()
        if not pair:
            continue
        s_str, e_str = pair.split(":")
        drop_ranges.append((float(s_str), float(e_str)))
    drop_ranges.sort()
    clip_overrides = {}
    for pair in args.clip_freeze_end.split(","):
        pair = pair.strip()
        if not pair:
            continue
        start_str, end_str = pair.split(":")
        clip_overrides[float(start_str)] = float(end_str)
    force_speed_ranges: list[tuple[float, float, float]] = []
    for triple in args.force_speed_range.split(","):
        triple = triple.strip()
        if not triple:
            continue
        parts = triple.split(":")
        if len(parts) != 3:
            print(f"error: --force-speed-range entry '{triple}' must be 'start:end:speed'", file=sys.stderr)
            sys.exit(1)
        force_speed_ranges.append((float(parts[0]), float(parts[1]), float(parts[2])))
    force_speed_ranges.sort()
    multiply_speed_ranges: list[tuple[float, float, float]] = []
    for triple in args.multiply_speed_range.split(","):
        triple = triple.strip()
        if not triple:
            continue
        parts = triple.split(":")
        if len(parts) != 3:
            print(f"error: --multiply-speed-range entry '{triple}' must be 'start:end:multiplier'", file=sys.stderr)
            sys.exit(1)
        multiply_speed_ranges.append((float(parts[0]), float(parts[1]), float(parts[2])))
    multiply_speed_ranges.sort()
    min_speed_ranges: list[tuple[float, float, float]] = []
    for triple in args.min_speed_range.split(","):
        triple = triple.strip()
        if not triple:
            continue
        parts = triple.split(":")
        if len(parts) != 3:
            print(f"error: --min-speed-range entry '{triple}' must be 'start:end:min_speed'", file=sys.stderr)
            sys.exit(1)
        min_speed_ranges.append((float(parts[0]), float(parts[1]), float(parts[2])))
    min_speed_ranges.sort()

    if not args.video.exists():
        print(f"error: {args.video} not found", file=sys.stderr)
        sys.exit(1)

    print(f"[scrub] analyzing {args.video.name}")
    duration = get_video_duration(args.video)
    print(f"[scrub] duration: {duration:.2f}s")

    freezes = detect_freezes(args.video, args.diff_threshold, args.min_dead_seconds)
    print(f"[scrub] found {len(freezes)} dead segment(s)")

    for f in freezes:
        for clip_start, clip_end in clip_overrides.items():
            if abs(f["start"] - clip_start) < 0.5:
                print(f"[scrub] clipping freeze at {f['start']:.1f}s: end {f['end']:.1f}s → {clip_end:.1f}s")
                f["end"] = clip_end
                f["duration"] = clip_end - f["start"]
                break

    cursor_force_uniform: list[bool] = [False] * len(freezes)
    if args.cursor_aware and freezes:
        print(f"[scrub] cursor-aware scan: {len(freezes)} freeze(s)")
        motion_windows_per_freeze: list[list[tuple[float, float]]] = []
        for f in freezes:
            windows = detect_cursor_motion_in_freeze(
                args.video, f["start"], f["end"],
                sample_fps=args.cursor_sample_fps,
                pixel_threshold=args.cursor_pixel_threshold,
                min_motion_pixels=args.cursor_min_px,
                max_motion_pixels=args.cursor_max_px,
            )
            motion_windows_per_freeze.append(windows)
            if windows:
                w_str = ", ".join(f"{s:.1f}-{e:.1f}s" for s, e in windows)
                print(f"[scrub]   freeze {f['start']:.1f}-{f['end']:.1f}s: "
                      f"{len(windows)} motion window(s) at {w_str}")

        # Split each freeze around cursor-motion windows. Motion windows are
        # removed from the freeze list (they play at 1x). Static sub-segments
        # between motion windows are kept as freezes for normal treatment.
        freezes_before = len(freezes)
        freezes = split_freezes_around_motion(
            freezes, motion_windows_per_freeze, args.min_dead_seconds
        )
        print(f"[scrub] after split around motion: {freezes_before} → {len(freezes)} freeze(s)")

        # Static sub-segments get default treatment (anchor-cut if long, uniform
        # if short). If a sub-segment has slow cursor drift below the per-sample
        # motion threshold, use --force-uniform-starts manually on the parent
        # freeze (the auto-endpoint check produced too many false positives on
        # content evolution during LLM-compute windows).
        cursor_force_uniform = [False] * len(freezes)
        print(f"[scrub] cursor-aware: motion windows extracted; "
              f"static sub-segments get default treatment (use --force-uniform-starts "
              f"for sub-segments with slow drift below detection)")

    if not freezes:
        print("[scrub] nothing to scrub. exiting.")
        sys.exit(0)

    plans = []
    for i, f in enumerate(freezes):
        effective_speed = get_freeze_effective_speed(
            f,
            anchor_speed=args.anchor_speed,
            force_speed_ranges=force_speed_ranges,
            multiply_speed_ranges=multiply_speed_ranges,
            min_speed_ranges=min_speed_ranges,
        )
        # Per-freeze raw thresholds derived from scrub-time settings + effective speed.
        # Deprecated raw flags override scrub-time defaults if explicitly passed.
        raw_cut_threshold = (
            args.cut_threshold
            if args.cut_threshold is not None
            else args.cut_threshold_scrub * effective_speed
        )
        raw_anchor_seconds = (
            args.anchor_seconds
            if args.anchor_seconds is not None
            else args.anchor_seconds_scrub * effective_speed
        )
        plans.append(plan_treatment(
            f,
            anchor_seconds=raw_anchor_seconds,
            anchor_speed=effective_speed,
            cut_threshold=raw_cut_threshold,
            force_uniform=(
                any(abs(f["start"] - fs) < 0.5 for fs in force_starts)
                or cursor_force_uniform[i]
            ),
            drop=any(abs(f["start"] - ds) < 0.5 for ds in drop_starts),
        ))

    timeline = build_timeline(duration, freezes, plans)

    if drop_ranges:
        new_timeline = []
        for seg in timeline:
            pieces = [(seg["start"], seg["end"])]
            for ds, de in drop_ranges:
                next_pieces = []
                for s, e in pieces:
                    if e <= ds or s >= de:
                        next_pieces.append((s, e))
                    elif s < ds and e > de:
                        next_pieces.append((s, ds))
                        next_pieces.append((de, e))
                    elif s < ds:
                        next_pieces.append((s, ds))
                    elif e > de:
                        next_pieces.append((de, e))
                pieces = next_pieces
            for s, e in pieces:
                if e - s > 0.01:
                    new_timeline.append({"start": s, "end": e, "speed": seg["speed"]})
        timeline = new_timeline
        for ds, de in drop_ranges:
            print(f"[scrub] dropping raw range {ds:.1f}-{de:.1f}s ({de-ds:.1f}s)")

    if force_speed_ranges:
        for rstart, rend, rspeed in force_speed_ranges:
            new_timeline = []
            for seg in timeline:
                if seg["end"] <= rstart or seg["start"] >= rend:
                    new_timeline.append(seg)
                else:
                    if seg["start"] < rstart:
                        new_timeline.append({**seg, "end": rstart})
                    if seg["end"] > rend:
                        new_timeline.append({**seg, "start": rend})
            new_timeline.append({"start": rstart, "end": rend, "speed": rspeed})
            new_timeline.sort(key=lambda s: s["start"])
            timeline = new_timeline
            print(f"[scrub] force-speed: raw {rstart:.1f}-{rend:.1f}s @ {rspeed}× "
                  f"(replaces all cuts/motion windows in this range with one continuous segment)")

    if multiply_speed_ranges:
        for rstart, rend, multiplier in multiply_speed_ranges:
            new_timeline = []
            for seg in timeline:
                if seg["end"] <= rstart or seg["start"] >= rend:
                    new_timeline.append(seg)
                elif seg["start"] >= rstart and seg["end"] <= rend:
                    new_timeline.append({**seg, "speed": seg["speed"] * multiplier})
                else:
                    if seg["start"] < rstart:
                        new_timeline.append({**seg, "end": rstart})
                    inner_start = max(seg["start"], rstart)
                    inner_end = min(seg["end"], rend)
                    new_timeline.append({
                        **seg,
                        "start": inner_start,
                        "end": inner_end,
                        "speed": seg["speed"] * multiplier,
                    })
                    if seg["end"] > rend:
                        new_timeline.append({**seg, "start": rend})
            timeline = new_timeline
            print(f"[scrub] multiply-speed: raw {rstart:.1f}-{rend:.1f}s × {multiplier} "
                  f"(keeps cuts/motion windows; each segment's existing speed multiplied)")

    if min_speed_ranges:
        for rstart, rend, min_speed in min_speed_ranges:
            new_timeline = []
            for seg in timeline:
                if seg["end"] <= rstart or seg["start"] >= rend:
                    new_timeline.append(seg)
                elif seg["start"] >= rstart and seg["end"] <= rend:
                    new_timeline.append({**seg, "speed": max(seg["speed"], min_speed)})
                else:
                    if seg["start"] < rstart:
                        new_timeline.append({**seg, "end": rstart})
                    inner_start = max(seg["start"], rstart)
                    inner_end = min(seg["end"], rend)
                    new_timeline.append({
                        **seg,
                        "start": inner_start,
                        "end": inner_end,
                        "speed": max(seg["speed"], min_speed),
                    })
                    if seg["end"] > rend:
                        new_timeline.append({**seg, "start": rend})
            timeline = new_timeline
            print(f"[scrub] min-speed: raw {rstart:.1f}-{rend:.1f}s @ min {min_speed}× "
                  f"(slower segments brought up to {min_speed}×; faster ones unchanged)")

    # Final cap pass — enforce --max-speed on any segment whose speed exceeded
    # the cap after min/multiply/force speed range adjustments.
    if args.max_speed and args.max_speed > 0:
        over_limit = [seg for seg in timeline if seg["speed"] > args.max_speed + 1e-6]
        if over_limit:
            speeds_str = ", ".join(f"{s['speed']:.2f}×" for s in over_limit[:5])
            print(f"[scrub] capping {len(over_limit)} segment(s) to --max-speed {args.max_speed}× "
                  f"(was: {speeds_str}{'...' if len(over_limit) > 5 else ''}) — workflow rule, "
                  f"pass --max-speed higher to override")
            timeline = [{**seg, "speed": min(seg["speed"], args.max_speed)} for seg in timeline]

    filter_graph = build_filter_graph(timeline)

    output_path = args.video.with_name(args.video.stem + "_scrubbed.mp4")
    print(f"[scrub] rendering to {output_path.name}")
    if not render(args.video, output_path, filter_graph):
        sys.exit(2)

    new_duration = get_video_duration(output_path)
    report = {
        "input": str(args.video),
        "output": str(output_path),
        "raw_duration": round(duration, 2),
        "scrubbed_duration": round(new_duration, 2),
        "compression_ratio": round(1 - (new_duration / duration), 3),
        "freezes": [
            {
                "start": round(f["start"], 2),
                "end": round(f["end"], 2),
                "duration": round(f["duration"], 2),
                "treatment": p["kind"],
            }
            for f, p in zip(freezes, plans)
        ],
        "config": {
            "diff_threshold": args.diff_threshold,
            "min_dead_seconds": args.min_dead_seconds,
            "cut_threshold_scrub": args.cut_threshold_scrub,
            "anchor_seconds_scrub": args.anchor_seconds_scrub,
            "cut_threshold_raw_override": args.cut_threshold,
            "anchor_seconds_raw_override": args.anchor_seconds,
            "anchor_speed": args.anchor_speed,
            "force_uniform_starts": force_starts,
            "clip_freeze_end": {str(k): v for k, v in clip_overrides.items()},
            "drop_starts": drop_starts,
            "drop_ranges": [[s, e] for s, e in drop_ranges],
            "cursor_aware": args.cursor_aware,
            "cursor_force_uniform_per_freeze": cursor_force_uniform if args.cursor_aware else [],
            "force_speed_ranges": [[s, e, sp] for s, e, sp in force_speed_ranges],
            "multiply_speed_ranges": [[s, e, m] for s, e, m in multiply_speed_ranges],
            "min_speed_ranges": [[s, e, m] for s, e, m in min_speed_ranges],
            "max_speed": args.max_speed,
        },
    }

    report_path = args.video.with_name(args.video.stem + "_scrub_report.json")
    report_path.write_text(json.dumps(report, indent=2))

    print()
    print(f"[scrub] done.")
    print(f"  raw:      {duration:.2f}s")
    print(f"  scrubbed: {new_duration:.2f}s ({report['compression_ratio']*100:.1f}% compression)")
    print(f"  report:   {report_path.name}")


if __name__ == "__main__":
    main()
