# 2026-05-23 — Tick-window compression moves to Phase 3 (gap-cut rule)

**Status:** active
**Supersedes (partially):** `decisions/2026-05-22-zoom-skeleton-standardization.md` (the "Hard Rule #23 — mandatory tail-cut as a Phase 5.5 post-process" wording is replaced; the rest of the 2026-05-22 ADR — standard skeleton, measured highlights, multi-VO-target sub-split — stands)
**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rules #20, #21, #23 updated), `.claude/skills/parallax-video/SKILL.md` (scrub + zoom dispatch rows updated), `tools/detect_ticks.py` (now emits `ffmpeg_keep_ranges` per gap-cut rule; `--compress-threshold` + `--target-gap` CLI flags added), `screen recordings/V2/*` (first video re-conformed under the new pipeline)

## Decision

Three coupled changes that together move tick-window compression from Phase 5.5 to Phase 3, and replace the V1-era "±tail_seconds window around each tick" framing with a gap-based rule.

### 1. Architecture move

`detect_ticks.py` runs on the **RAW recording** during Phase 3 (was: scrubbed file during Phase 5.5). The tick-window compression becomes part of the conform output, not a post-process applied later. The Phase 5.5 "tail-cut" step is removed entirely — `zoom.py`'s output IS the canonical zoomed file, no `_natural` + `_tickcut` intermediate.

### 2. Gap-cut rule (replaces ±tail_seconds windows)

For every dead segment inside the tick window — pre-first-tick gap, between-tick gaps, post-last-tick gap:

- **Gap > 2 seconds:** compress to **1 second**. Implementation: for between-tick gaps, keep 0.5s after the prior tick + 0.5s before the next tick, jump-cut between. For pre-first-tick, keep 1s before the first tick. For post-last-tick, keep 1s after the last tick.
- **Gap ≤ 2 seconds:** leave alone. Natural playback at 1×.

The viewer experience: ticks that fire close together in the recording stay close together in the output (no artificial spacing). Ticks separated by long dead loading get compressed to a tight 1s rhythm.

### 3. `scrub.py` scope narrows

With tick-window compression handled separately, `scrub.py`'s pixel-diff freeze compression applies only to the **two buffer zones** around the tick window:

- (1) **Post-typing-pre-first-tick** — the "Starting up…" period after submit and before the Progress sidebar starts showing checkmarks. Usually 2–5s of generic loading.
- (2) **Post-last-tick-pre-brief-landed** — the "Synthesizing brief…" period after the final checkmark and before the rendered output is fully visible. Usually 3–10s of synthesis.

