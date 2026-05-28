# 2026-05-18 — Cursor-Clear Rule for Output-Brief Zooms

**Status:** active
**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #16), `tools/zoom.py` (`wait_cursor_clear` flag + `find_cursor_clear_source_t` + `detect_cursor_position`), `screen recordings/V1/1vid_zooms.json` (z1, z2, z3 set `wait_cursor_clear: true`)

## Decision

Hold-mode zooms targeting the **output brief** content (rendered text the viewer reads — score panel, trajectory column, bottom-line verdict, etc.) must not trigger while the cursor is sitting on that text. Scope is narrow: applies only to brief-content zooms. Does NOT apply to zooms on tool-call loading sections (chat activity area) — cursor position over the chat is fine while the viewer is watching tool calls fire.

Encoded as the `wait_cursor_clear: true` flag on a zoom directive in `1vid_zooms.json`. Default is `false` (opt-in per directive). When set, `tools/zoom.py` auto-advances `source_t` until the cursor has moved outside the zoom's `region_pct`. Fallback after `DEFAULT_CURSOR_CLEAR_MAX_DELAY_S = 4s` if no clear moment is found within that window.

## Why

A pause-zoom that holds a still frame with the cursor obscuring the very content the viewer is supposed to read defeats the purpose of the zoom. The cursor sitting on a row of the score panel — or worse, on the trajectory text — pulls the eye to a distraction instead of the meaning the VO is delivering.

The scope distinction (output brief only, not tool-call loading) matters because tool-call zooms target the chat-activity column where cursor presence is part of the natural visual state — the viewer isn't reading specific text there, they're watching skill calls fire. Requiring cursor-clear on those would over-constrain the zoom timing for no visual benefit.

## Notes

- Implementation uses inter-frame pixel-diff to detect cursor position via motion centroid; for fully-static recordings (cursor never moves after content settles), the rule falls back to the user-specified `source_t` after `cursor_clear_max_delay`. Future improvement: template-matching cursor detection that works on static frames too.
- V1.2's three brief-targeting zooms (z1 score panel, z2 trajectory, z3 bottom line) opt in. The follow-mode `z0_prompt_typing` doesn't apply — follow-zoom expects continuous cursor activity by design.
- The flag is structural metadata in the zoom directive (alongside `mode`, `source_t`, `region_pct`, `wait_cursor_clear`); it's read by `tools/zoom.py:main()` before zoom planning.
