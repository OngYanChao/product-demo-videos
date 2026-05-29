#!/usr/bin/env python3
"""Wake diagnostic — does wake_chromium_render() bring Cowork back on-screen
after it's been occluded on a background Space?

Why this exists
---------------
test_phased_scroll.py proved the scroll EVENT payload is irrelevant — all six
variants scroll identically when Cowork is visible. The real failure is that
Cowork's Chromium renderer suspends when its window is occluded (off the
visible Space); synthetic scroll events then queue and don't paint until the
window is composited again.

That harness couldn't reproduce the bug because to DRIVE scroll events Cowork
must be key/frontmost (= visible) — the very state that prevents the suspend.
This script sidesteps that: it only READS window state (CGWindowList
kCGWindowIsOnscreen + frontmost z-order), so it can deliberately occlude
Cowork and measure whether the wake recovers it.

What it does, per trial
-----------------------
  1. Snapshot Cowork state (onscreen? frontmost?)
  2. Occlude — activate --occlude-app so Cowork loses key and (if fullscreen)
     its Space drops to the background
  3. Idle --idle-seconds so the renderer suspends
  4. Snapshot occluded state (expect onscreen False / frontmost False)
  5. Run wake_chromium_render()
  6. Snapshot post-wake state (did onscreen flip back to True?)
  7. Log the full transition + per-trial verdict

Reading the result
------------------
  - Occlude step shows onscreen True  → occlusion failed; Cowork stayed
    visible. Try a different --occlude-app or open a window for it. We can't
    test the wake until we can actually occlude.
  - Occlude True→False, wake False→True, every trial → the wake WORKS in
    isolation. The production bug is then a timing gap (wake fired but scroll
    came before compositing resumed) → fix = verify-onscreen + retry between
    wake and scroll.
  - Wake leaves onscreen False on some/all trials → reproduced the failure.
    wake_chromium_render itself is unreliable (likely the fullscreen-Space
    Cmd+Tab timing) → fix the wake.

Prereqs
-------
  - Claude / Cowork desktop running, ideally fullscreen on its own Space
    (that's the production configuration we're diagnosing).
  - Accessibility permission for the terminal (for the Cmd+Tab keystrokes).
  - Hands off the keyboard/trackpad during the run.

Usage
-----
  python3 news-pipeline/tools/diagnose_wake.py
  python3 news-pipeline/tools/diagnose_wake.py --trials 5 --idle-seconds 10
  python3 news-pipeline/tools/diagnose_wake.py --occlude-app "Visual Studio Code"
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture import cowork_window_state, wake_chromium_render, osascript  # noqa: E402


def fmt(state: dict) -> str:
    if not state["found"]:
        return f"NOT FOUND (top app: {state['frontmost_owner']})"
    return (f"onscreen={str(state['is_onscreen']):5} "
            f"frontmost={str(state['is_frontmost']):5} "
            f"(top app: {state['frontmost_owner']})")


def occlude(app: str) -> None:
    """Push Cowork to the background by activating another app.

    If Cowork is fullscreen on its own Space, activating an app whose windows
    live on the main Space forces a Space switch — Cowork's Space drops to the
    background and Chromium marks the window occluded.
    """
    try:
        osascript(f'tell application "{app}" to activate')
    except subprocess.CalledProcessError as e:
        print(f"      ⚠️  could not activate '{app}': {e}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Diagnose wake_chromium_render reliability.")
    ap.add_argument("--trials", type=int, default=3,
                    help="Number of occlude→wake cycles to run (default 3).")
    ap.add_argument("--idle-seconds", type=float, default=8.0,
                    help="Seconds to idle while occluded so the renderer suspends "
                         "(default 8).")
    ap.add_argument("--occlude-app", default="Finder",
                    help="App to activate to occlude Cowork (default Finder). "
                         "Use one with a window on the main Space for a reliable "
                         "Space switch, e.g. \"Visual Studio Code\".")
    args = ap.parse_args()

    print("=" * 76)
    print("Wake diagnostic — occlude Cowork, then measure if the wake recovers it")
    print("=" * 76)
    print()
    print(f"  trials:       {args.trials}")
    print(f"  idle (occl.): {args.idle_seconds}s")
    print(f"  occlude via:  activate '{args.occlude_app}'")
    print()
    print("  Hands off the keyboard/trackpad during the run.")
    print()
    for i in range(5, 0, -1):
        print(f"  starting in {i}...")
        time.sleep(1)
    print()

    # Make sure we start from Cowork visible.
    try:
        osascript('tell application "Claude" to activate')
    except subprocess.CalledProcessError:
        pass
    time.sleep(1.0)

    # results: list of (occluded_ok, wake_recovered)
    results: list[tuple[bool, bool]] = []
    for t in range(1, args.trials + 1):
        print(f"── Trial {t}/{args.trials} " + "─" * 50)

        s0 = cowork_window_state()
        print(f"  [1] initial:   {fmt(s0)}")

        occlude(args.occlude_app)
        time.sleep(1.0)
        s1 = cowork_window_state()
        print(f"  [2] occluded:  {fmt(s1)}")
        occluded_ok = s1["found"] and not s1["is_onscreen"]
        if not occluded_ok:
            print(f"      ⚠️  occlusion did NOT take — Cowork still on-screen. "
                  f"The wake test below is meaningless this trial.")

        print(f"  [3] idling {args.idle_seconds}s (renderer suspends)...")
        time.sleep(args.idle_seconds)

        print(f"  [4] running wake_chromium_render()...")
        wake_chromium_render()  # prints its own before/after lines
        time.sleep(0.5)
        s2 = cowork_window_state()
        print(f"  [5] post-wake: {fmt(s2)}")

        wake_recovered = s2["found"] and s2["is_onscreen"]
        verdict = "✓ recovered" if wake_recovered else "✗ STILL occluded"
        print(f"  → {verdict}")
        print()
        results.append((occluded_ok, wake_recovered))

    # ---- Summary ----
    print("=" * 76)
    print("SUMMARY")
    print("=" * 76)
    print(f"  {'Trial':<8}{'occlusion took?':<20}{'wake recovered?':<20}")
    print(f"  {'-'*6}  {'-'*16}  {'-'*16}")
    for i, (occ, rec) in enumerate(results, 1):
        print(f"  {i:<8}{('yes' if occ else 'NO'):<20}{('yes' if rec else 'NO'):<20}")
    print()

    valid = [rec for occ, rec in results if occ]
    if not valid:
        print("⚠ Occlusion never took — could not test the wake.")
        print(f"  '{args.occlude_app}' didn't push Cowork off-screen. If Cowork is")
        print("  fullscreen, try --occlude-app with an app that has a window on the")
        print("  main desktop Space (e.g. \"Visual Studio Code\" or \"Terminal\").")
        return

    recovered = sum(1 for r in valid if r)
    print(f"Across {len(valid)} valid trial(s): wake recovered Cowork "
          f"{recovered}/{len(valid)} times.")
    print()
    if recovered == len(valid):
        print("✓ The wake reliably brings Cowork back on-screen in isolation.")
        print("  → The production bug is a TIMING gap: the wake works, but the")
        print("    scroll fires before compositing has resumed. Fix = poll")
        print("    cowork_window_state().is_onscreen (and a short settle) AFTER")
        print("    the wake and BEFORE scrolling, with a retry.")
    elif recovered == 0:
        print("✗ The wake NEVER recovered Cowork — reproduced the failure cleanly.")
        print("  → wake_chromium_render itself is the problem (likely fullscreen-")
        print("    Space Cmd+Tab timing). Fix = a more reliable wake, then re-run")
        print("    this diagnostic until it hits 100%.")
    else:
        print("⚠ The wake is FLAKY — recovered some trials, not others.")
        print("  → Timing-sensitive. Fix = verify-onscreen + retry loop around the")
        print("    wake so a missed wake gets re-attempted rather than scrolled into.")


if __name__ == "__main__":
    main()
