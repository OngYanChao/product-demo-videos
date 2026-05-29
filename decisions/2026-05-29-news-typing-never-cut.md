# 2026-05-29 — News-pipeline: prompt typing segment is speedup-OK, never cut

**Status:** active
**Scope:** news-pipeline only. Main pipeline keeps Hard Rule #21 (prompt typing at 1×). The rules diverge because the two streams have different runtime budgets and different roles for the typing window.
**Affects:** `news-pipeline/README.md` (new row **N2** in the "News-pipeline-specific hard rules" table), `news-pipeline/tools/process.py` (scrub-invocation must force speedup-not-cut across the typing window; current default invocation `scrub.py <trimmed>` with no flags fails this rule).

## Decision

In the news-pipeline, the prompt-typing segment of a recording — `t = 0` through the moment cliclick releases focus and Claude begins streaming — **must never be cut**. It may be played back at uniform speedup (anchor speed, default 2×) to shorten the rendered runtime. Tapered cuts, `tapered_with_cut` freeze treatment, and any frame-dropping are forbidden in this window.

Outside the typing window, scrub.py's existing freeze treatment (`tapered_with_cut`, `uniform_speedup`) applies unchanged.

## Why

User feedback on N11's scrub output — verbatim:

> "Why is there a cut during the prompt typing segment? I never asked for that. This subproject should be for really short news pipeline videos so we can allow speeding up from typing segments just to shorten the runtime of the video but never cut."

N11's `trimmed_scrub_report.json` shows the first detected freeze at `0.0 → 24.55s` was given `tapered_with_cut` treatment — the very window where cliclick was typing the 18-holding portfolio into Cowork. The cut dropped frames mid-typing, which both breaks the visual flow of "watch the prompt land in Cowork" and removes a moment that has narrative value (this is the news event being phrased as a question).

Why the rules diverge from main pipeline Hard Rule #21:

- **Main pipeline** product-demo videos are script-driven and the typing window is *content* anchoring the value-framing for the whole video. Speedup at 2× makes the typing read as comedic and unreadable, so Hard Rule #21 locks it at 1×.
- **News pipeline** videos are short reactive demos with no script and no narration. The typing window establishes context but isn't load-bearing — viewers just need to see *that* a prompt was entered, not necessarily *read every keystroke*. The runtime budget is tighter (sub-90s targets), so 1× across a 20-30s typing window would dominate the video. Speedup is the right knob; cuts are the wrong knob.

The asymmetry the user is settling: speedup is acceptable because it preserves the visual continuity of typing-in-progress (characters flow in, just faster). Cuts break that continuity — the prompt appears to teleport, which reads as a recording-quality defect rather than a stylistic choice.

## How to apply (enforcement)

**Auto-enforced** for every `process.py` invocation, as of this ADR.

Two-part implementation:

1. **`capture.py` records the typing-end boundary.** A `mark("streaming_started")` call was added immediately after `wait_for_streaming_to_start()` returns (both the success branch and the timeout-warning branch), persisting `phases.streaming_started` into the slot's `manifest.json`. On the timeout branch the value is approximate (~8s past true typing-end), but always safe — speeding up a few extra seconds of empty chrome is fine; the rule only forbids cuts.

2. **`process.py` reads the boundary and prepends `--force-speed-range`.** A helper `_derive_typing_force_range()` reads `manifest.phases.streaming_started`, shaves a `TYPING_END_SAFETY_SHAVE_S = 0.5s` safety margin (so the forced range doesn't bleed into Cowork's first response frame), and emits `--force-speed-range "0:X:2.0"` (anchor = `TYPING_SPEEDUP_FACTOR`). The flag is prepended *before* user-supplied `--scrub-arg` values, so anything else the user passes still takes effect.

**Graceful degradation:**

- Manifest missing → warn, skip auto-force-range, scrub runs with its default treatment.
- `streaming_started` key missing (pre-2026-05-29 recordings) → warn, skip.
- User passed their own `--force-speed-range` via `--scrub-arg` → defer to user value, log that the auto value was skipped.
- `--no-typing-speedup` CLI flag → opt out; scrub uses default treatment (may cut typing).

**N11 status.** N11's current `zoom.mp4` violates this rule (typing was cut, pre-enforcement). Not retroactively re-scrubbing here; the rule applies to future runs and to N11 if the user asks for a re-scrub. Note that N11's existing `manifest.json` also lacks `phases.streaming_started` (pre-N2 recording) — a re-scrub would need either a manual `--scrub-arg --force-speed-range "0:24:2.0"` (X derived from the first detected freeze's end) or a fresh recording.

## Notes

- **Contrast with main pipeline.** Hard Rule #21 (typing at 1×) stays the rule for V1–V16. This ADR does not modify the main pipeline. The two rules coexist because their videos have different shapes.
- **Anchor-speed choice.** `scrub.py`'s default `--anchor-speed 2.0` is the right default for news typing. If a future news video has an unusually long prompt (e.g. multi-paragraph context), bumping to 2.5× or 3× via `--anchor-speed` is fine — speedup is the dial; cuts remain forbidden.
- **Why not auto-trim typing entirely?** Considered. Rejected because the typing window establishes the *question* the news video is answering — removing it entirely would land the viewer in mid-response with no context. Speedup preserves context at a cost of ~5–10s of runtime vs full removal.
- **Companion to N1** ([2026-05-28-news-1s-dead-time-cap.md](2026-05-28-news-1s-dead-time-cap.md)). N1 protects pre-tick (= pre-streaming, includes typing) from the dead-time cap. This ADR extends that protection: typing is also protected from scrub.py's `tapered_with_cut` freeze treatment.
- **Companion to Hard Rule #13** (never slow source). Speedup beyond 1× is fine; this rule only forbids the opposite of speedup (cuts that drop frames).
- **Cross-reference.** [`news-pipeline/README.md` § News-pipeline-specific hard rules — N2](../news-pipeline/README.md#news-pipeline-specific-hard-rules).
