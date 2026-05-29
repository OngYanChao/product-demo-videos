# news-pipeline

**Status:** experimental — Phase 1 (foundation/calibration) complete.

A *separate* workflow from the main product-demo pipeline. The idea: news event → LLM drafts a Parallax prompt → Claude desktop is driven via keystroke automation → output is captured → pipeline scrubs loading dead-time and renders a short demo video reacting to the news.

This directory holds **news-specific** policy + content. It consumes two shared layers from the project root: `tools/` (scrub.py, zoom.py, detect_ticks.py, etc.) and `automation/` (capture.py, calibrate.py + calibration data — the Claude-desktop driver). Both shared layers are invoked as **subprocesses or direct CLI calls** — no Python-level imports across folder boundaries. If the news experiment doesn't pan out, `rm -rf news-pipeline/` still leaves both shared layers + the main product-demo pipeline untouched.

## Architecture (current)

```
1. (optional) tools/draft_prompt.py    → LLM drafts a Parallax prompt (TBD)
2. automation/capture.py               → drive Claude desktop, record screen,
                                         detect end-of-streaming via the
                                         stop/mic dual-region match, scroll
                                         chat to top, smooth scroll-down
                                         read-through, then auto-trim the
                                         scroll-up segment
                                         → recordings/N<N>/raw.mp4
                                         → recordings/N<N>/trimmed.mp4
                                         → recordings/N<N>/manifest.json
3. tools/process.py                    → news's pipeline orchestrator. Invoked
                                         after capture.py by the news skill
                                         (was auto-chained inside capture.py
                                         pre-2026-05-29; capture.py is now
                                         workflow-agnostic). Scrubs trimmed.mp4
                                         + (if zooms.json present) applies
                                         zooms via the project root's
                                         tools/scrub.py + tools/zoom.py.
                                         → recordings/N<N>/zoom.mp4
                                         Standalone-callable for re-runs
                                         without re-recording (edit zooms.json
                                         and re-invoke process.py)
4. tools/news_render.py                → compose final news video (Hyperframes;
                                         title + recording + Polaris outro)
                                         → recordings/N<N>/final.mp4
```

## End-of-streaming detection (dual-region stop-vs-mic)

The detector watches BOTH the stop-button region (vs `send-streaming.png`) AND the mic region (vs `send-idle.png`) and decides by **which reference matches better** — not an absolute threshold. Earlier single-reference detection mis-read the post-streaming "Opus 4.7 ⌄ + mic" layout as still-streaming for ~130s because the mean diff stayed at 9.5 (below the 12.0 cutoff). The relative comparison flips the instant the mic appears, so the post-streaming sequence fires within ~1s of true end of output. With prompt detection the renderer never drifts into Chromium's deep-throttle state, so the synthetic scroll-up paints on the first try with no window-swap flush needed.

A `reset_cowork_window()` helper (Cmd+H hide → reshow) is defined but currently unused — it's a parked backstop in case a future Cowork build introduces faster compositor throttling. A working-with-flush backup of `capture.py` is preserved at `automation/capture.py.bak-with-flush` for quick revert.

## Hard rules inherited from the main pipeline

The news-pipeline is *not* automatically bound to the main pipeline's hard rules — it's a separate workflow with no script, no beat sheet, no avatar. But the **quality / craft** rules apply (they govern video output, not script structure), and the **script-driven** rules don't apply (no script in news).

Authoritative versions live in the main pipeline. These are *pointers, not copies* — when a rule changes there, this table needs reviewing.

**Hard rules in `.claude/skills/video-production-workflow/SKILL.md` (numbered list starting ~line 165):**

