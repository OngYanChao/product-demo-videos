#!/usr/bin/env python3
"""Dump Claude's accessibility tree for debugging the auto-click logic.

USAGE:
  Run this in your terminal WHILE a permission dialog (or any UI you want to
  inspect) is currently visible in Claude desktop. It will activate Claude,
  enumerate every accessible UI element, and print them — indented by depth,
  one element per line, with role + title + description.

  python3 news-pipeline/tools/diagnose_ui.py

Output goes to stdout AND to news-pipeline/calibration/ui_dump.txt for later
inspection. If a button isn't appearing in this dump, AppleScript can't see
it — which means the UI is HTML inside the Electron WebContents view and we
need pixel-based detection as a fallback.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DUMP_PATH = REPO_ROOT / "news-pipeline" / "calibration" / "ui_dump.txt"


# AppleScript written as a regular triple-quoted raw string. Saved to a temp
# file before running, so we don't have to worry about quoting/escaping in
# `osascript -e`.
SCRIPT = r"""
on dumpElem(elem, depth, outputLines)
    if depth > 12 then return
    set padding to ""
    repeat depth times
        set padding to padding & "  "
    end repeat
    set roleStr to "?"
    set titleStr to ""
    set descStr to ""
    set kids to {}
    tell application "System Events"
        try
            set roleStr to (value of attribute "AXRole" of elem) as text
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
    set lineParts to padding & "[" & roleStr & "]"
    if titleStr is not "" then
        set lineParts to lineParts & " title=" & titleStr
    end if
    if descStr is not "" then
        set lineParts to lineParts & " desc=" & descStr
    end if
    set end of outputLines to lineParts
    repeat with k in kids
        my dumpElem(k, depth + 1, outputLines)
    end repeat
end dumpElem

tell application "Claude" to activate
delay 1.2

set outputLines to {}

tell application "System Events"
    tell process "Claude"
        set winCount to count of windows
        set end of outputLines to "# Claude process — " & winCount & " window(s)"
        repeat with i from 1 to winCount
            set end of outputLines to ""
            set end of outputLines to "## Window " & i
            my dumpElem(window i, 0, outputLines)
        end repeat
    end tell
end tell

set AppleScript's text item delimiters to (ASCII character 10)
return outputLines as text
"""


def main() -> None:
    print("Activating Claude and dumping accessibility tree...")
    print("(Make sure the UI you want to inspect — e.g. a permission dialog — is visible.)\n")

    # Write the AppleScript to a temp file and invoke via osascript <file>.
    # This sidesteps quoting issues with `osascript -e <multi-line>`.
    with tempfile.NamedTemporaryFile(mode="w", suffix=".applescript", delete=False) as f:
        f.write(SCRIPT)
        script_path = f.name
    try:
        result = subprocess.run(
            ["osascript", script_path],
            capture_output=True, text=True,
        )
    finally:
        Path(script_path).unlink(missing_ok=True)

    if result.returncode != 0:
        print("❌ AppleScript failed:")
        print(result.stderr)
        sys.exit(1)

    DUMP_PATH.parent.mkdir(parents=True, exist_ok=True)
    DUMP_PATH.write_text(result.stdout)
    print(result.stdout)
    print(f"\n→ Also saved to: {DUMP_PATH.relative_to(REPO_ROOT)}")

    # Quick scan: AXButton lines that mention 'allow' (case-insensitive)
    matches = [
        line for line in result.stdout.splitlines()
        if "axbutton" in line.lower() and "allow" in line.lower()
    ]
    print(f"\n→ Buttons matching 'allow' (case-insensitive): {len(matches)}")
    for m in matches:
        print(f"   {m.strip()}")


if __name__ == "__main__":
    main()
