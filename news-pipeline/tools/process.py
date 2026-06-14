#!/usr/bin/env python3
"""process.py — post-capture: scrub + optional zoom on a news-pipeline slot.

Pipeline:
    trimmed.mp4 (from capture.py — preserved, never overwritten)
       │  python tools/scrub.py  (frame-diff dead-time scrub; -45dB default,
       │                          tuned in the main pipeline for Cowork chrome)
       ▼
    trimmed_scrubbed.mp4 (intermediate — deleted if zoom succeeds; renamed
                          to zoom.mp4 otherwise so the final filename is stable)
       │  python tools/zoom.py  (only if recordings/N<N>/zooms.json exists)
       ▼
    zoom.mp4 (final processed output; the deliverable)

Auto-runs at the end of capture.py via process_slot(). Also invokable
standalone to re-process an existing slot (no re-record needed — edit
zooms.json then re-run):

    python3 news-pipeline/tools/process.py N7
    python3 news-pipeline/tools/process.py news-pipeline/recordings/N7
    python3 news-pipeline/tools/process.py N7 --scrub-arg=--diff-threshold=-50dB

Failures are non-fatal: if scrub fails, trimmed.mp4 remains. If zoom fails,
the scrubbed result is renamed to zoom.mp4 so there's always a 'final' file.

Reuses the main pipeline's tools (project_root/tools/scrub.py and
project_root/tools/zoom.py) via subprocess — no imports, no shared state, so
the news-pipeline still teardown-cleanly with a rm -rf news-pipeline/.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

NEWS_PIPELINE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = NEWS_PIPELINE_ROOT.parent
MAIN_TOOLS = PROJECT_ROOT / "tools"

# Rule N2 (news-pipeline/README.md): the prompt-typing window must be sped up,
# not cut. We derive the window end from manifest.phases.streaming_started and
# shave a small safety margin so the forced-speedup range doesn't bleed into
# the first frame of Cowork's response.
TYPING_END_SAFETY_SHAVE_S = 0.5
TYPING_SPEEDUP_FACTOR = 2.0


def resolve_slot(arg: str) -> Path:
    """Accept 'N<num>' or a path to a slot directory."""
    p = Path(arg)
    if p.is_dir():
        return p.resolve()
    if re.match(r"^N\d+$", arg):
        candidate = NEWS_PIPELINE_ROOT / "recordings" / arg
        if candidate.is_dir():
            return candidate.resolve()
    sys.exit(f"❌ slot not found: {arg}")


def _derive_typing_force_range(slot_dir: Path,
                               scrub_extra: list[str] | None,
                               enabled: bool) -> tuple[str | None, bool, float | None]:
    """Derive the rule-N2 --force-speed-range value from the slot's manifest.

    Returns (force_range_str | None, buffer_compressed: bool,
             preserve_end_scrubbed: float | None).
    - force_range_str: comma-separated ranges for --force-speed-range, or None.
    - buffer_compressed: True if the buffer-1 region was force-compressed to a
      deterministic 3.0s (Rule #31 mech 2).
    - preserve_end_scrubbed: scrubbed-time position where the at-1× tick
      montage region ends and post-brief content begins. Used by tick_cut as
      scan_end_s so detect_ticks doesn't surface post-brief scroll peaks.
      None if tick montage detection didn't fire.
    """
    if not enabled:
        return (None, False, None)
    # Defer to user override.
    if any("--force-speed-range" in (a or "") for a in (scrub_extra or [])):
        print("[process] rule N2: user passed --force-speed-range; honoring "
              "their value (auto-derivation skipped)")
        return (None, False, None)
    manifest_path = slot_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"[process] ⚠️ rule N2: {manifest_path.name} missing; can't derive "
              f"typing window — scrub will use default treatment (may cut typing)")
        return (None, False, None)
    try:
        manifest = json.loads(manifest_path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"[process] ⚠️ rule N2: {manifest_path.name} unreadable "
              f"({type(e).__name__}); skipping auto force-range")
        return (None, False, None)
    t = manifest.get("phases", {}).get("streaming_started")
    if t is None:
        # Older recordings (pre-2026-05-29 capture.py) won't have this key.
        print(f"[process] ⚠️ rule N2: phases.streaming_started missing from manifest "
              f"(likely a pre-N2 recording); scrub will use default treatment")
        return (None, False, None)
    try:
        t_float = float(t)
    except (TypeError, ValueError):
        print(f"[process] ⚠️ rule N2: streaming_started={t!r} not a number; skipping")
        return (None, False, None)
    X = max(0.0, t_float - TYPING_END_SAFETY_SHAVE_S)
    if X <= 0.05:
        # Too small to matter — typing was instant or the safety shave ate the window.
        return (None, False, None)
    print(f"[process] rule N2: forcing typing window [0, {X:.2f}s] at "
          f"{TYPING_SPEEDUP_FACTOR}× (streaming_started={t_float:.2f}s)")
    ranges = [f"0:{X:.2f}:{TYPING_SPEEDUP_FACTOR}"]
    buffer_compressed = False

    # Also force tick-montage region to 1× (preserve at natural pace) so
    # detect_ticks downstream can find each tick clearly. Without this,
    # scrub.py's frame-diff compression smushes ticks together in the
    # scrubbed file and individual tick visibility is lost.
    streaming_ended = manifest.get("phases", {}).get("streaming_ended")
    if streaming_ended is not None:
        try:
            t_end_float = float(streaming_ended)
            tick_montage = _detect_raw_tick_montage(slot_dir, t_float, t_end_float)
            if tick_montage is not None:
                m_start, m_end = tick_montage
                # Buffer-1 speedup: force the [streaming_started, preserve_start]
                # region in raw to compress to exactly target_buffer_s = 3.0s
                # (= 2 × ease) in scrubbed. This makes first_tick land at
                # typing_end_scrubbed + 3.0s, which is precisely z0b's ease-in
                # completion. Replaces the old _compress_pre_tick_buffer probe
                # that struggled to find weak early ticks via detect_ticks.
                target_buffer_s = 3.0
                buffer_raw_dur = m_start - t_float
                if buffer_raw_dur > target_buffer_s + 0.2:
                    buffer_speedup = buffer_raw_dur / target_buffer_s
                    print(f"[process] rule #31 buffer-compress: forcing raw[{t_float:.2f}, "
                          f"{m_start:.2f}] ({buffer_raw_dur:.2f}s) at {buffer_speedup:.2f}× → "
                          f"{target_buffer_s}s scrubbed (first_tick lands at "
                          f"typing_end + {target_buffer_s}s = z0b ease-in completion)")
                    ranges.append(f"{t_float:.2f}:{m_start:.2f}:{buffer_speedup:.2f}")
                    buffer_compressed = True
                print(f"[process] rule #31 tick-preserve: forcing raw[{m_start:.2f}, "
                      f"{m_end:.2f}] at 1× (tick montage region preserved at "
                      f"natural pace so each tick is individually visible)")
                ranges.append(f"{m_start:.2f}:{m_end:.2f}:1.0")
                # Compute preserve_end in scrubbed coords for downstream
                # tick_cut to use as scan_end_s. Mapping:
                #   typing zone:  raw [0, streaming_started] → scrubbed [0, typing_end_scrubbed]
                #   buffer-1:     raw [streaming_started, m_start] → scrubbed [typing_end_scrubbed, +target_buffer_s]
                #   tick montage: raw [m_start, m_end] @ 1× → scrubbed [preserve_start, +(m_end-m_start)]
                typing_end_scrubbed = t_float / TYPING_SPEEDUP_FACTOR
                preserve_start_scrubbed = typing_end_scrubbed + (
                    target_buffer_s if buffer_compressed else (m_start - t_float)
                )
                preserve_end_scrubbed = preserve_start_scrubbed + (m_end - m_start)
                return (",".join(ranges), buffer_compressed, preserve_end_scrubbed)
        except (TypeError, ValueError):
            pass

    return (",".join(ranges), buffer_compressed, None)


def _detect_raw_tick_montage(slot_dir: Path, t_typing_end_raw: float,
                              t_streaming_end_raw: float,
                              region_pct: str = "80,0,20,30",
                              magnitude_threshold: float = 3.0,
                              tail_seconds: float = 1.0) -> tuple[float, float] | None:
    """Detect tick positions in trimmed.mp4 (raw timing, BEFORE scrub) and
    return the tick montage range [first_tick - tail, last_tick + tail].

    Rule #31 mechanism support: by detecting ticks at their raw positions
    (where they're well-separated by Cowork's natural pacing), we can tell
    scrub.py to preserve this range at 1× speed via --force-speed-range.
    The result: after scrub, each tick is individually visible with the V1
    ±1s buffer, instead of being smushed by frame-diff compression.

    Returns None if no real ticks found.
    """
    trimmed = slot_dir / "trimmed.mp4"
    if not trimmed.exists():
        return None
    ticks_json_tmp = slot_dir / "_raw_tick_montage_probe.json"
    try:
        subprocess.run([
            "python3", str(MAIN_TOOLS / "detect_ticks.py"),
            str(trimmed),
            "--time-range", f"{t_typing_end_raw:.3f}:{t_streaming_end_raw:.3f}",
            "--region-pct", region_pct,
            "--expected-ticks", "20",
            "--margin", "0.5",
            "--output", str(ticks_json_tmp),
        ], check=True, capture_output=True, cwd=str(PROJECT_ROOT))
    except subprocess.CalledProcessError:
        return None
    if not ticks_json_tmp.exists():
        return None
    try:
        data = json.loads(ticks_json_tmp.read_text())
    finally:
        ticks_json_tmp.unlink(missing_ok=True)
    # Filter to real ticks: mag ≥ threshold, exclude brief-landed (mag ≥ 100).
    # In raw timing brief-landed comes at the END of streaming, so we also
    # need its position to bound the montage.
    real_ticks = [t for t in data.get("ticks", [])
                  if magnitude_threshold <= t.get("magnitude", 0) < 100.0]
    if not real_ticks:
        return None
    tick_times = sorted(t["t_tick"] for t in real_ticks)
    first_tick = tick_times[0]
    last_tick = tick_times[-1]
    m_start = max(t_typing_end_raw, first_tick - tail_seconds)
    m_end = min(t_streaming_end_raw, last_tick + tail_seconds)
    if m_end - m_start < 0.5:
        return None
    print(f"[process] detected {len(tick_times)} raw ticks in trimmed.mp4: "
          f"first={first_tick:.2f}s, last={last_tick:.2f}s")
    return (m_start, m_end)


def _compress_pre_tick_buffer(slot_dir: Path, scrubbed: Path,
                              ease_s: float = 1.5,
                              magnitude_threshold: float = 3.0) -> bool:
    """Rule #31 mechanism 2: cut pre-first-tick dead time in scrubbed.mp4 so
    first_tick lands exactly at z0b's ease-in completion.

    Rule #31 has two mechanisms together — (1) the no-gap continuous z0→z0b
    camera transition (handled by tick_cut + Rule #22 override), and (2) this
    source cut. Without (2), mechanism (1) lands the camera on an empty
    sidebar that's still waiting for tools to fire. With (2), the camera
    arrival and first checkmark are the SAME visual moment.

    Target:
        first_tick_scrubbed = typing_end_scrubbed + 2 * ease
                            = typing_end + 3.0s   (with default ease=1.5)
    which is precisely when z0b's ease-in completes (camera fully on sidebar).

    Implementation:
    1. Read typing_end_scrubbed from manifest (= streaming_started / 2x speedup).
    2. Probe scrubbed[typing_end, typing_end+30] via detect_ticks.py.
    3. Filter peaks by magnitude_threshold (≥10 = real checkmark, <10 = noise
       like cursor blink or tool-call animations).
    4. first_tick = lowest-t qualifying peak.
    5. If buffer-1 = first_tick - typing_end > target (2*ease), trim
       [typing_end + 0.2s, first_tick - (target - 0.2)] from scrubbed.mp4
       via ffmpeg trim+concat. Post-trim: first_tick lands at target.

    Returns True if a cut was applied; False on no-op or failure. Operates
    in-place on scrubbed.mp4. No-op when:
      - manifest missing or streaming_started absent
      - detect_ticks finds no ticks ≥ magnitude_threshold in buffer-1 region
      - buffer-1 already ≤ target
    """
    target_buffer_s = 2.0 * ease_s  # 3.0s with default ease

    manifest_path = slot_dir / "manifest.json"
    if not manifest_path.exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    streaming_started = manifest.get("phases", {}).get("streaming_started")
    if streaming_started is None:
        return False
    typing_end_scrubbed = float(streaming_started) / TYPING_SPEEDUP_FACTOR

    try:
        scrubbed_dur = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(scrubbed)],
            capture_output=True, text=True, check=True,
        ).stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return False

    # Scan the entire post-typing region — buffer-1 can be 40+ seconds for
    # tool-heavy queries (N2's 6-bank analysis sets up 12+ tools before any
    # checkmarks fire). A narrower window risks missing first_tick entirely
    # and producing a no-op when a cut is actually needed.
    scan_start = typing_end_scrubbed
    scan_end = scrubbed_dur
    if scan_end - scan_start < 1.0:
        return False  # not enough region to scan

    ticks_json_tmp = slot_dir / "_buffer1_probe.json"
    try:
        subprocess.run([
            "python3", str(MAIN_TOOLS / "detect_ticks.py"),
            str(scrubbed),
            "--time-range", f"{scan_start:.3f}:{scan_end:.3f}",
            "--region-pct", "80,0,20,30",
            # Higher expected-ticks than typical 5-8 checklist ticks because
            # the scrubbed file's post-typing region also includes the
            # brief-landed snap (very high magnitude) + outro + scroll
            # animations. We need detect_ticks to surface all real ticks +
            # post-tick events so we can pick the LOWEST-t (= first real tick).
            "--expected-ticks", "20",
            "--margin", "0.5",
            "--output", str(ticks_json_tmp),
        ], check=True, capture_output=True, cwd=str(PROJECT_ROOT))
    except subprocess.CalledProcessError as e:
        print(f"[process] ⚠️ rule #31 buffer-cut: detect_ticks failed "
              f"(rc={e.returncode}); skipping")
        return False

    if not ticks_json_tmp.exists():
        return False
    try:
        ticks_data = json.loads(ticks_json_tmp.read_text())
    finally:
        ticks_json_tmp.unlink(missing_ok=True)

    real_ticks = [t for t in ticks_data.get("ticks", [])
                  if t.get("magnitude", 0) >= magnitude_threshold]
    if not real_ticks:
        print(f"[process] rule #31 buffer-cut: no ticks ≥{magnitude_threshold} "
              f"magnitude in [{scan_start:.2f}, {scan_end:.2f}]; no cut")
        return False

    first_tick_scrubbed = min(t["t_tick"] for t in real_ticks)
    actual_buffer = first_tick_scrubbed - typing_end_scrubbed

    if actual_buffer <= target_buffer_s:
        print(f"[process] rule #31 buffer-cut: buffer-1 = {actual_buffer:.2f}s "
              f"already ≤ {target_buffer_s:.1f}s target; no cut")
        return False

    cut_start = typing_end_scrubbed + 0.2
    cut_end = first_tick_scrubbed - (target_buffer_s - 0.2)
    cut_duration = cut_end - cut_start

    print(f"\n[process] rule #31 buffer-cut: first_tick={first_tick_scrubbed:.2f}s, "
          f"buffer-1={actual_buffer:.2f}s → {target_buffer_s:.1f}s target")
    print(f"[process] rule #31 buffer-cut: trimming scrubbed[{cut_start:.2f}, "
          f"{cut_end:.2f}] ({cut_duration:.2f}s removed)")

    tmp_pre = scrubbed.with_suffix(".pretick_pre.mp4")
    tmp_post = scrubbed.with_suffix(".pretick_post.mp4")
    tmp_concat = scrubbed.with_suffix(".pretick_concat.txt")
    tmp_out = scrubbed.with_suffix(".pretick.mp4")
    try:
        for cmd in [
            ["ffmpeg", "-y", "-i", str(scrubbed), "-t", f"{cut_start:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_pre)],
            ["ffmpeg", "-y", "-ss", f"{cut_end:.3f}", "-i", str(scrubbed),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_post)],
        ]:
            subprocess.run(cmd, check=True, capture_output=True)
        tmp_concat.write_text(f"file '{tmp_pre}'\nfile '{tmp_post}'\n")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp_concat),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_out),
        ], check=True, capture_output=True)
        tmp_out.replace(scrubbed)
        new_dur = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(scrubbed)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        print(f"[process] rule #31 buffer-cut: ✓ scrubbed now {new_dur}s "
              f"(first_tick now at ≈{typing_end_scrubbed + target_buffer_s:.2f}s)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[process] ⚠️ rule #31 buffer-cut failed (rc={e.returncode}); "
              f"leaving scrubbed.mp4 unmodified")
        return False
    finally:
        for f in [tmp_pre, tmp_post, tmp_concat]:
            f.unlink(missing_ok=True)


def _rule_22_override_auto_zooms(slot_dir: Path, auto_zooms_json: Path,
                                  ticks_json: Path | None = None,
                                  brief_landed_threshold: float = 100.0,
                                  real_tick_min_mag: float = 5.0,
                                  z0b_held_buffer_s: float = 1.0) -> None:
    """Override tick_cut's auto-emitted z0/z0b to comply with Rule #22 + #31.

    Three rewrites:
    1. z0.duration = typing_end_scrubbed + ease  (Rule #22 — ease-out at click)
    2. z0b.source_t = z0.duration  (Rule #31 mechanism 1 — no full-frame gap)
    3. z0b.duration sized so ease-out completes at last_real_tick + held_buffer.
       Camera retracts shortly after the last visible checkmark tick — BEFORE
       Cowork's auto-scroll-through-brief animation starts. Brief-landing
       happens during the ease-out (Rule #29 covers source with a frozen
       at-top frame), so the viewer never sees Cowork's auto-scroll-through.
       After ease-out + tpad, raw_tail plays — which is capture.py's explicit
       smooth_scroll_chat + smooth_scroll_doc sequence (the read-through the
       viewer is meant to see).

    "Real tick" identification:
    - magnitude ∈ [real_tick_min_mag, brief_landed_threshold) — excludes noise
      below 5 (cursor blinks, sub-pixel animations) and the brief-landed snap
      above 100 (much larger pixel change than any checkmark tick).
    - t > typing_end_scrubbed — excludes typing-zone false positives.
    - t < brief_landed_t (if brief_landed peak detected) — excludes post-brief
      scroll content which can register at mag 20-40.

    Fallback if no real ticks found: fixed z0b.duration = 2 × ease + held_buffer
    (= 4.0s with defaults). Camera still moves to sidebar briefly, no anchor.

    Operates on auto_zooms.json in-place. No-op if manifest missing.
    """
    if not auto_zooms_json.exists():
        return
    manifest_path = slot_dir / "manifest.json"
    if not manifest_path.exists():
        return
    try:
        manifest = json.loads(manifest_path.read_text())
        streaming_started = manifest.get("phases", {}).get("streaming_started")
        if streaming_started is None:
            return
        typing_end_scrubbed = float(streaming_started) / TYPING_SPEEDUP_FACTOR
        zooms = json.loads(auto_zooms_json.read_text())
        if not isinstance(zooms, list) or len(zooms) < 2:
            return
        z0, z0b = zooms[0], zooms[1]
        ease = float(z0.get("ease", 1.5))
        old_z0_duration = float(z0["duration"])
        old_z0b_source_t = float(z0b["source_t"])
        old_z0b_duration = float(z0b["duration"])

        new_z0_duration = round(typing_end_scrubbed + ease, 3)
        new_z0b_source_t = new_z0_duration  # No gap — sidebar is the focus

        # tick_cut now filters real ticks by magnitude (3-100) before
        # building keep_ranges, so its emitted z0b end position correctly
        # spans only the real tick montage (excludes brief-landed + scroll
        # peaks). Just preserve that emitted end position.
        old_z0b_end = old_z0b_source_t + old_z0b_duration
        new_z0b_duration = round(old_z0b_end - new_z0b_source_t, 3)
        sizing_note = (f"preserved tick_cut's z0b end "
                       f"({old_z0b_source_t:.2f}+{old_z0b_duration:.2f}={old_z0b_end:.2f}s)")

        if new_z0b_duration < 2 * ease:
            # Ensure at least the two eases meet.
            new_z0b_duration = round(2.0 * ease, 3)
            sizing_note += f" → bumped to {new_z0b_duration:.2f}s (2×ease floor)"

        z0["duration"] = new_z0_duration
        z0b["source_t"] = new_z0b_source_t
        z0b["duration"] = new_z0b_duration
        auto_zooms_json.write_text(json.dumps(zooms, indent=2))
        print(f"[process] rule 22 override: z0 dur {old_z0_duration:.2f}→{new_z0_duration:.2f}s "
              f"(ease-out at typing-end), z0b [{new_z0b_source_t:.2f}, "
              f"{new_z0b_source_t + new_z0b_duration:.2f}]s — {sizing_note}")
    except (json.JSONDecodeError, OSError, KeyError, TypeError, ValueError) as e:
        print(f"[process] ⚠️ rule 22 override failed ({type(e).__name__}); "
              f"keeping tick_cut's auto-emit")


def _rule_29_rebuild(slot_dir: Path,
                     intermediate: Path,
                     zooms_json_path: Path) -> bool:
    """Hard Rule #29: rebuild intermediate so z0b's ease-out plays over a
    frozen at-top frame AND the post-freeze segment stitches raw[T_at_top + 50ms, end].

    Replaces source content at [T_z0b_ease_out_start_src, end_of_intermediate]
    with: 50ms slice of raw[T_at_top_prompt_visible] + tpad clone for
    (z0b.ease + 2.0 − 0.05)s + raw[T_at_top_prompt_visible + 0.05, end_of_raw].

    Returns True if rebuild applied; False if a no-op condition fired.
    See decisions/2026-05-31-zoom-out-over-still-and-raw-tail-stitch.md.
    """
    raw = slot_dir / "raw.mp4"
    manifest_path = slot_dir / "manifest.json"
    if not manifest_path.exists():
        return False
    if not raw.exists():
        print(f"[process] rule 29: raw.mp4 missing in {slot_dir.name}; skipping rebuild "
              f"(Hard Rule #14 violation — can't stitch raw-tail)")
        return False
    try:
        manifest = json.loads(manifest_path.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    scroll_to_top_done = manifest.get("phases", {}).get("scroll_to_top_done")
    if scroll_to_top_done is None:
        return False
    try:
        zooms = json.loads(zooms_json_path.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    # Find z0b — first follow-mode directive on the Progress sidebar region.
    # Auto-emitted layout: zooms[1] = z0b. User-authored: scan for region_pct[80,0,20,30].
    z0b = None
    for z in zooms if isinstance(zooms, list) else []:
        if z.get("mode") == "follow" and z.get("region_pct") == [80, 0, 20, 30]:
            z0b = z
            break
    if z0b is None:
        return False
    try:
        z0b_source_t = float(z0b["source_t"])
        z0b_duration = float(z0b["duration"])
        z0b_ease = float(z0b["ease"])
    except (KeyError, TypeError, ValueError):
        return False

    T_ease_out_start = z0b_source_t + z0b_duration - z0b_ease
    T_at_top = max(0.0, float(scroll_to_top_done) - 0.5)  # Rule #27 (b) snap caveat
    # Rule #29 tpad provides 1.0s of the Rule #27 ≥2.0s hold (ease covers the
    # ease-out, +1.0s held after). Raw natural hold (capture.py) provides the
    # other 1.0s. Together = 2.0s total still frame after ease-out done.
    RULE_29_HOLD_S = 1.0
    RULE_27_NATURAL_HOLD_S = 1.0
    freeze_duration = z0b_ease + RULE_29_HOLD_S

    # Normalize raw natural hold to RULE_27_NATURAL_HOLD_S regardless of what
    # capture.py recorded. Use smooth_scroll_chat_start as the end-of-hold anchor.
    smooth_scroll_chat_start = manifest.get("phases", {}).get("smooth_scroll_chat_start")
    if smooth_scroll_chat_start is not None:
        T_raw_tail_start = max(T_at_top + 0.05,
                                float(smooth_scroll_chat_start) - RULE_27_NATURAL_HOLD_S)
    else:
        T_raw_tail_start = T_at_top + 0.05  # legacy fallback

    print(f"\n[process] rule 29: rebuild source at z0b ease-out window")
    print(f"[process]   T_z0b_ease_out_start_src = {T_ease_out_start:.3f}s (scrubbed)")
    print(f"[process]   T_at_top_prompt_visible  = {T_at_top:.3f}s (raw)")
    print(f"[process]   T_raw_tail_start         = {T_raw_tail_start:.3f}s (raw; "
          f"natural hold normalized to {RULE_27_NATURAL_HOLD_S}s)")
    print(f"[process]   freeze_duration          = {freeze_duration:.2f}s "
          f"(z0b.ease {z0b_ease:.2f} + {RULE_29_HOLD_S}s tpad hold)")

    tmp_pre = intermediate.with_suffix(".pre.mp4")
    tmp_slice = intermediate.with_suffix(".slice.mp4")
    tmp_freeze = intermediate.with_suffix(".freeze.mp4")
    tmp_tail = intermediate.with_suffix(".tail.mp4")
    tmp_concat = intermediate.with_suffix(".concat.txt")
    tmp_out = intermediate.with_suffix(".r29.mp4")
    try:
        for cmd in [
            ["ffmpeg", "-y", "-i", str(intermediate), "-t", f"{T_ease_out_start:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_pre)],
            ["ffmpeg", "-y", "-ss", f"{T_at_top:.3f}", "-i", str(raw), "-t", "0.05",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_slice)],
            ["ffmpeg", "-y", "-i", str(tmp_slice),
             "-vf", f"tpad=stop_mode=clone:stop_duration={freeze_duration - 0.05:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_freeze)],
            ["ffmpeg", "-y", "-ss", f"{T_raw_tail_start:.3f}", "-i", str(raw),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_tail)],
        ]:
            subprocess.run(cmd, check=True, capture_output=True)
        tmp_concat.write_text(
            f"file '{tmp_pre}'\nfile '{tmp_freeze}'\nfile '{tmp_tail}'\n"
        )
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp_concat),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", "60", "-an", str(tmp_out),
        ], check=True, capture_output=True)
        tmp_out.replace(intermediate)
        print(f"[process] rule 29: ✓ rebuilt {intermediate.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[process] ⚠️ rule 29 rebuild failed (rc={e.returncode}); "
              f"continuing with original intermediate")
        return False
    finally:
        for f in [tmp_pre, tmp_slice, tmp_freeze, tmp_tail, tmp_concat, tmp_out]:
            f.unlink(missing_ok=True)


def process_slot(slot_dir: Path,
                 scrub_extra: list[str] | None = None,
                 do_tick_cut: bool = True,
                 tick_tail_seconds: float | None = None,
                 tick_pre_seconds: float | None = "DEFAULT",
                 tick_post_seconds: float | None = "DEFAULT",
                 cap_dead: bool = True,
                 force_typing_speedup: bool = True) -> dict:
    """Run scrub → (optional) tick-cut → (optional) zoom on the slot's trimmed.mp4.

    Order per the V2 pattern (confirmed): scrub first compresses obvious
    dead-time freezes; tick-cut then compresses the inter-tick streaming
    dead-time using the Progress sidebar as the signal; zoom (if zooms.json
    present) adds visual emphasis on the tightened source.

    Returns a dict describing what was produced. Non-fatal on failure at any
    stage — there's always a `zoom.mp4` final file as long as scrub succeeded.
    """
    # Lazy-import — only need it when tick-cut is requested.
    from tick_cut import tick_cut as run_tick_cut

    slot_dir = slot_dir.resolve()
    trimmed = slot_dir / "trimmed.mp4"
    zooms_json = slot_dir / "zooms.json"
    out_zoom = slot_dir / "zoom.mp4"
    scrubbed = slot_dir / "trimmed_scrubbed.mp4"
    tickcut = slot_dir / "trimmed_scrubbed_tickcut.mp4"

    result = {
        "slot": str(slot_dir),
        "static_mode": False,
        "rule_30_applied": False,
        "scrubbed_intermediate": False,
        "tick_cut_applied": False,
        "zooms_applied": False,
        "final": None,
        "ok": False,
    }

    if not trimmed.exists():
        print(f"\n[process] skipped — no trimmed.mp4 in {slot_dir.name}")
        return result

    # ── 0. Rule #30 gateway: static-placeholder vs dynamic-checklist ─────
    # Probe the Progress sidebar during the loading window. If Cowork
    # rendered the static placeholder (0 ticks), pre-cut the loading window
    # to a 3.0s flash and signal downstream to skip z0b.
    # Shared implementation: project_root/tools/static_gateway.py.
    sys.path.insert(0, str(MAIN_TOOLS))
    try:
        from static_gateway import run_gateway as _rule_30_run
        gw = _rule_30_run(trimmed, slot_dir / "manifest.json", in_place=True)
        result["static_mode"] = gw["static_mode"]
        result["rule_30_applied"] = gw["applied"]
    except ImportError as e:
        print(f"[process] ⚠️ rule 30 module unavailable ({e}); defaulting to dynamic path")

    # ── 1. scrub: dead-time frame-diff cut ───────────────────────────────
    # Rule N2: derive the typing window from manifest.phases.streaming_started
    # and pass --force-speed-range "0:X:2.0" so scrub.py uses uniform speedup
    # (not tapered_with_cut) across the typing segment. User --scrub-arg with
    # their own --force-speed-range overrides the auto value.
    auto_force_range, buffer_compressed, preserve_end_scrubbed = _derive_typing_force_range(
        slot_dir, scrub_extra, enabled=force_typing_speedup,
    )
    print(f"\n[process] scrub: trimmed.mp4 → trimmed_scrubbed.mp4")
    cmd = ["python3", str(MAIN_TOOLS / "scrub.py"), str(trimmed)]
    if auto_force_range:
        cmd.extend(["--force-speed-range", auto_force_range])
        # Buffer-1 compression (Rule #31 mech 2) can require speedups >>2×
        # (e.g., 31s buffer → 3s target = 10.4×). Raise scrub's default
        # --max-speed cap (2.0) so the buffer-1 force-range isn't clipped.
        # Only matters when a force-speed-range is set; otherwise default
        # 2× cap applies to natural scrub segments.
        cmd.extend(["--max-speed", "20.0"])
    if scrub_extra:
        cmd.extend(scrub_extra)
    try:
        subprocess.run(cmd, check=True, cwd=str(PROJECT_ROOT))
    except subprocess.CalledProcessError as e:
        print(f"[process] ⚠️ scrub failed (rc={e.returncode}); keeping trimmed.mp4 as final")
        return result
    if not scrubbed.exists():
        print(f"[process] ⚠️ scrub didn't produce {scrubbed.name}; aborting")
        return result
    result["scrubbed_intermediate"] = True

    # ── 1.5. Rule #31 mechanism 2: buffer-1 compression.
    # Primary path: scrub.py --force-speed-range (set in _derive_typing_force_range)
    # compresses buffer-1 deterministically to 3.0s based on detected raw tick
    # positions. When that fires, skip the post-scrub fallback (which uses
    # detect_ticks on scrubbed and tends to miss low-mag early ticks for
    # tool-heavy queries — N3's first tick at scrubbed ~39s with mag ~6 gets
    # edged out by post-brief peaks in detect_ticks's top-N).
    # Fallback path: when raw tick detection didn't find ticks (no manifest,
    # no streaming_started, or scan returned empty), use the post-scrub probe.
    if buffer_compressed:
        print("[process] rule #31 buffer-cut: SKIPPED (buffer-1 already "
              "compressed deterministically via scrub --force-speed-range)")
        result["rule_31_buffer_cut"] = False
    else:
        result["rule_31_buffer_cut"] = _compress_pre_tick_buffer(slot_dir, scrubbed)

    # ── 2. tick-cut: inter-tick compression via Progress-sidebar peaks ──
    # Source for the next stage. Starts as the scrubbed intermediate; becomes
    # the tick-cut intermediate if tick_cut runs and succeeds.
    next_input = scrubbed
    if do_tick_cut:
        print(f"\n[process] tick-cut: trimmed_scrubbed.mp4 → trimmed_scrubbed_tickcut.mp4")
        # Use tick_cut's own defaults when caller didn't pass overrides — pass
        # through only what was specified so the tick_cut module owns the defaults.
        kw = {}
        if tick_tail_seconds is not None:
            kw["tail_seconds"] = tick_tail_seconds
        if tick_pre_seconds != "DEFAULT":
            kw["pre_seconds"] = tick_pre_seconds
        if tick_post_seconds != "DEFAULT":
            kw["post_seconds"] = tick_post_seconds
        # Tell tick_cut to skip the typing zone when detecting ticks — avoids
        # picking up cursor-blink / tool-call noise during typing as a "tick".
        # typing_end_scrubbed = streaming_started / TYPING_SPEEDUP_FACTOR.
        try:
            mf = json.loads((slot_dir / "manifest.json").read_text())
            t_stream = mf.get("phases", {}).get("streaming_started")
            if t_stream is not None:
                kw["scan_start_s"] = float(t_stream) / TYPING_SPEEDUP_FACTOR + 0.5
        except (FileNotFoundError, json.JSONDecodeError, OSError, KeyError):
            pass
        # Bound the detection scan upper end to preserve_end_scrubbed (boundary
        # between the at-1× tick montage and the scrub-compressed post-brief
        # region). Without this, high-mag post-brief scroll peaks dominate
        # detect_ticks's top-N and edge out low-mag real ticks.
        if preserve_end_scrubbed is not None:
            kw["scan_end_s"] = preserve_end_scrubbed + 0.5  # small buffer past preserve end
        try:
            ok = run_tick_cut(scrubbed, tickcut, **kw)
        except Exception as e:
            print(f"[process] ⚠️ tick-cut raised: {type(e).__name__}: {e}")
            ok = False
        if ok and tickcut.exists():
            result["tick_cut_applied"] = True
            # Drop the scrub-only intermediate; tickcut replaces it.
            scrubbed.unlink(missing_ok=True)
            next_input = tickcut
        else:
            print(f"[process] ⚠️ tick-cut didn't succeed; continuing with scrubbed only")
            # Leave `next_input = scrubbed`; the zoom/rename stage handles either.

    # ── 3. zoom: visual emphasis. User's zooms.json wins; otherwise we use
    #          tick_cut's auto-emitted progress-sidebar follow zoom (mirrors
    #          V1's z0b pattern). Skipped only if neither exists.
    auto_zooms_json = tickcut.with_suffix(".auto_zooms.json")
    # Apply Hard Rule #22 (news extension): z0 ease-out STARTS at typing-end.
    # Camera transitions z0 → z0b continuously (no full-frame gap). z0b
    # ease-out completes at the brief-landed snap so camera retracts as
    # the brief lands.
    ticks_json = tickcut.with_suffix(".ticks.json")
    _rule_22_override_auto_zooms(slot_dir, auto_zooms_json, ticks_json=ticks_json)
    if zooms_json.exists():
        zooms_to_use = zooms_json
        zoom_source = "zooms.json (user-authored)"
    elif auto_zooms_json.exists():
        zooms_to_use = auto_zooms_json
        zoom_source = f"{auto_zooms_json.name} (auto from tick-cut)"
    else:
        zooms_to_use = None
        zoom_source = None

    if zooms_to_use is not None:
        # Hard Rule #29 — auto-apply the source-content rebuild for automated
        # captures with z0b. Replaces source at z0b's ease-out window with a
        # freeze of the at-top frame + stitches raw-tail for natural continuation.
        # No-op on no-manifest / no-z0b / no-raw conditions.
        r29_applied = _rule_29_rebuild(slot_dir, next_input, zooms_to_use)
        result["rule_29_applied"] = r29_applied

        print(f"\n[process] zoom: {next_input.name} + {zoom_source} → zoom.mp4")
        try:
            subprocess.run([
                "python3", str(MAIN_TOOLS / "zoom.py"),
                str(next_input), str(out_zoom),
                "--zooms", str(zooms_to_use),
            ], check=True, cwd=str(PROJECT_ROOT))
            result["zooms_applied"] = True
            next_input.unlink(missing_ok=True)
        except subprocess.CalledProcessError as e:
            print(f"[process] ⚠️ zoom failed (rc={e.returncode}); renaming previous stage → zoom.mp4")
            if out_zoom.exists():
                out_zoom.unlink()
            next_input.rename(out_zoom)
    else:
        print(f"\n[process] no zooms available — renaming {next_input.name} → zoom.mp4")
        if out_zoom.exists():
            out_zoom.unlink()
        next_input.rename(out_zoom)

    # ── 4. dead-time hard cap (news-pipeline rule, decisions/2026-05-28-…) ─
    # Cap any freeze >1s in the post-tick portion of zoom.mp4 to 1s.
    # Protects the pre/tick region so prompt-typing pauses + phase-transition
    # holds aren't compressed; only the brief-done-to-cut-to-top dwell and
    # post-scroll tail get capped. Skipped if zoom.mp4 missing.
    if out_zoom.exists() and cap_dead:
        from tick_cut import cap_dead_times, NEWS_MAX_DEAD_S
        # protect_until_t = end of the auto-zoom timeline (= where the
        # full-frame post region begins). Read from auto_zooms.json if present;
        # if absent (user-authored zooms.json or no zooms), default to 0 — cap
        # the entire video.
        # When Hard Rule #29 fired, the protected window EXTENDS through the
        # 2s Rule #27 hold injected after z0b — otherwise cap_dead would trim
        # that hold to 1s (decisions/2026-05-31-…).
        protect_until_t = 0.0
        if auto_zooms_json.exists() and not zooms_json.exists():
            try:
                az = json.loads(auto_zooms_json.read_text())
                if az:
                    last = az[-1]
                    protect_until_t = float(last["source_t"]) + float(last["duration"])
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"[process] ⚠️ couldn't parse {auto_zooms_json.name} for "
                      f"protect_until_t: {e}; defaulting to 0")
        if result.get("rule_29_applied"):
            protect_until_t += 1.0
            print(f"[process] rule 29: extending cap-dead protect_until_t "
                  f"by 1.0s for tpad hold past z0b end → {protect_until_t:.2f}s")
        print(f"\n[process] cap-dead: zoom.mp4 (protect_until={protect_until_t:.2f}s, "
              f"max_dead={NEWS_MAX_DEAD_S}s)")
        cap_dead_times(out_zoom, max_dead_s=NEWS_MAX_DEAD_S,
                       protect_until_t=protect_until_t)

    result["final"] = str(out_zoom)
    result["ok"] = out_zoom.exists()
    if result["ok"]:
        print(f"\n[process] ✓ final: {out_zoom.relative_to(PROJECT_ROOT)}")
    return result


def run_news_render(slot_dir: Path) -> int:
    """Invoke news_render.py on the slot to compose final.mp4.

    Composites a 5s title card + the slot's zoom.mp4 + a 7s Polaris outro via
    the news Hyperframes template. Output: `<slot>/final.mp4`. Free — no
    HeyGen credits (news doesn't render an avatar talking-head; that's the
    product-demo pipeline's billable Phase 9 only).

    Returns news_render.py's exit code. The orchestrator (parent process.py)
    then either proceeds to lint or surfaces the render failure.
    """
    slot_id = slot_dir.name
    render_script = Path(__file__).parent / "news_render.py"
    print(f"\n[process] render: news-pipeline/tools/news_render.py {slot_id}")
    try:
        result = subprocess.run(
            ["python3", str(render_script), slot_id],
            check=False,
        )
        return result.returncode
    except FileNotFoundError:
        print(f"[process] ⚠️ news_render.py not found at {render_script}; skipping render")
        return 0


def run_lint(slot_dir: Path) -> int:
    """Invoke lint_news.py on the slot. Prints human report; writes JSON sidecar.

    Returns lint's exit code (0 = clean, 1 = errors, 2 = missing artifacts).
    The JSON sidecar at `<slot>/lint-report.json` is the structured feedback
    surface for any orchestrator (agent, CI, shell wrapper) that needs to
    machine-read the findings and decide what to do next.
    """
    slot_id = slot_dir.name
    json_out = slot_dir / "lint-report.json"
    lint_script = Path(__file__).parent / "lint_news.py"
    print(f"\n[process] lint: news-pipeline/tools/lint_news.py {slot_id}")
    try:
        result = subprocess.run(
            ["python3", str(lint_script), slot_id, "--json-out", str(json_out)],
            check=False,
        )
        return result.returncode
    except FileNotFoundError:
        print(f"[process] ⚠️ lint_news.py not found at {lint_script}; skipping lint")
        return 0


def main():
    ap = argparse.ArgumentParser(
        description="Post-capture scrub + tick-cut + optional zoom for a news-pipeline slot.",
    )
    ap.add_argument("slot", help="Slot id (e.g., 'N7') or path to slot directory")
    ap.add_argument("--scrub-arg", action="append", default=[],
                    help="Extra arg to pass to scrub.py (repeatable). "
                         "Example: --scrub-arg=--diff-threshold=-50dB")
    ap.add_argument("--no-tick-cut", action="store_true",
                    help="Skip the Progress-sidebar tick-cut compression step. "
                         "Use if the recording has too few/inconsistent phase ticks.")
    ap.add_argument("--tick-tail-seconds", type=float, default=None,
                    help="Per-tick window half-width. Lower = faster montage. "
                         "Defaults come from tick_cut.py (newsletter-friendly).")
    ap.add_argument("--tick-pre-seconds", type=float, default=None,
                    help="Max seconds of pre-tick intro to keep. Negative = full pre.")
    ap.add_argument("--tick-post-seconds", type=float, default=None,
                    help="Max seconds of post-tick segment to keep. Negative = full post (default).")
    ap.add_argument("--no-cap-dead", action="store_true",
                    help="Disable the news-pipeline 1s dead-time hard cap on the "
                         "post-tick region of zoom.mp4 (decisions/2026-05-28-…).")
    ap.add_argument("--no-typing-speedup", action="store_true",
                    help="Disable rule N2's auto --force-speed-range over the typing "
                         "window. Scrub will fall back to default treatment, which "
                         "MAY cut typing (decisions/2026-05-29-…).")
    ap.add_argument("--no-render", action="store_true",
                    help="Skip the post-process Hyperframes render step. By default "
                         "process.py invokes news_render.py after the scrub/tick_cut/"
                         "zoom pipeline to produce <slot>/final.mp4 (title card + "
                         "recording + Polaris outro). Free — news has no billable "
                         "avatar step.")
    ap.add_argument("--no-lint", action="store_true",
                    help="Skip the post-process lint step. By default process.py "
                         "ends by invoking lint_news.py on the slot, printing the "
                         "human report and writing lint-report.json. process.py's "
                         "exit code then reflects the lint result (0 clean, 1 errors).")
    args = ap.parse_args()
    # Translate sentinel: CLI default None means 'tick_cut defaults'; negative means 'unbounded (None)'.
    def _norm(v):
        if v is None: return "DEFAULT"
        if v < 0: return None
        return v
    slot_dir = resolve_slot(args.slot)
    process_slot(slot_dir,
                 scrub_extra=args.scrub_arg,
                 do_tick_cut=not args.no_tick_cut,
                 tick_tail_seconds=args.tick_tail_seconds,
                 tick_pre_seconds=_norm(args.tick_pre_seconds),
                 tick_post_seconds=_norm(args.tick_post_seconds),
                 cap_dead=not args.no_cap_dead,
                 force_typing_speedup=not args.no_typing_speedup)

    # Render runs BEFORE lint so lint can validate final.mp4 too (L02
    # framerate / L16 colour space currently target it when present). If
    # render fails, we still lint — the missing-artifact rule (L01 + L02
    # branch) will surface the failure cleanly via the JSON sidecar.
    render_rc = 0
    if not args.no_render:
        render_rc = run_news_render(slot_dir)
        if render_rc != 0:
            print(f"\n[process] ⚠️ render exited {render_rc}; continuing to lint anyway")

    if not args.no_lint:
        lint_rc = run_lint(slot_dir)
        # Surface lint result if render was clean; otherwise propagate render
        # failure (render failure is the more actionable signal).
        return render_rc or lint_rc

    return render_rc


if __name__ == "__main__":
    sys.exit(main() or 0)
