#!/usr/bin/env python3
"""
tools/render.py — Per-video render pipeline.

Reads a script's frontmatter, substitutes per-video copy + timing into the
template's HTML (with a backup-restore so the template stays clean between
renders), runs `npx hyperframes render`, and writes to `outputs/V<N>/<mode>.mp4`
plus a render-manifest.json.

`--mode preview` ($0): Hyperframes-only render with an avatar placeholder.
`--mode final` (billable): generates the HeyGen avatar clip first (cached at
`avatars/clips/V<N>_<scripthash>.mp4` so identical VO content never re-bills),
then injects it into the template before rendering.

Usage:
    python tools/render.py V1 --mode preview
    python tools/render.py V1 --mode preview --quality draft
    python tools/render.py V1 --mode preview --dry-run
    python tools/render.py V5 --mode preview      # substitution drives V5 from frontmatter
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Project root = parent of tools/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Sibling import
sys.path.insert(0, str(Path(__file__).resolve().parent))
from script_hash import hash_script, extract_spoken_vo


def _load_dotenv() -> None:
    """Load KEY=VALUE pairs from project-root .env into os.environ.
    Existing env vars take priority. No external deps."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text().split("\n"):
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and v and k not in os.environ:
            os.environ[k] = v


def parse_frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter from a markdown file. Uses pyyaml if available;
    falls back to a small hand-parser for the top-level + one-deep fields
    render.py needs (recording.path, video_id, pipeline_type, template).
    """
    text = path.read_text()
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    fm_text = text[4:end]

    try:
        import yaml
        return yaml.safe_load(fm_text) or {}
    except ImportError:
        return _hand_parse_frontmatter(fm_text)


def _hand_parse_frontmatter(fm_text: str) -> dict:
    """Minimal frontmatter parser for the few fields render.py needs.
    Handles top-level scalars and one level of nesting (e.g. recording.path).
    """
    out: dict = {}
    current_block: str | None = None
    current_dict: dict | None = None

    for raw in fm_text.split("\n"):
        # Top-level key (no leading whitespace)
        if raw and not raw.startswith((" ", "\t", "#")):
            if ":" in raw:
                k, _, v = raw.partition(":")
                k = k.strip()
                v = v.strip()
                if v == "" or v == "null":
                    # Block opens
                    current_block = k
                    current_dict = {}
                    out[k] = current_dict
                else:
                    out[k] = v.strip().strip('"').strip("'")
                    current_block = None
                    current_dict = None
        # Nested key (one level of indent)
        elif raw.startswith(("  ", "\t")) and current_dict is not None:
            stripped = raw.strip()
            if ":" in stripped and not stripped.startswith("-"):
                k, _, v = stripped.partition(":")
                v = v.strip().strip('"').strip("'")
                if v:
                    current_dict[k.strip()] = v
    return out


def find_script(video_id: str, override: Path | None = None) -> Path:
    if override:
        return override
    p = PROJECT_ROOT / "scripts" / f"{video_id} voiceover script.md"
    if p.exists():
        return p
    raise FileNotFoundError(
        f"Script not found at {p}. Use --script to specify a path."
    )


def find_template(family: str) -> Path:
    p = PROJECT_ROOT / "templates" / family
    if not p.exists():
        raise FileNotFoundError(f"Template not found at {p}")
    return p


def find_recording(video_id: str, frontmatter: dict) -> Path:
    """Find the recording for this video.

    Resolution order:
      1. `recording.path` from frontmatter (explicit override)
      2. `screen recordings/**/*_zoomed.mp4`  (Phase 5.5 output — canonical)
      3. `screen recordings/**/*_scrubbed.mp4` (Phase 3 output — early-iteration fallback)

    A unique match is required at whichever step resolves.
    """
    rec_block = frontmatter.get("recording", {})
    if isinstance(rec_block, dict) and rec_block.get("path"):
        p = PROJECT_ROOT / rec_block["path"]
        if p.exists():
            return p

    rec_root = PROJECT_ROOT / "screen recordings"
    zoomed = list(rec_root.glob("**/*_zoomed.mp4"))
    if len(zoomed) == 1:
        return zoomed[0]
    if len(zoomed) > 1:
        raise FileNotFoundError(
            f"Multiple zoomed recordings found ({len(zoomed)}); "
            f"specify recording.path in script frontmatter."
        )

    scrubbed = list(rec_root.glob("**/*_scrubbed.mp4"))
    if len(scrubbed) == 1:
        return scrubbed[0]

    raise FileNotFoundError(
        f"Could not find a zoomed or scrubbed recording for {video_id}. "
        f"Specify recording.path in script frontmatter."
    )


def stage_template(template_dir: Path, recording: Path, target_name: str,
                   verbose: bool = False) -> None:
    """Copy the recording into the template's assets/ as the slot filename."""
    target = template_dir / "assets" / target_name
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.resolve() == recording.resolve():
        if verbose:
            print(f"[render] recording already at {target.relative_to(PROJECT_ROOT)} (no copy)")
        return
    shutil.copy2(recording, target)
    if verbose:
        print(f"[render] staged: {recording.name} → assets/{target_name}")


