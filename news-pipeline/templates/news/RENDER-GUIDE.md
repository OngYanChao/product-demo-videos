# News template — render guide

How to render a Parallax news-pipeline video using this template. Read before generating.

## Structure of this template

A 1920×1080 composition with three logical sections. **Total runtime = 5s (title) + scrubbed recording length + 7s (outro).**

| Section | Duration | Visible elements |
|---|---|---|
| Title card | **fixed 5s** | Eyebrow ("Parallax news brief"), headline (auto-derived from the prompt), accent rule, navy gradient |
| Recording body | **variable — equals `zoom.mp4` length** | Full-bleed screen recording (the scrubbed + tick-cut + zoomed Cowork run), "Parallax" watermark bottom-left |
| Outro | **fixed 7s** | "Parallax" wordmark, accent rule, "Solve the market." tagline |

There is **no avatar talking-head clip** in this template (unlike the product-demo template's V-series). News videos are autonomous — Cowork's product UI carries the demonstration, the title card sets context, and the Polaris closer signs off. The video element in scene s2 plays the recording silently end-to-end.

There are **no lower-thirds, panels, or spotlight annotates** in this template. News-pipeline doesn't author a script-driven editorial layer — the deliverable is "watch Cowork solve this prompt" with a branded wrapper.

## Required inputs (per video)

When `news_render.py` invokes this template, it stages two things into the composition:

| Slot | Format | Path | How it's produced |
|---|---|---|---|
| Screen recording | MP4 | `assets/screen-recording.mp4` | Copied from `news-pipeline/recordings/N<N>/zoom.mp4` (or `trimmed.mp4` if zoom missing). The scrub + tick-cut + zoom + cap_dead pipeline owns this. Must be 60fps with ≤1s keyframe intervals per Hard Rule #15. |
| Title text | string | `<h1 id="t-headline">…</h1>` in `index.html` | Auto-derived by `news_render.py` from the slot's prompt (topic-cue extraction). Override via `--title "..."` on the render CLI. |

That's it. Everything else in the composition is hardcoded brand assets (gradient, wordmark, watermark, tagline) and doesn't change per video.

## Timing — structural vs. per-video

**Structural (fixed for every video using this template):**

| Beat | When |
|---|---|
| Title elements fade-in (staggered) | 0.0 → 1.4s |
| Title hold | 1.4 → 3.5s |
| Title fade-out (`power1.inOut`, 1.5s) | 3.5 → 5.0s |
| Watermark fade-in (during title) | 0.5 → 1.7s |
| Recording body | 5.0 → (5 + recording_duration)s |
| Outro fade-in | (5 + recording_duration) → +0.6s |
| Outro hold + fade-out | 7s total |

**Per-video (`news_render.py` substitutes at render time):**

| HTML attribute | Default placeholder | Substituted with |
|---|---|---|
| `<h1 id="t-headline">…</h1>` | `Twenty minutes of research, in one sentence.` (V1 legacy) | Auto-derived title from prompt, or `--title` value |
| Composition `data-duration` | `"90"` | `5 + recording_duration + 7` |
| Scene s2 `data-duration` | `"78"` | `recording_duration` |
| `<video>` element `data-duration` | `"78"` | `recording_duration` |
| Scene s3 (outro) `data-start` | `"83"` | `5 + recording_duration` |

> **Important:** the placeholders `"78"`, `"90"`, and `"83"` are load-bearing strings that `news_render.py`'s regex looks for. Do NOT edit `index.html` to change these defaults — the substitution will silently no-op and every rendered video will use the previous run's values (this happened during the parallel-render race in 2026-06-13). If the template gets corrupted, restore with `git checkout news-pipeline/templates/news/index.html`.

## Format invariants

These do NOT vary per video. Treat as locked.

- **Resolution:** 1920×1080
- **Framerate:** 60fps (set via `news_render.py --fps`; default 60). Source `zoom.mp4` must already be 60fps.
- **Audio:** none (silent video; `hasAudio: false` in hyperframes trace)
- **Outro tagline:** "Solve the market." — locked Chicago Global brand line. Do not modify per video.
- **Brand colours:** Chicago Global navy + accent rule. See `references/colour-kit.md` (project root).
- **No captions:** the news template never had captions; do not add them.
- **No avatar clip:** the news template does not composite an avatar talking head. That is exclusively for the product-demo template's V-series.

## Workflow

The normal news-pipeline workflow:

```
python automation/capture.py <prompt>          # produces raw.mp4 + trimmed.mp4 + manifest.json
python news-pipeline/tools/process.py N<N>    # chains:
                                              #   scrub → tick_cut → zoom → cap_dead → news_render → lint
                                              # produces: zoom.mp4, final.mp4, lint-report.json
```

`process.py` invokes `news_render.py` automatically — you do not need to run it manually. The render step is free (Hyperframes is local, no HeyGen, no per-clip billing) so it auto-fires on every process. Override with `--no-render` for partial debugging runs.

Manual render (e.g. to re-render with a different title) without re-processing:

```
python news-pipeline/tools/news_render.py N<N> --title "Custom title"
```

## Deliverable

`news-pipeline/recordings/N<N>/final.mp4` — 1920×1080, 60fps, no audio, `5 + zoom.mp4_duration + 7` seconds total.

Lint runs after render (per the process.py chain) and writes `news-pipeline/recordings/N<N>/lint-report.json` with structured findings. L02 (framerate) and L16 (colour space) include `final.mp4` in their checks.

## Cross-refs

- Render tool: `news-pipeline/tools/news_render.py`
- Pipeline orchestrator: `news-pipeline/tools/process.py`
- Lint: `news-pipeline/tools/lint_news.py`
- Hard Rules for the news pipeline: `.claude/skills/video-production-workflow/rules/phase-3-news.md` and `phase-5-5-news.md`
- Brand colour kit: `references/colour-kit.md`
- Product-demo template (different beast, has avatar + LTs + panels): `templates/product-demo/RENDER-GUIDE.md`
