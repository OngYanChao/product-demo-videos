# Project Decisions

This file archives strategic, architectural, and craft decisions made during the Parallax video project's evolution. Each entry captures: **what** was decided, **why**, what **alternative** was rejected, and **when**. Purpose: don't re-litigate the same question every few sessions.

**This is not a rules file.** Rules live elsewhere:

| Rule type | Home |
|---|---|
| Portable video-production methodology (beat sheet upstream, conform-not-compress, never-slow, framerate consistency, cleanup gate, zoom sized by beat sheet, overlay-ease-matches-camera, source-segment cleaning, two-pass script rhythm with Phase 6a polish, …) | `.claude/skills/video-production-workflow/SKILL.md` Hard Rules #1–#19 + Phase 6a |
| Script craft (voice composite, banned words, hallucination check, value framing, vocabulary lock) | `.claude/skills/video-scriptwriting/SKILL.md` |
| Parallax-project dispatch (commands, file paths, scrub thresholds) | `.claude/skills/parallax-video/SKILL.md` |
| Per-template format invariants (layout, taglines, char limits, animation timings) | `templates/<family>/RENDER-GUIDE.md` |

**Update discipline.** To add a decision: append a new entry under the appropriate section (Architectural / Strategic / Craft) with the decision / why / rejected / trade-off / when structure. Don't add rules here — those go in their respective skill or doc file per the table above.

---

## Architectural decisions

### Zoom runs at Phase 5.5 (post-script), not Phase 3 (with scrub)

**Decided:** 2026-05-15

**What:** Moved the zoom phase from Phase 3 (alongside scrub) to a new Phase 5.5 (after the script is locked). Phase 3 is now scrub-only; Phase 5.5 applies zoom directives derived from the script.

**Why:** Zoom region = the bounding box of what the VO names. With zoom in Phase 3 the script didn't exist yet, so zoom regions had to be guessed from the recording alone — then the script had to bend around guessed regions, or named content the zoom missed entirely. Putting zoom after the script lets script content drive region selection from VO names directly.

**Rejected alternative:** Keep zoom in Phase 3 with placeholder regions, fill in regions at script time. This required re-running zoom after script anyway, and underline measurements had to be redone against post-zoom timestamps.

**Trade-off accepted:** Adds an extra Phase 5.5 step between script and render. Worth it because zoom now serves the VO instead of being a separate artifact the script must accommodate.

---

### Pragmatic mode for beat sheet (rough guidance, not strict timeline)

**Decided:** 2026-05-13 (per memory `feedback_pragmatic_mode.md`)

**What:** Beat sheet target seconds are rough guidance for what to record and roughly how long. The zoomed recording's actual beat windows are the canonical downstream timeline, not the beat sheet's targets.

**Why:** User explicit: *"I just can't be bothered to do the screen recording the same timing as the beat sheet so the beat sheet is just there for like rough guidance."* Trying to record to exact beat-sheet timings added recording-day friction without proportional value — Phase 3 scrub + Phase 5.5 zoom absorb the drift.

**Rejected alternative:** Strict mode (beat-sheet seconds are canonical; recording must conform exactly to per-beat targets via aggressive scrub/slowdown).

**Trade-off accepted:** LT/script timing must always be re-derived against the zoomed recording after every re-conform — codified as workflow Hard Rule #12. Symptom of forgetting: LTs land on the wrong content.

---

### HeyGen v2 templates → local Hyperframes rendering

**Decided:** 2026-04-29 → 2026-05-11

**What:** Migrated the rendering pipeline from HeyGen v2 templates (cloud-based, per-render billing) to local Hyperframes (HTML composition + FFmpeg, free local iteration). HeyGen is retained ONLY for the avatar talking-head clip; everything else renders locally.

**Why:** HeyGen v2 sunsets October 31, 2026 — staying meant a forced migration eventually. Hyperframes gives free local iteration (preview renders cost $0) and full composition control via HTML + GSAP, vs HeyGen v2's template constraints. Avatar generation is still HeyGen-best — kept as the only billable step.

**Rejected alternative:** Stay on HeyGen v2 until forced sunset.

