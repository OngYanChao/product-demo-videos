# Chicago Global — Colour System
### Brand Colour Kit for Emails, Presentations, Reports & Future Surfaces

---

## How this kit is structured

This kit is the **single source of truth** for all Chicago Global brand colours. It provides the complete set of design tokens needed for emails, slide decks, reports, dashboards, and any future surface. Core brand colours are sourced from the CG Polaris slide deck theme; supporting colours are derived from those anchors following industry best practices (WCAG 2.1 AA, 60-30-10 composition, colourblind safety).

The kit uses a **three-tier token architecture** (primitive → semantic → component) so that colours can be referenced by intent rather than raw value. This enables future theming, dark mode, and cross-platform consistency without touching individual designs.

The kit follows the **60-30-10 rule**: ~60% neutrals/backgrounds, ~30% brand blues, ~10% accents and semantic colours.

---

## Token Architecture

This kit organises colours into three layers. Today, most usage will reference **Layer 2 (semantic tokens)** directly. The architecture is designed so that Layer 1 primitives can be remapped (e.g. for dark mode) without changing any Layer 2 or 3 references.

### Layer 1 — Primitive Tokens

Raw colour values with numeric scale names. These are reference-only — never use a primitive token directly in a design. They exist so that semantic tokens can point to them, and remapping a primitive automatically updates every semantic token that references it.

