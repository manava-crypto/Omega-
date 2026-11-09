#!/usr/bin/env python3
"""The record of one verifier-fix request, and its stage tracker: the one record that cannot say "done" without
evidence.

    python fix_record.py new <FIX-short id> [--row <sheet row>] [--trainer "<name>"] [--date YYYY-MM-DD]
    python fix_record.py <name> add <RL World zip> [...]      copy downloads into originals/, check judges, MANIFEST.md5
    python fix_record.py <name> status
    python fix_record.py <name> done <stage> --proof "<the proving line, quoted>" [--approved-by-user]
    python fix_record.py <name> block <stage> --why "<last lines of the failure>"
    python fix_record.py <name> reopen <stage>
    python fix_record.py <name> note "<one line for NOTES.md>"
    python fix_record.py <name> round --result "<run id: oracles, No-op, reviews valid/rejected and why>"

`new` makes <rlworld_dir>/<name>_fix_<date>/ with originals/, in/, work/, for_trainer/, NOTES.md, SCOPE.md and
STATE.json (stages F0 to F6). It never overwrites anything. <rlworld_dir> comes from fix_config.json (fix_setup.py),
default <root>/rlworld. Records made by the ekw-ots-qc skill's new_batch.py --path fix are the same shape and work here.

Stages: F0 claim, F1 download, F2 fix, F3 dataos-run, F4 pass, F5 hand-back, F6 dm-and-sheet.
Rules enforced:
  - a stage cannot be done until every earlier one is done (blocking a stage never opens the ones after it);
  - --proof must quote the proving line, not "done";
  - a user gate (F0, F1, F3, F6) needs --approved-by-user, passed only after the user said yes in the chat;
  - each proof must quote its tool's last line, with nothing contradicting it: F1 "JUDGES: OK n of n"; F2
    "ROUND <n>: READY" and "SCOPE: OK n verifier" (or "SCOPE: STOP" with --approved-by-user after the user chose to
    fix the verifier part alone); F4 "4/4 valid" and the manager read's "reviews read (...): 4 of 4"; F5 "AUDIT: PASS";
  - `round` logs a DataOS round that did not pass and reopens F2 to F6; `reopen` also reopens every later stage;
  - `new` refuses a second record for a task that has one (pass --again to start over on purpose).
Every done, block and round appends a dated line to NOTES.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_common import RLW_NAME, load_config, md5, say, write_text_atomic  # noqa: E402

ASSETS = Path(__file__).resolve().parent.parent / "assets"
STAGES = ["F0 claim", "F1 download", "F2 fix", "F3 dataos-run", "F4 pass", "F5 hand-back", "F6 dm-and-sheet"]
GATED = {"F0 claim", "F1 download", "F3 dataos-run", "F6 dm-and-sheet"}


def rl_dir(cfg: dict) -> Path:
    return Path(cfg.get("rlworld_dir") or Path(cfg["root"]) / "rlworld")


def template(tpl: str, **kw) -> str:
    p = ASSETS / tpl
    text = p.read_text(encoding="utf-8") if p.is_file() else f"# {tpl}\n"
    for k, v in kw.items():
        text = text.replace("{" + k + "}", str(v))
    return text


def write_new(path: Path, text: str) -> None:
    if path.exists():
        say(f"keep {path} (exists)")
    else:
        path.write_text(text, encoding="utf-8")
        say(f"new  {path}")


def add_downloads(zips: list[str], originals: Path) -> None:
    """Copy RL World exports into originals/ (never move them), check the versioned name and the judges, and write
    this record's MANIFEST.md5."""
    for z in zips:
        src = Path(z)
        if not src.is_file():
            say(f"skip {src}: not a file")
            continue
        if not RLW_NAME.match(src.stem):
            say(f"REFUSED {src.name}: the name must contain -v<N>-dataos-harbor (download it again from RL World)")
            continue
        if not zipfile.is_zipfile(src):
            say(f"REFUSED {src.name}: not a zip file (download it again from RL World)")
            continue
        dst = originals / src.name
        if dst.exists():
            say(f"keep {dst.name} (already in originals)")
        else:
            shutil.copy2(src, dst)
            say(f"copied {src.name} -> originals/ ({md5(dst)})")
        r = subprocess.run([sys.executable, "-X", "utf8", str(Path(__file__).with_name("check_judges.py")), str(dst)],
                           capture_output=True, text=True, encoding="utf-8")
        say("   " + ((r.stdout or r.stderr).strip().splitlines() or ["check_judges gave no output"])[-1])
    here = sorted(originals.glob("*.zip"))
    if here:
        (originals / "MANIFEST.md5").write_text("".join(f"{md5(p)}  {p.name}\n" for p in here), encoding="utf-8")
        say(f"wrote {originals / 'MANIFEST.md5'} ({len(here)} zips)")


