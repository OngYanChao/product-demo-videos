# 2026-05-20 — Clean Source Segments Between Annotates by Default

**Status:** active
**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #19 added), `.claude/skills/parallax-video/SKILL.md` (zoom V<N> dispatch row updated to default-pass `--clean-source-ranges`), `tools/zoom.py` (no code change — flag already supported)

## Decision

Every Phase 5.5 zoom run in this project passes `--clean-source-ranges` covering every source segment between annotate holds. zoom.py runs `mpdecimate` on those segments, dropping consecutive duplicate frames. The orchestrator's "zoom V<N>" dispatch derives the range string from the annotate directives' source_t values: for annotates at source_t = a, b, c with prior cursor d, the dispatch passes `"d:a,a:b,b:c"`.

## Why

V1.2's scrubbed recording had a 0.8s frozen-frame region at `scrubbed_t = 50.55–51.35` — too short for `tools/scrub.py`'s default `min_dead_seconds = 5.0` to catch, but long enough to read as a noticeable "lag" in the mid-scroll motion between z1's ease-out and z2's ease-in. User feedback: *"right before the second zoom and panel, there is some janky stuff going on with the scroll down, it lags."*

The freeze survived scrubbing because it's below the project's freeze-detection threshold. Lowering `min_dead_seconds` project-wide would over-cut natural pauses elsewhere. The targeted fix is `mpdecimate`, which operates at the encoder level on individual segments — only consecutive byte-identical (or near-identical) frames get dropped, so natural-motion frames are preserved.

`tools/zoom.py` already supports `--clean-source-ranges` as a per-segment opt-in; the rule promotes it from "opt-in for problem cases" to "default on for every annotate-having video." The cost is near-zero (mpdecimate is fast; no quality impact on natural motion); the benefit is removing a class of perceptible jank that would otherwise require manual freeze-hunting per video.

## Notes

- Detection (when authoring): sample frames at 0.25s intervals across each `seg_src_NN.mp4` time range; identical MD5 hashes flag freezes. zoom.py's "segment timing in zoomed file" log enumerates the ranges to check.
- The flag's contract requires the *entire segment* (from `cursor` to `next_annotate.source_t`) to be inside ONE of the comma-separated ranges. Sub-ranges that cover only part of a segment are silently ignored — pass the whole segment range.
- After cleaning, the zoomed file's annotate segments shift earlier by the total dropped duration. Per Hard Rule #12, re-derive `annotations[].in/out_recording_t` and `lower_thirds[].in/out_recording_t` against the new "segment timing in zoomed file" output.
- V1.2 application: `--clean-source-ranges "50.25:52.85,52.85:59.0"` — z1→z2 segment shed 1.14s (0.8s freeze + ~0.34s of micro-duplicates), z2→z3 segment shed 0.20s. The script frontmatter's `annotations[]` timings (50.25/66.25, 67.73/77.73, 83.40/87.40) were originally written assuming this clean — running zoom without the flag produced timings 1.34s late at z3, which the panel timing then chased into "early" territory.
- Future automation candidate: detect freezes inside `tools/zoom.py` and clean them automatically. For now, the orchestrator passes the flag by default; manual override (drop the flag) is available for the rare case where mpdecimate would harm a video's specific motion content.
