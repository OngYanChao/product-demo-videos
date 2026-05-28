#!/usr/bin/env python3
"""
tools/verify_render.py — Mechanical proof that `final.mp4 = preview.mp4 + avatar slot only`.

Extracts sample frames at known beat timestamps from both renders, masks out
the avatar bounding box, and computes pixel diff over the rest of the frame.
The non-avatar regions should be ~0 drift; non-zero drift means the substitution
layer or template state diverged between the two renders.

Usage:
    python tools/verify_render.py V1
    python tools/verify_render.py V1 --threshold 1.5    # mean abs diff per channel
    python tools/verify_render.py V1 --keep-frames      # leave extracted frames in /tmp for inspection
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Avatar bounding box (% of 1920×1080 frame).
# Updated 2026-05-14 — corner-only pose (no bookend, no settle animation).
# Avatar fades in at t=5.0s already in the corner, holds, fades out at outro.
AVATAR_BBOX_CORNER = (74, 72, 96, 96)          # left, top, right, bottom (%)
AVATAR_BBOX_NONE = None                         # no mask — avatar invisible


def avatar_bbox_at(t: float) -> tuple[int, int, int, int] | None:
    """Avatar bbox at composition-absolute time `t`. None = no avatar visible."""
    if t < 5.0:
        return None                             # avatar still hidden (title card)
    elif t < 5.8:
        return None                             # avatar fading in (alpha-thin, ignore for diff)
    else:
        return AVATAR_BBOX_CORNER               # holds in corner through recording + outro fade


def pct_to_px(bbox_pct: tuple[int, int, int, int],
              w: int = 1920, h: int = 1080) -> tuple[int, int, int, int]:
    l, t, r, b = bbox_pct
    return (int(l/100 * w), int(t/100 * h), int(r/100 * w), int(b/100 * h))


def extract_frame(video: Path, t: float, out: Path) -> None:
    """Use ffmpeg to extract a single frame at t seconds."""
    cmd = ["ffmpeg", "-y", "-ss", str(t), "-i", str(video),
           "-frames:v", "1", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed extracting t={t}s from {video.name}:\n{r.stderr}")


def mean_abs_diff_outside_bbox(a: Path, b: Path,
                                 mask_bbox: tuple[int, int, int, int] | None) -> float:
    """Mean absolute pixel difference (per channel, scale 0-255) over the
    region OUTSIDE the avatar bbox. If mask_bbox is None, diff over full frame."""
    img_a = Image.open(a).convert("RGB")
    img_b = Image.open(b).convert("RGB")
    diff = ImageChops.difference(img_a, img_b)

    if mask_bbox is not None:
        # Black out the avatar region so it doesn't contribute to the diff.
        bx = pct_to_px(mask_bbox, *img_a.size)
        black = Image.new("RGB", (bx[2] - bx[0], bx[3] - bx[1]), (0, 0, 0))
        diff.paste(black, (bx[0], bx[1]))

    stat = ImageStat.Stat(diff)
    # Average across the 3 channels
    return sum(stat.mean) / len(stat.mean)


SAMPLE_TIMESTAMPS = [
    (2.5,  "title card (no avatar)"),
    (30.0, "recording mid (LT2 region, corner avatar)"),
    (68.0, "recording late (LT4 region, corner avatar)"),
    (84.0, "outro (avatar faded out)"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    ap.add_argument("video_id", help="Video ID like V1")
    ap.add_argument("--threshold", type=float, default=2.0,
                    help="Pass threshold: mean abs pixel diff per channel (0-255). Default 2.0.")
    ap.add_argument("--keep-frames", action="store_true",
                    help="Don't delete extracted frames after diff (for debugging)")
    args = ap.parse_args()

    out_dir = PROJECT_ROOT / "outputs" / args.video_id
    preview = out_dir / "preview.mp4"
    final = out_dir / "final.mp4"

    if not preview.exists():
        print(f"error: {preview} not found — run `python tools/render.py {args.video_id} --mode preview` first",
              file=sys.stderr)
        sys.exit(2)
    if not final.exists():
        print(f"error: {final} not found — run `python tools/render.py {args.video_id} --mode final` first",
              file=sys.stderr)
        sys.exit(2)

    work_dir = Path(tempfile.mkdtemp(prefix=f"verify_{args.video_id}_"))
    print(f"[verify] {args.video_id}: preview={preview.name}, final={final.name}")
    print(f"[verify] threshold: ≤{args.threshold:.2f} mean abs diff per channel\n")

    failed = 0
    for t, label in SAMPLE_TIMESTAMPS:
        a = work_dir / f"preview_{t:.1f}.jpg"
        b = work_dir / f"final_{t:.1f}.jpg"
        extract_frame(preview, t, a)
        extract_frame(final, t, b)
        bbox = avatar_bbox_at(t)
        diff = mean_abs_diff_outside_bbox(a, b, bbox)
        ok = diff <= args.threshold
        status = "  PASS" if ok else "  FAIL"
        bbox_str = f"mask {bbox}%" if bbox else "no mask"
        print(f"  t={t:5.1f}s  {label:<48}  {bbox_str:<28}  diff={diff:5.2f}  {status}")
        if not ok:
            failed += 1

    if not args.keep_frames:
        import shutil
        shutil.rmtree(work_dir)
    else:
        print(f"\n[verify] frames kept at {work_dir}")

    if failed:
        print(f"\n[verify] {failed}/{len(SAMPLE_TIMESTAMPS)} samples failed — non-avatar pixels drifted between preview and final.")
        print(f"         Likely cause: substitution layer changed non-avatar content, or template was hand-edited mid-flow.")
        sys.exit(1)
    else:
        print(f"\n[verify] all {len(SAMPLE_TIMESTAMPS)} samples passed — final = preview + avatar slot only ✓")


if __name__ == "__main__":
    main()
