# PARALLAX PLUGIN — Demo Video Production Plan (Master)

*Single source of truth. Supersedes both the original `Parallax Demo Video Production Plan.md` and the `Updated Plan.md` companion doc.*

*Revised May 2026 (persona-and-moment overhaul + vault-stats integration rule).*

*20 videos: 4 instructional (I1–I4) + 16 use-case product demos (V1–V16).*

---

**Prepared for Chicago Global — Parallax Team**

---

## Executive Summary

A production plan for a 20-video content library demonstrating the Parallax MCP plugin to prospective clients. The slate is organised around `primary_persona × primary_moment × deliverable` rather than per-Parallax-command, so a single tool (e.g. `/parallax:stock`) can appear in multiple videos under different personas and decision moments.

**Slate composition:**

- **4 instructional (I1–I4)** — audience-general utility content: install, first-brief quickstart, free-tier walkthrough, exports & integrations. No persona pretense.
- **16 use-case product demos (V1–V16)** — persona-and-moment-driven, split across three complexity tiers:
  - **Tier 1 (V1–V6, single-feature)** — one Parallax tool serving one persona at one decision moment (e.g. V1 RM client-question stock check, V2 PM pre-trade score check, V4 Shariah screen).
  - **Tier 2 (V7–V13, workflow-chain)** — 2–4 chained tools producing a composite deliverable (quarterly portfolio review, IC position defense, full deep-dive, regime-window backtest, etc.).
  - **Tier 3 (V14–V16, hero playbooks)** — publishable synthesis (macro event response, stock initiation report, forensic earnings).

Per-video specifications live in the **NEW SLATE — Phase 3 Draft** section toward the bottom of this file. Each video carries a persona/moment anchor, a **Highlights** subsection naming the distinct output moments and value angles it owns, a beat sheet with target seconds per beat, locked recording inputs (ticker + prompt-to-type + pre-test checklist), title-card copy, YouTube title, and format invariants.

The **Vault-Sourced Stats Library** below is a reference of available stats, not a per-video ownership map. Per the 2026-05-21 *"Vault stats integrate, not narrate"* decision, use-case scripts include vault stats only when load-bearing for a specific output moment — standalone credibility-ribbon beats have been dropped.

**Intelligence briefs** (anchor-style market wraps) are shelved as a deferred future addition. Infrastructure is preserved for clean reactivation; no video in the current slate uses the style.

---

## Production workflow

**Beat-sheet first.** Each video's beat sheet is locked from its Highlights subsection in this document *before* the screen recording is captured — so every spoken line and on-screen callout traces back to a planned beat with a target duration. Recording, scripting, and zoom design all conform to the beat sheet; the beat sheet does not bend to the recording. This is enforced as the first hard rule of the methodology.

Each video proceeds through an 11-phase per-video loop:

1. **Lock beat sheet** — extract Highlights from this document; assign target seconds + dwell flags per beat.
2. **Record** — single-take screen capture at 1920×1080, 60fps.
3. **Conform** — tapered scrub of dead loading time (custom tooling, free).
4. **Extract frames** — even-spaced stills from the scrubbed recording for hallucination-checking the script.
5. **Write script** — voiceover written against the locked beat windows and the extracted frames. Hard rule: every on-screen claim cites a specific frame.
6. **Apply zoom** — script-driven pause-zoom-hold-resume directives over content-rich beats (factor table, score panel, brief paragraph). Zoom regions are derived from what the voiceover names — never the other way around.
7. **Preview render** — local render at full fidelity using Hyperframes (open-source HTML→MP4). Free, fast iteration; the avatar slot uses a placeholder.
8. **Auto polish pass** — runtime check, sentence-rhythm pass, beat coverage audit; auto-runs after every preview render and converges within 1–2 passes.
9. **Iterate** — re-script, re-zoom, re-render freely. Cost: $0.
10. **Final render** — generates a HeyGen avatar talking-head clip (the only billable step) and composites it into the preview. Clips are cached by script-body hash, so re-rendering with unchanged voiceover doesn't re-bill.
11. **Cleanup** — after explicit user approval, scratch frames are deleted; the script's `frames_used` audit trail is the durable record.

**Cost model.** Avatar generation is the only billable step in the pipeline. Local rendering, scrub, zoom, and frame extraction are all free, so iteration on layout, timing, and copy is unconstrained until the script body itself changes.

**Visual format.** 1920×1080 at 60fps. Each video uses one shared template — a 5-second title card (eyebrow + headline), the screen recording with an avatar picture-in-picture and lower-third callouts, and a ~7-second outro carrying the Chicago Global tagline (`"Solve the market."` by default; PM/CIO-audience hero playbooks may close with the Polaris one-liner — *"This isn't a backtest. Polaris has been running on these scores since 2019."*). Format invariants — layout positions, character limits, animation timings, lower-third constraints — are codified in the template's render guide.

---

## Vault-sourced stats library (reference, not distribution)

Every on-screen callout and voiceover number in this plan traces back to a vault source. Do not put a stat on screen that isn't in this table (or added here with a source before recording).

**2026-05-21 — Scope narrowed.** This table is now a *reference of available stats*, not a *distribution map of per-video ownership*. The "Owner" column reflects which video originally claimed each stat under the pre-2026-05-21 Highlights-ownership rule. Per the "Vault stats integrate, not narrate" decision (`decisions/2026-05-21-vault-stats-integrate-not-narrate.md`), use-case videos (V1–V16) no longer carry vault stats as ownership claims by default — stats appear in a script only when load-bearing for a specific output moment, via the two-mold inclusion test in `video-scriptwriting/SKILL.md`. The Owner column is now *historical*; treat it as "first author who used this stat" rather than "the video that must use this stat." Stats that don't integrate cleanly into use-case scripts (ICIR, Sharpe, +5.8%/yr selection return — jargon stats requiring their own definition) migrate to V9 Deep Dive / hero playbooks V14–V16 / instructionals (I1–I4 for orientation) / out-of-slate marketing surfaces.

| Stat | Source | Owner |
|---|---|---|
| Composite score: ICIR 4.10, Sharpe 2.34 (long/short), +5.8%/yr Q5 over 13 years | `stock-selection-alpha/2026-04_stock-selection-alpha.tex` | V1 |
| Live universe: **62,000+ primary listings** across **48 markets** (1.4M+ identifiers across exchanges) | `04-Marketing/Key Differentiators.md` | V0.5, V1, V9 |
| Score-to-recommendation map: 8.5–10.0 STRONG BUY · 6.5–8.4 BUY · 3.5–6.4 HOLD · 1.5–3.4 SELL · 0.0–1.4 STRONG SELL | `01-Product/Scoring System.md` | V1 |
| **100% of equal-weight alpha** comes from stock selection within markets (Brinson) | `stock-selection-alpha/2026-04_stock-selection-alpha.tex` | V8 |
| When sub-scores agree, **IC triples** (verify exact wording in WP) | same | V2 |
| **1 billion+ datapoints** processed weekly | `02-Methodology/Scoring Process.md` (also `04-Marketing/Key Differentiators.md`) | V2 |
| Behavioral momentum: stock price momentum **adjusted for news flow and market sentiment** (not raw momentum) | `02-Methodology/Investment Factors.md` | V2 |
| Momentum Sharpe **1.95**, most robust across horizons | `analyst-coverage-signal-perf` | V2, N5 |
| Tactical Sharpe 1.77 at 1 week, decays to <0 past 12 weeks | same | V6, N5 |
| **17.7% alpha among uncovered stocks** vs 5.4% covered (3.3×) | same | N14 |
| 65% of universe uncovered (25,545 of 39,403 stocks per WP cohort) | same | N14 |
| Momentum peaks at **24 months**, Value dominates at **60 months** | `beta-horizon-factor-scores` | N5 |
| Monthly beta misstates long-horizon risk: NVDA 1.79 → ~7× higher at 5-yr; XOM 0.70 → 0.24 | same | V3, V4, N5 |
| **80% of cross-sectional beta rankings stable at 6 months** | `macro-style-box` | V3 |
| Five macro forces explain **16% of monthly return variation** | same | V10 |
| Local macro dominates US macro by **6–9×** for non-US stocks | same | V10 |
| Macro module architecture: **9 specialist analysts** working in parallel | `01-Product/Macro Intelligence Reports.md` | V10 |
| Macro report generation: **~4 minutes per market** | same | V10 |
| Macro coverage: **10 country markets + 1 global = 11 reports** (US, China, Germany, Japan, UK, Canada, France, India, Malaysia, Singapore + Global) | same | V10 |
| NLP detects texts predicting large cash-flow impairments / financial restatements — proprietary research shows it accurately predicts future stock crashes | `02-Methodology/Investment Factors.md` | V12 |
| Polaris fund live since **2019** (through COVID + 2022–23 inflation) | `Parallax Overview.md`, leave-behinds | Closer on any PM/CIO-audience video |

**Polaris one-liner** (use on any PM/CIO-audience video as a closer): *"This isn't a backtest. Polaris has been running on these scores since 2019."*

---

## Unverified claims — resolve before recording

These numbers and quotes appear in drafts but lack a confirmed source. Verify before any on-screen use. Where a claim originally tied to an archived video, the current-slate equivalent is noted.

- **"$6K–$24K/year"** pricing callout (originally tagged to the install video; current equivalent: **I1** instructional) — no vault source. Confirm with Chicago Global pricing before putting on screen.
- **Investor quotes** — Buffett 1962, Klarman 1995, Greenblatt, Marks. Originally tagged to an archived investor-profiles video that did not carry forward into the current slate. If reused in any V14–V16 hero playbook, source-check verbatim against primary letters/books — paraphrases are easy to screenshot and hard to retract.
- **"IC triples"** — confirm the white paper says "triples" vs "roughly 3×" or "approximately triples." Precision matters for sophisticated audiences. Eligible for integration into any video that surfaces the sub-score-agreement framing.
- **Codex CLI support** — vault commits to Claude / Gemini / Qwen. Codex is not explicitly verified. Get engineering confirmation before any instructional video (**I1** install / **I4** exports & integrations) names Codex as a supported client.

---

## Per-video specs — archived 2026-05-13

The 28-video capability-organized plan (Main Showcase V0–V12 + Niche N1–N14) was **archived to `_archive/MASTER-pre-overhaul-2026-05-11.md` on 2026-05-13** as part of Phase 8 of the persona-and-moment overhaul. That archive contains all 28 per-video specs in their original form, plus a mapping table showing how each legacy video maps to the new 20-video slate (most fold into new videos; some were dropped; V1 carries forward as the canary).

**The new 20-video plan lives at the bottom of this file** under the *NEW SLATE — Phase 3 Draft* section: 4 instructional (I1–I4) + 16 use_case (V1–V16) organized around `primary_persona × primary_moment × deliverable` rather than per-Parallax-command. See `overhaul.md` for the full rewrite history.

---

## Production Notes

### Demo Environment

- **Model:** Opus for maximum demo impact. Test each workflow on Sonnet to verify graceful degradation — Sonnet is what most clients actually use.
- **Platform:** Record on Claude Desktop (Cowork mode) for all use-case product demos — seamless plugin integration. The install / multi-client positioning content lives in the instructional set (I1).
- **Tickers:** Pre-test every ticker before recording. Use well-known names (AAPL, NVDA, KO, TSMC, JPM) for recognition. For non-US demos, verify RIC resolution works cleanly.
- **Portfolios:** Build 2–3 sample portfolios in advance via `discover_stocks` or `build_stock_universe`. A US-only portfolio, a mixed Asia portfolio, and one with deliberately weak holdings so health flags trigger.

### Per-video recording mechanics

(High-level pipeline lives in the *Production workflow* section near the top of this file. This subsection covers the recording-specific mechanics.)

1. **Pre-test the prompt.** Run the demo prompt in Parallax. Inspect the output. If sections are missing, phrasing is off, or numbers are weird, adjust the prompt and re-run. Record only when the output is presentation-quality. The video's locked recording inputs (ticker + prompt + pre-test checklist) are in its per-video spec.
2. **Single take.** Full-screen Claude Desktop, 1920×1080 at 60fps. No cuts in the source recording — conformation and zoom are applied in post via the pipeline tooling.
3. **Voice over from script.** The voiceover script is written against the locked beat windows + extracted frames at Phase 5. Tone: Bloomberg TV anchor, not corporate training video. The avatar talking-head clip is generated at Phase 10 (final render) — no separate ElevenLabs / TTS step is run by hand.
4. **Composition.** Title card + recording + outro are composited locally by the renderer; the avatar is overlaid as a picture-in-picture. There is no manual "edit & export" pass — the renderer reads the script's frontmatter and produces the final MP4.

### Recording Tips

- One workflow per video. Don't try to show everything in one take.
- Show parallel execution in real time — it's the visual differentiator.
- Frame around the client's question, not the tool name. The NL prompts in the Demo Script rows already do this.
- Processing time is part of the story: "screenshot to full investment memo in under 10 minutes" is a selling point.
- Any stat shown on screen must have a source in the vault stats library. If it's not there, add it there first — with the source — before recording.

### Customer's-chair framing — all use_case copy (Highlights, LTs, panels, VO)

