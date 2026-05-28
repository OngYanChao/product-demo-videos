# 2026-05-19 — Annotate Mode Default: Soft-Edged Elliptical Spotlight

**Status:** active
**Supersedes:** `decisions/2026-05-19-annotate-border-dot-navy.md` (the navy rectangle border + numbered dot is now retired; its colour decisions are moot since the elements themselves are gone)
**Affects:** `tools/zoom.py` (`render_annotate_frame_pil` — ellipse mask block; rectangle-border + numbered-dot paths preserved in `if False:` blocks), `templates/product-demo/RENDER-GUIDE.md` (spotlight invariants), `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #17 wording), `.claude/skills/parallax-video/SKILL.md` (dispatch rows reference spotlight instead of border + dot), `screen recordings/V1/1vid_zooms.json` (no `halo_mode` keys)

## Decision

The default visual for `mode: "annotate"` directives is a **soft-edged elliptical spotlight** centered on `highlight_region_pct`. The bright oval area sits at full source brightness; the surrounding content within the scaled-crop area is dimmed at 60 % opacity (`ANNOTATE_DIM_ALPHA = 153`); the ellipse edge is Gaussian-blurred (radius ≈ 2 % of source height) so the transition reads as lighting, not a graphic cutout.

Ellipse half-axes hug the highlight rectangle with a small additive buffer (~0.5 % src_w horizontal, ~1.2 % src_h vertical). The bright area matches the area of text the directive names — no overshoot into adjacent content.

**Retired** from the default visual:
- Rectangular highlight border (navy-400 stroke around `highlight_region_pct`).
- Numbered callout dot beside the highlight on the recording.
- `halo_mode` flag (no longer meaningful — its semantic was "skip dim mask", which was the alternative to the box+dim default; with the box now gone, halo would just produce a left-anchored zoom with no annotation visual at all).

Both retired render paths (rectangle border, numbered dot) are preserved in `tools/zoom.py` inside `if False:` blocks for easy restore if a future video benefits from a UI/diagram aesthetic. The constants (`ANNOTATE_HIGHLIGHT_BORDER_COLOR`, `ANNOTATE_HIGHLIGHT_BORDER_PX`, `ANNOTATE_HIGHLIGHT_PAD_PX`, `ANNOTATE_CALLOUT_DOT_*`) remain in the source; only the call sites are gated off.

The right-side annotation panel still carries the numbered badge (`.ap-number` in `index.html`) so the per-callout ordering signal is preserved — just not duplicated on the recording side.

## Why

The rectangle-border + numbered-dot styling read as a graphic / UI element: "here is a box labeled '1' next to the thing." That framing competes visually with the right-side panel (which already provides the number + the explanatory copy) and pulls the eye to two separate "callout zones" per moment.

The elliptical spotlight is a lighting effect: "the rest of the page is in shadow; this is what you're meant to read." Single emphasis zone on the recording side, paired with the panel on the right. The Gaussian-blurred edge prevents the ellipse from reading as a circular badge — it fades into the dim like a flashlight cone.

User request was explicit: "delete the current preview, … try again. recreate the spotlight effect with the remaining area dimmed". Two follow-ups refined the geometry: "the area covered by the spotlight matches the area of text" (ellipse hugs the highlight rect tightly, doesn't overshoot) and "remove the numbering beside the spotlight now" (drop the on-recording numbered dot).

## Notes

- Spotlight readability check on V1.2: inside ellipse text ~195 brightness; outside ~40. ~5× contrast ratio without harsh edge. Reads as a lighting effect, not a cutout.
- For very flat highlights (a single text row spanning most of the brief column width — e.g. z3's first paragraph line at 42 % × 5.9 %), the ellipse stretches to ~5:1 aspect. Acceptable — still reads as a soft horizontal spotlight. If a future video's flat highlight degrades into a "horizontal slot" look, options are: (a) tighten the highlight to a shorter phrase, (b) add a minimum aspect-ratio clamp to `ry` so the ellipse never goes flatter than e.g. 4:1.
- `halo_mode` is gone. No replacement — the only annotate visual is spotlight. If a video genuinely needs the recording's full brightness preserved while still showing the panel, that's no longer covered by `mode: "annotate"` — author a `mode: "hold"` directive instead and let the panel substitution stand on its own.
- The blur radius (`src_h × 0.02`) was tuned by eye against V1.2. Higher = softer fade, lower = more cutout-like. If a future video's spotlight reads too soft (loses crispness around small text) or too hard (still feels like a graphic shape), this is the dial.
