# 2026-05-29 — Product-demo adaptive prompt-typing speedup (Hard Rule #21 zone (a) refinement)

**Scope:** Product-demo pipeline only. News-pipeline's Rule N2 (always-2× regardless of duration) is unchanged.

**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #21 zone (a) refined; Hard Rule #22 updated with the raw-vs-scrubbed conversion), `.claude/skills/parallax-video/SKILL.md` (Phase 3 dispatch step 6 + Phase 5 z0 sizing both updated to compute and apply the adaptive factor).

## Decision

Hard Rule #21 zone (a) — prompt typing → submit click — was originally locked at **always 1×** under the rationale that "the persona's question gets named in the customer's chair here; the value-framing for the whole video anchors at this moment" and "typing-at-2× reads as comedic." That holds for the canonical short NL prompts (V1, V2, V3 — typing under ~10s). It does NOT hold for genuinely long prompts: V13 family-office onboarding, I3 quad-client demonstration, hero playbooks. A 20–40s 1× typing segment burns dead-air and loses the viewer.

**New rule:**
- `typing_duration ≤ 10s` → `typing_factor = 1.0` (no speedup; existing behavior)
- `typing_duration > 10s` → `typing_factor = min(2.0, max(1.0, typing_duration / 10.0))` (adaptive speedup, capped at 2×)

Worked examples:

| Raw typing | typing_factor | Post-speedup |
|---|---|---|
| 8s | 1.0 | 8s |
| 10s | 1.0 | 10s |
| 12s | 1.2 | 10s |
| 15s | 1.5 | 10s |
| 20s | 2.0 | 10s |
| 30s | 2.0 (capped) | 15s |
| 40s | 2.0 (capped) | 20s |

The 10s threshold = upper bound of "tolerable 1× typing" (a short NL prompt of ~2–3 sentences, the canonical V1/V2/V3 shape).

The 2× cap = upper bound before keystroke-rate visibly registers as machine-fast and breaks the customer's-chair register.

For raw typing >20s, the post-speedup duration grows linearly (`raw / 2`) — accept some long-prompt videos will have 15–20s of post-speedup typing; that's still readable, just paced. The alternative (>2× speedup) is worse: keystrokes blur into noise, the prompt becomes unreadable, the persona's voice gets lost.

## Why a rule, not just code

The behavior encodes a viewer-experience tradeoff (readability vs. dead-air) with a non-obvious why. Without the rule documentation, future maintainers see a `--force-speed-range "0:T:<factor>"` invocation with adaptive math and don't know:
- Why the 10s threshold (not 5s or 15s)
- Why the 2× cap (not 1.5× or 3×)
- Why it diverges from news's always-2× rule
- Whether to apply it to news's pipeline too

Codifying as Hard Rule #21 zone (a) refinement preserves these tradeoffs across maintenance.

## Why this diverges from news's Rule N2

News's typing is **context**, not deliverable content. The prompt is "what someone might ask"; the deliverable is the response that follows. Aggressive 2× speedup across all news typing is fine — viewers don't need to read every keystroke; they just need to know what the question was.

Product-demo's typing IS deliverable content. The persona's NL prompt is the customer's-chair moment — the viewer reads it, the value-framing anchors on it, the VO references it verbatim. Speeding it up unconditionally would damage the customer's-chair register the rule set has invested heavily in (see `references/production-principles.md` Customer's-chair framing, `video-scriptwriting/SKILL.md` use_case Quality Check #9, the entire vocabulary-lock discipline).

The adaptive rule resolves the conflict: short prompts (the canonical case) stay 1× to preserve the customer's-chair register; long prompts get just enough speedup to avoid dead-air, capped before keystrokes go incomprehensible.

## Implementation

**Phase 3 dispatch (`parallax-video/SKILL.md`)** step 6 now:
1. Reads `T_typing_end` from `manifest.phases.streaming_started − 0.5s` (auto-capture) or frame-samples for it (manual)
2. Computes `typing_duration = T_typing_end - 0` and derives `typing_factor`
3. Builds `--force-speed-range "0:T_typing_end:<typing_factor>,T_first_tick:T_(N-1):1.0,T_brief_landed:end:1.0"` and passes to `tools/scrub.py`

**Phase 5 dispatch** z0 sizing now computes scrubbed-time duration: `(T_typing_end_raw / typing_factor) + ease_out`. For the canonical 1× case this is unchanged (`T_typing_end_raw + ease_out`); for the adaptive case it produces the correctly compressed duration.

**Hard Rule #22** updated with the raw-vs-scrubbed conversion in z0/z0b sizing.

## Why no new code in tools/

`tools/scrub.py` already supports `--force-speed-range` with arbitrary factors. The adaptive math lives in the orchestrator (the parallax-video skill at dispatch time) which has access to the manifest. No tool changes needed.

## User context

> "lets do n2 now. default 1x but if the prompt typing segment takes longer than 10s, speed up. adjust speed accordingly based on how much the segment overshoots, eg a 30 second segment shld use a 2x speed but a 15 second segment that only overshot by 5 seconds can maybe use 1.5x speed etc"

The adaptive formula matches the user's examples (15s → 1.5×; 30s → 2× capped). The threshold (10s) was derived from the user's framing "longer than 10s." The cap (2×) was suggested in my prior message and confirmed implicitly by the user's "30 second segment should use a 2× speed" example (formula without cap would give 3× for 30s).

## Cross-references

- News's N2 (always-2×, news-only): `decisions/2026-05-29-news-typing-never-cut.md`
- N1 case (a) global promotion (companion rule extracted from news same day): `decisions/2026-05-29-post-streaming-deadtime-cap-global.md`
- Hard Rule #22 (z0 sizing — updated with raw-vs-scrubbed conversion): `decisions/2026-05-22-zoom-skeleton-standardization.md`
- Pass 1 + 2 architecture extraction (branch `extract-automation-layer`)
