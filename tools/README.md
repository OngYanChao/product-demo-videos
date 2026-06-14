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

## CLI binaries (external)

| Binary | Path | Purpose |
|---|---|---|
| `heygen` | `~/.local/bin/heygen` | HeyGen API client. Used by `heygen-video` skill. Auth via `HEYGEN_API_KEY` in `.env`. |
| `npx hyperframes` | via npx | Hyperframes CLI: `init / lint / inspect / preview / render / transcribe / tts / doctor`. |

## Conventions

- All tools are callable from cron / OpenClaw — no interactive prompts, exit-code-based success/failure.
- All measurement tools (`measure_highlight.py`, `detect_ticks.py`) follow the "measured, not eyeballed" discipline — outputs are pasted into JSON config, never hand-edited.
- Run `python tools/<name>.py --help` for full flag documentation. This README captures only defaults that are load-bearing across sessions.
