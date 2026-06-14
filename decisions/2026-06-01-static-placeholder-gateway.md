# 2026-06-01 — Static-placeholder gateway: skip z0b + 3s loading flash when no ticks (Hard Rule #30)

**Scope:** Automated captures, both pipelines. The gateway probe runs early in Phase 3 dispatch (before z0b authoring + loading-window scrub strategy is committed).

**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #30 added), `.claude/skills/parallax-video/SKILL.md` (Phase 3 dispatch — gateway probe inserted before tick detection's main pass), `news-pipeline/tools/process.py` (auto-applies the static-path output when `tick_cut.py` returns 0 ticks).

## Decision

Cowork's Progress sidebar has two visually-distinct UI modes during a Claude response:

1. **Static placeholder** — a small graphic showing 3 dim circles connected by dashes, with the text "See task progress for longer tasks." underneath. Renders the same way for the entire response. Used for short / single-tool / cached responses. **Zero pixel motion** in the sidebar region across the response window.

2. **Dynamic checklist** — a numbered phase list ("1. Gathering...", "2. Phase 2: ...", "3. Phase 3: ..."), with each row's status circle transitioning from grey → blue → checkmark as the corresponding phase completes. Used for longer / tool-heavy responses (news briefs, multi-tool synthesis). **N pixel-diff peaks** in the sidebar region, one per phase tick.

Today's pipeline always zooms in on the Progress sidebar (z0b) and applies tick-window compression (news pipeline) or pre-cuts the brief-loading region (product-demo Variant B). Both behaviors assume the dynamic-checklist mode. When the recording is actually in the static-placeholder mode (V3 case — peer snapshot for a sector brief), z0b zooms in 2.5× on a frame that never changes, holds for ~17 seconds, then eases out. The viewer sees dead air during what should be a "Claude is working" beat.

**The rule:** before z0b is authored and the loading-window scrub treatment is chosen, run a tick-detection probe on the Progress sidebar over the loading window. Branch on the result:

- **`detect_ticks` returns 0 peaks → static-placeholder path.** Skip z0b entirely. Aggressively compress the loading window to a **3.0s flash** of the at-loading state via an ffmpeg pre-cut. Downstream zoom timing and beat sheet adjust accordingly.
- **`detect_ticks` returns ≥1 peak → dynamic-checklist path.** Proceed with the standard z0b + tick-cut (news) / Variant B pre-cut (product-demo) workflow as defined today.

## User observation (verbatim)

> "Can you look at V3, the progress task check bar there's no ticks can we add in a workflow where it will detect that there are no ticks in the progress task check bar and then we skip the zoom there. Just to extreme live, steep scrub of the loading segment to get to the output brief."

Follow-up clarification:
> "When i say that there are no ticks in the progress taskbar, that might be a bit confusing because if nothing is running in the top right corner of the screen at the progress taskbar, there are still actually tick symbols there. Can you compare v3 with N1 and see the difference between the top right zoom post prompt firing top right zoom in. You can see how for V3 there is actually nothing going on at the progress taskbar it is static and then for n1 you can see that there was a generated list of items to go through and there are blue ticks that take off"

