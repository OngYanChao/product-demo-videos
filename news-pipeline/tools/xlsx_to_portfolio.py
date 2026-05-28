#!/usr/bin/env python3
"""Convert a portfolio XLSX → CSV holdings + markdown metadata.

Expects the source XLSX to have:
  - A "Holdings" sheet: tabular, first row = column headers
  - An "Account Summary" sheet: key/value pairs in cols A/B, with section
    headers in col A (e.g. "ACCOUNT INFORMATION", "ACCOUNT TOTALS",
    "ALLOCATION BY ASSET CLASS", "ALLOCATION BY SECTOR", "NOTES")

Sheet names can be overridden with --holdings-sheet and --summary-sheet.

Outputs (next to news-pipeline/portfolios/):
  <basename>.csv   — holdings table, CSV
  <basename>.md    — markdown summary built from the Account Summary sheet

Usage:
  python3 news-pipeline/tools/xlsx_to_portfolio.py path/to/portfolio.xlsx
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_ROOT = REPO_ROOT / "news-pipeline"
PORTFOLIOS_DIR = PIPELINE_ROOT / "portfolios"


def load_workbook(path: Path):
    try:
        import openpyxl
    except ImportError:
        sys.exit("❌ openpyxl not installed. Run:\n"
                 "   python3 -m pip install openpyxl")
    return openpyxl.load_workbook(path, data_only=True)


def export_holdings(ws, out_csv: Path):
    """Dump a tabular sheet (first row = headers) straight to CSV."""
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        raise RuntimeError("Holdings sheet is empty.")
    # Trim trailing empty rows
    while rows and not any(rows[-1]):
        rows.pop()
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for row in rows:
            w.writerow(["" if c is None else c for c in row])


def parse_summary(ws) -> dict:
    """Parse a key/value style summary sheet into nested sections.

    Heuristics:
      - 1 non-empty cell, ALL CAPS or "Notes"  → section header
      - 1 non-empty cell, mixed case           → free-form note
      - 2 non-empty cells                       → key/value pair
      - 3+ non-empty cells, ALL strings        → sub-table header
      - rows after a header within the table    → sub-table data rows
    """
    sections: dict = {}
    current_section = None
    current_sub_headers = None
    current_sub_rows: list = []

    def flush_sub():
        nonlocal current_sub_headers, current_sub_rows
        if current_section is not None and current_sub_headers:
            sections.setdefault(current_section, {})["_table"] = {
                "headers": current_sub_headers,
                "rows": current_sub_rows,
            }
        current_sub_headers = None
        current_sub_rows = []

    for row in ws.iter_rows(values_only=True):
        cells = [c for c in row]
        # Strip trailing empties
        while cells and cells[-1] in (None, ""):
            cells.pop()
        if not cells:
            flush_sub()
            continue
        non_empty = [c for c in cells if c not in (None, "")]
        n_nonempty = len(non_empty)

        if n_nonempty == 1:
            text = str(non_empty[0]).strip()
            # Section header: ALL CAPS, or known section words
            if text.isupper() or text in ("Notes",):
                flush_sub()
                current_section = text
                sections.setdefault(current_section, {})
            else:
                # Free-form note attached to current section
                if current_section:
                    sections[current_section].setdefault("_notes", []).append(text)
            continue

        if n_nonempty == 2:
            # Key/value pair (terminates any in-progress sub-table)
            flush_sub()
            key, value = non_empty[0], non_empty[1]
            key_str = str(key).strip()
            if current_section is None:
                current_section = "_root"
                sections.setdefault(current_section, {})
            sections[current_section][key_str] = value
            continue

        # n_nonempty >= 3
        if all(isinstance(c, str) and c.strip() for c in non_empty):
            # Sub-table header row
            flush_sub()
            current_sub_headers = [str(c).strip() for c in non_empty]
        elif current_sub_headers:
            # Data row within the current sub-table
            row_cells = list(cells) + [None] * (len(current_sub_headers) - len(cells))
            current_sub_rows.append(row_cells[:len(current_sub_headers)])
    flush_sub()
    return sections


def render_markdown(account_name: str, summary: dict) -> str:
    lines: list[str] = []
    lines.append(f"# {account_name}\n")

    def fmt_value(v):
        if isinstance(v, float):
            if abs(v) < 1 and v != 0:
                return f"{v * 100:.2f}%"
            return f"{v:,.2f}"
        return str(v)

    # Skip section that's just the document title (e.g. "PORTFOLIO STATEMENT")
    skip_sections = {"PORTFOLIO STATEMENT"}

    for section, content in summary.items():
        if section.startswith("_"):
            continue
        if section in skip_sections:
            continue
        # Pretty section title (Title Case from ALL CAPS)
        title = " ".join(w.capitalize() for w in section.split())
        lines.append(f"## {title}\n")
        kv = {k: v for k, v in content.items() if not k.startswith("_")}
        if kv:
            for k, v in kv.items():
                lines.append(f"- **{k}**: {fmt_value(v)}")
            lines.append("")
        if "_table" in content:
            t = content["_table"]
            headers = t["headers"]
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("|" + "|".join(["---"] * len(headers)) + "|")
            for row in t["rows"]:
                cells = [fmt_value(c) if c is not None else "" for c in row]
                cells += [""] * (len(headers) - len(cells))
                lines.append("| " + " | ".join(cells) + " |")
            lines.append("")
        if "_notes" in content:
            for n in content["_notes"]:
                # Strip a leading "•" / "*" / "-" since we add our own bullet
                cleaned = n.lstrip("•*- ").strip()
                lines.append(f"- {cleaned}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def derive_basename(xlsx_path: Path) -> str:
    """Convert e.g. 'Wong_Family_Trust_Portfolio_2026-04-24.xlsx' →
    'Wong_Family_Trust_2026-04-24' (strip '_Portfolio' if present)."""
    stem = xlsx_path.stem
    return stem.replace("_Portfolio", "").replace("Portfolio_", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx", type=Path, help="Path to source XLSX portfolio file")
    ap.add_argument("--holdings-sheet", default="Holdings")
    ap.add_argument("--summary-sheet", default="Account Summary")
    ap.add_argument("--out-dir", type=Path, default=PORTFOLIOS_DIR)
    ap.add_argument("--basename", default=None,
                    help="Override output basename (default: derived from input filename)")
    args = ap.parse_args()

    if not args.xlsx.exists():
        sys.exit(f"❌ File not found: {args.xlsx}")

    wb = load_workbook(args.xlsx)
    if args.holdings_sheet not in wb.sheetnames:
        sys.exit(f"❌ Sheet '{args.holdings_sheet}' not found. "
                 f"Available: {wb.sheetnames}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    basename = args.basename or derive_basename(args.xlsx)
    # Each portfolio lives in its own subfolder so source files, screenshots,
    # or extra notes can sit alongside its holdings + summary.
    portfolio_dir = args.out_dir / basename
    portfolio_dir.mkdir(parents=True, exist_ok=True)
    csv_out = portfolio_dir / "holdings.csv"
    md_out = portfolio_dir / "summary.md"

    # ---- CSV ----
    export_holdings(wb[args.holdings_sheet], csv_out)
    csv_rows = csv_out.read_text().count("\n") - 1  # minus header
    print(f"✓ Wrote {csv_out.relative_to(REPO_ROOT)}  ({csv_rows} holdings)")

    # ---- Markdown ----
    if args.summary_sheet in wb.sheetnames:
        summary = parse_summary(wb[args.summary_sheet])
        # Try to pull the account name out of the summary
        account_name = "Portfolio"
        for section in summary.values():
            if "Account Name" in section:
                account_name = str(section["Account Name"])
                break
        md = render_markdown(account_name, summary)
        md_out.write_text(md)
        print(f"✓ Wrote {md_out.relative_to(REPO_ROOT)}")
    else:
        print(f"⚠️  Sheet '{args.summary_sheet}' not found — skipped metadata "
              f"(only the CSV was generated).")


if __name__ == "__main__":
    main()