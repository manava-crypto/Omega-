#!/usr/bin/env python3
"""Fix a task's verifiers from the two files QC shares, and nothing else. For task authors (trainers, experts).

    python -X utf8 trainer_fix.py start [<file or folder> ...]     find the task zip and the QC runs zip, unpack, list the findings
    python -X utf8 trainer_fix.py apply  [--work <folder>]         apply edits.json to tests/verifier.json
    python -X utf8 trainer_fix.py finish [--work <folder>]         check the result and show the list of changed checks for the author
    python -X utf8 trainer_fix.py finish --confirmed "<the author's words>"     build the zip to upload, write the report

What it needs: (1) your task as downloaded from RL World (a zip, or its folder), and (2) the zip QC shared with you: the
DataOS run with the reviews in it (`<task>-v<N>-dataos-with-runs.zip`). Give both, in any order, or just run `start`
in the folder that holds them. With only the QC zip it still works: the task files inside it are used.

What it never needs, and never asks for: a manifest, a config or setup file, the QC pipeline, DataOS or RL World
access, labels, or any Python package beyond Python itself. If something is absent it works without it and says what
it could not check.

`start` writes, in `fix_<task>/`: FINDINGS.md (every review finding, by verifier, with the evidence and the suggested
fix), RUNS.md (how the golden and each solver run scored on every verifier, with the judges' reasons), SWEEP.md (other
verifiers with the same kinds of problem), and an empty edits.json. The author is not asked at every step. They are
shown ONE list, once, before the upload file is built: `finish` writes SUMMARY_FOR_AUTHOR.md (every check changed, added
or removed, with what it said and what it says now) and stops with WAITING FOR THE AUTHOR until it is run again with
--confirmed "<their words>". Their OK is kept in DECISIONS.md and quoted in the report. The only file that ever changes is
tests/verifier.json, and in it never the `config` block.
Last lines: TRAINER FIX: STARTED ... | TRAINER FIX: APPLIED ... | TRAINER FIX: READY <file to upload> ...
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import predict  # noqa: E402
import qcio  # noqa: E402
import task_snapshot as ts  # noqa: E402
import upload_check  # noqa: E402

HERE = Path(__file__).resolve().parent
REV = re.compile(r"(?:^|/)(rev_\d+__\d+)/")
LIGHT = re.compile(r"/(?:verifications/[^/]+\.md|evaluations/[^/]+/eval_files/(?:result\.json|exception\.txt|verifier/"
                   r"(?:verifier-report\.json|reward\.txt|reward\.json|rlworld-reward\.(?:txt|json)|runtime\.log)))$")


def kind_of(path: Path) -> str:
    """'runs' (a DataOS with-runs zip or folder), 'task' (a task package), or ''."""
    if path.is_dir():
        if any(path.rglob("rev_*__*/verifications")) or any(path.rglob("rev_*__*/evaluations")):
            return "runs"
        return "task" if any(path.rglob("tests/verifier.json")) else ""
    if path.suffix.lower() != ".zip" or not zipfile.is_zipfile(path):
        return ""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
    if any(REV.search(n) and ("/verifications/" in n or "/evaluations/" in n) for n in names):
        return "runs"
    return "task" if any(n.endswith("tests/verifier.json") for n in names) else ""


def safe_extract(zpath: Path, dest: Path, keep=None, strip: str = "") -> int:
    n = 0
    root = dest.resolve()
    with zipfile.ZipFile(zpath) as z:
        for info in z.infolist():
            name = info.filename.replace("\\", "/")
            if info.is_dir() or not name.startswith(strip) or (keep and not keep(name)):
                continue
            rel = name[len(strip):]
            if rel.startswith("/") or ".." in rel.split("/"):
                continue
            out = (dest / rel).resolve()
            if root not in out.parents and out != root:
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(z.read(info))
            n += 1
    return n


def task_root_in_zip(zpath: Path) -> str:
    with zipfile.ZipFile(zpath) as z:
        cands = sorted((n for n in z.namelist() if n.endswith("tests/verifier.json") and "/task_files/" not in "/" + n), key=len)
    if not cands:
        raise SystemExit(f"{zpath.name}: no tests/verifier.json in it: this is not a task package")
    return cands[0][: -len("tests/verifier.json")]


def short_name(name: str) -> str:
    m = re.search(r"([a-z0-9]{6,10}-\d+)(?:-test-[0-9a-f]+)?-v(\d+)", name)
    return f"{m.group(1)}_v{m.group(2)}" if m else re.sub(r"[^\w.-]", "_", name)[:40]


def state_path(work: Path) -> Path:
    return work / "STATE.json"


def find_work(given: str | None) -> Path:
    if given:
        return Path(given).resolve()
    works = sorted((d for d in Path.cwd().glob("fix_*") if (d / "STATE.json").is_file()), key=lambda d: d.stat().st_mtime)
    if not works:
        raise SystemExit("no fix_<task> folder here: run `trainer_fix.py start` first, in the folder that holds the two zips")
    return works[-1].resolve()


def cmd_start(a) -> int:
    given = [Path(x) for x in a.paths] or [Path.cwd()]
    files: list[Path] = []
    for g in given:
        if g.is_dir() and not kind_of(g):
            files += sorted(p for p in g.iterdir() if p.suffix.lower() == ".zip" or p.is_dir())
        else:
            files.append(g)
    task = next((f for f in files if kind_of(f) == "task"), None)
    runs = [f for f in files if kind_of(f) == "runs"]
    runs = sorted(runs, key=lambda f: f.stat().st_mtime)[-1:] if runs else []
    if not task and not runs:
        print("TRAINER FIX: NOTHING TO WORK ON: no task package and no QC runs zip among: " + ", ".join(f.name for f in files[:8]))
        print("Put your RL World task zip and the zip QC shared (…-dataos-with-runs.zip) in this folder and run start again.")
        return 1
    base = (task or runs[0])
    work = (Path(a.work) if a.work else Path.cwd() / f"fix_{short_name(base.stem if base.is_file() else base.name)}").resolve()
    if state_path(work).is_file() and not a.again:
        print(f"TRAINER FIX: ALREADY STARTED in {work} (pass --again to start over; your edits.json is kept either way)")
        return 0
    work.mkdir(parents=True, exist_ok=True)
    notes: list[str] = []
    rev_dir = None
    if runs:
        r = runs[0]
        if r.is_file():
            with zipfile.ZipFile(r) as z:
                revs = sorted({n[: REV.search(n).end()] for n in z.namelist() if REV.search(n)}, key=lambda s: int(re.search(r"__(\d+)/$", s).group(1)))
            top = revs[-1]
            safe_extract(r, work / "runs", keep=lambda n: n.startswith(top) and (LIGHT.search(n) or "/task_files/" in n and "/environment/skills/" not in n), strip=top)
            rev_dir = work / "runs"
        else:
            cands = sorted(p.parent for p in r.rglob("rev_*__*/verifications"))
            rev_dir = cands[-1] if cands else None
    if task:
        tdir = work / "task"
        if task.is_file():
            safe_extract(task, tdir, strip=task_root_in_zip(task))
        else:
            tdir = next(p.parent.parent for p in sorted(task.rglob("tests/verifier.json"), key=lambda p: len(p.parts)))
    elif rev_dir and (rev_dir / "task_files" / "tests" / "verifier.json").is_file():
        tdir = rev_dir / "task_files"
        notes.append("no separate task zip was given: the task files inside the QC zip are used. The file to upload will be tests/verifier.json alone.")
    else:
        print("TRAINER FIX: NOTHING TO WORK ON: the QC zip holds no task files and no task zip was given")
        return 1
    vpath = tdir / "tests" / "verifier.json"
    spec = qcio.read_json_any(vpath)
    names = [v["name"] for v in spec.get("verifiers", [])]
    # FINDINGS.md
    lines = [f"# QC findings on {base.name}", ""]
    by_v: dict[str, list[str]] = {}
    n_find = 0
    reviews = ts.review_verdicts(rev_dir) if rev_dir else []
    for fname, verdict, items in reviews:
        rid = (re.search(r"_(\d+)_", fname) or re.search(r"(\d+)", fname))
        rid = rid.group(1) if rid else fname
        for k, x in enumerate([i for i in items if "checks_item" not in i], 1):
            n_find += 1
            crit = x.get("criteria")
            crit = crit if isinstance(crit, list) else ([crit] if crit else [])
            blob = json.dumps(x, ensure_ascii=False)
            vs = [c for c in crit if c in names] or [n for n in names if re.search(rf"(?<!\w){re.escape(n)}(?!\w)", blob)] or ["(not a single verifier)"]
            text = (f"- **review {rid} finding {k}** [{x.get('severity', '?')}] {x.get('type') or x.get('name') or ''}: "
                    f"{ts.flat(x.get('evidence') or x.get('justification') or '', 900)}"
                    + (f"\n  - a correct answer that fails: {ts.flat(x['correct_answer_that_fails'], 500)}" if x.get("correct_answer_that_fails") else "")
                    + (f"\n  - suggested fix: {ts.flat(x.get('fix') or x.get('suggested_fix') or '', 600)}" if (x.get("fix") or x.get("suggested_fix")) else ""))
            for v in vs:
                by_v.setdefault(v, []).append(text)
    if not rev_dir:
        notes.append("no QC runs zip was found: there are no review findings to read. SWEEP.md still lists pattern risks.")
    lines += [f"{len(reviews)} reviews, {n_find} findings, on {len([v for v in by_v if v in names])} verifiers. "
              "A finding raised by one review only is as likely to be real as one raised by all (QC's data: experts agreed with 88% of those).", ""]
    for v in sorted(by_v, key=lambda v: (v not in names, v)):
        lines += [f"## {v}" + (f"  ({len(by_v[v])} findings)" if len(by_v[v]) > 1 else ""), ""] + by_v[v] + [""]
    (work / "FINDINGS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # RUNS.md
    if rev_dir and (rev_dir / "task_files").is_dir():
        (work / "RUNS.md").write_text("\n".join(ts.snapshot(base.name, rev_dir / "task_files", rev_dir, False)) + "\n", encoding="utf-8")
        ran = qcio.read_json_any(rev_dir / "task_files" / "tests" / "verifier.json")
        moved = sorted(qcio.changed_names(ran, spec))
        if moved:
            notes.append(f"your task zip is not the version QC ran: {len(moved)} verifiers differ ({', '.join(moved[:6])}{' ...' if len(moved) > 6 else ''}). "
                         "Findings on those may already be fixed: read the current text before changing it.")
    # SWEEP.md
    items = predict.sweep(spec, tdir if (tdir / "instruction.md").is_file() else None)
    tier_a = [i for i in items if i["tier"] == "A"]
    sw = ["# Other verifiers with the same kinds of problem", "",
          "Found by pattern, not by a reviewer. When a finding's fix is 'do not insist on this sheet / this wording', the same change is usually "
          "due on every verifier in that family here; fix them together or the next QC round finds them one at a time.", "",
          "| Verifier | Kind | Why a reviewer would flag it | Named in a finding |", "|---|---|---|---|"]
    sw += [f"| {i['verifier']} | {i['family']} | {i['text'].replace('|', '/')[:220]} | {'yes' if i['verifier'] in by_v else 'no'} |" for i in sorted(tier_a, key=lambda i: (i["family"], i["verifier"]))]
    (work / "SWEEP.md").write_text("\n".join(sw) + "\n", encoding="utf-8")
    if not (work / "edits.json").is_file():
        (work / "edits.json").write_text(json.dumps({"edits": [], "keep_how": {}, "sweep": []}, indent=2) + "\n", encoding="utf-8")
    qcio.write_json_atomic(state_path(work), {"task": str(task) if task else None, "task_is_zip": bool(task and task.is_file()), "task_dir": str(tdir),
                                               "runs": str(runs[0]) if runs else None, "rev_dir": str(rev_dir) if rev_dir else None,
                                               "verifier": str(vpath), "verifier_md5": qcio.md5_file(vpath), "notes": notes,
                                               "finding_verifiers": sorted(v for v in by_v if v in names)})
    for n in notes:
        print("note: " + n)
    print(f"work folder: {work}")
    print("read: FINDINGS.md (what QC found), RUNS.md (how each run scored, with the judges' reasons), SWEEP.md (same-kind checks), "
          f"the task's instruction.md and tests/verifier.json under {tdir.name}/")
    print("next: decide the fix for each finding, write edits.json, run apply, then finish. finish shows ONE list of the checks you changed "
          "or added: show it to the author and get their OK before the upload file is built")
    print(f"TRAINER FIX: STARTED {work.name} ({n_find} findings on {len([v for v in by_v if v in names])} verifiers; {len(tier_a)} same-kind checks listed; "
          f"{len(names)} verifiers in the file)")
    return 0


def cmd_apply(a) -> int:
    work = find_work(a.work)
    st = qcio.read_json_any(state_path(work))
    out = work / "verifier.fixed.json"
    cmd = [sys.executable, "-X", "utf8", str(HERE / "apply_verifier_fix.py"), st["verifier"], str(work / "edits.json"), str(out),
           "--original", st["verifier"], "--changes", str(work / "CHANGES.md"), "--overwrite"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    text = ((r.stdout or "") + (r.stderr or "")).strip()
    print(text[-3000:])
    if r.returncode != 0 or not out.is_file():
        print("TRAINER FIX: NOT APPLIED (fix the edit the message names: `old` and `after` must match the verifier's text exactly, once)")
        return 1
    n = len(qcio.changed_names(qcio.read_json_any(Path(st["verifier"])), qcio.read_json_any(out)))
    print(f"TRAINER FIX: APPLIED ({n} verifiers changed; the result is {out.name}; run finish next)")
    return 0


def cmd_finish(a) -> int:
    work = find_work(a.work)
    st = qcio.read_json_any(state_path(work))
    fixed_p = work / "verifier.fixed.json"
    if not fixed_p.is_file():
        print("TRAINER FIX: NOT READY (no verifier.fixed.json: write edits.json and run apply)")
        return 1
    old, new = qcio.read_json_any(Path(st["verifier"])), qcio.read_json_any(fixed_p)
    ov = {v["name"]: v for v in old.get("verifiers", [])}
    nv = {v["name"]: v for v in new.get("verifiers", [])}
    stops, warns = [], []
    if old.get("config") != new.get("config"):
        stops.append("the `config` block changed: it is the platform's (judges, temperature); put it back")
    removed, added = sorted(set(ov) - set(nv)), sorted(set(nv) - set(ov))
    if removed:
        warns.append(f"verifier(s) removed: {', '.join(removed)}. RL World usually refuses a deleted check; remove one only when a finding asks for it")
    if added:
        warns.append(f"verifier(s) added: {', '.join(added)} (a split is fine; a brand-new check is not a fix)")
    ew = qcio.effective_weights(new.get("verifiers", []))
    if abs(sum(ew.values()) - 1.0) > 1e-6:
        stops.append(f"the weights sum to {sum(ew.values()):.6f}, not 1")
    eo = qcio.effective_weights(old.get("verifiers", []))
    cut = [n for n in nv if n in ov and ew[n] < eo[n] - 1e-9]
    if cut:
        warns.append(f"weight lowered on: {', '.join(cut)}. Cutting a weight is not a fix")
    for n, v in nv.items():
        if not qcio.prompt_of(v) and (v.get("assertion") or {}).get("type") in ("rubric", "agentic"):
            stops.append(f"{n}: empty prompt")
    changed = sorted(n for n in nv if n in ov and nv[n] != ov[n])
    named = set(st.get("finding_verifiers", []))
    extras = [n for n in changed if n not in named]
    for n in extras:
        sig = upload_check.loosening_signals(ov[n], nv[n])
        if sig:
            warns.append(f"{n} was loosened although no finding names it ({'; '.join(sig)}). Keep it only if the instruction never asked for what was dropped, and say so in the report")
    untouched = sorted(n for n in named if n in nv and n not in changed)
    sweep_now = [i for i in predict.sweep(new, Path(st["task_dir"]) if (Path(st["task_dir"]) / "instruction.md").is_file() else None)
                 if i["tier"] == "A" and i["verifier"] in changed]
    for i in sweep_now:
        warns.append(f"{i['verifier']} still has a {i['family']} pattern after the edit: {i['text'][:140]}")
    # One list for the author, shown once before the upload file is built: which checks changed or were added, and how.
    refs: dict[str, list[str]] = {}
    try:
        for e in qcio.read_json_any(work / "edits.json").get("edits", []):
            for n in ([e["verifier"]] if isinstance(e.get("verifier"), str) else []):
                if e.get("ref") and e["ref"] not in refs.setdefault(n, []):
                    refs[n].append(e["ref"])
    except (OSError, ValueError):
        pass

    def sentences(text: str) -> list[str]:
        return [s.strip() for s in re.split(r"(?<=[.;])\s+", " ".join(text.split())) if s.strip()]

    summ = [f"# What changes in your task's grading ({work.name})", "",
            f"{len(changed)} check(s) changed, {len(added)} added, {len(removed)} removed, out of {len(nv)}. Nothing else in your task changes: "
            "not the task text, not the golden answer, not the data.", ""]
    for k, n in enumerate(changed, 1):
        was, now = sentences(qcio.prompt_of(ov[n])), sentences(qcio.prompt_of(nv[n]))
        gone, new_s = [s for s in was if s not in now], [s for s in now if s not in was]
        summ += [f"## {k}. {n}" + ("" if n in named else "  (QC did not name this one; changed because it has the same problem)"),
                 f"- Why: {'; '.join(refs.get(n, [])) or 'see FINDINGS.md'}"]
        summ += [f"- Was: {s}" for s in gone[:4]] or (["- Was: (wording unchanged; a setting of the check changed)"] if not new_s else [])
        summ += [f"- Now: {s}" for s in new_s[:4]]
        if len(gone) > 4 or len(new_s) > 4:
            summ.append("- (more sentences changed: the full before and after are in CHANGES.md)")
        summ.append("")
    for n in added:
        summ += [f"## New check: {n}", f"- It passes when: {' '.join(qcio.prompt_of(nv[n]).split())[:500]}", ""]
    for n in removed:
        summ += [f"## Removed check: {n}", f"- It used to check: {' '.join(qcio.prompt_of(ov[n]).split())[:300]}", ""]
    if untouched:
        summ += ["## QC named these, and they stay as they are", ""] + [f"- {n}" for n in untouched] + [""]
    if warns:
        summ += ["## Please look at these", ""] + [f"- {w}" for w in warns] + [""]
    (work / "SUMMARY_FOR_AUTHOR.md").write_text("\n".join(summ) + "\n", encoding="utf-8")
    decisions = work / "DECISIONS.md"
    if not stops and (changed or added or removed) and not (a.confirmed or "").strip():
        print("\n".join(summ))
        print(f"TRAINER FIX: WAITING FOR THE AUTHOR (show them this list, in plain words, and ask once: \"These are the checks I changed or added. "
              f"OK to build the upload file?\" Then run finish again with --confirmed \"<their words>\". The list is also in {work.name}/SUMMARY_FOR_AUTHOR.md)")
        return 1
    if (a.confirmed or "").strip() and not stops:
        with open(decisions, "a", encoding="utf-8") as fh:
            fh.write(f"- The author saw the list of {len(changed)} changed, {len(added)} added and {len(removed)} removed checks "
                     f"(verifier.fixed.json md5 {qcio.md5_file(fixed_p)}) and said: \"{a.confirmed.strip()}\"\n")
    fixed_dir = work / "fixed"
    fixed_dir.mkdir(exist_ok=True)
    upload = None
    if not stops:
        raw = fixed_p.read_bytes()
        if st.get("task_is_zip"):
            src = Path(st["task"])
            root = task_root_in_zip(src)
            upload = fixed_dir / src.name
            with zipfile.ZipFile(src) as zi, zipfile.ZipFile(upload, "w", zipfile.ZIP_DEFLATED) as zo:
                for info in zi.infolist():
                    fresh = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                    fresh.external_attr, fresh.compress_type = info.external_attr, zipfile.ZIP_DEFLATED
                    zo.writestr(fresh, raw if info.filename == root + "tests/verifier.json" else zi.read(info))
            with zipfile.ZipFile(src) as zi, zipfile.ZipFile(upload) as zo:
                if zi.namelist() != zo.namelist():
                    stops.append("the zip's file list changed while it was written")
                diff = [n for n in zi.namelist() if not n.endswith("/") and zi.read(n) != zo.read(n)]
                if diff != [root + "tests/verifier.json"] and changed:
                    stops.append(f"files other than tests/verifier.json differ: {diff[:4]}")
        else:
            (fixed_dir / "tests").mkdir(exist_ok=True)
            upload = fixed_dir / "tests" / "verifier.json"
            upload.write_bytes(raw)
    rep = [f"# Verifier fix report ({work.name})", "",
           f"- changed verifiers: {len(changed)} ({', '.join(changed) or 'none'})",
           f"- named in a QC finding and changed: {len([n for n in changed if n in named])}; named and left as it is: {len(untouched)} ({', '.join(untouched) or 'none'})",
           f"- changed although no finding names it: {len(extras)} ({', '.join(extras) or 'none'})",
           f"- only tests/verifier.json differs; `config` untouched: {'yes' if old.get('config') == new.get('config') else 'NO'}", ""]
    rep += ["## Before you upload", ""] + ([f"- STOP: {s}" for s in stops] + [f"- check: {w}" for w in warns] or ["- nothing flagged"]) + [""]
    rep += ["## For each verifier left as it is", "",
            "Say in one line why (the instruction asks for it: quote the sentence; or the finding is about the golden answer, the task text or the data, which are yours to fix in RL World, not in this file).", ""]
    rep += [f"- {n}: " for n in untouched] + [""]
    if decisions.is_file():
        rep += ["## What the author decided", "", decisions.read_text(encoding="utf-8", errors="replace"), ""]
    ch = work / "CHANGES.md"
    if ch.is_file():
        rep += ["## What changed, verifier by verifier", "", ch.read_text(encoding="utf-8", errors="replace")]
    (work / "FIX_REPORT.md").write_text("\n".join(rep) + "\n", encoding="utf-8")
    for s in stops:
        print("STOP: " + s)
    for w in warns:
        print("check: " + w)
    if stops:
        print(f"TRAINER FIX: NOT READY ({len(stops)} thing(s) to put right; see FIX_REPORT.md)")
        return 1
    print(f"report: {work / 'FIX_REPORT.md'}")
    print(f"TRAINER FIX: READY {upload} ({len(changed)} verifiers changed; {len(untouched)} named ones left as they are; {len(warns)} point(s) to check) "
          f"md5 {hashlib.md5(upload.read_bytes()).hexdigest()}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("start"); p.add_argument("paths", nargs="*"); p.add_argument("--work"); p.add_argument("--again", action="store_true")
    p = sub.add_parser("apply"); p.add_argument("--work")
    p = sub.add_parser("finish"); p.add_argument("--work")
    p.add_argument("--confirmed", help="the author's own words after they saw the list of changed and added checks")
    a = ap.parse_args()
    return {"start": cmd_start, "apply": cmd_apply, "finish": cmd_finish}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
