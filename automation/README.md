# automation/

Shared Claude-desktop driving + screen-recording infrastructure. Workflow-agnostic — consumed as subprocess CLI calls by both the **news-pipeline** workflow and the **product-demo** workflow (via the `"capture V<N>"` dispatch in `parallax-video/SKILL.md`).

Extracted from `news-pipeline/tools/` on 2026-05-29 so the recording layer is no longer owned by one workflow.

## What's in here

| Path | Purpose |
|---|---|
| `capture.py` | The Claude-desktop driver. Reads a prompt from a text file, drives Claude desktop via cliclick keystrokes, starts an ffmpeg screen recording, detects end-of-streaming via dual-region stop-vs-mic match, runs the post-streaming read-through dance (scroll-to-top + smooth scroll-down at 300 px/s — captures the brief read-through for both news and product-demo workflows), auto-trims the scroll-up flicker segment, writes `raw.mp4` + `trimmed.mp4` + `manifest.json` into the slot. The `--no-readthrough` flag opts out of the scroll dance entirely (callers that just want the brief in its post-streaming state). **Exits when done** — post-processing is the workflow's responsibility. |
| `calibrate.py` | One-time setup. Detects display + Retina scale, captures the bottom-bar mic + stop icons in idle vs streaming states, saves `calibration/claude-desktop.json`. Re-run when display / theme / Claude desktop changes. |
| `calibration/` | Calibration data — `claude-desktop.json` (coords + window bounds) + reference PNGs (`send-idle.png`, `send-streaming.png`, `window_full.png`, `window_streaming.png`). |
| `dev/` | Diagnostic + test harnesses developed alongside capture.py. Investigate Chromium wake throttling, scroll-event flush behavior, smooth-scroll cadence. Not part of the production pipeline; useful when capture.py breaks against a new Cowork build. |
| `capture.py.bak-with-flush` | Working-with-window-swap-flush backup of capture.py for quick revert if the dual-region detection regresses. |

## Design principle: no policy in shared tools

`automation/` provides **data, not policy.** capture.py records and emits a manifest; calibrate.py establishes coordinates. Neither knows about news's tick-cut rules or product-demo's multi-zone scrub lock. Each workflow's orchestrator (`news-pipeline/tools/process.py`, `parallax-video/SKILL.md`) consumes the recording + manifest and applies its own policy.

If you find yourself adding a workflow-specific knob to capture.py (e.g., a `--mode news` flag), stop — the workflow-vs-workflow distinction belongs in the caller. Compose orthogonal behavior flags instead. See `.claude/skills/news-pipeline/SKILL.md` § Hard rules and `.claude/skills/parallax-video/SKILL.md` (Phase 2 dispatch, Pass 2) for how the workflow-specific behavior is applied at the call site.

## Manifest contract

`automation/capture.py` writes `manifest.json` alongside `raw.mp4` and `trimmed.mp4`. The schema is the load-bearing contract between this shared layer and its consumers.

### Universal fields (every capture writes these)

| Field | Type | Meaning |
|---|---|---|
| `n` | int | Slot number (e.g., `11` for `recordings/N11/`) |
| `prompt_file` | string | Path to the prompt file that was typed |
| `prompt_text` | string | Verbatim text that was typed |
| `started_at` / `ended_at` | ISO8601 | Recording start/end timestamps |
| `duration_s` | float | Recording duration in seconds |
| `interrupted` | bool | Whether the recording was killed mid-run |
| `samples_total` / `samples_streaming` / `samples_idle` / `samples_failed` | int | End-of-streaming detector sample counts (debugging) |
| `claude_window_id` | int | macOS CoreGraphics window ID at capture time |
| `claude_window_bounds` | object | `{X, Y, Width, Height}` of Claude's window at capture time |
| `calibration_used` | string | Path to the calibration JSON used (relative to repo root) |
| `phases.streaming_started` | float | Seconds into raw.mp4 when Claude began streaming (= approximate `T_typing_end`). **Load-bearing for product-demo Phase 3 Hard Rule #21 multi-zone lock + news Rule N2 typing speedup.** |
| `phases.streaming_ended` | float | Seconds into raw.mp4 when streaming completed |
| `tuning` | object | Detector parameters (poll interval, debounce frames, framerate) |
| `trimmed_file` | string \| null | Name of the trimmed.mp4 (if scroll-up trim succeeded), else null |

