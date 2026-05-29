# 2026-05-29 — Post-streaming pre-scroll-up dead-time cap promoted to global Hard Rule #26

**Scope:** Both pipelines — news-pipeline + product-demo. Promotes the narrow case of news's original Rule N1 (case (a) — post-checklist-finish pre-scroll-up dead time) into a shared automation-layer failsafe.

**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (new Hard Rule #26), `automation/capture.py` (new `cap_post_streaming_deadtime()` function + failsafe wiring after the existing auto-trim block), `news-pipeline/README.md` (N1 row narrowed to case (b) only; Hard Rule #26 added to inherited-rules table). The original news ADR `decisions/2026-05-28-news-1s-dead-time-cap.md` remains in force for case (b) — the trailing dead time post-scroll-down — which stays news-only.

## Decision

When `automation/capture.py` produces a recording, the window between `phases.streaming_ended` (mic icon appears, brief finished rendering) and the start of the post-streaming scroll-up dance is normally excised by the existing auto-trim. **If the auto-trim can't run** (`scroll_to_top_done` not marked in phases, or `trim_segment` errored), a freeze-detect failsafe finds any freeze >1s starting within 30s of `streaming_ended` and caps it to 1s via ffmpeg trim+concat. The output overwrites `trimmed.mp4`.

The failsafe is scoped narrowly:
- Targets ONE freeze near `streaming_ended` (the canonical dead-time gap)
- Does NOT touch typing pauses (pre-streaming), tick-window holds (during streaming), or annotate dwells (post-scroll, far after `streaming_ended`)
- No-op when auto-trim succeeded (window already gone)
- No-op when `--no-readthrough` was passed (no window exists)
- No-op when no qualifying freeze found (the typical good case)

Both pipelines benefit because both invoke `automation/capture.py` (Pass 1 + Pass 2 of the architecture extraction). The shared automation layer is the right home for this safety net.

## Why a rule, not just code

The behavior encodes a viewer-experience policy (dead time during a UI transition is never intentional content; cap it). Without the rule documentation, future maintainers see `cap_post_streaming_deadtime()` in capture.py and don't know why the 1s threshold, why the 30s search window, why it only fires when trim failed. The Hard Rule artifact preserves the WHY across maintenance.

## Why this scope and not broader

The original N1 in news targeted **two** dead-time cases:
- (a) post-streaming pre-scroll-up — the window this ADR promotes globally
- (b) post-scroll-down pre-outro — the trailing dead time after the scroll-down read-through completes

Case (b) stays news-only because product-demo's post-scroll-down region is filled with Phase 5.5 annotate dwells (Hard Rule #25 panel-hold minimums — 3–10+ seconds of intentional freeze-frame per annotate panel). A 1s cap there would destroy the annotate mechanism.

Case (a) — the window this ADR covers — exists identically in both pipelines because both use the same `automation/capture.py` scroll-dance flow. The post-streaming gap is mechanical (Cowork finishes streaming; capture.py wakes Chromium and initiates the scroll dance); it carries no intentional content in either workflow. Capping it to 1s is safe everywhere.

## User context

> "for n1, that rule specifically is for the post progress bar checklist finish, pre scroll up event, because there was a case where it froze there for a while. it doesnt happen anymore with our stop button microphone detection functioning, but just in case i want it there as a failsafe gateway to cut out dead time. since its only for that section, it applies for both product demo and news-pipeline, its a general editing choice for both, so i think it shld be safe to implement as a global rule/codify"

The dual-region stop-vs-mic detection (introduced earlier in the news-pipeline build) reliably catches end-of-streaming within ~1s of the true moment, so the dead-time gap is now small in practice (5–10s of expected post-streaming activity, all of which gets auto-trimmed by `trim_segment`). The failsafe exists for edge cases where the trim couldn't fire — e.g., scroll dance failure leaves `scroll_to_top_done` unmarked, or `trim_segment` errors on a corrupt frame.

## Implementation

`automation/capture.py::cap_post_streaming_deadtime(input_video, streaming_ended_t, output_video, max_dead_s=1.0, search_window_s=30.0)`:

1. Run `ffmpeg freezedetect=n=-45dB:d=max_dead_s` on `input_video`
2. Parse freeze intervals from stderr
3. Find the first freeze starting within `[streaming_ended_t, streaming_ended_t + search_window_s]` with duration > `max_dead_s + 0.05s` (50ms detector slack)
4. If found: build keep_ranges `[(0, f_start + max_dead_s), (f_end, total_duration)]`, apply ffmpeg trim+concat, write to `output_video`
5. If not found: `shutil.copy(input_video, output_video)` so downstream gets a usable file
6. Returns `(cap_applied: bool, capped_seconds: float)`

Wiring in `main()` falls through to the failsafe when:
- `not trim_ok` (auto-trim didn't succeed)
- `"streaming_ended" in phases` (have an anchor point)
- `not interrupted` (full run, not Ctrl+C'd)
- `not args.no_readthrough` (caller wanted the scroll dance to run)

## Cross-references

- Original news-only rule: `decisions/2026-05-28-news-1s-dead-time-cap.md`
- N2 (typing speedup, news-only): `decisions/2026-05-29-news-typing-never-cut.md`
- Pass 1 + 2 architecture extraction: branch `extract-automation-layer`, commits `7a8d760`, `7c6c9f7`, `937eb88`, `c8b7cc4`, `96e4e6e`
- Companion Hard Rule #14 (source preserved until approval — `raw.mp4` is kept regardless of failsafe outcome)
- Companion Hard Rule #25 (annotate panel-hold minimum — why case (b) can't be promoted globally)
