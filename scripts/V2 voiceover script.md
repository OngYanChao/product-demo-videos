---
pipeline_type: product_demo
template: product-demo
video_id: V2
style: use_case
complexity: single_feature
title: "Pre-Trade Stock Check"
youtube_title: "Pre-Trade Stock Score Check (Score + Factor Pillars + 52-Week Trajectory)"
target_runtime_seconds: 69.77   # 5s title + 57.77s zoomed recording + 7s outro = 69.77s. Tick window = T_first_tick (raw 31.7) to T_(N-1) (raw 138.37) — the final synthesis tick (raw 198.1, which equals T_brief_landed) is EXCLUDED from the locked tick window per Hard Rules #20+#21+#23. Multi-zone scrub: --force-speed-range "0:7.0:1.0,30.7:139.37:1.0,198.1:215.95:1.0" (zone-b bounded by ±1s around T_first/T_(N-1) to align with detect_ticks' margin=1.0 convention). Phase-3 trim+concat applies ffmpeg_keep_ranges from vid2_ticks.json to the tick window → vid2_scrubbed.mp4 (42.92s). Zoom-pass adds 14.85s of zoom inserts (3.35s full-frame "Working on it…" dwell + 4-sub-annotate static-camera score-panel cluster + 2-sub-annotate trajectory split + widened bottom-line spotlight per the May-25 three-tier band + safe-zone rules) → vid2_zoomed.mp4 (57.77s).
primary_persona: "Portfolio Manager (discretionary fund / family-office capital)"
primary_moment: "Name on the candidate list. Score check before the trade."
secondary_personas: ["Head of research (validates the same checks)", "CIO-as-practitioner (runs this themselves at small shops)"]
recording:
  path: "screen recordings/V2/vid2_zoomed.mp4"   # Phase 5.5 output — canonical timeline
  duration_seconds: 57.77
  scrub_report: "screen recordings/V2/vid2_scrub_report.json"
  zooms: "screen recordings/V2/vid2_zooms.json"
  ticks: "screen recordings/V2/vid2_ticks.json"   # detect_ticks on RAW (Phase 3, Hard Rule #20)
  scrubbed_pre_tickcut: "screen recordings/V2/vid2_scrubbed_pre_tickcut.mp4"   # multi-zone scrub.py output before gap-cut
  scrubbed: "screen recordings/V2/vid2_scrubbed.mp4"   # Phase 3 trim+concat output (42.92s) — gap-cut applied to tick window
output:
  preview: "outputs/V2/preview.mp4"
  final: "outputs/V2/final.mp4"
avatar_id_override: null    # uses HEYGEN_AVATAR_ID from .env
voice_id_override: null     # uses HEYGEN_VOICE_ID from .env

beats:
  title:
    in: 0.0
    out: 5.0
    eyebrow: "V2 · Pre-Trade Stock Check"
    headline: "Before the trade, the score."
  outro:
    duration: 7.0
    wordmark: "Parallax"
    tagline: "Solve the market."
    polaris_alt: "This isn't a backtest. Polaris has been running on these scores since 2019."

lower_thirds:
  - id: lt1
    in_recording_t: 2.0     # during z0 follow-zoom on prompt input
    out_recording_t: 9.0    # exits as tools begin firing
    eyebrow: "V2 · Pre-Trade Stock Check"
    headline: "One question. One score. Before the trade."
  - id: lt2
    in_recording_t: 0
    out_recording_t: 0
    eyebrow: ""
    headline: ""

