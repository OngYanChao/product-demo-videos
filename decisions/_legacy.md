# Legacy decisions (pre-2026-05-15)

These decisions predate the dated decisions log in `decisions/INDEX.md` and live in their original encoding sites (production-principles, skill files, references). Migrate to dated ADRs lazily as they're revisited.

- **Hyperframes-only render path.** Local rendering. The HeyGen template-based pipeline (v2, sunsetting Oct 31, 2026) was retired during the 2026-04-29 overhaul. See `references/claude-design-to-hyperframes.md` for the conversion reasoning.
- **Stock avatar + voice IDs.** No custom twin creation. `HEYGEN_AVATAR_ID` and `HEYGEN_VOICE_ID` in `.env` are the canonical identity for every video. Per-video override available via script frontmatter (rare).
- **Skills for judgment, code (`tools/`) for mechanics.** This is what unblocks the OpenClaw/cron automation — `tools/render.py` runs without Claude in the loop.
- **62K listings / 48 markets.** Replaced WP-era 48,403 / 36 markets in marketing collateral and Highlights. Sourced to `parallax-obsidian/04-Marketing/Key Differentiators.md`.
- **One template per video family** (not per video). Templates are authored once via Claude Design, parameterized via script frontmatter at render time.
- **Avatar-last in the pipeline.** Iteration on layout/script is free; only the final render bills HeyGen for the avatar clip. Caching by script hash prevents re-billing for unchanged scripts.
