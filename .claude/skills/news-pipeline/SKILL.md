---
name: news-pipeline
description: Orchestrator for the news-reactive Cowork demo video pipeline (separate, experimental workflow living in news-pipeline/). Takes a natural-language use-case description from the team, generates a tailored portfolio when needed (using the Wong Family Trust as a template), drafts a Cowork prompt designed not to trigger clarification tools, and drives Claude desktop via automation/capture.py to record the resulting demo session. Use whenever the user says "make a news video about X," "generate a demo for [scenario]," "draft a portfolio for [use case]," "capture this prompt," or any request to produce a news-reactive Parallax demo video. Pipeline is fully separate from the main parallax-video skill — do not mix tools, templates, or files across them. Recording infrastructure (capture.py + calibrate.py) is shared via the automation/ layer; this skill owns news policy + post-processing via news-pipeline/tools/.
---

# news-pipeline

Drives news-reactive demo video creation end-to-end from a natural-language use case. Lives in its own directory (`news-pipeline/`) to keep this experiment isolated from the main 20-video product-demo pipeline.

## What this skill does (in conversation)

The team describes a use case. You — Claude Code — orchestrate:

1. **Intake** — parse the use case, decide what's needed
2. **Portfolio** — generate or pick a portfolio (only if the use case benefits from one)
3. **Prompt** — draft the Cowork prompt that will be typed into Claude desktop
4. **Capture** — invoke `automation/capture.py` via Bash to record
5. **Process** — invoke `news-pipeline/tools/process.py` to scrub + tick-cut + zoom (was auto-chained inside capture.py pre-2026-05-29; capture.py is now workflow-agnostic and exits after producing raw.mp4 + trimmed.mp4 + manifest.json, so the news skill drives post-processing as a separate step)

After processing, hand the resulting `recordings/N<n>/zoom.mp4` back to the user with the manifest summary. `news-pipeline/tools/news_render.py` composes the final news video.

## Architecture

| Layer | Where it lives | Notes |
|---|---|---|
| Pre-recording orchestration | This skill | Intake, portfolio synthesis, prompt drafting — **you do all of it inline**, no separate Python scripts needed |
| Calibration (one-time) | `automation/calibrate.py` | Already run; produces `automation/calibration/claude-desktop.json` (shared with other workflows that drive Claude desktop) |
| Recording | `automation/capture.py` | Shared layer — drives Claude desktop + ffmpeg. Workflow-agnostic; exits after producing raw.mp4 + trimmed.mp4 + manifest.json |
| Post-processing | `news-pipeline/tools/process.py` | News-specific orchestrator. Calls scrub.py + tick_cut.py + zoom.py + cap-dead. Applies Rules N1 + N2 |
| Final compose | `news-pipeline/tools/news_render.py` | News Hyperframes renderer (title + recording + Polaris outro) |
| Portfolio XLSX import | `news-pipeline/tools/xlsx_to_portfolio.py` | For when a client provides a real `.xlsx` |
| Portfolio library | `news-pipeline/portfolios/<id>/` | Each portfolio is a subfolder with fixed-name files: `holdings.csv` + `summary.md` |
| Prompt files | `news-pipeline/prompts/<id>.txt` | One file per use case; what capture.py types verbatim |
| Recordings | `news-pipeline/recordings/N<n>/` | Auto-numbered; capture.py writes here |

The orchestration logic is **conversational**, not a script — when the user describes a use case, follow the phases below using your normal capabilities (read files, write files, run Bash). Do not build a separate `orchestrate.py` or CLI wrapper.

## Hard rules

1. **Never use a prompt that triggers the `parallax:scenario` tool.** That tool asks clarifying questions ("How should I scope this?") and stalls Claude waiting for user input — fatal for an unattended recording. Phrase prompts as direct, scoped questions naming a specific Parallax skill if possible (e.g. "Run a portfolio analysis on…", "Give me a full stock report on NVDA").
2. **Embed portfolios inline in the prompt text.** Do not try to attach files via the `+` button — that's a separate UI automation we haven't built. Inline embedding is what `capture.py` types, and it looks natural in the recording.
3. **Always check Claude desktop is in fullscreen mode** before running capture.py. Calibration coords are only valid in fullscreen. If it isn't, prompt the user to `ctrl+cmd+F` it.
4. **Reuse existing portfolios when the use case fits.** Check `news-pipeline/portfolios/` for a match before generating a new one. Wong Family Trust is the seed template.
5. **Don't mix with the main parallax-video skill.** This pipeline's policy + content lives under `news-pipeline/`. Don't import (Python-level) from `../tools/` or `../automation/`; subprocess-invoke them via CLI instead. Don't write to `../scripts/`; don't drop recordings into `../screen recordings/`. Shared infrastructure (`tools/` + `automation/`) is invoked via subprocess only.
6. **Capture.py runs unattended.** Once invoked, the user is told to leave keyboard/mouse alone. The script may take 30–600s depending on the response length.