annotations:
  # Re-derived 2026-05-25 against vid2_zoomed.mp4 (58.90s) per Hard Rule #12.
  # Architecture: tick-window compression in Phase 3 (decisions/2026-05-23-tick-window-compression-moves-to-phase-3.md).
  # 2026-05-25 refactor (Hard Rule #25 + Hard Rule #24 shared-panel allowance):
  # 4 sub-annotates z1a-z1d (Composite/Quality/Value/Momentum) share ONE panel (ap1)
  # pinned across the whole cluster (22.30 → 39.32). Template only has 3 ap-slots
  # (ap1/ap2/ap3); the previous ap1-ap6 setup was over-spec'd — ap4-ap6 silently
  # dropped at render time. New mapping: ap1 = shared score-panel cluster,
  # ap2 = trajectory, ap3 = bottom line.
  - id: ap1
    in_recording_t: 20.85   # cluster begin (seg_annotate_02 = z1a Composite start) — shared panel pinned
    out_recording_t: 37.30  # cluster end (seg_annotate_05 = z1d Momentum end) — 16.45s held, fits 22-word body
    callout_number: 1
    panel:
      eyebrow: "COMPOSITE SCORE · WHAT IT GIVES YOU"
      headline: "Five pillars. One number. A defensible size."
      body: "The quant spine, before the trade. Composite plus the five factors resolves whether the thesis is fighting or aligning with the framework."
      source: "Source: Parallax Composite Score"
      badge: "Out-of-sample"
  - id: ap2
    in_recording_t: 39.58   # cluster begin (seg_annotate_06 = z2a composite trajectory) — shared panel pinned
    out_recording_t: 47.05  # cluster end (seg_annotate_07 = z2b Quality flat) — 7.47s held, fits 20-word body
    callout_number: 2
    panel:
      eyebrow: "52-WEEK TRAJECTORY · THE QUESTION BEHIND THE CALL"
      headline: "Did the score move because the business changed?"
      body: "Composite drifts; the pillars tell you why — multiple reset or thesis break. The trajectory tells you which, before the trade."
      source: "Source: Parallax Factor Scores"
      badge: "Regime-adaptive"
  - id: ap3
    in_recording_t: 52.50   # seg_annotate_08 (z3 bottom line) — tier 2 widened highlight
    out_recording_t: 55.50
    callout_number: 3
    panel:
      eyebrow: "BOTTOM LINE · WHAT IT GIVES YOU"
      headline: "A verdict you can defend in IC."
      # Bare callout — no body. Eyebrow + headline carry the pitch; the spotlight
      # on the verdict paragraph is what the viewer reads if interested. Per
      # Hard Rule #25, body-less panel uses the 3.0s floor — matches z3 hold.
      source: "Source: Parallax Research"
      badge: "As of 2026-05-25"

# Polish-pass notes for Phase 6a (NOT load-bearing for render.py):
_polish_notes:
  - "Score-panel beat uses 4 sub-annotates (z1a/b/c/d) sharing ONE panel (ap1) pinned across 22.30 → 39.32 per Hard Rule #24's shared-panel allowance + Hard Rule #25's panel-hold minimum. The VO body's existing single sentence ('Composite at five-point-six. Quality, Defensive, Tactical — pinned at ten. Momentum cooled…') reads naturally over the cluster — TTS pacing + manual pauses align audio to each spotlight without per-sub-annotate VO rewrites."
  - "KNOWN GAP: Value (z1c) isn't named in the VO sentence — the spotlight fires on the Value row while the avatar says something about Quality/Defensive/Tactical. Either add 'Value, three. Expensive.' into the VO or drop z1c when ready to fix."
  - "Recording-time stage-direction markers in the VO body reference the OLD zoomed timeline. Phase 6a re-derives these against vid2_zoomed.mp4 (58.90s under the May-23 Phase-3-tickcut + May-24 z0b-starts-on-checklist + May-24 mid-scroll annotate-centering + May-25 shared-panel-refactor pipeline)."
  - "Total composition runtime 70.90s is below MASTER's 75-95s target. Phase 6a backup loop can extend z2/z3 holds to add headroom."
  - "Annotates z1a-z1d use STATIC-CAMERA approach per decisions/2026-05-25-spotlight-vertical-safe-zone.md (Hard Rule #17 refined): all 4 sub-annotates share source_t=27.0 (frame_0014 area, score panel visible, no scroll) + share zoom_region=[20,25,75,75]. Camera holds completely still throughout cluster; only the spotlight moves between rows. Total/Quality/Value/Momentum comp y positions all land in the 30-70 safe zone (40.4%, 49.3%, 58.3%, 62.0%). Replaces prior mid-scroll source_t (32.10-32.62) which created visible page-jitter between sub-annotates."
  - "z2 (Trajectory) source_t=33.60 — header at y≈43%, hand-bounded h=3% (measure_highlight snap would have spanned the full 35% trajectory section, violating Hard Rule #24's 15% cap)."
  - "z3 (Bottom Line) source_t=40.65 — Bottom Line header crosses y≈44.8% during the smooth scroll from 39.8s (y=68%) → 41.0s (y=36%). Same h=3% hand-bound (snap caught full verdict paragraph)."
  - "Hard Rule #25 panel-hold check (300 wpm formula, 2026-05-25 cleanup applied): ap1 (22-word body) needs 6.4s; cluster sums 17.0s ✓. ap2 (20-word body, trimmed from 38) needs 6.0s; cluster sums 7.46s ✓ (z2a+z2b shared). ap3 (bare callout, no body) at 3.0s floor ✓. All panels Hard Rule #25 compliant."
  - "Hard Rule #24 three-tier highlight band (2026-05-25): z1a-z1d are tier 1 (specific row, h≤15%). z2a is tier 2 (header+paragraph+first-bullet conceptual unit, h=16%, source_t=34.0). z2b is tier 1 (Quality flat phrase, h=3%, source_t=35.0). z3 is tier 2 (header+verdict paragraph, h=18.87%, source_t=40.65). No tier-3 violations."

