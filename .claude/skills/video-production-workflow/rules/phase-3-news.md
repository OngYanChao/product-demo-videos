# Phase 3 rules — news-pipeline (conform recording)

Read these when running the news-pipeline's `process.py` (scrub → tick_cut → zoom). Cross-load `meta.md` + `phase-2.md` (for #26 cap).

News-pipeline has no separate Phase 5 script-writing phase — `process.py` handles scrub + tick_cut + zoom auto-emitted from `tick_cut.py`. Most of the Phase 3 logic is encoded in `news-pipeline/tools/process.py` directly. These rules document the editorial invariants.

---

## Hard Rule #20 — Tick timestamps must be detected programmatically.

Same rule as product-demo. In news, `tick_cut.py` runs `detect_ticks.py` internally over the loading window in the Progress sidebar region. The gap-cut keep_ranges are emitted to `trimmed_scrubbed_tickcut.ticks.json` and applied via ffmpeg trim+concat to compress inter-tick waits.

Logged: `decisions/2026-05-21-detect-ticks-programmatic.md`.

---

## News Rule N2 — Prompt-typing segment is speedup-OK, never cut.

News-pipeline scope only. `tapered_with_cut` and any frame-drop treatment forbidden in the `[0, streaming_started]` window; uniform speedup at anchor speed (2×) is the right knob. Diverges from product-demo Hard Rule #21 (typing at 1×) because news videos have a tighter runtime budget and the typing window is context, not load-bearing script content.

**Auto-enforced:** `capture.py` records `phases.streaming_started`; `process.py::_derive_typing_force_range()` reads it and prepends `--force-speed-range "0:X:2.0"` to `scrub.py`. Per-run opt-out: `--no-typing-speedup`.

Logged: `decisions/2026-05-29-news-typing-never-cut.md`.

---

## Hard Rule #22 (news mechanism) — z0 ease-out STARTS at typing-end.

Cross-pipeline rule (full text in `phase-5-5-product-demo.md`). The principle: z0 ease-out begins right after the prompt fires and plays out during the first 1.5s of loading. Camera held during typing + click; click triggers retraction.