def new_record(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="fix_record.py new")
    ap.add_argument("name", help="FIX-<task short id>, e.g. FIX-faqgp68c-0")
    ap.add_argument("--row", help="EKW_QC_Fix_Request sheet row")
    ap.add_argument("--trainer", help="the trainer who asked for the fix")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--again", action="store_true",
                    help="start a second record for a task that already has one (the newest is the one the tracker uses)")
    a = ap.parse_args(argv)
    check_name(a.name)
    try:
        dt.date.fromisoformat(a.date)
    except ValueError:
        sys.exit(f"--date must be YYYY-MM-DD (got {a.date!r})")
    cfg = load_config()
    rec = rl_dir(cfg) / f"{a.name}_fix_{a.date}"
    others = sorted(p.parent.name for p in rl_dir(cfg).glob(f"{a.name}_fix_*/STATE.json")
                    if p.parent != rec) if rl_dir(cfg).is_dir() else []
    if others and not a.again:
        sys.exit(f"REFUSED: {a.name} already has a record ({', '.join(others)}). Continue it with "
                 f"`fix_record.py {a.name} status`; pass --again only to start over in a new record.")
    for d in ("originals", "in", "work", "for_trainer"):
        (rec / d).mkdir(parents=True, exist_ok=True)
    write_new(rec / "NOTES.md", template("NOTES_TEMPLATE.md", name=a.name, date=a.date,
                                         kind=f"verifier-fix request (sheet row {a.row or '?'}, trainer {a.trainer or '?'})"))
    write_new(rec / "SCOPE.md", template("SCOPE_TEMPLATE.md", name=a.name))
    state = rec / "STATE.json"
    if not state.exists():
        state.write_text(json.dumps({"name": a.name, "path": "fix", "date": a.date, "record_dir": str(rec),
                                     "sheet_row": a.row, "trainer": a.trainer, "rounds": [],
                                     "stages": [{"stage": s, "status": "pending", "gated": s in GATED, "proof": "",
                                                 "approved_by_user": False, "when": ""} for s in STAGES]},
                                    indent=2), encoding="utf-8")
        say(f"new  {state}")
    say("scope: tests/verifier.json only. Prompt, golden, data, task.toml and judges are never changed.")
    say(f"FIX RECORD READY: {rec}")
    say(f"next: python <skill>/scripts/fix_record.py {a.name} status")
    return 0


