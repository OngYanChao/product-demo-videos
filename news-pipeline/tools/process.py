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
                               enabled: bool) -> str | None:
    """Derive the rule-N2 --force-speed-range value from the slot's manifest.

    Returns a string like "0:24.05:2.0" if streaming_started is available and
    the user hasn't already passed their own --force-speed-range; otherwise
    None (no auto-force; scrub.py keeps its default treatment).
    """
    if not enabled:
        return None
    # Defer to user override.
    if any("--force-speed-range" in (a or "") for a in (scrub_extra or [])):
        print("[process] rule N2: user passed --force-speed-range; honoring "
              "their value (auto-derivation skipped)")
        return None
    manifest_path = slot_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"[process] ⚠️ rule N2: {manifest_path.name} missing; can't derive "
              f"typing window — scrub will use default treatment (may cut typing)")
        return None
    try:
        manifest = json.loads(manifest_path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"[process] ⚠️ rule N2: {manifest_path.name} unreadable "
              f"({type(e).__name__}); skipping auto force-range")
        return None
    t = manifest.get("phases", {}).get("streaming_started")
    if t is None:
        # Older recordings (pre-2026-05-29 capture.py) won't have this key.
        print(f"[process] ⚠️ rule N2: phases.streaming_started missing from manifest "
              f"(likely a pre-N2 recording); scrub will use default treatment")
        return None
    try:
        t_float = float(t)
    except (TypeError, ValueError):
        print(f"[process] ⚠️ rule N2: streaming_started={t!r} not a number; skipping")
        return None
    X = max(0.0, t_float - TYPING_END_SAFETY_SHAVE_S)
    if X <= 0.05:
        # Too small to matter — typing was instant or the safety shave ate the window.
        return None
    print(f"[process] rule N2: forcing typing window [0, {X:.2f}s] at "
          f"{TYPING_SPEEDUP_FACTOR}× (streaming_started={t_float:.2f}s)")
    return f"0:{X:.2f}:{TYPING_SPEEDUP_FACTOR}"


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
        "scrubbed_intermediate": False,
        "tick_cut_applied": False,
        "zooms_applied": False,
        "final": None,
        "ok": False,
    }

    if not trimmed.exists():
        print(f"\n[process] skipped — no trimmed.mp4 in {slot_dir.name}")
        return result

    # ── 1. scrub: dead-time frame-diff cut ───────────────────────────────
    # Rule N2: derive the typing window from manifest.phases.streaming_started
    # and pass --force-speed-range "0:X:2.0" so scrub.py uses uniform speedup
    # (not tapered_with_cut) across the typing segment. User --scrub-arg with
    # their own --force-speed-range overrides the auto value.
    auto_force_range = _derive_typing_force_range(
        slot_dir, scrub_extra, enabled=force_typing_speedup,
    )
    print(f"\n[process] scrub: trimmed.mp4 → trimmed_scrubbed.mp4")
    cmd = ["python3", str(MAIN_TOOLS / "scrub.py"), str(trimmed)]
    if auto_force_range:
        cmd.extend(["--force-speed-range", auto_force_range])
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
        print(f"\n[process] cap-dead: zoom.mp4 (protect_until={protect_until_t:.2f}s, "
              f"max_dead={NEWS_MAX_DEAD_S}s)")
        cap_dead_times(out_zoom, max_dead_s=NEWS_MAX_DEAD_S,
                       protect_until_t=protect_until_t)

    result["final"] = str(out_zoom)
    result["ok"] = out_zoom.exists()
    if result["ok"]:
        print(f"\n[process] ✓ final: {out_zoom.relative_to(PROJECT_ROOT)}")
    return result


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
    args = ap.parse_args()
    # Translate sentinel: CLI default None means 'tick_cut defaults'; negative means 'unbounded (None)'.
    def _norm(v):
        if v is None: return "DEFAULT"
        if v < 0: return None
        return v
    process_slot(resolve_slot(args.slot),
                 scrub_extra=args.scrub_arg,
                 do_tick_cut=not args.no_tick_cut,
                 tick_tail_seconds=args.tick_tail_seconds,
                 tick_pre_seconds=_norm(args.tick_pre_seconds),
                 tick_post_seconds=_norm(args.tick_post_seconds),
                 cap_dead=not args.no_cap_dead,
                 force_typing_speedup=not args.no_typing_speedup)


if __name__ == "__main__":
    main()