**Trade-off accepted:** Local complexity goes up (template authoring via Claude Design, render orchestration via `tools/render.py`, browser-based capture pipeline). Iteration cost goes way down. Avatar clips are cached by script hash so unchanged VO doesn't re-bill.

---

## Strategic decisions

### 28-video plan → 20-video persona-and-moment plan

**Decided:** 2026-05-11 → 2026-05-13

**What:** Reorganized the master plan from 28 videos organized by Parallax capability/tool to 20 videos organized around `persona × specific moment × deliverable`. Resulting slate: 4 instructional (I1–I4) + 16 use_case (V1–V16).

**Why:** A capability-organized catalogue tells the viewer *what the tool does*. A persona-and-moment-organized catalogue lets the buyer *see themselves in their own working day*. Conviction for fintech buyers (PMs, analysts, compliance officers, RIAs, family-office analysts) comes from recognition, not feature exposure.

**Rejected alternative:** Keep the 28-video capability-organized plan.

**Trade-off accepted:** Lost some capability-coverage breadth, but gained tighter persona-fit per video. The 8 Parallax capabilities aren't all individually showcased anymore — they appear in service of a persona's moment. Legacy 28-video plan archived to `_archive/MASTER-pre-overhaul-2026-05-11.md`.

---

### Stock HeyGen avatar (no custom Chicago Global twin)

**Decided:** ~2026-04-29

**What:** All 20 videos use the same stock HeyGen avatar + voice (defined in `.env` as `HEYGEN_AVATAR_ID` + `HEYGEN_VOICE_ID`). No custom-trained twin of a specific Chicago Global presenter. Per-video override available via script frontmatter (currently unused).

**Why:** Cost predictability per video, brand consistency across the entire 20-video catalogue, and no operational dependency on individual on-camera availability or recording-studio time.

**Rejected alternative:** Custom Chicago Global presenter twin.

**Trade-off accepted:** Less personalized than a twin, but operationally simpler and cheaper to scale. Brand presence is carried by the Chicago Global logo watermark + Parallax product chrome in the recording — the avatar is supporting cast, not the brand carrier.

---

### Intel-brief stream paused (deferred future addition)

**Decided:** 2026-05-13 (per `overhaul.md` Phase 5)

**What:** Don't build the intel-brief template family right now. Infrastructure (style enum in `video-scriptwriting/`, frontmatter `style:` field, paused-stub doc) is preserved so reactivation is a clean drop-in.

**Why:** The persona-and-moment overhaul consumes available production capacity. Intel briefs require a separate template family (Claude Design session) + a per-video vault-sourcing workflow that doesn't exist yet.

**Rejected alternative:** Build intel-brief in parallel with the persona-and-moment overhaul.

**Trade-off accepted:** Deferred a content stream. When ready: run a Claude Design session for the intel-brief template, fill in the paused stub in `video-scriptwriting/SKILL.md`, point `tools/render.py` at the new template family.

---

### Production order: V1 canary → I1–I4 → V2–V6 → V7–V13 → V14–V16

**Decided:** 2026-05-13

**What:** Production sequence is V1 canary first, then Tier 0 instructional (I1–I4), then Tier 1 single-feature (V2–V6), then Tier 2 workflow-chain (V7–V13), then Tier 3 hero playbooks (V14–V16).

**Why:** V1 acts as the canary — every production lesson (recording technique, scrub thresholds, conform discipline, voiceover register, avatar handoff, lower-third timing) gets surfaced and resolved on one 90-second video before the system tries to produce 19 more. Subsequent tiers ship in order of increasing complexity/risk.

**Rejected alternative:** Parallel production of all tiers, or random ordering by what looks easy in any given week.

**Trade-off accepted:** Slower start. Worth it because production cost is multiplied by 19 if a craft rule is wrong at scale.

---

## Parallax-specific craft decisions

### Series cohesion: cross-video beat overlap is preferred for cutting

**Decided:** original convention, codified during V1 production

**What:** Before cutting a beat from V<N>, check whether the master plan covers the same territory elsewhere. Beats overlapping with other videos are cheaper to drop (the viewer encounters that content in the adjacent demo). Beats unique to a given video are load-bearing.

**Why:** The 20 videos are a series, not 20 independent pieces. Cutting an overlapping beat reinforces each video's distinct role. Cutting a unique beat leaves a gap the series never fills.

