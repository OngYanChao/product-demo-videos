# Phase 5 rules — Write the script (product-demo)

Read these when invoking Phase 5 (script-writing) for V<N> / I<N>. News-pipeline has no Phase 5 (no separate script-writing step). Cross-load `meta.md`.

For voice composition / banned words / "show on screen, interpret in VO" / vault-stat integration / panel content authoring — consult the sibling `video-scriptwriting` skill (loaded via the orchestrator). This file covers the workflow-level rules.

---

## Hard Rule #6 — Cut whole beats, never word-by-word within a beat — and never telegraph when you have room.

Phase-aware: all editorial decisions (rhythm balance, beat cuts) defer to Phase 6a where actual post-render runtime is known. Phase 5 stays mechanically punchy.

(a) **Phase 5 — write all beats at punchy default.** Don't pre-cut beats; don't try to balance rhythm. At Phase 5 you have target seconds from the beat sheet but not actual post-zoom segment timings (Phase 5.5 zoom + Phase 6 render reveal those). Writing all beats fragment-heavy is conservative — short data-callout lines fit any final timing. Editorial judgment (what to keep, what to expand, what to cut) defers to Phase 6a where you can see actual numbers, not guesses.

(b) **Phase 6a — rhythm pass (when runtime fits).** Once Phase 6 is rendered, the actual breathing room is visible (zoom inserts, silent-scrolldown beats, and intentional silences typically leave 20–40% of the speakable window unspoken). Now expand the connective and interpretive lines from fragments to full sentences. Earned fragments stay (data callouts, hero shots). Project-local heuristic for use_case style: ~40% data-fragment + ~35% short-sentence + ~25% full-sentence across the polished draft.

(c) **Phase 6a — beat cut (when total runtime overflows).** When the rendered preview reveals that the spoken VO can't fit even at punchy rhythm, drop an entire beat at full rhythm rather than clip every line for fit. The choice is whole-beat-or-nothing, never word-by-word abbreviation. After cutting, also touch LTs and panels.

(d) **Phase 6a backup loop — re-open Phase 1.** When an individual beat's polished VO would overflow its zoom hold but global runtime still fits, extend the beat's target seconds in MASTER.md by `overflow_seconds + 0.5s buffer`, update the matching zoom directive's `duration` in `V<N>_zooms.json`, re-run Phase 5.5 → 6 → 6a. Backup loop fires at most once per beat; second trigger = escalate.

Logged: `decisions/2026-05-20-sentence-rhythm-with-budget-headroom.md`, `decisions/2026-05-20-phase-6a-polish-pass.md`.

---

## Hard Rule #7 — Every on-screen claim in the script must cite a frame.

Hallucination check is enforced at Phase 5, grounded in the Phase 4 frame audit. No exceptions — wrong stats in published video are credibility-destroying.

Each cited stat in the VO body has a corresponding frame in `frames_used:` in script frontmatter, with a brief note tying claim to visible content in that frame.

---

## Zoom directive duration sizing — read the beat sheet, not the punchy draft

The zoom directive's `duration` field equals the beat sheet target seconds — NOT the punchy VO's actual speech time at Phase 5. This is the load-bearing convention. The zoom hold is sized for the polished VO from the start, not the punchy under-fill. When Phase 5.5 produces the zoomed file, the hold has built-in headroom for Phase 6a to expand the VO into.

If you size `duration` from the punchy VO instead, the hold is too short and Phase 6a's rhythm expansion triggers the Phase 1 backup loop. Avoid by reading from the beat sheet's target seconds, not the punchy draft's spoken length.