Per `references/production-principles.md` → *Customer's-chair framing* (locked 2026-05-19). Every line of audience-facing copy in a `use_case` video — Highlights bullets, LT eyebrow / headline / stats, annotation panel fields, VO, title-card hook, YouTube title — speaks from the **buyer's** chair (MFO / RIA / advisor / PM / analyst per the video's `primary_persona`), never from the **system's** chair. No engineering vocabulary. No "eight parallel skill calls," "MCP tool invocations," "agent orchestration," or capability-counts. Every line is one of: **outcome** (what they get), **stakes** (what's on the line), **workflow-fit** (fits their day), or **methodology-credibility** (proof the answer holds up).

The recording itself can and should show parallel tool activity — that's the visual differentiator, per the Recording Tips above. But the *copy describing it* never names the mechanic. *"Twenty minutes of research, in one prompt"* (outcome) > *"Eight parallel skill calls"* (mechanic). The viewer sees activity in the chat sidebar and infers the speed; the copy doesn't need to count the activity for them.

Carve-out: `instructional` style (I1–I4) IS allowed to name system mechanics, because the audience for those is the technical operator setting up the plugin — *"Type `/parallax:stock AAPL` and confirm all eight skills fire"* is the right register for I1.

### What the Plugin Does NOT Have

- No dedicated morning-briefing command (assemble from macro + portfolio + news, or use watchlist mode).
- No corporate bond analysis — common objection, manage expectations.
- No DCF / intrinsic value calculator as a standalone workflow.
- No automated screenshot parsing — plugin expects structured holdings input.

---

*This is informational analysis based on Parallax factor scores, not investment advice. All outputs should be reviewed by qualified professionals before any investment decisions.*

---

# NEW SLATE — Phase 3 Draft (2026-05-13)

**Status:** ✅ locked 2026-05-13 (Phase 3 of the active overhaul). The 28-video legacy slate has been archived to `_archive/MASTER-pre-overhaul-2026-05-11.md` (Phase 8). The 20-video set below is the canonical plan going forward.

**Locked decisions (per `overhaul.md` Phase 1 + Phase 2):**

- **20 videos:** 4 instructional (I1-I4) + 6 Tier-1 single-feature (V1-V6) + 7 Tier-2 workflow-chain (V7-V13) + 3 Tier-3 hero (V14-V16). Numbering preserves V1 as the canary.
- **Persona-and-moment driven**, not capability-organized. Every use_case video anchors on `primary_persona × primary_moment × deliverable`.
- **Moment-anchored framing** (Principle #9 sibling): role labels never appear in VO copy; the situation phrase (`primary_moment`) carries the framing.
- **Natural-language prompts** (Principle #9): VO + on-screen demo use NL prompts; slash commands appear only as annotations.
- **20 videos cover all 11 flagship tools** (some as primary anchors, some as workflow sub-steps). Three intentional Tier-1 absences (`/rebalance`, `/scenario`, `/investor`) earn their screen time inside workflow chains.

---

### V1 — Stock Report  *(canary — being re-recorded under new framing)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `single_feature` (Tier 1) |
| **Duration target** | 90–110s |
| **Primary persona** | MFO / independent RIA / wealth advisor (Venise's RM Workflow Test is the canonical persona model) |
| **Secondary personas** | PM doing a pre-trade gut check; Analyst pulling a fast read for a PM ask (both translate without re-framing) |
| **Primary moment (in-VO)** | *"Client just texted about a holding. Ten minutes before your next meeting."* |
| **Tool** | `/parallax:stock` (LT module name: **Stock Report**) |
| **Deliverable** | Quick defensible read on the name — score panel, 52-week trajectory, bottom-line verdict |
| **Why it matters** | The moment where speed and defensibility both matter at once. A wrong answer to the client breaks trust; a slow answer makes you look unprepared. Parallax solves both: under 60 seconds, sourceable, score-defensible. |
| **Title-card headline (hook)** | *"Twenty minutes of research, in one sentence."* *(preserved from original V1 — standing brand hook)* |
| **Title-card eyebrow** | *"V1 · Quick Stock Research Brief"* |
| **YouTube title** | *"Quick Stock Research Brief"* |

**Highlights** — distinct output moments and value angles this video owns

*Per the 2026-05-21 "Vault stats integrate, not narrate" decision: Highlights name output moments and value angles, not vault-stat ownership claims. Vault stats integrate into VO lines only when load-bearing for problem-solving or why-can't-Claude framing — see the "Vault stats library (reference, not distribution)" section near the end of this file for available stats.*

- The *"client just texted, ten minutes before the meeting"* moment + the stakes (defensibility AND speed in the same window)
- *"Plain English in. Defensible brief out."* — the input-to-output framing line (revised 2026-05-19 from original *"Plain English in. Eight parallel calls out."* per Customer's-chair framing principle — engineering vocabulary in "parallel calls" replaced with audience-vocabulary "defensible brief")
- Score-to-recommendation map visible on screen (8.5+ STRONG BUY · 6.5–8.4 BUY · 3.5–6.4 HOLD · ≤3.4 SELL/STRONG SELL)
- Trajectory output moment: a name's composite score moving from 8.5 → 5.0 over 52 weeks while Quality pillar held at 10 — the "exceptional business at a rich multiple" framing (the canonical V1 recording — re-recorded 2026-05 — shows 8.5 → 5.0; the pre-overhaul April-era V1 recording was 8.7 → 5.9)
- Bottom Line output moment: 21% consensus upside + top-decile Quality + Tactical 10 + AI capex cycle context → defensible "Hold — case intact" verdict
- **Primary value angles** — *Moat headline:* **#12 Unverifiable frame** (the natural "vs eight Claude chats" comparison — eight LLM calls give eight reconciliation-failing answers; one Parallax call gives one reconciling answer). *Supporting:* **#1 Speed** · **#3 Defensibility** · **#7 Decision-readiness** · **#6 No black box** (score → factor → input chain visible).
- **"Why processing matters" beat** *(framework-consistency flavor)*: Parallax sub-processes reconcile because they all reference the same factor framework. Claude chats each invent their own methodology — they don't. The hard part isn't fan-out; it's framework consistency that lets the brief actually *integrate* rather than just stitch.
- **Vault stats that integrate** (per 2026-05-21 rule) — *13 years live* and *62k listings / 48 markets* are eligible for integration into specific output moments (the trajectory beat anchors "13 years of factor history"; the Value-row beat anchors "peer-ranked against AVGO, AMD, ARM and the broader sixty-two-thousand-listing universe"). *ICIR 4.10*, *Sharpe 2.34*, *+5.8%/yr selection return* do NOT integrate cleanly (require their own jargon explanation) and migrate to V9 Deep Dive / hero playbooks / out-of-slate surfaces.

**Beat sheet (target — to be re-locked against re-recorded source)**

- **Open (~14s, no zoom)** — Moment-setter VO: *"Client just texted about a holding. Ten minutes before your next meeting."* Cowork chrome visible; user types the NL prompt (*"Stock brief on NVDA — client query, need a defensible read on the position."* or similar). Tool activity fires visibly in the chat sidebar (parallel skill calls — visual differentiator, not narrated). **LT eyebrow:** *Stock Report*. **LT headline:** *"Twenty minutes of research, in one prompt."* (audience-perspective; revised 2026-05-19 from original *"Eight parallel skill calls. One natural-language prompt."* per Customer's-chair framing principle.)
- ~~**Vault stat (~12s, no zoom)** — ICIR 4.10 callout~~ — **REMOVED 2026-05-21** per "Vault stats integrate, not narrate" decision. Standalone credibility-ribbon beat dropped from V1; LT2 graphic dropped. The "13 years live" + "62k listings" stats that pass the integration test get folded into the processing-matters beat and the Value-row + trajectory hold beats (see V1 script frontmatter). ICIR 4.10 / Sharpe 2.34 / +5.8%/yr migrate to V9 Deep Dive (where they have room to be explained) or out-of-slate marketing.
- **Score panel + factor pillars (~16s, dwell:y — zoom on score table)** — Total Score + 5 factor pillars (Quality / Value / Momentum / Defensive / Tactical) on screen. VO names what to look at; doesn't read the numbers. *"Quality and Tactical pinned at ten. Momentum rolling. Value says it's expensive — and it is."*
- **Trajectory (~10s, dwell:y — zoom on 52-week trend paragraph)** — *"Eight-point-seven to five-point-nine over fifty-two weeks. Quality never moved."* (This is the "exceptional business at a rich multiple" reveal.)
- **Silent scrolldown (~6s, no VO)** — viewer reads Financial Health / Macro / Dividends / Risk / News / Analyst View on screen. These beats are owned by V2 (Deep Dive) / V6 (Macro) / V8 (PM IC) — not re-litigated here. Per Principle #3 (series overlap), defer to other videos.
- **Bottom line (~4s, dwell:y — zoom on Bottom Line section)** — verdict beat. *"Exceptional business at a rich multiple. Factor score cooling. Hold — don't add."* (or similar; depends on ticker chosen for re-record)
- **Closer (~3s, no zoom)** — *"Plain English in. Defensible brief out. In your client's hand before the meeting starts."* Outro tagline: *"Solve the market."* (standard — RM moment doesn't earn the Polaris closer). (Revised 2026-05-19 from *"Plain English in. Eight parallel calls out. Defensible read..."* per Customer's-chair framing — the middle clause was engineering vocabulary.)

**Tool chain** (single tool, multiple sub-calls visible)

`/parallax:stock` fan-outs eight underlying MCP tools in parallel:
- `get_company_info` — overview
- `get_score_analysis` (52w) — Total Score + 5 factor pillars (Quality / Value / Momentum / Defensive / Tactical) trajectory over 52 weeks
- `get_financials` (summary) — revenue and income trends
- `get_stock_outlook` × 4 aspects — analyst price targets, buy/hold/sell recommendations, risk/return vs peers, dividend history
- `get_news_synthesis` — recent catalysts (async, doesn't block output)
- `get_peer_snapshot` — factor scores + peer ranking
- `macro_analyst` × 1-2 countries (component=tactical) — home market + revenue geography
- `explain_methodology` — called for any unusually high or low factor score (free, 0 tokens)

*Note: `get_technical_analysis` and `get_financial_analysis` are NOT in `/parallax:stock`'s fan-out — they live in `/parallax:deep-dive` (V9) per the workflow reference doc.*

All eight visible in the chat as parallel work — this IS the "eight parallel calls" framing the VO names.

**Format invariants**

- Template: `templates/product-demo/index.html` (PiP layout — small avatar overlay, Cowork recording fills frame)
- 60fps, 1920×1080
- LTs use product-module name in eyebrow ("Stock Report"), persona-moment language in headline
- Three dwell:y beats need pause-zoom segments via `tools/zoom.py` — score panel, trajectory, bottom line
- Annotate highlights on key labels: Score / 52-Week Trajectory / Bottom Line (calibrate via `tools/measure_highlight.py`)
- Outro: standard tagline `"Solve the market."` (not Polaris closer — wrong audience)

**Recording plan (Phase 7)**

- Re-record under new framing: typed NL prompt opens (*"Quick read on \<ticker\>?"* or similar — match the "client question" register)
- Archive current `screen recordings/V1/1vid*.mp4` to `screen recordings/V1/_archive/v1-original-2026-04-*.mp4`
- Run scrub → zoom → extract_frames → measure_highlight pipeline on new recording
- Re-time beat sheet locked targets against the re-recorded source
- Re-author `scripts/V1 voiceover script.md` (archive current to `scripts/_archive/V1-original-2026-04-29.md`)
- Preview render free; final render gates on HeyGen wallet top-up (~$15)


**Recording inputs (locked)**

- **Input:** `NVDA`  *(high-recognition large-cap, widely held in client books — matches the "client texted about a holding" moment)*
- **Prompt to type:**
  > Stock brief on NVDA — client query, need a defensible read on the position.
- **Pre-test checklist:**
  - ☐ Eight parallel calls fire visibly in the chat
  - ☐ Score panel renders with Total Score + five factor pillars (Quality / Value / Momentum / Defensive / Tactical)
  - ☐ 52-week trajectory chart visible
  - ☐ Vault stats (ICIR 4.10, +5.8%/yr selection return, 13 years, 62,000+ listings, 48 markets) appear inline
  - ☐ Bottom-line verdict section present
- **Scrub params:** `python tools/scrub.py "screen recordings/V1/1vid.mp4" --cursor-aware --cursor-pixel-threshold 60 --cursor-min-px 40 --cursor-max-px 600 --force-uniform-starts "7.2" --min-speed-range "7.2:193.8:2.0" --drop-ranges "192:195.5"`
  - Uses the new (2026-05-18) scrub-time threshold defaults: `--cut-threshold-scrub 4.0` (cut if freeze produces >4s scrub) and `--anchor-seconds-scrub 1.5` (anchor cut = 3s scrub output = 1.5s front + 1.5s back). Both adapt to per-freeze effective playback speed.
  - `--cursor-aware` samples each freeze internally at 4 fps for cursor-sized localized motion.
  - `--force-uniform-starts "7.2"` overrides the 22.5s sub-freeze (raw 7.2–29.7) that had slow cursor drift.
  - `--min-speed-range "7.2:193.8:2.0"` floors loading-range speed at 2×.
  - `--drop-ranges "192:195.5"` cuts 3.5s of dead time between brief-complete and the user's first scroll. Both sides land on identical "5 of 5 + cursor at (310, 368)" state.
  - Output: 60.15s scrubbed (5 anchor cuts × 3s scrub each).

---

### I1 — Install Parallax

| Field | Details |
|---|---|
| **Style** | `instructional` |
| **Complexity** | `utility` (Tier 0) |
| **Duration target** | 60–90s |
| **Audience** | audience-general (any new Parallax user / buyer evaluator) |
| **Pipeline element shown** | install across the 4 supported AI clients |
| **Deliverable** | viewer can install Parallax on their preferred client and verify with a sanity-check NL prompt |
| **Why it matters** | foundational gate for every other Parallax workflow. Cross-client portability (4 clients, NL-prompt-universal) is itself a selling point that distinguishes Parallax from Bloomberg-style proprietary terminals. |
| **Title-card headline (hook)** | *"Five minutes. Any AI client."* |
| **Title-card eyebrow** | *"I1 · Installing Parallax"* |
| **YouTube title** | *"How to Install Parallax in Any AI Client (Claude Code, Desktop, Codex, Qwen)"* |

**Highlights** — distinct points this video owns

- The 4 supported clients: **Claude Code** (full plugin: 10 slash commands + 7 skills + .mcp.json), **Claude Desktop** / **Codex CLI** / **Qwen CLI** (raw MCP tools only, no slash commands)
- **NL prompt is the universal sanity check** — works in all 4 clients (per `V0 Install Research — 4 Clients.md`). Per Principle #9, slash commands only available in Claude Code; demo shows the NL prompt as the cross-client common ground.
- The plugin install path (Claude Code: `claude plugin install`) vs the raw-MCP install path (Desktop/Codex/Qwen: `claude mcp add-json` or equivalent)
- Value-framing (hook + close only per instructional carve-out): **#8 Workflow-native** ("meets you in your existing AI client") + **#1 Speed** ("five minutes, you're running briefs")

**Beat sheet (target)**

- **Open hook (~8s)** — *"If you're new to Parallax, here's the install. Five minutes, any AI client."*
- **Per-client click sequence (~45s)** — quad-split or sequenced: Claude Code (plugin install) → Claude Desktop (raw MCP add) → Codex CLI → Qwen CLI. Voiceover describes each click literally; no interpretation overlay.
- **Sanity check beat (~12s)** — same NL prompt typed into all 4: *"Run a quick brief on NVIDIA using Parallax."* Response renders in each → installation verified.
- **Close (~5s)** — *"Pick a client. Run an NL prompt. You're in."* Outro tagline: *"Solve the market."*

**Recording requirements**

- Screen recording of install across all 4 clients — quad-split layout preferred, or 4 sequential cuts
- Voiceover describes clicks literally; instructional style (no "imagine never opening Bloomberg again"-style interpretation mid-flow)
- **Slash commands MAY appear typed on screen for Claude Code** (instructional carve-out from Principle #9); the other 3 clients use NL prompts only
- No persona pretense — audience-general

**Format invariants**

- Template: `templates/product-demo/index.html` (no separate instructional template yet — use product-demo with minimal LT styling)
- 60fps, 1920×1080
- LT eyebrow optional; no LT headlines mid-flow (instructional doesn't interrupt the click sequence)
- No dwell:y zooms (instructional flow is sequential, not interpretation-heavy)
- Outro tagline: standard `"Solve the market."`

**Carry-over from old V0:** the old MASTER had this as "Video 0: Installing the Parallax MCP — Five Minutes, Any Client" (lines 90-119). `V0 Install Research — 4 Clients.md` is canonical research for this video's content; reuse it.


**Recording inputs (locked)**

- **Input:** NVIDIA — typed verbatim into each of the four supported AI clients as the cross-client sanity check.
- **Prompt to type (same prompt into Claude Code, Claude Desktop, Codex CLI, Qwen CLI):**
  > Run a quick brief on NVIDIA using Parallax.
- **Pre-test checklist:**
  - ☐ Prompt produces a clean response in all four AI clients (no install errors, no MCP-binding failures)
  - ☐ The brief renders end-to-end with score panel + factor pillars visible
  - ☐ Cross-client behaviour matches (same prompt → semantically equivalent response across the four)

---

### I2 — First Brief in 60 Seconds

| Field | Details |
|---|---|
| **Style** | `instructional` |
| **Complexity** | `utility` (Tier 0) |
| **Duration target** | 60–90s |
| **Audience** | audience-general (just-installed user, evaluating the product) |
| **Pipeline element shown** | from zero → first Parallax output |
| **Deliverable** | viewer types one NL prompt and sees a real Parallax brief render — "this thing works" validation |
| **Why it matters** | the 60-second moment of conviction: "I just typed a question and got an institutional-grade analyst brief." Many SaaS trials lose users in the first 5 minutes; this video collapses that to one prompt. |
| **Title-card headline (hook)** | *"One prompt. One full brief. Sixty seconds."* |
| **Title-card eyebrow** | *"I2 · First Brief in 60 Seconds"* |
| **YouTube title** | *"Your First Stock Research Brief in 60 Seconds"* |

**Highlights** — distinct points this video owns

- **One NL prompt → full Parallax brief**, no setup beyond install
- Time-stamped: under 60 seconds from prompt to rendered brief
- Real output shown (no mock data) — score panel, factor pillars, trajectory, bottom line
- Value-framing (hook + close only): **#1 Speed** ("twenty minutes of Bloomberg → sixty seconds") + **#7 Decision-readiness** ("brief is ready to use, not just ready to read")

**Beat sheet (target)**

- **Open hook (~7s)** — *"You just installed Parallax. Sixty seconds to your first brief."*
- **NL prompt typed (~10s)** — user types: *"Run a quick brief on Microsoft."* The prompt is the entire user input — no slash command, no config flags. (Demonstrates Principle #9 in its purest form.)
- **Brief renders (~35s, no zoom)** — parallel calls fire visibly → score panel, factor pillars, trajectory, financial health, bottom line scroll into view. Voiceover names what's on screen as it appears (instructional sequencing).
- **Close (~5s)** — *"One prompt. Sixty seconds. That's Parallax."* Outro tagline: *"Solve the market."*

**Recording requirements**

- Single-take screen recording, real network (not pre-rendered) — the timing IS the demo
- Voiceover paces *with* the render, describing what appears as it appears
- No interruption beats, no zoom segments — single continuous flow

**Format invariants**

- Same as I1 (product-demo template, 60fps, no dwell:y zooms, standard outro)
- LT eyebrow may name *Stock Report* briefly when the brief renders


**Recording inputs (locked)**

- **Input:** Microsoft
- **Prompt to type:**
  > Run a quick brief on Microsoft.
- **Pre-test checklist:**
  - ☐ Brief renders end-to-end in under 60 seconds
  - ☐ Parallel calls fire visibly in the chat
  - ☐ Score panel + factor pillars + 52-week trajectory + financial health + bottom line all populate
  - ☐ No errors, no missing sections

---

### I3 — Free Tier Walkthrough

| Field | Details |
|---|---|
| **Style** | `instructional` |
| **Complexity** | `utility` (Tier 0) |
| **Duration target** | 60–90s |
| **Audience** | audience-general (prospect evaluating before paying for API credits) |
| **Pipeline element shown** | what Parallax can do at zero cost — methodology lookup, plugin info, free MCP tools |
| **Deliverable** | viewer understands the free surface area + sees the upgrade path |
| **Why it matters** | removes the "pay before seeing value" objection. Free tier is a real product surface — methodology drawer, basic queries, plugin docs. Buyer can validate fit without commitment. |
| **Title-card headline (hook)** | *"Try the methodology before you pay."* |
| **Title-card eyebrow** | *"I3 · Free Tier Walkthrough"* |
| **YouTube title** | *"What Parallax Does on the Free Tier (No API Key Needed)"* |

**Highlights** — distinct points this video owns

- The free MCP tools: `get_docs`, `list_docs`, `explain_methodology` (Methodology drawer), `check_api_health`, `submit_feedback`
- What's gated (requires API key): factor scoring, deep-dive parallel calls, scenario analysis, anything calling Chicago Global's compute
- Value-framing (hook + close only): **#6 No black box** ("see the methodology before you pay") + **#1 Speed** ("free tier query in seconds")

**Beat sheet (target)**

- **Open hook (~7s)** — *"Curious about Parallax before you pay? Here's what the free tier does."*
- **Free-tier query examples (~50s)** — viewer sees: methodology lookup (factor framework definitions), plugin info (`list_docs`), API health check. Each query is one NL prompt; voiceover describes what's happening.
- **Upgrade transition (~10s)** — *"When you're ready for live scoring, deep dives, scenario work — that's the API key."* Brief shot of the upgrade flow.
- **Close (~5s)** — *"Free tier first. Upgrade when the methodology checks out."* Outro tagline: *"Solve the market."*

**Recording requirements**

- Same as I1/I2 (single recording, NL prompts only, sequential narration)
- Methodology drawer beat is the visual hero — the *"no black box"* moment lives here

**Format invariants**

- Same as I1/I2 (product-demo template, 60fps, no dwell:y zooms)
- LT eyebrow may name *Methodology* during the methodology beat

**Carry-over from old N12:** old MASTER had this as "Video N12: The Free Tier — Zero Tokens" (lines 899-928). Content rolls forward; reuse the framing.


**Recording inputs (locked)**

- **Inputs:** three example free-tier queries (exact phrasing chosen at recording time; suggested defaults below)
- **Prompts to type (in sequence):**
  > Explain the Parallax factor framework — what are the six factor pillars and how is each scored?

  > List the available Parallax methodology documents and plugin reference docs.

  > Check Parallax API health — is the live scoring service reachable?
- **Pre-test checklist:**
  - ☐ All three queries return responses on the free tier (no API key required)
  - ☐ Methodology response includes the six pillar definitions cleanly
  - ☐ Docs list renders with usable references
  - ☐ API health check returns a clear status indicator

---

### I4 — Exports & Integrations

| Field | Details |
|---|---|
| **Style** | `instructional` |
| **Complexity** | `utility` (Tier 0) |
| **Duration target** | 90–120s (slightly longer — covers two distinct export paths) |
| **Audience** | audience-general (existing or prospective user with downstream workflows in Excel / PowerPoint / shared docs) |
| **Pipeline element shown** | PDF report generation + CSV export — bridging Parallax output to existing tools |
| **Deliverable** | viewer can export a brief / portfolio analysis / peer comparison to PDF or CSV and use it in their existing stack |
| **Why it matters** | Parallax doesn't replace Excel or the client memo — it feeds them. Buyer eval often hinges on "can I get the output into my existing workflow?" Yes. |
| **Title-card headline (hook)** | *"Brief in your client. Output in your tools."* |
| **Title-card eyebrow** | *"I4 · Reports & Exports"* |
| **YouTube title** | *"Export Stock Research to PDF and Excel"* |

**Highlights** — distinct points this video owns

- PDF report path (`get_stock_report` with format=PDF, or `--format pdf` on relevant commands) — async render with job ID; downloadable artifact
- CSV path (`export_peer_comparison`, `export_price_series`) — spreadsheet-ready, named columns, no post-processing
- "Bridge to existing tools" framing — Parallax as the engine, Excel/PowerPoint as the surface the team already lives in
- Value-framing (hook + close only): **#7 Decision-readiness** ("drops straight into your memo, no rewriting") + **#8 Workflow-native** ("meets your stack where it is")

**Beat sheet (target)**

- **Open hook (~10s)** — *"Parallax answers in your AI client. But the memo, the deck, the spreadsheet — they're elsewhere. Here's how to bridge."*
- **PDF beat (~40s)** — NL prompt: *"Generate a PDF research report on NVIDIA."* → job ID → render kicks off → PDF download → quick flip through the artifact (it's branded, structured, drops into a client folder as-is).
- **CSV beat (~35s)** — NL prompt: *"Export peer comparison for NVIDIA to CSV."* → CSV opens in Excel/Numbers → columns named correctly, ready to pivot/sort.
- **Close (~10s)** — *"Brief in your client. Output in your tools. Solve the market."*

**Recording requirements**

- Single recording but with two distinct flows (PDF then CSV); could split-screen if the timing's tight
- Show the actual artifact (PDF opened, CSV in spreadsheet) — the artifact IS the proof
- Voiceover narrates each step literally; instructional sequencing

**Format invariants**

- Same as I1/I2/I3 (product-demo template, 60fps, no dwell:y zooms, standard outro)
- May benefit from a single LT eyebrow naming each export type as it appears (*PDF Report* / *CSV Export*)

**Carry-over from old N7 + N11:** consolidates "Video N7: Export to CSV — Bridging to Excel" (lines 758-784) and "Video N11: PDF Research Report Generation" (lines 870-897) into one bridge-to-existing-tools demo. Both are short enough to share a video; the consolidation tightens the catalogue without losing content.


**Recording inputs (locked)**

- **Input:** NVIDIA
- **Prompts to type (sequential — PDF first, then CSV):**
  > Generate a PDF research report on NVIDIA.

  > Export peer comparison for NVIDIA to CSV.
- **Pre-test checklist:**
  - ☐ PDF generation kicks off (job ID returned); render completes; download link works
  - ☐ PDF renders cleanly when opened (branded layout, no broken sections)
  - ☐ CSV export downloads and opens in Excel/Numbers
  - ☐ CSV columns are named correctly and rows are pivot-ready

---

### V2 — Stock Report  *(PM pre-trade variant)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `single_feature` (Tier 1) |
| **Duration target** | 75–95s |
| **Primary persona** | Portfolio Manager (discretionary fund / family-office capital) |
| **Secondary personas** | Head of research (validates the same checks) · CIO-as-practitioner (runs this themselves at small shops) |
| **Primary moment (in-VO)** | *"Name on the candidate list. Score check before the trade."* |
| **Tool** | `/parallax:stock` (LT module name: **Stock Report**, score + trajectory cut) |
| **Deliverable** | Total Score + 5 factor pillars (Quality / Value / Momentum / Defensive / Tactical) + 52-week trajectory + go/no-go read in under a minute |
| **Why it matters** | Pre-trade decision moment. PM has a thesis; needs the *quant spine* (Parallax's role per its own self-assessment) to defend the position-sizing call. Score-checking before a trade is the single most-repeated PM workflow. |
| **Title-card headline (hook)** | *"Before the trade, the score."* |
| **Title-card eyebrow** | *"V2 · Pre-Trade Stock Check"* |
| **YouTube title** | *"Pre-Trade Stock Score Check (Score + Factor Pillars + 52-Week Trajectory)"* |

**Highlights** — distinct points this video owns

- The *"candidate list, before the trade"* moment + the go/no-go stakes
- Score panel as the visual hero: Total Score + 5 factor pillars (Quality / Value / Momentum / Defensive / Tactical — the five canonical Parallax pillars)
- 52-week trajectory beat — the *"score ran 8.7 → 5.9, Quality never moved"* pattern (re-anchored to a fresh ticker for this video)
- *"Defensible quantitative spine"* framing — explicit nod to what Parallax IS and what it ISN'T (factor engine, not a thesis-tree tool — direct from plugin self-assessment)
- **Primary value angles** — *Moat headline:* **#5 Determinism** (re-run tomorrow, same score — that's what makes pre-trade score-checking trustworthy). *Supporting:* **#3 Defensibility** · **#6 No black box** (drill into the pillar that's driving the call) · **#1 Speed** · **#7 Decision-readiness**.

**Beat sheet (LOCKED 2026-05-22 against `screen recordings/V2/vid2.mp4`)**

Target seconds reflect *post-zoom* length for dwell:y beats (Phase 5.5 zoom inserts fill the dwell windows). Scrubbed (pre-zoom) recording target = sum of non-dwell beats + raw pre-zoom portion of dwell beats.

| # | Beat | Target | Dwell | Content |
|---|---|---|---|---|
| 1 | Open — NL prompt typed | 10s | n | Cowork chrome, user types: *"Stock brief on AAPL. Evaluating for position add — composite score, factor pillars, 52-week trajectory."* |
| 2 | Score panel reveal | 18s | **y** | Total Score + 5 factor pillars on screen. VO interprets the pillar values. Zoom: Total Score + 5 pillars block. |
| 3 | Trajectory beat | 15s | **y** | 52-week score-over-time chart. VO names the directionality story. Zoom: trajectory chart. |
| 4 | Determinism flex | 10s | n | VO names the #5 Determinism moat ("re-run tomorrow, same score"). No zoom — held on a stable screen state. |
| 5 | Bottom line | 8s | **y** | Verdict beat (Add / Wait based on AAPL's actual score). Zoom: Bottom Line section. |
| 6 | Closer | 4s | n | *"Pre-trade score check. Sixty seconds, before you commit."* |

**Recording target (post-zoom):** 65s. Plus title (5s) + outro (7s) → 77s composition runtime, sits cleanly in the 75–95s duration target.

**Recording target (pre-zoom / scrubbed):** ~36–42s (24s non-dwell + ~4s/dwell-beat raw source × 3 dwell beats). Phase 3 scrub aims for this; Phase 5.5 zoom inflates to the locked 65s.

**Tool chain**

Same fan-out as V1 since both use `/parallax:stock` — eight underlying MCP tools in parallel. But this video focuses the VO on **score + pillars + trajectory** (skipping the financial-health / macro / news beats that V1's "client question" framing emphasized). On-screen output is identical; the *interpretation* is what differs.

**Recording requirements**

- Pick a ticker whose score-and-trajectory story is *trade-decision-shaped* (clear directionality, defensible pillar reading). NOT NVIDIA again — that's V1's ticker.
- NL prompt typed verbatim in Cowork chrome — match the *"considering adding"* register
- Three dwell:y beats need pause-zoom segments (score panel, trajectory, bottom line) — same zoom template as V1
- 60fps, 1920×1080
- No persona pretense — the on-screen text is general; the persona-and-moment lives in the VO

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow: *Stock Report* (recurring across V1/V2/V3 since all three use this tool)
- LT headline at score-panel beat could read: *"Quality 10 · Tactical 9 · Momentum 7 · Value 3"* (factor-pillar callout — re-anchored to the chosen ticker)
- Outro tagline: standard `"Solve the market."` (PM moment, but doesn't earn Polaris closer — single-tool video doesn't carry the methodology-proof flex)


**Recording inputs (locked)**

- **Input:** `AAPL`  *(Quality + Tactical typically high, Value typically saying "expensive" — supports the "score's cooling" or "score supports the size" beat cleanly)*
- **Prompt to type:**
  > Stock brief on AAPL. Evaluating for position add — composite score, factor pillars, 52-week trajectory.
- **Pre-test checklist:**
  - ☐ Total Score + five factor pillars render with at-a-glance interpretation
  - ☐ Score-over-time chart shows a clear directional story across 52 weeks
  - ☐ Determinism beat: re-run the prompt — confirm score is byte-identical
  - ☐ Verdict line is unambiguous (Add / Wait)

---

### V3 — Stock Report  *(Analyst peer-snapshot variant)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `single_feature` (Tier 1) |
| **Duration target** | 75–95s |
| **Primary persona** | Financial analyst (sell-side coverage / buy-side support) |
| **Secondary personas** | Head of research (signing off the brief) · PM (consuming the peer table) |
| **Primary moment (in-VO)** | *"Peer snapshot for the brief. Before it goes out."* |
| **Tool** | `/parallax:stock` (LT module name: **Stock Report**, peer-snapshot cut) |
| **Deliverable** | Peer-comparison table — factor scores, valuation multiples, momentum, financial health across the comp set — drops straight into the brief |
| **Why it matters** | The analyst's ad-hoc *"need a fast peer read"* moment. Building a comp table by hand takes 30+ minutes (Bloomberg pulls, manual reconciliation across feeds). Parallax produces it cite-able and consistent in under a minute. Saves the analyst's evening. |
| **Title-card headline (hook)** | *"The comp table, in one prompt."* |
| **Title-card eyebrow** | *"V3 · Peer Snapshot Research"* |
| **YouTube title** | *"Stock Peer Comparison for Analyst Briefs"* |

**Highlights** — distinct points this video owns

- The *"brief due, peer table missing"* moment + the analyst-evening stakes
- Peer-snapshot table as the visual hero: tickers × factor pillars × valuation × momentum, side-by-side
- *"Consistent methodology across all comps"* framing — same factor framework applied to every peer, so the table actually integrates (Bloomberg pulls don't — different vendors, different reconciliations)
- Drop-into-brief workflow visible at the close (copy-to-clipboard or CSV export)
- **Primary value angles** — *Moat headline:* none (this is a productivity-anchored video, not a moat showcase). *Standard angles:* **#1 Speed** (30 min → 60s) · **#2 Coverage / scale** (every peer scored against same framework, not just top 3) · **#7 Decision-readiness** (drops into the brief) · **#3 Defensibility**.

**Beat sheet (target)**

- **Open (~10s, no zoom)** — Moment-setter VO. NL prompt: *"Peer snapshot on [TICKER] for sector brief — comp set, factor scores, valuation deltas."*
- **Peer table populates (~30s, dwell:y — zoom on table)** — table fills column-by-column or row-by-row. VO names what's striking: *"Quality leader of the group. Two cheapest on Value. The momentum split tells you who the market's already crowded into."*
- **Consistency flex (~12s, no zoom)** — VO names the framework-consistency moat: *"Same six pillars on every name. Same definitions. Same data feeds. The table actually integrates instead of just being stitched."*
- **Drop-into-brief beat (~8s, no zoom)** — visual of copy/export to the analyst's document
- **Closer (~5s, no zoom)** — *"Peer table. One prompt. Sixty seconds. Ready for the brief."*

**Tool chain**

`/parallax:stock` with peer-snapshot focus — emphasizes `get_peer_snapshot` + `export_peer_comparison` (the export sub-call). The full eight parallel calls still fire under the hood; the VO + LT center on the peer view.

**Recording requirements**

- Pick a stock with a *real, named* peer set (5-7 names) — preferably in a sector where peer comparison is genuinely informative (semis, banks, consumer staples, etc.)
- Show the peer table visibly populating — the *table forming on screen* is the visual hero
- One dwell:y beat (peer-table zoom + factor-column highlight via `tools/measure_highlight.py`)
- 60fps, 1920×1080

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow: *Stock Report* or *Peer Snapshot*
- Outro: standard `"Solve the market."`


**Recording inputs (locked)**

- **Input:** `JPM`  *(banking sector — clean peer set: BAC, WFC, C, GS, MS, USB; framework-consistency claim has a recognizable comp universe)*
- **Prompt to type:**
  > Peer snapshot on JPM for sector brief — comp set, factor scores, valuation deltas.
- **Pre-test checklist:**
  - ☐ Peer table populates with at least four comparable names
  - ☐ Each peer shows factor scores + valuation multiples + momentum + financial health columns
  - ☐ Framework-consistency claim holds: same six pillars on every peer
  - ☐ Table is copy-paste-ready for a brief

---

### V4 — Shariah Screen

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `single_feature` (Tier 1) |
| **Duration target** | 80–100s |
| **Primary persona** | Compliance officer (trade/portfolio compliance — Islamic finance / Shariah-mandate sub-specialty) |
| **Secondary personas** | RM at an Islamic-finance-aware wealth advisor · PM at a Shariah-compliant fund · the analyst tasked with prepping the sign-off packet |
| **Primary moment (in-VO)** | *"Shariah-mandate name. Sign-off before close."* ⓟ |
| **Tool** | `/parallax:screen` Shariah mode (LT module name: **Shariah Screen**) |
| **Deliverable** | AAOIFI pass/fail verdict + purification ratio + business-screen breakdown (revenue from non-compliant activities) + financial-screen breakdown (interest-bearing debt, etc.) |
| **Why it matters** | Shariah screening is a *regulatory* requirement for Islamic-finance products. Manual screening is a spreadsheet/checklist slog that takes hours per name. Parallax produces an AAOIFI-aligned verdict + the exact purification ratio + the underlying evidence trail in under 30 seconds. Direct hit on **moat #4 Auditability** for compliance audiences. Real prospect-mapped target: People's Partnership (UK, £40B+ AUM, Shariah fund), Wahed, MAS Shariah-AI grant work. |
| **Title-card headline (hook)** | *"AAOIFI-compliant screening, in seconds."* |
| **Title-card eyebrow** | *"V4 · Shariah Compliance Screening"* |
| **YouTube title** | *"Shariah-Compliant Stock Screening (AAOIFI Halal Verdict + Purification Ratio)"* |

**Highlights** — distinct points this video owns

- AAOIFI methodology referenced explicitly (the standard recognized by compliance officers globally)
- Purification ratio displayed as the headline output — the specific calculation Shariah investors need
- Business screen + financial screen broken out separately (visible, not blackbox)
- *"Manual: hours. Parallax: seconds."* productivity framing
- **Primary value angles** — *Moat headline:* **#4 Auditability** (every component of the verdict — revenue mix source, debt ratio source, etc. — has a paper trail; regulators accept this). *Supporting:* **#6 No black box** (drill into any screen rule and see why) · **#1 Speed** · **#3 Defensibility** (peer-reviewed methodology, not a partner can pick apart in committee).

**Beat sheet (target)**

- **Open (~10s, no zoom)** — Moment-setter VO (persona-locked language — "Shariah" is the role's vocabulary). NL prompt: *"Run AAOIFI Shariah compliance screen on [TICKER]. Need pass/fail verdict with purification ratio."*
- **Verdict reveals (~12s, dwell:y — zoom on verdict block)** — Pass / Fail / Conditional verdict + the headline ratios. *"Business screen: passes. Financial screen: passes. Purification ratio: [X]%."*
- **Drill-down (~25s, dwell:y — zoom on business + financial screen breakdowns)** — VO walks the components: *"Revenue from non-compliant activities: [X]%, under the 5% threshold. Interest-bearing debt to market cap: [Y]%, under the 33% threshold."* This is the visible-evidence-chain beat.
- **Auditability flex (~12s, no zoom)** — VO names the moat: *"Every component cites a source. Every threshold cites a standard. Regulators recognize the methodology. The audit is signed in one pass, not twenty."*
- **Closer (~6s, no zoom)** — *"Shariah-compliant. AAOIFI-aligned. Sign-off ready."* Outro tagline: standard.

**Tool chain**

`/parallax:screen` in Shariah mode — invokes the AAOIFI rule engine on top of the company's financials. Sub-calls visible: business-screen calc, financial-screen calc, purification-ratio calc, source citations (filing references for the underlying data).

**Recording requirements**

- Pick a real well-known stock where the verdict is *informative* — either a clear pass (a name compliance audiences would expect to pass) OR a borderline conditional case (more visually interesting). NOT something obviously non-compliant (alcohol / banking / etc. — those waste the demo on a foregone conclusion).
- Two dwell:y beats (verdict block, screen-breakdown table)
- Show the AAOIFI threshold values on screen at the drill-down beat — *the specific numbers are the credibility flex*
- 60fps, 1920×1080

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow: *Shariah Screen*
- LT headline at auditability beat could read: *"Every component traces to source"* or similar — the audit-trail visualization
- Outro: standard `"Solve the market."`


**Recording inputs (locked)**

- **Input:** `AAPL`  *(typical clean AAOIFI Pass — low debt, low interest income, no haram revenue streams; demonstrates the clean-pass evidence trail)*
- **Prompt to type:**
  > Run AAOIFI Shariah compliance screen on AAPL. Need pass/fail verdict with purification ratio.
- **Pre-test checklist:**
  - ☐ Pass / Fail / Conditional verdict renders prominently
  - ☐ Purification ratio displayed as a specific number
  - ☐ Business-screen breakdown visible (no haram revenue exposure)
  - ☐ Financial-screen breakdown visible (debt / total assets, interest income / total revenue, with thresholds named)
  - ☐ Every threshold cites a source (AAOIFI standard)

---

### V5 — ETF Analysis  *(Look-Through)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `single_feature` (Tier 1) |
| **Duration target** | 80–100s |
| **Primary persona** | Family-office analyst (single or multi-family office) — equity-side exposure read |
| **Secondary personas** | RM at a wealth advisor whose UHNW client holds ETF-heavy positions · PM doing a hidden-overlap check on a fund-of-ETF book |
| **Primary moment (in-VO)** | *"Half the equity portion is held through ETFs. What are they actually long underneath?"* |
| **Tool** | `/parallax:portfolio` with ETF look-through (LT module name: **ETF Analysis** — the look-through capability inside Analyzer) |
| **Deliverable** | True per-name equity exposure across an ETF-heavy book — compound concentration revealed, underlying factor profile, sector/geo exposure that the ETF layer was hiding |
| **Why it matters** | FOAs / RMs handling families with ETF-heavy equity portfolios literally don't know what their client owns — the ETF ticker hides the underlying holdings. Two ETFs that *look* diversified can both be 30% in the same five names. Parallax's look-through reveals the actual exposure in one query. This is the *honest narrowing* of the FOA video (no illiquids — Parallax's limit), but the equity look-through is genuinely a strong fit. |
| **Title-card headline (hook)** | *"Through the ETFs. To the underlying."* |
| **Title-card eyebrow** | *"V5 · ETF Look-Through Analysis"* |
| **YouTube title** | *"ETF Look-Through Analysis: What's Really in Your Portfolio"* |

**Highlights** — distinct points this video owns

- The *"two ETFs, same hidden bets"* reveal — visual hero is the compound-concentration moment
- True per-name exposure shown alongside the ETF-ticker view — side-by-side reframing
- Factor profile of the *underlying* (Quality / Value / Momentum etc.) — what the client actually owns vs what the ticker suggests
- Sector / geographic exposure of the underlying — frequently very different from what the ETF name implies
- **Primary value angles** — *Moat headline:* none (productivity + insight-anchored, not a moat showcase). *Standard angles:* **#2 Coverage / scale** (every ETF in the book gets looked through, not just the top one) · **#6 No black box** (see the actual holdings, not the ETF wrapper) · **#7 Decision-readiness** (factor + concentration read drops into a one-page principal update) · **#3 Defensibility** (the look-through reveal is defensible to the principal — sourced numbers, not gut interpretation) · **#8 Workflow-native** (FOA stack is Excel + DDQ + ad-hoc; Parallax slots in via the AI client they already use).

**Beat sheet (target)**

- **Open (~12s, no zoom)** — Moment-setter VO. Cowork chrome, NL prompt: *"Portfolio analysis with ETF look-through enabled — flag compound concentration, surface true per-name exposure."* Portfolio CSV / holdings table visible.
- **Surface view (~10s, no zoom)** — VO acknowledges what you see at the wrapper level: *"At the ticker level, it looks diversified — six ETFs across six sectors."*
- **Look-through reveals (~30s, dwell:y — zoom on underlying-holdings overlap reveal)** — the table flips to per-name underlying. VO reveals: *"Two of these ETFs overlap forty-percent on the same fifteen names. Your real top-five exposure is three names, not six."*
- **Factor profile beat (~15s, dwell:y — zoom on aggregated factor pillars)** — true factor exposure of the underlying. *"Looks balanced; isn't. Quality skew but a heavy Momentum tilt — that's the regime risk you didn't price."*
- **Closer (~6s, no zoom)** — *"ETF wrapper out. Real exposure in."* Outro tagline: standard.

**Tool chain**

`/parallax:portfolio` auto-routes to `analyze_mixed_portfolio` (not `analyze_portfolio`) when ETFs are detected in the holdings — same cost, but the routing expands the ETFs to their underlying holdings so factor exposure reflects the *real* positions. The user-facing slash command stays `/parallax:portfolio`; the routing is internal. Sub-calls fired: `etf_holdings` on each ETF position → aggregation of underlying-name exposures → portfolio factor analysis on the consolidated equity book. Visible on screen: ETF-level summary → look-through aggregation → consolidated per-name + factor view.

**Recording requirements**

- Construct a realistic test portfolio with 5-8 ETFs that *look* diversified but contain hidden overlaps (e.g., VOO + QQQ + IVV — heavy mega-cap-tech overlap). The reveal is the demo.
- Two dwell:y beats (overlap-reveal table, factor-profile aggregate)
- The reveal beat is the visual hero — the "look at the actual numbers vs what you thought" moment
- 60fps, 1920×1080

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow: *ETF Analysis* or *Look-Through*
- LT headline at reveal beat: something like *"40% overlap on 15 names"* — the specific concentration number
- Outro: standard `"Solve the market."`


**Recording inputs (locked)**

- **Sample portfolio** (save as `v5_sample_portfolio.csv` in working folder; reused in V13 — FOA onboarding):

  | Ticker | Weight |
  |---|---|
  | SPY | 25% |
  | QQQ | 20% |
  | VTV | 15% |
  | IEFA | 15% |
  | IEMG | 10% |
  | VYM | 15% |

  *(Looks diversified at the wrapper level — actually has heavy overlap between SPY/QQQ/VTV at the top US large-cap names. Look-through reveals the real top-5 names are AAPL, MSFT, GOOGL, NVDA, AMZN at multiples of the wrapper-level apparent weight.)*

- **Prompt to type:**
  > Portfolio analysis with ETF look-through enabled — flag compound concentration, surface true per-name exposure.
- **Pre-test checklist:**
  - ☐ Portfolio CSV loads without parsing errors
  - ☐ Surface view (wrapper-level) renders first with the six ETF positions visible
  - ☐ Look-through table flips to per-name underlying exposure
  - ☐ Compound concentration is flagged: top-5 underlying names show real weight (much higher than wrapper-level)
  - ☐ Aggregated factor profile is visible (Quality / Momentum / Value tilts)

---

### V6 — Macro Intelligence

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `single_feature` (Tier 1) |
| **Duration target** | 80–100s |
| **Primary persona** | PM (discretionary fund — global / Asia-Pacific / EM exposure) |
| **Secondary personas** | Financial analyst pulling a country read for a PM ask · CIO-as-practitioner setting tactical tilts |
| **Primary moment (in-VO)** | *"Korea election Sunday. Country-level read by Monday open."* |
| **Tool** | `/parallax:macro` (LT module name: **Macro Intelligence**) |
| **Deliverable** | Single-country macro outlook: regime classification + key indicator readings + sectors-in-favor (and -out-of-favor) + rates + FX direction + equity opportunity shortlist for the country |
| **Why it matters** | Country-level macro reads are usually consultant-grade (slow, expensive — Citi Research / GS Macro / Bloomberg ECO). When a PM needs a position-shaping country read *fast* (event reaction, weekly review, fresh thesis), the legacy options aren't built for that timeline. Parallax produces a structured country brief in under a minute, sourced and reproducible. |
| **Title-card headline (hook)** | *"Country read. Monday morning."* |
| **Title-card eyebrow** | *"V6 · Country Macro Outlook"* |
| **YouTube title** | *"Country-Level Macro Outlook (Single-Country Equity Opportunities)"* |

**Highlights** — distinct points this video owns

- Single-country read framing (NOT global — the focus is on actionable country-level positioning)
- Regime classification: expansion / recovery / slowdown / contraction — with the indicator evidence
- Sectors-in-favor list with explicit rationale (rates direction, currency move, regime fit)
- Equity opportunity shortlist — names that fit the country's current macro regime + factor profile
- **Primary value angles** — *Moat headline:* none (production-speed-anchored). *Standard angles:* **#1 Speed** (minutes vs days for consultant reports) · **#2 Coverage** (every country supported, not just G10) · **#7 Decision-readiness** (drops into Monday morning's IC note) · **#3 Defensibility** (regime classification has documented methodology — can be defended in committee).

**Beat sheet (target)**

- **Open (~10s, no zoom)** — Moment-setter VO. NL prompt: *"Macro analysis on South Korea: current regime, sector positioning, equity opportunities."* (Or Japan, India, Indonesia — pick a country with a *fresh news context* for the recording date.)
- **Regime + indicators (~20s, dwell:y — zoom on regime classification + indicator panel)** — VO walks the regime call + the indicator evidence: *"Mid-cycle expansion. Industrial production accelerating. Inflation cooling. The KOSPI has been pricing this in since Q1."*
- **Sectors in favor (~18s, dwell:y — zoom on sector rotation panel)** — VO calls the rotation: *"Semis, financials, industrials catching the bid. Consumer staples and utilities lagging — that's the textbook mid-cycle pattern."*
- **Equity shortlist (~12s, dwell:y — zoom on names list)** — names that fit the regime + factor profile, with brief one-line rationales
- **Closer (~6s, no zoom)** — *"Country read. Sectors. Names. Monday morning, you're positioned."* Outro tagline: standard.

**Tool chain**

`/parallax:macro` invokes `macro_analyst` for the chosen country — sub-calls: `list_macro_countries` (verifying coverage), regime-classification model, indicator pull, sector rotation logic, equity-shortlist filtering against country's universe. Visible on screen: regime card → indicators table → sector heatmap → shortlist table.

**Recording requirements**

- Pick a country with *current-event relevance* (Korea election, Japan rate decision, India earnings season, Indonesia post-election, etc.) — the demo's freshness IS the credibility
- Three dwell:y beats (regime+indicators, sector rotation, shortlist)
- 60fps, 1920×1080

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow: *Macro Intelligence*
- LT headline at regime beat: regime name + 2-3 indicator callouts
- Outro: standard `"Solve the market."` (PM moment but single-tool — Polaris closer goes to the multi-tool methodology-proof videos)


**Recording inputs (locked)**

- **Input:** South Korea  *(pre-test on recording day — if Korea's macro context has changed materially, swap to a country with fresher news: Japan, India, Indonesia, or Mexico)*
- **Prompt to type:**
  > Macro analysis on South Korea: current regime, sector positioning, equity opportunities.
- **Pre-test checklist:**
  - ☐ Regime classification renders (mid-cycle expansion / late cycle / contraction / recovery)
  - ☐ Key indicator readings appear (industrial production, inflation, rates)
  - ☐ Sector ranking populates (sectors in favor + lagging)
  - ☐ Rates + FX direction commentary present
  - ☐ Equity-opportunity shortlist names appear, each with a one-line rationale

---

### V7 — Quarterly Portfolio Review  *(workflow chain)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `workflow_chain` (Tier 2) |
| **Duration target** | 2:00–2:30 |
| **Primary persona** | MFO / independent RIA / wealth advisor (same persona model as V1) |
| **Secondary personas** | FOA running cyclical principal updates · CIO-as-practitioner reviewing the book before client-facing prep |
| **Primary moment (in-VO)** | *"Quarterly review with your biggest client tomorrow. Full prep by tonight."* |
| **Tools** | `/parallax:portfolio` → `/parallax:rebalance` → PDF export (LT module names: **Analyzer** → **Analyzer (Rebalance)** → **PDF Report**) |
| **Deliverable** | Refreshed portfolio read + rebalance memo + client-ready advisor output (written opinion in email/memo form) — the entire quarterly review packet in one workflow. *(Note: `/parallax:portfolio` advisor mode produces a written opinion as text output; there is no portfolio-level PDF generator in current product. `get_stock_report` exists for per-stock PDFs only.)* |
| **Why it matters** | The standing-quarterly-review moment is the highest-stakes recurring touchpoint between an RM and their UHNW clients. Manual prep is a multi-evening grind across spreadsheets, broker reports, and ad-hoc commentary. Parallax compresses the prep into a 90-minute session and produces an artifact that drops straight into the client conversation. |
| **Title-card headline (hook)** | *"The quarterly review, prepped by tonight."* |
| **Title-card eyebrow** | *"V7 · Quarterly Portfolio Review"* |
| **YouTube title** | *"Quarterly Portfolio Review for Wealth Advisors (Portfolio Health → Rebalance → Client-Ready Output)"* |

**Highlights** — distinct points this video owns

- The *"client review tomorrow, prep tonight"* moment — Venise's day-in-the-life canonical workflow
- Three-tool chain visible on screen as a coherent sequence (not three disconnected tool demos)
- Portfolio health beat: score every name in the book + flag drift from the IPS
- Rebalance beat: trim list + add list + before/after factor profile
- Client-ready output beat: advisor written opinion (with full evidence chain) drops into the review folder, ready to share via email or memo
- **Primary value angles** — *Moat headline:* none (this is the persona-resonance flagship — RMs see themselves doing their actual workflow). *Standard angles (rotation across ~150s):* **#7 Decision-readiness** (PDF drops into the client deck) · **#3 Defensibility** (every score sourced) · **#1 Speed** (multi-evening → 90 min) · **#8 Workflow-native** (lives in your AI client, not a new terminal) · **#6 No black box** (drill into any flagged name).

**Beat sheet (target — locked in Phase 7)**

- **Open (~12s, no zoom)** — Moment-setter VO. Cowork chrome with the client's portfolio CSV already loaded. NL prompt: *"Prepare quarterly client review for [client]. Portfolio health flags, rebalance proposal, client-ready written opinion for tomorrow's meeting."*
- **Portfolio health pass (~30s, dwell:y — zoom on health-flag table)** — Analyzer runs; flagged names surface (score-deteriorating, IPS-breach, concentration). VO names the flags + interprets: *"Three names slipped a notch since the last review — here's why. One position is now 8% of the book; IPS cap is 5."*
- **Rebalance pass (~30s, dwell:y — zoom on trim/add list + before/after factor)** — Rebalance tool produces the trade list. VO walks the proposal: *"Trim the over-concentration. Add two names that close the Quality gap. Before-and-after factor profile — Quality up two points, Value steady, Momentum gently down."*
- **Client-ready output beat (~25s, no zoom — show artifact)** — VO frames the artifact: *"Advisor output formatted for the client folder. Performance, attribution, rebalance proposal, factor profile — every claim sourced, written in client-facing register."* Advisor written opinion visible on screen, scrolled briefly.
- **Closer (~10s, no zoom)** — *"Quarterly review, prepped. Walk into tomorrow's meeting with the artifact in hand."* Outro tagline: standard.

**Tool chain**

`/parallax:portfolio` (advisor mode — auto-detected when client/benchmark context is present; produces analyze_portfolio + lens=performance + lens=concentration + per-holding drilldown + final get_assessment for the written opinion) → `/parallax:rebalance` (trade list + factor delta + before/after) → advisor mode's written opinion is the client-ready deliverable. *(No portfolio-level PDF tool exists in current product; the written advisor output IS the artifact.)*

**Recording requirements**

- Construct a realistic UHNW-style portfolio (15-25 holdings, equity + ETFs, $5-10M scale) — Venise's Workflow Test framework is the canonical reference
- Show clear IPS-drift / concentration flags (manufactured into the test portfolio — needs to be visible to the demo)
- Three dwell:y beats — health-flag table, rebalance trim/add list with before/after factor, PDF artifact view
- 60fps, 1920×1080
- VO maintains RM-flavored language throughout (per Principle #9 — moment-anchored, not role-labeled)

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow rotates: *Analyzer* (during health beat) → *Rebalance* (during proposal beat) → *PDF Report* (during export beat) — three LT eyebrow refreshes across the workflow
- Outro: standard `"Solve the market."` (RM audience — Polaris closer wrong fit)


**Recording inputs (locked)**

- **Sample UHNW portfolio** (save as `v7_sample_portfolio.csv`):

  | Ticker | Weight | Ticker | Weight |
  |---|---|---|---|
  | AAPL | 8% | LLY | 4% |
  | MSFT | 7% | UNH | 4% |
  | GOOGL | 5% | KO | 3% |
  | AMZN | 5% | SPY | 25% |
  | NVDA | 4% | VTI | 15% |
  | JPM | 5% | (cash) | 11% |
  | BRK.B | 4% |  |  |

- **Prompt to type:**
  > Prepare quarterly client review for the Smith family book. Portfolio health flags, rebalance proposal, client-ready written opinion for tomorrow's meeting.
- **Pre-test checklist:**
  - ☐ Portfolio loads; all 12 positions accounted for
  - ☐ Health flags surface: at least one score-deteriorating name, one IPS/concentration breach
  - ☐ Rebalance proposal includes specific trade list + before/after factor profile
  - ☐ Client-ready written output formatted in advisor register (no jargon, no internal references)
  - ☐ Every claim sourced (footnotes or inline citations)

---

### V8 — Investment Committee Position Defense  *(workflow chain)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `workflow_chain` (Tier 2) |
| **Duration target** | 2:15–2:45 |
| **Primary persona** | Portfolio Manager (discretionary fund preparing for IC) |
| **Secondary personas** | CIO-as-practitioner sitting on the IC · Head of research validating positions before the meeting · Analyst pulling the per-name evidence the PM will reference |
| **Primary moment (in-VO)** | *"Investment committee tomorrow. Every position needs a defense."* |
| **Tools** | `/parallax:portfolio` + per-name `/parallax:stock` + audit-trail navigation + `explain_methodology` (LT module names: **Analyzer** + **Stock Report** + **Audit Trail**) |
| **Deliverable** | IC-ready brief — every held position with composite score, factor evidence, methodology drill-down on demand, exception flags |
| **Why it matters** | The IC defense moment is where PMs get held to account on every position. *"Why are we still in this name?"* is a question the PM must be able to answer with sourced evidence — not gut feel. Parallax provides the evidence chain inline, so the PM doesn't need to flip through Bloomberg pulls and broker decks mid-defense. **Headlines moat #4 Auditability** in the "every claim cite-able" framing. |
| **Title-card headline (hook)** | *"Every position. Every number. Defendable."* |
| **Title-card eyebrow** | *"V8 · IC Position Defense"* |
| **YouTube title** | *"Defending Portfolio Positions at Investment Committee (Every Claim Cite-able)"* |

**Highlights** — distinct points this video owns

- The *"IC tomorrow"* moment + the every-position-defendable stakes
- Portfolio view → per-name drilldown → methodology drawer chain visible
- Methodology drawer (`explain_methodology`) appearing on demand: click any score, see the rationale — *not a chatbot's confident guess*
- *"Why are we still in this name?"* mock-challenge beat — VO frames the answer in real time, drilling from composite score → driving pillar → underlying factor input → source
- Exception flags column — names that warrant proactive committee attention
- **Primary value angles** — *Moat headline:* **#4 Auditability** (every claim has a paper trail). *Supporting:* **#6 No black box** (drill into any score, see methodology) · **#3 Defensibility** · **#7 Decision-readiness** (the brief IS the IC deck) · **#9 Live track record** (the engine running Polaris since 2019 is the same engine running this defense).

**Beat sheet (target)**

- **Open (~12s, no zoom)** — Moment-setter VO. Cowork chrome, portfolio loaded. NL prompt: *"Investment committee preparation — full book defense. Per-position composite, factor evidence, methodology drilldown for audit trail."*
- **Portfolio pass (~25s, dwell:y — zoom on score-ranked positions table)** — Analyzer surfaces every position with Total Score + 5 factor pillars + recent score delta. VO scans the table.
- **Mock-challenge beat — per-name drilldown (~35s, dwell:y — zoom on a single position's full breakdown)** — VO simulates an IC challenge: *"Why are we still in [name]?"* Cursor clicks into the position; per-name Stock Report appears with the latest score, factor evidence, financial health, and the **methodology drawer** open showing the exact rule that drove the call. **This is the auditability hero beat.**
- **Source-trail beat (~25s, dwell:y — zoom on methodology drawer)** — VO walks the evidence chain: *"Composite eight-point-one. Driven by Quality pillar — earnings stability, ROIC trend, debt service. Click through to the source filings — every input cite-able."* Eight-second hold on the visible source citations.
- **Exception flags beat (~15s, no zoom)** — back to portfolio view; exception column highlighted. *"These four warrant proactive raising tomorrow before the committee surfaces them."*
- **Live-fund flex (~12s, no zoom)** — *"This is the engine running Polaris — real capital, not a backtest, since 2019. Same audit trail. Same standards."* (Anchors #9 Live track record.)
- **Closer (~8s, no zoom)** — *"IC tomorrow. Every position. Every number. Defendable."* **Outro: Polaris closer earns this one** — PM audience, methodology-proof video. *"This isn't a backtest. Polaris has been running on these scores since 2019."*

**Tool chain**

`/parallax:portfolio` → per-name `/parallax:stock` (drill into each flagged name) → `explain_methodology` (drawer popup on any score) → audit-trail navigation (visible source citations). The chain isn't linear — it's *exploratory*: PM navigates between portfolio view and per-name detail multiple times. Recording needs to show this as natural exploration, not a scripted A→B→C walk.

**Recording requirements**

- Realistic 20-30 position PM book — mix of high-conviction holds and recent slip names so the challenge beat has visible material
- The methodology-drawer beat is the visual hero — needs careful framing (zoom + annotate-highlight calibration to point at the rule citation)
- 4 dwell:y beats (portfolio table, per-name drilldown, methodology drawer, exception flags)
- 60fps, 1920×1080

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow rotates: *Analyzer* → *Stock Report* → *Methodology* (during drawer beat) → *Audit Trail* (during source-trail beat)
- **Outro: Polaris closer** *(PM audience + methodology-proof flex earned)*


**Recording inputs (locked)**

- **Sample long-only PM book** (save as `v8_sample_portfolio.csv`; reused in V14 — book-level macro impact):

  | Ticker | Weight | Ticker | Weight |
  |---|---|---|---|
  | AAPL | 8% | LLY | 6% |
  | MSFT | 7% | UNH | 5% |
  | GOOGL | 6% | HD | 5% |
  | AMZN | 6% | COST | 5% |
  | NVDA | 7% | TSLA | 5% |
  | META | 6% | V | 5% |
  | JPM | 6% | MA | 5% |
  | BAC | 4% | TSM | 6% |
  |  |  | ASML | 4% |

- **Prompt to type:**
  > Investment committee preparation — full book defense. Per-position composite, factor evidence, methodology drilldown for audit trail.
- **Pre-test checklist:**
  - ☐ All 15 positions render with Total Score + factor pillars + recent score delta
  - ☐ Methodology drawer opens on at least one position (the visual hero beat) — every rule cite-able
  - ☐ Source-trail click-through works: composite → factor pillar → underlying input → original filing
  - ☐ Exception flags surface for at least 2-4 positions

---

### V9 — Full Stock Deep Dive  *(workflow chain)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `workflow_chain` (Tier 2) |
| **Duration target** | 2:00–2:30 |
| **Primary persona** | Financial analyst (sell-side or buy-side support — end-of-day brief turnaround) |
| **Secondary personas** | PM requesting the brief · Head of research signing it off |
| **Primary moment (in-VO)** | *"Brief request just landed. End-of-day deadline."* |
| **Tool** | `/parallax:deep-dive` (LT module name: **Deep Dive** — 11 parallel calls + AI assessment synthesis) |
| **Deliverable** | Full single-name due diligence brief — fundamentals, valuation, technicals, scenario context, peer comparison, news synthesis, AI assessment, all reconciling against the same factor framework |
| **Why it matters** | The full-DD-brief moment is the analyst's bread and butter. Pulling 11 parallel data feeds, reconciling them against each other, and synthesizing a defensible read — manually, that's 4-6 hours of work for a senior analyst. Parallax runs it as one workflow in under three minutes, with everything traceable back to source. |
| **Title-card headline (hook)** | *"Eleven parallel calls. One brief."* |
| **Title-card eyebrow** | *"V9 · Full Stock Deep Dive"* |
| **YouTube title** | *"Full Stock Due Diligence (11-Call Parallel Deep-Dive Research Brief)"* |

**Highlights** — distinct points this video owns

- The 11 parallel calls visible firing simultaneously — this is the visual hero (different scale from V1's 8-call moment, visibly more)
- AI assessment synthesis beat — the integrated read after the 11 components reconcile
- *"Reconciling, not just stitching"* framing — sub-call outputs all reference the same factor framework, so the synthesis actually integrates instead of contradicting itself
- Each of the 11 sub-components callable as a standalone (composite score, financials, technicals, scenario context, peers, news, analyst spread, AI assessment, etc.) — the deep-dive is a flagship-tools collection, not a separate tool
- **Primary value angles** — *Moat headline:* none (productivity + integration-anchored, not a moat showcase). *Standard angles:* **#1 Speed** (4-6 hours → 3 minutes) · **#2 Coverage** (every component, not just the easy ones) · **#6 No black box** (each component's source visible) · **#7 Decision-readiness** · **#3 Defensibility**.

**Beat sheet (target)**

- **Open (~12s, no zoom)** — Moment-setter VO. NL prompt: *"Full deep dive on [TICKER]: 11-call analysis, AI assessment, peer context, macro overlay. EOD deadline."*
- **Eleven-call fan-out (~20s, no zoom — let the parallelism breathe)** — chat shows 11 parallel calls firing. VO names the differentiator: *"Eleven calls. Parallel, not sequential. Each one referencing the same factor framework — they reconcile."*
- **Component walkthrough (~50s, dwell:y — zoom across composite → financials → scenario → peers → news → AI assessment)** — VO interprets each component as it lands, not reading the numbers but naming what's striking. Multiple sub-zooms (~8s each on 4-5 components).
- **AI assessment synthesis beat (~25s, dwell:y — zoom on the synthesis paragraph)** — the integrated read. VO frames: *"Eleven inputs. One framework. The synthesis isn't a chatbot summary — it's the framework's verdict, with every input sourced."*
- **Closer (~8s, no zoom)** — *"Brief request in. Brief out. End of day, in hand."* Outro tagline: standard `"Solve the market."`

**Tool chain**

`/parallax:deep-dive` invokes 11 underlying MCP tools in parallel: company info, score analysis, financial analysis, technical analysis, news synthesis, stock outlook, peer snapshot, macro analyst, financial health, scenario context, AI assessment. The 11 visible simultaneously in chat = the visual hero.

**Recording requirements**

- Pick a stock with a *non-trivial story* — something where the synthesis actually has to reconcile competing signals (a mid-cap with momentum-vs-value tension, or a name in a sector regime shift)
- The 11-call fan-out beat needs careful pacing — let the parallel work be visible long enough to register
- 3-4 dwell:y beats (composite, peer snapshot, AI assessment paragraph; possibly a 4th on technicals)
- 60fps, 1920×1080

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow: *Deep Dive*
- LT headline at fan-out beat: *"11 parallel calls. One framework."*
- Outro: standard


**Recording inputs (locked)**

- **Input:** `TSM`  *(multi-angle story: Quality factor, geo / Taiwan-China risk, cyclical semis, multi-philosophy investor interest — exercises every one of the 11 calls cleanly)*
- **Prompt to type:**
  > Full deep dive on TSM: 11-call analysis, AI assessment, peer context, macro overlay. EOD deadline.
- **Pre-test checklist:**
  - ☐ 11 parallel calls fire visibly in the chat
  - ☐ Each component lands cleanly: fundamentals → valuation → technicals → scenario → peers → news synthesis → AI assessment
  - ☐ AI assessment integrates inputs against the factor framework (not a chatbot summary)
  - ☐ Every component renders with sourceable claims (no LLM hallucination)

---

### V10 — Regime-Window Backtesting  *(workflow chain)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `workflow_chain` (Tier 2) |
| **Duration target** | 2:00–2:30 |
| **Primary persona** | Quant analyst / data person (quant fund, factor-investing shop, research-driven advisory) |
| **Secondary personas** | Head of research validating a methodology change · PM stress-testing the framework against a specific regime |
| **Primary moment (in-VO)** | *"Reproduce the regime-window analysis without look-ahead bias. Point-in-time portfolio scoring with historical rebalance dates."* ⓟ |
| **Tools** | `analyze_portfolio` raw MCP tool, invoked directly (not via `/parallax:portfolio` — the slash command doesn't expose `start_date` as a user-facing knob). Parameters: `start_date` (YYYY-MM-DD), `end_date` (defaults to yesterday), per-holding `date` field (rebalance/as-of date). (LT module name: **Analyzer — Point-in-Time mode**) |
| **Deliverable** | Reproducible point-in-time portfolio analysis — performance metrics, rolling metrics, drawdown analysis, portfolio_scores returned for a fixed historical window. Re-run tomorrow against the same fixed dates: byte-identical output. |
| **Why it matters** | The single most-asked question by quant teams: *"Can I reproduce a score AS OF a specific date, with no contamination from later data?"* If yes, the platform passes quant due diligence. If no, the quant team walks. This video is the canonical **#5 Determinism** showcase — reproducibility as a *property of the workflow*, not a marketing claim. Hands-off proof. |
| **Title-card headline (hook)** | *"Re-run tomorrow. Same number. Same source."* |
| **Title-card eyebrow** | *"V10 · Regime-Window Backtesting"* |
| **YouTube title** | *"Point-in-Time Backtesting for Factor Strategies (No Look-Ahead Bias)"* |

**Highlights** — distinct points this video owns

- *"Point-in-time"* and *"no look-ahead bias"* — the exact phrases quants use; persona-locked vocabulary
- `start_date` and `end_date` parameters visible in the query — the surface-level proof that the platform supports point-in-time evaluation
- Same input → byte-identical output: run it twice, get the same numbers (visible reproducibility demo)
- Regime-window framing (e.g., "post-COVID recovery", "2022-23 inflation regime") — not a single anchor date but a *window* with quant relevance
- Per-holding `date` field visible — each position can have its own rebalance/as-of date, supporting either static or rebalanced portfolio evaluation
- **Primary value angles** — *Moat headline:* **#5 Determinism** (this IS the canonical determinism showcase — byte-for-byte identical output across runs). *Supporting:* **#6 No black box** (factor framework documented, methodology defensible) · **#3 Defensibility** · **#11 Risk-adjusted return** (quants care about the risk side of the trade).

**Beat sheet (target)**

- **Open (~12s, no zoom)** — Moment-setter VO (persona-locked language). NL prompt: *"Run regime-window backtest, start_date = 2021-01-01, point-in-time evaluation. Need factor performance, IC stats, CSV export."*
- **start_date / end_date proof beat (~20s, dwell:y — zoom on the parameters in the query)** — VO names the discipline: *"start_date and end_date pinned. Each holding carries its own as-of date. The engine evaluates using only data available as of those dates — no look-ahead contamination."*
- **Same-input-same-output beat (~25s, no zoom)** — VO sets up the proof: *"Run it once. Get the score. Run it again — same score. Byte-identical. This isn't a backtest accident; it's a property of the workflow."* Visible re-run of the same query → identical output.
- **Regime-window analysis (~30s, dwell:y — zoom on performance + drawdown panels)** — actual results from `analyze_portfolio`: performance_metrics, rolling_metrics, drawdown_analysis, portfolio_scores across the regime window. VO interprets the regime-specific finding.
- **Reproducibility flex (~15s, no zoom)** — VO names the determinism property visibly: *"Run this tomorrow against the same fixed dates. Same input, byte-identical output. That's not a backtest accident — it's a property of how analyze_portfolio handles historical dates."* Visible re-run of the same query → identical output.
- **Closer (~8s, no zoom)** — *"Reproducible. Point-in-time. Audit-grade portfolio analysis."* Outro tagline: standard `"Solve the market."` (Quant audience — Polaris closer wrong fit; the determinism flex IS the close.)

**Tool chain**

`analyze_portfolio` raw MCP tool invoked directly. The `/parallax:portfolio` slash command doesn't expose `start_date` as a user-facing parameter — quants call the raw tool with `start_date`, `end_date`, and per-holding `date` fields for point-in-time evaluation. Output fields: performance_metrics, rolling_metrics, drawdown_analysis, portfolio_scores. Visible on screen: NL prompt → AI client routes to raw `analyze_portfolio` → date parameters set → results returned → reproducibility re-run.

**Recording requirements**

- Pick a regime window with quant relevance — post-COVID (early 2021), 2022 rate-shock, or a specific sector regime shift
- Show the re-run-same-output beat clearly — viewer needs to SEE the byte-identical proof, not just hear it
- 2-3 dwell:y beats (start_date / end_date parameters in query, regime-window performance + drawdown panels, possibly the reproducibility re-run)
- 60fps, 1920×1080

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow: *Analyzer — Point-in-Time* (default) or *Determinism* (custom eyebrow for the reproducibility flex beat)
- Outro: standard


**Recording inputs (locked)**

- **Sample factor-tilted basket as-of 2021-01-01** (save as `v10_sample_basket.csv`):

  | Ticker | Weight |
  |---|---|
  | AAPL | 12% |
  | MSFT | 12% |
  | GOOGL | 10% |
  | AMZN | 10% |
  | NVDA | 10% |
  | V | 8% |
  | MA | 8% |
  | COST | 8% |
  | LLY | 8% |
  | ASML | 7% |
  | (cash) | 7% |

  *(Skewed toward high-Quality + high-Momentum US large-cap as-of 2021-01-01. Each holding carries its 2021-01-01 as-of date for point-in-time evaluation.)*

- **Prompt to type:**
  > Point-in-time portfolio analysis with start_date = 2021-01-01, end_date = 2023-12-31. Per-holding rebalance dates set to scenario timeline. Need performance metrics, drawdown analysis, rolling factor scores.
- **Pre-test checklist:**
  - ☐ `start_date` and `end_date` parameters are accepted and reflected in the response
  - ☐ Performance metrics render (CAGR, vol, Sharpe, max DD) for the window
  - ☐ Rolling factor scores render (monthly or quarterly granularity)
  - ☐ Drawdown analysis chart populates
  - ☐ Re-run identical prompt: confirm byte-identical output (determinism flex)

---

### V11 — Compliance Audit Trail for Investment Advice  *(workflow chain)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `workflow_chain` (Tier 2) |
| **Duration target** | 2:15–2:45 |
| **Primary persona** | Compliance officer (trade/portfolio compliance — IPS drift, restricted-list, recommendation review) |
| **Secondary personas** | Head of advisory signing off on the audit · Regulator-facing internal liaison · RM whose recommendations are being reviewed |
| **Primary moment (in-VO)** | *"Signing off on this quarter's advisory recommendations. Each evidence chain verified before approval."* ⓟ |
| **Tools** | `/parallax:portfolio` (advisor mode on the current advice queue) + per-name `/parallax:stock` evidence drilldown + `explain_methodology` (Methodology drawer for any score in question) (LT module names: **Analyzer** + **Stock Report** + **Methodology**) |
| **Deliverable** | Pre-sign-off compliance review — each pending recommendation's evidence chain (score → factor → input → source) verified inline, exceptions raised and resolved before the advice ships |
| **Why it matters** | The compliance-sign-off-on-advice moment is the single highest-stakes regulated workflow in wealth management — MAS, FCA, SEC, HKMA all require defensible evidence chains. Manual sign-off means cross-referencing broker reports and Bloomberg pulls against each proposed recommendation — hours per cycle. Parallax produces the evidence chain inline at advice time: every score cites its driving factor + source filing; `explain_methodology` drills into any score on demand. **Canonical #4 Auditability headline — this is THE showcase video for the moat, in the prospective-review framing.** Direct hit on prospect-mapped buyers (People's Partnership, MAS Shariah-AI grant pipeline). |
| **Title-card headline (hook)** | *"Every number traces. Every recommendation defends."* |
| **Title-card eyebrow** | *"V11 · Advice Audit Trail"* |
| **YouTube title** | *"Compliance Review for Investment Advice (Evidence Chain Sign-Off)"* |

**Highlights** — distinct points this video owns

- The *"pre-sign-off on this quarter's advice, every recommendation needs a defensible evidence chain"* compliance moment
- Pending advice queue as the visual hero — proposed recommendations laid out for sign-off review, each tagged with its evidence chain inline
- Methodology drawer beat: click any score → see the rule + the input + the source — the audit-trail unrolled
- Exception cases flagged at sign-off — names where the proposed action's evidence isn't as clean as it should be (sign-off *catches* before the advice ships, not after the regulator does)
- Inline methodology drawer: any flagged score's rationale + driving factor + source filing visible on click during the review — sign-off happens with the chain visible, not reconstructed after the fact
- **Primary value angles** — *Moat headline:* **#4 Auditability** (THE showcase — every component of every recommendation has a paper trail). *Supporting:* **#6 No black box** (methodology drawer makes the rules visible) · **#3 Defensibility** (peer-reviewed methodology, regulator-recognized) · **#12 Unverifiable frame** (the explicit contrast with LLM-only advice review — *"an LLM can't reproduce the evidence chain; Parallax can"*) · **#9 Live track record** (the same engine running Polaris).

**Beat sheet (target)**

- **Open (~12s, no zoom)** — Moment-setter VO (persona-locked language). Cowork chrome, current advice queue visible. NL prompt: *"Compliance review for sign-off: this quarter's pending client recommendations. Provide evidence chain per recommendation for review before approval."*
- **Pending advice view (~25s, dwell:y — zoom on the recommendation queue)** — pending recommendations listed with: client, proposed action, current score, justifying factor pillar, source filing. VO frames: *"Every proposed recommendation tagged with the score driving it, the factor pillar, the source filing. The evidence chain is built into the proposal — sign-off reads it inline, not reconstructed after."*
- **Mock sign-off challenge beat (~40s, dwell:y — zoom on one recommendation's full evidence chain)** — *"Why are we recommending [name] for [client]?"* Cursor clicks into the pending recommendation; Stock Report opens. VO walks the chain: *"Composite 8.4. Driven by Quality and Tactical pillars. Quality pillar: ROIC trend over 8 quarters, debt service ratio improving. Methodology drawer open — click through to the underlying filing."* **The methodology drawer is the visual hero beat.**
- **Exception flags (~25s, dwell:y — zoom on flagged-name column)** — *"Three of this quarter's pending recommendations have flagged exceptions. Current score doesn't quite support the proposed action. Either revise the recommendation or document the override — but resolve it now, before sign-off, not after."*
- **Determinism + unverifiable frame combo (~15s, no zoom)** — VO ties it together: *"Same input today, same evidence chain. An LLM can't reproduce this — every answer would be different. Parallax IS the audit trail."*
- **Sign-off action beat (~10s, no zoom)** — approved recommendations move to client delivery; flagged ones return for revision. The evidence chain stays attached to each decision.
- **Closer (~8s, no zoom)** — *"Every recommendation defends. Every number traces. Signed in one pass."* Outro tagline: standard `"Solve the market."` (Compliance audience.)

**Tool chain**

`/parallax:portfolio` (advisor mode on the current advice set) → per-name `/parallax:stock` for evidence drilldown (current score + factor pillars + source filings) → `explain_methodology` drawer for any flagged score → sign-off decision. The auditability comes from the in-output evidence chain (every score cites its driving factor + source filing at production time) and `explain_methodology`'s drill-down. **No historical recommendation log retrieval needed** — the moment is prospective sign-off on current advice, not retrospective audit of past advice.

**Recording requirements**

- Construct a realistic pending advice queue: 10-15 client recommendations under review for sign-off this cycle, mix of clean and exception cases
- The methodology-drawer beat is the visual hero — careful framing + annotate-highlight calibration
- 3-4 dwell:y beats (pending advice queue, methodology drawer, exception column)
- 60fps, 1920×1080
- **Production note for Phase 7:** V11 pivoted from retrospective audit (which required a stored recommendation log — a feature gap) to prospective sign-off, which uses tools that exist today. No engineering verification needed.

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow rotates: *Analyzer* → *Stock Report* → *Methodology*
- Outro: standard


**Recording inputs (locked)**

- **Sample pending-recommendation queue** (save as `v11_pending_recs.csv`):

  | Client | Recommendation | Current score |
  |---|---|---|
  | Smith family | Trim NVDA from 5% → 3% | 7.2 |
  | Lee family | Add LLY to 4% | 8.4 |
  | Goh family | Reduce TSLA from 4% → 2% | 5.8 |
  | Tan family | Hold KO | 6.4 |
  | Wong family | Initiate position in V at 3% | 8.1 |

- **Prompt to type:**
  > Compliance review for sign-off: this quarter's pending client recommendations. Provide evidence chain per recommendation for review before approval.
- **Pre-test checklist:**
  - ☐ All 5 pending recs render with client + action + current score
  - ☐ Evidence chain per rec: score → driving factor pillar → input → source filing (click-through)
  - ☐ Methodology drawer opens on at least one rec — drilldown to the rule that drove the call
  - ☐ At least 2-3 recs surface exception flags (score doesn't quite support the proposed action)
  - ☐ Determinism: re-run produces identical evidence chain

---

### V12 — Building a Stock Portfolio from a Thesis  *(workflow chain)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `workflow_chain` (Tier 2) |
| **Duration target** | 2:15–2:45 |
| **Primary persona** | Portfolio Manager (discretionary — thematic / sector-rotation / factor-tilt strategy) |
| **Secondary personas** | CIO-as-practitioner setting tactical tilts · Analyst tasked with operationalising the PM's thesis · Head of research validating the basket |
| **Primary moment (in-VO)** | *"Have a thesis. Need a basket. Score-defensible, methodology-traceable."* |
| **Tools** | `/parallax:universe` (Builder — includes built-in `check_portfolio_redundancy` at Step 4) → `/parallax:portfolio` → per-name `/parallax:stock` health checks (LT module names: **Builder** → **Analyzer** → **Stock Report**) |
| **Deliverable** | Scored, factor-balanced basket aligned to the thesis — redundancy-checked, defensibility-traced, ready to size |
| **Why it matters** | The *thesis-to-basket* moment is where PMs operationalise a tactical view into an investable portfolio. Manual: pulling tickers from broker shortlists, hand-checking factor exposures, hoping no hidden overlaps. Parallax compresses thesis-articulation-to-scored-basket into one workflow with redundancy detection layered in — the unique-to-Parallax flex that no LLM-only workflow can replicate. |
| **Title-card headline (hook)** | *"Thesis in. Basket out. Redundancy-checked."* |
| **Title-card eyebrow** | *"V12 · Thesis-to-Portfolio Build"* |
| **YouTube title** | *"Building a Stock Portfolio from an Investment Thesis (Thematic Basket Construction)"* |

**Highlights** — distinct points this video owns

- The *natural-language thesis → scored basket* flow — Builder's flagship capability
- Redundancy check built into `/parallax:universe` (Step 4 of the Builder workflow) — surfaces hidden correlated bets the PM didn't realize they had; the unique-to-Parallax differentiator runs automatically as part of the basket build, not as an external layer
- Factor-balanced basket output — not just "names that match the theme" but "names that match AND balance against existing book"
- Defensibility-traced: every name in the basket cites its scoring rationale
- **Primary value angles** — *Moat headline:* none headline, but **#5 Determinism** strongly supporting (thesis → same basket every time, byte-identical). *Standard angles:* **#2 Coverage** (every name in the relevant universe scored, not just the obvious tickers) · **#6 No black box** (every score's rationale traceable) · **#7 Decision-readiness** · **#1 Speed** · **#3 Defensibility**.

**Beat sheet (target)**

- **Open (~12s, no zoom)** — Moment-setter VO. Cowork chrome. NL prompt: *"Universe build: high-quality US industrials, small-mid cap, momentum tailwinds, exclude defense. Scored basket with factor balance and redundancy check against existing book."*
- **Builder runs (~30s, dwell:y — zoom on emerging shortlist)** — Builder produces the scored shortlist. VO interprets: *"Twelve names match the thesis. Each scored against the same framework — Quality pillar high, Momentum tailwind confirmed, defense exclusion applied."*
- **Health pass on each name (~20s, no zoom — fast walkthrough)** — Portfolio view with per-name health checks. *"Three names flag — one has deteriorating financials, one has a sector drift, one is a duplicate exposure to a name in your existing book."*
- **Built-in redundancy check beat (~30s, dwell:y — zoom on redundancy detection output)** — **THE unique-to-Parallax beat — note: this runs automatically as Step 4 of `/parallax:universe`, not as a separate tool call.** VO names the in-Builder check: *"As part of the Builder, redundancy auto-runs on the proposed equal-weight allocation. Two of the twelve names overlap forty-percent factor-loading with positions you already hold. Adding them would double up the bet, not diversify it."* This is the differentiator no LLM-only workflow can replicate.
- **Refined basket (~15s, dwell:y — zoom on final scored basket)** — post-filter, factor-balanced basket. *"Nine names. Factor-balanced against your existing book. Each defensible against the thesis."*
- **Closer (~8s, no zoom)** — *"Plain English thesis. Scored basket. Ready to size."* Outro tagline: **Polaris closer earns this one** (PM audience, methodology-proof flex — the redundancy check is the kind of feature that earns the Polaris flex). *"This isn't a backtest. Polaris has been running on these scores since 2019."*

**Tool chain**

`/parallax:universe` (Builder workflow — `build_stock_universe` thesis-to-scored-universe, then `get_peer_snapshot` for top candidates, then built-in `check_portfolio_redundancy` at Step 4 of the universe workflow) → `/parallax:portfolio` (final basket analysis) → per-name `/parallax:stock` health checks. The redundancy check is a built-in step of `/parallax:universe`, not a separate tool layer.

**Recording requirements**

- Pick a thesis with *operational specificity* — not "buy quality" but "high-quality industrials with momentum, small-mid-cap, exclude defense" or similar. The specificity makes the NL-prompt-to-basket flow concrete.
- The redundancy check needs an EXISTING book to overlap against — construct a realistic PM book first (~25 holdings) then have the thesis build attempt against it
- 3 dwell:y beats (Builder output, redundancy detection, final basket)
- 60fps, 1920×1080

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow rotates: *Builder* → *Analyzer* → *Redundancy Check*
- **Outro: Polaris closer** *(PM audience + thesis-build methodology-proof earned)*


**Recording inputs (locked)**

- **Input:** the thesis itself (concrete, no ticker substitution needed). Existing book loaded for the redundancy check: reuse `v8_sample_portfolio.csv`.
- **Prompt to type:**
  > Universe build: high-quality US industrials, small-mid cap, momentum tailwinds, exclude defense. Scored basket with factor balance and redundancy check against existing book.
- **Pre-test checklist:**
  - ☐ Scored shortlist emerges with 8-15 names matching the thesis
  - ☐ Each name shows Quality + Momentum scores + sector tag
  - ☐ At least 2-3 names flag (deteriorating financials / sector drift / duplicate exposure)
  - ☐ Redundancy check auto-runs against the existing book
  - ☐ Refined basket renders with the redundant names removed
  - ☐ Each remaining name is defensible against the thesis with a one-line rationale

---

### V13 — Family Office Equity Portfolio Onboarding  *(workflow chain)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `workflow_chain` (Tier 2) |
| **Duration target** | 2:00–2:30 |
| **Primary persona** | Family-office analyst (single or multi-family office — equity-slice analysis only; Parallax doesn't handle illiquids) |
| **Secondary personas** | RM at a wealth advisor onboarding a new UHNW client · CIO-as-practitioner at a small family office |
| **Primary moment (in-VO)** | *"New principal. Multi-ETF book just landed. One-page equity exposure read by EOD."* |
| **Tools** | `/parallax:portfolio` (with ETF look-through) + deeper **`/parallax:etf`** beat + factor decomposition + macro context (LT module names: **Analyzer** + **ETF Analysis** + **Macro Intelligence**) |
| **Deliverable** | One-page equity exposure read for principal IC — factor profile, regional/sector concentration, ETF-by-ETF look-through, macro regime context, all on the equity slice the family owns |
| **Why it matters** | The new-principal-onboarding moment is FOA bread and butter. Family books often arrive ETF-heavy and the FOA is the first person who has to translate "what does this family actually own?" into a defensible read. Parallax's equity-slice analysis with look-through closes the loop in one workflow — what would otherwise be a multi-week consolidation exercise. **Bounded honestly:** illiquid holdings (PE, real estate, direct deals) are outside Parallax's surface; this video addresses the slice Parallax can actually improve. |
| **Title-card headline (hook)** | *"New principal. Equity read by EOD."* |
| **Title-card eyebrow** | *"V13 · Family Office Equity Onboarding"* |
| **YouTube title** | *"Family Office Equity Portfolio Onboarding (ETF Look-Through + Factor + Macro Context)"* |

**Highlights** — distinct points this video owns

- New-principal-onboarding moment (different from V5's "what's in my ETFs" moment — V13 is a workflow scaled to a whole book; V5 is the look-through capability alone)
- ETF look-through extended deeper than V5: not just look-through, but per-ETF profile + factor profile + alternatives consideration
- Aggregated factor profile across the entire equity slice — what the family ACTUALLY owns after look-through
- Macro regime context: where does this exposure sit relative to current macro positioning?
- One-page output: principal IC-ready, can sit in the family's quarterly meeting deck
- Honest bounding: illiquid portion of the family book is acknowledged but not analyzed — Parallax's surface is equity + ETF only
- **Primary value angles** — *Moat headline:* none (FOA productivity-anchored). *Standard angles:* **#2 Coverage** (every ETF looked through, every name scored — not just the top positions) · **#6 No black box** (the underlying revealed, not the wrapper) · **#7 Decision-readiness** (one-page principal-ready output) · **#8 Workflow-native** (the FOA's stack is Excel + DDQ + ad-hoc — Parallax fits as the equity-analysis layer).

**Beat sheet (target)**

- **Open (~12s, no zoom)** — Moment-setter VO. Cowork chrome, new client's equity portfolio CSV loaded. NL prompt: *"New client onboarding: full equity portfolio analysis with ETF look-through, factor decomposition, macro regime overlay. Single-page principal-ready output."*
- **Surface view (~15s, no zoom)** — VO acknowledges the wrapper level: *"Twelve positions on the surface. Seven of them ETFs. Without look-through, you can't tell the family what they actually own."*
- **ETF look-through (~25s, dwell:y — zoom on look-through aggregation)** — each ETF's underlying expanded. VO names the reveal: *"The seven ETFs hold one hundred and forty-two underlying names. Twenty-three of those overlap across multiple ETFs — the real concentration story."*
- **Deeper ETF beat (~25s, dwell:y — zoom on per-ETF profile + alternatives)** — for the largest 2-3 ETF positions, full profile: factor exposure, expense ratio, alternatives in the same exposure category. *"This emerging-markets ETF — high expense ratio for the exposure it gives. Three cheaper alternatives within ten basis points of tracking."*
- **Aggregated factor + macro context (~20s, dwell:y — zoom on the consolidated factor profile + macro overlay)** — *"After look-through: heavy Quality tilt, moderate Momentum, light Value. Macro regime: mid-cycle expansion. The factor positioning fits the regime — except for one underweight that's worth flagging."*
- **One-page output beat (~10s, no zoom)** — exportable one-page summary visible
- **Closer (~8s, no zoom)** — *"New principal. Equity book understood. One page. End of day."* Outro tagline: standard `"Solve the market."`

**Tool chain**

`/parallax:portfolio` (analyze_portfolio with ETF look-through enabled) → `/parallax:etf` deeper per-ETF beat (etf_profile + etf_holdings + alternatives via etf_search) → factor decomposition (built into portfolio analysis) → `/parallax:macro` context overlay → one-page export. The deeper ETF beat is the new content vs V5 — that video covered look-through alone; this one operationalises it into a full onboarding flow.

**Recording requirements**

- Construct a realistic UHNW family equity book: 10-15 positions, equity + ETF mix, principal-scale ($10-30M), some hidden overlap in the ETF layer
- The "illiquid disclaimer" can be a single line in the VO ("the family's PE and direct holdings are outside this analysis") — keep it honest but quick
- 3 dwell:y beats (look-through aggregation, per-ETF deeper, aggregated factor + macro)
- 60fps, 1920×1080

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow rotates: *Analyzer* → *ETF Analysis* → *Macro Intelligence*
- Outro: standard


**Recording inputs (locked)**

- **Sample portfolio:** reuse `v5_sample_portfolio.csv` (same 6-ETF book from V5 — cross-video consistency keeps the family-office storyline coherent)
- **Prompt to type:**
  > New client onboarding: full equity portfolio analysis with ETF look-through, factor decomposition, macro regime overlay. Single-page principal-ready output.
- **Pre-test checklist:**
  - ☐ Surface view of 6 ETF positions renders
  - ☐ ETF look-through expands each wrapper to underlying holdings (~140+ names)
  - ☐ Overlap detection: at least 20-30% of underlying names appear in multiple ETFs
  - ☐ Largest 2-3 ETF positions get a deeper profile (factor exposure, expense ratio, cheaper alternatives)
  - ☐ Aggregated factor profile + macro regime overlay render
  - ☐ Output is formatted single-page principal-ready (not multi-page)

---

### V14 — Macro Event Response: A PM Playbook  *(hero playbook — Iran/Korean Banks anchor)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `hero_playbook` (Tier 3) |
| **Duration target** | 3:30–4:30 |
| **Primary persona** | Portfolio Manager (discretionary fund — global / Asia-Pacific / EM exposure; event-driven mandate) |
| **Secondary personas** | CIO-as-practitioner setting tactical tilts post-event · Analyst publishing the playbook · Head of research validating before circulating |
| **Primary moment (in-VO)** | *"Iran war over the weekend. Oil to $82. Monday open in fourteen hours. What's the contrarian read?"* |
| **Tools** | `/parallax:scenario` (Impact Analysis) + `/parallax:macro` (Macro Intelligence — affected countries) + `/parallax:universe` (Builder — `build_stock_universe` on the affected universe with factor-screen criteria) + thesis synthesis (LT module names: **Impact Analysis** + **Macro Intelligence** + **Builder**) |
| **Deliverable** | Publishable PM playbook — scenario impact map across the book, macro context for the directly-affected and second-order countries, factor-screened contrarian shortlist, synthesized thesis with sourced evidence |
| **Why it matters** | The macro-event-over-the-weekend moment is one of the highest-stakes PM workflows there is. Monday open arrives in 14 hours; you need a defensible read across vulnerability AND opportunity, with citations for IC and (if you publish) clients. Manual: hours per affected country, gut-feel on the contrarian angle, no time to reconcile. This is the hero piece the catalogue exists for — **direct demonstration of the worked-example anchor** (Ivan Cheloliev's actual Iran/Korean Banks playbook, 2026-03-02), end-to-end. |
| **Title-card headline (hook)** | *"Monday open in fourteen hours. The contrarian read."* |
| **Title-card eyebrow** | *"V14 · Macro Event Response (Iran Playbook)"* |
| **YouTube title** | *"Macro Event Response: A PM Playbook (Scenario Analysis → Macro Context → Factor Screen → Contrarian Thesis)"* |

**Highlights** — distinct points this video owns

- **Anchored to a real artifact** — Ivan Cheloliev's *"Iran, $82 Oil, and the Contrarian Case for Korean Banks"* playbook, 2026-03-02 (`references/use-case-examples/iran-playbook/`)
- The four-tool workflow that produced it: scenario impact → macro context (oil-up regimes, Hormuz risk) → factor screen of Korean banks → contrarian thesis synthesis
- *"Indiscriminate sell-off setup"* framing — markets pricing in worst case, factor framework identifies what's mispriced
- Hormuz-scenario impact table — sourced from external (Goldman Commodity Research) for the macro framing, Parallax for the equity-side translation
- Korean banks factor-screen output: 5 candidate names with full metric table (sourced from Parallax)
- Reproducibility flex: re-run the workflow tomorrow against the same Friday-close inputs, get the same playbook
- **Primary value angles** — *Moat headline:* **#5 Determinism** (the entire workflow is reproducible against the as-of-event inputs — Friday close data; re-run Sunday or Monday and the playbook is byte-identical). *Supporting:* **#1 Speed** (hours → 30 minutes for the full playbook) · **#2 Coverage** (every affected country and every name in the relevant universe screenable) · **#3 Defensibility** · **#6 No black box** · **#7 Decision-readiness** (the playbook IS the IC note) · **#9 Live track record** (Polaris ran a version of this in March 2026 — Lena's actual playbook).

**Beat sheet (target)**

- **Open: the moment (~25s, no zoom)** — VO sets the stake. *"Friday evening. Iran headlines hit. Oil prints eighty-two by overnight. You have fourteen hours until Monday open. Every position with energy exposure needs a vulnerability read. And somewhere in the indiscriminate sell-off, there's a contrarian setup the market won't price until Tuesday — and you need to find it tonight."* The avatar / opening visual carries the weight here; recording can come in on the chrome.
- **Scenario impact across the book (~40s, dwell:y — zoom on the impact table)** — NL prompt: *"Macro event response: weekend Iran development, oil at $82/bbl with Hormuz tail risk active. Impact across every position in the book."* Impact table populates. VO walks the vulnerability story.
- **Macro context — affected countries (~45s, dwell:y — zoom on multi-country regime panel)** — *"Macro regime analysis on Korea, Japan, Saudi Arabia, India. Oil-up regime sensitivity per country."* Multi-country view; VO names the regime shifts that matter (Korea's energy-importer status, the second-order industrial-input effect).
- **The contrarian setup beat (~50s, dwell:y — zoom on factor screen of Korean banks)** — NL prompt: *"Factor screen on Korean banks: Quality + Value composite, oversold technical condition. Need ranked candidates with peer metrics."* Five names emerge with metric table. VO frames the contrarian thesis: *"Banks sold off with the indiscriminate Asia-EM trade. But the macro impact on Korean banks is third-order — net-positive if the Won weakens but Korean inflation cools. The factor screen flags five names where the sell-off pushed valuation below long-run average, Quality pillar held, momentum starting to base."*
- **Thesis synthesis (~35s, no zoom)** — the integrated read. VO names the workflow's integration: *"Three tools, one framework. Scenario, macro, builder — they reconcile because they reference the same model. The playbook reads like one analyst's voice, not three tools stitched."*
- **Reproducibility flex (~25s, no zoom)** — *"Run this Sunday. Run it Monday. As long as the input is Friday's close, the playbook is byte-identical. That's not a backtest property — it's a workflow property."* (Anchors #5 Determinism.)
- **Live-fund flex + Polaris (~20s, no zoom)** — *"Polaris ran a version of this in March 2026. Real capital, real Monday-morning execution. The engine running this playbook is the same engine running the fund."* Outro: **Polaris closer.** *"This isn't a backtest. Polaris has been running on these scores since 2019."*

**Tool chain**

`/parallax:scenario` (impact across the book under the Hormuz tail-risk shock) → `/parallax:macro` (multi-country regime context — Korea, Japan, Saudi, India, second-order effects) → `/parallax:universe` (Builder — `build_stock_universe` on Korean banks with Quality+Value oversold criteria) → manual thesis synthesis (the PM's value-add — Parallax is the spine; the thesis voice is the analyst's).

**Recording requirements**

- **Anchor the recording to the real playbook artifact** — `references/use-case-examples/iran-playbook/` has 6 screenshots from Ivan's actual document. The recording's beat sequence should mirror the playbook's structure.
- Pick a fresh-enough macro event for the recording date — if Iran/Korea is stale by recording time, swap to whatever's current (e.g., Japan rate-hike playbook, India election playbook, Mexico tariff playbook). The framework is the demo; the specific event is the surface.
- 4 dwell:y beats (scenario impact table, macro regime multi-country, factor screen, possibly synthesis paragraph)
- 60fps, 1920×1080
- **This is the Tier-3 hero recording — production complexity is highest in the catalogue. Allow the budget.**

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow rotates: *Impact Analysis* → *Macro Intelligence* → *Screener* → *Builder* (or *Thesis Synthesis*)
- **Outro: Polaris closer** *(PM audience + the deepest methodology-proof flex in the catalogue — the Iran playbook is exactly the kind of artifact where "Polaris ran this" earns its keep)*


**Recording inputs (locked)**

- **Sample portfolio:** reuse `v8_sample_portfolio.csv` for the book-level scenario impact (the long-only PM book defined in V8). The Iran/Korea/oil context is the named anchor; if a fresher major macro event lands closer to recording day, swap context and re-pre-test all three prompts.
- **Prompts to type (sequenced across the playbook):**
  > Macro event response: weekend Iran development, oil at $82/bbl with Hormuz tail risk active. Impact across every position in the book.

  > Macro regime analysis on Korea, Japan, Saudi Arabia, India. Oil-up regime sensitivity per country.

  > Factor screen on Korean banks: Quality + Value composite, oversold technical condition. Need ranked candidates with peer metrics.
- **Pre-test checklist:**
  - ☐ Impact table populates across every position in the loaded book (vulnerability story)
  - ☐ Multi-country regime panel renders cleanly (4-country comparison: Korea / Japan / Saudi / India)
  - ☐ Korean banks factor screen returns 4-6 ranked names with metrics
  - ☐ Reproducibility: re-run any of the three prompts — identical output
  - ☐ All three prompts' outputs synthesise into one coherent playbook (no cross-prompt contradictions)

---

### V15 — Stock Initiation Report  *(hero playbook)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `hero_playbook` (Tier 3) |
| **Duration target** | 3:30–4:30 |
| **Primary persona** | Financial analyst (sell-side coverage initiation OR buy-side initiation memo) |
| **Secondary personas** | Head of research signing off the initiation · PM receiving the brief · Compliance signing off the recommendation chain |
| **Primary moment (in-VO)** | *"New name handed to you for coverage. IC-grade initiation report, due Friday."* |
| **Tools** | `/parallax:deep-dive` (11 parallel calls) + `/parallax:scenario` (key risks tested) + `/parallax:investor` (multi-philosophy convergence on the name) + PDF export (LT module names: **Deep Dive** + **Impact Analysis** + **Investor Profile** + **PDF Report**) |
| **Deliverable** | Full-DD initiation report, IC-grade — fundamentals, valuation, technicals, peer set, scenario risks, multi-philosophy investor view (Buffett/Klarman/Soros/Greenblatt consensus), AI assessment synthesis, published artifact |
| **Why it matters** | The initiation-report moment is the analyst's flagship deliverable — the document that *defines* coverage for the firm. Manual: weeks of work, dozens of broker reports as cross-reference, multiple drafts before signoff. Parallax compresses to a single end-to-end workflow where every component reconciles against the same framework. The artifact that ships is **defensible against the universal LLM-only counter** — every claim has a source, every score has a methodology, every scenario has reproducible inputs. **Headlines moat #4 Auditability (the published artifact's evidence chain) + supports moat #12 Unverifiable frame** (the contrast against an LLM-generated initiation report). |
| **Title-card headline (hook)** | *"Initiation report, end-to-end. By Friday."* |
| **Title-card eyebrow** | *"V15 · Stock Initiation Report"* |
| **YouTube title** | *"Building a Stock Initiation Report (Deep-Dive + Scenario + Multi-Philosophy Investor View)"* |

**Highlights** — distinct points this video owns

- The *"new name, Friday deadline"* analyst-flagship moment
- Four-tool chain producing a published artifact (not just a screen output) — the initiation PDF IS the deliverable
- Multi-philosophy investor convergence beat (`/parallax:investor`) — unique-to-Parallax differentiator showing where Buffett, Klarman, Soros, Greenblatt agree and disagree on the name
- Scenario stress beat — the named risks tested with sourced inputs, not gut-feel "what could go wrong"
- AI assessment synthesis at the close — the integrated thesis, with every input traceable
- Published artifact as the close — branded PDF, evidence-chained, ready to ship to IC / client / coverage list
- **Primary value angles** — *Moat headline:* **#4 Auditability** (the published artifact's audit trail — every claim cite-able, every methodology drawer accessible from the PDF). *Supporting:* **#12 Unverifiable frame** (the natural contrast — an LLM initiation report has zero of these properties; reads identical, defensible against zero) · **#1 Speed** (weeks → hours) · **#2 Coverage** · **#6 No black box** · **#9 Live track record** (the same framework Polaris runs).

**Beat sheet (target)**

- **Open: the deliverable framing (~20s, no zoom)** — VO sets the moment. *"New name on your coverage list. Friday deadline for the initiation report — the document that defines how the firm thinks about this name for the next twelve months. Three pages, IC-grade, every claim defendable."*
- **Deep-dive parallel run (~40s, dwell:y — zoom on the 11-call fan-out)** — NL prompt: *"Initiation report on [TICKER] — full DD: deep dive, scenario stress on key risks, multi-philosophy investor convergence, PDF for IC by Friday."* The 11 calls fire in parallel; VO names the framework-integration story.
- **Scenario stress beat (~35s, dwell:y — zoom on scenario impact table)** — NL prompt: *"Stress test key risks: sector regime shift, regulatory event, earnings miss scenarios."* Multi-scenario impact populates. VO walks the named risks with sourced inputs.
- **Multi-philosophy investor convergence (~45s, dwell:y — zoom on the four-investor frame)** — NL prompt: *"Multi-philosophy investor analysis — Buffett, Klarman, Soros, Greenblatt. Identify convergence and divergence points."* The four-philosophy view appears. VO frames: *"This is unique to Parallax. Four legendary investor frameworks, each scoring the same name. Where they agree is conviction; where they diverge is the argument the analyst owns."* Distinctive vs an LLM that would just *paraphrase* each investor — Parallax operationalises the frameworks against the actual data.
- **AI assessment synthesis (~25s, dwell:y — zoom on synthesis paragraph)** — the integrated read. *"Eleven inputs. Scenario stress. Four philosophies. One framework holding them together."*
- **The artifact (~30s, dwell:y — zoom on the published PDF)** — branded initiation report PDF visible, scrolled. VO frames the artifact-level audit trail: *"Every page, every table, every score — clickable through to source. The published report has the audit trail baked in. An LLM-only initiation report can't do that — read it, you can't tell which numbers are right."* (Anchors #12 Unverifiable frame supporting role.)
- **Closer (~15s, no zoom)** — *"Initiation report. End-to-end. Defensible at every claim."* Outro tagline: standard `"Solve the market."` (Analyst audience — Polaris closer doesn't quite fit; the closer line emphasizes the artifact, not the engine.)

**Tool chain**

`/parallax:deep-dive` (11 parallel calls — full DD foundation) → `/parallax:scenario` (key risk stress tests) → `/parallax:investor` (Buffett/Klarman/Soros/Greenblatt multi-philosophy convergence) → PDF export (the published artifact). Methodology drawer + audit-trail navigation accessible throughout from the PDF (the artifact carries the audit trail forward — a buyer doesn't lose the chain when they hand the PDF to compliance).

**Recording requirements**

- Pick a stock with a *real coverage story* — something analysts would actually initiate on (mid-cap with a thesis-shaping question, sector regime shift candidate, etc.)
- The multi-philosophy investor beat is the visual hero — needs careful framing to show all four frameworks landing on the same name with distinct verdicts
- The published PDF beat at the end is the artifact-level visual hero — show the branded document with at least one click-through to source visible
- 5 dwell:y beats (11-call fan-out, scenario impact, investor convergence, synthesis paragraph, PDF artifact)
- 60fps, 1920×1080
- **Tier-3 hero production complexity — allow budget similar to V14**

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow rotates: *Deep Dive* → *Impact Analysis* → *Investor Profile* → *PDF Report*
- Outro: standard `"Solve the market."` (Analyst audience, artifact-anchored close — Polaris flex would dilute the artifact framing)


**Recording inputs (locked)**

- **Input:** `META`  *(rich multi-philosophy story: Buffett historically wouldn't touch, Klarman would on cheapness + quality, Soros on regime trade, Greenblatt on ROIC + quality — the divergence-then-convergence dynamic gives the four-philosophy beat the most dramatic frame)*
- **Prompts to type (sequenced across the report build):**
  > Initiation report on META — full DD: deep dive, scenario stress on key risks, multi-philosophy investor convergence, PDF for IC by Friday.

  > Stress test key risks: sector regime shift, regulatory event, earnings miss scenarios.

  > Multi-philosophy investor analysis — Buffett, Klarman, Soros, Greenblatt. Identify convergence and divergence points.
- **Pre-test checklist:**
  - ☐ 11 parallel calls fire on the first prompt
  - ☐ Scenario stress renders: 3-4 named scenarios with quantified impact
  - ☐ Four-philosophy view renders with both convergence and divergence points (not all-agree)
  - ☐ PDF generates and downloads
  - ☐ PDF renders cleanly when opened (3 pages, IC-grade, every page sourceable)

---

### V16 — Forensic Earnings Quality Analysis  *(hero playbook)*

| Field | Details |
|---|---|
| **Style** | `use_case` |
| **Complexity** | `hero_playbook` (Tier 3) |
| **Duration target** | 3:00–4:00 |
| **Primary persona** | Financial analyst (event-driven coverage — earnings response / forensic quality assessment) |
| **Secondary personas** | PM holding the position who needs the post-print read · Head of research signing off the forensic memo · Compliance reviewing whether the thesis remains intact |
| **Primary moment (in-VO)** | *"Stock fell twelve percent on earnings. Was it the print, or the guide?"* |
| **Tools** | `/parallax:screen` quality mode (Forensic Quality engine — Palepu-framework forensic analysis) + 8-quarter quality trajectory (`get_score_analysis`) + accounting-news context (`get_news_synthesis` — auditor changes, accounting-policy notes) + AI assessment + memo synthesis (LT module names: **Forensic Quality** + **Quality Trajectory** + **Stock Report**) |
| **Deliverable** | Forensic earnings memo — traffic-light verdict (thesis intact / thesis at risk / thesis broken), quality trajectory chart showing the 8-quarter pattern, Palepu-framework forensic flags (revenue-recognition patterns, accrual anomalies, cash-flow vs earnings divergence), accounting-news context (auditor changes, accounting-policy notes), AI assessment of whether the post-print sell-off was justified |
| **Why it matters** | The post-earnings forensic moment is high-stakes and time-sensitive. Stock dropped 12% on the print — does the analyst defend the existing recommendation, or pivot? Manual: re-read the call, compare to the prior 4 quarters by hand, gut-call whether the language changed. Parallax compresses the forensic into a sourced, traceable memo with a traffic-light verdict the analyst can stand behind. Vault evidence: M2 video concept *"When the Analyst Was Wrong"* directly supports this workflow as analyst-thesis-validation. |
| **Title-card headline (hook)** | *"The print, or the guide? The forensic memo."* |
| **Title-card eyebrow** | *"V16 · Forensic Earnings Analysis"* |
| **YouTube title** | *"Forensic Earnings Quality Analysis (Was the Sell-Off Justified? Thesis Intact or Broken?)"* |

**Highlights** — distinct points this video owns

- The *"stock dropped twelve percent post-earnings, was it justified?"* moment
- Quality trajectory beat — 8-quarter pattern shown visually (was the print continuous with the trend, or a break?)
- Palepu-framework forensic analysis beat — accrual anomalies, revenue-recognition patterns, cash-flow vs earnings divergence; the unique-to-Parallax forensic capability that runs the standard quality-of-earnings checks against the same factor framework that scored the name in the first place
- Traffic-light verdict: thesis intact / thesis at risk / thesis broken — a defensible call, not a gut take
- Memo synthesis: the analyst's framework-grounded answer to the PM/IC question
- **Primary value angles** — *Moat headline:* none headline (analyst-productivity-anchored). *Standard angles:* **#1 Speed** (hours of re-reading transcripts → 5 minutes for a sourced verdict) · **#2 Coverage** (every quarter back, not just the latest two) · **#6 No black box** (every Palepu flag cites the underlying financial signal — accrual ratios, cash-conversion deltas, revenue-recognition patterns) · **#3 Defensibility** (the verdict has methodology behind it, not analyst gut) · **#7 Decision-readiness**.

**Beat sheet (target)**

- **Open: the moment (~20s, no zoom)** — VO sets the stake. *"Earnings hit yesterday. Stock down twelve percent. Phone's ringing. The PM wants to know if the thesis is intact, the head of research wants the memo before COB, and your existing buy recommendation is going to look stupid if the answer's no. Forty minutes to know."*
- **Quality trajectory beat (~40s, dwell:y — zoom on 8-quarter quality chart)** — NL prompt: *"Forensic earnings quality analysis on [TICKER]: 8-quarter trajectory, Palepu-framework forensic checks, accounting-news context, traffic-light verdict for thesis-validation review."* Quality trajectory chart appears. VO interprets: *"Quality pillar held seven of the last eight quarters. This quarter cracked — but the crack started Q-minus-three. Operating margin softening, working-capital trend reversing. The print didn't break the trend; it confirmed a trend that was already there."*
- **Palepu forensic + accounting-news beat (~50s, dwell:y — zoom on Palepu finding panel)** — Palepu-framework forensic analysis surfaces accrual anomalies and cash-flow-vs-earnings divergence; `get_news_synthesis` overlays auditor changes and accounting-policy notes. VO walks the flagged signals: *"Accruals running fifteen percent above operating cash flow for three quarters running. Auditor changed in Q2. Inventory build outpacing revenue growth. These are the quality-of-earnings flags Palepu's framework catches — every flag cites the underlying ratio or filing."*
- **Traffic-light verdict (~25s, dwell:y — zoom on verdict block)** — *"Thesis-at-risk. Not broken — but the trend wasn't priced in. The post-print sell-off catches the market up to what the forensic was already telling you."* Verdict block visible.
- **AI assessment + memo synthesis (~30s, no zoom)** — the integrated read. *"Forensic quality, accounting news, AI assessment — all reconciling against the same framework. The memo writes itself in the framework's voice."*
- **Closer (~10s, no zoom)** — *"Forty minutes. Sourced verdict. Memo on the head-of-research desk."* Outro tagline: standard `"Solve the market."` (Analyst audience.)

**Tool chain**

`/parallax:screen` in quality mode fans out: `get_score_analysis` (52w quality trajectory) + `get_financials` × 4 statements × 4 periods (income, cash flow, ratios) + `get_financial_analysis` (async ~2-5 min — Palepu-framework forensic) + `get_news_synthesis` (accounting news, auditor changes) → `get_assessment` for the AI synthesis pass → memo. The Palepu forensic + framework-consistent quality trajectory is the unique-to-Parallax differentiator — no LLM-only workflow runs these quality-of-earnings checks with the methodology rigor the engine provides.

**Recording requirements**

- Pick a real stock with a *forensically interesting* recent earnings event — ideally a name where the trajectory tells a richer story than the headline print (e.g., a name whose quality cracked before the analyst consensus caught it)
- The Palepu forensic beat needs visible flag-and-evidence pairs — the demo's credibility depends on showing the actual numbers behind each verdict (accrual ratios, cash-conversion deltas, auditor changes)
- 4 dwell:y beats (quality trajectory chart, Palepu finding panel, verdict block, AI assessment paragraph)
- 60fps, 1920×1080
- **Tier-3 hero production complexity — allow budget similar to V14 + V15**

**Format invariants**

- Template: `templates/product-demo/index.html`
- LT eyebrow rotates: *Forensic Quality* → *Transcript Analysis* → *Quality Trajectory* → *Stock Report*
- Outro: standard `"Solve the market."` (Analyst audience, forensic-anchored close)


**Recording inputs (locked)**

- **Input:** **Pick at recording day** — the demo's whole hook is *a name that just dropped on earnings*. Default fallback if no fresh post-earnings sell-off is available: **WBA (Walgreens)** or **CMG (Chipotle)** — both have had Quality trajectory concerns. Confirm the name has 8+ quarters of historical Quality data before locking.
- **Prompt to type (substitute the chosen ticker):**
  > Forensic earnings quality analysis on [TICKER]: 8-quarter trajectory, Palepu-framework forensic checks, accounting-news context, traffic-light verdict for thesis-validation review.
- **Pre-test checklist:**
  - ☐ 8-quarter Quality trajectory chart populates (no data gaps)
  - ☐ Palepu-framework forensic flags render with specific ratios (accruals / OCF, working capital trend, inventory build)
  - ☐ At least 2-3 flags fire (the dramatic beat — if everything is green, swap ticker)
  - ☐ Accounting-news context surfaces (auditor changes, accounting-policy notes if any)
  - ☐ Traffic-light verdict renders (Thesis Intact / At Risk / Broken) with a clear narrative

---

**Phase 3 complete. All 20 video specs drafted.** 4 instructional (I1-I4) + 16 use_case (V1-V16) = 20 videos covering 6 personas across 4 tiers. Every flagship Parallax tool has at least one on-screen appearance; 3 of 4 active moats headline at least once at each tier; Polaris closer flagged for the two PM methodology-proof hero pieces (V8, V12, V14).

**Next Phase work:**

- **Phase 6 audit** — verify every use_case video has a moat headline + 3-4 supporting angles + rotation discipline. Quick consistency check (10 min) now that all specs exist.
- **Phase 8 archive** — move legacy V0-V12 / N1-N14 specs (lines 90-991) to `_archive/MASTER-pre-overhaul-2026-05-11.md`. 10-minute mechanical edit.
- **Propagation sweep** — update CLAUDE.md, SKILL files, and `references/value-framing-menu.md` per-batch distribution table against the new 20-video set.
- **Phase 7 production** — Tier 0 → Tier 1 → Tier 2 → Tier 3. Begins with V1 re-record (canary).
