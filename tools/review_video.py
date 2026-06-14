#!/usr/bin/env python3
"""
tools/review_video.py — Vision-based semantic review for V<N> / I<N>.

Companion to tools/lint_video.py. The linter catches mechanical/structural
failures (panel-hold math, safe-zone calc, framerate, sync drift). This
reviewer catches the semantic failures the linter can't:

  R01 — Subject-match     (frame): does the spotlit area visually match the panel's pitch?
  R02 — Customer's-chair  (text):  is panel copy in audience-perspective, not system-perspective?
  R03 — Panel rotation    (text):  do panels follow the 3-shape (capability/workflow/stakes) rotation?
  R04 — Vault-stats       (text):  are stats integrated into output moments, not narrated standalone?
  R05 — Beat content      (frame): does each dwell beat's frame visibly contain the claimed content?
  R06 — Hallucination     (frame): does each frames_used cite match its frame?

Uses claude-opus-4-7 via the Anthropic SDK. Caches LLM responses by content
hash so re-runs are free if nothing changed. Output: outputs/V<N>/review.md.

Usage:
    python tools/review_video.py V2
    python tools/review_video.py V2 --checks R01,R02      # subset
    python tools/review_video.py V2 --no-cache            # force re-run
    python tools/review_video.py V2 --model claude-sonnet-4-6   # cheaper model
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import anthropic
import yaml
from pydantic import BaseModel, Field


# ───────────────────────── constants ─────────────────────────
DEFAULT_MODEL = "claude-opus-4-7"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Opus 4.7 pricing (USD per 1M tokens)
PRICING = {
    "claude-opus-4-7":   {"input": 5.00,  "output": 25.00, "cache_read": 0.50, "cache_write": 6.25},
    "claude-sonnet-4-6": {"input": 3.00,  "output": 15.00, "cache_read": 0.30, "cache_write": 3.75},
    "claude-haiku-4-5":  {"input": 1.00,  "output":  5.00, "cache_read": 0.10, "cache_write": 1.25},
}


# ───────────────────────── verdict models (Pydantic) ─────────────────────────
class SubjectMatchVerdict(BaseModel):
    result: Literal["pass", "drift", "fail"]
    reasoning: str
    spotlit_content_description: str = Field(description="What's visually bright/in-focus in the frame")
    panel_pitch_description: str = Field(description="What the paired panel's eyebrow+headline+body pitches")


class FramingFinding(BaseModel):
    field: Literal["eyebrow", "headline", "body"]
    problem: str
    suggested_rewrite: str


class FramingVerdict(BaseModel):
    result: Literal["pass", "fail"]
    findings: list[FramingFinding] = Field(default_factory=list)


class PanelShape(BaseModel):
    panel_id: str
    shape: Literal["capability", "workflow", "stakes"]
    rationale: str


class RotationVerdict(BaseModel):
    result: Literal["pass", "fail"]
    shapes: list[PanelShape]
    consecutive_violations: list[str] = Field(default_factory=list, description="Pairs of consecutive panels with the same shape")


class VaultStatsViolation(BaseModel):
    quoted_line: str
    problem: str


class VaultStatsVerdict(BaseModel):
    result: Literal["pass", "fail"]
    violations: list[VaultStatsViolation] = Field(default_factory=list)


class BeatContentVerdict(BaseModel):
    result: Literal["pass", "fail"]
    reasoning: str
    beat_name: str
    visible_content_summary: str = Field(description="What's actually visible in the frame")


class HallucinationVerdict(BaseModel):
    result: Literal["pass", "fail"]
    reasoning: str
    cite_text: str
    frame_visible_content: str


# ───────────────────────── env loading ─────────────────────────
def load_env():
    """Parse .env file and set ANTHROPIC_API_KEY (and any other vars) in os.environ
    if not already set."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


# ───────────────────────── data loaders ─────────────────────────
def parse_frontmatter(script_path: Path) -> dict:
    text = script_path.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{script_path}: no YAML frontmatter found")
    return yaml.safe_load(parts[1])


def parse_vo_body(script_path: Path) -> str:
    text = script_path.read_text()
    m = re.search(r"^## Voiceover script\s*\n", text, re.MULTILINE)
    if not m:
        return ""
    body = text[m.end():]
    next_h2 = re.search(r"^## ", body, re.MULTILINE)
    if next_h2:
        body = body[: next_h2.start()]
    lines: list[str] = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith(">"):
            continue
        content = line.lstrip("> ").strip()
        if not content:
            continue
        if re.fullmatch(r"\*\*\[.*\]\*\*", content):
            continue
        lines.append(content)
    return "\n".join(lines)


def parse_master_beats(video_id: str) -> list[dict] | None:
    """Parse the V<N> beat-sheet table from MASTER.md.
    Returns [{ '#': '1', 'beat': '...', 'target_s': 10, 'dwell': True, 'content': '...' }, ...]."""
    master = PROJECT_ROOT / "Parallax Video Plan - MASTER.md"
    if not master.exists():
        return None
    text = master.read_text()
    header_re = re.compile(rf"^### {re.escape(video_id)}\b", re.MULTILINE)
    m = header_re.search(text)
    if not m:
        return None
    next_section = re.search(r"^### ", text[m.end():], re.MULTILINE)
    section = text[m.end(): m.end() + next_section.start()] if next_section else text[m.end():]
    rows = re.findall(r"^\| (\d+) \| ([^|]+?) \| (\d+)s \| ([^|]+?) \| ([^|]+?) \|", section, re.MULTILINE)
    out = []
    for num, beat, target_s, dwell, content in rows:
        out.append({
            "number": int(num),
            "beat": beat.strip(),
            "target_s": int(target_s),
            "dwell": "y" in dwell.lower(),
            "content": content.strip(),
        })
    return out


