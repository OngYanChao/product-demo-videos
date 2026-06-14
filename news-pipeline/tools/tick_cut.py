#!/usr/bin/env python3
"""tick_cut.py — tail-cut compression around progress-sidebar phase ticks.

After scrub.py's frame-diff dead-time cut, the streaming portion of a news
recording still contains long inter-tick stretches where Cowork is busy with
tool calls but the visible UI barely changes (scrub doesn't catch those because
text *is* slowly appearing in the chat — small per-frame deltas above the
freeze threshold). The Progress sidebar is the clean signal: it ticks through
discrete phases (Phase 1 active → checked → Phase 2 active → …), and we can
detect those tick moments precisely.

Pipeline position (V2 order, confirmed): scrub → tick-cut → zoom.

This tool wraps the main pipeline's tools/detect_ticks.py (the "measured, not
eyeballed" tick detector — Hard Rule #20) and then applies the resulting tick
windows via an ffmpeg trim+concat filter graph, keeping:
  • the pre-tick region [0 → first tick window start]   (user typing, intro)
  • each tick window from detect_ticks                   (phase-transition flash)
  • the post-tick region [last tick window end → end]    (response writing,
                                                          scroll, smooth scroll-down)
and dropping everything BETWEEN tick windows — that's the inter-tick dead time
we're targeting.

Region default `[78, 0, 22, 30]` was visually measured against N11's frame at
1920×1080-logical-equivalent (matches V1's [80, 0, 20, 30] with a small shift
for the news layout).

Usage:
    python3 news-pipeline/tools/tick_cut.py INPUT.mp4 OUTPUT.mp4
    python3 news-pipeline/tools/tick_cut.py INPUT.mp4 OUTPUT.mp4 \\
        --region-pct "78,0,22,30" --expected-ticks 8 --tail-seconds 1.0
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

NEWS_PIPELINE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = NEWS_PIPELINE_ROOT.parent
MAIN_TOOLS = PROJECT_ROOT / "tools"

# Cowork Progress-sidebar region — V1's canonical value from 1vid_zooms.json.
# Format: "x_pct,y_pct,w_pct,h_pct".
DEFAULT_REGION_PCT = "80,0,20,30"
# How many peaks to surface from detect_ticks. Cowork news tasks typically
# have 2–6 real phase ticks, but the scrubbed file also contains the brief-
# landed snap (mag 100+), outro animation, and scroll-start peaks that have
# higher magnitudes than the actual checklist ticks (mag ~10-15). If we cap
# detection too low (e.g., 8), the real first tick — which is the lowest-t
# real-checklist peak — gets edged out by these higher-mag post-streaming
# events, and tick_cut anchors z0b around the wrong content. Setting to 20
# safely surfaces all real ticks + the higher-mag post events; the lowest-t
# qualifying peak is then the real first tick. NMS still prevents adjacent
# peaks from double-counting.
DEFAULT_EXPECTED_TICKS = 100  # bumped from 20 → 100 (2026-06-08) so low-mag real ticks (mag 5-15 in tool-heavy queries) aren't edged out of the top-N by higher-mag post-brief scroll events
# Window kept around each tick: tail_seconds before + tail_seconds after.
# Newsletter/email embed default — ticks fire every 1s (tail=0.5 each side).
DEFAULT_TAIL_SECONDS = 1.0  # V1 pattern: ±1s around each tick (was 0.5; bumped 2026-06-05 so each tick has 1s of pre-tick anticipation + 1s of post-tick settling)
# Pre-segment: by default keep the FULL pre. The pre contains the prompt
# being typed in — that's the news question / topic the viewer needs as
# context for the analysis, not noise. Caller can pass a numeric value to
# compress further if a specific recording's pre is unusually long, but the
# default never silently cuts user-visible content.
DEFAULT_PRE_SECONDS: float | None = None  # None = keep entire pre-tick (process.py handles buffer-1 compression separately)
# Post-segment: by default keep ALL the post-tick segment — that's the
# response writing + scroll-down, the part the viewer is watching for.
DEFAULT_POST_SECONDS: float | None = None

# Auto-zoom — mirrors the main pipeline V1's z0 + z0b skeleton (Hard Rules
# #22 + #23 in .claude/skills/video-production-workflow/SKILL.md):
#   z0  — follow zoom on the CHAT INPUT BOX during prompt typing.
#         Region = the prompt input rect (Cowork chrome standard: [40, 24, 38, 11]).
#         Camera holds at zoom during typing; ease-out starts at T_click
#         (= start of the first tick window in output time) and plays through
#         the first `ease` seconds of loading.
#   z0b — follow zoom on the PROGRESS SIDEBAR during the tick montage.
#         Region = the Progress sidebar (measured: [78, 0, 22, 30]).
#         Starts immediately after z0 ends, eases in over the first part of
#         the tick montage, holds, eases out just before the response writes.
# Sequential, no inter-pause (natural source-t gap > the 1.5s pause threshold).
# Per-directive `pause_after: 0` belt-and-suspenders against future pause defaults.
# Literal values from V1's 1vid_zooms.json — never adapt these; the user has
# explicitly settled them through main-pipeline tuning. Per feedback memory
# `feedback_copy_v1_stats_literal`.
AUTO_ZOOM_INPUT_REGION_PCT = [40, 24, 38, 11]    # V1 z0.region_pct
AUTO_ZOOM_PROGRESS_REGION_PCT = [80, 0, 20, 30]  # V1 z0b.region_pct
AUTO_ZOOM_INPUT_FACTOR = 1.5             # V1 z0.zoom (NOT 2.5 — that's z0b's value)
AUTO_ZOOM_PROGRESS_FACTOR = 2.5          # V1 z0b.zoom
AUTO_ZOOM_EASE_S = 1.5                   # V1 ease for both z0 + z0b
# Gap (in OUTPUT time) between z0 ease-out and z0b ease-in. Set to 0 so the
# camera transitions continuously from chat-input zoom into Progress-sidebar
# zoom — sidebar IS the loading visual; full-frame gap defeats that focus.
AUTO_ZOOM_Z0_Z0B_GAP_S = 0.0

# News-pipeline hard rule (decisions/2026-05-28-news-1s-dead-time-cap.md):
# any dead-time interval >1s in the POST-tick portion of the output is capped
# to 1s. Catches: (a) brief-done-to-cut-to-top dwell, (b) post-scroll tail
# before outro. Pre + tick-montage are protected (typing pauses + phase-holds
# are intentional pacing).
NEWS_MAX_DEAD_S = 1.0


def ffprobe_duration(video: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return float(out)


def _build_keep_ranges(tick_windows: list[tuple[float, float]],
                       duration: float,
                       pre_seconds: float | None = None,
                       post_seconds: float | None = None) -> list[tuple[float, float]]:
    """Wrap the detect_ticks windows with the pre- and post-tick segments.

    detect_ticks gives us [tail_start, tail_end] for each tick. We additionally
    keep a slice of pre-tick time (default: last `pre_seconds` before the first
    tick, so the user-typed-prompt intro is trimmed to a glimpse) and the full
    post-tick segment (the response writing + read-through — the meat). Set
    pre_seconds=None to keep the entire pre; post_seconds=N to cap the tail.
    """
    if not tick_windows:
        return [(0.0, duration)]
    ranges: list[tuple[float, float]] = []

    # Pre segment
    first_start = tick_windows[0][0]
    if first_start > 0.0:
        pre_start = 0.0 if pre_seconds is None else max(0.0, first_start - pre_seconds)
        if pre_start < first_start:
            ranges.append((pre_start, first_start))

    # Tick windows
    ranges.extend(tick_windows)

    # Post segment
    last_end = tick_windows[-1][1]
    if last_end < duration:
        post_end = duration if post_seconds is None else min(duration, last_end + post_seconds)
        if last_end < post_end:
            ranges.append((last_end, post_end))
    return ranges


def _build_filter_graph(ranges: list[tuple[float, float]]) -> str:
    """trim+concat filter_complex for the given keep ranges."""
    parts = []
    refs = []
    for i, (s, e) in enumerate(ranges):
        parts.append(f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{i}]")
        refs.append(f"[v{i}]")
    parts.append(f"{''.join(refs)}concat=n={len(ranges)}:v=1:a=0[out]")
    return ";".join(parts)


def tick_cut(input_mp4: Path, output_mp4: Path,
             region_pct: str = DEFAULT_REGION_PCT,
             expected_ticks: int = DEFAULT_EXPECTED_TICKS,
             tail_seconds: float = DEFAULT_TAIL_SECONDS,
             pre_seconds: float | None = DEFAULT_PRE_SECONDS,
             post_seconds: float | None = DEFAULT_POST_SECONDS,
             scan_start_s: float = 0.0,
             scan_end_s: float | None = None) -> bool:
    """Run detect_ticks + trim+concat + emit z0/z0b zooms. Returns True on success.

    `scan_start_s`: limit detect_ticks's time range to [scan_start_s, scan_end_s].
    Caller passes typing_end_scrubbed (+ small buffer) so detect_ticks doesn't
    pick up typing-zone false positives.

    `scan_end_s`: upper bound for detection scan. Caller passes
    preserve_end_scrubbed (= the boundary between the at-1× preserved tick
    montage and the scrub-compressed post region) so post-brief scroll
    content peaks (mag 20-40) don't dominate the top-N and squeeze out
    low-mag real ticks. Defaults to in_duration if None.
    """
    input_mp4 = input_mp4.resolve()
    output_mp4 = output_mp4.resolve()
    if not input_mp4.exists():
        print(f"[tick-cut] ❌ input not found: {input_mp4}")
        return False

    in_duration = ffprobe_duration(input_mp4)
    ticks_json = output_mp4.with_suffix(".ticks.json")

    # ── 1. detect ticks via the main pipeline's tool ─────────────────────
    # Scan [scan_start_s, scan_end_s]. Caller bounds the range to the
    # at-1×-preserved tick montage region (skipping typing-zone false
    # positives at the front and post-brief scroll noise at the back).
    scan_end_effective = scan_end_s if scan_end_s is not None else in_duration
    time_range = f"{scan_start_s:.2f}:{scan_end_effective:.2f}"
    print(f"[tick-cut] detect_ticks range={time_range} region={region_pct} "
          f"expected={expected_ticks} tail={tail_seconds}s")
    try:
        subprocess.run([
            "python3", str(MAIN_TOOLS / "detect_ticks.py"),
            str(input_mp4),
            "--time-range", time_range,
            "--region-pct", region_pct,
            "--expected-ticks", str(expected_ticks),
            "--tail-seconds", str(tail_seconds),
            # detect_ticks' --margin (default 1.0) controls the WIDTH of each
            # ffmpeg_keep_ranges window independently of --tail-seconds (which
            # only sets per-tick tail_start/tail_end metadata). Bind them so
            # our tail_seconds knob actually changes the cut output.
            "--margin", str(tail_seconds),
            "--output", str(ticks_json),
        ], check=True, cwd=str(PROJECT_ROOT))
    except subprocess.CalledProcessError as e:
        print(f"[tick-cut] ⚠️  detect_ticks failed (rc={e.returncode}); "
              f"falling back to copying input unchanged")
        shutil.copy(input_mp4, output_mp4)
        return False
    if not ticks_json.exists():
        print(f"[tick-cut] ⚠️  detect_ticks didn't produce {ticks_json.name}")
        shutil.copy(input_mp4, output_mp4)
        return False

    # ── 2. parse keep ranges + wrap with pre/post ────────────────────────
    ticks_data = json.loads(ticks_json.read_text())
    all_peaks = ticks_data.get("ticks", [])
    # Filter detected peaks to REAL checkmark ticks by magnitude:
    #   - mag ≥ 3.0: excludes sub-tick noise (cursor blinks at 0.4-0.8)
    #   - mag < 100.0: excludes the brief-landed snap itself (mag 100-150)
    #     AND any other high-mag UI-collapse events. We exclude these because
    #     they're qualitatively different from checkmark ticks — they'd skew
    #     z0b sizing if treated as ticks.
    # Position filtering is handled at the scan layer: scan_end_s = preserve_
    # end_scrubbed bounds the range to the at-1× preserved tick montage, so
    # post-brief scroll content peaks don't reach this filter at all.
    real_ticks = [t for t in all_peaks
                  if 3.0 <= t.get("magnitude", 0) < 100.0]
    real_ticks.sort(key=lambda t: t["t_tick"])
    # Build per-tick windows: ±tail_seconds around each tick_t.
    tick_windows: list[tuple[float, float]] = [
        (max(0.0, t["t_tick"] - tail_seconds),
         min(in_duration, t["t_tick"] + tail_seconds))
        for t in real_ticks
    ]

    if not tick_windows:
        print(f"[tick-cut] no ticks detected; copying input unchanged")
        shutil.copy(input_mp4, output_mp4)
        return True

    keep_ranges = _build_keep_ranges(tick_windows, in_duration,
                                     pre_seconds=pre_seconds,
                                     post_seconds=post_seconds)
    kept = sum(e - s for s, e in keep_ranges)
    print(f"[tick-cut] {len(tick_windows)} ticks → keeping {len(keep_ranges)} segment(s) "
          f"= {kept:.2f}s of {in_duration:.2f}s ({100*(1-kept/in_duration):.1f}% cut)  "
          f"[tail={tail_seconds}s pre={pre_seconds}s post={post_seconds}]")

    # ── 3. apply trim+concat ────────────────────────────────────────────
    filter_graph = _build_filter_graph(keep_ranges)
    cmd = [
        "ffmpeg", "-y", "-i", str(input_mp4),
        "-filter_complex", filter_graph,
        "-map", "[out]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        # Hard Rule #15: 60fps + 1s keyframes end-to-end on every pipeline
        # intermediate, not just the final deliverable.
        "-g", "60", "-keyint_min", "60",
        "-pix_fmt", "yuv420p",
        str(output_mp4),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"[tick-cut] ⚠️  ffmpeg trim+concat failed (rc={e.returncode}); "
              f"stderr tail:\n{e.stderr.decode(errors='replace')[-800:]}")
        return False

    out_duration = ffprobe_duration(output_mp4)
    print(f"[tick-cut] ✓ {input_mp4.name} ({in_duration:.2f}s) → "
          f"{output_mp4.name} ({out_duration:.2f}s)")

    # Emit z0 + z0b auto-zoom directives (mirrors V1's skeleton per Hard Rules
    # #22 + #23). Pre + tick-windows in output time split into two sequential
    # follow zooms; post (response + scroll) plays at full frame.
    post_start_in_input = tick_windows[-1][1]
    first_tick_start = tick_windows[0][0]
    pre_output_dur = 0.0
    tick_montage_output_dur = 0.0
    for r_start, r_end in keep_ranges:
        if r_start >= post_start_in_input:
            continue  # this is the post segment
        if r_start < first_tick_start:
            pre_output_dur += (r_end - r_start)
        else:
            tick_montage_output_dur += (r_end - r_start)

    ease = AUTO_ZOOM_EASE_S
    auto_zooms = []

    # z0: chat-input follow during prompt typing. Skip if pre is too short to
    # be a meaningful zoom (<0.5s of held time after ease windows).
    if pre_output_dur > 0.5:
        z0_duration = round(pre_output_dur + ease, 3)
        auto_zooms.append({
            "source_t": 0.0,
            "duration": z0_duration,
            "region_pct": AUTO_ZOOM_INPUT_REGION_PCT,
            "zoom": AUTO_ZOOM_INPUT_FACTOR,
            "ease": ease,
            "mode": "follow",
            "pause_after": 0,
        })
        z0b_source_t = z0_duration + AUTO_ZOOM_Z0_Z0B_GAP_S
    else:
        z0b_source_t = pre_output_dur + AUTO_ZOOM_Z0_Z0B_GAP_S

    # z0b: Progress-sidebar follow during the tick montage. Starts where z0
    # ends (or at the tick-montage start if z0 was skipped) and runs to the
    # end of the montage.
    total_montage_out_dur = pre_output_dur + tick_montage_output_dur
    z0b_duration = round(total_montage_out_dur - z0b_source_t, 3)
    if z0b_duration > 2 * ease:
        auto_zooms.append({
            "source_t": round(z0b_source_t, 3),
            "duration": z0b_duration,
            "region_pct": AUTO_ZOOM_PROGRESS_REGION_PCT,
            "zoom": AUTO_ZOOM_PROGRESS_FACTOR,
            "ease": ease,
            "mode": "follow",
        })

    auto_zooms_path = output_mp4.with_suffix(".auto_zooms.json")
    auto_zooms_path.write_text(json.dumps(auto_zooms, indent=2))
    summary = ", ".join(
        f"{'z0' if i == 0 and pre_output_dur > 0.5 else 'z0b'} "
        f"@ source_t={d['source_t']} dur={d['duration']}s"
        for i, d in enumerate(auto_zooms)
    )
    print(f"[tick-cut] auto-zoom: {summary} → {auto_zooms_path.name}")
    return True


def _detect_freezes(video_path: Path, min_dead_s: float = 1.0,
                    noise_db: str = "-45dB") -> list[tuple[float, float]]:
    """Run ffmpeg freezedetect; return list of (start, end) freeze intervals.

    `noise_db` is freezedetect's `n` param (per-pixel diff tolerance — higher
    is more permissive). `-45dB` ≈ 0.5% pixel diff; catches Cowork's static
    chrome despite subtle cursor blinks etc. that defeat the default `-60dB`.

    If the video ends mid-freeze, the final interval is closed at video end.
    """
    duration = ffprobe_duration(video_path)
    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vf", f"freezedetect=n={noise_db}:d={min_dead_s}",
        "-an", "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    freezes: list[tuple[float, float]] = []
    start: float | None = None
    for line in result.stderr.splitlines():
        m_start = re.search(r"freeze_start:\s*([\d.]+)", line)
        m_end = re.search(r"freeze_end:\s*([\d.]+)", line)
        if m_start:
            start = float(m_start.group(1))
        elif m_end and start is not None:
            freezes.append((start, float(m_end.group(1))))
            start = None
    if start is not None:
        freezes.append((start, duration))
    return freezes


def cap_dead_times(video_path: Path,
                   max_dead_s: float = NEWS_MAX_DEAD_S,
                   protect_until_t: float = 0.0) -> tuple[float, float]:
    """News-pipeline hard rule: cap any freeze >max_dead_s after protect_until_t
    to max_dead_s. Modifies video in-place (re-encodes once).

    `protect_until_t` exempts the pre-tick region so prompt-typing pauses and
    intentional tick-montage holds aren't compressed. Typically passed as the
    end of the auto-zoom timeline (= source_t + duration of the last z0b).

    Returns (original_duration, new_duration). new == original if nothing
    needed capping.
    """
    original = ffprobe_duration(video_path)
    freezes = _detect_freezes(video_path, min_dead_s=max_dead_s)

    drops: list[tuple[float, float]] = []
    for f_start, f_end in freezes:
        if f_start < protect_until_t:
            continue
        if f_end - f_start > max_dead_s + 0.05:  # +50ms slack vs. detector jitter
            drops.append((f_start + max_dead_s, f_end))

    if not drops:
        return original, original

    # Build keep_ranges from drops
    keep_ranges: list[tuple[float, float]] = []
    cursor = 0.0
    for d_start, d_end in sorted(drops):
        if cursor < d_start:
            keep_ranges.append((cursor, d_start))
        cursor = d_end
    if cursor < original:
        keep_ranges.append((cursor, original))

    filter_graph = _build_filter_graph(keep_ranges)
    tmp = video_path.with_suffix(".capdead.mp4")
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-filter_complex", filter_graph,
        "-map", "[out]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        # Hard Rule #15: 60fps + 1s keyframes end-to-end. Without these
        # explicit flags ffmpeg uses its default 250-frame GOP (~4.17s gap
        # at 60fps), and since cap_dead_times is the LAST writer to
        # zoom.mp4 in the news pipeline it overrides zoom.py's correctly-
        # keyed segments. Caught by lint_news.py L03 (decisions/2026-06-14).
        "-g", "60", "-keyint_min", "60",
        "-pix_fmt", "yuv420p",
        str(tmp),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"[cap-dead] ⚠️  ffmpeg failed (rc={e.returncode}); leaving video unchanged\n"
              f"{e.stderr.decode(errors='replace')[-400:]}")
        return original, original

    tmp.replace(video_path)
    new_dur = ffprobe_duration(video_path)
    cuts_desc = ", ".join(f"{s:.2f}→{e:.2f}(-{e-s:.1f}s)" for s, e in drops)
    print(f"[cap-dead] capped {len(drops)} freeze(s) > {max_dead_s}s "
          f"after t={protect_until_t:.2f}s: {cuts_desc}")
    print(f"[cap-dead] {original:.2f}s → {new_dur:.2f}s (-{original-new_dur:.2f}s)")
    return original, new_dur


def main():
    ap = argparse.ArgumentParser(
        description="Tail-cut compression around progress-sidebar phase ticks."
    )
    ap.add_argument("input", type=Path, help="Input MP4 (typically *_scrubbed.mp4)")
    ap.add_argument("output", type=Path, help="Output MP4 (tick-cut)")
    ap.add_argument("--region-pct", default=DEFAULT_REGION_PCT,
                    help=f"Progress-sidebar region as 'x,y,w,h' percentages "
                         f"(default: {DEFAULT_REGION_PCT}).")
    ap.add_argument("--expected-ticks", type=int, default=DEFAULT_EXPECTED_TICKS,
                    help=f"Max number of tick peaks to detect "
                         f"(default: {DEFAULT_EXPECTED_TICKS}).")
    ap.add_argument("--tail-seconds", type=float, default=DEFAULT_TAIL_SECONDS,
                    help=f"Seconds to keep before/after each tick. Lower = "
                         f"faster tick montage (default: {DEFAULT_TAIL_SECONDS}, "
                         f"i.e. 1s per tick).")
    ap.add_argument("--pre-seconds", type=float, default=DEFAULT_PRE_SECONDS,
                    help=f"Max seconds of pre-tick intro (user typing) to keep. "
                         f"Set to a number to trim, or pass a negative value to "
                         f"keep the full pre (default: {DEFAULT_PRE_SECONDS}).")
    ap.add_argument("--post-seconds", type=float, default=-1.0,
                    help="Max seconds of post-tick segment (response + scroll) "
                         "to keep. Default: -1 = keep the FULL post (the meat).")
    args = ap.parse_args()
    pre = None if (args.pre_seconds is not None and args.pre_seconds < 0) else args.pre_seconds
    post = None if args.post_seconds < 0 else args.post_seconds
    ok = tick_cut(args.input, args.output,
                  region_pct=args.region_pct,
                  expected_ticks=args.expected_ticks,
                  tail_seconds=args.tail_seconds,
                  pre_seconds=pre,
                  post_seconds=post)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
