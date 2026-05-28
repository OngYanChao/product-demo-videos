# 2026-05-22 — Pre-Loading Recording Segments Play at 1x

**Status:** active
**Affects:** `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #21 added), `.claude/skills/parallax-video/SKILL.md` (scrub dispatch row notes the `--force-speed-range` flag for typing-intro videos), `screen recordings/V2/vid2_scrubbed.mp4` (first video re-scrubbed under this rule)

## Decision

The portion of a recording before tools begin firing — user typing the prompt, mouse moving toward submit, the brief moment of empty chrome after submit — must play at 1x in the scrubbed output. Never compressed, never sped up.

Encoded by invoking `tools/scrub.py` with `--force-speed-range "0:X:1.0"` where X is the timestamp at which tools first fire (the loading-segment boundary). X is identified from the raw recording: the first frame where the progress sidebar appears, the first "Starting up…" indicator, or the first parallel tool call. For V2 the boundary was 6.5s; the flag was `--force-speed-range "0:6.5:1.0"`.

## Why

Default `tools/scrub.py` behavior treats whole-frame near-static segments as "freezes" and uniform-speedups them at 2× (the project's `--anchor-speed` default). This catches the prompt-typing window because pixel diffs during typing sit below the `-45dB` freeze threshold — keystrokes don't move enough pixels per frame to register as content motion.

The cost is significant. At 2× the typing animation reads as comedic — characters flash in faster than any human types, and the viewer can't read the prompt before it's gone. The prompt is load-bearing content for use-case videos: it's the moment the persona's question gets named in the customer's chair, and the moment the value-framing for the whole video gets anchored. Losing it to a compression artifact is a real production defect.

User feedback during V2 production: *"the initial zoom on the chat box showing the prompt typing in, that's at 2x speed. it shld not be, it shld be at 1x speed. 2x only starts for the loading segment."*

Companion to Hard Rule #13 (never slow source). The asymmetry is deliberate: speedup beyond 1x is fine for true dead loading (tools running in background, user waiting), but the typing window is content, not loading, and gets locked at 1x.

## Notes

- **Boundary X identification.** Look at the raw recording for the first frame where the progress sidebar appears or the first tool call is logged in chat. That timestamp is X. For V2 the prompt was submitted at raw ~6.3s and the first tool fired by ~6.5s, so X=6.5 cleanly separates typing from loading.
- **Pairs with re-derive (Hard Rule #12).** Forcing 0–X at 1x lengthens the scrubbed recording by `X × (anchor_speed - 1) / anchor_speed` seconds (V2: 6.5 × 0.5 / 1 = ~3.25s). Every downstream `source_t` in `<recording>_zooms.json` for annotates AFTER the typing segment shifts by that amount. Re-extract frames, re-run zoom.py, re-derive LT/annotation timings.
- **Scope: pre-loading only.** Once tools begin firing, the loading section's 2× treatment is correct — viewer is reading tool activity in the sidebar, not parsing keystrokes. This rule does not change loading-section compression.
- **Alternative considered: `--cursor-aware`.** V1's scrub used `--cursor-aware` with cursor-pixel thresholds tuned for the typing window, achieving the same outcome via detection. Detection works but is harder to debug (which threshold matters?). `--force-speed-range` is more deterministic and easier to teach.
- **Future tooling.** `tools/scrub.py` could auto-detect the first cursor-active-but-pre-loading segment and lock it at 1x as a default. Not done — current rule is the explicit flag invocation, which keeps the decision visible in the scrub command.
- V2 application: scrubbed duration went from 50.43s (typing at 2x) to 53.68s (typing at 1x). All annotate `source_t` values in `vid2_zooms.json` shifted +3.25s. Final zoomed output: `vid2_zoomed.mp4` at 73.02s.
