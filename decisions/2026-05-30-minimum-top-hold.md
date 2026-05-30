# 2026-05-30 — Minimum 2.0s top-hold pause before scroll-down + scroll-to-prompt visibility (Hard Rule #27)

**Refinement note:** This rule went through THREE same-day iterations. **Morning:** initial proposal at 1.0s minimum top-hold with capture-time + freeze-frame failsafe mechanisms. **Afternoon (first attempt after V3 visual review):** two issues surfaced — (1) the at-top frame didn't show the prompt at the top of the chat (scroll-to-top was stopping at the top of the *response* with the prompt off-screen above), and (2) even at 1.0s, the pause felt rushed for a frame that needs to register *both* the prompt and the brief together. Refinements: duration floor raised to 2.0s; `automation/capture.py::scroll_chat_to_top()` raised from 80 to 200 events × 10 lines.

**Afternoon (second attempt — redo from raw):** the V3 redo from raw correctly captured the prompt-visible at-top frame and held it for 2s, but introduced a NEW issue: the post-freeze v2 segment was set to start at `raw[68.154]` (`smooth_scroll_chat_start`), skipping `raw[67.050, 68.154]`. This created a jump cut where the frozen prompt-visible frame transitioned directly to mid-scroll-down content. User feedback: *"After the freeze frame at the top, there's a sudden cut where it's already halfway scrolling down. What the hell is this? Just continue the clip of the scroll down from the freeze frame."* Diagnosis: the failsafe ffmpeg template's v2 segment must use `trim=start=<T_at_top>` (the same source position the freeze slice began), NOT a later timestamp. Surface symptom: jump cut from freeze to mid-content. Cause: synthetic discontinuity between freeze and post-freeze content. Fix: ensure v2 plays the source forward from `T_at_top` so the freeze "comes alive" into the natural recording — through the post-scroll snap animation, settle, and scroll-down all in original recorded sequence.

**Encoded as Hard Rule #27 (c)** — natural continuation from freeze into scroll-down, no jump cuts. The dispatch step 6b.5's ffmpeg template was rewritten to make this explicit (canonical filter chain shown with critical note), and step 6a gained a redo-from-raw subvariant for when the auto-trim's at-top frame doesn't satisfy Rule #27 (b).

**Scope:** Both pipelines, automated capture only (manual recordings handled at recording time by the human).

**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #27 — THREE requirements: (a) ≥2.0s hold + (b) prompt visible in at-top frame + (c) natural continuation from freeze, no jump cuts), `automation/capture.py` (`POST_SCROLL_TOP_HOLD_S` bumped from `0.5s` to `2.0s`; `scroll_chat_to_top()` raised from 80 to 200 scroll events per target), `.claude/skills/parallax-video/SKILL.md` (Phase 3 dispatch step 6a — redo-from-raw subvariant for the V3-style case where auto-trim's at-top frame lacks the prompt; step 6b.5 — freeze-frame failsafe with canonical ffmpeg template enforcing natural continuation via `trim=start=<T_at_top>` for the v2 segment).

## Decision

Two load-bearing requirements:

**(a) Hold duration ≥ 2.0s.** The at-top frame — first visible after the scroll-up flicker is auto-trimmed — must be held for at least 2.0s before smooth-scroll-down begins. Calibrated against a *two-element* visual (prompt + brief-title together), not the single-element visual that 1.0s would suffice for.

**(b) The at-top frame must show the prompt at the top of the chat.** `scroll_chat_to_top()` must reach the very top of the chat container so the user's first message (the prompt) is at the top of the captured frame, with the brief below it.

## User observations

**First (morning):**
> "Do you see in V3 Scrub how after the output brief is finished loading there's a cut and then we cut into the output brief already scrolling down. Can I have a minimum one second pause at the top of the brief, So what I want for you to do is to have a 1 second pause freeze frame if you have to at the very top of the brief after we do the scroll up... we still want to keep one second minimum one second of pause time at the very top where you see the prompt and you see the brief in the chat before we start the scroll down"

**Second (afternoon, after seeing V3 regenerated at 1.0s):**
> "It's not fully at the top, you are missing out on the prompt at the very top of the chat. Also can we extend the hold to 2 seconds? Add this under the hard rule"

The V3 1.0s output revealed two related issues: scroll didn't go high enough (prompt off-screen) AND 1.0s wasn't enough hold for the intended dual-element register. Both got addressed.

## Why 2.0s (not 1.0s)

The 2.0s floor is calibrated against a *two-element* visual (prompt + brief-title together), not a single-element visual. The at-top frame after the scroll-up cut requires the viewer to:

1. **Read the prompt** — the persona's question in customer's-chair voice. (~0.7-1.0s)
2. **Shift gaze to the brief** below and register "the response is here." (~0.5-0.8s)
3. **Form expectation** before the scroll-down camera moves. (~0.2-0.5s)

Total: ~1.5-2.3s of comprehension work for a two-element scan. 2.0s sits in the middle.