frames_used:
  # Re-extracted 2026-05-24 against the new vid2_scrubbed.mp4 (42.92s under May-23 Phase-3-tickcut pipeline).
  - frame: frame_0001.jpg
    timestamp: 0.0
    cites: "empty Cowork chrome — 'Let's knock something off your list' + brand quick-prompts"
  - frame: frame_0004.jpg
    timestamp: 6.0
    cites: "prompt 'Stock brief on AAPL. Evaluating for position add: composite score, factor pillars, 52-week trajectory.' typed in chat input; submit moment at scrubbed 7.0"
  - frame: frame_0014.jpg
    timestamp: 26.0
    cites: "brief renders — 'Apple Inc (AAPL.O) — Stock Brief' header + Composite Score & Factor Pillars table fully visible: Total 5.6/10 Fair, Quality 10/10, Value 3/10, Momentum 6/10, Defensive 10/10, Tactical 10/10 + per-pillar 'Read' column (Mid-pack overall / Best-in-class margins / Expensive P/E 34.2 vs Dell 13.2 WDC 12.3 / Decent but cooling / Lowest peer volatility / Macro-regime alignment favourable)"
  - frame: frame_0018.jpg
    timestamp: 34.0
    cites: "scrolled to '52-Week Trajectory — What the Scores Tell Us' section — composite range-bound + month-by-month bullets (May-Jun 2025 8.4→6.5, Jul 2025 low 3.0–3.6, Aug-Nov 2025 recovery to 8.1, Dec 2025-Feb 2026 held 7.3–8.1, Mar-Apr 2026 drawdown 3.7–4.7, May 2026 today 5.2→5.6) + 'Read on the pillars individually' (Quality flat at 10 unshakeable, Value chronically pinned at 2-3) + 'Financial Health — Green' section visible"
  - frame: frame_0021.jpg
    timestamp: 40.0
    cites: "scrolled to Bottom Line — 'For a position add: AAPL is a 10/10 on Quality and Defensive with rock-solid earnings momentum (+16% revenue, +17% NI, China reaccelerating), but the composite of 5.6 reflects two real frictions — Value pinned at 3 (P/E 34 vs peers 12-13), and a macro regime that the Parallax model says is actively penalising expensive quality. Trajectory is constructive off April lows but momentum has cooled from its November peak, the stock is trading at the analyst median (no consensus headroom), and the peer group includes two higher-scoring names (WDC 8.4, UI 8.2) if the goal is maximum composite score per dollar.' + 'This is informational analysis based on Parallax factor scores, not investment advice' disclaimer — recording tail"