# ───────────────────────── frame extraction ─────────────────────────
def extract_frame(video_path: Path, source_t: float, output_path: Path,
                  scale_width: int = 960) -> bytes:
    """Extract a single frame at source_t. Cache: skip ffmpeg if output already exists."""
    if output_path.exists():
        return output_path.read_bytes()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", f"{source_t:.3f}",
            "-i", str(video_path),
            "-frames:v", "1",
            "-vf", f"scale={scale_width}:-1",
            str(output_path),
        ],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed at t={source_t} on {video_path}: {result.stderr[-500:].decode()}")
    return output_path.read_bytes()


def b64_image(image_bytes: bytes) -> dict:
    """Build an Anthropic image content block."""
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": base64.standard_b64encode(image_bytes).decode("ascii"),
        },
    }


# ───────────────────────── response caching (skip re-billing) ─────────────────────────
def make_cache_key(check_id: str, system_prompt: str, user_text: str,
                   image_bytes: bytes | None, model: str) -> str:
    h = hashlib.sha256()
    h.update(check_id.encode())
    h.update(model.encode())
    h.update(system_prompt.encode())
    h.update(user_text.encode())
    if image_bytes:
        h.update(image_bytes)
    return h.hexdigest()[:24]


def load_cached(cache_dir: Path, key: str) -> dict | None:
    p = cache_dir / f"{key}.json"
    if p.exists():
        return json.loads(p.read_text())
    return None


def save_cached(cache_dir: Path, key: str, result: dict):
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / f"{key}.json").write_text(json.dumps(result, indent=2))


# ───────────────────────── Claude call wrapper ─────────────────────────
@dataclass
class CostTracker:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    n_calls: int = 0
    n_cache_hits: int = 0

    def add_response(self, response):
        usage = response.usage
        self.input_tokens += usage.input_tokens or 0
        self.output_tokens += usage.output_tokens or 0
        self.cache_read_tokens += getattr(usage, "cache_read_input_tokens", 0) or 0
        self.cache_creation_tokens += getattr(usage, "cache_creation_input_tokens", 0) or 0
        self.n_calls += 1

    def add_hit(self):
        self.n_cache_hits += 1

    def estimate_cost_usd(self, model: str) -> float:
        rates = PRICING.get(model, PRICING[DEFAULT_MODEL])
        return (
            self.input_tokens          * rates["input"]       / 1_000_000
            + self.output_tokens         * rates["output"]      / 1_000_000
            + self.cache_read_tokens     * rates["cache_read"]  / 1_000_000
            + self.cache_creation_tokens * rates["cache_write"] / 1_000_000
        )


def call_claude(
    client: anthropic.Anthropic,
    model: str,
    check_id: str,
    system_prompt: str,
    user_text: str,
    image_bytes: bytes | None,
    output_format: type[BaseModel],
    cache_dir: Path,
    cost: CostTracker,
    use_cache: bool = True,
) -> BaseModel:
    """Call Claude with vision + structured output. Caches response by content hash."""
    key = make_cache_key(check_id, system_prompt, user_text, image_bytes, model)

    if use_cache:
        cached = load_cached(cache_dir, key)
        if cached:
            cost.add_hit()
            return output_format.model_validate(cached)

    # Build content blocks
    content_blocks: list[dict] = []
    if image_bytes:
        content_blocks.append(b64_image(image_bytes))
    content_blocks.append({"type": "text", "text": user_text})

    response = client.messages.parse(
        model=model,
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": content_blocks}],
        output_format=output_format,
    )

    cost.add_response(response)
    verdict = response.parsed_output
    save_cached(cache_dir, key, verdict.model_dump())
    return verdict


# ───────────────────────── system prompts (cached prefix) ─────────────────────────
# Each prompt is sized to encourage prompt-cache hits on Opus 4.7 (≥4096 tokens of stable
# prefix). The hard rules + project principles are quoted in full so the cache prefix is
# substantial and meaningful — Claude has full context for the judgment.

R01_SYSTEM = textwrap.dedent("""
You are reviewing frames from rendered preview videos in the Chicago Global / Parallax video pipeline. These videos demonstrate Parallax product features through product-demo screencasts with VO narration and visual annotations.

# The visual contract you're evaluating

The pipeline uses "annotate-mode spotlights" for emphasis on the rendered output brief. Each spotlight:

- Is a soft-edged elliptical bright area centered on the named content
- Sits over a dimmed background (~60% black overlay) covering everything else in the source frame
- Pairs 1:1 with an annotation panel on the right side of the composition (eyebrow + headline + body)
- Carries an implicit numbered badge on the panel (#1, #2, #3) — the spotlight itself has no number

# What you're judging

Whether the bright/spotlit content in the frame *visually matches* what the paired panel pitches. The panel's eyebrow + headline + body together describe what the spotlight should be pointing at. You verify the spotlight is in fact pointing at that content.

# Verdict scale

- **pass** — the spotlit content visually matches the panel's pitch. The bright area contains the specific text/element the panel names. A viewer reading the panel would naturally look at the bright spot and find what they expect.
- **drift** — the spotlit content is in the same conceptual neighborhood (correct section, correct column, near the right row) but misses the specific element the panel names. E.g., panel pitches "Composite score 5.6/10" but spotlight is on the Quality row.
- **fail** — the spotlit content is on completely different content from what the panel pitches. E.g., panel pitches "Bottom Line verdict" but spotlight is on the Analyst View section.

# Authoritative rules you're checking against

## Hard Rule #17 — Vertical safe zone

Annotate-mode spotlights must land within the composition's vertical safe zone (comp y=30%-70%). The spotlight's center sits within this band so the viewer's eye doesn't have to track to the top or bottom edge of the frame.

## Hard Rule #24 — Tight bounding box

Annotate highlight regions are tight bounding boxes of the *specific text the paired VO line names* — not the section the text lives in. The three-tier band:

| Tier | What VO names | Height | Resolution |
|---|---|---|---|
| 1 | Specific row / cell / phrase | ≤15% | Tight bounding box, single spotlight |
| 2 | Conceptual unit (header + paragraph) | 15–25% | Single spotlight covering the WHOLE unit |
| 3 | Multi-paragraph section / table block | >25% | Split into sub-annotates with shared panel |

## Hard Rule #24 — Subject lock

Each panel's topic is the spotlit content; the rhetorical shape is the angle on that topic, not a license to drift. If the panel pitches "the Value factor," the spotlight covers the Value row across all four columns, not just the score cell. If it pitches "the Bottom Line verdict," the rect encloses the Bottom Line header + the whole paragraph.

## Coupling rule

Long-body panels (>15 words) pair with tight spotlights (≤15%). Short-body or bare-callout panels can pair with wider spotlights (15-25%) — viewer has time to scan a larger illuminated area.

# How to reason

1. **Describe what's bright/in-focus in the frame.** Be specific — what text, what number, what row, what section. Don't just say "the score panel" — say "the Total/Composite row showing 5.6/10 Fair."
2. **Describe what the panel pitches.** Read the eyebrow + headline + body. What is the panel claiming the viewer should look at?
3. **Match the two.** Does the bright content satisfy the panel's pitch?

Be honest about ambiguity. If you can't clearly tell what's bright vs dim in the frame (low contrast, motion blur, scroll-in-progress), say so in your reasoning and pick the verdict that reflects your confidence.
""").strip()


