---
pipeline_type: product_demo
template: product-demo
video_id: V1
style: use_case
complexity: single_feature
title: "Quick Stock Research Brief"
youtube_title: "Quick Stock Research Brief"
target_runtime_seconds: 78   # 5s title + 66.07s recording + 7s outro ≈ 78.1s. Loading segment uses eased zoom-in/out on Progress sidebar with tail-cut technique: keep ±1s around each tick moment (T1=27.033, T2+T3=34.700, T4=38.167, detected programmatically via tools/detect_ticks.py → 1vid_ticks.json), jump-cut between (see recording.path note for full pipeline).
primary_persona: "MFO / independent RIA / wealth advisor"
primary_moment: "Client just texted about a holding. Ten minutes before your next meeting."
secondary_personas: ["PM (pre-trade gut check)", "Analyst (fast read for PM ask)"]
recording:
  path: "screen recordings/V1/1vid_zoomed_route2v2_tickcut.mp4"
  duration_seconds: 66.07   # Loading-segment treatment: eased zoom-in/out on top-right Progress sidebar with TAIL-CUT around each programmatically-detected tick moment. Build pipeline: (1) `tools/zoom.py` reads `1vid_zooms.json` including the `z0b_progress_sidebar` follow directive (source_t=10.2, duration=31.3s, ease=1.5, zoom=2.5, region_pct=[80,0,20,30]) — produces `1vid_zoomed_route2v2_natural.mp4` (88.37s) with 1.5s ease in (10.2-11.7) + held with source playing through 11.7-40.0 + 1.5s ease out (40.0-41.5, just before brief writing begins). (2) `python tools/detect_ticks.py "1vid_scrubbed.mp4" --time-range "19:46" --region-pct "80,0,20,30" --expected-ticks 6 --tail-seconds 1.0 --output 1vid_ticks.json` — detects precise tick moments via frame-diff peak detection (T1=27.033s, T2+T3=34.700s, T4=38.167s). NEVER hand-tune tick timestamps (Hard Rule #20). (3) `ffmpeg` post-process trim+concat with 5 sections: (a) 0–11.7 z0 + 3s loading + ease-in kept; (b) 26.033–28.033 (2s around T1 step-1 tick); (c) 33.700–35.700 (2s around T2+T3 simultaneous tick); (d) 37.167–39.167 (2s around T4 step-4 tick); (e) 40.0–end kept (1.5s ease-out + brief lands + z1/z2/z3). Each tail-cut clip = 1s before tick + 1s after (tick precisely centered, no asymmetric wait time). 3 ticks × 2s = 6s zoom-hold + 1.5s ease-in + 1.5s ease-out + 3s pre-load = 12s loading sequence. To iterate tick timings: re-run detect_ticks.py and update the trim ranges. To iterate zoom region/factor/timing: edit `1vid_zooms.json` z0b directive and re-run step 1.
  scrub_report: "screen recordings/V1/1vid_scrub_report.json"
  zooms: "screen recordings/V1/1vid_zooms.json"
output:
  preview: "outputs/V1/preview.mp4"
  final: "outputs/V1/final.mp4"
avatar_id_override: null    # uses HEYGEN_AVATAR_ID from .env
voice_id_override: null     # uses HEYGEN_VOICE_ID from .env

# Beat structure (recording-relative for LTs; composition-absolute = recording_t + 5)
beats:
  title:
    in: 0.0
    out: 5.0
    eyebrow: "V1 · Quick Stock Research Brief"
    headline: "Twenty minutes of research, in one sentence."
  outro:
    duration: 7.0
    wordmark: "Parallax"
    tagline: "Solve the market."
    polaris_alt: "This isn't a backtest. Polaris has been running on these scores since 2019."

