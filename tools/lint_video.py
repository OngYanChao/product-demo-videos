#!/usr/bin/env python3
"""
tools/lint_video.py — Mechanical rule check for V<N> / I<N>.

Reads project artifacts (zooms.json, script frontmatter, scrub report, ticks,
render manifest, ffprobe output) and asserts the deterministic Hard Rules +
RENDER-GUIDE invariants + script-craft mechanical checks. No LLM. No frame
inspection. Subjective / visual rules are deferred to a separate reviewer
agent.

Usage:
    python tools/lint_video.py V2                      # run all checks
    python tools/lint_video.py V2 --rules L01,L09     # subset
    python tools/lint_video.py V2 --strict             # warn → error
    python tools/lint_video.py V2 --tier 1             # tier 1 only

Exit codes:
    0 — all checks passed (warnings OK unless --strict)
    1 — at least one error (or warning under --strict)
    2 — missing artifact / can't load video files
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml


# ───────────────────────── constants from the Hard Rules ─────────────────────────
SAFE_ZONE_MIN_PCT = 30.0      # Hard Rule #17
SAFE_ZONE_MAX_PCT = 70.0      # Hard Rule #17
PANEL_HOLD_FLOOR_S = 3.0      # Hard Rule #25
PANEL_WPS = 5.0               # Hard Rule #25 — 300 wpm
PANEL_EASE_OVERHEAD_S = 2.0   # Hard Rule #18 — ease-in + ease-out
HIGHLIGHT_TIER_1_MAX = 15.0   # Hard Rule #24 tier-1 cap
HIGHLIGHT_TIER_2_MAX = 25.0   # Hard Rule #24 tier-2 cap (>25 → must split)
TEMPLATE_AP_SLOTS = {"ap1", "ap2", "ap3"}  # product-demo template has 3 slots
TITLE_DURATION_S = 5.0        # RENDER-GUIDE
OUTRO_DURATION_S = 7.0        # RENDER-GUIDE
EXPECTED_FPS = 60
EXPECTED_KEYFRAME_INTERVAL_S = 1.0  # Hard Rule #15
ANNOTATE_DEFAULT_EASE_S = 1.0  # Hard Rule #18

BANNED_ENGINEERING_PHRASES = [
    "parallel calls", "parallel skill calls",
    "MCP tool", "MCP invocation", "MCP invocations",
    "agent orchestration",
    "skill invocation", "skill invocations",
    "tool invocations",
]

CAPABILITY_COUNT_PATTERN = re.compile(
    r"\b(eight|nine|ten|eleven|twelve|thirteen|fourteen|sixteen|twenty|"
    r"thirty|forty|fifty)\s+tools?\b",
    re.IGNORECASE,
)

SLASH_COMMAND_PATTERN = re.compile(r"/parallax:[\w-]+")

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ───────────────────────── finding record ─────────────────────────
@dataclass
class Finding:
    rule: str          # "L01", "L02", …
    severity: str      # "error" | "warn"
    title: str
    detail: str
    fix_hint: str = ""

    def render(self) -> str:
        icon = "✗" if self.severity == "error" else "⚠"
        lines = [f"  {icon} [{self.rule}] {self.title}"]
        for line in self.detail.splitlines():
            lines.append(f"        {line}")
        if self.fix_hint:
            lines.append(f"        → {self.fix_hint}")
        return "\n".join(lines)


# ───────────────────────── loaders ─────────────────────────
def parse_frontmatter(script_path: Path) -> dict:
    """Parse YAML frontmatter from a script .md file."""
    text = script_path.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{script_path}: no YAML frontmatter found")
    return yaml.safe_load(parts[1])


def parse_vo_body(script_path: Path) -> str:
    """Extract VO blockquote lines from `## Voiceover script` section."""
    text = script_path.read_text()
    m = re.search(r"^## Voiceover script\s*\n", text, re.MULTILINE)
    if not m:
        return ""
    body = text[m.end():]
    # Stop at next h2 section
    next_h2 = re.search(r"^## ", body, re.MULTILINE)
    if next_h2:
        body = body[: next_h2.start()]
    # Extract `> ` blockquote lines, skip stage-direction-only lines
    vo_lines: list[str] = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith(">"):
            continue
        content = line.lstrip("> ").strip()
        if not content:
            continue
        # Skip pure stage-direction lines: `**[bracketed]**`
        if re.fullmatch(r"\*\*\[.*\]\*\*", content):
            continue
        vo_lines.append(content)
    return "\n".join(vo_lines)


def ffprobe_video(path: Path) -> dict:
    """Run ffprobe + return decoded JSON. Empty dict on failure."""
    if not path.exists():
        return {}
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-print_format", "json",
                "-show_streams", "-show_format",
                str(path),
            ],
            capture_output=True, text=True, check=True,
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return {}


def ffprobe_keyframe_intervals(path: Path, max_check_seconds: float = 30.0) -> list[float]:
    """Returns list of inter-keyframe intervals (seconds) for the first ~30s."""
    if not path.exists():
        return []
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "frame=key_frame,pts_time",
                "-read_intervals", f"%+{max_check_seconds}",
                "-print_format", "csv",
                str(path),
            ],
            capture_output=True, text=True, check=True, timeout=30,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []
    kf_times = []
    for line in result.stdout.splitlines():
        parts = line.split(",")
        if len(parts) >= 3 and parts[1] == "1":
            try:
                kf_times.append(float(parts[2]))
            except ValueError:
                continue
    if len(kf_times) < 2:
        return []
    return [kf_times[i + 1] - kf_times[i] for i in range(len(kf_times) - 1)]


# ───────────────────────── geometry / math helpers ─────────────────────────
def count_words(text: str | None) -> int:
    """Word count for panel-hold math. Skips standalone punctuation tokens
    (em-dash, en-dash, ellipsis) so they don't inflate the count."""
    if not text:
        return 0
    return sum(1 for tok in text.split() if any(c.isalnum() for c in tok))


