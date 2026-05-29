#!/usr/bin/env python3
"""Phase 2 capture — automated Claude desktop screen recording.

Reads a prompt from a text file, drives Claude desktop via keystroke
automation, records the screen until Claude stops streaming, saves the
raw MP4 plus a metadata manifest.

Workflow:
  1. Parse args (prompt-file path)
  2. Load calibration JSON
  3. Find the next free recordings/N<N>/ slot
  4. Activate Claude desktop (fullscreen Space comes into view)
  5. Open a new chat (cmd+N)
  6. Start ffmpeg recording the screen (background process)
  7. Type prompt via cliclick (human-cadence delays)
  8. Press Enter — Claude starts streaming
  9. Wait for streaming to begin (stop-icon appears at calibrated coord)
 10. Poll the stop-region every 200ms vs the streaming reference image
 11. After 3 consecutive non-matches (600ms), declare done
 12. Send 'q' to ffmpeg → graceful stop
 13. Write recordings/N<N>/raw.mp4 + manifest.json

Usage:
  python3 automation/capture.py path/to/prompt.txt
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Force stdout to be line-buffered AND auto-flushing so the log file we write
# to in background mode reflects real-time progress. Without this, prints can
# sit in Python's buffer and only flush at process exit — which makes it look
# (in the log) like a bunch of things happened at the same instant when they
# actually happened seconds or minutes apart.
sys.stdout.reconfigure(line_buffering=True, write_through=True)
sys.stderr.reconfigure(line_buffering=True, write_through=True)


def _install_shutdown_handlers():
    """Route SIGTERM to the same path as SIGINT (Ctrl+C).

    Without this, an external `kill <pid>`, a parent process going down,
    or Claude Code's tool-interrupt mechanism would terminate Python
    without running the `finally` block — leaving ffmpeg to be killed
    abruptly and producing a corrupt MP4.
    """
    def _to_keyboard_interrupt(signum, frame):
        raise KeyboardInterrupt(f"received signal {signum}")
    signal.signal(signal.SIGTERM, _to_keyboard_interrupt)
    # SIGHUP fires when the controlling terminal closes; same treatment.
    try:
        signal.signal(signal.SIGHUP, _to_keyboard_interrupt)
    except (AttributeError, ValueError):
        pass  # SIGHUP not available on this platform / in this context


_install_shutdown_handlers()

# ---------- paths ----------
REPO_ROOT = Path(__file__).resolve().parents[1]
AUTOMATION_ROOT = REPO_ROOT / "automation"
CALIB_DIR = AUTOMATION_ROOT / "calibration"
CALIB_JSON = CALIB_DIR / "claude-desktop.json"
# Default recording slot directory. Defaults to news-pipeline's location for
# backward compatibility — Pass 2 (Workflow A integration) will make this a
# CLI arg so product-demo can target "screen recordings/V<N>/" instead.
RECORDINGS_DIR = REPO_ROOT / "news-pipeline" / "recordings"

# ---------- tuning ----------
POLL_INTERVAL_S = 0.2          # 5×/sec polling rate
DEBOUNCE_FRAMES = 3            # consecutive non-matches before declaring done
STREAMING_START_TIMEOUT_S = 8  # how long to wait for streaming to start
MAX_RECORDING_S = 1800         # 30-minute safety cap (Cowork multi-phase tasks can hit 15-20 min)
FFMPEG_FRAMERATE = 60
# avfoundation screen device index is auto-detected at runtime (it shifts
# when USB cameras connect/disconnect — hardcoding it is brittle).

# Freeze watchdog — abort the recording if the screen sits TOTALLY static
# during the post-streaming sequence (scroll-up + smooth-scroll-down). NOT
# armed during streaming itself, because Cowork's MCP tool calls often
# produce zero UI motion for 60-120s straight (no spinner, no streaming
# text, just a static "Running …" state) — those are legitimate, not stuck.
#
# Threshold is set low: real motion (cursor moves, scroll events, animated
# dots) registers above it and resets the timer; only a fully stuck screen
# (no cursor change, no scroll, nothing) accumulates to TIMEOUT.
FREEZE_WATCHDOG_TIMEOUT_S = 30.0            # seconds of zero-change before abort
FREEZE_WATCHDOG_CHECK_INTERVAL_S = 1.5      # sample cadence (intentionally not a
                                            # round multiple of common animation
                                            # rates like 0.5s/1s, so a looping
                                            # animation can't sync our sampling)
FREEZE_WATCHDOG_THRESHOLD = 0.3             # mean pixel diff — essentially identical

# Scroll-up verification — fast-path detection of "scroll-up didn't visibly
# fire" so we abort within ~5s instead of waiting for the 30s freeze watchdog.
# Compares the chat region BEFORE vs AFTER scroll_chat_to_top runs.
#
# Region must be:
#   - HIGH in the chat (y=200-500). When streaming ends, Cowork adds
#     follow-up suggestions / copy buttons / "what next?" UI near the
#     BOTTOM of the chat. Sampling near the bottom (y=600+) sees those
#     UI elements appear/move and falsely registers as a "successful scroll"
#     (saw diff=19 in a run where scroll-up didn't actually fire).
#   - Inside the chat panel width (x=300-900 stays inside chat in both
#     full-width and chat-with-doc-panel layouts)
#   - Tall enough that a real chat scroll (every pixel in the region
#     changes content) produces a HUGE diff (50+), so we can set
#     MIN_DIFF high enough to reject UI-element noise without false negatives
SCROLL_VERIFY_REGION_LOGICAL = (300, 200, 600, 350)
# Park cursor here before BOTH the BEFORE and AFTER snapshots so cursor pixels
# contribute zero to the diff. (50, 50) is top-left corner, in the macOS
# menubar area — guaranteed outside the verify region.
CURSOR_PARK_LOGICAL = (50, 50)
SCROLL_VERIFY_SETTLE_S = 0.8   # let any pending paint flush before the AFTER shot

# Post-wake on-screen gate. wake_chromium_render() reliably brings Cowork back
# to the visible Space (diagnose_wake.py: 3/3 cross-Space; confirmed again in a
# real capture run), but is_onscreen is a WindowServer flag that flips True a
# beat before Chromium's compositor actually paints input — so the old blind
# 0.25s wait scrolled into a window that wasn't painting yet and the events
# queued. We now poll for is_onscreen, then add a compositor settle, then
# scroll. The wake's on-screen confirmation is the success gate; the
# before/after pixel diff is logged for diagnostics but no longer aborts (a
# legitimate scroll-to-top of a short/at-top chat reads low, which used to
# false-abort).
WAKE_ONSCREEN_TIMEOUT_S = 2.5   # max wait for is_onscreen after one wake dance
WAKE_ONSCREEN_POLL_S = 0.1      # poll cadence while waiting
WAKE_COMPOSITOR_SETTLE_S = 0.7  # extra settle after onscreen confirmed, before scroll
WAKE_MAX_ATTEMPTS = 2           # re-dance this many times if onscreen never confirms

# Window-reset flush. After a long streaming session, synthetic scroll events
# posted to Cowork QUEUE and don't paint until a real window/occlusion change —
# a synthetic focus switch (the wake's Cmd+Tab) isn't enough, but the user's
# manual app-switch flushes them. Hiding the app (Cmd+H) is a stronger
# transition — it takes Cowork fully off-screen (occlusion change), forcing a
# recomposite on reshow that flushes the queue. (AXMinimized and Cmd+M are
# no-ops on this Electron window; Cmd+H is the one that works.) Runs inside the
# scroll-up segment that auto-trim removes, so the hide flash never reaches the
# video.
WINDOW_RESET_WAIT_S = 0.8       # settle after the hide and after the reshow

# cliclick typing tuning
TYPE_DELAY_MS = 25             # ms between keystrokes (~40 chars/sec)


def run(cmd, check=True, **kw):
    return subprocess.run(cmd, check=check, capture_output=True, text=True, **kw)


def osascript(script: str) -> str:
    return run(["osascript", "-e", script]).stdout.strip()


def ensure_cowork_frontmost(wait_s: float = 0.6) -> None:
    """Force Claude/Cowork to be the frontmost app and wait for it to settle.

    The post-streaming sequence (refresh_scroll_targets, scroll_chat_to_top,
    smooth_scroll_down) assumes Cowork is on top: screenshots, F19 keystrokes,
    cursor moves, and scroll-wheel events all hit the frontmost window. If
    the user swapped to another app during the run, those operations land on
    the wrong window.

    Idempotent — calling when Cowork is already frontmost is a no-op + sleep.
    """
    try:
        osascript('tell application "Claude" to activate')
    except subprocess.CalledProcessError:
        pass
    # Brief settle so the window-server has time to bring Cowork to the front
    # and route subsequent events to it.
    time.sleep(wait_s)
    print(f"      [frontmost] activated Claude (waited {wait_s}s)")


def _wake_dance() -> None:
    """One Cmd+Tab-away / Cmd+Tab-back / activate cycle.

    Chromium suspends rendering when its NSWindow sits idle/occluded without an
    incoming focus event. The renderer resumes ONLY when the window receives
    `windowDidBecomeKey:`, which fires on a real key-window transition: Cowork
    loses key status → a different normal NSWindow gets key status → Cowork
    regains it.

    What does NOT work: clicking an already-key window, F19/arbitrary
    keystrokes, `activate` when already frontmost, or a Spotlight bounce
    (overlay layer, never takes key status). What DOES work is the app-switcher
    round trip — the user's manual workaround verbatim — which routes through
    the regular NSWindow focus system.

    Caveat: app-switcher overlay briefly visible (~200-400ms). Lives in the
    `streaming_ended → scroll_to_top_done` segment that auto-trim removes.
    """
    # Tab away — Cowork loses key status to whatever app was previously focused.
    try:
        osascript('tell application "System Events" to key code 48 using {command down}')
    except subprocess.CalledProcessError:
        pass
    time.sleep(0.35)
    # Tab back — focus returns to Cowork → windowDidBecomeKey fires → wake.
    try:
        osascript('tell application "System Events" to key code 48 using {command down}')
    except subprocess.CalledProcessError:
        pass
    time.sleep(0.45)
    # Belt-and-suspenders: explicit activate in case the second Cmd+Tab landed
    # somewhere unexpected (e.g. short MRU list when few apps are open).
    try:
        osascript('tell application "Claude" to activate')
    except subprocess.CalledProcessError:
        pass


def wake_chromium_render() -> bool:
    """Wake Cowork's renderer and confirm it's back on-screen before returning.

    Runs _wake_dance(), then polls cowork_window_state() until is_onscreen &&
    is_frontmost (up to WAKE_ONSCREEN_TIMEOUT_S), re-dancing up to
    WAKE_MAX_ATTEMPTS times if it stalls. On confirmation, applies
    WAKE_COMPOSITOR_SETTLE_S — is_onscreen is a WindowServer flag that flips
    True a beat before Chromium's compositor actually paints input, so without
    the settle the caller's scroll events queue (the original bug; see
    diagnose_wake.py).

    Returns True if Cowork was confirmed on-screen, False if every attempt
    failed (caller should treat scrolling as unreliable and rely on its
    pixel-diff verify + retry).
    """
    before = cowork_window_state()
    print(f"      [wake] before: onscreen={before['is_onscreen']} "
          f"frontmost={before['is_frontmost']} (top app: {before['frontmost_owner']})")

    # If Cowork is already on-screen + frontmost there's nothing to wake — the
    # Cmd+Tab dance would just add a visible app-switcher swap for no benefit.
    # Skip straight to the compositor settle. The dance only earns its keep
    # when Cowork is actually occluded.
    if before["is_onscreen"] and before["is_frontmost"]:
        print(f"      [wake] already on-screen + frontmost; skipping dance, "
              f"settling {WAKE_COMPOSITOR_SETTLE_S}s")
        time.sleep(WAKE_COMPOSITOR_SETTLE_S)
        return True

    for attempt in range(1, WAKE_MAX_ATTEMPTS + 1):
        _wake_dance()
        deadline = time.time() + WAKE_ONSCREEN_TIMEOUT_S
        while time.time() < deadline:
            st = cowork_window_state()
            if st["is_onscreen"] and st["is_frontmost"]:
                print(f"      [wake] confirmed on-screen (attempt {attempt}/"
                      f"{WAKE_MAX_ATTEMPTS}); settling {WAKE_COMPOSITOR_SETTLE_S}s "
                      f"for compositor")
                time.sleep(WAKE_COMPOSITOR_SETTLE_S)
                return True
            time.sleep(WAKE_ONSCREEN_POLL_S)
        print(f"      [wake] ⚠️  not on-screen after attempt {attempt}/"
              f"{WAKE_MAX_ATTEMPTS} (waited {WAKE_ONSCREEN_TIMEOUT_S}s)")

    final = cowork_window_state()
    print(f"      [wake] ⚠️  GAVE UP — onscreen={final['is_onscreen']} "
          f"frontmost={final['is_frontmost']} (top app: {final['frontmost_owner']}). "
          f"Scroll events will likely queue.")
    return False


def reset_cowork_window() -> bool:
    """Hide (Cmd+H) → reshow Cowork to FLUSH queued synthetic scroll events.

    After a long streaming session, scroll events posted to Cowork queue and
    don't paint until a real window/occlusion change (the user's manual
    app-switch flushes them; the wake's synthetic Cmd+Tab does not). Hiding the
    app is a stronger transition than a focus switch — the app goes fully
    off-screen (occlusion change), forcing a full recomposite on reshow, which
    flushes the queue.

    Mechanism note: Cowork is Electron, and it ignores BOTH the System Events
    AXMinimized attribute AND Cmd+M (verified — both are no-ops, the window
    stays on-screen). Cmd+H (hide app) DOES work — it flips the window to
    onscreen=False — so that's what we use.

    Cmd+H hides the FRONTMOST app, so we confirm Claude is frontmost first;
    otherwise we'd hide whatever else is in front. Runs in the scroll-up
    segment that auto-trim removes, so the hide flash never reaches the video.
    Returns True if Cowork is confirmed back on-screen afterward.
    """
    # Cmd+H hides whatever is frontmost — make sure that's Claude, not e.g. the
    # terminal/VS Code, or we'd hide the wrong app.
    st = cowork_window_state()
    if not st["is_frontmost"]:
        try:
            osascript('tell application "Claude" to activate')
        except subprocess.CalledProcessError:
            pass
        time.sleep(0.5)
        st = cowork_window_state()
        if not st["is_frontmost"]:
            print(f"      [reset] ⚠️  Claude not frontmost (top={st['frontmost_owner']}); "
                  f"skipping hide to avoid hiding the wrong app")
            return st["is_onscreen"]

    print(f"      [reset] hide (Cmd+H) → reshow Cowork to flush queued scroll...")
    try:
        osascript('tell application "System Events" to keystroke "h" using command down')
    except subprocess.CalledProcessError:
        pass
    time.sleep(WINDOW_RESET_WAIT_S)
    try:
        osascript('tell application "Claude" to activate')
    except subprocess.CalledProcessError:
        pass
    time.sleep(WINDOW_RESET_WAIT_S)

    deadline = time.time() + WAKE_ONSCREEN_TIMEOUT_S
    while time.time() < deadline:
        st = cowork_window_state()
        if st["is_onscreen"] and st["is_frontmost"]:
            print(f"      [reset] Cowork reshown on-screen; settling "
                  f"{WAKE_COMPOSITOR_SETTLE_S}s")
            time.sleep(WAKE_COMPOSITOR_SETTLE_S)
            return True
        time.sleep(WAKE_ONSCREEN_POLL_S)
    print(f"      [reset] ⚠️  Cowork not confirmed on-screen after reshow")
    return False


def load_calibration() -> dict:
    if not CALIB_JSON.exists():
        sys.exit(
            f"❌ No calibration at {CALIB_JSON.relative_to(REPO_ROOT)}\n"
            f"   Run: python3 automation/calibrate.py"
        )
    return json.loads(CALIB_JSON.read_text())


def find_claude_main_window() -> dict | None:
    """Find Claude's main content window via CGWindowList."""
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
        candidates.append((b["Width"] * b["Height"], int(w.get("kCGWindowNumber")), b))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    _, wid, bounds = candidates[0]
    return {"id": wid, "bounds": bounds}


