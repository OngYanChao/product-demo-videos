---
name: parallax-video
description: Orchestrator for the Parallax video production pipeline (Hyperframes-based local render with HeyGen avatar clip). Drives the 20-video persona-and-moment-driven master plan — 4 instructional (I1–I4) + 16 use_case (V1–V16) organized around `primary_persona × primary_moment × deliverable`. Use whenever the user wants to scrub a recording, extract frames, write a script, apply post-script zoom (measure highlights + run tools/zoom.py), render a preview ($0), render a final cut (HeyGen avatar credits), debug a render, or clean up scratch artifacts after a final ships. Drafting must follow `video-scriptwriting` craft rules and `video-production-workflow` methodology, and ground every cited stat in the master plan, the scrubbed recording's frames, or `parallax-obsidian/` vault files. No hallucination. Renderer is local Hyperframes — HeyGen is only invoked for the avatar talking-head clip. Pipeline ordering: scrub → frames → script → zoom (Phase 5.5) → render. Intel-brief style is shelved as a deferred future addition (infrastructure preserved, no template built).
---

# parallax-video

Drives the full per-video pipeline. One stream (product_demo, recording-driven), one orchestrator, free preview iteration, billable final render only at the last step.

| Stream | Input | Use case |
|---|---|---|
| **product_demo** | Screen recording of Parallax running | The 20-video master plan: **4 instructional (I1–I4)** audience-general utility content + **16 use_case (V1–V16)** persona-and-moment-driven product demos across Tier 1 (single-feature) / Tier 2 (workflow chain) / Tier 3 (hero playbook) |
| ~~intel_brief~~ | *(shelved)* | Anchor-style market wraps — **paused as a deferred future addition** per overhaul.md Phase 5. Infrastructure (style enum, frontmatter `style:` field) preserved for clean reactivation; no template currently built. |

The product-demo stream produces 1920×1080 60fps MP4s using `templates/product-demo/` (title card → recording with avatar PiP → outro). All 20 videos share this template; the per-video copy + timing is substituted in at render time from each script's frontmatter.

## Architecture (read this once, then dispatch)

