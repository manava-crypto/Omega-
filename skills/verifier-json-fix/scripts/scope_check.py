#!/usr/bin/env python3
"""Scope check before a verifier fix: is every finding a verifier problem, and is each ruling backed by evidence?

    python scope_check.py <record>/SCOPE.md [--findings <n>]

Reads the table in SCOPE.md (assets/SCOPE_TEMPLATE.md): one row per finding with RL World's category, the trainer's
label, our category and quoted evidence. Checks every row has an allowed category and evidence that names a place
(file:line, a sheet!cell or a verifier) and quotes words; with --findings, that the table has at least that many rows.

Our categories: VERIFIER (fixed in tests/verifier.json), NOT A DEFECT, and the outside ones GOLDEN, PROMPT, DATA,
PLATFORM, which are never edited on a fix request (pod rule, 2026-11-03: "we only fix verifier, not mess with
anything else"). Any outside row stops the fix: the user decides whether to fix only the verifier part or hand the task back
(sheet status "Non-Verifier Issues").
A GOLDEN, PROMPT or DATA row must also say "REVALIDATED ... on the original" and quote at least two things (the task's
own text and the source or instruction it contradicts); without that it is INCOMPLETE, never a STOP, so no
unchecked content claim reaches the user or the trainer.
Last line: SCOPE: OK <n> verifier, <k> not a defect (exit 0) | SCOPE: STOP <m> outside verifier.json (...) (exit 2) |
SCOPE: INCOMPLETE <reasons> (exit 1).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

INSIDE = {"VERIFIER", "NOT A DEFECT"}
OUTSIDE = {"GOLDEN", "PROMPT", "DATA", "PLATFORM"}


def rows(text: str) -> list[list[str]]:
    out, header = [], None
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        out.append(cells)
    if header is None:
        sys.exit("SCOPE: INCOMPLETE no table found")
    return [dict(zip(header, r)) for r in out]


def main() -> int:
    if {"-h", "--help"} & set(sys.argv[1:]):  # a newcomer's first try; it was read as a file name
        print(__doc__)
        return 0
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    want = int(sys.argv[sys.argv.index("--findings") + 1]) if "--findings" in sys.argv else None
    table = rows(path.read_text(encoding="utf-8"))
    problems, counts = [], {}
    if not table:
        # the template as written by the record has no rows: nothing was checked, so nothing may pass
        print("  no finding rows: add one row per External QC finding (and per item you add) before any edit")
        print("SCOPE: INCOMPLETE 0 rows")
        return 1
    for i, r in enumerate(table, 1):
        cat_key = next((k for k in r if k.startswith("our category")), None)
        ev_key = next((k for k in r if k.startswith("evidence")), None)
        cat = (r.get(cat_key, "") if cat_key else "").upper().replace("_", " ").strip()
        ev = r.get(ev_key, "") if ev_key else ""
        label = r.get("finding (review id / no.)", r.get("#", str(i)))
        if cat not in INSIDE | OUTSIDE:
            problems.append(f"row {i} ({label}): category '{cat or 'empty'}' not one of {sorted(INSIDE | OUTSIDE)}")
            continue
        if len(ev) < 15 or not re.search(r"[\"“'].{4,}[\"”']", ev) or not re.search(r"(:\d+|![A-Z]+\d+|\.json|\.md|\.xlsx|\.docx|verifier|instruction|golden|sheet)", ev, re.I):
            problems.append(f"row {i} ({label}): evidence needs a place (file:line, sheet!cell or verifier) and quoted words")
        note = r.get("note", "")
        if cat in ("GOLDEN", "PROMPT", "DATA"):
            # A content-defect claim is reported only after it was rechecked on the untouched original download, with
            # the task's own text and the source quoted (Anunay: "make sure to give a genuine non verifier check
            # result, that is a must"; #38's first GOLDEN row was a misread).
            quotes = len(re.findall(r"[\"“][^\"”]{4,}[\"”]", ev + " " + note))
            if "REVALIDATED" not in (ev + " " + note).upper() or "ORIGINAL" not in (ev + " " + note).upper() or quotes < 2:
                problems.append(f"row {i} ({label}): {cat} needs 'REVALIDATED ... on the original' in Evidence/Note with "
                                f"at least two quotes (the task file and the source or instruction it contradicts)")
                continue
        counts[cat] = counts.get(cat, 0) + 1
        if cat in OUTSIDE:
            print(f"OUTSIDE row {i}: {cat} | {label} | {r.get('verifier(s)', '')} | {ev[:160]}")
    if want is not None and len(table) < want:
        problems.append(f"{len(table)} rows for {want} findings: every finding needs a row")
    if problems:
        for p in problems:
            print("  " + p)
        print(f"SCOPE: INCOMPLETE {len(problems)} problem(s) in {len(table)} rows")
        return 1
    out = {k: v for k, v in counts.items() if k in OUTSIDE}
    if out:
        detail = ", ".join(f"{k} {v}" for k, v in sorted(out.items()))
        print("Stop before editing: tell the user. Only VERIFIER rows may be fixed; the rest go to the trainer.")
        print(f"SCOPE: STOP {sum(out.values())} outside verifier.json ({detail}); {counts.get('VERIFIER', 0)} verifier, "
              f"{counts.get('NOT A DEFECT', 0)} not a defect")
        return 2
    print(f"SCOPE: OK {counts.get('VERIFIER', 0)} verifier, {counts.get('NOT A DEFECT', 0)} not a defect ({len(table)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