def cowork_window_state() -> dict:
    """Snapshot Cowork's window visibility + frontmost state via CGWindowList.

    Returns:
      found:           bool — Claude's main window present in the window list
      window_id:       int | None
      is_onscreen:     bool — kCGWindowIsOnscreen. True ONLY when the window is
                       on the active, visible Space and not fully occluded.
                       When Cowork is on a background fullscreen Space (the
                       production occlusion case), Chromium suspends compositing
                       and this reads False even though the window 'exists'.
      is_frontmost:    bool — is "Claude" the frontmost (z-order top) app
      frontmost_owner: str | None — owner name of the topmost on-screen window
      bounds:          dict | None

    is_onscreen is the load-bearing signal for diagnosing the wake: if a wake
    fails to flip it False→True, the renderer is still suspended and any scroll
    events we post will queue instead of paint.
    """
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionAll,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID,
    )
    # All windows (including other Spaces) — find Claude's main window and read
    # its on-screen flag.
    best = None  # (area, window_id, is_onscreen, bounds)
    for w in CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID):
        if w.get("kCGWindowOwnerName") != "Claude":
            continue
        if w.get("kCGWindowLayer", 0) != 0:
            continue
        b = dict(w.get("kCGWindowBounds", {}))
        if b.get("Width", 0) < 500 or b.get("Height", 0) < 500:
            continue
        area = b["Width"] * b["Height"]
        if best is None or area > best[0]:
            best = (area, int(w.get("kCGWindowNumber")),
                    bool(w.get("kCGWindowIsOnscreen", False)), b)

    # On-screen list is front-to-back z-order; first layer-0 window = the
    # frontmost app. No AppKit/NSWorkspace dependency this way.
    frontmost_owner = None
    for w in CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID):
        if w.get("kCGWindowLayer", 0) != 0:
            continue
        frontmost_owner = w.get("kCGWindowOwnerName")
        break

    if best is None:
        return {"found": False, "window_id": None, "is_onscreen": False,
                "is_frontmost": frontmost_owner == "Claude",
                "frontmost_owner": frontmost_owner, "bounds": None}
    _, wid, is_onscreen, bounds = best
    return {"found": True, "window_id": wid, "is_onscreen": is_onscreen,
            "is_frontmost": frontmost_owner == "Claude",
            "frontmost_owner": frontmost_owner, "bounds": bounds}


