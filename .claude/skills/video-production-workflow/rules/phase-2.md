# Phase 2 rules — Capture / record (both pipelines)

Read these when invoking Phase 2 (capture). Cross-load `meta.md` too (60fps + source preservation).

---

## Hard Rule #26 — Post-streaming pre-scroll-up dead-time is capped to 1s as a failsafe.

When automated screen capture drives Claude desktop (via `automation/capture.py`), the window between `phases.streaming_ended` (mic icon appears, brief finished rendering) and `phases.scroll_to_top_done` (the chat-scroll-to-top transition the post-streaming dance fires) is normally excised cleanly by `capture.py`'s auto-trim. If the trim can't run (scroll dance didn't fire, `scroll_to_top_done` absent from phases, or `trim_segment` errored), this window of dead time survives into the captured recording.

**The failsafe.** `capture.py::cap_post_streaming_deadtime()` runs ffmpeg `freezedetect` (`-45dB`, `min_dead_s=1.0`) and looks for the first freeze starting within 30s of `streaming_ended`. If one is found longer than 1s, it's clipped to 1s via ffmpeg trim+concat. The resulting file replaces `trimmed.mp4`.

**Scope is intentionally narrow.** The rule targets ONE specific window — post-checklist-finish, pre-scroll-up — where dead time is never intentional content (the brief has rendered; the scroll dance is about to start). Pre-tick typing pauses (intentional pacing — viewer reads the question being typed), tick-window phase holds (intentional — viewer watches Cowork sidebar tick through), and post-scroll annotate dwells (Hard Rule #25 panel-hold minimum — 3s+ holds where VO interprets the highlighted row) are all OUTSIDE this 30s window from `streaming_ended` and remain untouched.

**Applies globally** — both pipelines (news-pipeline, product-demo) consume `automation/capture.py` and benefit. Promoted from news's original "N1" rule (which was specifically scoped to this case; the now-deprecated broader implementation in `news-pipeline/tools/tick_cut.py::cap_dead_times` stays in place for news's case (b) — the trailing dead time between scroll-down completion and the Polaris outro — which is news-only).

**No-op conditions** (failsafe doesn't fire): (i) auto-trim succeeded (`scroll_to_top_done` was marked AND `trim_segment` returned ok); (ii) `--no-readthrough` was passed (caller deliberately skipped the scroll dance — no window to cap); (iii) `interrupted=True` (recording was Ctrl+C'd, partial state); (iv) no freeze >1s found within 30s of `streaming_ended` (the typical good case — detection worked, scroll dance fired promptly, no dead time accumulated).

Logged: `decisions/2026-05-29-post-streaming-deadtime-cap-global.md`. Companion to Hard Rule #14 (source preservation — `raw.mp4` is kept regardless of failsafe outcome).

---

## Hand-off contract

The recording must clearly contain the *content* each beat references, and each `dwell: y` beat must have a settled visual that Phase 5.5 zoom can dwell on. Frame extraction in Phase 4 audits the first half of that; the second half is verified at Phase 5.5.

Slowdown is banned (Hard Rule #13 — see `phase-3-*.md`). Per-beat duration in raw can be longer than target (Phase 3 scrub compresses; Phase 5.5 zoom adds back planned dwell time), but cannot be meaningfully shorter for non-dwell beats — there is no extension mechanism for those once dead time is gone.