### Read-through phase fields (written when the scroll dance ran — default behavior)

| Field | Meaning |
|---|---|
| `phases.scroll_to_top_done` | When chat scroll-to-top completed |
| `phases.smooth_scroll_chat_start` / `phases.smooth_scroll_chat_end` | Chat scroll-down read-through window |
| `phases.smooth_scroll_doc_start` / `phases.smooth_scroll_doc_end` | Doc-panel scroll-down read-through window (if a doc was visible) |

Both workflows (news + product-demo) capture with the scroll dance on by default. The fields are absent only when a caller explicitly passes `--no-readthrough`.

## Consumers

- **news-pipeline** (today): `news-pipeline/tools/process.py` reads `phases.streaming_started` for Rule N2 (typing window speedup). The news skill (`.claude/skills/news-pipeline/SKILL.md`) invokes `automation/capture.py` then `news-pipeline/tools/process.py` as a 2-step Bash sequence.
- **product-demo** (Pass 2, landed): Phase 3 scrub dispatch in `parallax-video/SKILL.md` reads `phases.streaming_started` as authoritative `T_typing_end` instead of frame-sampling. The `"capture V<N>"` trigger in `parallax-video` invokes `automation/capture.py` with `--slot-dir "screen recordings/V<N>"` (and the scroll-through read-through on, same as news — Phase 5.5 zoom freeze-frames during annotate panels). Post-renames `trimmed.mp4` → `vid<N>.mp4` (canonical Phase 3 input) and `raw.mp4` → `vid<N>_raw.mp4` (archival).

## Calibration

Run once per machine + display config:

```bash
python3 automation/calibrate.py
```

This activates Claude desktop, asks you to read the mic + stop icon coords via `cmd+shift+4`, captures reference crops in idle and streaming states, verifies they're distinguishable, and writes `automation/calibration/claude-desktop.json`. Re-run if you switch displays, change Claude's theme, or Claude desktop is redesigned.

## Manual setup (one-time, per machine)

1. `brew install cliclick`
2. `python3 -m pip install pyobjc-framework-Quartz`
3. Grant Accessibility permission to your terminal (System Settings → Privacy & Security → Accessibility)
4. Grant Screen Recording permission to your terminal (System Settings → Privacy & Security → Screen & System Audio Recording)
5. Run calibration

## Coordinate spaces

macOS has two coordinate systems on Retina displays:

- **Logical (1×)**: used by AppleScript window positioning, `cliclick` mouse coords, `cmd+shift+4` readouts
- **Physical (2×)**: used by `screencapture` output, `ffmpeg` capture

`calibrate.py` stores both. Don't mix them in calling code.

## Cross-Space capture

Claude desktop runs in macOS true-fullscreen mode (its own Space). `screencapture -R` only captures the currently-visible Space, so capturing Claude's UI from the terminal Space gives you the desktop wallpaper instead. The fix: find Claude's CoreGraphics window ID via Quartz, then use `screencapture -l <wid>` to capture the window's content directly. This works as long as Claude is active (in front), so the calibrator + capture script activate Claude (Space-switches) before each shot.

## Where the news policy + product-demo policy live (not here)

This README does NOT document workflow-specific rules. Those live where they're authoritative:

- News: `news-pipeline/README.md` § News-pipeline-specific hard rules (N1, N2)
- Product-demo: `.claude/skills/video-production-workflow/SKILL.md` Hard Rules #1–#25
- News orchestration: `.claude/skills/news-pipeline/SKILL.md`
- Product-demo orchestration: `.claude/skills/parallax-video/SKILL.md`

When changing `automation/capture.py`'s behavior, check that both workflows' policy still composes cleanly on top.