def screencap_window(wid: int, out: Path):
    run(["screencapture", "-x", "-o", "-l", str(wid), str(out)])


def crop_at(window_png: Path, btn_x: int, btn_y: int,
            window_bounds: dict, scale: float, radius: int, out: Path):
    """Crop a square at (btn_x, btn_y) screen-logical from a window screencap."""
    from PIL import Image
    img = Image.open(window_png)
    rel_x = (btn_x - window_bounds["X"]) * scale
    rel_y = (btn_y - window_bounds["Y"]) * scale
    r = radius * scale
    box = (int(rel_x - r), int(rel_y - r), int(rel_x + r), int(rel_y + r))
    img.crop(box).save(out)


def mean_pixel_diff(a: Path, b: Path) -> float:
    from PIL import Image, ImageChops, ImageStat
    ia = Image.open(a).convert("RGB")
    ib = Image.open(b).convert("RGB")
    if ia.size != ib.size:
        ib = ib.resize(ia.size)
    diff = ImageChops.difference(ia, ib)
    stat = ImageStat.Stat(diff)
    return sum(stat.mean) / len(stat.mean)


def resolve_recording_slot(new_slot: bool = False, create: bool = True) -> tuple[int, Path, str]:
    """Decide which N<n>/ slot to write to.

    Default behavior (`new_slot=False`): write to the highest-numbered existing
    slot, overwriting its contents. Re-running capture.py with the same
    prompt iterates on the same recording until the user explicitly advances.

    When `new_slot=True` (or no slots exist yet): create the next N<n+1>/.

    Returns (n, path, mode) where mode is 'new' or 'overwrite' for logging.
    """
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(
        int(p.name[1:]) for p in RECORDINGS_DIR.iterdir()
        if p.is_dir() and p.name.startswith("N") and p.name[1:].isdigit()
    )

    if new_slot or not existing:
        n = (existing[-1] + 1) if existing else 1
        mode = "new"
    else:
        n = existing[-1]
        mode = "overwrite"

    slot = RECORDINGS_DIR / f"N{n}"
    if create:
        slot.mkdir(parents=True, exist_ok=True)
    return n, slot, mode


def activate_claude_and_new_chat():
    """Activate Claude (Space comes into view), open a new chat (cmd+N)."""
    script = """
    tell application "Claude" to activate
    delay 1.0
    tell application "System Events"
      tell process "Claude"
        set frontmost to true
        keystroke "n" using command down
      end tell
    end tell
    delay 1.0
    """
    osascript(script)


def cliclick_type(text: str):
    """Type text via cliclick at human-cadence delays."""
    safe = text.replace("\n", " ")  # newlines could submit prematurely
    args = ["cliclick", "-w", str(TYPE_DELAY_MS), f"t:{safe}"]
    subprocess.run(args, check=True)


def press_send():
    """Press cmd+Enter to submit the prompt.

    Cowork mode in Claude desktop binds send to cmd+Return (shown in the UI
    as '⌘↵ to start a task and keep going'). Plain Enter adds a newline in
    that mode.
    """
    osascript('tell application "System Events" to keystroke return using command down')


# Coords of the first item in the Cowork "Recents" sidebar (screen-logical).
# After cmd+Enter creates a task, Cowork stays on the home page — we have
# to click the new task to open its streaming view. This coord is for the
# user's current display + sidebar layout. If the UI redesigns or the
# sidebar collapses, this needs re-measuring (extract a frame, eyeball it).
RECENTS_FIRST_ITEM_LOGICAL = (140, 320)


def click_first_recents_item():
    """Click the first task in the Recents sidebar to navigate into it."""
    x, y = RECENTS_FIRST_ITEM_LOGICAL
    subprocess.run(["cliclick", f"c:{x},{y}"], check=True)


# Coords (screen-logical) where to position the cursor before sending scroll
# events. Scroll-wheel events route to the element under the cursor, so the
# cursor MUST be inside the target scroll region. We want the cursor at the
# RIGHT edge of each panel (just inside the scroll region, but past the
# centered text content).
# These are the FALLBACK values when auto-detection fails. The chat right
# edge depends on the chat/doc boundary which the user can resize — at
# runtime we detect it via brightness analysis (find_chat_doc_boundary).
SCROLL_TARGETS_LOGICAL_FALLBACK = [
    (820, 500),    # main chat — right edge (just left of chat/doc divider)
    (1700, 500),   # doc panel — far right (just inside screen edge)
]
# Mutable globals updated by detect_chat_doc_boundary() at runtime
SCROLL_TARGETS_LOGICAL = list(SCROLL_TARGETS_LOGICAL_FALLBACK)


def find_chat_doc_boundary() -> int | None:
    """Detect the chat/doc panel boundary x-coord by analyzing step transitions.

    Cowork's chat and doc panels have nearly-identical-but-not-quite dark
    backgrounds — chat ≈ rgb(31,31,30), doc ≈ rgb(30,30,29). The boundary
    isn't a visible line; it's a STEP transition where brightness drops by
    ~1 unit going from chat to doc and STAYS dropped (because the entire
    doc panel is darker).

    Algorithm:
      1. Sample many rows in the middle of the screen
      2. For each x, compute the average brightness of pixels 5-15 to the
         LEFT vs 5-15 to the RIGHT (skip immediate neighbors to avoid
         anti-aliasing). If left > right, this x is a "chat→doc step".
      3. Find x positions where this step is consistently positive across
         many rows. The chat/doc boundary is the leftmost such x.

    Returns the detected x in logical points, or None.
    """
    import tempfile
    from PIL import Image
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            shot_path = f.name
        subprocess.run(["screencapture", "-x", shot_path], check=True, capture_output=True)
        img = Image.open(shot_path).convert("RGB")
        Path(shot_path).unlink(missing_ok=True)
    except (subprocess.CalledProcessError, OSError):
        return None

    width, height = img.size
    # Sample many rows across the middle vertical band — avoid top/bottom
    # UI bars and chat area where most text content lives.
    sample_ys_phys = list(range(int(height * 0.35), int(height * 0.75), 30))

    # Search range: physical 1000..2800 = logical 500..1400
    search_lo_phys = max(1000, 300)
    search_hi_phys = min(2800, width - 50)

    # For each x in the search range, count rows where the brightness step
    # (left - right) is positive (chat brighter than doc), excluding text
    # noise by using a small but persistent threshold.
    step_threshold = 0.4  # brightness units (chat=30.67, doc=29.67 → diff ~1.0)
    counts_by_x: dict[int, int] = {}
    for y in sample_ys_phys:
        for x in range(search_lo_phys, search_hi_phys):
            try:
                # Avg brightness 5-15 px to the left
                left_avg = sum(
                    sum(img.getpixel((x - i, y))) / 3 for i in range(5, 16)
                ) / 11
                # Avg brightness 5-15 px to the right
                right_avg = sum(
                    sum(img.getpixel((x + i, y))) / 3 for i in range(5, 16)
                ) / 11
            except IndexError:
                continue
            if left_avg - right_avg > step_threshold:
                counts_by_x[x] = counts_by_x.get(x, 0) + 1

    if not counts_by_x:
        return None

    # Find x with the highest row-vote count. If tied, prefer the leftmost x
    # (the chat→doc boundary should be the leftmost consistent step).
    max_count = max(counts_by_x.values())
    # Only consider x's that hit at least 50% of sampled rows
    threshold = len(sample_ys_phys) * 0.5
    if max_count < threshold:
        return None
    candidates = [x for x, c in counts_by_x.items() if c >= max_count - 2]
    boundary_phys = min(candidates)  # leftmost = chat/doc transition
    return boundary_phys // 2  # logical


def refresh_scroll_targets() -> None:
    """Re-detect chat/doc boundary and update SCROLL_TARGETS_LOGICAL.

    Called at start of post-streaming sequence so cursor positions adapt to
    the user's current Cowork layout (panels can be resized).

    CALLER MUST ensure Cowork is frontmost before invoking this — the screen
    capture inside find_chat_doc_boundary samples whatever app is currently
    on top.
    """
    boundary = find_chat_doc_boundary()
    if boundary is not None:
        chat_x = max(300, boundary - 20)
        doc_x = 1700
        SCROLL_TARGETS_LOGICAL[0] = (chat_x, 500)
        SCROLL_TARGETS_LOGICAL[1] = (doc_x, 500)
        print(f"      [layout] chat/doc boundary detected at x={boundary}; "
              f"cursors: chat=({chat_x},500) doc=({doc_x},500)")
    else:
        print(f"      [layout] boundary not detected; using fallback cursors")
END_OF_RECORDING_HOLD_S = 8.0  # seconds to hold view-at-top before stopping ffmpeg

