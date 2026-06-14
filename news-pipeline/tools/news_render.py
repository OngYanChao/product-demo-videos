#!/usr/bin/env python3
"""render.py — news-pipeline final compose.

Stages a slot's zoom.mp4 (or trimmed.mp4 fallback) into the news Hyperframes
template, substitutes a smart title derived from the prompt, re-anchors the
composition's recording / outro durations to the actual clip length, and runs
`npx hyperframes render`. Output: recordings/N<N>/final.mp4.

This is the news-pipeline analogue of project_root/tools/render.py — but
with all the script-driven machinery removed (no frontmatter, no avatar, no
lower-thirds, no annotate panels). Just title + recording + Polaris outro.

Usage:
    python3 news-pipeline/tools/render.py N11
    python3 news-pipeline/tools/render.py N11 --title "Sustained WTI drop scenario"
    python3 news-pipeline/tools/render.py N11 --dry-run
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

NEWS_PIPELINE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = NEWS_PIPELINE_ROOT.parent
TEMPLATE_DIR = NEWS_PIPELINE_ROOT / "templates" / "news"
TEMPLATE_INDEX = TEMPLATE_DIR / "index.html"
TEMPLATE_RECORDING_SLOT = TEMPLATE_DIR / "assets" / "screen-recording.mp4"

TITLE_FALLBACK = "Parallax news brief"
TITLE_MAX_LEN = 60
OUTRO_DURATION_S = 7.0    # matches the news template's s3 data-duration
TITLE_DURATION_S = 5.0    # matches the news template's s1 data-duration

# Hyperframes render settings — match the main pipeline's quality conventions:
# Hard Rule (CLAUDE.md): "60fps everywhere — re-encode source if keyframes are
# sparse." Source recording is 60fps (capture.py FFMPEG_FRAMERATE=60), so the
# final composition should be too. Hyperframes default is 30fps; we override.
RENDER_FPS = 60
RENDER_QUALITY = "high"   # "draft" | "standard" | "high"  (main pipeline uses
                          # "high" for final renders; news is always a final.)


# ──────────────────────────────────────────────────────────────────────────
# Title derivation
# ──────────────────────────────────────────────────────────────────────────

# Cue words that introduce the topic phrase. High-info ones get tried first
# because they're rare and almost always followed by the actual subject.
TOPIC_CUES_HIGH = (
    "worried about", "concerned about", "regarding", "analyzing",
    "covering", "investigating", "looking at",
)
TOPIC_CUES_LOW = ("about", "on")
# Topic phrases that start with these words are too generic to be a title.
TOPIC_BAD_LEADERS = {"this", "that", "these", "those", "it", "him", "her", "them"}
IMPERATIVE_PREFIX_RE = re.compile(
    r"^(?:Run|Write|Quick|Give\s+(?:me\s+)?|Do|Create|Generate|Build|Make|"
    r"Show|Draft|Compose|Tell|Explain|Summarize)\s+"
    r"(?:a\s+|an\s+|the\s+)?",
    flags=re.IGNORECASE,
)


def _clean_topic(s: str) -> str:
    s = s.strip()
    # Cut off clear sub-clause openers only ("because", "since", etc.). NOT
    # "and" / "that" / "which" / "when" — those appear inside noun phrases
    # we want to keep ("history and global impact", "stat that matters").
    s = re.split(r"\s+(?:because|since|so\s+that|in\s+order\s+to)\s+",
                 s, maxsplit=1)[0]
    return s.rstrip(".,;:—-")


def _topic_acceptable(topic: str) -> bool:
    if not (5 < len(topic) <= TITLE_MAX_LEN):
        return False
    first = topic.split()[0].lower()
    return first not in TOPIC_BAD_LEADERS


def derive_title(prompt_text: str) -> str:
    """Heuristic news-brief title from the user's prompt. Imperfect; the
    --title override is the actual fix when the heuristic picks badly."""
    if not prompt_text or not prompt_text.strip():
        return TITLE_FALLBACK
    sentences = re.split(r"(?<=[.!?])\s+", prompt_text.strip())[:4]

    for cues in (TOPIC_CUES_HIGH, TOPIC_CUES_LOW):
        for sentence in sentences:
            for cue in cues:
                m = re.search(
                    rf"\b{re.escape(cue)}\s+(?:the\s+|a\s+|an\s+)?(.+?)"
                    rf"(?:\s*[—\-,:]|\s*\.|\s*$)",
                    sentence, flags=re.IGNORECASE,
                )
                if not m:
                    continue
                topic = _clean_topic(m.group(1))
                if _topic_acceptable(topic):
                    return topic[0].upper() + topic[1:]

    # Fallback: first sentence with imperative prefix stripped, capped at 8 words
    first = sentences[0] if sentences else prompt_text
    first = IMPERATIVE_PREFIX_RE.sub("", first).strip()
    words = first.split()
    title = " ".join(words[:8])
    if len(title) > TITLE_MAX_LEN:
        title = title[:TITLE_MAX_LEN].rsplit(" ", 1)[0] + "…"
    title = title.rstrip(".,;:—-")
    return (title[0].upper() + title[1:]) if title else TITLE_FALLBACK


# ──────────────────────────────────────────────────────────────────────────
# Template HTML substitutions
# ──────────────────────────────────────────────────────────────────────────

def _substitute_title(html_src: str, new_title: str) -> str:
    pattern = re.compile(r'(<h1 id="t-headline">)[^<]*(</h1>)')
    new = pattern.sub(
        lambda m: m.group(1) + html.escape(new_title) + m.group(2),
        html_src, count=1,
    )
    if new == html_src:
        print("[render] ⚠️  title substitution didn't take — pattern didn't match")
    return new


def _substitute_durations(html_src: str, recording_duration: float) -> str:
    """Re-anchor the comp/recording/outro times to the actual recording length.

    The stripped news template defaults assume V1's 78s recording:
      composition data-duration="90"  (= 5 title + 78 rec + 7 outro)
      scene s2 + <video>: data-duration="78"   (recording length)
      scene s3 data-start="83"   (= 5 + 78)
    AND the GSAP timeline has the outro-anchor times hardcoded too:
      tl.set("#s2", {autoAlpha:0}, 83.0); tl.set("#s3", {autoAlpha:1}, 83.0);
      tl.set("#watermark", {autoAlpha:0}, 83.0); tl.from("#o-wordmark", ..., 83.0);
      tl.from("#o-rule", ..., 84.0); tl.from("#o-tagline", ..., 84.5);
      tl.to("#o-wordmark", ..., 84.5);  (breathing yoyo, time on own line)
    All of those need to shift by (new_outro_start - 83) too — otherwise the
    outro fires at 1:23 instead of (5 + recording_duration), the recording
    fades out 60+s early, and you see the outro over a black screen.
    """
    rec = round(recording_duration, 2)
    outro_start = round(TITLE_DURATION_S + rec, 2)
    comp_dur = round(outro_start + OUTRO_DURATION_S, 2)
    shift = outro_start - 83.0

    def _fmt(x: float) -> str:
        return f"{x:g}"  # drops trailing .0 to match template style

    # ── data-* attribute substitutions ───────────────────────────────────
    out = re.sub(r'data-duration="90"',
                 f'data-duration="{_fmt(comp_dur)}"', html_src, count=1)
    out = re.sub(r'data-duration="78"', f'data-duration="{_fmt(rec)}"', out)
    out = re.sub(r'data-start="83"', f'data-start="{_fmt(outro_start)}"', out, count=1)

    # ── GSAP timeline anchor times: shift 83/84/84.5 by (outro_start - 83)
    # All appear as ", N.N)" at end of tl.X(...) calls, except the breathing
    # yoyo's time which is "84.5," on its own line in a multi-line tl.to(...).
    if shift != 0:
        for old in (83.0, 84.0, 84.5):
            out = out.replace(f", {old})", f", {_fmt(old + shift)})")
        out = re.sub(
            r"^(\s*)84\.5,$",
            lambda m: f"{m.group(1)}{_fmt(84.5 + shift)},",
            out, flags=re.MULTILINE,
        )
    return out


# ──────────────────────────────────────────────────────────────────────────
# Slot resolution + helpers
# ──────────────────────────────────────────────────────────────────────────

def resolve_slot(arg: str) -> Path:
    p = Path(arg)
    if p.is_dir():
        return p.resolve()
    if re.match(r"^N\d+$", arg):
        candidate = NEWS_PIPELINE_ROOT / "recordings" / arg
        if candidate.is_dir():
            return candidate.resolve()
    sys.exit(f"❌ slot not found: {arg}")


def ffprobe_duration(video: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        check=True, capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def load_prompt_text(slot_dir: Path) -> str:
    manifest = slot_dir / "manifest.json"
    if manifest.exists():
        try:
            m = json.loads(manifest.read_text())
            text = m.get("prompt_text", "")
            if text:
                return text
        except (json.JSONDecodeError, OSError):
            pass
    return ""


# ──────────────────────────────────────────────────────────────────────────
# Main render
# ──────────────────────────────────────────────────────────────────────────

def render(slot_dir: Path, title_override: str | None = None,
           fps: int = RENDER_FPS, quality: str = RENDER_QUALITY,
           dry_run: bool = False) -> Path | None:
    # Pick the recording: zoom.mp4 (post-processed) is preferred; trimmed.mp4
    # is the fallback (process.py may have been skipped).
    zoom = slot_dir / "zoom.mp4"
    trimmed = slot_dir / "trimmed.mp4"
    if zoom.exists():
        recording = zoom
    elif trimmed.exists():
        recording = trimmed
        print(f"[render] ⚠️  no zoom.mp4; falling back to trimmed.mp4")
    else:
        sys.exit(f"❌ no zoom.mp4 or trimmed.mp4 in {slot_dir}")

    duration = ffprobe_duration(recording)
    print(f"[render] recording: {recording.name}  ({duration:.2f}s)")

    title = title_override or derive_title(load_prompt_text(slot_dir))
    print(f"[render] title:     {title!r}"
          f"{'  (auto-derived; --title to override)' if not title_override else ''}")

    output_path = slot_dir / "final.mp4"

    if dry_run:
        print(f"\n[dry-run] would stage {recording.name} → assets/screen-recording.mp4")
        print(f"[dry-run] would substitute title + comp duration {duration + 12:.2f}s")
        print(f"[dry-run] would render → {output_path.relative_to(PROJECT_ROOT)}")
        return None

    # Copy the canonical template into a per-run temp dir. All substitutions
    # + asset staging happen against this copy. The canonical template is
    # never mutated, so:
    #   - concurrent renders of different slots don't race on shared state
    #   - the canonical placeholders ("78"/"90"/"83") are always present at
    #     substitution time, so the regex always matches
    #   - if rendering is interrupted (KeyboardInterrupt, OOM, crash), there
    #     is no .bak to restore — the canonical template is already pristine
    #   - no need to git-checkout to recover from corrupted template state
    # Cost: ~50ms per render to copy ~200KB of HTML + ~80MB recording slot,
    # negligible vs the ~2min Hyperframes render itself.
    tmpdir = Path(tempfile.mkdtemp(prefix=f"news-render-{slot_dir.name}-"))
    try:
        work_template = tmpdir / "news"
        shutil.copytree(TEMPLATE_DIR, work_template)
        work_index = work_template / "index.html"
        work_recording_slot = work_template / "assets" / "screen-recording.mp4"

        # 1. Stage the recording into the temp template's assets slot.
        shutil.copy(recording, work_recording_slot)

        # 2. Substitute title + durations on the temp copy.
        html_src = work_index.read_text()
        html_src = _substitute_title(html_src, title)
        html_src = _substitute_durations(html_src, duration)
        work_index.write_text(html_src)

        # 3. Run Hyperframes against the temp template. --fps 60 + --quality
        # high mirror the main pipeline's settings per Hard Rule #15.
        print(f"\n[render] hyperframes render → {output_path.relative_to(PROJECT_ROOT)} "
              f"(fps={fps}, quality={quality})")
        cmd = [
            "npx", "hyperframes", "render", str(work_template),
            "-o", str(output_path),
            "--fps", str(fps),
            "--quality", quality,
        ]
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
        if result.returncode != 0:
            print(f"[render] ⚠️  hyperframes exited rc={result.returncode}")
            return None
        if not output_path.exists():
            print(f"[render] ⚠️  hyperframes did not produce {output_path.name}")
            return None
        print(f"\n[render] ✓ final: {output_path.relative_to(PROJECT_ROOT)}")
        return output_path
    finally:
        # Always clean up the temp tree. ignore_errors so a stuck file handle
        # on Windows or a lingering hyperframes subprocess doesn't mask the
        # actual render result.
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Compose a final news video from a slot.")
    ap.add_argument("slot", help="Slot id (e.g., 'N7') or path to slot directory")
    ap.add_argument("--title", default=None,
                    help="Override the auto-derived title.")
    ap.add_argument("--fps", type=int, default=RENDER_FPS,
                    help=f"Hyperframes render fps (default: {RENDER_FPS}, "
                         f"per the main-pipeline 60fps Hard Rule).")
    ap.add_argument("--quality", choices=["draft", "standard", "high"],
                    default=RENDER_QUALITY,
                    help=f"Hyperframes render quality (default: {RENDER_QUALITY}).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would happen; don't render.")
    args = ap.parse_args()
    result = render(resolve_slot(args.slot), title_override=args.title,
                    fps=args.fps, quality=args.quality, dry_run=args.dry_run)
    # dry-run returns None deliberately → exit 0. A real run that returned
    # None means render() hit a failure path (subprocess exit ≠ 0, missing
    # output, etc.) → exit 1 so the orchestrator (process.py) sees it.
    if args.dry_run:
        return 0
    return 0 if result is not None else 1


if __name__ == "__main__":
    sys.exit(main())