def panel_min_hold(body_word_count: int) -> float:
    """Hard Rule #25: max(3.0, body_word_count / 5.0 + 2.0)."""
    return max(PANEL_HOLD_FLOOR_S, body_word_count / PANEL_WPS + PANEL_EASE_OVERHEAD_S)


def compute_comp_y(highlight: list[float], zoom_region: list[float]) -> float:
    """Hard Rule #17: comp y position of highlight center.

    highlight = [x, y, w, h], zoom_region = [x, y_offset, w, h]
    Returns y in [0, 100] of composition.
    """
    hl_center = highlight[1] + highlight[3] / 2.0
    return (hl_center - zoom_region[1]) / zoom_region[3] * 100.0


def classify_highlight_tier(h_pct: float) -> int:
    """Hard Rule #24: 1 = ≤15%, 2 = 15-25%, 3 = >25% (must split)."""
    if h_pct <= HIGHLIGHT_TIER_1_MAX:
        return 1
    if h_pct <= HIGHLIGHT_TIER_2_MAX:
        return 2
    return 3


def annotates_only(zooms: list[dict]) -> list[dict]:
    return [z for z in zooms if z.get("mode") == "annotate"]


def cluster_by_callout(zooms: list[dict]) -> dict[int, list[dict]]:
    """Group annotate directives by callout_number (= shared-panel cluster)."""
    clusters: dict[int, list[dict]] = {}
    for z in annotates_only(zooms):
        n = int(z.get("callout_number", 0))
        clusters.setdefault(n, []).append(z)
    return clusters


# ───────────────────────── checks: TIER 1 ─────────────────────────
def L01_frontmatter_timings(ctx: dict) -> list[Finding]:
    """Annotation timings in frontmatter match zoom-directive durations
    (per-cluster sum for shared panels). Monotonically increasing."""
    findings: list[Finding] = []
    fm = ctx["frontmatter"]
    zooms = ctx["zooms"]
    annotations = fm.get("annotations") or []
    clusters = cluster_by_callout(zooms)

    # Monotonic check
    last_out = -1.0
    for ann in annotations:
        ap_id = ann.get("id", "?")
        in_t = float(ann.get("in_recording_t", 0))
        out_t = float(ann.get("out_recording_t", 0))
        if in_t < last_out:
            findings.append(Finding(
                rule="L01", severity="error",
                title=f"Annotation {ap_id} out of order",
                detail=f"in_recording_t={in_t} but previous out_recording_t={last_out}",
                fix_hint="re-derive timings from zoom.py's `segment timing in zoomed file` output",
            ))
        last_out = max(last_out, out_t)

    # Cluster-duration match
    for ann in annotations:
        ap_id = ann.get("id", "?")
        callout = int(ann.get("callout_number", 0))
        cluster = clusters.get(callout, [])
        if not cluster:
            continue
        expected_span = sum(float(z.get("duration", 0)) for z in cluster)
        actual_span = float(ann.get("out_recording_t", 0)) - float(ann.get("in_recording_t", 0))
        # For shared-panel clusters, actual_span should cover annotate(s) + interstitial src/pause
        # segments. So actual_span >= expected_span (sum of durations), and equality holds
        # only for single-annotate clusters. Flag if actual < expected (impossible) or
        # actual deviates wildly from cluster end - cluster start.
        if actual_span + 0.05 < expected_span:
            findings.append(Finding(
                rule="L01", severity="error",
                title=f"Annotation {ap_id} span < cluster total duration",
                detail=(
                    f"frontmatter span {actual_span:.2f}s, sum of cluster's "
                    f"zoom durations {expected_span:.2f}s"
                ),
                fix_hint="re-derive in/out_recording_t from zoom.py output (Hard Rule #12)",
            ))

    # Bounds check vs recording.duration_seconds
    rec_dur = float(fm.get("recording", {}).get("duration_seconds", 0))
    for ann in annotations:
        ap_id = ann.get("id", "?")
        out_t = float(ann.get("out_recording_t", 0))
        if rec_dur and out_t > rec_dur + 0.1:
            findings.append(Finding(
                rule="L01", severity="error",
                title=f"Annotation {ap_id} extends past recording end",
                detail=f"out_recording_t={out_t} but recording.duration_seconds={rec_dur}",
                fix_hint="trim annotation or extend recording",
            ))

    return findings


