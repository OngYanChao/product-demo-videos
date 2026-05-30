# 2026-05-30 — z0.ease = 1.5s standard + minimum scrubbed buffer 1 (Hard Rule #28)

**Scope:** Product-demo pipeline (V<N>, I<N>). News-pipeline's auto-zoom (`tick_cut.py`) is exempt — uses its own ease defaults.

**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #28 added; Hard Rule #22 amended to reference the standard).

## Decision

Two related codifications:

**(a) z0.ease = 1.5s is the standard.** V1 and V2 both used 1.5s by convention; codifying it as a Hard Rule prevents drift. When z0.ease varies between V<N>, the prompt-typing zoom pace feels inconsistent — viewer notices "why does the typing zoom keep getting faster?"

**(b) Scrubbed buffer 1 must be ≥ 2.5s.** With z0.ease=1.5s and z0b.margin=1.0s, the gap between z0 ending and z0b's ease-in starting must be at least their sum. If `scrub.py`'s freeze compression brings buffer 1 below this floor, the standard transitions don't fit — one of the eases would have to be shortened (visual inconsistency) or the zooms would overlap (zoom.py error).

Failsafe: Phase 3 freeze-frame injection in buffer 1 to extend it to ≥2.5s. Same architectural pattern as Rule #27 (capture-time primary + Phase 3 failsafe).

## User observation (verbatim)

> "First issue, why is the zoom in on the prompt typing and the chat box so fast? Compare this v3 version with v1 there is a very clear speed difference. Why does it keep getting faster and faster? I thought we already outlined or codified it to be a certain speed."

The V3 preview showed z0.ease=0.5s — 3× faster than V1+V2's 1.5s convention. Comparing across V1/V2/V3:

| Video | z0.ease | scrubbed buffer 1 | Notes |
|---|---|---|---|
| V1 | **1.5s** | ~3.0s | natural recording with longer post-typing gap |
| V2 | **1.5s** | ~3.4s | similar |
| V3 (before fix) | **0.5s** ← inconsistent | only 2.03s | scrub.py compressed buffer 1 too aggressively |

Diagnosis: V3's Cowork response started ticks quickly, so the raw post-typing buffer was short to begin with; scrub.py's freeze compression further squeezed it down to 2.03s. With the standard 1.5s ease, z0 would end at 10.06s but z0b would need to start at 9.59s — a 0.47s overlap. I shortened z0.ease in V3 to fix the overlap, which was the wrong direction — should have extended buffer 1 instead.

## Why a rule (not just convention)

The convention was implicit in V1/V2. Without explicit codification, the wrong fix for V3 (shortening ease) was a "natural" choice that drifted from the standard. The rule prevents this drift and provides a documented failsafe pattern for the underlying cause (tight scrubbed buffer 1).

## Why 2.5s minimum

2.5s = z0.ease (1.5) + z0b.margin (1.0). This is the tightest scrubbed buffer 1 that allows the standard transitions without overlap:
- z0 ends at `T_click + z0.ease` (scrubbed) — for V3 with T_click=8.56, z0 ends at 10.06
- z0b's ease-in starts at `T_first_tick − z0b.margin` (scrubbed) — z0b.ease-in must complete at T_first_tick per Hard Rule #23
- For these to not overlap: `T_first_tick − T_click ≥ z0.ease + z0b.margin = 2.5s`

A small safety buffer (~0.1s) is included in the failsafe to handle measurement jitter.

## Why both mechanisms

Same logic as Rule #27:

**Primary (z0.ease = 1.5s standard) alone** isn't enough — it just specifies what the ease should be. Doesn't help when the scrubbed buffer can't accommodate it.

**Failsafe (Phase 3 freeze-frame injection) alone** would let z0.ease drift across videos. With the standard codified, the failsafe is the mechanism that makes the standard achievable for any recording.

Together: every V<N> uses the same z0.ease (consistency) AND the buffer is always extended when needed (achievability).

## Implementation note — inject position matters

The freeze-frame inject must NOT be near `T_first_tick_scrubbed`:
- If the 50ms slice contains the tick animation start, the cloned padding freezes a frame mid-tick
- Then v2 (which starts at the same source position as v1) re-plays the slice, including the tick
- Result: tick "fires twice" — once at the slice, once when v2 re-plays. Looks broken.

Discovered the hard way during V3 implementation: first attempt injected at position 10.54-10.59, which overlapped with the tick at scrubbed 10.593. Resulting video had the tick visibly firing → freezing → un-firing → firing again. Wrong.

Fixed by injecting at the midpoint of buffer 1 (scrubbed 9.0 for V3), well inside the dead "Working on it…" state where there's no tick animation to disturb. The slice frame and the cloned frames all show the same "Working on it…" state; v2 re-plays the same dead state; no visible artifact.

Rule of thumb: pick the inject position at `T_typing_end + (scrubbed_buffer_1 / 2)` (midpoint of buffer 1). Don't go within ~0.5s of `T_typing_end` (cursor still in motion from typing→submit click) or within ~0.5s of `T_first_tick_scrubbed` (tick animation about to start).

## V3 outcome

- Original V3 scrubbed: 36.35s, buffer 1 = 2.03s
- Injected 0.55s freeze at scrubbed 9.0
- New V3 scrubbed: 36.90s, buffer 1 = 2.57s
- Updated zooms.json: z0.ease back to 1.5s, z0b.source_t shifted to 10.13, all annotates shifted by +0.55s
- Re-zoom: vid3_zoomed.mp4 = 53.38s
- Re-render preview: outputs/V3/preview.mp4 = 65.38s with V1/V2-consistent z0 ease

## Cross-references

- Hard Rule #22 (z0 sizing — amended to reference the 1.5s standard): `decisions/2026-05-22-zoom-skeleton-standardization.md`
- Hard Rule #23 (z0b ease ≤ margin = 1.0): `decisions/2026-05-24-z0b-starts-on-checklist.md`
- Hard Rule #27 (sibling failsafe pattern — Phase 3 freeze-frame injection): `decisions/2026-05-30-minimum-top-hold.md`
- V3 capture context: `screen recordings/V3/manifest.json`
