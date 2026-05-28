# Learnings (scratch / staging)

User-personal scratch space. Notes, drafts, and research that may eventually graduate to canonical reference docs but are **not** yet part of the load-bearing pipeline. The Parallax video pipeline (skills, MASTER.md, CLAUDE.md, tools/) does not read anything in this folder.

**Canonical reference docs live in `references/`** (not here). Anything in `learnings/` is provisional.

## Current contents

| File | Status | Notes |
|---|---|---|
| `INTEGRATION_LOG.md` | Status tracker | Tracks which findings have made it from notes → canonical refs / skills |
| `writing-for-the-ear.md` | Craft research | Source material for the spoken-vs-written rules in `video-scriptwriting` skill. May be promoted to `references/` if/when it becomes load-bearing |
| `voiceover-interprets-visuals.md` | Craft research | Source material for the "show on screen, interpret in VO" rule. Same status |
| `demo-video-format.md` | Format research | Live screen recording vs slide-deck vs hybrid analysis for B2B SaaS demos |
| `_archive/caption-design-for-fintech.md` | Obsolete | Captions removed from product-demo template 2026-05-08; spec retained for reference if a future template family ever re-introduces captions |

## Promoted to `references/`

These were previously here but graduated to canonical (load-bearing) status — moved to `references/`:

- `value-framing-menu.md` — canonical 12-angle vocabulary, consumed by MASTER + 2 skills + CLAUDE
- `production-principles.md` — locked production rules, referenced by CLAUDE.md
- `claude-design-to-hyperframes.md` — template-authoring guidance, referenced by CLAUDE.md + RENDER-GUIDE

## When to promote a file out of here

Move a file from `learnings/` to `references/` when:
1. Some part of the canonical pipeline (a skill, MASTER.md, CLAUDE.md, a tool, RENDER-GUIDE) starts referencing it by path, AND
2. Its content is stable enough that we'd want to enforce single-source-of-truth on it (i.e. don't want it duplicated inline elsewhere).

Until both are true, leave it here.
