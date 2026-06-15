# tools/

Deterministic helpers for the Parallax video pipeline. Each tool has a `--help` with full flag documentation; this README is the high-level catalog plus key defaults that need to survive across sessions. Relocated from CLAUDE.md 2026-05-22.

## Tool catalog

| Tool | Purpose |
|---|---|
| `scrub.py` | Tapered scrub of dead loading time. Frame-diff detection, anchor-and-cut for long freezes. Default: 2× speedup for short freezes, hard-cut middle (preserve front/back anchors) for ≥10s freezes. **Default `--diff-threshold=-45dB`** — tuned against V1's Cowork plugin chrome (spinner + text-highlight-wave loading); -60dB was too conservative, -40dB too aggressive. Override per-recording if a future video has a visually different loading pattern. |
| `extract_frames.py` | Extract evenly-spaced JPG stills from a video. Default: 1 frame every 2s, downscaled to 960px. Outputs `index.md` mapping frame # ↔ timestamp. |
| `render.py` | Main per-video render (preview + final modes). Reads script frontmatter, substitutes into template, calls `heygen-video` for avatar (cached by script hash), runs `npx hyperframes render -o outputs/V<N>/<mode>.mp4`. Handles both `V<N>` (use_case) and `I<N>` (instructional) script paths. |
| `script_hash.py` | Cache key util — hashes script body for avatar-clip caching. Extracts blockquoted VO lines from `## Voiceover script` section only; filters out stage-direction-only lines. |
| `verify_render.py` | Frame-diff verification masking the avatar bbox — compares render output to expected. |
| `zoom.py` | Script-driven pause-zoom-hold-resume + follow-mode + annotate-mode. Reads JSON list of zoom directives, produces MP4 with zoom segments inserted. Runs at **Phase 5.5** (after the script is locked) — zoom targets are derived from what the VO names in each `dwell:y` beat. Annotate-mode renders a left-anchored crop with a soft-edged elliptical spotlight over the named content + reserved right-band for the template's annotation panel. Mandatory ≥1.5s pause between consecutive zooms. |
| `measure_highlight.py` | Programmatic `highlight_region_pct` snapping for `mode: "annotate"` directives. Detects text rows in the highlight's x slice (count-based bright-pixel detection + 3-row dilation, catches sparse fragments like "246)."), then snaps the y bounds to the natural top/bottom gaps of the row run. Outputs the refined region_pct JSON snippet. Optional `--debug-overlay` writes a PNG with the rough (red) vs refined (green) rectangles. Use `--skip-x` for multi-column highlights (e.g., a whole table row); the default x-snap is meant for single-column highlights and can collapse multi-column rough rects. Per Hard Rule #10 in `video-production-workflow`. |
| `detect_ticks.py` | Programmatic detection of "tick" events (visual state transitions) in a sub-region of a recording — for the gap-cut tick-window compression on progress sidebars, status checklists, etc. Samples frames at high fps in the search region, computes frame-to-frame mean absolute pixel diff, returns top-N peaks (non-maximum suppression separates adjacent peaks). Outputs precise tick timestamps + ready-to-paste `ffmpeg_keep_ranges` for the trim+concat filter graph — never eyeball tick timestamps. Per Hard Rule #20 in `video-production-workflow`. Companion to `measure_highlight.py` — same "measured, not eyeballed" discipline. |
| `static_gateway.py` | Hard Rule #30 static-placeholder gateway. Probes the Cowork Progress sidebar over `[manifest.streaming_started, streaming_ended]` to distinguish static-placeholder mode (zero real tick transitions — "See task progress for longer tasks." graphic, V3 case) from dynamic-checklist mode (numbered phases with status indicator transitions — N1 case). On static detection: applies a 3.0s flash pre-cut to the loading window and signals downstream to skip z0b. Magnitude threshold (3.0) separates real checkmark transitions (N1: 6-9) from sidebar noise (V3: <2). Shared by news-pipeline (`process.py`) and product-demo (Phase 3 dispatch). Per Hard Rule #30 in `video-production-workflow`. |
| `lint_video.py` | Mechanical Hard-Rule check for V-series + I-series videos. Reads project artifacts (frontmatter, zooms.json, scrub report, ticks, render manifest, ffprobe) and asserts every Hard Rule that's deterministically checkable. **22 rules** split into Tier 1 (errors — L01–L11: timing sync, framerate, safe-zone, z0/z0b sizing, skeleton, panel-hold floor, highlight tier) and Tier 2 (warns — L12–L22: banned-engineering-phrases, slash-cmd-in-VO, capability-counts, draft markers). $0 always. Auto-chains after `render.py --mode preview` (after Phase 6a polish converges) and after `render.py --mode final`. Tier-1 errors stop the chain so the LLM reviewer isn't billed against broken artifacts. |
| `review_video.py` | Vision-based semantic review via `claude-opus-4-7`. The LLM tier the linter can't do — reads VO body, panel copy, frame stills + does six checks: **R01** subject-match (spotlight ↔ panel pitch, frame-level), **R02** customer's-chair framing (text), **R03** panel-shape rotation (text), **R04** vault-stat integration (text), **R05** beat content visible in recording (frame), **R06** hallucination check on `frames_used:` (frame, Hard Rule #7). Caches responses by content hash at `outputs/V<N>/.review-cache/`; first run ~$0.25, $0 on re-runs against unchanged input. Writes `outputs/V<N>/review.md`. Auto-chains after `lint_video.py` tier-1-clean pass. Skip via `--no-review` on `render.py`. |

For news-pipeline analogues, see `news-pipeline/tools/`:
- `lint_news.py` — 17 mechanical rules covering the news-pipeline rule surface; deterministic, $0 always. Auto-invoked at the end of `news-pipeline/tools/process.py`.
- `news_render.py` — Hyperframes composer for news (title + recording + Polaris outro; no avatar). Per-run temp-dir refactor (2026-06-13) eliminates parallel render race.
- `process.py` — news pipeline auto-chain orchestrator (scrub → tick_cut → zoom → cap_dead → news_render → lint_news).
- `tick_cut.py` — Progress sidebar tick detection + compression + auto-emit z0/z0b zooms.

## CLI binaries (external)

| Binary | Path | Purpose |
|---|---|---|
| `heygen` | `~/.local/bin/heygen` | HeyGen API client. Used by `heygen-video` skill. Auth via `HEYGEN_API_KEY` in `.env`. |
| `npx hyperframes` | via npx | Hyperframes CLI: `init / lint / inspect / preview / render / transcribe / tts / doctor`. |

## Conventions

- All tools are callable from cron / OpenClaw — no interactive prompts, exit-code-based success/failure.
- All measurement tools (`measure_highlight.py`, `detect_ticks.py`) follow the "measured, not eyeballed" discipline — outputs are pasted into JSON config, never hand-edited.
- Run `python tools/<name>.py --help` for full flag documentation. This README captures only defaults that are load-bearing across sessions.
