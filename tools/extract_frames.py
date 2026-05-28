#!/usr/bin/env python3
"""
extract_frames.py — dump periodic still frames from a recording so Claude can
read them with the Read tool when drafting a voiceover script.

Claude can't watch .mov files directly, but it can read JPG/PNG. Extracting a
frame every ~2 seconds produces a readable storyboard that covers the whole
recording at a manageable token cost. The index.md maps frame numbers to
timestamps so the drafted script can reference "0:15 — such and such" events
with real accuracy instead of guesses.

Usage:
  python3 extract_frames.py <recording.mov> <output_dir> [--every SECONDS] [--width PX]

Defaults: every=2 seconds, width=960 (downscaled; original 3420×2146 is
wasteful to read). Re-running overwrites the output directory.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def ffprobe_duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ], text=True).strip()
    return float(out)


def fmt_ts(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recording", type=Path)
    ap.add_argument("output_dir", type=Path)
    ap.add_argument("--every", type=float, default=2.0, help="Seconds between frames (default 2)")
    ap.add_argument("--width", type=int, default=960, help="Downscale width in px (default 960)")
    args = ap.parse_args()

    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg not found. Install: brew install ffmpeg")

    if not args.recording.exists():
        sys.exit(f"Recording not found: {args.recording}")

    out = args.output_dir
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    duration = ffprobe_duration(args.recording)
    fps = 1.0 / args.every

    print(f"Recording: {args.recording.name}  ({duration:.1f}s)")
    print(f"Extracting one frame every {args.every}s at width={args.width}px → {out}")

    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(args.recording),
        "-vf", f"fps={fps},scale={args.width}:-1",
        str(out / "frame_%04d.jpg"),
    ], check=True)

    frames = sorted(out.glob("frame_*.jpg"))
    index_lines = [
        f"# Frame index for {args.recording.name}",
        "",
        f"Recording duration: {duration:.1f}s. One frame every {args.every}s.",
        "Use this to map frame numbers to timestamps when drafting the VO script —",
        "stage directions in the script should cite the timestamp, not the frame number.",
        "",
        "| Frame | Timestamp |",
        "|---|---|",
    ]
    for i, f in enumerate(frames):
        ts = i * args.every
        index_lines.append(f"| `{f.name}` | {fmt_ts(ts)} ({ts:.1f}s) |")

    (out / "index.md").write_text("\n".join(index_lines) + "\n")
    print(f"Wrote {len(frames)} frames + index.md to {out}")


if __name__ == "__main__":
    main()
