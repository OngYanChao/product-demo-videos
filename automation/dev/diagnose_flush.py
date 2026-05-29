#!/usr/bin/env python3
"""diagnose_flush.py — which post-scroll action makes a synthetic scroll
actually PAINT on a just-occluded Cowork?

Context
-------
diagnose_wake.py proved wake_chromium_render() brings Cowork back on-screen
(is_onscreen flips True). But a real capture run showed the chat only scrolled
to the top AFTER the user manually swiped windows — i.e. synthetic scroll
events posted after the synthetic wake QUEUE and don't paint until a hardware
focus transition flushes them. Hypothesis: the flush trigger is a focus
transition that happens AFTER the scroll is posted (the wake happens before).

This isolates the flush WITHOUT capture.py or a Claude task. Per candidate:
  1. Reset: wake + scroll the chat to the BOTTOM (foreground, paints fine).
  2. Occlude Cowork (activate --occlude-app) + idle so the renderer suspends.
  3. Shared wake (brings it back on-screen).
  4. Snapshot 'pre' (chat at bottom, on-screen, cursor parked).
  5. Scroll UP, then run the candidate's flush action.
  6. Snapshot 'post' (cursor parked).
  7. diff(pre, post): a big diff = the scroll painted (flush worked); ~0 = it
     queued (chat still at bottom).

The pixel diff is a HINT. Ground truth is the saved PNGs in /tmp/flush_test/:
<candidate>_post.png shows the START of the chat (first prompt) if the scroll
painted, or the END of the conversation if it queued.

Candidates
----------
  1 control        — wake → scroll → nothing            (expect: queued)
  2 cmdtab_after   — wake → scroll → Cmd+Tab away+back   (focus transition AFTER scroll)
  3 click_rescroll — wake → scroll → click in window → scroll again
  4 space_switch   — wake → scroll → Ctrl+→ then Ctrl+←  (Spaces nav, if enabled)
  5 activate_cycle — wake → scroll → activate Finder → activate Claude

Prereq: Cowork open to a LONG chat. Hands off the keyboard/trackpad during the
run (~3-4 min for all 5).

Usage
-----
  python3 automation/dev/diagnose_flush.py
  python3 automation/dev/diagnose_flush.py --idle-seconds 8 --occlude-app "Visual Studio Code"
  python3 automation/dev/diagnose_flush.py --candidates 1 2
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture import (  # noqa: E402
    osascript,
    cowork_window_state,
    wake_chromium_render,
    _wake_dance,
    refresh_scroll_targets,
    _screencap_region,
    mean_pixel_diff,
    SCROLL_TARGETS_LOGICAL,
)

# Wide region covering the chat column, for visual inspection + diff.
CHAT_REGION_LOGICAL = (250, 100, 850, 950)
PARK_LOGICAL = (50, 50)
OUTDIR = Path("/tmp/flush_test")
# Diff hint only — NOT ground truth. Visual inspection of the PNG decides.
PAINTED_HINT_DIFF = 18.0


def _line_scroll(target: tuple[int, int], count: int = 80, lines: int = 10, sign: int = 1) -> None:
    from Quartz import CGEventCreateScrollWheelEvent, CGEventPost
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitLine
    x, y = target
    try:
        subprocess.run(["cliclick", f"m:{x},{y}"], check=True)
    except subprocess.CalledProcessError:
        return
    time.sleep(0.1)
    for _ in range(count):
        e = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitLine, 1, sign * lines)
        CGEventPost(kCGHIDEventTap, e)
        time.sleep(0.015)
    time.sleep(0.3)


def scroll_up_chat() -> None:
    _line_scroll(SCROLL_TARGETS_LOGICAL[0], sign=1)


def scroll_down_chat() -> None:
    _line_scroll(SCROLL_TARGETS_LOGICAL[0], sign=-1)


def park_cursor() -> None:
    subprocess.run(["cliclick", f"m:{PARK_LOGICAL[0]},{PARK_LOGICAL[1]}"], check=False)


def occlude(app: str) -> None:
    try:
        osascript(f'tell application "{app}" to activate')
    except subprocess.CalledProcessError as e:
        print(f"      ⚠️  could not activate '{app}': {e}")


# ---------- flush candidates (run AFTER the scroll-up is posted) ----------

def flush_none() -> None:
    pass


def flush_cmdtab() -> None:
    _wake_dance()  # Cmd+Tab away + back + activate — a focus transition AFTER the scroll


def flush_click_rescroll() -> None:
    x, y = SCROLL_TARGETS_LOGICAL[0]
    subprocess.run(["cliclick", f"c:{x},{y}"], check=False)
    time.sleep(0.2)
    scroll_up_chat()


def flush_space_switch() -> None:
    # Ctrl+Right then Ctrl+Left — Mission Control Spaces nav (only if enabled).
    try:
        osascript('tell application "System Events" to key code 124 using {control down}')
        time.sleep(0.8)
        osascript('tell application "System Events" to key code 123 using {control down}')
        time.sleep(0.8)
    except subprocess.CalledProcessError:
        pass


def flush_activate_cycle() -> None:
    try:
        osascript('tell application "Finder" to activate')
        time.sleep(0.6)
        osascript('tell application "Claude" to activate')
        time.sleep(0.6)
    except subprocess.CalledProcessError:
        pass


CANDIDATES = [
    ("1_control",        flush_none),
    ("2_cmdtab_after",   flush_cmdtab),
    ("3_click_rescroll", flush_click_rescroll),
    ("4_space_switch",   flush_space_switch),
    ("5_activate_cycle", flush_activate_cycle),
]


def run_candidate(name: str, flush_fn, occlude_app: str, idle_s: float) -> tuple[float, bool]:
    """One occlude→wake→scroll→flush cycle. Returns (diff, looks_painted)."""
    # 1. Reset: ensure on-screen, scroll to the bottom (creates scroll-up room).
    wake_chromium_render()
    scroll_down_chat()
    scroll_down_chat()
    time.sleep(1.0)

    # 2. Occlude + suspend.
    occlude(occlude_app)
    time.sleep(idle_s)

    # 3. Shared wake — brings Cowork back on-screen (common to all candidates).
    woke = wake_chromium_render()

    # 4. 'pre' snapshot (chat at bottom, cursor parked off-region).
    park_cursor()
    time.sleep(0.2)
    pre = OUTDIR / f"{name}_pre.png"
    _screencap_region(CHAT_REGION_LOGICAL, pre)

    # 5. Scroll up, then the candidate's flush action.
    scroll_up_chat()
    flush_fn()

    # 6. 'post' snapshot (cursor parked again so it doesn't pollute the diff).
    park_cursor()
    time.sleep(1.0)
    post = OUTDIR / f"{name}_post.png"
    _screencap_region(CHAT_REGION_LOGICAL, post)

    diff = mean_pixel_diff(pre, post) if (pre.exists() and post.exists()) else -1.0
    return diff, diff >= PAINTED_HINT_DIFF


def main() -> None:
    ap = argparse.ArgumentParser(description="Diagnose which flush action makes a synthetic scroll paint.")
    ap.add_argument("--idle-seconds", type=float, default=6.0,
                    help="Seconds occluded so the renderer suspends (default 6).")
    ap.add_argument("--occlude-app", default="Visual Studio Code",
                    help="App to activate to occlude Cowork (default 'Visual Studio Code').")
    ap.add_argument("--candidates", nargs="+", type=int,
                    help="Only run these candidate numbers (1-5). Default: all.")
    args = ap.parse_args()

    cands = CANDIDATES
    if args.candidates:
        cands = [CANDIDATES[i - 1] for i in args.candidates if 1 <= i <= len(CANDIDATES)]
        if not cands:
            sys.exit("❌ No valid candidate numbers (use 1-5).")

    OUTDIR.mkdir(parents=True, exist_ok=True)

    print("=" * 76)
    print("Flush diagnostic — what makes a synthetic scroll paint after occlusion?")
    print("=" * 76)
    print(f"  candidates:   {[c[0] for c in cands]}")
    print(f"  idle (occl.): {args.idle_seconds}s")
    print(f"  occlude via:  activate '{args.occlude_app}'")
    print(f"  screenshots:  {OUTDIR}/")
    print()
    print("  Prereq: Cowork open to a LONG chat. Hands OFF until done.")
    print()
    for i in range(5, 0, -1):
        print(f"  starting in {i}...")
        time.sleep(1)
    print()

    # Adapt cursor targets to the current layout (needs Cowork frontmost).
    try:
        osascript('tell application "Claude" to activate')
        time.sleep(1.0)
        refresh_scroll_targets()
    except Exception as e:
        print(f"  [layout] refresh_scroll_targets failed ({e}); using defaults")
    print(f"  scroll target: {SCROLL_TARGETS_LOGICAL[0]}")
    print()

    results: list[tuple[str, float, bool]] = []
    for name, fn in cands:
        print(f"── Candidate {name} " + "─" * 48)
        try:
            diff, painted = run_candidate(name, fn, args.occlude_app, args.idle_seconds)
            results.append((name, diff, painted))
            verdict = "LIKELY PAINTED" if painted else "likely queued (no paint)"
            print(f"  → diff(pre,post) = {diff:.2f}  →  {verdict}")
            print(f"    inspect: {OUTDIR}/{name}_post.png")
        except Exception as e:
            print(f"  ❌ raised: {type(e).__name__}: {e}")
            results.append((name, -1.0, False))
        print()

    print("=" * 76)
    print("SUMMARY (diff is a HINT — confirm with the _post.png images)")
    print("=" * 76)
    print(f"  {'Candidate':<20}{'diff(pre,post)':>16}  {'hint'}")
    print(f"  {'-'*18}  {'-'*14}  {'-'*22}")
    for name, diff, painted in results:
        d = "FAIL" if diff < 0 else f"{diff:.2f}"
        print(f"  {name:<20}{d:>16}  {'LIKELY PAINTED' if painted else 'queued'}")
    print()
    painters = [n for n, _, p in results if p]
    if painters:
        print(f"Candidate(s) that look like they painted: {painters}")
        print("Confirm in the _post.png (should show the TOP of the chat / first prompt),")
        print("then we port that flush action into capture.py's scroll sequence.")
    else:
        print("No candidate painted via the diff hint. Check the _post.png images —")
        print("if ALL show the chat still at the bottom, synthetic focus transitions")
        print("don't flush the queue and we need a hardware-level approach.")


if __name__ == "__main__":
    main()