def check_name(name: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        sys.exit(f"record name {name!r}: use letters, digits, '.', '_' and '-' only (e.g. FIX-faqgp68c-0)")


def find_state(name: str, cfg: dict) -> Path:
    check_name(name)
    cands = sorted(rl_dir(cfg).glob(f"{name}_fix_*/STATE.json"), reverse=True) if rl_dir(cfg).is_dir() else []
    if not cands:
        sys.exit(f"no fix record for {name} under {rl_dir(cfg)}; run: fix_record.py new {name}")
    return cands[0]


def pick(stages: list[dict], key: str) -> dict:
    """A stage by its number ("F2", "f2", "2"), its name ("fix", "dataos-run") or both ("F2 fix"); nothing looser."""
    key = " ".join(key.strip().lower().split())

    def names(s):
        n = s["stage"].lower()
        num = n.split(" ")[0]
        return {n, num, num.lstrip("f"), n.split(" ", 1)[-1]}

    hits = [s for s in stages if key and key in names(s)]
    if len(hits) != 1:
        sys.exit(f"no single stage matches {key!r}; use one of {[s['stage'] for s in stages]} (or just F0 to F6)")
    return hits[0]


JUDGES_OK = re.compile(r"\bJUDGES: OK \d+ of \d+\b")
ROUND_READY = re.compile(r"\bROUND \S+: READY\b")
SCOPE_OK = re.compile(r"\bSCOPE: OK \d+ verifier")
SCOPE_STOP = re.compile(r"\bSCOPE: STOP \d+ outside")
ALL_VALID = re.compile(r"\b4\s*(?:/|of)\s*4\s*valid\b")
# the manager report's own line: "Answer Check reviews read (the 4 automated DataOS pipeline reviews ...): 4 of 4"
READ_ALL = re.compile(r"reviews read[^:\n]*:\s*4 of 4\b")
NEGATED = re.compile(r"\b(?:not|no|never)\s+(?:all\s+)?(?:4\s*(?:/|of)\s*4|valid)", re.I)


def proof_problems(num: str, proof: str) -> list[str]:
    """Why a proof does not prove its stage. Each stage needs the exact last line of its tool, and no line that
    contradicts it (a WRONG, NOT READY, FAIL or 'not 4/4 valid' anywhere in the proof)."""
    out = []
    if num == "F1":
        if not JUDGES_OK.search(proof) or "JUDGES: WRONG" in proof:
            out.append("needs check_judges.py's last line 'JUDGES: OK n of n' and no 'JUDGES: WRONG'")
    if num == "F2":
        if not ROUND_READY.search(proof) or "NOT READY" in proof:
            out.append("needs build_round.py's last line 'ROUND <n>: READY' (a NOT READY round is not a fix)")
        if not SCOPE_OK.search(proof) and not SCOPE_STOP.search(proof):
            out.append("needs scope_check.py's last line 'SCOPE: OK n verifier ...' (or SCOPE: STOP with the user's yes)")
        if "AUDIT: FAIL" in proof or "SCOPE: INCOMPLETE" in proof:
            out.append("the proof itself shows a failed audit or an incomplete scope table")
    if num == "F4":
        if not ALL_VALID.search(proof) or NEGATED.search(proof):
            out.append("needs '4/4 valid' (oracles 1.00, No-op 0.00, all 4 reviews valid, from the review JSON), "
                       "and nothing that negates it")
        if not READ_ALL.search(proof):
            out.append("needs the manager read's line 'Answer Check reviews read (...): 4 of 4' quoted, with every "
                       "item settled (references/fix-request-flow.md, 'After DataOS passes')")
    if num == "F5" and "AUDIT: PASS" not in proof:
        out.append("needs audit_fix.py --trainer's last line 'AUDIT: PASS (n checks)'")
    return out


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "new":
        return new_record(sys.argv[2:])
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("name")
    ap.add_argument("cmd", choices=["status", "add", "done", "block", "reopen", "note", "round"])
    ap.add_argument("args", nargs="*", help="stage (done/block/reopen), text (note) or zips (add)")
    ap.add_argument("--proof")
    ap.add_argument("--why")
    ap.add_argument("--result")
    ap.add_argument("--approved-by-user", action="store_true")
    ap.add_argument("--state", help="a STATE.json, instead of finding the record by name")
    a = ap.parse_args()
    cfg = load_config()
    sp = Path(a.state) if a.state else find_state(a.name, cfg)
    st = json.loads(sp.read_text(encoding="utf-8"))
    if st.get("path") != "fix":
        sys.exit(f"{sp} is not a fix record (path {st.get('path')!r})")
    stages = st["stages"]
    notes = sp.parent / "NOTES.md"
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    def log(line: str) -> None:
        with open(notes, "a", encoding="utf-8") as fh:
            fh.write(f"- {now} {line}\n")

    if a.cmd == "add":
        if not a.args:
            sys.exit("add needs the RL World zip(s)")
        add_downloads(a.args, sp.parent / "originals")
        return 0

    if a.cmd == "round":
        if not a.result or len(a.result.strip()) < 15:
            sys.exit("round needs --result with the run id and what failed (oracles, No-op, reviews valid/rejected and why)")
        rounds = st.setdefault("rounds", [])
        rounds.append({"round": len(rounds) + 1, "result": a.result.strip(), "when": now})
        # every stage from F2 on describes the round that failed, hand-back included
        for s in stages[STAGES.index("F2 fix"):]:
            s.update({"status": "pending", "proof": "", "approved_by_user": False, "when": ""})
        log(f"ROUND {len(rounds)} DID NOT PASS: {a.result.strip()} -> F2 to F6 reopened")
        write_text_atomic(sp, json.dumps(st, indent=2))
        say(f"ROUND {len(rounds)} recorded; F2 to F6 reopened for round {len(rounds) + 1}")
        return 0

    if a.cmd == "status":
        say(f"{st['name']} (fix request, row {st.get('sheet_row') or '?'}, trainer {st.get('trainer') or '?'}) "
            f"started {st['date']}; record {sp.parent}")
        for r in st.get("rounds", []):
            say(f"    round {r['round']} ({r['when']}): {r['result'][:110]}")
        others = sorted(p.parent.name for p in sp.parent.parent.glob(f"{st['name']}_fix_*/STATE.json") if p != sp)
        if others:
            say(f"note: older records for this task, not used: {', '.join(others)}")
        nxt = None
        for s in stages:
            mark = {"pending": " ", "done": "x", "blocked": "!"}[s["status"]]
            gate = " [gate: user]" if s["gated"] else ""
            extra = f"  <- {s['proof'][:90]}" if s["proof"] else ""
            say(f"[{mark}] {s['stage']}{gate}{extra}")
            if nxt is None and s["status"] != "done":
                nxt = s
        if nxt and nxt["status"] == "blocked":
            say(f"BLOCKED: {nxt['stage']}. Nothing after it can close until it is reopened and done.")
        else:
            say(f"NEXT: {nxt['stage']}" + (" (needs the user's yes before you act)" if nxt["gated"] else "") if nxt
                else "ALL STAGES CLOSED")
        return 0

    if a.cmd == "note":
        if not a.args:
            sys.exit("note needs the text")
        log(" ".join(a.args))
        say("noted")
        return 0

    if not a.args:
        sys.exit(f"{a.cmd} needs a stage (F0 to F6)")
    s = pick(stages, a.args[0])
    if a.cmd == "reopen":
        # later stages were closed on what this stage proved, so they reopen with it
        later = [t for t in stages[stages.index(s):] if t["status"] != "pending" or t is s]
        for t in later:
            t.update({"status": "pending", "proof": "", "approved_by_user": False, "when": ""})
        log(f"REOPENED {', '.join(t['stage'] for t in later)}")
    elif a.cmd == "block":
        if not a.why or len(a.why.strip()) < 10:
            sys.exit("block needs --why with the last lines of the failure")
        s.update({"status": "blocked", "proof": "BLOCKED: " + a.why.strip(), "when": now})
        log(f"BLOCKED {s['stage']}: {a.why.strip()}")
    else:
        proof = (a.proof or "").strip()
        num = s["stage"].split(" ")[0]
        if len(proof) < 8 or proof.lower() in ("done", "ok", "complete", "finished"):
            sys.exit("REFUSED: --proof must quote the proving line (a tool's last line, a file and count, a row). "
                     "'done' is not evidence.")
        # every earlier stage must be done: a blocked stage is not a way past a gate
        earlier = [t for t in stages[: stages.index(s)] if t["status"] != "done"]
        if earlier:
            sys.exit(f"REFUSED: earlier stage {earlier[0]['stage']} is {earlier[0]['status']}. Finish it first"
                     + (" (reopen it, then done)." if earlier[0]["status"] == "blocked" else "."))
        for why in proof_problems(num, proof):
            sys.exit(f"REFUSED: {s['stage']}: {why}")
        if num == "F2" and SCOPE_STOP.search(proof) and not a.approved_by_user:
            sys.exit("REFUSED: SCOPE: STOP means findings outside verifier.json. Tell the user; pass "
                     "--approved-by-user only after they said to fix the verifier part alone.")
        if s["gated"] and not a.approved_by_user:
            sys.exit(f"REFUSED: {s['stage']} is a user gate. Pass --approved-by-user only after the user said yes to "
                     f"this act in this chat.")
        s.update({"status": "done", "proof": proof, "approved_by_user": bool(a.approved_by_user), "when": now})
        log(f"DONE {s['stage']}: {proof}")
    write_text_atomic(sp, json.dumps(st, indent=2))
    say(f"{s['status'].upper()} {s['stage']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
