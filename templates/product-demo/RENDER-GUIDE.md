# Product-demo template — render guide

How to render a Parallax product-demo video using this template. Read before generating.

## Current state — important caveat

This template's `index.html` currently has **V1-specific content baked in** — the title copy, lower-third text, and recording duration are all V1. It is *not yet parameterized*. Generating V2 onwards by hand means editing `index.html` for each video.

**Captions removed (2026-05-08).** Captions used to live in the bottom band but they overlapped on-screen brief text during zoom segments — the zoomed paragraph text grew large enough to collide with the caption layer, and on dark UI the white captions also clashed with the brief's body content. The lower-third bars carry on-screen graphic emphasis; the VO carries everything captions used to. Do NOT add captions back to this template — see Format invariants below.

**Phase 5 of `overhaul.md`** (the `parallax-video` orchestrator skill rewrite + `tools/render.py`) introduces frontmatter-driven substitution so this same template can render every video without manual edits. Until that's built, this guide describes the manual flow plus the eventual automated flow.

## Structure of this template

A 1920×1080 composition with three logical sections. **Total runtime = 5s (title) + scrubbed recording length + 7s (outro).** For V1, that's 5 + 66 + 7 = 78s. For other videos, total runtime scales with the scrubbed source.

| Section | Duration | Visible elements |
|---|---|---|
| Title card | **fixed 5s** | Eyebrow, headline, accent rule, sub-tagline, drifting orb, navy gradient |
| Recording body | **variable — equals scrubbed recording length** | Full-bleed screen recording, "Parallax" watermark bottom-left, avatar PiP (corner-pose from t=5.0s onward — no bookend, no settle animation; updated 2026-05-14), lower-thirds (no captions — see "Captions removed" note above) |
| Outro | **fixed 7s** | "Parallax" wordmark, accent rule, "Solve the market." tagline |

## Required inputs (per video)

When you (or the orchestrator) generate a new product demo using this template:

### Assets

| Slot | Format | Path | Notes |
|---|---|---|---|
| Screen recording | MP4 | `assets/screen-recording.mp4` | Must be ≥66s. Already scrubbed via `tools/scrub.py`. Re-encoded with 1s keyframe intervals (see `references/claude-design-to-hyperframes.md`). |
| Avatar clip | MP4 | `assets/avatar.mp4` | HeyGen-rendered talking head. Optional for preview renders. Phase 5 generates this on-demand. |

### Content (currently hardcoded — will move to script frontmatter in Phase 5)

| Slot | Where it lives in `index.html` | V1 value |
|---|---|---|
| Title eyebrow | `#t-eyebrow` | "V1 · Quick Stock Research Brief" |
| Title headline | `#t-headline` | "Twenty minutes of research, in one sentence." |
| Lower-third 1 (eyebrow + headline) | `#lt1` | "V1 · Quick Stock Research Brief" / "Eight parallel skill calls. One natural-language prompt." |
| Lower-third 2 (eyebrow + headline + stats) | `#lt2` | "Vault stat · Peer-reviewed · Out-of-sample" / "ICIR 4.10 · Information coefficient ranking" + 4 vault stats |
| Lower-third 3 (eyebrow + headline + stats) | `#lt3` | "52-week trajectory" / "Score ran 8.8 → 5.9 — Quality never moved" + 3 stats |
| Lower-third 4 (eyebrow + headline) | `#lt4` | "Bottom line" / "Exceptional business at a rich multiple — factor score cooling" |
| Outro tagline | `#o-tagline` | "Solve the market." |

### Timing — structural vs. per-video

**Structural (fixed for every video using this template):**

| Beat | When |
|---|---|
| Title elements fade-in (staggered) | 0.0 → 1.4s |
| Title hold | 1.4 → 3.5s |
| Title fade-out (1.5s `power1.inOut`) | 3.5 → 5.0s |
| Watermark fade-in (during title) | 0.5 → 1.7s |
| Recording body | 5.0 → (5 + recordingDuration)s |
| Avatar fade-in (already in corner) | 5.0 → 5.8s (`power2.out`, 0.8s) |
| Avatar label fade-in | 5.6 → 6.0s |
| Avatar holds in corner | 5.8 → (recording end − 1) |
| Avatar fade-out | recording end + 1s back |
| Watermark visible | entire recording body |
| Outro fade-in (wordmark/rule/tagline staggered) | (5 + recordingDuration) → (8 + recordingDuration)s |