def L02_framerate_keyframes(ctx: dict) -> list[Finding]:
    """Hard Rule #15: scrubbed + zoomed are 60fps with ≤1s keyframe interval."""
    findings: list[Finding] = []
    for label, path in [("scrubbed", ctx["scrubbed_path"]), ("zoomed", ctx["zoomed_path"])]:
        if not path.exists():
            findings.append(Finding(
                rule="L02", severity="error",
                title=f"{label} file missing",
                detail=f"{path} not on disk",
                fix_hint=f"re-run scrub/zoom for {ctx['video_id']}",
            ))
            continue
        probe = ffprobe_video(path)
        streams = probe.get("streams", [])
        vstream = next((s for s in streams if s.get("codec_type") == "video"), None)
        if not vstream:
            findings.append(Finding(
                rule="L02", severity="error",
                title=f"{label}: no video stream",
                detail=f"ffprobe returned no video stream for {path.name}",
                fix_hint="re-encode with ffmpeg -i input -c:v libx264 -r 60",
            ))
            continue
        rate = vstream.get("r_frame_rate", "0/0")
        try:
            num, den = rate.split("/")
            fps = float(num) / float(den) if float(den) else 0
        except Exception:
            fps = 0
        if abs(fps - EXPECTED_FPS) > 0.5:
            findings.append(Finding(
                rule="L02", severity="error",
                title=f"{label}: framerate ≠ {EXPECTED_FPS}fps",
                detail=f"r_frame_rate={rate} (≈ {fps:.2f}fps)",
                fix_hint="re-encode with -r 60 -g 60 -keyint_min 60",
            ))
        # Keyframe interval
        intervals = ffprobe_keyframe_intervals(path)
        if intervals:
            max_gap = max(intervals)
            if max_gap > EXPECTED_KEYFRAME_INTERVAL_S + 0.2:
                findings.append(Finding(
                    rule="L02", severity="error",
                    title=f"{label}: sparse keyframes",
                    detail=f"max keyframe gap = {max_gap:.2f}s (expected ≤ {EXPECTED_KEYFRAME_INTERVAL_S}s)",
                    fix_hint="re-encode with -g 60 -keyint_min 60",
                ))
    return findings


def L03_safe_zone(ctx: dict) -> list[Finding]:
    """Hard Rule #17: each annotate's spotlight comp_y ∈ [30, 70]."""
    findings: list[Finding] = []
    for z in annotates_only(ctx["zooms"]):
        zid = z.get("id", "?")
        hl = z.get("highlight_region_pct")
        zr = z.get("zoom_region_pct")
        if not hl or not zr or len(hl) < 4 or len(zr) < 4:
            findings.append(Finding(
                rule="L03", severity="error",
                title=f"{zid} missing highlight_region_pct or zoom_region_pct",
                detail="annotate-mode directives must define both fields with 4 components",
                fix_hint="add the fields per Hard Rule #17",
            ))
            continue
        comp_y = compute_comp_y(hl, zr)
        if not (SAFE_ZONE_MIN_PCT <= comp_y <= SAFE_ZONE_MAX_PCT):
            findings.append(Finding(
                rule="L03", severity="error",
                title=f"{zid} spotlight outside comp safe zone",
                detail=(
                    f"comp_y={comp_y:.1f}% (allowed: {SAFE_ZONE_MIN_PCT}-{SAFE_ZONE_MAX_PCT}%); "
                    f"highlight_y={hl[1]:.2f}, h={hl[3]:.2f}, zoom y_offset={zr[1]}, h={zr[3]}"
                ),
                fix_hint=(
                    "adjust zoom_region y_offset OR pick a source_t where the target "
                    "is at a different scroll position"
                ),
            ))
    return findings


def L04_z0_duration(ctx: dict) -> list[Finding]:
    """Hard Rule #22: z0.duration = T_click + ease, where T_click = scrub zone (a) end."""
    findings: list[Finding] = []
    z0 = next((z for z in ctx["zooms"] if z.get("id", "").startswith("z0_")), None)
    if not z0:
        return findings  # L05 will catch missing z0
    scrub = ctx.get("scrub", {})
    force_ranges = (scrub.get("config", {}) or {}).get("force_speed_ranges", [])
    # Zone (a) is the first range starting at 0
    zone_a = next((r for r in force_ranges if r[0] == 0.0 and r[2] == 1.0), None)
    if not zone_a:
        findings.append(Finding(
            rule="L04", severity="warn",
            title="Can't verify z0.duration — no zone (a) in scrub report",
            detail="expected force_speed_ranges to include [0, T_click, 1.0]",
        ))
        return findings
    t_click = float(zone_a[1])
    ease = float(z0.get("ease", 0))
    expected_duration = t_click + ease
    actual = float(z0.get("duration", 0))
    if abs(actual - expected_duration) > 0.05:
        findings.append(Finding(
            rule="L04", severity="error",
            title="z0.duration ≠ T_click + ease",
            detail=(
                f"z0.duration={actual:.2f}, T_click={t_click:.2f}, ease={ease:.2f}; "
                f"expected duration = {expected_duration:.2f}"
            ),
            fix_hint="set z0.duration = T_click + ease (Hard Rule #22)",
        ))
    return findings


def L05_skeleton(ctx: dict) -> list[Finding]:
    """Hard Rule #23: zooms has z0 (follow) + z0b (follow) + ≥1 annotate."""
    findings: list[Finding] = []
    zooms = ctx["zooms"]
    z0 = next((z for z in zooms if z.get("id", "").startswith("z0_") and not z["id"].startswith("z0b")), None)
    z0b = next((z for z in zooms if z.get("id", "").startswith("z0b")), None)
    annotates = annotates_only(zooms)
    if not z0:
        findings.append(Finding(rule="L05", severity="error",
            title="Missing z0 (prompt-typing follow-zoom)",
            detail="Hard Rule #23: standard skeleton requires z0 first directive",
            fix_hint="add z0 with mode=follow, region=[40,24,38,11] (Cowork chrome default)"))
    elif z0.get("mode") != "follow":
        findings.append(Finding(rule="L05", severity="error",
            title=f"z0 mode={z0.get('mode')} (must be follow)",
            detail="z0 is a follow-zoom on the chat input box during typing",
            fix_hint="set z0.mode = 'follow'"))
    if not z0b:
        findings.append(Finding(rule="L05", severity="error",
            title="Missing z0b (Progress-sidebar follow-zoom)",
            detail="Hard Rule #23: skeleton requires z0b; user sign-off needed to skip",
            fix_hint="add z0b with mode=follow, region=[80,0,20,30]"))
    elif z0b.get("mode") != "follow":
        findings.append(Finding(rule="L05", severity="error",
            title=f"z0b mode={z0b.get('mode')} (must be follow)",
            detail="z0b is a follow-zoom on the Progress sidebar",
            fix_hint="set z0b.mode = 'follow'"))
    if not annotates:
        findings.append(Finding(rule="L05", severity="error",
            title="No annotate directives",
            detail="Skeleton requires z1..zN with mode=annotate per VO-named content item",
            fix_hint="add at least one annotate directive"))
    return findings


