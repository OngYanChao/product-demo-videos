#!/usr/bin/env python3
"""Test that LINE scroll-wheel works on BOTH main chat AND right document panel.

The production scroll_chat_to_top targets two regions: the main chat on the
left, and any document/artifact panel on the right (when Cowork opens a
Google Drive doc alongside the chat). Each panel is its own scrollable
region. This test verifies that the LINE-scroll-wheel method scrolls each
independently.

PREREQUISITE:
  1. Open Cowork desktop.
  2. Open a task that has produced BOTH:
       - A long chat (left side)
       - A document/artifact panel open on the right side (Google Drive
         document or similar)
  3. Scroll BOTH panels to the BOTTOM manually.
  4. Keep Cowork visible.

Then run:
  python3 news-pipeline/tools/test_scroll_both.py
"""

from __future__ import annotations

import subprocess
import sys
import time
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture import osascript  # noqa: E402


# Per-target test config. Each target has cursor coords (where to scroll)
# and a diff region (what area to compare for change detection).
TARGETS = [
    {
        "name": "main chat (left)",
        "cursor":      (700, 500),
        "diff_region": (400, 200, 500, 700),   # x, y, w, h — left chat area
    },
    {
        "name": "right panel (document)",
        "cursor":      (1300, 500),
        "diff_region": (1100, 200, 500, 700),  # right panel area
    },
]


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


def line_scroll_up(x: int, y: int, n_events: int = 80) -> None:
    """The confirmed-working scroll method: LINE-unit scroll-wheel events.

    Move cursor over (x, y), then post n_events × 10 positive-delta LINE
    scroll events. Scrolls the element under the cursor toward the top.
    """
    from Quartz import CGEventCreateScrollWheelEvent, CGEventPost
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitLine
    subprocess.run(["cliclick", f"m:{x},{y}"], check=True)
    time.sleep(0.1)
    for _ in range(n_events):
        event = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitLine, 1, 10)
        CGEventPost(kCGHIDEventTap, event)
        time.sleep(0.015)


def main() -> None:
    print("Test scroll on both chat + document panels")
    print("=" * 64)
    print()
    print("Setup needed:")
    print("  - Cowork visible")
    print("  - Task with chat AND right-side document panel both open")
    print("  - Both panels scrolled to the BOTTOM")
    print()
    for i in range(5, 0, -1):
        print(f"  starting in {i}...")
        time.sleep(1)
    print()

    osascript('tell application "Claude" to activate')
    time.sleep(0.8)

    results = []
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for tgt in TARGETS:
            name = tgt["name"]
            cx, cy = tgt["cursor"]
            rx, ry, rw, rh = tgt["diff_region"]
            print(f"[TARGET] {name}")
            print(f"  Cursor:      ({cx}, {cy})")
            print(f"  Diff region: ({rx}, {ry}) {rw}x{rh}")

            try:
                before = tmpdir / f"{name.replace(' ', '_')}_before.png"
                screencap_region(rx, ry, rw, rh, before)

                line_scroll_up(cx, cy)
                time.sleep(1.2)

                after = tmpdir / f"{name.replace(' ', '_')}_after.png"
                screencap_region(rx, ry, rw, rh, after)

                d = content_diff(before, after)
                worked = d > 10.0
                results.append((name, d, worked))
                print(f"  → diff={d:.1f}  {'✓ SCROLLED' if worked else '✗ no change'}")

                # Save persistent copies for visual inspection
                persistent_before = Path(f"/tmp/scroll_both_{name.replace(' ', '_').replace('(', '').replace(')', '')}_before.png")
                persistent_after = Path(f"/tmp/scroll_both_{name.replace(' ', '_').replace('(', '').replace(')', '')}_after.png")
                import shutil
                shutil.copy(before, persistent_before)
                shutil.copy(after, persistent_after)
                print(f"  → saved {persistent_before.name} + {persistent_after.name}")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ failed: {e}")
                results.append((name, -1.0, False))
            print()
            time.sleep(0.5)

    print("=" * 64)
    print("RESULTS")
    print("=" * 64)
    for name, d, worked in results:
        d_s = "FAIL" if d < 0 else f"{d:.1f}"
        status = "YES" if worked else "no"
        print(f"  {name:<35}  diff={d_s:>6}  scrolled={status}")
    print()
    print("Visual inspection files at /tmp/scroll_both_*.png")
    print("(double-check the 'no change' cases — sometimes both panels look")
    print(" similar even when one scrolled; visual confirmation beats the diff)")


if __name__ == "__main__":
    main()
