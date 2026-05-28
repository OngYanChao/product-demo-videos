# 2026-05-15 — Rule-Routing Protocol Added to Decisions Capture

**Status:** active
**Affects:** `decisions/INDEX.md` (new "Rule routing" section), `CLAUDE.md` ("Decisions log (auto-captured)" section)

## Decision

The decisions-capture protocol is now a **two-step flow**:

1. Always create a dated ADR in `decisions/YYYY-MM-DD-<slug>.md` and append a row to `decisions/INDEX.md`.
2. *In addition*, route the rule's substance to its authoritative encoding site based on rule type:
   - **Portable methodology rule** → next numbered Hard Rule in `.claude/skills/video-production-workflow/SKILL.md`
   - **Parallax project decision** → next numbered Principle in `references/production-principles.md`
   - **Script craft** → `.claude/skills/video-scriptwriting/SKILL.md`
   - **Per-template invariant** → `templates/<family>/RENDER-GUIDE.md`
   - **Unclear / cross-cutting** → ADR only, then ask the user where to encode

Cross-link in both directions (ADR's `Affects:` ↔ encoding site's "Logged: `decisions/...`" suffix). Surface both file paths to the user after capture.

The full routing table + heuristics for ambiguous phrasing live in `decisions/INDEX.md` under "Rule routing."

## Why

The original bootstrap entry ([2026-05-15-decisions-log-adopted](2026-05-15-decisions-log-adopted.md)) captured *events* but left rules sitting in the ADR-only — meaning Claude wouldn't see them at work-time unless it specifically read `decisions/`. The encoding sites (`video-production-workflow/SKILL.md` Hard Rules, `production-principles.md`, skill files, RENDER-GUIDEs) are the files Claude actually reads when *executing* the relevant phase. Routing the rule to its encoding site means future-Claude picks up the rule in-flow; the dated ADR remains the queryable history.

Alternative considered: store rules *only* in encoding sites and skip the dated ADR. Rejected because (a) chronological history is the whole point of the user's request — "I keep re-litigating the same decisions," and (b) some decisions (architecture choices, vendor selections) don't have a natural encoding site beyond CLAUDE.md, so the ADR is their primary home.

Alternative considered: a single combined encoding site (one giant rules file). Rejected because the existing 4-home split is meaningful — portable methodology vs. Parallax-specific vs. script craft vs. template invariants each have different audiences and different rotation cycles. Forcing them into one file would dilute every audience.

## Notes

- The user specifically asked for `video-production-workflow/SKILL.md` to be auto-updated; the routing table generalizes that to all four encoding sites for consistency.
- Routing heuristics in `decisions/INDEX.md` bias on trigger phrase (`"hard rule"` → methodology; `"new principle"` → Parallax) and on keyword content (Parallax-specific terms vs. generic methodology vocabulary).
- When two homes seem plausible, prefer the more specific one and add a one-line pointer from the broader one.