**Applied to V1:** The four cut beats (Financial Health, Macro, Risk vs Peers, Analyst View) all have deeper coverage in V9 (Full Deep Dive) or dedicated videos (V6 Macro Intelligence). The beats that survived (parallel-call framing, ICIR callout, trajectory story, bottom line) are V1-unique.

**Operationally encoded in:** `video-scriptwriting/SKILL.md` Quality Check #4 + `parallax-video/SKILL.md` `"write V<N>"` cross-video overlap scan.

---

### Budget-first script drafting (plan the ramp before drafting)

**Decided:** original — codified after V1's first-draft rewrite cycles

**What:** The ramped video duration sets the word budget; draft to the budget, not to the script.

**The math:**

```
ramped_duration    = sum(segment_length × speed_multiplier)
max_audio_duration = ramped_duration × 1.3        # 30% held-frame tolerance
word_budget        = max_audio_duration × wpm / 60
```

**Pace anchors:** ~150 wpm for HeyGen avatar voice (or a human voice actor); ~110 wpm for edge-tts Christopher at `+8%` rate (legacy — not used since HeyGen migration).

**Why:** Computing budget after drafting produces scripts that overshoot and have to be cut multiple times. V1's first draft at 385 words had to be rewritten twice to fit a ramp that only supported ~235 words.

**Operationally encoded in:** `parallax-video/SKILL.md` `"write V<N>"` dispatch row.

---

### Every use_case beat states value explicitly

**Decided:** marketing direction confirmed 2026-05-11

**What:** Every beat in a `use_case` style script answers three questions for the viewer: **(1)** what is this on screen, **(2)** what problem does it solve, **(3)** why does it matter to me. Question 3 must be a labeled clause, not inferred.

**Per-tier value-framing rotation:** Tier 1 = 5–7 angles per ~90s of content; Tier 2 = 8–10; Tier 3 = up to 12. Repetition of one angle across consecutive beats triggers a rewrite. The canonical 12-angle menu lives at `references/value-framing-menu.md`.

**Style-axis qualifier:** Applies to `use_case` style only. **Does not apply to `instructional`** (collapses to hook + close only — per-beat explicit value clauses would interrupt the literal click-by-click sequence). `intel_brief` is paused.

**Why:** Sophisticated audiences (PMs, RMs, analysts) evaluate tools by asking *what does this do for me*. A demo that only describes features fails the mute test in slow motion.

**Moat angles** (auditability, determinism, failure isolation, unverifiable frame) sourced from `parallax-obsidian/04-Marketing/Auditability and the Unverifiable Frame.md`. Failure isolation targets risk/ops audiences and rarely headlines product demos — secondary-mention only unless a dedicated engineering-audience video is built.

**Operationally encoded in:** `video-scriptwriting/SKILL.md` use_case section Quality Checks #6 + #7 + `references/value-framing-menu.md`.

---

### Natural-language prompts in demo; slash commands annotated, never typed

**Decided:** original convention V0+V1; promoted to a locked decision 2026-05-12

**What:** The demo user types a natural-language prompt into the AI client — e.g. *"Run a deep dive on NVDA using Parallax"* — never a slash command like `/parallax:deep-dive NVDA`. Slash commands and underlying MCP tools appear only as on-screen annotations: lower-third labels, underline highlights, callouts. The VO never reads a slash command aloud.

**Three reasons:**

- **Portability across clients.** Only Claude Code consumes the full Parallax plugin with `/parallax:*` slash commands. The other three supported clients (Claude Desktop, Codex CLI, Qwen CLI) get raw MCP tools — no slash commands, no embedded skill guidance. NL prompts work across all four. A demo built around a slash command teaches a workflow 75% of supported clients can't reproduce.
- **Buyer-facing tone.** Slash commands read as developer-tool; NL prompts read as product. The audience (RM, PM, analyst, compliance, family-office analyst) is not developer-coded.
- **Honest register match.** The screen recording IS a chat-style interaction. CLI vocabulary in the VO on top of a chat UI feels forced. NL prompts let the VO and the recording carry the same register.

