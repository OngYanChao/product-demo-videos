#!/usr/bin/env python3
"""
tools/measure_highlight.py — Auto-fit a `highlight_region_pct` to text-row /
column boundaries so the annotate-mode highlight rectangle cleanly contains
its target words and does NOT cut neighboring rows or words at the edges.

Input: source video + source_t + a rough authored `highlight_region_pct` (the
user's first-pass guess at the rectangle). The tool extracts the source frame,
scans for text rows + column gaps within the rough region's neighborhood, and
emits the refined `highlight_region_pct` (snapped to gaps).

Programmatic measurement, never hand-tune. Run once per annotate directive
whose highlight is cutting words. Per Hard Rule #10 in `video-production-workflow`.

Usage:
    python tools/measure_highlight.py "screen recordings/V1/1vid_scrubbed.mp4" 50.25 \\
        --rough "27,58,44,6"             # x, y, w, h percentages
        [--zoom "25,24,50,73"]           # optional zoom_region for context
        [--row-threshold 50]             # brightness threshold for "text row"
        [--margin-pct 0.3]               # pad above/below the row run

Output: refined `[x, y, w, h]` JSON snippet ready to paste into 1vid_zooms.json.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def detect_text_rows(image_gray: np.ndarray, x_lo: int, x_hi: int,
                      threshold: int = 50, min_row_height_px: int = 4,
                      bright_px_threshold: int = 110
                      ) -> list[tuple[int, int]]:
    """Return [(start_y, end_y)] for each text row within column range [x_lo, x_hi].
    A 'text row' = a vertical run of rows that contain a meaningful number of
    individually-bright pixels (any pixel > `bright_px_threshold`). This
    catches sparse rows where short text like "246)." sits in an otherwise
    empty width — mean-brightness detection misses those because empty space
    dominates the mean. The `threshold` param is kept for backwards-compat
    callers but only applies as a lower bound on the bright-pixel count's
    fractional density (≥ 1% of the x slice).
    Runs shorter than `min_row_height_px` are filtered as noise.
    """
    width = x_hi - x_lo
    # Looser bound on what counts as "text in this row" so sparse content
    # like a short wrapped fragment ("246)." in a multi-line cell) isn't
    # missed. We then smooth with a 3-row dilation so isolated single rows
    # don't get filtered as noise.
    min_bright_per_row = max(5, int(width * 0.005))
    bright_count = (image_gray[:, x_lo:x_hi] > bright_px_threshold).sum(axis=1)
    is_text_raw = bright_count >= min_bright_per_row
    # Dilate by ±2 rows so a row passing is "supported" by nearby rows even if
    # individual rows have sub-threshold counts (text edges, anti-aliasing).
    is_text = is_text_raw.copy()
    for delta in (1, 2):
        is_text[:-delta] |= is_text_raw[delta:]
        is_text[delta:] |= is_text_raw[:-delta]
    rows: list[tuple[int, int]] = []
    in_run = False
    start = 0
    h = image_gray.shape[0]
    for y in range(h):
        if is_text[y]:
            if not in_run:
                start = y
                in_run = True
        else:
            if in_run:
                if y - start >= min_row_height_px:
                    rows.append((start, y))
                in_run = False
    if in_run and h - start >= min_row_height_px:
        rows.append((start, h))
    return rows


def detect_column_gaps(image_gray: np.ndarray, y_lo: int, y_hi: int,
                        threshold: int = 50, min_col_width_px: int = 6
                        ) -> list[tuple[int, int]]:
    """Return [(start_x, end_x)] for each text column within row range [y_lo, y_hi].
    A 'text column' = a horizontal run of pixels whose mean brightness across
    the y slice exceeds `threshold`. Used to find column boundaries for
    multi-column layouts (score table Factor / Score / Read / Trend).
    """
    col_brightness = image_gray[y_lo:y_hi, :].mean(axis=0)
    is_text = col_brightness > threshold
    cols: list[tuple[int, int]] = []
    in_run = False
    start = 0
    w = image_gray.shape[1]
    for x in range(w):
        if is_text[x]:
            if not in_run:
                start = x
                in_run = True
        else:
            if in_run:
                if x - start >= min_col_width_px:
                    cols.append((start, x))
                in_run = False
    if in_run and w - start >= min_col_width_px:
        cols.append((start, w))
    return cols


def snap_y_to_text_rows(rough_hr: list[float], src_w: int, src_h: int,
                         image_gray: np.ndarray, threshold: int = 50,
                         margin_pct: float = 0.3, intra_row_gap_pct: float = 2.0
                         ) -> tuple[float, float]:
    """Find the run of text rows that overlap the rough rectangle's y bounds
    and return (new_y_pct, new_h_pct) snapped to the gap ABOVE the first row
    and the gap BELOW the last row of the run.

    `intra_row_gap_pct`: gaps smaller than this percentage of frame height
    are treated as "within the same wrapped text block" (e.g. multi-line
    cell content); the function extends through them. Gaps larger than this
    are treated as paragraph/section boundaries; the run stops there.
    """
    hx0 = int(rough_hr[0] / 100.0 * src_w)
    hx1 = int((rough_hr[0] + rough_hr[2]) / 100.0 * src_w)
    hy0 = int(rough_hr[1] / 100.0 * src_h)
    hy1 = int((rough_hr[1] + rough_hr[3]) / 100.0 * src_h)

    rows = detect_text_rows(image_gray, hx0, hx1, threshold=threshold)
    if not rows:
        return rough_hr[1], rough_hr[3]

    # Find rows that intersect the rough rectangle.
    overlapping = [(s, e) for (s, e) in rows if e > hy0 and s < hy1]
    if not overlapping:
        # Rough rect is in a gap — return as-is.
        return rough_hr[1], rough_hr[3]

    # Extend forward and backward through small intra-row gaps to capture
    # multi-line wrapped text in the same cell/paragraph.
    intra_gap_px = intra_row_gap_pct / 100.0 * src_h
    first_s, first_e = overlapping[0]
    last_s, last_e = overlapping[-1]

    # Walk backward from `first_s` to include rows just above
    for s, e in reversed(rows):
        if e > first_s:
            continue
        if first_s - e <= intra_gap_px:
            first_s = s
            first_e = e if first_e <= first_s else first_e
        else:
            break
    # Walk forward from `last_e` to include rows just below
    for s, e in rows:
        if s < last_e:
            continue
        if s - last_e <= intra_gap_px:
            last_s = s if last_s >= last_e else last_s
            last_e = e
        else:
            break

    margin_px = margin_pct / 100.0 * src_h
    new_top = max(0, first_s - margin_px)
    new_bottom = min(src_h, last_e + margin_px)

    return new_top / src_h * 100.0, (new_bottom - new_top) / src_h * 100.0


def snap_x_to_column(rough_hr: list[float], src_w: int, src_h: int,
                      image_gray: np.ndarray, threshold: int = 50,
                      margin_pct: float = 0.2, intra_col_gap_pct: float = 0.8
                      ) -> tuple[float, float]:
    """Find the column run that the rough rectangle's x bounds intersect and
    snap to column boundaries. Important when the rough rect crosses a column
    gap and would otherwise cut words from a neighboring column.
    """
    hx0 = int(rough_hr[0] / 100.0 * src_w)
    hx1 = int((rough_hr[0] + rough_hr[2]) / 100.0 * src_w)
    hy0 = int(rough_hr[1] / 100.0 * src_h)
    hy1 = int((rough_hr[1] + rough_hr[3]) / 100.0 * src_h)

    cols = detect_column_gaps(image_gray, hy0, hy1, threshold=threshold)
    if not cols:
        return rough_hr[0], rough_hr[2]

    overlapping = [(s, e) for (s, e) in cols if e > hx0 and s < hx1]
    if not overlapping:
        return rough_hr[0], rough_hr[2]

    intra_gap_px = intra_col_gap_pct / 100.0 * src_w
    first_s, first_e = overlapping[0]
    last_s, last_e = overlapping[-1]

    # Walk left
    for s, e in reversed(cols):
        if e > first_s:
            continue
        if first_s - e <= intra_gap_px:
            first_s = s
        else:
            break
    # Walk right
    for s, e in cols:
        if s < last_e:
            continue
        if s - last_e <= intra_gap_px:
            last_e = e
        else:
            break

    margin_px = margin_pct / 100.0 * src_w
    new_left = max(0, first_s - margin_px)
    new_right = min(src_w, last_e + margin_px)

    return new_left / src_w * 100.0, (new_right - new_left) / src_w * 100.0


def main():
    parser = argparse.ArgumentParser(
        description="Snap an annotate `highlight_region_pct` to text-row + column boundaries.")
    parser.add_argument("video", type=Path, help="Source video (scrubbed recording)")
    parser.add_argument("source_t", type=float, help="Source timestamp (seconds)")
    parser.add_argument("--rough", required=True,
                        help="Rough authored highlight region as 'x,y,w,h' in percent")
    parser.add_argument("--zoom", help="Optional zoom_region_pct as 'x,y,w,h' in percent "
                                       "(used as outer bounds for the search)")
    parser.add_argument("--row-threshold", type=int, default=50,
                        help="Brightness threshold for 'is this a text row' (default 50; raise "
                             "for high-contrast captures, lower for dim UIs)")
    parser.add_argument("--margin-y-pct", type=float, default=0.3,
                        help="Y padding above/below the snapped row run (default 0.3%)")
    parser.add_argument("--intra-row-gap-pct", type=float, default=2.0,
                        help="Gaps smaller than this percent of frame height get merged into "
                             "one row run (default 2.0). Lower this when targeting individual "
                             "rows of a tightly-packed table where rows are <2% apart (e.g. "
                             "0.5 for a score panel with 6 rows in ~40% of frame height).")
    parser.add_argument("--margin-x-pct", type=float, default=0.3,
                        help="X padding left/right of the snapped column run (default 0.3%)")
    parser.add_argument("--skip-x", action="store_true",
                        help="Don't snap x bounds — only adjust y")
    parser.add_argument("--debug-overlay", type=Path,
                        help="Optional output PNG showing the snapped rectangle vs the rough one")
    args = parser.parse_args()

    rough = [float(p) for p in args.rough.split(",")]
    if len(rough) != 4:
        print("error: --rough must be 4 numbers (x,y,w,h)", file=sys.stderr)
        sys.exit(1)

    # Extract the source frame
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        out_png = Path(tf.name)
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-ss", f"{args.source_t:.6f}",
         "-i", str(args.video),
         "-frames:v", "1",
         str(out_png)],
        check=True,
    )

    img = Image.open(out_png).convert("RGB")
    src_w, src_h = img.size
    image_gray = np.array(img.convert("L"))

    # Snap y bounds
    new_y, new_h = snap_y_to_text_rows(
        rough, src_w, src_h, image_gray,
        threshold=args.row_threshold, margin_pct=args.margin_y_pct,
        intra_row_gap_pct=args.intra_row_gap_pct,
    )

    # Snap x bounds (with the snapped y range as context)
    if args.skip_x:
        new_x, new_w = rough[0], rough[2]
    else:
        new_hr_y = [rough[0], new_y, rough[2], new_h]
        new_x, new_w = snap_x_to_column(
            new_hr_y, src_w, src_h, image_gray,
            threshold=args.row_threshold, margin_pct=args.margin_x_pct,
        )

    refined = [round(new_x, 2), round(new_y, 2), round(new_w, 2), round(new_h, 2)]
    print(f"# Refined highlight_region_pct (snapped to text rows + columns)")
    print(f"# Source: {args.video.name}  t={args.source_t}s  {src_w}x{src_h}")
    print(f"#   Rough:    {rough}")
    print(f"#   Refined:  {refined}")
    print(f"\"highlight_region_pct\": {json.dumps(refined)}")

    if args.debug_overlay:
        from PIL import ImageDraw
        debug_img = img.copy()
        draw = ImageDraw.Draw(debug_img)
        # Rough in red
        rx = rough[0]/100*src_w; ry = rough[1]/100*src_h
        rw = rough[2]/100*src_w; rh = rough[3]/100*src_h
        draw.rectangle([rx, ry, rx+rw, ry+rh], outline=(255,0,0), width=6)
        # Refined in green
        nx = refined[0]/100*src_w; ny = refined[1]/100*src_h
        nw = refined[2]/100*src_w; nh = refined[3]/100*src_h
        draw.rectangle([nx, ny, nx+nw, ny+nh], outline=(0,255,0), width=6)
        debug_img.save(args.debug_overlay)
        print(f"# Debug overlay saved: {args.debug_overlay} (red=rough, green=refined)")


if __name__ == "__main__":
    main()
