#!/usr/bin/env python3
"""Scan every verifier for the twelve fairness properties (references/fairness-contract.md). Candidates, not verdicts.

    python -X utf8 fairness_lint.py <verifier.json | zip | task dir> [--export <verifier.json | zip>] [--plan FIX_PLAN.md]
        [--only v1,v2] [--all]

With --export, a verifier whose text, source or weight differs from the export is "changed"; hits on changed verifiers are
OPEN until the plan settles them (a row in a table with columns Verifier | Code | ... | Settled, as FIX_PLAN.md section E,
with Settled filled). Hits on unchanged verifiers are listed as pre-existing (not open) unless --all. Without --export every
verifier counts as changed. F12 hits are notes (never open). Last line: FAIRNESS: n hits, k on changed, j open.

Codes: F2 pinned anchor, F3 self-reference, F4 absence-only PASS, F5 literal or closed label list, F6 placement pin,
F7 quantified list, F8 cascade, F9 loosened wording (run the reverse check), F10 vague word / weekend date / cell address,
F11 shared figure without an owner, F12 the source command cannot see what the prompt grades (note). F1 (unasked, against
the instruction) is literal_demand_scan.py's job; run it on the rev folder.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import zipfile
from pathlib import Path

RX = {
    "self_ref": re.compile(r"\b(?:as|per) (?:the )?(?:prompt|instruction|instructions|task) (?:requires|specifies|states|says|asks)|"
                           r"\bper the instructions?\b|\bas required by the (?:prompt|instruction)\b|\bas instructed\b", re.I),
    "absence": re.compile(r"\b(?:contains? no|does not (?:introduce|state|include|restate|contain|add|present)|"
                          r"no \w+(?: \w+){0,3} (?:appears?|is stated|is shown|is included)|is free of|never (?:states|includes|introduces))\b", re.I),
    "presence_words": re.compile(r"\b(?:missing|empty|absent|omitted|omits|placeholder|header-only|not stated|not shown|not present|blank|"
                                 r"no substantive|lacks|does not exist)\b", re.I),
    "positive": re.compile(r"\b(?:states|shows|identifies|presents|includes|contains|lists|gives|reports|names|provides|computes|"
                           r"reconciles|are stated|is stated|is identified|is shown|are shown|quantif|explains|records|documents|"
                           r"ties|supports|cites|is present|are present)\w*\b", re.I),
    "literal_cue": re.compile(r"\b(?:exact|exactly|verbatim|literal(?:ly)?|the words?|labell?ed|the phrase|wording|titled|named|headed)\b", re.I),
    "quoted": re.compile(r"[\"'“‘]([^\"'”’]{3,80})[\"'”’]"),
    "label_list": re.compile(r"\b(?:labels?|status(?:es)?|marked as|one of|flag(?:ged)? as|classif\w+ as)\b[^.;]{0,40}?"
                             r"((?:[A-Z][A-Z0-9/_-]{2,}|[\"'“‘][^\"'”’]{1,25}[\"'”’])(?:\s*(?:,|/|or|and)\s*(?:[A-Z][A-Z0-9/_-]{2,}|[\"'“‘][^\"'”’]{1,25}[\"'”’])){1,})"),
    "pin": re.compile(r"\bslides? \d+(?:\s*(?:-|to|and)\s*\d+)?\b|\bon (?:the|a|its) [\w'&/ -]{1,40}? (?:sheet|tab|slide|worksheet)\b|"
                      r"\b(?:opening|leading|first|final|last|title|summary) (?:section|slide|page|sheet|tab)\b|"
                      r"\bin section \d+(?:\.\d+)?\b|\b(?:sheet|tab|worksheet) (?:named|called|titled) [\"'“‘]", re.I),
    "list": re.compile(r"\b(?:all|every|each)\s+(?:of\s+the\s+)?(?:\w+\s+){0,2}(?:two|three|four|five|six|seven|eight|nine|ten|\d{1,2})\b|"
                       r"\(\s*(?:1|i)\s*\)[^.]{0,400}\(\s*(?:[4-9]|iv|v)\s*\)", re.I),
    "cascade": re.compile(r"\b(?:given|assuming|using) the (?:correct|golden|right|expected)\b|\bif the \w+ is correct\b|"
                          r"\bcorrect(?:ly)? (?:upstream|input|derived)\b", re.I),
    "loosen": re.compile(r"\b(?:not required|need not|optional|rather than (?:a )?requirements?|accepted examples?|as (?:an )?examples?|"
                         r"is welcome|no longer required|may be omitted|not mandatory|acceptable alternatives?|accept(?:s|ed)? any|"
                         r"any (?:equivalent|explicit|defensible|reasonable|clear)|in any (?:words|form|wording)|or equivalent)\b", re.I),
    "vague": re.compile(r"\b(?:adequate(?:ly)?|appropriate(?:ly)?|reasonabl[ey]|sufficient(?:ly)?|clearly|properly|meaningful(?:ly)?|robust(?:ly)?|"
                        r"thorough(?:ly)?|comprehensive(?:ly)?|well[- ]supported|substantial(?:ly)?)\b", re.I),
    "anchor_near": re.compile(r"\b(?:for example|such as|at least|band|between|to|or|any|about|approximately|within|±|at most|under|over)\b", re.I),
    "cell": re.compile(r"\b[A-Z][A-Za-z0-9_ ]{0,30}![A-Z]{1,3}\d{1,5}\b|\b(?<![\w$])[A-Z]{1,2}\d{1,4}:[A-Z]{1,2}\d{1,4}\b"),
    "date": re.compile(r"\b(\d{1,2})\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?,?\s(\d{4})\b|"
                       r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s(\d{1,2}),?\s(\d{4})\b|\b(\d{4})-(\d{2})-(\d{2})\b"),
    "money": re.compile(r"[$£€]\s?\d(?:[\d,]*\d)?(?:\.\d+)?"),
    "ident": re.compile(r"\b[A-Z]{2,}[A-Z0-9]*-[A-Z0-9-]*\d[A-Z0-9-]*\b"),
    "decimal": re.compile(r"(?<![\w.$£€])\d+\.\d{3,}(?![\w.])"),
    "bignum": re.compile(r"(?<![\w.,$£€-])(?:\d{1,3}(?:,\d{3})+|\d{5,})(?:\.\d+)?(?![\w,-])"),
    "owner": re.compile(r"\b(?:graded by|not (?:graded )?here|owned by|is graded in|grade only|judge only|assess only|not this|elsewhere)\b", re.I),
    "visual": re.compile(r"\b(?:charts?|graphs?|images?|visuals?|colou?r|fills?|icons?|shading)\b", re.I),
    "formula": re.compile(r"\bformula-driven|live formulas?|hard-?coded|typed (?:numbers?|constants?|values?)|not typed\b", re.I),
}
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def load(path: Path) -> dict:
    if path.is_file() and path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.endswith("tests/verifier.json")]
            if not names:
                sys.exit(f"{path}: no tests/verifier.json inside")
            return json.loads(zf.read(sorted(names, key=len)[0]).decode("utf-8-sig"))
    if path.is_dir():
        cands = sorted(path.rglob("tests/verifier.json"), key=lambda p: len(p.parts))
        if not cands:
            sys.exit(f"{path}: no tests/verifier.json under it")
        path = cands[0]
    return json.loads(path.read_text(encoding="utf-8-sig"))


def prompt_of(v: dict) -> str:
    a = v.get("assertion", {})
    t = a.get("type")
    if t in ("rubric", "agentic"):
        return (a.get(t) or {}).get("prompt", "") or ""
    return ""


def source_of(v: dict) -> tuple[str, str, dict]:
    s = v.get("source", {}) or {}
    f = s.get("file") or {}
    return (f.get("type") or s.get("type") or "", f.get("command") or "", f.get("arguments") or {})


def pass_clause(p: str) -> str:
    m = re.search(r"\bFAIL\b", p)
    return p[: m.start()] if m else p


def snippet(text: str, start: int, end: int, width: int = 70) -> str:
    a, b = max(0, start - width), min(len(text), end + width)
    return ("..." if a else "") + text[a:b].replace("\n", " ") + ("..." if b < len(text) else "")


def weekend(m: re.Match) -> str | None:
    g = m.groups()
    try:
        if g[0]:
            d = dt.date(int(g[2]), MONTHS[g[1][:3].lower()], int(g[0]))
        elif g[3]:
            d = dt.date(int(g[5]), MONTHS[g[3][:3].lower()], int(g[4]))
        else:
            d = dt.date(int(g[6]), int(g[7]), int(g[8]))
    except (ValueError, KeyError):
        return None
    return f"{m.group(0)} is a {d.strftime('%A')}" if d.weekday() >= 5 else None


def lint(verifiers: list[dict], only: set[str] | None = None, export: dict | None = None) -> list[dict]:
    """Hits: {verifier, code, kind, text, note(bool)}. `export` (name -> verifier) marks changed verifiers and enables F9."""
    hits: list[dict] = []

    def add(v, code, kind, text, note=False):
        hits.append({"verifier": v["name"], "code": code, "kind": kind, "text": text, "note": note})

    # F11: figures and IDs shared by several verifiers with no owner wording
    shared: dict[str, list[str]] = {}
    for v in verifiers:
        p = prompt_of(v)
        for rx in (RX["money"], RX["ident"]):
            for m in rx.finditer(p):
                shared.setdefault(m.group(0), [])
                if v["name"] not in shared[m.group(0)]:
                    shared[m.group(0)].append(v["name"])
    for v in verifiers:
        if only is not None and v["name"] not in only:
            continue
        p = prompt_of(v)
        typ, cmd, args = source_of(v)
        old = (export or {}).get(v["name"])
        oldp = prompt_of(old) if old else None
        if not p:
            # deterministic: pins only
            if any(k in args for k in ("sheet", "cell_range", "sheet_names")):
                add(v, "F6", "PIN", f"deterministic argument pins layout: {json.dumps({k: args[k] for k in args if k in ('sheet', 'cell_range', 'sheet_names')})}")
            continue
        pc = pass_clause(p)
        # F2 pinned anchors in the PASS clause without an alternative nearby
        for rx in (RX["money"], RX["decimal"], RX["bignum"]):
            for m in rx.finditer(pc):
                window = pc[max(0, m.start() - 60): m.end() + 60]
                if not RX["anchor_near"].search(window):
                    add(v, "F2", "ANCHOR", f"{m.group(0)} pinned with no alternative or band nearby: {snippet(pc, m.start(), m.end(), 50)}")
                    break
        # F3
        m = RX["self_ref"].search(p)
        if m:
            add(v, "F3", "SELF-REF", snippet(p, m.start(), m.end()))
        # F4 absence-only
        m = RX["absence"].search(pc)
        if m and not RX["presence_words"].search(p) and not RX["positive"].search(pc):
            add(v, "F4", "ABSENCE", f"PASS rests on absence with no presence gate: {snippet(pc, m.start(), m.end())}")
        # F5 literal phrases and closed label lists
        for m in RX["quoted"].finditer(p):
            before = p[max(0, m.start() - 45): m.start()]
            if RX["literal_cue"].search(before) and len(m.group(1).split()) >= 2:
                add(v, "F5", "LITERAL", f"literal wording demanded: {snippet(p, m.start(), m.end(), 40)}")
                break
        m = RX["label_list"].search(p)
        if m:
            add(v, "F5", "LABELS", f"closed list of accepted labels: {snippet(p, m.start(), m.end(), 30)}")
        # F6 placement pins
        m = RX["pin"].search(p)
        if m:
            add(v, "F6", "PIN", snippet(p, m.start(), m.end(), 50))
        if "sheet_names" in args:
            add(v, "F6", "PIN", f"source sheet_names={args['sheet_names']} (a solver's tab names differ: use range)")
        # F7 quantified lists in a binary verdict
        m = RX["list"].search(pc)
        if m:
            add(v, "F7", "LIST", snippet(pc, m.start(), m.end(), 50))
        # F8 cascade
        m = RX["cascade"].search(p)
        if m:
            add(v, "F8", "CASCADE", snippet(p, m.start(), m.end()))
        # F9 loosened wording added since the export: the reverse check is due
        if oldp is not None and oldp != p:
            new_loose = {x.lower() for x in RX["loosen"].findall(p)} - {x.lower() for x in RX["loosen"].findall(oldp)}
            if new_loose:
                add(v, "F9", "LOOSENED", f"added {sorted(new_loose)}: read the wrong and hollow answers against it (reverse check)")
        # F10 vague words in PASS, weekend dates, cell addresses
        m = RX["vague"].search(pc)
        if m and not RX["anchor_near"].search(pc[max(0, m.start() - 80): m.end() + 80]):
            add(v, "F10", "VAGUE", f"'{m.group(0)}' with no concrete anchor near it: {snippet(pc, m.start(), m.end(), 40)}")
        for m in RX["date"].finditer(p):
            w = weekend(m)
            if w:
                add(v, "F10", "WEEKEND", w + " (accept the preceding business day?)")
                break
        m = RX["cell"].search(p)
        if m:
            add(v, "F10", "CELL", f"cell address in the prompt pins layout and leaks placement: {snippet(p, m.start(), m.end(), 30)}")
        # F11 shared figure with no owner wording
        if not RX["owner"].search(p):
            for tok, owners in shared.items():
                if v["name"] in owners and len(owners) > 1:
                    add(v, "F11", "SHARED", f"{tok} also graded in {', '.join(o for o in owners if o != v['name'])}: name the owner or give the twin the same rule")
                    break
        # F12 visibility notes
        if typ == "pptx" and cmd == "extract_text" and RX["visual"].search(p):
            add(v, "F12", "BLIND", f"pptx.extract_text cannot see {RX['visual'].search(p).group(0)}; agentic render tools or a command that sees it", note=True)
        if typ == "xlsx" and cmd in ("extract_text",) and RX["formula"].search(p):
            add(v, "F12", "BLIND", "xlsx.extract_text may not distinguish typed values from formulas in this library; check what the extractor returns", note=True)
        if typ == "xlsx" and cmd in ("extract_text", "extract_xlsx") and "range" not in args and "sheet_names" not in args:
            add(v, "F12", "BUDGET", "whole-workbook extract: size a per-verifier range on the golden and every solver file (xlsx_ranges.py)", note=True)
    return hits


def settled_from_plan(path: Path) -> set[tuple[str, str]]:
    import fix_plan  # same folder
    out = set()
    for heading, header, rows in fix_plan.parse_md_tables(path.read_text(encoding="utf-8-sig")):
        low = [h.lower() for h in header]
        if "verifier" in low[0] and "code" in " ".join(low) and "settled" in " ".join(low):
            ci, cs = next(k for k, h in enumerate(low) if "code" in h), next(k for k, h in enumerate(low) if "settled" in h)
            for r in rows:
                if r[cs].strip() and not r[0].startswith("("):
                    out.add((r[0].strip(), r[ci].strip()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("target")
    ap.add_argument("--export")
    ap.add_argument("--plan")
    ap.add_argument("--only")
    ap.add_argument("--all", action="store_true", help="hits on unchanged verifiers count as open too")
    a = ap.parse_args()
    vj = load(Path(a.target))
    verifiers = vj.get("verifiers", [])
    export = None
    changed: set[str] = {v["name"] for v in verifiers}
    if a.export:
        ex = load(Path(a.export))
        export = {v["name"]: v for v in ex.get("verifiers", [])}
        changed = {v["name"] for v in verifiers if export.get(v["name"]) != v}
    only = set(a.only.split(",")) if a.only else None
    settled = settled_from_plan(Path(a.plan)) if a.plan else set()
    hits = lint(verifiers, only=only, export=export)
    n_changed = n_open = 0
    for h in hits:
        is_changed = h["verifier"] in changed
        key = (h["verifier"], h["code"])
        state = "note" if h["note"] else ("settled" if key in settled else ("OPEN" if (is_changed or a.all) else "pre-existing"))
        if is_changed:
            n_changed += 1
        if state == "OPEN":
            n_open += 1
        tag = "changed" if is_changed else "unchanged"
        print(f"{h['code']} {h['kind']:<9} {h['verifier']} [{tag}, {state}]: {h['text']}")
    if not a.export and not a.all:
        print(f"FAIRNESS INVENTORY: {len(hits)} hits on {len({h['verifier'] for h in hits})} verifiers (no --export: nothing is open; "
              f"run with --export after a build to get the open hits)")
        return 0
    print(f"FAIRNESS: {len(hits)} hits, {n_changed} on changed verifiers, {n_open} open")
    return 1 if n_open else 0


if __name__ == "__main__":
    sys.exit(main())