| Layer | Tool | Cost |
|---|---|---|
| Renderer | [Hyperframes](https://hyperframes.heygen.com/) — `npx hyperframes render` | Free |
| Avatar talking head | HeyGen `video create -d <json> --wait` via `heygen-video` skill (called internally by `tools/render.py --mode final`) | Per-clip credits |
| Per-video orchestrator | `tools/render.py V<N> --mode preview\|final` | Free |
| Recording cleanup | `tools/scrub.py` | Free |
| Pause-zoom polish | `tools/zoom.py` (script-driven, JSON directives) | Free |
| Tick detection (tail-cut) | `tools/detect_ticks.py` (programmatic, never eyeball) | Free |
| Frame extraction | `tools/extract_frames.py` | Free |
| Cache key util | `tools/script_hash.py` (12-char hex hash of spoken VO) | — |

Cross-references — read these when applicable:
- **Methodology** (beat-sheet first, scrub → script → zoom phase order, dwelling principle, hard rules): `.claude/skills/video-production-workflow/SKILL.md`. Authoritative for "how phases hand off to each other."
- **Craft** (voice composite, banned words, hallucination rule, "show on screen / interpret in VO"): `.claude/skills/video-scriptwriting/SKILL.md`. Authoritative for "how to draft a line."
- **Avatar generation** (HeyGen v3 video pipeline, prompt engineering, voice selection): `.claude/skills/heygen-video/SKILL.md`. `tools/render.py --mode final` invokes the underlying CLI directly with the stock avatar/voice IDs from `.env`; only consult this skill for advanced cases (custom avatars, voice tuning, frame-check overrides).

## Hard rules (production-critical)

1. **Lock the beat sheet before recording or scripting** (product_demo). Sourced from `Parallax Video Plan - MASTER.md` Highlights. The zoomed recording's actual beat windows are the canonical timeline — re-derive LT/script timings after every re-zoom or re-scrub. (Hard Rule #12 in `video-production-workflow`.)
2. **Every on-screen stat traces to a frame, the master plan, the source document, or the vault.** Frames are scratch grounding for product demos — every claim cites a `frames_used:` entry in the script frontmatter. Intel briefs cite the source document. No hallucination.
3. **Renderer is local Hyperframes.** HeyGen is invoked only for the avatar talking-head clip, cached at `avatars/clips/V<N>_<scripthash>.mp4` so identical VO content never re-bills.
4. **Spoken VO lives under `## Voiceover script`, in `> ` blockquotes.** `tools/script_hash.py` only extracts blockquoted lines from that section, with stage-direction lines (`**[bracketed]**`-only) filtered out. Drafting metadata, workflow notes, hallucination logs etc. live in other sections and never reach the avatar.
5. **Pixel-bound zoom inputs are measured, never hand-tuned** (Hard Rule #10 in `video-production-workflow/`). Annotate-mode `highlight_region_pct` via `tools/measure_highlight.py`; tick search regions via `tools/detect_ticks.py`. Hand-tuned coordinates are forbidden.
6. **Tail-cut tick timestamps are detected, never eyeballed.** When a Phase 5.5 zoom compresses a progress-bar / status-checklist loading sequence using the tail-cut technique (keep ±N seconds around each visual tick, jump-cut the dead waits), run `python tools/detect_ticks.py "<recording>" --time-range "<t0>:<t1>" --region-pct "x,y,w,h" --expected-ticks N --tail-seconds 1.0 --output <ticks.json>` and paste `ffmpeg_trim_ranges` directly into the trim+concat filter graph. Hard Rule #20.

## When to invoke this skill

Trigger phrases (and the corresponding tool calls):

| User says | Action |
|---|---|
| "lock V5 beats" / "start V5" | **Phase 1 — Lock beats** (autonomous per memory `feedback_beat_sheet_autonomy.md`; no approval gate). **(1)** Read MASTER.md V<N> section — extract Highlights + beat ordering. **(2)** Convert Highlights into an ordered beat sheet with target seconds per beat. Sum = recording target. For dwell:y beats, target = post-zoom length (Phase 5.5 zoom inserts fill the dwell windows; size VO to that target, not the pre-zoom scrubbed length). **(3)** Mark `dwell: y` for beats that settle into a content-rich still (factor table, score panel, brief paragraph) where Phase 5.5 zoom can dwell. **(4)** Write back into MASTER.md beneath the Highlights subsection — no approval pause; user can rebudget after the fact (e.g., "rebudget V5 beat 4 to 14s"). **Cross-ref:** `video-production-workflow/` Phase 1 + Hard Rule #1 (beat sheet upstream of both recording and script). |
| "capture V5" / "record V5" / "auto-record V5" | **Phase 2 — Automated capture** (optional; manual recording still works — just drop `vid<N>.mp4` into the slot). **(1)** Read `Parallax Video Plan - MASTER.md`, locate the `### V<N>` (or `### I<N>`) section. **(2)** Within that section, find the `**Prompt to type:**` block — extract the verbatim text that follows (typically a quoted string or fenced code block). For instructional videos with multiple prompts in sequence, prompt the user for which one to capture. **(3)** Write the extracted text to `/tmp/V<N>_prompt.txt` via Write. **(4)** Pre-flight: confirm `automation/calibration/claude-desktop.json` exists (if not, point user at `python3 automation/calibrate.py`); remind user Claude desktop must be in macOS fullscreen mode (ctrl+cmd+F). **(5)** Run `python3 automation/capture.py --slot-dir "screen recordings/V<N>" --no-readthrough /tmp/V<N>_prompt.txt` via Bash. The capture script drives Claude desktop via keystroke automation (cliclick), records via ffmpeg at 60fps with 1s keyframes (Hard Rule #15), detects end-of-streaming via the dual-region stop-vs-mic match, settles 1s, then stops recording. `--no-readthrough` skips the news-style scroll-to-top + smooth-scroll-down dance (product-demo wants the brief on screen in its final state, not a scroll read-through). Output: `screen recordings/V<N>/raw.mp4` + `screen recordings/V<N>/manifest.json`. **(6)** Post-rename: `mv "screen recordings/V<N>/raw.mp4" "screen recordings/V<N>/vid<N>.mp4"` to match the project's canonical naming convention (V2+ pattern). **(7)** Inspect `manifest.json` — verify `phases.streaming_started` is present (load-bearing for Phase 3's `T_typing_end` per Hard Rule #21 + #22). **(8)** Surface to user: the slot path, `phases.streaming_started` value, recording duration, sample counts. Auto-chain into Phase 3 scrub — the manifest now provides `T_typing_end` without frame-sampling (see Phase 3 dispatch row's updated step 4). **Pre-conditions:** (a) Claude desktop installed + calibrated via `python3 automation/calibrate.py`; (b) Cowork running; (c) Claude desktop in fullscreen mode; (d) `automation/` infrastructure intact (Pass 1 extraction). **Failure modes:** if capture errors (calibration missing, Claude not frontmost, streaming-end detection times out), fall back to manual recording — drop your own `vid<N>.mp4` into the slot. **Cross-ref:** `automation/README.md` (shared layer + manifest schema), `video-production-workflow/` Phase 2, Hard Rules #15 (60fps), #21 (multi-zone lock — Phase 3 uses the manifest), #22 (z0 sizing — uses `phases.streaming_started` as `T_typing_end`). |
| "scrub vid5" / "scrub V5" / "conform V5 recording" | **Phase 3 — Conform recording (multi-step orchestration; zoom is Phase 5.5, NOT here).** **(1)** Read V<N> beat sheet from MASTER.md (target seconds + dwell:y flags per beat). **(2)** Audit raw `vid<N>.mp4` end-to-end — every beat's content visibly present? If a beat's content is missing, escalate to re-record BEFORE scrubbing. **(3)** Verify 60fps + 1s keyframes via `ffprobe`; re-encode with `-r 60 -g 60 -keyint_min 60` if not (workflow Hard Rule #15). **(4)** **Identify four boundary timestamps in the raw recording** (Hard Rule #21). **If `screen recordings/V<N>/manifest.json` exists** (Phase 2 auto-capture ran), `T_typing_end = manifest.phases.streaming_started − 0.5s` (safety shave, mirrors news's Rule N2 derivation). Skip the frame-sampling for `T_typing_end`. **Otherwise** (manual recording, no manifest), `T_typing_end` = submit-click moment (NOT typing-end; sample frames at 0.5s intervals to find submit-arrow → first sidebar appearance — the boundary). `T_brief_landed` = the raw timestamp where the brief is fully rendered on screen — for auto-capture, this is approximately `manifest.phases.streaming_ended`; verify visually. `T_first_tick` + `T_(N-1)` (penultimate tick) come from step 5 below. **(5)** **Run `detect_ticks.py` on the RAW recording — TWICE** (Hard Rule #20). First pass: broad search `python tools/detect_ticks.py "screen recordings/V<N>/vid<N>.mp4" --time-range "<T_typing_end>:<T_brief_landed>" --region-pct "80,0,20,30" --expected-ticks N --output /tmp/v<N>_all_ticks.json` finds all N ticks including the final synthesis tick. Inspect the output, identify `T_first_tick` = `ticks[0].t_tick` and `T_(N-1)` = `ticks[-2].t_tick` (penultimate). Second pass: scoped search `python tools/detect_ticks.py "screen recordings/V<N>/vid<N>.mp4" --time-range "<T_first_tick>:<T_(N-1)>" --region-pct "80,0,20,30" --expected-ticks N-1 --output "screen recordings/V<N>/vid<N>_ticks.json"` finds only the N-1 non-synthesis ticks and emits `ffmpeg_keep_ranges` derived from the gap-cut rule SCOPED to the penultimate-bounded window. Detection on RAW (not scrubbed) is mandatory — scrub.py's freeze compression squeezes ticks together before they can be measured. **Final synthesis tick is excluded from the locked tick window** per Hard Rules #20+#21+#23 (the synthesis tick fires AFTER the brief renders, so the synthesis zone needs to be compressible buffer, not locked at 1×). **(6)** **Run `scrub.py` with multi-zone 1× lock** (Hard Rule #21): `python tools/scrub.py "screen recordings/V<N>/vid<N>.mp4" --force-speed-range "0:T_typing_end:1.0,T_first_tick:T_(N-1):1.0,T_brief_landed:end:1.0"`. This locks typing + penultimate-bounded tick window + post-brief at 1×; scrub's freeze compression applies to the two buffer zones (post-typing-pre-first-tick = sidebar populating; post-`T_(N-1)`-pre-`T_brief_landed` = synthesis zone where brief progressively renders). Output: `vid<N>_scrubbed_pre_tickcut.mp4`. **(7)** **Apply the gap-cut to the tick window** via ffmpeg trim+concat using the `ffmpeg_keep_ranges` from step 5's second pass. The tick window in `vid<N>_scrubbed_pre_tickcut.mp4` retains the raw tick spacing (locked at 1×); the gap-cut compresses dead segments per the rule. Result is concatenated: `vid<N>_scrubbed.mp4` (canonical). **(8)** Run `python tools/extract_frames.py "screen recordings/V<N>/vid<N>_scrubbed.mp4" frames/V<N>/` (folded with Phase 4). **(9)** Map frame timestamps to beat windows; verify each beat survives with enough visible content for VO. **(10)** Apply decision tree to any failing beats: dwell:y short → defer to Phase 5.5 (zoom fills); non-dwell short → re-record (Hard Rule #13); too-long content motion → uniform 1.5–2× speedup. **(11)** Report: scrubbed duration vs beat-sheet target net of planned zoom inserts (±0.5s); per-beat audit pass/fail; **the four boundaries** (`T_typing_end`, `T_first_tick`, `T_last_tick`, `T_brief_landed`) and the tick timestamps — Phase 5 needs `T_typing_end` for the z0 duration field; Phase 5 + 5.5 need `T_last_tick` for z0b sizing. **Cross-ref:** `video-production-workflow/` Phase 3 + Hard Rules #2, #4, #12, #13, #15, #20, #21, #22. **Memory:** `feedback_pragmatic_mode.md` (zoomed recording is canonical). |
| "extract frames for V5" | **Phase 4 — Frame extraction** (often folded with Phase 3 scrub audit). `python tools/extract_frames.py "screen recordings/V<N>/vid<N>_scrubbed.mp4" frames/V<N>/` — 1 frame / 2s, downscaled to 960px. Outputs JPGs + `index.md` mapping frame # ↔ timestamp. **Audit:** every locked beat's content must be visible in at least one frame. Missing beat content = Phase 3 failure — escalate to re-scrub (different threshold) or re-record. **Re-extraction (Hard Rule #12):** if the scrubbed recording is re-run (different threshold, recording re-encoded), re-extract frames — old timestamps no longer map to correct content. Re-running Phase 5.5 zoom does NOT require re-extraction (zoom doesn't change content, only emphasis). Frames are scratch grounding for Phase 5 hallucination check (workflow Hard Rule #7) — the durable record is `frames_used:` in script frontmatter. **Cross-ref:** `video-production-workflow/` Phase 4 + Hard Rule #4 (recording must visibly contain each beat's content). |
| "detect V5 ticks" / "find the tick timings" / any time a tail-cut treatment is being built | `python tools/detect_ticks.py "screen recordings/V5/vid5_scrubbed.mp4" --time-range "<t0>:<t1>" --region-pct "x,y,w,h" --expected-ticks N --tail-seconds 1.0 --output "screen recordings/V5/vid5_ticks.json"`. Paste the JSON's `ffmpeg_trim_ranges` into the trim+concat filter graph that builds the tail-cut zoom file. **Never eyeball tick timestamps from sampled frames** (Hard Rule #20). For simultaneous ticks (two checklist items tick at the same instant) count as ONE moment when setting `--expected-ticks`. If lines have different visual magnitudes, request more peaks than expected and discard the lowest-magnitude false positives. |
| "snap V5 highlights" / any time a `mode: "annotate"` directive's highlight is cutting words | For each annotate directive: `python tools/measure_highlight.py "screen recordings/V5/vid5_scrubbed.mp4" <source_t> --rough "x,y,w,h" [--skip-x] --debug-overlay /tmp/v5_hl.png` → paste emitted `highlight_region_pct` into `scripts/V5_zooms.json`. Use `--skip-x` when the rough spans multiple columns (e.g., a whole table row); default x-snap is for single-column highlights only. Always inspect the debug overlay before pasting — paragraph-spanning rough rects will snap through the full paragraph since text rows are connected (in those cases, just tighten the rough manually). |
| "zoom V5" / "build V5 zooms" / "apply V5 zoom" | Phase 5.5 — runs AFTER `write V5`. Requires `scripts/V5_zooms.json` (drafted during `write V5`). **Standard skeleton check first** (Hard Rule #23): every product_demo zoom JSON contains z0 (prompt follow) + z0b (Progress-sidebar follow) + z1..zN (annotate per VO-named content item). If any is missing, return to Phase 5. **Pre-zoom calibration** (mandatory): measure every annotate highlight via `python tools/measure_highlight.py "screen recordings/V<N>/vid<N>_scrubbed.mp4" <source_t> --rough "x,y,w,h" --debug-overlay /tmp/v<N>_hl<i>.png` per Hard Rules #10 + #24. **Tick-window compression already happened in Phase 3** (Hard Rule #23 — the gap-cut rule is applied to `vid<N>_scrubbed.mp4` during conform, NOT here as a tail-cut post-process). zoom.py operates against the already-tick-compressed scrubbed file. **Run zoom.py:** `python tools/zoom.py "screen recordings/V<N>/vid<N>_scrubbed.mp4" "screen recordings/V<N>/vid<N>_zoomed.mp4" --zooms "screen recordings/V<N>/vid<N>_zooms.json" --clean-source-ranges "<gaps>"` per Hard Rule #19. The output `vid<N>_zoomed.mp4` is the canonical timeline (no separate `_natural` + `_zoomed` files — there's no Phase 5.5 tail-cut step anymore). `tools/render.py` auto-prefers `vid<N>_zoomed.mp4`. Re-derive LT + annotation timings against the zoomed timeline (Hard Rule #12). **For `mode: "annotate"` directives** (Hard Rule #17, refined by `decisions/2026-05-25-spotlight-vertical-safe-zone.md`): each annotate beat's spotlight must land within the comp's vertical safe zone (y=30%-70%, 40%-wide band). For sub-annotate clusters (Hard Rule #24 multi-VO-target split), prefer ONE source_t + ONE zoom_region across the cluster so the camera stays held still and only the spotlight moves between targets. A single zoom_region works for a cluster spanning source y from y_min to y_max iff `height ≥ (y_max − y_min) / 0.4`. If the cluster's span exceeds 40% of source, split into multiple source_t (accept the scroll between them). The annotate visual is a soft-edged elliptical spotlight centered on `highlight_region_pct` — no border, no numbered dot beside the highlight (panel carries the numbered badge on the right). zoom.py validates `zoom_region_pct` aspect and clamps `y_offset` to prevent black bands. **z0b sizing** (Hard Rule #23, refined by `decisions/2026-05-24-z0b-starts-on-checklist.md`): `z0b.source_t = T_first_tick − margin` (zone-b start in scrubbed — where the checklist first becomes fully visible). `z0b.ease = margin` (default 1.0s; previous ease=1.5 retired). `z0b.duration = (T_(N-1) + margin) − z0b.source_t + ease_out` — ease-out STARTS at `T_(N-1) + margin` (after the 1s post-last-tick settling hold), not at `T_(N-1)` itself. The final synthesis tick fires DURING ease-out — viewer watches the brief progressively load as the camera moves to full frame. **Always pass `--clean-source-ranges` covering every source segment between annotates** (Hard Rule #19). For annotates at source_t = a, b, c with prior cursor d, pass `--clean-source-ranges "d:a,a:b,b:c"`. **After every zoom rerun**, re-read the "segment timing in zoomed file" output and re-align both `lower_thirds[].in/out_recording_t` AND `annotations[].in/out_recording_t` in the script frontmatter (Hard Rule #12). **Panel-hold minimum** (Hard Rule #25): for every annotate directive, verify the paired panel's `duration >= max(3.0s, body_word_count / 5.0 + 2.0s)`. For sub-annotate clusters sharing a panel per Hard Rule #24, sum the cluster's `duration` values and check against the shared panel's `min_hold`. Violations: either tighten panel body, consolidate to a shared panel, or extend `duration` past the floor (which may trigger the Phase-6a backup loop to inflate the beat target in MASTER.md). **Cross-ref:** Hard Rules #10, #12, #17, #18, #19, #22, #23, #24, #25. (Tick detection + tail-cut moved to Phase 3 — see scrub dispatch row + Hard Rules #20 + #23.) |
| "write V5" | **Phase 5 — write punchy draft.** Output is a fragment-heavy "punchy" draft per Hard Rule #6(a) — at this phase you don't have actual post-zoom timings yet, so writing short data-callout lines is conservative. The full-sentence rhythm pass happens at Phase 6a after the preview is rendered (auto-chained — see polish dispatch below). **First, read the script's frontmatter `style:` + `complexity:` fields** — they determine which craft rules apply. Then read locked beat sheet + frames + MASTER.md V5 entry + `templates/product-demo/RENDER-GUIDE.md` + scrub report + `video-scriptwriting/SKILL.md` (Universal craft always applies; the matching style-specific section adds rules on top). Draft `scripts/V5 voiceover script.md`. **Hallucination check** (workflow Hard Rule #7): every on-screen claim cites a frame in `frames_used:`. VO body in `> ` blockquotes under `## Voiceover script`. **For `style: use_case`** — every beat answers the three questions (what is this / what problem / why does it matter to me) with an explicit value-to-viewer clause (see `references/production-principles.md` → *Every use_case beat states value explicitly*). Read `references/value-framing-menu.md` for definitions + value-line shapes. MASTER's `Primary value angles` bullet names the headline moat + supporting standard angles; rotation rule = 5–7 angles per ~90s of content (scales up for Tier 2/3). **Vocabulary lock** (see `references/production-principles.md` → *NL prompts in demo*): VO uses NL prompts verbatim from the recording — never reads slash commands aloud. LT eyebrow / headline names the *product module* (Stock Report, Screener, Analyzer, ETF Analysis, Impact Analysis, Macro Intelligence, Shariah Screen) — never the slash command or MCP tool name. **Customer's-chair framing** (see `references/production-principles.md` → *Customer's-chair framing*): every LT / annotation panel / VO line speaks from the buyer's chair (MFO / RIA / advisor / PM / analyst per the video's `primary_persona`), never from the system's chair. No engineering vocabulary in copy — no "parallel skill calls," "MCP invocations," "agent orchestration," or capability-counts. Every line is outcome / stakes / workflow-fit / methodology-credibility (the four require molds). Enforced as `video-scriptwriting/SKILL.md` use_case Quality Check #9. **Panel content authoring** (see `video-scriptwriting/SKILL.md` § *Panel content authoring*): annotation panels pitch the *capability/workflow/stakes value* of having the spotlit segment in every brief — NOT a literal interpretation of the specific numbers. Three rhetorical shapes (capability / workflow / stakes); no two consecutive panels in same shape. Panel format = eyebrow + headline + body + source + badge (no stats row). Subject-matches the paired spotlight (each panel's topic = the content the spotlight is pointing at). See `video-scriptwriting/SKILL.md` use_case section for the vocabulary-mapping table. **For `style: instructional`** — describe the screen literally in sequence (point-and-click). Value-framing collapses to hook + close only. No per-beat angle rotation. No persona pretense — audience-general utility videos. Slash commands MAY appear in VO when they're the literal action the viewer reproduces (instructional carve-out from the NL-prompts-in-demo decision). **Also at Phase 5: draft `screen recordings/V<N>/vid<N>_zooms.json` directives + skeleton `annotations:` entries in frontmatter, instantiating the STANDARD SKELETON** (Hard Rule #23) — every product_demo zoom JSON contains all four parts:

1. **`z0_prompt_typing`** (`mode: "follow"`): camera on the chat input box during prompt typing. `source_t: 0.0`, `duration: T` (the loading-segment boundary from Phase 3's report — same T as `--force-speed-range "0:T:1.0"`, per Hard Rule #22), `region_pct: [40, 24, 38, 11]` (Cowork chrome default), `zoom: 1.5`, `ease: 1.5`.
2. **`z0b_progress_sidebar`** (`mode: "follow"`): camera on the top-right Progress sidebar during the loading segment. `source_t: T_first_tick − margin` (= zone-b start in scrubbed, the moment the full checklist becomes visible — NOT a fixed ~3s buffer after z0). `ease: margin` (default 1.0s, so ease-in completes exactly when `T_first_tick` fires — the previous `ease: 1.5` is incompatible with `margin: 1.0` and retired). `duration: (T_(N-1) + margin) − source_t + ease_out` — ease-out starts after the post-last-tick settling hold completes, retracting during the brief-rendering animation. `region_pct: [80, 0, 20, 30]` (Cowork chrome default), `zoom: 2.5`. **z0b is mandatory** — skipping requires explicit user sign-off (rare case where the workflow has no tool activity sidebar visible). Logged: `decisions/2026-05-24-z0b-starts-on-checklist.md`.
3. **`z1..zN`** (`mode: "annotate"`): one annotate directive PER CONTENT ITEM the VO names during a `dwell:y` beat. **Multi-VO-target dwell beats split into multiple sub-annotates** (Hard Rule #24): a beat whose VO names Composite + Quality+Def+Tac + Momentum + Value across the factor table authors as FOUR sub-annotates (z1a, z1b, z1c, z1d), each with its own `callout_number` + `highlight_region_pct` tightly bounded on one row — NOT one big spotlight on the whole table. V1's z1+z2+z3 pattern (Value row / trajectory cell / Bottom Line opening) is canonical.

   For each annotate: `source_t` = a moment in the scrubbed recording where the comp y position of the target (after zoom_region transform) lands in the safe zone [30%-70%] per Hard Rule #17 (refined by `decisions/2026-05-25-spotlight-vertical-safe-zone.md`); for sub-annotate clusters, share one source_t + one zoom_region; `zoom_region_pct` = larger context view satisfying aspect; `highlight_region_pct` = TIGHT bounding box of what the VO names (height ≤15%, per Hard Rule #24 — measured via `tools/measure_highlight.py`, never hand-tuned); `callout_number` = global counter; `wait_cursor_clear: true` for output-brief content per Hard Rule #16.

4. **`annotations:` frontmatter entries** — drop a placeholder per annotate directive (in/out_recording_t left as `null` / TBD); exact recording-time values get filled in after Phase 5.5 zoom.py prints the segment timing log.

For tool-call loading sections where the VO orients without reading specific text, use `mode: "follow"` or `mode: "hold"` — annotate-mode is reserved for output-brief callouts.

**On completion, auto-chain into Phase 6a (polish) — no need to ask, immediately proceed to the polish dispatch below to apply sync + beat coverage + rhythm checks against the current zoomed timing.** **Cross-ref:** Hard Rules #16, #17, #22, #23, #24. |
| "write today's intel brief on X" | **Paused** — `intel_brief` style is out of scope for the current overhaul. See `overhaul.md` and `video-scriptwriting/SKILL.md` § *Style: `intel_brief` — PAUSED* for reactivation requirements. |
| "render V5 preview" | **Phase 6 — Preview render** ($0). `python tools/render.py V<N> --mode preview` → `outputs/V<N>/preview.mp4`. Free, ~2.5min wall. Substitutes script frontmatter into the template (16 slots). **Source-recording precondition:** `tools/render.py` auto-prefers `vid<N>_zoomed.mp4` and falls back to `vid<N>_scrubbed.mp4` for early-iteration previews. If dwell:y beats exist, Phase 5.5 zoom should have run before this — otherwise dwell:y windows render at scrubbed length and won't match the VO's planned dwell. **After every re-zoom or re-scrub (Hard Rule #12):** re-derive LT/caption timings in the script frontmatter against the new zoomed recording. Symptom of forgetting: LTs land on the wrong content (trajectory LT appears during score-panel zoom). **Auto-chains into Phase 6a (polish) on completion** — no need to ask, just run `tools/render.py` and immediately proceed to the polish dispatch below. **Cross-ref:** `video-production-workflow/` Phase 6 + Hard Rules #3 (graphics schedule into beat windows, not raw seconds), #12. |
| "polish V5" / "tweak V5" / explicit invocation **OR auto-chained after every "write V<N>" or "render V<N> preview"** | **Phase 6a — Polish pass (auto)**. Runs automatically after every Phase 5 script change AND every Phase 6 preview render — the user does not need to invoke. All editorial judgment (rhythm balance, beat cuts) lives here, not at Phase 5. **Seven steps in order:** (1) **Sync check** — every `lower_thirds[].in/out_recording_t` AND `annotations[].in/out_recording_t` in the script frontmatter matches the actual seg_annotate_NN / seg_src_NN timings from the latest `tools/zoom.py` "segment timing in zoomed file" output (Hard Rule #12). Mismatch = re-derive. (2) **Beat coverage check** — every spoken VO beat maps to a panel/LT/zoom hold; every panel/LT has a corresponding spoken beat. Catch orphaned beats from cuts or reorderings. (3) **Runtime check (branches step 4 vs 5):** measure spoken VO budget (words ÷ 150 wpm) against the speakable window (composition runtime − title − outro − intentional silences − scroll segments). If budget ≤ window → step 4. If budget > window → step 5 (skip step 4 this pass; the cut creates headroom for the next auto-Phase-6a run to use for rhythm). (4) **Rhythm pass (runtime fits)** — count fragments vs full sentences in the VO body. If fragments ≥ 60% of total, restore full sentences in connective/interpretive beats. Target mix for use_case: ~40% data-fragment + ~35% short-sentence + ~25% full-sentence (Hard Rule #6(b)). Earned fragments stay (data callouts, hero shots, factor scores). **Per-beat overflow:** if a single beat's polished VO (estimate punchy + 20–30% words) exceeds its zoom hold duration, trigger backup loop (step 5b). (5) **Beat cut (total runtime overflows)** — drop a whole beat at full rhythm. Selection: lowest-priority beat per MASTER's `Primary value angles` for the video. Re-author surrounding stage directions to bridge the cut. Hard Rule #6(c). **(5b) Backup loop — re-open Phase 1** (per-beat overflow, global runtime still fits) — extend the affected beat's target seconds in MASTER.md by `overflow + 0.5s buffer`, write the new duration into `V<N>_zooms.json`, re-run Phase 5.5 (`tools/zoom.py`), re-run Phase 6 preview render. Auto-Phase-6a fires after the re-render and proceeds normally. Backup loop fires AT MOST once per beat — second trigger = escalate (likely under-estimation or genuine over-scope). Hard Rule #6(d). (6) **LT + panel update (conditional)** — touch LTs and panels only when Phase 5 cut beats, reordered points, OR step 5 just cut a beat. Orphaned LTs/panels from a cut beat get removed. Otherwise leave them — they're locked-format. (7) **Auto-re-render preview** if any edits applied (steps 1, 4, 5, or 6) — and then the chain re-enters Phase 6a recursively (auto-trigger contract). If no changes needed, report "Phase 6a clean" and **auto-chain into Phase 6b (lint)** — see the lint dispatch row below. **Convergence:** the second auto-Phase-6a run after the auto-re-render should be clean. If it's still making edits after two passes, escalate — likely a misidentified check OR an unfixable runtime overflow (re-open Phase 1 beat sheet). **Cross-ref:** `video-production-workflow/` Phase 6a–6c + Hard Rule #6. |
| "lint V5" / explicit invocation **OR auto-chained after every Phase 6a "clean" convergence AND after every Phase 9 final render** | **Phase 6b — Mechanical lint (auto)**. `python tools/lint_video.py V<N>` — deterministic, free, no LLM. Asserts every Hard Rule that's mechanically checkable from project artifacts (zooms.json, script frontmatter, scrub report, ticks.json, render manifest, ffprobe of `vid<N>_zoomed.mp4`). **Tier 1 (errors — STOP the chain):** L01 frontmatter timings vs zoom.py segment timing (Hard Rule #12), L02 framerate 60fps + 1s keyframes (Hard Rule #15), L03 spotlight comp-y in safe zone 30–70% (Hard Rule #17), L04 z0 duration = `T_typing_end` (Hard Rule #22), L05 standard skeleton (z0 + z0b + z1..zN — Hard Rule #23), L06 z0b sizing (`source_t = T_first_tick − margin`, `ease ≤ margin`, `duration = (T_(N-1) + margin) − source_t + ease_out` — Hard Rule #23), L07 highlight three-tier band (≤15% / 15–25% / >25% must split — Hard Rule #24), L08 measurement-marker presence (every highlight cites `tools/measure_highlight.py` output — Hard Rule #10), L09 panel-hold floor `max(3.0s, body_word_count / 5.0 + 2.0s)` per panel or shared-cluster sum (Hard Rule #25), L10 template slot coverage (every `apN` referenced in frontmatter exists in `templates/<family>/index.html`), L11 timing math (composition runtime = 5s title + recording_duration + 7s outro ±0.1s — RENDER-GUIDE invariant). **Tier 2 (warns — chain continues to 6c, surfaced alongside):** L12 banned-engineering-phrase substring match against VO body (cross-checks `references/production-principles.md` *Customer's-chair framing*), L13 slash-command-in-VO substring (`/parallax:` etc. — Principle #9, except `style: instructional` exempted), L14 capability-count pattern ("eight tools", "twelve calls", etc.), L15 draft-mode markers (TBD, TODO, placeholder strings in shipping-tier copy), L16–L22 softer proxy checks per `tools/lint_video.py --help`. **Gate behavior:** any tier-1 finding STOPS the chain — do not run Phase 6c, surface findings to user, do not bill the reviewer. Tier-2 warnings carry through to Phase 6c's report. **Output:** terminal pass/warn/error report with per-finding diff hints. **On clean (no tier-1) → auto-chain into Phase 6c (review)** — see the review dispatch row below. **Cross-ref:** `video-production-workflow/` Phase 6b + all Hard Rules cited above. **Cost:** $0 always — pure local mechanical check. |
| "review V5" / explicit invocation **OR auto-chained after every Phase 6b "clean tier-1" pass** | **Phase 6c — Semantic LLM review (auto)**. `python tools/review_video.py V<N>` — vision-grounded LLM pass on the rules that require semantic judgment, run via `claude-opus-4-7` through the Anthropic SDK. **Six checks:** R01 subject-match (does the spotlit area visually match the panel's pitch? — frame-level), R02 customer's-chair framing (panel copy speaks from the buyer's chair, not engineering's — text-level), R03 panel-shape rotation (capability/workflow/stakes — no three consecutive panels in same shape — text-level), R04 vault-stat integration (stats appear inside output moments not as standalone narration — text-level), R05 beat content visibility (each `dwell:y` beat's frame visibly contains the claimed content — frame-level), R06 hallucination check (every `frames_used:` cite matches its frame — frame-level, per Hard Rule #7). **Caching:** responses are cached at `outputs/V<N>/.review-cache/<content-hash>.json` keyed by `(check_id + system_prompt + user_prompt + image_bytes + model)`. First run after a script body change or a re-render: ~$0.25 (Opus 4.7, ~16 calls for a 3-panel video). Subsequent re-runs against unchanged input: $0. **Output:** `outputs/V<N>/review.md` — markdown report grouped by rule with embedded evidence frames as relative-path image links + per-finding pass/drift/fail verdict + reasoning + cost summary. **Severity:** `fail` = concrete violation surfaced; `drift` = LLM uncertain or partial misalignment; `pass` = clear conformance. The chain does NOT auto-stop on reviewer findings — they're surfaced for user-side action (re-open Phase 5 / 5.5 / 6 as appropriate). **Skip flag:** `--no-review` on `tools/render.py` (when auto-chaining) skips Phase 6c for cost-sensitive iterations. **Cross-ref:** `video-production-workflow/` Phase 6c + Hard Rules #7 (hallucination), #17 (safe-zone) + `references/production-principles.md` *Customer's-chair framing* + *NL prompts in demo*. |
| "render V5 final" | **Phase 9 — Final render** ($$, billable HeyGen credits). `python tools/render.py V<N> --mode final` → `outputs/V<N>/final.mp4`. Generates avatar clip via HeyGen (cached at `avatars/clips/V<N>_<hash>.mp4` — keyed by script-body hash via `tools/script_hash.py`; unchanged VO doesn't re-bill), injects `<video>+<audio>` into the template's `#avatar` div, re-renders. **Only step that bills HeyGen.** **Preconditions:** (a) preview shipped + user approval gate cleared; (b) `vid<N>_zoomed.mp4` exists; (c) LT/caption timings re-derived against the zoomed recording (Hard Rule #12); (d) `.env` has `HEYGEN_API_KEY` / `HEYGEN_AVATAR_ID` / `HEYGEN_VOICE_ID`. Use `--dry-run` first to verify wiring + see what avatar clip would be generated. **Auto-chains into Phase 6b (lint) → Phase 6c (review) on completion** — the ship-gate artifact gets the same rule check as the preview. Tier-1 lint failures STOP the chain and surface to the user before the LLM reviewer is invoked. The reviewer's response cache typically hits on the final pass (same script body + same zoom timings as the approved preview), so the cost is usually $0. **Cross-ref:** `video-production-workflow/` Phase 6 final + Phase 6b/6c + Hard Rule #8 (preview free; final billed). |
| "render failed" / "dry-run V5" | `python tools/render.py V5 --mode <preview\|final> --dry-run -v` to see substitution slot list and (in final mode) what avatar clip would be generated. Check `.env` for `HEYGEN_API_KEY` / `HEYGEN_AVATAR_ID` / `HEYGEN_VOICE_ID` if final fails with "missing credentials." **If render fails with "Customer's-chair framing violations detected"**: this is the pre-flight check (defense-in-depth for `video-scriptwriting/SKILL.md` Quality Check #9 + `references/production-principles.md` → Customer's-chair framing) that scans the substituted HTML for engineering-vocabulary banned phrases ("parallel skill calls", "MCP tool invocations", "agent orchestration", etc.). Fix: rewrite the offending copy in audience-perspective vocabulary (outcome / stakes / workflow-fit / methodology-credibility molds). For `instructional` videos (I1–I4) where system-mechanics framing IS the right register, pass `--allow-engineering` to bypass. The check is enforced by default for use_case videos. |
| "ship V5" / "approve final" | After user confirms `outputs/V5/final.mp4` is shippable: ask before deleting `frames/V5/`. Do not auto-delete. (Workflow Hard Rule #14 — source material preserved until explicit user approval; ambiguous responses default to don't-touch.) |
| "clean V5 frames" | After explicit approval signal per workflow Hard Rule #14 — *"yes"*, *"approved"*, *"ship it"*, *"delete the frames"* (never *"thanks"*, *"will watch later"*, or silence): `rm -rf frames/V<N>/`. The script's `frames_used:` audit trail is the durable record. Files that are NEVER deleted regardless of signal: `outputs/V<N>/final.mp4`, `audio/V<N>.mp3` (if used), all `screen recordings/V<N>/*.mp4`, the script .md, and `scripts/V<N>_zooms.json`. |

## The daily loop (per video)

> The 11-phase loop comes from `CLAUDE.md` "Daily workflow per video." This skill dispatches each phase to the right tool. Read `.claude/skills/video-production-workflow/SKILL.md` for the phase methodology (why each phase exists, what counts as "done", failure handling).

```
1.  Lock beat sheet      → "lock V<N> beats" (writes into MASTER.md, no approval pause)
2.  Record               → screen recordings/V<N>/vidN.mp4
                           Two modes:
                             (a) Manual — user records via OS screen capture
                             (b) Automated — "capture V<N>" triggers
                                 automation/capture.py with --no-readthrough;
                                 also writes manifest.json with phases
                                 (Phase 3 reads streaming_started as T_typing_end)
3.  Conform (scrub only) → tools/scrub.py
                           Per-beat decision tree (skill: video-production-workflow):
                             too long, dead loading      → scrub
                             too long, content motion    → uniform 1.5–2× speedup
                             too short, dwell:y          → defer to Phase 5.5 zoom
                             too short, anything else    → re-record (escalate to user)
                           Zoom does NOT run here — see Phase 5.5.
                           Slowdown (any form) is BANNED — see workflow Hard Rule #13.
4.  Extract frames       → tools/extract_frames.py on vidN_scrubbed.mp4 (script grounding)
5.  Write script         → "write V<N>" (consults MASTER, frames, RENDER-GUIDE, video-scriptwriting)
                           Also produces scripts/V<N>_zooms.json declaring one zoom per
                           dwell:y beat — source_t, region placeholder, duration, mode.
                           Zoom region = what the VO names in that beat.
5.5 Apply zoom           → tools/measure_highlight.py (per annotate) + tools/zoom.py
                           Inputs: vidN_scrubbed.mp4 + scripts/V<N>_zooms.json
                           Output: vidN_zoomed.mp4 (canonical timeline for render).
                           Re-derive LT/caption timings against vidN_zoomed.mp4 per Hard Rule #12.
6.  Preview render       → "render V<N> preview" against vidN_zoomed.mp4  ($0)
6a. Polish (auto)        → sync + coverage + rhythm; re-render preview if edits
                           applied; auto-chains into 6b on "clean" convergence.
6b. Lint (auto)          → tools/lint_video.py — deterministic Hard-Rule check.
                           Tier-1 errors STOP the chain; tier-2 warns continue.
                           $0 always. Cross-ref: video-production-workflow/ 6b.
6c. Review (auto)        → tools/review_video.py — vision-grounded LLM pass
                           (claude-opus-4-7) for R01-R06 semantic checks.
                           ~$0.25 first run, $0 on cache hits. --no-review
                           opts out per-render. Writes outputs/V<N>/review.md.
7.  Iterate              → re-run 5 + 5.5 + 6 freely (each preview re-runs 6a/6b/6c)
8.  Approve preview      → user confirms layout/timing/copy + reviewer findings
9.  Final render         → "render V<N> final"   ($ — HeyGen avatar credits)
                           Auto-chains into 6b → 6c on final.mp4 (same rule check
                           as the ship gate; cache typically hits, $0).
10. Approve final        → user OKs
11. Cleanup              → after explicit OK: rm -rf frames/V<N>/
```

If conformation fails at step 3 (recording can't be scrubbed down to beat-sheet targets net of planned zoom inserts): re-record the failing beat, or re-open step 1 (rare, user sign-off). Do **not** proceed to step 5 with an unscrubbed recording.

If zoom design fails at step 5.5 (no settled visual on a dwell:y beat, or VO names content not present in the scrubbed recording): re-record. Zoom must serve the VO — don't paper over with an arbitrary zoom region.

## Frontmatter contract

Every product-demo script `.md` opens with YAML frontmatter that `tools/render.py` reads to substitute per-video copy + timing into the template. **Required** fields are marked.

```yaml
---
video_id: V1                              # required: V<N> (use_case) or I<N> (instructional)
template: product-demo                    # required: matches templates/<family>/
pipeline_type: product_demo               # required: "product_demo" or "intel_brief" (intel_brief is shelved)

# Style + complexity axis (required — drives which video-scriptwriting/SKILL.md section applies)
style: use_case                           # required: "use_case" or "instructional" (or "intel_brief" — paused)
complexity: single_feature                # required for use_case: "single_feature" (Tier 1) / "workflow_chain" (Tier 2) / "hero_playbook" (Tier 3)
                                          # required for instructional: "utility" (Tier 0)

# Persona-and-moment anchoring (required for use_case style; omitted for instructional)
primary_persona: "MFO / independent RIA / wealth advisor"   # structural metadata — drives beat selection + value-angle rotation. NEVER appears in VO copy.
primary_moment: "Client just texted about a holding. Ten minutes before your next meeting."  # the in-VO situation phrase that opens the script. Self-identifies the persona via verbs + stakes; role label not used.
secondary_personas: ["PM (pre-trade gut check)", "Analyst (fast read for PM ask)"]  # optional — other personas this video plausibly serves without re-framing

# YouTube distribution title (separate from on-screen title-card text)
youtube_title: "Quick Stock Research Brief"   # framed for search intent (the workflow/action), not the tool name

recording:                                # required for product_demo
  path: "screen recordings/V1/1vid_zoomed.mp4"   # Phase 5.5 zoom output (canonical)
  duration_seconds: 77.47                     # ffprobe-verified, post-zoom
  scrub_report: "screen recordings/V1/1vid_scrub_report.json"
  zooms: "scripts/V1_zooms.json"               # zoom directives drafted at Phase 5

beats:
  title:
    eyebrow: "V1 · Quick Stock Research Brief"
    headline: "Twenty minutes of research, in one sentence."
  outro:
    tagline: "Solve the market."          # default: locked tagline. Override only for PM/CIO Polaris-closer videos (V8, V12, V14 per MASTER Phase 3 spec).
    duration: 7.0

lower_thirds:                             # one entry per LT (lt1..lt4); lt3+lt4 default to (0,0)
                                          # = "retired" — only fire if frontmatter substitutes
                                          # in/out times. With annotate spotlights replacing the
                                          # output-brief LTs, lt3/lt4 typically stay retired.
  - id: lt1
    in_recording_t: 4.0                   # recording-relative; render.py adds 5s for composition-absolute
    out_recording_t: 11.0
    eyebrow: "V1 · Quick Stock Research Brief"
    headline: "Eight parallel skill calls. One natural-language prompt."
  - id: lt2
    in_recording_t: 23.0
    out_recording_t: 33.0
    eyebrow: "Vault stat · Peer-reviewed · Out-of-sample"
    headline: "ICIR 4.10 · Information coefficient ranking"
    stats:
      - {value: "+5.8%",   label: "/yr selection return"}
      - {value: "13",      label: "years"}
      - {value: "62,000+", label: "listings"}
      - {value: "48",      label: "markets"}

annotations:                              # one entry per annotate-mode zoom (apN ↔ zoom directive's callout_number)
                                          # in_recording_t / out_recording_t are derived AFTER zoom.py runs —
                                          # read the "segment timing in zoomed file" log from zoom.py and
                                          # copy the annotate segment's [start, end] into these fields.
                                          # Hard Rule #12: re-derive after every re-zoom (cleaning, cursor-clear
                                          # adjustments, or any directive change shifts the timeline).
  - id: ap1                               # template element id; pairs 1:1 with zoom directive callout_number=1
    in_recording_t: 50.25                 # = seg_annotate_01 start in zoomed timeline
    out_recording_t: 66.25                # = seg_annotate_01 end
    callout_number: 1
  - id: ap2
    in_recording_t: 67.73
    out_recording_t: 77.73
    callout_number: 2
  - id: ap3
    in_recording_t: 83.40
    out_recording_t: 87.40
    callout_number: 3

frames_used: [3, 8, 21, 31, 33]           # audit trail (product_demo only)
target_runtime_seconds: 89                # 5s title + recording + 7s outro
---
```

LT timings are anchored to the **zoomed** recording (Phase 5.5 output — `vid<N>_zoomed.mp4`, with all inserted zoom durations baked in). Hard Rule #12: re-derive after every re-zoom or re-scrub. The same applies to annotation panel timings (`annotations[].in_recording_t / out_recording_t`) — they reference the zoomed timeline and must be re-derived whenever zoom.py is re-run. RENDER-GUIDE.md describes the recording-relative-to-composition-absolute conversion (composition_t = recording_t + 5).

**Authoring annotation timings — recipe:**
1. Draft zoom directives in `scripts/V<N>_zooms.json` during Phase 5 (script writing). Each `mode: "annotate"` directive carries `source_t`, `duration`, `zoom_region_pct`, `highlight_region_pct`, `callout_number`, `wait_cursor_clear: true`.
2. Run zoom.py at Phase 5.5. It prints a "segment timing in zoomed file" report at the end — copy each `seg_annotate_NN` segment's `[start, end]` recording-time range into the matching `annotations[apN]` entry's `in_recording_t / out_recording_t`.
3. Re-render preview. The template's `annotatePanel("#apN", inT, outT)` GSAP calls get substituted from those values by `tools/render.py`.

Intel-brief frontmatter is a smaller subset (no recording fields, no LT timings tied to a recording). **Shelved as a deferred future addition** per overhaul.md Phase 5 — the spec lands when intel briefs are reactivated and the template is built (requires a Claude Design session).

## Render mechanics (what `tools/render.py` does)

### `--mode preview` (free)

1. Parse script frontmatter.
2. Find recording, ffprobe its duration, find template.
3. Compute `script_hash` (cache key for future final renders).
4. Apply substitutions to a copy of `index.html`:
   - Title eyebrow + headline content
   - LT eyebrow + headline + stats content
   - LT call-site timings (`lowerThird("#ltN", in, out)`)
   - Composition + scene durations + outro start
   - Scene-visibility flips at `scene_3_start = 5 + recording_duration`
   - Watermark fade-out, avatar fade-out, all 4 outro element entrance times
5. Stage recording into `templates/<family>/assets/screen-recording.mp4`.
6. `npx hyperframes render <template-dir> --fps 60 --quality standard -o outputs/V<N>/preview.mp4`.
7. Restore template from backup (template stays clean between runs).
8. Write `outputs/V<N>/render-manifest.json` + append to `render-history.jsonl`.

### `--mode final` (HeyGen avatar credits)

Same as preview, plus:

1. Compute `script_hash`. Look up `avatars/clips/V<N>_<hash>.mp4`. Cache hit → reuse. Cache miss → call HeyGen.
2. HeyGen call: `heygen video create -d '{"type":"avatar","avatar_id":...,"script":<spoken VO>,"voice_id":...}' --wait` then `heygen video download <video-id> --output-path <cache-path>`.
3. Stage the cached clip to `templates/<family>/assets/avatar.mp4`.
4. Inject `<video class="clip avatar-video" src="assets/avatar.mp4" muted playsinline ...>` + matching `<audio>` element inside the template's `#avatar` div.
5. Render to `outputs/V<N>/final.mp4`.

`--dry-run --mode final` exercises everything *except* the actual HeyGen call. Use this to validate wiring before a live run.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `error: missing HeyGen credentials in .env` | `.env` missing or fields blank | Copy `.env.example` → `.env`, fill in `HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID` |
| `heygen video create failed (code=insufficient_funds)` | Wallet too low | Top up at app.heygen.com — clip cost ~$15 |
| LT lands on wrong content (e.g. trajectory LT during score panel) | LT timings reference old recording, not the post-zoom timeline | Re-derive LT in/out recording-relative offsets against the zoomed recording's beat windows (Phase 5.5 output). Hard Rule #12. |
| Title-card shows diagonal banding | Linear gradient on dark navy → H.264 quantization | Use solid color + localized radial accent (or no accent). Hyperframes typography rule. |
| Final render shows different non-avatar pixels than preview | Substitution layer changed something it shouldn't have, or template was hand-edited between runs | Diff frames at t=2.5s (title), t=30s (LT2), t=68s (LT4) outside the avatar bbox. Should be ~0 drift. |
| Hyperframes render freezes on a seek | Source recording has sparse keyframes | Re-encode with `-r 60 -g 60 -keyint_min 60` (`tools/scrub.py` does this by default since 2026-05-05). |

## Files in this skill

```
.claude/skills/parallax-video/
├── SKILL.md                # this file (orchestrator dispatch table + frontmatter contract)
└── (assets, if any, live alongside)
```

The actual tools live at `tools/` (project root) — they're shell-callable without invoking the skill, which is what unblocks cron / OpenClaw-style automation.
