#!/usr/bin/env python3
"""Isolated test for HammerSpoon-style smooth scroll-down.

Mimics the user's HammerSpoon autoscroll config exactly:
  - 120 Hz tick rate
  - 300 px/s target speed
  - Accumulator pattern
  - Pixel-mode scroll events with negative Y (= scroll down)

Auto-stops when chat content stops changing.

PREREQUISITE: open Cowork with a long chat, scroll to the TOP, leave Cowork
visible. Then run:
  python3 automation/dev/test_smooth_scroll.py [pps]

  pps = optional pixels-per-second speed override (default 300, same as
        the HammerSpoon default).
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture import (  # noqa: E402
    osascript, SCROLL_TARGETS_LOGICAL, mean_pixel_diff,
    SMOOTH_SCROLL_TICK_HZ,
    SMOOTH_SCROLL_MAX_DURATION_S,
    SMOOTH_SCROLL_CHECK_INTERVAL_S,
    SMOOTH_SCROLL_UNCHANGED_THRESHOLD,
    SMOOTH_SCROLL_UNCHANGED_FRAMES_TO_STOP,
)


def smooth_scroll_with_region(
    pps: float, target_x: int, target_y: int,
    region: tuple, tmpdir: Path,
) -> tuple:
    return _smooth_scroll(pps, target_x, target_y, region, tmpdir)


def _smooth_scroll(
    pps: float, target_x: int, target_y: int,
    region: tuple, tmpdir: Path,
) -> tuple:
    """Smooth scroll with detailed tick-timing diagnostics.

    Uses absolute-time scheduling + background-thread end-detection +
    kCGScrollWheelEventIsContinuous flag on each event (tells Chromium
    these are part of a continuous gesture, not discrete wheel clicks,
    so Chromium doesn't animate-tween between them).

    Returns (elapsed, events_posted, pixels_scrolled, tick_intervals_ms).
    """
    import threading
    from Quartz import (
        CGEventCreateScrollWheelEvent, CGEventPost,
        CGEventSetIntegerValueField,
    )
    from Quartz.CoreGraphics import (
        kCGHIDEventTap, kCGScrollEventUnitPixel,
    )
    # kCGScrollWheelEventIsContinuous = 88 (field index). PyObjC may not
    # expose the constant by name in older versions, so use the integer.
    try:
        from Quartz.CoreGraphics import kCGScrollWheelEventIsContinuous
    except ImportError:
        kCGScrollWheelEventIsContinuous = 88

    subprocess.run(["cliclick", f"m:{target_x},{target_y}"], check=True)
    time.sleep(0.15)

    # Background end-detection (doesn't block scroll loop)
    stop_event = threading.Event()
    bottom_event = threading.Event()

    def detection_loop():
        sample = tmpdir / f"_sample_{target_x}_{target_y}.png"
        last = tmpdir / f"_last_{target_x}_{target_y}.png"
        unchanged = 0
        rx, ry, rw, rh = region
        while not stop_event.is_set():
            try:
                subprocess.run(
                    ["screencapture", "-x", "-R", f"{rx},{ry},{rw},{rh}", str(sample)],
                    check=True, capture_output=True,
                )
                if last.exists():
                    diff = mean_pixel_diff(sample, last)
                    if diff < SMOOTH_SCROLL_UNCHANGED_THRESHOLD:
                        unchanged += 1
                        if unchanged >= SMOOTH_SCROLL_UNCHANGED_FRAMES_TO_STOP:
                            bottom_event.set()
                            return
                    else:
                        unchanged = 0
                import shutil
                shutil.copy(sample, last)
            except Exception:
                pass
            stop_event.wait(SMOOTH_SCROLL_CHECK_INTERVAL_S)

    detector = threading.Thread(target=detection_loop, daemon=True)
    detector.start()

    tick_interval = 1.0 / SMOOTH_SCROLL_TICK_HZ
    start = time.monotonic()
    deadline = start + SMOOTH_SCROLL_MAX_DURATION_S
    next_tick = start
    accumulator = 0.0
    events_posted = 0
    pixels_scrolled = 0
    tick_times = []  # absolute monotonic at start of each tick
    last_tick_t = start

    while time.monotonic() < deadline and not bottom_event.is_set():
        accumulator += pps / SMOOTH_SCROLL_TICK_HZ
        whole = int(accumulator)
        if whole > 0:
            event = CGEventCreateScrollWheelEvent(
                None, kCGScrollEventUnitPixel, 1, -whole
            )
            # Mark as a continuous gesture so Chromium treats this as
            # smooth-pan input (no per-event animation) instead of a
            # discrete mouse-wheel click.
            CGEventSetIntegerValueField(event, kCGScrollWheelEventIsContinuous, 1)
            CGEventPost(kCGHIDEventTap, event)
            accumulator -= whole
            events_posted += 1
            pixels_scrolled += whole

        now = time.monotonic()
        tick_times.append((now - last_tick_t) * 1000.0)  # ms
        last_tick_t = now

        next_tick += tick_interval
        remaining = next_tick - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)

    stop_event.set()
    detector.join(timeout=1.0)

    elapsed = time.monotonic() - start
    return elapsed, events_posted, pixels_scrolled, tick_times


def main() -> None:
    pps = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0
    print(f"Smooth scroll test — {pps} px/s, {SMOOTH_SCROLL_TICK_HZ} Hz tick")
    print("=" * 60)
    print()
    print("Setup needed:")
    print("  - Cowork visible with a long chat AND an open document panel")
    print("  - BOTH panels scrolled to the TOP")
    print()
    for i in range(5, 0, -1):
        print(f"  starting in {i}...")
        time.sleep(1)
    print()

    osascript('tell application "Claude" to activate')
    time.sleep(0.8)

    # Auto-detect chat/doc boundary so cursor lands at the right edge of each
    # panel regardless of how the user has resized them.
    from capture import refresh_scroll_targets  # noqa: E402
    refresh_scroll_targets()
    print(f"Cursor positions after layout detection: {SCROLL_TARGETS_LOGICAL}")
    print()

    targets = [
        ("main chat",       SCROLL_TARGETS_LOGICAL[0], (400, 400, 600, 500)),
        ("document panel",  SCROLL_TARGETS_LOGICAL[1], (1100, 400, 500, 500)),
    ]

    all_results = []
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for name, (x, y), region in targets:
            print(f"--- {name} at cursor ({x}, {y}) ---")
            # Patch the detection region for this call by temporarily
            # rebinding it. (The detection_loop closes over `region` from
            # the function scope.)
            # Simpler: just inline the function with the desired region.
            elapsed, events, pixels, tick_times = smooth_scroll_with_region(
                pps, x, y, region, tmpdir
            )
            all_results.append((name, elapsed, events, pixels, tick_times))
            print(f"  Done: {elapsed:.2f}s, {events} events, ~{pixels}px scrolled "
                  f"(effective {pixels/elapsed:.0f} px/s)")
            print()
            time.sleep(0.5)

    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    for name, elapsed, events, pixels, tick_times in all_results:
        print()
        print(f"[{name}]")
        print(f"  Duration:        {elapsed:.2f}s")
        print(f"  Events posted:   {events}")
        print(f"  Pixels scrolled: ~{pixels}px")
        print(f"  Average rate:    {pixels/elapsed:.1f} px/s (target {pps})")
        if tick_times:
            import statistics
            intervals = tick_times[1:]
            intervals_sorted = sorted(intervals)
            n = len(intervals)
            p99 = intervals_sorted[int(n * 0.99)] if n else 0
            pauses = [t for t in intervals if t > 20.0]
            print(f"  Tick: median={statistics.median(intervals):.2f}ms  "
                  f"p99={p99:.2f}ms  max={max(intervals):.2f}ms  "
                  f"stdev={statistics.stdev(intervals):.2f}ms  "
                  f"pauses>20ms={len(pauses)}")


if __name__ == "__main__":
    main()