lower_thirds:
  # Recording-relative times below reference the canonical zoomed recording (1vid_zoomed_route2v2_tickcut.mp4).
  # Per Hard Rule #12 in video-production-workflow: re-derive after every tools/zoom.py rerun.
  # 2026-05-19 — z1/z2/z3 converted from hold mode to annotate mode (left-anchored zoom
  # + right-side panel). lt3 and lt4 retired: their content now lives in the annotation
  # panels (#ap1/#ap2/#ap3 in the template). lt1 + lt2 still fire during the loading
  # segment where no annotation panel applies. Updated timeline must be re-derived after
  # zoom.py runs (annotate mode advances cursor differently from hold mode).
  - id: lt1
    in_recording_t: 2.5     # during z0 follow-zoom on prompt input (pre-loading)
    out_recording_t: 9.0    # exits during full-frame loading (7.2-10.2), just before Progress-sidebar zoom-in at rec 10.2
    eyebrow: "V1 · Quick Stock Research Brief"
    headline: "Twenty minutes of research, in one prompt."   # audience-perspective per QC #9 — was "Eight parallel skill calls. One natural-language prompt." (engineering vocabulary, rejected 2026-05-19)
  - id: lt2
    # DROPPED 2026-05-21 per "Vault stats integrate, not narrate" decision.
    # Standalone four-stat credibility ribbon removed; the 13-years + 62k stats
    # integrate into the processing-matters / Value-row / trajectory beats instead.
    # ICIR / Sharpe / +5.8%/yr are jargon stats that don't integrate — they migrate
    # to V9 Deep Dive / out-of-slate marketing surfaces.
    in_recording_t: 0
    out_recording_t: 0
    eyebrow: ""
    headline: ""

# Annotation panels — right-side panel content for annotate-mode zooms.
# Phase A: timings + callout numbers only; panel content is a placeholder in the
# template (numbered badge + "Callout N · Placeholder"). Phase B will fill in
# eyebrow / headline / body / stats / source fields here and wire them through
# render.py substitutions.
# Timings are recording-relative; render.py adds 5s for composition-absolute.
# RE-DERIVE after every zoom.py run (annotate-mode segments shift the timeline).
annotations:
  - id: ap1
    in_recording_t: 27.95   # z1 hold start
    out_recording_t: 43.95  # z1 hold end (16s hold)
    callout_number: 1
    panel:
      # Shape: capability — names what the Value-factor row gives the buyer
      eyebrow: "VALUE FACTOR · WHAT IT GIVES YOU"
      headline: "A peer-adjusted answer to \"isn't NVDA expensive?\""
      body: "When the client opens with the P/E, \"expensive in absolute, cheap vs. AI-semi peers\" is the defensible answer. Parallax surfaces the peer comparison on every brief — no separate model, no Bloomberg pull, no scrambling for the comp set mid-call."
      source: "Source: Parallax Fundamentals"
      badge: "Peer-adjusted"
  - id: ap2
    in_recording_t: 45.43   # z2 hold start
    out_recording_t: 55.43  # z2 hold end (10s hold)
    callout_number: 2
    panel:
      # Shape: stakes — names the conversation the trajectory row serves
      eyebrow: "52-WEEK TRAJECTORY · THE QUESTION BEHIND THE CALL"
      headline: "Was it the market or was it the business?"
      body: "When a holding has slipped, the question isn't IF the score dropped — it's WHY. Quality persistence with Value compression is a valuation reset. Quality fading is the actual problem. The trajectory tells you which is which, before you tell the client."
      source: "Source: Parallax Factor Scores"
      badge: "Regime-adaptive"
  - id: ap3
    in_recording_t: 61.10   # z3 hold start
    out_recording_t: 65.10  # z3 hold end (4s hold)
    callout_number: 3
    panel:
      # Shape: capability — names what the Bottom Line gives the buyer
      eyebrow: "BOTTOM LINE · WHAT IT GIVES YOU"
      headline: "A conclusion-first verdict you can quote."
      body: "When time is short, you need the takeaway before the supporting data. The Bottom Line gives you the call — Hold, Trim, Add — with the reasoning compressed underneath. Citation-ready, no scrolling, no synthesis on the fly."
      source: "Source: Parallax Research"
      badge: "As of Feb 25, 2026"

vault_stats_used:
  - id: icir_lead
    stat: "ICIR 4.10 / Sharpe 2.34 / +5.8%/yr Q5 over 13 years"
    source: "stock-selection-alpha/2026-04_stock-selection-alpha.tex"
    owner: V1
  - id: live_universe
    stat: "62,000+ listings across 48 markets"
    source: "04-Marketing/Key Differentiators.md"
    owner: "V0.5, V1, V9"