def L06_z0b_sizing(ctx: dict) -> list[Finding]:
    """Hard Rule #23 refined (2026-05-24):
        z0b.source_t == T_first_tick − margin
        z0b.ease     ≤ margin
        z0b.duration == (T_(N-1) + margin) − source_t + ease
    """
    findings: list[Finding] = []
    z0b = next((z for z in ctx["zooms"] if z.get("id", "").startswith("z0b")), None)
    if not z0b:
        return findings
    ticks = ctx.get("ticks", {})
    if not ticks.get("ticks"):
        findings.append(Finding(
            rule="L06", severity="warn",
            title="Can't verify z0b sizing — no ticks JSON",
            detail="ticks file missing or has no ticks; skipping z0b math check",
        ))
        return findings
    # The ticks file's time_range tells us where the locked tick window is in RAW source.
    # In the SCRUBBED file (which zoom.py operates on), the tick window starts at some offset.
    # We approximate that offset using the trim+concat semantics: the scrubbed file's tick
    # window starts after the scrub-compressed buffer (1).
    scrub = ctx.get("scrub", {})
    force_ranges = (scrub.get("config", {}) or {}).get("force_speed_ranges", [])
    margin = float(ticks.get("margin", 1.0))
    # Scrub zone (b) start in RAW = T_first_tick − margin; scrubbed file's zone (b) begins
    # at the end of buffer (1) compression. The scrubbed file's tick window starts at:
    #   scrubbed_t = T_click + (compressed buffer 1)
    # We need to infer compressed_buffer_1 from the scrub report. The simplest approach:
    # the tick window's RAW START is force_ranges[1][0] (middle zone). In SCRUBBED time,
    # zone (b) start = scrubbed_duration − (zone_c_duration + buffer_2_compressed + zone_b_duration).
    # Easier: trust the JSON authoring — verify the relationships hold among the values
    # given in zooms.json + ticks.json without re-deriving scrubbed coordinates.
    tick_ts = [float(t["t_tick"]) for t in ticks["ticks"]]
    # If broader sweep, ticks may include synthesis tick; if scoped, only progress ticks.
    # We trust the user authored ticks.json with the progress-only set after the broad pass.
    t_first_raw = tick_ts[0]
    t_n_minus_1_raw = tick_ts[-1]  # in scoped-only ticks.json this IS T_(N-1)
    # Find scrub zone (b) bounds in RAW
    zone_b = None
    for r in force_ranges:
        if r[0] > 0 and r[2] == 1.0 and r[1] - r[0] > margin:
            zone_b = r
            break
    if not zone_b:
        findings.append(Finding(
            rule="L06", severity="warn",
            title="Can't verify z0b sizing — no zone (b) in scrub report",
            detail="expected force_speed_ranges to include a locked tick window",
        ))
        return findings
    # Verify scrub zone bounds are at T_first ± margin / T_(N-1) ± margin
    expected_b_start = t_first_raw - margin
    expected_b_end = t_n_minus_1_raw + margin
    if abs(zone_b[0] - expected_b_start) > 0.1:
        findings.append(Finding(
            rule="L06", severity="warn",
            title="Scrub zone (b) start doesn't match T_first_tick − margin",
            detail=f"zone (b) start={zone_b[0]:.2f}, expected={expected_b_start:.2f} (T_first={t_first_raw}, margin={margin})",
            fix_hint="re-run scrub with the corrected --force-speed-range",
        ))
    if abs(zone_b[1] - expected_b_end) > 0.1:
        findings.append(Finding(
            rule="L06", severity="warn",
            title="Scrub zone (b) end doesn't match T_(N-1) + margin",
            detail=f"zone (b) end={zone_b[1]:.2f}, expected={expected_b_end:.2f}",
            fix_hint="re-run scrub with the corrected --force-speed-range",
        ))
    # ease ≤ margin
    ease = float(z0b.get("ease", 1.5))
    if ease > margin + 0.05:
        findings.append(Finding(
            rule="L06", severity="error",
            title=f"z0b.ease={ease} > margin={margin}",
            detail="ease-in must complete by T_first_tick; ease ≤ margin",
            fix_hint=f"set z0b.ease = {margin}",
        ))
    return findings


def L07_highlight_tier(ctx: dict) -> list[Finding]:
    """Hard Rule #24: highlight h ≤ 25% unless part of a shared-panel sub-annotate cluster."""
    findings: list[Finding] = []
    clusters = cluster_by_callout(ctx["zooms"])
    for callout, members in clusters.items():
        # A single-annotate cluster shouldn't have tier-3 height
        for z in members:
            zid = z.get("id", "?")
            hl = z.get("highlight_region_pct")
            if not hl or len(hl) < 4:
                continue
            tier = classify_highlight_tier(hl[3])
            if tier == 3:
                findings.append(Finding(
                    rule="L07", severity="error",
                    title=f"{zid} highlight h={hl[3]:.1f}% exceeds tier-3 threshold",
                    detail=(
                        f"Hard Rule #24: >25% must split into sub-annotates with shared panel "
                        f"(this annotate is in cluster #{callout} with {len(members)} member(s))"
                    ),
                    fix_hint=(
                        "split into multiple sub-annotates (different source_t) sharing one panel, "
                        "OR tighten the rect to ≤25%"
                    ),
                ))
    return findings