R02_SYSTEM = textwrap.dedent("""
You are reviewing annotation panel copy in the Chicago Global / Parallax video pipeline. Each video targets a specific *primary_persona* (a buyer persona like Portfolio Manager, RIA, Analyst) and a *primary_moment* (the workflow moment the video addresses).

# What you're judging

Whether each panel field (eyebrow, headline, body) speaks from the **buyer's chair** — outcome, stakes, workflow-fit, methodology-credibility — and never from the **system's chair** — parallel calls, MCP invocations, agent orchestration, capability counts.

# Verdict scale

- **pass** — every field speaks from the buyer's chair. Even when describing what Parallax does, the framing is *what it gives the buyer*, not *how the system works internally*.
- **fail** — at least one field uses engineering vocabulary or describes system mechanics rather than buyer outcomes.

# The rule you're enforcing

## Customer's-chair framing (use_case Quality Check #9)

The audience for use_case content is the buyer named in `primary_persona`. They evaluate the demo by what it gives them at the moment named in `primary_moment` — never by what the system does internally. Apply this check to **every authored field**: panel eyebrow, panel headline, panel body.

**Engineering vocabulary banned phrases:**
- "parallel calls" / "parallel skill calls"
- "MCP tool" / "MCP invocation" / "MCP invocations"
- "agent orchestration"
- "skill invocation" / "skill invocations"
- "tool invocations"
- Capability counts ("eight tools," "twelve tools," "twenty MCP invocations")

**The four valid framing molds:**

1. **Outcome** — what the buyer walks away with. "A defensible position-size call." "A peer-adjusted answer ready for the IC."
2. **Stakes** — what's on the line in the named moment. "Before the trade, the score." "When the position has to clear committee."
3. **Workflow-fit** — how this slots into the buyer's existing process. "Same five pillars on every name. Drops into the brief."
4. **Methodology-credibility** — the specific discipline that makes the output defensible. "Peer-adjusted. Out-of-sample. Re-run tomorrow, same number."

**Mute test:** if the viewer watched this panel with audio off and no Parallax background, would the line read as "something this tool DOES for me" or "something this tool IS internally"? The former is correct; the latter is a violation.

# How to reason

For each field (eyebrow, headline, body), ask:
1. Does it use any banned phrase verbatim?
2. Does it cite a capability count (number of tools, calls, skills)?
3. Does it describe what the system does internally, or what the buyer gets?
4. Does it fit one of the four molds (outcome / stakes / workflow-fit / methodology-credibility)?

If any field fails, the verdict is "fail" and you must list each issue. Provide a suggested rewrite for each issue in audience-perspective vocabulary.

Eyebrow conventions are LOCKED VOCABULARY (e.g. "COMPOSITE SCORE · WHAT IT GIVES YOU" is canonical) — these are brand-locked and pass automatically as long as they don't include capability counts.
""").strip()


R03_SYSTEM = textwrap.dedent("""
You are reviewing annotation panel content in the Chicago Global / Parallax video pipeline. Each panel has a rhetorical *shape* — the angle it takes on the spotlit content.

# The three shapes

1. **Capability** — names what the segment *gives* the buyer. "A peer-adjusted answer to 'isn't NVDA expensive?'" "The quant spine, before the trade." Pitches what having this content in every brief enables.
2. **Workflow** — names how the segment *fits* into the buyer's existing process. "Drops into the IC packet." "Defensible to the head of research." Pitches the seam where this segment integrates into existing work.
3. **Stakes** — names *what's on the line* at the named moment. "When the position has to clear committee." "Before the trade goes on the books." Pitches the consequence of getting this segment right (or wrong).

# What you're judging

Two things:

1. **Classification accuracy** — classify each panel's body as capability, workflow, or stakes.
2. **Rotation rule** — no two consecutive panels (by callout_number) should have the same shape. The viewer's brain should experience rhetorical variety across the video's panels.

# Verdict scale

- **pass** — every panel classifies cleanly into one shape, and no two consecutive panels share that shape.
- **fail** — at least two consecutive panels have the same shape (rotation rule violated), OR a panel doesn't classify cleanly (mixed shape or none of the three).

# How to reason

For each panel in order (ap1, ap2, ap3...):
1. Read the body carefully.
2. Identify the angle — what is the panel asking the viewer to feel/understand? Capability (what you get), workflow (how it fits), or stakes (what's on the line)?
3. Assign exactly one shape. If the panel is mixed-shape, classify it by the *dominant* angle and note the mixture in your rationale.

Then check the sequence: are any two consecutive panels the same shape? If yes, list each violation as "ap_X (shape) → ap_Y (same shape)".

Note: For shared-panel clusters (multiple sub-annotates sharing one callout_number), treat the cluster as a single panel for rotation purposes — only the cluster's overall shape matters, not the sub-annotate sequence inside it.
""").strip()