| # | Rule (short) | Applies? | News-pipeline mapping |
|---|---|---|---|
| 1 | Beat sheet upstream | **No** | No script / no beat sheet |
| 2 | Conform recording, don't compress script | Partial | We compress aggressively, but only inter-tick dead time + scrub gaps. User-visible content (prompt typing, response, scroll) is preserved. |
| 3–5 | LTs/graphics → beat windows; recording contains beat content; dwell:y is beat-sheet property | **No** | Stripped from news template |
| 6 | Cut whole beats | **No** | No beats |
| 7 | Every on-screen claim cites a frame | **No** | No script |
| 8 | Preview free, final billed | **N/A** | No HeyGen avatar in news (silent output) |
| 9 | Pause-zoom sized by beat sheet | **No** | Auto-zoom is sized by `tick_cut`'s output structure |
| **10** | **Pixel bounds measured, not eyeballed** | **Yes** | `tick_cut.py` invokes `tools/detect_ticks.py`; Progress-sidebar region was measured via crop, not eyeballed |
| 11 | Colour-space consistency in zoom segments | Yes (passive) | `tools/zoom.py` enforces; news uses it unmodified |
| **12** | **Re-derive after every re-zoom/scrub** | **Yes** | `render.py` reads `zoom.mp4` duration via ffprobe and re-anchors comp/outro timings every run |
| **13** | **Never slow source** | **Yes** | News only cuts/trims; never `setpts`-stretches |
| **14** | **Source preserved until explicit approval** | **Yes** | `raw.mp4` + `trimmed.mp4` preserved; downstream `zoom.mp4`/`final.mp4` are derived |
| **15** | **60fps + 1s keyframes** | **Yes** | `capture.py FFMPEG_FRAMERATE=60`; `render.py` passes `--fps 60 --quality high` to Hyperframes |
| 16 | Cursor-clear on output-brief zooms | **No (per rule scope)** | The rule explicitly excludes "tool-call loading sections (the chat activity area)" — the news auto-zoom is on the Progress sidebar (loading area), so out of scope |
| 17 | Annotate spotlights in vertical safe zone | **No** | News uses `mode: "follow"`, not annotate |
| 18 | Overlay ease matches camera ease | Conditional | No overlays in news template currently; if added, this applies |
| 19 | Clean source segments between annotate holds | **No** | No annotates in news |
| **20** | **Tick timestamps detected programmatically** | **Yes** | `tick_cut.py` uses `tools/detect_ticks.py`, never hand-tunes |
| 21–25 | Multi-zone 1× lock; z0 ease-out at T_click; standard z0/z0b/z1..zN skeleton; annotate highlight measurement; panel-hold minimum | **No** | All specific to the product_demo zoom skeleton; news has its own auto-zoom on the Progress sidebar |

