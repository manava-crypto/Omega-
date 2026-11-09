#!/usr/bin/env python3
"""round1_sweep.py: the whole-rubric hardening scan that makes round 1 the only round.

    python -X utf8 round1_sweep.py <fixed verifier.json> [--original <export verifier.json>]
        [--instruction <instruction.md>] [--feedback <-external-qc-feedback.json>]
        [--history <earlier round verifier.json> ...] [--dispositions <SWEEP_OK.md>] [--out <report.md>]

Every pattern here cost a DataOS round on an EKW-OTS fix in 2026-10/11 (references/one-round-checklist.md gives the
task and criterion behind each code). The scan reads EVERY verifier, not only the ones the feedback names, because
the next run's judges and reviewers read every verifier.

Codes (FAIL on a verifier this round changed; WARN elsewhere, which the report must list as next-round items):
  PREFIX      garbled agentic prefix "PASS only if Return only a boolean verdict" / "PASS only if You are" (6eydtrq9 r2,
              jicq r2: verdict/reasoning flips)
  ABSENCE     PASS rests on absence ("omits", "does not", "no ...", "limited to", "$.truncated == false") with no
              presence gate, so an empty or placeholder deliverable earns the weight (6eydtrq9 r3, mpp3gdze r2/r3)
  PAREN-ALT   an alternative figure in parentheses beside the main figure: judges read it as a range or a second
              requirement (mpp3gdze-1 r2 "$280.5m (normalized $276.4-276.8m)" -> oracle split)
  REWORDED-3  this verifier's prompt changed in two earlier rounds already: a third wording never held (p8f6vjxz-0
              deck_operating_model_decision r1-r4); restructure to the facts, or delete
  EXAMPLE     "for example", "such as", "e.g." beside a figure, label, sheet or record: judges demand the example
              (0i4x19ri brief_auditor_question_areas, 9dp numeric_tieouts "kept as examples")
  LIST        a closed list of 3+ quoted labels/values the answer must match: synonyms fail (p8f6vjxz-1 "Sell/Hold/Add",
              6eydtrq9 "like-for-like")
  ANCHORS     3+ accepted numeric anchors joined by "or": adding one more anchor per round never ends (p8f6vjxz-1 r1)
  PLACE       a sheet, slide, section or position the instruction does not name (jicq "standards section", vwr
              "slide 5", 0i4x "cites Chronology")
  OWNER       named individuals or an owner per item demanded (mpp3gdze-1 deck_transition_implications, vwr "Group
              Controller")
  CENTS       a cent-exact amount in a memo/deck/brief/plan check with no rounding tolerance (mpp3gdze-1 r4 whole
              dollars failed 2-1)
  WORDS       "in exact words", "explicitly flags/states/labels", "the word(s)", "verbatim": grade the fact, not the word
  UNIT        a unit literal ("22 hours/week") in a memo/deck check: cumulative or per-person exhibits fail (p8f6vjxz-0)
  TWIN        the same figure, date or ID graded in 2+ verifiers; with --original, only one side changed this round
              (p8f6vjxz-0 points-and-dollars twin, 9dp funding-gap twin)
  DATE-BAND   a band or convention pinned to one date/convention ("as of 10/23 only", "+-$0.02")
  UNNAMED     (with --feedback) a verifier changed this round that the feedback never names: RL World refuses it in a
              trainer upload ("changes the task beyond a fix"); it belongs in the DataOS copy and the next-round list
  RISK        (with --feedback) a named verifier whose remediation offers deletion, kept and reworded: RL World refused
              6eydtrq9-2-v16 for this ("Data inconsistent"); delete it or drop the demand outright

Dispositions: a file with one line per accepted hit, "<verifier> <CODE> <reason of 15+ chars>", turns that FAIL into
ACCEPTED (the reason goes in the report). Last line: SWEEP: OK (n warnings) or SWEEP: FAIL n.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FAIL_CODES = {"PREFIX", "ABSENCE", "PAREN-ALT", "REWORDED-3", "RISK", "UNNAMED"}
TEXT_DELIVERABLE = ("docx", "pptx", "md", "txt", "pdf")

RX = {
    "PREFIX": re.compile(r"PASS only if (Return only|You are|Determine|Evaluate|Check whether)", re.I),
    "ABSENCE_PASS": re.compile(
        r"PASS(?: only)? if[^.]{0,200}?\b(omits?|does not|do not|contains? no|no (?:other|additional|extra|itemized|separate|ledger|trade)\b|"
        r"limited to|without (?:any|a|the)|never|free of|is absent|not (?:present|included|repeated))", re.I),
    "PRESENCE_GATE": re.compile(r"(missing|empty|placeholder|blank|absent deliverable|no substantive|has no content|file is absent)", re.I),
    "PAREN-ALT": re.compile(r"\((?:or|also|alternatively|normalized|normalised|equivalently|about|approx\.?)\b[^)]{0,80}?\$?\d[\d,.]*[mkbMKB%]?\)", re.I),
    "EXAMPLE": re.compile(r"\b(for example|such as|e\.g\.|for instance)\b[^.;]{0,120}?(\$?\d[\d,.]*[mkbMKB%]?|\"[^\"]{2,40}\"|'[^']{2,40}'|[A-Z][a-z]+ (?:sheet|tab|slide|section|table))", re.I),
    "QUOTED": re.compile(r"[\"“']([^\"”']{2,40})[\"”']"),
    "ANCHOR_NUM": re.compile(r"(?<![\w.])[-+]?\$?\d[\d,]*\.?\d*\s?(?:%|pp|bps|x|m|k|bn|million|billion)?(?![\w.])", re.I),
    "PLACE": re.compile(
        r"\b(on (?:the )?(?:first|opening|title|final|last|summary|decision|cover|same) (?:slide|sheet|tab|page|section)|"
        r"on slide \d+|slide \d+ only|in the [A-Z][\w-]+ (?:section|sheet|tab|slide)|on the [A-Z][\w-]+ (?:sheet|tab|slide)|"
        r"beside the|next to the|in the standards section|in the (?:executive )?summary section only|"
        r"must (?:cite|name|reference) (?:the )?[A-Z][\w-]+ (?:sheet|tab)|sheet named|tab named|same view)", re.I),
    "OWNER": re.compile(r"\b(named (?:individual|person|owner|lead|backup|approver|reviewer)s?|owner (?:for|per) each|each [\w ]{0,30}?owner|"
                        r"by name\b|a different (?:reviewer|checker|person)|second[- ](?:person|reviewer)|independent (?:checker|reviewer) by name)", re.I),
    "CENTS": re.compile(r"\$\d{1,3}(?:,\d{3})+\.\d{2}\b"),
    "TOLERANCE": re.compile(r"(rounding|rounded|round to|±|\+/-|\+-|tolerance|within \$|within \d|whole[- ]dollar|nearest|or \$0\.0\d ?m|precision)", re.I),
    "WORDS": re.compile(r"\b(in exact words|exact words|exact phrase|verbatim|the words? [\"“']|explicitly (?:flags?|states?|labels?|names?|says?|writes?) (?:the (?:word|phrase|term)|[\"“'])|"
                        r"uses? the (?:word|phrase|term|label) [\"“'])", re.I),
    "DATE-BAND": re.compile(r"\b(as of \d{1,2}/\d{1,2}(?: only)?|\d{1,2}/\d{1,2} only|on \d{1,2} \w+ 20\d\d only|only the \d{1,2} \w+ 20\d\d|"
                            r"±\s?\$0\.0\d\b|\+/-\s?\$0\.0\d\b|within \$0\.0\d\b|exactly \$\d)", re.I),
    "LABEL_CHAIN": re.compile(r"\bexplicit(?:ly)? [\w -]{0,25}?\b(\w+, \w+,? (?:or|and) \w+) (?:conclusion|label|status|verdict|flag|rating|call)\b", re.I),
    "UNIT": re.compile(r"\b\d+(?:\.\d+)?\s?(?:hours?|hrs?|h|days?|weeks?|minutes?|mins?|FTEs?)\s?(?:/|per)\s?\w+", re.I),
    "ANCHOR_ID": re.compile(r"\b(?:[A-Z]{2,}-[A-Z0-9]{2,}(?:-[A-Z0-9]+)*|\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w* 20\d\d|20\d\d-\d\d-\d\d|\$\d[\d,]*\.?\d*\s?(?:m|k|bn|million)?)\b"),
}


def prompt_of(v):
    a = v.get("assertion") or {}
    for key in ("rubric", "agentic", "llm"):
        if isinstance(a.get(key), dict) and a[key].get("prompt"):
            return a[key]["prompt"]
    return ""


def deliverable_kind(v):
    f = ((v.get("source") or {}).get("file") or {})
    return (f.get("type") or Path(str((f.get("arguments") or {}).get("path", ""))).suffix.lstrip(".") or "").lower()


def is_truncation_guard(v):
    a = v.get("assertion") or {}
    d = a.get("deterministic") or {}
    return a.get("type") == "deterministic" and "truncated" in json.dumps(d)


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def names_in_feedback(fb):
    """Criteria at risk plus names in each remediation (the trainer_upload.py rule); and the remediation text per name."""
    named, deletable = set(), set()
    for it in fb.get("feedback", []):
        text = " ".join(str(it.get(k, "")) for k in ("explanation", "description", "remediation", "criteria"))
        for m in re.finditer(r"Criteria at risk \(\d+\):\s*(.+?)(?:\n|$)", text):
            for n in re.findall(r"`([^`]+)`", m.group(1)):
                named.add(n)
        rem = str(it.get("remediation", ""))
        for n in re.findall(r"`([^`]+)`", rem):
            named.add(n)
        if re.search(r"\b(delete|drop|remove) (?:the|this) criterion\b|or delete\b|add to instruction\.md", rem, re.I):
            for n in re.findall(r"`([^`]+)`", text):
                deletable.add(n)
    return named, deletable


def anchors(text):
    out = set()
    for m in RX["ANCHOR_ID"].finditer(text):
        t = m.group(0).strip()
        if re.fullmatch(r"\$\d[\d,]*\.?\d*\s?(?:m|k|bn|million)?", t):
            digits = re.sub(r"[^\d]", "", t)
            if len(digits) < 4:  # $5, $10: not an anchor
                continue
        out.add(t)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("fixed")
    ap.add_argument("--original")
    ap.add_argument("--instruction")
    ap.add_argument("--feedback")
    ap.add_argument("--history", nargs="*", default=[], help="earlier rounds' verifier.json files, oldest first")
    ap.add_argument("--dispositions")
    ap.add_argument("--out")
    a = ap.parse_args()

    fixed = load(a.fixed)
    fv = {v["name"]: v for v in fixed.get("verifiers", [])}
    ov = {v["name"]: v for v in load(a.original).get("verifiers", [])} if a.original else {}
    def graded_part(v):  # everything but the weight: a weight-only move is not a rewording
        return {"source": v.get("source"), "assertion": v.get("assertion"),
                "how": (v.get("metadata") or {}).get("how_justification"), "importance": (v.get("metadata") or {}).get("importance")}
    changed = {n for n in fv if a.original and (n not in ov or graded_part(ov[n]) != graded_part(fv[n]))}
    instr = Path(a.instruction).read_text(encoding="utf-8", errors="replace").lower() if a.instruction else ""
    named, deletable = names_in_feedback(load(a.feedback)) if a.feedback else (set(), set())
    history = [load(h) for h in a.history]
    disp = {}
    if a.dispositions:
        for line in Path(a.dispositions).read_text(encoding="utf-8").splitlines():
            parts = line.strip().split(None, 2)
            if len(parts) == 3 and len(parts[2]) >= 15:
                disp[(parts[0], parts[1])] = parts[2]

    hits = []  # (verifier, code, level, detail)

    def hit(n, code, detail):
        level = "FAIL" if (code in FAIL_CODES and (n in changed or not a.original or code in ("RISK", "UNNAMED"))) else "WARN"
        if (n, code) in disp:
            level = "ACCEPTED"
            detail += f"  [disposition: {disp[(n, code)]}]"
        hits.append((n, code, level, detail))

    # per-verifier patterns
    anchor_owner = defaultdict(set)
    for n, v in fv.items():
        p = prompt_of(v)
        kind = deliverable_kind(v)
        if is_truncation_guard(v):
            hit(n, "ABSENCE", "deterministic $.truncated guard: passes an empty workbook, fails a large correct one; delete and move its weight")
        if not p:
            continue
        if RX["PREFIX"].search(p):
            hit(n, "PREFIX", f'prompt starts "{p[:60]}..."; strip "PASS only if " before the judge text')
        if RX["ABSENCE_PASS"].search(p) and not RX["PRESENCE_GATE"].search(p):
            m = RX["ABSENCE_PASS"].search(p)
            hit(n, "ABSENCE", f'PASS rests on "{m.group(1)}" with no missing/empty/placeholder FAIL sentence')
        for m in RX["PAREN-ALT"].finditer(p):
            hit(n, "PAREN-ALT", f'parenthetical alternative "{m.group(0)}": state it as its own conditional sentence')
        for m in RX["EXAMPLE"].finditer(p):
            hit(n, "EXAMPLE", f'example beside a concrete value "{m.group(0)[:90]}": judges demand it; drop it or say "not required" is not enough, grade the concept')
        quoted = RX["QUOTED"].findall(p)
        if len(quoted) >= 3:
            seg = re.search(r"(?:[\"“'][^\"”']{2,40}[\"”'],?\s*(?:or|and|/)?\s*){3,}", p)
            if seg:
                hit(n, "LIST", f'closed list of labels {quoted[:5]}: replace with the fact the labels stand for')
        m = RX["LABEL_CHAIN"].search(p)
        if m:
            hit(n, "LIST", f'label chain "{m.group(0)[:80]}": a synonym fails; grade the conclusion the labels stand for')
        nums = [x for x in RX["ANCHOR_NUM"].findall(p) if re.search(r"\d", x)]
        orchain = re.search(r"(?:\$?\d[\d,.]*[mkbMKB%x]?\s*,?\s*(?:or|/)\s*){2,}\$?\d[\d,.]*", p)
        if orchain and len(nums) >= 3:
            hit(n, "ANCHORS", f'accepted-value chain "{orchain.group(0)[:80]}": give the rule that produces the values and a tolerance, keep the old values as reference only')
        else:
            for s in re.split(r"(?<=[A-Za-z%)\]])\.(?=\s|$)", p):
                if not re.search(r"\b(accept(?:ed|able)?|any one (?:of|suffices)|one of the following)\b", s, re.I):
                    continue
                vals = [x for x in RX["ANCHOR_NUM"].findall(s) if re.search(r"\d", x)]
                if len(vals) >= 3:
                    hit(n, "ANCHORS", f'accepted-value sentence with {len(vals)} figures "{s.strip()[:90]}...": a partial list is read as the whole list; state the rule and tolerance instead')
                    break
        if kind in TEXT_DELIVERABLE:
            m = RX["UNIT"].search(p)
            if m:
                hit(n, "UNIT", f'unit literal "{m.group(0)}" in a {kind} check: grade the fact in any unit or aggregation against the source value (p8f6vjxz-0 "22 hours/week" took 4 rounds)')
        for m in RX["PLACE"].finditer(p):
            loc = m.group(0)
            key = re.sub(r"^(on|in) (the )?", "", loc, flags=re.I).lower()
            if key.split(" ")[0] not in instr:
                hit(n, "PLACE", f'placement pin "{loc}" the instruction does not name: accept the fact anywhere in the deliverable')
        for m in RX["OWNER"].finditer(p):
            if "named" not in instr or m.group(0).lower().startswith(("a different", "second", "independent")):
                hit(n, "OWNER", f'"{m.group(0)}": accept name, role or team unless the instruction says "named"; a second-person check the instruction never asks for is UNASKED')
        if kind in TEXT_DELIVERABLE and RX["CENTS"].search(p) and not RX["TOLERANCE"].search(p):
            hit(n, "CENTS", f'cent-exact {RX["CENTS"].search(p).group(0)} in a {kind} check with no rounding tolerance: add "(rounding to whole dollars or $0.01m is fine)"')
        for m in RX["WORDS"].finditer(p):
            hit(n, "WORDS", f'"{m.group(0)}": grade the fact in any wording')
        for m in RX["DATE-BAND"].finditer(p):
            hit(n, "DATE-BAND", f'"{m.group(0)}": enumerate every convention or date the sources allow and give each its figures')
        for t in anchors(p):
            anchor_owner[t].add(n)
        # history: how many earlier rounds changed this prompt
        if history:
            versions = []
            for h in history:
                hv = {x["name"]: x for x in h.get("verifiers", [])}
                versions.append(prompt_of(hv[n]) if n in hv else None)
            seq = [x for x in versions if x is not None] + [p]
            rewrites = sum(1 for i in range(1, len(seq)) if seq[i] != seq[i - 1])
            if rewrites >= 3 or (rewrites >= 2 and n in changed):
                hit(n, "REWORDED-3", f"prompt reworded {rewrites} times across rounds: restructure to the underlying facts (any form, any placement) or delete")

    # twins: the same anchor in 2+ verifiers, one side edited this round
    for t, owners in sorted(anchor_owner.items()):
        if len(owners) < 2:
            continue
        ch = owners & changed
        if a.original and ch and owners - ch:
            for n in sorted(ch):
                hit(n, "TWIN", f'anchor "{t}" also graded in {sorted(owners - ch)}: apply the same carve-out there, or name one owner')
        elif not a.original and len(owners) >= 2:
            hit(sorted(owners)[0], "TWIN", f'anchor "{t}" graded in {sorted(owners)}: one owner per fact, or the same accepted set in each')

    # feedback scope
    if a.feedback and a.original:
        for n in sorted(changed):
            if n not in named:
                hit(n, "UNNAMED", "changed this round but the feedback never names it: cannot ship in the trainer upload; DataOS copy + next-round list only")
        for n in sorted(deletable & named):
            if n in fv and n in ov and graded_part(fv[n]) != graded_part(ov[n]):
                hit(n, "RISK", "the remediation offers deletion; the criterion was kept and reworded. Read the item's claim against the new text: if the demand is still there, delete the criterion or drop the demand")
        for n in sorted(named):
            if n in ov and n in fv and graded_part(fv[n]) == graded_part(ov[n]):
                hit(n, "RISK", "named in the feedback and unchanged: an unaddressed item unless the report says NOT A DEFECT with evidence (disposition line: '<name> RISK NOT A DEFECT: <evidence>')")

    # report
    lines = [f"# round1 sweep: {a.fixed}", "",
             f"verifiers {len(fv)}; changed this round {len(changed) if a.original else 'n/a (no --original)'}; feedback-named {len(named) if a.feedback else 'n/a'}", ""]
    by_level = defaultdict(list)
    for n, code, level, detail in hits:
        by_level[level].append((n, code, detail))
    for level in ("FAIL", "ACCEPTED", "WARN"):
        if by_level[level]:
            lines += [f"## {level} ({len(by_level[level])})", ""]
            lines += [f"- {n} | {code} | {detail}" for n, code, detail in by_level[level]]
            lines.append("")
    fails = len(by_level["FAIL"])
    verdict = f"SWEEP: FAIL {fails}" if fails else f"SWEEP: OK ({len(by_level['WARN'])} warnings, {len(by_level['ACCEPTED'])} accepted)"
    lines.append(verdict)
    text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text, end="")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
