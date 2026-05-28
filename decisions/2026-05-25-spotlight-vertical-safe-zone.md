# 2026-05-25 — Annotate spotlight vertical centering relaxes to a safe-zone band

**Status:** active
**Refines:** `decisions/2026-05-19-annotate-vertical-centering.md` (replaces the strict y=44.8%/50% center-point requirement with a safe-zone band).
**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #17 reworded), `.claude/skills/parallax-video/SKILL.md` (zoom dispatch row reworded).

## Decision

Annotate spotlights must land within the **composition's vertical safe zone**: comp y=30% to y=70% (a 40%-tall band centered on comp middle). The previous strict "land at comp vertical center (y=50%)" requirement is retired.

For a target to satisfy the rule, its comp-space y position (computed via the zoom_region transform from `highlight_region_pct` y + h/2) must fall within [30%, 70%]. If the target's natural position in the source falls within this band when transformed, the spotlight is acceptable as-is — no scrolling, no source_t adjustment, no zoom_region y_offset gymnastics. Only when the target falls outside the band does the author choose between:

1. **Choose a different source_t** where the page has scrolled enough to bring the target into the band, OR
2. **Widen / shift the zoom_region** to bring the comp position into the band — provided the zoom_region's aspect/clamp constraints still hold (per `tools/zoom.py`'s validation), OR
3. **Split into sub-annotates** if multiple targets in the same cluster span more than the safe zone's vertical reach.

For multi-target clusters (Hard Rule #24 sub-annotate split — multiple sub-spotlights firing in sequence on the same beat), all targets in the cluster ideally share **one source_t + one zoom_region** so the camera stays held across the cluster and only the spotlight moves. The viewer sees a static frame with the highlight cycling between rows; no scroll motion, no camera shift, no jitter.

## Why

The 2026-05-19 strict-centering rule forced mid-scroll source_t selection for multi-row clusters. V2's score-panel cluster (z1a Composite + z1b Quality + z1c Value + z1d Momentum) was authored with four different source_t values (32.10, 32.26, 32.40, 32.62), each picked so its target row was at the exact comp y=44.8% during the page's active scroll. The result on preview: the camera holds, but the page underneath visibly scrolls between every sub-annotate — Total ticks at scroll position A, then page jumps to position B for Quality, then C for Value, then D for Momentum. Each "page jump" is the source between sub-annotates playing through (mpdecimate-cleaned but still visible).

User feedback at the trigger:

> "If you look at z1a to z1d they are all… it feels a bit jittery because they are also close together in [the table] which scrolls up a bit and then zooms in again. I think it's quite unnecessary. Maybe we have a limit — if the content is a certain number of pixels away from the top and from the bottom of the screen then just zoom in. And if it's in that range then we have to scroll to make sure it is in the middle of the page."

The cleaner interpretation: strict centering was over-constrained. The viewer doesn't need every spotlight to land at exactly comp y=50%; "comfortably in the middle band, not crammed against an edge" is what reads as professional. The 30-70% safe-zone gives a 40-percentage-point band of acceptable positions. For a cluster of 4 rows in a table (spanning ~15% of source height), they all fit in the safe zone with a single zoom_region + single source_t — exactly the static-frame multi-target pattern the original rule's "next annotate fires when the next target is centered" was unnecessarily blocking.

## How to apply (enforcement)

**For single annotates.** Compute the target's comp y position from the zoom_region transform: `comp_y = (highlight_y_center − zoom_region.y_offset) / zoom_region.height × 100`. If `30 ≤ comp_y ≤ 70`, the spotlight is acceptable. Otherwise, adjust.

**For sub-annotate clusters.** Pick one source_t + one zoom_region such that ALL sub-annotates' comp y positions fall in [30, 70]. Algebra: for the cluster spanning source y from `y_min` to `y_max`, the zoom_region must satisfy:

```
y_offset ≤ y_min − 0.3 × height
y_offset ≥ y_max − 0.7 × height
```

Both inequalities must hold, which requires `height ≥ (y_max − y_min) / 0.4`. If the cluster's vertical span exceeds 40% of source, no single zoom_region centers it — split into multiple clusters (different source_t, different scroll positions) per option 3.

**Cursor-clear check (Hard Rule #16) still applies.** The single-camera multi-target pattern shifts the cursor-clear region's y bounds to the union of all sub-annotates' highlight regions; if the cursor sits anywhere in that union, the cluster fires under the fallback `base_t`. Authors should pick source_t where the cursor isn't parked across the cluster.

## Notes

- **The safe zone is comp-space, not source-space.** A target at source y=56.8% might land at comp y=35% (in the safe zone) with one zoom_region and comp y=75% (outside) with another. The author has two levers (source_t + zoom_region) and only one constraint (the final comp y).
- **30-70 is a default; 25-75 is acceptable.** The numbers are empirical, not derived. If a preview shows a spotlight at comp y=28% reading "fine," it's fine — the rule's threshold can be relaxed per-video as needed. Beyond 25 / 75 starts to feel edge-crammed.
- **The 16:10 vs 16:9 source distinction from the 2026-05-19 rule disappears.** That distinction was about where source y=50% maps to in a 16:9 comp (source y=44.8% in a 16:10 source equals comp y=50% in a 16:9 comp after letterboxing). With the safe-zone band approach, the comp y is computed directly from zoom_region transform and the source aspect doesn't enter the rule.
- **Companion to** Hard Rule #16 (cursor-clear), Hard Rule #18 (overlay ease), Hard Rule #24 (multi-VO-target split + shared panel), Hard Rule #25 (panel-hold minimum). The shift from "exact center" to "safe zone" is a refinement, not a replacement — the spotlight visual contract (soft-edged ellipse over dim, panel + numbered badge to the right) is unchanged.
