# 2026-05-18 — Recording Top-Anchored Crop in Product-Demo Template

**Status:** active
**Affects:** `templates/product-demo/index.html` (`#rec-video` CSS), `templates/product-demo/RENDER-GUIDE.md` (recording fit invariant)

## Decision

The `#rec-video` element in the product-demo template uses `object-fit: cover` + `object-position: top center`. When a source recording's aspect ratio is taller than 16:9 (e.g. 16:10 Mac native, 1.594:1 like V1.2's 3420×2146), the crop is anchored to the top of the recording — preserving the top bar (window title, navigation tabs, search) and cropping the bottom (message-input box, footer) instead of center-cropping both edges.

For 16:9 sources, this is a no-op (no crop needed).

When a follow-up prompt-send or message-input moment is part of the script (multi-tool workflow-chain videos, V7+), use a follow-zoom directive on the input region (per the V1.2 `z0_prompt_typing` pattern) to bring the chatbox into the visible frame for that beat. This is treated as a feature, not a workaround — prompt-typing beats are already zoom moments in our methodology because viewer attention should follow the action.

## Why

Center-cropping a 16:10 source into a 16:9 frame loses ~60px from both top and bottom. The top contains the window title, navigation, and search affordances — load-bearing context for "where we are in the product." The bottom contains the message input and footer, which are (a) already covered by the avatar PiP in the bottom-right corner, and (b) only relevant during specific prompt-typing moments that are zoom-anchored anyway.

The alternative considered was pillarbox (`object-fit: contain`) — preserves everything but adds permanent black bars on the left/right of *every* moment of *every* video, making the recording feel smaller and more screencast-tutorial-like. The trade-off — pillarbox in idle moments to handle a few prompt-send moments — wasn't worth it. Top-anchored crop + follow-zoom on prompt moments preserves the hero-demo aesthetic and uses the zoom system we already have.

## Notes

- For future templates beyond `product-demo`, decide per template based on the avatar position. The rule is *anchor the crop away from the avatar* — for templates where the avatar sits at top, anchor crop to bottom; for product-demo (avatar at bottom-right corner), anchor to top.
- If a future video's recording has critical bottom content that *can't* be brought up via follow-zoom (e.g. a long-running animation in the input area), that video can override `object-position` per-template or fall back to pillarbox for that one render. No such case exists yet.
- Sources that are already 16:9 native are unaffected — `object-position: top center` is a no-op when no crop is needed.
