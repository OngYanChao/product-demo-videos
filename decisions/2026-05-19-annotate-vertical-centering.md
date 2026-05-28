# 2026-05-19 — Annotate-Mode Highlight Must Be at the Composition's Vertical Center

**Status:** active
**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (new Hard Rule #17), `tools/zoom.py` (`render_annotate_frame_pil` y_offset math + zoom_region aspect validation + y_offset clamping), `templates/product-demo/RENDER-GUIDE.md` (annotate-mode framing invariant)

## Decision

For every `mode: "annotate"` zoom directive, the highlighted content must land at the composition's vertical center (comp y=540 in 1920×1080). This is enforced two ways, both required:

1. **Author the source so the highlight is naturally near the source viewport's vertical center.** The recording must be at a scroll position where the target row/section sits at roughly source y=44.8% (= composition's center mapped back to source coordinates for a 16:10 source @ 16:9 comp). Pick `source_t` to land on a moment where the page has scrolled appropriately. If the natural recording doesn't have such a moment, re-record. **Do not** pick a `source_t` where the highlight is near a source edge and hope the zoom math compensates — the math can't, and the resulting frame either has a black band or a clamped off-center highlight.

2. **`tools/zoom.py` enforces it automatically as a fallback.** The `render_annotate_frame_pil` math computes `y_offset_target = visible_h_in_src/2 - hl_cy_in_scaled` and clamps to `[visible_h_in_src - scaled_h, 0]` to avoid black bands. The aspect-validation check (`zh_pct/zw_pct >= visible_h_in_src * src_w / (target_w_px * src_h)`) errors out if the zoom_region is too shallow for the comp height. These keep the output rendering coherent, but they DO NOT excuse step 1 — if the source has the highlight near an edge, the clamp will produce an off-center highlight and that's a failure of the rule, not a feature.

Verification: at each annotate hold, the highlight rectangle's center sits at comp y=540 ± a few pixels. If it lands lower or higher, the source needs a different `source_t` (or a different highlight target row).

## Why

The annotate-mode pattern is "left-anchored zoomed content + right-side panel + dim everywhere except the highlight + numbered callout dot." The visual contract with the viewer is that the highlight is the FOCAL POINT — the thing the panel content (and the VO) is about. Vertical centering keeps the highlight at the natural eye-resting point of the frame, in line with the right-side panel.

Without vertical centering, the highlight drifts to a corner of the frame. The eye then has to choose between the off-center highlight and the centered panel — splitting attention. The dim mask doesn't fix this; it just makes the off-center positioning more obvious by drawing a hard outline somewhere unexpected.

The trigger for this rule was V1.2: z2's `highlight_region_pct` was on the Total trajectory cell at source y=84–90% (the page hadn't scrolled — Total was near source bottom). Strict centering math would have created a 600+ px black band below the scaled crop; the clamp prevented the band but left Total stuck in the bottom-right of the comp. The fix was to shift `z2.source_t` from 49.80 → 52.85, where the natural recording has Total at source y=42–50% (straddling source center). The source playback between z1 and z2 then shows the page scrolling naturally until Total reaches center, and z2 fires.

## Notes

- For 16:10 sources @ 16:9 comp with top-anchored cover, `visible_h_in_src = src_w / (16/9)`. For V1.2's 3420×2146: 1924 px. Comp center maps to source y=962 ≈ 44.8% of source height.
- For 16:9 native sources, `visible_h_in_src = src_h`. Comp center maps to source y=50%.
- The aspect validation: for left content area of 62% × src_w, the zoom_region's height/width ratio must be ≥ `visible_h_in_src × src_w / (target_w × src_h)`. For V1.2: zh/zw ≥ 1.446. Below this, the scaled crop doesn't fill the comp's visible vertical extent and the result is a solid black band (not a dim mask — there's no content to dim).
- This rule replaces the implicit "center on whatever the source happens to show" behavior that produced the V1.2 z2 issue.
- It does NOT apply to `mode: "follow"` (camera-pan with continuous playback) or `mode: "hold"` (centered camera-pan zoom) — those have different framing contracts. Only `annotate`.
