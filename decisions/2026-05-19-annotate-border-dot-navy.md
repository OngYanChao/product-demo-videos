# 2026-05-19 — Annotate Highlight Border + Callout Dot Switched to CG Navy-400

**Status:** superseded by [2026-05-19-annotate-spotlight-default.md](2026-05-19-annotate-spotlight-default.md) — the rectangle border + numbered dot were retired in favor of a soft-edged elliptical spotlight; the colour decisions in this ADR are moot now since the elements themselves are gone (constants preserved in code under `if False:` blocks for future toggle).
**Affects:** `tools/zoom.py` (`ANNOTATE_HIGHLIGHT_BORDER_COLOR`, `ANNOTATE_CALLOUT_DOT_COLOR`), `templates/product-demo/RENDER-GUIDE.md` (annotate-mode invariant)

## Decision

The annotate-mode highlight border and the numbered callout dot in `tools/zoom.py` are both rendered in **CG navy-400 (`#547498`)**. Switched from the initial CG orange (`#ED7D31`) used for both elements.

Rationale chain:
1. The annotation panel on the right is **navy-900 (`#0C2746`)** background.
2. A blue border + dot pairs the recording-side emphasis with the panel-side emphasis as a single visual unit, rather than splitting attention between orange (recording) and navy (panel).
3. Navy-900 (panel-matching) was tried first but blended too far into the recording's dark UI to register as a border.
4. Navy-400 is the kit's explicit "borders, subtle highlights" token (per `references/colour-kit.md` Layer 2). Mid-tone — visible against the dark UI but still in the brand-blue family.

The CG orange remains in use elsewhere: title-card eyebrow accent, lower-third stripe (`.lt-stripe`), panel progress-bar header (`.ap-progress`), and the outro rule. None of those moved to navy.

## Why

The orange highlight border + orange dot competed visually with the orange in the title card / LT / outro accents. With three different "callout zones" (left-side highlight, right-side panel, bottom-of-frame LT) and only one accent color, every video moment looked like "another orange thing." Pulling the recording-side emphasis into the navy family unifies the annotate composition — the highlighted text + the numbered dot + the panel all read as one navy-tinted callout, and the orange is reserved for the title card / LT / outro accents that span the *whole* composition.

The single-tone navy is also closer to the user's reference screenshot (panel + highlight border + callout dot all in the brand blue family).

## Notes

- The numbered dot's text remains white (`#FFFFFF`) — readable against navy-400.
- The dim mask alpha (`ANNOTATE_DIM_ALPHA = 153`) is unchanged.
- The highlight padding (`ANNOTATE_HIGHLIGHT_PAD_PX = 12`) is unchanged — pad gives the border breathing room around the text.
- This decision is template-invariant for the product-demo family: every annotate moment across V1–V16 uses navy-400 unless explicitly overridden per video (no current override). Logged at `templates/product-demo/RENDER-GUIDE.md` → "Annotate mode — color invariants."
- For a hypothetical future template targeting a non-Chicago-Global client, the constants in `tools/zoom.py` would be swapped to match that client's kit. The constants exist precisely so this is a config change, not a code change.
