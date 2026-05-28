---
name: video-scriptwriting
description: Writing style and craft rules for Chicago Global Parallax video scripts. Use whenever you are drafting, editing, or critiquing a voiceover script — including phrases like "write V5," "tighten the V7 script," "is this VO line any good," or "draft the hook for V12." The parallax-video skill reads this one before any blockquote gets written, so its rules govern every line the viewer will eventually hear. Includes a hallucination-check rule that requires every stat or product fact to trace to the master plan, the recording, or the `parallax-obsidian/` vault at the project root. Scripts declare a `style:` (`use_case` / `instructional` / `intel_brief`-paused) and `complexity:` (`utility` / `single_feature` / `workflow_chain` / `hero_playbook`) in their frontmatter; this skill's universal rules apply to all of them, and style-specific sections add or modify rules. Do not apply this skill to investor letters, white papers, emails, or conversational dialogue — it is scoped to spoken-for-video content only.
---

# Video Scriptwriting

Craft rules for voiceover scripts in the Chicago Global Parallax video series. The goal: scripts that sound human, carry analytical weight, and earn every second of the viewer's attention — without falling into the patterns that flag as AI-generated.

> **Where this skill sits in the pipeline.** This skill owns *script craft* — the line-level rules that govern every sentence the viewer eventually hears. It is consumed by `video-production-workflow` (methodology) and `parallax-video` (orchestrator) at the script-writing phase. The workflow skill decides *when* and *against what timeline* a script gets written; this skill decides *how each line is built*.

## Style axis

Every Parallax script declares `style:` and `complexity:` in its frontmatter. The style determines which sections of this skill apply.

| Style | What it is | Complexity tiers |
|---|---|---|
| `use_case` | Persona × moment × deliverable. Interpretation-driven VO: show on screen, interpret in voiceover. | Tier 1 (`single_feature`), Tier 2 (`workflow_chain`), Tier 3 (`hero_playbook`) |
| `instructional` | Point-and-click utility content. Description-driven VO: describe the screen as the viewer follows along. | Tier 0 (`utility`) |
| `intel_brief` | **Paused** for the current overhaul. See the stub at the bottom of this file. | — |

The **Universal craft** section below applies to every style. The `use_case` and `instructional` sections layer style-specific rules on top.

---

## Universal craft — applies to every script style

### Voice

Composite blend:

| Writer | Take | Leave |
|--------|------|-------|
| Michael Lewis | Clarity for non-specialists, scene-setting | Occasional looseness with technical precision |
| John McPhee | Structural discipline, respect for technical detail | Extreme length |
| Christopher Hitchens | Word-level precision, confident assertions | Polemical heat |
| Joan Didion | Rhythm, control, the telling detail | Minimalism that now reads as AI-clean |
| Warren Buffett | Conversational authority, accessible complexity, dry self-deprecation | Folksy excess |

### Connective Tissue

Listeners should not have to infer how two sentences relate. Use: but, however, although, yet, then, and, so.

Without connectives, prose feels like swimming through sand — the ear does extra cognitive work at every sentence boundary, and in spoken delivery that gap reads as dead air.

### Hard Constraints

- No hedge phrases: "it's worth noting," "it's important to remember," "it bears mentioning."
- No "not just X, but Y" constructions (the single most flagged AI pattern).
- Em-dashes are fine when they earn emphasis, rhythm, or an aside that parentheses would flatten. Don't sprinkle them for pseudo-sophistication.
- AI-tell transitions to avoid: "Furthermore," "Moreover," "Additionally," "In conclusion." Use conversational connectives ("but," "and," "so," "then") instead.
- No bullet points in spoken lines — scripts are prose, read aloud.
- Sentence rhythm is **phase-aware**. At **Phase 5 (write)** write punchy by default — short data-callout fragments are safe because actual post-zoom timing isn't known yet. At **Phase 6a (polish)** the rendered preview reveals the actual breathing room, and you restore full sentences in the connective / interpretive beats. Earned fragments stay on data callouts and hero shots (*"Composite at five. Quality and Tactical, ten. Value, three."*); full interpretive sentences carry connective and analytic work (*"The pattern tells you the trade: you pay up for the compounder, and you go in with eyes open on the multiple."*). If a polished draft is ≥60% fragments, it's reading as telegraph — restore full sentences. Project-local mix target for polished use_case drafts: ~40% data-fragment + ~35% short-sentence + ~25% full-sentence. Cross-referenced with `video-production-workflow/` Hard Rule #6 (a/b/c) + Phase 6a.
- Specifics over generalities: numbers, names, dates wherever possible.
- Active voice by default; passive only for deliberate emphasis.

### Banned Words

delve, tapestry, landscape (metaphorical), nuanced, multifaceted, underscore (as verb), crucial, vital, realm, myriad, embark, straightforward, game-changer.

### Quality Checks (universal, #1–#4)

Apply to every draft regardless of style:

1. **Earn every sentence.** Assume the viewer is skeptical and busy. Earning a sentence can mean carrying a point with color or a confident assertion, not just transmitting information — a line like "Sequential models can't do this" earns its place. Padding, hedging, and decorative prose do not.
2. **Concise ≠ clipped.** Don't strip sentences down so far that the script reads like a time-pressed info drop. Short declaratives are fine in rhythm, but a script made entirely of them reads as robotic. Vary length, keep the connective tissue, let a line breathe when it's carrying a beat.
3. **When the budget is tight, cut beats — not words per beat.** A tight word count is a triage constraint, not a license to turn every sentence into a fragment. Prefer dropping entire beats at full rhythm over keeping all the beats in clipped form. If the master plan's beat sheet genuinely can't fit the budget, raise it with the user — don't silently compress every line. Widening the recording is always a legitimate alternative to dropping beats.
4. **Use the series to decide which beats to cut.** The videos form a series, not standalone pieces. Before cutting a beat from a video, check whether the master plan covers the same territory elsewhere. Beats that overlap with other videos' coverage are cheaper to drop — the viewer will encounter that content when they watch the adjacent demo. Beats unique to this video are load-bearing; cutting them leaves a gap the series won't fill.

