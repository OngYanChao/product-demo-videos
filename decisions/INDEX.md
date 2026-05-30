# Decisions log

Chronological, date-stamped archive of locked-in decisions and rules for this project. Append-only — supersede by adding a new entry, not by editing an old one.

Sorted oldest → newest. The current row at the bottom is the most recent decision.

---

## Capture protocol

When the user signals a new locked-in decision or rule, capture it. Trigger phrases (case-insensitive, anywhere in a user message):

- "lock this in" / "lock in" / "locked in"
- "decision:" / "we're deciding" / "we've decided"
- "from now on" / "going forward" / "henceforth"
- "don't re-litigate" / "this is settled" / "final answer"
- "remember this" / "log this decision" / "add to decisions"
- "new rule:" / "rule:" / "principle:"

When triggered:

1. **Create the entry file**: `decisions/YYYY-MM-DD-<short-kebab-slug>.md` using today's date. If a same-day file with the same slug already exists, append `-2`, `-3`, etc.
2. **Append to the chronological log table at the bottom of this file** — newest entries at the bottom. Format: `| YYYY-MM-DD | One-line decision summary | [filename](filename.md) |`.
3. **Route the rule to its encoding site** (see "Rule routing" below). The decisions log is the *event log*; the encoding sites are the *current state*. A new methodology rule gets appended as the next numbered Hard Rule; a new Parallax project decision gets appended to `production-principles.md`; etc. Cross-link in both directions — the ADR's `Affects:` line points at the encoding site, and the encoding site's new entry has a "(Logged: `decisions/YYYY-MM-DD-slug.md`)" suffix.
4. **Surface both file paths to the user** in your reply — the new ADR *and* the encoding-site edit — so they can verify or edit.
5. **If a new decision supersedes an old one**, set the old entry's `Status:` to `superseded by [YYYY-MM-DD-slug](...)` and add `Supersedes:` to the new entry's frontmatter. Don't delete superseded entries — they're history. The encoding site gets updated to the new rule; the old rule's text moves to a "Superseded" subsection or gets struck through, never silently overwritten.

When unsure whether a moment counts as a decision, ask: "Should I log this as a decision?"

---

## Rule routing

Every captured decision creates an ADR in `decisions/`. *In addition*, route the rule's substance to its authoritative encoding site based on type:

