---
pipeline_type: product_demo
output: outputs/V1_final.mp4
template_id: 6a10c4dd901a420a85a02ab0bce983c8   # brianna avatar 5 (test template)
caption: false
title: "Parallax V1 — Quick Stock Research Brief"

assets:
  # Uploaded to tmpfiles.org (60-min expiry — re-upload if URL goes stale).
  # Background is solid Chicago Global navy #0C2746, generated via ffmpeg.
  product_media: https://tmpfiles.org/dl/35515172/1vid.mov
  background: https://tmpfiles.org/dl/35515174/v1_background.png
---

# Video 1 — Quick Stock Research Brief

*Voiceover script, drafted against the actual `vid1.mov` recording (2:15 total runtime). Bracketed cues are on-screen events, not spoken.*

**Command demoed:** `/parallax:stock` (via natural-language prompt)
**Ticker:** NVIDIA (NVDA.O)
**Target length (voiced, after speed-ramp edit):** ~1:30–1:45
**Writing style:** video-scriptwriting (see `.claude/skills/video-scriptwriting/SKILL.md`).
**Delivery tone for TTS:** Bloomberg anchor — confident, brisk, not hyped.

**Beats cut for cross-video overlap** (per Quality Check #4): Financial Health details (covered deeper in V2 Deep Dive), Macro Context (V10 Macro is dedicated), Risk vs Peers (V4 Rebalance / V6 Scenario), Analyst View (V2 Deep Dive). Those sections render on screen without VO — viewer reads them visually. The VO stays focused on V1-unique beats: the parallel-call framing, the ICIR intro callout, the trajectory story, and the two-sided bottom line.

---

## Script

> **[0:00 — Cowork home screen. Empty prompt box. "Get to work with Parallax" suggestions visible below.]**
>
> Twenty minutes of research, in one sentence.

> **[0:04 — Prompt typed: "I keep hearing about NVIDIA — can you give me a quick rundown on whether it's actually worth the hype right now?"]**
>
> No ticker syntax. No filter flags. The question a real PM actually asks over coffee — and Parallax takes it from there.

> **[0:14 — Skills panel lights up with `stock`. First tool call fires.]**
>
> The stock skill routes the request, and eight calls go out in parallel. Sequential models can't do this — they'd run these one at a time. Here, they fire at once.

> **[0:20–1:45 — Tool calls stack: Get company info, Get peer snapshot, Get score analysis, Get stock outlook (×2), Get financials, Explain methodology (×3). Parallax connector visible throughout.]**
>
> Company info, peer snapshot, scores, outlook, financials, methodology checks. What used to be twenty minutes of Bloomberg pulls and broker reports, compressed into one orchestrated batch.

> **[1:20 — Lower-third card on screen: ICIR 4.10 · 36 of 37 markets · +5.8%/yr · 13 years · 48,403 stocks.]**
>
> And a word on the scoring. Parallax's composite runs an information coefficient of 4.10 globally — peer-reviewed, out-of-sample, across thirteen years and forty-eight thousand stocks. These aren't backtest numbers. These are the numbers running live.

> **[1:52 — Header: "Used Parallax integration, used a skill, loaded tools." NVIDIA (NVDA) — Quick Rundown begins rendering.]**
>
> Brief lands. NVIDIA — fifth-largest company on earth, ninety percent of revenue from one segment. That concentration is the story.

> **[1:58 — Factor table: Quality 10/10, Tactical 10/10, Defensive 8, Momentum 7, Value 3, Composite 5.9 (Fair).]**
>
> Quality and Tactical pinned at ten. Momentum rolling. Value says it's expensive — and it is.

> **[2:00 — "52-week trend" paragraph: score ran as high as 8.8 in mid-2025, dropped to 5.9 as momentum rolled from 10 to 7. Quality held at 10.]**
>
> But a composite of five-point-nine in isolation tells you nothing. The trajectory does. NVDA ran at eight-point-eight through most of last year, then rolled to five-point-nine over the past few weeks as momentum fell from ten to seven. Quality never moved. That's what Parallax catches that a single-number model misses — a great business going through a rerate, not a broken thesis.

> **[2:02 — Financial Health 🟢 Green. Q4 revenue $68.1B, +69% YoY. Q1 FY27 guide $78B. Visual only — no VO; covered in V2 Deep Dive.]**

> **[2:04 — Macro Context on screen: cautious on high-growth tech; elevated long rates. Visual only — no VO; V10 owns macro.]**

> **[2:06 — Risk vs Peers card on screen: NVDA 108.5% return with lowest vol in peer group. Visual only — no VO; covered in V4/V6.]**

> **[2:10 — Analyst View on screen: 59 analysts, mean target $269, one sell. Visual only — no VO; V2 Deep Dive covers analyst synthesis.]**

> **[2:12 — Bottom Line paragraph: exceptional business at rich P/E ~41, cooling factor score, Micron ranking higher on same framework.]**
>
> And the bottom line does what a good analyst should. Holds both sides. Exceptional business at a rich multiple, factor score cooling, Micron ranking higher on the same framework. Not a recommendation. A clear-eyed read.

> **[2:14 — Disclaimer + follow-ups offered: deeper dive, head-to-head vs Micron, or AI-infrastructure universe.]**
>
> One question. Eight parallel calls. Full brief. And the next three questions it already knows you'd want to ask.

> **[CLOSE CARD — PARALLAX wordmark, tagline: "Solve the market."]**
>
> *Parallax. Solve the market.*

---

## Production notes for this video

- **Open shot (0:00–0:14)** — empty Cowork chrome with the "Get to work with Parallax" quick prompts visible. Hold it long enough for the viewer to register that the starting point is plain English. Do not cut early.
- **Speed ramp.** Middle set to 0.40 (≈ 2.5× fast), covering 0:14 → 1:45. Loose enough that tool-call labels stay legible, tight enough to compress the long parallel-call stretch. If labels flicker too fast, push to 0.50; if the VO budget overshoots, drop to 0.30.
- **ICIR 4.10 lower-third (1:20)** — hold as a lower-third text card throughout the vault-stat VO beat. Format: *ICIR 4.10 · 36 of 37 markets · +5.8%/yr · 13 years · 48,403 stocks.*
- **Score table (1:58)** — zoom 10–15%. Hero frame. Linger two beats longer than the VO needs.
- **Trajectory section (2:00)** — the single most important narrative beat per the master plan. Consider a highlight overlay on the "8.8 → 5.9" numbers and the "Quality never moved" line.
- **Silent sections (2:02–2:10)** — Financial Health, Macro, Risk vs Peers, Analyst View render visually with no VO. Viewer reads. Those beats live more naturally in V2 (deep dive), V10 (macro), V4/V6 (peer/risk). Letting them breathe on screen here reinforces the "quick brief" framing — V1 shows *what* Parallax surfaces, the rest of the series shows *why* in depth.
- **Bottom Line (2:12)** — zoom and hold. The two-sided framing is the compliance-safe payoff.
- **Polaris alt close (optional)** — for cuts targeted specifically at PM/CIO audiences, swap the final wordmark line for: *"This isn't a backtest. Polaris has been running on these scores since 2019."*

## Vault stats used (all verified)

| Stat | Source |
|---|---|
| ICIR 4.10 global composite | `stock-selection-alpha/2026-04_stock-selection-alpha.tex` |
| +5.8%/yr Q5 selection return, 13 years, 48,403 stocks, 36 of 37 markets | same |
| Polaris live since 2019 (optional close) | `Parallax Overview.md`, leave-behinds |

All on-screen NVDA numbers (market cap, revenue, scores, targets, analyst counts) come directly from the recorded Parallax output, verified against extracted frames.