R04_SYSTEM = textwrap.dedent("""
You are reviewing voiceover scripts in the Chicago Global / Parallax video pipeline. The script body lives in `> ` blockquotes under a `## Voiceover script` heading.

# The rule you're enforcing

## Vault stats integrate, not narrate (Production Principle, 2026-05-21)

Vault stats (numbers from the Parallax vault: 62K+ listings, 48 markets, 13 years out-of-sample, ICIR 4.10, etc.) appear *anchored to a specific output moment on screen* — never narrated as standalone credibility prose. Standalone "credibility ribbon" beats — VO lines reciting stats outside of a spotlit output moment — are forbidden.

**Pass examples (integrated):**
- *"Value at three — peer-ranked against AVGO, AMD, ARM and the broader sixty-two-thousand-listing universe."* (Anchors 62K to the Value row being spotlit.)
- *"Quality stayed flat at ten through the year."* (Anchored to the Quality row's trajectory.)

**Fail examples (narrated standalone):**
- *"Parallax has been running on out-of-sample data since 2019, with an ICIR of four-point-one-zero across the universe."* (Standalone credibility prose — no spotlit output moment.)
- *"Sixty-two thousand listings across forty-eight markets, all scored by the same factor framework."* (Recites scale without anchoring to a specific on-screen element.)

# What you're judging

Whether the VO body has any vault stats appearing as standalone narration rather than integrated into a specific output moment.

# Verdict scale

- **pass** — every vault stat in the VO is anchored to a specific output element the viewer is looking at (a row, a cell, a paragraph, a header).
- **fail** — one or more vault stats appear as standalone credibility narration with no on-screen output moment anchor.

# How to reason

1. Scan the VO body for any *numeric* claim that comes from the Parallax vault — listing counts, market counts, year ranges, ICIR/IR/Sharpe numbers, percentile rankings.
2. For each, check the surrounding context — is it adjacent to a spotlit row/cell/section description? Or is it floating prose like *"the framework has been validated across X markets"*?
3. If it's standalone, quote the violating line and explain why it's not anchored.

Stage directions (`**[bracketed]**` text) are not VO — ignore them. Only blockquoted spoken lines count.
""").strip()


R05_SYSTEM = textwrap.dedent("""
You are reviewing frames from Parallax product-demo videos. Each video has a locked beat sheet in `Parallax Video Plan - MASTER.md` — a sequence of beats with target seconds and content descriptions.

# What you're judging

Whether the rendered frame at the beat's corresponding moment in the recording *visibly contains* the content the beat sheet promises.

# Verdict scale

- **pass** — the frame clearly shows the content described in the beat. A viewer landing on this frame would recognize the beat's claimed subject matter.
- **fail** — the frame doesn't show the claimed content, OR shows different content entirely.

# The rule you're enforcing

## Hard Rule #4 — Recording must visibly contain each beat's claimed content

The recording (raw → scrubbed → zoomed) must visibly contain each beat's content. If a beat claims "Score panel reveal with Total Score + 5 factor pillars," the corresponding moment in the recording must show that score panel with all 5 pillars visible. Missing beat content means re-record, not re-scrub.

# How to reason

1. Read the beat's content description carefully. Identify the *specific* visual elements it promises.
2. Look at the frame. Can you identify each promised element?
3. If yes — pass. Summarize what's visible.
4. If partial or no — fail. Describe what IS visible vs what was promised.

Be specific in your summary of visible content — name the actual sections, headers, numbers, rows you see. Don't just say "the brief is visible" — say "the Composite Score & Factor Pillars table with Total 5.6/10, Quality 10/10, Value 3/10, Momentum 6/10 rows visible."
""").strip()


R06_SYSTEM = textwrap.dedent("""
You are reviewing frame-citation pairs from Parallax video scripts. Every on-screen claim in a Parallax script must cite a frame in the `frames_used:` frontmatter section — and the frame must visibly contain the specifics described in the cite.

# What you're judging

Whether the cited frame visibly contains the content described in the `cites:` text.

# Verdict scale

- **pass** — the frame clearly contains the specific content the cite describes (numbers, sections, headers, etc).
- **fail** — the frame doesn't contain the cited content, or contains different content.

# The rule you're enforcing

## Hard Rule #7 — Every on-screen claim cites a frame

Hallucination check is enforced at Phase 5 (script drafting), grounded in the Phase 4 frame audit. No exceptions — wrong stats in published video are credibility-destroying. The `frames_used:` section is the durable record: each entry is `{ frame: <filename>, timestamp: <scrubbed-t>, cites: <description of what the frame shows> }`. The cite text must be verifiable against the actual frame pixels.

# How to reason

1. Read the cite text. Identify the *specific* elements claimed — section names, header text, numbers, ratings, table values.
2. Look at the frame. Can you find each cited element?
3. If yes — pass. Briefly describe what's visible.
4. If no — fail. List what's missing or different.

Pay particular attention to numeric values (scores like "5.6/10," ratios like "P/E 34.2," percentages) — these are the highest-risk hallucination vector. If the cite mentions a specific number, verify it character-by-character in the frame.
""").strip()


