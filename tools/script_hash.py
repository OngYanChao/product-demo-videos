#!/usr/bin/env python3
"""
tools/script_hash.py — Hash a voiceover script's spoken content.

Used by tools/render.py to cache HeyGen avatar clips: same spoken VO → same
avatar clip → reuse cached clip → zero API cost. The hash is computed over
just the spoken text (frontmatter, stage directions, section headers,
tables, and other markdown decoration are stripped) so iterating on
production notes or timing metadata without changing the words doesn't
invalidate the cache.

Usage:
    python tools/script_hash.py "scripts/V1 voiceover script.md"
    python tools/script_hash.py "scripts/V1 voiceover script.md" --show-vo
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path


def extract_spoken_vo(script_path: Path) -> str:
    """Extract just the spoken VO from a script file.

    Convention enforced (documented in video-scriptwriting skill):
      - Spoken VO lives under a `## Voiceover script` (or `## VO`) heading.
      - Within that section, every spoken line is wrapped in a Markdown
        blockquote (`> ...`).
      - Stage directions (`> **[bracketed bold]**`) are also blockquoted but
        get filtered out below.

    Strips:
      - YAML frontmatter
      - Everything outside the `## Voiceover script` section (drafting
        metadata, workflow notes, hallucination logs, etc. don't leak into
        the spoken VO that gets sent to HeyGen)
      - Non-blockquote lines within the section (commentary)
      - Stage directions (`**[...]**`-only lines)
      - Tables, sub-headers, horizontal rules, code blocks, list markers

    Falls back to whole-document blockquote scanning if no `## Voiceover
    script` heading is found (still safer than grabbing every prose line).
    """
    text = script_path.read_text()

    # Strip YAML frontmatter at top of file
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            text = text[end + 5:]

    # Restrict to the `## Voiceover script` (or `## VO`) section if present.
    section_start = None
    section_end = None
    for m in re.finditer(r"(?m)^(##\s+.+)$", text):
        heading = m.group(1).lower()
        is_vo_heading = (
            "voiceover" in heading
            or "vo script" in heading
            or re.match(r"^##\s+vo\s*$", heading) is not None
        )
        if section_start is None and is_vo_heading:
            section_start = m.end()
        elif section_start is not None and section_end is None:
            section_end = m.start()
            break

    if section_start is not None:
        section = text[section_start:section_end] if section_end else text[section_start:]
    else:
        section = text  # fallback: scan whole body for blockquote lines

    out = []
    in_code_block = False

    for raw in section.split("\n"):
        line = raw.rstrip()
        stripped = line.strip()

        # Toggle inside fenced code block
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # Spoken VO is always blockquoted — skip everything else (commentary,
        # tables, headers, horizontal rules, prose between VO blocks).
        if not line.startswith(">"):
            continue

        # Strip blockquote prefix
        line = line[1:].lstrip()
        stripped = line.strip()

        # Skip empty after stripping (the `>` separator lines)
        if not stripped:
            continue

        # Skip stage directions: line that is entirely **[...]**
        if re.match(r"^\*\*\[.*\]\*\*\s*$", stripped):
            continue

        # Skip Markdown list-marker-only lines
        if re.match(r"^[-*]\s*$", stripped):
            continue

        out.append(stripped)

    return "\n".join(out)


def hash_script(script_path: Path) -> str:
    """Hash the spoken VO content. Returns a 12-character hex digest."""
    vo = extract_spoken_vo(script_path)
    # Normalize: collapse all whitespace into single spaces
    normalized = " ".join(vo.split())
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return digest[:12]


def main():
    parser = argparse.ArgumentParser(
        description="Hash a VO script's spoken content for cache key.",
    )
    parser.add_argument("script", type=Path, help="Path to the voiceover script .md file")
    parser.add_argument(
        "--show-vo", action="store_true",
        help="Print extracted VO text instead of the hash (for debugging)",
    )
    args = parser.parse_args()

    if not args.script.exists():
        print(f"error: {args.script} not found", file=sys.stderr)
        sys.exit(1)

    if args.show_vo:
        print(extract_spoken_vo(args.script))
    else:
        print(hash_script(args.script))


if __name__ == "__main__":
    main()
