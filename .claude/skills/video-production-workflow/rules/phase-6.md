# Phase 6 / 6a / 6b / 6c / 9 rules — Render + polish + lint + review (both pipelines)

Read these when invoking any of: Phase 6 (preview render), Phase 6a (polish), Phase 6b (lint), Phase 6c (review), Phase 9 (final render). Cross-load `meta.md`.

Most rules in these phases live in the orchestrator (parallax-video Phase 6/6a/6b/6c dispatch rows) and in the deterministic tools (`tools/lint_video.py`, `tools/review_video.py`). This file covers the workflow-level rules.

---

## Hard Rule #8 — Preview is free; final is billed.

Iterate on layout, timing, and copy at preview. Promote to final only when the preview is shippable.

`tools/render.py --mode preview` runs the Hyperframes composition without invoking HeyGen. Final render (`--mode final`) generates the avatar clip via HeyGen — billed per clip. Cache the avatar clip by script-body hash so unchanged scripts don't re-bill on layout-only iterations.

---

## Hard Rule #12 — Re-derive timings after every zoom/scrub re-run.

If Phase 6a (polish) re-fires zoom or scrub via the backup loop (Hard Rule #6(d)), re-derive `lower_thirds[].in/out_recording_t` and `annotations[].in/out_recording_t` against the new zoomed file BEFORE re-rendering. Full mechanism in `phase-5-5-product-demo.md`.

---

## Hard Rule #6 — Phase 6a editorial decisions.

Cases (b)/(c)/(d) of Hard Rule #6 fire in Phase 6a. Full text in `phase-5.md`. Phase 6a auto-runs after every Phase 5 + Phase 6.

---

## Phase 6a polish pass — the seven-step protocol

Phase 6a runs automatically after Phase 5 completion (script change) AND after Phase 6 completion (preview re-render). The seven steps + backup loop:

1. **Sync check** — frontmatter timings match zoomed file's segment timings (Hard Rule #12).
2. **Beat coverage check** — every spoken VO beat maps to a panel, LT, or zoom hold; catch orphans.
3. **Runtime check** — measure rendered runtime against speakable window; decides between rhythm pass and beat cut.
4. **Rhythm pass (runtime fits)** — Hard Rule #6(b). Per-beat overflow check triggers backup loop (step 5b).
5. **Beat cut (runtime overflows globally)** — Hard Rule #6(c). Drop lowest-priority beat.
5b. **Backup loop — re-open Phase 1** — Hard Rule #6(d). Extend beat target, update zoom duration, re-cascade.
6. **LT + panel update (conditional)** — only if Phase 5 cut beats or step 5 dropped one.
7. **Re-render preview** if any edits were applied. Otherwise report "clean."

**Convergence:** idempotent — converges within 1–2 passes. If keeps making edits across iterations, investigate.

**Hand-off:** on "clean" → auto-chains into Phase 6b (lint).

---

## Phase 6b lint — deterministic mechanical check.

Runs after every Phase 6a "clean" convergence and after every Phase 9 final render. One finding per violated Hard Rule.

**Severity tiers:**
- **Tier 1 errors** — STOP the chain. Concrete numeric thresholds: framerate ≠ 60, keyframe interval > 1s, frontmatter timing drift, panel hold below `min_hold` floor, safe-zone position outside 30–70%, highlight height > tier-2 cap, skeleton element missing, z0b sizing off, etc.
- **Tier 2 warnings** — chain continues to Phase 6c. Softer violations (banned-engineering-phrase substring, slash-command-in-VO, capability-count pattern, draft markers).

**Hand-off:** if no Tier 1 errors → auto-chain into Phase 6c.

---

## Phase 6c semantic review — LLM-grounded.

Runs after every Phase 6b tier-1-clean pass. The reviewer expects a lint-passing artifact — lint-gates-reviewer ensures the API spend isn't wasted on a broken artifact.

**Six checks:**
- **R01** subject-match (spotlight ↔ panel pitch, frame-level)
- **R02** customer's-chair framing (text)
- **R03** panel-shape rotation (text)
- **R04** vault-stat integration (text)
- **R05** beat content visible in recording (frame)
- **R06** hallucination check on `frames_used:` (frame, Hard Rule #7)

**Cost:** first run ~$0.25, $0 on cache hits against unchanged input. Caching is load-bearing — without it, every Phase 6a convergence would re-bill.

**Verdicts:** pass / drift / fail per rule. Chain does NOT auto-stop on findings — surfaces to user for re-open decisions.

**Skip:** `--no-review` flag for cost-sensitive iterations.
