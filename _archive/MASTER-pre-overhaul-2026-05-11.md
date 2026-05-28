# Parallax Video Plan — Legacy 28-Video Specs (archived 2026-05-13)

**Status:** ARCHIVED. Superseded by the 20-video persona-and-moment-driven plan in `Parallax Video Plan - MASTER.md` (the *NEW SLATE — Phase 3 Draft* section).

**Why this exists:** the 28-video capability-organized plan (Main Showcase V0-V12 + Niche N1-N14) was the master plan from 2026-04 through the start of the 2026-05-11 overhaul. During the overhaul (Phases 1-8 in `overhaul.md`), it was replaced by a 20-video set organized around `primary_persona × primary_moment × deliverable` rather than per-Parallax-command.

**Why preserved (not deleted):**

- Content reference — many of the per-video Highlights have stat citations and framing lines that survive into the new slate (e.g., V1's ICIR 4.10 / 62K listings / 48 markets is preserved in the new V1 spec; V8 "Build a Portfolio from a Thesis" content informs the new V12; V11 Shariah survives largely intact into the new V4; V12 Forensic Earnings into the new V16; etc.)
- "Why processing matters" beats — the moat-flavored explanations developed for V1, V2, V3, V6, V7, V8, V10, V11, V12, N5, N14 are reusable craft anchors when Phase 7 scriptwriting drafts the new VOs
- Sequencing for Client Demos (was in the main MASTER, line 993+) — referenced this set; preserved here for legacy reference

**Mapping legacy → new:**

| Legacy | New | Notes |
|---|---|---|
| V0 (Install Parallax MCP) | **I1** | Install instructional |
| V0.5 (One Plugin, Every Client) | folded into **I1** / **I2** | Quad-split portability proof + first-brief sanity check |
| V1 (Quick Stock Research Brief) | **V1** | The canary — V<N> identity preserved; re-recorded under moment-anchored framing |
| V2 (Deep Dive — Full DD) | **V9** (Tier 2 Analyst EOD) + **V15** (Tier 3 Initiation Report) | Deep-dive content splits across two new videos |
| V3 (Portfolio Health Check) | folded into **V7** (RM Quarterly Review) | Health flags are a sub-step of the quarterly workflow |
| V4 (Portfolio Rebalancing) | folded into **V7** (RM Quarterly Review) | Rebalance is now a workflow step, not a Tier-1 standalone (per persona-and-moment principle) |
| V5 (Watchlist Monitoring) | DROPPED | Lower-stakes moment per Phase 2 audit |
| V6 (Scenario Analysis) | folded into **V14** (PM Iran Playbook hero) | Scenario is now a workflow step in the hero, not a Tier-1 standalone |
| V7 (AI Investor Profiles) | folded into **V15** (Analyst Initiation hero) | Investor profiles is now a workflow step in the hero |
| V8 (Build Portfolio from Thesis) | **V12** (PM Thesis-to-Portfolio Build) | Direct port — same workflow, persona-anchored framing |
| V9 (ETF Research & Comparison) | folded into **V5** (FOA ETF Look-Through) + **V13** (FOA Onboarding) | Look-through becomes the FOA-anchored Tier-1 moment |
| V10 (Macro Outlook & Country) | **V6** (PM Macro Single-Country Event) | Direct port — event-driven moment-anchored |
| V11 (Shariah Compliance Screening) | **V4** (Compliance Shariah Screen) | Direct port — strongest single mapping in the catalogue |
| V12 (Forensic Earnings Quality) | **V16** (Analyst Forensic Earnings hero) | Promoted to Tier-3 hero piece |
| N1 (Cash as a Portfolio Holding) | DROPPED | Lower-stakes |
| N2 (Mixed Stocks + ETFs) | folded into **V5** | ETF decomposition is V5's core capability |
| N3 (Custom Benchmark) | DROPPED | Lower-stakes |
| N4 (Smart ETF — Bonds & Commodities) | DROPPED | Outside Parallax's confirmed surface (no bonds, no commodities — confirmed 2026-05-13) |
| N5 (Score Trajectory & Inflection) | folded into **V2** (PM Pre-Trade Score Check) | Trajectory is a sub-beat of pre-trade checking |
| N6 (Soros Mode — Trade Ideas) | folded into **V15** | Investor-profile basket is a hero sub-step |
| N7 (Export to CSV) | folded into **I4** (Exports & Integrations) | Consolidated with N11 (PDF) into one bridge-to-existing-tools video |
| N8 (Portfolio Lens) | DROPPED | Surface-level UX detail, not a use_case moment |
| N9 (Backtest from Date) | **V10** (Quant Regime Backtest) | Promoted to Tier-2 with persona-and-regime-window framing |
| N10 (Methodology Deep-Dive) | folded into **I3** (Free Tier Walkthrough) + **V8/V11 beats** (methodology drawer) | Free-tool surface in I3; in-workflow methodology drawer in compliance + IC videos |
| N11 (PDF Research Report) | folded into **I4** (Exports & Integrations) | Consolidated with N7 |
| N12 (Free Tier — Zero Tokens) | **I3** | Direct port |
| N13 (Market Regime & Telemetry) | DROPPED | Lower priority — telemetry surface is operationally niche |
| N14 (Finding Alpha Where Wall Street Isn't Looking) | DROPPED | Strong content but uncovered-alpha story didn't survive the persona-and-moment scoping; revisit as a future intel-brief if reactivated |

---

# Legacy content begins here

## Main Showcase Videos (14)

Ordered roughly simplest to most complex. V0 and V0.5 are the new vault-informed additions placed at the front — setup plus platform positioning before any feature work. Suggested total runtime: 50–75 minutes.

> Each video's Highlights includes a `**Primary value angles**` bullet citing `#X` numbers from the value-framing menu at **`references/value-framing-menu.md`** — see that file for definitions, value-line shapes, and vault sources.

---

### Video 0: Installing the Parallax MCP — Five Minutes, Any Client

| Field | Details |
|---|---|
| **Duration** | 4–5 minutes |
| **Audience** | Any first-time user. Prerequisite for every other video. |
| **Plugin Command** | N/A — installation walkthrough |
| **Description** | Show installation across Claude Desktop, Claude Code, Codex CLI, and Qwen CLI. Frame MCP as an open protocol — Parallax doesn't lock you into one client. |
| **Demo Script** | Screen walkthrough: open each client, add the Parallax MCP entry, authenticate, run one sanity command (`/parallax:stock AAPL`). |
| **Why It Matters** | Kills the #1 objection: "is this going to be a pain to set up?" Five minutes, no IT ticket, no terminal license. Direct contrast with Bloomberg terminal provisioning. |

**Highlights** — distinct points this video owns

- Cross-client install in five minutes (Claude Desktop, Claude Code, Codex CLI, Qwen CLI)
- MCP as an open protocol — same plugin, every AI client
- Direct contrast with Bloomberg terminal provisioning ("No terminal. No IT ticket. No 12-month rollout.")
- Sanity-check command lands the same brief in every client
- **Primary value angles** — *No moat headline (install demo).* *Supporting:* #8 Workflow-native · #1 Speed.

**Beat sheet**

- Open: "Before we show you what Parallax does, let's get it running." Title card: *Install. Five minutes. Any client.*
- For each client (Claude Desktop → Claude Code → Codex CLI → Qwen CLI): show the Connectors/config screen, paste MCP URL, authenticate, run `/parallax:stock AAPL` as sanity check.
- Split-screen payoff: all clients showing the same AAPL brief.
- Callout (pending confirmation): pricing + speed-to-deploy vs Bloomberg ("No terminal. No IT ticket. No 12-month rollout.").
- Close: "Now let's look at what you can actually do with it."

**Must-verify before recording:** Codex support; any pricing displayed; exact install steps per client (plan currently written from first principles, not a vault install doc).

---

### Video 0.5: One Plugin, Every Client

| Field | Details |
|---|---|
| **Duration** | 3–4 minutes |
| **Audience** | Procurement, IT, CIO — anyone evaluating "what if we switch AI vendors later?" |
| **Plugin Command** | `/parallax:deep-dive NVDA` across all clients |
| **Description** | Quad split. Same prompt in Claude Desktop, Claude Code, Codex CLI, Qwen. Identical output. |
| **Why It Matters** | Bloomberg locks you into Bloomberg. Aladdin locks you into Aladdin. Parallax is MCP-native — it travels with whatever AI stack the firm picks this year or next. Removes vendor lock-in objection up front; ideal opener for any client demo sequence. |

**Highlights** — distinct points this video owns

- Quad-split same prompt, identical output across four clients (the visual proof-shot)
- MCP-native = vendor-lock-in killer (vs. Bloomberg, Aladdin, vendor-bundled platforms)
- Coverage breadth: 62,000+ listings across 48 markets (1.4M+ identifiers) — universal MCP-native coverage as a vendor-portability proof point
- Universal demo opener — kills the "what if we switch AI vendors later?" procurement objection up front
- **Primary value angles** — *No moat headline (install demo).* *Supporting:* #8 Workflow-native · #2 Coverage.

**Beat sheet**

- Open: "Most institutional tools pick a platform and trap you there. Parallax doesn't."
- Callout: *MCP = open protocol.* Anthropic wrote it, everyone adopted it.
- Type identical prompt in all four quadrants; press enter; parallel calls fire in each.
- Payoff shot: side-by-side identical factor tables, peer snapshots, AI assessments.
- Vault callout (use verified numbers): 36 of 37 markets (or updated live-universe number once confirmed).
- Close: "Pick your AI. Parallax follows."

**Production note:** Quad-split requires four separate recordings synced in post. Budget 1.5–2× the usual edit time.

---

### Video 1: Quick Stock Research Brief

| Field | Details |
|---|---|
| **Duration** | 3–4 minutes |
| **Audience** | Any investor, analyst, or PM wanting a fast overview |
| **Plugin Command** | `/parallax:stock [ticker]` |
| **Description** | One natural-language question fires 8+ parallel API calls; complete brief in under 60 seconds. |
| **Demo Script** | *"I keep hearing about NVIDIA — can you give me a quick rundown on whether it's actually worth the hype right now?"* |
| **Why It Matters** | What used to take 20 minutes of Bloomberg + broker reports happens in one sentence. |

**Highlights** — distinct points this video owns

- Eight-plus parallel API calls fired from one natural-language question
- Complete brief delivered in under sixty seconds
- ICIR 4.10 / Sharpe 2.34 / +5.8%/yr selection return over 13 years (this video's lead vault stat)
- Live universe: 62,000+ listings across 48 markets (1.4M+ identifiers)
- Score-to-recommendation map: 8.5–10 STRONG BUY · 6.5–8.4 BUY · 3.5–6.4 HOLD · 1.5–3.4 SELL · 0.0–1.4 STRONG SELL
- "Twenty minutes of Bloomberg + broker reports → one sentence" — this video's framing line
- **Primary value angles** — *Moat headline:* **#12 Unverifiable frame** (the natural "vs eight Claude chats" comparison in the parallel-calls beat). *Supporting:* #1 Speed · #3 Defensibility · #7 Decision-readiness.
- **"Why processing matters" beat** *(consistency flavor)*: eight Parallax calls reconcile because they all reference the same factor framework. Eight broker reports each run their own methodology — they don't. The hard part isn't the fan-out; it's the framework consistency that lets the brief actually integrate rather than just stitch.

**Beat sheet**

- Open: one NL question → eight parallel API calls → complete brief.
- Walk the viewer through the actual output in the order it renders (to be confirmed on recording): company overview → factor scores (with 52-week trend) → financial health traffic light → macro context → analyst view → bottom line.
- Vault callout: *"ICIR 4.10 globally. +5.8%/yr selection return, 13 years, 62,000+ listings across 48 markets."* (Source: stock-selection-alpha WP + Key Differentiators.)
- Close: "One question. Eight parallel calls. ~60 seconds."

**Beat sheet (locked targets)** — recording-relative timing per `video-production-workflow` Phase 1. Re-locked 2026-05-06 against the actual -45dB scrub (46.47s source) and the new zoom-per-beat rule (Hard Rule #9: zoom duration = beat duration; zoom region = what the VO names).

- r=0:00–0:13  Open: prompt + 8 parallel calls       (13s)
- r=0:13–0:26  Why processing matters (consistency)  (13s)
- r=0:26–0:38  Vault stat (ICIR 4.10 + universe)     (12s)
- r=0:38–0:54  Score panel + factor pillars          (16s, dwell:y — zoom on score table)
- r=0:54–1:04  Trajectory (8.7 → 5.9, quality held)  (10s, dwell:y — zoom on 52-week trend paragraph)
- r=1:04–1:10  Silent scrolldown                     (6s, no VO — viewer reads Financial Health / Macro / Dividends / Risk / News / Analyst View; covered in V2/V10/V4)
- r=1:10–1:14  Bottom line                           (4s, dwell:y — zoom on Bottom Line section)
- r=1:14–1:16.5  Closer (brief delivered)            (2.5s, no zoom — natural source playback)

Recording total: 76.5s. Composition: 5s title + 76.5s recording + 7s outro ≈ **88.5s**.

Conformation: 3 pause-zoom segments via `tools/zoom.py` aligned 1:1 with dwell:y beats — score panel (16s, source_t=38), trajectory (10s, source_t=38, different region), bottom line (4s, source_t=44). Total zoom duration: 30s added to 46.47s source = 76.47s recording. Pre-brief beats re-allocated to fit source's 38s of pre-brief content (was 33s in the original lock — adjusted because source has more pre-brief than the design guess assumed).

---

### Video 2: Deep Dive — Full Due Diligence

| Field | Details |
|---|---|
| **Duration** | 5–6 minutes |
| **Audience** | Analysts pre-investment, PMs evaluating new positions |
| **Plugin Command** | `/parallax:deep-dive [ticker]` |
| **Description** | 11 parallel calls including technical analysis and an AI assessment that synthesizes everything. |
| **Demo Script** | *"I'm considering a significant position in TSMC. Can you do a full deep dive — fundamentals, technicals, macro risks, the whole picture? I need to present this to my investment committee next week."* |
| **Why It Matters** | 11 simultaneous calls is something sequential-only models cannot do. The AI assessment shows Parallax as synthesis, not just data. |

**Highlights** — distinct points this video owns

- Eleven parallel calls (more than V1's brief), including async technical analysis (~15–30s)
- AI assessment as the synthesis moment — Parallax beyond data
- IC triples when Quality, Value, Momentum, Tactical, Defensive all agree (this video's lead vault stat)
- Momentum Sharpe 1.95 (most robust factor across horizons)
- 1 billion+ datapoints processed weekly (data infrastructure scale)
- Behavioral momentum: adjusted for news flow + market sentiment (not raw price momentum) — supports the "synthesis, not data" framing
- **Primary value angles** — *Moat headline:* **#4 Auditability** (eleven parallel calls, every one cites its source — the AI assessment's synthesis is traceable back to the underlying call that produced each number; full audit trail for the synthesis itself). *Supporting:* #6 No-black-box · #2 Coverage · #9 Live track record · #3 Defensibility.
- **"Why processing matters" beat**: eleven parallel calls is the visible feat; the harder feat is the AI assessment triangulating them — IC-weighted synthesis across Quality / Value / Momentum / Tactical / Defensive. Sequential review of any single sub-score misses the cross-validation.
- Polaris closer for PM/CIO IC presentations

**Beat sheet**

- Open: brief gives you the overview; deep dive gives you the IC presentation.
- 11 parallel calls fire; technical analysis runs async (~15–30s).
- Walk the output as rendered: factor profile with peer rankings → financial highlights → technical stance (RSI, MACD, S/R) → macro environment for revenue-geography countries → AI assessment (the synthesis moment) → explicit risk factors.
- Vault callouts: *"Momentum Sharpe 1.95, most robust across horizons."* And at the AI assessment: *"When Quality, Value, Momentum, Tactical, and Defensive all agree, the information coefficient triples."* (Sources: stock-selection-alpha WP — verify "triples" wording.)
- Polaris closer for PM/CIO audiences.
- Close: "Eleven calls. One synthesized thesis. IC-ready."

---

### Video 3: Portfolio Health Check

| Field | Details |
|---|---|
| **Duration** | 4–5 minutes |
| **Audience** | PMs, wealth advisors, compliance teams |
| **Plugin Command** | `/parallax:portfolio [holdings]` |
| **Description** | Checkup mode: paste holdings → health badge + five flags + overlap detection + plain-language summary. |
| **Demo Script** | *"Here's my current portfolio — [paste holdings]. I haven't looked at it in a few months. Is anything broken? Should I be worried about concentration or overlap?"* |
| **Why It Matters** | The 5-flag health system is a differentiator. Compliance-friendly "Consider" framing instead of directives. |

**Highlights** — distinct points this video owns

- 5-flag health system: Low Score, Concentration, Redundancy, Value Trap, Macro Misalignment (this video's signature framework)
- Health badge as the at-a-glance verdict
- "Consider" framing — compliance-friendly, never directive
- 80% of cross-sectional beta rankings stable at 6 months — exposures meaningful for next-quarter decisions (this video's lead vault stat)
- **Primary value angles** — *No moat headline.* The 5-flag system + ETF decomposition is a strong feature differentiator but isolates portfolio-diagnostic problems (which holding), not platform-layer bugs — so it isn't #10 Failure isolation in the strict vault sense. *Supporting:* #6 No-black-box · #7 Decision-readiness · #2 Coverage.
- **"Why processing matters" beat**: the overlap flag decomposes ETFs into underlying holdings — stated 8% AAPL might be a true 11% once SPY's holdings unpack. Surface-level weight tables miss this. Same for the 5 thresholds: "concentrated?" is intuition; top-3 > 45% is the math.

**Beat sheet**

- Open: "Is my portfolio actually healthy, or am I sitting on hidden problems?"
- Health badge first (e.g. "Monitor"), then the five flags: Low Score, Concentration, Redundancy, Value Trap, Macro Misalignment.
- Drill into the flags that lit up — show the triggers (e.g. top-3 > 45%, overlapping industries).
- Vault callout: *"Beta rankings are 80% stable at six months — today's exposures are meaningful for decisions you'll revisit next quarter."* (macro-style-box WP.) Optionally: NVDA/XOM monthly-vs-5yr beta contrast for long-horizon holdings.
- Emphasize "Consider" framing (compliance angle).
- Close: "Five flags. One badge. Plain language."

---

### Video 4: Portfolio Rebalancing with Trade Recommendations

| Field | Details |
|---|---|
| **Duration** | 5–6 minutes |
| **Audience** | Active PMs, wealth advisors with discretionary mandates |
| **Plugin Command** | `/parallax:rebalance [holdings with weights]` |
| **Description** | Full rebalance: current state → per-holding health flags → score momentum → prioritized trades → replacement candidates → before/after factor profile. |
| **Demo Script** | *"I've got this Taiwan-heavy portfolio and I know it's not great right now. Can you tell me what to trim, what to keep, and suggest some replacements? I want to reduce concentration but stay in Asia. Here are my holdings: [paste with weights]"* |
| **Why It Matters** | Every recommendation cites a specific flag or data finding. Before/after makes the value tangible. |

**Highlights** — distinct points this video owns

- Diagnose-then-prescribe pairing with V3 (health check → rebalance)
- Per-holding flag evaluation + priority matrix (High = 3+ flags, Medium = 2, Low = 1)
- Trade recommendations cite specific flags by name — never generic advice
- Replacement candidates from same market with factor scores (respects user constraints like "stay in Asia")
- Before/after factor profile as the proof-of-value shot
- Polaris closer for PM/CIO audiences
- **Primary value angles** — *Moat headline:* **#5 Determinism** (re-run the rebalance tomorrow → same trade list, byte-identical). *Supporting:* #7 Decision-readiness · #11 Risk-adjusted · #3 Defensibility.

**Beat sheet**

- Open: health check diagnoses, rebalance prescribes.
- Respect the user's constraint ("stay in Asia") — point that out on screen.
- Per-holding flag evaluation, then priority matrix: High (3+ flags), Medium (2), Low (1).
- Trade recs with flag-tied rationale (no generic advice).
- Replacement candidates in the same market with factor scores.
- Before/after factor profile as the payoff shot.
- Vault callout (optional): NVDA/XOM beta-horizon contrast — justifies why you can't assess risk on a single snapshot. Polaris closer.
- Close: "Diagnosis → action plan → validation. One workflow."

---

### Video 5: Watchlist Monitoring & Surveillance

| Field | Details |
|---|---|
| **Duration** | 3–4 minutes |
| **Audience** | PMs, analysts with 15–30 name watchlists |
| **Plugin Command** | `/parallax:rebalance [tickers without weights]` |
| **Description** | Watchlist mode: submit tickers without weights → surveillance scan → flagged movers + deep-dive recommendations. |
| **Demo Script** | *"I track about 15 names that I'm either holding or considering. Can you check if anything significant has changed in the last few weeks? Here they are: AAPL, MSFT, NVDA, TSMC, JPM, GS, UNH, JNJ, ASML, SAP, SHEL, TM, BHP, 0700.HK, 005930.KS"* |
| **Why It Matters** | The morning check-in use case. Global ticker mix showcases coverage. |

**Highlights** — distinct points this video owns

- Morning check-in use case for 15–30 name watchlists
- Parallel score analysis across all tickers (the visual differentiator)
- Threshold-based alerts (>1 point total, or >2 points on a single factor)
- Global ticker mix (US, Europe, Asia, EM) showcases coverage breadth
- Deep-dive recommendation for highest-magnitude movers
- Note: the uncovered-alpha story (17.7% vs 5.4%, 3.3× edge) is owned end-to-end by N14 — V5 may briefly reference but should not lead with it
- **Primary value angles** — *No moat headline (speed-hook demo).* *Supporting:* #1 Speed · #2 Coverage · #7 Decision-readiness.

**Beat sheet**

- Open: morning check-in — "anything significant changed in my watchlist?"
- Score analysis fires in parallel for all tickers (parallel execution as the visual differentiator).
- Alert table ranked by magnitude; thresholds are >1 point total or >2 points on a single factor.
- Drill into a flagged name: which factor moved, news synthesis catalyst.
- Stable names get one-liner each.
- Deep-dive recommendation for highest-magnitude movers.
- Close: "Fifteen names. ~30 seconds. You know where to focus today."

---

### Video 6: Scenario Analysis — What If X Happens?

| Field | Details |
|---|---|
| **Duration** | 5–6 minutes |
| **Audience** | PMs managing geopolitical/macro risk, CIOs, risk teams |
| **Plugin Command** | `/parallax:scenario [event] portfolio=[holdings]` |
| **Description** | 4-phase workflow: understand event → assess exposure → find rotation candidates → build action plan. |
| **Demo Script** | *"I just saw headlines about China considering export controls on rare earth minerals. I'm worried about my tech-heavy portfolio. Here are my holdings: [paste]. How exposed am I, and what should I be doing right now?"* |
| **Why It Matters** | The prompt captures genuine anxiety; system responds with structured, actionable analysis. |

**Highlights** — distinct points this video owns

- 4-phase workflow: understand event → assess exposure → find rotation → build action plan
- Transmission channels mapped (direct revenue, supply chain, regulatory, sentiment)
- Per-holding H/M/L exposure with the specific transmission mechanism explained
- Tactical signal strongest at 1 week, decays past 12 weeks — why acting on freshness matters
- "What to watch" — 2–3 confirming or invalidating signals as the closer
- **Primary value angles** — *No moat headline (depth demo — transmission channels).* *Supporting:* #11 Risk-adjusted · #7 Decision-readiness · #6 No-black-box.
- **"Why processing matters" beat**: transmission channels (revenue / supply chain / regulatory / sentiment) are the specific framework. "Tech is exposed to China" is intuition; per-holding mapping with explicit channel + magnitude is what makes the scenario actionable rather than vibes.

**Beat sheet**

- Open: headline drops → what do you do?
- Phase 1 (event): news synthesis + telemetry + macro, all parallel. Scenario summary with transmission channels (direct revenue, supply chain, regulatory, sentiment).
- Phase 2 (exposure): per-holding H/M/L with specific transmission mechanism explained.
- Phase 3 (rotation): beneficiary universe built and scored.
- Phase 4 (action): prioritized by urgency with weight suggestions and confidence caveats.
- Close with "what to watch" — 2–3 signals that confirm or invalidate.
- Vault callout (optional, risk team audience): *"Tactical signal is strongest at 1 week and decays past 12 weeks — why acting on signal freshness matters."* (analyst-coverage-signal-perf WP.)
- Close: "From headline to action plan."

---

### Video 7: AI Investor Profiles — The Legends

| Field | Details |
|---|---|
| **Duration** | 6–7 minutes |
| **Audience** | Anyone curious about factor-based philosophy; wealth advisors explaining approaches to clients |
| **Plugin Command** | `/parallax:investor [profile] [ticker]` |
| **Description** | Five modes: Buffett, Greenblatt Magic Formula, Klarman margin of safety, Soros macro reflexivity, Consensus with super-majority math. |
| **Demo Script** | *"Coca-Cola has been in Berkshire's portfolio forever. Does it actually fit the Buffett factor profile, or is it just legacy at this point?"* Then: *"What would all the legendary investors think about NVIDIA? Run them all."* |
| **Why It Matters** | Every profile anchors to a peer-reviewed paper or the investor's own writing. Academic rigor, not celebrity impersonation. |

**Highlights** — distinct points this video owns

- 5 investor profiles: Buffett, Greenblatt (Magic Formula), Klarman, Soros, Consensus
- Academic anchoring — every profile cites a peer-reviewed paper or the investor's own writing (Frazzini/Kabiller/Pedersen for Buffett, etc.)
- Super-majority math: ≥75% agreement threshold for consensus signals
- Verbatim primary-source quotes on screen: Buffett 1962 letter / Klarman 1995 / Greenblatt EBIT/EV + ROIC / Marks on price-vs-quality
- Verdict matrix: where profiles agree, where they disagree, collective blind spots
- **Primary value angles** — *Moat headline:* **#12 Unverifiable frame** (factor thresholds from peer-reviewed papers — Frazzini/Kabiller/Pedersen for Buffett, etc. — vs a chatbot impersonating the investor; the academic anchoring is what makes the profile signal verifiable, not vibes). *Supporting:* #9 Live track record · #6 No-black-box · #3 Defensibility.
- **"Why processing matters" beat**: factor thresholds aren't vibes. Buffett's profile uses Frazzini/Kabiller/Pedersen's *Buffett's Alpha* — Quality > 5, Value > 4, Momentum < 6, Defensive > 7. Academic anchoring separates factor-replication from celebrity impersonation.

**Beat sheet**

- Open: apply Buffett, Greenblatt, Klarman, Soros/Marks frameworks with academic rigor.
- Run 1 (single profile): Buffett on KO. Show four-threshold evaluation (Quality > 5, Value > 4, Momentum < 6, Defensive > 7) derived from Frazzini/Kabiller/Pedersen, *Buffett's Alpha*. Show citation on screen.
- Run 2 (consensus): all four profiles fire in parallel on NVDA.
- Walk the verdict matrix; explain super-majority math (≥75% agreement threshold).
- Key shot: factor-level agreement — which signals are shared, which are flagged by one, collective blind spots.
- Vault-informed quote callouts (verify verbatim before recording):
  - **Buffett**: 1962 letter — make purchase price attractive enough that a mediocre outcome still succeeds.
  - **Klarman**: 1995 letter — margin of safety compensates for being wrong.
  - **Greenblatt**: cheap price + good business (EBIT/EV + ROIC on screen).
  - **Marks**: what's embedded in the price vs. company quality.
- Vault callout (optional): *"When sub-scores agree, IC triples"* — quantitative backing for consensus.
- Close: "Four frameworks. Academic citations. One consensus signal."

---

### Video 8: Build a Portfolio from a Thesis

| Field | Details |
|---|---|
| **Duration** | 4–5 minutes |
| **Audience** | Thematic investors, product teams building model portfolios |
| **Plugin Command** | `/parallax:universe [thesis]` |
| **Description** | Natural-language thesis → scored, weighted, redundancy-checked portfolio. |
| **Demo Script** | *"I believe cloud infrastructure is going to be the backbone of the AI boom, but I want companies that are actually profitable, not just growing revenue. Can you build me a portfolio around that thesis?"* |
| **Why It Matters** | Extracts criteria from plain language; translates into a scored portfolio. |

**Highlights** — distinct points this video owns

- Natural-language thesis → scored, weighted, redundancy-checked portfolio
- Universe search across the live company corpus
- 100% of equal-weight alpha comes from stock selection within markets — Brinson decomposition (this video's lead vault stat — explains why the builder works bottom-up, not top-down)
- Re-rank by factor quality (relevance alone isn't enough)
- Redundancy check flags same-industry overlap; one gets weight-reduced
- Natural handoff to V3 (Portfolio Health Check) on the resulting portfolio
- **Primary value angles** — *Moat headline:* **#5 Determinism** (same thesis → same portfolio, byte-identical — determinism is what makes "natural language to investable allocation" trustworthy; re-run tomorrow with the same thesis and get the same names, weights, and redundancy decisions). *Supporting:* #2 Coverage · #7 Decision-readiness · #3 Defensibility.
- **"Why processing matters" beat**: re-ranking by factor quality is harder than picking thematic names. 100% of equal-weight alpha comes from selection within markets — the builder has to actually score the names against the factor framework, not just collect a relevance list.

**Beat sheet**

- Open: thesis → executable portfolio without hours of manual work.
- Universe search across the live company corpus (use verified universe size).
- Top candidates scored via peer snapshots.
- Re-rank by factor quality (relevance alone isn't enough).
- Redundancy check flags same-industry overlap, one gets weight-reduced.
- Final portfolio: 5–8 names with symbol, sector, total score, weight, key factor strengths.
- Overall factor profile (quality-tilted given the profitability filter).
- Vault callout: *"100% of the equal-weight alpha comes from stock selection within markets — not from country or sector allocation. That's why this builder focuses on names, not top-down allocation."* (stock-selection-alpha WP.)
- Close: "From thesis to executable portfolio. Say the word and we'll run a full health check on the result."

---

### Video 9: ETF Research & Comparison

| Field | Details |
|---|---|
| **Duration** | 3–4 minutes |
| **Audience** | Wealth advisors, passive investors, ETF selectors |
| **Plugin Command** | `/parallax:etf [tickers or keywords]` |
| **Description** | Three workflows: single snapshot, side-by-side comparison with overlap, theme-based search with factor filters. |
| **Demo Script** | *"I hold both QQQ and VGT because I wanted broad tech exposure plus a focused tech position. But my friend said they're basically the same thing — is that true? And what's a better way to diversify into emerging markets without sacrificing quality?"* |
| **Why It Matters** | The overlap revelation creates a natural segue into ETF search. |

**Highlights** — distinct points this video owns

- 3 ETF workflows: single snapshot, side-by-side comparison with overlap, theme search with factor filters
- Overlap revelation as the natural narrative pivot ("multiple ETFs ≠ diversification, necessarily")
- Hidden % overlap surfaced (e.g., QQQ vs VGT — the actual % comes from recording)
- Theme search with factor filter for genuine diversification candidates (e.g., emerging-markets quality)
- Optional callout: 62,000+ listings across 48 markets — coverage matches global allocation footprint
- **Primary value angles** — *No moat headline (overlap-revelation demo).* *Supporting:* #2 Coverage · #6 No-black-box · #7 Decision-readiness.

**Beat sheet**

- Open: multiple ETFs ≠ diversification, necessarily.
- Pull profiles for QQQ and VGT; run overlap analysis.
- Side-by-side: factor scores, top holdings, sector breakdown.
- Overlap result: confirm/deny the "basically the same" thesis (actual % overlap comes from recording).
- Theme search for emerging markets + quality filter.
- Top result: factor profile + holdings breakdown showing genuine EM diversification.
- Vault callout (optional for global audiences): *"Parallax works in 36 of 37 markets — coverage that matches your allocation footprint."* (stock-selection-alpha WP.)
- Close: "One question uncovered hidden overlap and found a quality alternative."

---

### Video 10: Macro Outlook & Country Deep Dive

| Field | Details |
|---|---|
| **Duration** | 4–5 minutes |
| **Audience** | Global macro investors, CIOs, asset allocators |
| **Plugin Command** | `/parallax:macro [country]` |
| **Description** | Full macro: regime status, 9 components, factor regime interaction, equity opportunity screening. |
| **Demo Script** | *"I've been reading about Japan's economic resurgence and the weak yen. What's the macro picture actually look like, and are there good equity opportunities there right now? Also, how does Japan compare to the US from a factor perspective?"* |
| **Why It Matters** | Connects macro views to actionable factor tilts. The factor-regime interaction is unique to Parallax. |

**Highlights** — distinct points this video owns

- Five macro variables (inflation, rates, currency, labor, GDP) explain 16% of monthly stock return variation globally (this video's lead vault stat)
- Local macro dominates US macro by 6–9× for non-US stocks
- Factor-regime interaction — the Parallax-only section (no other tool does this)
- Macro module architecture: 9 specialist analysts working in parallel
- Generation: ~4 minutes per market; coverage: 10 country markets + 1 global = 11 total reports (US, China, Germany, Japan, UK, Canada, France, India, Malaysia, Singapore + Global)
- Pipeline: regime tag → tactical outlook → factor tilts → equity opportunities → US comparison
- **Primary value angles** — *No moat headline (depth demo — factor-regime interaction).* *Supporting:* #11 Risk-adjusted · #2 Coverage · #6 No-black-box.
- **"Why processing matters" beat**: factor-regime interaction is the unique Parallax move. Connecting "late-cycle inflation" to specific factor tilts (Quality / Value win, Momentum cools) isn't in any standard macro tool — macro-style-box research is the underlying framework, and the connection from regime → factor is the load-bearing step.
- Polaris closer for CIO audiences

**Beat sheet**

- **Lead with vault callout**: *"Five macro variables — inflation, rates, currency, labor, GDP — explain 16% of monthly stock return variation globally. For non-US stocks, local macro dominates US macro by 6 to 9 times."* (macro-style-box WP.) This is the methodological spine of the module — establish credibility up front.
- Regime tag + signals (risk-on/off/transitioning).
- Tactical outlook with sector positioning.
- **Factor-regime interaction** — the Parallax-only section. Which of Q/V/M/D is favored in this regime.
- Equity opportunities: top Japanese picks screened & scored.
- US comparison side by side.
- Polaris closer for CIO audience.
- Close: "Headline → regime → factor tilts → stock picks."

---

### Video 11: Shariah Compliance Screening

| Field | Details |
|---|---|
| **Duration** | 3–4 minutes |
| **Audience** | Islamic finance teams, Shariah-compliant advisors, halal fund managers |
| **Plugin Command** | `/parallax:screen halal [ticker or portfolio]` |
| **Description** | AAOIFI/DJIM screening: prohibited industries, three ratio thresholds, purification ratios, portfolio mode with replacements. |
| **Demo Script** | *"I manage a Shariah-compliant fund and I need to check if these five holdings still pass AAOIFI screening. If any have drifted out of compliance, find me halal alternatives in the same sectors."* |
| **Why It Matters** | Islamic finance AUM is $4T+ globally. Addresses a compliance need that's currently manual. |

**Highlights** — distinct points this video owns

- AAOIFI/DJIM screening: prohibited-industry test + three ratio thresholds + purification ratios
- Specific thresholds visible on screen: total debt/assets <33%, interest-bearing securities/assets <33%, non-permissible revenue <5%
- Purification ratio for borderline passes (donation amount calculation)
- Replacements in same sector with factor scores
- Addresses $4T+ Islamic finance AUM — currently a manual workflow
- **Primary value angles** — *Moat headline:* **#4 Auditability** (AAOIFI thresholds documented — compliance officer signs off on the methodology once). *Supporting:* #6 No-black-box · #2 Coverage.
- **"Why processing matters" beat**: AAOIFI screening is three specific ratio thresholds — 33% / 33% / 5% — plus a purification ratio for borderline passes. A casual "is this halal?" skips the math; manual screens take hours per portfolio. The thresholds are the work.

**Beat sheet**

- Open: screening is a regulatory requirement, usually manual — automate it.
- Per-holding check: prohibited-industry test → three AAOIFI ratios.
- Compliance table: pass/fail with specific reason.
- Show the ratio thresholds explicitly: total debt / assets < 33%; interest-bearing securities / assets < 33%; non-permissible revenue < 5%.
- Purification ratio for borderline passes (donation amount).
- Replacements in same sector with factor scores.
- Close: "Compliance in under a minute."

---

### Video 12: Forensic Earnings Quality Analysis

| Field | Details |
|---|---|
| **Duration** | 4–5 minutes |
| **Audience** | Analysts, risk teams, short sellers, compliance officers |
| **Plugin Command** | `/parallax:screen quality [ticker]` |
| **Description** | Forensic workflow: quality trajectory, revenue/margin trends, cash flow divergence, accruals, AI synthesis with traffic light. |
| **Demo Script** | *"Something feels off about this company's earnings — revenue keeps growing but cash flow isn't keeping up. Can you run a forensic check on their earnings quality? I want to know if this is a red flag or if I'm being paranoid."* |
| **Why It Matters** | Captures an analyst's gut feeling and validates or dismisses it with data. |

**Highlights** — distinct points this video owns

- NLP detects texts predicting large cash-flow impairments and financial restatements — proprietary research shows it accurately predicts future stock crashes (this video's lead vault stat)
- Forensic Palepu-framework analysis runs async in the background
- Traffic-light risk summary (red/yellow/green) as the at-a-glance verdict
- Quality score trajectory over 52 weeks — surfaces the inflection point
- Cash conversion analysis: revenue vs operating cash flow over 4 reporting periods
- Specific red flags: receivables growing faster than revenue, working-capital deterioration
- AI assessment synthesizes quality trend + cash flow + accruals + news into one risk opinion
- Validates analyst gut feeling with data — "your gut was right, now you have evidence"
- **Primary value angles** — *Moat headline:* **#4 Auditability** (every NLP flag traces to a specific source quote in the management transcript — the forensic conclusion has a documented evidence chain from language pattern to citation; the flag is defensible because the underlying language is right there). *Supporting:* #6 No-black-box · #2 Coverage.
- **"Why processing matters" beat**: earnings-quality decline shows up in language before it shows up in numbers. The NLP layer detects texts predicting cash-flow impairments and restatements. A financial-only check misses the leading indicator — receivables-to-revenue catches it later, when the loss is already booked.

**Beat sheet**

- Open: revenue up, cash flow lagging — red flag or overthinking?
- Multiple data calls + async Palepu-framework analysis fires in background.
- Traffic light risk summary (red/yellow/green).
- Quality score trajectory over 52 weeks — show the inflection point.
- Cash conversion analysis: revenue vs operating cash flow over 4 periods.
- Specific red flags: receivables growing faster than revenue, working capital deterioration.
- AI assessment synthesizes quality trend + cash flow + accruals + news into one risk opinion.
- Recommendations: what to monitor quarterly, what to investigate, what would change the thesis.
- Close: "Your gut was right. Now you have the data."

---

## Niche Use Case Videos (14)

Shorter videos targeting power users, specific segments, or advanced capabilities. More direct prompts — audience already knows what they want.

---

### Video N1: Cash as a Portfolio Holding

| Field | Details |
|---|---|
| **Duration** | 2–3 minutes |
| **Audience** | Wealth advisors, PMs with significant cash positions |
| **Plugin Command** | `/parallax:portfolio` with cash-equivalent ETF in holdings |
| **Description** | Include BIL/SHV at actual cash weight for realistic factor scores. Run both versions side by side. |
| **Demo Script** | Same portfolio twice: first normalized to 100% equities, then with 30% BIL as a cash proxy. |
| **Why It Matters** | Real portfolios hold cash deliberately; ignoring it distorts everything. |

**Highlights** — distinct points this video owns

- Same portfolio normalized to 100% equities vs. with real cash weight (BIL/SHV proxy)
- The diff: Defensive score rises, concentration flags clear when cash is treated as a real position
- "Cash is a position. Treat it like one." — this video's framing line
- **Primary value angles** — *No moat headline (single-parameter demo).* *Supporting:* #6 No-black-box · #7 Decision-readiness.

**Beat sheet**

- Open: normalizing to 100% equities misrepresents real positioning.
- Run 1: stocks only, weights summing to 100%.
- Run 2: same stocks at real weights + 30% BIL.
- Highlight the diff: Defensive score up, concentration flags clear (no single stock > 15% of total).
- Close: "Cash is a position. Treat it like one."

---

### Video N2: Mixed Stocks + ETFs — True Factor Exposure

| Field | Details |
|---|---|
| **Duration** | 2–3 minutes |
| **Audience** | Clients holding both individual stocks and index ETFs |
| **Plugin Command** | `/parallax:portfolio` with mixed holdings |
| **Description** | Plugin decomposes ETFs into underlying holdings for true factor exposure + hidden redundancy. |
| **Demo Script** | AAPL 20%, MSFT 20%, SPY 40%, QQQ 20%. Show decomposition and hidden overlap. |
| **Why It Matters** | Catches hidden concentration a simple weight table misses. |

**Highlights** — distinct points this video owns

- Auto-decomposition of ETFs into their underlying holdings for true factor exposure
- Hidden compound concentration revealed (e.g., effective AAPL exposure via SPY + QQQ + direct holding)
- Catches what a simple weight table misses
- **Primary value angles** — *No moat headline.* *Supporting:* #10 Failure isolation (secondary — ETF decomposition is V3's mechanism applied directly) · #6 No-black-box · #2 Coverage.
- **"Why processing matters" beat**: ETF decomposition is the load-bearing step. AAPL via SPY's holdings + QQQ's holdings + a direct position can compound to 26% effective concentration where the stated weight table reads 20%. Without decomposition, the risk picture isn't real.

**Beat sheet**

- Open: "Four positions, right? Not quite."
- Paste mixed portfolio; system auto-decomposes ETFs.
- Effective AAPL exposure > stated (AAPL is top-weight in both SPY and QQQ).
- Redundancy check flags the compound concentration.
- Close: "Decompose your ETFs. Real exposure might surprise you."

---

### Video N3: Custom Benchmark Comparison

| Field | Details |
|---|---|
| **Duration** | 2–3 minutes |
| **Audience** | International PMs, thematic investors, anyone benchmarked to something other than S&P 500 |
| **Plugin Command** | `analyze_portfolio` with `benchmark` parameter |
| **Description** | Swap SPY → EWJ/EEM/any ETF. Narrative flips. |
| **Demo Script** | Japan-heavy portfolio vs SPY (default), then re-run with `benchmark=EWJ`. |
| **Why It Matters** | One parameter, entirely different client conversation. |

**Highlights** — distinct points this video owns

- One parameter (`benchmark=`) flips the entire narrative
- Default SPY is wrong for non-US mandates
- Same Japan portfolio: vs SPY underperforms; vs EWJ outperforms — different client conversation
- **Primary value angles** — *No moat headline (single-parameter demo).* *Supporting:* #6 No-black-box · #3 Defensibility.

**Beat sheet**

- Open: default benchmark = SPY. That's wrong for non-US mandates.
- Run 1: Japan portfolio vs SPY — looks like underperformance.
- Run 2: same portfolio vs EWJ — outperforming its actual benchmark.
- Close: "Match benchmark to mandate. One parameter changes the conversation."

---

### Video N4: Smart ETF Analysis — Bonds & Commodities

| Field | Details |
|---|---|
| **Duration** | 2–3 minutes |
| **Audience** | Multi-asset allocators, diversified wealth advisors |
| **Plugin Command** | `analyze_etf_smart` (auto-routing) |
| **Description** | Auto-detects non-equity ETFs, routes to macro analysis. |
| **Demo Script** | `analyze_etf_smart` on SPY (equity scoring), GLD (commodity macro), AGG (bond macro). |
| **Why It Matters** | Answers the "Parallax only does equities" objection. |

**Highlights** — distinct points this video owns

- Auto-detection of non-equity ETFs → routing to macro analysis (no manual asset-class tagging)
- Three asset classes in one tool: SPY (equity scoring), GLD (commodity macro), AGG (fixed-income macro)
- Routing metadata visible on screen: detected asset class, mapping rate, routing decision
- Answers "Parallax only does equities" objection — addresses multi-asset allocator concerns
- **Primary value angles** — *No moat headline (objection-handler demo).* *Supporting:* #2 Coverage · #8 Workflow-native.

**Beat sheet**

- Open: Parallax is known for equity scoring. What about gold? Bonds?
- SPY → full equity factor scoring.
- GLD → auto-routes to commodity macro analysis.
- AGG → auto-routes to fixed-income macro.
- Highlight the routing metadata on screen: detected asset class, mapping rate, decision.
- Close: "One tool, three asset classes, full transparency on how it decides."

---

### Video N5: Score Trajectory & Inflection Detection

| Field | Details |
|---|---|
| **Duration** | 2–3 minutes |
| **Audience** | Momentum-focused traders, analysts hunting turnarounds |
| **Plugin Command** | `get_score_analysis` with different time windows |
| **Description** | 4-week, 26-week, 52-week windows reveal inflection points where factor scores reversed. |
| **Demo Script** | Same stock at 4wk, 26wk, 52wk. Narrative shifts. |
| **Why It Matters** | Moves Parallax from snapshot tool to trend-analysis platform. |

**Highlights** — distinct points this video owns

- 4-week, 26-week, 52-week trajectories on the same ticker
- Momentum signal peaks at 24 months, Value dominates at 60 months (this video's lead vault stat)
- Inflection points surfaced — e.g., Quality declining for months → 4-week reversal
- Snapshot vs. trend distinction — "score is a snapshot, trajectory is the signal"
- Optional callout: monthly beta misstates long-horizon risk (NVDA 1.79 spot → ~7× higher at 5-yr)
- **Primary value angles** — *No moat headline.* Trajectory analysis with factor decomposition is a strong no-black-box demo (drill into which factor moved), but it isolates analytical components, not platform-layer bugs — so it isn't #10 Failure isolation in the strict vault sense. *Supporting:* #6 No-black-box · #9 Live track record.
- **"Why processing matters" beat**: a composite of 5.9 today is a snapshot. Trajectory matters because the signal lives at the time horizon — Momentum peaks at 24 months, Value at 60. Most reads stop at the spot value; that's where the actual edge starts.

**Beat sheet**

- **Reframe around vault**: *"Momentum signal peaks at 24 months. Value dominates at 60 months. Trajectory isn't a nice-to-have — it's where the signal actually lives."* (beta-horizon WP.)
- Run at 4wk, 26wk, 52wk on same ticker.
- Highlight the inflection point: Quality declining for months → reversal 4 weeks ago.
- Optional callout: *"Monthly beta misstates long-horizon risk — NVDA 1.79 spot goes to ~7× higher at five years."*
- Close: "Always check the trend. Score is a snapshot. Trajectory is the signal."

---

### Video N6: Soros Mode — Trade Ideas from Scratch

| Field | Details |
|---|---|
| **Duration** | 3–4 minutes |
| **Audience** | Macro-oriented PMs, global allocators |
| **Plugin Command** | `/parallax:investor soros` (basket mode, no ticker) |
| **Description** | No ticker → regime-based trade ideas generated top-down. |
| **Demo Script** | *"Soros view on current markets"* — no ticker. |
| **Why It Matters** | No other tool generates tradeable ideas from regime analysis alone. |

**Highlights** — distinct points this video owns

- Top-down ideation from regime analysis with no ticker as input (every other Investor Profile starts with a ticker)
- Scans 3–5 markets (US, Japan, Europe, India) for regime divergence
- Themes emerge → per-theme stock universe built and ranked → actual stock picks per theme
- "Macro strategist on demand" — this video's framing line
- **Primary value angles** — *No moat headline (ideation demo).* *Supporting:* #11 Risk-adjusted · #2 Coverage.

**Beat sheet**

- Open: every other profile starts with a ticker. Soros basket starts with nothing.
- System scans 3–5 markets for regime divergence (US, Japan, Europe, India).
- Themes emerge; per-theme stock universe built and ranked.
- Show actual stock picks per theme.
- Close: "Macro strategist on demand."

---

### Video N7: Export to CSV — Bridging to Excel

| Field | Details |
|---|---|
| **Duration** | 2 minutes |
| **Audience** | Analysts who live in Excel, compliance teams needing audit trails |
| **Plugin Command** | `export_price_series`, `export_peer_comparison` |
| **Description** | CSV/JSON export for Excel, charting, internal systems. |
| **Demo Script** | Export peer comparison in CSV, then 365-day price series. |
| **Why It Matters** | Parallax as a data source enhancing existing tools, not a walled garden. |

**Highlights** — distinct points this video owns

- Peer comparison + 365-day price series → CSV/JSON export
- Audit-trail-ready output for compliance and Excel workflows
- Parallax as a data source feeding existing tools — not a walled garden
- **Primary value angles** — *No moat headline (format demo).* *Supporting:* #4 Auditability (secondary — "audit-trail-ready output") · #8 Workflow-native.

**Beat sheet**

- Open: not everything stays in the chat.
- Export peer comparison for one ticker in CSV.
- Export 365 days of price data.
- Show structured output ready to paste into Excel.
- Close: "Parallax feeds your existing workflow."

---

### Video N8: Portfolio Lens — Fast Targeted Analysis

| Field | Details |
|---|---|
| **Duration** | 2–3 minutes |
| **Audience** | PMs who need quick answers, not full reports |
| **Plugin Command** | `analyze_portfolio` with `lens` parameter |
| **Description** | `lens=performance, risk, quality, concentration, holdings, attribution` for fast targeted answers. |
| **Demo Script** | Run with `lens=attribution`, then `=concentration`, then `=risk`. |
| **Why It Matters** | Parallax is fast enough for real-time conversations, not just batch. |

**Highlights** — distinct points this video owns

- `lens=` parameter for fast targeted answers (60–90s full analysis → near-instant lens)
- 6 lens modes: `performance`, `risk`, `quality`, `concentration`, `holdings`, `attribution`
- Real-time conversation pace, not batch reporting
- **Primary value angles** — *No moat headline (speed-of-iteration demo).* *Supporting:* #1 Speed · #7 Decision-readiness.

**Beat sheet**

- Open: full analysis is 60–90s. Sometimes you want one answer.
- `lens=attribution` → which stocks and sectors drove returns.
- `lens=concentration` → sector and market allocation at a glance.
- `lens=risk` → drawdown, volatility, the numbers risk teams want.
- Close: "Ask specific. Get specific. No waiting."

---

### Video N9: Backtest from a Specific Date

| Field | Details |
|---|---|
| **Duration** | 2–3 minutes |
| **Audience** | PMs evaluating strategies, advisors showing historical context |
| **Plugin Command** | `analyze_portfolio` with `start_date` |
| **Description** | Backtest from any date. Narrative shifts with starting point. |
| **Demo Script** | Default (1yr), then `start_date=2024-01-01`, then pre-rally date. |
| **Why It Matters** | Answers "how has it done since I invested?" |

**Highlights** — distinct points this video owns

- `start_date` parameter — backtest from any date, not just rolling-window defaults
- Same portfolio: 3 different stories from 3 different windows (default 1yr / Jan 2024 / pre-rally)
- Answers "how has it done since I invested?" naturally
- **Primary value angles** — *Moat headline:* **#5 Determinism** (niche slot — specify start_date, get the same backtest every time). *Supporting:* #6 No-black-box · #3 Defensibility.

**Beat sheet**

- Open: starting date changes everything.
- Run default (1yr lookback).
- Run from Jan 2024 — Sharpe and max drawdown shift.
- Run from pre-rally — different story again.
- Close: "Match the window to the question."

---

### Video N10: Live Methodology Deep-Dive (Free Tool)

| Field | Details |
|---|---|
| **Duration** | 2 minutes |
| **Audience** | Skeptical clients, quant-oriented prospects, compliance |
| **Plugin Command** | `explain_methodology` + `get_docs` (both free) |
| **Description** | Pull scoring methodology in real time. Free and instant. |
| **Demo Script** | Client asks why NVDA Value score is 2.5. Call `explain_methodology`; then `get_docs` for full methodology. |
| **Why It Matters** | Transparency sells. Every score has a documented, citable methodology. |

**Highlights** — distinct points this video owns

- `explain_methodology` + `get_docs` — both free tools, zero token cost
- Real-time score-by-score explanations contextualized to a specific score
- Full academic documentation pulled from docs.chicago.global on demand
- "No black box. Every score documented, citable, explainable on demand."
- **Primary value angles** — *Moat headline:* **#4 Auditability** (niche slot — methodology is documented, free to inspect, zero-token tool). *Supporting:* #6 No-black-box · #9 Live track record.

**Beat sheet**

- Open: client asks "what does a Value score of 2.5 actually mean?"
- Call `explain_methodology` — contextualized explanation for that specific score.
- Call `get_docs` — full academic documentation from docs.chicago.global.
- Close: "No black box. Every score documented, citable, explainable on demand."

---

### Video N11: PDF Research Report Generation

| Field | Details |
|---|---|
| **Duration** | 2–3 minutes |
| **Audience** | Analysts needing printable deliverables, RMs preparing for client meetings |
| **Plugin Command** | `get_stock_report` with `format=pdf` |
| **Description** | Print-ready PDF research report. Fire-and-forget, ~15 min generation. |
| **Demo Script** | `get_stock_report` for AAPL with `format=pdf`. Show job_id, check status, retrieve PDF. |
| **Why It Matters** | Institutional-grade deliverables, not just chat responses. |

**Highlights** — distinct points this video owns

- Print-ready institutional-grade PDF deliverable
- Fire-and-forget async pattern (~15 min generation)
- Job ID → status check → finished URL flow
- Charts, factor analysis, peer comparison, fully formatted
- **Primary value angles** — *No moat headline (format demo).* *Supporting:* #4 Auditability (secondary — institutional-grade PDF for compliance package) · #7 Decision-readiness · #8 Workflow-native.

**Beat sheet**

- Open: some viewers need a PDF to email or bring to a meeting.
- Fire the request — immediate job_id return.
- Check job status; show the URL when done.
- Open finished PDF — charts, factor analysis, peer comparison, fully formatted.
- Close: "Institutional-grade deliverables. One API call."

---

### Video N12: The Free Tier — Zero Tokens

| Field | Details |
|---|---|
| **Duration** | 3–4 minutes |
| **Audience** | Cost-conscious prospects, trial users, evaluators |
| **Plugin Command** | `explain_methodology`, `get_peer_snapshot`, `discover_stocks`, `search_stocks`, `search_etfs`, `etf_profile`, `etf_holdings`, `export_price_series`, `export_peer_comparison`, `list_macro_countries` |
| **Description** | Complete research workflow using only free tools. |
| **Demo Script** | Search for Apple → peer snapshot → discover similar → export price → explain score. All free. |
| **Why It Matters** | Removes the "pay before seeing value" objection. |

**Highlights** — distinct points this video owns

- Full research workflow using only free tools
- Free toolkit: `search_stocks`, `get_peer_snapshot`, `discover_stocks`, `export_price_series`, `explain_methodology` (and others)
- Removes the "pay before seeing value" objection
- "Peer scores, discovery, price data, methodology — all without spending a token."
- **Primary value angles** — *No moat headline (free-tier demo).* *Supporting:* #1 Speed · #8 Workflow-native.

**Beat sheet**

- Open: before you spend a token, here's the free tier.
- `search_stocks` finds AAPL.O.
- `get_peer_snapshot` — factor scores + peer comparison.
- `discover_stocks` — "quality tech in the US" — six scored results.
- `export_price_series` — 365 days of price CSV.
- `explain_methodology` — what the Quality score means.
- Close: "Peer scores, discovery, price data, methodology — all without spending a token."

---

### Video N13: Market Regime & Daily Telemetry

| Field | Details |
|---|---|
| **Duration** | 2–3 minutes |
| **Audience** | Macro traders, systematic strategists, anyone asking "what's the market doing today?" |
| **Plugin Command** | `get_telemetry` with targeted fields |
| **Description** | Daily regime snapshot: regime tag, signals, commentary, divergences. Use `fields` to control response size. |
| **Demo Script** | `get_telemetry` with targeted fields for regime + commentary. Show divergences. Mention `factor_view` for quants. |
| **Why It Matters** | Answers the most common morning question. |

**Highlights** — distinct points this video owns

- `get_telemetry` with focused `fields` parameter for response-size control
- Regime tag + signals + commentary explaining transmission mechanism
- Cross-market divergences — where opportunities and risks emerge across regions
- `factor_view` for quants: cross-market factor decomposition, 400 baskets, 1MB+ structured data
- "Morning briefing in one call"
- **Primary value angles** — *No moat headline (telemetry demo).* *Supporting:* #1 Speed · #2 Coverage.

**Beat sheet**

- Open: "What's the market doing, and what does it mean for my positioning?"
- Single `get_telemetry` call with focused fields.
- Regime tag + key signals + commentary explaining mechanism.
- Cross-market divergences — where opportunities and risks emerge.
- Mention `factor_view` for quant clients: cross-market factor decomposition, 400 baskets, 1MB+ structured data.
- Vault callout (optional): *"Five macro variables explain 16% of monthly return variation globally."* (macro-style-box WP.)
- Close: "Morning briefing in one call."

---

### Video N14: Finding Alpha Where Wall Street Isn't Looking *(new)*

| Field | Details |
|---|---|
| **Duration** | 2–3 minutes |
| **Audience** | Edge-seeking PMs, quant discretionary managers, small/mid-cap specialists |
| **Plugin Command** | `search_stocks` / `discover_stocks` with coverage filter |
| **Description** | Dedicated video for the uncovered-stock alpha story — most differentiated finding in the white-paper corpus. |
| **Demo Script** | Discover high-scoring stocks with zero analyst coverage. Compare against covered peers. |
| **Why It Matters** | 17.7% vs 5.4% alpha gap between uncovered and covered — 3.3× edge where no one else is looking. Currently buried in V5; deserves its own moment. |

**Highlights** — distinct points this video owns

- 17.7% alpha in uncovered stocks vs 5.4% covered = 3.3× edge gap (this video owns the uncovered-alpha story end-to-end; V5 may briefly reference)
- 65% of universe uncovered — 25,545 of 39,403 stocks
- Discovery query filtered by high composite score + zero analyst coverage
- Most differentiated finding in the white-paper corpus — this video is its dedicated home
- "Wall Street is fishing in the same pond. Parallax shows you where no one's cast a line." — this video's framing line
- **Primary value angles** — *Moat headline:* **#12 Unverifiable frame** (niche slot — alpha from peer-reviewed framework finding undercovered names, not from fabricated numbers). *Supporting:* #11 Risk-adjusted · #2 Coverage · #9 Live track record.
- **"Why processing matters" beat**: the empirical finding behind this — 17.7% alpha in uncovered names vs 5.4% in covered — is from peer-reviewed research, not folk wisdom. Discovery filters are common; the data on *where* to filter is the moat.

**Beat sheet**

- Open with the vault stat: *"Two-thirds of the global universe has zero analyst coverage — 25,545 of 39,403 stocks. The alpha gap is 17.7% vs 5.4%. That's 3.3× more edge where no one else is looking."* (analyst-coverage-signal-perf WP.)
- Run a discovery query filtered for high composite score + zero coverage.
- Show a handful of names that most clients have never heard of.
- Pull one peer snapshot to show the scoring is rigorous.
- Close: "The rest of the market is fishing in the same pond. Parallax shows you where no one's cast a line."

---
