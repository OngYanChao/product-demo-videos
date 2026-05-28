# Value-framing menu (12 angles)

The vocabulary the Parallax video pipeline uses to label *why each beat matters to the viewer*. Every video script — current 20-video persona-and-moment series (V1–V16 + I1–I4), future batches, and shelved intel briefs (when reactivated) — pulls per-beat value-framing from this menu.

This doc is the **canonical reference**. Consumers:

- `Parallax Video Plan - MASTER.md` — each video's Highlights section names its `**Primary value angles**` by `#X` number from this menu (e.g. *Moat headline: #4 Auditability*).
- `.claude/skills/video-scriptwriting/SKILL.md` — craft guidance for applying the menu (rotation rule, the three-question framework, explicit-value-framing requirement).
- `.claude/skills/parallax-video/SKILL.md` — orchestrator dispatch references this file when the user says *"write V<N>"*.
- `CLAUDE.md` — locked-rules section lists the four moat angles by name.
- `references/production-principles.md` — Principle #8 (every beat states value explicitly) references this menu.

If a moat angle is refined, an angle is added, or wording is sharpened: update this file once and all consumers inherit. Do not duplicate the menu inline elsewhere.

---

## The framework

Every beat in a script answers three questions for the viewer:

1. **What is this?** — name the on-screen element (the label / annotation layer)
2. **What problem does this solve?** — the problem-framing
3. **Why does this matter to me (the PM/CIO/RM)?** — the value-framing

Question 3 must be stated as a labelled clause, not left to the viewer to infer. The value-framing menu below gives the 12 distinct answers the project's scripts pull from when answering Q3.

---

## The 12 angles

