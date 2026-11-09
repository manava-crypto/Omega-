#!/usr/bin/env python3
"""Find formulas in the task's input workbooks whose range stops before more rows of the same data.

Reads only. Give it a task folder (holding environment/), a rev folder (holding task_files/) or workbook paths.

    python source_range_scan.py <folder or .xlsx> [...]

A source formula such as =SUMIFS('Charges'!$I$5:$I$22, ...) over a table that runs to row 24 silently drops rows 23-24.
When the golden copies that figure, and a verifier pins it, both are wrong. The instruction usually says to correct
source errors. That is a GOLDEN finding, outside verifier.json, plus a verifier fix to grade the corrected value.
Medical/nurses R2047 v9 (2026-10-31): the transfer/ED lookback was $29,740 instead of $47,540, and equipment
$4,860 instead of $4,989.

A flagged range is a candidate, not a defect. Check whether the cut-off rows meet the formula's own criteria
(entity, date window, category). In that same task the Labor and Therapy ranges were cut short too, but their extra
rows were other residents and outside the window, so those totals stood. Rows after the range count as data when they
are as full as the rows inside it, are not SUM/SUBTOTAL rows, and are not labelled total, note, source or check. The
first blank row ends the table. On 13 RL World tasks this flagged only the one real case.
"""
import re
import sys
from pathlib import Path

import openpyxl

REF = re.compile(r"(?:'([^']+)'|([A-Za-z0-9_]+))!\$?([A-Z]{1,3})\$?(\d+):\$?([A-Z]{1,3})\$?(\d+)")
FOOT = re.compile(r"total|note|source|check|subtotal|grand|memo|^n/?a$", re.I)
AGG = re.compile(r"=\s*(SUM|SUBTOTAL|AGGREGATE)\(", re.I)


def filled(ws, r):
    return sum(1 for c in ws[r] if c.value not in (None, ""))


def data_like(ws, r, typical):
    cells = [c.value for c in ws[r]]
    if any(isinstance(x, str) and AGG.match(x) for x in cells):
        return False
    if any(isinstance(x, str) and FOOT.search(x) for x in cells[:3]):
        return False
    return filled(ws, r) >= max(2, 0.6 * typical)


def scan(path: Path):
    wb = openpyxl.load_workbook(path)
    seen, hits = set(), []
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if not (isinstance(v, str) and v.startswith("=")):
                    continue
                for m in REF.finditer(v):
                    sh = m.group(1) or m.group(2)
                    start, end = int(m.group(4)), int(m.group(6))
                    if sh not in wb.sheetnames or end - start < 3 or (sh, end) in seen:
                        continue
                    t = wb[sh]
                    typical = sorted(filled(t, r) for r in range(start, end + 1))[(end - start) // 2]
                    extra = []
                    for r in range(end + 1, min(t.max_row, end + 400) + 1):
                        if filled(t, r) == 0 or not data_like(t, r, typical):
                            break
                        extra.append(r)
                    if extra:
                        seen.add((sh, end))
                        hits.append(f"{path.name}: {ws.title}!{c.coordinate} sums '{sh}' rows {start}-{end}, but rows "
                                    f"{extra[0]}-{extra[-1]} look like more of the same data. Formula: {v[:140]}")
    return hits


def main():
    if {"-h", "--help"} & set(sys.argv[1:]):
        print(__doc__)
        return
    paths = []
    for a in sys.argv[1:] or ["."]:
        p = Path(a)
        if p.suffix.lower() in (".xlsx", ".xlsm"):
            paths.append(p)
            continue
        for base in (p / "environment", p / "task_files" / "environment"):
            if base.is_dir():
                paths += sorted(x for x in base.rglob("*") if x.suffix.lower() in (".xlsx", ".xlsm"))
                break
    if not paths:
        sys.exit("no input workbooks found (looked under environment/ and task_files/environment/)")
    total = 0
    for p in paths:
        try:
            hits = scan(p)
        except Exception as exc:
            print(f"{p.name}: could not read ({exc})")
            continue
        for h in hits:
            print(h)
        total += len(hits)
    print(f"SOURCE RANGES: {total} truncated-range candidate(s) in {len(paths)} workbook(s)."
          + (" For each, check whether the cut-off rows meet the formula's criteria, then whether the golden or a verifier"
             " carries the truncated figure." if total else ""))


if __name__ == "__main__":
    main()