| Token | Hex | RGB | CMYK | Status |
|-------|-----|-----|------|--------|
| **Navy** | | | | |
| `navy-950` | `#0C1D30` | 12, 29, 48 | 75/40/0/81 | *new — expansion* |
| `navy-900` | `#0C2746` | 12, 39, 70 | 83/44/0/73 | original |
| `navy-800` | `#17375D` | 23, 55, 93 | 75/41/0/64 | *new — expansion* |
| `navy-700` | `#154175` | 21, 65, 117 | 82/44/0/54 | original |
| `navy-600` | `#285FA0` | 40, 95, 160 | 75/41/0/37 | *new — expansion* |
| `navy-500` | `#407ABC` | 64, 122, 188 | 66/35/0/26 | *new — expansion* |
| `navy-400` | `#547498` | 84, 116, 152 | 45/24/0/40 | original |
| `navy-300` | `#A2B8D3` | 162, 184, 211 | 23/13/0/17 | *new — expansion* |
| `navy-200` | `#92A6C1` | 146, 166, 193 | 24/14/0/24 | original |
| `navy-100` | `#E4E9EE` | 228, 233, 238 | 4/2/0/7 | *new — expansion* |
| `navy-50` | `#F1F3F6` | 241, 243, 246 | 2/1/0/4 | *new — expansion* |
| **Neutral** | | | | |
| `neutral-900` | `#1F2937` | 31, 41, 55 | 44/25/0/78 | original |
| `neutral-700` | `#4B5563` | 75, 85, 99 | 24/14/0/61 | original |
| `neutral-500` | `#6B7280` | 107, 114, 128 | 16/11/0/50 | original |
| `neutral-300` | `#9EA0A9` | 158, 160, 169 | 7/5/0/34 | original |
| `neutral-200` | `#E7E8E9` | 231, 232, 233 | 1/0/0/9 | original |
| `neutral-150` | `#CCCDCF` | 204, 205, 207 | 1/1/0/19 | original |
| `neutral-100` | `#EAEDF3` | 234, 237, 243 | 4/2/0/5 | original |
| `neutral-50` | `#F5F6F8` | 245, 246, 248 | 1/1/0/3 | original |
| `white` | `#FFFFFF` | 255, 255, 255 | 0/0/0/0 | original |
| **Green** | | | | |
| `green-950` | `#072011` | 7, 32, 17 | 78/0/47/87 | *new — expansion* |
| `green-900` | `#116631` | 17, 102, 49 | 83/0/52/60 | original |
| `green-800` | `#0E4020` | 14, 64, 32 | 78/0/50/75 | *new — expansion* |
| `green-700` | `#15803D` | 21, 128, 61 | 84/0/52/50 | original |
| `green-600` | `#126C34` | 18, 108, 52 | 83/0/52/58 | *new — expansion* |
| `green-500` | `#168941` | 22, 137, 65 | 84/0/53/46 | *new — expansion* |
| `green-400` | `#33AB60` | 51, 171, 96 | 70/0/44/33 | *new — expansion* |
| `green-300` | `#7AC596` | 122, 197, 150 | 38/0/24/23 | *new — expansion* |
| `green-200` | `#AFDCC0` | 175, 220, 192 | 20/0/13/14 | *new — expansion* |
| `green-100` | `#DEECE3` | 222, 236, 227 | 6/0/4/7 | *new — expansion* |
| `green-50` | `#ECF5EF` | 236, 245, 239 | 4/0/2/4 | original |
| **Red** | | | | |
| `red-950` | `#390B0B` | 57, 11, 11 | 0/81/81/78 | *new — expansion* |
| `red-900` | `#941616` | 148, 22, 22 | 0/85/85/42 | original |
| `red-800` | `#6B1616` | 107, 22, 22 | 0/79/79/58 | *new — expansion* |
| `red-700` | `#B91C1C` | 185, 28, 28 | 0/85/85/27 | original |
| `red-600` | `#BA1C1C` | 186, 28, 28 | 0/85/85/27 | *new — expansion* |
| `red-500` | `#E3140F` | 227, 20, 15 | 0/91/93/11 | original |
| `red-400` | `#D97B7B` | 217, 123, 123 | 0/43/43/15 | *new — expansion* |
| `red-300` | `#F4DDDD` | 244, 221, 221 | 0/9/9/4 | original |
| `red-200` | `#E9CACA` | 233, 202, 202 | 0/13/13/9 | *new — expansion* |
| `red-100` | `#F0E6E6` | 240, 230, 230 | 0/4/4/6 | *new — expansion* |
| `red-50` | `#F9EDED` | 249, 237, 237 | 0/5/5/2 | original |
| **Amber** | | | | |
| `amber-950` | `#2D1605` | 45, 22, 5 | 0/51/89/82 | *new — expansion* |
| `amber-900` | `#904207` | 144, 66, 7 | 0/54/95/44 | original |
| `amber-800` | `#582B09` | 88, 43, 9 | 0/51/90/65 | *new — expansion* |
| `amber-700` | `#B45309` | 180, 83, 9 | 0/54/95/29 | original |
| `amber-600` | `#994608` | 153, 70, 8 | 0/54/95/40 | *new — expansion* |
| `amber-500` | `#C0590A` | 192, 89, 10 | 0/54/95/25 | *new — expansion* |
| `amber-400` | `#D97F3B` | 217, 127, 59 | 0/41/73/15 | *new — expansion* |
| `amber-300` | `#D9AD8D` | 217, 173, 141 | 0/20/35/15 | *new — expansion* |
| `amber-200` | `#E7CCB8` | 231, 204, 184 | 0/12/20/9 | *new — expansion* |
| `amber-100` | `#EFE7E0` | 239, 231, 224 | 0/3/6/6 | *new — expansion* |
| `amber-50` | `#F9F1EB` | 249, 241, 235 | 0/3/6/2 | original |
| **Orange** | | | | |
| `orange-700` | `#C96A1F` | 201, 106, 31 | 0/47/85/21 | original |
| `orange-500` | `#ED7D31` | 237, 125, 49 | 0/47/79/7 | original |
| **Data Viz** | | | | |
| `blue-600` | `#2563EB` | 37, 99, 235 | 84/58/0/8 | original |
| `blue-50` | `#DBEAFE` | 219, 234, 254 | 14/8/0/0 | original |
| `purple-600` | `#7C3AED` | 124, 58, 237 | 48/76/0/7 | original |
| `teal-700` | `#0E7490` | 14, 116, 144 | 90/19/0/44 | original |

### Layer 2 — Semantic Tokens

Intent-based names that describe **how** a colour is used, not what it looks like. These are what you reference in designs. Each points to a primitive token.

