# 2026-05-20 — Spotlight Ellipse Circumscribes the Highlight Rect (×√2 scale)

**Status:** active
**Affects:** `tools/zoom.py` (`render_annotate_frame_pil` ellipse math: `rx, ry` half-axes now scaled by √2 + small additive buffer), `templates/product-demo/RENDER-GUIDE.md` (§ "Annotate-mode spotlight" updated — both ellipse geometry and the `highlight_region_pct` sizing rule), `.claude/skills/video-scriptwriting/SKILL.md` (§ "Panel content authoring" — sizing rule cross-ref added). Companion rule: the highlight rect must enclose the WHOLE conceptual unit the panel pitches, not just the inner phrase — sized to outer bounding box.

## Decision

The soft-edged elliptical spotlight that defines the bright zone for `mode: "annotate"` zooms now **circumscribes** the highlight rectangle — its half-axes are scaled by √2 so the ellipse passes through the rect's corners, not its edge midpoints. Every pixel inside `highlight_region_pct` is inside the bright zone, regardless of the rect's aspect ratio.

Concretely in `tools/zoom.py`:
```python
CIRCUMSCRIBE = 1.4142135623730951   # √2
rx = (hl_out_w / 2.0) * CIRCUMSCRIBE + src_w * 0.004
ry = (hl_out_h / 2.0) * CIRCUMSCRIBE + src_h * 0.008
```

The shape adapts to the rect's aspect — wide flat rects produce flat ovals; square rects produce circles. The aspect of the ellipse equals the aspect of the highlight, sized to contain.

## Why

Previously the half-axes equaled the rect's half-dimensions plus a small additive pad:
```python
rx = hl_out_w / 2.0 + src_w * 0.005     # = a + small
ry = hl_out_h / 2.0 + src_h * 0.012     # = b + small
```

For an ellipse `(a/rx)² + (b/ry)² ≤ 1` to contain a rect with half-widths `(a, b)`, the worst-case corner `(a, b)` must satisfy the inequality. With `rx ≈ a, ry ≈ b`, the corner sits ON the ellipse boundary at best — and with the additive pad slightly smaller than the rect dimensions, the corner falls INSIDE the bright zone marginally, but the corners are close to the dim edge. For rects with text filling the corners (paragraph blocks, multi-line cells with full-width text), the corner-text fell into the dim where the Gaussian blur transitioned the spotlight into the dim mask.

V1.2's z3 (Bottom Line paragraph spotlight, 42% × 5.9% — aspect ≈ 7:1) caught this: the user reported *"it doesn't cover everything in the paragraph, it sort of only spotlights the top half and the bottom line header words are also towards the edge of the oval shape"*. The previous math placed the ellipse's vertical extent right at the paragraph's vertical edges (`ry ≈ b`), which the Gaussian blur then partially faded into dim.

The √2 scale is the minimum factor that makes the ellipse pass through the rect's corners (when half-axes proportional to rect half-dimensions). For a rectangle of half-widths `(a, b)` and an ellipse of half-axes `(k×a, k×b)`, the corner is on the ellipse when `(1/k)² + (1/k)² = 1`, i.e. `k = √2`. So `rx, ry = a√2, b√2` is the tight-circumscribe geometry.

## Notes

- The shape adapts naturally: a rect with aspect `w:h = 10:1` produces an ellipse with aspect `10:1` (flat oval); a square rect produces a circle. The aspect of the ellipse equals the aspect of the highlight.
- The additive buffers (`src_w × 0.004` horizontal, `src_h × 0.008` vertical) absorb the Gaussian blur radius so the blur transition doesn't eat back into the rect from outside the strict ellipse bounds.
- For V1.2: z1 and z2 looked correct under the old math because their highlight rects had empty space near the corners (the Value-row text doesn't reach the cell corners; the Trajectory-cell text only fills the right portion of the row). z3's paragraph rect had text filling the rect to the corners — that's where the corner-dim issue manifested. With circumscribed scaling, all three look correct regardless of corner-fill.
- For future videos: this is a universal rule — any annotate highlight, any rect aspect, the spotlight will fully cover the rect's content. No per-video tuning needed.
- If a future video needs a TIGHTER spotlight (overshoot beyond rect corners feels too generous), the override is to scale by `k < √2` — but the math caveat is that pixels in the rect's corners will then fall into the dim zone. Generally `k = √2` is the right default for "spotlight everything in the rect" semantics.
- The Gaussian blur radius (`src_h × 0.02`) is unchanged — it provides the soft edge transition past the strict ellipse bounds. With the larger circumscribed ellipse, the effective bright spotlight (strict ellipse + blur halo) is broader, but the dim mask is still clearly visible in the corners and edges of the scaled-crop area.
