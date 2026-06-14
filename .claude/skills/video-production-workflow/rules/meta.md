# Cross-phase invariants

These rules apply at every phase of the pipeline. They're loaded alongside whichever phase-specific rules file the workflow is currently on. Both pipelines.

---

## Hard Rule #14 — Source material is preserved until the user explicitly approves the final output. Cleanup runs only on an explicit approval signal.

Source recordings, intermediate artifacts, scripts, and final outputs are never auto-deleted. Approval signals: *"yes"*, *"approved"*, *"ship it"*, *"looks good, ship"*, *"delete the frames"* — i.e., the user names the cleanup action or unambiguously OKs it. Non-approval (treat as don't-touch): *"thanks"*, *"will watch later"*, *"let me check"*, *"renders look ok"*, silence, or any ambiguity. The asymmetry exists because intermediate artifacts are cheap to regenerate but annoying to lose mid-review — the cost of an unwanted cleanup is much higher than the cost of leaving scratch files on disk for another session.

**Project-local:** in this project, `frames/V<N>/` is the scratch artifact whose cleanup is gated; the orchestrator's `"clean V<N> frames"` dispatch row requires the explicit approval signal. The following files are NEVER deleted at cleanup time regardless of signal: `outputs/V<N>/final.mp4`, `audio/V<N>.mp3` (if used), `screen recordings/V<N>/vid<N>.mp4`, `screen recordings/V<N>/vid<N>_scrubbed.mp4`, `screen recordings/V<N>/vid<N>_zoomed.mp4`, `scripts/V<N> voiceover script.md`, `scripts/V<N>_zooms.json` — these are the durable record.

---

## Hard Rule #15 — Source recordings and rendered output share a framerate; keyframe density is tight enough that the renderer's frame-by-frame seek operations don't hang on sparse keyframes.

Renderers that seek mid-clip during composition (zoom segments, transitions, cuts) decode forward from the nearest preceding keyframe. When keyframes are 2+ seconds apart, those seeks stall or hang — the renderer either takes 10× as long as expected or freezes outright. If the source arrives at the wrong framerate or with sparse keyframes, re-encode BEFORE Phase 3 scrub, not after.

**Project-local:** this project ships 60fps end-to-end with 1-second keyframe intervals. Re-encode with `ffmpeg -i input.mp4 -r 60 -g 60 -keyint_min 60 output.mp4` before running `tools/scrub.py`. Hyperframes (the project's renderer) exhibits the violation as: renders hang at the first zoom segment, or take 5+ minutes when they should take ~30 seconds. `tools/scrub.py` + `tools/zoom.py` preserve framerate and keyframe density on output; template render commands explicitly set `--fps 60`.