Three zones get **locked at 1×** via multi-zone `--force-speed-range` (Hard Rule #21):
- (a) Prompt typing → submit click (`0` to `T_typing_end`)
- (b) Tick window (`T_first_tick` to `T_last_tick`)
- (c) Brief-landed → end of recording (`T_brief_landed` to end)

## Why

V2 production exposed a structural duplication. The pipeline I produced for V2 had `scrub.py` aggressively compressing the loading segment (raw ~150s → scrubbed ~13s) via pixel-diff freeze detection. Then `detect_ticks.py` ran in Phase 5.5 on the already-compressed file. By the time the gap-cut tail-cut tried to compress dead time, scrub.py had already removed most of it via a different algorithm. Result: two compression passes doing similar work, with the second pass mostly redundant.

User feedback:

> "Why are we only doing the detect ticks in phase 5.5 after the natural zoom file has already been produced? Isn't that a bit too late? If you look at the natural zoom file, the ticks are all already compressed so there's nothing else to compress. So what the hell is going on here? Shouldn't it be earlier in the pipeline?"

The right ordering: `detect_ticks` runs FIRST on raw, identifies the natural tick spacing in the source, and drives compression via the gap-cut rule. `scrub.py`'s pixel-diff compression is told to STAY OUT of the tick window (locked at 1× via `--force-speed-range`) and only handles the two narrow buffer zones around it. Two compression mechanisms with clearly non-overlapping scopes.

The gap-cut rule (>2s → 1s; ≤2s → natural) replaces the V1-era "±1s window around each tick, jump-cut between" framing. The reason: V1's pattern worked by accident because V1's ticks were spaced wide enough that the ±1s windows didn't overlap. V2's ticks are closer together (1.5s and 3s apart in the scrubbed file); the ±1s framing required merging overlapping windows, which collapsed back to "everything checks off at once like a hard jump cut." Gap-cut is the cleaner formulation: focus on the gaps you want to compress, not on artificially-sized windows per tick.

User feedback for the new rule:

> "The whole point of the detect ticks file or code was just to make sure that we can cut out the dead segments in between each tick occurring. So if the ticks are very close to each other and the gap overlaps, then well we don't need to cut anymore. I think we should change the rules so instead of getting a one second window before and after each take, I think we do it such that if the time segment between each take happening or the date segment is more than two seconds then we do a cut and make sure that between each take occurring there is only one second of space and then if there is less than one second of space, then we don't bother and we don't need to touch it at all."

The rule applies symmetrically to all dead segments inside the tick window (pre-first-tick, between-tick, post-last-tick) — same threshold, same target gap.

## How to apply (enforcement)

1. **Phase 3 audit identifies four raw timestamps:** `T_typing_end` (submit-click moment), `T_first_tick` + `T_last_tick` (from `detect_ticks.py` on raw), `T_brief_landed` (frame-by-frame inspection where the rendered output is first fully visible).

2. **Run `detect_ticks.py` on raw recording** with `--time-range "<T_typing_end>:<T_brief_landed>"`. Output JSON includes the tick timestamps and `ffmpeg_keep_ranges` derived from the gap-cut rule (default `--compress-threshold 2.0 --target-gap 1.0`).

3. **Run `scrub.py` with three locked zones:** `--force-speed-range "0:T_typing_end:1.0,T_first_tick:T_last_tick:1.0,T_brief_landed:end:1.0"`. Output: `vid<N>_scrubbed_pre_tickcut.mp4` — the entire tick window is at 1× (ticks fire at natural raw spacing).

4. **Apply ffmpeg trim+concat to the tick window** using `ffmpeg_keep_ranges`. This produces the tick-compressed segment of the scrubbed file. Concatenate: pre-tick-window portion + tick-compressed window + post-tick-window portion = final `vid<N>_scrubbed.mp4`.

5. **All ticks must fall inside `z0b`'s held portion** during Phase 5.5 zoom (Hard Rule #23). `z0b.duration` extends past the last tick + buffer + ease-out. Zoom-out only after all ticks have fired.

6. **No Phase 5.5 tail-cut step exists.** `zoom.py`'s output is the canonical `vid<N>_zoomed.mp4` directly. The `vid<N>_zoomed_natural.mp4` intermediate (which the 2026-05-22 ADR introduced for the Phase 5.5 tail-cut) is no longer needed.

## Notes

- **Orchestration:** Option B was chosen — separate tools (`detect_ticks.py` + `scrub.py` + ad-hoc ffmpeg trim+concat) chained by the parallax-video skill's scrub dispatch row. Not integrated into `scrub.py` as a single tool — the two algorithms (tick detection vs pixel-diff freeze compression) stay focused, and the orchestration is documented at the skill layer rather than baked into either tool.
- **`scrub.py` already supports multi-zone `--force-speed-range`.** The flag parses a comma-separated list of `start:end:speed` triples. No code change to `scrub.py` was needed for this architecture move.
- **`detect_ticks.py` keeps the legacy `ffmpeg_trim_ranges` field for backwards-compat** alongside the new `ffmpeg_keep_ranges`. V1's existing `vid1_ticks.json` and its post-process pipeline still work; new videos should use the new field.
- **CLI flags `--compress-threshold` and `--target-gap`** are tunable per video if the rhythm calls for it (e.g., a video with a slower-paced loading sequence might prefer a 3s threshold + 1.5s target). Default to 2.0 + 1.0 per the locked rule.
- **`scrub.py` is unchanged.** Its scope narrows in the sense that the dispatch row tells it to leave the tick window alone — the tool itself doesn't need to know about ticks.
- **V1's legacy `1vid_zoomed_route2v2_tickcut.mp4` is not retroactively rebuilt.** The 2026-05-22 ADR's Phase 5.5 tail-cut pipeline produced V1 under the old rules; that output remains canonical for V1 until a future re-record. The new pipeline applies to V2 onward.
