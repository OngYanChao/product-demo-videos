# product-demo-videos

Video production pipelines for **Chicago Global / Parallax** that turn live Cowork product demos into branded, ship-ready videos.

This repo holds two distinct pipelines under one roof:

1. **A manual / human-in-the-loop pipeline** — for the flagship 20-video V-series content library. Every video is hand-authored: locked beat sheet, written voiceover script, hand-designed zoom moves, HeyGen-rendered avatar, multi-tier review. Human gates at each phase.
2. **A fully automated pipeline** — for autonomous news-driven Cowork briefs. One command from prompt to final mp4: capture → process → render → lint. No script writing, no avatar, no editorial layer, no human in the loop.

They share the underlying capture + scrub + zoom + render layer but diverge sharply on what comes between.

---

## What's in here

| Pipeline | Style | Status | Output |
|---|---|---|---|
| **Product-demo** (V-series, I-series) | **Manual / human-in-the-loop** — 11 phases per video, multiple human gates, billable final render | Phase 7 production active; V1–V3 in canary | Scripted product demo with HeyGen avatar, lower-thirds, annotate panels, vault-stat callouts |
| **News-pipeline** (N-series) | **Fully automated** — one command per slot, zero human decisions in the loop | End-to-end working | Title card → autonomous Cowork run → Polaris outro |

**Why the split.** The product-demo pipeline is intentionally manual because each V-series video is a marketing artifact — every beat is editorially designed against a 20-video master plan, every claim cites a frame, every panel speaks from the buyer's chair, every zoom is sized by the beat sheet. Automation would lose the editorial control that makes the V-series ship-worthy. The news-pipeline is intentionally automated because the deliverable is "watch Cowork solve this prompt with a branded wrapper" — there's no editorial layer to author, so removing the human from the loop is purely upside (faster iteration, $0/run, batchable).

---

## Quick start — news-pipeline (the fully-automated path)

```bash
# 1. One-time setup
brew install cliclick ffmpeg tesseract
python3 -m pip install pyobjc-framework-Quartz pillow pytesseract anthropic
python3 automation/calibrate.py    # ask you to click mic + stop button positions in Claude desktop

# 2. Write a prompt
echo "Compare TSMC and Samsung Foundry as a 2026 semiconductor allocation." \
  > news-pipeline/prompts/N5_my_brief.txt

# 3. Capture (drives Claude desktop, records the run end-to-end)
python3 automation/capture.py --slot-dir news-pipeline/recordings/N5 \
  news-pipeline/prompts/N5_my_brief.txt

# 4. Process (chained: scrub → tick_cut → zoom → cap_dead → render → lint)
python3 news-pipeline/tools/process.py N5

# Done. Output: news-pipeline/recordings/N5/final.mp4
#               news-pipeline/recordings/N5/lint-report.json
```

Step 4 is one command that does six things in sequence and exits with code 1 if any of them fail or lint surfaces tier-1 errors. The lint report (`lint-report.json`) is machine-readable so any orchestrator (CI, Claude agent, shell wrapper) can decide what to do next based on the structured findings.

## Quick start — product-demo pipeline (the V-series scripted path)

This pipeline has 11 phases per video and is orchestrated through the `parallax-video` skill. Trigger phrases in the CLAUDE.md "If user asks you to" table map to phases. The short version:

```bash
# 1. Lock the beat sheet for V<N> by reading from MASTER.md
#    (autonomous — no approval gate; see CLAUDE.md trigger "Lock V5 beats")

# 2. Capture the screen recording
python3 automation/capture.py --slot-dir "screen recordings/V5" <prompt>

# 3. Scrub + extract frames
python3 tools/scrub.py ...
python3 tools/extract_frames.py ...

# 4. Write the script (Phase 5) — read frames, draft VO + zoom design

# 5. Apply zoom (Phase 5.5) — measure highlights, apply camera moves
python3 tools/zoom.py ...

# 6. Render preview (free; iterate cheaply)
python3 tools/render.py V5 --mode preview

# 7. Polish + lint + LLM review (auto-chains from preview)
python3 tools/lint_video.py V5
python3 tools/review_video.py V5

# 8. Render final (billable HeyGen credits; one-shot human gate)
python3 tools/render.py V5 --mode final
```

The full daily workflow + trigger phrases live in `CLAUDE.md` under "If the user asks you to". Each phase has documented hard-rule constraints that the lint enforces mechanically and the LLM reviewer evaluates semantically.

---

## Architecture at a glance

```
                    ┌──────────────────────────────────────┐
                    │  automation/                          │
                    │  └─ capture.py (Cowork driver,        │
                    │     records raw.mp4 + trimmed.mp4)    │
                    └──────────────────────────────────────┘
                                       │
                ┌──────────────────────┴───────────────────┐
                ▼                                          ▼
   ┌────────────────────────┐                ┌─────────────────────────┐
   │  News pipeline         │                │  Product-demo pipeline  │
   │  news-pipeline/        │                │  tools/ + outputs/V<N>/ │
   ├────────────────────────┤                ├─────────────────────────┤
   │  process.py            │                │  scrub.py               │
   │   ├─ scrub             │                │  extract_frames.py      │
   │   ├─ tick_cut          │                │  zoom.py                │
   │   ├─ zoom              │  (shared      │  render.py              │
   │   ├─ cap_dead          │   tools/       │   ├─ mode=preview ($0)  │
   │   ├─ news_render       │   layer)       │   └─ mode=final (HeyGen)│
   │   └─ lint_news         │                │  lint_video.py          │
   │  (one-command auto-    │                │  review_video.py        │
   │   chain to final.mp4)  │                │  (auto-chain from render)│
   └────────────────────────┘                └─────────────────────────┘
                │                                          │
                ▼                                          ▼
   recordings/N<N>/final.mp4                   outputs/V<N>/final.mp4
   recordings/N<N>/lint-report.json            outputs/V<N>/review.md
```

