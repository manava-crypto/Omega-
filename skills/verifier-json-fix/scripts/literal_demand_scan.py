#!/usr/bin/env python3
"""List what each verifier demands literally that instruction.md never asks for: candidates for SKILL.md step 3, question 1.

Reads only. Give it a task folder (holding tests/verifier.json), a rev folder (holding task_files/) or a download.

    python literal_demand_scan.py <folder> [--only name,name] [--all]

For every judged verifier (rubric or agentic) it prints, per category:
  ID       an identifier (CUS-26-184, ORD-CA44B8, RW-CV-6B29F1) the prompt names
  FILE     a file name the prompt names
  PHRASE   a quoted phrase the prompt requires
  PRECISE  a number given to 4 or more decimals (or to the cent with 7+ digits)
  PLACE    a placement pin: one sheet, section, slide, row or labelled block
  LIST     a fixed-size list ("all five", "each of the eight", numbered items (1)..(5)+)
  LABELS   a closed list of accepted status words ("PASS, FAIL, or PENDING", "FAIL/mismatch/requires-correction labels"):
           judges reject other clear wording ("superseded", "not appropriate"); grade the concept instead
  DATE     a date the prompt requires that falls on a Saturday or Sunday: a correct answer may use the business-day-
           adjusted date (a 14 Nov 2026 deadline was met on Fri 13 Nov and a judge failed the golden for it)
and where the literal appears: in the instruction ("instr", fine), only in the input data ("data": a fact the solver
must find, so ask whether the instruction asks for it to be stated), or nowhere ("NONE": the golden's own value or an
internal code; the strongest UNASKED candidate). PLACE and LIST are flagged when the instruction does not name that
sheet or that count.

These are candidates, not verdicts. In 13 RL World tasks (2026-10-30/31) about 40 of 90 verifier fixes were of these
kinds, and every one was found by hand, often only after a review round. Settle each candidate with the four questions.
"""
import argparse
import json
import logging
import re
import sys
import zipfile
from pathlib import Path

ID = re.compile(r"\b[A-Z][A-Z0-9]{1,9}(?:-[A-Z0-9]{2,12}){1,4}\b")
FILE = re.compile(r"\b[\w.-]+\.(?:xlsx|xlsm|docx|pptx|pdf|csv|json|md|txt)\b", re.I)
QUOTE = re.compile(r"(?<![A-Za-z])['‘“\"]([^'’”\"]{6,90})['’”\"](?![A-Za-z])")
PRECISE = re.compile(r"(?<![\w.])(?:\d{1,3}(?:,\d{3})+|\d+)\.\d{4,}(?!\d)|(?<![\w.])\$?\d{1,3}(?:,\d{3}){2,}\.\d{2}(?!\d)")
PLACE = re.compile(
    r"\b(?:on|in|read) the ([A-Z][\w&/ -]{2,40}?) (?:sheet|worksheet|slide|tab|section)\b"
    r"|\b(opening|lead|first|dedicated|single|one labell?ed|same) (?:decision[/ ]summary |summary |decision |)"
    r"(?:section|block|slide|row|sheet|worksheet|statement|table)\b",
    re.I,
)
NUMWORD = {"three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
LIST = re.compile(r"\b(?:all|each of the|every one of the|exactly) (" + "|".join(NUMWORD) + r"|\d{1,2})\b", re.I)
NUMBERED = re.compile(r"\((\d{1,2})\)")
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
DATES = re.compile(
    r"\b(\d{1,2})[ -]([A-Za-z]{3,9})[ -](20\d\d)\b"          # 14-Nov-2026, 14 November 2026
    r"|\b([A-Za-z]{3,9}) (\d{1,2}),? (20\d\d)\b"             # November 14, 2026
    r"|\b(20\d\d)-(\d\d)-(\d\d)\b")                        # 2026-11-14
LABELS = re.compile(
    r"\b[A-Z]{3,}(?:\s*/\s*[A-Z][\w-]{2,}){2,}\b"                          # PASS/FAIL/PENDING
    r"|\b[A-Z]{3,},\s*[A-Z]{3,},?\s*(?:or|and)\s*[A-Z]{3,}\b"                # PASS, FAIL, or PENDING
    r"|\b[\w-]+(?:/[\w-]+){2,}\s+(?:labels?|statuses|status values|tokens)\b")  # FAIL/mismatch/... labels


DEADLINE = re.compile(r"\b(?:due|deadline|by|before|submi\w*|response|respond|filing|file|signing|sign-off|cutoff|cut-off|"
                      r"payment date|pay(?:able)? on|settle\w*|closing|close date|deliver\w*)\b", re.I)


def weekend_dates(text):
    """Weekend dates used as deadlines (a deadline word within ~60 characters); event dates are left alone."""
    import datetime
    out = []
    for m in DATES.finditer(text):
        if not DEADLINE.search(text[max(0, m.start() - 60):m.end() + 60]):
            continue
        try:
            if m.group(1):
                d = datetime.date(int(m.group(3)), MONTHS[m.group(2)[:3].lower()], int(m.group(1)))
            elif m.group(4):
                d = datetime.date(int(m.group(6)), MONTHS[m.group(4)[:3].lower()], int(m.group(5)))
            else:
                d = datetime.date(int(m.group(7)), int(m.group(8)), int(m.group(9)))
        except (KeyError, ValueError):
            continue
        if d.weekday() >= 5:
            out.append(f"{m.group(0)} is a {d.strftime('%A')}")
    return out
SKIP_IDS = {"PASS", "FAIL", "IFRS", "IAS", "GAAP", "ACT-360", "ACT-365F"}


def text_of(path: Path) -> str:
    """Plain text of an input file, best effort; empty when the format cannot be read here."""
    s = path.suffix.lower()
    try:
        if s in (".txt", ".md", ".csv", ".json"):
            return path.read_text(errors="ignore")
        if s in (".xlsx", ".xlsm"):
            import openpyxl
            wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            out = []
            for ws in wb:
                out.append(ws.title)
                for row in ws.iter_rows(values_only=True):
                    out.extend(str(v) for v in row if v is not None)
            return "\n".join(out)
        if s in (".docx", ".pptx"):
            with zipfile.ZipFile(path) as z:
                return " ".join(re.sub(r"<[^>]+>", " ", z.read(n).decode("utf8", "ignore"))
                                for n in z.namelist() if n.endswith(".xml") and ("word/" in n or "ppt/slides/" in n))
        if s == ".pdf":
            try:
                import pdfplumber
                with pdfplumber.open(path) as pdf:
                    return "\n".join(p.extract_text() or "" for p in pdf.pages)
            except Exception:
                return ""
    except Exception:
        return ""
    return ""


def find_task(folder: Path) -> Path:
    for cand in (folder, folder / "task_files"):
        if (cand / "tests" / "verifier.json").is_file():
            return cand
    hits = sorted(folder.rglob("tests/verifier.json"))
    if not hits:
        sys.exit(f"no tests/verifier.json under {folder}")
    return hits[-1].parent.parent


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower()).strip()


