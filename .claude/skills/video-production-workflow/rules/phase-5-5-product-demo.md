# Phase 5.5 rules — Apply zoom (product-demo)

Read these when invoking Phase 5.5 (zoom) for V<N> / I<N>. Cross-load `meta.md` + `phase-1.md` (#3 LTs into beat windows). Phase 5.5 has the most rules — they all govern how `tools/zoom.py` is invoked.

---

## Hard Rule #9 — Pause-zoom segments are sized by the beat sheet, never by runtime deficit.

Each dwell:y beat with a settled visual gets one zoom whose duration matches the beat's locked seconds and whose region is the bounding box of *what the VO names in that beat*. If three dwell:y beats discuss three regions, that's three zooms — not two stretched to fill the deficit. If the resulting runtime doesn't match the originally planned composition target, re-lock the beat sheet explicitly or accept the new runtime. Never compress, expand, or invent zoom durations to make the math work.

---

## Hard Rule #10 — Pixel-bound zoom inputs are measured, never eyeballed.

Any zoom-pipeline value that names a specific position in the source frame — `highlight_region_pct` for annotate-mode spotlights, search regions for tick detection, etc. — is derived programmatically from the scrubbed recording's pixels at the relevant `source_t`, never typed in by hand. Project-local tools: `tools/measure_highlight.py` for annotate highlights, `tools/detect_ticks.py` for tick events. Don't ship hand-tuned pixel values, ever — re-measure once per video and paste the output into the JSON. Per-video calibration is a one-command operation, not a re-tuning session.

---

## Hard Rule #11 — Freeze-frame and zoom-rendered segments must stay in the same colour space as the source playback.

When a zoom pipeline interleaves "freeze on a still" segments (zoom-on-held-frame, pre-zoom holds, post-zoom holds) with source playback, the still-derived segments must NOT round-trip through RGB. A YUV→RGB→YUV round-trip via PNG introduces ~1-2 luma units of brightness shift even with explicit colour-space flags, because libswscale's bidirectional conversions aren't perfectly symmetric in 8-bit precision. The visible result: the freeze frame looks slightly darker (or lighter) than the source playback, with a perceptible "pop" at the boundary.

Fix: extract the freeze frame as a single-frame YUV mp4 (preserving the source's `pix_fmt`, `colorspace`, `color_primaries`, `color_trc`, `color_range`) and stream-loop it rather than reading a PNG. All segments must encode with the same explicit colour metadata. `tools/zoom.py` enforces this via single-frame mp4 extraction and `-color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv` on every encoding step.

---

## Hard Rule #12 — The zoomed recording is the canonical timeline for downstream artifacts — re-derive after every re-zoom or re-scrub.

Once Phase 5.5 produces a zoomed recording, that is the timeline LTs, annotation panels, captions, script timing markers, and the composition template all reference. The beat sheet's target seconds were inputs to Phase 3 + 5.5, not outputs. If you re-run zoom (different durations, regions, pre_zoom_hold, `--clean-source-ranges`) or re-run scrub, the zoomed recording's beat windows shift — and every downstream artifact must be re-derived against the new zoomed recording.

Symptom of getting this wrong: LTs land on the wrong content, or annotation panels fade in BEFORE their corresponding zoom-in fires.

**Discipline:** after every `tools/zoom.py` rerun, re-read the "segment timing in zoomed file" output and re-align every script-frontmatter `lower_thirds[].in/out_recording_t` AND `annotations[].in/out_recording_t` against it.

---

## Hard Rule #16 — Hold-mode and annotate-mode zooms targeting OUTPUT BRIEF content must not trigger while the cursor is sitting on readable text in that area.

A pause-zoom that holds a still frame with the cursor obscuring the content the viewer is supposed to read defeats the purpose of the zoom. Wait until the cursor has moved off the readable column (or below/above the visible reading area), then trigger.

**SCOPE:** applies only to zooms targeting the rendered output brief content. Does NOT apply to zooms targeting tool-call loading sections.

Encoded in `tools/zoom.py` via the `wait_cursor_clear: true` flag on output-brief zoom directives (default off — opt-in per directive). When set, the tool auto-advances `source_t` until cursor detection confirms the cursor is outside the cursor-clear region (fallback after `DEFAULT_CURSOR_CLEAR_MAX_DELAY_S = 4s`).

**Cursor-clear region per mode:** hold-mode uses `region_pct` (focal centroid). Annotate-mode uses a synthetic region combining `highlight_region_pct`'s x extent (the readable column) with `zoom_region_pct`'s y extent (the full vertical reading area).

**Known limitation:** the detector uses inter-frame motion centroid; a fully-static I-beam parked on text won't be detected. Mitigation: re-record with deliberate cursor moves off the brief between content beats.

Logged: `decisions/2026-05-18-cursor-clear-rule.md`, `decisions/2026-05-19-cursor-clear-region-broader.md`.

---

## Hard Rule #17 — Annotate-mode spotlights must land within the composition's vertical safe zone — comp y=30% to y=70%.

For every `mode: "annotate"` directive, the soft-edged elliptical spotlight's comp-space y position (computed via the zoom_region transform from `highlight_region_pct.y + h/2`) must fall within [30%, 70%]. The visual contract: the annotation panel on the right and the spotlighted content on the left share a common eye-resting region.

**ENFORCEMENT:** compute `comp_y = (highlight_y_center − zoom_region.y_offset) / zoom_region.height × 100`. If `30 ≤ comp_y ≤ 70`, acceptable. Otherwise, choose a different `source_t` (scroll into the band) OR shift/widen `zoom_region` OR split into sub-annotates with different source_t per Hard Rule #24.

**For sub-annotate clusters:** prefer ONE source_t + ONE zoom_region across the cluster so the camera holds still and only the spotlight moves between rows. Algebra: for a cluster spanning source y from `y_min` to `y_max`, a single zoom_region centers it iff `height ≥ (y_max − y_min) / 0.4`.

`tools/zoom.py` enforces the aspect check + y_offset clamp (prevents black bands).

The default annotate visual is a soft-edged elliptical spotlight — no rectangle border, no numbered dot beside the highlight.

Logged: `decisions/2026-05-25-spotlight-vertical-safe-zone.md`.

---

## Hard Rule #18 — Overlay animations synced to a camera move must share the camera's ease curve.

When an annotation panel, lower third, or any overlay graphic fades/slides in lockstep with a camera move, both motions must use the same easing function. If camera uses `easeInOutSine` and overlay uses `power2.out`, at progress 0.25 the camera is at ~15% while overlay is at ~44% — visibly out of phase.

`tools/zoom.py` uses `easeInOutSine` (corresponds to GSAP `"sine.inOut"`). `templates/product-demo/index.html` `annotatePanel()` uses `ease: "sine.inOut"` for both in/out animations. The overlay's in/out duration matches the camera's ease duration (default 1.0s for annotate). If a future template changes the camera ease in `tools/zoom.py`, change the matching overlay ease in the same commit.

Logged: `decisions/2026-05-20-overlay-ease-matches-camera.md`.

---

## Hard Rule #19 — Source segments between annotate holds must be cleaned of held/duplicate frames before render.

After Phase 5.5 produces the zoomed recording, the `seg_src_NN.mp4` segments between annotate holds play through at scrubbed speed. If the scrubbed source has held frames shorter than `tools/scrub.py`'s `min_dead_seconds` threshold (default 5s), they remain frozen frames in the zoomed file's source-playback segments, perceived as "lag" or "stuttering."

**Fix:** pass `--clean-source-ranges "S1:E1,S2:E2,..."` to `tools/zoom.py`. zoom.py runs `mpdecimate` on those segments, dropping consecutive duplicate frames. Natural-motion frames are preserved.

**Default invocation:** for three annotates at source_t = a, b, c with prior cursor d, pass `"d:a,a:b,b:c"`. After cleaning, the segment timing in the zoomed file shifts — re-derive timings per Hard Rule #12.

Logged: `decisions/2026-05-20-clean-source-segments.md`.

---

## Hard Rule #22 — The prompt-typing follow-zoom (z0) ease-out STARTS at T_click.

The first zoom directive in every product_demo is a follow-mode zoom on the chat input box during prompt typing. Its `duration` field equals `T_click + ease_out_duration` where `T_click` is the scrubbed timestamp at which the cursor clicks the send button (visually identical to the moment the Progress sidebar first appears).

Setting `duration` to "where the click happens" (ease-out COMPLETES at the click) produces a premature retraction. Correct pattern: camera HELD during typing AND cursor-to-button transit AND the click itself, then the click TRIGGERS the retraction, which plays out during the first 1.5s of loading.

**Identification protocol:** during Phase 3 audit, sample raw frames at 0.2s intervals around the expected click moment; `T_click` = first frame where the Progress sidebar response is visible.

**For V2:** `T_click_raw = 7.0s`, ease=1.5s, typing_factor=1.0 → `z0.duration = 7.0/1.0 + 1.5 = 8.5s`.

The same `T_click_raw` value flows into three places in lockstep:
- `tools/scrub.py --force-speed-range "0:T_click_raw:<typing_factor>"`
- z0 directive's `duration = (T_click_raw / typing_factor) + ease`
- `z0b.source_t = (T_click_raw / typing_factor) + ease` (z0b starts immediately after z0 ends)

When Hard Rule #21 zone (a)'s adaptive typing speedup applies (raw typing >10s), `typing_factor > 1` and z0/z0b sizing uses the scrubbed-time post-speedup duration. Example: T_click_raw = 20s, typing_factor = 2.0, ease = 1.5 → `z0.duration = 20/2.0 + 1.5 = 11.5s`.

**`ease` is standardized to 1.5s** per Hard Rule #28. Scrubbed buffer 1 must accommodate this (≥ 4.0s = z0.ease + Rule #31 gap + z0b.margin); if scrub compression brings it below floor, Hard Rule #28's Phase 3 freeze-frame failsafe extends it.

**Cross-pipeline scope (added 2026-06-03):** Rule #22 applies to BOTH pipelines. The product-demo implementation is hand-authored zooms.json sized per this rule. The news-pipeline implementation is in `news-pipeline/tools/process.py::_rule_22_override_auto_zooms()` — it rewrites `tick_cut.py`'s auto-emitted `auto_zooms.json` to enforce `z0.duration = typing_end_scrubbed + ease`. See `phase-3-news.md` "Hard Rule #22 (news mechanism)" for details. The news override exists because `tick_cut.py` originally emitted `z0.duration = pre_output_dur + ease` (extending z0 through the entire pre-tick segment), which silently violated Rule #22 for news captures.

Companion to Hard Rule #21, Hard Rule #28, and Hard Rule #31 (gap between z0 and z0b). Logged: `decisions/2026-05-22-zoom-skeleton-standardization.md`, `decisions/2026-05-29-product-demo-adaptive-typing-speedup.md`, `decisions/2026-05-30-buffer-1-minimum.md`, `decisions/2026-06-03-zoom-out-moment-and-buffer-1-compression.md`.

---

## Hard Rule #23 — Every product_demo zoom plan instantiates the standard skeleton: z0 + z0b + z1..zN.

The three parts:

- **z0** (`mode: "follow"`): camera scales into chat input box during typing. Region = the prompt input rect. Duration = loading-segment boundary T (Hard Rule #22). Standard region for Cowork chrome: `[40, 24, 38, 11]`.

- **z0b** (`mode: "follow"`): camera scales into top-right Progress sidebar **starting at the scrubbed-t where the checklist becomes fully visible** — `z0b.source_t = T_first_tick − margin`. NOT a fixed offset after z0 ease-out. Region = the Progress sidebar rect. Standard region for Cowork chrome: `[80, 0, 20, 30]`, zoom 2.5×. **Ease ≤ margin** (default `margin = 1.0s` → `ease = 1.0s`); guarantees ease-in completes when `T_first_tick` fires.

  **Variant A — Manual screen recording** (no `manifest.json`). Eases out **starting at `T_(N-1) + margin`**. The viewer watches the brief progressively load in the chat area as the camera moves to full frame. The final synthesis tick fires DURING the ease-out. Sizing: `z0b.duration = (T_(N-1) + margin) − z0b.source_t + ease_out_duration`. With `source_t = T_first_tick − margin` and `ease = ease_out = margin`: `duration = (T_(N-1) − T_first_tick) + 3·margin`. If N=1, ease-out starts at that tick + margin. If N=0, skip z0b entirely.

  **Variant B — Automated capture** (`manifest.json` + `phases.scroll_to_top_done` set). Phase 3 pre-cuts `[T_N + post_synth_buffer, T_brief_landed]` (default `post_synth_buffer = 1.0s`). z0b ease-out starts at the scrubbed-time boundary where post-brief locked zone begins (= at-top frame's scrubbed position). Brief progressively rendering is HIDDEN. Sizing: `z0b.duration = at_top_frame_scrubbed_t − z0b.source_t + ease_out_duration`. The at-top frame's scrubbed time = `scrubbed_duration − (raw_end_t − T_brief_landed_raw)`.

- **z1..zN** (`mode: "annotate"`): one annotate per content item the VO names during a `dwell:y` beat (see Hard Rule #24 — multi-VO-target beats split into multiple sub-annotates).

**Tick-window compression (gap-cut rule, V1 ±margin pattern):**
- For every dead segment inside the locked tick window: if gap > 2s, compress by keeping `margin` seconds adjacent to each boundary tick (default `margin = 1.0s`). If gap ≤ 2s, leave alone.
- **Pre-first-tick** (gap > 2s): keep `[T1 − margin, T1]`.
- **Between-tick** (gap > 2s): keep `[T_a, T_a + margin] + [T_b − margin, T_b]`.
- **Post-last-tick** (gap > 2s): keep `[T_(N-1), T_(N-1) + margin]`.
- Locked tick window in `scrub.py` must extend: `[T_first_tick − margin, T_(N-1) + margin]`.

**z0b sizing under ±margin rule:** ease-in must complete BEFORE T1 fires. Ease-out STARTS at `T_(N-1) + margin`.

Skipping z0b: only with explicit user sign-off, or when Hard Rule #30 detects static-placeholder mode.

Logged: `decisions/2026-05-22-zoom-skeleton-standardization.md`, `decisions/2026-05-23-tick-window-compression-moves-to-phase-3.md`, `decisions/2026-05-24-z0b-starts-on-checklist.md`, `decisions/2026-05-29-automated-post-tick-cut.md`.

---

## Hard Rule #24 — Annotate highlight regions are tight bounding boxes of the *specific text the paired VO line names* — measured via `tools/measure_highlight.py`.

Specialisation of Hard Rule #10 for `mode: "annotate"` highlights.

**Three-tier height band** (per `decisions/2026-05-25-highlight-three-tier-band.md`):

| Tier | What VO names | Height | Resolution |
|---|---|---|---|
| 1 | Specific row / cell / phrase | ≤15% | Tight bounding box, single spotlight |
| 2 | Conceptual unit (header + paragraph) | 15–25% | Single spotlight covering the WHOLE unit |
| 3 | Multi-paragraph section / table block | >25% | SPLIT into sub-annotates with shared panel |

**Coupling with panel body length:** long-body panels (>15 words) pair with tier-1 tight spotlights. Short-body or bare-callout panels pair with tier-2 wider spotlights.

Every annotate's `highlight_region_pct` is snapped via `python tools/measure_highlight.py "<recording>" <source_t> --rough "x,y,w,h" --debug-overlay /tmp/<vN>_hl<N>.png` before render.

**Multi-VO-target dwell beats split into multiple sub-annotates.** A `dwell:y` beat whose VO names multiple discrete content items authors as multiple sub-annotates (z1a, z1b, z1c, z1d), one per named item, NOT one big spotlight. Sum of sub-annotate holds = post-zoom beat duration. Each sub-annotate has its own `callout_number` and panel (or shared panel).

Use `--skip-x` for multi-column highlights (table rows).

Logged: `decisions/2026-05-22-zoom-skeleton-standardization.md`, `decisions/2026-05-25-highlight-three-tier-band.md`.

---

## Hard Rule #25 — Annotate panel-hold duration has a minimum sized to the panel's body word count.

```
min_hold = max(3.0s, body_word_count / 5.0 + 2.0s)
```

Where `body_word_count` = words in the panel's `body` field only (eyebrow + headline + badge + source excluded). `5.0` wps = 300 wpm typical fluent silent reading. `2.0s` = ease-in + ease-out per Hard Rule #18. `3.0s` floor = absolute minimum.

**Sub-annotates sharing a single panel:** the panel-hold is the **sum** of all constituent sub-annotate `duration` values. The minimum applies to that sum.

**Worked examples (300 wpm default):**
| Panel body | Body words | `min_hold` |
|---|---|---|
| No body (bare callout) | 0 | 3.0s (floor) |
| Short body (~10 words) | 10 | 4.0s |
| Medium body (~25 words) | 25 | 7.0s |
| Verbose body (~40 words) | 40 | 10.0s |

**Enforcement:** at Phase 5 (drafting), compute `min_hold` per panel and verify. At Phase 6a, re-check against rendered timeline. If violated: (a) tighten panel body to bare callout, (b) consolidate sub-annotates to shared panel, or (c) extend per-sub-annotate `duration` past floor (triggers Phase-6a backup loop per Rule #6(d)).

**Default for sub-annotate clusters:** shared panel.

Logged: `decisions/2026-05-25-annotate-panel-hold-minimum.md`.

---

## Hard Rule #28 — z0.ease = 1.5s standard + scrubbed buffer 1 ≥2.5s.

`z0.ease = 1.5s` is the codified standard. Scrubbed buffer 1 (typing-end → first-tick in scrubbed time) must be ≥2.5s = z0.ease (1.5) + z0b.margin (1.0). This is the minimum that lets the z0 ease-out chain into the z0b ease-in continuously per Rule #31.

See `phase-3-product-demo.md` for the Phase 3 freeze-frame failsafe that extends scrubbed buffer 1 to accommodate this when needed.

---

## Hard Rule #31 — z0 → z0b transitions continuously (no full-frame gap).

After z0 ease-out completes (Rule #22 — ease-out at T_click), z0b ease-in starts immediately. **No held full-frame state between them.** The Progress sidebar IS the visual focus during loading.

**Concretely:** `z0b.source_t ≈ z0.source_t + z0.duration` in scrubbed time. With z0.ease=1.5 and z0b.margin=1.0 (Rule #28's 2.5s buffer-1 minimum), the eases chain back-to-back: z0 ease-out completes, z0b ease-in starts, camera moves continuously from chat input through full frame transit into Progress sidebar.

**Authoring (product-demo):** size `z0b.source_t = T_first_tick_scrubbed − z0b.margin` per Rule #23. Combined with Rule #22's `z0.duration = T_click_scrubbed + ease`, the gap is `buffer_1 − 2.5`. Rule #28's 2.5s minimum makes this 0 by default (eases meet).

**Phase 6b lint check:** `(z0b.source_t) - (z0.source_t + z0.duration) ≤ 1.0` (small leeway; anything bigger is a held-still gap that defeats the sidebar-as-focus principle).

**Why no full-frame held state:** Rule #31 was originally codified (2026-06-03 morning) as REQUIRING a 1.5s held gap, then reversed the same day after user feedback: "Why didn't we zoom in on the top right and use that as the scrubbing process for the loading segment." Held full-frame view defeats the camera focus on the active checklist.

**News implementation:** see `phase-3-news.md`. `AUTO_ZOOM_Z0_Z0B_GAP_S = 0` in `tick_cut.py`; Rule #22 override sets `z0b.source_t = z0.duration`.

Logged: `decisions/2026-06-03-zoom-out-moment-and-buffer-1-compression.md` (codification + same-day revision).

---

## Hard Rule #29 (Phase 5.5 / pre-zoom rebuild) — z0b ease-out over still + raw-tail stitch.

For automated captures with z0b in zooms.json, Phase 3 dispatch rebuilds the scrubbed intermediate before `zoom.py` runs. Full mechanism documented in `phase-3-product-demo.md`. By the time Phase 5.5 fires, the rebuild has already happened and zoom.py just consumes the rebuilt intermediate.