| Semantic Token | → Primitive | Hex | Purpose |
|----------------|-------------|-----|---------|
| `color-bg-primary` | white | `#FFFFFF` | Default page/email background |
| `color-bg-secondary` | neutral-50 | `#F5F6F8` | Alternate section backgrounds |
| `color-bg-surface` | neutral-200 | `#E7E8E9` | Card backgrounds, alternating rows |
| `color-bg-brand` | navy-900 | `#0C2746` | Header banners, title slide backgrounds |
| `color-bg-brand-secondary` | navy-700 | `#154175` | Section divider slides, sidebar backgrounds |
| `color-bg-table-even` | neutral-100 | `#EAEDF3` | Even table row fill |
| `color-bg-table-odd` | white | `#FFFFFF` | Odd table row fill |
| `color-bg-success` | green-50 | `#ECF5EF` | Positive callout backgrounds |
| `color-bg-error` | red-50 | `#F9EDED` | Negative callout backgrounds |
| `color-bg-alert` | red-300 | `#F4DDDD` | Critical alert banner backgrounds |
| `color-bg-warning` | amber-50 | `#F9F1EB` | Caution callout backgrounds |
| `color-bg-selection` | blue-50 | `#DBEAFE` | Selected row/cell highlight |
| `color-text-primary` | neutral-900 | `#1F2937` | Primary body text on light backgrounds |
| `color-text-secondary` | neutral-700 | `#4B5563` | Secondary body text, supporting copy |
| `color-text-tertiary` | neutral-500 | `#6B7280` | Placeholder text, icon labels |
| `color-text-muted` | neutral-300 | `#9EA0A9` | Captions, footnotes, metadata |
| `color-text-inverse` | white | `#FFFFFF` | Text on dark/brand backgrounds |
| `color-text-heading` | navy-900 | `#0C2746` | Headings on light backgrounds |
| `color-text-link` | navy-400 | `#547498` | Hyperlinks on light backgrounds |
| `color-text-success` | green-700 | `#15803D` | Positive values, gains, BUY ratings |
| `color-text-error` | red-700 | `#B91C1C` | Negative values, losses, SELL ratings |
| `color-text-alert` | red-500 | `#E3140F` | Urgent alerts, critical emphasis |
| `color-text-warning` | amber-700 | `#B45309` | HOLD ratings, pending, caution labels |
| `color-border-default` | neutral-150 | `#CCCDCF` | Default borders, dividers, gridlines |
| `color-border-strong` | neutral-300 | `#9EA0A9` | Emphasised borders, active outlines |
| `color-border-brand` | navy-400 | `#547498` | Branded borders, accent dividers |
| `color-accent-decorative` | navy-200 | `#92A6C1` | Decorative fills, card accents, tag backgrounds |
| `color-action-primary` | orange-500 | `#ED7D31` | CTA buttons, primary action elements |
| `color-action-hover` | orange-700 | `#C96A1F` | CTA hover/pressed state |
| `color-focus-ring` | blue-600 | `#2563EB` | Keyboard focus indicator ring |
| `color-interactive-success-hover` | green-900 | `#116631` | Hover state on green elements |
| `color-interactive-error-hover` | red-900 | `#941616` | Hover state on red elements |
| `color-interactive-warning-hover` | amber-900 | `#904207` | Hover state on amber elements |

### Layer 3 — Component Tokens (reference guide)

Component tokens map semantic tokens to specific UI elements. These are provided as a reference architecture — implement them when building coded templates or design system components.

| Component Token | → Semantic Token | Usage |
|-----------------|------------------|-------|
| `button-cta-bg` | color-action-primary | CTA button background |
| `button-cta-bg-hover` | color-action-hover | CTA button hover state |
| `button-cta-text` | color-text-inverse | CTA button label |
| `table-header-bg` | color-bg-brand | Table header row background |
| `table-header-text` | color-text-inverse | Table header text |
| `table-row-even` | color-bg-table-even | Even row background |
| `table-row-odd` | color-bg-table-odd | Odd row background |
| `table-positive` | color-text-success | Positive return figures |
| `table-negative` | color-text-error | Negative return figures |
| `email-header-bg` | color-bg-brand | Email header banner |
| `email-body-text` | color-text-primary | Email body copy |
| `email-footer-bg` | color-bg-secondary | Email footer background |
| `slide-title-bg` | color-bg-brand | Title slide background |
| `slide-heading` | color-text-heading | Content slide headings |
| `slide-body` | color-text-primary | Slide body text |
| `callout-success-bg` | color-bg-success | Green callout background |
| `callout-error-bg` | color-bg-error | Red callout background |
| `callout-warning-bg` | color-bg-warning | Amber callout background |

---

## 1. CORE BRAND COLOURS

These are your identity colours sourced from the CG Polaris slide deck theme. They should appear on every email and slide deck.

| Role | Token | Hex | RGB | Usage |
|------|-------|-----|-----|-------|
| **Primary Navy** | `navy-900` | `#0C2746` | 12, 39, 70 | Headers, title bars, slide title backgrounds, email header banners |
| **Secondary Blue** | `navy-700` | `#154175` | 21, 65, 117 | Sub-headers, secondary sections, sidebar backgrounds, table headers |
| **Accent Blue** | `navy-400` | `#547498` | 84, 116, 152 | Body links, icon fills, borders, subtle highlights |
| **Light Blue** | `navy-200` | `#92A6C1` | 146, 166, 193 | Decorative fills, card accents, tag backgrounds |
| **Light Neutral** | `neutral-200` | `#E7E8E9` | 231, 232, 233 | Alternating table rows, card backgrounds, dividers |