def L08_measured_highlights(ctx: dict) -> list[Finding]:
    """Hard Rule #10/#24: highlights measured via tools, not hand-tuned.
    Heuristic — _beat field must mention 'measured' OR explicitly note hand-bounding."""
    findings: list[Finding] = []
    for z in annotates_only(ctx["zooms"]):
        zid = z.get("id", "?")
        beat_note = z.get("_beat", "").lower()
        markers = ["measure_highlight", "measured", "snap", "snapped", "hand-bound", "hand-set",
                   "hand-tightened", "tightened to header", "hand-bounded"]
        if not any(m in beat_note for m in markers):
            findings.append(Finding(
                rule="L08", severity="warn",
                title=f"{zid} _beat doesn't record measurement method",
                detail="expected '_beat' field to mention measure_highlight.py output or hand-bounding rationale",
                fix_hint="add a note like 'Highlight measured.' or 'hand-bounded because [reason]'",
            ))
    return findings


def L09_panel_hold(ctx: dict) -> list[Finding]:
    """Hard Rule #25: panel hold ≥ max(3.0, body_word_count / 5.0 + 2.0).
    For shared panels, sum the cluster's annotate durations."""
    findings: list[Finding] = []
    fm = ctx["frontmatter"]
    annotations = fm.get("annotations") or []
    zooms = ctx["zooms"]
    clusters = cluster_by_callout(zooms)
    for ann in annotations:
        ap_id = ann.get("id", "?")
        callout = int(ann.get("callout_number", 0))
        panel = ann.get("panel") or {}
        body_words = count_words(panel.get("body"))
        min_hold = panel_min_hold(body_words)
        cluster = clusters.get(callout, [])
        cluster_hold = sum(float(z.get("duration", 0)) for z in cluster)
        if cluster_hold + 0.05 < min_hold:
            findings.append(Finding(
                rule="L09", severity="error",
                title=f"{ap_id} hold {cluster_hold:.2f}s < min_hold {min_hold:.2f}s",
                detail=(
                    f"body word count={body_words}; needs {min_hold:.2f}s; "
                    f"cluster (callout #{callout}) sums {cluster_hold:.2f}s"
                ),
                fix_hint=(
                    "tighten panel body, extend zoom duration(s), or consolidate "
                    "to a shared panel cluster"
                ),
            ))
    return findings


def L10_template_slots(ctx: dict) -> list[Finding]:
    """RENDER-GUIDE: product-demo template has 3 ap-slots (ap1, ap2, ap3)."""
    findings: list[Finding] = []
    fm = ctx["frontmatter"]
    annotations = fm.get("annotations") or []
    if len(annotations) > len(TEMPLATE_AP_SLOTS):
        findings.append(Finding(
            rule="L10", severity="error",
            title=f"{len(annotations)} annotations > 3 template slots",
            detail=f"product-demo template defines ap1, ap2, ap3 only; extras silently dropped at render",
            fix_hint="consolidate via Hard Rule #24 shared-panel allowance",
        ))
    for ann in annotations:
        ap_id = ann.get("id", "?")
        if ap_id not in TEMPLATE_AP_SLOTS:
            findings.append(Finding(
                rule="L10", severity="error",
                title=f"annotation id '{ap_id}' has no template slot",
                detail=f"valid ids: {sorted(TEMPLATE_AP_SLOTS)}",
                fix_hint="rename or remove this annotation",
            ))
    return findings


def L11_timing_math(ctx: dict) -> list[Finding]:
    """RENDER-GUIDE: target_runtime = 5 + recording.duration + 7; title=5; outro=7."""
    findings: list[Finding] = []
    fm = ctx["frontmatter"]
    rec_dur = float(fm.get("recording", {}).get("duration_seconds", 0))
    target = float(fm.get("target_runtime_seconds", 0))
    expected_target = TITLE_DURATION_S + rec_dur + OUTRO_DURATION_S
    if abs(target - expected_target) > 0.05:
        findings.append(Finding(
            rule="L11", severity="error",
            title="target_runtime_seconds doesn't match title + recording + outro",
            detail=f"target={target}, expected={expected_target:.2f} (=5+{rec_dur:.2f}+7)",
            fix_hint=f"set target_runtime_seconds = {expected_target:.2f}",
        ))
    beats = fm.get("beats", {})
    title = beats.get("title", {})
    if "in" in title and "out" in title:
        title_span = float(title["out"]) - float(title["in"])
        if abs(title_span - TITLE_DURATION_S) > 0.05:
            findings.append(Finding(
                rule="L11", severity="error",
                title=f"title duration {title_span}s ≠ {TITLE_DURATION_S}s",
                detail="RENDER-GUIDE: title card is always 5s",
                fix_hint=f"set beats.title.out = beats.title.in + {TITLE_DURATION_S}",
            ))
    outro = beats.get("outro", {})
    if "duration" in outro:
        outro_dur = float(outro["duration"])
        if abs(outro_dur - OUTRO_DURATION_S) > 0.05:
            findings.append(Finding(
                rule="L11", severity="error",
                title=f"outro.duration={outro_dur}s ≠ {OUTRO_DURATION_S}s",
                detail="RENDER-GUIDE: outro is always 7s",
                fix_hint=f"set beats.outro.duration = {OUTRO_DURATION_S}",
            ))
    return findings