| Rule type | Encoding site | How to append |
|---|---|---|
| **Portable video-production methodology** — phasing, ordering, conform-vs-compress, framerate invariants, anything that would apply to any video project, not just Parallax | `.claude/skills/video-production-workflow/SKILL.md` — `## Hard rules` section | Append as the next numbered Hard Rule (#16, #17, …). Match the existing style: bold opener sentence, then 1–3 sentences of rationale, optional project-local note. |
| **Parallax project decision** — NL prompts in demo, Polaris closer, Highlights ownership, persona-overhaul choices, value-framing, Parallax-specific phasing decisions | `references/production-principles.md` — next numbered Principle (currently #1–#13) | Append as the next Principle, mirroring the existing template (Rule → Why → Encoded at → History). Update the cross-ref table at the top of the file. |
| **Script craft** — voice composite, banned words, vocabulary lock, hallucination-check enforcement, value-framing rotation | `.claude/skills/video-scriptwriting/SKILL.md` | Append to the relevant Universal / use_case / instructional / intel_brief section. |
| **Per-template format invariant** — layout positions, char/word limits, animation timings, fonts, watermark/avatar positions, locked taglines for a specific template | `templates/<family>/RENDER-GUIDE.md` | Append to that template's RENDER-GUIDE under the relevant invariant section. |
| **CLAUDE.md-level meta** — dispatch table changes, file layout, project-wide conventions | `CLAUDE.md` | Edit the relevant section. Keep CLAUDE.md slim — prose-heavy rules belong in one of the encoding sites above, with CLAUDE.md just pointing. |
| **Unclear / cross-cutting** | `decisions/` ADR only — ask the user where it should be encoded | Don't guess. Capture the ADR, then ask: "Where should this rule live — methodology Hard Rule, Parallax principle, script craft, or template?" |

**Routing heuristics (when the user's phrasing is ambiguous):**

- Mentions specific Parallax terms (Polaris, HeyGen, MASTER, V<N>, I<N>, persona, moment, Highlights) → likely a **Parallax principle**.
- Mentions a phase number, "always X before Y", "conform", "framerate", "keyframe", "beat sheet" → likely a **methodology Hard Rule**.
- Mentions VO, voice, blockquote, banned word, vocabulary, tone, value-framing → likely **script craft**.
- Mentions a specific template family ("product-demo template", "intel-brief template") or layout positions → likely a **template invariant**.
- The user's trigger phrase itself biases routing: `"new rule:"` / `"hard rule"` → methodology; `"new principle"` → Parallax principle.

If two homes seem plausible, prefer the more specific one and add a one-line pointer from the broader one.

---

## File format

Use this template for each decision file:

```markdown
# YYYY-MM-DD — <Short title in title case>

**Status:** active
**Supersedes:** (optional — link to prior decision file)
**Affects:** (optional — paths/skills/principles that encode this)

## Decision

One short paragraph stating exactly what is being locked in.

## Why

One short paragraph: the reasoning, the alternative considered and rejected, the trigger (incident / preference / constraint).

## Notes

(Optional — context, edge cases, follow-up TODOs, related decisions.)
```

Keep it short. The decisions log is for finding decisions later, not for re-deriving them. If a decision needs a long rationale, put the long version in `references/production-principles.md` (or wherever the rule is encoded) and keep this entry as a pointer.

---

## Log

| Date | Decision | File |
|---|---|---|
| 2026-05-15 | Adopt date-stamped decisions log | [2026-05-15-decisions-log-adopted.md](2026-05-15-decisions-log-adopted.md) |
| 2026-05-15 | Rule-routing protocol added to decisions capture | [2026-05-15-rule-routing-protocol.md](2026-05-15-rule-routing-protocol.md) |
| 2026-05-18 | Cursor-clear rule: brief-targeting zooms must wait for cursor to clear region | [2026-05-18-cursor-clear-rule.md](2026-05-18-cursor-clear-rule.md) |
| 2026-05-18 | Product-demo template: recording crop anchored to top (preserves top bar; bottom is zoom-on-demand) | [2026-05-18-recording-top-anchored-crop.md](2026-05-18-recording-top-anchored-crop.md) |
| 2026-05-19 | Annotate-mode highlight must land at composition's vertical center (source must be at a scroll position that supports it) | [2026-05-19-annotate-vertical-centering.md](2026-05-19-annotate-vertical-centering.md) |
| 2026-05-19 | Cursor-clear region for annotate mode = highlight x-extent × zoom y-extent (catches adjacent-row cursors; excludes dark padding) | [2026-05-19-cursor-clear-region-broader.md](2026-05-19-cursor-clear-region-broader.md) |
| 2026-05-19 | Annotate highlight border + numbered dot use CG navy-400 (#547498), not orange — pairs visually with the navy panel | [2026-05-19-annotate-border-dot-navy.md](2026-05-19-annotate-border-dot-navy.md) (superseded) |
| 2026-05-19 | Annotate default switched to soft-edged elliptical spotlight — no rectangle border, no numbered dot beside highlight (panel still carries numbered badge); `halo_mode` flag removed | [2026-05-19-annotate-spotlight-default.md](2026-05-19-annotate-spotlight-default.md) |
| 2026-05-19 | Customer's-chair framing: all use_case copy speaks from buyer's chair (outcome/stakes/workflow-fit/methodology), never system's chair (parallel calls / MCP / agents / capability counts) | [2026-05-19-customers-chair-framing.md](2026-05-19-customers-chair-framing.md) |
| 2026-05-19 | Annotation panel content: capability framing (not specifics) + 3-shape rotation (capability/workflow/stakes) + subject-match-to-spotlight + source+badge required + no stats row | [2026-05-19-panel-content-authoring.md](2026-05-19-panel-content-authoring.md) |
| 2026-05-20 | Spotlight ellipse circumscribes the highlight rect (half-axes × √2 + small additive buffer) so every rect-pixel is inside the bright zone regardless of aspect | [2026-05-20-spotlight-circumscribes-rect.md](2026-05-20-spotlight-circumscribes-rect.md) |
| 2026-05-20 | Overlay animations synced to a camera move share the camera's ease curve — panels use GSAP `sine.inOut`, matching `tools/zoom.py`'s `easeInOutSine` | [2026-05-20-overlay-ease-matches-camera.md](2026-05-20-overlay-ease-matches-camera.md) |
| 2026-05-20 | Clean source segments between annotates by default via zoom.py `--clean-source-ranges` (drops sub-`min_dead_seconds` freezes that survived scrub) | [2026-05-20-clean-source-segments.md](2026-05-20-clean-source-segments.md) |
| 2026-05-20 | Panel `source:` + `badge:` drawn from locked vocabulary (4 Parallax product names; 8 methodology-virtue tags + 1 temporal special-case) — no freelance values | [2026-05-20-panel-source-badge-vocabulary.md](2026-05-20-panel-source-badge-vocabulary.md) |
| 2026-05-20 | Hard Rule #6 expanded — "match rhythm to budget" applies both ways: tight budget cuts whole beats, loose budget uses breathing room with natural sentence rhythm (not stylistic-reflex fragments) | [2026-05-20-sentence-rhythm-with-budget-headroom.md](2026-05-20-sentence-rhythm-with-budget-headroom.md) |
| 2026-05-20 | Phase 6a auto polish pass — between Phase 6 preview and Phase 7 iterate; runs automatically after every Phase 5 + Phase 6; sync + beat coverage + rhythm + conditional LT/panel update; Hard Rule #6 refined as phase-aware (write punchy / polish to rhythm) | [2026-05-20-phase-6a-polish-pass.md](2026-05-20-phase-6a-polish-pass.md) |
| 2026-05-21 | Vault stats integrate, not narrate — use-case videos (V1–V16) include vault stats only when load-bearing for problem-solving or why-can't-Claude framing of a specific output moment; standalone credibility-ribbon beats and LT graphics dropped | [2026-05-21-vault-stats-integrate-not-narrate.md](2026-05-21-vault-stats-integrate-not-narrate.md) |
| 2026-05-21 | Detect ticks programmatically — `tools/detect_ticks.py` for tail-cut tick timestamps; never eyeball (Hard Rule #20). Frame-diff peak detection at 30fps in a configurable region, outputs ffmpeg trim ranges | [2026-05-21-detect-ticks-programmatic.md](2026-05-21-detect-ticks-programmatic.md) |
| 2026-05-22 | Pre-loading recording segments (prompt typing + pre-submit chrome) play at 1x — never compressed (Hard Rule #21). Encoded as `tools/scrub.py --force-speed-range "0:X:1.0"` where X = the loading-segment boundary | [2026-05-22-prompt-typing-1x.md](2026-05-22-prompt-typing-1x.md) |
| 2026-05-22 | Zoom skeleton standardization — z0 ease-out aligns with loading-segment boundary (Hard Rule #22); every product_demo includes z0 + z0b + z1..zN with mandatory tail-cut on z0b (Hard Rule #23); annotate highlight regions measured via `measure_highlight.py`, height ≤15%, multi-VO-target beats split into sub-annotates (Hard Rule #24, extension of #10) | [2026-05-22-zoom-skeleton-standardization.md](2026-05-22-zoom-skeleton-standardization.md) |
| 2026-05-23 | Tick-window compression moves to Phase 3 (supersedes the Phase 5.5 tail-cut part of 2026-05-22). `detect_ticks.py` runs on RAW recording, emits `ffmpeg_keep_ranges` per gap-cut rule (>2s gap → compress to 1s; ≤2s → leave). `scrub.py` locks 3 zones at 1× (typing, tick window, post-brief); pixel-diff freeze compression applies only to the 2 buffer zones around the tick window. No Phase 5.5 tail-cut step. Hard Rules #20, #21, #23 updated | [2026-05-23-tick-window-compression-moves-to-phase-3.md](2026-05-23-tick-window-compression-moves-to-phase-3.md) |
| 2026-05-24 | z0b ease-in starts when the checklist is fully visible — `source_t = zone-b start in scrubbed = T_first_tick − margin`; `ease ≤ margin` (default 1.0s) so ease-in completes by T_first_tick. Replaces the "~3s after z0 ease-out" fixed-offset heuristic from 2026-05-22. Hard Rule #23 refined | [2026-05-24-z0b-starts-on-checklist.md](2026-05-24-z0b-starts-on-checklist.md) |
| 2026-05-25 | Annotate panel-hold minimum = `max(3.0s, body_word_count / 5.0 + 2.0s)` so the panel registers + skims without dead-space hang. Viewer-driven pacing: 300 wpm fluent-skim, viewers who want depth pause. Body word count only (eyebrow + headline + badge + source excluded — all glance-readable). Sub-annotates sharing a panel sum their durations against the floor. New Hard Rule #25 | [2026-05-25-annotate-panel-hold-minimum.md](2026-05-25-annotate-panel-hold-minimum.md) |
| 2026-05-25 | Annotate highlight height splits into three tiers: ≤15% tight (specific row/phrase), 15-25% relaxed (header+paragraph conceptual unit, single spotlight), >25% must split into sub-annotates with shared panel. Plus coupling rule: long-body panel → tight spotlight; short/bare-callout → wider spotlight OK. Refines Hard Rule #24's flat ≤15% cap | [2026-05-25-highlight-three-tier-band.md](2026-05-25-highlight-three-tier-band.md) |
| 2026-05-28 | News-pipeline rule N1: 1s hard cap on any freeze in the post-tick region of `zoom.mp4`. Targets the brief-done-to-cut-to-top dwell + post-scroll tail before outro. Implemented as `tick_cut.cap_dead_times()`, called from `process.py` after `zoom.py`. Pre + tick-montage protected via `protect_until_t = auto_zoom_end`. News-pipeline scope only (main pipeline pacing is script-driven). New rule, not a refinement | [2026-05-28-news-1s-dead-time-cap.md](2026-05-28-news-1s-dead-time-cap.md) |
| 2026-05-25 | Spotlight vertical centering relaxes to a comp-space safe zone (y=30%-70%, 40%-wide band) — replaces strict y=44.8%/50% center-point rule. Lets sub-annotate clusters share one source_t + one zoom_region (static camera, just spotlight moves), eliminating mid-scroll jitter between consecutive sub-spotlights. Refines Hard Rule #17 | [2026-05-25-spotlight-vertical-safe-zone.md](2026-05-25-spotlight-vertical-safe-zone.md) |
| 2026-05-29 | News-pipeline rule N2: prompt-typing segment (t=0 → streaming start) is **speedup-OK, never cut**. `tapered_with_cut` and any frame-drop treatment forbidden in this window; uniform speedup at anchor speed (2×) is the right knob. Diverges from main-pipeline Hard Rule #21 (typing at 1×) because news videos have a tighter runtime budget and the typing window is context, not load-bearing script content. News-pipeline scope only. **Auto-enforced**: `capture.py` records `phases.streaming_started`; `process.py::_derive_typing_force_range()` reads it and prepends `--force-speed-range "0:X:2.0"` to `scrub.py`. Per-run opt-out: `--no-typing-speedup` | [2026-05-29-news-typing-never-cut.md](2026-05-29-news-typing-never-cut.md) |
| 2026-05-29 | Post-streaming pre-scroll-up dead-time cap promoted from news's N1 case (a) to **global Hard Rule #26**. When `automation/capture.py`'s auto-trim can't run (no `scroll_to_top_done`, or `trim_segment` errored), the failsafe finds any freeze >1s within 30s of `phases.streaming_ended` and caps it to 1s. Lives in `automation/capture.py::cap_post_streaming_deadtime()`. Both pipelines benefit. Case (b) of N1 (post-scroll-down trailing dead time) stays news-only — would destroy product-demo's annotate dwells (Hard Rule #25) | [2026-05-29-post-streaming-deadtime-cap-global.md](2026-05-29-post-streaming-deadtime-cap-global.md) |
| 2026-05-29 | Hard Rule #21 zone (a) refined: product-demo prompt-typing default 1× lock holds, but **adaptive speedup applies when typing >10s** — `typing_factor = min(2.0, max(1.0, typing_duration / 10.0))`, capped at 2×. Worked examples: 15s → 1.5×; 20s → 2×; 30s → 2× (post-speedup 15s). 10s threshold = upper bound of tolerable 1× typing; 2× cap = upper bound before keystrokes register as machine-fast. Diverges from news's N2 (always-2×) because product-demo's typing is deliverable customer's-chair content, news's is context. Hard Rule #22 (z0 sizing) also updated with the raw-vs-scrubbed conversion: `z0.duration = (T_typing_end_raw / typing_factor) + ease`. Phase 3 dispatch step 6 computes the factor; Phase 5 z0 sizing applies it | [2026-05-29-product-demo-adaptive-typing-speedup.md](2026-05-29-product-demo-adaptive-typing-speedup.md) |
| 2026-05-29 | Hard Rule #23 split into **Variant A (manual) + Variant B (automated)** for post-tick treatment. Manual (existing): z0b ease-out at `T_(N-1) + margin`, brief progressively loads during retract — production value, viewer sees Cowork "working". Automated (new): Phase 3 pre-cuts `[T_N + 1.0s, T_brief_landed]` from raw via ffmpeg trim+concat BEFORE scrub; combined with capture.py's existing scroll-up auto-trim, the brief-loading + scroll-up segments are both hidden. z0b ease-out sized to retract onto the at-top frame (where post-brief locked zone begins in scrubbed time). `post_synth_buffer = 1.0s` default. Detection: `manifest.json` + `phases.scroll_to_top_done` both present = automated; else manual. No tool changes — orchestrator-only (Phase 3 + Phase 5 dispatch in parallax-video/SKILL.md). Option A (pre-trim) chosen over Option B (zoom.py mid-ease-out source cut) for lower implementation risk; same visual outcome | [2026-05-29-automated-post-tick-cut.md](2026-05-29-automated-post-tick-cut.md) |
| 2026-05-30 | **Hard Rule #28 — z0.ease = 1.5s standard + scrubbed buffer 1 ≥ 2.5s.** Surfaced by V3 preview review: V3's z0 ease was 0.5s, visibly faster than V1+V2's 1.5s convention. Root cause: V3's scrub-compressed buffer 1 (2.03s) couldn't accommodate the standard z0.ease + z0b.margin = 2.5s, so I shortened ease instead of extending buffer. Codifies the 1.5s convention as the standard + adds Phase 3 freeze-frame failsafe (analogous to Rule #27 mechanism) to extend scrubbed buffer 1 when below floor. Inject position must be midpoint of buffer 1 (NOT near T_first_tick, or the slice contains the tick animation and v2's re-play causes a "tick fires twice" artifact — discovered during V3 fix). Hard Rule #22 amended to reference the 1.5s standard. V3 re-done: buffer extended 2.03→2.57s, z0.ease restored to 1.5s, preview now visually consistent with V1+V2 | [2026-05-30-buffer-1-minimum.md](2026-05-30-buffer-1-minimum.md) |
| 2026-05-30 | **Hard Rule #27 — minimum 2.0s top-hold + prompt visible in at-top frame + natural continuation from freeze.** Three requirements: (a) ≥2.0s hold; (b) at-top frame must include the prompt at the top of the chat; (c) after the freeze-frame injection, source must continue naturally from the same raw timestamp the freeze began — NO jump cuts. Went through three same-day refinements: (1) initial 1.0s proposal at morning; (2) afternoon V3 visual review raised duration to 2.0s + identified prompt-not-visible issue; (3) V3 redo-from-raw surfaced jump-cut issue when v2 segment used a later timestamp than the freeze position. Cowork UI snap caveat: after scroll-up events stop, a snap animation can push the prompt off-screen ~0.5-0.7s after `scroll_to_top_done`. Implementations: capture.py `POST_SCROLL_TOP_HOLD_S` = 2.0; `scroll_chat_to_top()` 80 → 200 events; Phase 3 step 6a gains redo-from-raw subvariant (use `t_at_top_prompt_visible` instead of `scroll_to_top_done` blindly); step 6b.5 ffmpeg template enforces `trim=start=<T_at_top>` for the v2 post-freeze segment. Surfaced by V3 Variant B test | [2026-05-30-minimum-top-hold.md](2026-05-30-minimum-top-hold.md) |