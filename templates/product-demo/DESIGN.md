# Parallax V1 — Design Reference

Brand identity tokens used in this composition. All values are pulled from the Chicago Global colour kit (`uploads/colour-kit.md`).

## Palette

| Token        | Hex       | Role                                                       |
| ------------ | --------- | ---------------------------------------------------------- |
| `--bg`       | `#0C1D30` | Composition background (`navy-950`, the deeper Parallax navy)        |
| `--navy-900` | `#0C2746` | Title card gradient start, outro background, lower-third gradient |
| `--navy-700` | `#154175` | Title card gradient end                                    |
| `--navy-400` | `#547498` | Avatar PiP border (corner pose, default)                   |
| `--navy-200` | `#92A6C1` | Title wordmark, subtitle, lower-third eyebrow, outro tagline |
| `--ink`      | `#FFFFFF` | All primary copy, lower-third headlines, outro wordmark |
| `--accent`   | `#ED7D31` | Eyebrow chip, accent rules (title + outro), lower-third stripe |

## Typography

- **Family:** Inter — weights 400, 500, 600, 700, 800 (Google Fonts)
- **Title headline:** 92px / 800 / -0.018em
- **Outro wordmark:** 168px / 800 / -0.026em
- **Lower-third headline:** 42px / 700 / -0.012em

## Composition timeline

```
0s ─── 5s ─────────────────────── 71s ─── 78s
│ Title │ Recording (66s) + overlays │ Outro │

Avatar PiP (updated 2026-05-14 — corner-only, no bookend):
  5s ──────────────────────── 71s
  │ fades in at corner (0.8s) │ holds 22%×24% @ 74%/72% │

Chicago Global logo (top-center, white via CSS filter):
  Title card (0–5s): 64px tall
  Outro (last 7s): 72px tall

Watermark "Parallax" (bottom-left): 5–71s persistent

Lower-thirds:        9–16  ·  28–38  ·  54–64  ·  64–70
```

> Captions were specified in the original Claude Design output but **removed 2026-05-08** — they overlapped on-screen brief text during zoom segments. See `RENDER-GUIDE.md` "No captions" rule.