## Phase 1 — Intake

The user says something like:
- "Make a news video about Middle East oil exposure for a tech-heavy portfolio"
- "Generate a demo of forensic earnings analysis on NVDA"
- "Draft a portfolio analysis for a Chinese-ADR-heavy book"

Extract from the request:
- **Use case** — what should the demo show? (sector exposure analysis, single-stock deep-dive, portfolio rebalance, etc.)
- **Needs portfolio?** — Yes if the use case requires "given my holdings…" framing; no for direct single-asset queries (e.g. "give me a stock report on NVDA")
- **Required exposure** — what positions must the portfolio have for the answer to be meaningful? (e.g. "≥15% energy" for an oil-shock demo)
- **Target tool** — which Parallax skill should fire? (parallax:portfolio, parallax:stock, parallax:macro, parallax:rebalance, parallax:screen, parallax:etf, parallax:deep-dive)

Briefly tell the user your read of the use case in 2–3 lines, then proceed.

## Phase 2 — Portfolio (if needed)

**If the use case doesn't need a portfolio**, skip to Phase 3.

**If it reuses an existing one**: read the relevant `news-pipeline/portfolios/<id>/summary.md` to know its holdings, and note which one you'll use.

**If a new portfolio is needed**: synthesize one directly (you are the LLM — no API call). Use the Wong Family Trust as a structural template.

