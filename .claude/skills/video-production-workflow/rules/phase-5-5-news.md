# Phase 5.5 rules — news-pipeline (apply zoom)

News doesn't have a separate Phase 5.5 — `zoom.py` is invoked by `news-pipeline/tools/process.py` after `tick_cut.py` produces `auto_zooms.json`. These rules document the editorial invariants for the auto-zoom application.

Cross-load `meta.md` + `phase-3-news.md`.

---

## Hard Rule #11 — Colour space consistency.

Same as product-demo (see `phase-5-5-product-demo.md`). Applies to every encoding step in `zoom.py`. `tools/zoom.py` enforces this via single-frame mp4 extraction and explicit `-color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv`.

---

## Hard Rule #12 — Zoomed recording is canonical timeline.

For news, the canonical timeline is `zoom.mp4` (= `news-pipeline/recordings/N<N>/zoom.mp4`). News's `news_render.py` stages this into the Hyperframes template. No script timings to re-derive (news has no script frontmatter).

---

## Hard Rule #23 (news) — z0 + z0b auto-emitted by tick_cut.py.

Documented in `phase-3-news.md`. `zoom.py` consumes the auto-emitted `trimmed_scrubbed_tickcut.auto_zooms.json`.

---

## Hard Rule #29 (news) — z0b ease-out over still + raw-tail stitch.

Auto-applied in `news-pipeline/tools/process.py` BEFORE `zoom.py` runs. Documented in `phase-3-news.md`.
