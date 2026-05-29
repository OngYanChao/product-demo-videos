# 2026-05-29 — Automated post-tick cut: hide brief-loading + scroll-up segments via Phase 3 pre-cut + late z0b retract

**Scope:** Product-demo pipeline, automated capture flow only (recordings produced by `automation/capture.py` with `manifest.json` alongside). Manual screen recordings keep the existing Hard Rule #23 behavior.

**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #23 split into Variant A — manual + Variant B — automated), `.claude/skills/parallax-video/SKILL.md` (Phase 3 dispatch step 6 + Phase 5 z0b sizing dispatch both gain a manual/automated conditional).

## Decision

Two-pipeline divergence for the post-tick segment treatment:

**Variant A — Manual recording** (canonical V1–V16 today; human records via OS screen capture, no manifest): Hard Rule #23's existing behavior. The brief-progressively-loading segment between `T_(N-1)` (penultimate tick) and `T_brief_landed` IS content — the camera retracts (z0b ease-out) starting at `T_(N-1) + margin` so the viewer watches the brief render in the chat area as the camera moves to full frame. `T_N` (synthesis tick) fires during the ease-out, completing the sidebar checklist at the moment the brief becomes fully visible. Production value: shows Cowork "working."

**Variant B — Automated capture** (recording produced by `automation/capture.py`): the brief-progressively-loading segment IS filler, not content. Two reasons it diverges from manual:

1. Automated capture has a deterministic recording-quality contract (driven by manifest phases), so we can trim with precision. Manual recordings vary.
2. Automated capture has the synthetic scroll-up flicker that capture.py already auto-trims `[streaming_ended → scroll_to_top_done]`. The brief-loading segment is the OTHER undesirable artifact in that region. Trimming both produces a cleaner shipped video.

Phase 3 adds a pre-scrub ffmpeg trim+concat that excises `[T_N + post_synth_buffer, T_brief_landed]` (default `post_synth_buffer = 1.0s`). After this cut + capture.py's existing auto-trim, the post-penultimate region in the trimmed file runs `[T_(N-1), T_N + 1.0s]` then jumps directly to the at-top brief frame. z0b ease-out starts at the at-top frame's scrubbed-time boundary and retracts to reveal it. Viewer sees: tick montage held → all ticks complete → 1s post-synth hold → camera retracts to reveal at-top brief, ready for scroll-down.

The cut between buffer zone 2 and post-brief locked zone happens just before ease-out begins. The camera motion immediately after the cut masks the content discontinuity — viewer perceives "camera retracted and at-top appeared," not a jarring jump.

## Implementation choice (Option A vs Option B)

User chose **Option A — pre-trim** over **Option B — true mid-zoom-out cut**:

- Option A: Phase 3 pre-cuts `[T_N + 1.0s, T_brief_landed]` from raw, scrub.py operates on the shortened input, z0b ease-out plays over the at-top frame. **No zoom.py changes.** Implementation cost: ~30 lines in the orchestrator (Phase 3 dispatch); ffmpeg trim+concat is a single invocation. Cut happens BEFORE the ease-out's first frame (visually masked by zero static hold between cut and motion-onset).

- Option B: zoom.py extended to support source-time discontinuity within a single ease-out segment. Cut happens DURING the ease-out animation, masked by camera motion. Implementation cost: ~100-150 lines + new failure modes.

Both achieve the same visual end-state. Option A is shipped first because the visual masking is similar enough; Option B remains available as a future refinement if side-by-side comparison shows Option A's cut-before-motion reads as less smooth.

## `post_synth_buffer = 1.0s` default

Hold zoom on sidebar for 1.0s AFTER the synthesis tick fires, before the cut + ease-out. Tradeoffs:

| Buffer | Effect |
|---|---|
| 0s | Instant cut at T_N — feels rushed |
| 0.3-0.5s | Brief beat (subtle) |
| **1.0s** | **Matches existing `margin` convention; viewer registers "all ticks complete" before content + motion changes** |

User chose 1.0s. Tunable per-video if needed.

## Detection logic

"Is this automated?" — checked via `manifest.json` presence alongside `vid<N>.mp4` AND `phases.scroll_to_top_done` set in the manifest. This is implicit but reliable:

- Manual recordings: no manifest (no detection needed — Variant A applies)
- Automated capture with readthrough on: manifest present with `phases.scroll_to_top_done` (Variant B applies)
- Automated capture with `--no-readthrough` (hypothetical edge case — current product-demo dispatch doesn't pass this): manifest present BUT no `phases.scroll_to_top_done`. Treat as Variant A (no scroll dance happened, so the trim that produces the at-top frame didn't happen either).

The two-key check (manifest present + `scroll_to_top_done` present) avoids false positives.

## Why a rule, not just code

Two reasons:

1. **Cross-rule consistency.** Hard Rule #23 is the central document for the z0b skeleton. Splitting into Variant A/B at the rule level keeps the divergence visible — future maintainers searching for z0b sizing find both variants in one place.

2. **The Phase 3 pre-cut creates a non-obvious dependency** on the Phase 5 z0b sizing computation. The cut shrinks buffer zone 2 in scrubbed time AND moves the at-top frame to a new scrubbed-t position. Without documentation, a future Phase 3 modification that changed the cut (e.g., tightened `post_synth_buffer`) could silently break z0b ease-out positioning. The rule makes the coupling explicit.

## No tool changes

All changes are in the orchestrator (skill dispatch) — the LLM at runtime computes T_N from the broad detect_ticks pass, builds the ffmpeg trim+concat command, derives the new `T_brief_landed_effective`, and adjusts z0b's duration. `tools/scrub.py`, `automation/capture.py`, and `tools/zoom.py` are unchanged.

## User context

> "for manual screen recordings we send, we will have to zoom out before the last tick, which is usually 'synthesising brief', to watch the brief load. this should be outlined somewhere as a hard rule or code. but, for automated prompts and screen recording workflow, i want to zoom out AFTER the last tick, doing a cut during the zoom out to land right on the frame where we have already done the scroll up, right before the scroll down, skipping the whole scroll up segment and hiding the brief loading segment entirely. can we do this"

The user articulated the manual-vs-automated divergence cleanly. The "cut during the zoom out" framing pointed to Option B's literal interpretation; the analysis surfaced that Option A achieves the same visual outcome with much lower implementation cost. User chose Option A after the tradeoff was laid out.

## Cross-references

- Original Hard Rule #23 + z0b skeleton: `decisions/2026-05-22-zoom-skeleton-standardization.md`
- z0b ease-in timing refinement: `decisions/2026-05-24-z0b-starts-on-checklist.md`
- Tick-window compression in Phase 3: `decisions/2026-05-23-tick-window-compression-moves-to-phase-3.md`
- Capture.py auto-trim (the other half of the "hide artifacts" picture — excises scroll-up flicker): `automation/capture.py::main()` trim block + Hard Rule #26 failsafe
- N1 promotion (global Hard Rule #26 — companion safety net): `decisions/2026-05-29-post-streaming-deadtime-cap-global.md`
- N2 → Hard Rule #21 zone (a) adaptive (companion product-demo refinement same day): `decisions/2026-05-29-product-demo-adaptive-typing-speedup.md`
- Pass 1 + 2 architecture extraction: branch `extract-automation-layer`
