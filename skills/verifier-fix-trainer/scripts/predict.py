#!/usr/bin/env python3
"""PREDICT: before a DataOS run, list the Majors its reviewers would raise, on EVERY verifier, and gate on them.

    python -X utf8 predict.py check <record> --round <n> [--task <unpacked task folder>] [--reviews-dir <folder>]
    python -X utf8 predict.py settle <record> --verifier <name> --family <FAMILY> --state kept|risk
                                     (--quote "<words from instruction.md>" | --evidence <file in the record>) [--why "..."]
    python -X utf8 predict.py inventory <task folder | verifier.json | zip>     the sweep alone, nothing written

Why: 13 of the 29 failed DataOS runs after 2026-11-06 were a new Major on a verifier the feedback never named, found
one run at a time (#21: five runs on the same sheet-pin pattern). The old lint flagged those verifiers but counted hits
on unchanged verifiers as "pre-existing". PREDICT looks at all of them, from four sources:

  sweep    fairness_lint + the literal-demand scan + two patterns the runs taught us: DEFAULT_PASS (a criterion that
           returns true when it cannot assess, #62) and UNIT (a time unit the instruction never uses, #46)
  runs     the last graded run's matrix: a verifier every solver failed, one the empty answer passed, one the oracle failed
  reviews  every Major of the local reviews (practice_review.py) bound to this round's verifier.json
  pipeline fail-level findings of the pipeline's pin and alternative checks, when the round ran them

Gate families (tier A; each item must be settled): PIN, LITERAL, LABELS, ABSENCE, DEFAULT_PASS, UNIT, UNASKED_ID, RUNS,
REVIEW, PIPELINE. Information only (tier B): ANCHOR, SHARED, LIST, VAGUE, SELF_REF, CASCADE, WEEKEND, SPLIT, BLIND.

An item is settled when it is gone (the round's edit removed the hit), or KEPT (the instruction asks for it: the quote
is searched in instruction.md, or an evidence file in the record exists), or RISK (kept knowing a reviewer may flag
it; counts toward the report and needs the user's word in approvals.jsonl before the gate clears). A settlement is
bound to the verifier's text: edit the verifier and the item opens again.

Writes <record>/round<n>/PREDICT.json and PREDICT.md. Last line: PREDICT: CLEAR <verifiers hash> (a tier-A items settled)
or PREDICT: OPEN n (...). Exit 0 only on CLEAR.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fairness_lint  # noqa: E402
import literal_demand_scan as lds  # noqa: E402
import qcio  # noqa: E402
import task_snapshot as ts  # noqa: E402

TIER_A = ("PIN", "LITERAL", "LABELS", "ABSENCE", "DEFAULT_PASS", "UNIT", "UNASKED_ID", "RUNS", "REVIEW", "PIPELINE")
FIRST_ROUND_REVIEWS, LATER_ROUND_REVIEWS = 4, 2   # Anunay, 2026-11-11

RX_DEFAULT_PASS = re.compile(
    r"(?:not assessable|cannot be (?:assessed|determined|verified|measured|established|seen)|unable to (?:assess|determine|verify)|"
    r"no reliable \w+(?: \w+){0,3}|if (?:the )?extraction (?:exposes|shows|returns) no)[^.]{0,160}?"
    r"\b(?:return true|treat (?:it|the requirement|this) as (?:met|satisfied|passing|not assessable)|PASS\b|pass by default)"
    r"|\b(?:default to|otherwise|in (?:that|this) case)\s+(?:return true|PASS)\b"
    r"|\breturn true (?:if|when) (?:it|this|the \w+) cannot\b", re.I)
RX_UNIT = re.compile(r"\b(\d{1,3}|one|two|three|four|five|six|seven|eight|nine|ten)[- ]((?:business|working|calendar|trading)[- ]days?|days?|weeks?|months?|quarters?|hours?)\b", re.I)
UNIT_ROOT = {"business day": "business day", "working day": "working day", "calendar day": "calendar day", "trading day": "trading day",
             "day": "day", "week": "week", "month": "month", "quarter": "quarter", "hour": "hour"}
RX_PIN_NAME = re.compile(r"\bon (?:the|a|its) ([\w'&/ -]{1,40}?) (?:sheet|tab|slide|worksheet)\b", re.I)
PIPELINE_CHECKS = ("cell_address_pinned_check", "pinned_value_prescreen_check", "accepted_alternative_compatibility_check",
                   "tab_naming_check", "verifier_requirements_pin_mismatch_check")
FAIRNESS_FAMILY = {("F6", "PIN"): "PIN", ("F10", "CELL"): "PIN", ("F5", "LITERAL"): "LITERAL", ("F5", "LABELS"): "LABELS",
                   ("F4", "ABSENCE"): "ABSENCE", ("F2", "ANCHOR"): "ANCHOR", ("F11", "SHARED"): "SHARED", ("F7", "LIST"): "LIST",
                   ("F10", "VAGUE"): "VAGUE", ("F3", "SELF-REF"): "SELF_REF", ("F8", "CASCADE"): "CASCADE",
                   ("F10", "WEEKEND"): "WEEKEND", ("F12", "BLIND"): "BLIND", ("F12", "BUDGET"): "BLIND", ("F9", "LOOSENED"): "LOOSENED"}


def text_hash(v: dict) -> str:
    return hashlib.sha256(json.dumps(v, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]


def unit_root(u: str) -> str:
    u = re.sub(r"s$", "", u.lower().replace("-", " "))
    return UNIT_ROOT.get(u, u)


def sweep(spec: dict, task_dir: Path | None) -> list[dict]:
    """Tier A and B items from the text alone. With a task folder the instruction filters pins and literals."""
    vs = spec.get("verifiers", [])
    items: list[dict] = []
    instr_raw = instr = data = None
    if task_dir and (task_dir / "instruction.md").is_file():
        try:
            instr_raw, instr, data = lds.task_texts(task_dir)
        except Exception:
            instr_raw = (task_dir / "instruction.md").read_text(encoding="utf-8", errors="ignore")
            instr, data = lds.norm(instr_raw), ""

    def add(v, family, text, source="sweep", tier=None):
        items.append({"verifier": v if isinstance(v, str) else v["name"], "family": family, "text": " ".join(str(text).split())[:300],
                      "source": source, "tier": tier or ("A" if family in TIER_A else "B")})

    for h in fairness_lint.lint(vs):
        fam = FAIRNESS_FAMILY.get((h["code"], h["kind"]), h["kind"])
        tier = None
        # A pin stays tier A even when the instruction names that sheet: #21's five failed runs were pins on sheets the
        # instruction did name, failing correct values placed elsewhere. It is KEPT only with the instruction's own words.
        if fam in ("PIN", "LITERAL") and re.search(r"\b(?:do not|need not|never|not) (?:demand|require|insist on|expect)\b", h["text"], re.I):
            tier = "B"          # the wording already says the pin or phrase is NOT required
        if fam == "LITERAL" and instr is not None:
            q = fairness_lint.RX["quoted"].search(h["text"])
            if q and lds.norm(q.group(1)) in instr:
                tier = "B"
        add(h["verifier"], fam, h["text"], tier=tier)
    by_name = {v["name"]: v for v in vs}
    for v in vs:
        p = qcio.prompt_of(v)
        if not p:
            continue
        m = RX_DEFAULT_PASS.search(p)
        if m:
            add(v, "DEFAULT_PASS", "passes when it cannot assess, so no answer can fail it: " + fairness_lint.snippet(p, m.start(), m.end(), 60))
        if instr is not None:
            seen = set()
            for m in RX_UNIT.finditer(fairness_lint.pass_clause(p)):
                root = unit_root(m.group(2))
                if root in seen or root == "day":
                    continue
                seen.add(root)
                if root not in instr and root not in (data or "") and re.search(r"\b(?:days?|weeks?|months?|quarters?|hours?)\b", instr):
                    add(v, "UNIT", f"demands '{m.group(0)}' but neither the instruction nor the input data uses '{root}': "
                        + fairness_lint.snippet(p, m.start(), m.end(), 50))
            for cat, lit, where in lds.literals(p, instr, instr_raw, data or ""):
                if cat == "ID" and where == "NONE":
                    add(v, "UNASKED_ID", f"identifier {lit} is in neither the instruction nor the input data")
                elif cat == "PHRASE" and where == "NONE" and not any(i["verifier"] == v["name"] and i["family"] == "LITERAL" for i in items):
                    add(v, "LITERAL", f"quoted phrase in neither the instruction nor the data: '{lit[:90]}'", tier="B")
                elif cat == "PLACE" and where == "NONE" and not any(i["verifier"] == v["name"] and i["family"] == "PIN" for i in items):
                    add(v, "PIN", f"placement the instruction does not name: {lit}")
    # one item per (verifier, family): keep the first text, count the rest
    merged: dict[tuple, dict] = {}
    for it in items:
        k = (it["verifier"], it["family"])
        if k in merged:
            merged[k]["more"] = merged[k].get("more", 0) + 1
            if it["tier"] == "A":
                merged[k]["tier"] = "A"
        else:
            merged[k] = it
    out = list(merged.values())
    for it in out:
        it["text_hash"] = text_hash(by_name[it["verifier"]]) if it["verifier"] in by_name else ""
    return out


def run_matrix(rev_dir: Path, spec: dict) -> list[dict]:
    """RUNS items from one graded download, only for verifiers whose definition is the one that run graded."""
    vpath = rev_dir / "task_files" / "tests" / "verifier.json"
    if not vpath.is_file():
        return []
    graded = {v["name"]: v for v in qcio.read_json_any(vpath).get("verifiers", [])}
    runs = [r for r in ts.load_runs(rev_dir) if r["health"][0] == "ok" and r["reward"] != "?"]
    out = []
    for v in spec.get("verifiers", []):
        n = v["name"]
        if graded.get(n) != v:
            continue
        marks = {k: [ts.mark(r["res"].get(n)) for r in runs if r["kind"] == k] for k in ("oracle", "solver", "nop")}
        flags = []
        if marks["oracle"] and any(m != "P" for m in marks["oracle"]):
            flags.append("the oracle (golden) did not pass it")
        if len(marks["solver"]) >= 2 and all(m == "F" for m in marks["solver"]):
            flags.append(f"all {len(marks['solver'])} solver runs failed it (a reviewer calls that a Major when their work meets the prompt)")
        if "P" in marks["nop"]:
            flags.append("the empty answer passed it")
        for f in flags:
            out.append({"verifier": n, "family": "RUNS", "text": f + f" [{rev_dir.name}]", "source": "runs", "tier": "A", "text_hash": text_hash(v)})
        split = [r["kind"] for r in runs if (r["res"].get(n) or {}).get("ok") and (r["res"].get(n) or {}).get("dissent")]
        if split:
            out.append({"verifier": n, "family": "SPLIT", "text": f"passed by a split judge vote on {', '.join(sorted(set(split)))} [{rev_dir.name}]",
                        "source": "runs", "tier": "B", "text_hash": text_hash(v)})
    return out


def review_items(reviews_dir: Path, spec: dict, vmd5: str | None) -> tuple[list[dict], int, list[str]]:
    """REVIEW items: every Major of every local review in the folder that is bound to this verifier.json.
    Returns (items, number of bound reviews, notes)."""
    names = [v["name"] for v in spec.get("verifiers", [])]
    by_name = {v["name"]: v for v in spec.get("verifiers", [])}
    items, bound, notes = [], 0, []
    if not reviews_dir or not reviews_dir.is_dir():
        return items, 0, ["no local-review folder"]
    binding = reviews_dir / "REVIEWS.json"
    meta = qcio.read_json_any(binding) if binding.is_file() else {}
    if vmd5 and meta.get("verifiers_hash") and meta["verifiers_hash"] != vmd5:
        return items, 0, [f"the reviews in {reviews_dir.name} were run on another verifier.json ({meta['verifiers_hash']}); run them again"]
    if not meta:
        notes.append(f"{reviews_dir.name} has no REVIEWS.json binding (made before v4): counted, but not proven to be on this file")
    for f in sorted(reviews_dir.glob("practice_review_*.md")):
        text = qcio.read_text_any(f)
        v = ts.last_verdict(text)
        if v is None:
            notes.append(f"{f.name}: no verdict JSON (did not finish); not counted")
            continue
        bound += 1
        for x in v.get("findings") or []:
            if str(x.get("severity", "")).lower() != "major":
                continue
            crit = x.get("criteria")
            crit = crit if isinstance(crit, list) else ([crit] if crit else [])
            blob = json.dumps(x, ensure_ascii=False)
            vs = [c for c in crit if c in names] or [n for n in names if re.search(rf"(?<!\w){re.escape(n)}(?!\w)", blob)] or ["(task)"]
            for n in vs:
                items.append({"verifier": n, "family": "REVIEW", "source": f"review:{f.name}", "tier": "A",
                              "text": f"{x.get('type', '')}: {ts.flat(x.get('evidence') or x.get('justification') or '', 240)}",
                              "kind": str(x.get("type", "")).upper(), "text_hash": text_hash(by_name[n]) if n in by_name else ""})
    return items, bound, notes


def pipeline_items(round_dir: Path, names: list[str]) -> list[dict]:
    """Fail-level findings of the pipeline's pin checks in the round's own reports (round<n>/pdiff/fixed/reports)."""
    base = round_dir / "pdiff" / "fixed" / "reports"
    out = []
    if not base.is_dir():
        return out
    for check in PIPELINE_CHECKS:
        for f in base.rglob(check + ".json"):
            try:
                d = qcio.read_json_any(f)
            except Exception:
                continue

            def walk(x):
                if isinstance(x, dict):
                    sev = str(x.get("severity") or x.get("status") or "").lower()
                    crit = next((str(x[k]) for k in ("criterion", "name", "id", "where") if isinstance(x.get(k), (str, int))), "")
                    if sev in ("fail", "major", "high", "error") and crit:
                        n = next((n for n in names if n == crit or n in crit), "(task)")
                        if n != "(task)":
                            out.append({"verifier": n, "family": "PIPELINE", "source": f"pipeline:{check}", "tier": "A",
                                        "text": f"{check}: {ts.flat(x.get('evidence') or x.get('message') or x.get('detail') or sev, 200)}"})
                    for v in x.values():
                        walk(v)
                elif isinstance(x, list):
                    for v in x:
                        walk(v)
            walk(d)
    return out


# ---------- settlements ----------

def settled_path(record: Path) -> Path:
    return record / "predict_settled.json"


def load_settled(record: Path) -> dict:
    p = settled_path(record)
    return qcio.read_json_any(p) if p.is_file() else {}


def instruction_of(record: Path, task_dir: Path | None) -> Path | None:
    for c in ([task_dir] if task_dir else []) + [record / "work" / "export", record / "orig_x"]:
        if c and (c / "instruction.md").is_file():
            return c / "instruction.md"
    return None


def cmd_settle(a) -> int:
    record = a.record.resolve()
    if a.state == "kept" and not (a.quote or a.evidence):
        sys.exit("kept needs --quote \"<words from instruction.md>\" or --evidence <file in the record>")
    basis = {}
    if a.quote:
        ins = instruction_of(record, a.task)
        if not ins:
            sys.exit("no instruction.md found (give --task <unpacked task folder>)")
        hay = lds.norm(qcio.read_text_any(ins))
        if lds.norm(a.quote) not in hay:
            sys.exit(f"SETTLE REFUSED: the quote is not in {ins}. Copy the words exactly; a kept item rests on what the instruction says.")
        basis["quote"] = a.quote
    if a.evidence:
        ev = (record / a.evidence).resolve()
        if not ev.is_file() or record not in ev.parents:
            sys.exit(f"SETTLE REFUSED: evidence file not found inside the record: {a.evidence}")
        basis["evidence"] = a.evidence
        basis["evidence_md5"] = qcio.md5_file(ev)
    spec_round = None
    for d in sorted((p for p in record.glob("round*") if (p / "verifier.json").is_file()), key=lambda p: p.stat().st_mtime):
        spec_round = d
    if not spec_round:
        sys.exit("no round<n>/verifier.json in the record yet: build the round first")
    by = {v["name"]: v for v in qcio.read_json_any(spec_round / "verifier.json").get("verifiers", [])}
    if a.verifier not in by and a.verifier != "(task)":
        sys.exit(f"no verifier named {a.verifier} in {spec_round.name}/verifier.json")
    s = load_settled(record)
    s[f"{a.verifier}|{a.family}"] = {"state": a.state, "why": a.why or "", "text_hash": text_hash(by[a.verifier]) if a.verifier in by else "",
                                     "round": spec_round.name, **basis}
    qcio.write_json_atomic(settled_path(record), s)
    print(f"SETTLED: {a.verifier} {a.family} -> {a.state}" + (" (needs the user's word in approvals.jsonl before the gate clears)" if a.state == "risk" else ""))
    return 0


def risk_approved(record: Path, key: str, text_hash_: str) -> bool:
    for ap in qcio.read_jsonl(record / "approvals.jsonl"):
        if ap.get("gate") == "G4-risk" and ap.get("item") == key and ap.get("text_hash") in ("", None, text_hash_) and ap.get("words"):
            return True
    return False


# ---------- the gate ----------

def latest_graded_rev(record: Path) -> Path | None:
    import ledger
    best = None
    for rev in ledger.rev_dirs(record):
        if "relabel" in rev.as_posix().lower():
            continue
        if any(r["health"][0] == "ok" and r["reward"] != "?" and r["kind"] == "oracle" for r in ts.load_runs(rev)):
            if best is None or fairness_key(rev) > fairness_key(best):
                best = rev
    return best


def fairness_key(rev: Path):
    m = re.fullmatch(r"rev_(\d+)__(\d+)", rev.name)
    return (int(m.group(2)), int(m.group(1))) if m else (-1, -1)


def cmd_check(a) -> int:
    record = a.record.resolve()
    round_dir = record / (a.round if a.round.startswith("round") else f"round{a.round}")
    vpath = round_dir / "verifier.json"
    if not vpath.is_file():
        sys.exit(f"{vpath} not found: build the round first")
    spec = qcio.read_json_any(vpath)
    vhash = qcio.verifiers_hash(spec)
    names = [v["name"] for v in spec.get("verifiers", [])]
    task_dir = a.task or next((c for c in (record / "work" / "export", record / "orig_x") if (c / "instruction.md").is_file()), None)
    notes = []
    if not task_dir:
        notes.append("no unpacked task folder: UNIT, UNASKED_ID and the instruction filter on pins were skipped")
    items = sweep(spec, task_dir)
    rev = latest_graded_rev(record)
    if rev:
        items += run_matrix(rev, spec)
    else:
        notes.append("no graded run in the record: the RUNS family is empty")
    reviews_dir = a.reviews_dir or (record / "practice" / round_dir.name)
    ritems, bound, rnotes = review_items(reviews_dir, spec, vhash)
    items += ritems
    notes += rnotes
    items += pipeline_items(round_dir, names)
    first_round = not any((d / "PREDICT.json").is_file() and qcio.read_json_any(d / "PREDICT.json").get("clear")
                          for d in record.glob("round*") if d.is_dir() and d != round_dir)
    need_reviews = 0 if a.no_reviews else (FIRST_ROUND_REVIEWS if first_round else LATER_ROUND_REVIEWS)
    settled = load_settled(record)
    by_name = {v["name"]: v for v in spec.get("verifiers", [])}
    n_open = n_a = n_risk = 0
    for it in items:
        key = f"{it['verifier']}|{it['family']}"
        th = text_hash(by_name[it["verifier"]]) if it["verifier"] in by_name else ""
        s = settled.get(key)
        state = "info" if it["tier"] == "B" else "open"
        if it["tier"] == "A":
            n_a += 1
            if s and s.get("text_hash") in ("", th):
                if s["state"] == "kept":
                    state = "kept"
                elif s["state"] == "risk":
                    state = "risk" if risk_approved(record, key, th) else "open (risk recorded, the user's word is missing)"
                    n_risk += state == "risk"
            elif s:
                state = "open (the verifier changed since it was settled)"
            if state.startswith("open"):
                n_open += 1
        it["state"] = state
        it["basis"] = {k: s[k] for k in ("quote", "evidence", "why") if s and s.get(k)} if s and not state.startswith("open") else {}
    reviews_short = bound < need_reviews
    clear = n_open == 0 and not reviews_short
    out = {"round": round_dir.name, "verifiers_hash": vhash, "verifier_md5": qcio.md5_file(vpath), "clear": clear,
           "tier_a": n_a, "open": n_open, "risk_accepted": n_risk, "reviews_bound": bound, "reviews_needed": need_reviews,
           "notes": notes, "items": items}
    qcio.write_json_atomic(round_dir / "PREDICT.json", out)
    lines = [f"# PREDICT for {round_dir.name} (verifiers hash {vhash})", "",
             f"- tier A items: {n_a}; open: {n_open}; kept on the instruction: {sum(1 for i in items if i['state'] == 'kept')}; risks accepted: {n_risk}",
             f"- local reviews on this file: {bound} of {need_reviews} needed" + ("  **(run practice reviews first)**" if reviews_short else "")]
    lines += [f"- note: {n}" for n in notes]
    lines += ["", "## Settle these before the run (tier A)", "", "| Verifier | Family | Why a reviewer would flag it | From | State |", "|---|---|---|---|---|"]
    for it in sorted((i for i in items if i["tier"] == "A"), key=lambda i: (not i["state"].startswith("open"), i["family"], i["verifier"])):
        lines.append(f"| {it['verifier']} | {it['family']} | {it['text'].replace('|', '/')[:230]} | {it['source']} | {it['state']} |")
    fams: dict[str, list[str]] = {}
    for it in items:
        if it["tier"] == "A" and it["state"].startswith("open"):
            fams.setdefault(it["family"], []).append(it["verifier"])
    if fams:
        lines += ["", "## Families (fix the whole family in one round, never one verifier per run)", ""]
        lines += [f"- {f}: {len(v)} open: {', '.join(sorted(set(v)))}" for f, v in sorted(fams.items())]
    lines += ["", "## Information only (tier B)", ""]
    lines += [f"- {it['verifier']} {it['family']}: {it['text'][:200]}" for it in items if it["tier"] == "B"]
    last = (f"PREDICT: CLEAR {vhash} ({n_a} tier-A items settled, {n_risk} carried as accepted risks, {bound} local reviews)" if clear else
            f"PREDICT: OPEN {n_open}" + (f" + {need_reviews - bound} local review(s) still to run" if reviews_short else "") +
            f" ({n_a} tier-A items; see {round_dir.name}/PREDICT.md)")
    lines += ["", last]
    qcio.write_text_atomic(round_dir / "PREDICT.md", "\n".join(lines) + "\n")
    print(last)
    return 0 if clear else 1


def cmd_inventory(a) -> int:
    target = a.target
    task_dir = None
    if target.is_dir():
        task_dir = next((c for c in (target, target / "task_files") if (c / "instruction.md").is_file()), None)
    spec = qcio.load_verifier_json(target)
    items = sweep(spec, task_dir)
    for it in sorted(items, key=lambda i: (i["tier"], i["family"], i["verifier"])):
        print(f"{it['tier']} {it['family']:<12} {it['verifier']}: {it['text'][:200]}")
    na = [i for i in items if i["tier"] == "A"]
    by = {}
    for i in na:
        by[i["family"]] = by.get(i["family"], 0) + 1
    print(f"PREDICT INVENTORY: {len(na)} tier-A items on {len({i['verifier'] for i in na})} of {len(spec.get('verifiers', []))} verifiers ("
          + ", ".join(f"{k} {v}" for k, v in sorted(by.items())) + f"); {len(items) - len(na)} tier-B notes")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check")
    p.add_argument("record", type=Path)
    p.add_argument("--round", required=True)
    p.add_argument("--task", type=Path)
    p.add_argument("--reviews-dir", type=Path)
    p.add_argument("--no-reviews", action="store_true", help="skip the local-review count (a dry run; the gate in fx.py never passes this)")
    p = sub.add_parser("settle")
    p.add_argument("record", type=Path)
    p.add_argument("--verifier", required=True)
    p.add_argument("--family", required=True)
    p.add_argument("--state", required=True, choices=("kept", "risk"))
    p.add_argument("--quote")
    p.add_argument("--evidence")
    p.add_argument("--why")
    p.add_argument("--task", type=Path)
    p = sub.add_parser("inventory")
    p.add_argument("target", type=Path)
    a = ap.parse_args()
    return {"check": cmd_check, "settle": cmd_settle, "inventory": cmd_inventory}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