frames_used:
  # Audit trail — every on-screen claim in the VO must trace to one of these.
  # Frames extracted from screen recordings/V1/1vid_scrubbed.mp4 (re-extracted 2026-05-20
  # for the 2026-05 re-record; the pre-overhaul April-era V1 recording showed Total 8.7 → 5.9
  # vs this recording's actual 8.5 → 5.0).
  - frame: frame_0001.jpg
    timestamp: 0.0
    cites: "empty Cowork chrome with 'Let's knock something off your list' greeting + brand quick-prompts (Deep dive analysis / Build scored portfolio / Analyze investor profile)"
  - frame: frame_0008.jpg
    timestamp: 14.0
    cites: "user prompt visible 'Stock brief on NVDA. Client query, need a defensible read on the position.' + Working state + Running skill / Loading tools indicators + Progress sidebar appearing"
  - frame: frame_0015.jpg
    timestamp: 28.0
    cites: "continued parallel work in chat — multiple sub-processes visible, Progress sidebar populating"
  - frame: frame_0022.jpg
    timestamp: 42.0
    cites: "brief nearly complete — Progress sidebar near full, brief page rendering"
  - frame: frame_0023.jpg
    timestamp: 44.0
    cites: "brief delivered — 'Used Parallax integration, used 13 tools, used a skill' + 'NVDA — Stock Brief (NVIDIA Corp, NVDA.O)' + 'Price $225.32 · Mkt Cap $5.46T · P/E 45.7 · Today −4.4%' + Progress sidebar 5-of-5 complete (Resolve NVDA ticker & company info / Run parallel data batch / Pull US macro tactical context / Explain extreme factor scores / Writing the client brief) + factor table visible (Quality 10, Value 3, Momentum 7, Defensive 8, Tactical 10)"
  - frame: frame_0026.jpg
    timestamp: 50.0
    cites: "factor table fully visible at z1 hold scroll position — Quality 10 (Flat at 10, extraordinary consistency), Value 3 (2→3 slight cheapening, still bottom quartile, P/E 45.7 vs AVGO 80 / AMD 140 / ARM 246), Momentum 7 (Faded from 9-10 down to 7 since late March), Defensive 8, Tactical 10, Total 5 (Fair)"
  - frame: frame_0027.jpg
    timestamp: 52.0
    cites: "Total row's 52-wk trend cell visible — '8.5 → 5.0 — material derating in the composite even as the underlying business stayed top-tier' (this is the trajectory beat z2 spotlights)"
  - frame: frame_0030.jpg
    timestamp: 58.0
    cites: "Bottom Line section visible — 'NVDA scores top-decile on Quality and Tactical with a 21% consensus upside, lowest peer volatility, and a still-accelerating AI capex cycle (Q1 FY27 guide $78B) — the fundamental case for holding is intact and defensible' + Analyst View (mean target $272.94 / median $275 / 21% implied upside, 61 analysts: 10 Strong Buy / 48 Buy / 2 Hold / 1 Sell / 0 Strong Sell)"

beats_cut_for_series_overlap:
  - "Financial Health detail → covered in V2 (Deep Dive)"
  - "Macro context → V10 (Macro Outlook)"
  - "Risk vs. peers → V4 (Rebalance) / V6 (Scenario)"
  - "Analyst view synthesis → V2 (Deep Dive)"
---

# Video 1 — Quick Stock Research Brief

Rewritten 2026-05-20 against the 2026-05 re-recorded V1 zoomed recording (88.37s) under the locked rule set: Customer's-chair framing (QC #9), panel-VO complementarity, hallucination check on the re-recorded frames, NL-prompts-in-demo vocabulary lock. **Revised 2026-05-21** per "Vault stats integrate, not narrate" decision — standalone ICIR / vault-stat ribbon beat removed; LT2 retired; surviving stats (*13 years live*, *62k listings*) integrate into processing-matters / Value-row / trajectory beats as problem-solving and why-can't-Claude framing.

**Total runtime**: ~100.4s = 5s title + 88.37s zoomed recording + 7s outro (recording duration unchanged; loading-segment compression deferred to a follow-on workstream)
**Voice budget**: ~150 wpm AI TTS; current draft ~158 spoken words ≈ 63s across ~93s of speakable window. Stats now integrated (not standalone) — *"thirteen years live, out-of-sample"* anchors the processing-matters beat; *"peer-ranked against AVGO, AMD, ARM and the broader sixty-two-thousand-listing universe"* anchors the Value-row beat; *"thirteen years of factor history says: this is what a repricing looks like, not a thesis break"* anchors the trajectory beat. ICIR / Sharpe / +5.8%/yr removed — they don't integrate cleanly (require jargon explanation); migrate to V9 Deep Dive / out-of-slate.
**Frames cited**: 8 frames from the 2026-05 re-recorded V1 (`frames_used:` in frontmatter)

