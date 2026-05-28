# portfolios/

Saved portfolios that get embedded into Cowork prompts when a news event maps to one of them. Keeping prompts grounded in *real* (or realistic) holdings makes the videos more useful — viewers see how Parallax answers questions about a *specific* book, not generic toy stocks.

## One subfolder per portfolio

Each portfolio lives in its own subfolder with **fixed-name files** inside:

```
portfolios/
└── Wong_Family_Trust_2026-04-24/
    ├── holdings.csv     ← positions table
    └── summary.md       ← account info, totals, allocations, notes
```

The subfolder name carries the portfolio's identity (basename + statement date so versions don't collide). The files inside have **predictable names** so code can reference them as `portfolios/<id>/holdings.csv` without parsing.

Drop any extras into the subfolder alongside — the source XLSX, screenshots, custom notes — they won't interfere with the pipeline as long as `holdings.csv` and `summary.md` exist.

## CSV schema

Universal columns (used in every portfolio):

| Column | Required | Notes |
|---|---|---|
| `Symbol` | ✅ | Ticker as it appears on the listing exchange (e.g. `NVDA`, `0700.HK`) |
| `Weight %` | ✅ | Position weight as a decimal fraction (0.18 = 18%) |
| `Security Name` | recommended | Full security name for readability |
| `Sector` | recommended | Used for sector-exposure analysis |
| `Asset Class` | recommended | "Equity - US", "ETF - US Equity", "ADR", "Equity - International", etc. |
| `Quantity` | optional | Share count — only needed for rebalancing analysis |
| `Market Value (USD)` | optional | Absolute dollar value |
| `Cost Basis (USD)` | optional | For tax-lot scenarios |
| `Unrealized G/L (USD)` | optional | Position-level P&L |
| `Unrealized G/L %` | optional | Position-level return |
| `Currency` | optional | Native trading currency |
| `Price (Local)` | optional | Native-currency price |
| `FX to USD` | optional | FX rate at statement date |
| `CUSIP/ISIN` | optional | Identifier for reconciliation |

Tools that consume portfolios should treat all but `Symbol` + `Weight %` as best-effort optional.

## `summary.md` schema

Free-form markdown summary of the account. Suggested structure:

```markdown
# <Account Name>

## Account
- Account Number: …
- Custodian: …
- Statement Period: …
- Mandate / Risk Tolerance: …

## Totals
- Total Market Value (USD): …
- Total Cost Basis (USD): …
- Unrealized G/L: …

## Allocation by Asset Class
…

## Allocation by Sector
…

## Notes
…
```

This file is what gets embedded as the "I hold X" context when a prompt references the portfolio.

## Referencing portfolios in prompts

(Phase 3 — `tools/draft_prompt.py` will handle this automatically.)

When a news-event prompt template references `{{portfolio:<id>}}`, the drafter pulls the matching portfolio's `summary.md` (and optionally the holdings CSV) and substitutes it into the prompt text. The result is the literal text that `capture.py` types into Cowork.

## Adding a new portfolio

If you have it as Excel (`.xlsx`):

```bash
python3 news-pipeline/tools/xlsx_to_portfolio.py \
  /path/to/Wong_Family_Trust_Portfolio_2026-04-24.xlsx
```

This produces `news-pipeline/portfolios/<base>/holdings.csv` + `<base>/summary.md`.

The converter expects two sheets:
- `Holdings` — tabular, first row = headers
- `Account Summary` — key/value style metadata

If your XLSX uses different sheet names, pass `--holdings-sheet "..."` and `--summary-sheet "..."`.