**News implementation:** `tick_cut.py` initially emits `z0.duration = pre_output_dur + ease` (which would extend z0 through the entire pre-tick segment — typing + buffer 1 + brief loading). After tick_cut runs, `news-pipeline/tools/process.py::_rule_22_override_auto_zooms()` rewrites `auto_zooms.json` to enforce Rule #22:
- `z0.duration = typing_end_scrubbed + ease` where `typing_end_scrubbed = streaming_started_raw / TYPING_SPEEDUP_FACTOR` (accounting for Rule N2's 2× speedup)
- `z0b.source_t` adjusted to `first_tick_compressed - z0b_margin` (so z0b ease-in completes at first tick per Rule #23)
- `z0b.duration` adjusted to preserve the tick-montage end position

**No-op conditions:** override skips if (a) manifest missing, (b) `streaming_started` absent, (c) computed gap between z0 end and z0b start would be <0.5s (recording's buffer 1 is naturally tight enough), or (d) z0b would be too short after shift (<2×ease).

Logged: `decisions/2026-06-03-zoom-out-moment-and-buffer-1-compression.md`. Companion to Rule N3 (buffer-1 compression — makes the override's `first_tick_compressed` predictable) and Rule #31 (the full-frame gap the override creates).

---

## Hard Rule #23 (news variant) — z0 + z0b auto-emitted by tick_cut.py.

News doesn't author zooms by hand. `tick_cut.py` after tick detection emits an `auto_zooms.json` with:
- **z0** (`mode: "follow"`): chat-input follow during prompt typing. `source_t=0`, initial `duration = pre_output_dur + ease`, **then overridden by Rule #22** to `typing_end_scrubbed + ease`.
- **z0b** (`mode: "follow"`): Progress sidebar follow during the tick montage. `source_t` = z0 end + `AUTO_ZOOM_Z0_Z0B_GAP_S` (1.5s gap per Rule #31), **then adjusted by Rule #22 override** to first_tick - margin.
- Region `[80, 0, 20, 30]`, zoom 2.5×.

`auto_zooms.json` is then consumed by `zoom.py` to apply the camera moves. If 0 ticks detected (Rule #30 static path), `tick_cut.py` skips z0b emission entirely.

---

## Hard Rule #31 — Camera focus on the checkmark phase only (continuous z0 → z0b transition, pre-tick buffer compression, last-real-tick anchoring).

**Three mechanisms applied together to the loading window** — from submit-click to brief-landed. Together they produce a tight "camera lands on sidebar exactly when ticks begin firing, then retracts shortly after the last tick, BEFORE Cowork's auto-scroll-through-brief animation starts." Cowork's auto-scroll-through is then hidden by Rule #29's freeze frame; the viewer only sees capture.py's explicit smooth-scroll read-through that comes from the raw tail.

**Mechanism 1 — Camera move plan (no full-frame gap):**
After z0 ease-out completes (per Rule #22), z0b ease-in starts immediately. No held full-frame view between them. The camera reads as one continuous motion from chat input → full frame transit → Progress sidebar.

- Code: `tick_cut.py`'s `AUTO_ZOOM_Z0_Z0B_GAP_S = 0.0` + `_rule_22_override_auto_zooms()` sets `z0b.source_t = z0.duration`.

**Mechanism 2 — Pre-tick buffer compression (source edit):**
Cut the dead time in scrubbed.mp4 between typing-end and first-tick so first_tick fires exactly at z0b's ease-in completion. Camera arrives on the sidebar AS ticks begin, not before.

- **Target:** `first_tick_scrubbed = typing_end_scrubbed + 2 × ease = typing_end + 3.0s`
- **Code:** `process.py::_compress_pre_tick_buffer()`, between scrub.py and tick_cut.py
- **Algorithm:**
  1. Read `typing_end_scrubbed = manifest.streaming_started / TYPING_SPEEDUP_FACTOR` (per Rule N2's 2× speedup).
  2. Probe `scrubbed[typing_end, scrubbed_dur]` via `detect_ticks.py` (region 80,0,20,30; `--expected-ticks 20`).
  3. Filter peaks by `magnitude ≥ 10.0` (separates real checkmarks from noise).
  4. `first_tick_scrubbed` = lowest-t qualifying peak.
  5. If `buffer-1 > 3.0s`, trim `[typing_end + 0.2s, first_tick − 2.8s]` from scrubbed via ffmpeg trim+concat. Post-trim: first_tick lands at typing_end + 3.0s.

**Mechanism 3 — Last-real-tick anchoring (z0b duration sizing):**
Size z0b so its ease-out completes `held_buffer_s` (= 1.0s default) AFTER the LAST real checkmark tick fires. Camera retracts shortly after the visible tick activity, BEFORE Cowork's auto-scroll-through-brief animation begins. Brief-landing happens during the ease-out window — and Rule #29's freeze frame covers the source content there, so the viewer never sees Cowork's noisy auto-scroll-through.

- **Target:** `z0b.duration = last_real_tick_t + held_buffer_s + ease − z0b.source_t`
- **Code:** `process.py::_rule_22_override_auto_zooms()` after `tick_cut` runs
- **Algorithm:**
  1. Read `trimmed_scrubbed_tickcut.ticks.json` (written by `tick_cut`'s detect_ticks pass).
  2. Identify `brief_landed_t` = lowest-t peak with `magnitude ≥ 100` (the uniquely high-mag pixel-change as Cowork transitions sidebar → doc panel). May be absent for short queries.
  3. Identify `real_ticks` = peaks with `5 ≤ magnitude < 100` AND `t > typing_end_scrubbed` AND (`t < brief_landed_t` if brief_landed exists). This filter excludes: typing-zone false positives, sub-tick noise (mag < 5), brief-landed snap, post-brief scroll content peaks (which can register at mag 20-40 if camera region overlaps doc scroll).
  4. `last_real_tick_t = max(t_tick for t in real_ticks)`. Anchor z0b end to `last_real_tick_t + held_buffer_s + ease`.
- **Fallback if no real ticks found:** `z0b.duration = 2 × ease + held_buffer_s` (= 4.0s with defaults). Camera still does the sidebar move briefly, no tick anchoring.

**Why all three mechanisms together:**
- Without M1: full-frame view between zooms breaks continuity.
- Without M2: camera lands on an empty sidebar before any ticks fire — empty-sidebar dead time.
- Without M3: camera held too long, source advances past the checkmark phase into Cowork's auto-scroll-through-brief animation — viewer sees the brief auto-scrolling under a held zoom.
- With all three: chat-input zoom retracts → camera moves to sidebar → first tick fires AS camera lands → ticks fire visibly → camera retracts shortly after last tick → brief lands during ease-out (covered by Rule #29 freeze) → at-top hold → capture.py's smooth scroll-through plays.

**No-op conditions:**
- M1: always applies (no-op when manifest absent).
- M2: no-op when buffer-1 already ≤ 3.0s, manifest missing, or no ticks ≥ 10 mag found.
- M3: falls back to fixed 4.0s when no real ticks found.

**Scope:** news-pipeline only. M1 generalizes (also applies to product-demo manual via Hard Rule #28's buffer-1 minimum), but M2 + M3 both require a manifest with `streaming_started` and an automatic `tick_cut` pass — neither exists in product-demo manual.

**Rationale & history:**
- 2026-06-03 morning: Rule #31 codified with a 1.5s held-still full-frame gap.
- 2026-06-03 same day: reversed to "no full-frame gap" after user feedback ("Why didn't we zoom in on the top right and use that as the scrubbing process for the loading segment").
- 2026-06-05: merged the previously-separate Rule N3 (buffer-1 compression) into Rule #31 as mechanism 2. Target reduced from 4.0s to 3.0s.
- 2026-06-05 (later): added mechanism 3 (last-real-tick anchoring) after observing that anchoring z0b end to brief_landed instead allowed Cowork's auto-scroll-through-brief animation to play visibly during z0b held. Mechanism 3 retracts the camera before that animation begins, leaving it hidden behind Rule #29's freeze.

Logged: `decisions/2026-06-03-zoom-out-moment-and-buffer-1-compression.md`. Companion to Rule N2 (typing speedup), Rule #22 (z0 ease-out at typing-end), Rule #29 (freeze frame covers z0b ease-out window — hides brief-landing transition that happens during retraction), and Rule #30 (static path bypasses M2 + M3).

---

## Hard Rule #27 (news) — At-top frame must be held for ≥2.0s + prompt visible + natural continuation.

Same as product-demo Hard Rule #27 (see `phase-3-product-demo.md`), but applied to news's `trimmed.mp4`. Primary mechanism: `capture.py::POST_SCROLL_TOP_HOLD_S = 2.0s`. Failsafe: Phase 3 freeze-frame inject (runs in `news-pipeline/tools/process.py`).

---

## Hard Rule #29 (news) — z0b ease-out over still + raw-tail stitch (auto-applied).

Same as product-demo Hard Rule #29 (see `phase-3-product-demo.md`). For news, the rebuild runs in `news-pipeline/tools/process.py::_rule_29_rebuild()` between `tick_cut.py` and `zoom.py`. The intermediate is `trimmed_scrubbed_tickcut.mp4`.

**cap_dead interaction:** when Rule #29 fires, `process.py` extends `cap_dead`'s `protect_until_t` by 1.0s to preserve the tpad freeze past z0b end (= half of the Rule #27 hold; the other half is the 1.0s normalized natural hold in the stitched raw tail).

Logged: `decisions/2026-05-31-zoom-out-over-still-and-raw-tail-stitch.md`.

---

## Hard Rule #30 (news) — Static-placeholder gateway: auto-applied in process.py before scrub.

Same as product-demo Hard Rule #30 (see `phase-3-product-demo.md`). For news, the gateway runs in `news-pipeline/tools/process.py` via `from static_gateway import run_gateway` BEFORE scrub.

If static detected, `trimmed.mp4` is rebuilt in-place with: pre + 3s time-warp + **2s at-top hold (Rule #27)** + natural continuation. The at-top hold ensures the prompt + brief are held still for 2s before the scroll-down begins — same Rule #27 requirement as the dynamic path, applied here too.

Logged: `decisions/2026-06-01-static-placeholder-gateway.md`.

---

## News-only cap-dead (the deprecated N1 case b)

The trailing dead-time between scroll-down completion and the Polaris outro is still capped by `news-pipeline/tools/tick_cut.py::cap_dead_times()` — news-only because product-demo's annotate dwells (Hard Rule #25) would be destroyed by it. Triggered by `process.py` after `zoom.py` runs.
