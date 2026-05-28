#!/usr/bin/env python3
"""
tools/zoom.py — Zoom segments for screen recordings. Three modes:

  mode: "hold" (default) — Pause playback at source_t, ease into a zoomed view
    of a target region, hold the zoomed STILL frame for the segment duration,
    ease back out, then resume playback at source_t. The underlying video does
    not advance during the zoom. Used for dwell:y beats where VO discusses a
    settled visual (score panel, trajectory, bottom line).

  mode: "follow" — Apply a time-varying zoom transform to a range of frames
    that CONTINUE PLAYING. source[source_t:source_t+duration] plays through at
    1x while the camera eases in, holds at zoom_factor, then eases out. Used
    when the content is evolving and you want to zoom in on it without freezing
    (e.g. prompt typing, content reveal).

  mode: "annotate" — Pause playback at source_t, cut to a left-anchored crop
    of `zoom_region_pct` with `highlight_region_pct` vertically centered in
    the output frame. Apply a dim mask over the cropped view except over the
    highlight region (full brightness — soft-edged elliptical spotlight). Reserve
    the right ~38% of the output as black space — the template overlays the
    annotation panel (eyebrow/headline/body) there. Used for OUTPUT-BRIEF zooms
    (score panel, trajectory column, bottom-line verdict).

CURSOR-CLEAR RULE (workflow Hard Rule #16): zooms targeting the OUTPUT BRIEF
  content (the rendered text the viewer reads — score panel, trajectory,
  bottom line, etc.) must not trigger while the cursor is sitting on that
  text. Set `"wait_cursor_clear": true` on those zooms and the camera will
  auto-advance source_t until the cursor has moved outside region_pct (or
  fall back to base if no clear moment within DEFAULT_CURSOR_CLEAR_MAX_DELAY_S).
  DO NOT set on tool-call loading zooms (the chat activity area) — the cursor
  position over the chat is fine while the viewer is watching tool calls fire,
  not reading deliberately. Default is OFF (opt-in per directive).

Input: source MP4 + JSON list of zoom directives.
Output: MP4 with zoom segments inserted.

Each directive (positions and sizes are percentages of source frame, not pixels):
    {
        "source_t": 22.0,           # source-video timestamp where zoom triggers
        "duration": 8.0,            # total zoom segment in output (incl. ease in + out)
        "region_pct": [24, 4, 56, 26],  # [x, y, w, h] as % of source frame — defines the
                                        # FOCUS POINT (region center) for hold/follow modes.
        "zoom": 1.5,                # optional, default 1.5. Magnification factor at peak.
        "ease": 0.5,                # ease-in == ease-out duration in seconds
    }

For annotate-mode directives the schema replaces `region_pct` with
`zoom_region_pct` + `highlight_region_pct` + `callout_number`; see Hard Rule
#17 + #24 in `video-production-workflow/SKILL.md` for the contract.

Usage:
    python tools/zoom.py input.mp4 output.mp4 --zooms zooms.json
"""

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def get_video_info(video_path: Path) -> tuple[float, int, int, float]:
    """Returns (duration, width, height, fps)."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate",
         "-show_entries", "format=duration",
         "-of", "json", str(video_path)],
        capture_output=True, text=True,
    )
    info = json.loads(result.stdout)
    stream = info["streams"][0]
    width = int(stream["width"])
    height = int(stream["height"])
    fps_num, fps_den = stream["r_frame_rate"].split("/")
    fps = float(fps_num) / float(fps_den)
    duration = float(info["format"]["duration"])
    return duration, width, height, fps


def detect_cursor_position(video_path: Path, t: float, prev_dt: float = 0.15,
                            pixel_threshold: int = 50, min_motion_pixels: int = 5,
                            max_motion_pixels: int = 80,
                            bbox_max_pct: float = 15.0) -> tuple[float, float] | None:
    """
    Estimate cursor position at time `t` by comparing frame[t] to frame[t-prev_dt].
    When the cursor has just moved, the inter-frame diff shows a small localized
    blob; its centroid approximates where the cursor LANDED at time t.

    Returns (x_pct, y_pct) of source frame, or None if no cursor-sized motion
    was detected in that window (cursor static, or motion too diffuse/large to
    plausibly be the cursor — e.g. text rendering, content settling, UI fades).

    Thresholds are tuned for the macOS cursor at 480p downsample against Cowork
    dark chrome: cursor motion empirically produces 5-20 changed pixels with a
    bounding box < 10% of the frame. Content settling produces 40-200+ pixels
    spread across 30%+ of the frame — those get filtered.
    """
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return None

    if t - prev_dt < 0:
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        for label, ts in [("prev", t - prev_dt), ("curr", t)]:
            cmd = [
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-ss", f"{ts:.3f}",
                "-i", str(video_path),
                "-frames:v", "1",
                "-vf", "scale=480:-1,format=gray",
                f"{tmpdir}/{label}.png",
            ]
            subprocess.run(cmd, capture_output=True, check=False)

        prev_p = os.path.join(tmpdir, "prev.png")
        curr_p = os.path.join(tmpdir, "curr.png")
        if not (os.path.exists(prev_p) and os.path.exists(curr_p)):
            return None

        prev_a = np.array(Image.open(prev_p), dtype=np.int16)
        curr_a = np.array(Image.open(curr_p), dtype=np.int16)

    diff = np.abs(curr_a - prev_a)
    mask = diff > pixel_threshold
    changed = int(mask.sum())
    if not (min_motion_pixels <= changed <= max_motion_pixels):
        return None  # too little or too much motion to be a cursor

    ys, xs = np.where(mask)
    h, w = curr_a.shape
    bbox_w_pct = (xs.max() - xs.min()) / w * 100.0
    bbox_h_pct = (ys.max() - ys.min()) / h * 100.0
    if bbox_w_pct > bbox_max_pct or bbox_h_pct > bbox_max_pct:
        return None  # motion too spread out — content update, not cursor

    cy_px = float(ys.mean())
    cx_px = float(xs.mean())
    return (cx_px / w, cy_px / h)


def find_cursor_clear_source_t(
    video_path: Path,
    base_t: float,
    region_pct: list[float],
    *,
    max_delay: float = 4.0,    # see DEFAULT_CURSOR_CLEAR_MAX_DELAY_S below
    sample_dt: float = 0.25,   # see DEFAULT_CURSOR_CLEAR_SAMPLE_DT_S below
    pad_pct: float = 0.02,
) -> tuple[float, str]:
    """
    Per the cursor-clear rule (workflow Hard Rule #16): a hold-mode zoom must
    not trigger while the cursor is sitting on the text being zoomed.

    Scans frames from base_t forward in `sample_dt` increments. Tracks the
    last known cursor position via inter-frame motion detection. Returns the
    first t where cursor is *outside* `region_pct` (plus a small `pad_pct`
    buffer around the region).

    If no clear moment is found within `max_delay`, falls back to base_t and
    returns a reason string indicating fallback.

    Returns: (adjusted_source_t, status_string)
    """
    rx, ry, rw, rh = region_pct
    rx_min = max(0.0, rx / 100.0 - pad_pct)
    ry_min = max(0.0, ry / 100.0 - pad_pct)
    rx_max = min(1.0, (rx + rw) / 100.0 + pad_pct)
    ry_max = min(1.0, (ry + rh) / 100.0 + pad_pct)

    last_pos: tuple[float, float] | None = None
    detections = 0
    t = base_t
    end_t = base_t + max_delay
    while t <= end_t:
        pos = detect_cursor_position(video_path, t)
        if pos is not None:
            last_pos = pos
            detections += 1
        # If we have a known cursor position and it's outside the region, we're clear
        if last_pos is not None:
            x, y = last_pos
            if not (rx_min <= x <= rx_max and ry_min <= y <= ry_max):
                return (t, f"cursor-clear at t={t:.2f}s (cursor at {x*100:.1f}%, {y*100:.1f}%; "
                           f"region {rx:.0f}-{rx+rw:.0f}% × {ry:.0f}-{ry+rh:.0f}%; "
                           f"{detections} detection(s) over {t-base_t:.2f}s)")
        t += sample_dt

    return (base_t, f"cursor never cleared region within {max_delay:.1f}s "
                    f"(last known pos: {last_pos}); fallback to base_t={base_t:.2f}")


def render_held_still(input_path: Path, source_t: float, pause_s: float, fps: float,
                      src_w: int, src_h: int, output_path: Path, tmp_dir: Path) -> bool:
    """Render `pause_s` seconds of the still frame at `source_t` — un-zoomed, frozen.

    Used to insert breathing room between consecutive zoom segments so the viewer
    sees the camera fully zoom out, hold, then zoom back in to the next region.
    """
    # Two-step YUV-only pipeline (no PNG / RGB round-trip):
    #   (a) Extract a single-frame mp4 at source_t, BT.709/limited.
    #   (b) Stream-loop it for `pause_s` seconds with -c copy (no re-encode), so the
    #       output frames are bit-exact copies of (a). Result: zero colour shift
    #       between this held-still and the source playback before/after it.
    one_frame = tmp_dir / f"oneframe_{source_t:.3f}.mp4"
    extract = subprocess.run(
        ["ffmpeg", "-hide_banner", "-y",
         "-ss", f"{source_t:.6f}",
         "-i", str(input_path),
         "-frames:v", "1",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "10",
         "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709",
         "-colorspace", "bt709", "-color_range", "tv",
         "-an",
         str(one_frame)],
        capture_output=True, text=True,
    )
    if extract.returncode != 0:
        print(f"[zoom] one-frame extract for hold failed: {extract.stderr[-1500:]}", file=sys.stderr)
        return False

    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-stream_loop", "-1",
        "-i", str(one_frame),
        "-t", f"{pause_s:.4f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-g", "60", "-keyint_min", "60",
        "-pix_fmt", "yuv420p",
        "-color_primaries", "bt709", "-color_trc", "bt709",
        "-colorspace", "bt709", "-color_range", "tv",
        "-an",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[zoom] held-still pause failed at t={source_t}: {result.stderr[-1500:]}", file=sys.stderr)
        return False
    return True


def _ease_in_out_sine(p: float) -> float:
    """Matches the existing render_zoom_segment ease curve. p in [0, 1]."""
    return (1.0 - math.cos(math.pi * p)) / 2.0


def render_annotate_frame_pil(src_img: "Image.Image", alpha: float,
                                zoom_region_pct: list[float], highlight_region_pct: list[float],
                                callout_number: int, src_w: int, src_h: int) -> "Image.Image":
    """Render one frame of the annotate animation at progress `alpha` ∈ [0, 1].

    alpha = 0: full-frame view of source (no crop, no spotlight).
    alpha = 1: full-frame-width zoom composite (cropped to zoom_region_pct, scaled
      to fill the entire frame width, positioned so highlight_region_pct's vertical
      center lands at frame vertical center) with a soft-edged elliptical SPOTLIGHT
      centered on the highlight rectangle. The brief lands on the LEFT portion of
      the scaled crop; zoomed continuation of the recording (chat thread, etc.)
      fills the RIGHT portion where the panel overlays. The area inside the ellipse
      stays at full brightness; the area outside is dimmed at ANNOTATE_DIM_ALPHA
      opacity. A Gaussian blur on the spotlight mask gives the edge a gentle
      fadeout so the effect reads as lighting, not as a graphic shape.
    0 < alpha < 1: linearly interpolated state along all of the above axes.

    `callout_number` is kept in the signature for backwards compatibility — the
    panel on the right carries the numbered badge; no number is drawn on the
    recording itself (rectangle-border + numbered-dot rendering preserved in the
    code below in `if False:` blocks for future toggle).

    All interpolation is on linear alpha. Callers wrap alpha in an ease curve
    (easeInOutSine) before calling for the camera glide.
    """
    from PIL import ImageFont

    # Zoom-region in source pixels (target crop at alpha=1).
    zx = zoom_region_pct[0] / 100.0 * src_w
    zy = zoom_region_pct[1] / 100.0 * src_h
    zw = zoom_region_pct[2] / 100.0 * src_w
    zh = zoom_region_pct[3] / 100.0 * src_h

    # Highlight-region in source pixels.
    hx = highlight_region_pct[0] / 100.0 * src_w
    hy = highlight_region_pct[1] / 100.0 * src_h
    hw = highlight_region_pct[2] / 100.0 * src_w
    hh = highlight_region_pct[3] / 100.0 * src_h

    # Scaled-crop fills the FULL frame width (not just the left band). The panel
    # overlays the right portion of the scaled crop, not a black band. Brief lands
    # on the LEFT of the scaled crop because zoom_region's left edge is at the
    # brief's left edge; whatever's to the right of the brief in the zoom_region
    # appears in the right portion of the frame where the panel sits on top.
    target_w = float(src_w)

    # Composition-visible source-y range. With object-fit:cover + object-position:top,
    # a source taller than the comp aspect has its bottom cropped; only the top
    # `visible_h_in_src` pixels of source y are visible in the composition. The
    # highlight is centered on the comp's visible vertical midpoint, not the source
    # frame's geometric midpoint.
    src_aspect = src_w / src_h
    if src_aspect >= ANNOTATE_COMP_ASPECT:
        visible_h_in_src = src_h
    else:
        visible_h_in_src = src_w / ANNOTATE_COMP_ASPECT

    # Interpolated crop window (full frame → zoom_region).
    crop_left = zx * alpha
    crop_top = zy * alpha
    crop_w = src_w - (src_w - zw) * alpha
    crop_h = src_h - (src_h - zh) * alpha

    # Interpolated output width (src_w → target_w). Right band grows from 0 → 38%.
    output_w = src_w - (src_w - target_w) * alpha
    scale = output_w / crop_w
    scaled_h = crop_h * scale

    # Target y_offset computed at alpha=1 (left-anchored composite), then linearly
    # interpolated by alpha. At alpha=0 y_offset=0 (no shift); at alpha=1 the
    # highlight's vertical center lands at the comp's visible vertical center
    # (when possible — clamped below if strict centering would create black bands).
    scale_at_1 = target_w / zw
    hl_y_in_scaled_at_1 = (hy - zy) * scale_at_1
    hl_h_scaled_at_1 = hh * scale_at_1
    hl_cy_in_scaled_at_1 = hl_y_in_scaled_at_1 + hl_h_scaled_at_1 / 2.0
    scaled_h_at_1 = zh * scale_at_1
    y_offset_strict = visible_h_in_src / 2.0 - hl_cy_in_scaled_at_1
    # Clamp y_offset so the scaled crop covers the comp's visible vertical extent
    # (no black bands top or bottom). If the highlight is near a source edge and
    # strict centering would push the scaled crop off the visible area, the
    # highlight ends up off-center but the frame stays fully filled with content.
    y_offset_min = visible_h_in_src - scaled_h_at_1     # bottom of crop at visible bottom
    y_offset_max = 0.0                                  # top of crop at visible top
    y_offset_target = max(y_offset_min, min(y_offset_max, y_offset_strict))
    y_offset = y_offset_target * alpha

    # Crop, resize, paste onto black canvas.
    # The scaled-crop fills the full frame width (target_w = src_w) — the
    # zoom_region is scaled up to occupy the entire visible width, with the
    # brief on the LEFT portion of the scaled crop and zoomed continuation
    # of the recording (chat thread, etc.) extending across the RIGHT portion
    # where the panel overlays. No black band, no source backdrop at natural
    # scale — the eye sees a single continuous zoomed recording. The canvas
    # is initialized black for safety (covers any rounding gaps); in practice
    # the scaled-crop covers the whole frame at alpha=1.
    crop_box = (int(crop_left), int(crop_top),
                int(crop_left + crop_w), int(crop_top + crop_h))
    crop = src_img.crop(crop_box)
    scaled = crop.resize((max(1, int(output_w)), max(1, int(scaled_h))), Image.LANCZOS)

    canvas = Image.new("RGBA", (src_w, src_h), (0, 0, 0, 255))
    canvas.paste(scaled, (0, int(y_offset)))

    # Highlight rect in OUTPUT coords at the current alpha.
    hl_x_in_scaled = (hx - crop_left) * scale
    hl_y_in_scaled = (hy - crop_top) * scale
    hl_w_scaled = hw * scale
    hl_h_scaled = hh * scale
    hl_out_x = int(round(hl_x_in_scaled))
    hl_out_y = int(round(hl_y_in_scaled + y_offset))
    hl_out_w = int(round(hl_w_scaled))
    hl_out_h = int(round(hl_h_scaled))

    # Scaled-crop bbox in output coords (clipped to canvas).
    crop_left_out = 0
    crop_top_out = max(0, int(y_offset))
    crop_right_out = min(src_w, int(output_w))
    crop_bottom_out = min(src_h, int(y_offset + scaled_h))

    # Spotlight mask — a soft-edged oval (ellipse) centered on the highlight
    # rect lets the highlight area through at full brightness; everything else
    # in the scaled-crop area is dimmed. Replaces the earlier rectangle-border-
    # plus-cutout-rectangle scheme. The dim layer's alpha is built as a single-
    # channel mask (full alpha outside ellipse, zero inside ellipse) then
    # Gaussian-blurred so the ellipse fades softly into the dim instead of
    # snapping at a hard edge. opacity scales with alpha so the spotlight
    # fades in over the ease-in.
    from PIL import ImageFilter
    dim_alpha_now = int(round(ANNOTATE_DIM_ALPHA * alpha))
    if dim_alpha_now > 0:
        # Ellipse bounds: CIRCUMSCRIBE the highlight rectangle. Scale half-axes
        # by √2 (≈1.414) so the ellipse passes through the rect's corners — i.e.
        # every pixel inside the rect is inside the bright zone, no matter how
        # corner-y the text is. (Earlier additive-pad math gave rx=a+small,
        # ry=b+small — that ellipse cuts INSIDE the rect at the corners, since
        # the equation (a/rx)²+(b/ry)²<=1 fails at corner (a, b) when rx≈a,
        # ry≈b. Tall paragraphs with corner-filling text fell into the dim.)
        #
        # Shape adapts to rect aspect: a flat rect → flat oval; a square rect →
        # a circle. Aspect always matches the highlight, sized to contain it.
        # The Gaussian blur below adds the soft-edge transition past these
        # bounds — so the effective bright spotlight extends a bit further
        # than the strict ellipse, but no rect pixel is ever in the dim zone.
        hl_cx = hl_out_x + hl_out_w / 2.0
        hl_cy = hl_out_y + hl_out_h / 2.0
        CIRCUMSCRIBE = 1.4142135623730951   # √2 — minimum scale for the ellipse to contain the rect
        # Small additive buffer (~0.4% src dim) on top of the √2 scale so the
        # blur radius doesn't eat back into the rect from outside.
        rx = (hl_out_w / 2.0) * CIRCUMSCRIBE + src_w * 0.004
        ry = (hl_out_h / 2.0) * CIRCUMSCRIBE + src_h * 0.008

        # Build single-channel mask: dim_alpha_now outside ellipse, 0 inside.
        # Restrict the dim to the scaled-crop bbox. With target_w = src_w the
        # bbox now covers the whole frame width, so the dim mask effectively
        # covers the full visible scaled-crop area. The ellipse spotlight
        # punches the bright hole over the highlight.
        mask = Image.new("L", (src_w, src_h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rectangle([crop_left_out, crop_top_out, crop_right_out, crop_bottom_out],
                            fill=dim_alpha_now)
        mask_draw.ellipse([hl_cx - rx, hl_cy - ry, hl_cx + rx, hl_cy + ry], fill=0)

        # Gaussian blur the mask so the ellipse edge is a soft gradient
        # (~3-5% of frame height worth of blur radius). Without the blur the
        # spotlight has a hard cut-out edge that reads as a graphic shape
        # rather than a lighting effect.
        blur_radius = max(8, src_h * 0.02)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # Build the black-with-alpha-from-mask dim layer.
        dim_layer = Image.new("RGBA", (src_w, src_h), (0, 0, 0, 255))
        dim_layer.putalpha(mask)
        canvas = Image.alpha_composite(canvas, dim_layer)

    # Rectangle-border highlight — retired 2026-05-19 in favor of the soft-edged
    # elliptical spotlight (above). Code preserved for future toggle: a tighter
    # rectangle-with-hard-edges style might suit videos where the brand wants a
    # diagram/UI feel rather than a lighting feel. Re-enable per directive via a
    # `border_style: "box"` directive flag and gate this block on it.
    if False:  # border_style="box" path — wire up if a future video needs it
        border_alpha_now = int(round(255 * alpha))
        if border_alpha_now > 8:
            border_overlay = Image.new("RGBA", (src_w, src_h), (0, 0, 0, 0))
            border_draw = ImageDraw.Draw(border_overlay)
            pad = ANNOTATE_HIGHLIGHT_PAD_PX
            border_color = ANNOTATE_HIGHLIGHT_BORDER_COLOR[:3] + (border_alpha_now,)
            border_draw.rectangle(
                [hl_out_x - pad, hl_out_y - pad,
                 hl_out_x + hl_out_w + pad, hl_out_y + hl_out_h + pad],
                outline=border_color,
                width=ANNOTATE_HIGHLIGHT_BORDER_PX,
            )
            canvas = Image.alpha_composite(canvas, border_overlay)

    # Numbered callout dot — disabled 2026-05-19 per user feedback ("remove the
    # numbering beside the spotlight"). The numbered badge in the right-side
    # panel (template's .ap-number) still carries the callout number so the
    # ordering signal is preserved; the dot beside the highlight was redundant
    # once the spotlight's bright area itself draws the eye. Re-enable per
    # directive by reading `z.get("show_callout_dot", False)` and gating this
    # block on it — code preserved below in a no-op branch for easy restore.
    if False:  # show_callout_dot path — wire up if a future video needs it
        dot_alpha_now = int(round(255 * alpha))
        if dot_alpha_now > 8:
            dot_overlay = Image.new("RGBA", (src_w, src_h), (0, 0, 0, 0))
            dot_draw = ImageDraw.Draw(dot_overlay)
            dot_cx = hl_out_x - ANNOTATE_HIGHLIGHT_PAD_PX - ANNOTATE_CALLOUT_DOT_GAP_PX
            dot_cy = hl_out_y + hl_out_h // 2
            r = ANNOTATE_CALLOUT_DOT_RADIUS_PX
            dot_color = ANNOTATE_CALLOUT_DOT_COLOR[:3] + (dot_alpha_now,)
            dot_draw.ellipse([dot_cx - r, dot_cy - r, dot_cx + r, dot_cy + r], fill=dot_color)
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",
                                          ANNOTATE_CALLOUT_FONT_SIZE_PX)
            except (OSError, IOError):
                font = ImageFont.load_default()
            text = str(callout_number)
            text_bbox = dot_draw.textbbox((0, 0), text, font=font)
            tw = text_bbox[2] - text_bbox[0]
            th = text_bbox[3] - text_bbox[1]
            text_color = (255, 255, 255, dot_alpha_now)
            dot_draw.text(
                (dot_cx - tw // 2 - text_bbox[0], dot_cy - th // 2 - text_bbox[1]),
                text, fill=text_color, font=font,
            )
            canvas = Image.alpha_composite(canvas, dot_overlay)

    return canvas


def render_annotate_segment(input_path: Path, source_t: float, duration: float,
                             ease: float, zoom_region_pct: list[float],
                             highlight_region_pct: list[float], callout_number: int,
                             src_w: int, src_h: int, fps: float,
                             output_path: Path, tmp_dir: Path, segment_id: str = "0") -> bool:
    """Render an animated annotate-mode segment:

        [ease-in]   `ease` seconds — camera glides from full-frame view to the
                    left-anchored composite. Dim mask + highlight border + numbered
                    callout dot fade in via alpha. easeInOutSine curve.
        [hold]      `duration - 2 * ease` seconds — held composite (alpha=1).
        [ease-out]  `ease` seconds — reverse of ease-in. Composite fades back out
                    to the full-frame source frame.

    Pipeline: render N+1 unique PNGs at alpha = easeInOutSine(0/N..N/N), use a
    numbered image sequence with hardlinks for the held frames and symlinks
    pointing into the same files for the ease-out (mirror of ease-in).

    Validates that highlight_region_pct is fully contained within zoom_region_pct.
    """
    # Validate regions
    for name, r in [("zoom_region_pct", zoom_region_pct),
                    ("highlight_region_pct", highlight_region_pct)]:
        if not (len(r) == 4 and all(isinstance(v, (int, float)) for v in r)):
            print(f"[zoom] {name} must be 4 numbers, got {r}", file=sys.stderr)
            return False
        x, y, w, h = r
        if not (0 <= x <= 100 and 0 <= y <= 100 and 0 < w <= 100 and 0 < h <= 100):
            print(f"[zoom] {name} out of bounds: {r}", file=sys.stderr)
            return False
        if x + w > 100 + 0.01 or y + h > 100 + 0.01:
            print(f"[zoom] {name} extends past frame edge: {r}", file=sys.stderr)
            return False

    zx, zy, zw, zh = zoom_region_pct
    hx, hy, hw, hh = highlight_region_pct
    if not (zx - 0.01 <= hx and hx + hw <= zx + zw + 0.01
            and zy - 0.01 <= hy and hy + hh <= zy + zh + 0.01):
        print(f"[zoom] highlight_region_pct {highlight_region_pct} must be fully inside "
              f"zoom_region_pct {zoom_region_pct}", file=sys.stderr)
        return False

    # Aspect validation: the scaled crop must be tall enough to fill the comp's
    # visible vertical extent — otherwise black bands appear above and/or below
    # the scaled crop in the rendered composition. The user's expectation is dim
    # everywhere except the highlight, not solid black.
    #
    # scaled_h = zh_px * (target_w / zw_px) where target_w = src_w (full frame).
    # For scaled_h >= visible_h_in_src:
    #   zh_pct/zw_pct >= visible_h_in_src / src_h
    src_aspect = src_w / src_h
    visible_h_in_src = src_h if src_aspect >= ANNOTATE_COMP_ASPECT else src_w / ANNOTATE_COMP_ASPECT
    target_w_px = float(src_w)
    required_ratio = visible_h_in_src * src_w / (target_w_px * src_h)
    actual_ratio = zh / zw
    if actual_ratio < required_ratio - 0.005:
        min_zh = zw * required_ratio
        print(f"[zoom] zoom_region_pct {zoom_region_pct} aspect zh/zw={actual_ratio:.3f} is too "
              f"shallow — the scaled crop won't fill the composition's visible height and the "
              f"top/bottom of the panel area will render as solid black instead of dimmed. "
              f"Increase zh to at least {min_zh:.1f}% (or decrease zw proportionally). "
              f"Required zh/zw >= {required_ratio:.3f} for {src_w}×{src_h} source @ "
              f"{ANNOTATE_COMP_ASPECT:.3f} comp aspect.", file=sys.stderr)
        return False

    if duration <= 2 * ease:
        print(f"[zoom] annotate duration {duration} must be > 2 * ease ({ease})", file=sys.stderr)
        return False

    ease_frames = int(round(ease * fps))
    hold_frames = int(round((duration - 2 * ease) * fps))
    total_frames = ease_frames + hold_frames + ease_frames

    # 1. Extract source frame at source_t as PNG (load once into memory).
    still_png = tmp_dir / f"annotate_still_{segment_id}.png"
    extract = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-ss", f"{source_t:.6f}",
         "-i", str(input_path),
         "-frames:v", "1",
         str(still_png)],
        capture_output=True, text=True,
    )
    if extract.returncode != 0 or not still_png.exists():
        print(f"[zoom] frame extract failed at t={source_t}: {extract.stderr[-1500:]}", file=sys.stderr)
        return False

    src_img = Image.open(still_png).convert("RGBA")

    # 2. Render ease-in PNGs: N+1 unique frames at alpha = easeInOutSine(i/N) for i=0..N.
    #    Frame 0 is full source (alpha=0). Frame N is the held composite (alpha=1).
    frame_dir = tmp_dir / f"annotate_frames_{segment_id}"
    frame_dir.mkdir(parents=True, exist_ok=True)

    ease_unique_paths: list[Path] = []
    for i in range(ease_frames + 1):
        p = i / ease_frames if ease_frames > 0 else 1.0
        alpha = _ease_in_out_sine(p)
        png_path = frame_dir / f"unique_{i:06d}.png"
        frame = render_annotate_frame_pil(
            src_img, alpha, zoom_region_pct, highlight_region_pct,
            callout_number, src_w, src_h,
        )
        frame.convert("RGB").save(png_path, "PNG", optimize=False, compress_level=1)
        ease_unique_paths.append(png_path)

    held_png = ease_unique_paths[-1]   # frame at alpha=1

    # 3. Assemble the image sequence directory.
    #    Frames 0..ease_frames        = ease-in (unique_000000.png .. unique_{ease_frames:06d}.png)
    #    Frames ease_frames+1..ease_frames+hold_frames = held composite (hardlinks to held_png)
    #    Frames ease_frames+hold_frames+1..total_frames-1 = ease-out (hardlinks back to ease-in unique frames in reverse)
    seq_dir = tmp_dir / f"annotate_seq_{segment_id}"
    seq_dir.mkdir(parents=True, exist_ok=True)

    def _link(src: Path, dst: Path) -> None:
        if dst.exists():
            dst.unlink()
        try:
            os.link(src, dst)
        except OSError:
            # Cross-device or unsupported fs — fall back to copy.
            import shutil as _sh
            _sh.copy2(src, dst)

    idx = 0
    # ease-in
    for i in range(ease_frames + 1):
        _link(ease_unique_paths[i], seq_dir / f"{idx:06d}.png")
        idx += 1
    # held composite
    for _ in range(hold_frames - 1):     # -1 because alpha=1 was already placed at end of ease-in
        _link(held_png, seq_dir / f"{idx:06d}.png")
        idx += 1
    # ease-out (mirror of ease-in, skip the held duplicate)
    for i in range(ease_frames - 1, -1, -1):
        _link(ease_unique_paths[i], seq_dir / f"{idx:06d}.png")
        idx += 1

    if idx != total_frames:
        print(f"[zoom] annotate frame-count mismatch: assembled {idx}, expected {total_frames}",
              file=sys.stderr)
        return False

    # 4. Encode the image sequence to mp4.
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-framerate", f"{fps}",
        "-start_number", "0",
        "-i", str(seq_dir / "%06d.png"),
        "-frames:v", f"{total_frames}",
        "-r", f"{fps}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-g", "60", "-keyint_min", "60",
        "-pix_fmt", "yuv420p",
        "-color_primaries", "bt709", "-color_trc", "bt709",
        "-colorspace", "bt709", "-color_range", "tv",
        "-an",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[zoom] annotate render failed at t={source_t}: {result.stderr[-1500:]}", file=sys.stderr)
        return False
    return True


def render_source_segment(input_path: Path, start: float, end: float,
                          output_path: Path, fps: float,
                          drop_duplicates: bool = False) -> bool:
    """Trim a section of the source video, no zoom applied.

    If `drop_duplicates` is True, apply `mpdecimate` to drop near-identical
    consecutive frames, then re-time the kept frames at a constant `fps`. Used
    to scrub held-frame artifacts that scrub.py left in the source (e.g.
    short user-reading static periods that didn't trip the loading-freeze
    detector). Result: the output is shorter than `end - start` by the duration
    of the dropped frames — concat handles this naturally, and the rest of the
    zoom timeline shifts by the same amount.
    """
    vf_filter = (f"mpdecimate,setpts=N/FRAME_RATE/TB,fps={fps}"
                 if drop_duplicates else None)
    # -ss and -t must both be INPUT options (before -i) so the read-window is
    # limited at the input side. With -t as an OUTPUT option (after -i), ffmpeg
    # would pad the output with frame repeats to hit the requested duration —
    # silently undoing the work of mpdecimate.
    cmd = ["ffmpeg", "-hide_banner", "-y",
           "-ss", f"{start:.6f}",
           "-t", f"{end - start:.6f}",
           "-i", str(input_path)]
    if vf_filter:
        cmd.extend(["-vf", vf_filter])
    else:
        cmd.extend(["-r", f"{fps}"])
    cmd.extend(["-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-g", "60", "-keyint_min", "60",
                "-pix_fmt", "yuv420p",
                "-color_primaries", "bt709", "-color_trc", "bt709",
                "-colorspace", "bt709", "-color_range", "tv",
                "-an",
                str(output_path)])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[zoom] source segment failed: {result.stderr[-1500:]}", file=sys.stderr)
        return False
    return True


DEFAULT_ZOOM_FACTOR = 1.5             # focus-point magnification — gentle nudge, not a snap
DEFAULT_ZOOM_EASE_S = 1.5             # seconds — duration of zoom-in (and zoom-out) ease.
DEFAULT_CURSOR_CLEAR_MAX_DELAY_S = 4.0  # seconds — max we'll wait past the requested source_t
                                        # for the cursor to move outside the zoom region. If not
                                        # cleared within this window, fall back to original source_t.
DEFAULT_CURSOR_CLEAR_SAMPLE_DT_S = 0.25 # how often to check cursor position
                                      # Slow + smooth feel: the camera takes 1.5s to glide
                                      # from full-frame to peak zoom, and 1.5s to glide back.
                                      # The `ease` field in the zoom JSON is optional; if
                                      # omitted, this default applies. easeInOutSine curve
                                      # is wrapped around the linear ramp.
DEFAULT_INTER_ZOOM_PAUSE_S = 1.5      # seconds — minimum gap of un-zoomed playback between
                                      # consecutive zooms. If two zooms share a source_t (no
                                      # natural source playback between them), this pause is
                                      # inserted as a held still. If the natural source-playback
                                      # gap is already >= this, no extra pause is added.
DEFAULT_PRE_ZOOM_HOLD_S = 0.0         # seconds — held still inserted RIGHT BEFORE the zoom starts.
                                      # Set per-zoom via "pre_zoom_hold".

# ── Annotate mode visual constants ──
# These are the framing/dim/highlight/callout parameters for `mode: "annotate"`.
# The right ANNOTATE_PANEL_WIDTH_PCT % of the output frame is left BLACK in zoom.py
# output; the template overlays the annotation panel (eyebrow/headline/body/stats)
# in that space. Recording's content fills the left (100 - panel_width) %.
ANNOTATE_PANEL_WIDTH_PCT = 38.0       # right band reserved for template panel
ANNOTATE_DIM_ALPHA = 153              # 0..255 — dim opacity over the cropped view EXCEPT the
                                      # highlight rect. 153/255 ≈ 60% dim — readable but de-emphasised.
ANNOTATE_HIGHLIGHT_BORDER_PX = 4      # outline width around the highlight rectangle (source pixels)
ANNOTATE_HIGHLIGHT_PAD_PX = 12        # gap between highlight content and its outline (source pixels)
ANNOTATE_HIGHLIGHT_BORDER_COLOR = (84, 116, 152, 255)  # CG navy-400 (#547498), "Accent Blue".
                                      # 2026-05-19: switched from orange (#ED7D31) per user
                                      # request to a brand blue. The kit explicitly lists this
                                      # token for "borders, subtle highlights". Mid-tone so it's
                                      # visible against the dark recording UI but still in the
                                      # brand-blue family (pairs visually with the navy panel).
                                      # Navy-900 was tried first but too dark — blended into the
                                      # UI background. Callout dot stays orange for contrast.
ANNOTATE_CALLOUT_DOT_RADIUS_PX = 32   # numbered dot at highlight's left edge (source pixels)
ANNOTATE_CALLOUT_DOT_COLOR = (84, 116, 152, 255)   # CG navy-400, matches highlight border.
                                      # 2026-05-19: switched dot from orange to navy-400 so the
                                      # callout marker pairs visually with the border + panel
                                      # rather than competing as a separate accent. The orange
                                      # is now reserved for the title-card accent + panel
                                      # progress-bar header only.
ANNOTATE_CALLOUT_TEXT_COLOR = (255, 255, 255, 255)
ANNOTATE_CALLOUT_DOT_GAP_PX = 28      # distance from highlight left edge to callout dot center
ANNOTATE_CALLOUT_FONT_SIZE_PX = 38    # source pixels
ANNOTATE_COMP_ASPECT = 16.0 / 9.0     # the Hyperframes composition aspect (1920×1080). zoom.py
                                      # outputs at src dims; render.py composes that via
                                      # object-fit: cover + object-position: top center. For
                                      # source aspect < comp aspect (e.g. V1.2's 16:10 native),
                                      # only the top portion of the source is visible in the
                                      # comp. The annotate composite centers the highlight at
                                      # the *visible* area's vertical center (comp y=540), not
                                      # the source frame center — otherwise the highlight lands
                                      # ~60px below comp center on 16:10 sources.
DEFAULT_ANNOTATE_EASE_S = 1.0         # seconds — duration of zoom-in (and zoom-out) ease for
                                      # mode: annotate. Camera glides from full-frame to the
                                      # left-anchored composite over this duration, while the
                                      # dim mask + highlight border + callout dot fade in.
                                      # easeInOutSine curve. Shorter than hold-mode's 1.5s
                                      # because the panel slide-in (template GSAP) is 0.5s and
                                      # the animations should feel light and snappy together.



def render_zoom_segment(input_path: Path, source_t: float, duration: float,
                        ease: float, region_pct: list[float],
                        src_w: int, src_h: int, fps: float,
                        output_path: Path, tmp_dir: Path,
                        zoom_factor: float = DEFAULT_ZOOM_FACTOR,
                        segment_id: str = "0") -> bool:
    """Render a held-frame zoom segment (ease in -> hold -> ease out).

    Focus-point zoom: the camera pushes toward the *center* of `region_pct` at
    the given `zoom_factor` (default 1.5x). The region's width/height locate
    the centroid only — they don't size the crop to fit the region exactly.
    """
    x_pct, y_pct, w_pct, h_pct = region_pct
    if not (0 <= x_pct <= 100 and 0 <= y_pct <= 100 and 0 < w_pct <= 100 and 0 < h_pct <= 100):
        print(f"[zoom] invalid region_pct: {region_pct}", file=sys.stderr)
        return False
    if x_pct + w_pct > 100 or y_pct + h_pct > 100:
        print(f"[zoom] region_pct extends past frame edge", file=sys.stderr)
        return False
    if zoom_factor <= 1.0:
        print(f"[zoom] zoom_factor must be > 1.0, got {zoom_factor}", file=sys.stderr)
        return False

    # Focus point = region centroid (in source pixel coords)
    cx = src_w * (x_pct + w_pct / 2.0) / 100.0
    cy = src_h * (y_pct + h_pct / 2.0) / 100.0
    zoom = zoom_factor

    # zoompan x/y are the top-left of the crop window (size src_w/zoom × src_h/zoom)
    # in SOURCE coords. Centered on (cx,cy) at peak zoom: top-left = (cx - src_w/(2z), cy - src_h/(2z)).
    # Clamp so the crop window stays inside the source frame (no black bars).
    x_target = max(0.0, min(cx - src_w / (2.0 * zoom), src_w - src_w / zoom))
    y_target = max(0.0, min(cy - src_h / (2.0 * zoom), src_h - src_h / zoom))

    # 1. Extract still frame at source_t as a single-frame YUV mp4 (NOT PNG). Keeping
    #    the freeze-frame in YUV (same colour space + range as the source playback)
    #    eliminates the brightness/colour shift that a YUV→RGB→YUV PNG round-trip
    #    introduces at the zoom↔playback boundary.
    still_path = tmp_dir / f"still_{source_t:.3f}.mp4"
    extract = subprocess.run(
        ["ffmpeg", "-hide_banner", "-y",
         "-ss", f"{source_t:.6f}",
         "-i", str(input_path),
         "-frames:v", "1",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "10",
         "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709",
         "-colorspace", "bt709", "-color_range", "tv",
         "-an",
         str(still_path)],
        capture_output=True, text=True,
    )
    if extract.returncode != 0:
        print(f"[zoom] frame extract failed at t={source_t}: {extract.stderr[-1500:]}", file=sys.stderr)
        return False

    # 2. Build piecewise interpolation using zoompan
    # alpha: 0 (full frame) -> 1 (peak zoom) -> 0  (parameterised by output time)
    # We compute a piecewise-LINEAR alpha across the ease/hold/ease windows, then
    # wrap it in easeInOutSine so the camera glides in/out smoothly (no linear-ramp
    # snap). easeInOutSine: f(p) = (1 - cos(PI * p)) / 2.
    hold_end = duration - ease
    # zoompan uses commas as separators inside expressions, so escape them with backslash
    alpha_linear = (
        f"if(lt(out_time\\,{ease})\\,out_time/{ease}\\,"
        f"if(lt(out_time\\,{hold_end})\\,1\\,"
        f"1-(out_time-{hold_end})/{ease}))"
    )
    alpha = f"(1-cos(PI*({alpha_linear})))/2"
    z_expr = f"1+({zoom}-1)*({alpha})"
    # At alpha=0 (Z=1), the crop window IS the full frame, so top-left must be (0,0).
    # At alpha=1 (Z=zoom), top-left is (x_target, y_target) — centered on the focus
    # point and clamped to source bounds. Linear interpolate between them.
    x_expr = f"({x_target})*({alpha})"
    y_expr = f"({y_target})*({alpha})"

    total_frames = int(round(duration * fps))

    # 3. Build ffmpeg input list and filter graph.
    # `-stream_loop -1` loops the single-frame mp4 indefinitely (combined with
    # `-frames:v total_frames` on the output, exactly total_frames frames are emitted).
    ffmpeg_inputs: list[str] = ["-stream_loop", "-1", "-i", str(still_path)]
    filter_complex = (
        f"[0:v]zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':"
        f"d=1:fps={fps}:s={src_w}x{src_h}[zout]"
    )

    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        *ffmpeg_inputs,
        "-filter_complex", filter_complex,
        "-map", "[zout]",
        "-frames:v", f"{total_frames}",
        "-r", f"{fps}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-g", "60", "-keyint_min", "60",
        "-pix_fmt", "yuv420p",
        "-color_primaries", "bt709", "-color_trc", "bt709",
        "-colorspace", "bt709", "-color_range", "tv",
        "-an",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[zoom] zoom segment failed at t={source_t}: {result.stderr[-1500:]}", file=sys.stderr)
        return False
    return True


def render_follow_zoom_segment(input_path: Path, start: float, duration: float,
                                ease: float, region_pct: list[float],
                                src_w: int, src_h: int, fps: float,
                                output_path: Path,
                                zoom_factor: float = DEFAULT_ZOOM_FACTOR,
                                segment_id: str = "0") -> bool:
    """Render a FOLLOW-ZOOM segment — playback continues during the zoom.

    Unlike render_zoom_segment (which freezes a single frame and animates the
    zoom on that still), this applies a time-varying crop+scale transform to a
    range of moving frames: source[start:start+duration] plays through at 1x
    while the camera eases into a zoom at region_pct, holds at zoom_factor for
    the middle, then eases back out by the segment end.

    Timing:
      [0, ease]                 ease in: zoom = 1.0 → zoom_factor (smoothstep)
      [ease, duration-ease]     hold:    zoom = zoom_factor
      [duration-ease, duration] ease out: zoom = zoom_factor → 1.0 (smoothstep)

    Total output duration = `duration` (NO time added — unlike held-still zooms
    which insert a separate zoom segment, this transforms existing playback).
    """
    if duration <= 2 * ease:
        print(f"[zoom] follow-zoom duration {duration} must be > 2 * ease ({ease})", file=sys.stderr)
        return False
    if zoom_factor <= 1.0:
        print(f"[zoom] zoom_factor must be > 1.0, got {zoom_factor}", file=sys.stderr)
        return False

    # Same math as render_zoom_segment (camera-pan): at peak zoom, the focus
    # point is centered in the output frame. alpha drives BOTH the zoom and
    # the crop position linearly: at alpha=0 crop is (0,0) and z=1 (full
    # frame); at alpha=1 crop is at x_target/y_target and z=zf (focus
    # centered). Linear interp between, wrapped in easeInOutSine for smooth
    # camera glide.
    x_pct, y_pct, w_pct, h_pct = region_pct
    cx = src_w * (x_pct + w_pct / 2.0) / 100.0
    cy = src_h * (y_pct + h_pct / 2.0) / 100.0

    zf = float(zoom_factor)
    hold_end = duration - ease

    # At peak zoom, position the crop so the focus point lands at output
    # center. Clamped so the crop window stays inside source frame.
    x_target = max(0.0, min(cx - src_w / (2.0 * zf), src_w - src_w / zf))
    y_target = max(0.0, min(cy - src_h / (2.0 * zf), src_h - src_h / zf))

    # easeInOutSine alpha — same as render_zoom_segment. Piecewise linear
    # ramp 0→1→0 over ease/hold/ease, wrapped in (1-cos(PI*p))/2 for smooth
    # entry/exit. `out_time` is the rendered output timestamp.
    alpha_linear = (
        f"if(lt(out_time\\,{ease})\\,out_time/{ease}\\,"
        f"if(lt(out_time\\,{hold_end})\\,1\\,"
        f"1-(out_time-{hold_end})/{ease}))"
    )
    alpha = f"(1-cos(PI*({alpha_linear})))/2"
    z_expr = f"1+({zf}-1)*({alpha})"

    # Linear interp between (0,0) at alpha=0 and (x_target, y_target) at
    # alpha=1. With the same alpha driving zoom, the focus point smoothly
    # moves to output center as zoom increases.
    x_expr = f"({x_target})*({alpha})"
    y_expr = f"({y_target})*({alpha})"

    filter_expr = (
        f"zoompan="
        f"z='{z_expr}':"
        f"x='{x_expr}':"
        f"y='{y_expr}':"
        f"d=1:"
        f"s={src_w}x{src_h}:"
        f"fps={fps:.6f}"
    )

    # Color tags match render_source_segment so there's no color/brightness
    # shift at the boundary between this segment and the source segment that
    # follows (was causing a visible "snap" at the zoom-out tail).
    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-ss", f"{start:.6f}",
        "-i", str(input_path),
        "-t", f"{duration:.6f}",
        "-vf", filter_expr,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-r", f"{fps:.4f}",
        "-g", "60", "-keyint_min", "60",
        "-pix_fmt", "yuv420p",
        "-color_primaries", "bt709", "-color_trc", "bt709",
        "-colorspace", "bt709", "-color_range", "tv",
        "-movflags", "+faststart",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[zoom] follow-zoom render failed for segment {segment_id} (t={start} dur={duration}):",
              file=sys.stderr)
        print(result.stderr[-2000:], file=sys.stderr)
        return False
    return True


def concat_segments(segment_paths: list[Path], output_path: Path) -> bool:
    """Concat all rendered segments into the final output via ffmpeg concat demuxer."""
    list_path = output_path.parent / f".{output_path.stem}_concat.txt"
    list_path.write_text("\n".join(f"file '{p.resolve()}'" for p in segment_paths))
    try:
        cmd = [
            "ffmpeg", "-hide_banner", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(list_path),
            "-c", "copy",
            "-movflags", "+faststart",
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[zoom] concat failed: {result.stderr[-1500:]}", file=sys.stderr)
            return False
        return True
    finally:
        list_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Pause-zoom-hold-resume zoom segments.")
    parser.add_argument("--keep-temp", action="store_true", help="Don't delete the temp dir on exit (for debugging)")
    parser.add_argument("input", type=Path, help="Input video (typically a scrubbed recording)")
    parser.add_argument("output", type=Path, help="Output video with zooms applied")
    parser.add_argument("--zooms", type=Path, required=True, help="JSON file with zoom directives")
    parser.add_argument("--clean-source-ranges",
                        help="Comma-separated source_t ranges in the form 'start:end' where the "
                             "source-playback segment should pass through ffmpeg mpdecimate to "
                             "drop near-identical consecutive frames. Use for tightening "
                             "user-reading static periods that scrub.py's loading-freeze detector "
                             "missed (e.g. 1-2s of fully-rendered brief before the user scrolls). "
                             "Only applies to the SOURCE-PLAYBACK segments whose [cursor, source_t) "
                             "range fully overlaps a specified range; partial-overlap segments are "
                             "rendered normally. The cleaned output is shorter than the input by "
                             "the duration of dropped frames — re-derive downstream annotation "
                             "timings after re-zoom. Example: '49.80:59.00' cleans the source "
                             "playback between z2 and z3 in V1.2.")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"error: {args.input} not found", file=sys.stderr)
        sys.exit(1)
    if not args.zooms.exists():
        print(f"error: {args.zooms} not found", file=sys.stderr)
        sys.exit(1)

    zooms = json.loads(args.zooms.read_text())
    if not isinstance(zooms, list) or not zooms:
        print("error: zooms file must contain a non-empty JSON list", file=sys.stderr)
        sys.exit(1)

    zooms.sort(key=lambda z: z["source_t"])

    # Parse --clean-source-ranges into a list of (start, end) tuples.
    clean_ranges: list[tuple[float, float]] = []
    if args.clean_source_ranges:
        for piece in args.clean_source_ranges.split(","):
            piece = piece.strip()
            if not piece:
                continue
            s, _, e = piece.partition(":")
            clean_ranges.append((float(s), float(e)))

    def _should_clean(seg_start: float, seg_end: float) -> bool:
        """Return True if this source segment is fully contained inside any cleaned range."""
        for cs, ce in clean_ranges:
            if seg_start >= cs - 0.01 and seg_end <= ce + 0.01:
                return True
        return False

    src_duration, src_w, src_h, fps = get_video_info(args.input)
    print(f"[zoom] source: {args.input.name}  {src_w}x{src_h}  {src_duration:.2f}s @ {fps:.2f}fps")
    print(f"[zoom] {len(zooms)} zoom directive(s)")

    for z in zooms:
        # Annotate mode uses its own (shorter) ease default; hold/follow use the
        # standard zoom ease.
        if z.get("mode", "hold") == "annotate":
            z.setdefault("ease", DEFAULT_ANNOTATE_EASE_S)
        else:
            z.setdefault("ease", DEFAULT_ZOOM_EASE_S)
        if z["source_t"] >= src_duration:
            print(f"error: zoom source_t={z['source_t']} >= source duration {src_duration}", file=sys.stderr)
            sys.exit(1)
        if z["duration"] <= 2 * z["ease"]:
            print(f"error: zoom duration {z['duration']} ({z.get('id','?')}) must be > 2 * ease "
                  f"({z['ease']}). Either lengthen the zoom or set a shorter explicit `ease` "
                  f"in the JSON for this directive.", file=sys.stderr)
            sys.exit(1)

    # Cursor-clear rule (Hard Rule #16): zooms targeting the OUTPUT BRIEF
    # content (the rendered text the viewer reads) must not trigger while
    # the cursor is sitting on that text. Opt-in per directive via
    # `wait_cursor_clear: true`. Set ONLY on output-brief zooms — not on
    # tool-call loading zooms (where the cursor over the chat is fine since
    # the viewer is watching tool activity, not reading deliberately).
    #
    # Order preservation: the zooms were sorted by authored source_t above.
    # Cursor-clear can only push source_t FORWARD. To preserve authored order
    # (z[i] before z[i+1] in the composition), any cursor-clear scan for z[i+1]
    # starts at max(its authored source_t, z[i]'s adjusted source_t + epsilon).
    # Non-cursor-clear zooms also have their source_t advanced if a prior zoom
    # was delayed past them. No re-sort — authored order is the canonical sequence.
    ORDER_EPS = 0.05
    prev_source_t = -float("inf")
    for z in zooms:
        if not z.get("wait_cursor_clear", False):
            if z["source_t"] < prev_source_t + ORDER_EPS:
                new_t = prev_source_t + ORDER_EPS
                print(f"[zoom] {z.get('id','?')}: source_t {z['source_t']:.2f} → {new_t:.2f} "
                      f"(order preservation — prior zoom delayed past this one)")
                z["source_t"] = new_t
            prev_source_t = z["source_t"]
            continue
        base_t = z["source_t"]
        start_t = max(base_t, prev_source_t + ORDER_EPS)
        # For annotate mode the cursor-clear scan uses a SYNTHETIC region that
        # combines:
        #   x bounds = highlight_region_pct's x extent  (= where the readable
        #              brief content sits horizontally — the score table column,
        #              the Bottom Line paragraph column, etc.)
        #   y bounds = zoom_region_pct's y extent       (= the full vertical
        #              extent of the content the viewer is reading, not just
        #              the highlighted row)
        # This says "the cursor must be left or right of the readable column
        # OR above/below the visible reading area." A cursor sitting on an
        # adjacent row (Quality when z1 highlights Value) still counts as
        # obscuring because it's inside the readable x range. A cursor in the
        # dark padding to the right of the content column does NOT count —
        # it's not on any text. (Earlier iterations used highlight_region_pct
        # alone — too narrow; or zoom_region_pct alone — too wide, including
        # dark UI padding where the cursor doesn't obscure anything.)
        # For hold/follow it uses region_pct (focus center).
        if z.get("mode") == "annotate":
            hr = z["highlight_region_pct"]
            zr = z["zoom_region_pct"]
            cursor_clear_region = [hr[0], zr[1], hr[2], zr[3]]
        else:
            cursor_clear_region = z["region_pct"]
        adjusted_t, status = find_cursor_clear_source_t(
            args.input, start_t, cursor_clear_region,
            max_delay=float(z.get("cursor_clear_max_delay", DEFAULT_CURSOR_CLEAR_MAX_DELAY_S)),
        )
        if abs(adjusted_t - base_t) > 0.05:
            print(f"[zoom] {z.get('id','?')}: source_t {base_t:.2f} → {adjusted_t:.2f} "
                  f"(cursor-clear: {status})")
        else:
            print(f"[zoom] {z.get('id','?')}: cursor-clear — {status}")
        z["source_t"] = adjusted_t
        prev_source_t = adjusted_t

    if args.keep_temp:
        td_path = Path(tempfile.mkdtemp(prefix="zoom_"))
        td_cm = None
    else:
        td_cm = tempfile.TemporaryDirectory(prefix="zoom_")
        td_path = Path(td_cm.name)
    try:
        tmp_dir = td_path
        if args.keep_temp:
            print(f"[zoom] keeping temp dir: {tmp_dir}")
        segments: list[Path] = []
        cursor = 0.0

        for i, z in enumerate(zooms):
            mode = z.get("mode", "hold")
            if mode not in ("hold", "follow", "annotate"):
                print(f"error: zoom mode must be 'hold', 'follow', or 'annotate', got '{mode}'",
                      file=sys.stderr)
                sys.exit(1)

            if z["source_t"] > cursor:
                seg_path = tmp_dir / f"seg_src_{i:02d}.mp4"
                print(f"[zoom]   src segment {cursor:.2f} -> {z['source_t']:.2f}")
                clean = _should_clean(cursor, z["source_t"])
                if clean:
                    print(f"[zoom]     (cleaning duplicates in this segment via mpdecimate)")
                if not render_source_segment(args.input, cursor, z["source_t"], seg_path, fps,
                                              drop_duplicates=clean):
                    sys.exit(2)
                segments.append(seg_path)

            if mode == "follow":
                # Follow-zoom: playback continues during the zoom. Underlying
                # frames raw[source_t:source_t+duration] play through with a
                # time-varying crop+scale transform. Cursor advances.
                if z.get("pre_zoom_hold", 0) > 0:
                    print(f"error: zoom id={z.get('id','?')} has mode=follow + pre_zoom_hold — "
                          f"pre_zoom_hold is only supported in hold mode", file=sys.stderr)
                    sys.exit(1)
                seg_path = tmp_dir / f"seg_follow_{i:02d}.mp4"
                zf = float(z.get("zoom", DEFAULT_ZOOM_FACTOR))
                print(f"[zoom]   FOLLOW @ {z['source_t']:.2f}  focus={z['region_pct']}  "
                      f"zoom={zf:.2f}x  duration={z['duration']:.2f}s  ease={z['ease']:.2f}s")
                if not render_follow_zoom_segment(
                    args.input, z["source_t"], z["duration"], z["ease"],
                    z["region_pct"], src_w, src_h, fps, seg_path,
                    zoom_factor=zf, segment_id=f"{i:02d}",
                ):
                    sys.exit(2)
                segments.append(seg_path)
                cursor = z["source_t"] + z["duration"]
                continue

            if mode == "annotate":
                # Annotate-mode: hard cut to the annotate composite, hold for `duration`,
                # hard cut back out (next segment is normal source playback at source_t).
                if z.get("pre_zoom_hold", 0) > 0:
                    print(f"error: zoom id={z.get('id','?')} has mode=annotate + pre_zoom_hold — "
                          f"pre_zoom_hold is only supported in hold mode", file=sys.stderr)
                    sys.exit(1)
                seg_path = tmp_dir / f"seg_annotate_{i:02d}.mp4"
                callout_num = int(z.get("callout_number", i + 1))
                print(f"[zoom]   ANNOTATE @ {z['source_t']:.2f}  "
                      f"zoom={z['zoom_region_pct']}  highlight={z['highlight_region_pct']}  "
                      f"callout=#{callout_num}  duration={z['duration']:.2f}s  ease={z['ease']:.2f}s")
                if not render_annotate_segment(
                    args.input, z["source_t"], z["duration"], z["ease"],
                    z["zoom_region_pct"], z["highlight_region_pct"],
                    callout_num, src_w, src_h, fps, seg_path, tmp_dir,
                    segment_id=f"{i:02d}",
                ):
                    sys.exit(2)
                segments.append(seg_path)
                cursor = z["source_t"]  # Source playback resumes at source_t (no advance).

                # Inter-zoom pause (same logic as hold mode)
                if i + 1 < len(zooms):
                    pause_target = float(z.get("pause_after", DEFAULT_INTER_ZOOM_PAUSE_S))
                    natural_gap = zooms[i + 1]["source_t"] - z["source_t"]
                    pause_to_add = max(0.0, pause_target - natural_gap)
                    if pause_to_add > 0:
                        seg_path = tmp_dir / f"seg_pause_{i:02d}.mp4"
                        print(f"[zoom]   pause {pause_to_add:.2f}s @ {z['source_t']:.2f} "
                              f"(target {pause_target:.2f}s − natural {natural_gap:.2f}s)")
                        if not render_held_still(args.input, z["source_t"], pause_to_add,
                                                 fps, src_w, src_h, seg_path, tmp_dir):
                            sys.exit(2)
                        segments.append(seg_path)
                continue

            # Pre-zoom hold: held still at source_t for `pre_zoom_hold` seconds before the
            # zoom-in begins.
            pre_hold = float(z.get("pre_zoom_hold", DEFAULT_PRE_ZOOM_HOLD_S))
            if pre_hold > 0:
                seg_path = tmp_dir / f"seg_prehold_{i:02d}.mp4"
                print(f"[zoom]   pre-zoom hold {pre_hold:.2f}s @ {z['source_t']:.2f}")
                if not render_held_still(args.input, z["source_t"], pre_hold, fps,
                                         src_w, src_h, seg_path, tmp_dir):
                    sys.exit(2)
                segments.append(seg_path)

            # Hold-mode zoom: the zoom itself
            seg_path = tmp_dir / f"seg_zoom_{i:02d}.mp4"
            zf = float(z.get("zoom", DEFAULT_ZOOM_FACTOR))
            print(f"[zoom]   zoom @ {z['source_t']:.2f}  focus={z['region_pct']}  zoom={zf:.2f}x  duration={z['duration']:.2f}s")
            if not render_zoom_segment(
                args.input, z["source_t"], z["duration"], z["ease"],
                z["region_pct"], src_w, src_h, fps, seg_path, tmp_dir,
                zoom_factor=zf,
                segment_id=f"{i:02d}",
            ):
                sys.exit(2)
            segments.append(seg_path)
            cursor = z["source_t"]

            # Inter-zoom pause: hold the un-zoomed still for breathing room before
            # the next zoom in. Only inserted when the natural source-playback gap
            # to the next zoom is shorter than the configured pause; otherwise the
            # natural gap already provides breathing room.
            if i + 1 < len(zooms):
                pause_target = float(z.get("pause_after", DEFAULT_INTER_ZOOM_PAUSE_S))
                natural_gap = zooms[i + 1]["source_t"] - z["source_t"]
                pause_to_add = max(0.0, pause_target - natural_gap)
                if pause_to_add > 0:
                    seg_path = tmp_dir / f"seg_pause_{i:02d}.mp4"
                    print(f"[zoom]   pause {pause_to_add:.2f}s @ {z['source_t']:.2f} (target {pause_target:.2f}s − natural {natural_gap:.2f}s)")
                    if not render_held_still(args.input, z["source_t"], pause_to_add,
                                             fps, src_w, src_h, seg_path, tmp_dir):
                        sys.exit(2)
                    segments.append(seg_path)

        # Final source segment after the last zoom
        if cursor < src_duration:
            seg_path = tmp_dir / f"seg_src_tail.mp4"
            print(f"[zoom]   src segment {cursor:.2f} -> {src_duration:.2f}")
            clean = _should_clean(cursor, src_duration)
            if clean:
                print(f"[zoom]     (cleaning duplicates in this tail segment via mpdecimate)")
            if not render_source_segment(args.input, cursor, src_duration, seg_path, fps,
                                          drop_duplicates=clean):
                sys.exit(2)
            segments.append(seg_path)

        print(f"[zoom] concatenating {len(segments)} segments -> {args.output.name}")
        if not concat_segments(segments, args.output):
            sys.exit(2)

        # Report per-segment durations and cumulative recording_t so script
        # frontmatter annotations / lower-thirds can be timed against the
        # actual zoomed timeline (especially useful when --clean-source-ranges
        # has shifted things). Mirrors what zoom.py's segment-naming convention
        # implies but with concrete numbers.
        print(f"[zoom] segment timing in zoomed file:")
        rec_t = 0.0
        for seg in segments:
            seg_dur, _, _, _ = get_video_info(seg)
            print(f"[zoom]   {seg.name:<24}  {rec_t:6.2f} → {rec_t+seg_dur:6.2f}  ({seg_dur:.2f}s)")
            rec_t += seg_dur
    finally:
        if td_cm is not None:
            td_cm.cleanup()

    out_duration, _, _, _ = get_video_info(args.output)
    added = out_duration - src_duration
    print(f"[zoom] done. {src_duration:.2f}s -> {out_duration:.2f}s (+{added:.2f}s)")


if __name__ == "__main__":
    main()
