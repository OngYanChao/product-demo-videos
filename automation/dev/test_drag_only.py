#!/usr/bin/env python3
"""Isolated drag-up test — captures full-screen before/after for visual inspection.

We suspect the diff=18.5 reported for the drag method might be from text
SELECTION (drag highlights chat text), not actual scrolling. This script
runs ONLY the drag method, saves full-screen before+after screenshots and
crops of the chat region, then prints the diff so we can compare visually.

PREREQUISITE: open Cowork with a long chat, scroll to the BOTTOM, leave
Cowork visible. Then run:
  python3 automation/dev/test_drag_only.py

Output files:
  /tmp/drag_before.png   — full screen before the drag
  /tmp/drag_after.png    — full screen after the drag
  /tmp/drag_region_before.png  — chat region only, before
  /tmp/drag_region_after.png   — chat region only, after
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture import osascript, SCROLL_TARGETS_LOGICAL  # noqa: E402


CHAT_REGION = (400, 200, 600, 700)
DRAG_TARGET = SCROLL_TARGETS_LOGICAL[0]  # (700, 500)


def screencap_full(out: Path) -> None:
    subprocess.run(["screencapture", "-x", str(out)], check=True, capture_output=True)


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


def main() -> None:
    print("Drag-up isolated test")
    print("=" * 60)
    print()
    print("Setup needed:")
    print("  - Cowork visible with a long chat")
    print("  - Scrolled to the BOTTOM")
    print()
    for i in range(5, 0, -1):
        print(f"  starting in {i}...")
        time.sleep(1)
    print()

    x, y = DRAG_TARGET
    rx, ry, rw, rh = CHAT_REGION

    osascript('tell application "Claude" to activate')
    time.sleep(0.8)

    # Capture before
    print("Capturing BEFORE...")
    screencap_full(Path("/tmp/drag_before.png"))
    screencap_region(rx, ry, rw, rh, Path("/tmp/drag_region_before.png"))

    # Run drag: from y+200 (lower) up to y-200 (higher).
    # cliclick `dd:` = drag down (mouse button DOWN at coord)
    # cliclick `du:` = drag up (mouse button UP at coord)
    # In between, the mouse "drags" along the path.
    start_y = y + 200   # lower starting point
    end_y = y - 200     # upper ending point
    print(f"Dragging from ({x}, {start_y}) UP to ({x}, {end_y})...")
    subprocess.run(
        ["cliclick",
         f"dd:{x},{start_y}",
         "w:80",
         f"du:{x},{end_y}"],
        check=True,
    )
    time.sleep(1.5)

    # Capture after
    print("Capturing AFTER...")
    screencap_full(Path("/tmp/drag_after.png"))
    screencap_region(rx, ry, rw, rh, Path("/tmp/drag_region_after.png"))

    # Compute diff
    full_diff = content_diff(Path("/tmp/drag_before.png"), Path("/tmp/drag_after.png"))
    region_diff = content_diff(
        Path("/tmp/drag_region_before.png"),
        Path("/tmp/drag_region_after.png"),
    )

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"  Full-screen diff: {full_diff:.2f}")
    print(f"  Chat-region diff: {region_diff:.2f}")
    print()
    print("Screenshots saved:")
    print("  /tmp/drag_before.png         (full screen, before)")
    print("  /tmp/drag_after.png          (full screen, after)")
    print("  /tmp/drag_region_before.png  (chat region only, before)")
    print("  /tmp/drag_region_after.png   (chat region only, after)")
    print()
    print("Open these files (cmd+click in Finder, or `open /tmp/drag_*.png`)")
    print("and visually compare. If 'after' shows text SELECTED (blue highlight)")
    print("but otherwise the SAME content as 'before', the drag was selecting")
    print("text, not scrolling. If 'after' shows different content (the top of")
    print("the chat), the drag was actually scrolling.")


if __name__ == "__main__":
    main()