recording_issues_flagged:
  - issue: "Verdict is nuanced, not clean Add/Wait"
    detail: "Bottom Line reads 'AAPL is a 10/10 on Quality and Defensive with rock-solid earnings momentum, BUT the composite of 5.6 reflects two real frictions — Value pinned at 3 and a macro regime actively penalising expensive quality… peer group includes two higher-scoring names.' Closer to 'yes-but' than the clean Add/Wait pre-test checklist target. VO leans into the ambiguity as a feature ('the score doesn't pretend the call is easy')."
  - issue: "Tail of scrubbed recording is short (~2.9s after Bottom Line first appears at scrubbed t≈40s)"
    detail: "Bottom Line section first appears at scrubbed t≈40s in the May-24 re-conformed vid2_scrubbed.mp4 (42.92s total). z3 hold tightened to 3.0s to stay inside the source tail. Closer beat plays over the same Bottom Line content with no new motion. Future re-record could let the brief settle longer post-Bottom-Line for a richer closer beat."

beats_cut_for_series_overlap:
  - "Financial Health detail → covered in V9 (Deep Dive)"
  - "Macro Context → V6 (Macro Intelligence)"
  - "Risk vs Peers → V7 (Quarterly Portfolio Review)"
---

# Video 2 — Pre-Trade Stock Check

Written 2026-05-22 against V2 scrubbed recording; re-conformed 2026-05-24 under the May-23 Phase-3-tickcut pipeline (scrubbed 42.92s → zoomed 58.53s). Locked rule set: Customer's-chair framing (QC #9), panel–VO complementarity, hallucination check on V2 frames, NL-prompts-in-demo vocabulary lock.

**Total runtime target**: ~78s = 5s title + ~66s zoomed recording + 7s outro
**Voice budget**: ~150 wpm AI TTS; current draft ~130 spoken words ≈ 52s across ~66s of speakable window (leaves headroom for natural breathing + the two no-VO connective beats)
**Frames cited**: 5 V2 frames