def run_hyperframes_render(template_dir: Path, output_path: Path,
                           fps: int, quality: str, verbose: bool) -> float:
    """Run npx hyperframes render. Returns wall-clock seconds."""
    cmd = [
        "npx", "hyperframes", "render", str(template_dir),
        "--fps", str(fps),
        "--quality", quality,
        "-o", str(output_path),
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if verbose:
        print(f"[render] running: {' '.join(cmd)}")
    t0 = time.time()
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    elapsed = time.time() - t0
    if result.returncode != 0:
        raise RuntimeError(f"hyperframes render failed (exit {result.returncode})")
    return elapsed


def write_manifest(manifest_path: Path, manifest: dict) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2))


# ─────────────────────────────────────────────────────────────────────────────
# Substitution layer (Phase 5 Chunk 1.5)
# Applies per-video copy + timing from script frontmatter into the template's
# index.html. HTML element substitutions use BeautifulSoup (proper parser,
# nested-element-safe). JS-call timing substitutions use regex.
# Operates in-place with backup-restore via .index.html.orig.
# ─────────────────────────────────────────────────────────────────────────────

import re

from bs4 import BeautifulSoup, NavigableString


def _set_text(elem, new_text: str) -> bool:
    """Replace inner content of a BS4 element with plain text.
    Returns True if a change was made, False if content already matches.
    Uses get_text() comparison to ignore surrounding whitespace differences.
    """
    if elem is None:
        return False
    current = elem.get_text()
    # If already equal (after stripping outer whitespace, since template
    # often has leading/trailing newlines + indent around inner text), skip.
    if current.strip() == new_text.strip():
        return False
    elem.clear()
    elem.append(NavigableString(new_text))
    return True


def _set_stats_spans(elem, soup, stats: list) -> bool:
    """Replace the inner content of an .lt-stats element with regenerated
    <span><strong>VALUE</strong> LABEL</span> children. Returns True if changed.
    """
    if elem is None:
        return False

    # Build the new spans
    new_spans = []
    for stat in stats:
        span = soup.new_tag("span")
        strong = soup.new_tag("strong")
        strong.string = str(stat.get("value", ""))
        span.append(strong)
        span.append(NavigableString(" " + str(stat.get("label", ""))))
        new_spans.append(span)

    # Compare flattened text content
    current_pairs = []
    for span in elem.find_all("span", recursive=False):
        strong = span.find("strong")
        value = strong.get_text() if strong else ""
        # Label = whatever follows the <strong>, trimmed
        label_parts = []
        for sib in (strong.next_siblings if strong else span.children):
            label_parts.append(sib.get_text() if hasattr(sib, "get_text") else str(sib))
        label = "".join(label_parts).strip()
        current_pairs.append((value.strip(), label))

    new_pairs = [(str(s.get("value", "")).strip(),
                  str(s.get("label", "")).strip()) for s in stats]

    if current_pairs == new_pairs:
        return False

    elem.clear()
    for span in new_spans:
        elem.append(span)
    return True


def _fmt_time(t: float) -> str:
    """Format a float matching the template's style: always at least one decimal.
    9.0 → '9.0', 9.5 → '9.5', 9.25 → '9.25'. Avoids spurious 'modified' detection
    when frontmatter integer-valued times collide with `:g` stripping the `.0`.
    """
    s = f"{t:.2f}".rstrip("0")
    if s.endswith("."):
        s += "0"
    return s


def _replace_lower_third_timing(html: str, lt_id: str, in_t: float, out_t: float) -> str:
    """Replace lowerThird("#ltN", IN, OUT) call args with new IN, OUT.
    Times are composition-absolute (recording_t + 5)."""
    pattern = rf'lowerThird\("#{re.escape(lt_id)}",\s*[\d.]+,\s*[\d.]+\)'
    replacement = f'lowerThird("#{lt_id}", {_fmt_time(in_t)}, {_fmt_time(out_t)})'
    return re.sub(pattern, replacement, html, count=1)


def _replace_annotate_panel_timing(html: str, ap_id: str, in_t: float, out_t: float) -> str:
    """Replace annotatePanel("#apN", IN, OUT) call args with new IN, OUT.
    Times are composition-absolute (recording_t + 5)."""
    pattern = rf'annotatePanel\("#{re.escape(ap_id)}",\s*[\d.]+,\s*[\d.]+\)'
    replacement = f'annotatePanel("#{ap_id}", {_fmt_time(in_t)}, {_fmt_time(out_t)})'
    return re.sub(pattern, replacement, html, count=1)


