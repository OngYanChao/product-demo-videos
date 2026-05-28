# 2026-05-24 — z0b ease-in starts when the checklist is fully visible, not after a fixed buffer

**Status:** active
**Refines:** `decisions/2026-05-22-zoom-skeleton-standardization.md` (z0b's "~3s after z0 ease-out" wording is replaced by a content-anchored start-time), `decisions/2026-05-23-tick-window-compression-moves-to-phase-3.md` (z0b sizing under ±margin is made precise).
**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #23, z0b bullet), `.claude/skills/parallax-video/SKILL.md` (zoom dispatch row's z0b spec), `screen recordings/V2/vid2_zooms.json` (z0b directive corrected).

## Decision

z0b's `source_t` and `ease` are determined by the scrubbed file's structure — not by a fixed "~3s after z0 ease-out" heuristic.

- **`z0b.source_t` = start of zone (b) in scrubbed time** — i.e., the scrubbed timestamp where the source jumps from buffer (1) compression into the locked tick window. This is the first frame where the Progress sidebar's full checklist is reliably visible.
  - Equivalently: `z0b.source_t = T_first_tick − margin` (since the first keep_range in the gap-cut output starts at `T_first_tick − margin` in raw, and zone (b) is locked at 1×, so the same offset applies in scrubbed-t).
- **`z0b.ease` ≤ `margin`** (default `margin = 1.0s` → `ease = 1.0s`). Ease-in completes EXACTLY at `T_first_tick`. The viewer sees: checklist appears → camera approaches → camera settles → first checkmark fires.
- **`z0b.duration` = `(T_(N-1) + margin) − z0b.source_t + ease_out_duration`**. With `ease_out = ease`, this simplifies to `(T_(N-1) + margin) − (T_first_tick − margin) + ease`.

Pre-`source_t` content (the buffer (1) compressed period — "Working on it…" / 3-circle placeholder) plays at full frame between z0 ease-out completion and z0b ease-in start. This is intentional — the viewer should perceive the loading state without zoom emphasis until there's something concrete to zoom on.

## Why

V2 production exposed the failure mode. The 2026-05-22 ADR specified z0b "~3s after z0 ease-out" — a fixed offset disconnected from the recording's actual content. Under the post-2026-05-23 multi-zone scrub, buffer (1) compression depends on the recording's specific loading length: V2's buffer (1) compresses ~3.5s, V1's was different. A fixed "~3s after z0" puts z0b's ease-in inside buffer (1) — the camera is zooming toward an area that doesn't yet show the checklist.

User feedback:

> "the zoom in on the progress taskbar is way too early. The zoom-in should only start once the checklist appears."

The correct anchor isn't a fixed offset — it's the content state. The checklist is visible iff source playback has entered zone (b). z0b's ease-in must start AT zone-b-start in scrubbed-t.

The `ease ≤ margin` constraint follows from the existing Hard Rule #23 sub-bullet ("ease-in must complete BEFORE T1 fires so the 1s pre-T1 hold plays inside the held portion"). With `source_t = T_first_tick − margin` and ease ≤ margin, ease-in completes at or before `T_first_tick`. The previous standard of `ease=1.5s` is incompatible with `margin=1.0s`; the rule resolves the conflict in favor of margin (which is set per the gap-cut rule's user-facing buffer time) — ease defers.

## How to apply (enforcement)

For every future product_demo zoom plan:

1. After Phase 3 produces `vid<N>_scrubbed.mp4`, compute `Z_start` = scrubbed-t at which zone (b) begins. Equivalent: `Z_start = T_first_tick − margin` where `T_first_tick` and `margin` come from `vid<N>_ticks.json`.
2. Set `z0b.source_t = Z_start`. Document this in the directive's `_beat` field.
3. Set `z0b.ease = margin`. Default `margin = 1.0s` → `ease = 1.0s`.
4. Compute `z0b.duration = (T_(N-1) + margin) − Z_start + ease`. Tighten if the trim+concat tick window's tail is short.
5. Do NOT extend z0's `duration` to cover the buffer (1) gap. The 2–4s of full-frame loading between z0 retraction and z0b approach is intentional dwell on the "Starting up…" state.

For V1 (canary, produced under the pre-Phase-3-tickcut pipeline): not retroactively reapplied. V1's existing zoom plan stands until a future re-record. The new rule applies to V2 onward.

## Notes

- The rule is a refinement to Hard Rule #23's existing prose. The standard `ease 1.5s` recommendation in that rule is replaced with `ease = margin` (default 1.0s). The standard region `[80, 0, 20, 30]` and zoom `2.5×` are unchanged.
- `tools/zoom.py` enforces nothing automatically — the directive author is responsible for setting `source_t` and `ease` consistent with the rule. Hard Rule #23's existing "ease-in must complete BEFORE T1 fires" constraint is the validation; orchestrator dispatch should check it.
- If a future recording has `margin ≠ 1.0` (e.g., a slower-paced loading sequence with `margin = 1.5`), the rule scales — `ease` matches whatever `margin` is. The constraint is `ease ≤ margin`, never `ease = 1.5` regardless of margin.