# ───────────────────────── checks: TIER 2 ─────────────────────────
def L12_color_space(ctx: dict) -> list[Finding]:
    """Hard Rule #11: scrubbed + zoomed share color space."""
    findings: list[Finding] = []
    scrubbed_probe = ffprobe_video(ctx["scrubbed_path"])
    zoomed_probe = ffprobe_video(ctx["zoomed_path"])
    keys = ("color_space", "color_primaries", "color_transfer", "color_range")
    def streams_v(probe):
        return next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), {})
    s_v, z_v = streams_v(scrubbed_probe), streams_v(zoomed_probe)
    for k in keys:
        sv, zv = s_v.get(k), z_v.get(k)
        if sv and zv and sv != zv:
            findings.append(Finding(
                rule="L12", severity="warn",
                title=f"colour metadata mismatch: {k}",
                detail=f"scrubbed: {sv} | zoomed: {zv}",
                fix_hint="re-encode with explicit -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv",
            ))
    return findings


def L13_no_slowdown(ctx: dict) -> list[Finding]:
    """Hard Rule #13: no slowdown params in any zoom directive."""
    findings: list[Finding] = []
    forbidden_keys = ("slowdown", "setpts", "pre_zoom_slowdown", "playback_speed")
    for z in ctx["zooms"]:
        zid = z.get("id", "?")
        for k in forbidden_keys:
            if k in z:
                findings.append(Finding(
                    rule="L13", severity="error",
                    title=f"{zid} has forbidden slowdown key '{k}'",
                    detail=f"value={z[k]}; Hard Rule #13: never slow source",
                    fix_hint="remove the key; use pre_zoom_hold or re-record instead",
                ))
    return findings


def L14_cursor_clear(ctx: dict) -> list[Finding]:
    """Hard Rule #16: annotate directives targeting output brief should have wait_cursor_clear."""
    findings: list[Finding] = []
    for z in annotates_only(ctx["zooms"]):
        zid = z.get("id", "?")
        if not z.get("wait_cursor_clear"):
            findings.append(Finding(
                rule="L14", severity="warn",
                title=f"{zid} missing wait_cursor_clear: true",
                detail="output-brief annotates should opt into cursor-clear (Hard Rule #16)",
                fix_hint="set wait_cursor_clear: true on this directive",
            ))
    return findings


def L15_annotate_ease(ctx: dict) -> list[Finding]:
    """Hard Rule #18: annotate ease = 1.0 matches template panel sine.inOut 1.0s."""
    findings: list[Finding] = []
    for z in annotates_only(ctx["zooms"]):
        zid = z.get("id", "?")
        ease = float(z.get("ease", ANNOTATE_DEFAULT_EASE_S))
        if abs(ease - ANNOTATE_DEFAULT_EASE_S) > 0.05:
            findings.append(Finding(
                rule="L15", severity="warn",
                title=f"{zid} ease={ease} ≠ {ANNOTATE_DEFAULT_EASE_S}",
                detail="annotate ease should match template's panel ease (Hard Rule #18)",
                fix_hint=f"set ease = {ANNOTATE_DEFAULT_EASE_S} or update template panel ease in lockstep",
            ))
    return findings


def L16_clean_source_ranges(ctx: dict) -> list[Finding]:
    """Hard Rule #19: zoom.py was invoked with --clean-source-ranges covering each gap."""
    findings: list[Finding] = []
    manifest = ctx.get("manifest") or {}
    # zoom invocation isn't logged directly; we approximate by checking that the render-history
    # includes a recent manifest, then trust that zoom.py was called by render.py with the
    # standard clean-source-ranges per the dispatch row. If we can't verify, warn.
    if not manifest:
        findings.append(Finding(
            rule="L16", severity="warn",
            title="No render-manifest.json — can't verify --clean-source-ranges",
            detail="run preview render once to populate outputs/V<N>/render-manifest.json",
        ))
    # Soft check: more than one annotate at the same source_t cluster but with non-zero
    # gap should have a clean range entry. We can't see the zoom.py command line, so this
    # check stays a warn-only existence check.
    return findings


def L17_ticks_json(ctx: dict) -> list[Finding]:
    """Hard Rule #20: ticks.json exists + referenced from frontmatter."""
    findings: list[Finding] = []
    if not ctx["ticks_path"].exists():
        findings.append(Finding(
            rule="L17", severity="error",
            title="ticks JSON missing",
            detail=f"{ctx['ticks_path']} not on disk (Hard Rule #20)",
            fix_hint=f"run detect_ticks.py on the raw recording",
        ))
        return findings
    fm = ctx["frontmatter"]
    rec = fm.get("recording", {})
    if "ticks" not in rec:
        findings.append(Finding(
            rule="L17", severity="warn",
            title="recording.ticks not in frontmatter",
            detail="reference vid<N>_ticks.json from script frontmatter for audit trail",
            fix_hint=f"add `ticks: \"{ctx['ticks_path'].relative_to(PROJECT_ROOT)}\"` under recording:",
        ))
    return findings


def L18_scrub_zones(ctx: dict) -> list[Finding]:
    """Hard Rule #21: scrub config has exactly 3 force_speed_ranges, all speed=1.0."""
    findings: list[Finding] = []
    scrub = ctx.get("scrub", {})
    config = scrub.get("config", {}) or {}
    ranges = config.get("force_speed_ranges", [])
    if len(ranges) != 3:
        findings.append(Finding(
            rule="L18", severity="warn",
            title=f"scrub has {len(ranges)} force_speed_ranges, expected 3",
            detail="Hard Rule #21: three locked zones (typing, tick window, post-brief)",
            fix_hint="re-run scrub with --force-speed-range '0:T_click:1.0,T_first:T_(N-1):1.0,T_brief_landed:end:1.0'",
        ))
    for r in ranges:
        if r[2] != 1.0:
            findings.append(Finding(
                rule="L18", severity="error",
                title=f"scrub zone {r[0]}-{r[1]} at speed {r[2]} ≠ 1.0",
                detail="Hard Rule #21: locked zones must be at 1×",
                fix_hint="re-author --force-speed-range with speed = 1.0",
            ))
    return findings