# ───────────────────────── findings + report ─────────────────────────
@dataclass
class CheckFinding:
    rule: str               # "R01", etc.
    subject: str            # "ap1", "ap2", or for cross-panel checks "all_panels"
    severity: str           # "error" | "warn" | "pass"
    summary: str            # one-line conclusion
    detail: str             # full reasoning
    evidence_frame: Path | None = None  # path to extracted frame, for markdown embed
    was_cached: bool = False


# ───────────────────────── check implementations ─────────────────────────
def check_R01_subject_match(client, model, ctx, cost) -> list[CheckFinding]:
    """Per-annotate: does the spotlit content match the panel pitch?"""
    findings: list[CheckFinding] = []
    preview = ctx["preview_path"]
    if not preview.exists():
        return [CheckFinding(rule="R01", subject="-", severity="error",
                              summary="preview.mp4 missing",
                              detail=f"{preview} not on disk. Run `tools/render.py {ctx['video_id']} --mode preview` first.")]

    # Get the annotate cluster map from zooms.json
    annotations = ctx["frontmatter"].get("annotations") or []
    zooms = ctx["zooms"]

    clusters: dict[int, list[dict]] = {}
    for z in zooms:
        if z.get("mode") != "annotate":
            continue
        n = int(z.get("callout_number", 0))
        clusters.setdefault(n, []).append(z)

    for ann in annotations:
        ap_id = ann.get("id", "?")
        callout = int(ann.get("callout_number", 0))
        panel = ann.get("panel") or {}
        in_t = float(ann.get("in_recording_t", 0))
        out_t = float(ann.get("out_recording_t", 0))
        cluster = clusters.get(callout, [])
        # Mid-hold timestamp for the SHARED panel = (in + out) / 2 in zoomed-file time
        mid_t = (in_t + out_t) / 2.0 + 5.0  # +5s to skip the title card in composition

        frame_path = ctx["evidence_dir"] / f"R01_{ap_id}_t{mid_t:.2f}.jpg"
        try:
            image_bytes = extract_frame(preview, mid_t, frame_path)
        except RuntimeError as e:
            findings.append(CheckFinding(rule="R01", subject=ap_id, severity="error",
                                          summary=f"frame extraction failed at t={mid_t:.2f}s",
                                          detail=str(e)))
            continue

        beat_notes = "\n".join(f"  - {z['id']}: {z.get('_beat', '')[:300]}" for z in cluster)
        user_text = textwrap.dedent(f"""
        Annotate ID: {ap_id}
        Callout number: #{callout}
        Cluster size: {len(cluster)} sub-annotate(s)

        Paired panel content:
          eyebrow:  {panel.get('eyebrow', '(none)')}
          headline: {panel.get('headline', '(none)')}
          body:     {panel.get('body', '(none — bare callout)')}

        Sub-annotate _beat notes (one per sub-spotlight in the cluster):
        {beat_notes}

        Evaluate whether the spotlit (bright) area in the frame matches what this panel pitches.
        """).strip()

        verdict: SubjectMatchVerdict = call_claude(
            client=client, model=model, check_id=f"R01_{ap_id}",
            system_prompt=R01_SYSTEM,
            user_text=user_text,
            image_bytes=image_bytes,
            output_format=SubjectMatchVerdict,
            cache_dir=ctx["cache_dir"], cost=cost,
            use_cache=ctx["use_cache"],
        )

        if verdict.result == "pass":
            severity = "pass"
        elif verdict.result == "drift":
            severity = "warn"
        else:
            severity = "error"

        findings.append(CheckFinding(
            rule="R01", subject=ap_id, severity=severity,
            summary=f"{verdict.result} — {verdict.reasoning[:120]}",
            detail=(
                f"**Spotlit content (frame):** {verdict.spotlit_content_description}\n\n"
                f"**Panel pitches:** {verdict.panel_pitch_description}\n\n"
                f"**Reasoning:** {verdict.reasoning}"
            ),
            evidence_frame=frame_path,
            was_cached=cost.n_cache_hits > 0 and cost.n_calls == 0,
        ))
    return findings


def check_R02_framing(client, model, ctx, cost) -> list[CheckFinding]:
    """Per-panel: customer's-chair framing."""
    findings: list[CheckFinding] = []
    annotations = ctx["frontmatter"].get("annotations") or []
    primary_persona = ctx["frontmatter"].get("primary_persona", "(unknown persona)")

    for ann in annotations:
        ap_id = ann.get("id", "?")
        panel = ann.get("panel") or {}
        user_text = textwrap.dedent(f"""
        Panel ID: {ap_id}
        Primary persona for this video: {primary_persona}

        Panel content:
          eyebrow:  {panel.get('eyebrow', '(none)')}
          headline: {panel.get('headline', '(none)')}
          body:     {panel.get('body', '(none — bare callout)')}

        Evaluate each field against customer's-chair framing. Pass if all fields speak from the buyer's chair; fail with findings if any field uses engineering vocabulary or system-perspective framing.
        """).strip()

        verdict: FramingVerdict = call_claude(
            client=client, model=model, check_id=f"R02_{ap_id}",
            system_prompt=R02_SYSTEM,
            user_text=user_text,
            image_bytes=None,
            output_format=FramingVerdict,
            cache_dir=ctx["cache_dir"], cost=cost,
            use_cache=ctx["use_cache"],
        )

        if verdict.result == "pass":
            findings.append(CheckFinding(
                rule="R02", subject=ap_id, severity="pass",
                summary="customer's-chair framing OK",
                detail="all fields speak from the buyer's chair",
            ))
        else:
            detail_lines = []
            for f in verdict.findings:
                detail_lines.append(f"- **{f.field}**: {f.problem}\n  - *Suggested:* {f.suggested_rewrite}")
            findings.append(CheckFinding(
                rule="R02", subject=ap_id, severity="error",
                summary=f"{len(verdict.findings)} field(s) in system-chair framing",
                detail="\n".join(detail_lines),
            ))
    return findings


