# 2026-05-19 — Customer's-Chair Framing for All Use_Case Copy

**Status:** active
**Affects:** `references/production-principles.md` (new Principle, decision record), `.claude/skills/video-scriptwriting/SKILL.md` (new use_case Quality Check #9, enforcement), `.claude/skills/parallax-video/SKILL.md` ("write V<N>" dispatch row, reliability hook), `Parallax Video Plan - MASTER.md` (V1 Highlight + Open beat LT + Closer revised; new global Production Notes section), this ADR

## Decision

Every line of audience-facing copy in a `use_case` video — LT eyebrow / headline / stats, annotation panel eyebrow / headline / body / stats, VO, MASTER Highlights, title-card hook, YouTube title — speaks from the **buyer's** chair, never from the **system's** chair.

**Buyer = the persona named in each video's `primary_persona`** (MFO / RIA / wealth advisor for V1; PM / analyst / quant / etc. for others). They evaluate the demo by what it gives them at the moment named in `primary_moment` — never by what the system does internally.

**Reject:** "Eight parallel skill calls," "MCP tool invocations," "Agent orchestration," "Watch as N things happen in parallel," any counting of internal operations even when factually true, any builder vocabulary, any line that asks the viewer to imagine the system's plumbing.

**Require:** outcome ("twenty minutes of research, in one prompt"), stakes ("defensible read before the meeting"), workflow-fit ("score, trajectory, bottom line in 30 seconds"), or methodology-credibility ("peer-reviewed factor model, 13-year out-of-sample"). Every line should match one of these four molds.

**Carve-out:** Does NOT apply to `instructional` style (I1–I4). Tutorial audiences ARE the technical operator setting up the plugin; system mechanics framing is the right register there. *"Type `/parallax:stock AAPL`, press enter, watch all eight skills fire — that confirms the plugin loaded"* is correct for an instructional. The carve-out is narrow: only when the system mechanic IS the step the viewer must reproduce.

## Why

The audience for `use_case` content is sophisticated financial professionals — MFOs, RIAs, advisors, PMs, analysts. They evaluate a tool by asking *"what does this do for me when the client texts at 2pm before my 2:10 meeting?"* They are not engineers evaluating system architecture.

Engineering framing fails in two ways:
1. **Irrelevance** — the buyer doesn't speak "skill calls" or "agent orchestration." Those phrases either fly past unparsed (best case) or read as the producer is showing off internals the buyer doesn't care about (worst case).
2. **Defensive over-explanation** — counting operations ("eight parallel calls!") implicitly admits the operation needed to be sold on grounds of *how many things happen*, rather than *what comes out*. It positions Parallax as a system you'd evaluate vs. another system, instead of as a workflow that fits the buyer's day.

Outcome / stakes / workflow-fit / methodology-credibility framing positions Parallax as a workflow tool the buyer adopts — confident, audience-anchored, no defensive showmanship.

## How we found it

V1's original demo plan carried over *"Plain English in. Eight parallel calls out."* as a tagline, and the first LT was authored as *"Eight parallel skill calls. One natural-language prompt."*. During the V1.2 LT content-strategy review (just before Phase 5 scriptwriting kicked off), user explicitly rejected the engineering framing: the second half of the tagline and the LT headline both lean on system-mechanic vocabulary that the MFO / RIA audience doesn't speak.

The fix: replace the mechanic-talk half with an outcome-talk half. *"Plain English in. Defensible brief out."* preserves the parallel rhythm of the original tagline while putting both halves in the buyer's vocabulary. The LT headline becomes *"Twenty minutes of research, in one prompt."* — same hook as the title card, repeated for the LT moment.

## Notes

- The rule applies to *copy*, not to *production specs*. The Recording Tips section in MASTER continues to say "Show parallel execution in real time" because that's a producer instruction — the producer needs to know the recording must capture tool activity firing in the sidebar. The visual is fine; it's the *describing* of the visual to the audience that has to stay in audience-vocabulary.
- For V2–V16 and I1–I4 production: every author who drafts copy for those videos reads `video-scriptwriting/SKILL.md` (auto-loaded at Phase 5), which now carries QC #9. The check runs as part of every script draft — the principle is enforced by default, not opt-in.
- Audit trail: V1's three reverted lines are tagged in MASTER with "Revised 2026-05-19 per Customer's-chair framing principle" so the substitution is traceable. If a future video author re-introduces engineering framing, the MASTER + ADR + Principle + QC chain catches it at draft time.
- The four require-molds (outcome / stakes / workflow-fit / methodology-credibility) overlap with the 12-angle value-framing menu but aren't a strict subset of it. The menu in `references/value-framing-menu.md` covers *which dimension of value to express*; this rule covers *whose vocabulary to express it in*. Both apply together.
