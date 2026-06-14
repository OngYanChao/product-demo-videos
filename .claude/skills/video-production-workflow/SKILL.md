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

## Hard rules — phase + pipeline routing

The Hard Rules live in per-phase, per-pipeline files under `rules/`. **At the start of each phase, load only the relevant rules file** — don't try to hold all 30 rules in context at once. Each phase file is short and self-contained.

### Routing table

| Phase | Pipeline | Rules file | Rules in scope |
|---|---|---|---|
| **Any phase** | Both | `rules/meta.md` | #14 (source preservation), #15 (60fps + 1s keyframes) |
| **Phase 1** — Lock beats | Both | `rules/phase-1.md` | #1, #3, #5 |
| **Phase 2** — Capture | Both | `rules/phase-2.md` | #14, #15, #26 |
| **Phase 3** — Scrub / conform | Product-demo | `rules/phase-3-product-demo.md` | #2, #4, #13, #20, #21, #23 (Variant A/B), #27, #28, #29, #30 |
| **Phase 3** — Scrub / conform | News | `rules/phase-3-news.md` | #20, N2, #23 (news variant), #27, #29, #30 |
| **Phase 5** — Script | Product-demo | `rules/phase-5.md` | #6, #7 |
| **Phase 5** — Script | News | (no script phase) | — |
| **Phase 5.5** — Apply zoom | Product-demo | `rules/phase-5-5-product-demo.md` | #9, #10, #11, #12, #16, #17, #18, #19, #22, #23, #24, #25, #28, #29 |
| **Phase 5.5** — Apply zoom | News | `rules/phase-5-5-news.md` | #11, #12, #23, #29 |
| **Phase 6 / 6a / 6b / 6c / 9** — Render + polish + lint + review | Both | `rules/phase-6.md` | #6 (Phase 6a parts), #8, #12 |

**How to use:** when the orchestrator dispatches a phase, it names the rules file in its dispatch row. Load that one file (plus `meta.md`). Do not load the other rule files — they don't apply to the current phase and would just bloat context.

### Rule catalog (one-line summaries)

| # | Title | Lives in |
|---|---|---|
| 1 | Beat sheet is upstream | `phase-1.md` |
| 2 | Conform recording, don't compress script | `phase-3-product-demo.md` |
| 3 | LTs schedule into beat windows, not recording timestamps | `phase-1.md` |
| 4 | Recording must visibly contain each beat's claimed content | `phase-3-product-demo.md` |
| 5 | Dwell-eligibility is a beat-sheet property | `phase-1.md` |
| 6 | Cut whole beats, never word-by-word — phase-aware | `phase-5.md`, `phase-6.md` |
| 7 | Every on-screen claim cites a frame (hallucination check) | `phase-5.md` |
| 8 | Preview is free, final is billed | `phase-6.md` |
| 9 | Pause-zoom sized by beat sheet, never by runtime deficit | `phase-5-5-product-demo.md` |
| 10 | Pixel-bound zoom inputs measured, never eyeballed | `phase-5-5-product-demo.md` |
| 11 | Freeze-frame + zoom segments stay in source colour space | `phase-5-5-product-demo.md`, `phase-5-5-news.md` |
| 12 | Zoomed recording is canonical timeline — re-derive after every re-zoom/re-scrub | `phase-5-5-product-demo.md`, `phase-5-5-news.md`, `phase-6.md` |
| 13 | Never slow down source playback | `phase-3-product-demo.md` |
| 14 | Source preserved until explicit approval (cleanup gate) | `meta.md` |
| 15 | 60fps + 1s keyframes end-to-end | `meta.md` |
| 16 | Hold/annotate zooms don't trigger while cursor is on readable text | `phase-5-5-product-demo.md` |
| 17 | Annotate spotlights land within comp y=30%-70% safe zone | `phase-5-5-product-demo.md` |
| 18 | Overlay animations share camera's ease curve | `phase-5-5-product-demo.md` |
| 19 | Source segments between annotates cleaned of duplicate frames | `phase-5-5-product-demo.md` |
| 20 | Tick timestamps detected programmatically (not eyeballed) | `phase-3-product-demo.md`, `phase-3-news.md` |
| 21 | Multi-zone 1× lock (typing / tick window / brief-landed) | `phase-3-product-demo.md` |
| 22 | z0 ease-out STARTS at T_click (not completes) | `phase-5-5-product-demo.md` |
| 23 | Standard skeleton z0 + z0b + z1..zN; Variant A/B selection at Phase 3 | `phase-5-5-product-demo.md`, `phase-3-*.md` |
| 24 | Annotate highlights measured; multi-VO-target beats split into sub-annotates | `phase-5-5-product-demo.md` |
| 25 | Panel-hold minimum sized to body word count | `phase-5-5-product-demo.md` |
| 26 | Post-streaming dead-time capped to 1s (failsafe) | `phase-2.md` |
| 27 | At-top frame held ≥2s + prompt visible + natural continuation | `phase-3-product-demo.md`, `phase-3-news.md` |
| 28 | z0.ease=1.5s standard + scrubbed buffer 1 ≥2.5s | `phase-3-product-demo.md`, `phase-5-5-product-demo.md` |
| 29 | z0b ease-out over still frame + raw-tail stitch (auto-rebuild) | `phase-3-product-demo.md`, `phase-3-news.md` |
| 30 | Static-placeholder gateway: skip z0b + 3s loading flash when no ticks | `phase-3-product-demo.md`, `phase-3-news.md` |
| 31 | z0 → z0b transitions continuously (no full-frame gap; sidebar is the loading focus) | `phase-3-news.md`, `phase-5-5-product-demo.md` |

Rule #22 also has a news-specific mechanism (see `phase-3-news.md`) — `news-pipeline/tools/process.py::_rule_22_override_auto_zooms()` rewrites `tick_cut.py`'s auto-emit to enforce `z0.duration = typing_end_scrubbed + ease`. Catalog row above shows the canonical product-demo location.

### News-pipeline-only rules

| # | Title | Lives in |
|---|---|---|
| N2 | Prompt-typing window is always 2× speedup-OK, never cut | `phase-3-news.md` |
| N3 | Buffer-1 compression: typing-end-to-first-tick gap compressed to 4.0s | `phase-3-news.md` |

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