**Shared layer:**
- `automation/` — screen capture driver, calibration, prompt typing, end-of-streaming detection, AskUserQuestion popup auto-dismiss, scroll read-through
- `tools/` — `scrub.py`, `zoom.py`, `extract_frames.py`, `measure_highlight.py`, `detect_ticks.py`, `static_gateway.py`, `script_hash.py`

**Pipeline-specific layers:**
- `news-pipeline/tools/` — `process.py` (auto-chain orchestrator), `tick_cut.py` (Progress sidebar tick compression), `news_render.py` (Hyperframes composer), `lint_news.py` (17 mechanical rules)
- `tools/` (V-series-specific) — `render.py` (preview + final modes, HeyGen integration), `lint_video.py` (22 mechanical rules), `review_video.py` (6 LLM semantic checks via `claude-opus-4-7`)

**Templates:**
- `templates/product-demo/` — V-series Hyperframes composition (title + recording + avatar PiP + lower-thirds + outro)
- `news-pipeline/templates/news/` — News Hyperframes composition (title + recording + outro; no avatar, no lower-thirds)

---

## Cost model

| Step | Pipeline | Cost |
|---|---|---|
| Screen capture | Both | $0 — `ffmpeg avfoundation`, local |
| Scrub, tick_cut, zoom, cap_dead | Both | $0 — local FFmpeg |
| Hyperframes render (Title + Recording + Outro) | Both | $0 — local Puppeteer + FFmpeg |
| HeyGen avatar clip | Product-demo only (final mode) | ~$15/clip first render; **cached by script-body hash** so unchanged VO doesn't re-bill |
| LLM semantic review | Product-demo only | ~$0.25 first run via `claude-opus-4-7`; **cached by content hash** so unchanged input is $0 |
| News lint | News only | $0 — deterministic |
| News full pipeline | News only | **$0 end-to-end** (no avatar, no LLM) |

The product-demo pipeline has one **deliberately human-gated** billable step (Phase 9, "render V<N> final" — the HeyGen call). Everything else auto-chains. The news pipeline is entirely free and end-to-end automated.

---

## Where to read next

| You want to… | Go to |
|---|---|
| Understand the full per-video product-demo workflow + trigger phrases | `CLAUDE.md` — "If the user asks you to" table |
| See the 20-video plan (V1–V16 + I1–I4) | `Parallax Video Plan - MASTER.md` |
| Read about a specific Hard Rule | `.claude/skills/video-production-workflow/rules/` (per-phase files) |
| Capture-layer details (calibration, screen recording, popup handling) | `automation/README.md` |
| News-pipeline conventions + hard-rule mapping | `news-pipeline/README.md` |
| V-series template format + render mechanics | `templates/product-demo/RENDER-GUIDE.md` |
| News template format | `news-pipeline/templates/news/RENDER-GUIDE.md` |
| Decisions log (ADRs, chronological) | `decisions/INDEX.md` |
| Project file layout (full annotated tree) | `references/file-layout.md` |
| Build status, pending items, ship order | `overhaul.md` |

---

## Requirements

- macOS (Apple Silicon or Intel; tested on macOS 14+)
- Python 3.11+ with: `pillow`, `pyobjc-framework-Quartz`, `pytesseract`, `anthropic`, `yaml`
- Homebrew with: `cliclick`, `ffmpeg`, `tesseract`
- Node.js (for `npx hyperframes`)
- Claude desktop installed and authorized for Cowork access
- `.env` with `ANTHROPIC_API_KEY` (for LLM review) and `HEYGEN_API_KEY` + `HEYGEN_AVATAR_ID` + `HEYGEN_VOICE_ID` (for V-series final renders)
- macOS Accessibility + Screen Recording permissions granted to your terminal

See `automation/README.md` for the one-time calibration walkthrough.

---

## Repository conventions

- **Branch flow**: feature work on named branches (e.g. `extract-automation-layer`); `main` is the integration branch
- **Commits**: descriptive, present tense, scoped to one logical change
- **Decisions**: locked-in rules → ADR in `decisions/YYYY-MM-DD-<slug>.md` + index entry in `decisions/INDEX.md` (chronological, append-only). See `decisions/INDEX.md` for the trigger phrases and routing protocol.
- **Hard Rules**: portable methodology rules (numbered #1–#31 + news-only N1–N3) live in `.claude/skills/video-production-workflow/rules/` (loaded per-phase, not in bulk)
- **Project-specific principles**: rules that depend on Parallax product specifics live in `references/production-principles.md`
- **Per-template invariants**: each template's `RENDER-GUIDE.md`

---

*This repo runs on a Hyperframes-first local rendering architecture. The migration from HeyGen-only (2026-04-29 → 2026-05-11) and the persona-and-moment overhaul (2026-05-11 → 2026-05-13) are documented in `overhaul.md`. The active production stream is the 20-video V/I slate; the news-pipeline is a separate cheaper experimental track that turned out to be useful for autonomous content.*