def _replace_data_attr_for_id(html: str, element_id: str, attr: str, value: str) -> str:
    """Replace `attr="OLD"` on the element with the given id. Tolerates attr ordering."""
    patterns = [
        rf'(id="{re.escape(element_id)}"[^>]*?{re.escape(attr)}=")[^"]*(")',
        rf'({re.escape(attr)}=")[^"]*("[^>]*?id="{re.escape(element_id)}")',
    ]
    out = html
    for p in patterns:
        new = re.sub(p, rf'\g<1>{value}\g<2>', out, count=1)
        if new != out:
            return new
    return out


def _replace_tl_set_alpha(html: str, target: str, alpha: int, new_t: float) -> str:
    """Replace `tl.set("TARGET", { autoAlpha: ALPHA }, OLD_T)` with new_t."""
    pattern = (
        rf'(tl\.set\("{re.escape(target)}"\s*,\s*\{{\s*autoAlpha:\s*{alpha}\s*\}}\s*,\s*)'
        rf'[\d.]+(\s*\))'
    )
    return re.sub(pattern, rf'\g<1>{_fmt_time(new_t)}\g<2>', html, count=1)


def _replace_tl_method_time(html: str, method: str, target: str, new_t: float,
                            occurrence: int = 1) -> str:
    """Replace the time argument of `tl.<method>("<target>", { vars }, TIME)`.

    method = 'from' or 'to'.
    occurrence = 1-indexed; lets callers disambiguate when multiple tweens
    target the same element (e.g. #o-wordmark has both a fade-in `tl.from`
    and a breathing `tl.to`).

    The vars block matcher tolerates one level of nested braces (sufficient
    for GSAP vars like `{ y: 18, autoAlpha: 0, ... }` — no nested object
    options are used in this template).
    """
    # \s* after `tl.METHOD(` to tolerate multi-line tweens (some calls have
    # the target on a separate line from the opening paren).
    pattern = (
        rf'(tl\.{re.escape(method)}\(\s*"{re.escape(target)}"\s*,\s*'
        rf'\{{[^{{}}]*(?:\{{[^{{}}]*\}}[^{{}}]*)*\}}\s*,\s*)'
        rf'[\d.]+(\s*,?\s*\))'
    )
    matches = list(re.finditer(pattern, html))
    if len(matches) < occurrence:
        return html
    m = matches[occurrence - 1]
    return html[:m.start()] + f'{m.group(1)}{_fmt_time(new_t)}{m.group(2)}' + html[m.end():]


def _replace_avatar_fadeout_time(html: str, new_t: float) -> str:
    """Replace the avatar fade-out timing: tl.to("#avatar", { autoAlpha:0, ... }, OLD_T)."""
    pattern = (
        r'(tl\.to\("#avatar"\s*,\s*\{\s*autoAlpha:\s*0\s*,\s*duration:\s*[\d.]+\s*,\s*'
        r'ease:\s*"[^"]+"\s*\}\s*,\s*)[\d.]+(\s*\))'
    )
    return re.sub(pattern, rf'\g<1>{_fmt_time(new_t)}\g<2>', html, count=1)


# ─────────────────────────────────────────────────────────────────────────────
# Avatar generation (--mode final)
# Calls the heygen CLI to generate a stock-avatar talking-head clip from the
# script's spoken VO. Cached per-video by script hash so identical VO content
# never re-bills HeyGen credits.
# ─────────────────────────────────────────────────────────────────────────────


