#!/usr/bin/env python3
"""Phased-scroll-event probe — does trackpad-phase metadata bypass Chromium's
render-suspend on Cowork?

Context
-------
capture.py's scroll-up step fires 80 LINE-unit scroll wheel events at Cowork
after streaming ends. On some machines the events queue against a suspended
WebContents renderer and don't visually apply until the user manually switches
windows (windowDidBecomeKey fires → Chromium wakes → queued events flush).

`wake_chromium_render()` tries to fix this with a Cmd+Tab dance but doesn't
work reliably when Cowork is in a fullscreen Space (Space-switch animations
exceed the script's wait timings).

Hypothesis
----------
Real trackpad swipes work even against a partially-suspended Chromium because
phased gesture events (kCGScrollPhaseBegan / Changed / Ended) dispatch through
a separate pipeline that doesn't require the WebContents render thread to be
fully active. Our current unphased CGEvents take the render-thread-required
path.

What this tests
---------------
Six scroll methods, each tested under two conditions:
  - "fresh":     run immediately after activating + nudging Cowork (control).
  - "suspended": idle --idle-seconds with no input to Cowork first, so its
                 renderer suspends. This is the production failure scenario.

For each (method, condition), screencap a chat region before + after and
mean-pixel-diff to detect whether the scroll visibly happened.

Caveat: the harness can only simulate suspension by waiting. Real production
suspension involves the user actively focusing another app — which we can't
fully reproduce without losing our ability to drive the test. If every method
"works" even in the suspended condition, try --idle-seconds 15+, or run the
test with the terminal moved to another Space so Cowork sits truly idle.

Prereqs
-------
1. Cowork desktop visible (fullscreen Space is fine — it's the worst case).
2. A long chat conversation open, scrolled to the BOTTOM.
3. Hands off the keyboard/trackpad during the run.

Usage
-----
  python3 news-pipeline/tools/test_phased_scroll.py
  python3 news-pipeline/tools/test_phased_scroll.py --idle-seconds 8
  python3 news-pipeline/tools/test_phased_scroll.py --methods 3 4 5
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture import osascript, SCROLL_TARGETS_LOGICAL  # noqa: E402


CHAT_REGION_LOGICAL = (400, 200, 600, 700)  # matches auto_test_scroll.py
SCROLL_DIFF_THRESHOLD = 10.0  # mean pixel diff above this = scroll happened

# CGEvent field constants — values from <CoreGraphics/CGEventTypes.h>.
# PyObjC exposes them as module names but availability has varied across
# versions, so we hard-code the integers for portability.
FIELD_IS_CONTINUOUS = 88     # kCGScrollWheelEventIsContinuous
FIELD_SCROLL_PHASE = 99      # kCGScrollWheelEventScrollPhase
FIELD_MOMENTUM_PHASE = 123   # kCGScrollWheelEventMomentumPhase

# CGScrollPhase enum
PHASE_BEGAN = 1
PHASE_CHANGED = 2
PHASE_ENDED = 4
PHASE_CANCELLED = 8
PHASE_MAY_BEGIN = 128

# CGMomentumScrollPhase enum
MOMENTUM_NONE = 0
MOMENTUM_BEGIN = 1
MOMENTUM_CONTINUE = 2
MOMENTUM_END = 3


# ---------- helpers ----------

def screencap_region(x: int, y: int, w: int, h: int, out: Path) -> None:
    subprocess.run(
        ["screencapture", "-x", "-R", f"{x},{y},{w},{h}", str(out)],
        check=True, capture_output=True,
    )


def content_diff(a: Path, b: Path) -> float:
    from PIL import Image, ImageChops, ImageStat
    ia = Image.open(a).convert("RGB")
    ib = Image.open(b).convert("RGB")
    if ia.size != ib.size:
        ib = ib.resize(ia.size)
    diff = ImageChops.difference(ia, ib)
    stat = ImageStat.Stat(diff)
    return sum(stat.mean) / len(stat.mean)


def activate_claude() -> None:
    osascript('tell application "Claude" to activate')
    time.sleep(0.8)


def reset_scroll_to_bottom(x: int, y: int) -> None:
    """LINE scroll wheel, negative delta — proven to scroll DOWN reliably."""
    from Quartz import CGEventCreateScrollWheelEvent, CGEventPost
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitLine
    subprocess.run(["cliclick", f"m:{x},{y}"], check=True)
    time.sleep(0.1)
    for _ in range(80):
        event = CGEventCreateScrollWheelEvent(
            None, kCGScrollEventUnitLine, 1, -10
        )
        CGEventPost(kCGHIDEventTap, event)
        time.sleep(0.015)
    time.sleep(0.5)


# ---------- scroll method implementations ----------
# All methods assume the cursor has already been parked at the scroll target
# by the harness — they just post events.

def m1_unphased_line(x: int, y: int) -> None:
    """Control — current production path. 60 LINE events, no phase metadata."""
    from Quartz import CGEventCreateScrollWheelEvent, CGEventPost
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitLine
    for _ in range(60):
        e = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitLine, 1, 10)
        CGEventPost(kCGHIDEventTap, e)
        time.sleep(0.015)


def m2_unphased_pixel(x: int, y: int) -> None:
    """Pixel-unit, no phase. Should fail the same way as M1 if suspend is the cause."""
    from Quartz import CGEventCreateScrollWheelEvent, CGEventPost
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitPixel
    for _ in range(40):
        e = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitPixel, 1, 30)
        CGEventPost(kCGHIDEventTap, e)
        time.sleep(0.025)


def m3_phased_pixel(x: int, y: int) -> None:
    """Trackpad-style: Began → Changed × N → Ended. Pixel units, no IsContinuous."""
    from Quartz import (
        CGEventCreateScrollWheelEvent, CGEventPost,
        CGEventSetIntegerValueField,
    )
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitPixel

    began = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitPixel, 1, 0)
    CGEventSetIntegerValueField(began, FIELD_SCROLL_PHASE, PHASE_BEGAN)
    CGEventPost(kCGHIDEventTap, began)
    time.sleep(0.02)

    for _ in range(40):
        e = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitPixel, 1, 30)
        CGEventSetIntegerValueField(e, FIELD_SCROLL_PHASE, PHASE_CHANGED)
        CGEventPost(kCGHIDEventTap, e)
        time.sleep(0.025)

    ended = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitPixel, 1, 0)
    CGEventSetIntegerValueField(ended, FIELD_SCROLL_PHASE, PHASE_ENDED)
    CGEventPost(kCGHIDEventTap, ended)


def m4_phased_continuous_pixel(x: int, y: int) -> None:
    """Phased pixel + explicit IsContinuous=1. Closest to a real trackpad swipe."""
    from Quartz import (
        CGEventCreateScrollWheelEvent, CGEventPost,
        CGEventSetIntegerValueField,
    )
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitPixel

    def post(delta: int, phase: int) -> None:
        e = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitPixel, 1, delta)
        CGEventSetIntegerValueField(e, FIELD_IS_CONTINUOUS, 1)
        CGEventSetIntegerValueField(e, FIELD_SCROLL_PHASE, phase)
        CGEventPost(kCGHIDEventTap, e)

    post(0, PHASE_BEGAN)
    time.sleep(0.02)
    for _ in range(40):
        post(30, PHASE_CHANGED)
        time.sleep(0.025)
    post(0, PHASE_ENDED)


def m5_phased_continuous_with_momentum(x: int, y: int) -> None:
    """Phased + continuous + a momentum tail. Mimics a flick gesture where
    Chromium's kinetic-scroll path takes over after the fingers lift.
    """
    from Quartz import (
        CGEventCreateScrollWheelEvent, CGEventPost,
        CGEventSetIntegerValueField,
    )
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitPixel

    def post(delta: int, phase: int, momentum: int = MOMENTUM_NONE) -> None:
        e = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitPixel, 1, delta)
        CGEventSetIntegerValueField(e, FIELD_IS_CONTINUOUS, 1)
        CGEventSetIntegerValueField(e, FIELD_SCROLL_PHASE, phase)
        CGEventSetIntegerValueField(e, FIELD_MOMENTUM_PHASE, momentum)
        CGEventPost(kCGHIDEventTap, e)

    # Active gesture
    post(0, PHASE_BEGAN)
    time.sleep(0.02)
    for _ in range(20):
        post(40, PHASE_CHANGED)
        time.sleep(0.020)
    post(0, PHASE_ENDED)
    time.sleep(0.02)

    # Momentum tail — scroll-phase is 0 (no active gesture) during momentum.
    post(40, 0, MOMENTUM_BEGIN)
    time.sleep(0.020)
    for _ in range(20):
        post(30, 0, MOMENTUM_CONTINUE)
        time.sleep(0.020)
    post(0, 0, MOMENTUM_END)


def m6_phased_line(x: int, y: int) -> None:
    """Hybrid: LINE units with phase metadata. Some Chromium versions key off
    LINE-vs-PIXEL differently from the phase field, so worth isolating.
    """
    from Quartz import (
        CGEventCreateScrollWheelEvent, CGEventPost,
        CGEventSetIntegerValueField,
    )
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitLine

    began = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitLine, 1, 0)
    CGEventSetIntegerValueField(began, FIELD_SCROLL_PHASE, PHASE_BEGAN)
    CGEventPost(kCGHIDEventTap, began)
    time.sleep(0.02)

    for _ in range(60):
        e = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitLine, 1, 10)
        CGEventSetIntegerValueField(e, FIELD_SCROLL_PHASE, PHASE_CHANGED)
        CGEventPost(kCGHIDEventTap, e)
        time.sleep(0.015)

    ended = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitLine, 1, 0)
    CGEventSetIntegerValueField(ended, FIELD_SCROLL_PHASE, PHASE_ENDED)
    CGEventPost(kCGHIDEventTap, ended)


METHODS = [
    ("M1 unphased LINE (production)",        m1_unphased_line),
    ("M2 unphased PIXEL",                    m2_unphased_pixel),
    ("M3 phased PIXEL",                      m3_phased_pixel),
    ("M4 phased+continuous PIXEL",           m4_phased_continuous_pixel),
    ("M5 phased+continuous+momentum PIXEL",  m5_phased_continuous_with_momentum),
    ("M6 phased LINE",                       m6_phased_line),
]


# ---------- harness ----------

def run_method_under_condition(name: str, method,
                                x: int, y: int,
                                tmpdir: Path,
                                idle_seconds: float,
                                condition_label: str,
                                ) -> tuple[float, bool]:
    """Activate → reset to bottom → idle (maybe) → snap BEFORE → run → snap AFTER → diff."""
    activate_claude()
    reset_scroll_to_bottom(x, y)
    time.sleep(0.5)

    # Park cursor at the scroll target so subsequent cursor pixels contribute
    # zero diff between BEFORE and AFTER. The method itself does NOT move the
    # cursor — it just posts events at this location.
    subprocess.run(["cliclick", f"m:{x},{y}"], check=True)
    time.sleep(0.15)

    if idle_seconds > 0:
        # Wait without touching Cowork so its renderer can suspend. NB: cliclick
        # mouse moves above do NOT typically wake a suspended WebContents — only
        # window-focus transitions (windowDidBecomeKey) do.
        print(f"      idling {idle_seconds:.1f}s (no input to Cowork)...")
        time.sleep(idle_seconds)

    rx, ry, rw, rh = CHAT_REGION_LOGICAL
    safe_name = name.replace(' ', '_').replace('+', '_').replace('(', '').replace(')', '')
    before = tmpdir / f"{condition_label}_{safe_name}_before.png"
    after = tmpdir / f"{condition_label}_{safe_name}_after.png"

    screencap_region(rx, ry, rw, rh, before)
    method(x, y)
    time.sleep(1.5)  # let any kinetic animation settle
    screencap_region(rx, ry, rw, rh, after)

    d = content_diff(before, after)
    return d, d > SCROLL_DIFF_THRESHOLD


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Test phased vs unphased scroll events against Cowork.",
    )
    ap.add_argument("--idle-seconds", type=float, default=5.0,
                    help="Seconds to idle before the 'suspended' pass (default 5). "
                         "Set 0 to skip the suspended pass entirely.")
    ap.add_argument("--methods", nargs="+", type=int,
                    help="Only run these method numbers (1-6). Default: all.")
    ap.add_argument("--suspend-only", action="store_true",
                    help="Skip the 'fresh' pass and only run the 'suspended' "
                         "condition. Use once 'fresh' is known to pass — halves "
                         "runtime so you can afford a much longer --idle-seconds.")
    args = ap.parse_args()

    conditions = [("fresh", 0.0), ("suspended", args.idle_seconds)]
    if args.suspend_only:
        conditions = [("suspended", args.idle_seconds)]

    methods = METHODS
    if args.methods:
        methods = [METHODS[i - 1] for i in args.methods if 1 <= i <= len(METHODS)]
        if not methods:
            sys.exit("❌ No valid method numbers selected (use 1-6).")

    print("=" * 76)
    print("Phased-scroll probe — Cowork suspend bypass test")
    print("=" * 76)
    print()
    print("Prereqs:")
    print("  - Cowork desktop visible (fullscreen Space OK — that's the worst case)")
    print("  - A long chat open, scrolled to the BOTTOM")
    print("  - Hands off the keyboard/trackpad during the run")
    print()
    print(f"Running {len(methods)} method(s), {len(conditions)} condition(s) each:")
    if not args.suspend_only:
        print(f"  - 'fresh'     — run immediately (renderer awake)")
    if args.idle_seconds > 0:
        print(f"  - 'suspended' — idle {args.idle_seconds}s first (renderer may suspend)")
    elif not args.suspend_only:
        print(f"  - 'suspended' — SKIPPED (--idle-seconds 0)")
    print()
    for i in range(5, 0, -1):
        print(f"  starting in {i}...")
        time.sleep(1)
    print()

    x, y = SCROLL_TARGETS_LOGICAL[0]
    rx, ry, rw, rh = CHAT_REGION_LOGICAL
    print(f"Cursor target: ({x}, {y})")
    print(f"Diff region:   ({rx}, {ry}) {rw}x{rh}")
    print()

    results: dict[tuple[str, str], tuple[float, bool]] = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for name, fn in methods:
            for condition_label, idle in conditions:
                if condition_label == "suspended" and args.idle_seconds <= 0:
                    continue
                print(f"[{condition_label.upper():9}] {name}")
                try:
                    d, ok = run_method_under_condition(
                        name, fn, x, y, tmpdir, idle, condition_label,
                    )
                    results[(name, condition_label)] = (d, ok)
                    print(f"  → diff={d:5.1f}  {'✓ SCROLLED' if ok else '✗ no change'}")
                except subprocess.CalledProcessError as e:
                    print(f"  ❌ failed: {e}")
                    results[(name, condition_label)] = (-1.0, False)
                except Exception as e:
                    print(f"  ❌ raised: {type(e).__name__}: {e}")
                    results[(name, condition_label)] = (-1.0, False)
                print()

    # ---- Results table ----
    print("=" * 76)
    print("RESULTS")
    print("=" * 76)
    print(f"  {'Method':<42}  {'fresh':>12}  {'suspended':>12}")
    print(f"  {'-'*42}  {'-'*12}  {'-'*12}")
    for name, _ in methods:
        cells = []
        for cond in ("fresh", "suspended"):
            if (name, cond) not in results:
                cells.append("—")
                continue
            d, ok = results[(name, cond)]
            if d < 0:
                cells.append("FAIL")
            else:
                marker = "✓" if ok else "✗"
                cells.append(f"{marker} {d:5.1f}")
        print(f"  {name:<42}  {cells[0]:>12}  {cells[1]:>12}")
    print()

    # ---- Verdict ----
    if args.idle_seconds <= 0:
        print("Skipped suspended pass. Re-run without --idle-seconds 0 to test the "
              "production failure scenario.")
        return

    production_susp = results.get(("M1 unphased LINE (production)", "suspended"))
    if production_susp is not None and not production_susp[1]:
        print("✓ Reproduced the bug — production method (M1) failed while suspended.")
    elif production_susp is not None:
        print("⚠ Did NOT reproduce the bug — M1 worked even when suspended.")
        print("  Either --idle-seconds wasn't long enough, or your machine isn't "
              "suspending the way the production failure does. Try")
        print("  --idle-seconds 15, or move the terminal to another Space so")
        print("  Cowork sits truly idle while the harness waits.")

    winners_susp = [
        name for (name, cond), (_, ok) in results.items()
        if cond == "suspended" and ok
    ]
    print()
    if winners_susp:
        print(f"Methods that worked while suspended ({len(winners_susp)}):")
        for n in winners_susp:
            print(f"  ✓ {n}")
        print()
        print("Pick the simplest one that worked — that's the one to port into")
        print("capture.py's scroll_chat_to_top() in place of the unphased loop.")
    else:
        print("⚠ NO method scrolled while suspended.")
        print("  → Phased events do NOT bypass the renderer suspend on this machine.")
        print("  → The wake-Cowork step is the real lever — wake_chromium_render()")
        print("    needs a different approach (e.g. AXRaise on a transient sub-window,")
        print("    or a real activate cycle through Finder) rather than the event-")
        print("    payload changes tested here.")


if __name__ == "__main__":
    main()
