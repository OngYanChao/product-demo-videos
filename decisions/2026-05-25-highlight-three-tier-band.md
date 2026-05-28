# 2026-05-25 — Annotate highlight height splits into three tiers

**Status:** active
**Refines:** `decisions/2026-05-22-zoom-skeleton-standardization.md` (Hard Rule #24's flat "≤15%" cap is replaced by a three-tier band).
**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #24 reworded), `.claude/skills/video-scriptwriting/SKILL.md` (§ Panel content authoring — "WHOLE conceptual unit" rule clarified against the new band).

## Decision

Annotate highlight rect height is governed by what the paired VO line names, with three tiers:

| What the VO names | Highlight height | Resolution |
|---|---|---|
| **Specific row / cell / phrase** | ≤15% | Tight bounding box around the named element. Single spotlight. |
| **Conceptual unit (header + paragraph)** | 15–25% | Single spotlight covering the WHOLE unit (header + body paragraph). The 15% target relaxes to the natural height of the unit, up to 25%. |
| **Multi-paragraph section / table block / cross-row data** | >25% threshold | SPLIT into sub-annotates per Hard Rule #24's multi-VO-target rule. Shared panel across the cluster per Hard Rule #24's shared-panel allowance + Hard Rule #25's sum-of-durations rule. |

The 25% threshold is the hard cap for a single spotlight. Beyond 25%, the spotlight illuminates too much of the frame; the dim becomes the minority and the spotlight loses its "look here" function.

**Coupling rule:** spotlight size pairs with panel body length.
- **Long-body panel (>15 words) → tight spotlight (≤15%)**. Viewer's eye is on the panel; the spotlight needs to be small enough to find quickly without distracting from the panel read.
- **Short-body or bare-callout panel → wider spotlight (15-25%) acceptable**. Viewer has time to scan a larger illuminated area; coverage of the whole conceptual unit reads as deliberate, not vague.

## Why

V2 production exposed the tension. Hard Rule #24's ≤15% cap conflicts with `templates/product-demo/RENDER-GUIDE.md` § "Annotate-mode spotlight" + `video-scriptwriting/SKILL.md` § "Panel content authoring," both of which require the rect to "cover the WHOLE conceptual unit the panel pitches — not just the opening sentence." For ap3 (Bottom Line verdict), the conceptual unit is header + 4-line paragraph ≈ 19% tall. Either rule could be violated:

- Honor the 15% cap → spotlight only the header → 4 lines of verdict paragraph fall into the dim → "the panel pitches the verdict, but the spotlight points at the title only" reads as broken.
- Honor the "whole conceptual unit" → spotlight reaches 19% → violates the 15% cap.

V2's earlier resolution honored the cap; user feedback flagged the result as wrong ("zoom in only on the title which is a bit stupid"). The three-tier band resolves the conflict by recognizing that the 15% cap was a target for *tight phrase-level* highlights; conceptual-unit highlights (header + paragraph) naturally exceed it, and that's fine up to 25%.

User feedback at the trigger:

> "There's an issue with that rule because if you look at AP2 and AP3 they zoom in only on the title which is a bit stupid — you should zoom in on the body text as well. So maybe for some we need to zoom in on the whole chunk."

## How to apply (enforcement)

**At Phase 5 (drafting):** for each annotate, classify the VO target into the three tiers:

1. *Specific phrase?* (e.g., "Composite at five-point-six" → just the Total row) → tier 1, ≤15%.
2. *Conceptual unit?* (e.g., "Bottom Line verdict" → header + 1 paragraph) → tier 2, 15–25%, cover the whole unit.
3. *Section / multi-paragraph?* (e.g., "the trajectory pattern across the year" → header + paragraph + bullet list) → tier 3, split into sub-annotates with shared panel.

**Measurement.** `tools/measure_highlight.py`'s auto-snap output can be used directly for tier 1 (snap caps naturally at the row/phrase boundary) and tier 2 (the conceptual unit is what the snap finds). For tier 3 the snap output will be >25% and signals a split is needed — author the sub-annotates manually, measure each separately.

**Panel-body coupling check.** When authoring panel body for a tier-2 (wider spotlight) annotate, keep body short (≤15 words) so viewer attention can split between panel and spotlight. Long bodies belong with tier-1 tight spotlights where the panel does most of the work.

**At Phase 6a (polish):** verify each annotate's highlight against its tier classification + the panel-body coupling. Violations: re-tier (likely tighten body OR widen spotlight) and re-measure.

## Notes

- The 15% number didn't go away — it's still the target for tier 1. Tier 2 relaxes the cap; tier 3 splits.
- Tier 3 is what V2's score-panel cluster already does (4 sub-annotates for the 5-pillar section, shared panel ap1). This rule formalizes the pattern as the resolution for any "too tall to spotlight cleanly" case.
- The "conceptual unit" definition is the same as in `video-scriptwriting/SKILL.md` § "Panel content authoring" — what the panel pitches the value of. The header + the paragraph that elaborates it. Not the whole section if the section has multiple paragraphs.
- 25% is the operational threshold; the precise number is empirical. If preview reveals a 22% spotlight reading fine but a 28% spotlight reading as "too much frame lit up," the threshold can be tightened in a follow-up ADR.
- Companion to Hard Rule #17 (vertical centering — the spotlight's center sits at composition vertical center regardless of height), Hard Rule #24 (sub-annotate split, now the resolution path for tier 3), and Hard Rule #25 (panel-hold minimum, ties into the panel-body coupling).