def generate_avatar_clip(script_path: Path, output_path: Path,
                         dry_run: bool = False, verbose: bool = False) -> None:
    """Generate avatar clip via HeyGen CLI from script's spoken VO.

    Reads HEYGEN_API_KEY, HEYGEN_AVATAR_ID, HEYGEN_VOICE_ID from .env or env.
    Writes the resulting MP4 to output_path.

    Caller is responsible for caching (this always generates fresh when called).

    Raises RuntimeError on:
      - missing credentials in .env
      - script has no spoken VO content
      - heygen API errors (low balance, invalid avatar_id, etc.)
    """
    _load_dotenv()
    api_key = os.environ.get("HEYGEN_API_KEY")
    avatar_id = os.environ.get("HEYGEN_AVATAR_ID")
    voice_id = os.environ.get("HEYGEN_VOICE_ID")

    missing = [n for n, v in [
        ("HEYGEN_API_KEY", api_key),
        ("HEYGEN_AVATAR_ID", avatar_id),
        ("HEYGEN_VOICE_ID", voice_id),
    ] if not v]
    if missing:
        raise RuntimeError(
            f"missing HeyGen credentials in .env: {', '.join(missing)}. "
            "Copy .env.example → .env and fill in values."
        )

    vo = extract_spoken_vo(script_path)
    if not vo.strip():
        raise RuntimeError(f"script {script_path} has no spoken VO content")

    payload = json.dumps({
        "type": "avatar",
        "avatar_id": avatar_id,
        "script": vo,
        "voice_id": voice_id,
    })

    if dry_run:
        print(f"[render] [dry-run] would generate avatar clip:")
        print(f"  - VO chars:   {len(vo)}")
        print(f"  - VO preview: {vo[:120]!r}...")
        print(f"  - avatar_id:  {avatar_id}")
        print(f"  - voice_id:   {voice_id}")
        print(f"  - output:     {output_path.relative_to(PROJECT_ROOT)}")
        print(f"  - command:    heygen video create -d <payload> --wait")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"[render] generating avatar clip via heygen CLI ({len(vo)} chars VO)...")
    cmd = ["heygen", "video", "create", "-d", payload, "--wait"]
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    elapsed = time.time() - t0

    if result.returncode != 0:
        # Surface heygen's structured error if present
        try:
            err = json.loads(result.stdout or result.stderr or "{}")
            err_obj = err.get("error", {}) if isinstance(err, dict) else {}
            err_msg = err_obj.get("message", "")
            err_hint = err_obj.get("hint", "")
            err_code = err_obj.get("code", "")
            raise RuntimeError(
                f"heygen video create failed (exit {result.returncode}, code={err_code}): "
                f"{err_msg}" + (f"\nHint: {err_hint}" if err_hint else "")
            )
        except (json.JSONDecodeError, ValueError):
            raise RuntimeError(
                f"heygen video create failed (exit {result.returncode}):\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )

    response = json.loads(result.stdout)
    video_id = response.get("video_id") or (response.get("data") or {}).get("video_id")
    if not video_id:
        raise RuntimeError(f"heygen response missing video_id: {response}")

    if verbose:
        print(f"[render] heygen video {video_id} created in {elapsed:.1f}s, downloading...")

    cmd_dl = ["heygen", "video", "download", video_id,
              "--output-path", str(output_path), "--force"]
    result = subprocess.run(cmd_dl, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(
            f"heygen video download failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


def inject_avatar_clip(html: str, recording_duration: float) -> tuple[str, bool]:
    """Insert <video> + <audio> clip elements inside #avatar div.

    Idempotent — if a <video> child already exists, returns (html, False)
    without modification.

    Hyperframes rule: video must be muted + playsinline; audio is a separate
    <audio> element. Both clips span the recording window (data-start=5,
    data-duration=recording_duration).

    Returns (modified_html, was_modified).
    """
    soup = BeautifulSoup(html, "html.parser")
    avatar_div = soup.find(id="avatar")
    if avatar_div is None:
        raise RuntimeError("template missing #avatar div")

    if avatar_div.find("video"):
        return html, False

    fallback = avatar_div.find(class_="avatar-fallback")
    if fallback is None:
        raise RuntimeError("template's #avatar missing .avatar-fallback element")

    rec = recording_duration
    video = soup.new_tag("video", attrs={
        "class": "clip avatar-video",
        "data-start": "5",
        "data-duration": f"{rec:.2f}",
        "data-track-index": "2",
        "src": "assets/avatar.mp4",
        "muted": "",
        "playsinline": "",
        "preload": "auto",
    })
    audio = soup.new_tag("audio", attrs={
        "class": "clip avatar-audio",
        "data-start": "5",
        "data-duration": f"{rec:.2f}",
        "data-track-index": "3",
        "src": "assets/avatar.mp4",
        "data-volume": "1",
    })

    fallback.insert_after(video)
    video.insert_after(audio)
    return str(soup), True


def _get_video_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {r.stderr}")
    return float(r.stdout.strip())


# Engineering-vocabulary banned phrases per Customer's-chair framing (Quality Check
# #9 in video-scriptwriting/SKILL.md). Scanned in the substituted HTML before
# render. Any match hard-fails the render (unless --allow-engineering is passed,
# which is the instructional-video carve-out).
#
# This is a defense-in-depth layer. The primary enforcement is QC #9 at script
# drafting time — a script writer should never produce a frontmatter containing
# these phrases. This check catches any that slip through.
#
# Phrases are matched case-insensitively as substrings. List is from the reject
# list in `references/production-principles.md` → "Customer's-chair framing".
CUSTOMERS_CHAIR_BANNED_PHRASES = (
    "parallel skill calls",
    "parallel skill-calls",
    "parallel tool calls",
    "parallel mcp calls",
    "mcp tool invocations",
    "agent orchestration",
    "skill calls fire",
    "tool calls fire in parallel",
    "watch as eight",
    "watch as ten",
)


def check_customers_chair_compliance(html: str, allow_engineering: bool = False) -> list[str]:
    """Scan the substituted HTML for engineering-vocabulary banned phrases per
    `references/production-principles.md` → Customer's-chair framing.
    Returns a list of detected violations (one per matched phrase). Empty list = clean.

    Bypassed when `allow_engineering=True` (the instructional-video carve-out —
    I1–I4 videos legitimately describe system mechanics as the tutorial step).
    """
    if allow_engineering:
        return []
    haystack = html.lower()
    return [p for p in CUSTOMERS_CHAIR_BANNED_PHRASES if p in haystack]


def apply_substitutions(html: str, fm: dict, recording_duration: float | None = None) -> tuple[str, list[str]]:
    """Apply per-video substitutions from script frontmatter to template HTML.

    Returns (modified_html, list_of_slot_names_filled).

    Substitution targets (this template family):
      - Composition durations: #main / #avatar data-duration = 5 + rec + 7
      - Recording-scene durations: #s2 / #rec-video data-duration = rec
      - Outro start: #s3 data-start = 5 + rec
      - Scene-visibility GSAP triggers: tl.set("#s2"|"#s3", { autoAlpha }, 5 + rec)
      - Watermark fade-out: tl.set("#watermark", { autoAlpha: 0 }, 5 + rec)
      - Avatar fade-out: tl.to("#avatar", ..., 5 + rec - 1)
      - Outro element entrances: tl.from on #o-wordmark/#o-rule/#o-tagline +
        the wordmark breathing tl.to (anchored to scene_3_start + offsets)
      - Title: #t-eyebrow, #t-headline
      - Lower-thirds (lt1–lt4): .lt-eyebrow, .lt-headline, .lt-stats inside #ltN
      - GSAP timing: lowerThird("#ltN", in, out)
      - Outro: #o-tagline (only if frontmatter overrides)

    Frontmatter shape (subset):
      beats:
        title:    { eyebrow, headline }
        outro:    { tagline }
      lower_thirds:
        - { id: lt1, in_recording_t, out_recording_t, eyebrow, headline,
            stats: [{value, label}, ...] }

    `recording_duration` is the actual conformed recording's duration in seconds
    (via ffprobe). Required for duration substitutions; if None, those are skipped.
    """
    filled: list[str] = []
    soup = BeautifulSoup(html, "html.parser")

    # Title slots
    title = (fm.get("beats") or {}).get("title") or {}
    if title.get("eyebrow") and _set_text(soup.find(id="t-eyebrow"), title["eyebrow"]):
        filled.append("title.eyebrow")
    if title.get("headline") and _set_text(soup.find(id="t-headline"), title["headline"]):
        filled.append("title.headline")

    # Lower-thirds — text content
    for lt in fm.get("lower_thirds") or []:
        lt_id = lt.get("id")
        if not lt_id:
            continue
        parent = soup.find(id=lt_id)
        if parent is None:
            continue

        if lt.get("eyebrow") and _set_text(parent.find(class_="lt-eyebrow"), lt["eyebrow"]):
            filled.append(f"{lt_id}.eyebrow")
        if lt.get("headline") and _set_text(parent.find(class_="lt-headline"), lt["headline"]):
            filled.append(f"{lt_id}.headline")
        if lt.get("stats") and _set_stats_spans(parent.find(class_="lt-stats"), soup, lt["stats"]):
            filled.append(f"{lt_id}.stats")

    # Outro tagline (rare override; template default is "Solve the market.")
    outro = (fm.get("beats") or {}).get("outro") or {}
    if outro.get("tagline") and _set_text(soup.find(id="o-tagline"), outro["tagline"]):
        filled.append("outro.tagline")

    new_html = str(soup)

    # ── Duration / scene-timing substitutions (depend on the recording's actual
    #    duration via ffprobe — script frontmatter doesn't carry composition-level
    #    timing) ─────────────────────────────────────────────────────────────
    if recording_duration is not None:
        rec = recording_duration
        comp_total = 5.0 + rec + 7.0     # 5s title + recording + 7s outro
        scene_3_start = 5.0 + rec
        avatar_fadeout_t = scene_3_start - 1.0  # 1s before outro begins

        before = new_html
        new_html = _replace_data_attr_for_id(new_html, "main", "data-duration", _fmt_time(comp_total))
        if new_html != before:
            filled.append("main.data-duration")
            before = new_html
        new_html = _replace_data_attr_for_id(new_html, "avatar", "data-duration", _fmt_time(comp_total))
        if new_html != before:
            filled.append("avatar.data-duration")
            before = new_html
        new_html = _replace_data_attr_for_id(new_html, "s2", "data-duration", _fmt_time(rec))
        if new_html != before:
            filled.append("s2.data-duration")
            before = new_html
        new_html = _replace_data_attr_for_id(new_html, "rec-video", "data-duration", _fmt_time(rec))
        if new_html != before:
            filled.append("rec-video.data-duration")
            before = new_html
        new_html = _replace_data_attr_for_id(new_html, "s3", "data-start", _fmt_time(scene_3_start))
        if new_html != before:
            filled.append("s3.data-start")
            before = new_html
        new_html = _replace_tl_set_alpha(new_html, "#s2", 0, scene_3_start)
        if new_html != before:
            filled.append("tl.set#s2.timing")
            before = new_html
        new_html = _replace_tl_set_alpha(new_html, "#s3", 1, scene_3_start)
        if new_html != before:
            filled.append("tl.set#s3.timing")
            before = new_html
        new_html = _replace_tl_set_alpha(new_html, "#watermark", 0, scene_3_start)
        if new_html != before:
            filled.append("tl.set#watermark.timing")
            before = new_html
        new_html = _replace_avatar_fadeout_time(new_html, avatar_fadeout_t)
        if new_html != before:
            filled.append("avatar.fadeout.timing")
            before = new_html

        # Outro element entrance times — anchor to scene_3_start so the outro
        # fade-in always lands the moment s3 becomes visible (no hard cut).
        # Offsets match the template's defaults at scene_3_start = 83.0:
        #   wordmark fades in at scene_3_start + 0.0
        #   rule wipes in    at scene_3_start + 1.0
        #   tagline fades in at scene_3_start + 1.5
        #   wordmark breathing tl.to at scene_3_start + 1.5
        outro_tweens = [
            ("from", "#o-wordmark", scene_3_start + 0.0, "outro.wordmark.timing"),
            ("from", "#o-rule",     scene_3_start + 1.0, "outro.rule.timing"),
            ("from", "#o-tagline",  scene_3_start + 1.5, "outro.tagline.timing"),
            ("to",   "#o-wordmark", scene_3_start + 1.5, "outro.wordmark.breathing.timing"),
        ]
        for method, target, t, label in outro_tweens:
            new_html = _replace_tl_method_time(new_html, method, target, t)
            if new_html != before:
                filled.append(label)
                before = new_html

    # Lower-third call-site timing substitutions (JS function calls).
    # Preserve the template's "(0, 0) = retire" sentinel — when in_recording_t
    # and out_recording_t are both 0, pass (0, 0) through unchanged so the
    # template's `lowerThird` function skip-clause fires (the LT slot stays
    # invisible). Adding the 5s title-card offset to a retire-sentinel would
    # produce (5, 5) which fires the fade-in at t=5 and never fades out.
    for lt in fm.get("lower_thirds") or []:
        lt_id = lt.get("id")
        if not lt_id:
            continue
        if "in_recording_t" in lt and "out_recording_t" in lt:
            in_rt = float(lt["in_recording_t"])
            out_rt = float(lt["out_recording_t"])
            if in_rt == 0.0 and out_rt == 0.0:
                in_abs = 0.0
                out_abs = 0.0
            else:
                in_abs = in_rt + 5.0
                out_abs = out_rt + 5.0
            updated = _replace_lower_third_timing(new_html, lt_id, in_abs, out_abs)
            if updated != new_html:
                new_html = updated
                filled.append(f"{lt_id}.timing")

    # Annotation panel call-site timing substitutions (mode: annotate output-brief
    # callouts; panel slides in from right during the zoom.py annotate-segment
    # hold). Each annotation in frontmatter maps id (apN) -> in_recording_t +
    # out_recording_t. Times are recording-relative and converted to comp-absolute
    # by adding 5s (title card duration).
    for ann in fm.get("annotations") or []:
        ap_id = ann.get("id")
        if not ap_id:
            continue
        if "in_recording_t" in ann and "out_recording_t" in ann:
            in_rt = float(ann["in_recording_t"])
            out_rt = float(ann["out_recording_t"])
            if in_rt == 0.0 and out_rt == 0.0:
                # Retire sentinel — pass (0, 0) through unchanged so the
                # template's `annotatePanel` skip-clause fires.
                in_abs = 0.0
                out_abs = 0.0
            else:
                in_abs = in_rt + 5.0
                out_abs = out_rt + 5.0
            updated = _replace_annotate_panel_timing(new_html, ap_id, in_abs, out_abs)
            if updated != new_html:
                new_html = updated
                filled.append(f"{ap_id}.timing")

        # Panel content substitution — eyebrow / headline / body / source / badge.
        # See video-scriptwriting/SKILL.md § "Panel content authoring" for the
        # content contract (capability-not-specifics framing, 3-shape rotation,
        # subject-match to paired spotlight, source + badge required).
        panel = ann.get("panel") or {}
        if panel:
            soup_local = BeautifulSoup(new_html, "html.parser")
            parent = soup_local.find(id=ap_id)
            if parent is not None:
                if panel.get("eyebrow") and _set_text(parent.find(class_="ap-eyebrow"), panel["eyebrow"]):
                    filled.append(f"{ap_id}.eyebrow")
                if panel.get("headline") and _set_text(parent.find(class_="ap-headline"), panel["headline"]):
                    filled.append(f"{ap_id}.headline")
                if panel.get("body") and _set_text(parent.find(class_="ap-body"), panel["body"]):
                    filled.append(f"{ap_id}.body")
                if panel.get("source") and _set_text(parent.find(class_="ap-source"), panel["source"]):
                    filled.append(f"{ap_id}.source")
                if panel.get("badge") and _set_text(parent.find(class_="ap-badge"), panel["badge"]):
                    filled.append(f"{ap_id}.badge")
                new_html = str(soup_local)

    return new_html, filled


def recover_stale_backup(template_dir: Path, verbose: bool = False) -> bool:
    """If a previous interrupted run left .index.html.orig behind, restore it.
    Returns True if recovery happened.
    """
    index_path = template_dir / "index.html"
    backup_path = template_dir / ".index.html.orig"
    if backup_path.exists():
        shutil.copy2(backup_path, index_path)
        backup_path.unlink()
        if verbose:
            print(f"[render] recovered: restored template from .index.html.orig "
                  f"(previous run was interrupted)")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Per-video render pipeline.")
    parser.add_argument("video_id", help="Video ID like V1, V5, N3")
    parser.add_argument("--mode", choices=["preview", "final"], default="preview")
    parser.add_argument("--script", type=Path, help="Override script path")
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--quality", choices=["draft", "standard", "high"], default=None,
                        help="Render quality. Default: standard for --mode preview "
                             "(reviewing layout), high for --mode final (deliverable).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print plan without running render or copying files")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--allow-engineering", action="store_true",
                        help="Bypass the Customer's-chair framing pre-flight check that scans "
                             "the substituted HTML for engineering-vocabulary banned phrases "
                             "(parallel skill calls, MCP invocations, agent orchestration, "
                             "etc.). Use for instructional videos (I1–I4) where system-mechanics "
                             "framing IS the right register. Defaults to OFF — use_case videos "
                             "(V1–V16) fail-fast if banned phrases slip through QC #9.")
    args = parser.parse_args()

    # Mode-dependent quality default (Hyperframes guidance: standard for review,
    # high for final delivery, draft only when iterating on the template).
    if args.quality is None:
        args.quality = "high" if args.mode == "final" else "standard"

    print(f"[render] video={args.video_id}  mode={args.mode}  fps={args.fps}  quality={args.quality}")

    # 1. Find script
    script_path = find_script(args.video_id, args.script)
    print(f"[render] script:    {script_path.relative_to(PROJECT_ROOT)}")

    # 2. Parse frontmatter
    fm = parse_frontmatter(script_path)
    pipeline_type = fm.get("pipeline_type", "product_demo")
    template_family = fm.get("template", "product-demo")
    print(f"[render] pipeline:  {pipeline_type}  →  template family: {template_family}")

    # 3. Find template
    template_dir = find_template(template_family)
    print(f"[render] template:  {template_dir.relative_to(PROJECT_ROOT)}")

    # 4. Recover stale backup from any previously interrupted run
    recover_stale_backup(template_dir, verbose=args.verbose)

    # 5. Find recording (product demos)
    recording = None
    if pipeline_type == "product_demo":
        recording = find_recording(args.video_id, fm)
        print(f"[render] recording: {recording.relative_to(PROJECT_ROOT)}")

    # 6. Hash the script (cache key for avatar clip)
    script_h = hash_script(script_path)
    print(f"[render] script_hash: {script_h}")

    rec_dur = _get_video_duration(recording) if recording else None
    if rec_dur is not None:
        print(f"[render] rec dur:    {rec_dur:.2f}s  →  composition {5+rec_dur+7:.2f}s")

    # ── Mode-specific: avatar clip resolution (final only) ───────────────
    avatar_clip_path: Path | None = None
    if args.mode == "final":
        avatar_clip_path = (PROJECT_ROOT / "avatars" / "clips"
                            / f"{args.video_id}_{script_h}.mp4")
        if avatar_clip_path.exists():
            if args.verbose:
                print(f"[render] avatar:    cached at "
                      f"{avatar_clip_path.relative_to(PROJECT_ROOT)} (skip generation)")
        else:
            if args.verbose or args.dry_run:
                print(f"[render] avatar:    no cache at "
                      f"{avatar_clip_path.relative_to(PROJECT_ROOT)} → generating")
            try:
                generate_avatar_clip(script_path, avatar_clip_path,
                                     dry_run=args.dry_run, verbose=args.verbose)
            except RuntimeError as e:
                print(f"error: avatar generation failed: {e}", file=sys.stderr)
                sys.exit(2)

    if args.dry_run:
        # Show what substitution WOULD do
        index_path = template_dir / "index.html"
        original_html = index_path.read_text()
        _, slots_filled = apply_substitutions(original_html, fm, rec_dur)
        if args.mode == "final":
            slots_filled.append("avatar.video+audio.injected")
        print(f"[render] would-substitute slots: "
              f"{', '.join(slots_filled) if slots_filled else 'none (template content matches)'}")
        print("[render] --dry-run; stopping before any file writes.")
        return

    # 7. Apply per-video substitution into the template (Chunk 1.5)
    index_path = template_dir / "index.html"
    backup_path = template_dir / ".index.html.orig"
    original_html = index_path.read_text()
    substituted_html, slots_filled = apply_substitutions(original_html, fm, rec_dur)

    # 7a. Final-mode: also inject the avatar <video>+<audio> clip elements
    if args.mode == "final":
        substituted_html, injected = inject_avatar_clip(substituted_html, rec_dur or 0.0)
        if injected:
            slots_filled.append("avatar.video+audio.injected")

    # 7b. Customer's-chair framing pre-flight (Quality Check #9 defense-in-depth).
    # Scans the substituted HTML for engineering-vocabulary banned phrases that
    # QC #9 should have caught at script drafting time. Hard-fails the render
    # for use_case videos so a forgotten frontmatter line can't ship engineering
    # framing to a buyer audience. Bypassed via --allow-engineering for
    # instructional videos (I1–I4) where system-mechanics framing is correct.
    violations = check_customers_chair_compliance(
        substituted_html, allow_engineering=args.allow_engineering,
    )
    if violations:
        raise RuntimeError(
            "Customer's-chair framing violations detected in substituted HTML:\n"
            + "\n".join(f"  - banned phrase: {repr(p)}" for p in violations)
            + "\n\nThese engineering-vocabulary phrases are rejected per "
            "`references/production-principles.md` → Customer's-chair framing "
            "and `video-scriptwriting/SKILL.md` Quality Check #9. Rewrite the "
            "offending copy in audience-perspective vocabulary (outcome / stakes "
            "/ workflow-fit / methodology-credibility). For instructional videos "
            "where system-mechanics framing is correct, pass --allow-engineering."
        )

    template_modified = substituted_html != original_html
    if template_modified:
        shutil.copy2(index_path, backup_path)  # backup before write
        index_path.write_text(substituted_html)
        if args.verbose or slots_filled:
            print(f"[render] substituted {len(slots_filled)} slot(s): "
                  f"{', '.join(slots_filled)}")
    else:
        if args.verbose:
            print("[render] no substitutions — template content already matches script")

    try:
        # 8. Stage template (copy recording into template's assets/)
        if recording is not None:
            stage_template(template_dir, recording, "screen-recording.mp4",
                           verbose=args.verbose)

        # 8a. Final-mode: stage avatar clip too
        if args.mode == "final" and avatar_clip_path is not None and avatar_clip_path.exists():
            stage_template(template_dir, avatar_clip_path, "avatar.mp4",
                           verbose=args.verbose)

        # 9. Output path (Option C layout: outputs/V<N>/<mode>.mp4)
        output_dir = PROJECT_ROOT / "outputs" / args.video_id
        output_path = output_dir / f"{args.mode}.mp4"

        # 9a. Rotate previous render — keep last 2 (current + one previous)
        # so iteration runs can compare/rollback. Older -prev gets evicted.
        if output_path.exists():
            prev_path = output_path.with_name(f"{output_path.stem}-prev{output_path.suffix}")
            if prev_path.exists():
                prev_path.unlink()
            output_path.rename(prev_path)
            if args.verbose:
                print(f"[render] rotated: {output_path.name} → {prev_path.name}")

        # 10. Run hyperframes render
        render_seconds = run_hyperframes_render(
            template_dir, output_path, args.fps, args.quality, args.verbose,
        )

        # 11. Write manifest
        manifest_path = output_dir / "render-manifest.json"
        manifest = {
            "video_id": args.video_id,
            "mode": args.mode,
            "rendered_at": datetime.now(timezone.utc).isoformat(),
            "render_seconds_wall": round(render_seconds, 2),
            "script_path": str(script_path.relative_to(PROJECT_ROOT)),
            "script_hash": script_h,
            "template": template_family,
            "recording": str(recording.relative_to(PROJECT_ROOT)) if recording else None,
            "avatar_clip": (
                str(avatar_clip_path.relative_to(PROJECT_ROOT))
                if avatar_clip_path and avatar_clip_path.exists() else None
            ),
            "fps": args.fps,
            "quality": args.quality,
            "output": str(output_path.relative_to(PROJECT_ROOT)),
            "phase_5_chunk": "1+1.5+2",
            "substitution": {
                "applied": template_modified,
                "slots_filled": slots_filled,
            },
        }
        write_manifest(manifest_path, manifest)

        # 11a. Append to render-history.jsonl — full timeline of all renders for
        # this video. One JSON object per line. Survives -prev eviction; useful
        # for "what was rendered when, with what script hash, what slots filled."
        history_path = output_dir / "render-history.jsonl"
        with history_path.open("a") as f:
            f.write(json.dumps(manifest) + "\n")

        print(f"[render] done in {render_seconds:.1f}s")
        print(f"  output:   {output_path.relative_to(PROJECT_ROOT)}")
        print(f"  manifest: {manifest_path.relative_to(PROJECT_ROOT)}")
        print(f"  history:  {history_path.relative_to(PROJECT_ROOT)} (appended)")

    finally:
        # 12. Restore template
        if template_modified and backup_path.exists():
            shutil.copy2(backup_path, index_path)
            backup_path.unlink()
            if args.verbose:
                print("[render] template restored to original state")


if __name__ == "__main__":
    main()
