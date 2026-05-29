# CLAUDE.md — Parallax Video Production

*Project handoff context. Pipeline architecture: **Hyperframes-based local rendering** with HeyGen invoked only for the avatar clip. The 2026-04-29 → 2026-05-11 HeyGen-to-Hyperframes migration is complete. A subsequent **persona-and-moment overhaul** (2026-05-11 → 2026-05-13) replaced the capability-organized 28-video master plan with a persona-and-moment-driven 20-video slate. Both overhauls' planning is captured in `overhaul.md` (kept as the active-overhaul tracker; not deleted).*

---

## What this project is

A persona-and-moment-driven video content library for Chicago Global / Parallax — **20 videos** organized around `primary_persona × primary_moment × deliverable` rather than per-Parallax-command:

- **4 instructional (I1–I4)** — audience-general utility content: install, first-brief quickstart, free-tier walkthrough, exports & integrations. Style: `instructional`.
- **6 Tier-1 single-feature use-cases (V1–V6)** — persona × specific moment × single Parallax tool. Includes V1 (canary, RM client-question moment). Style: `use_case`, complexity: `single_feature`.
- **7 Tier-2 workflow-chain use-cases (V7–V13)** — persona × moment × 2-4 chained tools producing a composite deliverable. Style: `use_case`, complexity: `workflow_chain`.
- **3 Tier-3 hero playbooks (V14–V16)** — persona × event-moment × publishable synthesis (Iran playbook, initiation report, forensic earnings). Style: `use_case`, complexity: `hero_playbook`.

Driven by `Parallax Video Plan - MASTER.md` (the *NEW SLATE — Phase 3 Draft* section). All videos are recording-driven product demos.

**Intelligence briefs (intel_brief style)** are *shelved as a deferred future addition* (per `overhaul.md` Phase 5). Infrastructure (style enum, frontmatter `style:` field, paused stub in `video-scriptwriting/SKILL.md`) stays in place to make reactivation a clean drop-in. The intel-brief template family has not been built.

---

## Pipeline architecture

