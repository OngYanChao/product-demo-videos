# 2026-05-20 — Overlay Ease Must Match Camera Ease

**Status:** active
**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #18 added), `templates/product-demo/index.html` (`annotatePanel()` uses `sine.inOut`), `templates/product-demo/RENDER-GUIDE.md` (panel animation invariant)

## Decision

Any overlay graphic (annotation panel, lower third, caption) that animates synchronously with a camera move (annotate zoom-in/out, hold-mode zoom-in/out, follow-mode pan-in/out) must use the **same ease curve** as the camera. Project default: `tools/zoom.py` uses `easeInOutSine` for annotate-mode ease-in and ease-out. The composition template's GSAP timeline animates panels with `ease: "sine.inOut"` (GSAP's name for the same curve) and matching `duration: 1.0` (= zoom.py's `DEFAULT_ANNOTATE_EASE_S`).

## Why

V1.2 preview at composition_t = 55.5 (= 0.25s into z1's 1.0s ease-in) showed the panel ~44% faded in while the camera was only ~15% zoomed in. Both started at composition_t = 55.25 — the panel wasn't *temporally* early, it was *progress-curve* early. The panel used `power2.out` (fast start, slow end) while the zoom used `easeInOutSine` (slow start, fast middle, slow end). At equal progress through 1.0s of animation, the two curves diverge by ~30 percentage points in the first quarter, which the eye reads as "panel leading the zoom."

User complaint: *"the panel fade in should happen at the same time as the zoom in. it's too early, it comes in when the scrolling is still happening / before the zoom in."* The fix isn't shifting the panel timing (both motions already started at the same `inT` = composition_t = 55.25) — it's matching the curve. With `sine.inOut`, the panel is at ~15% progress when the camera is at ~15% progress, both arriving at 100% simultaneously at the end of the 1.0s window.

## Notes

- GSAP's `sine.inOut` corresponds to the same `(1 - cos(πt)) / 2` half-sinusoid that `tools/zoom.py` uses for `ANNOTATE_EASE_NAME = "easeInOutSine"`. Symmetric S-curve, identical derivative profile.
- If a future template needs a different camera ease (e.g., a snappy `easeOutExpo` for fast-paced cuts), the matching overlay ease must change in the same commit.
- The overlay's animation *duration* should also match the camera's ease duration. If `zoom.py` changes `DEFAULT_ANNOTATE_EASE_S` from 1.0 to 0.6, the panel `duration` in `annotatePanel()` must change too.
- Cross-stream consistency: lower-third entrances during `mode: "follow"` segments (not currently used) would inherit the follow-zoom's ease, not the annotate ease. The rule is *match the camera move you're synced to*, not *use sine.inOut everywhere*.
- Companion rule: Hard Rule #12 — annotation panel `in/out_recording_t` must be re-derived against the zoomed-file segment timing after every re-zoom or `--clean-source-ranges` change. A panel can be in-sync curve-wise and still "early" if its timing references stale zoom output.