**Per-video (specified in script frontmatter — currently V1-hardcoded):**

LT windows are anchored to **recording-time** (the scrubbed recording's own t=0 = composition t=5). Because the conformed recording inserts pause-zoom segments at `dwell:y` beats, each LT must land on its actual beat window in the *conformed* recording — not the raw scrubbed recording. For V1's 77.47s conformed recording:

| Element | Recording-relative | Composition-absolute | Lands during |
|---|---|---|---|
| LT1 (Open / parallel calls) | 4.0 → 11.0s | 9.0 → 16.0s | Open beat (raw playback) |
| LT2 (ICIR vault stats) | 23.0 → 33.0s | 28.0 → 38.0s | Vault-stat beat (raw playback) |
| LT3 (Trajectory) | 60.0 → 67.0s | 65.0 → 72.0s | z2 zoom hold (subject visible) |
| LT4 (Bottom line) | 72.0 → 74.5s | 77.0 → 79.5s | z3 zoom hold |

**Important:** LTs that should appear during a zoom segment must be timed to the *conformed* recording timeline, which includes the inserted zoom durations. e.g. if z1 inserts 16s of zoom and z2 inserts 10s, recording-time after those zooms is shifted by +26s relative to the raw scrubbed recording. Always re-derive LT timing from the conformed recording's actual beat windows after re-running `tools/zoom.py`.

For V2 onward, frontmatter expresses LT timing as recording-relative offsets, and the orchestrator (Phase 5) computes the composition-absolute times during render.

## Format invariants — apply to every video using this template

These are locked. Do NOT vary per video. They define the consistency of the Parallax product-demo "look."

### Visual identity

- Colors: navy `#0C1D30` (background, also `--navy-950`), navy-900 `#0C2746`, navy-700 `#154175`, navy-400 `#547498`, accent orange `#ED7D31`
- Font: `"Inter"` (literal name in `font-family` — do NOT use `var(--font-display)` or any CSS variable; the Hyperframes font compiler can't resolve through CSS variables)
- Outro tagline (locked): "Solve the market."
- Layout pattern: title card → recording with corner avatar PiP → outro (no other arrangement)

### Frame rate (locked at 60fps)

- **60fps for both the source recording and the rendered output.** Source recording must be encoded at 60fps with 1s keyframe intervals (`-r 60 -g 60 -keyint_min 60`). Renders run at `--fps 60`.
- The 30fps `--quality draft` mode is for layout iteration only — never ship a 30fps render. The recording's native 60fps detail will be visibly lost.

### Layout positions

- **Watermark** (Chicago Global logo, 2026-05-15 — replaced the prior "Parallax" text watermark): **bottom-left** channel-bug, position `bottom: 4%, left: 3.2%`, `104px × 40px`, opacity 0.62 (matches prior text-watermark weight). PNG source rendered white via `filter: brightness(0) invert(1)` on navy background. **Never top-left** — top-left collides with Claude chat chrome that's commonly visible in product-demo recordings. Persists across title card (s1) + recording body (s2); hidden in outro (s3) via `tl.set("#watermark", { autoAlpha: 0 }, scene_3_start)`. Rationale: Chicago Global is the firm-credibility signal for fintech buyers (PM/CIO/analyst); the parent brand travels persistently through the demo while "Parallax" is communicated by the recording UI itself and the outro wordmark.
- **Avatar PiP** (updated 2026-05-14 — corner-only, no bookend pose):
  - **Default + only pose:** bottom-right corner, **22% width × 24% height**, **left 74% / top 72%**, border-radius 22, with a 3px `--navy-400` border (border baked into default CSS — no `.settled` class swap)
  - **Fade-in:** at t=5.0s (recording start), 0.8s `power2.out`. No mid-handoff settle animation; no bookend pose.
  - **Fade-out:** at outro, 1.2s `power2.inOut` (~1s before recording end)
- **Chicago Global logo as big top-center mark** (retired 2026-05-15): the top-center 64px/72px treatment on title card and outro has been removed. The Chicago Global PNG has its own typography that clashed with Inter when displayed at headline scale. The single brand surface for Chicago Global is now the bottom-left corner watermark (see "Watermark" above). Title card and outro are intentionally clean — headline + rule + eyebrow (s1) and Parallax wordmark + rule + "Solve the market." tagline (s3) — with no overlapping firm-brand element.
- **Lower-thirds** (`#lt1`–`#lt4`): bottom band, full-bleed horizontal layout with eyebrow text, headline, and optional stats row. Orange accent stripe on the left edge.
  - **Stat hierarchy** (updated 2026-05-14): each stat is `<span><strong>VALUE</strong> LABEL</span>` inside `.lt-stats`. Visual hierarchy: stat value 38px bold white (the proof — dominant element), stat label 14px grey uppercase tracked (stacked beneath the value via `display: flex; flex-direction: column` on each span). Old 20px-uniform style retired.
  - **Selection + count + rhythm** (per `video-scriptwriting/SKILL.md` Quality Check #8, revised 2026-05-14):
    - **Selection:** each LT must introduce (a) a vault-verified stat with a specific number the VO doesn't recite, (b) the single most important conclusion not readable on screen, or (c) an orientation cue during a low-content stretch where the recording is loading/processing/silent. Restating VO or visible text = cut.
    - **Count by tier (target ranges, not hard caps):** Tier 1 = 2–5 LTs · Tier 2 = 3–7 · Tier 3 = 4–10. Allow more if content earns it; ship fewer if fewer earn their place.
    - **Rhythm:** content-density-driven, not uniform spacing. Cluster where insight density is highest (front-loaded / back-loaded / mid-loaded / mixed are all legitimate patterns).
    - **Attention floor:** no >40s stretch without LT, zoom, annotate-spotlight, or other graphic emphasis — UNLESS the recording itself carries visual interest (parallel calls firing, scrolling, score panel rendering). Don't force an LT to satisfy the floor; fix upstream content gaps.
    - **Self-check:** every LT maps to a VO line; removing it must make the video weaker.

### Recording fit — top-anchored crop (locked 2026-05-18)

The `#rec-video` element uses `object-fit: cover` + `object-position: top center`. For 16:9 sources, this is a no-op. For sources taller than 16:9 (e.g. 16:10 Mac native, 1.594:1 — V1.2's 3420×2146 falls here), the cover-crop is **anchored to the top**, preserving the window title bar / nav tabs / search affordances and cropping the bottom (message-input box, footer) instead.

The bottom is the safe side to crop because:
1. The avatar PiP sits at `left: 74%, top: 72%` and already covers that region.
2. Message-input moments are intentionally zoom-anchored — for multi-tool workflow-chain videos (V7+) that need to show prompt-typing or follow-up message sends mid-recording, add a follow-zoom directive on the input region (V1.2's `z0_prompt_typing` is the canonical example). Don't fall back to pillarbox just to keep the input visible at idle.

**Do not** change `object-fit` to `contain` (pillarbox). Pillarbox forces every video to render with permanent black bars on the left/right, which (a) shrinks the recording and degrades the hero-demo aesthetic across the entire library and (b) loses the focus-signal value of zoom-on-input. Logged: `decisions/2026-05-18-recording-top-anchored-crop.md`.

### Annotate-mode spotlight (locked 2026-05-19; ellipse math revised 2026-05-20)

`mode: "annotate"` zooms render a **soft-edged elliptical spotlight** centered on `highlight_region_pct`:

- Inside the ellipse: source content at full brightness.
- Outside the ellipse (within the scaled-crop area): dimmed at 60 % opacity (`ANNOTATE_DIM_ALPHA = 153`).
- Edge: Gaussian-blurred (~2 % of source height blur radius) so the transition reads as a lighting effect, not a graphic cutout.
- Right ~35 % of the output frame: panel sits on top of the **zoomed-up continuation of the recording** (chat thread, dead space, right sidebar) — not a black band. With `target_w = src_w` (full-frame fill, locked 2026-05-20), the scaled crop spans the entire frame width; the panel overlays the scaled-crop's right portion. Brief lands on the LEFT half of the scaled crop because `zoom_region_pct.x` is at the brief's left edge and `zw` is wide enough to extend past the brief into surrounding dead-space content (V1.2: zw=75, brief at output x=0–53 %).

**Ellipse half-axes circumscribe the highlight rect** — half-axes are scaled by **√2** (≈ 1.414) so the ellipse passes through the rect's corners. This guarantees every pixel of the highlight rect is inside the bright zone, no matter how aspect-ratio-extreme the rect is. (Previously the half-axes equaled the rect's half-dimensions plus a small additive pad — that left the rect's corners *inside the dim zone* because an ellipse with `rx=a, ry=b` only passes through the rect's edge midpoints, not its corners. Tall paragraphs with corner-filling text would have edge words fall into the dim — caught 2026-05-20 on z3 of V1.2.)

**Shape adapts to the rect's aspect:**
- Flat wide rect (e.g. a single text row spanning the brief column): wide flat oval.
- Tall narrow rect (e.g. a single column running multiple lines): tall narrow oval.
- Square rect (e.g. a small icon callout): near-circle.

The ellipse aspect always matches the highlight aspect, sized via the √2 scale plus a small additive buffer (~0.4 % src_w horizontal, ~0.8 % src_h vertical) so the Gaussian blur edge doesn't eat back into the rect from outside.

**Authoring rule: `highlight_region_pct` must cover the WHOLE conceptual unit the panel pitches** — not just the first phrase or top half of it. The spotlight only brightens the rect's content (plus the small blur halo); content outside the rect falls into the dim. If the panel pitches "the Bottom Line verdict," the rect must enclose the Bottom Line header + the whole paragraph, not just the opening sentence. If the panel pitches "the Value factor," the rect must enclose the Value row across all four columns, not just the Factor cell. The unit is whatever the spotlit content the viewer should read while the panel is on screen — author the rect to that bounding box. Caught 2026-05-20 on V1.2 z3, where an earlier draft had the rect at lines 1–3 of the paragraph and the user spotted that lines 4–7 fell into dim. Rule: when in doubt, size the rect to the OUTER bounding box of the conceptual segment, not the inner phrase.

**No rectangle border. No numbered dot beside the spotlight.** The panel on the right carries the numbered badge (`.ap-number`); the spotlight's bright area is its own marker. Both signals are preserved in `tools/zoom.py` in `if False:` blocks for future toggle (rectangle border, numbered dot) — re-enable per-directive via `border_style: "box"` or `show_callout_dot: true` if a future video calls for either.

### Panel animation invariant — ease curve matches camera (locked 2026-05-20)

The `annotatePanel()` GSAP timeline in `index.html` uses **`ease: "sine.inOut"`** with **`duration: 1.0`** for both the in (`fromTo`) and out (`to`) animations. These match `tools/zoom.py`'s annotate ease curve (`ANNOTATE_EASE_NAME = "easeInOutSine"`) and duration (`DEFAULT_ANNOTATE_EASE_S = 1.0`). Both motions progress in lockstep — at 25 % through the 1.0s window, both the panel and the camera are at ~15 % progress.

Previously the panel used `power2.out` (in) + `power2.in` (out). At progress 0.25, `power2.out` is at ~44 % while `easeInOutSine` is at ~15 % — the panel visibly led the camera through the first half of the animation, even though both started at the exact same composition time. The viewer reads "panel is early" even when temporally synced. Caught 2026-05-20 on V1.2 preview.

**Rule:** if `tools/zoom.py`'s `ANNOTATE_EASE_NAME` or `DEFAULT_ANNOTATE_EASE_S` changes, change `annotatePanel()`'s `ease` + `duration` in the same commit. Logged: `decisions/2026-05-20-overlay-ease-matches-camera.md`, Hard Rule #18.

### Annotate-mode colour invariants (locked 2026-05-19)

For `mode: "annotate"` zooms (the left-anchored crop + right-side panel + soft-edged spotlight pattern — see workflow Hard Rules #16 + #17):

- **Spotlight dim**: black at alpha 153/255 (~60 % opacity). Token = `ANNOTATE_DIM_ALPHA`.
- **Right-side panel** (`.annotate-panel` in `index.html`): navy-900 `#0C2746` background, 14 px corner radius. Internal progress-bar header uses 22 / 78 % split of orange `#ED7D31` and `#1b4f8a`.
- **Panel numbered badge** (`.ap-number`): orange `#ED7D31` filled circle with white text inside. Sits at the top of the panel — the only numbered ordering signal in the composition.

Constants for the retired rectangle-border style (navy-400 stroke, orange-paired dot beside the highlight) remain in `tools/zoom.py` (`ANNOTATE_HIGHLIGHT_BORDER_COLOR`, `ANNOTATE_CALLOUT_DOT_COLOR`, etc.) — wired to the `if False:` code paths. Don't reference them in active code.

Orange remains reserved for composition-spanning accents (title-card eyebrow, lower-third stripe, panel badge, outro rule). The spotlight is intentionally untinted — it's a lighting cue, not a brand-coloured graphic element. Logged: `decisions/2026-05-19-annotate-spotlight-default.md` (supersedes `decisions/2026-05-19-annotate-border-dot-navy.md`).

Do NOT override these per-video. If a hypothetical future template targets a non-CG client, swap the `tools/zoom.py` constants — not the per-video `_zooms.json`.

### No captions

Captions were removed (2026-05-08). Reasons:
1. They overlapped on-screen brief text during zoom segments — the zoomed paragraph text was large enough to land in the same vertical band as the captions, making both unreadable.
2. The white-on-transparent caption styling clashed with the brief's body text on dark UI.
3. The VO carries the line-by-line narrative; the LT bars provide the per-beat headline emphasis. Captions added redundancy without information.

**Do NOT add captions back to this template.** The bottom band is reserved for lower-thirds only. If a future video genuinely needs captions, build a separate template family rather than re-introducing them here.

### Title-card layout (locked 2026-05-09)

- **Three elements only, top-down order**: big white hook headline → orange rule → orange tracked subtitle (eyebrow). Centered vertical stack. No top-center wordmark, no sub-tagline. Brand presence = bottom-left "Parallax" watermark, shared with the recording scene (hoisted to root composition level so it spans s1+s2; hidden in s3 outro).
- Pattern reference: B2B fintech "hook-forward + brand-watermark" (Ramp, Notion, Acquired, Carta product tours, Bloomberg/Koyfin terminal demos). The rule between hook and subtitle acts as a "signed off as" mark — hook is the promise, subtitle attributes the publication.
- **HTML element order** in `.title-stack`: `<h1 id="t-headline">` first, `<div id="t-rule">` second, `<div id="t-eyebrow">` last. The element ordering must match the visual ordering (no `flex-direction: row-reverse` tricks) so the GSAP entrance reveals top-down naturally.
- **Reveal animation order** (top-down): headline drops first at t=0.0, rule wipes in at t=0.5, eyebrow fades in at t=0.8. Hero-first cinematic stagger.
- **Headline authoring rule** — the headline wraps via absolute `max-width: 1350px` at Inter Bold 92px. Author each video's headline so the natural wrap lands on a punctuation boundary (comma, em-dash, period). Worked example for V1: "Twenty minutes of research, in one sentence." → "Twenty minutes of research," fits at ~1299px (line 1), "in" pushed to line 2. **Never use `<br>` in headline text** — Hyperframes Rule #11. The substitution layer in `tools/render.py` flattens the `<h1>` element on update, which would silently destroy any `<br>` markers anyway.
- Headline width budget: line 1 must fit in ≤1350px at Inter Bold 92px (CSS `letter-spacing: -0.018em` compresses ~1.8%, so PIL measurements are slightly wider than browser-rendered). Important: do NOT use `%` units for `max-width` — `.title-stack` has 5% padding so a `%` resolves against the content box (1728px), not the full frame (1920px). Use absolute px.

### Animation timing — locked for consistency across videos

| Element | Fade in | Fade out | Easing |
|---|---|---|---|
| Title card elements (top-down: headline, rule, eyebrow) | 1.0–1.4s, staggered 0.0/0.5/0.8s offsets | 1.5s at t=3.5s | `power2.out` in / `power1.inOut` out |
| Avatar fade-in (corner-pose default — no bookend, no settle; 2026-05-14) | 0.8s at t=5.0s | — | `power2.out` |
| Avatar label fade-in (corner) | 0.4s at t=5.6s | — | `power2.out` |
| Avatar outro fade-out | — | 1.2s, ~1s before recording end | `power2.inOut` |
| Lower-thirds | 0.85s | 0.85s | `power2.inOut` |
| Outro elements (wordmark, rule, tagline) | 1.0–1.5s, staggered 0.0/1.0/1.5s offsets from `scene_3_start` | — | `power2.out` |
| Recording → outro transition | hard cut at `scene_3_start` (s2 hides + s3 reveals via `tl.set`); outro element entrance animations carry the visual handoff | — | — |

These easings and durations were tuned during V1 design iteration. Don't alter for cosmetic preference. If brand direction changes, update this table and re-render existing videos for consistency.

## Pre-render checklist

Before running `npx hyperframes render`:

1. ☐ Source recording exists at `screen recordings/V<N>/<vidname>.mp4`
2. ☐ Scrubbed: `python tools/scrub.py "screen recordings/V<N>/<vidname>.mp4"` ran and produced `<vidname>_scrubbed.mp4`
3. ☐ Re-encoded with 1s keyframes (see `references/claude-design-to-hyperframes.md` — should bake into `tools/scrub.py` later)
4. ☐ Recording copied/symlinked to `templates/product-demo/assets/screen-recording.mp4`
5. ☐ Avatar clip at `templates/product-demo/assets/avatar.mp4` (or placeholder for preview)
6. ☐ Per-video content (titles, LTs) is what you want
7. ☐ `npx hyperframes lint .` passes 0 errors

## Render

```bash
cd templates/product-demo

# Draft (30fps, fast turn-around for layout review):
npx hyperframes render . --quality draft

# Standard delivery (60fps, recommended for ship):
npx hyperframes render . --fps 60 --quality standard

# Final (60fps, highest bitrate, slowest):
npx hyperframes render . --fps 60 --quality high
```

Hyperframes' default output is `templates/product-demo/renders/<name>_<timestamp>.mp4`. Two distinct uses for that folder:

- **`renders/template-reference.mp4`** — the canonical "what this template produces" sample. Update only when the template itself changes (layout fix, new slot, animation tweak). Useful for regression checks and onboarding.
- **`renders/<name>_<timestamp>.mp4`** — ad-hoc test renders during template development. Throwaway; clean up periodically.

Per-video deliverables (V1's preview, V5's final, etc.) do **not** live here — the orchestrator (Phase 5 `tools/render.py`) directs those to `outputs/V<N>/preview.mp4` (or `final.mp4`) via the `-o` flag.

## Post-render checklist

Watch the rendered MP4 end-to-end and verify:

1. ☐ Title card displays the right copy and fades cleanly to recording
2. ☐ Recording plays smoothly through the entire 5–71s window (no freezing — if freezing, source video keyframes are too sparse, re-encode)
3. ☐ Chicago Global watermark (bottom-left, ~104×40px, opacity 0.62) is visible throughout title card + recording body, hidden during outro
4. ☐ Avatar PiP fades in at ~5s already in bottom-right corner (no bookend, no settle animation), holds in corner through recording, fades out at outro
5. ☐ Title card is headline-only — no top-center logo, no other brand surface besides the bottom-left watermark
6. ☐ Lower-thirds appear at their scheduled times with correct copy — each card matches a VO line (Quality Check #8); cap of 2-4 LTs per video
7. ☐ Outro shows only "Parallax" wordmark (centre) + rule + "Solve the market." tagline — no top-center Chicago Global logo, no bottom-left watermark
8. ☐ Total runtime equals 5 + scrubbed-recording-length + 7 (e.g., 89s for V1's 77s recording)
7. ☐ Total runtime equals 5 + scrubbed-recording-length + 7 (e.g., 78s for V1's 66s recording)

## Known limitations to fix later

- **Hardcoded V1 content** — Phase 5 will introduce frontmatter substitution so per-video copy (titles, LTs) comes from the script frontmatter, not from manually editing `index.html`
- **Hardcoded recording-body duration** — the timeline currently locks recording at 5–71s (V1's 66s). Phase 5's `tools/render.py` will read the scrubbed recording's duration and update both the root `data-duration` and the GSAP timeline boundaries dynamically. Until then, swapping in a new recording requires manually fixing three timing constants in `index.html` (see top of the GSAP `<script>` block)
- **Per-video LT windows hardcoded** — in Phase 5 these come from frontmatter as recording-relative offsets, computed into composition-absolute times by the orchestrator
- **Avatar is a placeholder** until Phase 5 wires in real `heygen-video` clips via `assets/avatar.mp4`
- **`composition_file_too_large` lint warning** (655 lines) — could be split into sub-compositions if it becomes unwieldy. Low priority.

## What changes when Phase 5 ships

This guide will be partially superseded:

- "Required inputs / Content" becomes a *frontmatter spec* — the orchestrator reads from the script's frontmatter and substitutes into `index.html` automatically before rendering
- "Pre-render checklist" steps 1–6 become automated by `tools/render.py`
- "Brand-locked" stays a manual rule (the orchestrator never overwrites these)
- The "Render" command gets wrapped behind `python tools/render.py <vidname> --mode preview|final` which calls `npx hyperframes render` after substitution
