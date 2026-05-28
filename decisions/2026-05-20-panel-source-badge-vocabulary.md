# 2026-05-20 — Panel Source + Badge Vocabulary Locked

**Status:** active
**Affects:** `.claude/skills/video-scriptwriting/SKILL.md` (§ "Panel content authoring" — new locked-vocabulary table for source + badge), `scripts/V1 voiceover script.md` (ap1/ap2/ap3 rewritten to canonical values)

## Decision

The `panel.source:` and `panel.badge:` fields on every annotation panel draw from a **locked vocabulary** sourced from the Parallax vault — no freelancing.

**Source — `Source: <Parallax product name>`** from four canonical names:
- `Parallax Fundamentals` — peer comparison + pricing (P/E, P/B, EV/EBITDA)
- `Parallax Factor Scores` — 5-factor scoring output incl. trajectory
- `Parallax Factor Library` — 30+ alpha signal library
- `Parallax Research` — analyst-consensus synthesis + alternative-data integration

**Badge — one of nine tags:**
- 8 methodology-virtue tags (each ≤ 18 chars): `Peer-adjusted`, `Regime-adaptive`, `Percentile-ranked`, `Ensemble-based`, `Academically-grounded`, `Live-tested`, `Auditable`, `Transparent`
- 1 temporal special-case: `As of <Mon DD, YYYY>` — for verdicts/calls where freshness is the relevant credibility signal

**Pairing convention:** the badge describes the *spotlit segment*, not Parallax broadly. The tag must be especially true of *this row/cell/paragraph*, not a generic Parallax virtue.

## Why

V1.2's three panels shipped with ad-hoc source + badge values I invented while authoring ("Parallax fundamentals" lowercase — fictional file; "Out-of-sample" — not canonical vault language; "61-analyst consensus" — derived from recording but inconsistent with the other panels' citation format). User flagged it: *"whats the source on the panel? what do you use for sources"* + *"whats the 'peer-adjusted' and 'out of sample' tag"* — exposing that I had no vocabulary discipline and was freelancing the credibility signals.

The credibility signals on these panels are *the* Parallax-credibility move — what distinguishes the brief from a generic AI summary. Letting them drift to whatever felt right per-panel makes the brand read amateur and the citations un-auditable.

Vault research (vault explore agent, 2026-05-20) confirmed the 8 methodology-virtue tags as actual recurring vault language across `01-Product/Scoring System.md`, `02-Methodology/Investment Factors.md`, `02-Methodology/Vendor-FAQ.md`, and `04-Marketing/Key Differentiators.md`. The 4 product names recur as well — they're Parallax's actual data-product taxonomy, not labels I made up.

## Notes

- V1.2 panel rewrites applied as part of this decision:
  - ap1: `Parallax fundamentals` / `Peer-adjusted` → `Parallax Fundamentals` (capitalized) / `Peer-adjusted` (kept — was correct)
  - ap2: `Parallax weekly factor scores` / `Out-of-sample` → `Parallax Factor Scores` / `Regime-adaptive`
  - ap3: `61-analyst consensus` / `As of 2026-02-25` → `Parallax Research` / `As of Feb 25, 2026` (American date format reads better than ISO at small UI size)
- The vocabulary is intentionally small (4 products × 9 badges = 36 combinations). A 16-panel video like V14 (Iran playbook) will repeat combinations. That's fine — the badge isn't a unique identifier, it's a methodology signal. Repetition reinforces the brand.
- Adding a new tag: escalate, name the vault file/line, add to the locked table in the same commit as the panel using it. Silent additions are forbidden.
- Companion to the 12-angle value-framing menu (`references/value-framing-menu.md`) and the 3-shape panel rotation. Those vary the rhetorical stance; source + badge stay constrained.
- For the date-stamped temporal badge: the date should be a value present in the recording (or derivable from the vault stat being cited). Don't invent dates. Format = `As of Mon DD, YYYY` (American), not ISO.
