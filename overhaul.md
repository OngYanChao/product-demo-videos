# Parallax Video Production — Overhaul Plan

*This file tracks the **active** overhaul of the Parallax video pipeline. One overhaul at a time; previous cycles get summarized here while active and cleared once their open items resolve.*

---

## Carry-over from prior overhaul *(HeyGen → Hyperframes-local, 2026-04-29 → 2026-05-11 — now complete; carry-over resolved 2026-05-13)*

The migration from HeyGen-template rendering to local Hyperframes (with HeyGen used only for the avatar talking-head clip) is **done**. All pipeline tooling, skills, templates, and orchestration are built and validated. Two deferred items have now been resolved alongside Phase 5 of the active overhaul:

- [x] **Intel-brief template (`templates/intel-brief/`)** — **SHELVED 2026-05-13** as a deferred-future-addition (not retired). The new persona-and-moment slate has zero intel-brief videos — it's all use_case + instructional. The intel-brief format (anchor-style market wraps, full-frame avatar, no live product) is a categorically different content type and isn't part of this overhaul's buyer-evaluation focus. Reactivation requires: (a) a use case for the format, (b) a Claude Design session to build the template, (c) re-opening the paused `intel_brief` style section in `video-scriptwriting/SKILL.md`. Infrastructure (style enum, frontmatter `style:` field accepting `intel_brief`, paused stub in skill) stays in place to make reactivation a clean drop-in rather than a refactor.

- [x] **V1 canary final render** — **DEFERRED 2026-05-13; RE-SCOPED 2026-05-14.** Original plan called for a full V1 re-record under the new framing. **Revised plan:** the existing V1 recording's product flow (Cowork chrome → `/parallax:stock` call → score panel → trajectory → bottom-line beat) is structurally correct for U-1. **What needs to change is the script (VO + LTs) and a small re-take of just the typed-prompt segment** — the original typed prompt (*"I keep hearing about NVIDIA — can you give me a quick rundown on whether it's actually worth the hype right now?"*) reads conversationally rather than in the formal professional register locked 2026-05-14 (`video-scriptwriting/SKILL.md` "typed-prompt register" rule). New prompt to type: *"Stock brief on NVDA — client query, need a defensible read on the position."* The re-take is ~30 seconds of recording (typed prompt only); the rest of the recording (post-prompt-typed) survives intact. Archive plan: current `scripts/V1 voiceover script.md` → `scripts/_archive/V1-original-2026-04-29.md` when re-script begins; the recording itself splices in the new prompt segment via `tools/scrub.py` or manual editing. HeyGen wallet top-up still needed before final render.

**Open technical curiosity (non-blocking):** avatar clip background — transparent, chroma-key, or solid. Will be observed on the first `--mode final` run; the template handles any of the three.

---

## Active overhaul: persona-and-moment-driven master plan rewrite *(opened 2026-05-11)*

**Driver.** A strategic-meeting feedback: the current 28-video master plan is organized around Parallax *capabilities* (one video per command/workflow). A video that demonstrates something a wide spread of client types could use is too broad. The new direction is **one video per specific persona × specific moment × specific outcome**.

**Approach.** Work backwards. Start from "a specific person doing a specific task at a specific moment, needing a specific deliverable" → identify the Parallax tools that chain together to produce that deliverable → *that* is the video.

**Audience.** Primary target = **end users of the platform** — relationship managers (RMs) and financial analysts who'd actually use Parallax day-to-day in their work. **Not** executive buyers (CEOs, CIOs-as-purchaser, ops/strategy heads, procurement). The personas in Phase 1 should be working-level: RM prepping a client meeting, analyst running a brief, PM responding to an event, etc. Executive-buyer-focused content (ROI pitch, vendor positioning vs Aladdin/Bloomberg, procurement objection-handling) is **out of scope** for this overhaul and would belong to a separate series if ever commissioned.

### Worked-example anchors

Concrete deliverables that represent "what good looks like" for a use-case video. Each anchor is a real artifact a working-level analyst/PM produced; the corresponding video would demonstrate how a viewer can produce the same deliverable using Parallax tools. As more anchor examples land, list them here so the Phase 1 persona inventory has tangible targets to map against.

| # | Anchor | Location | Persona × moment × deliverable |
|---|---|---|---|
| 1 | **Ivan's Iran / Korean Banks Playbook** — published "PM Playbook" by Ivan Cheloliev, 2026-03-02. Walks from macro event (Iran war over weekend, oil to $82) → indiscriminate sell-off setup → Hormuz-scenario impact table (sourced from Goldman Sachs Commodity Research) → factor screen of 5 Korean bank candidates with full metric table (sourced from Parallax) → contrarian thesis. | `references/use-case-examples/iran-playbook/` (6 screenshots) | **PM / financial analyst** × **a macro event breaks (weekend headline)** × **a publishable contrarian read, factor-screen-backed**. Multi-tool workflow: scenario analysis + factor screen + macro context, synthesized into a defensible piece. |

(More anchors to come as the overhaul scopes additional use cases.)

### Library tiers (all tiers in MASTER from day 1; ship simple → complex)

The use_case style splits into three complexity tiers; together with the instructional style (tier 0) they form the full library shape. **Every tier — including the single-feature ones — is persona-and-moment-anchored.** A Tier 1 single-feature video is NOT "demo the tool with a persona prefix"; it's *"PM Jane at 9am on Tuesday, before her 10am with a wealth client, runs a quick brief on the client's biggest holding."* Persona specificity carries even when only one tool is on screen.