# Smooth scroll-down (HammerSpoon-style) settings.
# Match the user's HammerSpoon autoscroll config exactly: 300 px/s at 120 Hz,
# accumulator pattern so each event is a small even step (smooth in recording).
SMOOTH_SCROLL_PPS = 300
SMOOTH_SCROLL_TICK_HZ = 120
SMOOTH_SCROLL_MAX_DURATION_S = 90.0
# Content-change detection: every N seconds, screencap a region and compare
# to the previous capture. When K consecutive checks show no change, we've
# reached the bottom of the conversation and stop scrolling.
SMOOTH_SCROLL_CHECK_INTERVAL_S = 0.6
SMOOTH_SCROLL_UNCHANGED_THRESHOLD = 2.0
SMOOTH_SCROLL_UNCHANGED_FRAMES_TO_STOP = 3
# Brief holds at top + bottom so viewers register the start/end state.
# Lowered from 2.0/2.5 — those were perceived as dead time in newsletter-pace
# output. Keep them short but non-zero so the cut → scroll-down isn't jarring.
POST_SCROLL_TOP_HOLD_S = 0.5
POST_SCROLL_BOTTOM_HOLD_S = 1.0


def _force_claude_frontmost(wait_s: float = 2.0) -> None:
    """Activate Claude AND set its process frontmost, then wait for the
    Space switch + render to fully resume.

    A simple `tell application "Claude" to activate` brings the app forward
    but Chromium suspends rendering of inactive windows — when we send
    scroll events too quickly afterwards, they're queued but don't visually
    apply until the window is actually rendering again. Using BOTH activate
    AND System Events frontmost, plus a longer wait, ensures Cowork is fully
    awake before we send input events.
    """
    script = '''
    tell application "Claude" to activate
    tell application "System Events"
        tell process "Claude"
            set frontmost to true
        end tell
    end tell
    '''
    try:
        osascript(script)
    except subprocess.CalledProcessError:
        return
    time.sleep(wait_s)


def scroll_chat_to_top() -> None:
    """Scroll Cowork's chat AND right-side artifact panel to the top.

    Empirically tested (see tools/auto_test_scroll.py): the ONLY synthetic
    scroll method that reliably moves Cowork's chat container is CGEvent
    LINE-unit scroll wheel events. PIXEL-unit scroll, cmd+Up, Home key,
    Page Up, and drag-up gestures all silently fail (or work inconsistently)
    on Cowork — a Chromium-WebContents quirk. (test_phased_scroll.py later
    confirmed the event payload is irrelevant when the window is visible; the
    real failure was the renderer being suspended, handled by the wake below.)

    80 events × 10 lines per target = 800 lines worth of scroll-up, plenty
    for any realistic conversation length.

    Pure scroll events — the caller is responsible for waking Cowork first
    (see scroll_to_top_with_verify), so the before/after verify snapshot can be
    taken AFTER the wake (otherwise the 'before' shot captures whatever app was
    occluding Cowork, not the chat).
    """
    from Quartz import CGEventCreateScrollWheelEvent, CGEventPost
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitLine

    for x, y in SCROLL_TARGETS_LOGICAL:
        # Move cursor over the scroll target.
        try:
            subprocess.run(["cliclick", f"m:{x},{y}"], check=True)
        except subprocess.CalledProcessError:
            continue
        time.sleep(0.1)

        # CGEvent scroll wheel, LINE units. 80 events × 10 lines positive
        # delta = scroll up. Small inter-event delay so the OS treats these
        # as separate scroll ticks instead of coalescing.
        for _ in range(80):
            event = CGEventCreateScrollWheelEvent(
                None, kCGScrollEventUnitLine, 1, 10
            )
            CGEventPost(kCGHIDEventTap, event)
            time.sleep(0.015)
        time.sleep(0.4)


def smooth_scroll_down(target_x: int, target_y: int, check_region: tuple[int, int, int, int],
                       tmpdir: Path, pps: float = SMOOTH_SCROLL_PPS) -> float:
    """Smooth scroll DOWN at HammerSpoon-style pacing for ANY target region.

    Mimics the user's HammerSpoon autoscroll config (300 px/s, 120 Hz tick,
    accumulator pattern, pixel-mode events with negative Y = down). Two
    critical refinements over a naive sleep-based loop:

      1. ABSOLUTE-TIME SCHEDULING — `time.sleep()` drifts on macOS (each
         8.3ms sleep can take 12-15ms), which both slows the effective
         scroll rate AND causes uneven pacing. Instead we compute the
         exact next-tick time from a fixed start, and sleep only the
         remaining time. Drift gets corrected; pace stays constant.

      2. BACKGROUND END-DETECTION — a daemon thread runs the content-
         change checks (screencap + diff, each ~100ms) so the main
         scroll loop NEVER blocks waiting for it. This eliminates the
         periodic stutter we saw at 0.6s intervals.

    Returns: seconds spent scrolling (for logging).
    """
    import threading
    from Quartz import CGEventCreateScrollWheelEvent, CGEventPost
    from Quartz.CoreGraphics import kCGHIDEventTap, kCGScrollEventUnitPixel

    # NB: no wake_chromium_render() here. smooth_scroll_down is only called
    # from run_post_streaming_scroll_sequence AFTER scroll_to_top_with_verify
    # has already woken + flushed Cowork (Cmd+H reset) — so the window is live
    # and frontmost. An extra Cmd+Tab here would just add a visible app-switcher
    # artifact to the START of the kept read-through segment.
    # Move cursor over the scroll target.
    try:
        subprocess.run(["cliclick", f"m:{target_x},{target_y}"], check=True)
    except subprocess.CalledProcessError:
        return 0.0
    time.sleep(0.15)

    # ---- background end-detection thread ----
    stop_event = threading.Event()
    bottom_event = threading.Event()

    def detection_loop():
        sample = tmpdir / f"_ssd_sample_{target_x}_{target_y}.png"
        last = tmpdir / f"_ssd_last_{target_x}_{target_y}.png"
        unchanged = 0
        rx, ry, rw, rh = check_region
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
            except (subprocess.CalledProcessError, OSError):
                pass
            stop_event.wait(SMOOTH_SCROLL_CHECK_INTERVAL_S)
        sample.unlink(missing_ok=True)
        last.unlink(missing_ok=True)

    detector = threading.Thread(target=detection_loop, daemon=True)
    detector.start()

    # ---- main scroll loop with absolute-time scheduling ----
    tick_interval = 1.0 / SMOOTH_SCROLL_TICK_HZ
    start = time.monotonic()
    deadline = start + SMOOTH_SCROLL_MAX_DURATION_S
    next_tick = start
    accumulator = 0.0

    while time.monotonic() < deadline and not bottom_event.is_set():
        accumulator += pps / SMOOTH_SCROLL_TICK_HZ
        whole = int(accumulator)
        if whole > 0:
            # Plain pixel-unit scroll event — matches HammerSpoon's
            # hs.eventtap.event.newScrollEvent({0,-whole}, {}, "pixel"):post()
            # exactly. No IsContinuous flag (Chromium would otherwise apply
            # its own kinetic-scroll smoothing on top of our pacing).
            event = CGEventCreateScrollWheelEvent(
                None, kCGScrollEventUnitPixel, 1, -whole
            )
            CGEventPost(kCGHIDEventTap, event)
            accumulator -= whole
        # Sleep until exactly the next tick should fire — corrects sleep drift
        next_tick += tick_interval
        remaining = next_tick - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)
        # If we're already behind schedule (remaining < 0), don't sleep —
        # just continue immediately to catch up.

    stop_event.set()
    detector.join(timeout=1.0)
    return time.monotonic() - start


def smooth_scroll_chat_down(tmpdir: Path) -> float:
    """Smooth scroll the MAIN CHAT downward (HammerSpoon-style)."""
    x, y = SCROLL_TARGETS_LOGICAL[0]
    return smooth_scroll_down(x, y, check_region=(400, 400, 600, 500), tmpdir=tmpdir)


def smooth_scroll_document_down(tmpdir: Path) -> float:
    """Smooth scroll the RIGHT DOCUMENT panel downward (if present).

    Watches a region on the right side for content change. If no document
    panel exists (just the Progress/Context sidebar), this still scrolls
    that, which is harmless — and content-change detection will fire fast
    when the sidebar can't scroll further.
    """
    x, y = SCROLL_TARGETS_LOGICAL[1]
    return smooth_scroll_down(x, y, check_region=(1100, 400, 500, 500), tmpdir=tmpdir)


def scroll_to_top_with_verify(tmpdir: Path) -> bool:
    """Wake Cowork (no-op if already frontmost), then scroll the chat to the top.

    Experimental: no flush. The previous version did
        wake → scroll-up → reset_cowork_window() (Cmd+H flush) → scroll-up
    on the theory that the first scroll might queue against a deep-throttled
    renderer. But N7/N9/N10 showed the first scroll paints just fine once the
    dual-region detector fires the moment streaming ends — the renderer never
    drifts into deep-throttle, so the flush isn't actually needed. We're trying
    a single scroll, no flush. If long-session runs start showing frozen scrolls
    again, restore the flush from capture.py.bak-with-flush.

    Snapshots are taken AFTER the wake so the before/after diff is chat-vs-chat.
    The diff is INFORMATIONAL only — never an abort trigger.

    Returns True if Cowork was confirmed on-screen, False if the wake could not
    recover it.
    """
    if not wake_chromium_render():
        return False

    pre = tmpdir / "_pre_scroll_up.png"
    post = tmpdir / "_post_scroll_up.png"

    # Park cursor outside the verify region for both snapshots so cursor pixels
    # contribute zero diff.
    subprocess.run(["cliclick", f"m:{CURSOR_PARK_LOGICAL[0]},{CURSOR_PARK_LOGICAL[1]}"],
                   check=False)
    time.sleep(0.15)
    _screencap_region(SCROLL_VERIFY_REGION_LOGICAL, pre)

    print(f"      Scrolling chat to top...")
    scroll_chat_to_top()

    subprocess.run(["cliclick", f"m:{CURSOR_PARK_LOGICAL[0]},{CURSOR_PARK_LOGICAL[1]}"],
                   check=False)
    time.sleep(SCROLL_VERIFY_SETTLE_S)
    _screencap_region(SCROLL_VERIFY_REGION_LOGICAL, post)

    if pre.exists() and post.exists():
        scroll_diff = mean_pixel_diff(pre, post)
        print(f"      [scroll-verify] before/after chat diff = {scroll_diff:.2f} "
              f"(informational — prompt detection means renderer is fresh idle, no flush needed)")
    return True