| Layer | Tool | Where it runs | Cost |
|---|---|---|---|
| **Renderer** | [Hyperframes](https://hyperframes.heygen.com/) — open-source HTML→MP4 (Apache 2.0) | Local (Puppeteer + FFmpeg) | Free |
| **Avatar generation** | HeyGen `heygen-video` skill via `heygen` CLI | HeyGen API | Per-clip credits |
| **Orchestration** | Custom `parallax-video` skill + `tools/render.py` (preview + final modes) | Local | — |
| **Frame extraction** | `tools/extract_frames.py` | Local (FFmpeg) | Free |
| **Recording polish** | `tools/scrub.py` (tapered cuts of dead loading) | Local (FFmpeg) | Free |

**Cost model:** the avatar talking-head clip is the only billable step. Local Hyperframes render (preview AND final composition) is free. Avatar clips are cached at `avatars/clips/V<N>_<scripthash>.mp4` so iteration on layout / timing / copy is free until the script body itself changes.

---

## Daily workflow per video

- **Methodology** (portable, all phases + Hard Rules): `.claude/skills/video-production-workflow/SKILL.md`
- **Project wiring** (orchestrator — handles every phase trigger, routes through the methodology): `.claude/skills/parallax-video/SKILL.md`
- **Visual flowchart** of the 11 phases: `references/product-demo-pipeline.md`

The hard rule: the beat sheet (from MASTER.md Highlights) is upstream of recording AND script. Never let recording length silently dictate script content; conform the recording instead. The *If the user asks you to* table below maps trigger phrases to phases — invoke the `parallax-video` skill on each trigger; do not shortcut to bash.

*Intel-brief style (`intel_brief`) is shelved as a deferred future addition — see `overhaul.md` Phase 5.*

---

## Source-of-truth content

| File / folder | What it is | When to read |
|---|---|---|
| `Parallax Video Plan - MASTER.md` | Master spec for the **20 product-demo videos** (4 instructional I1–I4 + 16 use_case V1–V16). The new slate lives in the *NEW SLATE — Phase 3 Draft* section near the bottom of the file. Per-video table + **Highlights** subsection (locked stat ownership) + beat sheet + title-card values + YouTube title + value-framing assignment + recording requirements + format invariants. Plus the vault-stats library, defensibility tiers, production notes (these surive from the pre-overhaul plan). Legacy 28-video specs archived to `_archive/MASTER-pre-overhaul-2026-05-11.md`. | Read the relevant V<N> or I<N> section before drafting any product-demo script. The Highlights are canonical for what stats that video owns. |
| `parallax-obsidian/` | Cloned source-of-truth vault (2,200+ markdown files: product facts, methodology, positioning, investor letters). | For: intel-brief stat sourcing, methodology grounding, brand voice. **Don't draft from**: `06-Investor-Letters/` (read-only reference) or `07-Reference-Library/` (third-party). Refresh with `cd parallax-obsidian && git pull`. |
| `references/colour-kit.md` | Chicago Global brand colour system. | Reference when authoring or updating templates in Claude Design. |
| `templates/<family>/RENDER-GUIDE.md` | Per-template format invariants: layout positions, animation timings, character limits, locked tagline. | Read whenever drafting a script that targets that template — orchestrator enforces these constraints. |
| `learnings/` | Craft principles, Claude Design-to-Hyperframes checklist, integration log. | Reference for craft rules and template authoring. |

---

## Skills + tools

### Skills (`.claude/skills/`)

| Skill | Origin | Status |
|---|---|---|
| `parallax-video/` | Ours (project-local orchestrator) | Active — wires `video-production-workflow` + `video-scriptwriting` to this project's tools. Dispatch table handles `V<N>` (use_case) + `I<N>` (instructional) prefixes. |
| `video-production-workflow/` | Ours (portable methodology) | Active — beat-sheet-first phasing, conformation decision tree, dwelling principle. Reusable across video projects. |
| `video-scriptwriting/` | Ours (portable craft) | Active — voice composite, banned words, hallucination check, "show on screen / interpret in VO." Consumed by `video-production-workflow` at Phase 5. |
| `hyperframes/`, `hyperframes-cli/`, `gsap/` (+ siblings) | Imported via `npx skills add heygen-com/hyperframes` | Active. **Don't edit** — `npx skills update` to pull upstream changes |
| `heygen-video/` | Imported (`heygen-com/skills`) | Active — generates avatar clips |
| `heygen-avatar/` | Same repo | Installed but unused — we use stock avatar/voice IDs from `.env`, not custom twins |

### Tools (`tools/`)

`scrub.py`, `extract_frames.py`, `render.py`, `script_hash.py`, `verify_render.py`, `zoom.py`, `measure_highlight.py`, `detect_ticks.py`. **Catalog + load-bearing defaults: `tools/README.md`. Full flag docs: `python tools/<name>.py --help`.**

### CLI binaries

- `heygen` (`~/.local/bin/heygen`) — HeyGen API client, auth via `HEYGEN_API_KEY` in `.env`. Used by `heygen-video` skill.
- `npx hyperframes` — Hyperframes CLI: `init / lint / inspect / preview / render / transcribe / tts / doctor`.

---

## File layout

Top-level dirs (full annotated tree: **`references/file-layout.md`**):

- `Parallax Video Plan - MASTER.md`, `CLAUDE.md`, `overhaul.md` — root-level plan + handoff + active-overhaul tracker
- `parallax-obsidian/` — cloned vault (source-of-truth, gitignored)
- `references/` — canonical load-bearing docs (colour-kit, production-principles, value-framing-menu, product-demo-pipeline, file-layout, claude-design-to-hyperframes)
- `learnings/` — user scratch (not pipeline-load-bearing)
- `scripts/` — VO scripts (frontmatter + body)
- `screen recordings/` — raw + scrubbed + zoomed recordings
- `frames/` — scratch stills (cleaned after final ships)
- `templates/<family>/` — Hyperframes compositions per video family (product-demo active; intel-brief shelved)
- `avatars/clips/` — cached HeyGen avatar clips
- `tools/` — deterministic helpers (see `tools/README.md`)
- `decisions/` — dated ADRs + chronological INDEX.md + `_legacy.md`
- `outputs/V<N>/` — per-video `preview.mp4`, `final.mp4`, `render-manifest.json`, `render-history.jsonl`
- `.claude/skills/` — orchestrator + craft skills + imported skills

---

## Where the rules live

Project rules are split across four homes — read the relevant one when working on a phase. Don't duplicate rule substance into CLAUDE.md; this section is a pointer map, not a rule archive.

| Rule type | Home |
|---|---|
| **Portable video-production methodology** (beat sheet upstream, conform-not-compress, never-slow source, framerate consistency, cleanup gate, zoom sized by beat sheet, every claim cites a frame, overlay-ease-matches-camera, clean source segments between annotates, lint-gates-LLM-review, …) | `.claude/skills/video-production-workflow/SKILL.md` Hard Rules #1–#25 + Phases 6a / 6b / 6c |
| **Parallax project decisions** (zoom at Phase 5.5, pragmatic mode, persona-overhaul, NL prompts in demo, Polaris closer, Highlights ownership, …) | `references/production-principles.md` (current-state rules) + `decisions/INDEX.md` (chronological event log — date-stamped, append-only) |
| **Script craft** (voice composite, banned words, hallucination-check enforcement, value-framing rotation, vocabulary lock) | `.claude/skills/video-scriptwriting/SKILL.md` |
| **Per-template format invariants** (layout positions, char/word limits, animation timings, fonts, watermark/avatar positions, locked taglines) | `templates/<family>/RENDER-GUIDE.md` |

When in doubt, search both **Hard Rules** (`video-production-workflow/`) and **Project decisions** (`references/production-principles.md`); cross-refs in both should point at each other and at the script-craft / orchestrator skills where rules are operationally enforced.

---

## Build status

Pipeline tooling, skills, templates, and orchestration are all built and validated. Active production workstream is Phase 7 (V1 canary re-record → I1-I4 instructional → V2-V6 Tier 1 → V7-V13 Tier 2 → V14-V16 Tier 3 hero). `templates/intel-brief/` is shelved. **Current build + production status, pending items, and ship order live in `overhaul.md`.**

---

## If the user asks you to

> **All phase triggers below route through the `parallax-video` skill — invoke it via the Skill tool first.** This table is an index of triggers and which phase they map to, not a substitute for the skill's protocol. Shortcutting to the underlying bash command (e.g. running `tools/scrub.py` directly on a "scrub V5" request) bypasses Phase 3's raw audit, ffprobe verify, frame extract, and per-beat audit — exactly the steps the locked-in rules require. CLAUDE.md is the index; the skill is the protocol.

| Request | Phase / what it triggers |
|---|---|
| **"Lock V5 beats"** / **"Start V5"** | **Phase 1** — autonomous beat-sheet drafting from MASTER.md Highlights (no approval gate per `feedback_beat_sheet_autonomy.md`). Writes back into MASTER.md beneath the Highlights subsection. |
| **"Capture V5"** / **"Record V5"** / **"Auto-record V5"** | **Phase 2 — Automated capture** (optional; manual recording still works). Reads V<N> section in MASTER.md, extracts the `**Prompt to type:**` block to a temp file, then runs `python3 automation/capture.py --slot-dir "screen recordings/V<N>" /tmp/V<N>_prompt.txt`. Capture drives Claude desktop via cliclick, records at 60fps + 1s keyframes (Hard Rule #15), detects end-of-streaming, then runs the post-streaming read-through (scroll chat to top → smooth scroll-down at 300 px/s → auto-trim scroll-up flicker) so the brief read-through is captured for Phase 5.5 freeze-frame annotates. Post-renames `raw.mp4` → `vid<N>_raw.mp4` (archival per Hard Rule #14) AND `trimmed.mp4` → `vid<N>.mp4` (canonical input for Phase 3, scroll-up flicker already removed). Manifest's `phases.streaming_started` is then read by Phase 3 as `T_typing_end` (no frame-sampling needed). **Pre-conditions:** calibrated via `automation/calibrate.py`; Claude desktop in fullscreen. **Manual fallback** still supported — just drop your own `vid<N>.mp4` and Phase 3 frame-samples for boundaries. |
| **"Scrub V5"** / **"Conform V5 recording"** | **Phase 3** — 8 steps: read beat sheet, raw end-to-end audit, ffprobe 60fps + 1s keyframes (Hard Rule #15), `tools/scrub.py` at -45dB, frame extract (folded), per-beat audit, dwell:y decision tree, precise net-of-zoom-inserts report. |
| **"Extract frames for V5"** | **Phase 4** — `tools/extract_frames.py` (1 frame / 2s, 960px). Usually folded into Phase 3 audit. Re-extract after any re-scrub (Hard Rule #12). |
| **"Detect V5 ticks"** / **"find the tick timings"** (any tail-cut treatment) | `python tools/detect_ticks.py "<recording>" --time-range "<t0>:<t1>" --region-pct "x,y,w,h" --expected-ticks N --tail-seconds 1.0 --output <ticks.json>`. Paste `ffmpeg_trim_ranges` into the trim+concat filter graph. **Never eyeball tick timestamps** (Hard Rule #20). |
| **"Write V5"** (use_case) | **Phase 5** — produces a **punchy draft** (fragment-heavy, conservative on rhythm per Hard Rule #6(a)). Reads beat sheet + frames + RENDER-GUIDE + scrub report + `video-scriptwriting` Universal + matching style section. Drafts `scripts/V5 voiceover script.md` + `scripts/V5_zooms.json`. Hallucination check (Hard Rule #7): every on-screen claim cites a frame. **Auto-chains into Phase 6a (polish) on completion.** |
| **"Write I1"** (instructional) | **Phase 5** — instructional style. No persona-and-moment anchoring. Value-framing collapses to hook + close only. Slash commands MAY appear typed (Principle #9 instructional carve-out). |
| **"Write today's intel brief on X"** | **Paused.** Not in the orchestrator. `intel_brief` style is shelved (per `overhaul.md` Phase 5). Reactivation requires a Claude Design session + filling the paused stub in `video-scriptwriting/SKILL.md`. |
| **"Apply V5 zoom"** | **Phase 5.5** — runs *after* script is locked. Calibrates each annotate's highlight via `tools/measure_highlight.py`, runs `tools/zoom.py` → `vid5_zoomed.mp4`. Re-derive LT timings against zoomed file (Hard Rule #12). |
| **"Render V5 preview"** | **Phase 6** — `tools/render.py V5 --mode preview` → `outputs/V5/preview.mp4`. Free, ~2.5min wall. **Auto-chains into Phase 6a (polish) → 6b (lint) → 6c (review) on completion.** |
| **"Polish V5"** / **"Tweak V5"** | **Phase 6a — auto polish pass** (also auto-runs after every Phase 5 + Phase 6). All editorial decisions live here — rhythm + cuts both defer to actual rendered runtime. **Seven steps + backup loop:** (1) sync — frontmatter timings match `tools/zoom.py` segment timing (Hard Rule #12); (2) beat coverage — every spoken beat has a panel/LT/zoom hold, no orphans; (3) runtime check — global spoken VO budget vs speakable window decides step 4 vs step 5; (4) rhythm pass (fits) — restore full sentences in connectives if draft ≥ 60% fragments (target ~40/35/25 mix, Hard Rule #6(b)); **per-beat check:** if polished VO would overflow a beat's zoom hold → step 5b; (5) beat cut (global overflow) — drop lowest-priority beat per MASTER value angles (Hard Rule #6(c)); **(5b) backup loop** — re-open Phase 1: extend beat's target seconds in MASTER.md by `overflow + 0.5s buffer`, update `V<N>_zooms.json`, re-cascade Phase 5.5 → 6 → 6a (Hard Rule #6(d)); fires at most once per beat — second trigger = escalate; (6) LT/panel update — only if a beat was cut OR reordered; (7) auto-re-render preview if any edits applied. Reports "clean" + stops if no changes. **On `clean` → auto-chains into Phase 6b (lint).** Idempotent — converges 1–2 passes (3–4 if backup loop fires). |
| **"Lint V5"** | **Phase 6b — deterministic mechanical lint.** `python tools/lint_video.py V5` — checks every Hard Rule mechanically computable from project artifacts (frontmatter, zooms.json, scrub report, ticks, render manifest, ffprobe). **Tier 1 errors** (L01–L11: timing sync, framerate, safe-zone, z0/z0b sizing, skeleton, panel-hold floor, highlight tier, etc.) STOP the chain → 6c does not run. **Tier 2 warns** (L12–L22: banned-engineering-phrase substring, slash-cmd-in-VO, capability-counts, draft markers) carry through. $0 always. **Auto-runs after every Phase 6a "clean" + after every Phase 9 final render.** |
| **"Review V5"** | **Phase 6c — semantic LLM review.** `python tools/review_video.py V5` via `claude-opus-4-7`. Six checks: **R01** subject-match (spotlight ↔ panel pitch, frame-level), **R02** customer's-chair framing (text), **R03** panel-shape rotation (text), **R04** vault-stat integration (text), **R05** beat content visible in recording (frame), **R06** hallucination check on `frames_used:` (frame, Hard Rule #7). Responses cached at `outputs/V5/.review-cache/`; first run ~$0.25, $0 on re-runs against unchanged input. Writes `outputs/V5/review.md`. Verdicts: pass/drift/fail per rule; chain does NOT auto-stop on findings — surfaces to user for re-open decisions. **Skip:** `--no-review` flag on the upstream render call. **Auto-runs after every Phase 6b tier-1-clean pass.** |
| **"Render V5 final"** | **Phase 9** — `tools/render.py V5 --mode final`. Generates avatar via `heygen-video` (cached at `avatars/clips/V5_<hash>.mp4`), renders to `outputs/V5/final.mp4`. **Only step that costs HeyGen credits.** Use `--dry-run` first. **Auto-chains into Phase 6b → 6c on final.mp4** — same Hard-Rule + semantic check that gated the preview also gates ship; reviewer cache typically hits ($0). |
| **"Clean V5 frames"** | **Phase 11** — `rm -rf frames/V5/` after user confirms final is shippable. Script's `frames_used:` is the durable record. |
| **"Build a Hyperframes template"** | Not in the orchestrator — Claude Design is browser-only. Walk the user through `references/claude-design-to-hyperframes.md`. |
| **"Render failed, debug"** | Not a phase — debug checklist: `.env` loaded? `npx hyperframes lint <template>` clean? Source 60fps with 1s keyframes? RENDER-GUIDE constraints respected? Wallet balance > $0? |

---

## Decisions log (auto-captured)

All new locked-in decisions and rules are date-stamped and archived in `decisions/`. The chronological index + full capture protocol + rule-routing table live in `decisions/INDEX.md` (read that file for trigger phrases, file format, routing logic, and the supersede convention).

**Trigger phrases** — when the user says any of these, capture per `decisions/INDEX.md`:

- "lock this in" / "locked in"
- "decision:" / "we've decided"
- "from now on" / "going forward"
- "don't re-litigate" / "this is settled"
- "remember this" / "log this decision" / "add to decisions"
- "new rule:" / "rule:" / "hard rule" / "principle:"

**Two-step capture (always both):**

1. **Always** create the dated ADR in `decisions/YYYY-MM-DD-<slug>.md` and append a row to `decisions/INDEX.md` (newest at bottom).
2. **Route the rule to its authoritative encoding site** per the routing table in `decisions/INDEX.md`:
   - Portable methodology rule (phasing, ordering, framerate, conform-not-compress, overlay-ease, source-segment cleaning, etc.) → append as the next numbered Hard Rule in `.claude/skills/video-production-workflow/SKILL.md` (`## Hard rules` section, currently #1–#25).
   - Parallax project decision → next numbered Principle in `references/production-principles.md`.
   - Script craft → relevant section in `.claude/skills/video-scriptwriting/SKILL.md`.
   - Per-template invariant → that template's `templates/<family>/RENDER-GUIDE.md`.
   - Unclear → ADR only, then ask where to encode.

Cross-link in both directions (ADR's `Affects:` ↔ encoding site's "Logged: …" suffix). Surface both file paths after capture. When unsure whether a moment counts as a decision, ask.

---

## Legacy decisions (pre-2026-05-15)

Pre-2026-05-15 decisions (Hyperframes-only render path, stock avatar IDs, 62K/48-markets, one template per family, avatar-last, skills-for-judgment) live in their original encoding sites. Index: **`decisions/_legacy.md`**.

---

## Conventions worth preserving

- **Beat sheet first → record → scrub → frames → punchy script → zoom → preview → polish → final.** The beat sheet from MASTER.md is upstream of recording, script, and zoom. Zoom runs after the script (Phase 5.5) so zoom regions can be driven by what the VO names. Phase 5 produces a **punchy draft** (fragment-heavy default); all editorial decisions — rhythm balance, beat cuts — defer to **Phase 6a (polish)** where actual rendered runtime is known. Phase 6a auto-runs after every Phase 5 or Phase 6, with a backup loop into Phase 1 when individual beats need more headroom. Don't let recording length silently dictate script content. Methodology: `video-production-workflow` skill. Hard Rule #6 (a/b/c/d) + Phase 6a.
- **Punchy first, polish second.** At Phase 5 you don't know post-zoom timings yet — write all beats fragment-heavy. At Phase 6a the preview reveals actual breathing room — restore full sentences in connective/interpretive beats. Target mix for use_case after polish: ~40% data-fragment + ~35% short-sentence + ~25% full-sentence. Don't try to balance rhythm at Phase 5 against numbers you don't have.
- **Every beat states value explicitly** — three questions (what is this / what problem / why does it matter to me) answered per beat, with the value-to-viewer as a labeled clause. Pull from the 12-angle menu in `video-scriptwriting/SKILL.md`; rotate angles. Production Principle #8.
- **Every cited stat traces to a source.** Frames for on-screen content, Highlights for stat ownership, vault for grounding.
- **Spoken VO lives under `## Voiceover script`, in `> ` blockquotes.** `tools/script_hash.py` only extracts blockquoted lines from that section, with stage-direction lines (`**[bracketed]**`-only) filtered out.
- **Stage directions use `**[bracketed bold]**`** in scripts — inline and as full-line blocks. The pipeline's VO-extraction conventions assume this format.
- **Polaris closer** for PM/CIO-targeted cuts.
- **60fps everywhere** — re-encode source if keyframes are sparse.
- **Frames are scratch.** Cleaned after final render is approved. Audit trail in script frontmatter.

---

End of CLAUDE.md.

For migration progress: `overhaul.md`
For per-template render rules: `templates/<family>/RENDER-GUIDE.md`
For craft rules: `.claude/skills/video-scriptwriting/SKILL.md`
For master plan: `Parallax Video Plan - MASTER.md`
For Claude Design → Hyperframes lessons: `references/claude-design-to-hyperframes.md`
For product-demo pipeline flowchart: `references/product-demo-pipeline.md`
