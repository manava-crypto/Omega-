#!/usr/bin/env python3
"""Write the fix plan skeleton from the export, the labelled findings and the earlier run; check a filled plan.

    python -X utf8 fix_plan.py --export <export zip | task_files dir | verifier.json> --findings <RLWORLD_FEEDBACK.md | findings.json>
        [--snapshot <snapshot.md from task_snapshot.py>] [--out FIX_PLAN.md] [--overwrite]
    python -X utf8 fix_plan.py --check FIX_PLAN.md

The plan has six tables. You fill the empty cells before any edit (SKILL.md S2, references/settle-playbook.md):
  A. Findings: one row per finding (id, category, label, verifiers, remediation quoted) + Verdict, Tier, Carried out as,
     Twin, Evidence.
  B. Golden ledger: every verifier the golden failed or split on in the earlier run + Ruling, Evidence.
  C. Anchors: one row per named verifier with every figure, band, date or count it pins + Readings, Decision.
  D. Unlabelled findings: each one + Asked (the user's answer, quoted).
  E. Fairness hits on the named verifiers (fairness_lint.py codes) + Settled. Add rows for hits that appear after an edit.
  F. Siblings and extracts (free text).

--check reads the filled plan, writes SCOPE.md beside it (the pod's non-verifier check, from A and B) and runs
scope_check.py on it, then ends PLAN: COMPLETE or PLAN: INCOMPLETE (<what is missing>). Rules: tables A to E must exist;
every A row has a Verdict in {FIX, NOT A DEFECT, OUTSIDE VERIFIER.JSON (GOLDEN|PROMPT|DATA|PLATFORM), CANNOT SETTLE,
DEFERRED} and non-empty Evidence; a FIX row has Tier 1 or 2 (tier 3 is DEFERRED, never built), Twin filled ("none" is an
answer) and, for tier 1, "Carried out as"; an Agree row that is not FIX has "user:" in its Evidence (the user's words); an
OUTSIDE GOLDEN / PROMPT / DATA row has "REVALIDATED ... on the original" and two quotes in its Evidence; every B row has a
Ruling in {VERIFIER, GOLDEN, NOT A DEFECT} and Evidence (GOLDEN: revalidated the same way); every C row has Readings and a
Decision; every D row has Asked; every E row has Settled. A cell may hold a pipe written as \\|.

Findings file: the record's RLWORLD_FEEDBACK.md (a markdown table whose header has "Label" and "Remediation"; the id,
category, review, verifier and label columns are found by their header words; lines of the form `alias = full_name` or
"`alias` = `full_name`" under the table define short names), or a JSON {"findings": [{"id", "category", "verifiers":
[...], "label", "remediation", "review"}]}, or RL World's QC feedback JSON ({"feedback": [...]}, no labels).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fairness_lint  # noqa: E402

VERDICTS = {"FIX", "NOT A DEFECT", "OUTSIDE VERIFIER.JSON", "CANNOT SETTLE", "DEFERRED"}
OUTSIDE_KINDS = {"GOLDEN", "PROMPT", "DATA", "PLATFORM"}
RULINGS = {"VERIFIER", "GOLDEN", "NOT A DEFECT"}
MONEY = re.compile(r"[$£€]\s?\d(?:[\d,]*\d)?(?:\.\d+)?(?:\s?(?:m|million|k|thousand|bn|billion))?", re.I)
PERCENT = re.compile(r"\b\d+(?:\.\d+)?\s?%")
DECIMAL = re.compile(r"(?<![\w.$£€])\d+\.\d{3,}(?![\w.])")
BIGNUM = re.compile(r"(?<![\w.,$£€-])(?:\d{1,3}(?:,\d{3})+|\d{5,})(?:\.\d+)?(?![\w,-])")
BAND = re.compile(r"(?<![\w.,])\d[\d,]*(?:\.\d+)?\s?(?:to|-|–)\s?\d[\d,]*(?:\.\d+)?(?![\d.,\w])")
DATE = re.compile(r"\b(?:\d{1,2}\s)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s\d{1,2}(?:,?\s\d{4})?\b|"
                  r"\b\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}\b|"
                  r"\b\d{4}-\d{2}-\d{2}\b")
COUNTWORD = re.compile(r"\b(?:all|every|each|at least|exactly)\s+(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\b", re.I)
SNAKE = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+")
ALIAS = re.compile(r"^\s*(?:[-*]\s*)?`?([a-z][a-z0-9_]+)`?\s*(?:=|:|->|→)\s*`?([a-z][a-z0-9_]+)`?\s*$", re.M)
PIPE = re.compile(r"(?<!\\)\|")
TABLE_KEY = re.compile(r"^([A-F])\b")


def load_verifier_json(path: Path) -> dict:
    if path.is_file() and path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.endswith("tests/verifier.json")]
            if not names:
                sys.exit(f"{path}: no tests/verifier.json inside")
            return json.loads(zf.read(sorted(names, key=len)[0]).decode("utf-8-sig"))
    if path.is_dir():
        cands = list(path.rglob("tests/verifier.json"))
        if not cands:
            sys.exit(f"{path}: no tests/verifier.json under it")
        path = sorted(cands, key=lambda p: len(p.parts))[0]
    return json.loads(path.read_text(encoding="utf-8-sig"))


def prompt_of(v: dict) -> str:
    a = v.get("assertion", {})
    t = a.get("type")
    if t in ("rubric", "agentic"):
        return (a.get(t) or {}).get("prompt", "") or ""
    return ""


def split_cells(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip().replace("\\|", "|") for c in PIPE.split(s)]


def parse_md_tables(text: str) -> list[tuple[str, list[str], list[list[str]]]]:
    """Every markdown table: (nearest heading above, header cells, rows)."""
    out, heading = [], ""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("#"):
            heading = ln.strip("# ").strip()
        if ln.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            header = split_cells(ln)
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                cells = split_cells(lines[j])
                cells += [""] * (len(header) - len(cells))
                rows.append(cells[: len(header)])
                j += 1
            out.append((heading, header, rows))
            i = j
            continue
        i += 1
    return out


def col(header: list[str], *words: str) -> int | None:
    low = [h.lower() for h in header]
    for w in words:
        for k, h in enumerate(low):
            if w in h:
                return k
    return None


def load_findings(path: Path, names: list[str]) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    items: list[dict] = []
    aliases: dict[str, str] = {}
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        for f in data.get("findings") or data.get("feedback") or []:
            items.append({"id": str(f.get("id", "")), "category": f.get("category", ""), "review": f.get("review", ""),
                          "verifiers_raw": ", ".join(f.get("verifiers", [])) if isinstance(f.get("verifiers"), list)
                          else str(f.get("verifiers") or f.get("artifacts") or ""),
                          "label": f.get("label", ""), "remediation": f.get("remediation", "")})
    else:
        for m in ALIAS.finditer(text):
            if m.group(2) in names and m.group(1) not in names:
                aliases[m.group(1)] = m.group(2)
        for heading, header, rows in parse_md_tables(text):
            if col(header, "remediation") is None or col(header, "label") is None:
                continue
            ci, cc, cr = col(header, "#", "id", "item"), col(header, "category"), col(header, "review", "finding", "source")
            cv, cl, cm = col(header, "verifier"), col(header, "label"), col(header, "remediation")
            if cv is None:
                continue
            for r in rows:
                if not any(r):
                    continue
                items.append({"id": r[ci] if ci is not None else "", "category": r[cc] if cc is not None else "",
                              "review": r[cr] if cr is not None else "", "verifiers_raw": r[cv],
                              "label": r[cl], "remediation": r[cm]})
            break
    for it in items:
        it["verifiers"], it["unresolved"] = resolve_names(it["verifiers_raw"], names, items, aliases)
    return items


def match_name(tok: str, names: list[str], aliases: dict[str, str]) -> str | None:
    if tok in names:
        return tok
    if tok in aliases:
        return aliases[tok]
    parts = tok.split("_")
    cands = [n for n in names if len(tok) >= 8 and (tok in n or n in tok)]
    if not cands and len(parts) >= 2:
        cands = [n for n in names if set(parts) <= set(n.split("_"))]
    return cands[0] if len(cands) == 1 else None


def resolve_names(raw: str, names: list[str], items: list[dict], aliases: dict[str, str]) -> tuple[list[str], list[str]]:
    """Verifier names in a cell, plus the tokens that matched nothing (they are listed as UNRESOLVED)."""
    found, missing = [], []
    for tok in SNAKE.findall(raw):
        n = match_name(tok, names, aliases)
        if n and n not in found:
            found.append(n)
        elif not n:
            missing.append(tok)
    m = re.search(r"\bsame\s+(\d+)?\s*(\w+)?", raw, re.I)
    if not found and m:
        want = int(m.group(1)) if m.group(1) else None
        qual = (m.group(2) or "").lower()
        for prev in reversed(items):
            vs = prev.get("verifiers") or []
            if not vs:
                continue
            if want is not None and len(vs) != want:
                continue
            if qual and qual not in ("as", "verifiers", "three", "two") and qual not in prev["verifiers_raw"].lower() \
                    and not any(qual in v for v in vs):
                continue
            return list(vs), missing
        missing.append(raw.strip())
    return found, missing


def parse_snapshot(path: Path) -> tuple[list[dict], set[str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    rows, seen = [], set()
    for heading, header, trows in parse_md_tables(text):
        if not header or "verifier" not in header[0].lower():
            continue
        oracle_cols = [k for k, h in enumerate(header) if h.strip().lower().startswith("oracle")]
        flag_col = col(header, "flag")
        for r in trows:
            name = r[0].strip("` ")
            if not name:
                continue
            seen.add(name)
            fails = [header[k] for k in oracle_cols if r[k].strip().upper() in ("F", "ERR")]
            flags = r[flag_col] if flag_col is not None else ""
            why = []
            if fails:
                why.append("ORACLE-NOT-PASS (" + ", ".join(fails) + ")")
            if "ORACLE-SPLIT" in flags:
                why.append("ORACLE-SPLIT")
            if why:
                rows.append({"verifier": name, "why": "; ".join(why)})
    m = re.search(r"^## Look first\n(.*?)(?:\n## |\Z)", text, re.S | re.M)
    if m:
        for ln in m.group(1).splitlines():
            mm = re.match(r"^- (\S+): (.+)$", ln.strip())
            if mm and "ORACLE" in mm.group(2) and not any(x["verifier"] == mm.group(1) for x in rows):
                rows.append({"verifier": mm.group(1), "why": mm.group(2)})
    return rows, seen


def anchors_in(text: str) -> list[str]:
    """Figures pinned with no alternative, band or example wording near them, plus every band, date and count word."""
    out = []
    near = fairness_lint.RX["anchor_near"]
    for rx in (MONEY, PERCENT, DECIMAL, BIGNUM):
        for m in rx.finditer(text):
            s = m.group(0).strip().rstrip(",")
            window = text[max(0, m.start() - 60): m.end() + 60]
            if s and s not in out and not re.fullmatch(r"\d{4}", s) and not near.search(window):
                out.append(s)
    for rx in (BAND, DATE, COUNTWORD):
        for m in rx.finditer(text):
            s = m.group(0).strip().rstrip(",")
            if s and s not in out and not re.fullmatch(r"\d{4}", s):
                out.append(s)
    return out[:25]


def esc(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def write_plan(a) -> int:
    vj = load_verifier_json(Path(a.export))
    verifiers = vj.get("verifiers", [])
    names = [v["name"] for v in verifiers]
    byname = {v["name"]: v for v in verifiers}
    items = load_findings(Path(a.findings), names)
    named = []
    for it in items:
        for n in it["verifiers"]:
            if n not in named:
                named.append(n)
    unresolved = [it for it in items if it["unresolved"]]
    ledger, seen = ([], set())
    if a.snapshot:
        ledger, seen = parse_snapshot(Path(a.snapshot))
    hits = fairness_lint.lint(verifiers, only=set(named))
    out = []
    out.append(f"# FIX PLAN: {Path(a.export).name}")
    out.append("")
    n_agree = sum(1 for i in items if i["label"].lower().startswith("agree"))
    n_dis = sum(1 for i in items if i["label"].lower().startswith("disagree"))
    out.append(f"Export: `{a.export}`. Findings: `{a.findings}` ({len(items)} items, {n_agree} Agree, {n_dis} Disagree, "
               f"{len(items) - n_agree - n_dis} unlabelled). Earlier run: `{a.snapshot or 'none given'}`. "
               f"Verifiers in the file: {len(verifiers)}; named by findings: {len(named)}.")
    out.append("")
    out.append("Fill every empty cell before the first edit (references/settle-playbook.md). Verdicts: FIX, NOT A DEFECT, "
               "OUTSIDE VERIFIER.JSON (GOLDEN | PROMPT | DATA | PLATFORM), CANNOT SETTLE, DEFERRED. Tiers (references/change-policy.md): "
               "1 named Agree, 2 evidenced extra; tier 3 is DEFERRED. Evidence = file:line, cell, run id with the judge's reason, "
               "or a recompute; an OUTSIDE golden/prompt/data row needs 'REVALIDATED <date> on the original' and two quotes. "
               "`fix_plan.py --check` must end PLAN: COMPLETE.")
    out.append("")
    out.append("## A. Findings")
    out.append("")
    out.append("| # | Finding | Category | Label | Verifiers | Remediation (verbatim) | Verdict | Tier | Carried out as | Twin | Evidence |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for k, it in enumerate(items, 1):
        vs = ", ".join(it["verifiers"])
        if it["unresolved"]:
            vs = (vs + "; " if vs else "") + "UNRESOLVED: " + esc(", ".join(it["unresolved"]))
        out.append(f"| {esc(it['id'] or k)} | {esc(it['review'])} | {esc(it['category'])} | {esc(it['label']) or 'unlabelled'} | {vs} | "
                   f"{esc(it['remediation'])} |  |  |  |  |  |")
    if unresolved:
        out.append("")
        out.append(f"UNRESOLVED verifier names on {len(unresolved)} row(s): put the exact names in the Verifiers cell.")
    out.append("")
    out.append("## B. Golden ledger (settle before any edit)")
    out.append("")
    out.append("| Verifier | Earlier run | Ruling (VERIFIER / GOLDEN / NOT A DEFECT) | Evidence |")
    out.append("|---|---|---|---|")
    for r in ledger:
        out.append(f"| {r['verifier']} | {esc(r['why'])} |  |  |")
    if not ledger:
        out.append("| (none: the golden passed every verifier in every graded run, or no earlier run was given) | - | NOT A DEFECT | snapshot.md |")
    out.append("")
    out.append("## C. Anchors to enumerate (reading matrix), one row per named verifier")
    out.append("")
    out.append("| Verifier | Anchors it pins | Readings (per anchor: value, basis, file:cell) | Decision (keep pin: instruction line / accept all / grade on stated basis) |")
    out.append("|---|---|---|---|")
    n_anchor = 0
    for n in named:
        v = byname.get(n)
        if not v:
            continue
        anc = anchors_in(prompt_of(v))
        if anc:
            out.append(f"| {n} | {esc('; '.join(anc))} |  |  |")
            n_anchor += 1
    if not n_anchor:
        out.append("| (no pinned figure, date or count in the named verifiers) | - | - | - |")
    out.append("")
    out.append("## D. Unlabelled findings (ask before treating as Agree or leaving)")
    out.append("")
    out.append("| # | Verifiers | Asked (the user's answer, quoted) |")
    out.append("|---|---|---|")
    n_unl = 0
    for k, it in enumerate(items, 1):
        lab = it["label"].lower()
        if not (lab.startswith("agree") or lab.startswith("disagree")):
            out.append(f"| {esc(it['id'] or k)} | {', '.join(it['verifiers']) or esc(it['verifiers_raw'])} |  |")
            n_unl += 1
    if not n_unl:
        out.append("| (none) | - | - |")
    out.append("")
    out.append("## E. Fairness hits on the named verifiers (settle each: fixed, or kept with the instruction line)")
    out.append("")
    out.append("| Verifier | Code | Hit | Settled |")
    out.append("|---|---|---|---|")
    for h in hits:
        out.append(f"| {h['verifier']} | {h['code']} | {esc(h['text'])} |  |")
    if not hits:
        out.append("| (no hits on the named verifiers) | - | - | - |")
    out.append("")
    out.append("## F. Siblings and extracts")
    out.append("")
    out.append("- SWEEP: every verifier that shares a figure, ID, label list or demand with a FIX row (apply_verifier_fix.py prints the SWEEP; grep before the build).")
    out.append("- EXTRACTS: every extract_text / extract_xlsx on a multi-sheet solver workbook gets a per-verifier range in round 1 (xlsx_ranges.py); write the ranges here.")
    out.append("")
    text = "\n".join(out) + "\n"
    dest = Path(a.out)
    if dest.exists() and not a.overwrite:
        sys.exit(f"{dest} exists; pass --overwrite to replace it (a filled plan is lost that way)")
    dest.write_text(text, encoding="utf-8")
    print(f"wrote {dest}: {len(items)} findings ({len(named)} named verifiers, {len(unresolved)} rows with UNRESOLVED names), "
          f"{len(ledger)} golden-ledger rows, {n_anchor} anchor rows, {n_unl} unlabelled, {len(hits)} fairness hits")
    print("PLAN: SKELETON (fill it, then fix_plan.py --check)")
    return 0


def tables_by_key(text: str) -> dict[str, tuple[list[str], list[list[str]]]]:
    out: dict[str, tuple[list[str], list[list[str]]]] = {}
    for heading, hdr, rows in parse_md_tables(text):
        m = TABLE_KEY.match(heading.strip())
        if not m:
            continue
        key = m.group(1)
        if key in out:
            sys.exit(f"PLAN: INCOMPLETE (two tables under heading {key}: keep one)")
        out[key] = (hdr, rows)
    return out


def cell(hdr: list[str], r: list[str], key: str) -> str:
    for k, h in enumerate(hdr):
        if h.lower().startswith(key) or key in h.lower():
            return r[k].strip() if k < len(r) else ""
    return ""


def revalidated(evid: str) -> bool:
    up = evid.upper()
    return "REVALIDATED" in up and "ORIGINAL" in up and len(re.findall(r"[\"“][^\"”]{4,}[\"”]", evid)) >= 2


def write_scope(plan: Path, hdrA, rowsA, hdrB, rowsB) -> Path:
    """SCOPE.md in scope_check.py's format, derived from the plan (one row per finding, plus golden-ledger rows)."""
    lines = [f"# Scope check (derived from {plan.name} by fix_plan.py --check; edit the plan, not this file)", "",
             "| # | Finding (review id / no.) | Verifier(s) | RL World category | Trainer label | Our category | Evidence (file:line, \"quote\") | Note |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rowsA:
        if not r or r[0].startswith("("):
            continue
        verdict = cell(hdrA, r, "verdict").upper()
        if verdict.startswith("OUTSIDE"):
            m = re.search(r"\((GOLDEN|PROMPT|DATA|PLATFORM)\)", verdict)
            cat = m.group(1) if m else "GOLDEN"
        elif verdict.split("(")[0].strip() == "FIX":
            cat = "VERIFIER"
        elif verdict in ("NOT A DEFECT", "CANNOT SETTLE", "DEFERRED"):
            cat = verdict
        else:
            cat = ""
        lines.append(f"| {esc(r[0])} | {esc(cell(hdrA, r, 'finding'))} | {esc(cell(hdrA, r, 'verifiers'))} | {esc(cell(hdrA, r, 'category'))} | "
                     f"{esc(cell(hdrA, r, 'label'))} | {cat} | {esc(cell(hdrA, r, 'evidence'))} | tier {esc(cell(hdrA, r, 'tier'))} |")
    for r in rowsB:
        if not r or r[0].startswith("("):
            continue
        ruling = cell(hdrB, r, "ruling").upper()
        lines.append(f"| ledger | {esc(r[1])} | {esc(r[0])} | golden ledger | - | {ruling} | {esc(cell(hdrB, r, 'evidence'))} | from the earlier run |")
    dest = plan.with_name("SCOPE.md")
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dest


def check_plan(path: Path) -> int:
    text = path.read_text(encoding="utf-8-sig")
    tables = tables_by_key(text)
    problems: list[str] = []
    counts = {}
    for key in "ABCDE":
        if key not in tables:
            problems.append(f"table {key} missing (keep every table; a table with nothing to settle holds one '(none)' row)")
    hdrA, rowsA = tables.get("A", ([], []))
    real = [r for r in rowsA if r and not r[0].startswith("(")]
    counts["findings"] = len(real)
    if "A" in tables and not real:
        problems.append("A: no findings rows")
    for r in real:
        rid = r[0]
        verdict = cell(hdrA, r, "verdict").upper()
        vbase = verdict.split("(")[0].strip()
        tier = cell(hdrA, r, "tier")
        label = cell(hdrA, r, "label").lower()
        evid = cell(hdrA, r, "evidence")
        carried = cell(hdrA, r, "carried out as")
        twin = cell(hdrA, r, "twin")
        if "UNRESOLVED" in cell(hdrA, r, "verifiers"):
            problems.append(f"A #{rid}: Verifiers still UNRESOLVED")
        if vbase not in VERDICTS:
            problems.append(f"A #{rid}: Verdict {verdict or '(empty)'} is not one of {sorted(VERDICTS)}")
        if vbase == "OUTSIDE VERIFIER.JSON":
            m = re.search(r"\((GOLDEN|PROMPT|DATA|PLATFORM)\)", verdict)
            if not m:
                problems.append(f"A #{rid}: OUTSIDE VERIFIER.JSON needs its kind: (GOLDEN), (PROMPT), (DATA) or (PLATFORM)")
            elif m.group(1) != "PLATFORM" and not revalidated(evid):
                problems.append(f"A #{rid}: a {m.group(1)} claim needs 'REVALIDATED <date> on the original' and two quotes in Evidence")
        if not evid:
            problems.append(f"A #{rid}: Evidence empty")
        if vbase == "FIX":
            if tier not in ("1", "2"):
                problems.append(f"A #{rid}: a FIX needs Tier 1 or 2 (got {tier or '(empty)'}; a tier-3 item is DEFERRED)")
            if tier == "1" and not carried:
                problems.append(f"A #{rid}: tier 1 needs 'Carried out as' (the new text that carries out the remediation)")
            if not twin:
                problems.append(f"A #{rid}: Twin empty (write the twin verifier on the other deliverable, or 'none')")
        if label.startswith("agree") and vbase != "FIX" and "user:" not in evid.lower():
            problems.append(f"A #{rid}: an Agree finding left unfixed needs the user's words in Evidence ('user: ...')")
    hdrB, rowsB = tables.get("B", ([], []))
    real = [r for r in rowsB if r and not r[0].startswith("(")]
    counts["golden"] = len(real)
    for r in real:
        ruling = cell(hdrB, r, "ruling").upper()
        evid = cell(hdrB, r, "evidence")
        if ruling not in RULINGS:
            problems.append(f"B {r[0]}: Ruling {ruling or '(empty)'} not one of {sorted(RULINGS)}")
        if not evid:
            problems.append(f"B {r[0]}: Evidence empty")
        elif ruling == "GOLDEN" and not revalidated(evid):
            problems.append(f"B {r[0]}: GOLDEN needs 'REVALIDATED <date> on the original' and two quotes in Evidence")
    hdrC, rowsC = tables.get("C", ([], []))
    real = [r for r in rowsC if r and not r[0].startswith("(")]
    counts["anchor rows"] = len(real)
    for r in real:
        if not cell(hdrC, r, "readings"):
            problems.append(f"C {r[0]}: Readings empty")
        if not cell(hdrC, r, "decision"):
            problems.append(f"C {r[0]}: Decision empty")
    hdrD, rowsD = tables.get("D", ([], []))
    real = [r for r in rowsD if r and not r[0].startswith("(")]
    counts["unlabelled"] = len(real)
    for r in real:
        if not cell(hdrD, r, "asked"):
            problems.append(f"D #{r[0]}: Asked empty (the user decides unlabelled items)")
    hdrE, rowsE = tables.get("E", ([], []))
    real = [r for r in rowsE if r and not r[0].startswith("(")]
    counts["fairness"] = len(real)
    for r in real:
        if not cell(hdrE, r, "settled"):
            problems.append(f"E {r[0]} {r[1] if len(r) > 1 else ''}: Settled empty")
    for p in problems:
        print("MISSING: " + p)
    summary = ", ".join(f"{v} {k}" for k, v in counts.items())
    if problems:
        print(f"PLAN: INCOMPLETE ({len(problems)} missing; {summary})")
        return 1
    scope = write_scope(path, hdrA, rowsA, hdrB, rowsB)
    r = subprocess.run([sys.executable, "-X", "utf8", str(Path(__file__).with_name("scope_check.py")), str(scope),
                        "--findings", str(counts["findings"])], capture_output=True, text=True, encoding="utf-8")
    scope_out = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
    last = scope_out[-1] if scope_out else "SCOPE: INCOMPLETE (scope_check.py gave no output)"
    print(f"wrote {scope}")
    if last.startswith("SCOPE: INCOMPLETE"):
        # the pod's scope check wants a place (file:line, cell or verifier) and quoted words in every Evidence cell
        for ln in scope_out[:-1]:
            print("MISSING (scope): " + ln.strip())
        print(last)
        print(f"PLAN: INCOMPLETE (scope check: evidence cells need a place and quoted words; {summary})")
        return 1
    print(last)
    print(f"PLAN: COMPLETE ({summary})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--export")
    ap.add_argument("--findings")
    ap.add_argument("--snapshot")
    ap.add_argument("--out", default="FIX_PLAN.md")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--check", help="a filled FIX_PLAN.md to check")
    a = ap.parse_args()
    if a.check:
        return check_plan(Path(a.check))
    if not (a.export and a.findings):
        ap.error("--export and --findings are needed to write a plan (or --check <plan>)")
    return write_plan(a)


if __name__ == "__main__":
    sys.exit(main())
