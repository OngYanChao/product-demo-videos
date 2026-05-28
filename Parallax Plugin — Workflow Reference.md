# Parallax Plugin — Workflow Reference

*Every command in the plugin, what it does, what tools it fires, and what you get back. Compiled by reading the command and skill files directly (`plugin_015A5ZUDZcthymkzdmBgQkgY`). April 2026.*

---

## The big picture

Parallax ships **10 slash commands** (each a guided workflow) plus **~30 underlying MCP tools** (each a single API call to Chicago Global's servers). The slash commands are recipes — they fire a specific batch of tools in a specific order and synthesize the output. The raw tools can also be called individually for surgical questions.

Every command runs as many calls as possible **in parallel** to keep total latency low. Async tools (the ones that take 15 seconds to a few minutes) return a job ID you poll on.

Behind the scenes there's a factor-scoring system producing six scores per stock on a 0–10 scale: **Quality**, **Value**, **Momentum**, **Defensive**, **Tactical**, plus a composite **Total Score**. Almost every workflow centers on these scores. There's also a **regime engine** that classifies macro environments and a **news synthesis** layer that summarizes recent catalysts.

Tokens are Chicago Global's internal billing unit. Free tools are 0 tokens; cheap tools are 1; medium are 5; the heavy synthesis tools are 10. Rough cost per workflow is listed below.

---

## The 10 slash commands

### 1. `/parallax:stock [ticker]` — Quick research brief

**What it is.** A one-minute overview of a stock. Natural-language question in, ~8 parallel API calls out, structured brief back.

**How it works.**

1. **Resolve ticker.** Calls `get_company_info` to find the stock (handles plain tickers like AAPL, Reuters codes like AAPL.O, HK numeric codes, etc.).
2. **Parallel data batch.** Once the ticker is confirmed, fires these simultaneously:
   - `get_peer_snapshot` — factor scores + where the stock ranks among its peers
   - `get_financials` (summary) — revenue and income trend
   - `get_score_analysis` (52 weeks) — how the factor scores have moved over a year
   - `get_stock_outlook` × 4 aspects — analyst price targets, buy/hold/sell recommendations, risk/return vs peers, dividend history
   - `get_news_synthesis` — recent news catalysts (runs async, doesn't block output)
3. **Macro context.** After ticker resolves, identifies the home market + main revenue geography (capped at 2 countries) and fires `macro_analyst` with `component="tactical"` for each.
4. **Interpret.** For any unusually high or low factor score, calls `explain_methodology` (free) to include the Parallax definition. Synthesizes everything.

**What you get.** Company overview → factor scores table with 52-week trend arrows → financial health traffic light → macro context → dividends → risk vs peers → recent news → analyst view → two-sentence bottom line (balanced, not a recommendation).

**Cost.** ~24 tokens.

---

### 2. `/parallax:deep-dive [ticker]` — Full due diligence

**What it is.** The IC-presentation version. Everything `/parallax:stock` does plus technical analysis and an AI-synthesized assessment. Designed for pre-investment research or investment-committee prep.

**How it works.**

1. **Batch A — 11 parallel data calls.** Everything `/parallax:stock` pulls, plus:
   - `get_financials` with `statement="ratios"` — margins, ROE, P/E
   - `get_technical_analysis` — trend, RSI, MACD, support/resistance. This one is async (~15–30 seconds). The plugin polls `check_job_status` every 15 seconds until it finishes.
2. **Batch B — Macro.** `list_macro_countries` + `macro_analyst` (tactical) for up to 3 relevant countries (home market + revenue geographies + commodity/supply-chain exposure).
3. **Batch C — AI Assessment.** After A and B are done, fires `get_assessment` with a comprehensive prompt that feeds in all the scores, trends, ratios, technicals, macro context, and any specific user question. This is the synthesis step — it produces the narrative assessment, not just tables.
4. **Optional "Full Mode".** For maximum due diligence, also pulls all four financial statements (income, balance sheet, cash flow, ratios) and fires `get_stock_report` (a ~2-minute async call that produces a formal PDF research report, 10 tokens).

**What you get.** Company overview, macro environment, factor profile with peer ranks and 52-week trends, financial highlights, dividend profile, risk/return profile, technical stance, news catalyst watch, **AI assessment (the synthesis paragraph)**, risk factors.

**Cost.** ~45 tokens.

---

### 3. `/parallax:portfolio [holdings]` — Portfolio health check

**What it is.** Paste your holdings, get a diagnostic. Two modes: **checkup** (educational, plain-language, for retail-ish users) and **advisor** (presentation-ready, drill-down on flagged holdings, for PMs and wealth advisors).

The command auto-detects advisor mode if you mention a client, a benchmark, or anything that sounds like advisor framing.

**How it works (checkup mode).**

1. **Batch A — Scoring + macro (parallel).**
   - `quick_portfolio_scores` — factor scores per holding and for the portfolio as a whole
   - `check_portfolio_redundancy` — overlap detection
   - `list_macro_countries` — which markets are covered
2. **Batch B — Macro context.** Reads the exchange suffixes on the holdings (`.O`=US, `.L`=UK, `.HK`=Hong Kong, etc.), identifies the home markets, and fires `macro_analyst` (tactical) for each unique covered market, capped at 3.
3. **Batch C — Health flag evaluation.** Runs the five-flag system (see sidebar below). Assigns an overall status: **Healthy** (0 flags), **Monitor** (1–2), **Attention** (3+).

**How advisor mode extends it.** Everything above, plus:
- Two more `analyze_portfolio` calls in Batch A with `lens="performance"` and `lens="concentration"`
- Per-holding drill-down in Batch C: picks up to 8 holdings (prioritized by flag count then weight) and runs `get_score_analysis` + `get_stock_outlook` (risk/return) + `get_peer_snapshot` for each
- Selective news: `get_news_synthesis` for any holding >10% weight AND flagged, capped at 5
- A final `get_assessment` call that synthesizes the whole thing into a written opinion with client context

**Mixed stocks + ETFs.** Uses `analyze_mixed_portfolio` instead of `analyze_portfolio` — same cost, but expands the ETFs to their underlying holdings so factor exposure reflects the *real* positions (catches hidden AAPL overlap between SPY and QQQ, for instance).

**What you get.** Health badge → factor scorecard (plain-language labels like "Strong quality, weak value") → triggered flags with explanations → redundancy/overlap findings → macro context → "What this means" narrative → "Consider" suggestions (framed as questions, not directives, for compliance reasons). Advisor mode adds a performance-vs-benchmark block, per-holding analysis, and prioritized action list.

**Cost.** ~36 tokens (checkup) / ~105 tokens (advisor).

**Sidebar: the 5 health flags.**

- **Low Score** — overall portfolio composite ≤ 5.0
- **Concentration** — any single holding > 15%, or top-3 > 45%
- **Redundancy** — 2+ overlapping pairs flagged by `check_portfolio_redundancy`
- **Value Trap** — portfolio Value score ≤ 3.0
- **Macro Misalignment** — overweight in sectors the current macro regime doesn't favor

Each recommendation the plugin produces must cite a specific flag or data finding. No generic advice — that's a hard rule in the health-flags skill.

---

### 4. `/parallax:rebalance [holdings with weights]` — Trade recommendations

**What it is.** The prescriptive follow-up to `/parallax:portfolio`. Tells you what to trim, what to keep, what to add. Two modes auto-detected: **rebalance** (with weights) and **watchlist** (tickers only, no weights).

#### Watchlist mode (no weights)

1. `get_score_analysis` for each symbol with 4–8 weeks in parallel — compute score change.
2. Flag "movers" = symbols whose total score changed more than 1 point, or any single factor moved more than 2 points.
3. For flagged symbols only, fire in parallel: `get_news_synthesis` (the catalyst), `get_technical_analysis` (with job polling), `get_stock_outlook` (recommendations).
4. Output: alert table ranked by magnitude of change → per-alert detail (which factor moved, what the news says) → stable names (one-liner each) → which names warrant a follow-up `/parallax:deep-dive`.

This is the "morning check-in" workflow. 15 tickers in, ~30 seconds out, you know exactly where to focus.

#### Rebalance mode (with weights)

Four batches:

- **Batch A — Current state.** `analyze_portfolio` with lens=performance + lens=concentration, `quick_portfolio_scores`, `check_portfolio_redundancy`, `list_macro_countries` — all parallel.
- **Batch B — Macro + score trends.** `macro_analyst` (tactical) per covered market, `get_score_analysis` per holding (top/bottom 5 by weight if 10+ holdings).
- **Batch C — Health flags + trade decisions.** Evaluates the 5 flags per holding, assigns priority:
  - **High** (3+ flags) → Trim or Exit
  - **Medium** (2 flags) → Investigate or Trim
  - **Low** (1 flag) → Monitor or Hold
  Combines flags + score trends + macro to decide actions. For trim candidates, builds a replacement universe (`build_stock_universe`) and scores the top candidates (`get_peer_snapshot`).
- **Batch D — Validation.** Runs `quick_portfolio_scores` on the *proposed* new allocation to confirm it actually improves on the current one. If it doesn't, the recommendations get flagged for revision.

**What you get.** Current assessment → health status badge → flag table per holding → macro context → score momentum table → **trade recommendations table** (Priority | Action | Symbol | Current Weight | Target Weight | Rationale, where every rationale cites a specific flag or finding) → replacement candidates with factor scores → **before/after factor profile comparison** → implementation notes.

**Cost.** ~76 tokens.

---

### 5. `/parallax:scenario [event] portfolio=[holdings]` — What-if analysis

**What it is.** Something happened (or might). What's exposed, what shifts, what do I do. Four-phase workflow with AI synthesis at two stages.

**How it works.**

- **Phase 1 — Understand the event (parallel).**
  - `get_news_synthesis` on 2–3 most-affected sectors — what the market already knows
  - `get_telemetry` (with specific `fields` passed to cap response size — regime tag, signals, commentary, divergences)
  - `macro_analyst` (tactical) on relevant countries/regions

- **Phase 2 — Assess portfolio exposure (after 1).**
  - `analyze_portfolio` with lens=concentration — sector/factor exposures
  - `get_score_analysis` (4–8 weeks) per holding — current trajectories
  - Then: `get_assessment` with a prompt that describes the scenario, lists each holding with its sector and factor profile, and asks: *"Rank these from most-exposed to least-exposed. For each, explain the transmission mechanism — direct revenue, supply chain, regulatory, sentiment."*

- **Phase 3 — Rotation candidates (after 2).**
  - `build_stock_universe` with a theme describing scenario beneficiaries (e.g., "rare-earth alternatives, US domestic mining")
  - `get_peer_snapshot` for the top 5 candidates in parallel
  - `get_financials` (summary) for the top 2–3 to verify fundamentals

- **Phase 4 — Action plan (after 3).**
  - Final `get_assessment` incorporating scenario + transmission mechanisms + macro regime + exposure ranking + rotation candidates, with an explicit ask for specific adjustments prioritized by urgency.

**What you get.** Scenario summary → macro regime impact → **exposure heat map** (each holding, High/Medium/Low exposure, transmission mechanism) → most-exposed names → least-affected names → sector rotation thesis → replacement candidates → prioritized action plan → "what to watch" (2–3 signals that would confirm or invalidate the thesis) → confidence & caveats.

**Cost.** ~68 tokens.

---

### 6. `/parallax:investor [profile] [ticker]` — Apply an investor framework

**What it is.** Applies one of four documented investor philosophies to a stock, or runs all four and produces a consensus signal. Not celebrity impersonation — each profile is derived from a peer-reviewed paper or the investor's own writing, with citations shown on screen. Every render is third-person ("Buffett-style," never "Buffett says").

Five modes:

- **buffett** — quality-value factor profile from *Buffett's Alpha* (Frazzini/Kabiller/Pedersen)
- **greenblatt** — Magic Formula (ROIC + earnings yield ranking)
- **klarman** — margin-of-safety, balance-sheet-first
- **soros** — macro regime + reflexivity
- **consensus** — all four in parallel, with super-majority voting

Input rules:
- Single ticker → runs selected profile
- No ticker + greenblatt → universe/basket mode
- No ticker + soros → regime-themed basket
- No ticker + consensus → rejected (needs at least one ticker)
- 2–5 tickers + consensus → basket mode
- >5 tickers → rejected

**Buffett mode** — parallel pull of `get_company_info` + `get_peer_snapshot` + `get_financials` (summary) + `get_score_analysis`. Applies four factor thresholds: Quality > 5, Value > 4, Momentum < 6, Defensive > 7. Verdict: 4/4 = match, 1–3 = partial, 0 = no match. For any notable factor score, calls `explain_methodology` (free) to show the definition.

**Greenblatt mode** — builds a sector-scoped universe (e.g. "US large-cap consumer staples"), caps at 30 names, pulls `get_financials` ratios in parallel for all 30, ranks each on ROIC and earnings yield separately, sums the ranks, sorts ascending. Top 3 = Magic Formula basket. In ticker-check mode, looks up where a specific stock falls: top 10% = match, top 25% = partial, below = no match.

**Klarman mode** — parallel pull of four financials statements (balance sheet, cash flow, ratios, plus `get_company_info` for market cap). Runs four checks: net cash position (computed directly from balance sheet, not ratios summary — critical detail), debt vs peers, FCF stability across 4 periods, valuation discount. Plus a Parallax Value ≥ 4 backup check. If no match AND Value < 4, appends a "no position warranted" footer.

**Soros mode** — the macro-heavy one. Builds covered-market list, picks 3–5 tactically interesting markets (default US + JP + EU + 2 EMs based on divergence), runs `macro_analyst` (tactical) per market in parallel, adds `get_telemetry` for cross-market regime divergence. Identifies 1–3 regime themes. In basket mode, builds a thematic universe per theme and ranks the top 3–5 by momentum × macro sensitivity. In single-ticker mode, runs a dual-channel exposure check (Channel A has two sub-paths, Channel B can be UNAVAILABLE which caps verdict at `partial_match`).

**Consensus mode** — runs Buffett, Greenblatt, Klarman, Soros in parallel where dependencies don't overlap. Each profile returns a verdict, verdict detail, factor flags, and any fallback notes. Then applies super-majority math: `required_matches = ceil(0.75 × applicable)`. Minimum 3 applicable profiles to produce a signal, otherwise INSUFFICIENT_PROFILES.

Consensus output includes a load-bearing "Factor-Level Agreement" section: shared signals (flagged by ≥2 profiles), single-profile signals (flagged by just one), and **absence signals** — collective blind spots all four profiles missed. The skill file marks that section as pedagogically load-bearing; don't cut it in the video edit.

**Cross-validation gate.** Every profile runs a name-check after `get_peer_snapshot` returns. If the company name from scoring doesn't match `get_company_info`, the profile refuses to render. Protects against ticker collisions between markets.

**Cost.** Buffett ~4 / Greenblatt ticker-check ~10–15 / Greenblatt universe ~15–30 / Klarman ~5–7 / Soros single-ticker ~25–30 / Soros basket ~25–40 / **Consensus single ticker ~45–55 / Consensus basket-of-5 ~150–200 (most expensive operation in the plugin).**

---

### 7. `/parallax:macro [country]` — Macro outlook

**What it is.** Full macro read on any covered country: regime status, 9 macro components, factor-regime interaction, equity opportunities. Can also do multi-country comparisons.

**How it works.**

- **Batch A — Coverage + telemetry (parallel).** `list_macro_countries` + `check_macro_health` + `get_telemetry` (with field filtering — the full response is 60KB+, too big to return raw).
- **Batch B — Macro depth.** Calls `macro_analyst` for the target country *without* a `component` parameter (summary mode) — this single call returns all 9 components inline (macro indicators, tactical, fixed income, currency, sectors, sector positioning, liquidity, news, factors) for the same 5-token cost as a single-component call. Other commands that only need one slice pass `component="tactical"` explicitly.
- **Multi-country.** "Compare US, Japan, Europe" fires `macro_analyst` for each in parallel.
- **Equity opportunities (conditional).** If the user asks, or if it's a country deep-dive, runs `build_stock_universe` ("[country] equities") → `get_peer_snapshot` for top 5 → `get_score_analysis` (26 weeks) for top 3.

**What you get.** Regime status + signals → full macro summary (indicators, rates, FX, sectors, tactical) → **factor regime interaction** (which of Quality/Value/Momentum/Defensive is favored in this regime — this is the Parallax-only section) → positioning implications → tactical bias → data freshness → top equity opportunities (if screened) → score trends on those picks.

**Cost.** ~28 tokens without equity screening, ~41 with.

---

### 8. `/parallax:etf [tickers or keywords]` — ETF research

**What it is.** Three workflows collapsed into one command. The plugin detects intent and routes.

- **Single ETF** → `get_etf_snapshot` + `get_etf_holdings` — profile, factor scores, top holdings
- **Compare ETFs (2–5)** → `compare_etfs` then `get_etf_overlap` — side-by-side plus actual % overlap between them (the "QQQ and VGT are basically the same thing" reveal)
- **Find ETFs by theme** → `search_etfs` with keywords + optional factor filters (`min_quality`, `min_momentum`, etc.), then snapshots on top results
- **Overlap check standalone** → `get_etf_overlap` with 2–5 tickers
- **Price history** → `get_etf_price_history` with a date range

ETF tickers are plain format (SPY, QQQ, IWM) — no exchange suffix needed.

**What you get.** ETF profile → factor scores → top holdings → overlap analysis (if comparing) → recommendation framing.

---

### 9. `/parallax:screen [halal or quality] [ticker or portfolio]` — Specialized screening

Two completely different screens, gated by the first argument.

#### Halal mode (Shariah compliance)

Applies AAOIFI / DJIM screening thresholds:

| Ratio | Threshold |
|---|---|
| Total debt / Total assets | < 33% |
| (Cash + interest-bearing securities) / Total assets | < 33% |
| (Interest income + non-permissible revenue) / Total revenue | < 5% |

**Single stock.** `get_company_info` (check sector against prohibited industries: banking, insurance, alcohol, tobacco, gambling, pork, weapons, adult), then parallel `get_financials` balance sheet + ratios, compute the three ratios, **fail hard if any threshold breached**. If non-permissible revenue is >0 but <5%, compute the purification ratio (the donation amount). Optional `get_financial_analysis` for deeper profitability decomposition (async ~2–5 min).

**Portfolio.** Single-stock check for each holding, `check_portfolio_redundancy` on compliant-only, then for any non-compliant name: `build_stock_universe` in the same sector → screen alternatives → `get_peer_snapshot` on the compliant ones.

Output: screening criteria, compliance table, key ratios, purification amount, scored alternatives. Ends with the standard Parallax disclaimer **plus a Shariah-specific one** ("not a fatwa — consult a qualified Shariah advisor for binding rulings").

**Cost.** ~8 tokens.

#### Quality mode (forensic earnings quality)

The analyst-gut-feel-validation workflow. "Revenue's up but cash flow isn't — is this a red flag?"

- **Batch A — Parallel.**
  - `get_score_analysis` (52 weeks) — quality score trajectory
  - `get_financials` income statement × 4 periods — revenue/margin trends
  - `get_financials` cash flow × 4 periods — cash conversion
  - `get_financials` ratios — accrual ratios
  - `get_financial_analysis` — Palepu-framework forensic analysis (async ~2–5 min, warn user)
  - `get_news_synthesis` — accounting news, auditor changes (async, don't block)
- **Batch B — AI synthesis.** `get_assessment` with a prompt focused on earnings-quality concerns: revenue-recognition patterns, accrual anomalies, cash flow vs earnings divergence, and any specific user concerns.

Output: traffic-light risk summary → 52-week quality score trajectory with inflection points → forensic findings → red flags (specific items) → accounting-news context → AI assessment → recommended monitoring actions.

**Cost.** ~24 tokens.

---

### 10. `/parallax:universe [thesis]` — Thesis-to-portfolio builder

**What it is.** Natural-language investment thesis → scored, weighted, redundancy-checked portfolio. The "I believe X is going to happen, build me a portfolio around it" workflow.

**How it works.** Six steps:

1. **Build universe.** `build_stock_universe` with the thesis as a query — searches 65K+ company descriptions.
2. **Score top picks.** `get_peer_snapshot` for the top 10 candidates in parallel (the universe tool ranks by *relevance* to the thesis, not factor quality — so every candidate needs scoring).
3. **Rank and select.** Re-ranks by total score, picks top 5–8 for the portfolio.
4. **Redundancy check.** `check_portfolio_redundancy` on proposed equal-weight allocation. Identifies sector concentration and industry overlap.
5. **Optimize weights.** Adjusts based on scores, redundancy flags, and sector balance. Runs `quick_portfolio_scores` on the final allocation to verify the factor profile matches the thesis (e.g., a "profitable companies" thesis should produce a quality-tilted portfolio).
6. **Validate (conditional).** `analyze_portfolio` on the final allocation to confirm it behaves as intended. If the response is truncated (the 180K char fallback kicks in), relies on steps 4–5 for validation.

Query tip baked into the skill: specific beats generic. "Profitable cloud infrastructure US" outperforms "tech."

**What you get.** Investment thesis restated → universe built (candidate count, key sectors) → **selected holdings table** (symbol, name, sector, total score, weight, key factor strengths) → portfolio factor profile → redundancy notes and how they were resolved → implementation notes (liquidity, position sizing, rebalance frequency).

Ends with a handoff: *"Would you like me to run a portfolio health check on these holdings?"* — if yes, passes the allocation to `/parallax:portfolio`.

**Cost.** ~36 tokens.

---

## The underlying MCP tools

The slash commands above are the normal entry points. But the MCP server exposes the individual tools too — useful for surgical questions that don't warrant a full workflow. Cost is in tokens.

### Free (0 tokens)

- **`explain_methodology`** — returns Parallax's definition for any factor, score, or methodology. Called liberally by the workflow commands for any notably high or low factor score.
- **`list_docs` / `get_docs`** — pull academic methodology docs from docs.chicago.global for the compliance/quant skeptics.

### Cheap (1 token)

- **`get_company_info`** — sector, market cap, description, name
- **`get_peer_snapshot`** — factor sub-scores + peer ranking. *The default fallback for any ambiguous stock question.*
- **`get_financials`** — one statement per call (summary, income, balance_sheet, cash_flow, ratios)
- **`get_stock_outlook`** — one aspect per call (analyst_targets, recommendations, risk_return, dividends)
- **`get_score_analysis`** — time-series of the six factor scores, configurable window
- **`export_price_series`** / **`export_peer_comparison`** — CSV/JSON exports for Excel
- **`list_macro_countries`** — which countries the macro engine covers
- **`get_telemetry`** — daily market regime snapshot. Full response is 60KB+ — always pass a `fields` filter.
- **`search_stocks`** / **`search_etfs`** — catalog lookup
- **`get_etf_profile`** / **`get_etf_holdings`** — ETF basics
- **`check_api_health`** / **`check_macro_health`** — data-freshness/uptime checks

### Per-holding (1 per holding)

- **`quick_portfolio_scores`** — factor scores per holding and for the portfolio. Breakeven vs `analyze_portfolio` at 5 holdings.
- **`check_portfolio_redundancy`** — overlap detection

### Medium (5 tokens)

- **`build_stock_universe`** — natural-language thesis or theme into a ranked candidate list. Note: times out on broad queries; default to sector-scoped queries.
- **`get_news_synthesis`** — recent catalysts for a symbol. Async — don't block output.
- **`get_technical_analysis`** — trend, RSI, MACD, support/resistance. Async ~15–30s, poll `check_job_status`.
- **`get_financial_analysis`** — Palepu-framework forensic analysis. Async ~2–5 min.
- **`analyze_portfolio`** — full portfolio analysis with lens parameter (performance, risk, quality, concentration, holdings, attribution).
- **`analyze_mixed_portfolio`** — expands ETFs to underlyings for true factor exposure. Use on any portfolio mixing stocks and ETFs.
- **`macro_analyst`** — macro analysis for one country. Summary mode (no `component`) returns all 9 components; component-specific mode returns the same content for the same cost but signals intent.

### Heavy (10 tokens)

- **`get_stock_report`** — formal PDF research report. Fire-and-forget, ~2-minute async job.
- **`get_assessment`** — the AI synthesis call. Feeds all gathered data into a reasoning pass that produces the narrative verdict.

### Other

- **`check_job_status`** — poll an async job ID. Used internally by commands for `get_technical_analysis`, `get_financial_analysis`, `get_stock_report`.
- **`submit_feedback`** — report a bug or feature request.

---

## Which command to use when

Baked into the plugin's `tool-selection` skill:

| User asks | Command |
|---|---|
| "Tell me about AAPL" / "Should I buy NVDA?" | `/parallax:stock` |
| "Deep dive on TSMC" | `/parallax:deep-dive` |
| "Analyze my portfolio" / "Is my portfolio concentrated?" | `/parallax:portfolio` |
| "Rebalance my portfolio" | `/parallax:rebalance` (rebalance mode) |
| "Monitor my watchlist" | `/parallax:rebalance` (watchlist mode) |
| "What if China banned rare-earth exports? My portfolio is..." | `/parallax:scenario` |
| "What would Buffett think of KO?" / "Magic Formula screen" / "Margin of safety on X" / "What do the legends think about NVDA?" | `/parallax:investor` |
| "Macro outlook for Japan" / "Compare US vs Japan macro" | `/parallax:macro` |
| "Tell me about QQQ" / "Compare QQQ vs VGT" / "Find EM quality ETFs" | `/parallax:etf` |
| "Is AAPL halal?" / "Forensic check on earnings quality" | `/parallax:screen` |
| "Build me a portfolio for profitable AI infrastructure" | `/parallax:universe` |
| Quick factor scores, no full workflow | raw `get_peer_snapshot` |
| One-line news | raw `get_news_synthesis` |
| Price history for Excel | raw `export_price_series` |
| "How does the Quality score actually work?" | raw `explain_methodology` (free) |
| "What's the market doing today?" | raw `get_telemetry` with `fields` filter |

---

## Conventions worth knowing

Lifted from the skill files; these shape every output.

- **Every on-screen recommendation cites a specific flag or data finding.** No generic advice ever. "Trim NVDA because Concentration flag + declining Momentum score" is allowed; "consider reducing tech exposure" is not.
- **Wording is compliance-friendly.** Portfolio suggestions frame as "Consider..." questions, not directives. Investor profiles use third-person ("Buffett-style", never "Buffett says"). Every output ends with a standard disclaimer.
- **Macro component summary trick.** `macro_analyst` with no `component` returns all 9 components at the same 5-token cost as asking for one. The macro command uses this; other commands pass `component="tactical"` to signal they only need the tactical slice, even though the data is identical.
- **Mixed-exchange fallback.** If `quick_portfolio_scores` covers <50% of a portfolio (common when holdings span US + Europe + Asia), the command splits by exchange suffix, scores each group separately, and merges — noted on screen as "Scoring used split-and-merge due to partial coverage."
- **180K character truncation.** Large portfolios can exceed `analyze_portfolio`'s response limit. Every workflow that uses it has a fallback path to `quick_portfolio_scores` + `check_portfolio_redundancy`.
- **Async is handled transparently.** `get_technical_analysis`, `get_financial_analysis`, `get_stock_report` all return a job ID; the workflow polls every 15 seconds and assembles the final output. From the user's perspective, it's just a slightly longer wait.
- **Graceful fallback beats hard failure.** If a data call fails after retry, the section renders as "Data unavailable" and the rest of the workflow continues. Verdicts computed on incomplete data cap at `partial_match` — they can't upgrade to full `match` without full data.