def check_R03_rotation(client, model, ctx, cost) -> list[CheckFinding]:
    """Across-panels: 3-shape rotation (capability/workflow/stakes), no consecutive same."""
    annotations = ctx["frontmatter"].get("annotations") or []
    if len(annotations) < 2:
        return [CheckFinding(rule="R03", subject="all_panels", severity="pass",
                              summary=f"only {len(annotations)} panel(s) — rotation rule N/A",
                              detail="rotation rule requires ≥2 panels")]

    panels_block = []
    for ann in annotations:
        ap_id = ann.get("id", "?")
        panel = ann.get("panel") or {}
        panels_block.append(textwrap.dedent(f"""
        Panel {ap_id}:
          eyebrow:  {panel.get('eyebrow', '(none)')}
          headline: {panel.get('headline', '(none)')}
          body:     {panel.get('body', '(none — bare callout)')}
        """).rstrip())

    user_text = textwrap.dedent(f"""
        {len(annotations)} panels in this video, in callout order:

        {chr(10).join(panels_block)}

        For each panel, classify its rhetorical shape (capability / workflow / stakes) based on the body content. Then check whether any two consecutive panels share the same shape.
    """).strip()

    verdict: RotationVerdict = call_claude(
        client=client, model=model, check_id="R03_all",
        system_prompt=R03_SYSTEM,
        user_text=user_text,
        image_bytes=None,
        output_format=RotationVerdict,
        cache_dir=ctx["cache_dir"], cost=cost,
        use_cache=ctx["use_cache"],
    )

    shape_lines = [f"- **{s.panel_id}**: *{s.shape}* — {s.rationale}" for s in verdict.shapes]
    # Compute severity from actual evidence rather than the LLM's `result`
    # field. Observed on V1: LLM returned result="fail" + zero consecutive
    # violations + all panels cleanly classified — internally inconsistent.
    # Source-of-truth is consecutive_violations: empty list ↔ no rotation
    # rule violation ↔ pass.
    if len(verdict.consecutive_violations) == 0:
        return [CheckFinding(
            rule="R03", subject="all_panels", severity="pass",
            summary="all panels classified, no consecutive same-shape",
            detail="\n".join(shape_lines),
        )]
    else:
        violations = "\n".join(f"- {v}" for v in verdict.consecutive_violations)
        return [CheckFinding(
            rule="R03", subject="all_panels", severity="error",
            summary=f"{len(verdict.consecutive_violations)} consecutive same-shape violation(s)",
            detail=f"**Classifications:**\n{chr(10).join(shape_lines)}\n\n**Violations:**\n{violations}",
        )]


def check_R04_vault_stats(client, model, ctx, cost) -> list[CheckFinding]:
    """VO body: integrate-not-narrate for vault stats."""
    vo = ctx["vo_body"]
    if not vo.strip():
        return [CheckFinding(rule="R04", subject="vo_body", severity="warn",
                              summary="no VO body found",
                              detail="VO body is empty — nothing to evaluate")]

    user_text = textwrap.dedent(f"""
        VO body for video {ctx['video_id']}:

        ```
        {vo}
        ```

        Identify any vault stats appearing as standalone narration (not anchored to a specific spotlit output moment). Quote each violating line.
    """).strip()

    verdict: VaultStatsVerdict = call_claude(
        client=client, model=model, check_id="R04_vo",
        system_prompt=R04_SYSTEM,
        user_text=user_text,
        image_bytes=None,
        output_format=VaultStatsVerdict,
        cache_dir=ctx["cache_dir"], cost=cost,
        use_cache=ctx["use_cache"],
    )

    if verdict.result == "pass":
        return [CheckFinding(
            rule="R04", subject="vo_body", severity="pass",
            summary="vault stats integrate cleanly",
            detail="no standalone credibility narration found",
        )]
    else:
        detail_lines = []
        for v in verdict.violations:
            detail_lines.append(f"- *\"{v.quoted_line}\"*\n  - **Problem:** {v.problem}")
        return [CheckFinding(
            rule="R04", subject="vo_body", severity="error",
            summary=f"{len(verdict.violations)} vault-stat violation(s)",
            detail="\n".join(detail_lines),
        )]


