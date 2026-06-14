#!/usr/bin/env python3
"""static_gateway.py — Hard Rule #30 static-placeholder gateway probe.

Detects Cowork's Progress-sidebar UI mode during the loading window:
  - STATIC placeholder ("See task progress for longer tasks." graphic, zero
    pixel motion). 0 ticks detected. Applies the 3.0s flash pre-cut and
    signals downstream to skip z0b.
  - DYNAMIC checklist (numbered phases with status indicator transitions).
    N ticks detected. Returns without modifying the recording — caller
    proceeds with standard z0b + tick-cut / Variant B workflow.

Shared between news-pipeline (`news-pipeline/tools/process.py`) and
product-demo (Phase 3 dispatch in `.claude/skills/parallax-video/SKILL.md`)
so both pipelines pick up the same gateway logic.

CLI:
    python3 tools/static_gateway.py <recording> <manifest> [--in-place]
        [--probe-only] [--out-meta <path>]

    --in-place        : overwrite <recording> with the pre-cut version (only
                        when STATIC detected). Default: write to
                        <recording>.r30.mp4 alongside the input.
    --probe-only      : count ticks + report mode; do NOT modify recording.
    --out-meta <path> : write {"static_mode": bool, "applied": bool,
                        "tick_count": int, "loading_dwell_s": float} to JSON.

See decisions/2026-06-01-static-placeholder-gateway.md for full rationale.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent  # project_root/tools
DETECT_TICKS = THIS_DIR / "detect_ticks.py"

# Sidebar region the gateway probes (Cowork chrome default).
SIDEBAR_REGION_PCT = "80,0,20,30"
# Floor below which no compression is applied (loading is already tight enough).
LOADING_FLASH_FLOOR_S = 3.0
# How far past T_typing_end to start the flash slice (clears any in-flight
# submit-button cursor motion).
PRE_FLASH_OFFSET_S = 0.2
# Magnitude threshold separating real checkmark transitions from sidebar
# noise. Real ticks register ≥5.0 (N1 sample: 6.45–9.56). Noise/cursor flicker
# in the static-placeholder graphic stays under 2.0 (V3 sample: 0.06–1.07).
# 3.0 is the safe midpoint.
TICK_MAGNITUDE_THRESHOLD = 3.0
# How many peaks to probe before applying the threshold filter. 16 covers any
# real checklist length we've seen (N1 has 8 phases; longer briefs occasionally
# show 10-12) while staying cheap to evaluate.
PROBE_PEAK_COUNT = 16
# Rule #27 at-top hold inserted between warp end and natural continuation.
# Applies on static path too (extends Rule #27 to compose with Rule #30).
AT_TOP_HOLD_S = 2.0
# How much earlier than scroll_to_top_done to sample the at-top-prompt-visible
# frame (Rule #27 (b) cowork-UI-snap caveat — snap pushes prompt off-screen
# ~0.5-0.7s after scroll_to_top_done; sample before the snap fires).
AT_TOP_SAMPLE_BACKOFF_S = 0.5
# After the scroll-down completes, the raw recording often has 3-5s of fully
# static frame before capture.py stops recording. That's pure dead space —
# trim it. Buffer kept after detected freeze start so the closer VO and outro
# transition have breathing room.
TAIL_FREEZE_BUFFER_S = 1.0
# freezedetect noise threshold (matches scrub.py default).
FREEZEDETECT_NOISE_DB = "-45dB"
# Minimum freeze duration to consider as "static end" (don't trim mid-scroll pauses).
FREEZEDETECT_MIN_S = 1.0


def _read_manifest(manifest_path: Path) -> tuple[float, float, float | None] | None:
    """Return (T_typing_end, T_brief_landed, scroll_to_top_done) from manifest.
    scroll_to_top_done is optional (None if absent). Returns None on failure.
    """
    if not manifest_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    phases = manifest.get("phases", {})
    streaming_started = phases.get("streaming_started")
    streaming_ended = phases.get("streaming_ended")
    scroll_to_top_done = phases.get("scroll_to_top_done")
    if streaming_started is None or streaming_ended is None:
        return None
    try:
        sttd = float(scroll_to_top_done) if scroll_to_top_done is not None else None
        return float(streaming_started), float(streaming_ended), sttd
    except (TypeError, ValueError):
        return None


def _probe_tick_count(recording: Path, t0: float, t1: float) -> int | None:
    """Count REAL checkmark-transition ticks in [t0, t1] of the Progress sidebar.

    `detect_ticks.py` always returns up to `--expected-ticks` peaks regardless
    of magnitude — it picks the top-N pixel-diff peaks via NMS, even if the
    "top" peaks are just noise. To distinguish static-placeholder noise from
    real dynamic-checklist transitions we probe with a wide PROBE_PEAK_COUNT
    and then filter by TICK_MAGNITUDE_THRESHOLD. The threshold separates real
    UI transitions (N1 sample: 6-9) from sidebar noise / cursor flicker
    (V3 sample: <2). Returns the filtered count, or None on probe error.
    """
    probe_json = recording.with_suffix(".r30probe.json")
    try:
        subprocess.run([
            "python3", str(DETECT_TICKS),
            str(recording),
            "--time-range", f"{t0:.2f}:{t1:.2f}",
            "--region-pct", SIDEBAR_REGION_PCT,
            "--expected-ticks", str(PROBE_PEAK_COUNT),
            "--output", str(probe_json),
        ], check=True, capture_output=True)
        probe = json.loads(probe_json.read_text())
        ticks = probe.get("ticks", [])
        real_ticks = [t for t in ticks if t.get("magnitude", 0) >= TICK_MAGNITUDE_THRESHOLD]
        return len(real_ticks)
    except (subprocess.CalledProcessError, json.JSONDecodeError, OSError):
        return None
    finally:
        probe_json.unlink(missing_ok=True)


def _find_raw_source(recording: Path) -> Path | None:
    """Locate the raw.mp4 / vid<N>_raw.mp4 alongside the trimmed recording.
    Hard Rule #14 preserves raw for both pipelines. Returns None if not found.
    """
    slot_dir = recording.parent
    # News-pipeline convention: slot has both raw.mp4 + trimmed.mp4.
    raw_news = slot_dir / "raw.mp4"
    if raw_news.exists() and raw_news != recording:
        return raw_news
    # Product-demo convention: vid<N>.mp4 (trimmed) + vid<N>_raw.mp4 (raw).
    raw_pd = recording.with_name(recording.stem + "_raw" + recording.suffix)
    if raw_pd.exists():
        return raw_pd
    return None


def _apply_flash_precut(recording: Path,
                        T_typing_end: float,
                        T_brief_landed: float,
                        scroll_to_top_done: float | None,
                        out_path: Path) -> bool:
    """ffmpeg pre-cut: pre + 3.0s time-warped loading + post → out_path.

    The 'flash' is a 3.0s TIME-WARPED segment of the actual loading content
    (generation tokens streaming in + scroll-up animation), not a freeze on
    one frame. Viewer sees natural motion fast-forwarded: typing → submit →
    3s of rapid progress → at-top → natural smooth scroll-down.

    Implementation requires the raw recording (not the auto-trimmed one),
    because the auto-trim leaves a seam at T_brief_landed in trimmed.mp4 —
    splicing across the seam produces a jump cut from "chat at bottom of
    generated content" to "at-top frame after auto-scroll-up". The raw
    timeline is continuous through the scroll-up, so the warp + natural
    continuation flows without seams.

    If raw is unavailable, falls back to a static at-top hold (original
    behavior — has the seam but preserves the 3s compression goal).

    Returns True on success.
    """
    raw = _find_raw_source(recording)
    if raw is None:
        print(f"[rule-30] ⚠️ no raw source alongside {recording.name}; "
              f"falling back to static at-top hold (seam present)", file=sys.stderr)
        return _apply_static_hold_fallback(recording, T_typing_end,
                                           T_brief_landed, out_path)

    # In RAW timeline: warp ends at t_at_top_prompt_visible (Rule #27 (b)
    # cowork-snap-aware) — typically scroll_to_top_done − 0.5s. Sampling
    # AT scroll_to_top_done risks landing past the snap (prompt off-screen).
    pre_end = T_typing_end + PRE_FLASH_OFFSET_S
    warp_start = pre_end
    if scroll_to_top_done is not None:
        t_at_top_prompt_visible = scroll_to_top_done - AT_TOP_SAMPLE_BACKOFF_S
    else:
        # No scroll dance — fall back to T_brief_landed (no useful at-top moment).
        t_at_top_prompt_visible = T_brief_landed
    warp_end = t_at_top_prompt_visible
    warp_duration = warp_end - warp_start
    if warp_duration <= LOADING_FLASH_FLOOR_S:
        return _apply_static_hold_fallback(recording, T_typing_end,
                                           T_brief_landed, out_path)
    speedup = warp_duration / LOADING_FLASH_FLOOR_S
    # Post-hold continuation starts a tiny offset past the freeze sample so
    # natural raw motion picks up cleanly (Rule #27 (c) — natural continuation
    # from the same T_at_top the freeze was sampled at).
    post_start = t_at_top_prompt_visible + 0.05

    tmp_pre = recording.with_suffix(".r30pre.mp4")
    tmp_warp_src = recording.with_suffix(".r30wsrc.mp4")
    tmp_warp = recording.with_suffix(".r30warp.mp4")
    tmp_at_top_slice = recording.with_suffix(".r30atslice.mp4")
    tmp_at_top_hold = recording.with_suffix(".r30athold.mp4")
    tmp_post = recording.with_suffix(".r30post.mp4")
    tmp_concat = recording.with_suffix(".r30concat.txt")
    print(f"[rule-30] time-warp: raw[{warp_start:.2f}, {warp_end:.2f}] "
          f"({warp_duration:.2f}s) → 3.0s @ {speedup:.2f}×")
    print(f"[rule-30] + Rule #27 at-top hold: {AT_TOP_HOLD_S}s freeze of "
          f"raw[{t_at_top_prompt_visible:.2f}] before scroll-down")
    try:
        for cmd in [
            # pre: typing + submit
            ["ffmpeg", "-y", "-i", str(raw), "-t", f"{pre_end:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_pre)],
            # warp source: extract the loading + scroll-up window from raw
            ["ffmpeg", "-y", "-ss", f"{warp_start:.3f}", "-i", str(raw),
             "-t", f"{warp_duration:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_warp_src)],
            # warp: setpts compresses timestamps, fps=60 resamples to 60fps
            ["ffmpeg", "-y", "-i", str(tmp_warp_src),
             "-vf", f"setpts=PTS/{speedup:.4f},fps=60",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-an", str(tmp_warp)],
            # at-top slice: 50ms slice of the at-top-prompt-visible frame
            ["ffmpeg", "-y", "-ss", f"{t_at_top_prompt_visible:.3f}",
             "-i", str(raw), "-t", "0.05",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_at_top_slice)],
            # at-top hold: 2s freeze (tpad clone)
            ["ffmpeg", "-y", "-i", str(tmp_at_top_slice),
             "-vf", f"tpad=stop_mode=clone:stop_duration={AT_TOP_HOLD_S - 0.05:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_at_top_hold)],
            # post: natural raw continuation (snap + scroll-down + outro)
            ["ffmpeg", "-y", "-ss", f"{post_start:.3f}", "-i", str(raw),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_post)],
        ]:
            subprocess.run(cmd, check=True, capture_output=True)
        tmp_concat.write_text(
            f"file '{tmp_pre}'\nfile '{tmp_warp}'\nfile '{tmp_at_top_hold}'\nfile '{tmp_post}'\n"
        )
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp_concat),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", "60", "-an", str(out_path),
        ], check=True, capture_output=True)
        # Trim post-natural-continuation dead frame. Skip past the intentional
        # at-top hold (it's a freeze too, but on-purpose); scan only the
        # natural raw continuation.
        scan_from = pre_end + LOADING_FLASH_FLOOR_S + AT_TOP_HOLD_S + 0.5
        _trim_static_tail(out_path, scan_from)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[rule-30] ⚠️ time-warp failed (rc={e.returncode})", file=sys.stderr)
        return False
    finally:
        for f in [tmp_pre, tmp_warp_src, tmp_warp, tmp_at_top_slice,
                  tmp_at_top_hold, tmp_post, tmp_concat]:
            f.unlink(missing_ok=True)


def _trim_static_tail(recording: Path, scan_from: float = 0.0) -> None:
    """Detect static-frame freeze in `recording[scan_from, end]` via ffmpeg
    freezedetect and trim it to scan_from + TAIL_FREEZE_BUFFER_S past the
    detected freeze start. Operates in-place. No-op if no freeze ≥
    FREEZEDETECT_MIN_S found (recording naturally ends with motion).

    `scan_from` lets the caller skip intentional freezes earlier in the
    recording (e.g. Rule #27 at-top hold). Pass the timestamp where the
    natural continuation begins.
    """
    try:
        # Scan only the post-scan_from segment. -ss before -i is fast-seek.
        result = subprocess.run(
            ["ffmpeg", "-ss", f"{scan_from:.3f}", "-i", str(recording), "-vf",
             f"freezedetect=n={FREEZEDETECT_NOISE_DB}:d={FREEZEDETECT_MIN_S}",
             "-map", "0:v:0", "-f", "null", "-"],
            capture_output=True, text=True, check=False,
        )
        stderr = result.stderr

        # freezedetect timestamps are relative to the seeked input — add scan_from.
        freeze_start_rel = None
        for line in stderr.splitlines():
            if "freeze_start:" in line:
                try:
                    freeze_start_rel = float(
                        line.split("freeze_start:")[1].strip().split()[0]
                    )
                    break
                except (ValueError, IndexError):
                    continue
        if freeze_start_rel is None:
            return  # no qualifying freeze
        freeze_start = scan_from + freeze_start_rel

        dur_result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(recording)],
            capture_output=True, text=True, check=True,
        )
        duration = float(dur_result.stdout.strip())
        trim_end = freeze_start + TAIL_FREEZE_BUFFER_S
        if trim_end >= duration - 0.1:
            return  # would be a no-op trim

        print(f"[rule-30] tail trim: scroll-end freeze at {freeze_start:.2f}s "
              f"(scan from {scan_from:.2f}s), trimming to {trim_end:.2f}s "
              f"({duration - trim_end:.2f}s of static cut)")
        tmp_trim = recording.with_suffix(".r30trim.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", str(recording), "-t", f"{trim_end:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_trim),
        ], check=True, capture_output=True)
        tmp_trim.replace(recording)
    except (subprocess.CalledProcessError, ValueError, OSError) as e:
        print(f"[rule-30] ⚠️ tail-trim failed ({type(e).__name__}); leaving recording untrimmed",
              file=sys.stderr)


def _apply_static_hold_fallback(recording: Path,
                                T_typing_end: float,
                                T_brief_landed: float,
                                out_path: Path) -> bool:
    """Fallback: 3s static hold on at-top frame (used when raw is unavailable).
    Has a visible seam between typing-end frame and at-top frame.
    """
    pre_end = T_typing_end + PRE_FLASH_OFFSET_S
    hold_sample_t = T_brief_landed + 0.1
    tmp_pre = recording.with_suffix(".r30pre.mp4")
    tmp_slice = recording.with_suffix(".r30slice.mp4")
    tmp_hold = recording.with_suffix(".r30hold.mp4")
    tmp_post = recording.with_suffix(".r30post.mp4")
    tmp_concat = recording.with_suffix(".r30concat.txt")
    try:
        for cmd in [
            ["ffmpeg", "-y", "-i", str(recording), "-t", f"{pre_end:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_pre)],
            ["ffmpeg", "-y", "-ss", f"{hold_sample_t:.3f}", "-i", str(recording),
             "-t", "0.05",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_slice)],
            ["ffmpeg", "-y", "-i", str(tmp_slice),
             "-vf", f"tpad=stop_mode=clone:stop_duration={LOADING_FLASH_FLOOR_S - 0.05:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_hold)],
            ["ffmpeg", "-y", "-ss", f"{hold_sample_t + 0.05:.3f}", "-i", str(recording),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_post)],
        ]:
            subprocess.run(cmd, check=True, capture_output=True)
        tmp_concat.write_text(
            f"file '{tmp_pre}'\nfile '{tmp_hold}'\nfile '{tmp_post}'\n"
        )
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp_concat),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", "60", "-an", str(out_path),
        ], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[rule-30] ⚠️ fallback failed (rc={e.returncode})", file=sys.stderr)
        return False
    finally:
        for f in [tmp_pre, tmp_slice, tmp_hold, tmp_post, tmp_concat]:
            f.unlink(missing_ok=True)


def run_gateway(recording: Path, manifest: Path,
                in_place: bool = False,
                probe_only: bool = False) -> dict:
    """Run the Hard Rule #30 gateway probe + optional pre-cut.

    Returns a dict:
      {"static_mode": bool, "applied": bool, "tick_count": int | None,
       "loading_dwell_s": float | None, "output_path": str | None}
    """
    result = {
        "static_mode": False,
        "applied": False,
        "tick_count": None,
        "loading_dwell_s": None,
        "output_path": None,
    }
    times = _read_manifest(manifest)
    if times is None:
        print(f"[rule-30] manifest missing or unreadable; defaulting to dynamic path")
        return result
    T_typing_end, T_brief_landed, scroll_to_top_done = times
    loading_dwell = T_brief_landed - T_typing_end
    result["loading_dwell_s"] = round(loading_dwell, 3)
    if loading_dwell <= LOADING_FLASH_FLOOR_S:
        print(f"[rule-30] loading_dwell {loading_dwell:.2f}s ≤ {LOADING_FLASH_FLOOR_S}s floor; "
              f"no compression needed")
        return result

    tick_count = _probe_tick_count(recording, T_typing_end, T_brief_landed)
    result["tick_count"] = tick_count
    if tick_count is None:
        print(f"[rule-30] probe errored; defaulting to dynamic path "
              f"(safer than silent content loss)")
        return result
    if tick_count > 0:
        print(f"[rule-30] DYNAMIC checklist ({tick_count} ticks in "
              f"[{T_typing_end:.1f}s, {T_brief_landed:.1f}s]) — standard z0b + tick-cut")
        return result

    result["static_mode"] = True
    print(f"[rule-30] STATIC placeholder (0 ticks in "
          f"[{T_typing_end:.1f}s, {T_brief_landed:.1f}s], "
          f"loading_dwell={loading_dwell:.1f}s) — z0b should be skipped downstream")

    if probe_only:
        return result

    out_path = recording if in_place else recording.with_suffix(".r30.mp4")
    if in_place:
        tmp_out = recording.with_suffix(".r30tmp.mp4")
        ok = _apply_flash_precut(recording, T_typing_end, T_brief_landed,
                                 scroll_to_top_done, tmp_out)
        if ok:
            tmp_out.replace(recording)
            result["applied"] = True
            result["output_path"] = str(recording)
            print(f"[rule-30] ✓ pre-cut applied in-place "
                  f"({loading_dwell:.1f}s loading → 3.0s flash) → {recording.name}")
        else:
            tmp_out.unlink(missing_ok=True)
    else:
        ok = _apply_flash_precut(recording, T_typing_end, T_brief_landed,
                                 scroll_to_top_done, out_path)
        if ok:
            result["applied"] = True
            result["output_path"] = str(out_path)
            print(f"[rule-30] ✓ pre-cut written ({loading_dwell:.1f}s → 3.0s) → {out_path.name}")
    return result


def main():
    ap = argparse.ArgumentParser(
        description="Hard Rule #30 static-placeholder gateway (probe + optional pre-cut).",
    )
    ap.add_argument("recording", type=Path,
                    help="Path to the recording (trimmed.mp4 or vid<N>.mp4).")
    ap.add_argument("manifest", type=Path,
                    help="Path to the capture manifest.json with phases.streaming_started/_ended.")
    ap.add_argument("--in-place", action="store_true",
                    help="Overwrite <recording> with the pre-cut output. "
                         "Default: write alongside as <recording>.r30.mp4.")
    ap.add_argument("--probe-only", action="store_true",
                    help="Report mode + tick count; do not modify the recording.")
    ap.add_argument("--out-meta", type=Path, default=None,
                    help="If set, write the gateway result dict to this JSON path.")
    args = ap.parse_args()

    if not args.recording.exists():
        sys.exit(f"❌ recording not found: {args.recording}")
    if not DETECT_TICKS.exists():
        sys.exit(f"❌ detect_ticks.py not found at {DETECT_TICKS}")

    result = run_gateway(args.recording.resolve(), args.manifest.resolve(),
                         in_place=args.in_place, probe_only=args.probe_only)
    if args.out_meta:
        args.out_meta.write_text(json.dumps(result, indent=2))
        print(f"[rule-30] meta → {args.out_meta}")
    # Exit code: 0 if probe succeeded (regardless of path), 1 if probe errored
    # (caller can treat as dynamic-path fallback either way).
    sys.exit(0 if result["tick_count"] is not None else 1)


if __name__ == "__main__":
    main()