*(Removed 2026-05-14: previous Quality Check #5 was "if a line sounds like marketing, rewrite it as a memo." Carried over from an older Chicago Global Voice skill. The 20-video catalogue **is** marketing content — sandbagging the copy into pure-memo register isn't the goal. Numbering preserved: #5 retired, #6 + #7 unchanged below.)*

(Additional style-specific Quality Checks #6 + #7 for `use_case` style live below.)

### Writing for the Ear

- **Read drafts aloud before delivery.** If a clause trips you on first listen, rewrite it. A line can be grammatically clean and still be hard to parse by ear.
- **Contractions are usually better.** "Don't," "can't," "here's" sound natural; the formal equivalents read stiff in a voice actor's mouth.
- **Silence counts.** A beat of silence after an important line adds weight. Don't pack every second with words — the space between sentences is part of the script.
- **Rhythm test.** Mix sentence lengths deliberately. Three shorts in a row need a longer one next, or the piece reads staccato. AI tools default to fragmented sentences; catch it on the read-through.
- **Pacing anchors.** A human voice actor averages ~130 wpm. AI TTS runs ~150–170 wpm. Per ~90 seconds of content, aim 200–225 words; per ~60 seconds, 130–150.

### Source-of-truth grounding (hallucination check)

Every stat, product fact, capability claim, or methodology reference in a script must trace to one of:

- **The master plan** (`Parallax Video Plan - MASTER.md`) — for series-level beat sheets and pre-cleared vault stats
- **The recording itself** (`use_case` / `instructional` styles) — for what's literally on screen
- **The source document** (`intel_brief` style — paused) — for the user-supplied newsletter or market data
- **The `parallax-obsidian/` vault** at the project root — the canonical Parallax knowledge base (product facts, methodology, positioning, investor-letter voice)

If a sentence in the script makes a factual claim that can't be cited to one of those four sources, it doesn't go in. This is the single most important rule for accuracy — viewers and clients will catch hallucinated numbers and stale capability claims faster than craft issues, and a wrong stat in a published demo is a credibility hit Parallax can't afford.

**High-leverage vault folders for grounding:**
- `parallax-obsidian/01-Product/` — product facts
- `parallax-obsidian/02-Methodology/` — methodology + framework + tactical overlays
- `parallax-obsidian/04-Marketing/` — positioning, key differentiators, competitive landscape
- `parallax-obsidian/06-Investor-Letters/` — voice/tone reference (read for voice, do not author from)
- `parallax-obsidian/00-Index/Parallax MOC.md` — navigation hub

**Refresh** the vault before drafting if the upstream repo has changed: `cd parallax-obsidian && git pull`.

---

## Style: `use_case` — interpret on screen

The `use_case` style covers Tier 1 (single-feature), Tier 2 (workflow-chain), and Tier 3 (hero-playbook) videos. Every one of these is **persona × moment × deliverable** — even Tier 1. A use_case video is NOT "demo the tool with a persona prefix"; it's *"[specific persona] at [specific moment] producing [specific deliverable] using [tool / tool chain]."*

A video runs two narratives in parallel — what the eye sees, what the ear hears. They must *complement*, not duplicate. The single most common failure mode: **VO that narrates the visual is the top redundancy trap.**

### Operating rule: show on screen, interpret in voiceover

- If the viewer can read a number off the screen, the VO shouldn't list it — it should say what the number *means*. "Four-point-nine trillion market cap" is description. "Fifth-largest company on earth, ninety percent of revenue from one segment — that concentration is the story" is interpretation.
- VO must still connect to the visuals, not orphan from them. Total disconnect ("VO talks about X while the screen shows Y") loses the viewer. The rule is interpret-while-anchored, not ignore.
- **Subject-matching is a hard constraint.** The rule is about LAYER (description vs. interpretation), NOT about TOPIC. When the spotlight is on the Value row, the VO talks about Value — just at the interpretation layer, never at the description layer. The VO never drifts to a different on-screen subject than what's spotlit; the beat sheet ties timing to topic precisely so this can't happen accidentally. If a draft has the spotlight on X and the VO on Y, that's a beat-alignment failure (Hard Rule #1) — not a creative choice.
- **Coordinated depths within a topic.** During an annotate hold, four layers all carry the same subject at different depths: the recording shows the raw content, the spotlight names "look here," the VO delivers the thesis sentence (*"Value says it's expensive — and it is"*), and the panel pitches the capability framing (*why* a buyer wants this kind of content in every brief). All four sync on the same topic; only the depth changes.
- Differentiation lines pay rent. A well-placed comparison — "what used to be twenty minutes of Bloomberg pulls and broker reports is one orchestrated batch" — makes competitors irrelevant by reframing the evaluation criteria. The MUD framework from product marketing calls this Meaningfulness + Uniqueness + Differentiation.
- Gut check for every line: *if the viewer had the video on mute, would this line still have value as commentary?* If yes, you're adding signal. If no, the visual is already doing the work — cut or rewrite.

Quick reference:

| Description (⚠️ cut) | Interpretation (✓ keep) |
|---|---|
| "Quality at 10, Tactical at 10, Momentum at 7, Value at 3." | "Quality and Tactical pinned at ten. Momentum rolling. Value says it's expensive — and it is." |
| "Revenue up 69% to $68 billion." | "Sixty-nine percent year-over-year at this scale isn't normal growth. It changes the valuation question." |
| "59 analysts, mean target $269." | "Fifty-nine analysts, one sell. The consensus spread you'd expect on a consensus buy." |

Sources this section draws on: [Industrial Scripts](https://industrialscripts.com/voice-over-narration/), [Final Draft](https://blog.finaldraft.com/narration-how-voiceover-can-sometimes-make-a-script-better), [MotionCue](https://motioncue.com/product-demo-videos/), [Contrast demo script guide](https://www.getcontrast.io/learn/product-demo-script), [MUD framework / Product Marketing Alliance](https://www.productmarketingalliance.com/identifying-product-differentiators-mud-framework/), [Celtx AV Script guide](https://blog.celtx.com/essential-av-script-template-for-better-video-scripts/).

### Operating rule: moment-anchored framing — role labels banned in VO

Per **overhaul.md Phase 1 Q4** (locked 2026-05-12). Every use_case video anchors on `primary_persona × primary_moment × deliverable` — but **the persona role NEVER appears in the VO copy.** The *moment* carries the framing: the trigger, the stake, the deadline. The verbs and stakes self-identify the user, making the role label unnecessary and (worse) distancing.

**Frontmatter contract for use_case scripts:**

- `primary_persona:` — structural metadata. Drives beat selection, value-angle rotation, tool-chain choice. **Never read aloud in VO. Never appears in lower-thirds.**
- `primary_moment:` — the in-VO situation phrase. The trigger + stakes language that opens the script. Picks a moment whose verbs self-identify the user.
- `secondary_personas:` (optional) — other personas the video plausibly addresses without re-framing. Listed for catalogue coverage tracking; never named in the VO.

**Examples (right vs wrong):**

| ❌ Role-labeled (banned) | ✅ Moment-anchored (correct) |
|---|---|
| "If you're an RM and a client just asked about Iran exposure..." | "Client just texted about Iran. Ten minutes before your next meeting." |
| "As a portfolio manager preparing for the IC, you..." | "Investment committee tomorrow. Every position needs a defense." |
| "When an analyst gets stuck between buy and pass..." | "Stuck on a name. Buy or pass?" |
| "A family-office analyst onboarding a new principal..." | "New principal. Multi-ETF book just landed. One-page exposure read by EOD." |

**Why the rule exists:** PM, CIO-as-practitioner, RM, and analyst workflows overlap heavily on the same Parallax tools — the click-flow is often identical, only the top-of-moment framing shifts. A video that labels its persona excludes all the others from feeling addressed. A video that opens on the moment (verbs + stakes) lets every persona who lives that moment see themselves in the demo.

**Persona-locked language carve-out.** Some moments are so role-specific that the natural vocabulary IS the role. **This is not a violation of the rule** — it's the moment doing its job. Examples:

- Compliance moments: *"Shariah-mandate name. Sign-off before close."* (the "Shariah-mandate" and "sign-off" vocabulary is compliance-coded by content, not by typecasting)
- Quant moments: *"Reproduce the regime-window analysis without look-ahead bias."* (the "regime-window" and "look-ahead bias" vocabulary is quant-coded by content)

The rule is *"don't typecast with role labels"* — it's not *"scrub all professional vocabulary."*

**Tier scaling.** The rule applies across all use_case tiers (1 / 2 / 3):

- Tier 1: situation gives the script a real moment to write to. Role becomes unnecessary because the moment is concrete enough.
- Tier 2: workflow is structurally persona-locked (only one persona has THIS workflow). The role becomes obvious from the situation itself without needing a label.
- Tier 3: the persona's full event-response artifact IS the video. The persona doesn't need naming because the deliverable speaks for them.

`instructional` style has no persona anchoring at all — audience-general, point-and-click. The moment-anchored rule doesn't apply to instructional content.

### Operating rule: natural-language prompts in the VO; slash commands annotated, never spoken

Per **Principle #9** in `references/production-principles.md`. The demo user types a **natural-language prompt** into the AI client — *"Run a deep dive on NVDA using Parallax"* — not `/parallax:deep-dive NVDA`. Slash commands and underlying MCP tool names appear only as on-screen annotations: lower-third labels, underline-highlights, callouts. **The VO never reads a slash command aloud.**

Why: portability (only Claude Code supports slash commands; 3 of 4 supported clients are NL-only and reach the same tools via natural language), buyer-facing tone (slash = developer; NL = product), and register match with the chat UI on screen.

**Vocabulary mapping — use this for both VO copy and LT eyebrow / headline text:**

| What's invoked under the hood | What the VO says (NL prompt + interpretation) | What the LT can name (product module) |
|---|---|---|
| `/parallax:stock` | *"Plain English in. Eight parallel calls out."* / *"Quick read on the name."* | Stock Report / Research Brief |
| `/parallax:deep-dive` | *"Eleven parallel calls. One brief."* | Deep Dive |
| `/parallax:portfolio` (basic scores) | *"Score every name in the book."* | Analyzer |
| `/parallax:portfolio` (ETF look-through) | *"Through the ETFs. To the underlying."* | ETF Analysis |
| `/parallax:rebalance` | *"Trade list. Before-and-after factor profile."* | Analyzer (Rebalance) |
| `/parallax:scenario` | *"Stress the position. Single scenario."* | Impact Analysis |
| `/parallax:macro` | *"Single-country macro read."* | Macro Intelligence |
| `/parallax:screen` (Shariah) | *"Shariah screen against the full universe."* | Shariah Screen |
| `/parallax:screen` (forensic earnings) | *"Forensic earnings quality. Eight quarters back."* | Forensic Quality |
| `/parallax:universe` | *"Build a basket from the thesis. Plain English in, scored universe out."* | Builder |
| `/parallax:investor` | *"Five legendary investors. One name."* | Investor Profile |
| `/parallax:etf` | *"Holdings. Overlap. Factor profile."* | ETF Analysis |

**Banned in VO** (use_case style only): any phrase that reads the slash command aloud — *"Run /parallax:stock..."*, *"Slash command. Stock NVDA."*, *"Type forward-slash parallax colon..."*. The VO and the recording carry the same register; CLI vocabulary on top of a chat UI is a register break.

**Instructional carve-out.** This rule applies to `use_case` style only. `instructional` style MAY type the slash command when it IS the action the viewer must reproduce (e.g., a sanity-check step: *"Type `/parallax:stock AAPL` to verify the plugin loaded."*). See the `instructional` style section below for the carve-out's full scope.

### Operating rule: typed-prompt register — formal, imperative, professional

The typed-on-screen NL prompt must read like a professional desk query, not a casual chatbot conversation. Parallax is institutional-grade tooling (RM / PM / Analyst / Compliance audience); the prompt vocabulary should match that audience's working register.

**Style requirements** (all 16 use_case videos):

- **Imperative or noun-phrase opening.** Start with the action (*"Run…"*, *"Prepare…"*, *"Stock brief on…"*) or the workflow type (*"Macro event response:"*). **Never** with first-person throat-clearing (*"I keep hearing…"*, *"Can you give me…"*, *"I'm wondering if…"*).
- **No contractions.** "Oil at $82/bbl" not "oil's at $82". "I am" not "I'm" (and prefer to remove the "I" entirely in favor of imperative voice). "Cannot" not "can't".
- **Precise parameters where natural.** *"oil at $82/bbl with Hormuz tail risk"* not *"oil's at $82 and Iran stuff"*. *"start_date = 2021-01-01"* not *"the post-COVID period"*. *"high-quality US industrials, small-mid cap"* not *"some good industrial names"*.
- **Professional vocabulary.** *"position thesis"*, *"factor profile"*, *"vulnerability map"*, *"composite score"*, *"redundancy check"* — desk language. Avoid *"hype"*, *"worth it"*, *"actually good"*, *"interesting"*.
- **Scope the deliverable cleanly at the end.** *"PDF for tomorrow's meeting"*, *"CSV export"*, *"single-page principal-ready output"*, *"before Monday open"*.

**Three reusable templates** (most prompts fit one of these):

1. **`[Workflow type] on [target]. [Parameters / scope]. [Deliverable / deadline].`**
   - *"Stock brief on NVDA — client query, need a defensible read on the position."*
   - *"Forensic earnings quality analysis on [TICKER]: 8-quarter trajectory, transcript language differential, traffic-light verdict."*

2. **`[Action verb] [scope]: [parameters list]. [Deliverable].`**
   - *"Universe build: high-quality US industrials, small-mid cap, momentum tailwinds, exclude defense. Scored basket with redundancy check."*
   - *"Run regime-window backtest, start_date = 2021-01-01, point-in-time evaluation. Need factor performance, IC stats, CSV export."*

3. **`[Context phrase]: [parameters]. [Need clause].`** *(event-response / contextual triggers)*
   - *"Macro event response: weekend Iran development, oil at $82/bbl with Hormuz tail risk. Vulnerability map across the book plus factor-screened contrarian setups before Monday open."*

**Before / after — getting the register right:**

| ❌ Conversational (too casual) | ✅ Formal (professional) |
|---|---|
| *"I keep hearing about NVIDIA — quick rundown on whether it's worth the hype?"* | *"Stock brief on NVDA — client query, need a defensible read on the position."* |
| *"Iran hit the wires over the weekend. Oil's at $82. I need a vulnerability map…"* | *"Macro event response: weekend Iran development, oil at $82/bbl with Hormuz tail risk. Vulnerability map across the book…"* |
| *"Quick score on [ticker]? Considering adding to the book."* | *"Stock brief on [TICKER]. Evaluating for position add — composite score, factor pillars, 52-week trajectory."* |
| *"Pull the book. I need to defend every name in tomorrow's IC."* | *"Investment committee preparation — full book defense. Per-position composite, factor evidence, methodology drilldown for audit trail."* |
| *"Onboard this family's equity book. ETF look-through, factor profile, macro context. One page."* | *"New client onboarding: full equity portfolio analysis with ETF look-through, factor decomposition, macro regime overlay. Single-page principal-ready output."* |

**Instructional carve-out applies here too:** `instructional` style videos (I1-I4) can use simpler / more casual typed prompts since they're teaching the viewer, not modeling a working-day query. *"Run a quick brief on Microsoft."* is fine for I2's first-brief demo because the viewer IS that user. The formal register applies to `use_case` videos only.

### Quality Checks #6 + #7 (use_case-specific)

In addition to the universal Quality Checks #1–#4:

6. **Every beat states value explicitly.** For each beat in the script, the VO must answer all three questions: (1) *what is this on screen*, (2) *what problem does it solve*, (3) *why does it matter to me*. Question 3 is the most commonly dropped — it's the one analyst audiences evaluate tools by. Implicit "the viewer will infer the value" is not enough; state it as a labelled clause. See **"Every beat answers three questions"** + **"The value-framing menu"** below.
7. **Rotate value angles across beats.** Per ~90 seconds of content, draw from 5–7 of the 12 angles in the value-framing menu. Two consecutive beats leaning on the same angle = rewrite one. Repetition of the same angle is the failure mode that makes a script feel like one note repeated.
8. **Lower-thirds earn their place — five layered constraints; quality + adaptive density, not arbitrary count.** *(Revised 2026-05-14 — the earlier hard 2-4 cap was too rigid; longer videos and content-density rhythm need a flexible rule.)*

   **Layer 1 — Selection.** Each LT card must introduce **one of three things**:
   - **(a)** A vault-verified stat with a *specific number* the VO doesn't recite (e.g., *"ICIR 4.10 · 62K listings · 48 markets · +5.8%/yr"*)
   - **(b)** The single most important *conclusion* the viewer cannot read off the screen (e.g., *"Exceptional business at a rich multiple — factor score cooling"* — the brief shows the data; the LT names what it MEANS)
   - **(c)** An *orientation cue* during a low-content stretch where the recording is still loading / processing / silent and the viewer needs anchoring (e.g., V1's open LT *"Twenty minutes of research, in one prompt."* — the brief hasn't loaded yet; tool calls firing in the chat sidebar; LT keeps the viewer oriented to the *deliverable they're about to receive*, not the system's internal mechanics). **Note:** orientation LTs are subject to QC #9 below — the framing must be customer-perspective ("twenty minutes of research" = time saved, audience-relevant) and never system-mechanic ("eight parallel skill calls" = builder vocabulary — rejected per 2026-05-19 feedback).

   Cards that restate the VO or the visible on-screen text get cut. **The (c) carve-out is narrow:** orientation LTs are legitimate ONLY when the recording is genuinely low-content AND the LT helps the viewer parse what's happening. Promotional LTs ("Welcome to Parallax") fail (c) because they add no orientation value — they're just brand noise.

   **Layer 2 — Target count scales with video length, not a hard cap.**

   | Tier | Duration | Target LT count |
   |---|---|---|
   | Tier 1 (single-feature) | 60–120s | 2–5 LTs |
   | Tier 2 (workflow chain) | 2–3 min | 3–7 LTs |
   | Tier 3 (hero playbook) | 3–5 min | 4–10 LTs |

   These are *target ranges*, not caps. If content genuinely earns more (e.g., a Tier-3 hero with 11 distinct reveals across scenario + macro + screen + thesis), allow more. If fewer earn their place, ship with fewer. Don't pad to hit the target floor; don't cut for the sake of the ceiling.

   **Layer 3 — Content-density rhythm, not uniform spacing.** LTs cluster where insight density is highest. Don't space them at fixed intervals (e.g., one every 20s). Legitimate distribution patterns:

   - **Front-loaded** — orientation LT during a slow start (loading, processing, parallel calls firing)
   - **Back-loaded** — conclusion cluster (score / trajectory / bottom-line in sequence near the end)
   - **Mixed** — orientation + conclusion cluster (no standalone vault-stat LT — see vault-stat inclusion test below)

   **Note: vault-stat LTs are not a default category.** The 2026-05-21 decision ("Vault stats integrate, not narrate") removed standalone vault-stat LT graphics (the four-stat ribbon pattern) from use-case video drafts. Vault stats now integrate into VO lines that explain specific output moments — they don't earn their own LT card. The exception: if a stat is being shown on the screen as part of the *recording's actual content* (e.g., the brief's Analyst View section literally displays "61 analysts: 10 Strong Buy / 48 Buy..."), an LT can underline-and-emphasize that on-screen number — but the LT is annotating a visible element, not standing alone as credibility.

   **Layer 4 — Attention floor (no LT drought).** No stretch longer than ~40 seconds should pass without **some** on-screen graphic emphasis — LT, zoom callout, annotate-spotlight, or other overlay. But this is satisfied if the recording itself is carrying visual interest:
   - Parallel calls firing visibly ✓ counts as visual variation
   - A score panel rendering line-by-line ✓ counts
   - A scrolldown through a brief ✓ counts
   - Static screen with VO doing all the lifting ✗ — earn an LT or a zoom

   If a 40s stretch has nothing — recording is quiet AND no LT/zoom — that's a content problem upstream of the LT decision. Either reframe a beat to earn the emphasis, or revisit recording pacing. **Don't force an LT to satisfy the floor; fix the underlying content gap.**

   **Layer 5 — Post-write self-check.** After drafting LTs, run two tests on each card:
   - **Maps to a VO line:** for each LT, identify the specific VO line it reinforces. If no line maps to it, cut.
   - **"Would removing this make the video weaker?"** If removing the card doesn't make the video weaker (viewer would still understand the beat, the VO carries it alone, no orientation/insight is lost), cut.

9. **Customer's-chair framing — every line speaks from the buyer's chair, not the system's.** Per `references/production-principles.md` → *Customer's-chair framing*. The audience for `use_case` content is the buyer named in `primary_persona` (MFO / RIA / wealth advisor / PM / analyst). They evaluate the demo by what it gives them at the moment named in `primary_moment` — never by what the system does internally. Apply this check to **every** authored line: VO, LT eyebrow, LT headline, LT stats, annotation panel eyebrow, annotation panel headline, annotation panel body, annotation panel stats, and (when authoring) MASTER's per-video Highlights.

   **Reject (engineering-perspective — never appears in any copy):**
   - *"Eight parallel skill calls"* / *"Ten tools fire at once"* — capability boast in builder language
   - *"MCP tool invocations"* / *"Agent orchestration"* / *"Skill calls fire"* — technical vocabulary the buyer doesn't speak
   - *"Watch as N things happen in parallel"* — mechanic-as-narrative
   - Anything that asks the viewer to imagine the system's plumbing to understand the value
   - Counting internal operations ("six MCP calls," "thirteen retrievals") even when factually true

   **Require (audience-perspective — every line should match one of these molds):**
   - **Outcome** — *"Twenty minutes of research, in one prompt."* — what they get
   - **Stakes** — *"Defensible read before the meeting."* / *"Citation-ready for the client."* — what's on the line
   - **Workflow-fit** — *"Score, trajectory, bottom line — in 30 seconds."* / *"Under 60s, before your next call."* — fits the buyer's day
   - **Methodology-credibility** — *"Peer-reviewed factor model."* / *"62K listings, 13-year out-of-sample."* — proof the answer holds up

   **Mute test for engineering-talk.** When in doubt, ask: *"If the viewer watched this LT/panel/VO with audio off and no Parallax background, would the line read as 'something this tool DOES for me' or 'something this tool IS internally'?"* If the answer is the latter, rewrite. The viewer doesn't care that the system runs eight things in parallel; they care that they get a defensible brief in 30 seconds.

   **Instructional carve-out.** Does not apply to `style: instructional` (I1–I4). Tutorial audiences ARE the technical operator setting up the plugin, and system mechanics framing is the right register there. *"Type `/parallax:stock AAPL`, press enter, watch all eight skills fire — that confirms the plugin loaded across all four MCP clients."* is correct framing for an instructional. The carve-out is narrow: only when the system mechanic IS the step the viewer must reproduce.

   **Why this is QC #9 and not #1.** This rule constrains the *vocabulary* of QCs #6–#8 (every-beat-states-value, rotate-value-angles, LT economics). All three of those checks specify *what* to express; #9 specifies *whose vocabulary* to express it in. A beat can pass #6 (states value) and still fail #9 (states it in builder-speak). Run #9 last during self-review — it's the lens you sweep across the already-drafted copy.

### Vault-stat inclusion test (use_case-specific, locked 2026-05-21)

Vault stats (ICIR, Sharpe, years live, listing counts, market counts, alpha-signal counts, selection-return numbers) appear in use-case scripts (V1–V16) **only when they pass the two-mold inclusion test**:

1. **Problem-solving mold** — the stat explains *why* the spotlit output element solves the viewer's client-facing problem. Stat is anchored to a specific on-screen content moment; without it, the viewer fails to understand what makes *that specific* output element defensible.
2. **Why-can't-Claude mold** — the stat names what Parallax has that an LLM-alone can't produce, anchored to *this* output. Without the stat, the analytic claim (e.g., "this is a repricing, not a thesis break") has no basis.

**Standalone "credibility ribbon" beats are forbidden.** No VO beat reciting stats outside of a specific output moment. No LT graphic displaying a stat row (`{value, label}` quadrupled) without a corresponding on-screen content element being annotated. Stats appear *integrated*, not *narrated*.

**Authoring test before including any stat:** *"If this stat weren't in the script, would the viewer fail to understand what the spotlit output element does or why it's defensible?"* If yes → keep (integrated, anchored to its moment). If no → drop (it's narrating credibility, not explaining the output).

**Integration patterns:**

| Stat | Example integration (problem-solving mold) | Example integration (why-can't-Claude mold) |
|---|---|---|
| *13 years live* | *"The trajectory's read against thirteen years of factor history — so we know this is a repricing, not a thesis break."* (Anchored to the trajectory cell.) | *"Thirteen years of out-of-sample performance is what makes this pattern recognizable in the first place — Claude couldn't compute this trajectory from a prompt alone."* (Less natural; usually problem-solving works better.) |
| *62,000+ listings / 48 markets* | *"Value at three — peer-ranked against AVGO, AMD, ARM and the broader sixty-two-thousand-listing universe."* (Anchored to the Value row; makes "peer-adjusted" concrete.) | *"Claude can read a stock page; it can't peer-compare against sixty-two thousand listings."* (Works for the panel context.) |
| *30+ alpha signals* | *"Quality at ten — composite of thirty-plus signals across earnings, balance sheet, and forensic accounting."* (Anchored to the Quality cell.) | (Less natural standalone.) |

**Stats that don't integrate (migrate elsewhere):**

| Stat | Why it doesn't integrate | Where it lives |
|---|---|---|
| *ICIR 4.10* | Domain jargon — requires its own explanation of what "Information Coefficient" means. Can't integrate into a 3-second moment. | V9 Deep Dive, V14–V16 hero playbooks, or out-of-slate marketing (one-pagers, methodology decks, pricing page) |
| *Sharpe 2.34* | Same — Sharpe ratio needs framing. | Same as ICIR |
| *+5.8%/yr selection return* | "Selection return" needs definition (alpha vs benchmark, gross vs net). | Same |

**Inheritance from `references/production-principles.md` → "Vault stats integrate, not narrate."** That principle states the rule; this section is the operational test for applying it during script drafting.

**Cross-reference:** Customer's-chair framing (QC #9) — same family of discipline. QC #9 rejects engineering-vocabulary; this section rejects ornamental-credibility. Both push toward: *every line either does analytic work for the buyer or doesn't appear.*

### Panel content authoring (use_case-specific)

Annotation panels are the right-side blocks that appear during `mode: "annotate"` zoom holds — paired 1:1 with each spotlight. They have their own content contract distinct from LTs and VO.

**Format contract:**

```yaml
annotations:
  - id: ap1                              # 1:1 with zoom directive's callout_number
    in_recording_t: ...                  # filled after zoom.py prints seg timing
    out_recording_t: ...
    callout_number: 1
    panel:
      eyebrow: "VALUE FACTOR · WHAT IT GIVES YOU"     # 4-7 words, all caps, dot-separator framing
      headline: "A peer-adjusted answer to 'isn't NVDA expensive?'"   # 8-15 words, one sentence
      body: |
        Two-to-three sentences. The capability framing.
        Why a buyer adopts this kind of content in every brief.
      source: "Source: Parallax Fundamentals"        # canonical product name (required, see vocabulary below)
      badge: "Peer-adjusted"                          # locked vocabulary tag (required, see below)
```

No `stats` field on panels. The spotlight on the recording already shows the specifics; the panel pitches the *value* of having that segment, not the specifics of *this particular* output. (LTs carry stats; panels don't.)

**Job:** Each panel pitches the **capability / workflow / stakes value** of having that segment of brief, framed for the buyer named in `primary_persona`. NOT a literal interpretation of the specific numbers on screen. The viewer reads the panel and thinks *"okay, I understand why Parallax shows me this — I see what it gives me for my client conversations."* — not *"okay, here's what 8.5 → 5.0 specifically means."*

**Three rhetorical shapes — pick one per panel, rotate across the video:**

| Shape | What it does | Eyebrow pattern | Headline opener pattern |
|---|---|---|---|
| **Capability** | Names what the tool gives the buyer | `[SEGMENT] · WHAT IT GIVES YOU` | *"A [adjective] answer to..."*, *"[Capability] every brief..."*, *"[Outcome], on demand..."* |
| **Workflow** | Situates the segment in the buyer's day | `[SEGMENT] · WHY IT EARNS ITS PLACE` / `WHY THIS ROW MATTERS` / `WHY IT'S WHERE IT IS` | *"[Capability], every name, every brief."*, *"[Format], sourced, ready for the meeting."* |
| **Stakes** | Names the conversation/decision the segment serves | `[SEGMENT] · THE CALL YOU WILL HAVE` / `THE QUESTION BEHIND THE CALL` / `THE ANSWER TO "..."`  | *"Win the [scenario] before it starts."*, *"Was it [option A] or [option B]?"*, *"[Decision] — with the [evidence] compressed."* |

**Rotation rule:** No two consecutive panels in the same shape. For a 3-panel video like V1.2, a natural rotation is **capability → stakes → capability** or **capability → workflow → stakes** — anything except all three same shape. (Six-panel videos can repeat shapes but should still not have two-in-a-row.)

**Why panels need a shape rotation when LTs and VO don't:**

- VO has the 12-angle rotation (QC #7) AND it's interleaved with recording activity / audio variation / silence — three consecutive sentences in the same rhetorical stance read fine because surrounding context varies.
- LTs are spaced ~20-40s apart with different *jobs* (vault stat / conclusion / orientation) — they naturally vary because the jobs differ.
- Panels are all the same JOB (interpret-the-spotlit-segment), all in the same FORMAT, all in the same temporal cluster (V1.2 has three panels stacked 50-95s into a 100s video). Without a shape rotation rule, three panels in a row read like the same template re-skinned three times.

**Subject-matching to the spotlight is a hard constraint.** Each panel's topic is the spotlit content; the rhetorical shape is the angle on that topic, not a license to drift. For V1.2: ap1 is about the Value factor (z1 spotlights Value row); ap2 is about the 52-wk trajectory (z2 spotlights Total trajectory); ap3 is about the Bottom Line verdict (z3 spotlights the full Bottom Line section). Different shapes, three different angles on three different topics — but each panel's topic locks to its paired spotlight.

**`highlight_region_pct` covers the WHOLE conceptual unit, not a partial phrase.** When authoring zoom directives for `mode: "annotate"`, the rect must enclose the entire spotlit content the panel pitches the value of — not just the opening sentence or top half. The spotlight only brightens what's inside the rect (plus a small blur halo); content outside falls into the dim. If the panel pitches "the Bottom Line verdict," the rect covers the Bottom Line header AND the whole paragraph, not just line 1. If the panel pitches "the Value factor," the rect covers the Value row across all four columns, not just the score cell. Caught 2026-05-20 on V1.2 z3 where an earlier draft sized the rect to lines 1–3 and user spotted lines 4–7 falling into dim. Rule: size the rect to the OUTER bounding box of the segment, not the inner phrase. **Height interpretation per the three-tier band** (Hard Rule #24, refined by `decisions/2026-05-25-highlight-three-tier-band.md`): tier 1 (specific row/phrase) ≤15%; tier 2 (header+paragraph conceptual unit) 15-25% — cover the unit; tier 3 (>25% multi-paragraph section) → split into sub-annotates with shared panel. The "WHOLE conceptual unit" rule here is the tier-2 case — cover the whole unit even if it exceeds 15%, up to 25%. Verify by sampling a rendered frame at the hold and confirming every text line inside the conceptual unit is visibly bright. See `templates/product-demo/RENDER-GUIDE.md` § "Annotate-mode spotlight" for the underlying spotlight geometry.

**Other rules that apply to panels:**

- **QC #9 (customer's-chair framing) applies to every field** — eyebrow, headline, body. No engineering vocabulary anywhere in panel copy.
- **QC #7 (12-angle rotation) applies to panel body content** — pick a value angle for each panel and don't repeat across panels. (Independent of shape rotation; you can have a capability-shape panel about defensibility OR about time savings — shape is the stance, angle is the underlying value.)
- **Panel body is budgeted against the paired hold duration** (Hard Rule #25 in `video-production-workflow/SKILL.md`). `min_hold = max(3.0s, body_word_count / 5.0 + 2.0s)`. At 300 wpm fluent-skim reading + 2s ease overhead, a 10-word body needs 4.0s, a 25-word body needs 7.0s, a 40-word body needs 10.0s. Pacing target is viewer-driven (viewers who want depth pause; viewers who don't don't get stuck) — comprehension-on-first-pass isn't required. Drafting choice: either keep body tight enough that the paired sub-annotate's `duration` covers it, or consolidate sub-annotates to a shared panel (Hard Rule #24's shared-panel allowance) — total cluster hold sums against the shared panel's body. Default for sub-annotate clusters is the shared panel; per-sub-annotate distinct panels force tight body copy.
- **Source + badge are required** — every panel cites where the data came from. This is the Parallax-credibility move; distinguishes the brief from a generic AI summary. Both fields are drawn from a **locked vocabulary** (no freelancing): freelance values like "Parallax fundamentals" (lowercase) or "Out-of-sample" (not canonical vault language) get rejected at review. See *Panel source + badge vocabulary* below.

**Panel source + badge vocabulary (locked 2026-05-20):**

The `source:` field is `Source: <canonical Parallax product name>`. Four canonical product names, sourced from the vault (`02-Methodology/`, `01-Product/`, `04-Marketing/Key Differentiators.md`):

| Product name | What it covers | Use when the panel pitches… |
|---|---|---|
| `Parallax Fundamentals` | Pricing metrics, peer comparison engine (P/E, P/B, EV/EBITDA, etc.) | Valuation / pricing / peer comparison segments |
| `Parallax Factor Scores` | The 5-factor scoring output (Quality, Value, Momentum, Tactical, Total) including trajectory | Factor-score rows, trajectory cells, ML-composite scores |
| `Parallax Factor Library` | The 30+ alpha-signal library that feeds the factor scores | Methodology-deep-dive segments naming individual signals or signal counts |
| `Parallax Research` | Analyst-consensus synthesis + alternative-data integration (the editorial layer atop the factors) | Bottom Line verdicts, consensus rollups, narrative synthesis paragraphs |

The `badge:` field is one of nine locked tags. Eight methodology-virtue tags pulled from vault language (each ≤ 18 chars to fit the pill); one temporal special-case for verdicts/calls where freshness is the relevant credibility signal:

| Tag | What it signals | Source in vault |
|---|---|---|
| `Peer-adjusted` | Score is relative to peers, not absolute | `01-Product/Scoring System.md` |
| `Regime-adaptive` | Factor weights shift with the market regime | `01-Product/Scoring System.md` |
| `Percentile-ranked` | Score is a percentile in the universe, not raw | `01-Product/Scoring System.md` |
| `Ensemble-based` | ML composite, not single-signal | `01-Product/Scoring System.md` |
| `Academically-grounded` | Signals trace to peer-reviewed research | `04-Marketing/Key Differentiators.md` |
| `Live-tested` | Multi-year live since 2019 fund launch | `04-Marketing/Key Differentiators.md` |
| `Auditable` | Every score traces to underlying signals | `02-Methodology/Vendor-FAQ.md` |
| `Transparent` | Factor weights + signals disclosed | `02-Methodology/Investment Factors.md` |
| `As of <Mon DD, YYYY>` | Date stamp — use when the panel pitches a time-sensitive call/verdict where recency is the credibility signal | n/a (temporal) |

**Pairing convention:** the badge describes the *spotlit segment*, not Parallax broadly. ap1 spotlighting the Value row → `Peer-adjusted` (how the Value cell is computed). ap2 spotlighting trajectory → `Regime-adaptive` (factor weights adapt over the 52-week window). ap3 spotlighting the Bottom Line verdict → `As of Feb 25, 2026` (the verdict's credibility is its freshness). Don't pick a tag that's true of Parallax but not *especially true* of this panel's segment.

**Adding a new tag:** if a future segment doesn't fit any of the 9 locked tags, escalate — propose the new tag, name the vault file/line it's drawn from, and add it to this table in the same commit as the panel that uses it. No silent additions.

**Self-check after drafting panels:**
- For each panel, name the spotlight it pairs with. If you can't identify a 1:1 mapping, the panel is orphaned.
- For each panel, name the *shape* (capability / workflow / stakes) and the *value angle* (from the 12-angle menu). If two consecutive panels have the same shape, rewrite one.
- For each panel, ask: *"Would the body read identically if I swapped the specifics on screen?"* If yes (the body is generic about the capability, not the moment), good. If no (the body decomposes the literal numbers), rewrite — that's specifics, not capability framing.

### Every beat answers three questions

The job of a beat is not to describe what's on screen — it's to make the viewer care. Three questions to ask of every beat:

1. **What is this?** — name the on-screen element (the label / annotation layer)
2. **What problem does this solve?** — the problem-framing
3. **Why does this matter to me (the PM/CIO/RM)?** — the value-framing

The first is necessary — without it the viewer is guessing what they're looking at. The second sets up tension. The third is the one PMs evaluate tools by — *what does this do for ME* — and it's the most commonly dropped of the three.

**Be explicit, not implicit.** Every beat states the value-to-viewer as a labelled clause: *"This means [concrete value]."* Don't rely on the viewer to infer. Cold viewers (PMs/CIOs who don't already know Parallax) won't connect dots that aren't drawn.

| Implicit (rewrite) | Explicit (keep) |
|---|---|
| "Quality never moved. A rerate, not a broken thesis." | "Quality never moved. A rerate, not a broken thesis. **This is hold-or-trim conviction in seconds — not a position you have to research from scratch.**" |
| "Thirteen years live. Sixty-two thousand listings." | "Thirteen years live. Sixty-two thousand listings, out-of-sample. **This is the kind of number you take into an IC and defend on the spot — not a backtest a partner could pick apart.**" |
| "Two-sided. Drop in the memo." | "Two-sided framing — bull case and bear case. **Drop it straight into your CIO memo. No rewriting.**" |

The explicit value statement is usually 1 short clause (5–12 words). Don't pad — punch.

### The value-framing menu

The canonical 12-angle menu lives at **`references/value-framing-menu.md`** — read that file for the full angle definitions, value-line shapes, vault sources, current-batch headline distribution, and the moat distribution caveat. This skill provides the craft rules for *applying* the menu; the menu file is the data.

**Quick reference** (so this skill is self-contained for the basics):

- 12 angles total. Four are **moats** (structural answers to "why not generic AI?"): **#4 Auditability**, **#5 Determinism**, **#10 Failure isolation**, **#12 Unverifiable frame**. The other 8 are standard angles (speed, coverage, defensibility, no-black-box, decision-readiness, workflow-native, live track record, risk-adjusted return).
- Moats trace to `parallax-obsidian/04-Marketing/Auditability and the Unverifiable Frame.md`; standard angles trace to `Key Differentiators.md` + project rules.
- **#12 (Unverifiable frame)** is the sharpest wedge for regulated-wealth audiences: *"unverifiable" lands harder than "hallucinated"* because it's a property of the workflow, not a judgement on the output.
- **#10 (Failure isolation)** has a strict vault meaning — pinning a platform bug to renderer / API / data layer. It's a technical/ops moat; secondary-mention only unless a dedicated engineering-targeted video is built.

**Rotation rule** (per ~90s of content): draw from 5–7 different angles. Two consecutive beats on the same angle = rewrite one. Repetition is the failure mode that makes a script feel like one note repeated. Longer videos rotate through more angles (the absolute count scales with duration, not the rotation discipline).

**Per-video angle assignment** lives in `Parallax Video Plan - MASTER.md` — each video's Highlights section has a `**Primary value angles**` bullet naming its moat headline (if any) plus 2–3 supporting standard angles. Workflow when drafting a script: read MASTER for the per-video assignment, then read `references/value-framing-menu.md` for the angle's definition + value-line shape, then craft the beat lines.

### The "why processing matters" beat — the moat-flavor instance

This is the specific craft guidance for writing beats that pull from angles **#4 Auditability**, **#5 Determinism**, **#10 Failure isolation**, or **#12 Unverifiable frame** in the value-framing menu above. These four are the structural moats — the angles a competitor or generic AI literally cannot match by construction. The "why processing matters" framing is how you write the beat that *demonstrates* one of these moats on screen.

**Three principles this beat must address:**

1. **Why the workflow isn't trivially simple.** Be explicit about the specific processing happening — what's computed, cross-validated, or unified — rather than letting the viewer assume it's surface-level.
2. **What knowledge is embedded — why is this impressive?** Point at the specialized domain knowledge baked into the methodology (factor thresholds from academic papers, AAOIFI ratios, NLP trained on crash predictors, a shared framework across parallel calls, etc.). The reader should infer *this required real domain work*.
3. **What a surface check or Claude-alone interaction would miss.** Articulate the failure mode of the casual approach as a concrete contrast — not as combative framing ("Claude can't do this") but as a positive statement of what the workflow does that the surface alternative doesn't (e.g., "broker reports each run their own methodology and never reconcile").

When all three principles are present in the beat, the angle earns its place. If only one or two land, the beat tends to read as either marketing fluff (only #2) or defensive padding (only #3) — rewrite or cut.

**Two flavors the angle can take:**

- **Depth flavor**: the analysis embeds methodology a quick check would miss.
- **Consistency flavor**: the workflow's load-bearing step isn't the analysis itself, it's that all the analyses share one framework so the output reconciles.

**How to write it:**

- **Specific to this video's workflow.** Not "Parallax does deep analysis." Specific: "AAOIFI screening means three ratio thresholds — 33/33/5 — plus a purification ratio for borderline passes."
- **Position:** usually at or just after the vault-stat moment, where the framework's depth is on screen.
- **Length:** one to two sentences. Earns its place by being concrete.
- **Don't make it compulsory.** Repetition reads as defensive. Pick the videos where the workflow's depth is the actual differentiator and let the other videos earn their place via different beats.

**Trap to avoid:** "Claude alone couldn't do this" framing risks reading as combative. Instead, focus on the *embedded methodology* — what specialized knowledge the workflow brings. The reader infers the differentiation; you don't need to underline it.

### Example: Before and After (use_case)

A draft passage, before and after applying these rules.

**Before (description-driven — narrates the visual):**

> Company info, peer snapshot, scores, outlook, financials, methodology — all firing at once. Quality and Tactical max at ten. Momentum cooled to seven. Value at three — expensive. Composite five-point-nine. Fifty-nine analysts cover it. Mean target two-sixty-nine — thirty-three percent upside. One sell.

**After (interpretation-driven — anchored to the same visuals):**

> What used to be twenty minutes of Bloomberg pulls and broker reports — now one orchestrated batch. Quality and Tactical pinned at ten. Momentum rolling. Value says it's expensive — and it is. Fifty-nine analysts, one sell. The consensus spread you'd expect on a consensus buy.

**What changed:**

- Opening swapped from a tool-list readout to a competitive-differentiation reframe (MUD: Meaningfulness + Uniqueness).
- Factor-grid narration became interpretation ("pinned at ten," "says it's expensive — and it is"). The viewer still sees the scores — the VO now tells them what the scores *mean*.
- Analyst readout replaced by commentary on the spread. The numbers are visible; the VO earns its seconds by pointing out what's notable about them.
- Word count is roughly the same. This is not about compressing — it's about where each word spends the viewer's attention.

### Example 2: The three-question framework, beat-by-beat (use_case)

The "After" version above already does Q1 (label) + Q2 (interpretation). What's still implicit is **Q3 (value-to-viewer)**. The score-panel beat with all three questions explicit, and the value-framing angle named:

> *(Q1 — what is this)* The composite at five-point-nine. Quality and Tactical pinned at ten. Momentum rolling. Value says it's expensive — and it is. *(Q2 — what problem)* That's your triage in one read, no broker-tab juggling. *(Q3 — value-to-viewer, decision-readiness angle)* **You can run it across every name in your book before lunch — and trust the read because the framework is the same on every one.**

The Q3 clause is what was missing in the earlier pass. The viewer no longer has to infer the value-add — it's stated. The angle pulled from the menu is **#7 decision-readiness** with a touch of **#2 coverage**.

Same beat, **moat-flavor** version (pulling from angle **#4 auditability** and **#12 unverifiable frame**):

> The composite at five-point-nine. Quality and Tactical pinned at ten. Value says it's expensive — and it is. *(Q3 — moat angle)* **Every one of these scores has a paper trail. Tool call, timestamp, input. Not a chatbot's confident guess.**

Both versions are valid — choose the angle that fits the beat's natural emphasis. Don't try to cram every angle into every beat.

---

## Style: `instructional` — describe on screen

The `instructional` style covers Tier 0 utility content: installation, configuration, format-flag demos, free-tier walkthroughs. These videos are point-and-click: the viewer is following along to learn how to *do* a specific thing, not to be sold on *why* it matters.

**Instructional videos are NOT persona-anchored.** They don't claim "Jane the RM at 9am" framing. The audience is "anyone who wants to learn this specific feature." This is the one place in the library where audience generality is correct, because the deliverable is *the user's ability to perform the action*, not a piece of analysis. (Use-case videos with persona-and-moment specificity remain the rule everywhere else.)

### Operating rule: describe on screen, in order, so the viewer can follow along

The "show on screen / interpret in voiceover" rule is **inverted** here. The VO mirrors the on-screen action: name the element, describe the click, say what happens next. Cadence is literal-sequential. No flowery interpretation, no "this means X for you" overlay mid-flow — those obscure the literal sequence the viewer needs to follow.

| Description (✓ keep — instructional) | Interpretation (⚠️ cut — wrong style for instructional) |
|---|---|
| "Open Claude Desktop. Go to Settings → Developer. Click 'Edit Config.'" | "Imagine never opening a Bloomberg terminal again." |
| "Paste this JSON block. Save the file. Restart Claude Desktop." | "Three minutes of work and you've got institutional intelligence at your fingertips." |
| "Type `/parallax:stock NVDA`. The brief generates in about sixty seconds." | "Watch as the engine that runs Polaris springs to life." |

### Rules that apply

- All **Universal craft** above — voice composite, banned words, hard constraints, Quality Checks #1–#5, Writing for the Ear, source-of-truth grounding (no fabricated paths / clicks / outputs).
- Pacing anchors apply: per ~90s of content aim 200–225 words, but instructional videos run shorter and tend to be denser (lots of literal steps in sequence).

### Rules that DON'T apply (and why)

- **Quality Check #6 (every beat states value explicitly)** — relaxed. Value-framing collapses to **hook + close only**, not per-beat. Per-beat value clauses would interrupt the click-by-click flow the viewer is trying to follow. State the value once at the open ("In five minutes you'll have Parallax running in any AI client") and once at the close ("That's it — same brief, every client").
- **Quality Check #7 (rotate value angles)** — not applicable. No per-beat angle rotation; the hook + close together pull from at most 2 angles (typically #1 Speed + #8 Workflow-native for install demos; #1 + #2 Coverage for screen demos).
- **"Show on screen, interpret in VO"** — INVERTED to "describe on screen, in order." The VO follows the screen, not interprets it.

### What instructional ISN'T

- **Not "feature demo with a persona prefix."** That's a misuse — Tier 1 single-feature `use_case` videos have personas; instructional videos don't claim one. If you find yourself writing "Jane the RM installs Parallax" — that's wrong; an install demo is style-`instructional`, audience-generic.
- **Not "narrate every pixel literally."** The Earn-Every-Sentence rule still applies. "Click the blue button in the top-right" is the right level; "now your cursor moves over to the right side of the screen and approaches the blue button" is not.
- **Not "ignore the banned words list."** Banned words still banned. Voice composite still applies.

### Examples

*(To be added when the first instructional script lands. **I1** (Install Parallax in any AI client) and **I2** (First Brief in 60 Seconds) are the natural first candidates — see MASTER.md *NEW SLATE — Phase 3 Draft* section for the full I1–I4 spec.)*

---

## Style: `intel_brief` — PAUSED

This style is **paused** for the current overhaul (per `overhaul.md`'s active scope). Intel briefs — anchor-style market wraps with full-frame avatar over a static background, no live product on screen — are not being produced under the persona-and-moment-driven plan.

**Reactivation requires:**
- Defining the full-frame avatar VO model (no on-screen product; VO carries 100% of content load)
- Source-document grounding (the user-supplied newsletter or market data, vs frame-grounding for product demos)
- Building the `templates/intel-brief/` composition family (Claude Design session — see `references/claude-design-to-hyperframes.md`)
- Per-style craft section in this skill (filling in this stub)

When the style reactivates, **Universal craft above still applies unchanged**. The intel_brief-specific rules will go here as a parallel section to `use_case` + `instructional`.

Until then: scripts must not declare `style: intel_brief` — render.py / parallax-video will reject it.
