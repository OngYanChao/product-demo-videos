# 2026-05-22 — Zoom Skeleton Standardization (Hard Rules #22 + #23 + #24)

**Status:** active
**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rules #22, #23, #24 added), `.claude/skills/parallax-video/SKILL.md` (Phase 5 + 5.5 dispatch rows updated to enforce skeleton), `screen recordings/V2/vid2_zooms.json` (first video re-authored under the standard skeleton)

## Decision

Three rules locked in, governing the zoom skeleton every product_demo must follow:

1. **Hard Rule #22 — z0 ease-out aligns with the loading-segment boundary.** The z0 prompt-typing follow-zoom's `duration` field equals the scrubbed timestamp T at which the Progress sidebar first appears. That same T is the `--force-speed-range "0:T:1.0"` cutoff in Hard Rule #21. One number flows into both the scrub flag and the zoom directive.
2. **Hard Rule #23 — Standard zoom skeleton: z0 + z0b + z1..zN.** Every product_demo zoom plan includes a prompt-typing follow (z0), a Progress-sidebar follow with mandatory tail-cut (z0b + `detect_ticks.py` + ffmpeg trim), and per-content-item annotates (z1..zN per Hard Rule #24). z0b is the default, not an opt-in. Tail-cut is part of the standard skeleton, not a per-video optimization.
3. **Hard Rule #24 — Annotate highlight regions are measured + tight.** Extension of Hard Rule #10 (originally underline-only) to cover `mode: "annotate"` highlights. `highlight_region_pct` height ≤15% unless the VO genuinely covers a wider span; every annotate's region is snapped via `tools/measure_highlight.py`; multi-VO-target dwell beats split into multiple sub-annotates rather than authoring one big spotlight on the whole section.

## Why

User feedback during V2 production after reviewing `screen recordings/V2/vid2_zoomed.mp4`:

> "the zoom out that happens for the prompt occurs way too early, if you compare the timing between v1 and v2, v1 only zooms out once the cursor clicks on the send button and fires off the prompt, here the zoom out is premature. next, there is no zoom for the top right progress bar like in v1. last, the spotlights are all not highlighting the specific section of text like we outlined and enforced in v1. can we make sure these changes are replicable and enforced for future videos?"

Each of the three issues exposed a pattern that V1 had right but V2 violated, with no Hard Rule blocking the violation. V1 was operating on craft intuition; V2 was authored without that intuition; the resulting drift is exactly what Hard Rules exist to prevent.

**Issue 1 — premature z0 ease-out.** V1 set `z0.duration: 7.2` because V1's first detected loading freeze started at raw t=7.22s — V1 anchored to the *loading boundary*. V2 set `z0.duration: 6.5` to match the `--force-speed-range "0:6.5:1.0"` cutoff, which was the *typing-end boundary*, not the loading-fire boundary. The click+sidebar moment was at scrubbed t≈7.0; the zoom-out at 6.5 completed ~0.5s before that, reading as premature. Without a Hard Rule, the two boundaries (typing-end vs loading-fire) were conflated.

**Issue 2 — missing z0b.** V1 had an elaborate z0b directive (`region [80, 0, 20, 30]`, zoom 2.5×) plus a tail-cut pipeline using `detect_ticks.py` + ffmpeg trim+concat to compress 28s of dead loading to 12s. V2 had none — the loading segment played as 15.5s of full-frame static-feeling content with no camera direction. The z0b pattern was visible in V1's frontmatter notes but never codified as a rule, so V2's zoom JSON omitted it without any flag firing.

**Issue 3 — loose spotlights.** V1's highlight regions are tight: `[27, 58.88, 44, 6.19]` (Value row only, height 6.19%), `[54.5, 43.83, 16.5, 6.52]` (single trajectory cell, height 6.52%), `[27, 30, 42, 22]` (Bottom Line opening 2-3 lines, height 22%). V2's highlights were section-sized: `[28, 30, 43, 44]` (whole score table, height 44%), `[28, 22, 43, 38]` (whole trajectory section, height 38%), `[28, 53, 43, 25]` (whole Bottom Line, height 25%). V2 violated the implicit V1 contract that the spotlight illuminates *what the VO names*, not the section the content lives in. Hard Rule #10 forbade hand-tuned underlines but said nothing about annotate highlights — gap exploited.