def run_post_streaming_scroll_sequence(tmpdir: Path, mark) -> None:
    """Bring Cowork forward, scroll chat to top (verified+retried), then smooth
    scroll the read-through down. Shared by the streaming-ended and the
    MAX_RECORDING_S cutoff paths so the wake-retry fix lives in one place.

    `mark` is main()'s phase-timestamp callback. Raises KeyboardInterrupt if the
    scroll-up can't be confirmed after retries, so the caller's finally-block
    finalizes ffmpeg gracefully (same contract as the old inline abort).
    """
    ensure_cowork_frontmost()
    refresh_scroll_targets()

    scrolled = scroll_to_top_with_verify(tmpdir)
    mark("scroll_to_top_done")
    if not scrolled:
        print(f"      ⚠️  Wake could not bring Cowork back on-screen after "
              f"{WAKE_MAX_ATTEMPTS} attempts — renderer stayed suspended. Aborting.")
        raise KeyboardInterrupt

    print(f"      Holding {POST_SCROLL_TOP_HOLD_S}s at top...")
    time.sleep(POST_SCROLL_TOP_HOLD_S)
    mark("smooth_scroll_chat_start")
    print(f"      Smooth scroll DOWN — main chat @ {SMOOTH_SCROLL_PPS}px/s...")
    chat_scroll_s = smooth_scroll_chat_down(tmpdir)
    mark("smooth_scroll_chat_end")
    print(f"        chat bottom reached after {chat_scroll_s:.1f}s")
    print(f"      Smooth scroll DOWN — document panel @ {SMOOTH_SCROLL_PPS}px/s...")
    mark("smooth_scroll_doc_start")
    doc_scroll_s = smooth_scroll_document_down(tmpdir)
    mark("smooth_scroll_doc_end")
    print(f"        document bottom reached after {doc_scroll_s:.1f}s")
    print(f"      Holding {POST_SCROLL_BOTTOM_HOLD_S}s at bottom...")
    time.sleep(POST_SCROLL_BOTTOM_HOLD_S)


def click_allow_button_via_ax() -> str | None:
    """Try to find + click an 'Allow' button via macOS Accessibility (AppleScript).

    NOTE: This only works for NATIVE macOS dialogs (file pickers, OS-level
    permission prompts). Cowork's in-chat MCP permission dialogs are rendered
    as HTML inside Electron's WebContents view, which Chromium does not expose
    to macOS Accessibility — those are invisible to AppleScript and must be
    handled by `click_allow_button_via_ocr` instead.

    Kept as a cheap pre-check (fast no-op when no native dialog present).
    """
    script = r'''
    on findAllowBtn(elem)
        set titleStr to ""
        set descStr to ""
        set roleVal to ""
        set kids to {}
        tell application "System Events"
            try
                set roleVal to (value of attribute "AXRole" of elem) as text
            end try
            try
                set titleStr to (value of attribute "AXTitle" of elem) as text
            end try
            try
                set descStr to (value of attribute "AXDescription" of elem) as text
            end try
            try
                set kids to value of attribute "AXChildren" of elem
            end try
        end tell
        if roleVal is "AXButton" then
            set combined to titleStr & " " & descStr
            ignoring case
                if combined contains "allow" then
                    if combined does not contain "don't allow" and combined does not contain "disallow" and combined does not contain "deny" then
                        tell application "System Events"
                            try
                                perform action "AXPress" of elem
                            on error
                                try
                                    click elem
                                end try
                            end try
                        end tell
                        return combined
                    end if
                end if
            end ignoring
        end if
        repeat with k in kids
            set foundResult to my findAllowBtn(k)
            if foundResult is not "" then return foundResult
        end repeat
        return ""
    end findAllowBtn

    tell application "System Events"
        tell process "Claude"
            repeat with w in windows
                set foundResult to my findAllowBtn(w)
                if foundResult is not "" then return foundResult
            end repeat
        end tell
    end tell
    return ""
    '''
    try:
        result = osascript(script)
        return result.strip() if result and result.strip() else None
    except subprocess.CalledProcessError:
        return None


