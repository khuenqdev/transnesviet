#!/usr/bin/env python3
"""Validate a CSV/TSV translation catalog's required fields and duplicates.

Minimum required columns: id, english, vietnamese. Optional capacity column is
`capacity_bytes`; optional encoded length column is `encoded_bytes`.
"""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

def read_rows(path: Path, delimiter: str | None):
    text = path.read_text(encoding="utf-8-sig")
    if delimiter is None:
        delimiter = "\t" if path.suffix.lower() in (".tsv", ".tab") else ","
    return delimiter, list(csv.DictReader(text.splitlines(), delimiter=delimiter))

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("catalog", type=Path)
    ap.add_argument("--delimiter", choices=["tab", "comma"], default=None)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()
    delim = "\t" if args.delimiter == "tab" else ("," if args.delimiter == "comma" else None)
    delim, rows = read_rows(args.catalog, delim)
    errors, warnings = [], []
    if not rows:
        errors.append("Catalog has no data rows")
        fields = []
    else:
        fields = list(rows[0])
    missing = [x for x in ("id", "english", "vietnamese") if x not in fields]
    if missing:
        errors.append("Missing required column(s): " + ", ".join(missing))
    ids = {}
    for line_no, row in enumerate(rows, start=2):
        ident = (row.get("id") or "").strip()
        if not ident:
            errors.append(f"Row {line_no}: empty id")
        elif ident in ids:
            errors.append(f"Row {line_no}: duplicate id {ident!r} (first at row {ids[ident]})")
        else:
            ids[ident] = line_no
        if not (row.get("english") or "").strip():
            warnings.append(f"Row {line_no} ({ident}): empty English source")
        if not (row.get("vietnamese") or "").strip():
            errors.append(f"Row {line_no} ({ident}): empty Vietnamese translation")
        cap = row.get("capacity_bytes")
        enc = row.get("encoded_bytes")
        if cap and enc:
            try:
                if int(enc) > int(cap):
                    errors.append(f"Row {line_no} ({ident}): encoded bytes {enc} exceed capacity {cap}")
            except ValueError:
                errors.append(f"Row {line_no} ({ident}): capacity_bytes/encoded_bytes must be integers")
    report = {
        "catalog": str(args.catalog), "delimiter": "tab" if delim == "\t" else "comma",
        "rows": len(rows), "columns": fields, "errors": errors, "warnings": warnings,
        "status": "PASS" if not errors else "FAIL",
    }
    output = json.dumps(report, indent=2, ensure_ascii=False)
    print(output)
    if args.json:
        args.json.write_text(output + "\n", encoding="utf-8")
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
