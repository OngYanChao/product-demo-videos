#!/usr/bin/env python3
"""Automated scroll method tester — detects scroll via screen region diff.

PREREQUISITE: open Cowork with a long chat conversation, scroll to the
BOTTOM manually. Make sure Cowork is visible. Then run this script.

The script:
  1. For each method (6 total), captures a region of the chat content
     screenshot BEFORE, runs the method, captures AFTER.
  2. Computes mean pixel diff — high diff means content changed = scroll
     happened.
  3. Between methods, tries to scroll back to the BOTTOM using cmd+End +
     Page Down × 30 (best-effort; if that fails the later tests may not
     produce reliable diffs).
  4. Prints a results table.

If multiple methods report high diff, they all work. If only one does,
that's the keeper. If none, scroll-to-top isn't possible on Cowork with
synthetic input — we'd need to switch to gesture simulation or live with
"recording ends at bottom."
"""

from __future__ import annotations

import subprocess
import sys
import time
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture import osascript, SCROLL_TARGETS_LOGICAL  # noqa: E402


CHAT_REGION_LOGICAL = (400, 200, 600, 700)  # x, y, w, h — covers chat content


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
    """Scroll back to the bottom using LINE scroll wheel with negative delta.

    End/Page Down keystrokes don't reliably work on Cowork's chat (Chromium
    WebContents quirk — same reason Home/cmd+Up/PageUp barely scroll). But
    LINE-unit scroll wheel events DO work reliably (confirmed by auto-test).
    So we use the same mechanism that works for scrolling up, just inverted.
    """
    from Quartz import CGEventCreateScrollWheelEvent, CGEventPost
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitLine
    subprocess.run(["cliclick", f"m:{x},{y}"], check=True)
    time.sleep(0.1)
    # 80 events × -10 lines = 800 lines worth of scroll-down. Enough for any
    # conversation length we'll realistically encounter.
    for _ in range(80):
        event = CGEventCreateScrollWheelEvent(
            None, kCGScrollEventUnitLine, 1, -10
        )
        CGEventPost(kCGHIDEventTap, event)
        time.sleep(0.015)
    time.sleep(0.5)


def method_1_line_scroll(x: int, y: int) -> None:
    from Quartz import CGEventCreateScrollWheelEvent, CGEventPost
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitLine
    subprocess.run(["cliclick", f"m:{x},{y}"], check=True)
    time.sleep(0.1)
    for _ in range(60):
        event = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitLine, 1, 10)
        CGEventPost(kCGHIDEventTap, event)
        time.sleep(0.015)


def method_2_pixel_scroll(x: int, y: int) -> None:
    from Quartz import CGEventCreateScrollWheelEvent, CGEventPost
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitPixel
    subprocess.run(["cliclick", f"m:{x},{y}"], check=True)
    time.sleep(0.1)
    for _ in range(40):
        event = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitPixel, 1, 400)
        CGEventPost(kCGHIDEventTap, event)
        time.sleep(0.015)


def method_3_home(x: int, y: int) -> None:
    subprocess.run(["cliclick", f"c:{x},{y}"], check=True)
    time.sleep(0.15)
    osascript('tell application "System Events" to key code 115')


def method_4_cmd_up(x: int, y: int) -> None:
    subprocess.run(["cliclick", f"c:{x},{y}"], check=True)
    time.sleep(0.15)
    osascript('tell application "System Events" to key code 126 using {command down}')


def method_5_pageup_barrage(x: int, y: int) -> None:
    subprocess.run(["cliclick", f"c:{x},{y}"], check=True)
    time.sleep(0.15)
    osascript('''
tell application "System Events"
    repeat 40 times
        key code 116
        delay 0.02
    end repeat
end tell
''')


def method_6_drag_up(x: int, y: int) -> None:
    start_y = y + 200
    end_y = y - 200
    subprocess.run(
        ["cliclick", f"dd:{x},{start_y}", "w:80", f"du:{x},{end_y}"],
        check=True,
    )
    time.sleep(0.3)


METHODS = [
    ("LINE scroll wheel (60 × 10)",        method_1_line_scroll),
    ("PIXEL scroll wheel (40 × 400)",      method_2_pixel_scroll),
    ("Click + Home key",                    method_3_home),
    ("Click + cmd+Up",                      method_4_cmd_up),
    ("Click + Page Up × 40",                method_5_pageup_barrage),
    ("cliclick drag-up",                    method_6_drag_up),
]


def main() -> None:
    print("=" * 68)
    print("Automated Cowork scroll-to-top tester")
    print("=" * 68)
    print()
    print("Will sleep 5s now so you can confirm Cowork is in the right state:")
    print("  - Cowork desktop visible (in front)")
    print("  - A long chat is open (scroll required to see the top)")
    print("  - Chat is scrolled to the BOTTOM (we'll detect scroll-UP changes)")
    print()
    for i in range(5, 0, -1):
        print(f"  starting in {i}...")
        time.sleep(1)
    print()

    x, y = SCROLL_TARGETS_LOGICAL[0]
    rx, ry, rw, rh = CHAT_REGION_LOGICAL
    print(f"Cursor target: ({x}, {y})")
    print(f"Diff region:   ({rx}, {ry}) {rw}x{rh} (chat content area)")
    print()

    results: list[tuple[str, float, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for i, (name, method) in enumerate(METHODS, 1):
            print(f"[METHOD {i}] {name}")
            try:
                activate_claude()
                # Reset chat to bottom (best-effort).
                reset_scroll_to_bottom(x, y)
                time.sleep(0.5)

                before = tmpdir / f"m{i}_before.png"
                screencap_region(rx, ry, rw, rh, before)

                method(x, y)
                time.sleep(1.2)

                after = tmpdir / f"m{i}_after.png"
                screencap_region(rx, ry, rw, rh, after)

                d = content_diff(before, after)
                worked = d > 10.0
                results.append((name, d, worked))
                print(f"  → diff={d:.1f}  {'✓ SCROLLED' if worked else '✗ no change'}")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ failed: {e}")
                results.append((name, -1.0, False))
            time.sleep(0.5)
            print()

    print("=" * 68)
    print("RESULTS")
    print("=" * 68)
    print(f"  {'Method':<40}  {'diff':>8}  {'scrolled?'}")
    print(f"  {'-'*40}  {'-'*8}  {'-'*10}")
    for name, d, worked in results:
        d_s = "FAIL" if d < 0 else f"{d:.1f}"
        print(f"  {name:<40}  {d_s:>8}  {'YES' if worked else 'no'}")
    print()
    winners = [name for name, _, w in results if w]
    if winners:
        print(f"Working methods ({len(winners)}):")
        for n in winners:
            print(f"  ✓ {n}")
    else:
        print("⚠️  NO METHOD SCROLLED THE CHAT.")
        print("    Either: (1) Cowork wasn't set up correctly, (2) chat is too short")
        print("    to require scrolling, or (3) synthetic scroll events truly don't")
        print("    affect Cowork's chat container.")


if __name__ == "__main__":
    main()