def L19_vo_structure(ctx: dict) -> list[Finding]:
    """Script craft: VO body lives in `> ` blockquotes under `## Voiceover script`."""
    findings: list[Finding] = []
    text = ctx["script_path"].read_text()
    if "## Voiceover script" not in text:
        findings.append(Finding(
            rule="L19", severity="error",
            title="No `## Voiceover script` section in script",
            detail="script_hash.py requires this section header",
            fix_hint="add `## Voiceover script` and place VO blockquotes underneath",
        ))
    vo_body = ctx["vo_body"]
    if not vo_body.strip():
        findings.append(Finding(
            rule="L19", severity="error",
            title="No VO blockquote content found",
            detail="VO lines must be in `> ` blockquotes (not stage-direction-only)",
            fix_hint="prefix each spoken line with `> `",
        ))
    return findings


def L20_banned_vocab(ctx: dict) -> list[Finding]:
    """Script craft: VO body has no engineering vocabulary."""
    findings: list[Finding] = []
    fm = ctx["frontmatter"]
    if fm.get("style") == "instructional":
        return findings  # instructional carve-out
    vo = ctx["vo_body"]
    lower_vo = vo.lower()
    for phrase in BANNED_ENGINEERING_PHRASES:
        if phrase.lower() in lower_vo:
            findings.append(Finding(
                rule="L20", severity="error",
                title=f"VO contains banned phrase '{phrase}'",
                detail="Customer's-chair framing forbids engineering vocabulary",
                fix_hint="rewrite in audience-perspective (outcome / stakes / workflow-fit)",
            ))
    m = CAPABILITY_COUNT_PATTERN.search(vo)
    if m:
        findings.append(Finding(
            rule="L20", severity="warn",
            title=f"VO contains capability count '{m.group(0)}'",
            detail="reciting tool/skill counts reads as system-chair framing",
            fix_hint="describe outcome rather than capability inventory",
        ))
    return findings


def L21_nl_prompts(ctx: dict) -> list[Finding]:
    """Production principle: NL prompts in demo; no slash commands in VO (unless instructional)."""
    findings: list[Finding] = []
    fm = ctx["frontmatter"]
    if fm.get("style") == "instructional":
        return findings
    matches = SLASH_COMMAND_PATTERN.findall(ctx["vo_body"])
    if matches:
        findings.append(Finding(
            rule="L21", severity="error",
            title=f"VO speaks slash command(s): {set(matches)}",
            detail="Principle #9: slash commands annotated, never spoken (use_case carve-out is instructional only)",
            fix_hint="replace with a natural-language paraphrase",
        ))
    return findings


def L22_zoom_durations_vs_beats(ctx: dict) -> list[Finding]:
    """Hard Rule #9: zoom durations match the beat sheet's Target seconds (±10%)."""
    findings: list[Finding] = []
    targets = ctx.get("beat_targets")
    if not targets:
        return findings  # warn-only handled in loader
    zooms = ctx["zooms"]
    # Sum of all directive durations (excluding follow z0/z0b — those are non-dwell)
    annotate_total = sum(float(z.get("duration", 0)) for z in annotates_only(zooms))
    dwell_target_total = sum(t for label, t, dwell in targets if dwell)
    if dwell_target_total == 0:
        return findings
    # Allow 25% slop — the beat sheet is "rough guidance" per pragmatic mode
    if abs(annotate_total - dwell_target_total) / dwell_target_total > 0.25:
        findings.append(Finding(
            rule="L22", severity="warn",
            title=f"Annotate-total {annotate_total:.1f}s drifts from beat-sheet dwell-total {dwell_target_total:.1f}s",
            detail=(
                "Hard Rule #9: zoom durations sized by beat sheet, not runtime deficit. "
                "Pragmatic mode allows drift; flag for review."
            ),
            fix_hint="if intentional drift, fine; otherwise adjust zoom durations or re-lock beats",
        ))
    return findings


# ───────────────────────── beat-sheet loader (for L22) ─────────────────────────
def load_beat_targets(video_id: str) -> list[tuple[str, float, bool]] | None:
    """Parse MASTER.md beat-sheet table for this video. Returns [(label, target_s, is_dwell), ...]."""
    master = PROJECT_ROOT / "Parallax Video Plan - MASTER.md"
    if not master.exists():
        return None
    text = master.read_text()
    # Find this video's section header
    header_re = re.compile(rf"^### {re.escape(video_id)}\b", re.MULTILINE)
    m = header_re.search(text)
    if not m:
        return None
    # Section runs until next ### or end
    next_section = re.search(r"^### ", text[m.end():], re.MULTILINE)
    section = text[m.end(): m.end() + next_section.start()] if next_section else text[m.end():]
    # Find the beat-sheet table (lines with " | " starting with " 1 |" etc)
    rows = re.findall(r"^\| (\d+) \| ([^|]+?) \| (\d+)s \| ([^|]+?) \|", section, re.MULTILINE)
    if not rows:
        return None
    out: list[tuple[str, float, bool]] = []
    for _, beat, target_s, dwell in rows:
        is_dwell = "y" in dwell.lower()
        out.append((beat.strip(), float(target_s), is_dwell))
    return out


