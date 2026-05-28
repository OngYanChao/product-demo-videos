# Integration Log

Tracks which findings in this folder have been operationalized into the skills / pipeline, and which are still documented-only. Update whenever a pending item gets integrated, or when new research adds a row.

**Legend:**
- ✅ **Integrated** — rule/finding is encoded in a skill, script, or the pipeline; future sessions will apply it automatically
- ⚠️ **Partial** — implemented in some form but not fully codified
- ❌ **Pending** — documented in a learnings file, not yet in any skill or code path
- 🚫 **Obsolete** — superseded by later pipeline decisions (HeyGen pivot 2026-04-28, Hyperframes-local pivot 2026-04-29, caption removal 2026-05-08)

## Pipeline pivots (timeline)

- **2026-04-28: HeyGen-only pivot** — the local ffmpeg/edge-tts pipeline was retired. Findings specific to it (speed-ramping, edge-tts voice selection) became obsolete.
- **2026-04-29: Hyperframes-local pivot** — HeyGen template rendering retired. Compositions render locally via `npx hyperframes render`; HeyGen is invoked only for the avatar talking-head clip via `tools/render.py --mode final`.
- **2026-05-08: Captions removed** — captions overlapped on-screen brief text during zoom segments. Caption-design research archived at `_archive/caption-design-for-fintech.md`.

---

## From `writing-for-the-ear.md`

| Finding | Status | Where it lives | Notes |
|---|---|---|---|
| Pacing/rhythm guidance (mix short + long sentences) | ✅ | `video-scriptwriting/SKILL.md` → Hard Constraints + Writing for the Ear | Three-shorts-need-a-longer rule is explicit |
| Silence counts; don't pack every second | ✅ | `video-scriptwriting/SKILL.md` → Writing for the Ear | |
| Contractions preferred over formal equivalents | ✅ | `video-scriptwriting/SKILL.md` → Writing for the Ear | |
| Read-aloud test as a rewrite trigger | ✅ | `video-scriptwriting/SKILL.md` → Writing for the Ear | |
| AI-tell transitions to avoid (Furthermore, Moreover, etc.) | ✅ | `video-scriptwriting/SKILL.md` → Hard Constraints | |
| Pacing anchors (130 wpm voice actor / 150–170 wpm AI TTS / 110 wpm edge-tts Christopher) | ✅ | `video-scriptwriting/SKILL.md` → Writing for the Ear + `parallax-video/SKILL.md` → Stage 1 Step 5 worked example | Used by the budget-first workflow |
| First-7-seconds retention importance | ❌ | — | Implicitly respected in V1's 7-word hook, but not formalized as a skill rule |

## From `voiceover-interprets-visuals.md`

| Finding | Status | Where it lives | Notes |
|---|---|---|---|
| "Show on screen, interpret in VO" operating rule | ✅ | `video-scriptwriting/SKILL.md` → Writing for Video (voiceover + visuals) | Top of that section |
| MUD framework (Meaningfulness / Uniqueness / Differentiation) | ✅ | `video-scriptwriting/SKILL.md` → Writing for Video | Cited inline |
| Don't orphan VO from visuals (interpret-while-anchored) | ✅ | `video-scriptwriting/SKILL.md` → Writing for Video | |
| Mute test (would this line have value on mute?) | ✅ | `video-scriptwriting/SKILL.md` → Writing for Video | |
| Before/after examples (description vs interpretation) | ✅ | `video-scriptwriting/SKILL.md` → Writing for Video + Example: Before and After | |
| Every narrated claim must match something on screen | ✅ | `video-scriptwriting/SKILL.md` → Writing for the Ear (last bullet) + Example shows record-first-script-second discipline | |

## ~~From `caption-design-for-fintech.md`~~

Section removed 2026-05-11. Captions were stripped from the product-demo template (2026-05-08) — they overlapped on-screen brief text during zoom segments. The caption-design research is archived at `learnings/_archive/caption-design-for-fintech.md` in case a future template family ever re-introduces captions.

## From `demo-video-format.md`

| Finding | Status | Where it lives | Notes |
|---|---|---|---|
| Live screen recording as the winning format for B2B SaaS proof | ❌ | — | Implicit in the current pipeline (we record + stitch) but not articulated as a rule anywhere |
| Hybrid (live + strategic cutaways) as the dominant 2026 format | ❌ | — | Research-only so far; no implementation |
| Cutaway timing (2–10s per b-roll clip) | ❌ | — | |
| Duration benchmarks (90s–2min for top-of-funnel, up to 3min for deep) | ⚠️ | `parallax-video/SKILL.md` references target lengths per video via the master plan, but the benchmark data isn't surfaced | |
| V1 cutaway treatment proposal (ICIR stat card, optional parallel-call diagram, end card) | ❌ | — | Documented as a proposal in `demo-video-format.md`; not yet in V1's frontmatter or as production assets |
| Pure slide-deck style unsuitable for fintech product proof | ❌ | — | Not encoded as a skill rule; relevant when HeyGen template decision is made |
| Live-dominant PiP as Parallax's canonical format | ❌ | — | Pending HeyGen template shape decision (see HeyGen pivot notes) |

## From `references/production-principles.md`

| Principle | Status | Where it lives | Notes |
|---|---|---|---|
| #1 Never slow the video down | ✅ | `parallax-video/SKILL.md` Hard Rules + `pipeline.py` `build_ramped_video` (rejects multipliers > 1.0) + `finalize_video` (uses `tpad` not `setpts>1`) | |
| #2 Cut beats, not words per beat | ✅ | `video-scriptwriting/SKILL.md` → Quality Check #3 | |
| #3 Use the series to decide which beats to cut | ✅ | `video-scriptwriting/SKILL.md` → Quality Check #4 + `parallax-video/SKILL.md` → Stage 1 Step 2 (cross-video overlap sub-step) | |
| #4 Budget-first workflow | ✅ | `parallax-video/SKILL.md` → Stage 1 Step 5 with worked example | |
| #5 Record first, script second | ✅ | `CLAUDE.md` → Conventions + `parallax-video/SKILL.md` → Stage 1 Step 4 + `extract_frames.py` helper | |
| #6 Hard gate on cleanup — never auto-delete | ✅ | `parallax-video/SKILL.md` → Stage 4 (explicit approval-vs-ambiguity language + never-delete list) | |
| #7 Committable TTS artifact (lock audio once) | ✅ | Superseded — HeyGen avatar clip is cached at `avatars/clips/V<N>_<scripthash>.mp4`. Identical spoken VO never re-bills. `tools/script_hash.py` is the cache key. | |

---

## Summary of pending work

**High priority (blocks other work):**
- Lock in the demo-video-format decisions inside `templates/product-demo/RENDER-GUIDE.md` (cutaway timing, duration benchmarks)

**Lower priority:**
- First-7-seconds retention importance — formalize as a skill rule (or accept that the 7-word V1 hook already encodes it implicitly)
- Duration benchmarks — surface the 90s–2min / up-to-3min numbers in the skill's Stage 1 Step 2 alongside the master-plan reference

**Pending external decisions:**
- HeyGen pivot (whether to replace the local pipeline or keep both)
- Asset hosting for HeyGen

## How to use this log

- When integrating a finding, change its row from ⚠️/❌ to ✅ and add where it landed
- When a new learning gets documented in a learnings file, add a row to this log with its status
- When the skills change substantively, spot-check this log against the actual skill content to catch drift