def where(lit: str, instr: str, data: str) -> str:
    n = norm(lit)
    if n in instr:
        return "instr"
    return "data" if n in data else "NONE"


def main():
    logging.disable(logging.WARNING)  # pdfminer font warnings are noise here
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("folder", type=Path)
    ap.add_argument("--only", default="", help="comma-separated verifier names")
    ap.add_argument("--all", action="store_true", help="also show literals the instruction itself contains")
    a = ap.parse_args()
    task = find_task(a.folder)
    instr_raw = (task / "instruction.md").read_text(errors="ignore")
    instr = norm(instr_raw)
    data = norm(" ".join(text_of(p) for p in sorted((task / "environment").rglob("*")) if p.is_file()))
    only = {x for x in a.only.split(",") if x}
    vs = json.loads((task / "tests" / "verifier.json").read_text())["verifiers"]
    total = {}
    for v in vs:
        asr = v.get("assertion") or {}
        if asr.get("type") not in ("rubric", "agentic") or (only and v["name"] not in only):
            continue
        p = (asr.get(asr["type"]) or {}).get("prompt") or ""
        found = []
        for m in ID.finditer(p):
            lit = m.group(0)
            if lit in SKIP_IDS or re.fullmatch(r"[A-Z]+-\d{1,2}", lit):
                continue
            found.append(("ID", lit, where(lit, instr, data)))
        for m in FILE.finditer(p):
            found.append(("FILE", m.group(0), where(m.group(0), instr, data)))
        for m in QUOTE.finditer(p):
            lit = m.group(1).strip()
            if len(lit.split()) >= 2:
                found.append(("PHRASE", lit, where(lit, instr, data)))
        for m in PRECISE.finditer(p):
            lit = m.group(0)
            # A number in neither source is usually a computed result: legitimate when it re-derives from the sources and
            # every defensible reading is accepted (questions 2 and 3), a defect when it pins the golden's own convention.
            w = where(lit, instr, data)
            found.append(("PRECISE", lit, "derived" if w == "NONE" else w))
        # A named sheet is navigation, not a pin, when the prompt accepts equivalent sheet names elsewhere.
        flexible = re.search(r"names its sheets differently|equivalent (?:worksheet|sheet) names?|any equivalent worksheet|wherever (?:they|it) (?:sit|appear)", p, re.I)
        for m in PLACE.finditer(p):
            sheet = (m.group(1) or "").strip()
            if sheet and flexible:
                continue
            hit = "instr" if sheet and norm(sheet) in instr else "NONE"
            found.append(("PLACE", m.group(0).strip(), hit))
        for m in LIST.finditer(p):
            k = m.group(1).lower()
            n = NUMWORD.get(k, int(k) if k.isdigit() else 0)
            if n >= 3:
                word = [w for w, x in NUMWORD.items() if x == n]
                hit = "instr" if (str(n) in instr_raw or (word and word[0] in instr)) else "NONE"
                found.append(("LIST", m.group(0), hit))
        for lit in weekend_dates(p):
            found.append(("DATE", lit, "check"))
        for m in LABELS.finditer(p):
            found.append(("LABELS", m.group(0), "check"))
        nums = sorted({int(x) for x in NUMBERED.findall(p)})
        if len(nums) >= 5 and nums[:5] == [1, 2, 3, 4, 5]:
            found.append(("LIST", f"numbered items (1)..({nums[-1]})", "NONE"))
        seen, rows = set(), []
        for cat, lit, w in found:
            if (cat, lit) in seen or (w == "instr" and not a.all):
                continue
            seen.add((cat, lit))
            rows.append((cat, lit, w))
        if rows:
            print(f"## {v['name']} [{asr['type']} w={(v.get('metadata') or {}).get('weight', 0):.4f}]")
            for cat, lit, w in sorted(rows, key=lambda r: ({"NONE": 0, "check": 1, "data": 2, "derived": 3}.get(r[2], 4), r[0])):
                print(f"  {cat:7} {w:5} {lit[:110]}")
                total[(cat, w)] = total.get((cat, w), 0) + 1
    print("\nsummary (category, where): " + ", ".join(f"{c}/{w} {n}" for (c, w), n in sorted(total.items())) if total else "\nno literal demands beyond the instruction")
    print("NONE = in neither the instruction nor the input text: the strongest UNASKED candidates. Settle each with SKILL.md step 3.")


if __name__ == "__main__":
    main()