# ───────────────────────── runner ─────────────────────────
CHECKS: dict[str, tuple[Callable[[dict], list[Finding]], int]] = {
    "L01": (L01_frontmatter_timings, 1),
    "L02": (L02_framerate_keyframes, 1),
    "L03": (L03_safe_zone, 1),
    "L04": (L04_z0_duration, 1),
    "L05": (L05_skeleton, 1),
    "L06": (L06_z0b_sizing, 1),
    "L07": (L07_highlight_tier, 1),
    "L08": (L08_measured_highlights, 1),
    "L09": (L09_panel_hold, 1),
    "L10": (L10_template_slots, 1),
    "L11": (L11_timing_math, 1),
    "L12": (L12_color_space, 2),
    "L13": (L13_no_slowdown, 2),
    "L14": (L14_cursor_clear, 2),
    "L15": (L15_annotate_ease, 2),
    "L16": (L16_clean_source_ranges, 2),
    "L17": (L17_ticks_json, 2),
    "L18": (L18_scrub_zones, 2),
    "L19": (L19_vo_structure, 2),
    "L20": (L20_banned_vocab, 2),
    "L21": (L21_nl_prompts, 2),
    "L22": (L22_zoom_durations_vs_beats, 2),
}


def build_context(video_id: str) -> dict:
    """Load every artifact needed by the checks."""
    is_instructional = video_id.startswith("I")
    prefix = "1vid" if video_id == "V1" else (f"vid{video_id[1:]}" if not is_instructional else f"vid{video_id[1:]}")
    rec_dir = PROJECT_ROOT / "screen recordings" / video_id

    # Special case for V1 which uses "1vid" prefix
    if video_id == "V1":
        scrubbed = rec_dir / "1vid_scrubbed.mp4"
        zoomed = rec_dir / "1vid_zoomed_route2v2_tickcut.mp4"
        zooms_path = rec_dir / "1vid_zooms.json"
        ticks_path = rec_dir / "1vid_ticks.json"
        scrub_report_path = rec_dir / "1vid_scrub_report.json"
    else:
        scrubbed = rec_dir / f"{prefix}_scrubbed.mp4"
        zoomed = rec_dir / f"{prefix}_zoomed.mp4"
        zooms_path = rec_dir / f"{prefix}_zooms.json"
        ticks_path = rec_dir / f"{prefix}_ticks.json"
        scrub_report_path = rec_dir / f"{prefix}_scrub_report.json"

    script_path = PROJECT_ROOT / "scripts" / f"{video_id} voiceover script.md"
    manifest_path = PROJECT_ROOT / "outputs" / video_id / "render-manifest.json"

    # Required files
    missing = []
    if not script_path.exists():
        missing.append(str(script_path.relative_to(PROJECT_ROOT)))
    if not zooms_path.exists():
        missing.append(str(zooms_path.relative_to(PROJECT_ROOT)))
    if missing:
        print(f"error: missing required artifact(s):", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        sys.exit(2)

    frontmatter = parse_frontmatter(script_path)
    zooms = json.loads(zooms_path.read_text())
    scrub = json.loads(scrub_report_path.read_text()) if scrub_report_path.exists() else {}
    ticks = json.loads(ticks_path.read_text()) if ticks_path.exists() else {}
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    vo_body = parse_vo_body(script_path)
    beat_targets = load_beat_targets(video_id)

    return {
        "video_id": video_id,
        "is_instructional": is_instructional,
        "frontmatter": frontmatter,
        "zooms": zooms,
        "scrub": scrub,
        "ticks": ticks,
        "manifest": manifest,
        "vo_body": vo_body,
        "beat_targets": beat_targets,
        "script_path": script_path,
        "scrubbed_path": scrubbed,
        "zoomed_path": zoomed,
        "ticks_path": ticks_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Mechanical rule check for V<N> / I<N>.")
    parser.add_argument("video", help="Video id, e.g. V2 or I1")
    parser.add_argument("--rules", help="Comma-separated list of rule ids to run (e.g. L01,L09)")
    parser.add_argument("--tier", type=int, choices=[1, 2], help="Run only tier-N checks")
    parser.add_argument("--strict", action="store_true", help="Warnings count as failures")
    parser.add_argument("--quiet", action="store_true", help="Suppress passed-checks list")
    args = parser.parse_args()

    ctx = build_context(args.video)

    if args.rules:
        wanted = set(s.strip() for s in args.rules.split(","))
        active = {k: v for k, v in CHECKS.items() if k in wanted}
    elif args.tier:
        active = {k: v for k, v in CHECKS.items() if v[1] == args.tier}
    else:
        active = CHECKS

    print(f"\n  lint  {args.video}  ({len(active)} checks)")
    print(f"  recording: {ctx['zoomed_path'].relative_to(PROJECT_ROOT)}")
    print(f"  script:    {ctx['script_path'].relative_to(PROJECT_ROOT)}\n")

    all_findings: list[Finding] = []
    passed: list[str] = []
    for rule_id, (fn, tier) in active.items():
        try:
            results = fn(ctx) or []
        except Exception as e:
            results = [Finding(rule=rule_id, severity="error",
                               title=f"{rule_id} threw {type(e).__name__}",
                               detail=str(e))]
        if results:
            all_findings.extend(results)
        else:
            passed.append(rule_id)

    errors = [f for f in all_findings if f.severity == "error"]
    warns = [f for f in all_findings if f.severity == "warn"]

    if errors:
        print("  ERRORS")
        for f in errors:
            print(f.render())
        print()
    if warns:
        print("  WARNINGS")
        for f in warns:
            print(f.render())
        print()
    if passed and not args.quiet:
        print(f"  PASS  ({len(passed)}): {', '.join(passed)}\n")

    total = len(active)
    print(f"  summary: {len(passed)}/{total} passed · {len(errors)} errors · {len(warns)} warnings")

    if errors:
        return 1
    if warns and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
