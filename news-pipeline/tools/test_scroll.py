#!/usr/bin/env python3
"""Test scroll-to-top methods against Cowork desktop interactively.

PURPOSE: figure out which (if any) of our scroll methods actually scrolls
Cowork's chat. The polling/recording loop in capture.py has no way to verify
this on its own — visual confirmation is the only signal.

HOW TO USE:
  1. Open Cowork desktop and navigate to a chat that has more content than
     fits in one viewport (a previous Cowork task with a long brief works).
  2. Manually scroll the chat all the way DOWN.
  3. Make Cowork the visible app (full screen).
  4. From a terminal, run:
       python3 news-pipeline/tools/test_scroll.py
  5. The script will try 5 different scroll methods, one at a time, with
     a pause between each so you can watch.
  6. After each method, the chat should snap toward the top if the method
     works. If it doesn't move, that method failed.
  7. Between methods, manually scroll back to the bottom so each test
     starts from the same state.
  8. At the end, tell me which method numbers worked.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

# Reuse the canonical coords from capture.py so we test the same targets.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture import osascript, SCROLL_TARGETS_LOGICAL  # noqa: E402


def activate_claude() -> None:
    osascript('tell application "Claude" to activate')
    time.sleep(0.8)


def method_1_line_scroll(x: int, y: int) -> None:
    """CGEvent scroll wheel, LINE units — 60 events × 10 lines."""
    from Quartz import CGEventCreateScrollWheelEvent, CGEventPost
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitLine
    subprocess.run(["cliclick", f"m:{x},{y}"], check=True)
    time.sleep(0.1)
    for _ in range(60):
        event = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitLine, 1, 10)
        CGEventPost(kCGHIDEventTap, event)
        time.sleep(0.015)


def method_2_pixel_scroll(x: int, y: int) -> None:
    """CGEvent scroll wheel, PIXEL units — 40 events × 400 pixels."""
    from Quartz import CGEventCreateScrollWheelEvent, CGEventPost
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitPixel
    subprocess.run(["cliclick", f"m:{x},{y}"], check=True)
    time.sleep(0.1)
    for _ in range(40):
        event = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitPixel, 1, 400)
        CGEventPost(kCGHIDEventTap, event)
        time.sleep(0.015)


def method_3_home(x: int, y: int) -> None:
    """Click for focus, then Home key (key code 115)."""
    subprocess.run(["cliclick", f"c:{x},{y}"], check=True)
    time.sleep(0.15)
    osascript('tell application "System Events" to key code 115')


def method_4_cmd_up(x: int, y: int) -> None:
    """Click for focus, then cmd+Up arrow (key code 126 + command modifier)."""
    subprocess.run(["cliclick", f"c:{x},{y}"], check=True)
    time.sleep(0.15)
    osascript('tell application "System Events" to key code 126 using {command down}')


def method_5_pageup_barrage(x: int, y: int) -> None:
    """Click for focus, then 40 Page Up key presses (key code 116)."""
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
    """Simulate a finger-drag from low → high (drags content up = scrolls up)."""
    # cliclick: dd:x,y = drag-down (mouse down at coord),
    #           m:x,y  = move while held? Actually drag continue is implicit
    #           du:x,y = drag-up (mouse up at coord)
    # Drag from below the cursor up to above it — content scrolls UP.
    start_y = y + 200
    end_y = y - 200
    subprocess.run(["cliclick", f"dd:{x},{start_y}", "w:80", f"du:{x},{end_y}"], check=True)
    time.sleep(0.3)


METHODS = [
    ("CGEvent scroll wheel — LINE units (60 × 10)",      method_1_line_scroll),
    ("CGEvent scroll wheel — PIXEL units (40 × 400)",    method_2_pixel_scroll),
    ("Click + Home key",                                  method_3_home),
    ("Click + cmd+Up",                                    method_4_cmd_up),
    ("Click + Page Up × 40",                              method_5_pageup_barrage),
    ("cliclick drag up (finger-drag simulation)",         method_6_drag_up),
]


def main() -> None:
    print("=" * 64)
    print("Cowork scroll-to-top method tester")
    print("=" * 64)
    print()
    print("BEFORE STARTING:")
    print("  1. Open Cowork with a long chat (one that needs scrolling)")
    print("  2. Manually scroll the chat to the BOTTOM")
    print("  3. Keep Cowork visible")
    print()
    print("Each method will be tried separately. After each one, the chat")
    print("should snap toward the top if that method works. Between tests,")
    print("manually scroll back to bottom so each test starts the same.")
    print()
    x, y = SCROLL_TARGETS_LOGICAL[0]
    print(f"Will scroll at target coords: ({x}, {y})  — main chat region")
    print()
    input("Press Enter when Cowork is ready (scrolled to bottom) >>> ")

    worked: list[int] = []
    for i, (name, method) in enumerate(METHODS, 1):
        print()
        print("-" * 64)
        print(f"METHOD {i}: {name}")
        print("-" * 64)
        input(f"Press Enter to try method {i} >>> ")
        print(f"  Running... (activating Claude, then method {i})")
        try:
            activate_claude()
            method(x, y)
            time.sleep(1.5)
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed with error: {e}")
            continue
        print(f"  Done. Did Cowork's chat scroll up?")
        ans = input(f"    (y/n) >>> ").strip().lower()
        if ans.startswith("y"):
            worked.append(i)
            print(f"  ✓ Method {i} works.")
        else:
            print(f"  ✗ Method {i} did not scroll.")
        print(f"  → Now scroll Cowork's chat back to the BOTTOM before the next test.")

    print()
    print("=" * 64)
    print("RESULTS")
    print("=" * 64)
    if worked:
        print(f"  Working methods: {worked}")
        for i in worked:
            print(f"    {i}. {METHODS[i-1][0]}")
        print()
        print("  → Use any of these in capture.py's scroll_chat_to_top().")
    else:
        print("  No methods worked. We need a different approach entirely.")
        print("  Possibilities: trackpad gesture simulation, Chromium DevTools,")
        print("  or accept that scroll-to-top isn't reliable for Cowork.")


if __name__ == "__main__":
    main()
