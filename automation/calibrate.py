#!/usr/bin/env python3
"""Calibrate Claude desktop for the shared automation layer.

Run this ONCE before any workflow that drives Claude desktop via
capture.py (news-pipeline; product-demo automated Phase 2 once wired),
and re-run if you switch displays, theme, or Claude desktop is redesigned.

What it does:
  1. Activates Claude desktop and puts it in macOS fullscreen mode.
  2. Detects your main display's logical bounds + Retina scale.
  3. Captures a reference screenshot of the fullscreen window.
  4. Asks you to point out the bottom-bar button's screen coords (the
     MICROPHONE icon visible when Claude is in-chat and idle).
  5. Captures the button region in IDLE (microphone) state.
  6. Asks you to trigger a streaming response, captures the same
     region in STREAMING (stop) state.
  7. Verifies the two crops differ enough to be reliably distinguishable.
  8. Saves calibration/claude-desktop.json + reference PNGs.

Outputs:
  automation/calibration/claude-desktop.json
  automation/calibration/window_full.png
  automation/calibration/send-idle.png        (microphone crop)
  automation/calibration/send-streaming.png   (stop crop)

Usage:
  python3 automation/calibrate.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ---------- paths ----------
REPO_ROOT = Path(__file__).resolve().parents[1]
AUTOMATION_ROOT = REPO_ROOT / "automation"
CALIB_DIR = AUTOMATION_ROOT / "calibration"
CALIB_JSON = CALIB_DIR / "claude-desktop.json"

BTN_RADIUS = 30  # 60×60 logical-point crop around the button center


def run(cmd, check=True):
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def osascript(script: str) -> str:
    r = run(["osascript", "-e", script])
    return r.stdout.strip()


def enter_fullscreen():
    """Activate Claude desktop, ensure a window exists, enter macOS fullscreen."""
    script = """
    tell application "Claude" to activate
    delay 0.8
    tell application "System Events"
      tell process "Claude"
        set frontmost to true
        if (count of windows) = 0 then
          keystroke "n" using command down
          delay 1
        end if
        try
          set value of attribute "AXFullScreen" of window 1 to true
        on error
          keystroke "f" using {control down, command down}
        end try
      end tell
    end tell
    delay 2.5
    """
    osascript(script)


def screencap_region(x: int, y: int, w: int, h: int, out: Path):
    """Capture a region of the currently-visible Space. NOT cross-Space safe."""
    run(["screencapture", "-x", "-R", f"{x},{y},{w},{h}", str(out)])


def find_claude_main_window() -> dict | None:
    """Find Claude's main content window. Returns dict with 'id' and 'bounds'.

    Picks the largest layer-0 window owned by 'Claude' with reasonable
    dimensions. This is the chat content area (typically Y=34 when in
    fullscreen mode, below a 34pt overlay strip).
    """
    from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionAll, kCGNullWindowID
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
    candidates = []
    for w in windows:
        if w.get("kCGWindowOwnerName") != "Claude":
            continue
        if w.get("kCGWindowLayer", 0) != 0:
            continue
        b = dict(w.get("kCGWindowBounds", {}))
        if b.get("Width", 0) < 500 or b.get("Height", 0) < 500:
            continue
        area = b["Width"] * b["Height"]
        candidates.append((area, int(w.get("kCGWindowNumber")), b))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    _, wid, bounds = candidates[0]
    return {"id": wid, "bounds": bounds}


def screencap_claude_window(out: Path) -> dict:
    """Activate Claude (so its Space is visible) then capture its main window.

    Uses shell `screencapture -l <wid>`. Window IDs are re-resolved on each
    call since Claude may have been quit/relaunched between captures.
    Returns the window dict for crop coordinate conversion.
    """
    osascript('tell application "Claude" to activate')
    time.sleep(1.2)  # Space-switch animation + paint settle
    win = find_claude_main_window()
    if not win:
        raise RuntimeError(
            "Could not find Claude's main window. Is Claude.app running and "
            "does it have a window open?"
        )
    run(["screencapture", "-x", "-o", "-l", str(win["id"]), str(out)])
    return win


def detect_screen_bounds() -> tuple[int, int, int, int, float]:
    """Return (x, y, w, h) of the main display in logical points + Retina scale.

    Uses a full-screen + small-region capture probe. Doesn't depend on Claude.
    """
    from PIL import Image
    full = CALIB_DIR / "_screen_probe.png"
    run(["screencapture", "-x", str(full)])
    phys_w, phys_h = Image.open(full).size
    full.unlink()
    probe = CALIB_DIR / "_scale_probe.png"
    screencap_region(0, 0, 100, 100, probe)
    scale = Image.open(probe).size[0] / 100.0
    probe.unlink()
    log_w = int(round(phys_w / scale))
    log_h = int(round(phys_h / scale))
    return 0, 0, log_w, log_h, scale


def crop_button(window_png: Path, btn_x: int, btn_y: int,
                window_bounds: dict, scale: float, out: Path) -> Path:
    """Crop the button region from a Claude-window screencap to `out`.
    btn_x/y are screen-logical (cmd+shift+4 coords).
    window_bounds is from find_claude_main_window().
    """
    from PIL import Image
    img = Image.open(window_png)
    win_x = window_bounds["X"]
    win_y = window_bounds["Y"]
    rel_x = (btn_x - win_x) * scale
    rel_y = (btn_y - win_y) * scale
    r = BTN_RADIUS * scale
    box = (int(rel_x - r), int(rel_y - r), int(rel_x + r), int(rel_y + r))
    img.crop(box).save(out)
    return out


def read_xy(prompt_text: str) -> tuple[int, int]:
    while True:
        try:
            return parse_xy(input(prompt_text))
        except (ValueError, IndexError):
            print("      Bad input — try again as 'x y' (e.g. '1800 1150').")


def mean_pixel_diff(a: Path, b: Path) -> float:
    from PIL import Image, ImageChops, ImageStat
    ia = Image.open(a).convert("RGB")
    ib = Image.open(b).convert("RGB")
    diff = ImageChops.difference(ia, ib)
    stat = ImageStat.Stat(diff)
    return sum(stat.mean) / len(stat.mean)


def parse_xy(s: str) -> tuple[int, int]:
    parts = s.replace(",", " ").split()
    if len(parts) < 2:
        raise ValueError("need two numbers")
    return int(float(parts[0])), int(float(parts[1]))


def banner(title: str):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def main():
    CALIB_DIR.mkdir(parents=True, exist_ok=True)

    banner("automation: Claude desktop calibration")
    print(
        "One-time setup. This will activate Claude desktop and put it in\n"
        "macOS FULLSCREEN mode (its own Space). You'll calibrate against\n"
        "the bottom-bar microphone/stop icon.\n\n"
        "Spaces tips while running this script:\n"
        "  - To switch between Claude (fullscreen) and your terminal:\n"
        "    3-finger swipe left/right, or ctrl+left/right arrow.\n"
        "  - cmd+shift+4 (coordinate readout) works in any Space.\n"
    )
    input("Press Enter to start...")

    print("\n[1/5] Activating + fullscreening Claude desktop...")
    try:
        enter_fullscreen()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ AppleScript failed:\n{e.stderr or e.stdout}")
        print("\nLikely causes:")
        print("  - Claude.app not installed at /Applications/Claude.app")
        print("  - Terminal lacks Accessibility permission")
        print("    (System Settings → Privacy & Security → Accessibility)")
        sys.exit(1)

    print("\n[2/5] Detecting screen bounds + Retina scale...")
    x, y, w, h, scale = detect_screen_bounds()
    print(f"      Display: {w}×{h} logical points")
    print(f"      Pixel scale: {scale:g}× ({'Retina' if scale > 1 else 'standard DPI'})")
    print(f"      Physical capture: {int(w*scale)}×{int(h*scale)} pixels")

    print("\n[3/5] Capturing reference screenshot of Claude window...")
    print("      (Will briefly switch to Claude's Space to capture.)")
    window_png = CALIB_DIR / "window_full.png"
    win = screencap_claude_window(window_png)
    print(f"      Saved: {window_png.relative_to(REPO_ROOT)}")
    print(f"      Window: id={win['id']} bounds={win['bounds']}")

    print("\n[4/5] Idle state — find the MICROPHONE button")
    print(
        "      Claude is currently active. Find the MICROPHONE icon (the\n"
        "      icon that shows when Claude is NOT responding). It may be:\n"
        "        - centered on screen (fresh task layout)\n"
        "        - at the bottom-right of the input bar (in-chat layout)\n"
        "      Either is fine — pick whichever state you can see.\n"
        "\n"
        "      Use cmd+shift+4 to read its center coords (works in any Space):\n"
        "        1. Press cmd+shift+4 (don't drag — just hover)\n"
        "        2. Hover the crosshair over the microphone center\n"
        "        3. Read the (x, y) tooltip\n"
        "        4. Press Escape to cancel\n"
        "        5. Swipe back to terminal and type below\n"
    )
    mic_x, mic_y = read_xy("Microphone button (x y): ")
    # Re-capture Claude window (activates Claude → captures across Spaces)
    win = screencap_claude_window(window_png)
    idle_png = CALIB_DIR / "send-idle.png"
    crop_button(window_png, mic_x, mic_y, win["bounds"], scale, idle_png)
    print(f"      Saved: {idle_png.relative_to(REPO_ROOT)}  (mic at {mic_x},{mic_y})")

    print("\n[5/5] Streaming state — find the STOP button")
    print(
        "      Now we capture the STOP icon. IMPORTANT: it may be in a\n"
        "      DIFFERENT position than the microphone — that's normal.\n"
        "\n"
        "      What to do:\n"
        "        1. Swipe to Claude\n"
        "        2. Send a LONG prompt (e.g. 'write a 1000-word essay on\n"
        "           the history of jazz'). Long enough that you'll still be\n"
        "           streaming after the steps below.\n"
        "        3. While streaming, press cmd+shift+4 and hover over the\n"
        "           STOP icon. Read the (x, y) tooltip. Press Escape.\n"
        "        4. Swipe back to terminal, type the coords.\n"
        "\n"
        "      The script will then briefly switch back to Claude to\n"
        "      capture the stop icon. Streaming must still be active.\n"
    )
    stop_x, stop_y = read_xy("Stop button (x y): ")
    streaming_full = CALIB_DIR / "window_streaming.png"
    win = screencap_claude_window(streaming_full)
    streaming_png = CALIB_DIR / "send-streaming.png"
    crop_button(streaming_full, stop_x, stop_y, win["bounds"], scale, streaming_png)
    print(f"      Saved: {streaming_png.relative_to(REPO_ROOT)}  (stop at {stop_x},{stop_y})")

    # ---- Self-test: validate that the mic location actually changes between states.
    # We use the streaming_full screencap we just took (Claude is mid-response).
    # If the mic location during streaming differs significantly from idle ref,
    # detection will work. If not, the chosen mic position isn't state-sensitive.
    print("\nSelf-test: is the mic location state-sensitive?")
    mic_in_stream = Path(tempfile.mktemp(suffix=".png"))
    crop_button(streaming_full, mic_x, mic_y, win["bounds"], scale, mic_in_stream)
    mic_change = mean_pixel_diff(mic_in_stream, idle_png)
    mic_in_stream.unlink()
    print(f"      mic-region during STREAMING vs idle ref: diff={mic_change:.1f}")
    if mic_change > 20:
        print("      ✓ Strong — mic position disappears/changes during streaming.")
    elif mic_change > 8:
        print("      ⚠️  Weak — detection may need threshold tuning.")
    else:
        print("      ❌ Mic region barely changes between states. Detection will be")
        print("         ambiguous. Pick a mic position that's visually absent during")
        print("         streaming (e.g. the bottom-bar mic, not a static UI element).")

    print("\nVerifying reference quality...")
    # If mic and stop are at the same coords, compute diff between them as before.
    # If they're at different coords, the diff between the two crops is less
    # meaningful — instead we'll trust that each ref captures its own state.
    if (mic_x, mic_y) == (stop_x, stop_y):
        diff = mean_pixel_diff(idle_png, streaming_png)
        print(f"      Same location — mean per-pixel diff (0–255): {diff:.1f}")
        if diff < 5:
            print("      ⚠️  Very low diff — both crops look identical. Re-run.")
        elif diff < 15:
            print("      ⚠️  Low but workable.")
        else:
            print("      ✓ Strong diff signal.")
    else:
        diff = None
        dx = stop_x - mic_x
        dy = stop_y - mic_y
        print(f"      Mic and stop are at DIFFERENT locations "
              f"(offset Δx={dx}, Δy={dy} logical pt).")
        print(f"      capture.py will sample both regions independently.")

    cfg = {
        "window": {"x": x, "y": y, "width": w, "height": h, "mode": "fullscreen"},
        "claude_window_bounds": win["bounds"],  # last captured window bounds (X, Y, Width, Height)
        "pixel_scale": scale,
        "mic_button": {
            "center_logical": {"x": mic_x, "y": mic_y},
            "radius_logical": BTN_RADIUS,
            "idle_crop": str(idle_png.relative_to(AUTOMATION_ROOT)),
        },
        "stop_button": {
            "center_logical": {"x": stop_x, "y": stop_y},
            "radius_logical": BTN_RADIUS,
            "streaming_crop": str(streaming_png.relative_to(AUTOMATION_ROOT)),
        },
        "same_location": (mic_x, mic_y) == (stop_x, stop_y),
        "verified_mean_diff": round(diff, 2) if diff is not None else None,
        "calibrated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    CALIB_JSON.write_text(json.dumps(cfg, indent=2))

    banner("Done")
    print(f"Calibration → {CALIB_JSON.relative_to(REPO_ROOT)}")
    print(f"Next:        python3 automation/capture.py <prompt-file>")


if __name__ == "__main__":
    main()
