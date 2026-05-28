# File layout

Full annotated tree of the Parallax video production repo. Relocated from CLAUDE.md 2026-05-22 — kept out of always-loaded context to keep CLAUDE.md compact. Refresh when top-level dirs change.

```
cowork plugin videos/
├── CLAUDE.md                              ← project handoff context
├── .env                                   ← HEYGEN_API_KEY + HEYGEN_AVATAR_ID + HEYGEN_VOICE_ID (gitignored)
├── .env.example                           ← template for env vars
├── overhaul.md                            ← active-overhaul tracker + build status
│
├── Parallax Video Plan - MASTER.md        ← 20 video specs (Phase 3 draft section) + Highlights + vault stats library
├── V0 Install Research — 4 Clients.md     ← V0-specific research
├── Parallax Plugin — Workflow Reference.md ← reference for plugin workflows
├── Archetype 1 - The Contrarian.mp4       ← sample manually-produced video (separate from this pipeline)
│
├── parallax-obsidian/                     ← cloned source-of-truth vault (gitignored)
│
├── references/                            ← canonical load-bearing reference docs (pipeline reads these)
│   ├── colour-kit.md                      ← Chicago Global brand colour system
│   ├── value-framing-menu.md              ← 12-angle value-framing vocabulary (consumed by MASTER + scriptwriting + parallax-video skills + CLAUDE)
│   ├── production-principles.md           ← locked production rules (#1–#13); cross-ref to where each is encoded
│   ├── product-demo-pipeline.md           ← visual flowchart of the 11 production phases
│   ├── file-layout.md                     ← this file
│   └── claude-design-to-hyperframes.md    ← Claude Design → Hyperframes template-authoring checklist
│
├── learnings/                             ← user scratch / staging (NOT pipeline-load-bearing)
│   ├── INTEGRATION_LOG.md, README.md
│   ├── writing-for-the-ear.md             ← craft research (already distilled into video-scriptwriting skill)
│   ├── voiceover-interprets-visuals.md    ← craft research (already distilled into video-scriptwriting skill)
│   ├── demo-video-format.md               ← format research
│   └── _archive/caption-design-for-fintech.md  ← obsolete (captions removed 2026-05-08)
│
├── scripts/                               ← VO scripts (markdown with frontmatter + body)
│   ├── V<N> voiceover script.md
│   └── V<N> voiceover script (legacy ...).md  ← archived legacy versions
│
├── screen recordings/                     ← raw + scrubbed + zoomed recordings
│   ├── <vidname>.mp4                      ← raw screen capture (any name)
│   ├── <vidname>_scrubbed.mp4             ← tools/scrub.py output (Phase 3)
│   ├── <vidname>_scrub_report.json
│   └── <vidname>_zoomed.mp4               ← tools/zoom.py output (Phase 5.5,
│                                            script-derived). Canonical input
│                                            to render.
│
├── frames/                                ← scratch — extracted stills, deleted after final ships
│   └── V<N>/
│       ├── frame_NNNN.jpg
│       └── index.md
│
├── templates/                             ← Hyperframes compositions (one per video family)
│   ├── product-demo/
│   │   ├── index.html                     ← Hyperframes composition (60fps, 1920×1080)
│   │   ├── RENDER-GUIDE.md                ← format invariants for this template
│   │   ├── DESIGN.md, README.md           ← Claude Design exports
│   │   ├── assets/screen-recording.mp4    ← gets swapped per video by render.py
│   │   ├── renders/
│   │   │   ├── template-reference.mp4     ← canonical "what this template produces" sample (regenerate on template changes)
│   │   │   └── <name>_<ts>.mp4            ← throwaway test renders during template work
│   │   └── uploads/                       ← Claude Design uploads
│   └── intel-brief/                       ← ⏸ shelved (deferred future addition)
│
├── avatars/                               ← persistent avatar config + per-video clip cache
│   └── clips/
│       └── V<N>_<scripthash>.mp4          ← cached HeyGen avatar clips
│
├── tools/                                 ← deterministic helpers (callable from cron / orchestrator)
│   ├── README.md                          ← per-tool table with flags + defaults
│   ├── scrub.py
│   ├── extract_frames.py
│   ├── render.py                          ← preview + final modes
│   ├── script_hash.py
│   ├── verify_render.py
│   ├── zoom.py
│   ├── measure_highlight.py
│   └── detect_ticks.py
│
├── decisions/                             ← dated ADRs + chronological index
│   ├── INDEX.md                           ← capture protocol + rule-routing table
│   ├── _legacy.md                         ← pre-2026-05-15 decisions
│   └── YYYY-MM-DD-<slug>.md               ← one ADR per locked-in decision
│
├── outputs/                               ← canonical per-video deliverables
│   └── V<N>/
│       ├── preview.mp4                    ← latest preview (no avatar, free)
│       ├── preview-prev.mp4               ← one render back, for comparison / rollback
│       ├── final.mp4                      ← latest final (with avatar, costs credits)
│       ├── final-prev.mp4                 ← one render back
│       ├── render-manifest.json           ← latest run's metadata
│       └── render-history.jsonl           ← append-only log: one JSON per render, full timeline
│
└── .claude/
    └── skills/
        ├── parallax-video/                ← orchestrator (handles V<N> + I<N> dispatch)
        ├── video-scriptwriting/           ← craft rules (active)
        ├── video-production-workflow/     ← portable methodology (active)
        ├── heygen-skills/                 ← cloned heygen-com/skills repo
        ├── heygen-avatar, heygen-video    ← symlinks for Claude Code discovery
        ├── hyperframes, hyperframes-cli, gsap, ...  ← imported via npx skills add
        └── (other auto-installed siblings)
```
