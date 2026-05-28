# 2026-05-21 — Detect Ticks Programmatically (Tail-Cut Technique)

**Status:** active
**Affects:** `tools/detect_ticks.py` (new), `.claude/skills/video-production-workflow/SKILL.md` (Hard Rule #20 added), `.claude/skills/parallax-video/SKILL.md` (dispatch row added for "detect V<N> ticks"), `CLAUDE.md` (tools table + trigger-phrase table updated)

## Decision

When a Phase 5.5 zoom segment uses the tail-cut technique to compress a long progress-bar / status-checklist loading sequence (keep ±N seconds around each visual "tick" event, jump-cut the dead waits between), the tick timestamps that center each kept clip must come from `tools/detect_ticks.py` — never from sampling frames at 1s intervals and eyeballing.

Tool: `tools/detect_ticks.py`. Samples frames at high fps (default 30) in a configurable sub-region, computes frame-to-frame mean absolute pixel diff, returns top-N peaks with non-maximum suppression. Outputs JSON with precise tick timestamps + ready-to-paste `ffmpeg_trim_ranges` (tail_start:tail_end) for the trim+concat filter graph.

Usage pattern:
```bash
python tools/detect_ticks.py "<recording>" \
    --time-range "<t0>:<t1>" \
    --region-pct "x,y,w,h" \
    --expected-ticks N \
    --tail-seconds 1.0 \
    --output <ticks.json>
```

## Why

V1.2's loading-segment treatment used the tail-cut technique: zoom into the Progress sidebar, keep ±1s of source playback around each checkmark tick, jump-cut between. With 3 ticks × 2s clips = 6s of zoom-hold content. The eyeballed tick timestamps (T1≈27.5, T2+T3≈34.7, T4≈39.0) were sampled at 1s intervals — which gives ±1s precision. User flagged: *"the second + third check together had a longer waiting time after the first check as compared to the fourth check after the second + third check."*

Investigation: the actual ticks (via frame-diff at 30fps) were T1=27.033, T2+T3=34.700, T4=38.167. In the eyeballed cut:
- Clip 1 (26.5–28.5): true T1 fires at 0.53s into the clip → 0.53s pre-tick wait, 1.47s post-tick hold
- Clip 2 (33.7–35.7): true T2+T3 fires at 1.00s → symmetric (lucky)
- Clip 3 (38.0–40.0): true T4 fires at 0.17s → 0.17s pre-tick wait, 1.83s post-tick hold

The asymmetric pre-tick wait times are exactly what the viewer reads as "the third tick fires immediately, the others wait" — even though every clip is the same 2s length. Programmatic detection placed each tick at precisely 1.0s into its 2s clip, restoring perceived symmetry.

User feedback: *"wait you estimated? bad claude. dont be lazy, write code and codify it just like how we did for the loading segment cutting technique."* (See `feedback_underline_calibration.md`, `feedback_video_pipeline_pitfalls.md` — "measured, not eyeballed" is a recurring discipline in this project.)

## Notes

- **Simultaneous ticks count as ONE moment.** V1.2 has steps 2 + 3 ticking at the same instant — that's one peak in the frame-diff signal, not two. Set `--expected-ticks` to the number of distinct *moments*, not lines.
- **Magnitude varies by line length.** A tick on a long text line ("Pulling factor scores, financials & analyst data") produces a larger pixel diff than a tick on a short line ("Explain extreme factor scores"). If true ticks have very different magnitudes, request more peaks than expected and discard the lowest-magnitude noise from the result. For V1.2, requesting 6 peaks captured all 4 real events (sidebar load, step 1 active, T1, T2+T3, T4) plus 2 noise peaks.
- **Region sizing matters.** Narrow `--region-pct` to just the area where ticks happen — wider regions pick up cursor motion, chat-thread updates, etc. as false positives. For V1.2 the sidebar occupies source x=80-100%, y=0-30%, hence `--region-pct "80,0,20,30"`.
- **Output is a durable artifact.** Save to `screen recordings/V<N>/<vidname>_ticks.json` (analogous to `<vidname>_scrub_report.json`). Re-run if the source recording is re-scrubbed or re-encoded (timestamps shift).
- **Companion to existing measurement tools** (`measure_underline.py` Hard Rule #10, `measure_highlight.py` for annotate mode). Same discipline: any visual coordinate or timestamp that affects what the viewer sees must come from the file's actual pixels, not from sampled-and-rounded estimates.
- V1.2 application: tail-cut ffmpeg filter rebuilt from `26.5/28.5 → 33.7/35.7 → 38.0/40.0` (eyeballed) to `26.033/28.033 → 33.700/35.700 → 37.167/39.167` (detected). Output file: `1vid_zoomed_route2v2_tickcut.mp4`. Each tick now lands at 1.000s into its 2s clip — symmetric pre-tick wait across all three.