The combined effect: V2's zoomed output looked visibly less polished than V1's even though both went through the "same" pipeline, because the polishing-equivalent decisions were uncodified in V1 and absent in V2.

## How to apply (enforcement)

1. **z0 duration = loading-segment boundary T.** During Phase 3 scrub audit (Hard Rule #21 step):
   - Sample raw recording frames around the expected boundary (where tools first fire visibly).
   - Pick the first frame showing the Progress sidebar at all — faint/initiating/partial all count.
   - Use that timestamp as T.
   - Apply T in three places: `tools/scrub.py --force-speed-range "0:T:1.0"`, the z0 zoom directive's `duration: T`, and the script's `target_runtime_seconds` recording-portion calculation.
   - Validation check: in the zoomed file, the z0 ease-out should COMPLETE at the exact frame where the Progress sidebar first becomes visible. If ease-out completes earlier, T was set too low. If ease-out lingers past sidebar-visible, T was set too high.

2. **z0b always runs, tail-cut always runs.** During Phase 5 (`write V<N>`) when drafting the zoom JSON:
   - Author a `z0b_progress_sidebar` directive after z0 in the JSON. Standard region for Cowork chrome: `[80, 0, 20, 30]`, mode `follow`, zoom 2.5×, ease 1.5s.
   - `source_t` for z0b = z0.duration + ~3s buffer (lets the sidebar populate before the camera moves to it).
   - `duration` for z0b = scrubbed timestamp where the last checkmark fires (or where the brief begins rendering on-screen) minus z0b.source_t.
   - During Phase 5.5: before running `tools/zoom.py`, run `tools/detect_ticks.py` on the sidebar region to find checkmark moments. Build the ffmpeg trim+concat command from `ffmpeg_trim_ranges` in the output JSON. Apply the trim+concat as a post-process step after `tools/zoom.py` (V1's pattern).
   - Skip z0b only with explicit user sign-off + the rare case of "no tool activity sidebar visible." Default = z0b runs.

3. **Annotate highlights are measured + tight + split.** During Phase 5 (`write V<N>`) when drafting annotate directives:
   - For every `mode: "annotate"` directive, run `python tools/measure_highlight.py "<recording>" <source_t> --rough "x,y,w,h" --debug-overlay /tmp/<vN>_hl<N>.png` before pasting `highlight_region_pct`.
   - Hand-tuned values forbidden.
   - For a dwell:y beat whose VO names multiple discrete content items, split into multiple sub-annotates — one per item — with distinct `callout_number`s. Don't author one big spotlight on the section containing all items.
   - Reject any rough rect with `height_pct > 15` unless the VO genuinely names content spanning that vertical range.

4. **Phase 5 dispatch updated.** The `parallax-video/SKILL.md` "write V<N>" dispatch row requires the standard skeleton in every drafted zoom JSON. The "zoom V<N>" dispatch row requires running `detect_ticks.py` + the trim+concat post-process by default.

## Notes

- **Why V1 didn't need the rules.** V1 was authored interactively by the user who held the visual intuition; the rules existed in their head, not on paper. V2 was authored by Claude operating on the available skill text. Codifying the rules makes V2-and-later reach V1's visual quality without per-video back-and-forth.
- **Standard region values.** `[40, 24, 38, 11]` (z0 prompt input) and `[80, 0, 20, 30]` (z0b sidebar) are Cowork-chrome-specific. If a future template ships a different chat UI layout, these regions move with it — the rule is "follow the prompt box / follow the sidebar," and the regions are the layout-specific encoding of that rule.
- **Tail-cut tunable: `--tail-seconds`.** `detect_ticks.py` keeps ±N seconds around each tick. V1 used N=1.0 (2s clip per tick). The right value depends on tick rhythm — too narrow and the tick has no breathing room; too wide and dead time creeps back in. Project default: 1.0s. Tunable per video if the rhythm calls for it; document the override in the zoom JSON's `_beat` note.
- **Companion to Hard Rule #21.** Hard Rule #21 locks the *scrub flag*; Hard Rule #22 locks the *zoom duration*; both feed off the same boundary T. Identifying T once at Phase 3 carries through to Phase 5.5.
- **Companion to Hard Rule #10.** Hard Rule #10 governs underline regions ("measured, not eyeballed"). Hard Rule #24 extends the same discipline to annotate highlights. Same `tools/measure_*` pattern, same forbidden-to-hand-tune principle.