def click_allow_button_via_ocr(wid: int, window_bounds: dict, scale: float,
                                tmpdir: Path) -> str | None:
    """OCR the Claude window screencap; click an 'Allow'-style button if found.

    Works for HTML-rendered dialogs that Accessibility can't see. Slower than
    the AppleScript path (~300-500ms per call) so caller should rate-limit.

    Returns a short status string ("Allow @ x,y") if clicked, else None.
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return None

    screencap = tmpdir / "_ocr_scan.png"
    try:
        screencap_window(wid, screencap)
    except subprocess.CalledProcessError:
        return None

    try:
        img = Image.open(screencap)
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    except Exception:
        screencap.unlink(missing_ok=True)
        return None
    finally:
        screencap.unlink(missing_ok=True)

    n = len(data["text"])
    # Prefer matches in this priority order — earlier = better:
    # 1. "Allow for this task"  (covers all tool calls in this run, conservative)
    # 2. "Allow for all tasks"  (persistent across runs)
    # 3. "Allow once"           (one-shot)
    # 4. anything containing "allow" but not the exclusions below
    priority_match: tuple[int, int, str] | None = None  # (priority_rank, index, text)
    for i in range(n):
        text = (data["text"][i] or "").strip()
        if not text:
            continue
        low = text.lower()
        # NB: a substring check for "allow" matches both the literal button
        # ("Allow") and tesseract word-merge variants ("Allowonce"). But it
        # ALSO matches "Allowing" / "Allowed" from the warning paragraph
        # ("Allowing this action comes with risks...") — explicitly exclude.
        if "allowing" in low or "allowed" in low:
            continue
        if "allow" not in low:
            continue
        if "disallow" in low or "deny" in low:
            continue
        # Check the previous word in the same line — e.g. "Don't Allow"
        if i > 0 and data["line_num"][i] == data["line_num"][i - 1]:
            prev = (data["text"][i - 1] or "").strip().lower()
            if "don't" in prev or "dont" in prev or "deny" in prev:
                continue

        # Look at neighboring words on the same line to figure out which button
        # this is. We want the FULL button text (e.g. "Allow for this task")
        # so we can score priority — tesseract sometimes splits one button's
        # label into multiple word entries.
        line_text_parts = [text]
        for j in range(i + 1, min(i + 5, n)):
            if data["line_num"][j] != data["line_num"][i]:
                break
            t = (data["text"][j] or "").strip()
            if t:
                line_text_parts.append(t)
        button_label = " ".join(line_text_parts).lower()

        if "this task" in button_label:
            rank = 1
        elif "all task" in button_label:
            rank = 2
        elif "once" in button_label or low == "allowonce":
            rank = 3
        else:
            rank = 4

        if priority_match is None or rank < priority_match[0]:
            priority_match = (rank, i, button_label)

    if priority_match is None:
        return None

    _, i, button_label = priority_match
    img_x = data["left"][i] + data["width"][i] / 2
    img_y = data["top"][i] + data["height"][i] / 2
    logical_x = int(window_bounds["X"] + img_x / scale)
    logical_y = int(window_bounds["Y"] + img_y / scale)
    try:
        subprocess.run(["cliclick", f"c:{logical_x},{logical_y}"], check=True)
    except subprocess.CalledProcessError:
        return None
    return f"OCR '{button_label}' @ ({logical_x},{logical_y})"


def find_screen_device() -> str:
    """Find the avfoundation device index for 'Capture screen 0'.

    Indices shift when USB cameras connect/disconnect, so we re-discover
    on each run by parsing `ffmpeg -list_devices`.
    """
    import re
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-f", "avfoundation",
         "-list_devices", "true", "-i", ""],
        capture_output=True, text=True,
    )
    # The list goes to stderr in ffmpeg's normal output convention.
    output = r.stderr + r.stdout
    in_video = False
    for line in output.splitlines():
        if "video devices:" in line:
            in_video = True
            continue
        if "audio devices:" in line:
            in_video = False
            continue
        if not in_video:
            continue
        m = re.search(r"\[(\d+)\]\s+(Capture screen \d+)", line)
        if m:
            return m.group(1)
    raise RuntimeError(
        "Could not find 'Capture screen 0' in avfoundation device list. "
        "Make sure ffmpeg + Screen Recording permission are working."
    )


def start_ffmpeg(out_path: Path, log_path: Path) -> subprocess.Popen:
    """Spawn ffmpeg recording the screen via avfoundation. Returns Popen handle.

    ffmpeg stderr is captured to `log_path` so silent failures are debuggable.
    Output is written as a fragmented MP4 — index/moov data is interleaved
    with the video stream instead of saved only at the end. This means a
    SIGKILL or crash still produces a playable file (truncated to the last
    complete fragment) instead of an unreadable one.
    """
    device = find_screen_device()
    cmd = [
        "ffmpeg", "-y",
        "-f", "avfoundation",
        "-framerate", str(FFMPEG_FRAMERATE),
        "-capture_cursor", "0",
        "-i", device,
        "-c:v", "h264_videotoolbox",
        "-b:v", "8000k",
        "-pix_fmt", "yuv420p",
        # Fragmented MP4 so interruption-mid-record still leaves a playable file.
        # - empty_moov writes a minimal moov at the start
        # - frag_keyframe + frag_duration cuts fragments at keyframes / every ~1s
        "-movflags", "+empty_moov+frag_keyframe+default_base_moof",
        "-frag_duration", "1000000",  # microseconds — 1 fragment per second
        str(out_path),
    ]
    log_fh = open(log_path, "wb")
    return subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=log_fh,
        stderr=log_fh,
    )


def _screencap_region(region_logical: tuple[int, int, int, int], out_path: Path) -> bool:
    """Screen-capture a logical-coord region. Returns True on success."""
    rx, ry, rw, rh = region_logical
    try:
        subprocess.run(
            ["screencapture", "-x", "-R", f"{rx},{ry},{rw},{rh}", str(out_path)],
            check=True, capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, OSError):
        return False


def start_freeze_watchdog(tmpdir: Path,
                          region_logical: tuple[int, int, int, int] = (300, 200, 600, 350),
                          ) -> "threading.Event":
    """Spawn a daemon thread that aborts if the chat sits unchanged vs baseline.

    What this watchdog detects: "the chat content hasn't moved since the
    moment post-streaming started." NOT "no pixel changed anywhere." The
    distinction matters because our own code (cursor moves, synthetic clicks,
    title-bar redraws on focus changes, scroll-indicator flickers, etc.)
    creates pixel changes in lots of places during post-streaming — even
    when Cowork's chat itself is frozen. Comparing consecutive samples is
    fooled by all that automation noise.

    The fix: take ONE baseline snapshot when the watchdog arms, then every
    CHECK_INTERVAL_S compare the CURRENT chat region to that baseline. If
    the chat region keeps matching the baseline for FREEZE_WATCHDOG_TIMEOUT_S
    accumulated seconds straight, the chat truly never moved → abort.

    Region defaults to a 600×300 box at logical (300, 600). That's:
      - Inside the chat content area (between the title bar at y≈90 and the
        input bar at y≈1000)
      - Below the cursor's y=500 scroll-target height (so cursor moves don't
        contaminate)
      - Within the chat panel width even in chat-with-doc-panel layouts
        (the chat panel always extends from ~280 to at least ~1000 logical)
      - Wide enough to catch ANY chat scroll motion (one full message bubble
        is wider than this region; scroll by 10px shifts everything visibly)

    On abort: sends SIGINT so the main flow's `except KeyboardInterrupt`
    finalizes ffmpeg gracefully. Caller MUST .set() the returned stop_event
    on normal exit so the watchdog doesn't trigger during graceful shutdown.
    """
    import threading
    stop_event = threading.Event()

    rx, ry, rw, rh = region_logical

    def loop():
        sample = tmpdir / "_freeze_sample.png"
        baseline = tmpdir / "_freeze_baseline.png"
        baseline_taken = False
        freeze_start_t: float | None = None
        import shutil

        while not stop_event.is_set():
            try:
                subprocess.run(
                    ["screencapture", "-x", "-R", f"{rx},{ry},{rw},{rh}", str(sample)],
                    check=True, capture_output=True,
                )
                if not baseline_taken:
                    # First iteration — record the chat's starting state and
                    # begin the freeze countdown (trivially matches baseline).
                    shutil.copy(sample, baseline)
                    baseline_taken = True
                    freeze_start_t = time.monotonic()
                else:
                    diff = mean_pixel_diff(sample, baseline)
                    if diff < FREEZE_WATCHDOG_THRESHOLD:
                        # Chat hasn't moved since baseline — keep accumulating.
                        if freeze_start_t is None:
                            freeze_start_t = time.monotonic()
                        else:
                            frozen_for = time.monotonic() - freeze_start_t
                            if frozen_for >= FREEZE_WATCHDOG_TIMEOUT_S:
                                print(f"\n[freeze-watchdog] Chat region matched "
                                      f"baseline for {frozen_for:.1f}s straight "
                                      f"(threshold {FREEZE_WATCHDOG_THRESHOLD}, "
                                      f"timeout {FREEZE_WATCHDOG_TIMEOUT_S}s). "
                                      f"Scroll-up didn't move the chat — aborting.")
                                os.kill(os.getpid(), signal.SIGINT)
                                return
                    else:
                        # Chat has moved off baseline — healthy scroll motion.
                        # Reset; if chat returns to baseline state later (e.g.
                        # smooth_scroll_down completes), the counter restarts
                        # then but typically doesn't accumulate to TIMEOUT
                        # before recording stops.
                        freeze_start_t = None
            except (subprocess.CalledProcessError, OSError):
                pass
            stop_event.wait(FREEZE_WATCHDOG_CHECK_INTERVAL_S)

        sample.unlink(missing_ok=True)
        baseline.unlink(missing_ok=True)

    threading.Thread(target=loop, daemon=True).start()
    return stop_event


def stop_ffmpeg(proc: subprocess.Popen, timeout: float = 3.0):
    """Send 'q' to ffmpeg's stdin; fall back to SIGINT then SIGKILL.

    Timeout shortened from 10s → 3s so that abort feels responsive. We use
    fragmented MP4 output (+empty_moov+frag_keyframe+default_base_moof) so
    each ~1s fragment is self-contained — a SIGINT or even SIGKILL still
    produces a playable file truncated to the last complete fragment.
    The 'q' graceful path usually completes in well under 3s; the SIGINT
    fallback handles the rare slow-flush case in another 3s.
    """
    try:
        proc.stdin.write(b"q")
        proc.stdin.flush()
    except (BrokenPipeError, OSError):
        pass
    try:
        proc.wait(timeout=timeout)
        return
    except subprocess.TimeoutExpired:
        pass
    proc.send_signal(signal.SIGINT)
    try:
        proc.wait(timeout=3.0)
        return
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def trim_segment(raw_path: Path, out_path: Path, cut_start_s: float, cut_end_s: float) -> bool:
    """Cut the time range [cut_start_s, cut_end_s] out of `raw_path`.

    Writes the result (concatenation of the before-segment and after-segment)
    to `out_path`. Uses ffmpeg's trim+concat filter with h264_videotoolbox
    re-encoding (matches the original recording's codec).

    Returns True on success, False on failure. Failures are non-fatal —
    the raw recording is preserved either way.
    """
    if cut_end_s <= cut_start_s or cut_start_s < 0:
        return False
    cmd = [
        "ffmpeg", "-y", "-i", str(raw_path),
        "-filter_complex",
        # Keep [0..cut_start] then [cut_end..end], reset timestamps so the
        # concat is seamless.
        f"[0:v]trim=end={cut_start_s:.3f},setpts=PTS-STARTPTS[v0];"
        f"[0:v]trim=start={cut_end_s:.3f},setpts=PTS-STARTPTS[v1];"
        f"[v0][v1]concat=n=2:v=1:a=0[outv]",
        "-map", "[outv]",
        "-c:v", "h264_videotoolbox",
        "-b:v", "8000k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+empty_moov+frag_keyframe+default_base_moof",
        str(out_path),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        # Log to stderr for debugging
        print(f"      ⚠️ trim failed: {e.stderr.decode(errors='replace')[-500:]}")
        return False


def _region_diff(center: dict, radius: int, ref_rel: str, tmpdir: Path) -> float:
    """Screen-region screencap at `center`±radius (logical), diffed vs `ref_rel`.

    Region capture (`screencapture -R`) needs no window ID — works even if
    Cowork restarts — and reflects what's displayed with no renderer-cache lag.
    """
    cx, cy = center["x"], center["y"]
    x, y, w, h = cx - radius, cy - radius, radius * 2, radius * 2
    sample = tmpdir / "_sample_ib.png"
    try:
        subprocess.run(
            ["screencapture", "-x", "-R", f"{x},{y},{w},{h}", str(sample)],
            check=True, capture_output=True,
        )
        return mean_pixel_diff(sample, AUTOMATION_ROOT / ref_rel)
    finally:
        sample.unlink(missing_ok=True)


def sample_input_bar_scores(cfg: dict, tmpdir: Path) -> tuple[float, float]:
    """Return (stop_score, mic_score) for the input-bar control.

    stop_score = diff of the stop-button region vs the streaming reference
                 (LOW = ■ stop button present = STREAMING).
    mic_score  = diff of the mic region vs the idle reference
                 (LOW = 🎤 mic present = ENDED / idle).

    The states are mutually exclusive and live in DIFFERENT spots (the input
    bar re-lays-out between streaming and idle), so we sample both and let the
    caller decide by which is lower — a relative comparison, no absolute
    threshold. The old single-region detector compared only the stop spot to
    the streaming ref; when streaming ended that spot showed "Opus 4.7" text,
    which differs from ■ by only ~9.5 — under the 12.0 cutoff — so it read
    "still streaming" for ~130s. Comparing stop_score vs mic_score avoids that.

    Raises subprocess.CalledProcessError / OSError on screencap failure.
    """
    stop = cfg["stop_button"]
    mic = cfg["mic_button"]
    stop_score = _region_diff(stop["center_logical"], stop["radius_logical"],
                              stop["streaming_crop"], tmpdir)
    mic_score = _region_diff(mic["center_logical"], mic["radius_logical"],
                             mic["idle_crop"], tmpdir)
    return stop_score, mic_score


def wait_for_streaming_to_start(wid: int, cfg: dict, tmpdir: Path) -> bool:
    """Poll until the input bar looks more like streaming (stop) than idle (mic).

    Tolerates transient screencap failures (e.g. permission dialog appears mid-poll,
    window-list churn) — treats them as 'not yet' and keeps trying.
    """
    deadline = time.time() + STREAMING_START_TIMEOUT_S
    while time.time() < deadline:
        try:
            stop_score, mic_score = sample_input_bar_scores(cfg, tmpdir)
        except (subprocess.CalledProcessError, OSError):
            time.sleep(POLL_INTERVAL_S)
            continue
        if stop_score < mic_score:  # stop button present → streaming has begun
            return True
        time.sleep(POLL_INTERVAL_S)
    return False


def main():
    ap = argparse.ArgumentParser(description="Automated Claude desktop screen capture.")
    ap.add_argument("prompt_file", type=Path, help="Path to a text file containing the prompt.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Skip ffmpeg + cliclick — just print what would happen.")
    ap.add_argument("--new-slot", action="store_true",
                    help="Advance to a fresh N<n+1>/ slot. Without this, the script "
                         "overwrites the highest existing N<n>/ slot — iterating on "
                         "the same recording until you explicitly move on. "
                         "Ignored if --slot-dir is passed.")
    ap.add_argument("--slot-dir", type=str, default=None,
                    help="Override the auto-numbered news-pipeline/recordings/N<n>/ slot. "
                         "Pass a path (absolute or repo-relative) — e.g. \"screen "
                         "recordings/V5\" — and capture.py will write raw.mp4 + "
                         "manifest.json into that directory directly. Used by the "
                         "product-demo workflow's automated Phase 2 mode.")
    ap.add_argument("--no-readthrough", action="store_true",
                    help="Skip the post-streaming wake + scroll-to-top + smooth-scroll-"
                         "down + auto-trim sequence. When set, capture stops shortly "
                         "after streaming ends and produces raw.mp4 only (no "
                         "trimmed.mp4). Use for workflows that want the brief on screen "
                         "in its final state without the news-style read-through.")
    args = ap.parse_args()

    # ---- Validate ----
    if not args.prompt_file.exists():
        sys.exit(f"❌ Prompt file not found: {args.prompt_file}")
    prompt_text = args.prompt_file.read_text().strip()
    if not prompt_text:
        sys.exit(f"❌ Prompt file is empty: {args.prompt_file}")

    cfg = load_calibration()

    # ---- Slot ----
    if args.slot_dir:
        # Explicit slot — product-demo workflow's path (or any caller that
        # wants to bypass the auto-numbered N<n>/ convention).
        slot = Path(args.slot_dir)
        if not slot.is_absolute():
            slot = REPO_ROOT / slot
        if not args.dry_run:
            slot.mkdir(parents=True, exist_ok=True)
        n = slot.name
        mode = "explicit"
    else:
        n, slot, mode = resolve_recording_slot(
            new_slot=args.new_slot,
            create=not args.dry_run,
        )
    raw_mp4 = slot / "raw.mp4"
    manifest_path = slot / "manifest.json"
    mode_label = {
        "new": "new slot",
        "overwrite": "OVERWRITING — pass --new-slot to advance",
        "explicit": f"explicit slot ({args.slot_dir})",
    }[mode]
    slot_label = n if isinstance(n, str) else f"N{n}"
    print(f"\n→ recording slot: {slot_label}  [{mode_label}]  ({slot.relative_to(REPO_ROOT)})")
    print(f"→ prompt file:    {args.prompt_file}")
    print(f"→ prompt ({len(prompt_text)} chars):")
    for line in prompt_text.splitlines()[:5]:
        print(f"    {line}")
    if len(prompt_text.splitlines()) > 5:
        print(f"    ... ({len(prompt_text.splitlines()) - 5} more lines)")

    if args.dry_run:
        print("\n[dry-run] would activate Claude, open new chat, type prompt, record.")
        return

    started_at = time.time()
    iso_started = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    # ---- Activate Claude + new chat ----
    print("\n[1/6] Activating Claude + cmd+N...")
    activate_claude_and_new_chat()
    win = find_claude_main_window()
    if not win:
        sys.exit("❌ Could not find Claude's main window. Is Claude.app running?")
    print(f"      Claude window: id={win['id']} bounds={win['bounds']}")

    # Recheck window bounds against calibration. If wildly different, warn.
    cb = cfg["claude_window_bounds"]
    if abs(cb["Width"] - win["bounds"]["Width"]) > 50 \
       or abs(cb["Height"] - win["bounds"]["Height"]) > 50:
        print(f"      ⚠️  Window size differs from calibration "
              f"({cb['Width']}×{cb['Height']} → {win['bounds']['Width']}×{win['bounds']['Height']}). "
              f"Detection may be unreliable.")

    # ---- Start ffmpeg ----
    ffmpeg_log = slot / "ffmpeg.log"
    print(f"\n[2/6] Starting ffmpeg recording → {raw_mp4.relative_to(REPO_ROOT)}")
    ff = start_ffmpeg(raw_mp4, ffmpeg_log)
    # Mark the moment ffmpeg actually began capturing — phase timestamps
    # below are recorded RELATIVE to this so they map directly into the
    # raw.mp4 timeline (which is what the trim step needs).
    ffmpeg_started_at = time.monotonic()
    time.sleep(1.5)  # let ffmpeg initialize
    if ff.poll() is not None:
        log_excerpt = ffmpeg_log.read_text(errors="replace").splitlines()[-30:]
        print("\nffmpeg log tail:")
        for line in log_excerpt:
            print(f"  {line}")
        sys.exit(f"❌ ffmpeg exited immediately (rc={ff.returncode}). See log above.")

    # Pre-init so the `finally` block can always reference it, even if the
    # try-body raises something other than KeyboardInterrupt.
    interrupted = False
    freeze_stop = None  # set to a threading.Event once the watchdog is armed
    freeze_aborted = False  # True if the watchdog was the one that fired SIGINT
    # Phase timestamps relative to ffmpeg_started_at (so they index into raw.mp4)
    phases: dict[str, float] = {}

    def mark(label: str) -> None:
        """Record a recording-relative timestamp for a phase boundary."""
        phases[label] = time.monotonic() - ffmpeg_started_at

    try:
        # ---- Type prompt ----
        print("\n[3/6] Typing prompt via cliclick...")
        cliclick_type(prompt_text)
        time.sleep(0.3)
        press_send()  # cmd+Enter (Cowork mode send shortcut)

        # Cowork creates the task but stays on the home page. Click the new
        # task in the Recents sidebar to navigate to its streaming view.
        time.sleep(1.0)  # let the task appear in Recents
        click_first_recents_item()
        time.sleep(0.6)  # let the task page paint

        # ---- Wait for streaming to start ----
        print("\n[4/6] Waiting for streaming to start...")
        with tempfile.TemporaryDirectory() as td:
            tmpdir = Path(td)
            if not wait_for_streaming_to_start(win["id"], cfg, tmpdir):
                print(f"      ⚠️  Stop icon never appeared within {STREAMING_START_TIMEOUT_S}s.")
                print("         Claude may not have started responding. Continuing anyway.")
            else:
                print("      ✓ Streaming started.")
            # Boundary between the typing window and Cowork's response — drives
            # rule N2 (news-pipeline/README.md): scrub.py must speedup-not-cut
            # across [0, streaming_started]. Marked on both branches so the
            # boundary is recorded even if stop-icon detection timed out
            # (in which case "streaming_started" is the give-up moment, ~8s
            # past true typing-end — speeding up the extra slack is fine).
            mark("streaming_started")

            # ---- Poll until done ----
            print(f"\n[5/6] Polling for streaming-end "
                  f"(stop-vs-mic relative match, debounce={DEBOUNCE_FRAMES} frames)...")
            non_match_streak = 0
            samples = 0
            samples_streaming = 0
            samples_idle = 0
            samples_failed = 0
            allow_clicks = 0
            poll_deadline = time.time() + MAX_RECORDING_S
            # Track consecutive screencap failures so we know when to refresh
            # the Claude window ID (it can go stale if Cowork desktop restarts
            # mid-run, e.g. to apply a pending update).
            consecutive_failures = 0
            while time.time() < poll_deadline:
                # Auto-dismiss MCP permission dialogs.
                # Two paths: cheap AppleScript (native dialogs) every poll, OCR
                # (HTML/Electron dialogs) every 5th poll = ~1s. OCR is the path
                # that actually works for Cowork's in-chat permission prompts.
                try:
                    clicked = click_allow_button_via_ax()
                except Exception:
                    clicked = None
                if not clicked and samples % 5 == 0:
                    try:
                        clicked = click_allow_button_via_ocr(
                            win["id"], cfg["claude_window_bounds"], cfg["pixel_scale"], tmpdir,
                        )
                    except Exception:
                        clicked = None
                if clicked:
                    allow_clicks += 1
                    elapsed = time.time() - started_at
                    print(f"      [t={elapsed:5.1f}s]  ✓ auto-clicked permission: {clicked}")
                    time.sleep(0.6)  # let the dialog dismiss + UI repaint

                # Sample both input-bar regions. Tolerate transient screencap
                # failures (modal dialogs in flight, window-list churn, etc.) —
                # treat as ambiguous, don't crash.
                try:
                    stop_score, mic_score = sample_input_bar_scores(cfg, tmpdir)
                    consecutive_failures = 0  # success — reset the counter
                except (subprocess.CalledProcessError, OSError):
                    samples += 1
                    samples_failed += 1
                    consecutive_failures += 1
                    elapsed = time.time() - started_at
                    if samples_failed <= 3 or samples_failed % 25 == 0:
                        print(f"      [t={elapsed:5.1f}s]  ⚠️ screencap failed ({samples_failed} total)")
                    # After 5 consecutive failures, the window ID is likely
                    # stale (Cowork desktop restarted / window replaced).
                    # Try to refresh it. Retry every 25 failures thereafter
                    # so we recover even if Claude takes a while to come back.
                    if consecutive_failures == 5 or (consecutive_failures > 5 and consecutive_failures % 25 == 0):
                        new_win = find_claude_main_window()
                        if new_win and new_win["id"] != win["id"]:
                            print(f"      [t={elapsed:5.1f}s]  ↻ refreshed Claude window: "
                                  f"id {win['id']} → {new_win['id']}")
                            win = new_win
                            consecutive_failures = 0
                    time.sleep(POLL_INTERVAL_S)
                    continue

                samples += 1
                # Relative comparison: streaming while the stop button matches
                # better than the mic; ended once the mic region matches better.
                matching = stop_score < mic_score
                if matching:
                    samples_streaming += 1
                    non_match_streak = 0
                else:
                    samples_idle += 1
                    non_match_streak += 1
                    if non_match_streak >= DEBOUNCE_FRAMES:
                        elapsed = time.time() - started_at
                        print(f"      ✓ Streaming ended at t={elapsed:.1f}s "
                              f"(mic matched better than stop for {non_match_streak} "
                              f"frames; stop={stop_score:.1f} mic={mic_score:.1f}).")
                        mark("streaming_ended")
                        # Arm the freeze watchdog NOW — only the post-streaming
                        # sequence runs from here on, and it should never sit
                        # static for >FREEZE_WATCHDOG_TIMEOUT_S. During streaming
                        # itself, MCP tool calls can legitimately freeze the UI
                        # for 60-120s — those aren't stuck, so the watchdog
                        # stays off during the streaming-poll phase.
                        freeze_stop = start_freeze_watchdog(tmpdir)
                        print(f"      [freeze-watchdog] armed (abort after "
                              f"{FREEZE_WATCHDOG_TIMEOUT_S}s of zero screen change)")
                        if args.no_readthrough:
                            # Product-demo / non-news caller: stop shortly after
                            # streaming ends. Brief settle so ffmpeg captures the
                            # final brief state cleanly without the news-style
                            # scroll dance.
                            print(f"      [--no-readthrough] settling 1.0s then stopping recording...")
                            time.sleep(1.0)
                        else:
                            # News default: post-streaming sequence (wake →
                            # scroll-to-top with verify+retry → smooth scroll-
                            # down). Shared helper so the wake-retry fix lives
                            # in one place.
                            run_post_streaming_scroll_sequence(tmpdir, mark)
                        break
                if samples % 25 == 0:  # status every ~5s
                    elapsed = time.time() - started_at
                    state = "streaming" if matching else f"idle? ({non_match_streak}/{DEBOUNCE_FRAMES})"
                    print(f"      [t={elapsed:5.1f}s]  stop={stop_score:5.1f} mic={mic_score:5.1f}  state={state}")
                time.sleep(POLL_INTERVAL_S)
            else:
                print(f"      ⚠️  Hit MAX_RECORDING_S ({MAX_RECORDING_S}s). Cutting off.")
                mark("streaming_ended")
                freeze_stop = start_freeze_watchdog(tmpdir)
                print(f"      [freeze-watchdog] armed (abort after "
                      f"{FREEZE_WATCHDOG_TIMEOUT_S}s of zero screen change)")
                if args.no_readthrough:
                    # Even on cutoff, --no-readthrough means stop without scroll dance.
                    print(f"      [--no-readthrough] settling 1.0s then stopping recording...")
                    time.sleep(1.0)
                else:
                    # News default: run the full scroll-up + smooth-scroll-down
                    # sequence so the recording ends with a clean read-through.
                    run_post_streaming_scroll_sequence(tmpdir, mark)
        interrupted = False
    except KeyboardInterrupt:
        interrupted = True
        print("\n⚠️ Interrupted — stopping recording and saving what we have...")
    finally:
        # ---- Stop freeze watchdog FIRST so it can't fire during shutdown ----
        if freeze_stop is not None:
            freeze_stop.set()
        # ---- Stop ffmpeg gracefully no matter why we got here ----
        print("\n[6/6] Stopping ffmpeg...")
        stop_ffmpeg(ff)

        ended_at = time.time()
        duration = ended_at - started_at
        print(f"      ✓ Recording saved: {raw_mp4.relative_to(REPO_ROOT)}  ({duration:.1f}s)")

        # ---- Auto-trim: cut the scroll-up motion segment from raw.mp4 ----
        # The scroll-up [streaming_ended → scroll_to_top_done] is a fast
        # synthetic-input flicker we don't want viewers to see. Splice it
        # out into a separate trimmed.mp4 alongside the raw for review.
        trimmed_mp4 = slot / "trimmed.mp4"
        trim_ok = False
        if (
            "streaming_ended" in phases and "scroll_to_top_done" in phases
            and not interrupted
        ):
            cut_start = phases["streaming_ended"]
            cut_end = phases["scroll_to_top_done"]
            print(f"\n      Trimming scroll-up segment [{cut_start:.2f}s → {cut_end:.2f}s] "
                  f"({cut_end - cut_start:.2f}s) → {trimmed_mp4.relative_to(REPO_ROOT)}")
            trim_ok = trim_segment(raw_mp4, trimmed_mp4, cut_start, cut_end)
            if trim_ok:
                print(f"      ✓ Trimmed:         {trimmed_mp4.relative_to(REPO_ROOT)}")
            else:
                print(f"      ⚠️ Trim failed; raw.mp4 still available as fallback.")

        # ---- Manifest (always written, even on interrupt) ----
        manifest = {
            "n": n,
            "prompt_file": str(args.prompt_file),
            "prompt_text": prompt_text,
            "started_at": iso_started,
            "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "duration_s": round(duration, 2),
            "interrupted": interrupted,
            "samples_total": locals().get("samples", 0),
            "samples_streaming": locals().get("samples_streaming", 0),
            "samples_idle": locals().get("samples_idle", 0),
            "samples_failed": locals().get("samples_failed", 0),
            "allow_clicks": locals().get("allow_clicks", 0),
            "claude_window_id": win["id"],
            "claude_window_bounds": win["bounds"],
            "calibration_used": str(CALIB_JSON.relative_to(REPO_ROOT)),
            # Recording-relative timestamps (in raw.mp4's timeline) for each
            # post-streaming phase boundary. Downstream editing tools use
            # these to splice specific segments.
            "phases": {k: round(v, 3) for k, v in phases.items()},
            "trimmed_file": str(trimmed_mp4.name) if trim_ok else None,
            "tuning": {
                "poll_interval_s": POLL_INTERVAL_S,
                "end_detection": "stop-vs-mic relative match",
                "debounce_frames": DEBOUNCE_FRAMES,
                "framerate": FFMPEG_FRAMERATE,
            },
        }
        manifest_path.write_text(json.dumps(manifest, indent=2))
        print(f"      ✓ Manifest:        {manifest_path.relative_to(REPO_ROOT)}")
        if interrupted:
            print(f"\n⚠️ Recording was interrupted — file is playable up to ~t={duration:.1f}s.")
            sys.exit(130)  # standard exit code for Ctrl+C
        if trim_ok:
            # capture.py is workflow-agnostic — it produces raw.mp4 +
            # trimmed.mp4 + manifest.json and exits. Each workflow's
            # orchestrator decides what runs next (news: process.py +
            # tick_cut + zoom; product-demo: Phase 3 scrub via the
            # parallax-video skill). See automation/README.md.
            print(f"\n→ Done.  Files in {slot.relative_to(REPO_ROOT)}/: "
                  f"raw.mp4 + trimmed.mp4 + manifest.json")
            print(f"   Next (news): python3 news-pipeline/tools/process.py {slot.name}")
        else:
            print(f"\n→ Done.  N{n}/raw.mp4 saved.")


if __name__ == "__main__":
    main()
