# 2026-05-19 — Cursor-Clear Region Widened for Annotate Mode

**Status:** active
**Supersedes:** `decisions/2026-05-18-cursor-clear-rule.md` (extends — original rule still in effect)
**Affects:** `tools/zoom.py` (cursor-clear region calculation in `main()` for annotate directives), `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #16 updated)

## Decision

For `mode: "annotate"` directives with `wait_cursor_clear: true`, the cursor-clear region is no longer just `highlight_region_pct` (the specific subsection). It is a synthetic rectangle:

```
cursor_clear_region = [
  highlight_region_pct.x,      # readable-column x position
  zoom_region_pct.y,           # full visible reading area top
  highlight_region_pct.width,  # readable-column width
  zoom_region_pct.height,      # full visible reading area height
]
```

This means: a cursor sitting on **any row of the table being zoomed** counts as obscuring (e.g., cursor on Quality while z1 highlights Value still blocks the zoom). A cursor in the dark padding to the right/left of the content column does NOT count — it's not on text.

Hold-mode and follow-mode are unaffected; they continue to use `region_pct`.

## Why

The original Hard Rule #16 (cursor-clear) used `highlight_region_pct` to define the region. For V1.2's z1 (Value row highlight), that worked when the cursor was clearly off the score table — but failed when the cursor sat on the Quality row (the row immediately above Value). The motion-centroid detector reported the cursor was "outside" the Value-only rectangle, so the zoom fired with the cursor still visibly on score-table text — defeating the rule's purpose.

Widening to `zoom_region_pct` was the first attempted fix, but `zoom_region_pct` covers the entire visible content area including the dark UI padding on the right of the brief column. A cursor at x=74.9% (just past the score table, in dark area) was considered "inside" the zoom_region (which extends to x=75%), so the cursor-clear scan ran out the 4s window and fell back to base_t — leaving the zoom firing with the cursor on text.

The synthetic combined region resolves both failures: x bounds come from `highlight_region_pct` (the actual text column), y bounds come from `zoom_region_pct` (the full reading area). A cursor on any row of the table is "inside" because it sits in the text column's x range. A cursor in the dark padding is "outside" because it's outside the text column's x.

## Notes

- Verified on V1.2 z1: cursor-clear correctly advances `source_t` from 49.00 → 50.25, where the cursor sits in the dark area to the right of the score table.
- The detection itself remains motion-centroid-based. Fully static cursors (I-beam parked on text, no movement) still aren't detected — the fallback runs the 4s window then defaults to base_t. That's a known limitation; mitigations include re-recording with deliberate cursor moves between content beats, or increasing `cursor_clear_max_delay` per-directive.
- Template-based cursor detection (cursor shape correlation, not motion) would resolve the static-cursor case. Deferred — current behavior is acceptable for V1.2; revisit when a static-cursor video surfaces the limitation more sharply.
- For unusual layouts where the readable x range diverges from `highlight_region_pct.x_extent` (e.g., when `highlight_region_pct` is a single cell in a wide row but the full row is visible), introduce an explicit `cursor_clear_region_pct` field per directive. Not needed for any current V1.2 directive.