def check_R05_beat_content(client, model, ctx, cost) -> list[CheckFinding]:
    """Per-dwell-beat: beat sheet content visible in matching annotate's frame."""
    findings: list[CheckFinding] = []
    beats = ctx["beat_targets"]
    if not beats:
        return [CheckFinding(rule="R05", subject="-", severity="warn",
                              summary="MASTER.md beat sheet not parseable",
                              detail=f"no beat-sheet table found for {ctx['video_id']}")]
    annotations = ctx["frontmatter"].get("annotations") or []
    zoomed = ctx["zoomed_path"]
    if not zoomed.exists():
        return [CheckFinding(rule="R05", subject="-", severity="error",
                              summary="zoomed file missing",
                              detail=f"{zoomed} not on disk")]

    # Map dwell beats to annotate clusters in order
    dwell_beats = [b for b in beats if b["dwell"]]
    if len(dwell_beats) != len(annotations):
        findings.append(CheckFinding(
            rule="R05", subject="-", severity="warn",
            summary=f"dwell beats ({len(dwell_beats)}) ≠ panels ({len(annotations)})",
            detail="best-effort mapping by ordinal position — some beats may be skipped",
        ))

    for beat, ann in zip(dwell_beats, annotations):
        ap_id = ann.get("id", "?")
        in_t = float(ann.get("in_recording_t", 0))
        # Sample at a moment well inside the hold so the spotlight has materialized
        sample_t = in_t + 1.0

        frame_path = ctx["evidence_dir"] / f"R05_beat{beat['number']}_{ap_id}.jpg"
        try:
            image_bytes = extract_frame(zoomed, sample_t, frame_path)
        except RuntimeError as e:
            findings.append(CheckFinding(rule="R05", subject=f"beat{beat['number']}", severity="error",
                                          summary=f"frame extraction failed at t={sample_t:.2f}s",
                                          detail=str(e)))
            continue

        user_text = textwrap.dedent(f"""
            Beat #{beat['number']}: {beat['beat']}
            Target duration: {beat['target_s']}s
            Beat content (from MASTER.md beat sheet):
            {beat['content']}

            Mapped to annotate: {ap_id}
            Frame sampled at zoomed-recording t = {sample_t:.2f}s.

            Verify whether the frame visibly contains the content this beat promises.
        """).strip()

        verdict: BeatContentVerdict = call_claude(
            client=client, model=model, check_id=f"R05_beat{beat['number']}",
            system_prompt=R05_SYSTEM,
            user_text=user_text,
            image_bytes=image_bytes,
            output_format=BeatContentVerdict,
            cache_dir=ctx["cache_dir"], cost=cost,
            use_cache=ctx["use_cache"],
        )

        severity = "pass" if verdict.result == "pass" else "error"
        findings.append(CheckFinding(
            rule="R05", subject=f"beat{beat['number']} ({beat['beat'][:40]})",
            severity=severity,
            summary=f"{verdict.result} — {verdict.reasoning[:120]}",
            detail=(
                f"**Beat:** {verdict.beat_name}\n\n"
                f"**Visible content in frame:** {verdict.visible_content_summary}\n\n"
                f"**Reasoning:** {verdict.reasoning}"
            ),
            evidence_frame=frame_path,
        ))
    return findings


def check_R06_hallucination(client, model, ctx, cost) -> list[CheckFinding]:
    """Per frames_used: verify frame contains cited content."""
    findings: list[CheckFinding] = []
    frames_used = ctx["frontmatter"].get("frames_used") or []
    frames_dir = PROJECT_ROOT / "frames" / ctx["video_id"]

    for fu in frames_used:
        frame_name = fu.get("frame", "")
        timestamp = fu.get("timestamp", "?")
        cite = fu.get("cites", "")
        frame_path = frames_dir / frame_name
        if not frame_path.exists():
            findings.append(CheckFinding(
                rule="R06", subject=frame_name, severity="error",
                summary=f"frame file missing: {frame_name}",
                detail=f"{frame_path} not on disk; re-run extract_frames.py",
            ))
            continue

        image_bytes = frame_path.read_bytes()
        user_text = textwrap.dedent(f"""
            Frame: {frame_name}
            Recording timestamp: {timestamp}s
            Cite text (claimed content of the frame):

            "{cite}"

            Verify whether the frame contains the cited content.
        """).strip()

        verdict: HallucinationVerdict = call_claude(
            client=client, model=model, check_id=f"R06_{frame_name}",
            system_prompt=R06_SYSTEM,
            user_text=user_text,
            image_bytes=image_bytes,
            output_format=HallucinationVerdict,
            cache_dir=ctx["cache_dir"], cost=cost,
            use_cache=ctx["use_cache"],
        )

        severity = "pass" if verdict.result == "pass" else "error"
        findings.append(CheckFinding(
            rule="R06", subject=frame_name, severity=severity,
            summary=f"{verdict.result} — {verdict.reasoning[:120]}",
            detail=(
                f"**Cite:** \"{verdict.cite_text}\"\n\n"
                f"**Visible content:** {verdict.frame_visible_content}\n\n"
                f"**Reasoning:** {verdict.reasoning}"
            ),
            evidence_frame=frame_path,
        ))
    return findings


# ───────────────────────── check registry ─────────────────────────
CHECKS = {
    "R01": ("Subject-match (spotlight vs panel)", check_R01_subject_match),
    "R02": ("Customer's-chair framing (panel copy)", check_R02_framing),
    "R03": ("Panel shape rotation",                 check_R03_rotation),
    "R04": ("Vault stats integrate-not-narrate",    check_R04_vault_stats),
    "R05": ("Beat content visible in recording",    check_R05_beat_content),
    "R06": ("Hallucination check (frames_used)",    check_R06_hallucination),
}


# ───────────────────────── context loader ─────────────────────────
def build_context(video_id: str, use_cache: bool) -> dict:
    rec_dir = PROJECT_ROOT / "screen recordings" / video_id
    if video_id == "V1":
        prefix = "1vid"
        scrubbed = rec_dir / f"{prefix}_scrubbed.mp4"
        zoomed = rec_dir / f"{prefix}_zoomed_route2v2_tickcut.mp4"
    else:
        prefix = f"vid{video_id[1:]}"
        scrubbed = rec_dir / f"{prefix}_scrubbed.mp4"
        zoomed = rec_dir / f"{prefix}_zoomed.mp4"

    script_path = PROJECT_ROOT / "scripts" / f"{video_id} voiceover script.md"
    zooms_path = rec_dir / f"{prefix}_zooms.json"
    preview_path = PROJECT_ROOT / "outputs" / video_id / "preview.mp4"

    missing = [p for p in (script_path, zooms_path) if not p.exists()]
    if missing:
        for m in missing:
            print(f"error: missing required artifact: {m.relative_to(PROJECT_ROOT)}", file=sys.stderr)
        sys.exit(2)

    out_dir = PROJECT_ROOT / "outputs" / video_id
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = out_dir / ".review-cache"
    evidence_dir = out_dir / "review-frames"

    return {
        "video_id": video_id,
        "frontmatter": parse_frontmatter(script_path),
        "zooms": json.loads(zooms_path.read_text()),
        "vo_body": parse_vo_body(script_path),
        "beat_targets": parse_master_beats(video_id),
        "script_path": script_path,
        "scrubbed_path": scrubbed,
        "zoomed_path": zoomed,
        "preview_path": preview_path,
        "out_dir": out_dir,
        "cache_dir": cache_dir,
        "evidence_dir": evidence_dir,
        "use_cache": use_cache,
    }