**Moat angles** (#4, #5, #10, #12) are bolded — these are the structural answers to *"why not generic AI?"* — properties a competitor or LLM-only workflow literally cannot match. Standard angles are broadly applicable and rotate through every video's supporting cast. Each angle's vault source is cited in the right column.

| # | Angle | What it means | Value-line shape | Vault source |
|---|---|---|---|---|
| 1 | Speed | Tool finishes in seconds what the analyst does in 20 minutes per name | "Twenty minutes → ninety seconds. Every name in your portfolio." | (project rule; V1 hook line) |
| 2 | Coverage / scale | Same depth applied to thousands of names, not just the top five | "Analyst-grade read on every one of your 200 names — not just the top five." | `04-Marketing/Key Differentiators.md` → Data Edge (62K listings, 48 markets, 1B datapoints/wk) |
| 3 | Defensibility | Numbers a PM can defend in an IC meeting because the methodology is peer-reviewed and explainable | "Numbers you can defend in committee — peer-reviewed methodology, not a partner can pick apart." | (project rule, vault-adjacent) |
| **4** | **Auditability** | Every score / flag has a documented evidence chain — tool call, timestamp, input, source quote — that compliance + regulators recognise | "Every score has a paper trail. One audit, then signed off." | `04-Marketing/Auditability and the Unverifiable Frame.md` |
| **5** | **Determinism / reproducibility** | Same input + same reference date → byte-for-byte identical output. Re-run tomorrow, get the same number | "Re-run tomorrow, same number. Same input → byte-identical output. The score won't move on you." | `Auditability and the Unverifiable Frame.md` §3 |
| 6 | No black box | Drill into any score, flag, or signal to see the underlying rationale — not a chatbot's confident guess | "Drill into any score and see the rationale — not a chatbot's confident guess." | `Key Differentiators.md` §1 |
| 7 | Decision-readiness | Output drops straight into a memo / trade ticket / compliance package with no rewriting | "Drop straight into your memo. No rewriting." | (project rule, vault-adjacent — "allocation-ready", "client-ready talking points") |
| 8 | Workflow-native | Intelligence meets the user in their existing tools (API, MCP, email, Slack, CLI) — no new terminal, no new login | "API, MCP, email, Slack — meets you in your workflow. No terminal subscription." | `Key Differentiators.md` §6 |
| 9 | Live track record | The engine running this score is the same one running real fund capital — Polaris since 2019 | "Same engine running Polaris since 2019. Real money. Real outcomes." | `Key Differentiators.md` + Polaris locked closer in `CLAUDE.md` |
| *10* | *Failure isolation* | *When a number is wrong, you can pin the bug to the renderer / API / data layer in minutes. LLM-only output: you can't tell which number is wrong, let alone where.* ***Strict meaning — targets risk/ops audiences, not PM/CIO. No current feature-demo video headlines this; secondary mentions only*** *(see "moat distribution caveat" below).* | "If a number's off, we pin it to the data layer, the API, or the renderer — in minutes." | `Auditability and the Unverifiable Frame.md` §3 |
| 11 | Risk-adjusted return | Outperforms benchmarks with less risk than the market — backed by the live fund using these same scores | "Less risk than the market — backed by a live fund using these same scores." | `Key Differentiators.md` Risk Edge |
| **12** | **Unverifiable frame** | The killer regulated-wealth wedge: an RM can't tell a lucky-correct LLM number from a wrong one. Both look identical on the page. Parallax removes the luck. *"Unverifiable" lands harder than "hallucinated" for compliance audiences — it's a property of the workflow, not a judgement on the output.* | "An RM can't tell a lucky-correct LLM number from a wrong one. Parallax removes the luck." | `Auditability and the Unverifiable Frame.md` §1–2 (killer line) |

---

## When this menu applies

The menu's per-beat assignment + rotation rule apply to **`use_case` style scripts only** (Tier 1 / 2 / 3). See `.claude/skills/video-scriptwriting/SKILL.md` § *Style axis* for the full style enum.

| Style | Menu use |
|---|---|
| `use_case` | Full menu in scope. Per-beat rotation rule below. MASTER per-video bullets cite angles by `#X`. |
| `instructional` | Menu **does not apply per-beat.** Value-framing collapses to hook + close only — typically pulls from #1 Speed + #2 Coverage or #1 + #8 Workflow-native. Inside the video body, VO describes the screen literally. |
| `intel_brief` (paused) | TBD on reactivation. Vocabulary likely survives; mapping to no-on-screen-product VO is the open craft question. |

## Rotation rule (use_case style)

**Per ~90 seconds of content** (~6–8 beats), expect to draw from **5–7 different angles**. If two consecutive beats lean on the same angle, rewrite one. Repetition of the same angle is the failure mode that makes a script feel like one note repeated.

The rotation discipline does not change with duration — only the absolute angle count scales:

| Complexity tier | Typical duration | Angles drawn (typical) |
|---|---|---|
| Tier 1 — single_feature | 60–120s | 5–7 angles |
| Tier 2 — workflow_chain | 2–3 min | 8–10 angles |
| Tier 3 — hero_playbook | 3–5 min | up to all 12 angles (still no two consecutive beats on the same one) |

The moat angle (if any) typically anchors the script — opening hook, mid-video reinforcement, and closer — while standard angles carry the supporting beats.

---

## Per-batch headline distribution — current 20-video persona-and-moment series *(locked 2026-05-13)*

| Moat | Tier 1 (single-feature) | Tier 2 (workflow chain) | Tier 3 (hero playbook) |
|---|---|---|---|
| **#4 Auditability** | V4 Shariah Screen | **V11 Compliance Audit Trail** *(strongest fit)* · V8 PM IC Defense *(supporting — every claim cite-able)* | V15 Stock Initiation Report *(supporting — IC-grade evidence chain in the published artifact)* |
| **#5 Determinism** | V2 PM Pre-Trade Stock Check | **V10 Regime-Window Backtesting** *(strongest fit — point-in-time, no look-ahead)* | V14 PM Iran Playbook *(whole workflow reproducible against Friday-close inputs)* |
| **#12 Unverifiable frame** | V1 RM Client Question *(the "vs eight Claude chats" beat)* | — | V15 Stock Initiation Report *(supporting — published artifact defensible vs LLM-only)* |
| *#10 Failure isolation* | *—* | *—* | *—* |

**9 of 16 use_case videos** headline a moat angle (2 of which are at the supporting level, not headline). The other 7 use_case videos lean on standard angles (most commonly #1 Speed, #2 Coverage, #6 No-black-box, #7 Decision-readiness).

**Each active moat headlines at each tier:** #4 spans T1+T2+T3 (full spread, plus T2 supporting), #5 spans T1+T2+T3 (full spread), #12 spans T1+T3 (T2 has no natural #12 fit without overlapping V1's framing). This is the "catalogue's gestalt teaches the moats" design intent — a buyer who watches one short video (T1) sees the same moat as one who watches the hero workflow (T3), demonstrated at appropriate depth.

**Polaris closer earned by 3 videos:** V8 (PM IC Defense), V12 (PM Thesis-to-Portfolio Build), V14 (PM Iran Playbook). All three are PM-audience + methodology-proof flex earns the live-fund closer. Other 13 use_case videos use the standard *"Solve the market."* tagline. Instructional (I1-I4) always uses the standard tagline.

### Moat distribution caveat

The new 20-video batch is **persona-and-moment organized** (each video anchors on `primary_persona × primary_moment × deliverable`), not feature-organized. Moats land where the natural workflow showcases them, not where a coverage-completionist matrix would push them. #10 Failure isolation has 0 videos because its strict vault meaning targets risk/ops audiences (a separate engineering-targeted video, Venise-test-style, would be its canonical home — not part of the current 20).

**Distribution philosophy**: *strict semantic fit over distribution math.* Better to leave a video without a moat headline than twist the moat angle to fit. The 7 use_case videos without a moat headline (V3, V5, V6, V7, V9, V12, V13, V16) lean on standard angles — that's the supporting cast expected to anchor the bulk of any catalogue.

---

### Legacy distribution — superseded 2026-05-13

The previous 28-video feature-organized distribution (V0-V12 main + N1-N14 niche) is archived in `_archive/MASTER-pre-overhaul-2026-05-11.md` (moved 2026-05-13). Headline distribution from that batch, for historical reference:

| Moat | Main showcase slots | Niche slot |
|---|---|---|
| #4 Auditability | V2 Deep Dive · V11 Shariah · V12 Forensic Earnings | N10 Methodology Deep-Dive |
| #5 Determinism | V4 Rebalancing · V8 Build from Thesis | N9 Backtest from date |
| #12 Unverifiable frame | V1 Quick Stock Brief · V7 Investor Profiles | N14 Finding Alpha |

The new 20-video batch maintains the same moat distribution philosophy (strict semantic fit, every active moat headlined at each tier) but reorganized around persona-and-moment rather than feature-coverage.

---

## When this menu changes

- **Adding an angle**: only if (a) the project has demoed a value claim that doesn't fit any existing angle, and (b) the new angle traces to a vault source. Update this file, then verify all consumer references still make sense.
- **Refining wording**: tighten value-line shapes, sharpen pain definitions. Update once here; do not duplicate.
- **Adding a moat headline assignment to a video**: update the video's `**Primary value angles**` bullet in MASTER.md and the per-batch distribution table here. Verify the strict-semantic-fit rule.
- **Future batches**: this menu carries forward. Per-batch distribution tables (like the "current 28-video series" table above) get appended below as new batches are planned.
