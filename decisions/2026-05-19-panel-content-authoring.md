# 2026-05-19 — Panel Content Authoring: Capability Framing + Three-Shape Rotation

**Status:** active
**Affects:** `.claude/skills/video-scriptwriting/SKILL.md` (new use_case § *Panel content authoring*), `.claude/skills/parallax-video/SKILL.md` ("write V<N>" dispatch row), `references/production-principles.md` (cross-ref table row), `templates/product-demo/index.html` (panel divs get `headline / body / footer / source / badge` children; CSS for those classes), `tools/render.py` (substitution for `annotations[].panel.{eyebrow|headline|body|source|badge}`), this ADR

## Decision

Annotation panels in `mode: "annotate"` zooms pitch the **capability / workflow / stakes value** of having that segment of brief in every Parallax output, framed for the buyer named in `primary_persona`. They do **not** decompose or literally interpret the specific numbers on screen — the spotlight on the recording already shows those.

**Format:** `eyebrow + headline + body + source + badge`. **No `stats` row** (specifics belong on the recording side, in the spotlight).

**Three rhetorical shapes — rotate across panels in a video, never two consecutive in same shape:**

- **Capability** — names what the tool gives the buyer (eyebrow pattern: `[SEGMENT] · WHAT IT GIVES YOU`)
- **Workflow** — situates the segment in the buyer's day (eyebrow pattern: `[SEGMENT] · WHY IT EARNS ITS PLACE` / `WHY THIS ROW MATTERS`)
- **Stakes** — names the conversation/decision the segment serves (eyebrow pattern: `[SEGMENT] · THE CALL YOU WILL HAVE` / `THE QUESTION BEHIND THE CALL`)

**Subject-matching is a hard constraint:** each panel's topic equals the spotlit content's topic. The rhetorical shape is the angle taken on that topic, not a license to drift.

**Other rules that apply:**
- QC #9 (customer's-chair framing) applies to all panel fields — no engineering vocabulary.
- QC #7 (12-angle rotation) applies to panel body content — pick an angle from `references/value-framing-menu.md` for each panel, don't repeat across panels.
- Source + badge required — every panel cites where the data came from (vault, factor scores, fundamentals).

## Why

Three problems the rule solves:

1. **Panels that decompose specifics make the demo look like a stat-walkthrough.** The advisor doesn't need a 3-sentence paragraph saying *"the P/E is 45.7, AVGO is 80, AMD is 140..."* — they can read that off the brief. What they need is *"this is the capability that gives me a peer-adjusted answer for the 'isn't NVDA expensive?' client question."* The capability framing positions Parallax as a workflow tool the buyer adopts; specifics-framing positions it as a calculator they consult.
2. **Three consecutive panels in the same rhetorical stance read like template re-skins.** LTs and VO have built-in variety (LT jobs differ; VO has 12-angle rotation + interleaved with recording activity). Panels are all the same JOB, same FORMAT, same time cluster. Without a shape rotation rule, they monotonize.
3. **Subject-matching prevents drift.** Without an explicit rule, a panel could plausibly pitch any value of the tool. Constraining each panel to its paired spotlight's topic keeps the four layers (recording / spotlight / VO / panel) coordinated.

## How we found it

Phase B of the panel content build-out. Initial proposal (during V1.2 content-strategy review) had panels with `stats[]` rows decomposing the spotlit numbers + body paragraphs interpreting them literally. User feedback: *"that's not what I want — I don't want them to explain the exact specific output being generated, I want it to explain the value of that segment of output, framing it to show the value to the target audience."*

The fix reframes panels from "interpret this specific stat" to "pitch the capability of having this kind of stat in every brief." Three rhetorical shapes give variety. Stats row dropped (panels are no longer about the specifics).

## Notes

- Panel content authoring is `use_case`-only. `instructional` videos don't use `mode: "annotate"` (their format is point-and-click sequence, not callout-driven), so panels don't appear there.
- Three-shape rotation is a *no-two-consecutive* rule, not a *strict-cycle* rule. A 4-panel video could go capability → workflow → capability → stakes; a 6-panel video could go capability → stakes → capability → workflow → capability → stakes. As long as no two adjacent panels share a shape.
- The 12-angle rotation (QC #7) and the 3-shape rotation are independent axes — a capability-shape panel can use any of the 12 value angles. Shape = rhetorical stance; angle = underlying value dimension.
- For V1.2 specifically: ap1 (Value row) = capability shape · ap2 (Trajectory) = stakes shape · ap3 (Bottom Line) = capability shape. Three different topics, rotating shapes, no two consecutive same.
- `tools/render.py` now substitutes `annotations[].panel.{eyebrow|headline|body|source|badge}` from frontmatter into the template's panel divs. Format substitution is the same pattern as LT substitution (BeautifulSoup, `_set_text` on the matching class within the panel div).
