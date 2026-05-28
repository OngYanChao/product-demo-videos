# 2026-05-20 — Sentence-Rhythm Rule Made Explicit for Budget-Loose Drafts

**Status:** active
**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #6 expanded to two cases — budget tight + budget loose), `.claude/skills/video-scriptwriting/SKILL.md` (Hard Constraints line on sentence rhythm strengthened with explicit fragment-vs-sentence mix heuristic)

## Decision

Hard Rule #6 now reads as a two-case rule, not one. Same principle ("match rhythm to budget"), applied to both directions:

- **(a) Budget tight** — drop a whole beat at full rhythm rather than clip word-by-word within beats. Same as the original rule.
- **(b) Budget loose** — use the breathing room with natural sentence rhythm; don't default-clip into all-fragments for stylistic punch. Earned fragments (data callouts) interleave with full interpretive sentences (connective + analytic VO). Project-local mix for use_case-style: ~40% data-fragment + ~35% short-sentence + ~25% full-sentence.

The two clauses are about the same underlying principle: telegraph rhythm is a *symptom*, not a *style*. It appears when the writer abbreviates against pressure (case a) or against reflex (case b). The rule rejects both.

## Why

V1.2's first VO body draft (this morning, 2026-05-20) used fragments for ~70% of beats: *"Brief lands. Under a minute. Every claim sourced."* / *"Plain English in. Parallax pulls..."* / *"Hold — case is intact. Twenty-one percent upside, top-decile quality."* User caught it: *"why are all the sentences so short and 'impact' like, instead of having a variation of full sentences and 'impact' sentences. is it something in the scriptwriting skill that defines this style? or is it we are trying to cram too many points in for the time limit we have"* — and noted the rule that should have caught it: *"didnt we have something in the scripwriting skill that says to cut beats out instead of making everything punchy if there is not enough time? was that rule applicable here?"*

The honest answer: the rule's *letter* (Hard Rule #6 original) was about budget pressure, and budget wasn't tight here (148 words / 100s composition = 30+ seconds of headroom). So "cut a beat" didn't trigger. But the rule's *spirit* — that natural pacing beats telegraph style — clearly applied. The writer (me) defaulted to financial-newsroom punch because nothing in the codified rules forced full sentences when the budget allowed them.

The fix is to make the second case explicit: when budget is loose, *use the room*. The 20–40% breathing room that zoom inserts + silent-scrolldown beats + intentional silences create is **for full-sentence interpretive VO**, not for cramming more fragments. Telegraph rhythm in a loose-budget draft is a stylistic reflex; the rule now names it as a violation.

## Notes

- The fragment/sentence mix heuristic (~40/35/25) is calibrated against the V1.2 second-cut rewrite. Other styles may calibrate differently:
  - **use_case** (V1–V16): ~40% data-fragment + ~35% short + ~25% full-sentence — the mix above.
  - **instructional** (I1–I4): heavier on short directive sentences ("Click the brand-prompt") with fewer interpretive full sentences. Fragments still earn punch on UI-state callouts.
  - **intel_brief** (paused): TBD when reactivated — will likely lean more full-sentence (anchor-tone delivery).
- Detection rule: count sentences across the spoken VO body. If fragments (≤3 words OR clearly missing subject/verb) > 60%, restore full sentences in connective beats.
- TTS-specific: voice synthesizers handle natural-rhythm prose better than telegraph rhythm. Fragments work for hero shots but stress the model's prosody when chained. Full sentences give the synthesizer a clearer breath structure.
- The V1.2 second-cut rewrite is the canonical example of applying this rule: kept fragments on data callouts ("Composite at five. Quality and Tactical, ten. Value, three."), restored full sentences on connective beats ("You type the question in plain English, and Parallax pulls every input — scores, peers, macro, news, methodology — through the same factor framework.") — net ~165 spoken words instead of the first cut's ~148, still ~30s of breathing room across the 100s composition.
- Companion to existing constraint on `video-scriptwriting/SKILL.md` line 53: "Vary sentence rhythm." That line is now explicit about the mix, not just the principle.