### Usage proportions in emails/slides
- **Primary Navy** → ~15% (headers, key structural elements)
- **Secondary Blue** → ~10% (supporting structure)
- **Accent Blue** → ~5% (interactive/highlighted elements)
- **Light Blue & Light Neutral** → As needed for backgrounds and table striping

### Adjacent contrast note
Adjacent brand blues are designed for structural hierarchy, not for text-on-background pairing with each other. Always place blue text on white, off-white, or light neutral backgrounds — never on the adjacent blue shade. Primary Navy and Secondary Blue both pass AAA on white; Accent Blue passes AA on white.

---

## 2. NEUTRAL SYSTEM

Neutrals make up the majority of your email and slide surfaces. This scale runs from off-white through to near-black, giving you dedicated colours for every level of text and surface emphasis.

| Role | Token | Hex | RGB | vs White | Usage |
|------|-------|-----|-----|----------|-------|
| **White** | `white` | `#FFFFFF` | 255, 255, 255 | — | Primary backgrounds, card surfaces |
| **Off-White** | `neutral-50` | `#F5F6F8` | 245, 246, 248 | 1.1:1 | Alternate section backgrounds, email footer |
| **Table Stripe Light** | `neutral-100` | `#EAEDF3` | 234, 237, 243 | 1.2:1 | Alternating table rows (blue-tinted) |
| **Light Neutral** | `neutral-200` | `#E7E8E9` | 231, 232, 233 | 1.2:1 | Card backgrounds, dividers (shared with core) |
| **Table Stripe Dark** | `neutral-150` | `#CCCDCF` | 204, 205, 207 | 1.6:1 | Alternating table rows (grey), border fills |
| **Mid Grey** | `neutral-300` | `#9EA0A9` | 158, 160, 169 | 2.6:1 | Captions, footnotes, metadata — large text only |
| **Grey** | `neutral-500` | `#6B7280` | 107, 114, 128 | 4.8:1 AA | Placeholder text, secondary labels, icons |
| **Dark Grey** | `neutral-700` | `#4B5563` | 75, 85, 99 | 7.6:1 AAA | Body text (secondary), paragraph copy |
| **Near-Black** | `neutral-900` | `#1F2937` | 31, 41, 55 | 14.7:1 AAA | Body text (primary), headings on light surfaces |

