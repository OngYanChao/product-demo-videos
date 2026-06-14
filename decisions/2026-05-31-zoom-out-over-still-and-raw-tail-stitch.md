# 2026-05-31 — z0b ease-out plays over a frozen at-top frame + post-freeze raw-tail stitch (Hard Rule #29)

> **2026-06-04 amendment:** the Rule #27 2.0s hold is now split — 1.0s from Rule #29's tpad freeze (`freeze_duration = z0b.ease + 1.0s`, was `+ 2.0s`) + 1.0s from the normalized raw natural hold (raw_tail stitched from `smooth_scroll_chat_start − 1.0s`, was from `T_at_top + 0.05s` which double-counted capture.py's `POST_SCROLL_TOP_HOLD_S = 2.0s`). `cap_dead`'s `protect_until_t` extension drops from `+2.0s` to `+1.0s` to match. See changes in `news-pipeline/tools/process.py::_rule_29_rebuild()`.

**Scope:** Automated captures with z0b — both pipelines (news-pipeline always; product-demo when captured via `automation/capture.py` per Hard Rule #23 Variant B). Manual recordings (no auto-scroll-up motion in source, no `manifest.json`) are exempt.

**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #29 added), `.claude/skills/parallax-video/SKILL.md` (Phase 3 dispatch: new step that auto-applies the freeze + raw-tail rebuild between scrub/tick-cut and zoom.py), `news-pipeline/tools/process.py` (auto-applies the rebuild between `tick_cut.py` and `zoom.py`).

## Decision

Two load-bearing requirements, applied as a single rebuild step between the source-conformance stage and `zoom.py`:

**(a) z0b's ease-out must play over a FROZEN at-top source frame.** When the camera retracts from the Progress-sidebar zoom back to full frame, the source content visible during the retract must be a still image of the brief at the top of the chat (prompt + brief-title together — same content as Rule #27 (b)). If the source still contains live motion during this window (auto scroll-up residue, Cowork UI snap, or the first frames of the smooth scroll-down), the zoom-out reveals a moving scene — viewer perceives "the chat is scrolling while the camera zooms back," which reads as jarring/unreadable. Replacing the source content at the z0b ease-out window with a freeze of the at-top frame makes the zoom-out reveal a STATIC reading scene.

**(b) After the freeze, the source must stitch the natural raw continuation from `raw[T_at_top + 50ms onwards]`.** This extends Rule #27 (c)'s "no jump cuts" principle to the auto-zoom workflow. Concretely: after z0b ends + the 2s Rule #27 hold, the source continues with the original raw footage from immediately after the freeze slice — letting the natural snap animation + smooth scroll-down + outro play out in their original recorded sequence. No skipped source segments, no synthetic discontinuities.

## User observation (verbatim)

**First (after Rule #27-only fix to N1):**
> "After the freeze frame, after the zoom out on the progress taskbar, there is this hard cut where we cut into the scroll down already happening. Can we have a smooth transition? just just freeze frame and then from the first frame after the scroll the scroll up happens in the original footage just stitch that there and then from there we will have the full clip of the smooth scroll down"

The Rule #27 fix to N1 satisfied the 2s top-hold + prompt-visible requirements, but two visual issues remained: (i) during z0b's ease-out, the source still showed mid-scroll-down motion (the post-tick-cut content) → zoom-out felt unreadable; (ii) after the freeze ended, the source resumed at the OLD post-tick content (mid-scroll-down) rather than at the natural moment immediately after the at-top frame → jump cut.

Fix that satisfied the user: rebuild the `trimmed_scrubbed_tickcut.mp4` intermediate to (i) replace the source content at the z0b ease-out window with a 1.5s freeze of raw[353.85], (ii) extend the freeze by 2.0s for the Rule #27 hold (total 3.5s frozen), (iii) append `raw[353.85, end]` for natural continuation, then re-run `zoom.py`. Visual result: prompt-typing zoom → ticks → zoom-out over still at-top scene → 2s held still → seamless transition into natural snap + smooth scroll-down + outro.

## Why a rule (not just an N1 fix)

The Rule #27 codification was scoped to a SINGLE-MECHANISM Phase 3 freeze-frame inject — appropriate for V3-style manual recordings or for retroactively-fixing the top-hold duration. It does not cover the visual relationship between z0b's camera retraction and the source content during that retraction, nor the post-freeze stitch behavior in the auto-zoom workflow (news + product-demo Variant B).

Both behaviors are deterministic functions of the recording structure: any automated capture with z0b will exhibit the same "scroll motion during ease-out" + "post-freeze jump cut" issues unless explicitly handled. Codifying as Hard Rule #29 ensures Phase 3 dispatch auto-applies the rebuild for every future automated capture.

## Why one rule, two halves

Splitting (a) and (b) into separate rules was considered but rejected: the rebuild step that satisfies (a) is the SAME step that satisfies (b) — both fall out of "modify the intermediate's source content at and beyond the z0b ease-out window." Implementation atomicity (one rebuild operation, one chance to drift) keeps them as a single rule with two requirements. Mirrors Rule #27's three-requirements-one-rule pattern.

## Implementation — auto-applied in Phase 3 dispatch

Phase 3 detects:
- `manifest.json` present (automated capture, per Hard Rule #14)
- `phases.scroll_to_top_done` present (scroll dance fired, Hard Rule #23 Variant B)
- An intermediate exists with z0b in its auto/scoped zooms.json (`trimmed_scrubbed_tickcut.mp4` for news; `vid<N>_pre_zoom.mp4` for product-demo automated)

When all three are true, Phase 3 dispatch runs the rebuild step BEFORE `zoom.py`:

```
T_z0b_ease_out_start_src  = z0b.source_t + z0b.duration − z0b.ease       # in scrubbed/source time
T_at_top_prompt_visible   = scroll_to_top_done − 0.5s                      # per Rule #27 (b) — cowork UI snap caveat
freeze_duration           = z0b.ease + 2.0s                                # ease-out window + Rule #27 hold

ffmpeg pattern:
  tc_pre   = intermediate[0, T_z0b_ease_out_start_src]
  slice    = raw[T_at_top_prompt_visible, T_at_top_prompt_visible + 50ms]
  freeze   = slice + tpad=stop_mode=clone:stop_duration=(freeze_duration − 50ms)
  raw_tail = raw[T_at_top_prompt_visible + 50ms, end_of_raw]
  concat( tc_pre, freeze, raw_tail ) → intermediate (overwrites)

Then run zoom.py on the rebuilt intermediate.
```

The 50ms slice + tpad pattern matches Rule #27 (c)'s ffmpeg template — same `tpad=stop_mode=clone` mechanism, just applied to a wider source-content window and combined with the raw-tail stitch.

## Why both halves are necessary together

**(a) without (b)** — freezing source during ease-out but cutting back to OLD post-tick content after creates the original N1 issue: ease-out reads cleanly, then jump-cut to mid-scroll-down. Visual incoherence.

**(b) without (a)** — stitching raw-tail correctly but leaving live motion in source during ease-out means viewer perceives "zoom-out over scrolling chat" right before the freeze starts. Less jarring than the jump cut, but still violates the "still reading scene" expectation set by the freeze itself.

**(a) and (b) together** — viewer perceives: sidebar zoom held → smooth zoom-out reveals at-top scene → 2s held still to register prompt + brief → natural snap into smooth scroll-down. Continuous, no synthetic transitions.

## No-op conditions

The rebuild step skips if:
1. **No manifest** (manual recording — no `automation/capture.py` artifacts to identify the at-top moment).
2. **`phases.scroll_to_top_done` absent** (scroll dance didn't fire — typically `--no-readthrough` captures, where there's no auto scroll-up motion to obscure and no at-top moment to stitch from).
3. **No z0b in the zooms JSON** (no ease-out window to freeze; rule has nothing to enforce).
4. **`raw.mp4` missing** (per Hard Rule #14, source must be preserved — if it's gone, the rebuild can't access the natural-continuation footage).

## Scope edge cases

- **Pre-2026-05-31 automated captures already rendered:** rule applies retroactively if the recording is re-rendered. N1 (current N1 in `news-pipeline/recordings/N1/`) was the canary that surfaced this — already conformed.
- **`tools/cap_dead_times` interaction:** the rebuild includes the full natural raw_tail (no compression). Subsequent `cap_dead` (Rule #26) would cap freezes >1s in that tail to 1s, including the 2s Rule #27 hold. Two options: (i) skip `cap_dead` for the protected window via `protect_until_t = z0b_end + 2.0s`; (ii) cap_dead recognizes the Rule #27 hold as a protected freeze. Implementation chooses (i) — `protect_until_t` extended to include the Rule #27 hold.
- **Product-demo Variant A (manual recordings):** rule's no-op condition (1) catches this — no `manifest.json` means the rebuild skips. Manual recordings rely on the human controlling pacing at recording time.

## Cross-references

- Hard Rule #23 Variant B (the cut whose downstream visual artifact this rule corrects): `decisions/2026-05-29-automated-post-tick-cut.md`
- Hard Rule #27 (sibling rule — sets up the at-top freeze the rebuild leverages; rule #29 extends #27 (c) to the auto-zoom workflow): `decisions/2026-05-30-minimum-top-hold.md`
- Hard Rule #26 (cap_dead interaction — Phase 3 widens `protect_until_t` to include Rule #27 hold): `decisions/2026-05-29-post-streaming-deadtime-cap-global.md`
- N1 capture context (canary): `news-pipeline/recordings/N1/manifest.json` (2026-05-29 capture; conformed under Rule #29 on 2026-05-30 → 2026-05-31).
