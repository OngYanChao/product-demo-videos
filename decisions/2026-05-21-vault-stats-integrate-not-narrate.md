# 2026-05-21 — Vault Stats Integrate, Not Narrate

**Status:** active
**Affects:** `references/production-principles.md` (new principle), `.claude/skills/video-scriptwriting/SKILL.md` (use_case section — new sub-rule with two-mold inclusion test), `Parallax Video Plan - MASTER.md` (V1–V16 Highlights stop owning vault stats as ownership claims; vault-stats library kept as reference of what stats exist), `scripts/V1 voiceover script.md` (LT2 dropped, ICIR beat dropped, stats integrated into output-interpretation beats)

## Decision

Vault stats appear in use-case videos (V1–V16) **only when load-bearing for one of two molds**:

1. **Problem-solving** — the stat explains *why* the spotlit output element actually solves the viewer's client-facing problem (e.g., "Value at three — peer-ranked against AVGO, AMD, ARM and the broader sixty-two-thousand-listing universe" — the 62k stat makes "peer-adjusted" concrete for *this specific* Value reading)
2. **Why-can't-Claude** — the stat names what Parallax has that an LLM-alone can't produce, anchored to *this* output (e.g., "Thirteen years of factor history says: this is what a repricing looks like, not what a thesis break looks like" — the 13-year stat is doing analytic work for the trajectory interpretation, not standing alone as credibility)

**Standalone "credibility ribbon" beats are out.** No LT graphic that just lists ICIR / years / listings / markets as a stat row. No VO beat that recites stats without anchoring them to a specific output moment. Stats appear *next to* the output they explain, doing the work of one of the two molds above.

## Why

User feedback today: *"to be honest do we even need to talk about icir and vault stats? and this kind of general content highlighting parallax's upsides. feels a bit filler. especially when we want to showcase the output"* — followed by the refinement *"what if we integrate vault stats into the explanation of the output, remember how i highlighted the script/panels for the output should come from a 'how does this solve the clients problem' problem solving perspective, as well as a 'why cant claude do this by itself' perspective."*

The original "Highlights ownership" rule (production-principles #N) was designed to prevent vault-stat repetition across videos by assigning each stat to a single owner-video. It assumed stats *should* appear in videos. This decision questions the assumption itself for use-case videos:

- **The product is the credibility argument.** A brief that lands in <60s with sourced panels (Source: Parallax Fundamentals / Factor Scores / Research) and a methodology trace IS the credibility proof. Stating "ICIR 4.10" alongside is told-not-shown — like adding a "We're Real" sticker to a working product.
- **Sophisticated audiences distrust stated credibility.** MFO / RIA / PM / CIO viewers have been pitched track records their whole careers. What they can't discount is watching the brief assemble with provable lineage.
- **Stats that interrupt narrative interrupt narrative.** Use-case videos are narratives: client question → workflow → defensible answer. A credibility-stat-ribbon beat in the middle is a brochure inside a story.

The integration-not-narration rule preserves the *useful* function of vault stats (explaining what makes Parallax outputs defensible for a specific case) while eliminating the *ornamental* function (generic credibility ribbon).

## Notes

- **Side-effect — which stats survive integration:** stats with intuitive numeracy (*13 years live*, *62k listings*, *48 markets*, *30+ alpha signals*) integrate naturally into output explanations. Stats requiring their own definition (*ICIR 4.10*, *Sharpe 2.34*, *+5.8%/yr selection return*) don't integrate cleanly — they need standalone explanation, which the rule forbids. So those jargon-stats migrate to methodology-deep-dive videos (V9, hero playbooks) or out-of-slate marketing surfaces (one-pagers, methodology decks, pricing pages).
- **Instructional videos (I1–I4) are the natural home for orientation-style stats.** First-time viewer asking "what IS Parallax?" — that's where credibility framing is contextually justified. *"Parallax runs on 13 years of factor scoring across 62,000+ listings. Now let's get it installed."* One sentence, contextually anchored, then move on. The integration-not-narration rule applies less strictly to instructionals because the *job* of an instructional is partly orientation.
- **Highlights ownership rule narrows scope.** Previously: prevent stat repetition across videos by assigning each stat one owner. Now: use-case videos own *output moments* and *value angles*, not vault stats. Stats appear in scripts only when they integrate naturally with those moments — no per-video ownership claim. The "vault stats library" in MASTER.md stays as a reference for *which stats exist* (so authors can pull from it when integration is load-bearing), but it's no longer a distribution map.
- **V1.2 application** (companion to this decision): LT2 dropped entirely (was a four-stat credibility ribbon); ICIR/Sharpe/+5.8% beat at r=0:22 dropped; "13 years live" integrated into the processing-matters beat (r=0:09) and the trajectory beat (r=1:08); "62k listings" integrated into the Value-row beat (r=0:50). ICIR, Sharpe, +5.8% specifically don't appear in V1.2 — they migrate to V9 (Deep Dive) or out-of-slate.
- **Test for whether a stat earns its place:** ask, *"if this stat weren't in the script, would the viewer fail to understand what the spotlit output element does or why it's defensible?"* If yes — keep it (integrated). If no — drop it (it's narrating credibility, not explaining the output).
- **Cross-references:** Customer's-chair framing (production-principles #13), Hard Rule #6(b) rhythm pass (the integration adds words, which Phase 6a accounts for), Panel content authoring (`video-scriptwriting/SKILL.md` — panels were already constrained to capability/workflow/stakes; the integration extends the same discipline to VO body).
