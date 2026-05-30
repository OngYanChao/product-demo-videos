# 2026-05-30 — Minimum 1.0s top-hold pause before scroll-down (Hard Rule #27)

**Scope:** Both pipelines, automated capture only (manual recordings handled at recording time by the human).

**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (new Hard Rule #27), `automation/capture.py` (`POST_SCROLL_TOP_HOLD_S` bumped from `0.5s` to `1.0s`), `.claude/skills/parallax-video/SKILL.md` (Phase 3 dispatch gains step 6b.5 — freeze-frame failsafe).

## Decision

The at-top brief frame — first visible after the scroll-up flicker is auto-trimmed — must be held for at least 1.0s before smooth-scroll-down begins. Editorial reason: viewer needs time to register "the brief is at its top, prompt visible, ready to read" before the camera starts moving down. Less than 1s reads as a jarring cut into mid-scroll; 1s or more lets the eye land and form expectation; the scroll-down then begins from a settled state.

## User observation (verbatim)

> "Do you see in V3 Scrub how after the output brief is finished loading there's a cut and then we cut into the output brief already scrolling down. Can I have a minimum one second pause at the top of the brief, So what I want for you to do is to have a 1 second pause freeze frame if you have to at the very top of the brief after we do the scroll up. so we do after the segment is downloading we do a cut to cut out the scroll up animation but we still want to keep one second minimum one second of pause time at the very top where you see the prompt and you see the brief in the chat before we start the scroll down"

The V3 test run surfaced this — V3 was captured 2026-05-29 with `POST_SCROLL_TOP_HOLD_S = 0.5s`, so after the auto-trim of the scroll-up dance, only 0.5s remained between scroll-to-top-done and smooth-scroll-chat-start. The viewer perceived this as cut-into-mid-scroll.

## Implementation (two mechanisms — primary + failsafe)

**Primary: capture-time hold raised to 1.0s.** `automation/capture.py::POST_SCROLL_TOP_HOLD_S = 1.0` (was 0.5). All new captures bake the 1s pause natively. `manifest.phases.smooth_scroll_chat_start − scroll_to_top_done` will equal ~1.0s on captures from 2026-05-30 onward.

**Failsafe: Phase 3 freeze-frame injection.** For recordings made before this constant bump (V3 has the 0.5s baked in already), or any future case where the manifest indicates `natural_top_hold < 1.0s`, the Phase 3 dispatch's new step 6b.5 injects a freeze frame after the gap-cut and before scrub. Mechanism: extract the at-top frame, generate `freeze_s = 1.0 - natural_top_hold` of cloned-frame content via ffmpeg's `tpad=stop_mode=clone:stop_duration=<freeze_s>` filter, splice it into the gap-cut file at position `T_brief_landed_effective_gapcut`. Result: ≥1.0s held at-top regardless of when the recording was captured.

## Why 1.0s

Calibrated against the same reading-comprehension floor used in Hard Rule #25 (panel-hold minimum). Lower bound for "register a visual and form an expectation":
- <1s feels cut-into (the original V3 condition the user objected to)
- 1.0s feels settled-then-revealed
- \>2s starts feeling like dead time before the read-through

1.0s is the floor, not a target — natural top-hold can exceed 1s without issue. The bump from 0.5 to 1.0 in capture.py is just enough to clear the floor with no slack.

## Why both mechanisms

**Primary alone (capture-time bump)** would leave existing recordings broken — V3 already has 0.5s baked in; would need re-capture to fix. Re-capturing isn't always free (real Cowork API call, manual setup, time).

**Failsafe alone (Phase 3 injection)** would mean every capture does extra work (freeze-frame ffmpeg call) when the underlying recording could just produce the right pause natively. Wasteful for the 99% case.

**Together:** new captures get the 1s pause cheaply (native); old captures get retrofitted via failsafe. Both safety nets reinforce each other — if `POST_SCROLL_TOP_HOLD_S` ever drifts back to <1s (bug, accidental edit), Phase 3 catches it.

## Scope

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
- Hard Rule #25 (companion pause-floor rule, also 1.0s-anchored): `decisions/2026-05-25-annotate-panel-hold-minimum.md`
- V3 capture context (the canary that surfaced this): `screen recordings/V3/manifest.json` (2026-05-29 capture with 0.5s baked in)
