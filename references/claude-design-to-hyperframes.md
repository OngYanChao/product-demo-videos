# Claude Design → Hyperframes templates

How to get a valid Hyperframes composition out of Claude Design, what breaks on first export, and how to fix it. Drafted 2026-05-04 from the V1 product-demo template integration.

## Scope and shelf life

**This is a finite-use checklist, not an evergreen reference.** Templates are authored *once* and reused across every video in their family — the project plan calls for two template families total (product-demo, weather/intel-brief), so this doc has roughly **two direct uses** before it becomes archival reference.

| Audience | Lifespan |
|---|---|
| Authoring the weather/intel-brief template (next) | active use |
| Refreshing a template's design (rare — templates last many videos) | active reference |
| Adding a third template family later (e.g., quarterly review format) | active reference |
| Daily video production (`scrub` → `write` → `render preview` → `render final`) | **does not apply** — that loop never runs Claude Design |
| Debugging a regression after a Hyperframes major-version bump | active reference |
| Onboarding someone new to how templates were built | active reference |

Distinguish this from the craft-rules learnings (`writing-for-the-ear.md`, `voiceover-interprets-visuals.md`, `production-principles.md`) — those apply to *every* script and every video forever. This one only fires when we author a template, which is a rare event by design.

## Claude Design has two output modes

**Default mode** — produces a self-contained React + Babel app driven by a custom "Stage" timeline engine. Renders fine in any browser with a built-in scrubber. Not compatible with `npx hyperframes render` because the timing model (JSX components calling `useTime()`) doesn't map to Hyperframes' data-attribute system.

**Hyperframes mode** — produces a single `index.html` using `@hyperframes/core` runtime + GSAP + elements with `data-start` / `data-duration` attributes. Compatible with `npx hyperframes lint / preview / render`.

## Forcing Hyperframes mode

Attach the **Hyperframes instruction file** from `hyperframes.heygen.com/guides/claude-design` to the Claude Design chat alongside your concept brief and any reference materials (e.g., `references/colour-kit.md`). Without that file, Claude Design defaults to Stage.

If you already have a Stage version of the design and want to preserve specific visual decisions: attach the existing Stage template files + the instruction file + tell Claude Design to *"rebuild this as a valid Hyperframes composition."* Faster than re-iterating from scratch and the design choices transfer.

## What to expect on first export — common lint errors

Run `npx hyperframes lint .` immediately after dropping the new template into the project. Frequent errors and their fixes:

| Lint error | Root cause | Fix |
|---|---|---|
| `imperative_media_control` | Inline JS calls `play()` / `pause()` / `currentTime =` on a `<video>` tag | Remove the imperative ticker code entirely. Hyperframes owns playback when the video has `data-start` / `data-duration`. |
| `media_missing_data_start` | `<video>` element with `src` but no timing attributes | Add `data-start="X"` and `data-duration="Y"` in composition seconds. Use `data-media-start` to offset into the source if needed. |
| `gsap_exit_missing_hard_kill` | `tl.to(elem, { autoAlpha: 0, ... })` with no matching `tl.set` after the fade | Add `tl.set("#elem", { autoAlpha: 0 }, fadeEndTime)` immediately after the exit tween. Required because non-linear seeks (renderer scrubbing to arbitrary times) won't replay the fade and will leave stale visibility. |
| `timed_element_missing_clip_class` | Element with `data-start` / `data-duration` but no `class="clip"` | Add `class="clip"`. The runtime uses that class to control visibility based on the timing attributes. |

All four were present on V1's first Hyperframes export. Each fix is mechanical and takes <1 min.

## Common warnings worth addressing

| Warning | Why it matters | Fix |
|---|---|---|
| `composition_file_too_large` | Soft suggestion to split scenes into sub-compositions | Ignore unless the file is genuinely unmanageable. The runtime doesn't care. |
| `gsap_exit_missing_hard_kill` (warning version) | Same as the error — can become real visibility bugs on non-linear seeks | Always add the `tl.set` |
| Sparse keyframes on source video (compiler warning) | Renderer must seek the video per frame; sparse keyframes mean slow decode + freezing | Re-encode source: see below |

## Source video preparation

Hyperframes' renderer seeks `<video>` elements frame-by-frame. If the source MP4 has sparse keyframes (e.g., one every 4–5 seconds), seeks land on non-keyframes and the decoder must walk forward — slow, sometimes visibly freezing. Re-encode any recording before using it in a template:

```bash
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -r 60 -g 60 -keyint_min 60 \
  -movflags +faststart \
  -an output.mp4
```

`-r 60 -g 60 -keyint_min 60` = 1-second keyframe interval at 60fps. Match `-r` to your target render fps. `-an` drops audio (recordings are silent in our pipeline anyway). `-movflags +faststart` puts the moov atom at the start so the player doesn't have to download the whole file before seeking.

For our scrubbed recordings (`screen recordings/**/*_scrubbed.mp4`), this re-encode step should ideally happen at the end of `tools/scrub.py` so the keyframe density is baked in from the start. Future improvement.

## Font handling

Hyperframes has a deterministic-font catalog — fonts that get embedded into the rendered output for cross-machine reproducibility. Inter, Outfit, Playfair Display, IBM Plex Mono, etc. The compiler resolves font-family declarations against this catalog at render time.

**CSS variables don't resolve.** The compiler can't trace through `var(--whatever)` to find the actual font name. Symptom: render warning "No deterministic font mapping for: var(--font-display)" + the rendered MP4 falls back to a system font.

Fix — use literal font names in font-family rules:

```css
/* breaks: compiler can't resolve through the var */
body { font-family: var(--font-display); }

/* works: literal name maps cleanly to Inter in the catalog */
body { font-family: "Inter", system-ui, sans-serif; }
```

Keeping CSS vars for *colors* and *spacing* is fine — the compiler issue is specific to font-family.

## What this saves us

These are not subtle bugs — they all show up in the lint output with clear messages. But re-debugging them from scratch on each rare template-authoring session wastes 30+ min each time. Knowing the patterns in advance:

- Skip the back-and-forth with Claude Design when its embedded preview iframe can't load the recording (it's a sandbox issue, not a composition issue — the local render is fine)
- Fix the four lint errors in one pass rather than discovering them sequentially
- Re-encode source video before composing rather than after seeing freezing in the rendered output
- Use literal font names from the start

## Related

- `learnings/INTEGRATION_LOG.md` — should get a row for this once integrated into the orchestrator skill (Phase 5) or a `template-checklist` skill
- `overhaul.md` Phase 4 / Phase 5 — should reference this doc for "what to do after Claude Design hands back a ZIP"
