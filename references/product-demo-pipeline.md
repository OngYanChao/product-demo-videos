# Product Demo Video Pipeline

Visual reference for the master-plan product-demo stream — **20 videos total: 4 instructional (I1–I4) + 16 use_case (V1–V16)** organized around `primary_persona × primary_moment × deliverable`. Each video walks through a Parallax workflow: screen recording + avatar PiP + lower-thirds, rendered locally via Hyperframes with HeyGen billed only for the avatar clip. (Legacy 28-video plan archived to `_archive/MASTER-pre-overhaul-2026-05-11.md` on 2026-05-13.)

The intel-brief stream is **shelved as a deferred future addition** (per `overhaul.md` Phase 5) — infrastructure stays in place but no current videos. For the prose version of these phases (with command examples and decision trees), see `CLAUDE.md` → "Daily workflow per video".

---

## Phase flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: LOCK BEATS         "start V<N>" / "lock V<N> beats"       │
│                                                                     │
│  Read MASTER.md V<N> → draft beat sheet (target sec/beat,           │
│  dwell:y flags) → write back into MASTER.md (no approval gate)      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 2: RECORD                  (manual — user screen-captures)   │
│                                                                     │
│  screen recordings/V<N>/vidN.mp4   (60fps, keyframes ≤1s)           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 3: SCRUB ONLY        (zoom deferred to Phase 5.5)            │
│                                                                     │
│   python tools/scrub.py "screen recordings/V<N>/vidN.mp4"           │
│        → vidN_scrubbed.mp4 + vidN_scrub_report.json                 │
│                                                                     │
│   Decision tree per beat:                                           │
│     too long + dead loading  → scrub                                │
│     too long + content motion → 1.5–2× uniform speedup              │
│     too short + dwell:y      → defer to Phase 5.5 (script-driven    │
│                                  zoom — region needs the VO first)  │
│     too short + non-dwell    → re-record (escalate to user)         │
│                                                                     │
│   Slowdown (any form — uniform, ramp, pre-zoom) is BANNED.          │
│   Hard Rule #13: deceleration creates rubber-banding stutter and    │
│   slowed motion reads as syrupy. Stretch via held-still or zoom.    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 4: EXTRACT FRAMES                                            │
│                                                                     │
│   python tools/extract_frames.py vidN_scrubbed.mp4 frames/V<N>/     │
│        → 30-ish JPGs + index.md (frame # ↔ timestamp)               │
│                                                                     │
│   Audit: every locked beat's content visible in at least 1 frame    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 5: WRITE SCRIPT             "write V<N>"                     │
│                                                                     │
│   Inputs:  beat sheet + frames + MASTER Highlights                  │
│          + RENDER-GUIDE + scrub report                              │
│          + video-scriptwriting craft skill                          │
│                                                                     │
│   Outputs: scripts/V<N> voiceover script.md                         │
│            frames_used: <audit trail in frontmatter>                │
│            scripts/V<N>_zooms.json  (one zoom per dwell:y beat;     │
│              region = bounding box of what VO names;                │
│              duration = beat's locked seconds)                      │
│                                                                     │
│   Rules: every claim cites frame|MASTER|vault — no hallucination    │
│          every beat answers what/problem/why-it-matters             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 5.5: APPLY ZOOM      "zoom V<N>" / "apply V<N> zoom"         │
│                                                                     │
│   python tools/measure_highlight.py  (per annotate directive)      │
│        → paste emitted highlight_region_pct JSON into V<N>_zooms    │
│                                                                     │
│   python tools/zoom.py vidN_scrubbed.mp4 \                          │
│                        --zooms scripts/V<N>_zooms.json \            │
│                        -o vidN_zoomed.mp4                           │
│        → vidN_zoomed.mp4  (canonical timeline for Phase 6+)         │
│                                                                     │
│   Re-derive LT/caption timings against vidN_zoomed.mp4              │
│   per Hard Rule #12 in video-production-workflow.                   │
│                                                                     │
│   If zoom design fails (no settled visual on a dwell:y beat,        │
│   or VO names content not in the scrubbed recording): re-record.    │
│   Don't paper over with an arbitrary region.                        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 6: PREVIEW RENDER ($0)      "render V<N> preview"            │
│                                                                     │
│   Local Hyperframes against vidN_zoomed.mp4                         │
│        → outputs/V<N>/preview.mp4                                   │
│   Avatar slot = placeholder. Iterate freely.                        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                       ◄──── iterate ────►  (back to Phase 5, 5.5, or 6 — all $0)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 7: APPROVE PREVIEW         (user sign-off)                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 8: FINAL RENDER ($$)        "render V<N> final"              │
│                                                                     │
│   heygen-video → avatars/clips/V<N>_<scripthash>.mp4  (cached)      │
│   Hyperframes re-render with avatar slot filled                     │
│   → outputs/V<N>/final.mp4                                          │
│                                                                     │
│   ⚠ Only billable step in the entire pipeline                       │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 9: CLEANUP             (after user approves final)           │
│                                                                     │
│   rm -rf frames/V<N>/   ← user must OK; audit lives in frontmatter  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Cost & cache model

```
   Phase 1–7   ════════════════════════════════════════  $0 (iterate freely)
   Phase 8     ████████████████  HeyGen credits  ← cached by script hash
                                                  same script body → no rebill
```

Avatar clips are keyed by hash of the script's blockquoted VO body (see `tools/script_hash.py`). Layout, timing, frontmatter, and stage-direction edits don't invalidate the cache — only changes to the spoken words do.

---

## Source-of-truth map

```
   MASTER.md ─────────► Highlights = locked stat ownership (no reuse within stream)
                        Beat sheet = upstream of both recording AND script

   parallax-obsidian/ ─► vault grounding (skip 06-Investor-Letters, 07-Reference-Library)

   templates/<family>/RENDER-GUIDE.md ─► format invariants (timings, char limits, tagline)

   frames/V<N>/ ──────► SCRATCH — deleted after final ships
                        Durable record = frames_used: in script frontmatter
```

---

## Hard rules (don't violate silently)

- Beat sheet is upstream — conform the recording to it, never the reverse
- Every on-screen claim cites a frame; every stat traces to MASTER / vault / source
- Annotate highlights: always `tools/measure_highlight.py`, never hand-tune `highlight_region_pct`
- Zoom duration = beat duration; ≥1.5s held-still pause between consecutive zooms
- 60fps source + render everywhere; sparse keyframes break Hyperframes seeks
- Polaris closer (`"This isn't a backtest…"`) only for PM/CIO cuts; default tagline is `"Solve the market."`

---

## Intel-brief stream (for contrast)

Same Phase 5–8 shape, but no recording → no scrub, no zoom, no frame extraction. Stats trace to the source document and `parallax-obsidian/` vault instead of frames.

```
   Source doc           parallax-obsidian/          last 5 intel briefs
   (newsletter,         (stat library,              (dedup filter —
    market data)         methodology, voice)         cross-stream reuse OK)
        │                       │                           │
        └───────────┬───────────┴───────────────┬───────────┘
                    ▼                           ▼
        ┌───────────────────────────────────────────────────┐
        │  WRITE BRIEF       "write today's intel brief…"   │
        │  → scripts/intel-brief-<date>.md   (~150–225 wds) │
        └───────────────────────────────────────────────────┘
                              │
                              ▼
        ┌───────────────────────────────────────────────────┐
        │  PREVIEW → FINAL   (same Phase 6→8 as Stream A,   │
        │                    templates/intel-brief/ ⏳ TBD)  │
        └───────────────────────────────────────────────────┘
```

---

## Pipeline status

All daily-loop phases (1, 2, 3 scrub, 4 frames, 5 script, 5.5 zoom, 6 preview, 7 approve, 8 final, 9 cleanup) are built and validated as of 2026-05-15. The remaining open workstream is **production** under the persona-and-moment overhaul (see `overhaul.md`) — starting with the V1 re-record canary, then I1–I4 instructional, then V2–V6 Tier-1, V7–V13 Tier-2, V14–V16 Tier-3.