**Project-specific principles in `references/production-principles.md`** — primarily about script-driven product demos (value-framing, NL prompts in demo, vault-stats integrate, customer's-chair framing). All currently **No** for news (no script).

**Polaris closer** (Parallax wordmark + "Solve the market." tagline) — inherited verbatim via the news template's copy from `templates/product-demo/index.html` Scene 3.

### News-pipeline-specific hard rules

Rules that don't exist in the main pipeline because they're specific to the news-pipeline's no-script, recording-driven shape. Listed here as the authoritative encoding site.

| # | Rule | Enforced by | Decision |
|---|---|---|---|
| **N1** | **1s dead-time cap on the post-tick region.** Any freeze >1s after the auto-zoom timeline ends (= start of the full-frame post-tick segment) is capped to 1s. Catches the two specific dwells the user identified: (a) the dead time between "output brief done loading" and the auto-trim cut to the top of the chat, and (b) the trailing dead time after smooth-scroll-down completes, before the Polaris outro. Pre-tick (prompt typing) and tick-montage (phase-transition holds) are explicitly protected — typing pauses and phase holds are intentional pacing. | `tick_cut.cap_dead_times()` called from `process.py` after `zoom.py`; uses ffmpeg `freezedetect` (`-45dB`, `min_dead_s=1.0`) to find offending freezes, then ffmpeg `trim+concat` to cap them. Disable per-run with `process.py --no-cap-dead`. | [`decisions/2026-05-28-news-1s-dead-time-cap.md`](../decisions/2026-05-28-news-1s-dead-time-cap.md) |
| **N2** | **Prompt-typing segment is speedup-OK, never cut.** From `t=0` through the moment Claude begins streaming, `scrub.py` must use uniform speedup (anchor speed, default 2×) — never `tapered_with_cut` or any frame-drop treatment. Diverges from main-pipeline Hard Rule #21 (typing at 1×): news videos have a tighter runtime budget and the typing window is context, not load-bearing script content. Speedup preserves the visual continuity of typing-in-progress (characters flow in, just faster); cuts make the prompt appear to teleport, which reads as a recording defect. | **Auto-enforced.** `capture.py` records `phases.streaming_started` in the slot's `manifest.json`; `process.py::_derive_typing_force_range()` reads it (with a 0.5s safety shave) and prepends `--force-speed-range "0:X:2.0"` to its `scrub.py` invocation. Defers to a user-supplied `--scrub-arg --force-speed-range …`. Per-run opt-out: `process.py --no-typing-speedup`. Pre-N2 recordings (no `streaming_started` key in manifest) fall back to scrub's default treatment with a warning. | [`decisions/2026-05-29-news-typing-never-cut.md`](../decisions/2026-05-29-news-typing-never-cut.md) |

### How this gets enforced

By **glance, not by automation**. Anyone (including future-me) touching the news-pipeline should open this section first; the **bold** rows are load-bearing for video quality. The 60fps miss earlier this session traced directly to not having this table — `news-pipeline/tools/render.py` was built without ever cross-referencing the main pipeline's rule set.

## Phase 1 — foundation (current state)

- [x] Install `cliclick`, verify `ffmpeg` avfoundation, verify Python PIL
- [x] Install `pyobjc-framework-Quartz` (for window-ID lookup)
- [x] `automation/calibrate.py` — fullscreen Claude, capture mic + stop button references via cross-Space window-ID capture
- [x] `automation/capture.py` — drives Claude desktop + records (relocated to shared automation/ layer 2026-05-29)

## Manual setup (one-time)

1. `brew install cliclick`
2. `python3 -m pip install pyobjc-framework-Quartz`
   (note: use `python3 -m pip`, not `pip` — `pip` may belong to a different Python install like anaconda)
3. **Grant Accessibility permission to your terminal**:
   System Settings → Privacy & Security → Accessibility → enable for Terminal / iTerm / Ghostty / whatever you use.
   Without this, AppleScript window-positioning and `cliclick` keystrokes silently fail.
4. **Grant Screen Recording permission** to the same terminal:
   System Settings → Privacy & Security → Screen & System Audio Recording.

## How the cross-Space capture works

Claude desktop runs in macOS true-fullscreen mode (its own Space). The terminal lives in your regular Desktop Space. Plain `screencapture -R x,y,w,h` only captures the currently-visible Space, so capturing Claude's UI from the terminal Space gives you the desktop wallpaper instead of Claude.

The fix: find Claude's CoreGraphics window ID via Quartz, then use `screencapture -l <wid>`, which captures the window's content directly. This works as long as Claude is active (in front), so the calibrator activates Claude (Space-switches) before each shot.

## Coordinate spaces

macOS has two coordinate systems on Retina:
- **Logical (1×)**: used by AppleScript window positioning, `cliclick` mouse coords, `cmd+shift+4` readouts
- **Physical (2×)**: used by `screencapture` output, `ffmpeg` capture

Calibration stores both. Don't mix them.

## Running calibration

```bash
# from project root:
python3 automation/calibrate.py
```

The script will:
1. Activate Claude desktop and put it in macOS fullscreen
2. Detect screen size + Retina scale
3. Capture a reference screenshot of Claude's window
4. Ask you for the microphone icon's screen coords (read via `cmd+shift+4`)
5. Ask you to trigger a streaming response and read the stop icon's screen coords
6. Self-test: confirm the mic location is state-sensitive (its appearance changes between idle/streaming)
7. Save calibration to `calibration/claude-desktop.json` plus reference PNGs

You only need to do this once per machine (re-run if you switch displays, theme, or Claude desktop is redesigned).