The clarifier surfaced the actual mechanic — static placeholder vs dynamic checklist as two UI modes Cowork itself selects between (we don't control which). The visible "tick symbols" in the static mode are decorative; they don't pulse, change color, or accumulate. `detect_ticks` measures pixel-diff peaks in the region, which is exactly zero for the static mode (no animation) and N for the dynamic mode (one peak per row transition).

## Why this is a gateway, not a fallback

A fallback rule ("if z0b looks bad, fix it") would require visual review after rendering. The gateway runs at the start of Phase 3 — before scrub strategy, before zoom authoring, before any expensive rendering — so the rest of the pipeline branches cleanly. Static-path videos don't carry a vestigial z0b directive in their `zooms.json`; dynamic-path videos don't carry a 3s-flash artifact in their scrubbed file. Same architectural pattern as Hard Rule #23's Variant A / Variant B branch (chosen at Phase 3 step 6a based on `manifest.json` presence), with the static/dynamic split adding a third axis.

## The 3.0s flash duration

3.0s is the minimum that lets the viewer register "Claude is working" without the segment feeling instant. Calibrated against the rhythm of:
- ~0.5s for the eye to drop from prompt → sidebar
- ~1.5s to read "Working on it..." + register the static placeholder graphic
- ~1.0s of expectation before the brief appears

Less than 2s reads as a jump cut (typing-zoom → brief, no breathing room). 3s is the right floor for "the work happened but we're showing the snippy version." If the original loading dwell is already under 3s, no compression needed — keep as-is.

## Implementation — ffmpeg pre-cut on the loading window

Inputs needed: `T_typing_end` (raw), `T_brief_landed` (raw), `loading_dwell = T_brief_landed − T_typing_end`.

If `loading_dwell ≤ 3.0s`: skip the pre-cut entirely (already shorter than the floor).

Otherwise, perform an ffmpeg pre-cut on `raw.mp4` / `trimmed.mp4` (the input to scrub):

```
ffmpeg pattern:
  pre   = source[0, T_typing_end + 0.2]               # everything through submit + brief settle
  flash = source[T_typing_end + 0.2, T_typing_end + 0.25]  # 50ms slice mid-loading
        + tpad=stop_mode=clone:stop_duration=2.95     # padded to 3.0s total
  post  = source[T_brief_landed, end]                 # natural continuation from brief-landed
  concat( pre, flash, post ) → modified_source
```

The 50ms slice + tpad clone matches Rule #27 (c) and Rule #29's ffmpeg template — same canonical mechanism, applied to a different artifact (loading dwell instead of at-top hold).

`T_brief_landed` shifts in the modified source: new `T_brief_landed_static = T_typing_end + 0.2 + 3.0 = T_typing_end + 3.2`. All downstream timing (z0's `T_click + ease` is unaffected since z0 ends before the cut; annotates at `source_t` shift by `−(loading_dwell − 3.0)`).

z0b is omitted from `zooms.json` entirely — not just zeroed out. `tools/zoom.py` skips the missing directive cleanly.

## Why both pipelines

**News-pipeline**: news briefs almost always run the dynamic checklist (multi-phase synthesis), so this rule fires rarely. But occasionally a cached news response or a one-shot fact lookup runs in static mode — without this gateway, the rendered video would have a wasted z0b zoom on a static graphic.

**Product-demo**: many V1-V16 videos fire in static mode (peer snapshot, single stock pull, simple capability demos). V3 is the canary. The gateway makes static-mode product-demos render cleanly without the author having to manually omit z0b from `zooms.json`.

## Implementation — auto-applied in Phase 3 dispatch

**News-pipeline (`news-pipeline/tools/process.py`):**
- `tick_cut.py` already runs `detect_ticks` internally. Extend it to gracefully handle 0-tick output: emit no z0b in `auto_zooms.json`, perform the 3s-flash pre-cut on `trimmed.mp4` before scrub, record the static-mode decision in the result dict.
- `process.py` then proceeds as normal — scrub runs on the modified trimmed file (loading window already compressed), zoom.py runs with z0-only zooms.json, downstream cap_dead doesn't need a wider `protect_until_t` because there's no Rule #27 hold to protect.

**Product-demo (`parallax-video/SKILL.md` Phase 3 dispatch):**
- Step 5 already runs `detect_ticks` to find tick positions. Modify the first pass to use a low magnitude threshold and no `--expected-ticks` constraint — count peaks without committing.
- If count == 0: branch into the static path. Pre-cut the loading window, set `T_brief_landed_effective = T_typing_end + 3.2`, instruct Phase 5 to omit z0b from `zooms.json`.
- If count ≥ 1: proceed with the existing dispatch (Variant A or B per Hard Rule #23).

## Interaction with Hard Rules #27 and #29

Both #27 (2s top-hold) and #29 (zoom-out over still + raw-tail stitch) reference z0b — they describe how z0b's ease-out should be edited. **When z0b is skipped (static-placeholder path), Rules #27 and #29 don't apply**: there's no z0b to edit, no at-top moment within z0b's timing window. The static-path video still ends with the natural raw scroll-down via Variant B's existing logic (or simply by letting the post-brief content play through).

## Cross-references

- Hard Rule #23 (Variant A / Variant B branching that this rule sits parallel to): `decisions/2026-05-29-automated-post-tick-cut.md`
- Hard Rule #27 (top-hold rule that doesn't fire on static path): `decisions/2026-05-30-minimum-top-hold.md`
- Hard Rule #29 (zoom-out-over-still rule that doesn't fire on static path): `decisions/2026-05-31-zoom-out-over-still-and-raw-tail-stitch.md`
- V3 capture context (the canary that surfaced this): `screen recordings/V3/manifest.json` (peer snapshot, static placeholder mode)
- N1 capture context (comparison case — dynamic checklist): `news-pipeline/recordings/N1/manifest.json`
