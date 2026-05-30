---
name: video-production-workflow
description: Production workflow methodology for any video project that combines a recording (screen capture, b-roll, or live footage) with a voiceover and on-screen graphics — product demos, tutorials, walkthroughs, marketing explainers, anchor briefs. Use whenever you are sequencing the phases of video production, deciding what gets done in what order, or resolving timing conflicts between a recording and a script. Solves the "ouroboros" problem where a script's runtime is dictated by recording length while the recording's content was paced for an imagined script. Phases covered: beat sheet → recording → scrub → frame audit → script → zoom → render. (Zoom runs after the script, not during scrub, so zoom regions can be driven by what the VO names.) This skill is methodology only — it does not ship code or project-specific orchestrators. Pair it with a craft skill for the script-writing phase (e.g., `video-scriptwriting`) and a project-local orchestrator that knows how to invoke the project's tools.
---

# Video Production Workflow

A methodology for sequencing video production so the recording, the script, and the on-screen graphics align without forcing late-stage compromises. Project-agnostic — applies to any pipeline where a recording carries the visual track and a separate voiceover carries the audio track.

## The problem this skill solves

Video projects with separate visual and audio tracks fall into a circular dependency:

- The script must fit the recording's runtime, or the VO will overrun or run short.
- The recording's pacing was designed against an *imagined* script, so its dead-loading segments and content-reveal segments aren't actually calibrated to anything.
- When the two are reconciled at the end, either the script is forced to drop crucial beats to fit, or the recording is awkwardly stretched/compressed to cover beats it wasn't built for.

The fix: **the beat sheet is upstream of both.** Beats with target seconds get locked first. The recording is conformed to those targets. The script is written to those targets. Both downstream artifacts converge on the same canonical timeline instead of negotiating with each other.

## The phases

Each phase has a defined input, output, and hand-off contract. Don't skip ahead — a phase that runs without its input can't produce its output reliably.

### Phase 1 — Lock the beat sheet (with target seconds)

**Input:** the project's plan / brief / outline. Whatever document defines what this video is supposed to communicate.

**Output:** a beat sheet — ordered list of beats, each with a target seconds count, summing to the locked total runtime.

**Format:**

```
Beat sheet (target seconds, recording portion)
- 0:00–0:05  Title card                              (5s)
- 0:05–0:16  Open: question + system fans out        (11s)  dwell: n
- 0:16–0:28  Why this isn't trivial                  (12s)  dwell: n
- 0:28–0:38  Vault stat / framing                    (10s)  dwell: n
- 0:38–0:54  Score panel + transition                (16s)  dwell: y (panel settles at 0:48)
- 0:54–1:08  Trajectory + bottom line                (14s)  dwell: y (final brief settled)
- 1:08–1:16  Outro                                   (8s)
```

**`dwell: y`** marks beats where the visual settles into a content-rich still that the VO can dwell on for longer than the underlying motion took to reveal. This is the asymmetry that lets a 6-second factor-table reveal carry 14 seconds of VO commentary.

**Total = locked target runtime — but two interpretations are valid:**

- **Strict mode (default):** beat-sheet target seconds are the canonical timeline. The recording is scrubbed (Phase 3) to per-beat targets net of planned zoom inserts, and zoomed (Phase 5.5) to fill the dwell:y windows. Downstream artifacts reference the beat sheet's beat windows directly.
- **Pragmatic mode:** beat-sheet target seconds are *rough guidance* for what to record and how long each beat should last. The recording will drift from those targets in practice. Phase 3 scrub removes dead time, Phase 5.5 zoom (sized by beat sheet, regions chosen from the script) realizes the final beat windows. **The zoomed recording is the canonical downstream timeline.** Script + LT timing reference the zoomed recording's actual windows, not the beat sheet's targets.

Which mode you operate in depends on your tooling and discipline. The portable rule that survives both is: **downstream artifacts must reference whatever the canonical timeline turns out to be at the end of Phase 5.5 — not whatever was on paper before recording began.** If you re-run zoom (with different durations, regions, or pre_zoom_hold values) or re-scrub at a different threshold, re-derive LT/script timings from the new zoomed recording. Never let LTs or script timing reference a beat sheet that the recording no longer matches. See Hard Rule #12.

If a beat genuinely can't be cut and won't fit the budget, escalate before recording — don't silently compress the script later.

**Beat sheet targets are calibrated for the intended-rhythm (polished) VO, not the Phase 5 punchy draft.** When you lock a beat's target seconds, you're allocating room for the polished VO that Phase 6a will eventually produce — full sentences for connectives + interpretation, fragments only where data is the punch. The Phase 5 punchy draft under-fills this allocation by design; that under-fill is the source of headroom Phase 6a uses for rhythm expansion. If you calibrate the beat sheet to the punchy length instead, Phase 6a has no room to expand and the polished version overflows — triggering the backup loop (re-open Phase 1, extend the beat, re-cascade Phase 5.5 → 6 → 6a). Avoid the loop by calibrating once, correctly, at Phase 1.

### Phase 2 — Record (or source) the visual track

**Input:** the locked beat sheet from Phase 1.

**Output:** a raw recording where each beat's content is present. Per-beat duration in the raw recording can be longer than the target (Phase 3 scrub compresses; Phase 5.5 zoom adds back planned dwell time). It cannot be meaningfully shorter for non-dwell beats — there is no extension mechanism for those once dead time is gone. Slowdown is banned (Hard Rule #13).

**Hand-off contract:** the recording must clearly contain the *content* each beat references, and each `dwell: y` beat must have a settled visual that Phase 5.5 zoom can dwell on. If beat 4 says "score panel visible," the score panel must actually appear. If beat 5 is `dwell: y`, the visual must settle for long enough that Phase 5.5 has a still to zoom into. Frame extraction in Phase 4 audits the first half of that; the second half is verified at Phase 5.5.

### Phase 3 — Conform the recording (scrub only; zoom is deferred to Phase 5.5)

**Input:** raw recording + locked beat sheet.

**Output:** scrubbed recording where each beat's runtime is either at-target or within tolerance for the dwell-aware rules below. Zoom inserts are NOT applied here.

This is the phase where most projects lose alignment, because the temptation is to skip it and let the script absorb whatever the recording happens to be. Don't.

**Why zoom is not in this phase.** Zoom region is "the bounding box of what the VO names" — and the VO doesn't exist yet. Applying zoom here forces the zoom region to be guessed from the recording alone, which the script later has to bend around (or the script names something different and the zoom highlights the wrong thing). Phase 3 does scrub-only; Phase 5.5 applies zoom after the script is locked and can drive region selection from VO content.

**Conformation decision tree per beat:**

| If the beat's raw runtime is… | Apply | Notes |
|---|---|---|
| **Within ±10% of target** | Pass through unchanged | Within tolerance. |
| **Too long, mostly dead loading** | Scrub (compress freezes via tapered cut + speedup) | Default tooling: detect freezes, anchor front+back at speed-up, cut the middle for long stalls. |
| **Too long, content motion** | Speed up the segment uniformly (max 1.5–2×) | Content motion looks fine at 1.5–2×; faster reads as comedic. |
| **Too short, beat is `dwell: y`** | Defer to Phase 5.5 zoom | A short dwell:y beat is *not* a Phase 3 failure — Phase 5.5 zoom is the canonical extension tool, and it has to wait for the script. Phase 3 just leaves the beat at its scrubbed length. |
| **Too short, anything else** | Re-record that section | Cheaper than shipping a misaligned video. Escalate to user. See Hard Rule #13 — slowdown is not an option. |

**The dwelling principle is doing heavy lifting in this table.** Most "the recording is too short" anxiety dissolves once you recognize that content-rich settled visuals (factor tables, brief paragraphs, score panels, dashboards, code blocks) absorb 2–3× their reveal motion in VO commentary. The recording doesn't have to *do something new* every VO second. Phase 5.5 zoom is what realizes that dwell — but the *option* exists already at Phase 3 because the beat sheet marked the beat dwell:y.

