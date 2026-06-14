# Phase 3 rules — product-demo (conform recording, scrub-only)

Read these when invoking Phase 3 for V<N> / I<N> videos. Cross-load `meta.md` + `phase-2.md` (for Rule #26 cap).

---

## Hard Rule #2 — Conform the recording, don't compress the script.

When the recording doesn't match the beat sheet, change the recording. Never silently shrink VO beats to absorb recording mismatch.

---

## Hard Rule #4 — The recording must visibly contain each beat's claimed content.

Audited via Phase 4 frame extraction against the scrubbed recording. If a beat's content isn't visible, re-scrub or re-record — don't silently rewrite the script to match what's actually on screen.

---

## Hard Rule #13 — Never slow down source playback. Anywhere. For any reason.

No uniform-rate slowdown of a too-short beat, no pre-zoom deceleration ramp, no setpts stretch on a transition. Slowed motion reads as syrupy at uniform rates and produces a rubber-banding stutter on ramps — the user has rejected both ("looks like shit"). The only sanctioned ways to extend a beat are: insert a held-still frame, insert a script-driven pause-zoom on a dwell:y beat, or re-record. If none of those apply, the beat is unfit and Phase 3 escalates to re-record (or, rarely, re-opens Phase 1). The `pre_zoom_slowdown` machinery has been removed from `tools/zoom.py` accordingly; the only zoom-prep extension knob that remains is `pre_zoom_hold` (held still, no motion).

---

## Hard Rule #20 — Tick timestamps must be detected programmatically, never eyeballed — and detection runs on the RAW recording during Phase 3, not on the scrubbed file during Phase 5.5.

When a recording contains a progress-bar or status-checklist loading sequence (Cowork's top-right Progress sidebar, equivalent UIs), the tick events are compressed via the gap-cut rule (see Hard Rule #23). Tick timestamps that drive that compression come from frame-diff detection on the RAW recording — not from sampling frames at 1s intervals and guessing, AND not from running detect_ticks on the scrubbed file (by which time the freeze-compression in scrub.py has already squeezed ticks together, leaving the gap rule nothing to compress).

Run `python tools/detect_ticks.py "<raw_recording>" --time-range "<t0>:<t1>" --region-pct "x,y,w,h" --expected-ticks N --output <ticks.json>` once per video, BEFORE scrub.py runs. The tool samples at 30fps in the search region, computes frame-to-frame mean absolute pixel diff, returns the top-N peaks with non-maximum suppression, and emits `ffmpeg_keep_ranges` derived from the gap-cut rule (gaps > 2s compress to 1s, gaps ≤ 2s leave alone).

**Tick-window bound is the PENULTIMATE tick `T_(N-1)`, not `T_N`.** The final tick in a Parallax product_demo is reliably "Synthesize and deliver brief," which fires AFTER the brief is fully rendered. The tick window for the scrub.py lock + gap-cut compression extends from `T_first_tick` to `T_(N-1)`, excluding the synthesis tick. The synthesis tick `T_N` falls in buffer zone 2 (post-`T_(N-1)`, pre-`T_brief_landed`), which scrub.py compresses — `z0b`'s ease-out plays during this compressed buffer so the viewer watches the brief progressively render in fast-forward.

Implementation: invoke detect_ticks with a search range covering all ticks (e.g., `--time-range "T_typing_end:T_brief_landed"`), then in orchestration use `ticks[N-2]` (zero-indexed penultimate) as the tick window's upper bound; re-invoke detect_ticks with `--time-range "T_first_tick:T_(N-1)"` to get gap-cut keep_ranges scoped to the penultimate-bounded window. Paste those keep_ranges into the ffmpeg trim+concat that builds the tick-compressed segment of the scrubbed file. For simultaneous ticks (two checklist items tick at the same instant), count as ONE moment when setting `--expected-ticks`. If true ticks have very different visual magnitudes, request more peaks than expected and discard the lowest-magnitude false positives.

Companion to Hard Rule #10 (measured pixel bounds) — same "measured, not eyeballed" discipline. Logged: `decisions/2026-05-21-detect-ticks-programmatic.md`, `decisions/2026-05-23-tick-window-compression-moves-to-phase-3.md`.

---

## Hard Rule #21 — Multiple recording segments are locked at 1× — never compressed.

`scrub.py` only compresses dead time in the buffer zones between them. Three zones get 1× lock; `scrub.py`'s pixel-diff freeze compression applies only to the gaps between them. The three locked zones for a product_demo:

(a) **Prompt typing → submit click** (`0` to `T_typing_end`). The persona's question gets named in the customer's chair here; the value-framing for the whole video anchors at this moment. **Default: 1× lock** — viewers read the question being typed. **Adaptive speedup when typing exceeds 10s** (long-prompt videos: V13 family-office onboarding, I3 quad-client demonstration, hero playbooks): `speedup_factor = min(2.0, max(1.0, typing_duration / 10.0))`, capped at 2× to avoid the comedic register that more aggressive speedup produces. Worked examples: 15s → 1.5× (post-speedup 10s); 20s → 2× (post-speedup 10s); 30s → 2× (post-speedup 15s); 40s → 2× (post-speedup 20s). Threshold of 10s = the upper bound of "tolerable 1× typing." **Diverges from news's Rule N2** (always-2× speedup regardless of duration): news's typing is context (not deliverable content), so aggressive speedup is fine throughout. Product-demo's typing IS load-bearing content (the persona's NL prompt the viewer reads), so 1× is the right default. Encoded via the Phase 3 scrub dispatch reading `manifest.phases.streaming_started` to derive typing duration, computing the speedup factor, and emitting `--force-speed-range "0:T_typing_end:<factor>"` to `tools/scrub.py`. Logged: `decisions/2026-05-29-product-demo-adaptive-typing-speedup.md`.

(b) **Tick window — PENULTIMATE-bounded** (`T_first_tick` to `T_(N-1)`, the SECOND-TO-LAST tick). The Progress sidebar tick events fire here, BUT the final synthesis tick `T_N` is deliberately excluded — `T_N` ("Synthesize and deliver brief" or equivalent) fires AFTER the brief is fully rendered on screen, and treating it as the end of the locked tick window would put the actual brief-rendering animation INSIDE the locked zone (where it can't be compressed). Excluding `T_N` puts the synthesis/brief-rendering period in buffer zone 2 below, where `scrub.py` compresses it — the brief-loading animation then plays out during `z0b`'s ease-out (Hard Rule #23). `scrub.py` must NOT compress this tick window; compression happens via the gap-cut rule (Hard Rule #20 + #23) which is tick-aware.

(c) **Brief-landed → end of recording** (`T_brief_landed` to recording end). The viewer reads the rendered output here; annotates fire during this zone in Phase 5.5. Compressing it would rush the read.

Encoded by invoking `tools/scrub.py` with multiple `--force-speed-range` zones:
`--force-speed-range "0:T_typing_end:1.0,T_first_tick:T_(N-1):1.0,T_brief_landed:end:1.0"`

`scrub.py`'s general pixel-diff freeze compression applies only to the two buffer zones in between:
- **Buffer 1** (`T_typing_end → T_first_tick`): post-submit, sidebar populating but no checkmarks yet — true blind dead-time.
- **Buffer 2** (`T_(N-1) → T_brief_landed`): post-penultimate-tick synthesis. This is where the brief progressively renders in the chat area and the final synthesis tick `T_N` fires. `scrub.py` compresses this zone (typically a 24s tapered-with-cut down to ~1.5s), and `z0b`'s ease-out plays over the compressed result — the viewer watches the brief load in fast-forward as the camera retracts.

Boundary identification: `T_first_tick` and `T_(N-1)` come from `detect_ticks.py` running on raw (Hard Rule #20). `T_typing_end` and `T_brief_landed` come from frame-by-frame inspection (the boundaries are visually obvious — submit-click animation; brief content first fully rendered).

Companion to Hard Rule #13 (never slow source) — the asymmetry is deliberate: blind 2× freeze compression is fine for true dead loading but content moments get locked at 1×. Companion to Hard Rule #20 (tick detection) — the tick window's 1× lock depends on tick timestamps from `detect_ticks` running BEFORE `scrub.py`. Logged: `decisions/2026-05-22-prompt-typing-1x.md`, `decisions/2026-05-23-tick-window-compression-moves-to-phase-3.md`.

---

## Hard Rule #23 (Variant A/B selection) — Every product_demo zoom plan instantiates the standard skeleton: z0 + z0b + z1..zN. Variant A/B chosen at Phase 3.

The variant decision happens in Phase 3 step 6a:
- **Variant A — Manual screen recording** (no `manifest.json` alongside). Use Variant A z0b sizing in Phase 5.5.
- **Variant B — Automated capture** (`manifest.json` with `phases.scroll_to_top_done` set). Phase 3 pre-cuts `[T_N + post_synth_buffer, T_brief_landed]` (default `post_synth_buffer = 1.0s`) from `vid<N>.mp4` via ffmpeg trim+concat BEFORE running `scrub.py`. The cut shrinks buffer zone 2 to `[T_(N-1), T_N + post_synth_buffer]` and re-anchors `T_brief_landed` in pre-scrub time. After scrub, the brief-rendered position is adjacent to the at-top frame. Use Variant B z0b sizing in Phase 5.5.

**Default `post_synth_buffer = 1.0s`** — matches `margin` convention; tunable per-video if a longer beat is needed.

Full sizing formulas live in `phase-5-5-product-demo.md` (Hard Rule #23 z0b section).

Logged: `decisions/2026-05-24-z0b-starts-on-checklist.md`, `decisions/2026-05-29-automated-post-tick-cut.md`.

---

## Hard Rule #27 — The at-top frame must be held for ≥2.0s, must show the prompt + brief together at the top of the chat, and must flow naturally into the scroll-down without jump cuts.

**Scope:** only fires on automated captures (manifest present).

When the automated screen capture trims `[streaming_ended → scroll_to_top_done]` (the synthetic scroll-up flicker), the viewer's first sight after the cut is the at-top frame — and that frame needs to show the *whole exchange* (prompt at the top of the chat + the brief below it), held long enough to register, and then transition smoothly into the read-through.

**Three requirements, all load-bearing:**

(a) **Hold duration ≥ 2.0s.** Calibrated against human reading-comprehension for a *two-element* visual (prompt + brief-title), not the single-element visual that 1s would suffice for. 2.0s gives the viewer time to read the prompt, shift gaze to the brief beneath, and register "the response is here."

(b) **The frame must include the prompt at the top of the chat.** `automation/capture.py::scroll_chat_to_top()` must scroll the Cowork chat container all the way to the top — past the response, past any sticky brief header, to the FIRST message (the user's prompt). Implementation: 200 events × 10 lines per target. **Cowork UI snap caveat:** after the scroll-up events stop firing, Cowork's UI runs a snap animation that can push the prompt off-screen by ~0.5-0.7s after `scroll_to_top_done`. When this happens, find an earlier raw timestamp `t_at_top_prompt_visible` (typically `scroll_to_top_done − 0.5 to 0.7s`). Use `t_at_top_prompt_visible` as the cut boundary.

(c) **Natural continuation from freeze into scroll-down — no jump cuts.** When the failsafe injects a freeze frame at the at-top position, the source MUST continue from the same raw timestamp where the freeze slice began. The ffmpeg chain is `[source up to T_at_top] + [50ms slice at T_at_top + tpad clone padding] + [source from T_at_top onward]`. The post-freeze segment uses `trim=start=<T_at_top>` — NOT a later timestamp.

**Primary mechanism — capture-time hold.** `automation/capture.py` holds for `POST_SCROLL_TOP_HOLD_S = 2.0s` after scroll-to-top completes and before smooth-scroll-down begins. New captures bake the 2s pause natively.

**Failsafe — Phase 3 freeze-frame injection.** For recordings where `natural_top_hold < 2.0s`, Phase 3 dispatch injects a freeze frame at the at-top position: `freeze_s = 2.0 - natural_top_hold`. Uses `tpad=stop_mode=clone:stop_duration=<freeze_s>`.

**No-op conditions.** Failsafe doesn't inject if: (i) no manifest (manual recording), (ii) `smooth_scroll_chat_start` or `scroll_to_top_done` absent from phases, (iii) `natural_top_hold ≥ 1.0s` already.

Logged: `decisions/2026-05-30-minimum-top-hold.md`.

---

## Hard Rule #28 — z0.ease = 1.5s standard, and scrubbed buffer 1 (typing-end → first-tick) must be ≥ 2.5s.

**Scope:** product-demo (V<N>, I<N>) — news pipeline's auto-zoom uses its own ease defaults.

V1 and V2 both used `z0.ease = 1.5s` by convention. Codified here as the standard so the prompt-typing zoom plays at consistent speed across all V<N> videos.

**The minimum-buffer-1 requirement.** With `z0.ease = 1.5s` (standard) and `z0b.margin = 1.0s` (Hard Rule #23 standard), the scrubbed gap between z0 ending and z0b starting must be ≥ z0.ease + z0b.margin = 2.5s. If scrub.py's freeze compression brings buffer 1 below this floor, extend buffer 1 to satisfy the minimum.

**Phase 3 freeze-frame failsafe** (analogous to Rule #27's mechanism). After Phase 3 scrub completes, measure scrubbed buffer 1. If `scrubbed_buffer_1 < 2.5s`, inject a freeze frame in buffer 1: `freeze_s = 2.5 − scrubbed_buffer_1 + 0.1s_safety`. Inject at MIDPOINT of buffer 1 — *not* near `T_first_tick_scrubbed` (the 50ms tpad slice would contain the tick animation and cause a re-play artifact), *not* at `T_typing_end` (cursor still moving). ffmpeg pattern: `[0:v]trim=end=<inject_pos>[v0]; [0:v]trim=start=<inject_pos>:end=<inject_pos+0.05>,tpad=stop_mode=clone:stop_duration=<freeze_s>[v1]; [0:v]trim=start=<inject_pos>[v2]; [v0][v1][v2]concat=n=3`. After injection, re-run `detect_ticks` to confirm new `T_first_tick_scrubbed`, then update zooms.json: `z0b.source_t = T_first_tick_scrubbed_new − margin`; all annotate `source_t` shift by `+freeze_s`.

**No-op conditions.** Failsafe doesn't fire if: (i) `scrubbed_buffer_1 ≥ 2.5s` already; (ii) `T_typing_end` or `T_first_tick_scrubbed` can't be determined; (iii) recording lacks the tick-window structure entirely.

Logged: `decisions/2026-05-30-buffer-1-minimum.md`. Companion to Hard Rule #27 (sibling failsafe pattern).

---

## Hard Rule #29 (Phase 3 / pre-zoom rebuild) — For automated captures with z0b, rebuild the intermediate before zoom.py runs.

**Scope:** automated captures with z0b (manifest + scroll_to_top_done + z0b in zooms.json present).

The rebuild step (auto-applied by Phase 3 dispatch) modifies the intermediate that feeds `zoom.py` so:
- z0b's ease-out plays over a frozen at-top frame (not live scroll/snap motion)
- After z0b ends, 1.0s of tpad freeze continues (provides half the Rule #27 2.0s hold)
- Stitch `raw[smooth_scroll_chat_start − 1.0s, end_of_raw]` for natural continuation (the 1.0s of natural at-top hold from raw provides the other half of the Rule #27 hold)

Compute:
- `T_z0b_ease_out_start_src = z0b.source_t + z0b.duration − z0b.ease`
- `freeze_duration = z0b.ease + 1.0s` (was `+ 2.0s`; reduced 2026-06-04 to split the Rule #27 hold across tpad + raw natural hold, avoiding double-count)
- `T_raw_tail_start = max(T_at_top + 0.05s, smooth_scroll_chat_start − 1.0s)` (normalizes natural at-top hold in raw to 1.0s regardless of capture.py's `POST_SCROLL_TOP_HOLD_S`)

Rebuild via ffmpeg:
- `tc_pre` = `intermediate[0 : T_z0b_ease_out_start_src]`
- `freeze` = 50ms slice of `raw[T_at_top_prompt_visible]` + `tpad=stop_mode=clone:stop_duration=(freeze_duration − 0.05)`
- `raw_tail` = `raw[T_raw_tail_start : end_of_raw]`
- Concat `tc_pre + freeze + raw_tail` → overwrite intermediate

Then run `zoom.py` on rebuilt intermediate. z0b's ease-out plays over still scene; remaining 1.0s of tpad freeze + 1.0s of raw natural hold = 2.0s Rule #27 hold; raw scroll-down plays naturally.

**cap_dead interaction.** When Rule #29 fires, extend `cap_dead`'s `protect_until_t = z0b.source_t + z0b.duration + 1.0s` (= end of tpad freeze past z0b end).

**No-op:** skip if no manifest, no `scroll_to_top_done`, no z0b, or `raw.mp4` missing.

Logged: `decisions/2026-05-31-zoom-out-over-still-and-raw-tail-stitch.md`.

---

## Hard Rule #30 — Static-placeholder gateway: before authoring z0b and choosing the loading-window scrub treatment, run a tick-detection probe on the Progress sidebar.

**Scope:** automated captures, both pipelines. Runs at Phase 3 start (step 3.5), BEFORE tick detection and Variant A/B selection.

If ZERO real ticks detected (Cowork's static-placeholder UI mode), skip z0b entirely AND compress the loading window to a fixed 3.0s flash. If ≥1 ticks detected (Cowork's dynamic-checklist UI mode), proceed with the standard z0b + tick-cut workflow.

**The probe.** `python3 tools/static_gateway.py "<recording>" "<manifest>" --in-place --out-meta /tmp/<slot>_r30.json`. The shared module probes the Progress sidebar over `[streaming_started, streaming_ended]`, filters peaks by magnitude (≥3.0 = real checkmark, <3.0 = noise), branches static vs dynamic.

**Static-path action.** Three operations applied as one rebuild:

(a) **Omit z0b from `zooms.json`** entirely. Tools handle missing z0b cleanly.

(b) **Time-warp the loading window to a 3.0s flash** via ffmpeg pre-cut on raw.mp4. The 3s segment shows actual loading content (tool calls firing, brief generation, scroll-up) at high speedup — not a static freeze. Implementation uses raw.mp4 (not trimmed.mp4) to avoid the auto-trim seam. Warp ends at `t_at_top_prompt_visible = scroll_to_top_done − 0.5s` (Rule #27 (b) cowork-snap-aware), not at `scroll_to_top_done` itself.

(c) **2s at-top hold after the warp** (composes Rule #30 with Rule #27). A 50ms slice of `raw[t_at_top_prompt_visible]` is padded via `tpad=stop_mode=clone:stop_duration=1.95` between the warp and the natural continuation. This guarantees the viewer sees the prompt + brief at top of chat for 2 full seconds before scroll-down begins — same requirement as Rule #27 on the dynamic path, applied here too. Natural continuation then plays from `raw[t_at_top_prompt_visible + 0.05]` so the snap + scroll-down + outro flow without seams (Rule #27 (c)).

**Why 3.0s.** Calibrated as the minimum that registers "Claude is working" without reading as a jump cut. Less than 2s feels instant; 3s is the floor for "the work happened, here's the snippy version." If `loading_dwell ≤ 3.0s` already, skip the pre-cut.

**Dynamic-path action.** Proceed with the existing pipeline (z0b authored per #23, Variant A/B per Phase 3 step 6a, Rules #27 + #29 apply).

**Composition with Rule #27.** Rule #27's at-top hold (2s + prompt visible + natural continuation) is BAKED INTO the static-path rebuild (step (c) above). The flow is: warp ends at the prompt-visible at-top moment → 2s freeze of that frame → natural raw plays forward. Rule #29 (z0b-ease-out-over-still + raw-tail stitch) doesn't fire on static path — no z0b — but the spirit of Rule #29 (smooth transition into natural continuation) is preserved via step (c)'s `t_at_top_prompt_visible + 50ms` post-segment start.

**No-op:** skip if probe errors (default to dynamic — safer), if `T_typing_end` or `T_brief_landed` can't be determined, or `loading_dwell ≤ 3.0s`.

Logged: `decisions/2026-06-01-static-placeholder-gateway.md`. Companion to Hard Rule #23 (parallel branch on a different axis — manifest presence vs tick-count) and Hard Rules #27 + #29 (both no-op on static path).