# ───────────────────────── report rendering ─────────────────────────
def render_report(video_id: str, model: str, findings: list[CheckFinding],
                  cost: CostTracker, out_dir: Path) -> Path:
    SEVERITY_RANK = {"error": 0, "warn": 1, "pass": 2}
    findings = sorted(findings, key=lambda f: (f.rule, SEVERITY_RANK[f.severity], f.subject))

    pass_count = sum(1 for f in findings if f.severity == "pass")
    warn_count = sum(1 for f in findings if f.severity == "warn")
    err_count = sum(1 for f in findings if f.severity == "error")

    cost_usd = cost.estimate_cost_usd(model)

    lines = [
        f"# Review report — {video_id}",
        "",
        f"- **Model:** `{model}`",
        f"- **Generated:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- **Summary:** {pass_count} pass · {warn_count} warn · {err_count} error",
        f"- **Total findings:** {len(findings)}",
        "",
        "## Token usage + cost",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| API calls | {cost.n_calls} |",
        f"| Cache hits (free) | {cost.n_cache_hits} |",
        f"| Input tokens (uncached) | {cost.input_tokens:,} |",
        f"| Cache-read tokens | {cost.cache_read_tokens:,} |",
        f"| Cache-write tokens | {cost.cache_creation_tokens:,} |",
        f"| Output tokens | {cost.output_tokens:,} |",
        f"| **Estimated cost USD** | **${cost_usd:.4f}** |",
        "",
    ]

    # Findings grouped by rule
    by_rule: dict[str, list[CheckFinding]] = {}
    for f in findings:
        by_rule.setdefault(f.rule, []).append(f)

    for rule_id in sorted(by_rule.keys()):
        rule_title = CHECKS.get(rule_id, ("Unknown rule",))[0]
        rule_findings = by_rule[rule_id]
        lines.append(f"## {rule_id} — {rule_title}")
        lines.append("")
        for finding in rule_findings:
            icon = {"error": "✗", "warn": "⚠", "pass": "✓"}[finding.severity]
            lines.append(f"### {icon} `{finding.subject}` — {finding.summary}")
            lines.append("")
            lines.append(finding.detail)
            if finding.evidence_frame and finding.evidence_frame.exists():
                # os.path.relpath handles upward traversal (../frames/…) which
                # Path.relative_to cannot — frames live at frames/V<N>/, a
                # sibling of outputs/V<N>/, not a subdir.
                rel = os.path.relpath(finding.evidence_frame, out_dir)
                lines.append("")
                lines.append(f"![{finding.subject}]({rel})")
            lines.append("")

    report_path = out_dir / "review.md"
    report_path.write_text("\n".join(lines))
    return report_path


# ───────────────────────── main ─────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(description="Vision-based semantic review for V<N>.")
    parser.add_argument("video", help="Video id, e.g. V2 or I1")
    parser.add_argument("--checks", help="Comma-separated list of rule ids (e.g. R01,R06)")
    parser.add_argument("--no-cache", action="store_true", help="Force re-run (ignore cached responses)")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Claude model id (default: {DEFAULT_MODEL})")
    args = parser.parse_args()

    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("error: ANTHROPIC_API_KEY not set (checked .env and environment)", file=sys.stderr)
        return 2

    if args.checks:
        wanted = {s.strip() for s in args.checks.split(",")}
        active = {k: v for k, v in CHECKS.items() if k in wanted}
    else:
        active = CHECKS

    ctx = build_context(args.video, use_cache=not args.no_cache)
    client = anthropic.Anthropic()
    cost = CostTracker()

    print(f"\n  review  {args.video}  (model: {args.model}; {len(active)} checks)")
    print(f"  script:    {ctx['script_path'].relative_to(PROJECT_ROOT)}")
    print(f"  preview:   {ctx['preview_path'].relative_to(PROJECT_ROOT)}")
    print(f"  cache dir: {ctx['cache_dir'].relative_to(PROJECT_ROOT)}")
    print()

    all_findings: list[CheckFinding] = []
    for rule_id, (title, fn) in active.items():
        print(f"  → {rule_id} {title}...", end=" ", flush=True)
        try:
            findings = fn(client, args.model, ctx, cost) or []
        except Exception as e:
            print(f"FAILED ({type(e).__name__})")
            findings = [CheckFinding(
                rule=rule_id, subject="-", severity="error",
                summary=f"check threw {type(e).__name__}",
                detail=str(e),
            )]
        all_findings.extend(findings)
        passes = sum(1 for f in findings if f.severity == "pass")
        warns  = sum(1 for f in findings if f.severity == "warn")
        errors = sum(1 for f in findings if f.severity == "error")
        print(f"{passes}p {warns}w {errors}e")

    report_path = render_report(args.video, args.model, all_findings, cost, ctx["out_dir"])
    cost_usd = cost.estimate_cost_usd(args.model)

    print()
    print(f"  report: {report_path.relative_to(PROJECT_ROOT)}")
    print(f"  api calls: {cost.n_calls}  ·  cache hits: {cost.n_cache_hits}  ·  cost: ${cost_usd:.4f}")

    err_count = sum(1 for f in all_findings if f.severity == "error")
    return 1 if err_count else 0


if __name__ == "__main__":
    sys.exit(main())