**Output sanity check:** sum of scrubbed beat durations + planned zoom-insert seconds (from the beat sheet's dwell:y windows) should equal the beat sheet's recording total ±0.5s. If not, the recording is unfit at Phase 3 — adjust scrub or re-record. Don't proceed to script writing with a recording that's 4 seconds off net of planned zooms; those 4 seconds will reappear as VO overrun later.

### Phase 4 — Audit visual content (frame extraction)

**Input:** scrubbed recording (Phase 3 output, pre-zoom).

**Output:** evenly-spaced frames + an index mapping frame number to timestamp. This is the grounding artifact for the script-writing phase's hallucination check — every on-screen claim in the script must trace to one of these frames.

Default cadence: one frame every 2 seconds, downscaled. Strategic frames cited in the script's `frames_used:` audit trail are the durable record; the JPGs themselves are scratch and get deleted after the final render is approved. Frames are extracted *before* zoom is applied because they're a content audit — zoom doesn't add content, just emphasis.

### Phase 5 — Write the script (punchy draft)

**Input:** locked beat sheet + scrubbed recording + frame audit.

**Output:** voiceover script with stage directions, plus zoom directives (one per `dwell: y` beat) declaring what the VO names in that beat — `source_t`, region (placeholder until Phase 5.5 measures), `duration` = the beat's locked seconds, mode (`hold` / `follow` / `annotate`).

**This phase produces a "punchy draft" — fragment-heavy, conservative on rhythm.** At Phase 5 you have the beat sheet's *target* seconds but not the post-zoom *actual* segment timings (Phase 5.5 zoom + Phase 6 render reveal those). Writing punchy is the safe move — short data-callout lines fit any final timing. The rhythm expansion happens at Phase 6a once the preview is rendered and the real breathing room is visible.

By this phase the post-Phase-3 timeline is *known*, and the beat sheet declares which beats are `dwell: y` (zoom-eligible). The script writes to the beat sheet's locked seconds per beat — for dwell:y beats, that target *includes* the planned zoom-insert seconds, so the VO is sized to the *post-zoom* beat length, not the scrubbed length.

For each `dwell: y` beat, the script also identifies the zoom target: the specific on-screen subject the VO names (a header, a number, a panel). That target becomes a row in the project's zoom-directive file, consumed by Phase 5.5.

**The zoom directive's `duration` field equals the beat sheet target seconds — NOT the punchy VO's actual speech time at Phase 5.** This is the load-bearing convention. The zoom hold is sized for the polished VO from the start, not the punchy under-fill. When Phase 5.5 produces the zoomed file, the hold has built-in headroom for Phase 6a to expand the VO into. If you size `duration` from the punchy VO instead, the hold is too short and Phase 6a's rhythm expansion triggers the Phase 1 backup loop (re-open Phase 1, extend the target, re-cascade). Avoid the loop by reading from the beat sheet's target seconds, not the punchy draft's spoken length.

For craft rules within the script-writing phase — voice composition, banned words, AI-tell transitions, "show on screen / interpret in voiceover," hallucination check — consult a sibling craft skill. The companion `video-scriptwriting` skill is one such; future projects can author their own or adapt it.

**The dwelling principle, restated for the script-writing phase:** recording activity time ≠ VO time. When a content-rich visual settles, VO can dwell on it for 2–3× the reveal motion via Phase 5.5 zoom. Don't cut beats just because the visual finished animating. The beat sheet's `dwell: y` flag tells you which beats can carry extra VO without forcing recording changes.

### Phase 5.5 — Apply zoom

**Input:** scrubbed recording + script + zoom directives (one per dwell:y beat).

**Output:** zoomed recording — the canonical timeline for Phase 6 render.

This is where the dwelling principle is realized. For each zoom directive: measure the precise pixel bounds of the named subject (project-local measurement tools per Hard Rule #10 — `measure_highlight.py` for annotate spotlights, `detect_ticks.py` for tick events), then apply the pause-zoom-hold-resume via the project's zoom tool. The zoomed recording is the timeline LTs, captions, and the composition template all reference from here on (Hard Rule #12).

**Why this phase exists separately from Phase 3.** Zoom region is what the VO names; you can only know that after Phase 5. Phase 5.5 is where script content gets to drive visual emphasis instead of guessing it upfront.

**If zoom design fails here** — no settled visual on a dwell:y beat to zoom into, or VO names content not present in the scrubbed recording — re-record. Don't paper over with an arbitrary zoom region. Zoom serves the VO, never the other way around.

### Phase 6 — Render

**Input:** zoomed recording + script + project's render template.

**Output:** preview render (no avatar, no billable steps — fast iteration), then final render (with avatar / TTS, billed).

Iteration on layout, timing, and copy happens at the preview stage and costs nothing. Only the final render bills the avatar / TTS provider. Cache the avatar clip by script-body hash so unchanged scripts don't re-bill on layout-only iterations.

### Phase 6a — Polish pass (auto)

**Input:** rendered preview from Phase 6 + the script (Phase 5 output or revised mid-iteration) + `tools/zoom.py` segment-timing output (actual seg_annotate_NN start/end + seg_src_NN durations after `--clean-source-ranges` cleaning).

**Output:** revised script — VO body rhythm-balanced (fragments where data IS the punch, full sentences for connective / interpretive lines); LT and panel content updated *only if Phase 5 cut beats or reordered points*; stage-direction timestamps re-synced to the rendered preview.

**Auto-trigger contract — Phase 6a runs automatically after:**
- Every Phase 5 completion (script change) — to verify beat coverage (no orphaned LTs/panels), 12-angle rotation still intact, and apply the rhythm pass against the latest known timings.
- Every Phase 6 completion (preview re-render) — to re-derive stage-direction timestamps from the freshly rendered timing and apply the rhythm pass against the now-known breathing room.

The user does not need to invoke Phase 6a manually; it chains off Phase 5 and Phase 6 automatically. Project-local trigger phrases (*"polish V<N>"*, *"tweak V<N>"*) are available for explicit re-runs.

**What Phase 6a does (in order):**

1. **Sync check** — for each `lower_thirds[].in/out_recording_t` and `annotations[].in/out_recording_t` in the script frontmatter, verify the values match the zoomed file's actual segment timings. Per Hard Rule #12 — re-derive against the canonical zoomed timeline, not the beat sheet's pre-zoom targets.
2. **Beat coverage check** — every spoken VO beat in the body maps to a panel, LT, or zoom hold. Catch orphaned beats (VO references a panel that doesn't exist) or orphaned graphics (LT fires with no VO content).
3. **Runtime check (decides between rhythm pass and beat cut)** — measure the rendered runtime against the speakable window. *Speakable window* = total composition runtime − (title card + outro + intentional silences + scroll segments). *Spoken VO budget* = current VO word count ÷ 150 wpm. **Two branches:**
   - **Runtime fits** (spoken budget ≤ speakable window): proceed to step 4 (rhythm pass).
   - **Runtime overflows** (spoken budget > speakable window): proceed to step 5 (beat cut) and skip step 4 this pass. The cut beat creates new headroom that the next auto-Phase-6a run can use for rhythm expansion.
4. **Rhythm pass (runtime fits)** — count fragments vs full sentences across the VO body. If fragments ≥ 60% of total sentences, restore full sentences in the connective/interpretive beats. Project-local mix target for `use_case` style: ~40% data-fragment + ~35% short-sentence + ~25% full-sentence (Hard Rule #6(b)). Earned fragments stay (data callouts, hero shots). **Per-beat overflow check:** for each beat, estimate the polished VO length (punchy → polished ≈ +20–30% words). If `polished_seconds > zoom_hold_seconds` for that beat, the expansion can't fit within the existing hold → trigger the backup loop (step 5b) for that beat. Otherwise apply the expansion.
5. **Beat cut (runtime overflows globally)** — when the total spoken VO budget overflows the speakable window globally, drop a whole beat at full rhythm. Never abbreviate word-by-word across remaining beats. Selection criterion: drop the *lowest-priority* beat per the video's `Primary value angles` (MASTER spec) — the beat whose value-angle is most expendable / most served by other beats. Re-author the surrounding stage directions to bridge the cut. Hard Rule #6(c).
5b. **Backup loop — re-open Phase 1 (per-beat overflow, runtime globally still fits)** — when an individual beat's polished VO overflows its zoom hold but the global runtime can still accommodate it (i.e., the beat is under-allocated, not the video over-stuffed), auto-fix by extending the beat upstream: (i) read the beat's current target seconds from MASTER.md beat sheet; (ii) extend it by `overflow_seconds + 0.5s buffer`; (iii) write the new target back into MASTER.md beneath that video's beat sheet; (iv) update the matching zoom directive's `duration` in `V<N>_zooms.json` to the new value; (v) re-run Phase 5.5 (`tools/zoom.py` with the new duration); (vi) re-run Phase 6 (preview render against the new zoomed file). The auto-Phase-6a that fires after the re-render now sees a hold large enough — proceeds normally to step 4 rhythm pass. Convergence: the backup loop should fire AT MOST once per beat. If a single beat triggers it twice across iterations, escalate — likely an under-estimation of polished VO length OR the beat is genuinely over-scoped for the video's runtime envelope.
6. **LT + panel update (conditional)** — touch LTs and panels only when Phase 5 cut beats OR reordered points OR step 5 just dropped a beat (large restructure cases). Orphaned LTs/panels from a cut beat get removed; remaining LTs/panels stay format-locked (eyebrow + headline + locked vocabulary).
7. **Re-render preview** if any changes were applied (steps 4, 5, 5b, or 6 made edits). If only step 1 (sync) updated frontmatter timings but no body changes happened, also re-render. If no changes, report "Phase 6a clean — no edits needed" and stop.

**Convergence:** Phase 6a is idempotent — running it on a script that already passes all four checks produces no edits and returns "clean." After Phase 6a applies changes and triggers a re-render, the next Phase 6a run (auto-triggered by the re-render) should converge to clean within one or two passes. If Phase 6a keeps making edits across multiple iterations, that's a bug — investigate (likely a check that's misidentifying acceptable patterns as violations).

**Hand-off to Phase 6b:** when Phase 6a returns "clean" (no edits applied this pass), the chain proceeds automatically to Phase 6b (lint). The polish phase has converged — the artifact is structurally consistent against its own frontmatter and the post-render timing. Phase 6b verifies it's also consistent against the project's Hard Rules.

### Phase 6b — Mechanical lint (auto)

**Input:** the converged script frontmatter (Phase 6a output) + zoom directives + scrub report + tick JSON + render manifest + ffprobe of the zoomed source recording.

**Output:** a pass/warn/error report from the project's deterministic linter — one finding per violated Hard Rule, each citing the rule ID and a concrete diff hint.

**What this phase is.** A deterministic, free, no-LLM mechanical check of every Hard Rule that's computable from project artifacts alone (framerate, keyframe density, panel-hold floor, safe-zone position, highlight tier, frontmatter timing sync, skeleton presence, z0b sizing, template-slot exhaustion, etc.). It's the project's contract test for its own pipeline — the assertion that the artifacts you're about to ship satisfy the rules the project has locked in.

**Why this phase exists separately from Phase 6a.** Phase 6a's job is to make the script internally consistent against the rendered preview (the polish phase converges *the artifact against itself*). Phase 6b's job is to verify the artifact is consistent against *the project's Hard Rules*. These are different invariants — a script can be perfectly polished and still violate Hard Rule #15 (sparse keyframes) or Hard Rule #17 (safe-zone). Splitting them keeps the polish phase focused on rhythm/coverage/timing and the lint phase focused on rule conformance.

**Auto-trigger contract — Phase 6b runs automatically after:**
- Every Phase 6a "clean" convergence (the chain proceeds the moment polish has no more edits to make).
- Every Phase 9 final render completion (the final artifact gets the same rule check as the preview).

**Severity tiers:**
- **Error-tier findings (Tier 1)** — violations of Hard Rules with concrete numeric thresholds that can be checked mechanically (framerate ≠ 60, keyframe interval > 1s, frontmatter timing drift > tolerance, panel hold < `min_hold` floor, safe-zone position outside 30–70%, highlight height > tier-2 cap, skeleton element missing, z0b sizing off, template slot referenced but undefined). These STOP the chain — do not proceed to Phase 6c.
- **Warn-tier findings (Tier 2)** — softer violations or proxy checks for things the linter can't perfectly verify (banned-engineering-phrase substring match, slash-command-in-VO substring, capability-count pattern, draft-mode markers). The chain continues to Phase 6c; warnings are surfaced alongside the reviewer's findings in the final report.

**Hand-off to Phase 6c:** if Phase 6b returns no error-tier findings, the chain proceeds automatically to Phase 6c (LLM review). If it returns *any* error-tier finding, the chain stops at 6b — surface findings to the user, do not run the reviewer.

**Why lint gates the reviewer.** The LLM reviewer expects a well-formed input. Running R01 (subject-match) against a video whose annotate timings drifted out of sync with the rendered timeline produces garbage findings — the spotlight isn't where the panel says it should be, so every R01 reads "drift," but the root cause is L01 (timing sync), not a real subject-match failure. Lint-as-gate keeps the reviewer's findings actionable and saves the API spend that would otherwise be wasted on a broken artifact. Tier-1 == hard gate is the load-bearing convention.

**Convergence:** Phase 6b is non-iterative. It runs once per Phase 6a convergence (or once per Phase 9 final). Findings are reported; the user (or upstream phases) act on them. There is no "Phase 6b applies its own fixes" — that would couple the linter to the artifact's mutation logic, which belongs in Phase 6a.

### Phase 6c — Semantic review (auto)

**Input:** the lint-passing artifact from Phase 6b (frontmatter, VO body, zoom directives, frames_used, the rendered preview or final).

**Output:** a markdown review report at the project's per-video output path with the LLM's verdicts on the rules that require semantic judgment — subject-match between spotlight and panel, customer's-chair framing, panel-shape rotation, vault-stat integration, beat content visibility, hallucination check against frames_used.

**What this phase is.** A vision-grounded LLM pass that catches the semantic failures the deterministic linter can't — does the spotlit area visually match what the panel pitches? Is panel copy in audience-perspective vocabulary? Do the panels rotate through capability/workflow/stakes shapes, or do three in a row land in the same mold? Does each `frames_used:` citation actually depict what the script claims it does? These are judgment calls — they require a model that can look at a frame, read the surrounding copy, and reason about whether the two cohere.

**Why this phase exists separately from Phase 6b.** Lint is deterministic and free; reviewer is semantic and billed. Mixing them would either (a) couple the deterministic checks to the LLM round-trip's variance and cost, or (b) force the reviewer to do mechanical checks it's bad at (it would have to compute panel-hold floors and safe-zone percentages from scratch instead of just reading the linter's output). Separating them keeps the cheap pass cheap, makes the expensive pass narrowly-scoped, and gives the user a clean failure mode if the LLM call errors out (the lint result is still authoritative).

**Auto-trigger contract — Phase 6c runs automatically after:**
- Every Phase 6b pass (no error-tier findings). The chain fires whether the preceding render was a preview or a final.

**Cost model.** The reviewer is billed per API call. The project caches responses by content hash so re-runs against unchanged input cost zero; the first run after a script body change or a re-render is the only billable case. Caching is a load-bearing optimization — without it, every Phase 6a convergence would re-bill the reviewer, which makes the auto-chain too expensive to leave on by default.

**Severity tiers:** the reviewer reports findings as pass / drift / fail per rule. "Fail" means a concrete violation surfaced (e.g., R01 — the spotlight is illuminating a row the panel doesn't discuss). "Drift" means the LLM is unsure or sees partial misalignment. "Pass" means clear conformance. The chain doesn't auto-stop on reviewer findings — the report is surfaced to the user, who decides whether to re-open earlier phases.

**Skip behavior:** the reviewer is the only billable step in the lint+review chain. Project-local: a `--no-review` flag (or equivalent skill-level opt-out) skips Phase 6c entirely for cost-sensitive iterations. The default is to run.

**Convergence:** Phase 6c is non-iterative. It runs once per Phase 6b pass. Findings drive user-side action; the reviewer doesn't mutate the artifact.

## Hard rules

These are non-negotiable across projects. Violations compound through the pipeline.

1. **The beat sheet is upstream.** It is locked before recording begins. Changes to the beat sheet after Phase 2 require re-scrubbing (Phase 3) and/or re-zooming (Phase 5.5) the recording, not patching the script.
2. **Conform the recording, don't compress the script.** When the recording doesn't match the beat sheet, change the recording. Never silently shrink VO beats to absorb recording mismatch.
3. **Captions, lower-thirds, and on-screen graphics schedule into beat windows, not recording timestamps.** All downstream artifacts reference beats, not raw seconds. When the beat sheet shifts, graphics shift with it because they were never bound to the recording's timeline in the first place.
4. **The recording must visibly contain each beat's claimed content.** Audited via Phase 4 frame extraction against the scrubbed recording. If a beat's content isn't visible, re-scrub or re-record — don't silently rewrite the script to match what's actually on screen.
5. **Dwell-eligibility is a beat-sheet property, not a script discovery.** Mark `dwell: y` at Phase 1. The script-writing phase reads it; it doesn't invent it.
6. **Cut whole beats, never word-by-word within a beat — and never telegraph when you have room.** Phase-aware: all editorial decisions (rhythm balance, beat cuts) defer to Phase 6a where actual post-render runtime is known. Phase 5 stays mechanically punchy.

   (a) **Phase 5 — write all beats at punchy default.** Don't pre-cut beats; don't try to balance rhythm. At Phase 5 you have target seconds from the beat sheet but not actual post-zoom segment timings (Phase 5.5 zoom + Phase 6 render reveal those). Writing all beats fragment-heavy is conservative — short data-callout lines fit any final timing. Editorial judgment (what to keep, what to expand, what to cut) defers to Phase 6a where you can see actual numbers, not guesses.

   (b) **Phase 6a — rhythm pass (when runtime fits).** Once Phase 6 is rendered, the actual breathing room is visible (zoom inserts, silent-scrolldown beats, and intentional silences typically leave 20–40% of the speakable window unspoken). Now expand the connective and interpretive lines from fragments to full sentences. Earned fragments stay (data callouts, hero shots: *"Composite at five. Quality and Tactical, ten. Value, three."*). Connective VO becomes full sentences (the analytic / interpretive work that names *what the on-screen data means*: *"The pattern tells you the trade: you pay up for the compounder, and you go in with eyes open on the multiple."*). TTS reads natural rhythm better than telegraph rhythm. Symptom of getting this wrong: every line lands as a fragment, VO reads like a stock-ticker alert feed instead of a person speaking to a person. Project-local heuristic for use_case style: ~40% data-fragment + ~35% short-sentence + ~25% full-sentence across the polished draft.

   (c) **Phase 6a — beat cut (when total runtime overflows).** When the rendered preview reveals that the spoken VO can't fit even at punchy rhythm, drop an entire beat at full rhythm rather than clip every line for fit. A script covering six beats with natural pacing lands better than ten in telegraph style. The choice is whole-beat-or-nothing, never word-by-word abbreviation across remaining beats. After cutting, also touch LTs and panels — they're the load-bearing visual companions of the cut beat (Phase 6a check #4 — LT/panel update is conditional on this case).

   (d) **Phase 6a backup loop — re-open Phase 1 (when an individual beat's polished VO would overflow its zoom hold, but global runtime still fits).** This means the beat sheet under-allocated for that one beat; the polished VO has nowhere to expand within the hold's duration. Auto-fix: extend the beat's target seconds in MASTER.md (Phase 1) by `overflow_seconds + 0.5s buffer`, update the matching zoom directive's `duration` in `V<N>_zooms.json`, re-run Phase 5.5 (zoom), re-run Phase 6 (preview), let auto-Phase-6a fire again — this time the hold accommodates the expansion. The backup loop should fire AT MOST once per beat; if a beat triggers it twice across iterations, escalate (likely under-estimated polished length or beat is genuinely over-scoped). This case exists because the upstream calibration rule ("beat sheet targets calibrated for polished VO, not punchy") sometimes gets it wrong on the first pass — the backup loop is the corrective.

   Note: cases (b), (c), and (d) are mutually exclusive *per beat per polish-pass run*. Global runtime check decides between (b) and (c). Per-beat overflow check within step 4 (rhythm pass) triggers (d). Cases compose across iterations: a (c) beat cut creates headroom that the next auto-Phase-6a run uses for (b) rhythm expansion on remaining beats; a (d) backup loop fixes one beat's allocation and the next auto-Phase-6a run completes (b). Convergence is expected within 1–2 passes per beat overflow, 1–2 passes per global overflow.

   Logged: `decisions/2026-05-20-sentence-rhythm-with-budget-headroom.md`, `decisions/2026-05-20-phase-6a-polish-pass.md`.
7. **Every on-screen claim in the script must cite a frame.** Hallucination check is enforced at Phase 5, grounded in the Phase 4 frame audit. No exceptions — wrong stats in published video are credibility-destroying.
8. **Preview is free; final is billed.** Iterate on layout, timing, and copy at preview. Promote to final only when the preview is shippable.
9. **Pause-zoom segments are sized by the beat sheet, never by runtime deficit.** Each dwell:y beat with a settled visual gets one zoom whose duration matches the beat's locked seconds and whose region is the bounding box of *what the VO names in that beat*. If three dwell:y beats discuss three regions, that's three zooms — not two stretched to fill the deficit. If the resulting runtime doesn't match the originally planned composition target, re-lock the beat sheet explicitly or accept the new runtime. Never compress, expand, or invent zoom durations to make the math work.

10. **Pixel-bound zoom inputs (highlight rects, spotlight regions, tick search regions) are anchored to measured source-frame pixels, not eyeballed coordinates.** Any zoom-pipeline value that names a specific position in the source frame — `highlight_region_pct` for annotate-mode spotlights, search regions for tick detection, etc. — is derived programmatically from the scrubbed recording's pixels at the relevant `source_t`, never typed in by hand. Project-local tools own the actual measurement: `tools/measure_highlight.py` for annotate highlights (Hard Rule #24), `tools/detect_ticks.py` for tick events (Hard Rule #20). The portable rule is just: *don't ship hand-tuned pixel values, ever — re-measure once per video and paste the output into the JSON*. Per-video calibration is a one-command operation, not a re-tuning session. Hand-tuning bypasses the consistency the measurement tools enforce (text-row snapping, gap detection, etc.) and produces visually inconsistent results across the project.

    *History: this rule was originally written about underline overlays in the pre-2026-05-19 pipeline. Underlines were retired in favour of soft-edged elliptical spotlights (Hard Rule #17), and the rule generalised to cover every pixel-bound input to the zoom pipeline. The "measured, not eyeballed" discipline is the through-line — the specific overlay style changed, the rule about how to author its pixel coordinates didn't. Logged: `decisions/2026-05-19-annotate-spotlight-default.md` (spotlight replaces underline as default emphasis).*

11. **Freeze-frame and zoom-rendered segments must stay in the same colour space as the source playback.** When a zoom pipeline interleaves "freeze on a still" segments (zoom-on-held-frame, pre-zoom holds, post-zoom holds) with source playback, the still-derived segments must NOT round-trip through RGB. A YUV→RGB→YUV round-trip via PNG introduces ~1-2 luma units of brightness shift even with explicit colour-space flags, because libswscale's bidirectional conversions aren't perfectly symmetric in 8-bit precision. The visible result: the freeze frame looks slightly darker (or lighter) than the source playback, with a perceptible "pop" at the boundary. Fix: extract the freeze frame as a single-frame YUV mp4 (preserving the source's `pix_fmt`, `colorspace`, `color_primaries`, `color_trc`, `color_range`) and stream-loop it rather than reading a PNG. All segments — source playback, freeze holds, zoom segments — must encode with the same explicit colour metadata so concatenation produces a colour-consistent output. Project-local: `tools/zoom.py` enforces this via single-frame mp4 extraction and `-color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv` on every encoding step (or the source's actual color metadata, which `ffprobe` reveals).

12. **The zoomed recording is the canonical timeline for downstream artifacts — re-derive after every re-zoom or re-scrub.** Once Phase 5.5 produces a zoomed recording, that is the timeline LTs, annotation panels, captions, script timing markers, and the composition template all reference. The beat sheet's target seconds were inputs to Phase 3 + 5.5, not outputs. If you re-run zoom (different durations, regions, pre_zoom_hold, `--clean-source-ranges`) or re-run scrub (different threshold), the zoomed recording's beat windows shift — and every downstream artifact must be re-derived against the new zoomed recording, not the original beat sheet. Symptom of getting this wrong: LTs land on the wrong content (a "trajectory" lower-third appears during the score-panel zoom), or annotation panels fade in BEFORE their corresponding zoom-in fires (e.g., panel ap2 at recording_t=67.73 while seg_annotate_02 actually starts at 68.87 because the prior source segment wasn't cleaned, shifting the zoom 1.14s later than the script frontmatter expected). Project-local discipline: after every `tools/zoom.py` rerun, re-read the "segment timing in zoomed file" output and re-align every script-frontmatter `lower_thirds[].in/out_recording_t` AND `annotations[].in/out_recording_t` against it. This rule lets you operate the workflow in **pragmatic mode** (Phase 1 beat sheet = rough guidance, recording naturally drifts, Phase 3 + 5.5 absorb drift) without breaking downstream — you just have to re-derive after each pass instead of trusting the beat sheet's targets.

13. **Never slow down source playback. Anywhere. For any reason.** No uniform-rate slowdown of a too-short beat, no pre-zoom deceleration ramp, no setpts stretch on a transition. Slowed motion reads as syrupy at uniform rates and produces a rubber-banding stutter on ramps — the user has rejected both ("looks like shit"). The only sanctioned ways to extend a beat are: insert a held-still frame, insert a script-driven pause-zoom on a dwell:y beat, or re-record. If none of those apply, the beat is unfit and Phase 3 escalates to re-record (or, rarely, re-opens Phase 1). The `pre_zoom_slowdown` machinery has been removed from `tools/zoom.py` accordingly; the only zoom-prep extension knob that remains is `pre_zoom_hold` (held still, no motion).

14. **Source material is preserved until the user explicitly approves the final output. Cleanup runs only on an explicit approval signal.** Source recordings, intermediate artifacts, scripts, and final outputs are never auto-deleted. Approval signals: *"yes"*, *"approved"*, *"ship it"*, *"looks good, ship"*, *"delete the frames"* — i.e., the user names the cleanup action or unambiguously OKs it. Non-approval (treat as don't-touch): *"thanks"*, *"will watch later"*, *"let me check"*, *"renders look ok"*, silence, or any ambiguity. The asymmetry exists because intermediate artifacts are cheap to regenerate but annoying to lose mid-review — the cost of an unwanted cleanup is much higher than the cost of leaving scratch files on disk for another session. Project-local: in this project, `frames/V<N>/` is the scratch artifact whose cleanup is gated; the orchestrator's `"clean V<N> frames"` dispatch row requires the explicit approval signal. The following files are NEVER deleted at cleanup time regardless of signal: `outputs/V<N>/final.mp4`, `audio/V<N>.mp3` (if used), `screen recordings/V<N>/vid<N>.mp4`, `screen recordings/V<N>/vid<N>_scrubbed.mp4`, `screen recordings/V<N>/vid<N>_zoomed.mp4`, `scripts/V<N> voiceover script.md`, `scripts/V<N>_zooms.json` — these are the durable record.

15. **Source recordings and rendered output share a framerate; keyframe density is tight enough that the renderer's frame-by-frame seek operations don't hang on sparse keyframes.** Renderers that seek mid-clip during composition (zoom segments, transitions, cuts) decode forward from the nearest preceding keyframe. When keyframes are 2+ seconds apart, those seeks stall or hang — the renderer either takes 10× as long as expected or freezes outright. If the source arrives at the wrong framerate or with sparse keyframes, re-encode BEFORE Phase 3 scrub, not after. Project-local: this project ships 60fps end-to-end with 1-second keyframe intervals. Re-encode with `ffmpeg -i input.mp4 -r 60 -g 60 -keyint_min 60 output.mp4` before running `tools/scrub.py`. Hyperframes (the project's renderer) exhibits the violation as: renders hang at the first zoom segment, or take 5+ minutes when they should take ~30 seconds. `tools/scrub.py` + `tools/zoom.py` preserve framerate and keyframe density on output; template render commands explicitly set `--fps 60`.

16. **Hold-mode and annotate-mode zooms targeting the OUTPUT BRIEF content must not trigger while the cursor is sitting on any readable text in that area.** A pause-zoom that holds a still frame with the cursor obscuring the content the viewer is supposed to read defeats the purpose of the zoom. Wait until the cursor has moved off the readable column (or below/above the visible reading area), then trigger. SCOPE: applies only to zooms targeting the rendered output brief content (score panel, factor pillars, trajectory column, bottom-line verdict, methodology paragraphs, etc.) where the viewer is reading specific text. DOES NOT apply to zooms targeting tool-call loading sections (the chat activity area showing parallel calls firing) — the viewer is watching tool activity, not reading deliberately, so cursor position over that area is fine. Encoded in `tools/zoom.py` via the `wait_cursor_clear: true` flag on output-brief zoom directives (default off — opt-in per directive). When set, the tool auto-advances `source_t` until cursor detection confirms the cursor is outside the cursor-clear region (fallback to base `source_t` after `DEFAULT_CURSOR_CLEAR_MAX_DELAY_S = 4s` if no clear moment is found). **Cursor-clear region per mode:** hold-mode uses `region_pct` (focal centroid). Annotate-mode uses a synthetic region combining `highlight_region_pct`'s x extent (the readable column) with `zoom_region_pct`'s y extent (the full vertical reading area) — so a cursor sitting on an *adjacent row* of the same table (e.g., Quality when z1 highlights Value) still counts as obscuring, but a cursor in the dark padding to the right of the content column does NOT. **Known limitation:** the detector uses inter-frame motion centroid; a fully-static I-beam parked on text won't be detected (no motion) and the fallback to base_t lets the zoom fire with the cursor still on text. Mitigation: re-record with deliberate cursor moves off the brief between content beats, or extend `cursor_clear_max_delay` per-directive. Logged: `decisions/2026-05-18-cursor-clear-rule.md`, `decisions/2026-05-19-cursor-clear-region-broader.md`.

17. **Annotate-mode spotlights must land within the composition's vertical safe zone — comp y=30% to y=70% (a 40%-tall band centered on comp middle).** The previous strict "land at comp vertical center (y=50%)" requirement is retired (per `decisions/2026-05-25-spotlight-vertical-safe-zone.md`). For every `mode: "annotate"` directive, the soft-edged elliptical spotlight's comp-space y position (computed via the zoom_region transform from `highlight_region_pct.y + h/2`) must fall within [30%, 70%]. The visual contract with the viewer is unchanged: the annotation panel on the right and the spotlighted content on the left share a common eye-resting region, so attention doesn't split between top and bottom edges of the frame. ENFORCEMENT: (a) compute `comp_y = (highlight_y_center − zoom_region.y_offset) / zoom_region.height × 100`. If `30 ≤ comp_y ≤ 70`, the spotlight is acceptable as-is. Otherwise, choose a different `source_t` (scroll into the band) OR shift/widen `zoom_region` (transform the comp position into the band) OR split into sub-annotates with different source_t per Hard Rule #24. (b) **For sub-annotate clusters (Hard Rule #24 multi-VO-target split):** prefer ONE source_t + ONE zoom_region across the cluster so the camera holds still and only the spotlight moves between rows. Algebra: for a cluster spanning source y from `y_min` to `y_max`, a single zoom_region centers it iff `height ≥ (y_max − y_min) / 0.4`. If the cluster's span exceeds 40% of source, no single zoom_region works — split into multiple source_t (accept the scroll between them) or restructure. (c) `tools/zoom.py` enforces the aspect check + y_offset clamp (prevents black bands) and the cursor-clear region per Hard Rule #16. SCOPE: only `mode: "annotate"`. Hold-mode (centered camera-pan zoom) and follow-mode (continuous-playback pan) have different framing contracts. The default annotate visual is a soft-edged elliptical spotlight (oval bright area centered on `highlight_region_pct`, surrounding content dimmed at 60% with Gaussian-blurred edge transition) — no rectangle border, no numbered dot beside the highlight. Logged: `decisions/2026-05-19-annotate-vertical-centering.md` (original strict-center rule, now refined), `decisions/2026-05-19-annotate-spotlight-default.md` (visual style), `decisions/2026-05-25-spotlight-vertical-safe-zone.md` (this refinement).

18. **Overlay animations synced to a camera move must share the camera's ease curve.** When an annotation panel, lower third, or any overlay graphic fades/slides in lockstep with a camera move (annotate zoom-in, hold-mode zoom-in, follow-mode pan-in), both motions must use the same easing function. If the camera uses `easeInOutSine` (slow start, fast middle, slow end — the project default) and the overlay uses `power2.out` (fast start, slow end), at progress 0.25 the camera is at ~15% of its move while the overlay is at ~44% — visibly out of phase. The viewer reads the overlay as "early" or "ahead of" the camera even when both start at the exact same composition time. Cause: GSAP's `power2.out` and `sine.inOut` have different derivative profiles; `sine.inOut` matches the symmetric S-curve `tools/zoom.py` uses (`ANNOTATE_EASE_NAME = "easeInOutSine"` in zoom.py corresponds to GSAP `"sine.inOut"`). Project-local: `templates/product-demo/index.html` `annotatePanel()` uses `ease: "sine.inOut"` for both the in (`fromTo`) and out (`to`) animations. The duration of the overlay's in/out animation should also match the camera's ease duration (default 1.0s for annotate). If a future template changes the camera ease in `tools/zoom.py`, change the matching overlay ease in the same commit. Logged: `decisions/2026-05-20-overlay-ease-matches-camera.md`.

19. **Source segments between annotate holds must be cleaned of held/duplicate frames before render.** After Phase 5.5 produces the zoomed recording, the `seg_src_NN.mp4` segments between annotate holds play through at scrubbed speed. If the scrubbed source has held frames shorter than `tools/scrub.py`'s `min_dead_seconds` threshold (default 5s — anything ~0.5–4s long survives scrubbing), they remain frozen frames in the zoomed file's source-playback segments, perceived by the viewer as "lag" or "stuttering" in mid-scroll motion. Detection: sample frames at 0.25s intervals across each `seg_src_NN.mp4` range; identical MD5 hashes flag freezes. Fix: pass `--clean-source-ranges "S1:E1,S2:E2,..."` to `tools/zoom.py`, listing each cleanable source-time range (the function requires the entire segment from `cursor` to `next_annotate.source_t` be inside one of the ranges); zoom.py runs `mpdecimate` on those segments, dropping consecutive duplicate frames at the encoder level. Natural-motion frames are preserved (they're not duplicates). Project-local: the orchestrator's "zoom V<N>" dispatch defaults to cleaning every source segment between annotates (e.g., for three annotates at source_t = a, b, c with prior cursor d, pass `"d:a,a:b,b:c"`). After cleaning, the segment timing in the zoomed file shifts — re-derive `lower_thirds[].in/out_recording_t` and `annotations[].in/out_recording_t` per Hard Rule #12. Logged: `decisions/2026-05-20-clean-source-segments.md`.

20. **Tick timestamps must be detected programmatically, never eyeballed — and detection runs on the RAW recording during Phase 3, not on the scrubbed file during Phase 5.5.** When a recording contains a progress-bar or status-checklist loading sequence (Cowork's top-right Progress sidebar, equivalent UIs), the tick events are compressed via the gap-cut rule (see Hard Rule #23). Tick timestamps that drive that compression come from frame-diff detection on the RAW recording — not from sampling frames at 1s intervals and guessing, AND not from running detect_ticks on the scrubbed file (by which time the freeze-compression in scrub.py has already squeezed ticks together, leaving the gap rule nothing to compress). Run `python tools/detect_ticks.py "<raw_recording>" --time-range "<t0>:<t1>" --region-pct "x,y,w,h" --expected-ticks N --output <ticks.json>` once per video, BEFORE scrub.py runs. The tool samples at 30fps in the search region, computes frame-to-frame mean absolute pixel diff, returns the top-N peaks with non-maximum suppression, and emits `ffmpeg_keep_ranges` derived from the gap-cut rule (gaps > 2s compress to 1s, gaps ≤ 2s leave alone). **Tick-window bound is the PENULTIMATE tick `T_(N-1)`, not `T_N`.** The final tick in a Parallax product_demo is reliably "Synthesize and deliver brief," which fires AFTER the brief is fully rendered. The tick window for the scrub.py lock + gap-cut compression extends from `T_first_tick` to `T_(N-1)`, excluding the synthesis tick. The synthesis tick `T_N` falls in buffer zone 2 (post-`T_(N-1)`, pre-`T_brief_landed`), which scrub.py compresses — `z0b`'s ease-out plays during this compressed buffer so the viewer watches the brief progressively render in fast-forward. Implementation: invoke detect_ticks with a search range covering all ticks (e.g., `--time-range "T_typing_end:T_brief_landed"`), then in orchestration use `ticks[N-2]` (zero-indexed penultimate) as the tick window's upper bound; re-invoke detect_ticks with `--time-range "T_first_tick:T_(N-1)"` to get gap-cut keep_ranges scoped to the penultimate-bounded window. Paste those keep_ranges into the ffmpeg trim+concat that builds the tick-compressed segment of the scrubbed file (Hard Rule #23 step 3). For simultaneous ticks (two checklist items tick at the same instant), count as ONE moment when setting `--expected-ticks`. If true ticks have very different visual magnitudes, request more peaks than expected and discard the lowest-magnitude false positives. Companion to Hard Rule #10 (measured pixel bounds) — same "measured, not eyeballed" discipline. Logged: `decisions/2026-05-21-detect-ticks-programmatic.md`, `decisions/2026-05-23-tick-window-compression-moves-to-phase-3.md`.

21. **Multiple recording segments are locked at 1× — never compressed. `scrub.py` only compresses dead time in the buffer zones between them.** Three zones get 1× lock; `scrub.py`'s pixel-diff freeze compression applies only to the gaps between them. The three locked zones for a product_demo:

    (a) **Prompt typing → submit click** (`0` to `T_typing_end`). The persona's question gets named in the customer's chair here; the value-framing for the whole video anchors at this moment. **Default: 1× lock** — viewers read the question being typed. **Adaptive speedup when typing exceeds 10s** (long-prompt videos: V13 family-office onboarding, I3 quad-client demonstration, hero playbooks): `speedup_factor = min(2.0, max(1.0, typing_duration / 10.0))`, capped at 2× to avoid the comedic register that more aggressive speedup produces (keystroke pixel-diffs already sit below the freeze threshold; >2× rates the keystrokes as visibly machine-fast, breaking the customer's-chair register). Worked examples: 15s → 1.5× (post-speedup 10s); 20s → 2× (post-speedup 10s); 30s → 2× (post-speedup 15s — can't do better without exceeding the cap); 40s → 2× (post-speedup 20s). Threshold of 10s = the upper bound of "tolerable 1× typing" (a short NL prompt of ~2–3 sentences, the canonical V1/V2/V3 shape). **Diverges from news's Rule N2** (always-2× speedup regardless of duration): news's typing is context (not deliverable content), so aggressive speedup is fine throughout. Product-demo's typing IS load-bearing content (the persona's NL prompt the viewer reads), so 1× is the right default. Encoded via the Phase 3 scrub dispatch reading `manifest.phases.streaming_started` to derive typing duration, computing the speedup factor, and emitting `--force-speed-range "0:T_typing_end:<factor>"` to `tools/scrub.py`. Logged: `decisions/2026-05-29-product-demo-adaptive-typing-speedup.md`.

    (b) **Tick window — PENULTIMATE-bounded** (`T_first_tick` to `T_(N-1)`, the SECOND-TO-LAST tick). The Progress sidebar tick events fire here, BUT the final synthesis tick `T_N` is deliberately excluded — `T_N` ("Synthesize and deliver brief" or equivalent) fires AFTER the brief is fully rendered on screen, and treating it as the end of the locked tick window would put the actual brief-rendering animation INSIDE the locked zone (where it can't be compressed). Excluding `T_N` puts the synthesis/brief-rendering period in buffer zone 2 below, where `scrub.py` compresses it — the brief-loading animation then plays out during `z0b`'s ease-out (Hard Rule #23). `scrub.py` must NOT compress this tick window; compression happens via the gap-cut rule (Hard Rule #20 + #23) which is tick-aware.

    (c) **Brief-landed → end of recording** (`T_brief_landed` to recording end). The viewer reads the rendered output here; annotates fire during this zone in Phase 5.5. Compressing it would rush the read.

    Encoded by invoking `tools/scrub.py` with multiple `--force-speed-range` zones:
    `--force-speed-range "0:T_typing_end:1.0,T_first_tick:T_(N-1):1.0,T_brief_landed:end:1.0"`

    `scrub.py`'s general pixel-diff freeze compression applies only to the two buffer zones in between:
    - **Buffer 1** (`T_typing_end → T_first_tick`): post-submit, sidebar populating but no checkmarks yet — true blind dead-time.
    - **Buffer 2** (`T_(N-1) → T_brief_landed`): post-penultimate-tick synthesis. This is where the brief progressively renders in the chat area and the final synthesis tick `T_N` fires. `scrub.py` compresses this zone (typically a 24s tapered-with-cut down to ~1.5s), and `z0b`'s ease-out plays over the compressed result — the viewer watches the brief load in fast-forward as the camera retracts.

    Boundary identification: `T_first_tick` and `T_(N-1)` come from `detect_ticks.py` running on raw (Hard Rule #20). `T_typing_end` and `T_brief_landed` come from frame-by-frame inspection (the boundaries are visually obvious — submit-click animation; brief content first fully rendered).

    Companion to Hard Rule #13 (never slow source) — the asymmetry is deliberate: blind 2× freeze compression is fine for true dead loading but content moments get locked at 1×. Companion to Hard Rule #20 (tick detection) — the tick window's 1× lock depends on tick timestamps from `detect_ticks` running BEFORE `scrub.py`. Logged: `decisions/2026-05-22-prompt-typing-1x.md`, `decisions/2026-05-23-tick-window-compression-moves-to-phase-3.md`.

22. **The prompt-typing follow-zoom (z0) ease-out STARTS at T_click — the moment the cursor clicks the send button. The ease-out plays out during the loading initiation; it does NOT complete at the click moment.** The first zoom directive in every product_demo is a follow-mode zoom on the chat input box during prompt typing. Its `duration` field equals `T_click + ease_out_duration` where `T_click` is the scrubbed timestamp at which the cursor clicks the send button (visually identical to the moment the Progress sidebar first appears, since the click triggers the sidebar). Setting `duration` to "where the click happens" (i.e., ease-out COMPLETES at the click) produces a premature retraction: the camera starts retracting at typing-finishes, runs through the cursor-moving-to-button phase, and completes at the click — but the visible action (cursor reaching the button + clicking) happens DURING the retraction, so the viewer reads the camera as moving AHEAD of the action. The correct pattern: camera is HELD during typing AND during cursor-to-button transit AND during the click itself, then the click TRIGGERS the retraction, which plays out during the first 1.5s of loading. Identification protocol: during Phase 3 audit, sample raw frames at 0.2s intervals around the expected click moment; `T_click` = first frame where the Progress sidebar response is visible (sidebar appearing, prompt-box-empty state, "Starting up…" indicator — whichever comes first). For V1 (where the click → sidebar latency was longer): the equivalent computation yields a different duration than V2. For V2: `T_click_raw = 7.0s`, ease=1.5s, typing_factor=1.0 (typing under 10s), so `z0.duration = 7.0/1.0 + 1.5 = 8.5s`. The same `T_click_raw` value flows into three places in lockstep: `tools/scrub.py --force-speed-range "0:T_click_raw:<typing_factor>"`, the z0 directive's `duration = (T_click_raw / typing_factor) + ease`, and `z0b.source_t = (T_click_raw / typing_factor) + ease` (z0b starts immediately after z0 ends in scrubbed time). **When Hard Rule #21 zone (a)'s adaptive typing speedup applies** (raw typing >10s), `typing_factor > 1` and z0/z0b sizing uses the scrubbed-time post-speedup duration. Example: T_click_raw = 20s, typing_factor = 2.0, ease = 1.5 → `z0.duration = 20/2.0 + 1.5 = 11.5s` (not `20 + 1.5 = 21.5s`); `z0b.source_t = 11.5s` accordingly. Per Hard Rule #21's multi-zone lock, `T_click_raw` doubles as `T_typing_end` for the first locked zone. Companion to Hard Rule #21. Logged: `decisions/2026-05-22-zoom-skeleton-standardization.md`, `decisions/2026-05-29-product-demo-adaptive-typing-speedup.md`.

23. **Every product_demo zoom plan instantiates the standard skeleton: z0 (prompt follow) + z0b (Progress-sidebar follow) + z1..zN (annotate per VO-named content item). Tick-window compression happens in Phase 3 via the gap-cut rule, NOT in Phase 5.5.** The three parts of the skeleton:
    - **z0** (`mode: "follow"`): camera scales into the chat input box during prompt typing. Region = the prompt input rect. Duration = loading-segment boundary T (Hard Rule #22). Standard region for the Cowork chrome layout: `[40, 24, 38, 11]`.
    - **z0b** (`mode: "follow"`): camera scales into the top-right Progress sidebar **starting at the scrubbed-t where the checklist becomes fully visible** — equivalently, `z0b.source_t = zone-b start = T_first_tick − margin` (per the gap-cut rule below). NOT a fixed offset after z0 ease-out — the pre-checklist "Working on it…" period plays at full frame between z0 retraction and z0b approach, however long buffer (1) compression renders it. Region = the Progress sidebar rect. Standard region for the Cowork chrome layout: `[80, 0, 20, 30]`, zoom 2.5×. **Ease ≤ margin** (default `margin = 1.0s` → `ease = 1.0s`); this guarantees ease-in completes exactly when `T_first_tick` fires. The previous `ease 1.5s` standard is incompatible with `margin = 1.0s` and is retired; ease defers to margin. Holds zoomed while tool activity ticks accumulate.

      **z0b ease-out timing has two variants** depending on how the recording was produced:

      **Variant A — Manual screen recording** (the canonical case for V1–V16 today; recording produced by a human via OS screen capture, no `manifest.json` alongside). Eases out **starting at `T_(N-1) + margin`** — i.e., after the 1s post-penultimate-tick settling hold completes — NOT at `T_(N-1)` itself and NOT at the final synthesis tick. The visual contract: the final tick in a Parallax brief is always "Synthesize and deliver brief," which fires AFTER the brief is fully rendered on screen. If z0b eases out at the last tick, the viewer misses the brief progressively rendering. By easing out after the second-to-last tick's settling buffer, the camera retracts during the synthesis period — the viewer watches the brief progressively load in the chat area as the camera moves back to full frame. The final synthesis tick fires DURING the ease-out, completing the sidebar checklist at the same moment the brief becomes fully visible. Sizing: `z0b.duration = (T_(N-1) + margin) − z0b.source_t + ease_out_duration`. With `source_t = T_first_tick − margin` and `ease = ease_out = margin`: `duration = (T_(N-1) − T_first_tick) + 3·margin`. Edge case: if N=1 (only one tick), ease-out starts at that tick + margin. If N=0 (no ticks visible), skip z0b entirely.

      **Variant B — Automated capture** (`automation/capture.py` produced the recording; `manifest.json` is alongside `vid<N>.mp4` with `phases.scroll_to_top_done` set). The brief-progressively-loading segment between `T_N` and `T_brief_landed` is treated as filler (different from manual, where it's content) and excised by an additional Phase 3 cut. Specifically, Phase 3 pre-cuts `[T_N + post_synth_buffer, T_brief_landed]` (default `post_synth_buffer = 1.0s`) from `vid<N>.mp4` via ffmpeg trim+concat BEFORE running `scrub.py`. The cut shrinks buffer zone 2 to `[T_(N-1), T_N + post_synth_buffer]` and re-anchors `T_brief_landed` in pre-scrub time to `T_N + post_synth_buffer`. After scrub + gap-cut, the position where the brief was fully rendered is now adjacent to the at-top frame (capture.py's auto-trim already excised `[streaming_ended → scroll_to_top_done]`). z0b ease-out **starts at the scrubbed-time boundary where post-brief locked zone begins** — equivalently, at the at-top frame's scrubbed-time position. The viewer sees: tick montage held → all ticks complete → 1s post-synth hold (Variant B's `post_synth_buffer`) → camera retracts to reveal the at-top brief, ready for scroll-down. Brief progressively rendering is HIDDEN. The cut between buffer zone 2 and post-brief locked zone happens just before ease-out begins; the camera motion immediately after masks the content discontinuity. Sizing in scrubbed time: `z0b.duration = at_top_frame_scrubbed_t − z0b.source_t + ease_out_duration`. The at-top frame's scrubbed time is computed from the scrub report or by ffprobing the post-scrub file (= `scrubbed_duration − (raw_end_t − T_brief_landed_raw)`).

      **Default `post_synth_buffer = 1.0s`** — matches existing `margin` convention; gives viewer a beat to register "all ticks complete" before the cut + camera motion. Tunable per-video if a longer beat is needed.

      Logged: `decisions/2026-05-24-z0b-starts-on-checklist.md`, `decisions/2026-05-29-automated-post-tick-cut.md`.
    - **z1..zN** (`mode: "annotate"`): one annotate per content item the VO names during a `dwell:y` beat (see Hard Rule #24 — multi-VO-target beats split into multiple sub-annotates).

    **Tick-window compression (gap-cut rule — V1 ±margin pattern):** The dead time between ticks (and before the first tick / after the last tick, inside the locked tick window) is compressed during Phase 3 — NOT as a tail-cut post-process in Phase 5.5. The rule is per-tick margin-based:

    - For every dead segment inside the locked tick window (pre-first-tick, between-tick, post-last-tick): if the gap is **> 2 seconds**, compress by keeping **`margin` seconds adjacent to each boundary tick** (default `margin = 1.0s`). If the gap is **≤ 2 seconds**, leave it alone (natural playback at 1×).
    - **Pre-first-tick** (gap > 2s): keep `[T1 − margin, T1]` — 1s of anticipation hold before the first checkmark fires.
    - **Between-tick** (gap > 2s): keep `[T_a, T_a + margin] + [T_b − margin, T_b]` — 1s settling after the prior tick + 1s anticipation before the next tick, with jump-cut between. Total natural breathing between consecutive ticks = 2 × margin = 2s.
    - **Post-last-tick** (gap > 2s): keep `[T_(N-1), T_(N-1) + margin]` — 1s of settling hold after the last checkmark before z0b ease-out begins.
    - This is V1's actual pattern (±1s windows around each tick). The earlier "1s total between ticks" framing has been superseded — see `decisions/2026-05-24-v1-tick-spacing-pattern.md`.
    - The locked tick window in `scrub.py`'s `--force-speed-range` must extend to encompass these margins: `[T_first_tick − margin, T_(N-1) + margin]` rather than `[T_first_tick, T_(N-1)]`.
    - Implementation: `tools/detect_ticks.py` runs on the RAW recording (per Hard Rule #20), emits `ffmpeg_keep_ranges` derived from the margin rule (CLI: `--margin 1.0`). `scrub.py` locks the expanded tick window at 1× via `--force-speed-range`. A separate ffmpeg trim+concat step applies the keep-ranges to the tick-window portion, producing the tick-compressed segment. The full scrubbed file is assembled from: (pre-typing) + (typing at 1×) + (pre-tick buffer compressed by scrub.py) + (tick-window compressed by gap-cut) + (post-tick buffer compressed by scrub.py) + (brief-landed onward at 1×).
    - **z0b sizing under the ±margin rule:** ease-in must complete BEFORE T1 fires so the 1s pre-T1 hold plays inside the held portion (camera fully on sidebar before any checkmark fires). Ease-out STARTS at `T_(N-1) + margin` (after the post-last-tick settling hold completes). `z0b.duration = (T_(N-1) + margin) − z0b.source_t + ease_out_duration`.

    Skipping z0b: only with explicit user sign-off, and only for the rare case where the recording's workflow doesn't surface tool activity in any sidebar. Default = z0b runs. User-visible symptom of skipping: the loading segment reads as 10–20s of full-frame static-feeling content with no camera move — attention drifts. Logged: `decisions/2026-05-22-zoom-skeleton-standardization.md`, `decisions/2026-05-23-tick-window-compression-moves-to-phase-3.md`.

24. **Annotate highlight regions are tight bounding boxes of the *specific text the paired VO line names* — measured via `tools/measure_highlight.py`, never the section the text lives in.** Specialisation of Hard Rule #10 (measured pixel bounds) for `mode: "annotate"` highlights. Concrete contract:
    - `highlight_region_pct` height is governed by a **three-tier band** keyed off what the VO names (per `decisions/2026-05-25-highlight-three-tier-band.md`):

      | Tier | What VO names | Height | Resolution |
      |---|---|---|---|
      | 1 | Specific row / cell / phrase | ≤15% | Tight bounding box, single spotlight |
      | 2 | Conceptual unit (header + paragraph) | 15–25% | Single spotlight covering the WHOLE unit |
      | 3 | Multi-paragraph section / table block / cross-row data | >25% | SPLIT into sub-annotates with shared panel |

      The 25% threshold is the hard cap for a single spotlight. Beyond 25%, the spotlight illuminates too much of the frame, the dim becomes the minority, and the spotlight loses its "look here" function — split per Hard Rule #24's multi-sub-annotate mechanism + Hard Rule #25's shared-panel allowance.

      **Coupling with panel body length:** long-body panels (>15 words) pair with tier-1 tight spotlights (viewer's eye is on the panel; spotlight needs to be findable fast). Short-body or bare-callout panels pair with tier-2 wider spotlights (viewer has time to scan a larger illuminated area; coverage of the whole conceptual unit reads as deliberate, not vague). Mis-pairing (long panel + wide spotlight, or short panel + tight phrase-only spotlight) reads as eye-attention conflict.
    - Every annotate's `highlight_region_pct` is snapped via `python tools/measure_highlight.py "<recording>" <source_t> --rough "x,y,w,h" --debug-overlay /tmp/<vN>_hl<N>.png` before render. Hand-tuned coordinates are forbidden per Hard Rule #10 ("measured, not eyeballed" discipline).
    - **Multi-VO-target dwell beats split into multiple sub-annotates.** A `dwell:y` beat whose VO names multiple discrete content items (e.g., "Composite at 5.6 / Quality, Defensive, Tactical pinned at ten / Momentum cooled / Value at three" — naming four distinct rows) authors as four sub-annotates (z1a, z1b, z1c, z1d), one per named item, NOT one big spotlight on the whole table. The post-zoom beat duration is the sum of the sub-annotate holds; each sub-annotate has its own `callout_number` and panel (or shares panels per `video-scriptwriting/SKILL.md` Panel content authoring rules). V1's z1+z2+z3 pattern (Value row / trajectory cell / Bottom Line opening) is the canonical example.
    - Project-local: `tools/measure_highlight.py` is the calibration tool. Its `--debug-overlay` flag writes a PNG showing the rough (red) vs refined (green) rectangles; inspect before pasting. Use `--skip-x` for multi-column highlights (table rows); the default x-snap targets single-column highlights and will collapse multi-column rough rects.

    Companion to Hard Rule #10 (measured pixel bounds), Hard Rule #17 (annotate vertical centering), and Hard Rule #20 (detect_ticks) — same "measured, not eyeballed" discipline that governs every pixel-bound input to the render pipeline. Logged: `decisions/2026-05-22-zoom-skeleton-standardization.md`, `decisions/2026-05-25-highlight-three-tier-band.md`.

25. **Annotate panel-hold duration has a minimum sized to the panel's body word count.** Every annotate-mode panel must be on screen long enough for the viewer to actually read its copy. The floor:

    ```
    min_hold = max(3.0s, body_word_count / 5.0 + 2.0s)
    ```

    Where `body_word_count` = words in the panel's `body` field only (eyebrow + headline + badge + source excluded — eyebrow is glance-readable ALL-CAPS brand-locked vocab, headline is a 1-sentence hook, badge/source are 1–4-word labels; all parse in ~2s combined regardless of length). `5.0` wps = 300 wpm typical fluent silent reading. The pacing model is **viewer-driven**: the panel holds long enough to register and skim, not long enough to fully comprehend on first pass — viewers who want depth can pause; viewers who don't don't get stuck. `2.0s` = ease-in + ease-out per Hard Rule #18. `3.0s` floor = absolute minimum so even a body-less bare callout (eyebrow + headline only) has ≥1s of fully-visible readable time.

    **Sub-annotates sharing a single panel** (per Hard Rule #24's shared-panel allowance): the panel-hold is the **sum** of all constituent sub-annotate `duration` values. The minimum applies to that sum, not to each sub-annotate. This is the lever that makes sub-annotate splits readable — a 4-sub-annotate cluster at 3s each gives 12s of shared-panel hold, which fits a 50-word body (`min_hold = 50/5.0 + 2.0 = 12.0s`).

    Worked examples (300 wpm default):

    | Panel body | Body words | `min_hold` |
    |---|---|---|
    | No body — eyebrow + headline only (bare callout) | 0 | 3.0s (floor) |
    | Short body (~10 words) | 10 | 4.0s |
    | Medium body (~25 words) | 25 | 7.0s |
    | Verbose body (~40 words) | 40 | 10.0s |

    **Enforcement.** At Phase 5 (drafting), compute `min_hold` per panel from its body word count and verify `duration >= min_hold` (or sum for shared-panel clusters). At Phase 6a (post-preview), re-check against the rendered timeline — preview reveals actual hold times after cursor-clear fallback, `mpdecimate` segment cleaning, etc. If violated, choose: (a) tighten panel body (drop body, keep eyebrow + headline as a bare callout), (b) consolidate sub-annotates to a shared panel per Hard Rule #24, or (c) extend the per-sub-annotate `duration` past `min_hold` and propagate the beat-target inflation back to MASTER.md via the Phase-6a backup loop.

    **Default for sub-annotate clusters.** When a `dwell:y` beat is split into sub-annotates per Hard Rule #24, the default authoring choice is the **shared panel** — one panel pitching the cluster's conceptual unit, numbered badges per sub-annotate. Per-sub-annotate distinct panels are allowed but rare (each must satisfy `min_hold` individually, which forces tighter body copy).

    If preview reveals panels feeling rushed AND the segment is load-bearing for the watch-through narrative (not just pause-bait), drop to 240 wpm (`min_hold = max(3.0, body_word_count / 4.0 + 2.0)`) in a follow-up ADR. Companion to Hard Rule #18 (ease curve, sets the 2.0s overhead) and Hard Rule #24 (sub-annotate split + shared-panel allowance). Logged: `decisions/2026-05-25-annotate-panel-hold-minimum.md`.

26. **Post-streaming pre-scroll-up dead-time is capped to 1s as a failsafe.** When automated screen capture drives Claude desktop (via `automation/capture.py`), the window between `phases.streaming_ended` (mic icon appears, brief finished rendering) and `phases.scroll_to_top_done` (the chat-scroll-to-top transition the post-streaming dance fires) is normally excised cleanly by `capture.py`'s auto-trim. If the trim can't run (scroll dance didn't fire, `scroll_to_top_done` absent from phases, or `trim_segment` errored), this window of dead time survives into the captured recording.

    **The failsafe.** `capture.py::cap_post_streaming_deadtime()` runs ffmpeg `freezedetect` (`-45dB`, `min_dead_s=1.0`) and looks for the first freeze starting within 30s of `streaming_ended`. If one is found longer than 1s, it's clipped to 1s via ffmpeg trim+concat. The resulting file replaces `trimmed.mp4`.

    **Scope is intentionally narrow.** The rule targets ONE specific window — post-checklist-finish, pre-scroll-up — where dead time is never intentional content (the brief has rendered; the scroll dance is about to start). Pre-tick typing pauses (intentional pacing — viewer reads the question being typed), tick-window phase holds (intentional — viewer watches Cowork sidebar tick through), and post-scroll annotate dwells (Hard Rule #25 panel-hold minimum — 3s+ holds where VO interprets the highlighted row) are all OUTSIDE this 30s window from `streaming_ended` and remain untouched.

    **Applies globally** — both pipelines (news-pipeline, product-demo) consume `automation/capture.py` and benefit. Promoted from news's original "N1" rule (which was specifically scoped to this case; the now-deprecated broader implementation in `news-pipeline/tools/tick_cut.py::cap_dead_times` stays in place for news's case (b) — the trailing dead time between scroll-down completion and the Polaris outro — which is news-only).

    **No-op conditions** (failsafe doesn't fire): (i) auto-trim succeeded (`scroll_to_top_done` was marked AND `trim_segment` returned ok); (ii) `--no-readthrough` was passed (caller deliberately skipped the scroll dance — no window to cap); (iii) `interrupted=True` (recording was Ctrl+C'd, partial state); (iv) no freeze >1s found within 30s of `streaming_ended` (the typical good case — detection worked, scroll dance fired promptly, no dead time accumulated).

    Logged: `decisions/2026-05-29-post-streaming-deadtime-cap-global.md`. Companion to Hard Rule #14 (source preservation — `raw.mp4` is kept regardless of failsafe outcome) and `news-pipeline/README.md` § Rule N1 (the original news-only formulation).

27. **The at-top brief frame must be held for at least 1.0s after the scroll-up cut, before smooth-scroll-down begins.** When the automated screen capture trims `[streaming_ended → scroll_to_top_done]` (the synthetic scroll-up flicker), the viewer's first sight of the at-top brief frame is immediately followed by the post-scroll-up pause and then the scroll-down read-through. That pause is editorial — without it, the viewer doesn't have time to register "the brief is here, the prompt is at the top" before the camera starts moving down. With less than 1s, the cut into the scroll-down reads as jarring; with 1s or more, the eye lands, registers, and the scroll-down begins from a settled state.

    **Primary mechanism — capture-time hold.** `automation/capture.py` holds for `POST_SCROLL_TOP_HOLD_S = 1.0s` (since 2026-05-30) after scroll-to-top completes and before smooth-scroll-down begins. This bakes the 1s pause natively into every new recording. The `manifest.json`'s `smooth_scroll_chat_start − scroll_to_top_done` interval reflects this hold and should equal ~1.0s on captures made on/after 2026-05-30.

    **Failsafe — Phase 3 freeze-frame injection.** For recordings made BEFORE 2026-05-30 (e.g. V3 captured with `POST_SCROLL_TOP_HOLD_S = 0.5`), or any future case where the manifest indicates `natural_top_hold < 1.0s`, the Phase 3 dispatch injects a freeze frame at the at-top position to extend the pause: `freeze_s = 1.0 - natural_top_hold`. The freeze frame is generated by `ffmpeg`'s `tpad=stop_mode=clone:stop_duration=<freeze_s>` filter cloning the last frame of a 50ms slice taken at the at-top position. Result: the final scrubbed file has ≥1.0s of held at-top brief before scroll-down begins, regardless of when the recording was captured.

    **Why 1.0s.** Calibrated against human reading-comprehension: 1.0s is roughly the lower bound of "register a visual and form an expectation" (the same floor used in Hard Rule #25's panel-hold minimum). Less than 1s feels cut-into; 1s feels settled-then-revealed; >2s feels like dead time before the read-through. 1.0s is the floor, not a target — captures may have more if the recording's natural pause exceeds 1s.

    **Scope.** Applies to automated captures with the readthrough scroll dance (both pipelines: news + product-demo via `automation/capture.py`). Does NOT apply to `--no-readthrough` captures (no scroll dance happens; no top-hold to enforce) or to manual recordings (the human controls pacing during recording). Failsafe checks for `manifest.json` + `phases.smooth_scroll_chat_start` + `phases.scroll_to_top_done` presence; absent → skip.

    **No-op conditions.** Failsafe doesn't inject if: (i) no manifest (manual recording), (ii) `smooth_scroll_chat_start` or `scroll_to_top_done` absent from phases (scroll dance didn't fire), (iii) `natural_top_hold ≥ 1.0s` already (capture.py's default does this for post-2026-05-30 recordings).

    Logged: `decisions/2026-05-30-minimum-top-hold.md`. Companion to Hard Rule #23 Variant B (the cut whose post-conditions this rule enforces) and Hard Rule #26 (the other Phase 3 failsafe — they're siblings, both shoring up automated-capture artifacts).

## Notes (smaller things worth knowing)

- **Anchor preservation when cutting long freezes.** When scrubbing a freeze long enough to cut the middle entirely, keep a few seconds at the front and back at fast-forward speed. This preserves the "loading begins / result lands" transition so the cut reads as real, not janky. Specific anchor seconds are project-tuned (depends on the recording's pacing aesthetics) — the rule is just that *some* anchor exists.
- **Eyeball the scrubbed recording before Phase 5.** After Phase 3, play the scrubbed output start to finish: are all beats visible, do transitions feel right, any scrubbing artifacts? Catching a bad scrub here is an order of magnitude cheaper than catching it after the script is written. Don't expect this output to match the beat sheet's total target — dwell:y beats will be short by exactly the planned zoom-insert amount; that's correct.
- **Re-extract frames after re-scrubbing.** Frame audit timestamps map to whatever scrubbed recording was used at the time. If you re-run Phase 3 (different threshold, different hold choices), re-run Phase 4 — old frame timestamps no longer point at the right content. (Re-running Phase 5.5 zoom doesn't require re-extracting frames, since zoom doesn't change content — only emphasis.)
- **Dwell:y means VO *can* dwell, not must.** The beat's locked seconds are still authoritative. Dwell:y just means the visual won't fight you if the VO uses more time than the underlying motion took.
- **Project-tuned values stay project-local.** Scrub thresholds, anchor seconds, font choices, frame-rate, render-template invariants — none of these belong in a portable methodology skill. They live in the project's tools, CLAUDE.md, or render-template guide.

## When the recording can't be conformed

Sometimes Phase 3 reveals that the raw recording can't be scrubbed down to the beat sheet's per-beat targets (non-dwell beats too short, motion content too dense to compress within 1.5–2×) — or Phase 5.5 reveals that a dwell:y beat has no settled visual to zoom into. Two options:

- **Re-record the failing beat.** Cheaper than shipping misaligned video. The cost of a 5-minute re-record is dwarfed by the cost of stretched motion or compressed VO.
- **Re-open the beat sheet.** If the recording's actual runtime is fundamentally different from what was planned (a feature was faster than expected, a workflow had more dead time than anticipated), update Phase 1 and propagate. This is rare and should be flagged to the user, not done silently.

What you do *not* do: silently compress the script to absorb a recording mismatch. That's the ouroboros this skill exists to break.

## How this skill composes with other skills

This skill owns *order and methodology*. It does not own:

- **Script craft** — voice composition, banned words, AI-tell avoidance, "show on screen / interpret in VO," sentence rhythm. Consult a craft skill (e.g., `video-scriptwriting`) at Phase 5.
- **Render mechanics** — Hyperframes / FFmpeg / HeyGen / your renderer of choice. Consult that tool's skill or docs at Phase 6.
- **Project-specific glue** — what file paths your project uses, what your beat sheet lives in, which scrub thresholds work for your recording style. That belongs in a project-local orchestrator skill (e.g., a `<project>-video` skill) that knows how to invoke this methodology against your specific tools and content.

The pattern: install this skill + a craft skill, write a thin project orchestrator, build the deterministic mechanics as code in `tools/`. Skill for judgment, code for mechanics, project orchestrator wires them together.

## Example: applying the workflow to a screen-recording-driven product demo

Concrete walk-through, with placeholder values. The project happens to be a Parallax product demo, but the steps generalize.

1. **Phase 1.** Read the project's plan for video V<N>. Locked beat sheet:
   ```
   - 0:00–0:05  Title card                          (5s)
   - 0:05–0:16  Prompt + parallel calls fan out     (11s)
   - 0:16–0:28  Why this isn't trivial              (12s)
   - 0:28–0:38  Vault stat (ICIR 4.10)              (10s)
   - 0:38–0:54  Score panel + trajectory setup      (16s, dwell:y from 0:48)
   - 0:54–1:08  Trajectory + bottom line            (14s, dwell:y full)
   - 1:08–1:16  Outro                               (8s)
   Recording portion target: 66s
   ```

2. **Phase 2.** Screen-record the workflow. Raw recording lands at 150s.

3. **Phase 3 (scrub only).** Run scrub at the project's tuned threshold. Output: 46s. Look beat-by-beat:
   - First five beats sum to 53s in raw, scrub down to 40s. Fine — within tolerance.
   - Beat 5 ("score panel") is dwell:y and the dwell window is short by ~4s. Note as a Phase 5.5 zoom candidate; do not extend in Phase 3.
   - Beat 6 ("trajectory + bottom line") is dwell:y full and is short by ~6s. Same — note as zoom candidate.
   - Scrubbed recording total = 46s. The 20s gap from the 66s recording target is the planned zoom-insert budget (within ±0.5s sanity tolerance for the two dwell:y beats).

4. **Phase 4.** Extract frames from the 46s scrubbed recording. Audit content: every beat's content is present.

5. **Phase 5.** Write the script to the locked beat windows (script VO sized to the *post-zoom* 66s total, not the 46s scrubbed). Identify zoom targets for the two dwell:y beats — the specific subject the VO names (e.g., "BUY rating from 14 analysts," "ICIR 4.10 cell"). Caption/LT schedules drop into beat-internal slots. Hallucination check against the frame audit.

6. **Phase 5.5.** Measure the precise pixel bounds for each zoom target, apply the two zooms (6s on beat 5, 4s on beat 6) via the project's zoom tool. Output: 56s zoomed recording. Re-derive LT/caption timings against this file (Hard Rule #12).

7. **Phase 6.** Render preview (free) against the zoomed recording. Iterate.

8. **Phases 6a → 6b → 6c.** Polish converges (rhythm + sync); the chain auto-fires lint (mechanical Hard-Rule check) and then the LLM reviewer (semantic + vision-grounded). Lint gates the reviewer — error-tier findings stop the chain; tier-2 warnings carry through to the reviewer's report. Surface both reports; iterate Phase 5 / 5.5 / 6 based on findings.

9. **Phase 9.** Render final (billed once). The 6a → 6b → 6c chain reattaches to the final artifact — the same rule checks apply to ship gates that applied to preview iterations.

The recording, the script, and the graphics all converged on the same canonical timeline because Phase 1 owned that timeline upstream of all of them, and Phase 5.5 zoom was sized from the beat sheet (Hard Rule #9) while targeted from the script (Hard Rule #5). The 6a → 6b → 6c convergence verifies both internal consistency (polish) and external Hard-Rule conformance (lint + review) without re-coupling those concerns.

## Anti-patterns

Recognizable shapes that mean the workflow has broken:

- **"Let me re-time the captions to match the recording."** Captions and LTs schedule into beat windows, not recording timestamps. If the recording shifted, the scrub (Phase 3) or zoom (Phase 5.5) wasn't conformed properly — fix the upstream phase, not the captions. After every Phase 5.5 zoom rerun, re-derive LT/caption timings against the new zoomed recording (Hard Rule #12).
- **"Let me pick the zoom regions while I'm scrubbing the recording."** Zoom region = what the VO names. The VO doesn't exist at Phase 3. Move the zoom-region decision to Phase 5.5 where the script is in hand; Phase 3 is scrub-only.
- **"The script is 30 words too long, let me clip a few sentences."** Word-count compression within beats is the wrong lever. Either the beat sheet allocated too few seconds (re-open Phase 1) or you have one beat too many for this video (cut a whole beat).
- **"The recording's a bit short, the VO will just speed up."** The TTS doesn't speed up gracefully and the viewer notices. Hold a settled frame, insert a script-driven pause-zoom on a dwell:y beat, or re-record. (Slowing the recording is not an option — see Hard Rule #13.)
- **"We'll figure out the beat sheet after the recording."** This is the ouroboros. There is no version of this workflow where Phase 1 happens after Phase 2.
