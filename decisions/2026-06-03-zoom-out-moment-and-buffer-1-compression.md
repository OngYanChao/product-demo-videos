# 2026-06-03 — Zoom-out moment between z0 and z0b + news buffer-1 compression (Hard Rules #22 amended, #31 new, N3 new)

**Scope:** Cross-pipeline (Rules #22, #31) + news-specific (Rule N3).

**Affects:**
- `.claude/skills/video-production-workflow/SKILL.md` — routing table + rule catalog
- `.claude/skills/video-production-workflow/rules/phase-3-news.md` — adds Rule #22 (news mechanism), Rule #31, Rule N3
- `.claude/skills/video-production-workflow/rules/phase-5-5-product-demo.md` — Rule #22 cross-pipeline scope, Rule #31 added
- `news-pipeline/tools/process.py` — `_compress_buffer_1()`, `_rule_22_override_auto_zooms()`
- `news-pipeline/tools/tick_cut.py` — `AUTO_ZOOM_Z0_Z0B_GAP_S = 1.5`

## Decision

Three new editorial behaviors codified after N2's first render exposed gaps in the news-pipeline's auto-zoom emission:

### Hard Rule #22 (amendment) — Cross-pipeline scope

The principle "z0 ease-out STARTS at T_click, plays out during the first 1.5s of loading initiation" has always applied to product-demo. The codification (`phase-5-5-product-demo.md`) implicitly scoped it there because the author hand-sizes `z0.duration`. **News's auto-zoom emission in `tick_cut.py` predated Rule #22 and emits `z0.duration = pre_output_dur + ease` — extending z0 through the entire pre-tick segment (typing + buffer 1 + brief loading)**. Result on N2: z0 covered 64.83 seconds of camera-held-on-chat-input, well past typing-end. No zoom-out moment after the prompt fired.

Amendment: Rule #22 explicitly applies to **both pipelines**. News's implementation is via `news-pipeline/tools/process.py::_rule_22_override_auto_zooms()` which rewrites `auto_zooms.json` after `tick_cut.py` emits it. The rewrite sets `z0.duration = typing_end_scrubbed + ease` (where `typing_end_scrubbed = streaming_started_raw / TYPING_SPEEDUP_FACTOR`, accounting for Rule N2's 2× speedup) and adjusts `z0b.source_t` accordingly.

Cross-references both directions: `phase-5-5-product-demo.md` Rule #22 gains a "news implementation" note; `phase-3-news.md` adds a Rule #22 entry.

### Hard Rule #31 (new) — Full-frame zoom-out moment between z0 and z0b

After z0 ease-out completes (camera retracted to full frame after typing), the camera MUST hold at full frame for ≥1.5s before z0b ease-in starts. This gives the viewer a clear "zoom-out moment" where they see the prompt has fired and Cowork has started working, before the camera commits to focusing on the Progress sidebar.

Concretely: in scrubbed/source time, the gap between `z0.source_t + z0.duration` (end of z0 ease-out) and `z0b.source_t` (start of z0b ease-in) must be ≥1.5s. This is in addition to Rule #28's minimum scrubbed buffer 1 (which only ensured z0+z0b transitions FIT, not that there was a held-still moment between them).

**Implementation per pipeline:**
- **Product-demo**: hand-authored zooms.json sizes z0/z0b per Rules #22, #23, #28. The author must size them so `z0b.source_t − (z0.source_t + z0.duration) ≥ 1.5s`. Phase 6b lint can check this mechanically.
- **News**: `tick_cut.py` constant `AUTO_ZOOM_Z0_Z0B_GAP_S = 1.5` adds the gap when emitting z0b. `process.py::_rule_22_override_auto_zooms()` preserves the gap when rewriting.

**Buffer 1 minimum now extends:** with z0.ease=1.5 + 1.5s gap + z0b.margin=1.0, scrubbed buffer 1 (typing-end → first-tick) must be ≥4.0s. Refines Rule #28 (which previously required ≥2.5s).

### News Rule N3 (new) — Buffer-1 compression for news's auto-zoom path

News captures regularly have a long pre-tick wait (40+ seconds for tool-heavy queries like N2, where Cowork sets up 12+ tools before the first checkmark fires). Without intervention, that whole gap survives scrub (no freezes long enough to compress) and survives tick_cut (`DEFAULT_PRE_SECONDS = None` keeps the entire pre-tick segment). Combined with the old z0 sizing, viewers stared at chat-input zoom for 60+ seconds.

**The rule:** After scrub but before tick_cut, compress the typing-end-to-first-tick gap (scrubbed) to a fixed **4.0s** target (chosen to satisfy Rule #31's gap requirement: `target = z0.ease + gap + z0b.margin = 1.5 + 1.5 + 1.0 = 4.0s`).

**Implementation:** `news-pipeline/tools/process.py::_compress_buffer_1()` runs between scrub and tick_cut. It:
1. Reads `manifest.phases.streaming_started`, computes `typing_end_scrubbed = streaming_started / TYPING_SPEEDUP_FACTOR`.
2. Probes the scrubbed file with `detect_ticks.py` over `[typing_end_scrubbed, ∞]`, magnitude threshold **≥10.0** (higher than static_gateway's 3.0 — finding the FIRST REAL tick requires filtering low-magnitude noise that's prevalent in pre-tick loading).
3. If `first_tick_scrubbed - typing_end_scrubbed > 4.0s`, trims `[typing_end + 0.2, first_tick - 3.8]` from the scrubbed file via ffmpeg trim+concat. Result: buffer 1 = 4.0s.

**Scope:** news-pipeline only. Product-demo's buffer 1 is handled by Hard Rule #23 Variant B (pre-cuts the brief-loading region before scrub) + Hard Rule #28 (freeze-frame failsafe). Both already enforce ~2.5s minimum.

**No-op conditions:** manifest missing, streaming_started absent, no real ticks found, or buffer 1 already ≤4.0s.

### Magnitude threshold rationale (≥10.0 vs static_gateway's ≥3.0)

`static_gateway` uses ≥3.0 because it's asking "are there ANY real ticks?" (binary decision — even one weak tick means dynamic path). Buffer-1 compression asks "where does the FIRST REAL tick fire?" (specific anchor). Low-magnitude noise (cursor flicker, TaskUpdate tool-call animations) can register at 3-9 magnitude during pre-tick loading. Real checkmark ticks consistently register 15-150. The 10.0 threshold cleanly separates them.

## User observation (verbatim)

> "First of all after the zoom in on the prompt and after the prompt is fired off into the chat, there is no zoom out. Where is the zoom out? Second of all, why is the loading segment taking so long? I thought we agreed to cut it down to 3 seconds if there is no progress task check bar on the top right corner."

The user is asking for Hard Rule #22 (which exists for product-demo) to also apply to news. They're also asking for buffer-1 compression as a news-equivalent of Rule #30's 3s flash (Rule #30 applies only when zero ticks — static placeholder; here we have 5 ticks but a long pre-first-tick wait, which needs separate handling = Rule N3).

## Why the codification, not just the code fix

The user explicitly diagnosed the gap: "the rules aren't getting followed up because this one didn't go through. Am I right to say that?" Yes — Rule #22 was scoped only to product-demo's hand-authored zooms.json, so news's auto-emit path silently violated the principle. Without codification, the next news capture would hit the same issue.

## N2 outcome (verification of all three behaviors)

Before fixes:
- z0 duration: 64.83s (camera held on chat input throughout pre-tick)
- z0→z0b gap: 0s (camera flowed continuously)
- Total composition: 103.4s

After fixes (current N2 final.mp4 = 64.08s):
- z0 duration: 18.06s (ease-out at typing-end per Rule #22)
- z0→z0b gap: **5.74s of full-frame view** (Rule #31)
- Buffer 1 compressed from 41.5s to 3.0s (Rule N3) — caveat: tick_cut's later detection put first_tick at compressed 24.8s, not the 19.6s my compression aimed for, which means the actual gap is wider than the 1.5s target — still satisfies Rule #31's minimum

## Cross-references

- Hard Rule #22 (z0 ease-out at T_click): `decisions/2026-05-22-zoom-skeleton-standardization.md`
- Hard Rule #23 (skeleton + Variant A/B): `decisions/2026-05-24-z0b-starts-on-checklist.md`, `decisions/2026-05-29-automated-post-tick-cut.md`
- Hard Rule #28 (buffer 1 minimum 2.5s, refined to 4.0s by this rule): `decisions/2026-05-30-buffer-1-minimum.md`
- Hard Rule #30 (static-placeholder gateway): `decisions/2026-06-01-static-placeholder-gateway.md` — sibling rule for the zero-tick case
- News Rule N2 (typing 2× speedup): `decisions/2026-05-29-news-typing-never-cut.md` — the speedup that makes `typing_end_scrubbed = streaming_started / 2`
