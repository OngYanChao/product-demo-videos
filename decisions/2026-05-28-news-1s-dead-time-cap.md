# 2026-05-28 — News-pipeline: 1s hard cap on dead time in the post-tick region

**Status:** active
**Scope:** news-pipeline only (no equivalent rule in the main product-demo pipeline; pacing requirements differ).
**Affects:** `news-pipeline/README.md` (new section "News-pipeline-specific hard rules", rule N1), `news-pipeline/tools/tick_cut.py` (new `cap_dead_times()` helper + `NEWS_MAX_DEAD_S = 1.0`), `news-pipeline/tools/process.py` (new step 4 calls `cap_dead_times` after `zoom.py`; `--no-cap-dead` CLI escape hatch).

## Decision

In the news-pipeline, after `zoom.py` produces the final `zoom.mp4`, any freeze interval longer than **1.0 seconds** that starts after the auto-zoom timeline ends (= the boundary where the full-frame post-tick segment begins) is capped to **1.0 seconds**.

Two specific dwells the user identified as awkward in N11's render are the target of this rule:

1. The dead time between **"output brief done loading"** and the auto-trim cut to the top of the chat (Cowork stops generating, then there's a small idle window before `capture.py`'s scroll-up sequence fires and the trim point is taken).
2. The dead time **after smooth-scroll-down completes** (chat at bottom, doc panel scrolled, bottom-hold) before the Polaris outro begins.

Both come out as freezes in the rendered video: scrub already compresses the obvious >2s ones, but residual 2–8s freezes survive because Cowork's chrome has subtle non-static elements (cursor blinks, indicator animations) that defeat the strict `-60dB` default. `cap_dead_times` uses a permissive `-45dB` noise threshold so those count as freezes, then ffmpeg trim+concat reduces each to 1.0s.

**Pre-tick (prompt typing) and tick-montage (phase-transition holds) are explicitly protected.** Typing pauses give the prompt context room to land; phase holds are intentional pacing for the user to read each phase. The cap only runs on `t ≥ protect_until_t` where `protect_until_t = source_t + duration` of the last auto-zoom entry. If no auto-zooms were emitted (user-authored `zooms.json` instead, or no zoom step), `protect_until_t = 0` and the cap applies to the entire output.

## Why

User feedback on N11 (the canary news-pipeline render) — verbatim:

> "The awkward holding time after the upper brief is done loading before the scroll up to the top or the cut to the top is still there. It's still a bit too long. Can we set this to be one second hard limit? And then also after the entire scroll down has finished there is a solid seven seconds of nothing there can we fix that as well — again one second after the scroll down is done give it a one second window and then we cut the outro. Make this a consistent rule for this subproject."

N11's `zoom.mp4` (pre-cap) showed exactly those two freezes when run through `ffmpeg freezedetect=n=-45dB:d=0.5`:

- `16.82 → 19.65` (2.83s) — Cowork finished writing the brief, sat still, then the cut to top fired. This is the *brief-done-to-cut-to-top dwell*.
- `35.52 → 43.73` (8.20s) — smooth-scroll-down completed at ~35.5s; the trailing 8.2s before outro is the bottom-hold + ffmpeg-stop latency that scrub couldn't fully catch. This is the *post-scroll tail*.

Both feel like the video has stalled. Capping both to 1.0s reclaims ~9s and the resulting pacing reads as "moment to register, then move on" rather than "did the video freeze?"

`scrub.py` is the wrong place to enforce this:

- scrub operates on `trimmed.mp4` (pre-tick-cut, pre-zoom) where these two specific freezes have different timestamps and aren't yet bracketed by anything stable.
- scrub's threshold (default `min_dead_seconds=5`, overridable) governs *all* freezes uniformly — lowering it to 1s would catch unintended pauses elsewhere in the streaming.
- The two dwells under cap are at the **post-tick boundary** in the *final* render, not in the raw trimmed source. The boundary is only known after `tick_cut.py` runs and `zoom.py` materializes the timeline. Cap belongs there.

The cap is **end-of-pipeline** by design: it runs on `zoom.mp4` after all other transformations, so it sees the same content the viewer sees and can target post-tick freezes precisely via the auto-zoom timeline's end as the boundary marker.

## How to apply (enforcement)

**Automatic** for any `process.py` run on a news-pipeline slot. The relevant code path:

```
news-pipeline/tools/process.py::process_slot()
  └─ step 4 (after zoom.py succeeds):
       protect_until_t = (last auto-zoom).source_t + (last auto-zoom).duration
       tick_cut.cap_dead_times(zoom.mp4, max_dead_s=1.0, protect_until_t=...)
```

`cap_dead_times` uses:

- `ffmpeg -vf freezedetect=n=-45dB:d=1.0` to find all freeze intervals ≥1.0s.
- For each freeze with `start ≥ protect_until_t` and `duration > 1.05s` (50ms detector-jitter slack), drop the range `[start + 1.0, end]`.
- Apply ffmpeg `trim+concat` filter graph in a single re-encode (`libx264 preset fast crf 20`).

**Manual escape hatch** — `python3 news-pipeline/tools/process.py N<N> --no-cap-dead` disables the cap for a single run (use when validating that a specific freeze IS intentional content).

**For user-authored `zooms.json` cases:** `protect_until_t` defaults to 0, so the cap runs on the entire video. If a user-authored zoom intentionally needs a >1s hold somewhere, either rephrase as a `pause_after` (which is content, not a freeze of static frames) or pass `--no-cap-dead`.

## Notes

- **Pre-emptive fix in `capture.py`.** `POST_SCROLL_TOP_HOLD_S` and `POST_SCROLL_BOTTOM_HOLD_S` were reduced in the same session (2.0s → 0.5s and 2.5s → 1.0s) to shrink the baked-in holds for FUTURE recordings. The cap is the post-process safety net that catches whatever still leaks through (the cap is what actually enforces the rule; the capture-time reductions just narrow the cap's job).
- **Not propagated to the main product-demo pipeline.** Main-pipeline videos are script-driven and the recording length is shaped by beat-sheet pacing (Phase 1/3/5/6a). Dead times in main-pipeline outputs are deliberate beat holds or `pause_after` directives — capping them automatically would fight the script. News-pipeline videos have no script and no beat sheet, so the cap is unambiguous.
- **The `-45dB` noise threshold is empirical.** Default ffmpeg `-60dB` (= 0.1% pixel diff) misses Cowork's freezes because of cursor blink + Progress sidebar indicator animations. `-45dB` (= ~0.5% pixel diff) was the lowest threshold that caught the two N11 dwells without false-positiving on smooth-scroll content. Adjustable per-call if a future Cowork UI change shifts the noise floor.
- **Cross-references.** [`news-pipeline/README.md` § News-pipeline-specific hard rules — N1](../news-pipeline/README.md#news-pipeline-specific-hard-rules). Memory: [[feedback_copy_v1_stats_literal]] (companion: don't substitute judgement for user's settled values — here, "1s hard cap" is the settled value).
