# 2026-05-20 — Phase 6a Auto Polish Pass

**Status:** active
**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (new Phase 6a section; Hard Rule #6 reframed as phase-aware), `.claude/skills/video-scriptwriting/SKILL.md` (Hard Constraints sentence-rhythm line now phase-aware), `.claude/skills/parallax-video/SKILL.md` (new dispatch row "polish V<N>" / "tweak V<N>"; "write V<N>" + "render V<N> preview" rows updated to auto-chain into Phase 6a), `CLAUDE.md` (daily workflow loop extended from 11 to 12 phases; dispatch table row added)

## Decision

Introduce **Phase 6a** between Phase 6 (Preview render) and Phase 7 (Iterate). Phase 6a is an auto-triggered polish pass that runs after every Phase 5 (script change) AND every Phase 6 (preview re-render). User does not invoke; the orchestrator chains it automatically. Explicit trigger phrases (*"polish V<N>"*, *"tweak V<N>"*) exist for ad-hoc re-runs but aren't required.

Phase 6a performs seven steps in order — both editorial decisions (rhythm balance AND beat cuts) live here, because both depend on knowing actual rendered runtime:

1. **Sync check** — every `lower_thirds[].in/out_recording_t` and `annotations[].in/out_recording_t` in the script frontmatter matches the actual seg_annotate_NN / seg_src_NN timings from `tools/zoom.py`'s "segment timing in zoomed file" output (Hard Rule #12).
2. **Beat coverage check** — every spoken VO beat maps to a panel/LT/zoom hold; every panel/LT has a corresponding spoken beat. Catches orphans from cuts/reorderings.
3. **Runtime check (decides between step 4 and step 5)** — measure spoken VO budget (words ÷ 150 wpm) against the speakable window (composition runtime − title − outro − intentional silences − scroll segments). If budget ≤ window → step 4. If budget > window → step 5 (skip step 4 this pass).
4. **Rhythm pass (runtime fits)** — count fragments vs full sentences. If fragments ≥ 60% of total, restore full sentences in connective/interpretive beats. Project-local mix target for use_case style: ~40% data-fragment + ~35% short-sentence + ~25% full-sentence. Earned fragments stay (data callouts, hero shots).
5. **Beat cut (runtime overflows)** — drop a whole beat at full rhythm. Selection: lowest-priority beat per MASTER's `Primary value angles` for the video. Re-author surrounding stage directions to bridge the cut. The cut creates headroom; the next auto-Phase-6a run uses it for rhythm expansion on the remaining beats.
6. **LT + panel update (conditional)** — touch LTs and panels only when Phase 5 cut beats, reordered points, OR step 5 just cut a beat. Otherwise LTs and panels are untouched (locked-format — eyebrow + headline + locked vocabulary — don't drift with rhythm changes).
7. **Auto-re-render preview** if any edits applied. If all checks pass clean, report "Phase 6a clean" and stop. Idempotent — should converge within 1–2 passes.

Hard Rule #6 reframed: **all editorial decisions defer to Phase 6a where actual runtime is known. Phase 5 stays mechanically punchy.**
- (a) **Phase 5 — write all beats at punchy default.** No pre-cuts, no rhythm balancing. Conservative — fragment-heavy lines fit any final timing because actual post-zoom timing isn't known yet at write-time.
- (b) **Phase 6a — rhythm pass (when global runtime fits AND per-beat polished VO fits zoom hold).** Once preview reveals actual breathing room, expand connectives/interpretives to full sentences.
- (c) **Phase 6a — beat cut (when total runtime overflows).** Drop a whole beat at full rhythm rather than telegraph-clip across all beats.
- (d) **Phase 6a backup loop — re-open Phase 1 (per-beat overflow, global runtime still fits).** Auto-extend the beat's target seconds in MASTER.md, update zoom directive `duration`, re-cascade Phase 5.5 → 6 → 6a. Backup loop fires AT MOST once per beat; second trigger escalates.

Calibration rules that make the workflow self-contained (so the backup loop is the *corrective*, not the *default*):

- **Phase 1**: beat sheet target seconds calibrated for intended-rhythm (polished) VO, not punchy. The Phase 5 punchy draft under-fills by design; that under-fill is Phase 6a's rhythm-expansion headroom.
- **Phase 5**: zoom directive `duration` = beat sheet target seconds, NOT the punchy VO's actual speech time. Hold is sized for polished VO from the start.

When both calibrations are correct on the first pass, Phase 6a step 4 fits without triggering 5b. When either is off, the backup loop (5b) auto-corrects on the next iteration.

## Why

User feedback today (two related observations that drove the same refactor):

1. *"i want to make it such that the script is generated with the short punchy lines first, like how it was generated just now before i said to add more full sentences to it. then, after the preview is done and final runtime is known, add another workflow to tweak the script again to add full sentences to add variation between full sentences and punchy lines."*
2. *"since we are cutting beats based off the final runtime of the preview, shouldnt we move hard rule 6 part a to phase 6a as well"* — pushed the same logic to its conclusion: **both** rhythm balance AND beat cuts depend on knowing actual runtime, so both belong at Phase 6a (the polish pass), not at Phase 5 (the punchy draft).

The earlier (this morning's) ADR `2026-05-20-sentence-rhythm-with-budget-headroom.md` codified the *rhythm-mix discovery* but framed it as a write-time rule. That framing has a hole: at Phase 5, the writer doesn't yet know the post-zoom segment timings — zoom inserts can be ~30–60s longer than the scrubbed timeline depending on dwell:y beats + `--clean-source-ranges` cleaning, silent-scrolldown beats can be 5–10s, and intentional silences are only knowable after the preview is rendered. Writing "balanced rhythm" at Phase 5 against unknown numbers is guessing. Writing "punchy by default" at Phase 5 is conservative — short lines fit any final timing — and the rhythm expansion can happen confidently at Phase 6a once the preview is rendered.

Beyond rhythm, the user wants the polish pass to also handle the two other classes of post-render drift: (1) timestamp re-sync against the actual zoomed file (already covered by Hard Rule #12 but easy to forget manually), and (2) beat coverage when Phase 5 has cut or reordered beats (a panel for a cut beat is orphaned; a new beat without a panel is unilluminated). Folding all three checks into one auto-triggered pass + having it always run = automation pipeline goal: human intervention only for review of preview + script.

## Notes

- The trigger contract is auto-chain — "write V<N>" auto-chains into "polish V<N>"; "render V<N> preview" auto-chains into "polish V<N>". The orchestrator doesn't pause for user invocation between these phases.
- Convergence rule: Phase 6a is idempotent. The second auto-Phase-6a run after an auto-re-render should be clean (no edits). If it keeps making edits across multiple iterations, that's a bug — a check is misidentifying acceptable patterns as violations. Escalate.
- LT + panel conditionality keeps Phase 6a from over-rewriting. LTs and panels have locked formats (eyebrow + headline + locked source/badge vocabulary) — they don't drift with rhythm changes. Only Phase 5's *structural* changes (cut beats, reordered points) warrant touching LTs/panels at Phase 6a.
- The user's explicit goal: *"i want this pipeline to be automated as much as possible with only human intervention to review the preview and script."* Phase 6a is the load-bearing automation step — the human review point is after Phase 6a converges, not after every individual edit.
- V1.2 retrospective: today's morning session went Phase 5 (punchy draft) → Phase 6 (preview) → Phase 6a-equivalent (rhythm expansion) manually. The pattern proved useful; codifying it as an automatic phase prevents future drafts from skipping the polish step.
- Cross-references: Hard Rule #6 (a/b/c), Hard Rule #12 (re-derive timings), Hard Rule #19 (clean source segments — affects timing that Phase 6a re-syncs against), the earlier ADR `2026-05-20-sentence-rhythm-with-budget-headroom.md` (rhythm-mix discovery — still active, now refined by phase-awareness).