**Style-axis qualifier:** Applies to `use_case` style (Tier 1 / 2 / 3). **Instructional carve-out:** slash commands MAY appear typed in `instructional` videos when they ARE the literal action the viewer must reproduce — e.g., *"To verify the plugin loaded, type `/parallax:stock AAPL`."* The carve-out is narrow: only when the slash command IS the step.

**Operationally encoded in:** `video-scriptwriting/SKILL.md` use_case vocabulary lock (NL prompts verbatim in VO; LT eyebrow/headline names the product module — Stock Report, Screener, Analyzer, ETF Analysis, Impact Analysis, Macro Intelligence, Shariah Screen) + `parallax-video/SKILL.md` `"write V<N>"` dispatch row.

---

### Customer's-chair framing: outcomes for the buyer, never system mechanics

**Decided:** 2026-05-19 — V1 LT feedback rejected the carried-over *"Eight parallel skill calls"* line as engineering-perspective

**What:** Every LT eyebrow / headline / stat, every annotation panel field, every VO line, and every MASTER Highlight in a `use_case` video frames the demo from the **buyer's** chair — what they get out of running Parallax, what it lets them say to a client or in an IC discussion, how it fits their workflow window. Never from the **system's** chair — internal mechanics, agent count, parallelism, MCP plumbing, tool-call orchestration.

**Reject list (engineering-perspective — never appears in copy):**

