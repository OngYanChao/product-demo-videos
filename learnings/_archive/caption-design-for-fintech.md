# Caption Design for Fintech

The viral CapCut/Submagic caption aesthetic (big bold UPPERCASE, yellow highlights, bouncy pop-ins) is not the right fit for B2B fintech product demos. Professional/regulated-industry guidance diverges from mainstream-content guidance in specific, fixable ways.

## Legibility baseline (WCAG 2.1 AA — required, not optional)

These are hard minimums for any cut that might reach institutional clients or get posted to a regulated context.

- **Contrast ratio:** ≥ 4.5:1 for normal text; ≥ 3:1 for large (18pt+) or bold (14pt+) text
- **Font:** sans-serif with uniform strokes. Ruled out: decorative, script, thin-stroke faces
- **Line length:** ≤ 32 characters per line
- **Lines on screen:** ≤ 2 per frame
- **Display duration:** 2–4 seconds per chunk — long enough to read, short enough to keep pace
- **Captions must convey all meaningful audio** — not just dialogue, also speaker identification and relevant sound cues

Most professional organizations target WCAG Level AA. It's what the DOJ requires for ADA Title II and what courts reference in ADA Title III cases.

## Where fintech diverges from viral-style captions

| Viral/CapCut style | Fintech adaptation | Why |
|---|---|---|
| UPPERCASE for emphasis words | Mixed case (sentence case) throughout | UPPERCASE reads as creator/TikTok content, not professional product demo |
| Yellow highlight on active word | Brand-color accent on 1–2 emphasized words per phrase | Pure yellow often fails 4.5:1 contrast against variable video backgrounds; brand color with outline passes and reinforces identity |
| Large bouncy pop-ins with scale animations | Soft fade-in per phrase, no bounce | Animation attracts attention *away* from the product demo. Restrained = trustworthy for fintech |
| Every word bold + oversized | Bold sans-serif at appropriate size (~4–5% of frame height) | Oversized text obscures the product UI |
| Emojis common | None, or extremely sparingly | "Using emojis excessively can make B2B content feel gimmicky" — OpusClip LinkedIn guidance |

The principle in one line: **accessibility before aesthetics**. Using brand fonts and colors that are illegible defeats the point.

## Typography

Sources converge on the same short list of acceptable fonts for professional video captions:

- **Inter Bold** (modern, digital-native, excellent at small sizes)
- **Montserrat SemiBold or Bold** (widely used in SaaS video)
- **Roboto Bold** (Google's workhorse, universally available)
- **Helvetica Neue Bold** (macOS native, professional default)
- **SF Pro Display Bold** (macOS native, Apple's system font)

Harvard University's Digital Accessibility guidelines recommend sans-serif for digital legibility — clean letterforms without decorative extensions, easier to read at smaller sizes and on lower-resolution displays.

## Brand color application (Chicago Global specifics)

Pulling from `colour-kit.md`:

| Role | Token | Hex | Use |
|---|---|---|---|
| Primary caption text | `color-text-inverse` | `#FFFFFF` | The default text color on video backgrounds |
| Outline | kit's primary text color | `#1F2937` (Near-Black) | Thick outline (4–6px) for contrast against variable backgrounds |
| Emphasis / key word highlight | `color-action-primary` | `#ED7D31` (CTA Orange) | The kit's designated attention accent. Complementary to navy, colorblind-safe, reinforces brand identity |
| Drop shadow | Near-black | `#000000` | Subtle shadow offset for depth |

The kit explicitly warns: white on CTA Orange is only 2.8:1 contrast. But captions use Orange *as text* on a variable video background with a 4–6px Near-Black outline — the outline is what passes the contrast check, not the orange itself. Always verify the composed layer passes 4.5:1 (large-text threshold) against a worst-case bright background frame.

## The spec that V1's test video was built against

- Font: Helvetica Neue Bold
- Size: ~68pt on a 1080p-normalized canvas (~56–72 translates well to 1080p; scales proportionally for 4K)
- Case: mixed case throughout
- Primary color: white (`#FFFFFF`) with 4–6px Near-Black outline and subtle drop shadow
- Emphasis color: CTA Orange (`#ED7D31`) on 1–2 key words per phrase
- Chunking: 3–4 words per phrase chunk, pop-in as spoken (120ms fade in, 60ms fade out)
- Position: lower-third, ~140px from bottom on 1080-normalized canvas
- Emphasis pick heuristic: numbers first, then longest non-stopword

## Platform reality (about "burn-in vs soft subs")

Soft subtitles (embedded track, toggle-able) are supported on desktop players (Preview, QuickTime, VLC, YouTube) but **fail on social feed autoplay** — LinkedIn, Twitter/X, Facebook, Instagram, TikTok all ignore embedded MP4 subtitle tracks during muted autoplay.

For a demo series that will be distributed on LinkedIn (explicitly in the master plan), captions must be **burnt in**. Soft subs are not a viable option for the primary deliverable.

## Format-specific caption guidance

- **LinkedIn:** algorithm rewards watch time, engagement, and accessibility signals. Captions are the fastest lever. Videos with well-formatted captions earn 40–60% higher average watch time.
- **Caption usage has risen 572% since 2021** — captions are now an expected baseline, not a differentiator
- **Test on mobile and with sound off** to catch formatting issues before shipping

## Applied to Parallax

The caption test rendered at [`outputs/V1_with_captions_test.mp4`](../outputs/V1_with_captions_test.mp4) implements this spec end-to-end. The helper script `gen_captions_test.py` in the project root converts edge-tts's VTT output to ASS with these styles baked in.

Pending: integrate into `pipeline.py` behind a `captions: on | off | style-name` frontmatter field so each video can opt in, and optionally define a LinkedIn-vertical variant with larger text/faster chunks.

## Sources

- [LinkedIn Video Caption Best Practices | OpusClip](https://www.opus.pro/blog/linkedin-video-caption-subtitle-best-practices)
- [Video Caption Design: Font, Color, Placement | OpusClip](https://www.opus.pro/blog/video-caption-design-placement)
- [Closed Caption Styling & Formatting | 3Play Media](https://www.3playmedia.com/blog/closed-caption-styling-formatting-best-practices-you-need-to-know/)
- [Best Practices for Branded Video Captions | Zight](https://zight.com/blog/best-practices-for-branded-video-captions/)
- [WCAG 2.0 Requirements for Video Captioning | 3Play Media](https://www.3playmedia.com/blog/wcag-2-0-requirements-for-video-captioning-and-audio-description/)
- [Video Accessibility & WCAG Compliance Guide | Swarmify](https://swarmify.com/blog/video-accessibility-captions-wcag/)
- [7 Best Fonts for Subtitles and Captions | Rev](https://www.rev.com/blog/7-best-fonts-for-subtitles-and-captions-in-videos)
- [Boost B2B Engagement with Closed Captioning | Goldcast](https://www.goldcast.io/blog-post/closed-captioning-on-video)
- [Captions/Subtitles | W3C WAI](https://www.w3.org/WAI/media/av/captions/)