- <1s feels cut-into (the original V3 condition that surfaced this rule)
- 1.0s works if you're only looking at the brief, but rushed if you're meant to read the prompt too
- 2.0s feels settled-then-revealed — the eye traces prompt → brief and the scroll-down begins from a registered state
- \>3s starts feeling like dead time before the read-through

2.0s is the floor, not a target — natural top-hold can exceed 2s without issue.

## Why requirement (b): scroll all the way to the top

The scroll-to-top function originally used 80 events × 10 lines = 800 lines of scroll per target. This worked for short briefs but for moderately long responses (V3 case — JPM peer snapshot with table + bullet points + several paragraphs of key takeaways), 800 lines wasn't enough to scroll past the response and reach the prompt above it. The at-top frame ended up showing the response title at the top, with the user's prompt still off-screen above.

Bumped to 200 events × 10 lines = 2000 lines. At ~16-20px per line, that's ~32,000-40,000px of scroll-up — well past any conceivable response length. Excess events become no-ops once the chat hits its absolute top, so over-providing is safe.

**Requirement (b) is not retrofitted by the Phase 3 freeze-frame failsafe** — if the recording didn't scroll high enough at capture time, freezing whatever frame WAS at the at-top moment still won't include the prompt. The fix has to happen at capture time. This means pre-2026-05-30 recordings (like V3) still won't have the prompt visible even after the failsafe extends the hold to 2.0s; they need re-capture for full Rule #27 conformance.

## Implementation (three mechanisms)

**Primary 1: scroll all the way to the top.** `automation/capture.py::scroll_chat_to_top()` raised from 80 to 200 scroll events per target. Ensures the chat container is fully scrolled past the response to the prompt at the top.

**Primary 2: capture-time hold raised to 2.0s.** `automation/capture.py::POST_SCROLL_TOP_HOLD_S = 2.0` (was 0.5; briefly 1.0 same-day). New captures bake the 2s pause natively. `manifest.phases.smooth_scroll_chat_start − scroll_to_top_done` will equal ~2.0s on captures from 2026-05-30 onward.

**Failsafe: Phase 3 freeze-frame injection.** For recordings made before these constant bumps (V3 has 0.5s baked in already), or any future case where `manifest.smooth_scroll_chat_start - scroll_to_top_done < 2.0s`, the Phase 3 dispatch's step 6b.5 injects a freeze frame after the gap-cut and before scrub. Mechanism: extract a 50ms slice at the at-top position, pad it via ffmpeg `tpad=stop_mode=clone:stop_duration=<freeze_s>` where `freeze_s = 2.0 - natural_top_hold`, splice into the gap-cut file at position `T_brief_landed_effective_gapcut`. Result: ≥2.0s held at-top regardless of recording age. **Limitation:** failsafe extends the *duration* but cannot fix the scroll-position — if the original recording's at-top frame didn't show the prompt, the failsafe-extended frame still won't.

## Why both mechanisms (1.0 → 2.0 didn't change this)

**Primary alone (capture-time bump)** leaves existing recordings broken — V3 already has 0.5s baked in; would need re-capture to fix. Re-capturing isn't always free (real Cowork API call, manual setup, time).

**Failsafe alone (Phase 3 injection)** means every capture does extra work when the underlying recording could just produce the right pause natively. Wasteful for the 99% case.

**Together:** new captures get the 2s pause cheaply (native); old captures get retrofitted via failsafe (duration only — scroll position can't be fixed retroactively).

## Scope (unchanged from initial proposal)

Applies to **automated captures with the readthrough scroll dance**: both pipelines (news + product-demo) since both invoke `automation/capture.py` with default flags (scroll dance on).

Does NOT apply to:
- `--no-readthrough` captures: no scroll dance happened, no top-hold to enforce
- Manual recordings: no `manifest.json`, human controls pacing during recording
- Recordings where `scroll_to_top_done` or `smooth_scroll_chat_start` are missing from phases: scroll dance didn't fire cleanly, separate problem

## Implementation note — `tpad=stop_mode=clone`

ffmpeg's `tpad` filter pads a stream by cloning the last input frame. Used here to take a 50ms slice of the at-top moment and extend it by `freeze_s` seconds. Alternative approaches considered:
- Extract a single frame via `-frames:v 1` and loop via `-stream_loop`: works but requires a separate file
- Use `setpts` to slow down a slice: distorts the frame's encoding semantics
- `tpad` with `stop_mode=clone`: cleanest, single-filter solution within the existing trim+concat graph

The 50ms slice (rather than a single frame) avoids precision issues with frame-accurate seeking; the clone padding extends from there.

## Cross-references

- Hard Rule #23 Variant B (the cut whose post-conditions Rule #27 enforces): `decisions/2026-05-29-automated-post-tick-cut.md`
- Hard Rule #26 (sibling failsafe — post-streaming dead-time cap, same architecture pattern): `decisions/2026-05-29-post-streaming-deadtime-cap-global.md`
- Hard Rule #25 (companion pause-floor rule): `decisions/2026-05-25-annotate-panel-hold-minimum.md`
- V3 capture context (the canary that surfaced this): `screen recordings/V3/manifest.json` (2026-05-29 capture with 0.5s baked in)