**Sentence-rhythm correction (2026-05-20, mid-day):** first cut of this draft used fragments for ~70% of beats (e.g. *"Brief lands. Under a minute. Every claim sourced."* / *"Plain English in. Parallax pulls..."*) — defensible for data callouts but read as Bloomberg-ticker telegraph elsewhere. Hard Rule #6's *letter* (cut beats when budget is tight) didn't trigger — budget had 30+ seconds of headroom. But Hard Rule #6's *spirit* (natural pacing > telegraph style) was violated by stylistic reflex. Fix: kept fragments where the data IS the punch ("Composite at five. Quality and Tactical, ten. Value, three." — earned); restored full sentences where the VO is doing connective/interpretive work ("You type the question in plain English, and Parallax pulls every input — scores, peers, macro, news, methodology — through the same factor framework." — connective, full sentence). Final mix: ~40% data-fragment, ~35% short-sentence, ~25% full-sentence — rhythm reads as varied across beats.

**Value-framing angles applied** (per `references/value-framing-menu.md`, V1's MASTER assignment):
- **Moat headline:** #12 Unverifiable frame — beat 2 (Parallax pulls every signal through the same factor framework — reconciles, doesn't stitch)
- **Supporting:** #1 Speed + #2 Coverage (title), persona/moment (beat 1), #3 Defensibility + #9 Live track record (beat 3 — ICIR vault stat), #1 Speed + #3 Defensibility (beat 4 — "brief lands, every claim sourced"), #7 Decision-readiness (beats 5 / 6 / 7 — factor pattern, trajectory, verdict)
- **#6 No black box** sits implicit in beat 2 (every signal through the same framework — visible, not hidden)
- **Rotation:** 7 distinct angles across 8 spoken beats; #7 appears 3× with differentiated value-clauses (factor-pattern triage / trajectory interpretation / verdict).

**Customer's-chair framing (QC #9) discipline:**
- No engineering vocabulary anywhere: dropped "eight parallel calls" / "every call hits the Vault" / "tool call traces" from the previous draft. Replaced with outcome/methodology/workflow-fit language ("Parallax pulls every signal through the same factor framework" / "every claim sourced" / "ICIR four-point-one, thirteen years live").
- Panel-VO complementarity: panels pitch the *capability value* of each spotlit segment (ap1: peer-adjusted answer to "isn't NVDA expensive?"; ap2: was it the market or the business?; ap3: conclusion-first verdict you can quote). VO carries the *interpretation* (what the factor pattern means / what the trajectory reveals / what the verdict is). VO does NOT duplicate the panel's pitch — the two layers complement, don't echo.

**Hallucination check applied:**
- Every claim traces to a `frames_used:` entry from the 2026-05 re-recorded V1 (not the pre-overhaul April-era V1).
- "Eight-point-five to five-point-oh" → `frame_0027` (Total trajectory cell, not the V1's old 8.7 → 5.9).
- "Twenty-one percent upside, top-decile quality" → `frame_0030` (Bottom Line + Analyst View "~21% implied upside").
- No verifiable claims from V2 / V6 / V10 owned content (Financial Health detail, Macro deep dive, Analyst View synthesis) — those are spoken-silent beats per MASTER's "Beats cut for series overlap."

---

## Voiceover script

> **[Title card 0:00–0:05 — angle: #1 Speed + #2 Coverage]**
>
> Twenty minutes of research, in one sentence. For every name in your portfolio.

> **[r=0:00 — prompt typing region; z0 follow-zoom on the input box; LT1 visible r=2.5–9.0 ("V1 · Quick Stock Research Brief" / "Twenty minutes of research, in one prompt."); `frame_0001` shows empty Cowork chrome with "Let's knock something off your list" + brand quick-prompts — angle: persona/moment opener]**
>
> A client just texted about a holding. Your next meeting is in ten minutes.

> **[r=0:09 — brief generating; parallel work firing in chat sidebar; Progress sidebar populating; `frame_0008` shows prompt typed "Stock brief on NVDA — client query, need a defensible read on the position." + Working state — angle: #12 Unverifiable frame (moat headline) + #6 No black box. Integrates "13 years live" as why-can't-Claude (the framework's age is what makes "reconcile, not stitch" defensible).]**
>
> You type the question in plain English, and Parallax pulls every input — scores, peers, macro, news, methodology — through the same factor framework. Thirteen years live, out-of-sample. The brief reconciles. It doesn't stitch.

> **[r=0:22–0:42 — brief continuing to generate; LT2 retired (2026-05-21 vault-stats-integrate rule); no VO — visible parallel work + Progress checklist do the talking. Loading compression deferred to a follow-on workstream; the current ~20s of silence here will be addressed by speed-ramping the loading recording in a subsequent re-scrub. `frame_0015` + `frame_0022` show continued processing.]**

> **[r=0:42–0:50 — brief lands; `frame_0023` shows "Used Parallax integration, used 13 tools, used a skill" + 5-of-5 Progress checklist complete (Resolve / Run parallel data batch / Pull US macro tactical context / Explain extreme factor scores / Writing the client brief) + NVDA — Stock Brief header + Price $225.32 + factor table appearing — angle: #1 Speed + #3 Defensibility]**
>
> The brief lands in under a minute, every claim sourced.

> **[r=0:50–1:06 — z1 hold; ap1 panel visible on right ("VALUE FACTOR · WHAT IT GIVES YOU" / "A peer-adjusted answer to 'isn't NVDA expensive?'"); factor table spotlit on left with Value row bright (Quality 10, Value 3, Momentum 7, Defensive 8, Tactical 10, Total 5 (Fair)); `frame_0026` — angle: #7 Decision-readiness (factor pattern). Integrates "62k listings / peer universe" as problem-solving (makes "peer-adjusted" concrete for the Value=3 reading).]**
>
> Composite at five. Quality and Tactical, ten. Value, three — peer-ranked against AVGO, AMD, ARM and the broader sixty-two-thousand-listing universe. The pattern tells you the trade: you pay up for the compounder, and you go in with eyes open on the multiple.

> **[r=1:06–1:08 — scroll between z1 and z2; brief page advances to trajectory view; no VO]**

> **[r=1:08–1:18 — z2 hold; ap2 panel visible on right ("52-WEEK TRAJECTORY · THE QUESTION BEHIND THE CALL" / "Was it the market or was it the business?"); Total row's trajectory cell spotlit on left ("8.5 → 5.0 — material derating in the composite even as the underlying business stayed top-tier"); `frame_0027` — angle: #7 Decision-readiness (trajectory interpretation). Integrates "13 years of factor history" as problem-solving (the framework's tenure is what enables the repricing-vs-thesis-break call).]**
>
> Eight-point-five to five-point-oh over the past year. Quality never moved. The market repriced the multiple — the business didn't change. Thirteen years of factor history says: this is what a repricing looks like, not a thesis break.

> **[r=1:18–1:23 — silent scrolldown; Financial Health (Green) / Macro Context (Cross-current) / Analyst View scroll past; no VO per MASTER beat sheet (those beats are owned by V2 Deep Dive / V6 Macro / V10 Macro Outlook — not re-litigated here)]**

> **[r=1:23–1:27 — z3 hold; ap3 panel visible on right ("BOTTOM LINE · WHAT IT GIVES YOU" / "A conclusion-first verdict you can quote."); Bottom Line section spotlit on left ("NVDA scores top-decile on Quality and Tactical with a 21% consensus upside, lowest peer volatility, and a still-accelerating AI capex cycle..."); `frame_0030` — angle: #7 Decision-readiness (verdict)]**
>
> Hold — the case is intact. Twenty-one percent upside on top-decile quality.

> **[r=1:27–1:28 — tail; brief sits on screen; no VO]**

> **[Outro 1:33.37–1:40.37 — Parallax wordmark + "Solve the market." tagline]**
>
> Parallax. Solve the market.

---

## Workflow + rules followed

### Inputs read (this draft, 2026-05-20)

| Source | What I took |
|---|---|
| `Parallax Video Plan - MASTER.md` V1 section (new slate, Phase 3 spec) | Persona/moment anchoring, beat sheet, primary value angles (#12 moat + #1/#3/#6/#7 supporting), recording inputs, title-card framing |
| `references/value-framing-menu.md` | 12-angle definitions + value-line shapes per angle |
| `references/production-principles.md` § Customer's-chair framing | Reject/require lists for QC #9 — no engineering vocabulary in any layer (VO, LTs, panels) |
| `.claude/skills/video-production-workflow/SKILL.md` Hard Rules #7 (hallucination) + #12 (re-derive timings) + #16 (cursor-clear) + #17 (vertical centering) + #18 (overlay ease) + #19 (clean source segments) | Workflow enforcement |
| `.claude/skills/video-scriptwriting/SKILL.md` Universal craft + use_case section + Panel content authoring + Quality Checks #1–#9 | Voice composite, banned words, AI-tell transitions, NL-prompts-in-demo lock, panel format contract, source/badge vocabulary |
| `templates/product-demo/RENDER-GUIDE.md` | Title (5s) + recording + outro (7s) structure; recording-relative LT/annotation timing model; locked outro tagline ("Solve the market." — RM moment, not Polaris) |
| `screen recordings/V1/1vid_scrubbed.mp4` + `frames/V1.2/` (8 frames) | Ground truth for every on-screen claim. Caught: the 2026-05 re-record's trajectory is 8.5 → 5.0 (vs the pre-overhaul recording's 8.7 → 5.9); Progress sidebar shows 5 grouped steps (not the MASTER spec's "8 parallel calls" — actual UI surface is 5 steps); used 13 tools (not 8 — but VO doesn't count tools per QC #9) |
| Zoom segment timing in `1vid_zoomed.mp4` (88.37s total, post-`--clean-source-ranges` cleaning of src_02 + src_03) | Annotation in/out_recording_t (ap1: 50.25/66.25, ap2: 67.73/77.73, ap3: 83.40/87.40) — re-derived per Hard Rule #12 |

### Panel–VO complementarity (load-bearing rule)

Each annotate hold has TWO copy layers: the right-side panel and the VO. They have distinct jobs:

| Layer | Job | V1 example |
|---|---|---|
| **Panel** | Pitches the *capability value* of having this segment in every brief | ap1: "A peer-adjusted answer to 'isn't NVDA expensive?'" — names what the Value row gives the buyer |
| **VO** | Carries the *interpretation* of what's visually on screen now — reads the pattern, not the panel's pitch | "The pattern names the trade — pay up for the compounder, eyes open on the multiple." |

If both layers said the same thing, the panel would be ornamental noise. Authored against the "show on screen, interpret in voiceover" rule (`video-scriptwriting/SKILL.md` Universal) + the Panel content authoring section's subject-match constraint (panel topic = spotlit content's topic, but the *angle* differs from the VO's angle).

### Customer's-chair framing — QC #9 enforced

Reject list (none appear in this draft, confirmed by `tools/render.py`'s pre-flight check):
- "parallel skill calls" / "parallel tool calls" / "parallel MCP calls" / "MCP tool invocations"
- "agent orchestration" / "skill calls fire" / "tool calls fire in parallel"
- "watch as eight" / "watch as ten" — no capability-counting framings

Require pattern: every line is **outcome / stakes / workflow-fit / methodology-credibility**. Examples:
- *Outcome:* "Brief lands. Under a minute. Every claim sourced."
- *Stakes / workflow-fit:* "Client just texted about a holding. Ten minutes before your next meeting."
- *Methodology-credibility:* "ICIR four-point-one. Thirteen years live. Out-of-sample."
- *Decision-readiness:* "Hold — case is intact. Twenty-one percent upside, top-decile quality."

### Beats cut for series overlap (silent VO during these visuals)

Per MASTER's overlap discipline: r=1:18–1:23 silent scrolldown shows Financial Health (V2 owns), Macro Context (V6/V10 owns), Analyst View (V2 owns). VO does not narrate these — the viewer reads them while transitioning to z3.

### Hard constraints respected (Quality Checks)

| Check | Status |
|---|---|
| QC #1 No banned words | ✓ none used |
| QC #2 No AI-tell transitions (Furthermore, Moreover, etc.) | ✓ |
| QC #3 No "not just X, but Y" constructions | ✓ |
| QC #4 No hedge phrases | ✓ |
| QC #5 Active voice | ✓ |
| QC #6 Sentence-rhythm variation | ✓ short clusters ("Composite at five. Quality and Tactical, ten. Value, three.") + longer interpretation beats |
| QC #7 12-angle rotation across beats | ✓ 7 distinct angles, #7 appears 3× with differentiated value-clauses |
| QC #8 Show on screen / interpret in VO | ✓ factor scores on screen — VO interprets ("the pattern names the trade"); trajectory cell on screen — VO interprets ("market repriced, business didn't change") |
| QC #9 Customer's-chair framing | ✓ no engineering vocabulary in VO, LTs, panels |
| Vocabulary lock (NL prompts in demo) | ✓ no slash-command read aloud; product module names ("Stock Report") used in LTs not slash commands |
| Hallucination check | ✓ every claim cites a frame from the 2026-05 re-recorded V1; "13 tools" / "5-of-5 Progress" / "8.5 → 5.0" / "21% upside" all visible in cited frames |