- *"Eight parallel skill calls"* / *"Ten tools fire at once"* (capability boast in builder language)
- *"MCP tool invocations"* / *"Agent orchestration"* / *"Skill calls"* (technical vocabulary the buyer doesn't speak)
- *"Watch as N things happen in parallel"* (mechanic-as-narrative)
- Anything that asks the viewer to imagine the system's plumbing to understand the value

**Require list (audience-perspective — every line should match one of these molds):**

- **Outcome framing** — *"Twenty minutes of research, in one prompt"*
- **Stakes framing** — *"Defensible read before the meeting"* / *"Citation-ready answer for the client"*
- **Workflow-fit framing** — *"Score, trajectory, bottom line — in 30 seconds"* / *"Under 60s, before your next call"*
- **Methodology-credibility** — *"Peer-reviewed factor model"* / *"62K listings, 13-year out-of-sample"*

**Style-axis qualifier:** Applies to `use_case` style (Tier 1 / 2 / 3). **Does not apply to `instructional`** — for I1–I4 tutorials the audience IS the technical/builder operator setting up the plugin, and system mechanics framing is the right register (*"Type `/parallax:stock AAPL`, press enter, watch all eight skills fire — that confirms the plugin loaded across all four MCP clients."* is the right framing for an instructional). The carve-out is narrow: only when the system mechanic IS the step the viewer must reproduce.

**Why:** The audience for `use_case` content (MFO / RIA / wealth advisor / PM / analyst — per each video's `primary_persona` in MASTER) evaluates a tool by asking *"what does this do for me when the client texts at 2pm before my 2:10 meeting?"* They are not engineers evaluating system architecture. Engineering framing reads as either irrelevant (they tune it out) or as defensive over-explanation (they wonder what's broken). Buyer framing reads as confident workflow design.

**How we found it:** V1's original draft carried over *"Plain English in. Eight parallel calls out."* from the pre-overhaul demo plan. User feedback rejected the second half as engineering-perspective — the viewer is a financial professional, not a builder. The fix is *"Plain English in. Defensible brief out."* (preserves the parallel structure, swaps the mechanic for the outcome).

**Operationally encoded in:** `video-scriptwriting/SKILL.md` use_case Quality Check (drafted alongside this principle) + `parallax-video/SKILL.md` `"write V<N>"` dispatch row (names this principle so it's read at Phase 5) + `Parallax Video Plan - MASTER.md` per-video Highlights subsections (authored customer-perspective at the source-of-truth level).

---

### Highlights ownership: no within-stream stat reuse

**Decided:** original convention, codified after V1→V2 ICIR repetition was caught. **Narrowed 2026-05-21** — see "Vault stats integrate, not narrate" below.

**What:** Within a single content stream (master-plan ↔ master-plan within the 20-video catalogue), no stat is reused across videos. Each master-plan video's `**Highlights**` subsection in MASTER.md declares its single-owner stats.

**Cross-stream reuse IS allowed:** a master-plan video and an intel brief (when reactivated) can both cite the same stat — e.g., ICIR 4.10. The constraint is only on within-stream duplication.

**Why:** The 20 master-plan videos are seen in sequence (buyer eval flow, sales walkthrough). Within-stream repetition reads as padding (*"didn't they already say that?"*). Cross-stream reuse is fine because the audiences and viewing contexts differ.

**Narrowing 2026-05-21:** This rule only applies to stats that *appear in the video*. Per the "Vault stats integrate, not narrate" decision, use-case videos (V1–V16) no longer assign vault stats as ownership claims by default — stats appear only when load-bearing for a specific output moment. The vault-stats library in MASTER.md becomes a *reference of available stats* that authors can draw from, not a distribution map. Within-stream reuse is still checked at script-write time, but the scope of stats to check has shrunk substantially.

**How we found it:** An early V2 draft re-used V1's ICIR 4.10 callout. In back-to-back V1→V2 playback, the repetition felt like the producer ran out of stats.

**Operationally encoded in:** `Parallax Video Plan - MASTER.md` per-video Highlights subsections (single-owner declarations for stats that *do* appear) + `video-scriptwriting/SKILL.md` stat-overlap Quality Check.

---

### Vault stats integrate, not narrate

**Decided:** 2026-05-21

**What:** Vault stats appear in use-case videos (V1–V16) **only when load-bearing for one of two molds**:

1. **Problem-solving** — the stat explains *why* the spotlit output element solves the viewer's client-facing problem (e.g., *"Value at three — peer-ranked against AVGO, AMD, ARM and the broader sixty-two-thousand-listing universe"* makes "peer-adjusted" concrete for *this specific* Value reading; the 62k stat is doing analytic work).
2. **Why-can't-Claude** — the stat names what Parallax has that an LLM-alone can't produce, anchored to *this* output (e.g., *"Thirteen years of factor history says: this is what a repricing looks like, not what a thesis break looks like"* — the 13-year stat enables the trajectory interpretation; without it the analytic claim has no basis).

**Standalone "credibility ribbon" beats are out.** No LT graphic that lists ICIR / years / listings / markets as a stat row. No VO beat that recites stats without anchoring them to a specific output moment.

**The test:** *"If this stat weren't in the script, would the viewer fail to understand what the spotlit output element does or why it's defensible?"* If yes → keep (integrated). If no → drop (it's narrating credibility, not explaining the output).

**Why:** Use-case videos are narratives (client question → workflow → defensible answer). Standalone credibility-stat beats interrupt the narrative with brochure content. The product itself — a brief that lands in <60s with sourced citations and methodology traces — IS the credibility argument. Stating "ICIR 4.10" alongside is told-not-shown. Sophisticated audiences (MFO / RIA / PM / CIO) have been pitched track records their whole careers; they discount stated credibility but can't discount watching a brief assemble with provable lineage.

**Rejected alternative:** "Spread stats across videos for credibility distribution" (original Highlights ownership framing). This was solving a real problem (within-stream stat repetition) but on a false premise — that stats should appear in videos by default. The new rule says they appear only when functional.

**Side-effect — which stats survive integration:** stats with intuitive numeracy (*13 years live*, *62k listings*, *48 markets*, *30+ alpha signals*) integrate naturally into output explanations. Stats requiring their own definition (*ICIR 4.10*, *Sharpe 2.34*, *+5.8%/yr selection return*) don't integrate cleanly — they need standalone explanation, which the rule forbids. So those jargon-stats migrate to methodology-deep-dive videos (V9, hero playbooks V14–V16) or out-of-slate marketing surfaces (one-pagers, methodology decks).

**Instructional carve-out:** Instructional videos (I1–I4) have orientation as part of their job — they can carry vault stats more freely, because a first-time viewer asking "what IS Parallax?" needs some credibility framing to know what they're learning to use. The two-mold inclusion test still applies (stats serve a purpose), but the bar is lower for instructionals than use-cases.

**How we found it:** V1.2 draft had an LT2 ribbon (*"Vault stat · Peer-reviewed · Out-of-sample / ICIR 4.10 · Information coefficient ranking"* + four-stat row) and a VO beat at r=0:22 reciting the same stats. User: *"to be honest do we even need to talk about icir and vault stats? and this kind of general content highlighting parallax's upsides. feels a bit filler. especially when we want to showcase the output."* The refinement: *"what if we integrate vault stats into the explanation of the output."*

**Trade-off accepted:** Total runtime of use-case videos shrinks by ~8–12s per video (the credibility-beat allocation goes away). Vault stats that don't integrate (ICIR, Sharpe, +5.8%/yr) become invisible inside V1–V16 — they live in V9 / V14–V16 methodology contexts or out-of-slate. Marketing-collateral users may need to source those stats from one-pagers instead of pulling clips from V<N> videos. Acceptable: the videos do their job better; the stats live where they earn their place.

**Operationally encoded in:** `references/production-principles.md` (this entry), `.claude/skills/video-scriptwriting/SKILL.md` use_case section (two-mold inclusion test), `Parallax Video Plan - MASTER.md` (V1–V16 Highlights no longer declare vault-stat ownership; vault-stats library is reference-only), `scripts/V1 voiceover script.md` (canary application — LT2 dropped, ICIR beat dropped, 13-years + 62k integrated). ADR: `decisions/2026-05-21-vault-stats-integrate-not-narrate.md`.

---

## Cross-reference table

| Decision | Where it's operationally enforced |
|---|---|
| Zoom at Phase 5.5 | `video-production-workflow/` Phase 5.5 + `parallax-video/` "zoom V<N>" row + `tools/zoom.py` + `tools/render.py` (prefers `*_zoomed.mp4`) |
| Pragmatic mode for beat sheet | `video-production-workflow/` Hard Rule #12 + memory `feedback_pragmatic_mode.md` |
| HeyGen v2 → Hyperframes | `tools/render.py` + `parallax-video/` render rows + `.env` HeyGen credentials |
| 28→20 video overhaul | `Parallax Video Plan - MASTER.md` NEW SLATE section + `_archive/MASTER-pre-overhaul-2026-05-11.md` |
| Stock HeyGen avatar | `.env` (`HEYGEN_AVATAR_ID` + `HEYGEN_VOICE_ID`) + `tools/render.py --mode final` |
| Intel-brief paused | `video-scriptwriting/` paused-stub section + `overhaul.md` Phase 5 |
| V1 canary production order | `overhaul.md` Phase 7 plan |
| Series cohesion (beat cutting) | `video-scriptwriting/` QC #4 + `parallax-video/` "write V<N>" row |
| Budget-first drafting | `parallax-video/` "write V<N>" row (word budget math) |
| Explicit per-beat value framing (use_case) | `video-scriptwriting/` QC #6 + #7 + `references/value-framing-menu.md` |
| Customer's-chair framing (use_case) | `video-scriptwriting/` use_case Quality Check + `parallax-video/` "write V<N>" dispatch row + MASTER per-video Highlights |
| Annotation panel content authoring (use_case) | `video-scriptwriting/` § "Panel content authoring" — capability framing not specifics, 3-shape rotation (capability/workflow/stakes), subject-match-to-spotlight, source+badge required |
| NL prompts in demo | `video-scriptwriting/` use_case vocabulary lock + `parallax-video/` "write V<N>" row |
| Highlights ownership (stat reuse, narrowed scope) | MASTER.md per-video Highlights + `video-scriptwriting/` overlap check |
| Vault stats integrate, not narrate | `references/production-principles.md` (this file) + `video-scriptwriting/` use_case § "Vault-stat inclusion test" + MASTER.md vault-stats-library is reference-only + per-script integration check at Phase 5/6a |
| news-pipeline as downstream consumer of quality rules | `news-pipeline/README.md` § "Hard rules inherited from the main pipeline" — maps each `video-production-workflow` Hard Rule (1–25) to applies-yes / applies-no for the news workflow. **When a Hard Rule changes in `.claude/skills/video-production-workflow/SKILL.md`, update that table too.** Quality rules carry through (60fps + 1s keyframes #15, measured-not-eyeballed #10/#20, re-derive after re-zoom #12, never slow source #13, source preserved until approval #14). Script-driven rules don't (beat sheet #1, hallucination check #7, dwell sizing #9, cursor-clear-on-brief #16, standard zoom skeleton #21–25). |