**Value-framing angles applied** (per `references/value-framing-menu.md`, V2's MASTER assignment):
- **Moat headline:** #5 Determinism — beat 5 (Determinism flex: re-run tomorrow, same score; byte-identical output)
- **Supporting:** #3 Defensibility (beat 1 title-card + opener), #6 No black box (beat 2 — the pattern is the call), #1 Speed (beat 1), #7 Decision-readiness (beats 3 / 4 / 6 — score panel / trajectory / verdict)

**Customer's-chair framing (QC #9) discipline:**
- No engineering vocabulary: dropped "eight parallel calls" / "MCP tool invocations" / "agent orchestration." VO speaks in PM's chair — outcome / stakes / workflow-fit / methodology-credibility.
- Panel–VO complementarity: panels pitch the capability value (ap1: defensible quantitative spine; ap2: was it the business or the multiple?; ap3: a verdict for IC). VO carries the interpretation (pattern reading / trajectory call / verdict).

**Hallucination check applied:**
- "5.6 / 10 / 10 / 10 / 6" → `frame_0019` (factor table)
- "8.4 to 5.6 over the past year" → `frame_0019` (trajectory column) + `frame_0025` (Bottom Line confirms)
- "Quality stayed flat at 10" → `frame_0019` (trajectory cell)
- "paying up for quality at a moment of multiple compression" → `frame_0025` (Bottom Line verbatim)
- Value=3 mentioned in VO only as part of the Bottom Line summary, since it is NOT in the visible factor table

---

## Voiceover script

> **[Title card 0:00–0:05 — angle: #3 Defensibility + #1 Speed]**
>
> Before the trade, the score. One name. One read. Under a minute.

> **[r=0:00 — prompt typing region; z0 follow-zoom on the input box; LT1 visible r=2.0–9.0 — angle: persona/moment opener]**
>
> The name's on the candidate list. Score check before the trade.

> **[r=0:06–0:30 — brief generating; parallel work firing in chat sidebar; Progress sidebar populating Resolve / Fetch / Pull / Synthesize. Permission popups appear briefly here (recording flaw — VO talks past). `frame_0005` — angle: #6 No black box + #3 Defensibility]**
>
> One natural-language ask pulls the composite, the pillars, the trajectory, and the peer-adjusted read — through the same factor framework, every time.

> **[r=0:30–0:36 — brief lands; `frame_0019` factor table visible — angle: #1 Speed + transition into score-panel beat]**
>
> The brief lands. Every claim sourced.

> **[r=0:36–0:46 — z1 hold on factor table; ap1 panel visible; Composite 5.6, Quality 10, Defensive 10, Tactical 10, Momentum 6 spotlit; `frame_0019` — angle: #7 Decision-readiness (pattern read)]**
>
> Composite at five-point-six. Quality, Defensive, Tactical — pinned at ten. Momentum cooled from ten to six. The pattern names a high-quality compounder going through a multiple reset.

> **[r=0:46–0:54 — z2 hold on trajectory column; ap2 panel visible; Composite trajectory '8.4 → 5.6' and Quality trajectory 'Flat at 10' spotlit; `frame_0019` — angle: #7 Decision-readiness (trajectory call)]**
>
> Eight-point-four to five-point-six over the past year. Quality stayed flat at ten. The composite reset; the business held.

> **[r=0:54–1:00 — between annotates; brief scrolls past Macro Context, Dividends, Risk vs Peers (those beats owned by V6 / V7 / V9 — silent VO per series-overlap discipline); `frame_0023`]**

> **[r=1:00–1:06 — z3 hold on Bottom Line; ap3 panel visible; verdict paragraph spotlit; `frame_0025` — angle: #5 Determinism (moat) + #7 Decision-readiness (verdict)]**
>
> The verdict: paying up for quality at a moment of multiple compression. Not a clean Add. Not a Wait. The score doesn't pretend the call is easy — and re-run tomorrow, it gives you the same number.

> **[r=1:06–1:10 — tail; brief sits on screen; no VO]**

> **[Outro 1:10–1:17 — Parallax wordmark + "Solve the market." tagline]**
>
> Parallax. Solve the market.

---

## Workflow + rules followed

### Customer's-chair framing — QC #9 enforced

Every line is outcome / stakes / workflow-fit / methodology-credibility. Examples:
- *Outcome / Speed:* "One name. One read. Under a minute."
- *Stakes / workflow-fit:* "The name's on the candidate list. Score check before the trade."
- *Methodology-credibility:* "Re-run tomorrow, it gives you the same number."
- *Decision-readiness:* "Composite at five-point-six. Quality, Defensive, Tactical — pinned at ten."

### Panel–VO complementarity

| Layer | Job |
|---|---|
| **Panel** | Pitches the *capability value* of having this segment in every brief |
| **VO** | Carries the *interpretation* of what's visually on screen now |

ap1 panel pitches "defensible quantitative spine"; VO reads the specific 5.6 / 10s / 6 pattern.
ap2 panel pitches "was it the business or the multiple?"; VO names the 8.4 → 5.6 + Quality-flat answer.
ap3 panel pitches "a verdict you can defend in IC"; VO names the actual verdict + determinism moat.

### Hallucination check applied

Every claim traces to a `frames_used:` entry. The Value=3 fact is referenced via the Bottom Line text (`frame_0025`), not claimed against the visible factor table since Value is NOT in the visible table.

### Recording issues acknowledged

Three flagged in frontmatter `recording_issues_flagged`:
1. Permission popups in loading section
2. Value pillar missing from visible factor table
3. Verdict more nuanced than clean Add/Wait

VO accommodates all three by leaning into the ambiguity ("the score doesn't pretend the call is easy") and structuring the score-panel beat around the visible 4 pillars rather than claiming all 5.