| Tier | Style | Length | Shape | Viewer question | Example |
|---|---|---|---|---|---|
| **0** | `instructional` | 30–90s | Point-and-click utility | "How do I install / export / configure X?" | V0 install, format-flag demos, free-tier walkthroughs |
| **1** | `use_case` (single-feature) | 60–120s | Persona × moment × single tool × deliverable | "What does this feature do for me in this moment?" | RM running a quick brief 10 minutes before a client call |
| **2** | `use_case` (workflow chain) | 2–3 min | Persona × moment × 2–4 chained tools × composite deliverable | "How does this fit into my actual workflow?" | RM Tuesday-morning client review: health flags → rebalance → PDF memo |
| **3** | `use_case` (hero playbook) | 3–5 min | Persona × event-moment × full multi-tool workflow × publishable synthesis | "What's the most defensible read this platform can produce?" | PM responding to an event → scenario + factor screen + contrarian thesis *(see worked-example anchor #1: Ivan's Iran playbook)* |

**Per-video frontmatter** adds a `complexity:` (or `tier:`) field with values `utility` / `single_feature` / `workflow_chain` / `hero_playbook`. Combined with `style:`, this fully specifies the video shape.

**Build order:** ship Tier 0 → 1 → 2 → 3 (simple → complex). Each lower tier provides production reps, persona-validation, and visual reference points the higher tiers reuse (a Tier 2 video can call back to a Tier 1 video for the single-tool step, keeping its own runtime shorter). **All tiers must be present in MASTER from day 1** even if Tier 3 ships months after Tier 1 — locks the strategic shape rather than letting Tier 3 hero pieces stay perpetually "after we finish the basics."

**Critical rule — applies especially to Tier 1.** Persona specificity does NOT bend for low-tier videos. Tier 1 single-feature videos are the easiest to slip back into "feature demo with a persona prefix" — and that's exactly what the overhaul exists to fix. Test: *"could six different client types watch this video and find it equally useful?"* If yes, the persona/moment is too broad — narrow it down. The whole point of the new MASTER is that "any analyst could use this" is a failure mode, not a virtue.

### What changes

| | Current MASTER (capability map) | Target (use-case map) |
|---|---|---|
| Organizing axis | Parallax tool / command | Specific persona × moment × deliverable |
| Video count | 28 (14 main + 14 niche) | Likely 8–14 use-case videos (estimate; finalize per persona inventory) |
| Per-video framing | "Here's what `/parallax:X` does" | "Here's how [persona] [does action] at [moment], delivering [outcome]" |
| Audience fit | Broad — any user interested in the feature | Specific — a named buyer persona at a named time |
| Niche / feature-flag videos | Standalone demos (CSV, free tier, custom benchmark, etc.) | Mostly dissolve into use-case videos as workflow steps, not standalone targets |

### What survives the rewrite (persona-agnostic infrastructure)

- All tools in `tools/` — `render.py`, `scrub.py`, `zoom.py`, `measure_highlight.py`, `detect_ticks.py`, `extract_frames.py`, `verify_render.py`, `script_hash.py`
- All skills — `parallax-video` (orchestrator), `video-scriptwriting` (craft), `video-production-workflow` (methodology)
- `templates/product-demo/index.html` + `RENDER-GUIDE.md` — parameterized via frontmatter; works for any V<N>
- `references/value-framing-menu.md` — 12-angle vocabulary is persona-agnostic
- `references/production-principles.md` — locked production rules
- `references/colour-kit.md` — brand system
- The vault-stats library structure in MASTER (specific assignments may shift; the structure + canonical-citation pattern stays)

### Phases *(to fill in as scoping happens)*

- [x] **Phase 1 — Persona inventory.** ✅ **LOCKED 2026-05-12.** All 8 working-level personas in, weighted Tier-A/B/C. See Phase 1 section below.
- [x] **Phase 2 — Outcome definition.** ✅ **LOCKED 2026-05-12 at 20 videos.** 4 instructional + 6 Tier-1 single-feature + 7 Tier-2 workflow-chain + 3 Tier-3 hero. Every persona tiering target met; every flagship tool covered on screen; all 3 active moats headlined. See Phase 2 section + Distribution audit below.
- [x] **Phase 3 — New master plan draft.** ✅ **COMPLETE 2026-05-13.** All 20 video specs drafted into `Parallax Video Plan - MASTER.md` under the *NEW SLATE — Phase 3 Draft* section. Each spec carries: style, complexity, duration, primary/secondary personas, in-VO moment, tool chain, deliverable, why-it-matters, title-card headline (hook), title-card eyebrow, YouTube title, Highlights with value-angle assignment, beat sheet, tool chain detail, recording requirements, format invariants. V1 = canary (re-record). 4 instructional (I1-I4) + 16 use_case (V1-V16) covering 6 personas across 4 tiers; every flagship tool covered on screen; 3 of 4 active moats headline at each tier; Polaris closer flagged on V8, V12, V14 (the PM methodology-proof pieces).
- [x] **Phase 4 — Restructure `video-scriptwriting/SKILL.md` around a style axis.** ✅ **DONE 2026-05-12.** Style axis section added; Universal craft separated from use_case-specific and instructional-specific layers; intel_brief style paused-stub in place; style enum propagated to `parallax-video/SKILL.md` dispatch table, `references/value-framing-menu.md`, `references/production-principles.md` Principle #8, `CLAUDE.md` Locked rules; angle-rotation duration anchor generalized from "90-second video" to "per ~90s of content"; Principle #9 (NL prompts + slash-command annotation) added and encoded across `production-principles.md`, both SKILLs, and CLAUDE.md. Full task description preserved below for reference. Currently the skill mixes universal craft + product-demo-use-case-specific craft, with a single one-off carve-out for intel briefs. Split into clean layers:
  - **Universal craft** (applies to every script regardless of style): voice composite, banned words, hard constraints, hallucination check, writing-for-the-ear, source-of-truth grounding, generic Quality Checks #1–#5
  - **Style: `use_case`** — the interpretation-driven rules: "show on screen, interpret in VO," three-question framework, value-framing menu with per-beat rotation, "why processing matters" moat-flavor beat, Quality Checks #6 + #7
  - **Style: `instructional`** — describe the screen as the user follows along (point-and-click narration), value-framing collapses to hook + close only (no per-beat rotation), banned: flowery interpretation / "this means X for you" overlay mid-flow, cadence is literal-sequence
  - **Style: `intel_brief`** — **paused, stub-only.** Captures the design constraints (full-frame avatar, no on-screen product, VO carries 100%, source-document grounding vs frame grounding) as a placeholder so the style enum is forward-compatible. Reactivation = filling in the stub when intel briefs come back into scope.

  Propagate the style enum to consumer files (same set as the "Files to update" section below): `parallax-video/SKILL.md` dispatch table (read `style:`, route to matching scriptwriting section), `references/value-framing-menu.md` (add an applies-when qualifier — rotation rule + per-beat-explicit applies to `use_case` only), `references/production-principles.md` Principle #8 (same qualifier), `CLAUDE.md` "Explicit value-framing per beat" locked rule (same qualifier), script frontmatter `pipeline_type` field (acceptable values: `use_case`, `instructional`, `intel_brief`-paused — consider renaming to `style:` for clarity).

  **Also generalize the angle-rotation duration anchor.** Current wording in `references/value-framing-menu.md`, `references/production-principles.md` Principle #8, and `video-scriptwriting/SKILL.md` says *"in a 90-second video (~6–8 beats), draw from 5–7 different angles."* The 90s figure crept in from V1 ending up at ~90s; it was never a project limit. Change to *"per ~90 seconds of content"* (or scale-aware equivalent) so the rule holds when use-case videos range from 60s utility demos to 3–5min multi-tool workflows (per the worked-example anchor table — the Iran playbook alone is a 4-step workflow that probably needs 2–4 min). Per-video target durations get set explicitly in Phase 3's per-video specs.
- [x] **Phase 5 — Interlock the carry-over decisions.** ✅ **RESOLVED 2026-05-13.** Intel-brief: SHELVED as deferred-future-addition (infrastructure stays, no template build). V1: re-record under new framing (current recording archives; new recording matches U-1's moment-anchored framing; HeyGen canary spend goes against the new V1). See Carry-over section above for full decisions.
- [x] **Phase 6 — Apply value-framing.** ✅ **DONE 2026-05-13.** Value-framing was embedded as a row in each Phase 3 per-video spec; this phase did the audit + per-batch distribution rewrite. Findings: all 3 active moats headline at every tier (#4 spans T1+T2+T3, #5 spans T1+T2+T3, #12 spans T1+T3); #10 Failure isolation correctly absent per locked rule. V5 lightly thickened from 3 → 5 supporting angles. `references/value-framing-menu.md` per-batch distribution table rewritten for the new 20-video set; legacy 28-video distribution preserved below the new table for reference.
- [ ] **Phase 7 — Beat sheets + recording plans.** Per video, lock the beat sheet (use `video-production-workflow` Phase 1) and prep the recording. **Production order: Tier 0 → Tier 1 → Tier 2 → Tier 3.** Each lower tier provides production reps, persona-validation evidence, and visual reference points that higher tiers reuse — a Tier 2 workflow-chain video can call back to a Tier 1 single-feature video for the simple-tool step, keeping its own runtime shorter. Resist the temptation to start with a Tier 3 hero piece before the production pipeline is hardened on lower tiers.
- [x] **Phase 8 — Archive the old master plan.** ✅ **DONE 2026-05-13.** Moved the legacy 28-video per-video specs (Main Showcase V0–V12 + Niche N1–N14) from `Parallax Video Plan - MASTER.md` lines 82–991 to `_archive/MASTER-pre-overhaul-2026-05-11.md`. Archive includes a legacy-to-new mapping table (which old V/N maps to which new V/I, plus drops). Pointer note inserted in MASTER.md where the legacy block used to be. *Sequencing for Client Demos* section in MASTER preserved but flagged as legacy — it references old V<N> names and needs rewriting against the new 20-video slate during Phase 7 production planning.

### Open questions *(to be filled in as scoping surfaces them)*

*(none yet — populate as decisions need making)*

---

## Phase 1 — Persona inventory ✅ LOCKED *(2026-05-12)*

**User decision:** all 8 personas in. Weighted by importance — Tier-A personas get more videos, Tier-B/C get proportionally fewer. No persona excluded.

### Persona weighting

| Weight | Personas | Rationale |
|---|---|---|
| **Tier-A (highest weight, 2-3 videos each)** | RM · PM · Financial analyst | Highest-volume buyer-side audience; primary "end users" the audience note targets |
| **Tier-B (medium weight, 1-2 videos each)** | Compliance officer · Quant analyst · Family-office analyst | Real personas with distinct moments; lower-volume but key for moat-headline videos (#4 Auditability lands hardest for compliance, etc.) |
| **Tier-C (lower weight, 1 video each)** | CIO-as-practitioner · Head of research | Adjacent to PM and analyst respectively; can also consume videos owned by Tier-A; included for breadth |

### Working-level personas

Per the *Audience* note (working-level only, NO executive buyers). Each persona is defined by **role + organisation context + what their week looks like + what they're judged on**.

| Persona | Org context | Day-to-day | Judged on | Vault evidence |
|---|---|---|---|---|
| **Relationship Manager (RM)** | Private bank, wealth advisory, family office | Multiple client meetings/week, portfolio reviews, ad-hoc client questions | Client retention + AUM growth + how defensible their recommendations sound to the client | `04-Marketing/Target Personas.md`, `Sales Playbook.md`, Venise RM workflow test docs |
| **Portfolio Manager (PM)** | Discretionary fund (hedge, mutual, family-office capital) | Allocation decisions, position monitoring, event response, IC presentations | Returns vs benchmark + risk control + how fast they can act on new info | Polaris fund context, Hormuz/Iran playbook anchor, `Investment Philosophy.md` |
| **Financial analyst** | Sell-side coverage, buy-side support, or independent | Producing briefs / DD / forecasts / sector reads on demand for PMs or RMs | Quality of analysis + speed of turnaround + correctness when proven against outcomes | `06-Investor-Letters/` voice, Ivan's playbook anchor (analyst-grade output) |
| **Compliance officer** | Private bank, wealth platform, RIA | Reviewing screens, mandates, exception reports; signing off on what RMs propose to clients | Catching what shouldn't pass + reducing time-to-sign-off on what should | `Auditability and the Unverifiable Frame.md`, Shariah-mandate context |
| **Quant analyst / data person** | Quant fund, factor-investing shop, research-driven advisory | Building screens, running backtests, validating signals | Signal quality + reproducibility + ability to defend methodology in research notes | `02-Methodology/` body, factor-thresholds documentation |
| **Family-office analyst (FOA)** | Single or multi-family office | New-client portfolio assessment, ongoing rebalance + reporting, ad-hoc requests from principals | Quality of bespoke read + speed + breadth across asset classes the family holds | UK EMEA Prospect Map context, Family Office segment in Target Personas |

**Likely excluded** from this batch (executive-buyer-coded — out of scope per Audience note): CIO-as-purchaser, head of strategy, head of operations, head of investment platform, CEO. Their concerns (ROI, vendor-positioning vs Aladdin/Bloomberg, procurement) are a separate series if ever commissioned.

**Possibly in scope, possibly executive — needs your call**:
- **CIO-as-practitioner** (a CIO who's also hands-on with the platform — common in small shops). If yes, treat as a PM-flavoured persona.
- **Head of research / research director** (running an analyst team, may use Parallax themselves before delegating). If yes, treat as analyst-flavoured.

### High-stakes moments (per persona — starting list, expand or trim)

These are the moments where the persona reaches for a tool because they need a specific deliverable *fast*. Each moment is a candidate for a use_case video.

| Persona | Moment | Deliverable they need |
|---|---|---|
| **RM** | Tomorrow morning's client review meeting (recurring quarterly) | Refreshed portfolio read with rebalance recommendations + memo for the client |
| **RM** | Client just texted asking about a specific holding | Quick defensible read on that name in <10 min, before the next meeting starts |
| **RM** | Onboarding a new client, need to assess their existing portfolio | Health check + gap analysis vs the firm's house view |
| **RM** | Annual review pack going to a UHNW client | Comprehensive PDF brief covering performance, risk, peer comparison, outlook |
| **PM** | Macro event breaks (Iran, Hormuz, FOMC surprise) on a weekend | Vulnerability map across the book + actionable opportunity list by COB Monday *(Iran playbook anchor — Tier 3 hero piece)* |
| **PM** | Monthly investment committee — defend each position | Per-name defensible read, IC-quality, every claim cite-able |
| **PM** | Evaluating a new thematic idea | Build a scored universe from the thesis, run health check, decide weight |
| **Financial analyst** | Brief request landed in inbox — need a stock read by end-of-day | Multi-tool brief: company info + factor scores + macro context + analyst spread + AI assessment |
| **Financial analyst** | Forensic flag on an earnings release | Quality trajectory + transcript-language analysis + traffic-light verdict |
| **Financial analyst** | Quant-style screen for a thesis | Factor screen + factor decomposition + custom universe + export |
| **Compliance officer** | New Shariah-mandate portfolio submission to sign off | AAOIFI screen pass/fail + purification calc + exception report |
| **Compliance officer** | Quarterly review of advice given by RMs | Audit-trail spot-check: pick 10 client recommendations, verify each number traces to source |
| **Quant analyst** | Backtesting a thesis from a specific date | Reproducible backtest with start_date parameter; CSV export for further analysis |
| **Quant analyst** | Validating a methodology change to the factor framework | Methodology deep-dive + back-test of the change vs current framework |
| **Family-office analyst** | New-client onboarding (multi-asset portfolio) | Mixed-asset analysis (equities + bonds + commodities + ETFs); factor decomposition through ETF holdings |
| **Family-office analyst** | Quarterly principal update | Lightweight monitoring view (Portfolio Lens) + commentary |

(Some moments are obviously stronger than others. Phase 2 will winnow these to the ~8–14 that become videos.)

### Q1 answer (locked): all 8 personas in, weighted as Tier-A/B/C above.

### Q2 answer (locked): moments selected by pitch-power × frequency × differentiation; see **Phase 2** below for the resolved list.

### Q3 answer (locked): no real customer stories to incorporate — work from the inferred list distilled from vault patterns + general buyer-side knowledge.

### Q4 answer (locked): **moment-anchored framing, persona implicit.** PM and CIO-as-practitioner workflows do not vary widely on the same tool — the click-flow is identical; only the top-of-moment framing shifts slightly (PM: "hold/add/cut?", CIO-practitioner: "fit the mandate?"). One video per moment, single primary persona owner — Option A. **But the script never names the role in the VO.** The *moment* carries the framing: "client just texted...", "before the call", "by EOD", "for the IC memo". The verbs and stakes self-identify the user; the role label is unnecessary noise. Other plausible personas can watch the same video without feeling excluded — nobody got labeled.

**Per-video frontmatter convention:**
- **`primary_persona:`** — structural metadata, NOT in-VO copy. Names who we're writing the script for internally (RM / PM / Analyst / Compliance / Quant / FOA / CIO-practitioner / Head-of-Research). Drives beat selection, value-angle rotation, and tool-chain decisions.
- **`primary_moment:`** — the in-VO situation phrase. The trigger + stakes language that opens the script. Picks a moment whose verbs self-identify the user. Examples: *"Client just texted about a holding. Ten minutes before your next meeting."* / *"Iran war over the weekend. Oil to $82. Monday open in 14 hours."*
- **`secondary_personas:`** (optional) — other personas the video plausibly addresses without re-framing. Listed for coverage tracking; never named in the VO.

**Carve-out — persona-locked language.** Some moments are so role-specific that the natural language IS the role: compliance moments ("audit memo deadline", "Shariah sign-off"), quant moments ("backtest from this date", "factor decomposition"). For these, the moment phrase may legitimately read as role-coded — that's not a violation of the rule, it's the moment doing its job. The rule is "don't *typecast* with role labels"; it's not "scrub all professional vocabulary."

**Tier scaling.** The moment-anchored rule applies across all use_case tiers (1 / 2 / 3). At Tier 1 it's framing — picks the most plausible primary user, situation gives the script a real moment to write to. At Tier 2/3 it's structural — the workflow only makes sense for the named persona, so the role becomes obvious from the situation itself without needing a label. **Tier 0 instructional** has no persona anchoring at all (point-and-click, audience-general).

**Where this gets encoded:** the moment-anchored rule needs adding to `.claude/skills/video-scriptwriting/SKILL.md` under the `use_case` style section (a new sub-rule alongside the three-question framework). Deferred to the post-overhaul SKILL.md update sweep — flagged here so it doesn't get lost.

---

## Phase 2 — Outcome definition + moment selection (DRAFT, awaiting user review)

*Drafted 2026-05-12 by me, off Phase 1's locked persona inventory. **Pending user review** — adjust the moment selection and persona ownership before Phase 3 starts drafting MASTER specs.*

### How I graded moments

Each candidate moment was scored on three axes:

- **Pitch power** — does watching this make a buyer say "I need that"?
- **Frequency** — does the persona hit this moment often (daily / weekly / quarterly / annually)?
- **Differentiation** — does Parallax produce a meaningfully better deliverable than the casual alternative (Bloomberg, Claude, manual)?

Moments scoring high on all three become videos. Moments scoring low on any one were either cut or rolled into a multi-tool higher-tier video.

### Framing convention

Each use_case video (Tier 1 / 2 / 3) carries two parallel fields per Phase 1 Q4 above:

- **Primary persona (structural)** — who we're writing for internally. Drives beat selection, value-angle rotation, tool-chain choice. **Not named in the VO.**
- **In-VO moment phrase** — the trigger + stakes language the script actually opens on. Picks a moment whose verbs self-identify the user (*"client just texted..."*, *"before the IC..."*, *"Monday open in 14 hours..."*) so the role label becomes unnecessary.

Tier 0 instructional videos have neither — they're audience-general point-and-click.

### Selected moments (15 candidate videos: 4 instructional + 11 use_case)

#### Tier 0 — Instructional (3-4 videos)

Style: `instructional`. Audience-general. Point-and-click.

| # | Title (working) | Complexity | Why included |
|---|---|---|---|
| I-1 | **Install Parallax in any AI client** (Claude Desktop, Claude Code, Codex, Qwen) | `utility` | Foundational. Any buyer eval starts here. (Was V0.) |
| I-2 | **First brief in 60 seconds** — quickstart from zero to a Parallax output | `utility` | Validates "this thing works" for new users. Cross-client install pairs with this. |
| I-3 | **Free tier walkthrough** — what you can do with zero credits | `utility` | Removes the "pay before seeing value" objection. (Was N12.) |
| I-4 | **Exports & integrations** — PDF report, CSV, Excel bridges | `utility` | One video covers N7 (CSV) + N11 (PDF) — both are bridge-to-existing-tools demos. |

#### Tier 1 — Single-feature use cases (6 videos)

Style: `use_case`. Persona × moment × single-tool × deliverable. Length 60-120s.

| # | Persona (structural) | In-VO moment phrase | Tool | Deliverable |
|---|---|---|---|---|
| U-1 | MFO / independent RIA / wealth advisor | *"Client just texted about a holding. Ten minutes before your next meeting."* | `/parallax:stock` (Stock Report) | Quick defensible read on the name |
| U-2 | PM | *"Name on the candidate list. Score check before the trade."* | `/parallax:stock` (score + trajectory) | Score check + 52-week trajectory + go/no-go read |
| U-3 | Financial analyst | *"Peer snapshot for the brief. Before it goes out."* | `/parallax:stock` (peer view) | Peer-comparison table for the brief |
| U-4 | Compliance officer (trade/portfolio) | *"Shariah-mandate name. Sign-off before close."* ⓟ | `/parallax:screen` (Shariah Screen) | AAOIFI pass/fail + purification ratio |
| U-5 | Family-office analyst | *"Half the equity portion is held through ETFs. What are they actually long underneath?"* | `/parallax:portfolio` (ETF Analysis / look-through) | Compound concentration revealed; effective per-name exposure within the equity slice |
| U-6 | PM | *"Korea election Sunday. Country-level read by Monday open."* | `/parallax:macro` (Macro Intelligence) | Single-country macro read — regime, sectors-in-favor, equity-opportunity shortlist |

ⓟ = persona-locked language (compliance/quant moments where the role IS the natural vocabulary; carve-out per Phase 1 Q4).

**Persona-scoping notes post-research (2026-05-12):**
- **U-1 RM** anchored to MFO / independent RIA / wealth advisor (not large-bank private banker). Large-bank RMs consume briefs from internal advisory desks; the "self-serve before a meeting" framing is MFO/RIA-shaped. Venise's RM Workflow Test (`parallax-obsidian/04-Marketing/2026-04-19 Venise RM Workflow Test.md`) is the canonical persona model.
- **U-4 Compliance** anchored to trade/portfolio compliance (IPS drift, restricted-list, audit-trail). NOT regulatory/AML — different tool stack (Fenergo / NICE Actimize); outside Parallax's surface.
- **U-5 FOA** narrowed to the *equity slice only*. Parallax cannot analyze private / illiquid holdings (confirmed by user 2026-05-12). The bigger FOA pain (cross-asset incl illiquids — Addepar's surface) is out of reach; this video honestly addresses only the slice Parallax dramatically improves.
- **U-6 PM macro** — single-country event read (Korea, Japan, etc.). Closes `/parallax:macro`'s standalone gap. Distinct from H-1 (Iran playbook) which uses `/macro` as one of four tools in a multi-tool hero chain; U-6 is the standalone moment that justifies `/macro` on its own.

#### Tier 2 — Workflow chain (7 videos)

Style: `use_case`. Persona × moment × 2-4 chained tools × composite deliverable. Length 2-3 min.

| # | Persona (structural) | In-VO moment phrase | Tools | Deliverable |
|---|---|---|---|---|
| W-1 | MFO / independent RIA / wealth advisor | *"Quarterly review with your biggest client tomorrow. Full prep by tonight."* | `/parallax:portfolio` → `/parallax:rebalance` → PDF export | Refreshed read + rebalance memo + client-ready PDF |
| W-2 | PM | *"Investment committee tomorrow. Every position needs a defense."* | `/parallax:portfolio` + per-name `/parallax:stock` + audit-trail navigation | IC-ready brief with each claim cite-able |
| W-3 | Financial analyst | *"Brief request just landed. End-of-day deadline."* | `/parallax:deep-dive` (11 parallel calls) | Full brief with AI assessment synthesis |
| W-4 | Quant analyst | *"Reproduce the regime-window analysis without look-ahead bias. Spreadsheet-ready out."* ⓟ | `start_date` parameter + `/parallax:stock` + CSV export | Reproducible point-in-time backtest in spreadsheet-ready format |
| W-5 | Compliance officer (trade/portfolio) | *"Quarterly review of advice. Ten client recommendations on the table. Every number has to trace."* ⓟ | Audit-trail navigation + per-name `/parallax:stock` evidence drilldown + **`explain_methodology` drawer** + exception export | Compliance-ready audit packet: each recommendation's evidence chain (score → factor → input → source) documented and exception-flagged |
| W-6 | PM | *"Have a thesis. Need a basket. Score-defensible, methodology-traceable."* | `/parallax:universe` (Builder) → `/parallax:portfolio` → per-name `/parallax:stock` health checks + **`check_portfolio_redundancy`** | Scored basket aligned to the thesis, redundancy-checked, ready to size |
| W-7 | Family-office analyst | *"New principal. Multi-ETF book just landed. One-page equity exposure read by EOD."* | `/parallax:portfolio` (with ETF look-through) + **deeper `/parallax:etf`** (holdings + factor profile on the largest ETFs) + factor decomposition + macro context | One-page equity exposure read: factor profile, regional/sector concentration, ETF-by-ETF look-through, macro framing |

ⓟ = persona-locked language (compliance/quant moments where the role IS the natural vocabulary; carve-out per Phase 1 Q4).

**Persona-scoping notes:**
- **W-1 RM** same MFO / independent RIA / wealth-advisor framing as U-1 (Venise's day-in-life is the canonical model).
- **W-4 Quant** reframed from "backtest from a specific date" to *"reproduce a regime-window analysis without look-ahead bias"* per web research — quants think in regime windows + point-in-time discipline, not single anchor dates. Single-window backtest is the simpler visual; the discipline framing is what the moment actually means.
- **W-5 Compliance audit** — the second compliance video (alongside U-4 Shariah), lifting compliance to its Tier-B 2-video target. Headlines moat #4 Auditability; vault evidence is the strongest in the catalogue (`Auditability and the Unverifiable Frame.md`). The **`explain_methodology` drawer beat** is load-bearing — it's the visual proof that every score has a documented evidence chain, the exact thing compliance needs in a regulated workflow.
- **W-6 PM thesis-build** — covers `/parallax:universe` (Builder), the natural-language-to-portfolio capability. The **`check_portfolio_redundancy` beat** appears after the basket is built, surfacing hidden correlated bets the PM didn't realize they had — a unique-to-Parallax differentiator with no other video coverage.
- **W-7 FOA onboarding** — extends U-5's equity-slice framing into a full multi-step workflow. The **deeper `/parallax:etf` beat** (etf_profile, etf_holdings, alternatives) gives ETF Analysis a second appearance beyond U-5's look-through sub-step. Bounded by no-illiquids: this video addresses only the equity slice the family holds (often heavy in ETFs as proxy exposures).
- **W-5 CIO-practitioner × post-IC validation was DROPPED in the research-validation pass** (see *Moments cut* below). The W-5 slot is now Compliance audit.

#### Tier 3 — Hero playbook (3 videos)

Style: `use_case`. Full multi-tool workflow. Persona × event-moment × publishable synthesis. Length 3-5 min.

| # | Persona (structural) | In-VO moment phrase | Tools | Deliverable |
|---|---|---|---|---|
| H-1 | PM | *"Iran war over the weekend. Oil to $82. Monday open in fourteen hours. What's the contrarian read?"* | `/parallax:scenario` + `/parallax:macro` + factor screen + thesis synthesis | **Anchor: Ivan's Iran/Korean Banks Playbook** (`references/use-case-examples/iran-playbook/`) — full reproducible workflow |
| H-2 | Financial analyst | *"New name handed to you for coverage. IC-grade initiation report, due Friday."* | `/parallax:deep-dive` + `/parallax:scenario` + `/parallax:investor` + PDF export | Full-DD initiation report, IC-grade |
| H-3 | Financial analyst | *"Stock fell twelve percent on earnings. Was it the print, or the guide?"* | `/parallax:screen` (forensic earnings mode) + transcript-language analysis + quality trajectory over 8 quarters + AI assessment | Forensic earnings memo: traffic-light verdict + thesis intact-or-broken + quality trajectory chart |

**Persona-scoping notes:**
- **H-3 Forensic earnings** — anchored on the analyst's event moment (stock moves on earnings, need to forensically assess whether the print broke the thesis). Vault has supporting M2 video concept (*"When the Analyst Was Wrong"*) framing this as analyst-thesis-validation workflow. Covers `/parallax:screen` forensic mode — the unique-to-Parallax forensic earnings capability that has no other video coverage in the slate.

### Distribution audit — Phase 2 LOCKED at 20 videos (2026-05-12)

**Video count: 20 total** (4 instructional + 16 use_case). All 5 expansion candidates from the persona × tool coverage audit were added after passing the persona-and-moment authenticity test; one candidate (U-7 Analyst ETF deep-dive) was cut as tool-driven dressing. Three beat-level tool-coverage additions ensure every flagship tool appears at least once in the slate.

**Per-persona coverage:**

| Persona | Primary videos | Notes |
|---|---|---|
| RM (Tier-A; framed as MFO/RIA/wealth advisor) | 2 (U-1, W-1) | Anchor to Venise's RM Workflow Test framing. Saturated — 2 natural moments; more would feel forced. |
| PM (Tier-A) | 4 (U-2, U-6, W-2, W-6, H-1) — 5 | Heaviest weight; aligns with Tier-A weighting and tool diversity (stock, macro, IC, thesis-build, event) |
| Financial analyst (Tier-A) | 4 (U-3, W-3, H-2, H-3) | Heavy weight; covers peer-snapshot, EOD brief, initiation, forensic earnings |
| Compliance officer (Tier-B; trade/portfolio sub-role) | 2 (U-4, W-5) | Tier-B 2-video target met. W-5 headlines moat #4 Auditability — strongest single mapping in catalogue. |
| Quant analyst (Tier-B) | 1 (W-4) | Minimum coverage; vault explicitly deprioritizes pure quants ("Man AHL, Winton build their own tools"). Tier-B floor of 1 is correct. |
| Family-office analyst (Tier-B) | 2 (U-5, W-7) | Tier-B 2-video target met. Both bounded by no-illiquids — equity slice only. |
| CIO-as-practitioner (Tier-C) | 0 primary, secondary on W-2 + H-1 | No tactical workflow distinct from PM at small shops |
| Head of research (Tier-C) | 0 primary, secondary on W-3 + H-2 + H-3 | Per plugin's own self-assessment, Parallax is "the quantitative spine, not the variant view" — does not headline head-of-research's publication moments |
| **Total persona-anchored** | **16 use_case videos** | (6 Tier-1 + 7 Tier-2 + 3 Tier-3) |
| + instructional (audience-general) | 4 | |
| **= total** | **20** | |

PM count = 5 (U-2, U-6, W-2, W-6, H-1).

### Tool coverage matrix — every flagship tool has at least one on-screen appearance

| Tool / feature | Primary anchor | Sub-step appearances |
|---|---|---|
| `/parallax:stock` (Stock Report) | U-1, U-2, U-3 | W-2, W-4, W-5, W-6 |
| `/parallax:deep-dive` (Deep Dive) | W-3 | H-2 |
| `/parallax:portfolio` (Analyzer) | U-5, W-7 | W-1, W-2, W-6 |
| `/parallax:rebalance` (Analyzer Rebalance) | — | W-1 |
| `/parallax:scenario` (Impact Analysis) | — | H-1, H-2 |
| `/parallax:macro` (Macro Intelligence) | U-6 | H-1, W-7 |
| `/parallax:screen` (Shariah Screen) | U-4 | — |
| `/parallax:screen` (Forensic Quality) | H-3 | — |
| `/parallax:universe` (Builder) | W-6 | — |
| `/parallax:investor` (Investor Profile) | — | H-2 |
| `/parallax:etf` (ETF Analysis) | — | U-5 (sub-step), W-7 (deeper beat) |
| `explain_methodology` (Methodology drawer) | — | **W-5 (new beat)** |
| `check_portfolio_redundancy` (Redundancy check) | — | **W-6 (new beat)** |
| `start_date` (point-in-time backtest) | W-4 | — |
| Factor screen (`search_stocks`) | — | H-1 |
| PDF / CSV exports | I-4 | W-1, W-4, H-2 |

Tools that intentionally have no Tier-1 standalone (per the persona-and-moment principle — no natural single-moment persona use): `/parallax:rebalance`, `/parallax:scenario`, `/parallax:investor`. These earn their screen time in workflow chains because that's how the persona actually reaches for them in real life.

Peripheral dashboard features intentionally skipped: Watchlists, Markets dashboard, News curation, Trending stocks. Not flagship — not worth bending the slate.

**Moments deliberately cut (original draft pass):**

- *Annual UHNW review pack* — folded into W-1 (RM quarterly client review) since the workflow is identical, just with a bigger time window.
- *Watchlist monitoring (PM)* — lower stakes vs other PM moments.
- *Quarterly principal update (FOA)* — lower pitch power.

**Moments cut post-research (2026-05-12):**

- **Original U-6 Head of research × `/parallax:investor` (validating juniors)** — DROPPED. Two reasons: (1) Vault evidence for head-of-research as a primary persona is thin (confidence 4/10 per vault scan); (2) The Parallax plugin's own honest self-assessment (cited 2026-05-12) explicitly says *"It's a factor engine, not a fundamental-DCF or thesis-tree tool. The qualitative 'why this name, why now' narrative is still on the analyst — Parallax gives you the defensible quantitative spine, not the variant view"* and *"'Recommendations' map mechanically from score bands... For a head-of-research publication you'll want to treat that as input, not output."* Pitching Parallax as the head-of-research's primary tool sets buyer expectations Parallax can't meet. *(Note: the U-6 slot was subsequently reassigned to PM × `/parallax:macro` single-country event read.)*
- **Original W-5 CIO-as-practitioner × post-IC validation** — DROPPED. Vault evidence positions CIO-as-practitioner as a *buyer* persona (Synthesis Layer / B-CIO framing) but not a distinct tactical workflow. Web research confirms tactical overlap with PM at small shops. No distinct moment to anchor a video on. *(Note: the W-5 slot was subsequently reassigned to Compliance × audit-trail workflow.)*
- **U-7 Analyst × ETF deep-dive standalone (expansion candidate)** — CUT as tool-driven dressing. *"Client asked about HACK, what's in it"* is more naturally an RM-client-question or FOA-context moment than an analyst's primary moment. Analysts cover sectors and names, not typically ETFs as standalone work. Adding U-7 would have been unconsciously reaching for "a video for `/etf`" rather than asking "is there a persona × moment where `/etf` standalone is the right deliverable?" The principle says no — `/etf` is correctly served by U-5 sub-step and W-7's deeper-beat addition.

### On-screen vocabulary lock — natural-language prompts, slash commands highlighted (2026-05-12)

**The rule.** Videos demonstrate Parallax via **natural-language prompts** typed by the user — *"Run a deep dive on NVDA using Parallax"*, not `/parallax:deep-dive NVDA`. The avatar or overlay highlights which slash command or tool was triggered under the hood. Viewer sees what they would type in their own client (universal across Claude Code, Claude Desktop, Codex, Qwen — only Claude Code supports the slash-command syntax); the production layer annotates which tool the platform invokes.

**Why the rule exists.**

- **Portability.** Only Claude Code consumes the full plugin with `/parallax:*` slash commands. The other three supported clients (Claude Desktop, Codex CLI, Qwen CLI) get the raw MCP tools only — no slash commands. NL prompts work across all four. Per `V0 Install Research — 4 Clients.md:46, 214`.
- **Buyer-facing tone.** Slash commands read as developer-tool; NL prompts read as product. Buyer audience (RM / PM / analyst) is not developer-coded.
- **Honest demo.** The screen recording inevitably shows the chat-style interaction; the VO + LT should match that visual register, not impose a CLI vocabulary on top.

**Where the rule already lives in the project (scattered evidence, not formally codified):**

- `scripts/V1 voiceover script.md:38` — LT headline *"Eight parallel skill calls. One natural-language prompt."*
- `scripts/V1 voiceover script.md:134` — VO body *"Plain English in. Eight parallel calls out."*
- `scripts/V1 voiceover script (legacy old pipeline).md:19, 87` — frontmatter metadata + stage direction
- `learnings/demo-video-format.md:58` — research note (*"Hook needs to feel real — plain-English prompt, typed by a human"*)
- `V0 Install Research — 4 Clients.md:46, 214` — installation/portability rationale

**Where the rule is NOT yet codified (should be):**

- `references/production-principles.md` — needs a new locked principle (proposed: **Principle #9 — Natural-language prompts in the demo; slash commands annotated, never typed**).
- `.claude/skills/video-scriptwriting/SKILL.md` — under the `use_case` style section, codify VO + LT vocabulary convention (use natural-language prompt verbatim from the recording; never read the slash command aloud; LT eyebrow/headline can name the *product module* (Stock Report, Screener, Analyzer, ETF Analysis, Impact Analysis, Macro Intelligence, Shariah Screen) for buyer-facing context).
- `.claude/skills/parallax-video/SKILL.md` — orchestrator dispatch table should reference this convention when routing `"write V<N>"` requests.

**Codification deferred** to the post-overhaul SKILL.md / production-principles sweep — see *Files to update* section below.

### Phase 2 LOCKED (2026-05-12) — ready to start Phase 3

All Phase 2 questions resolved:

1. **~~Compliance Tier-2 audit-trail video?~~** → **Added as W-5.** Headlines moat #4 Auditability; lifts compliance to Tier-B 2-video target.
2. **~~Expansion candidates?~~** → **Resolved.** 5 of 6 added after passing the persona-and-moment authenticity test (U-6 PM macro, W-5 Compliance audit, W-6 PM thesis-build, W-7 FOA onboarding, H-3 Analyst forensic). U-7 (Analyst ETF) cut as tool-driven dressing. Three beat-level tool-coverage additions ensure every flagship tool appears at least once (W-5 explain_methodology, W-6 check_portfolio_redundancy, W-7 deeper `/parallax:etf`).
3. **Names** — the working titles (I-1, U-1, etc.) remain placeholders. Phase 3 assigns real names.
4. **Tools-to-video matching** — primary tools named per video; Phase 3 locks the full command chain per video with any tooling gaps surfaced.

**Net slate locked at 20 videos** (4 instructional + 6 Tier-1 + 7 Tier-2 + 3 Tier-3). Every persona's tiering target met; every flagship tool has at least one on-screen appearance; all 3 active moats (#4 Auditability, #5 Determinism, #12 Unverifiable frame) properly headlined.

**Phase 3 starts now — write the new MASTER per-video specs against this locked slate.**

---

## Files updated during the overhaul *(all swept 2026-05-12 → 2026-05-14)*

✅ **Propagation sweep complete.** All planning-phase documentation, skill files, references, and the template now reflect the persona-and-moment 20-video slate.

| File | What changed |
|---|---|
| `CLAUDE.md` | Preamble + filesystem tree caption + status table rewritten for new slate. Dispatch table now handles `V<N>` (use_case) + `I<N>` (instructional) prefixes. Locked rules section collapsed into one-paragraph pointers citing `production-principles.md` Principles #1–#13. |
| `Parallax Video Plan - MASTER.md` | Legacy 28-video specs (V0–V12 + N1–N14) archived to `_archive/MASTER-pre-overhaul-2026-05-11.md`. New 20-video Phase 3 draft appended at the bottom with full per-video specs (frontmatter + Highlights + value angles + beat sheets + title-card values + YouTube titles + recording requirements). |
| `references/production-principles.md` | Added Principle #9 (NL prompts). Promoted CLAUDE.md orphan rules into Principles #10–#13. Added update-discipline note. Cross-ref table covers #1–#13. |
| `references/value-framing-menu.md` | Per-batch distribution table rewritten for the 20-video slate. Legacy 28-video distribution preserved below for historical reference. |
| `references/product-demo-pipeline.md` | Top description updated for 20-video slate; intel-brief marked shelved. |
| `.claude/skills/parallax-video/SKILL.md` | Description + architecture table updated for 20-video slate (single product_demo stream; intel_brief shelved). Frontmatter contract expanded with `style:`, `complexity:`, `primary_persona:`, `primary_moment:`, `secondary_personas:`, `youtube_title:`. Dispatch table cites Principles #8 + #9 + #10. |
| `.claude/skills/video-scriptwriting/SKILL.md` | Style axis added (use_case / instructional / intel_brief-paused). New operating rules under use_case: show-on-screen / interpret-in-VO; moment-anchored framing; NL prompts; LT selection rule + cap + self-check (Quality Check #8). Memo-not-marketing rule (old Quality Check #5) retired. |
| `templates/product-demo/index.html` | Avatar default → corner pose (no bookend, no settle). LT hierarchy → stat values 38px / labels 14px stacked. Chicago Global logo inlined as base64 (transparency-processed) with CSS filter for white rendering, placed top-center of title card + outro. |
| `templates/product-demo/RENDER-GUIDE.md` | Avatar timing tables + checklist updated. LT hierarchy + selection rule documented. CG logo positioning + filter approach documented. |
| `templates/product-demo/DESIGN.md` | Avatar PiP description updated. CG logo block added. |
| `templates/product-demo/README.md` | Avatar settle-ease bullet retired. |
| `tools/verify_render.py` | `AVATAR_BBOX_TRANSITION` / `AVATAR_BBOX_BOOKEND` constants retired. Simplified to `AVATAR_BBOX_CORNER`. Sample timestamp labels updated. |
| `scripts/all-28-voiceover-scripts-DRAFT.md` | Archived to `_archive/` — legacy draft from old slate. |

### Phase 7 production items — pending, archive happens during V1 re-record

These are the only items still untouched, by design — they archive when V1 production starts (per Phase 5 carry-over decision):

- **`scripts/V1 voiceover script.md`** — pre-overhaul V1 script. Archive to `scripts/_archive/V1-original-2026-04-29.md` when V1 re-record begins.
- **`screen recordings/V1/1vid*.mp4`** — pre-overhaul V1 recording (NVIDIA-anchored, feature-led framing). Archive to `screen recordings/V1/_archive/v1-original-2026-04-*.mp4` when V1 re-record begins.
- **`outputs/V1/preview.mp4`** — fine as-is; will get overwritten on first V1 re-record render. Old version stays in `preview-prev.mp4` for comparison.
- **`outputs/V1/final.mp4`** — doesn't exist yet (HeyGen wallet top-up required first).
