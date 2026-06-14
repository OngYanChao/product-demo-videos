---
pipeline_type: product_demo
template: product-demo
video_id: V3
style: use_case
complexity: single_feature
title: "Peer Snapshot Research"
youtube_title: "Stock Peer Comparison for Analyst Briefs"
target_runtime_seconds: 39.02   # 5s title + 27.02s zoomed recording + 7s outro (Rule #30 static path: 3s warp + Rule #27 2s at-top hold + scroll-down + 1s tail buffer)
primary_persona: "Financial analyst (sell-side coverage / buy-side support)"
primary_moment: "Peer snapshot for the brief. Before it goes out."
secondary_personas: ["Head of research (signing off the brief)", "PM (consuming the peer table)"]
recording:
  path: "screen recordings/V3/vid3_zoomed.mp4"   # Phase 5.5 output — canonical timeline
  duration_seconds: 27.02
  scrub_report: "screen recordings/V3/vid3_combined_gapcut_scrub_report.json"
  zooms: "screen recordings/V3/vid3_zooms.json"
  ticks: "screen recordings/V3/vid3_ticks.json"
  scrubbed: "screen recordings/V3/vid3_scrubbed.mp4"
output:
  preview: "outputs/V3/preview.mp4"
  final: "outputs/V3/final.mp4"
avatar_id_override: null
voice_id_override: null

beats:
  title:
    in: 0.0
    out: 5.0
    eyebrow: "V3 · Peer Snapshot Research"
    headline: "The comp table, in one prompt."
  outro:
    duration: 7.0
    wordmark: "Parallax"
    tagline: "Solve the market."

lower_thirds:
  - id: lt1
    in_recording_t: 2.0
    out_recording_t: 9.0
    eyebrow: "V3 · Peer Snapshot Research"
    headline: "Comp table. One prompt. Sixty seconds."
  - id: lt2
    in_recording_t: 0
    out_recording_t: 0
    eyebrow: ""
    headline: ""
  - id: lt3
    in_recording_t: 0
    out_recording_t: 0
    eyebrow: ""
    headline: ""
  - id: lt4
    in_recording_t: 0
    out_recording_t: 0
    eyebrow: ""
    headline: ""

# Annotation panel timings derived from zoom.py "segment timing in zoomed file"
# log after Phase 5.5 runs. Cluster z1a+z1b share panel ap1. z2 has panel ap2.
annotations:
  - id: ap1
    in_recording_t: 11.78      # = start of seg_annotate_01 (z1a)
    out_recording_t: 20.25     # = end of seg_annotate_02 (z1b) — shared panel for cluster (~8.5s)
    callout_number: 1
    panel:
      eyebrow: "PEER SNAPSHOT"
      headline: "Same framework. Every comp."
      body: "Six factor pillars across the comp set. Same definitions, same scoring. Drops cleanly into the brief — no reconciliation."
      source: "Parallax Stock Report · peer-snapshot cut"
      badge: "PEER · COMPOSITE"
  - id: ap2
    in_recording_t: 21.52      # = start of seg_annotate_03 (z2)
    out_recording_t: 25.52     # = end of seg_annotate_03 (4s)
    callout_number: 2
    panel:
      eyebrow: "MODEL SUGGESTION"
      headline: "Buy-list and swap, in one read."
      body: "Top pick + the relative-value swap from one scan."
      source: "Parallax Stock Report · peer-snapshot cut"
      badge: "WORKFLOW · TRADE-READY"
  - id: ap3
    in_recording_t: 0
    out_recording_t: 0
    callout_number: 0

frames_used: [14, 17]   # frame_0014 (at-top freeze) + frame_0017 (Key Takeaways visible)
---

## Voiceover script

> **[0:00–0:10 — Open. z0 follow zoom on chat input box during prompt typing.]**

> Peer snapshot for the brief. Before it goes out.

> The analyst's evening — built by hand from Bloomberg pulls, this takes thirty minutes. One prompt does it in sixty seconds, with the same framework on every name.

> **[0:10–0:27 — Tools fire. z0b follow zoom on Progress sidebar; eight skills run in parallel.]**

> Score, peers, valuation, momentum, financial health. Same six pillars on every comp.

> **[0:27–0:35 — z1 annotate cluster on peer table. z1a spotlights JPM row (Total 2.8). z1b spotlights Citigroup row (Total 9.0).]**

> JPM at two-eight. Bottom of the cluster on the composite.

> Citi pops at nine. The model's outlier.

> **[0:35–0:45 — z2 annotate on "Top pick by model: Citigroup" + "Model suggestion vs JPM: swap to BAC" in Key Takeaways.]**

> The interesting spread is on Value and Quality — that's where JPM's premium multiple isn't supported.

> The model's call: Citi for the buy-list, BAC for the relative-value swap.

> **[0:45–0:53 — Close beat. Camera at full frame; brief read-through completing.]**

> Peer table. One prompt. Sixty seconds. Ready for the brief.

## Annotation panel content

> **ap1 (z1a + z1b shared panel — peer table cluster)**
> - **eyebrow:** PEER SNAPSHOT
> - **headline:** Same framework. Every comp.
> - **body:** Six factor pillars applied identically across the comp set. The table actually integrates — same definitions, same data feeds, same scoring. Bloomberg pulls don't. That's why the peer view drops cleanly into the analyst's brief instead of needing reconciliation.
> - **source:** Parallax Stock Report · peer-snapshot cut
> - **badge:** PEER · COMPOSITE

> **ap2 (z2 — top pick line)**
> - **eyebrow:** MODEL SUGGESTION
> - **headline:** Buy-list and swap, in one read.
> - **body:** The peer scan returns both the top-of-cluster name (Citi at 9.0) and the closest-match swap candidate for the underweight position (BAC for JPM). Two trade ideas surfaced from the same six-pillar comparison the analyst was already going to do.
> - **source:** Parallax Stock Report · peer-snapshot cut
> - **badge:** WORKFLOW · TRADE-READY

## Hallucination check (frame audit trail)

Every on-screen claim cites a frame from `frames/V3/`:

- "JPM at two-eight" — frame 14 (0:26, freeze on peer table; row 1 = JPM, Total column = 2.8)
- "Citi pops at nine" — frame 14 (row 4 = C, Total = 9.0)
- "JPM's premium multiple isn't supported" — frame 17 (0:32, Key Takeaways visible: "JPM trades at 14.2x P/E vs peer median ~12.5x — a ~14% premium")
- "Citi for the buy-list, BAC for the relative-value swap" — frame 17 (Key Takeaways: "Top pick by model: Citigroup (C) at 9.0" + "Model suggestion vs JPM: swap to BAC")

All four cited stats trace to visible content in the captured recording. No hallucinations.
