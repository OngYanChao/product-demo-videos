# 2026-05-25 — Annotate panel-hold minimum sized to panel copy reading time

**Status:** active
**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (new Hard Rule #25), `.claude/skills/video-scriptwriting/SKILL.md` (§ Panel content authoring — cross-ref), `.claude/skills/parallax-video/SKILL.md` (zoom dispatch row — cross-ref).

## Decision

Every annotate-mode panel must be on screen for at least long enough that the viewer can read its copy. The minimum panel-hold duration is driven by the panel's **body word count**:

```
min_hold = max(3.0s, body_word_count / 5.0 + 2.0s)
```

Where:
- `body_word_count` = words in the panel's `body` field. **`eyebrow`, `headline`, `badge`, and `source` are excluded** — eyebrow + headline are glance-readable (brand-locked caps + hook line; viewer parses them in ~2s regardless of word count), and badge/source are labels.
- `5.0` = reading speed in words-per-second (300 wpm — typical fluent silent reading speed). The pacing target is *viewer-driven* — if a particular segment doesn't engage the viewer they can scroll past, and if it does engage they can pause to read in depth. The floor exists to prevent dead-space hang, not to guarantee full comprehension at first pass.
- `2.0s` = sum of ease-in + ease-out (1.0s each, per Hard Rule #18).
- `3.0s` floor = absolute minimum so even a body-less panel (eyebrow + headline only — bare callout) has ≥1s of fully-visible readable time.

For sub-annotates **sharing a single panel** (per Hard Rule #24's shared-panel allowance), the panel-hold is the **sum** of all constituent sub-annotate `duration` values. The minimum applies to that sum, not to each sub-annotate.

Worked examples:

| Panel body content | Body words | `min_hold` |
|---|---|---|
| No body — eyebrow + headline only (bare callout) | 0 | **3.0s** (floor) |
| Short body (~10 words) | 10 | **4.0s** |
| Medium body (~25 words) | 25 | **7.0s** |
| Verbose body (~40 words — V2 ap2 size) | 40 | **10.0s** |

## Why

V2's score-panel sub-annotates (4 sub-annotates × 3.0s each, each paired with a separate ~40-word-body panel) revealed the failure mode. Per Hard Rule #18 the panel ease-in + ease-out consume 2.0s of every hold, leaving 1.0s of fully-visible readable window for a 3.0s sub-annotate. A 40-word body at 300 wpm fluent-skim speed needs ~8s. The viewer gets ~12% of the time they need. Effectively the panel exists but cannot be skimmed, let alone paused-and-read.

The constraint isn't a new design opinion — it's a math floor that the existing rules (Hard Rule #18 ease curve, Hard Rule #24 sub-annotate split) implicitly assumed but never enforced. Without the floor, Phase 5 authoring can produce sub-annotate plans that look correct on paper (one sub-annotate per VO-named item, panels per sub-annotate) but render as unreadable.

User feedback at the trigger:

> "If we have these four small very short segments, how will we have the panels come in during the preview? Won't it be too short of a time for the viewer to read what's on the panels?"

Encoding the floor as a numbered Hard Rule makes the constraint visible at Phase 5 (drafting) and at Phase 6a (post-preview verification), and forces an explicit authoring choice between:

1. **Tighter copy per panel** — drop body, keep eyebrow + headline only. Each sub-annotate's panel reads in 4–5s, fits a 6–7s hold.
2. **Shared panel across sub-annotates** (Hard Rule #24's shared-panel allowance) — write one panel about the conceptual unit (e.g., "the score panel as defensible quantitative spine"), keep numbered badges per sub-annotate, the panel stays pinned for the entire cluster's hold. Total cluster hold = sum of sub-annotate durations, which scales naturally with panel word count.
3. **Longer per-sub-annotate holds** — extend each sub-annotate `duration` past `min_hold`. Trades off video pacing; the beat sheet's beat target must accommodate the inflation.

## How to apply (enforcement)

**Phase 5 (drafting zoom directives + panel content).** After authoring each panel's content + the paired zoom directive's `duration`, compute `min_hold` from the panel's word count and verify `duration >= min_hold`. If a sub-annotate cluster shares a panel, sum the cluster's durations and check against the shared panel's `min_hold`. If violated, choose one of the three resolution paths above.

**Phase 6a (polish, post-preview).** Re-check after the preview is rendered — preview reveals actual rendered hold times (zoom.py's `seg_annotate_NN` and `seg_pause_NN` segments may shift due to cursor-clear fallback, `--clean-source-ranges` mpdecimate, etc.). If a panel violates `min_hold` in the rendered timeline, trigger the backup loop into Phase 1 (extend the beat's target seconds in MASTER.md) or rewrite the panel copy shorter.

**Default panel format for sub-annotate clusters.** When a `dwell:y` beat is split into sub-annotates per Hard Rule #24, the default authoring choice is the **shared panel** (Mechanism #2 above) — one panel pitching the cluster's conceptual unit, numbered badges per sub-annotate. Per-sub-annotate distinct panels are allowed but rare (e.g., if each sub-annotate names a genuinely distinct capability angle that doesn't reduce to a single cluster headline).

## Notes

- 300 wpm = 5.0 wps is typical fluent silent reading speed for adults. The pacing model is viewer-driven: the panel sits long enough to register and skim, not long enough to fully comprehend on first pass. A viewer interested in the segment can pause to read in depth; a viewer who isn't interested doesn't get stuck waiting. This trades comprehension-on-first-pass for video momentum. If preview reveals panels feeling rushed AND the segments are load-bearing for the watch-through narrative (not just pause-bait), drop to 240 wpm (`min_hold = max(3.0, body_word_count / 4.0 + 2.0)`) in a follow-up ADR.
- The rule counts **only body words** because eyebrow + headline are designed for glance-reading: eyebrow is ALL-CAPS brand-locked vocabulary (e.g., "COMPOSITE SCORE · WHAT IT GIVES YOU"), and headline is a 1-sentence hook. Both parse in ~2s combined regardless of word count. The body is the linear-reading paragraph that drives the floor. `badge` and `source` are even shorter glance-readable labels.
- The rule does NOT mandate `duration = min_hold` — it sets the **floor**. Authors can hold longer for emphasis or to absorb planned silence. `min_hold` is a violation threshold, not a target.
- Companion to Hard Rule #18 (ease curve matches camera, sets the 2.0s ease overhead) and Hard Rule #24 (sub-annotate split + shared-panel allowance). Without #18's 1.0s ease default, the `+2.0s` constant in the formula would change.