### Why not pure black?
Pure black (#000000) on white creates a harsh 21:1 ratio that causes visual fatigue. Near-Black `#1F2937` at 14.7:1 is well above WCAG AAA while being significantly easier on the eyes — especially important for dense financial reports and slide decks.

---

## 3. SEMANTIC COLOURS

Semantic colours communicate meaning: gains/losses, success/failure, warnings and alerts. Each family includes a base colour for text/icons, a light tint for backgrounds, and a dark shade for hover/active states.

### Success (Green)

| Role | Token | Hex | RGB | vs White | When to use |
|------|-------|-----|-----|----------|-------------|
| **Light BG** | `green-50` | `#ECF5EF` | 236, 245, 239 | 1.1:1 | Success callout backgrounds, positive row tint |
| **Positive Green** | `green-700` | `#15803D` | 21, 128, 61 | 5.0:1 AA | Gains, positive returns, BUY ratings, success |
| **Green Dark** | `green-900` | `#116631` | 17, 102, 49 | 7.1:1 AAA | Hover/active state for green elements |

### Error (Red)

| Role | Token | Hex | RGB | vs White | When to use |
|------|-------|-----|-----|----------|-------------|
| **Light BG** | `red-50` | `#F9EDED` | 249, 237, 237 | 1.1:1 | Error callout backgrounds, negative row tint |
| **Negative Red** | `red-700` | `#B91C1C` | 185, 28, 28 | 6.5:1 AA | Losses, negative returns, SELL ratings, errors |
| **Red Dark** | `red-900` | `#941616` | 148, 22, 22 | 8.8:1 AAA | Hover/active state for red elements |

### Alert (Bright Red)

| Role | Token | Hex | RGB | vs White | When to use |
|------|-------|-----|-----|----------|-------------|
| **Alert Light BG** | `red-300` | `#F4DDDD` | 244, 221, 221 | 1.3:1 | Critical alert banner backgrounds |
| **Alert Red** | `red-500` | `#E3140F` | 227, 20, 15 | 4.8:1 AA | Urgent alerts, critical warnings, emphasis text |

### Warning (Amber)

| Role | Token | Hex | RGB | vs White | When to use |
|------|-------|-----|-----|----------|-------------|
| **Light BG** | `amber-50` | `#F9F1EB` | 249, 241, 235 | 1.1:1 | Warning callout backgrounds, HOLD-rating row tint |
| **Caution Amber** | `amber-700` | `#B45309` | 180, 83, 9 | 5.0:1 AA | HOLD ratings, warnings, pending states |
| **Amber Dark** | `amber-900` | `#904207` | 144, 66, 7 | 7.1:1 AAA | Hover/active state for amber elements |

### Critical rule: Never use colour alone
Every instance of semantic colour must be paired with a text label, icon, or directional indicator (↑ ↓ →). This ensures accessibility for colourblind users (~8% of male recipients) and renders correctly in plain-text email fallbacks.

### Intensity matching
The three base semantic colours (green `#15803D`, red `#B91C1C`, amber `#B45309`) are matched at similar perceived brightness (~101–117) and contrast ratios (~5.0–6.5:1 on white). This means gains and losses appear at the same visual "loudness" — neither dominates unfairly.

---

## 4. CTA / ACTION ACCENT

| Role | Token | Hex | RGB | Usage |
|------|-------|-----|-----|-------|
| **CTA Orange** | `orange-500` | `#ED7D31` | 237, 125, 49 | Primary CTA buttons, key action highlights, chart secondary series |
| **CTA Hover** | `orange-700` | `#C96A1F` | 201, 106, 31 | Hover/pressed state for CTA buttons |

### Why orange?
Orange is the **complementary colour** to your navy blue (opposite on the colour wheel), creating maximum visual contrast. It is safe for the most common form of colour blindness (red-green deficiency) and carries associations of energy, warmth, and action.

### Usage rules
- Maximum **1–2 CTA buttons per email** in orange
- On slides: use for the single most important callout, chart annotation, or action item
- Never use orange for large background areas — it is a 10% accent colour
- White text on CTA Orange is 2.8:1 — use **bold text at 16px+** or use on navy backgrounds (5.4:1 AA)

---

## 5. DATA VISUALISATION

A 7-colour categorical palette for charts, graphs, and data tables. Colours are sequenced by hue for maximum distinction. The first 4 reuse semantic/accent tokens; the last 3 are chart-specific additions.

| # | Role | Token | Hex | vs White | When to use |
|---|------|-------|-----|----------|-------------|
| 1 | **Portfolio / Primary series** | `blue-600` | `#2563EB` | 5.2:1 AA | Your fund/strategy line in performance charts |
| 2 | **Benchmark / Secondary series** | `orange-500` | `#ED7D31` | 2.8:1 | Benchmark or comparison line (e.g., index) |
| 3 | **Positive figures** | `green-700` | `#15803D` | 5.0:1 AA | Monthly returns > 0, gains, outperformance |
| 4 | **Negative figures** | `red-700` | `#B91C1C` | 6.5:1 AA | Monthly returns < 0, losses, underperformance |
| 5 | **Series 3** | `purple-600` | `#7C3AED` | 5.7:1 AA | 3rd categorical data series |
| 6 | **Series 4** | `teal-700` | `#0E7490` | 5.4:1 AA | 4th categorical data series |
| 7 | **Series 5** | `amber-700` | `#B45309` | 5.0:1 AA | 5th categorical data series (reuses warning amber) |

### Rules
- **Two-line charts:** Always Blue (portfolio) + Orange (benchmark)
- **Performance tables:** Green text for positive, red text for negative — always paired with the +/− sign
- **Red is reserved for negative data only** — never use it as a generic category colour
- **Green vs Red pairing:** Always accompany with ↑/↓ icons for colourblind safety
- **Amber vs Orange proximity:** Avoid placing these as adjacent series — use non-adjacent positions when both appear
- Keep chart backgrounds white or off-white for maximum readability on projected slides

### Interactive states
| Token | Hex | Usage |
|-------|-----|-------|
| `blue-600` | `#2563EB` | Focus ring for keyboard navigation |
| `blue-50` | `#DBEAFE` | Selected row/cell highlight background |

---

## 6. APPLICATION RULES BY FORMAT

### Emails — Two Modes

**Mode A: Dark Background (Newsletters)**
Use for: Daily Intel Digest, internal product updates, external industry briefings.

| Element | Token | Hex | Notes |
|---------|-------|-----|-------|
| Header banner | `color-bg-brand` | `#0C2746` | Full-width, with white logo |
| Header text | `color-text-inverse` | `#FFFFFF` | Company name, newsletter title |
| Body background | `color-bg-brand` | `#0C2746` | Consistent dark surface |
| Body text | `color-text-inverse` | `#FFFFFF` | Primary body copy |
| Secondary text | `color-text-link` | `#547498` | Timestamps, source labels, metadata |
| Section headers | `color-text-inverse` | `#FFFFFF` | Bold, all-caps for scannability |
| Links | `color-accent-decorative` | `#92A6C1` | Underline recommended for distinction |
| CTA button (bg) | `color-action-primary` | `#ED7D31` | High contrast against navy |
| CTA button (text) | `color-text-inverse` | `#FFFFFF` | Bold |
| Section dividers | `color-bg-brand-secondary` | `#154175` | 1px horizontal rules |
| Footer text | `color-text-link` | `#547498` | Legal, unsubscribe, address |

**Mode B: Light Background (Reports & Data Emails)**
Use for: Performance reports, portfolio summaries, emails with tables, charts, or dense data.

| Element | Token | Hex | Notes |
|---------|-------|-----|-------|
| Header banner | `color-bg-brand` | `#0C2746` | Full-width, with white logo |
| Header text | `color-text-inverse` | `#FFFFFF` | On navy background |
| Body background | `color-bg-primary` | `#FFFFFF` | Maximum readability for data |
| Body text | `color-text-primary` | `#1F2937` | Near-Black — never pure black |
| Secondary text | `color-text-muted` | `#9EA0A9` | Timestamps, disclaimers, footnotes |
| Links | `color-text-link` | `#547498` | Underlined for accessibility |
| CTA button (bg) | `color-action-primary` | `#ED7D31` | Rounded corners, centered |
| CTA button (text) | `color-text-inverse` | `#FFFFFF` | Bold, high contrast |
| Section dividers | `color-border-default` | `#CCCDCF` | 1px horizontal rules |
| Alternating table rows | `color-bg-table-even` | `#EAEDF3` | Subtle distinction |
| Performance (positive) | `color-text-success` | `#15803D` | Always paired with ↑ or + |
| Performance (negative) | `color-text-error` | `#B91C1C` | Always paired with ↓ or − |
| Performance (hold) | `color-text-warning` | `#B45309` | Always paired with → or HOLD label |
| Footer background | `color-bg-secondary` | `#F5F6F8` | Subtle separation from body |
| Footer text | `color-text-muted` | `#9EA0A9` | Legal, unsubscribe, address |

### Slide Decks

| Element | Token | Hex | Notes |
|---------|-------|-----|-------|
| Title slide background | `color-bg-brand` | `#0C2746` | High-impact, brand-forward |
| Title slide text | `color-text-inverse` | `#FFFFFF` | Company name, presentation title |
| Content slide background | `color-bg-primary` | `#FFFFFF` | Clean, data-friendly |
| Content slide headings | `color-text-heading` | `#0C2746` | Consistent hierarchy |
| Body text | `color-text-primary` | `#1F2937` | Near-Black for readability |
| Section divider slides | `color-bg-brand-secondary` | `#154175` | With white text, marks transitions |
| Key metric callouts | `color-action-primary` | `#ED7D31` | Sparingly — 1–2 per deck section |
| Chart colours | Data viz sequence | See §5 | In order of data series |
| Table headers | `color-bg-brand` | `#0C2746` | White text |
| Table alternating rows | `color-bg-table-even` | `#EAEDF3` | Subtle striping |
| Callout: positive | `color-bg-success` | `#ECF5EF` | Green-tinted callout box |
| Callout: negative | `color-bg-error` | `#F9EDED` | Red-tinted callout box |
| Callout: warning | `color-bg-warning` | `#F9F1EB` | Amber-tinted callout box |
| Footnotes/sources | `color-text-muted` | `#9EA0A9` | Small size, low emphasis |

---

## 7. ACCESSIBILITY CHECKLIST

Before sending any email or presenting any deck:

- [ ] All body text achieves **4.5:1 contrast ratio** against its background (WCAG AA)
- [ ] All heading/large text achieves **3:1 minimum** (WCAG AA for large text)
- [ ] Semantic colours (green, red, amber) are **never used alone** — always paired with text labels or icons
- [ ] Charts include **patterns or labels** alongside colour coding
- [ ] Email has been tested in **dark mode** (Apple Mail, Gmail, Outlook)
- [ ] No critical information is conveyed through colour alone
- [ ] CTA buttons have sufficient padding and contrast for touch targets

### Quick contrast reference

| Combination | Ratio | WCAG Rating |
|-------------|-------|-------------|
| Near-Black `#1F2937` on White | 14.7:1 | ✅ AAA |
| Dark Grey `#4B5563` on White | 7.6:1 | ✅ AAA |
| Primary Navy `#0C2746` on White | 15.1:1 | ✅ AAA |
| White on Primary Navy `#0C2746` | 15.1:1 | ✅ AAA |
| White on Secondary Blue `#154175` | 10.3:1 | ✅ AAA |
| Accent Blue `#547498` on White | 4.9:1 | ✅ AA |
| Grey `#6B7280` on White | 4.8:1 | ✅ AA |
| Positive Green `#15803D` on White | 5.0:1 | ✅ AA |
| Positive Green on Green BG `#ECF5EF` | 4.5:1 | ✅ AA |
| Negative Red `#B91C1C` on White | 6.5:1 | ✅ AA |
| Negative Red on Red BG `#F9EDED` | 5.7:1 | ✅ AA |
| Caution Amber `#B45309` on White | 5.0:1 | ✅ AA |
| Caution Amber on Amber BG `#F9F1EB` | 4.5:1 | ✅ AA |
| Alert Red `#E3140F` on White | 4.8:1 | ✅ AA |
| Mid Grey `#9EA0A9` on White | 2.6:1 | ⚠️ Large text / decorative only |
| White on CTA Orange `#ED7D31` | 2.8:1 | ⚠️ Bold 16px+ only |
| White on CTA Hover `#C96A1F` | 3.8:1 | ✅ AA Large |
| CTA Orange on Navy `#0C2746` | 5.4:1 | ✅ AA |

> **CTA Orange note:** White text on the orange button is 2.8:1 — use bold text at 16px+ minimum. For small text contexts, use CTA Hover `#C96A1F` (3.8:1) or place the orange on a navy background (5.4:1 AA).

---

## 8. COMPLETE PALETTE SUMMARY

### All colours at a glance — 58 token slots (27 new expansion tokens)

**Core Brand — Navy (11, was 4)**
`#0C1D30` · `#0C2746` · `#17375D` · `#154175` · `#285FA0` · `#407ABC` · `#547498` · `#A2B8D3` · `#92A6C1` · `#E4E9EE` · `#F1F3F6`

**Core Brand — Neutral (9, unchanged)**
`#FFFFFF` · `#F5F6F8` · `#EAEDF3` · `#E7E8E9` · `#CCCDCF` · `#9EA0A9` · `#6B7280` · `#4B5563` · `#1F2937`

**Semantic — Success / Green (11, was 3)**
`#072011` · `#116631` · `#0E4020` · `#15803D` · `#126C34` · `#168941` · `#33AB60` · `#7AC596` · `#AFDCC0` · `#DEECE3` · `#ECF5EF`

**Semantic — Error / Red (11, was 5)**
`#390B0B` · `#941616` · `#6B1616` · `#B91C1C` · `#BA1C1C` · `#E3140F` · `#D97B7B` · `#F4DDDD` · `#E9CACA` · `#F0E6E6` · `#F9EDED`

**Semantic — Alert (2, unchanged)**
`#F4DDDD` · `#E3140F`

**Semantic — Warning / Amber (11, was 3)**
`#2D1605` · `#904207` · `#582B09` · `#B45309` · `#994608` · `#C0590A` · `#D97F3B` · `#D9AD8D` · `#E7CCB8` · `#EFE7E0` · `#F9F1EB`

**CTA Accent (2, unchanged)**
`#ED7D31` · `#C96A1F`

**Data Viz (3 unique + 4 shared)**
`#2563EB` · `#7C3AED` · `#0E7490` — plus reuses orange, green, red, amber from above

**Interactive (2, unchanged)**
`#2563EB` · `#DBEAFE`

---

## 9. PROVENANCE

| Source | Colours |
|--------|---------|
| **CG Polaris deck theme** (accent1–6) | `#0C2746`, `#154175`, `#E7E8E9` (from theme + hardcoded deck values) |
| **CG Polaris deck hardcoded** | `#EAEDF3`, `#CCCDCF`, `#9EA0A9`, `#E3140F`, `#ED7D31` |
| **Adjusted from deck blues** | `#547498` (widened from `#517398`), `#92A6C1` (widened from `#6F8BAA`) |
| **Derived: accessibility-matched** | `#15803D` (green AA), `#B91C1C` (red AA, brightness-matched to green), `#B45309` (amber AA) |
| **Derived: tint/shade scales** | `#ECF5EF`, `#116631`, `#F9EDED`, `#941616`, `#F4DDDD`, `#F9F1EB`, `#904207` |
| **Derived: neutral scale** | `#F5F6F8`, `#6B7280`, `#4B5563`, `#1F2937` |
| **Derived: data viz** | `#2563EB`, `#7C3AED`, `#0E7490`, `#DBEAFE` |
| **Derived: monochromatic expansion** | All tokens marked *(new — expansion)* in Layer 1; generated via perceptual lightness targeting (see Appendix A) |

---

## APPENDIX A — COLOUR SCALE ANALYSIS

This appendix documents the analysis methods used to evaluate the existing colour kit and generate the expansion tokens. Three algorithms were applied.

### A.1 Lightness scale evaluation

Each existing ramp was measured for perceptual lightness (CIE L*) to check whether steps are evenly spaced. Even spacing ensures consistent visual weight between adjacent tokens.

**Key findings:**

- **Navy ramp**: Steps 200→400→700 have roughly even perceptual gaps (~20 L* each). The 700→900 gap is tighter (ΔL* 12), meaning the two darkest navys are perceptually closer than the rest of the ramp. Acceptable for current use but limits expansion headroom.
- **Neutral ramp**: The `neutral-200` (`#E7E8E9`, L* 91.9) is perceptually lighter than `neutral-150` (`#CCCDCF`, L* 82.4), creating a lightness inversion in the naming sequence. A 26-point cliff between 200 and 300 is the largest gap. The non-standard 150 slot was inserted to bridge this gap.
- **Green & Amber**: Both have a ~49 L* void between 50 and 700 with no intermediate stops — the largest gaps in the kit.
- **Red**: The 300 (`#F4DDDD`, L* 89.9) sits very close to 50 (L* 94.7) with only ΔL* 4.7, then drops 41.8 points to 500. The 300 is functioning as a second tint rather than a true mid-light value.

### A.2 Tailwind CSS benchmark

Each ramp was compared against what Tailwind CSS's algorithm would generate from the same anchor colour. This benchmarks the kit's hand-picked values against the industry-standard curve that the kit's naming convention mirrors.

**Key findings:**

- **Navy 700 and 900** align within ΔL* 1–5 of Tailwind output (validates the anchor values). Navy 200 and 400 are significantly darker than Tailwind equivalents (ΔL* −16 to −21), reflecting their functional roles as link/decorative colours rather than standard light tints.
- **Neutral 50, 100, 500, 700, 900** all land within ΔL* 1–4 of Tailwind. The `neutral-300` (`#9EA0A9`, L* 66) is 13 points darker than Tailwind's 300 equivalent — it sits at roughly the Tailwind 400 position.
- The kit intentionally diverges from algorithmic purity in favour of accessibility-matched values. This is documented for future designers who should not expect standard step-to-lightness mapping.

### A.3 Monochromatic expansion

Full 11-step monochromatic ramps were generated for each semantic colour family (green, red, amber) and the navy brand ramp. The algorithm varies lightness and saturation together from a single hue anchor, targeting perceptual lightness values of L* 96 (step 50) down to L* 10 (step 950).

**Expansion method:**
- Hue is preserved from the original anchor colour at each ramp's 700 step
- Saturation is reduced at very light stops (×0.35 at L* > 85) and slightly at very dark stops (×0.9 at L* < 35) to prevent oversaturation
- Perceptual lightness targets follow a Tailwind-inspired curve: 50=96, 100=92, 200=84, 300=74, 400=62, 500=50, 600=40, 700=31, 800=23, 900=16, 950=10
- Original hand-picked values are preserved at their existing steps; only missing steps are filled

**Note on naming vs lightness**: The original kit's semantic colours (green-700, red-700, amber-700) were deliberately brightness-matched at similar perceived intensity (~L* 40–47, contrast ratios ~5.0–6.5:1 on white) for equal visual weight in financial data display. The expansion tokens follow the monochromatic curve around these anchors, so adjacent expansion steps (600, 800) may have closer-than-expected gaps to the original values. This is by design — the expansion fills the perceptual gaps above and below the accessibility-matched core, not between the core values themselves.