Steps to generate:
1. Read `news-pipeline/portfolios/Wong_Family_Trust_2026-04-24/holdings.csv` for the column schema
2. Read `.../summary.md` for the metadata sections you need to mirror
3. Generate a new portfolio with:
   - **Different account name, custodian, advisor firm, mandate** — varied for realism. Examples: "Sterling Family Office", "Meridian Capital Trust", "Bridge Lane Foundation", "Hadar Wealth Partners"
   - **10–20 holdings** with realistic prices, quantities, weights summing to 1.0
   - **Required exposure baked in** (e.g. if Middle East oil shock → ≥15% energy stocks, ideally including Saudi/UAE-listed names like ARAMCO.SR, ADNOCDIST.AD)
   - **Diversified beyond just the use-case area** (don't make a 100% energy portfolio for oil shock — make it 20% energy + 80% other for realistic risk framing)
   - **Plausible CUSIPs/ISINs** — 9-character alphanumeric for US, 12 for international. Approximate is fine; the audience doesn't reconcile against a trustee.
4. Pick a portfolio ID: `<descriptive-name>_<YYYY-MM-DD>` where date is today
5. Write `news-pipeline/portfolios/<id>/holdings.csv` and `<id>/summary.md` directly using Write
6. Briefly summarize the new portfolio to the user (account name, total value, biggest positions, sector mix)

Auto-proceed unless the user originally said "--review" or "review portfolio".

## Phase 3 — Prompt

Compose the Cowork prompt that gets typed into Claude desktop.

Structure:
```
<Direct question framed around the use case>

<Portfolio context if applicable — short comma-separated weights>
```

Rules:
- Name a specific Parallax skill in the prompt if you can ("Run a portfolio analysis on…", "Use parallax:rebalance to…")
- Make the question specific and scoped — no open-ended "what should I do" framings
- Keep the portfolio inline as a one-liner: `NVDA 18%, SPY 12%, MSFT 10%, ...` (not a full CSV — saves typing time + reads natural)
- Total prompt should be 1–4 sentences

Write to `news-pipeline/prompts/<id>.txt` (same `<id>` as the portfolio if there is one; otherwise `<usecase-slug>_<YYYY-MM-DD>.txt`).

Show the prompt to the user in your response before invoking capture.

## Phase 4 — Capture

Tell the user: "I'm about to record. Make sure Claude desktop is in fullscreen mode (`ctrl+cmd+F` if not). Don't touch the keyboard or mouse once it starts."

**Default behavior: capture.py overwrites the highest existing `recordings/N<n>/` slot.** This means re-running for the same use case keeps iterating on the same N — no slot bloat from repeated attempts. The user explicitly says "move on" / "next batch" / "advance to a new recording" to advance.

```bash
# Default — iterate on the current slot. Two steps: capture, then post-process.
python3 automation/capture.py news-pipeline/prompts/<id>.txt
python3 news-pipeline/tools/process.py N<n>     # N<n> = the slot capture just wrote

# When user confirms they want a fresh slot:
python3 automation/capture.py news-pipeline/prompts/<id>.txt --new-slot
python3 news-pipeline/tools/process.py N<n+1>
```

The capture script (`automation/capture.py`):
- Activates Claude desktop (Space switches in)
- cmd+N → new task in Cowork
- ffmpeg starts recording the full screen
- cliclick types the prompt char-by-char
- cmd+Enter to send
- Clicks the newly-created task in the Recents sidebar to navigate into it
- Polls the calibrated stop-button region every 200ms
- After 3 consecutive non-matches (~600ms), declares streaming ended
- Scrolls chat to top + smooth scroll-down read-through (news-specific behavior — Pass 2 will make this opt-in via flag)
- Stops ffmpeg, writes raw.mp4 + trimmed.mp4 + manifest.json
- **Exits** — post-processing is the workflow's responsibility (no longer auto-chained as of 2026-05-29)

The post-process script (`news-pipeline/tools/process.py`):
- Reads `recordings/N<n>/manifest.json` for `phases.streaming_started` (Rule N2)
- Scrubs trimmed.mp4 via `tools/scrub.py` with the typing-window forced at 2× uniform speedup
- Tick-cut via `news-pipeline/tools/tick_cut.py` (Progress-sidebar tick montage compression)
- Applies zooms via `tools/zoom.py` if `zooms.json` present (or auto_zooms.json from tick_cut)
- Caps dead-time per Rule N1 (max 1s freeze in post-tick region)

When the chain finishes, surface to the user:
- The path to `news-pipeline/recordings/N<n>/zoom.mp4` (or `raw.mp4` if process.py wasn't run)
- Key manifest stats: duration, samples_streaming/idle (sanity check)
- Any ffmpeg.log warnings if present

## When to invoke this skill

Trigger phrases (and the action):

| User says | Action |
|---|---|
| "Make a news video about X" | Full pipeline: intake → portfolio → prompt → capture (overwrites the current slot by default) |
| "Generate a demo for [client/scenario]" | Same |
| "Capture this prompt" + a prompt file path | Skip to Phase 4 (overwrite current slot) |
| "Re-run" / "try again" / "the recording was bad, retry" | Re-run capture.py without `--new-slot` — overwrites current N<n>/ |
| "Move on" / "next batch" / "advance to a new recording" / "lock this one in" | Re-run with `--new-slot` so the next capture lands in N<n+1>/ |
| "Draft a portfolio for [use case]" | Phase 2 only — generate portfolio, don't draft prompt or record |
| "Draft a prompt for [portfolio + use case]" | Phase 3 only |
| "Import this XLSX as a portfolio" | Run `tools/xlsx_to_portfolio.py <path>` via Bash |
| "Re-calibrate" | Tell user to run `python3 automation/calibrate.py` themselves (it's interactive — they have to read coords and switch Spaces) |
| "Dump Claude's UI" / "the auto-allow isn't working" | Tell user to run `python3 automation/dev/diagnose_ui.py` while a permission dialog is showing |

## File layout

```
automation/                             ← shared layer (used by news AND product-demo)
├── capture.py                          ← Claude-desktop driver + ffmpeg recorder
├── calibrate.py                        ← one-time calibration
├── calibration/                        ← shared calibration data
│   ├── claude-desktop.json             ← coord config + window bounds
│   ├── send-idle.png, send-streaming.png
│   └── window_full.png, window_streaming.png
└── dev/                                ← scroll/wake/flush diagnostic harnesses

news-pipeline/
├── README.md                           ← user-facing overview
├── portfolios/
│   ├── README.md                       ← schema spec
│   └── <id>/
│       ├── holdings.csv
│       └── summary.md
├── prompts/
│   └── <id>.txt                        ← what capture.py types verbatim
├── recordings/
│   └── N<n>/
│       ├── raw.mp4
│       ├── trimmed.mp4
│       ├── manifest.json               ← timing + tuning stats
│       ├── zoom.mp4                    ← after process.py
│       ├── final.mp4                   ← after news_render.py
│       └── ffmpeg.log
├── outputs/                            ← reserved for final-render outputs
└── tools/
    ├── process.py                      ← news's pipeline orchestrator (Rules N1+N2)
    ├── tick_cut.py                     ← Progress-sidebar tick montage compression
    ├── news_render.py                  ← news Hyperframes composer
    └── xlsx_to_portfolio.py            ← portfolio XLSX importer
```
