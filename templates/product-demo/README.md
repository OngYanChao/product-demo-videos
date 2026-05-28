# Parallax V1 — Quick Stock Research Brief

A HyperFrames video composition. Plain HTML + GSAP; rendered to MP4 by the `hyperframes` CLI.

**Runtime:** 78 seconds, 1920×1080
**Structure:** title card (0–5s) → screen recording with overlays (5–71s) → outro (71–78s)

## Requirements

- **Node.js 22+** — [nodejs.org](https://nodejs.org/)
- **FFmpeg** — `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Debian/Ubuntu) or [ffmpeg.org/download](https://ffmpeg.org/download.html) (Windows)

Verify: `npx hyperframes doctor`

## Assets

- `assets/screen-recording.mp4` — the 66s product capture (already in place)
- `assets/avatar.mp4` — **placeholder** for the HeyGen avatar render. Drop in when ready; the composition will pick it up automatically if you wire it into the `#avatar` element (currently uses a styled silhouette fallback).

## Preview

```bash
npx hyperframes preview
```

Opens the HyperFrames Studio at `http://localhost:3002` with frame-accurate scrubbing.

## Refine with Claude Code

```bash
npx skills add heygen-com/hyperframes
npx hyperframes lint
npx hyperframes preview
```

Likely refinements:

- Tune the avatar fade-in (currently 0.8s `power2.out` at t=5.0) if it competes with title fade-out (which ends exactly at t=5.0)
- Consider a soft `light-leak` shader on title→recording (5s) and recording→outro (71s) once the avatar render is in place

## Render

```bash
npx hyperframes render index.html -o output.mp4
```

1920×1080 / 30fps by default. Use `--fps 60` or `--resolution 3840x2160` to override.
