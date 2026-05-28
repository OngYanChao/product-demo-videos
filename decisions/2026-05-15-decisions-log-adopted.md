# 2026-05-15 — Adopt Date-Stamped Decisions Log

**Status:** active
**Affects:** `CLAUDE.md` (new "Decisions log" section), `decisions/INDEX.md` (chronological log + capture protocol)

## Decision

All locked-in project decisions and rules are now archived in `decisions/` as dated markdown files (`YYYY-MM-DD-slug.md`) and indexed chronologically in `decisions/INDEX.md`. The index also documents the trigger phrases and capture protocol that Claude follows when the user signals a new decision.

Going forward, *new* decisions go through this system. Pre-existing decisions live in their original homes:

- **Project decisions / locked rules** — `references/production-principles.md` (Principles #1–#13)
- **High-level architectural choices** — `CLAUDE.md` "Decisions made (don't re-litigate)" section
- **Per-template format invariants** — `templates/<family>/RENDER-GUIDE.md`
- **Skill/methodology rules** — `.claude/skills/video-production-workflow/SKILL.md` Hard Rules, `.claude/skills/video-scriptwriting/SKILL.md`

Migration of legacy entries into the dated log is optional and can be done lazily — when an old decision is re-visited or modified, that's a natural moment to log the change as a new entry.

## Why

Recurring problem: the user re-litigates the same architectural decisions across Claude sessions because earlier decisions aren't surfaced consistently. CLAUDE.md is loaded every session but its "Decisions made" bullet list isn't dated and isn't append-friendly — adding a new decision requires editing CLAUDE.md prose, which discourages capture. A separate `decisions/` folder with a chronological INDEX makes capture a one-file-write operation and gives the log a clear linear timeline.

Alternative considered: a `Stop` hook that auto-extracts decisions from each turn via an LLM call. Rejected for v1 because (a) false positives clutter the log, (b) requires hook configuration the user hasn't authorized, (c) trigger-phrase capture in CLAUDE.md is reversible and zero-risk. Revisit if trigger-phrase capture proves too lossy.

## Notes

- Chronological order is **oldest → newest** (newest entries at the bottom of the INDEX table). If the user later prefers newest-first, flip the sort.
- The decisions log is the *event log*; existing files like `production-principles.md` and skill files remain the *authoritative current-state encoding*. When a decision changes a rule, update both — cross-link in both directions.
- Trigger phrases are intentionally broad to err toward over-capture in v1. Tighten later if noise becomes a problem.
