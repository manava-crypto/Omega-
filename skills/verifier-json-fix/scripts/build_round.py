#!/usr/bin/env python3
"""Build one fix round from an edit list: apply, validate, zip, DataOS copy and every check, into a new round folder.

    python -X utf8 build_round.py --original <RL World export zip> --edits edits_r<n>.json --rec <record folder>
        --round <n> [--from <last round's verifier.json>] [--runs <with-runs zip> ...] [--scope SCOPE.md]
        [--pipeline <EKW_QC_pipeline root>] [--python <QC venv python>]

Replaces the hand-chained run_round*.ps1 / build_fixed_zip.py of each round. Writes only into <rec>/round<n>/,
which must not exist yet (a second try of a round is a new name, e.g. --round 3b). Nothing is deleted or overwritten,
so every earlier round's zips stay on disk (ISSUES-LOG row 26). The original zip is only read.

<rec>/round<n>/
  edits.json, verifier.json, changes.md      the edit list, its output, the change table for the report
  fixed/<original zip name>                  the original zip entry by entry, only tests/verifier.json replaced
  dataos/<original zip name>                 the DataOS copy (dataos_copy.py: task.toml only)
  work/orig, work/fixed                      unpacked packages for the folder-based checks
  pdiff/                                     pipeline_diff.py raw reports
  *.txt                                      one log per step;  ROUND.md  the summary
Gates, in order (the round is READY only when all pass): apply_verifier_fix APPLY: OK, validate_verifier VERIFIER
CHECK: PASS, fixed zip (only tests/verifier.json differs, and its bytes are the round's verifier.json), DATAOS COPY,
qc.py integrity INTEGRITY: PASS, PIPELINE DIFF: NO NEW FINDINGS (WORSE FINDINGS fails it), xlsx_ranges RANGES: OK,
audit_fix AUDIT: PASS. run_readiness, and xlsx_ranges when it measured nothing, are shown for information.
The validator gets the keep_how reasons of every round's edits.json. The practice review is not run here (it needs a
terminal tab).

--from is required once any round<...> folder exists in the record, so a round never silently restarts from the
export (or from the export's own verifier.json, unless --restart-from-export). The pipeline is --pipeline, else
$EKW_QC_PIPELINE, else `clone` in fix_config.json. Without a clone the round needs nothing outside this skill: the
pipeline diff runs the bundled pipeline_lite checks, and integrity is covered by the fixed-zip gate. NEW or WORSE pipeline findings, or verifiers switched to agentic
(which the pipeline cannot read), fail the round unless --accept-diff "<why each one stands>" is given; the reason is
written into ROUND.md and belongs in the report. A NOT READY round is retried under a new name: --round <n>b, with
--from the same verifier.json the failed try started from.
Last line: ROUND <n>: READY (k gates) or ROUND <n>: NOT READY (failed: ...; skipped: ...).
"""
import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
ENV = {**os.environ, "PYTHONUTF8": "1"}


def configured(key):
    """A value from fix_config.json (or the ekw-ots-qc qc_config.json), if a config is found."""
    sys.path.insert(0, str(HERE))
    from fix_common import find_config  # noqa: E402
    p = find_config()
    return json.loads(p.read_text(encoding="utf-8")).get(key) if p else None


def md5(b):
    return hashlib.md5(b).hexdigest()


def zip_prefix(z):
    """'' for RL World's flat export, '<root>/' for a one-folder zip."""
    names = [n for n in z.namelist() if not n.endswith("/")]
    if "task.toml" in names:
        return ""
    roots = {n.split("/")[0] for n in names}
    if len(roots) == 1 and f"{next(iter(roots))}/task.toml" in names:
        return next(iter(roots)) + "/"
    raise SystemExit(f"setup: {z.filename} has no task.toml at its root or under one folder")


def unpack(z, prefix, dest):
    root = os.path.realpath(dest)
    for info in z.infolist():
        if info.is_dir() or not info.filename.startswith(prefix):
            continue
        rel = info.filename[len(prefix):]
        t = os.path.realpath(os.path.join(dest, rel))
        if not t.startswith(root + os.sep):
            raise SystemExit(f"setup: zip member escapes the folder: {info.filename}")
        os.makedirs(os.path.dirname(t), exist_ok=True)
        with open(t, "wb") as fh:
            fh.write(z.read(info))


def last_line(text):
    lines = [x for x in text.splitlines() if x.strip()]
    return lines[-1].strip() if lines else "(no output)"


class Round:
    def __init__(self, out):
        self.out = out
        self.rows = []  # (step, status, last line, log)

    def run(self, step, cmd, log, want, cwd=None, gate=True, info_if=None, accept=None, accept_if=None):
        """Run one step; its whole output goes to <log>. PASS when the last line matches `want`; INFO, not a gate, when
        it matches `info_if`; PASS with the stated reason when it fails but matches `accept_if` and `accept` is given."""
        p = subprocess.run(cmd, cwd=cwd, env=ENV, capture_output=True, text=True, encoding="utf-8", errors="replace")
        text = (p.stdout or "") + (("\n" + p.stderr) if p.stderr and p.stderr.strip() else "")
        (self.out / log).write_text(text, encoding="utf-8")
        last = last_line(p.stdout or p.stderr or "")
        ok = bool(re.search(want, last)) if want else p.returncode == 0
        if info_if and re.search(info_if, last):
            gate = False
        if not ok and gate and accept and accept_if and re.search(accept_if, last):
            self.add(step, "PASS", f"{last} - ACCEPTED: {accept}", log)
            return True
        self.add(step, ("PASS" if ok else "FAIL") if gate else "INFO", last, log)
        return ok

    def add(self, step, status, last, log=""):
        self.rows.append((step, status, last, log))
        print(f"{status:7} {step}: {last}" + (f"   [{log}]" if log else ""), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--original", type=Path, required=True, help="the RL World export zip the trainer gave (never written)")
    ap.add_argument("--edits", type=Path, required=True, help="this round's edit list (apply_verifier_fix.py format)")
    ap.add_argument("--rec", type=Path, required=True, help="the record folder; the round goes in <rec>/round<n>/")
    ap.add_argument("--round", required=True, help="round name: 1, 2, 3b ...")
    ap.add_argument("--from", dest="start", type=Path, help="verifier.json to start from (the last round's output)")
    ap.add_argument("--runs", type=Path, nargs="*", default=[], help="with-runs zips or unpacked rev_* folders (solver workbooks for xlsx_ranges)")
    ap.add_argument("--scope", type=Path, help="SCOPE.md for audit_fix (default <rec>/SCOPE.md if present)")
    ap.add_argument("--pipeline", type=Path, default=os.environ.get("EKW_QC_PIPELINE"), help="EKW QC pipeline root")
    ap.add_argument("--python", default=sys.executable, help="interpreter for the pipeline's checks (3.11+)")
    ap.add_argument("--accept-diff", metavar="REASON",
                    help="the pipeline diff showed NEW or WORSE findings, or verifiers now agentic and unchecked, and "
                         "the report explains why each one stands: say why here; it goes into ROUND.md")
    ap.add_argument("--restart-from-export", action="store_true",
                    help="build this round from the export on purpose, although earlier rounds exist")
    ap.add_argument("--expert", action="store_true",
                    help="a task author fixing their own task (also set by fix_setup.py --expert): no DataOS copy "
                         "(experts have no DataOS; QC runs the task after the upload); every other check runs as usual")
    ap.add_argument("--feedback", type=Path,
                    help="the version's RL World -external-qc-feedback.json. The round is then built for RL World's "
                         "\"Upload Updated Task\": the full edit is kept as verifier.full.json and the next-round list, "
                         "the round's verifier.json is scoped to the feedback-named verifiers (scope_finalize.py), the "
                         "trainer zip is built and checked (trainer_upload.py), every item is read against the upload "
                         "(feedback_resolution_dump.py) and the DataOS copy grades the scoped file")
    ap.add_argument("--dispositions", "--instruction-sweep-dispositions", dest="dispositions", type=Path,
                    help="one file for the sweep and the items-resolved gate: '<verifier> <CODE> <reason>' per settled FAIL")
    a = ap.parse_args()
    a.expert = a.expert or bool(configured("expert"))
    if a.feedback and not a.feedback.is_file():
        sys.exit(f"setup: {a.feedback} not found")

    py = [sys.executable, "-X", "utf8"]
    out = a.rec / f"round{a.round}"
    if out.exists():
        sys.exit(f"setup: {out} exists; never rebuild a round in place, use a new name (e.g. --round {a.round}b)")
    earlier = sorted(p.name for p in a.rec.glob("round*") if p.is_dir()) if a.rec.is_dir() else []
    if earlier and not a.start and not a.restart_from_export:
        cands = [str(p) for p in sorted(a.rec.glob("round*/verifier.json"))]
        sys.exit(f"setup: the record already has {', '.join(earlier)}; pass --from with the verifier.json this round "
                 f"builds on" + (f" (candidates: {', '.join(cands)})" if cands else
                                 " (older rounds keep it inside round<n>/fixed/<zip>: extract tests/verifier.json)"))
    for p in [a.original, a.edits] + ([a.start] if a.start else []):
        if not p.is_file():
            sys.exit(f"setup: {p} not found")
    for p in a.runs:
        if not (p.is_file() or p.is_dir()):
            sys.exit(f"setup: {p} not found")
    # check the zip before making the round folder, so a bad download leaves nothing behind
    if not zipfile.is_zipfile(a.original):
        sys.exit(f"setup: {a.original} is not a zip file; download the RL World export again")
    with zipfile.ZipFile(a.original) as z0:
        p0 = zip_prefix(z0)
        export_bytes = z0.read(p0 + "tests/verifier.json") if p0 + "tests/verifier.json" in z0.namelist() else None
    if export_bytes is None:
        sys.exit(f"setup: {a.original} has no tests/verifier.json: this skill does not apply")
    if earlier and a.start and md5(a.start.read_bytes()) == md5(export_bytes) and not a.restart_from_export:
        sys.exit(f"setup: --from {a.start} is the export's verifier.json, but the record already has "
                 f"{', '.join(earlier)}. Pass the last round's verifier.json, or --restart-from-export to start over")
    if earlier and a.start:
        newest = sorted(a.rec.glob("round*/verifier.json"), key=lambda q: q.stat().st_mtime)
        if newest and newest[-1].resolve() != a.start.resolve() and md5(newest[-1].read_bytes()) != md5(a.start.read_bytes()):
            print(f"note: --from is not the newest round's output ({newest[-1]}); make sure that is intended")
    scope = a.scope or (a.rec / "SCOPE.md" if (a.rec / "SCOPE.md").is_file() else None)
    pipe = a.pipeline or (Path(configured("clone")) if configured("clone") else None)
    pipe = pipe if pipe and (pipe / "qc.py").is_file() else None

    out.mkdir(parents=True)
    r = Round(out)
    print(f"round {a.round} -> {out}")
    (out / "edits.json").write_bytes(a.edits.read_bytes())

    oz = zipfile.ZipFile(a.original)
    prefix = zip_prefix(oz)
    orig_dir, fix_dir = out / "work" / "orig", out / "work" / "fixed"
    unpack(oz, prefix, orig_dir)
    export_vj = orig_dir / "tests" / "verifier.json"
    start = a.start or export_vj
    print(f"from {start}  md5 {md5(start.read_bytes())}" + ("  (the export)" if start == export_vj else ""))

    # 1. apply the edit list
    new_vj = out / "verifier.json"
    if not r.run("apply", py + [str(HERE / "apply_verifier_fix.py"), str(start), str(out / "edits.json"), str(new_vj),
                                "--original", str(export_vj), "--changes", str(out / "changes.md")],
                 "apply.txt", r"^APPLY: OK"):
        return finish(a, r, out)
    vj_bytes = new_vj.read_bytes()

    # 1b. RL World scope: the trainer upload may carry only the verifiers the feedback names ("changes the task beyond
    # a fix" otherwise, p8f6vjxz-1 v13 2026-11-02). Keep the full edit for the next-round list; scope the round's file.
    if a.feedback:
        (out / "verifier.full.json").write_bytes(vj_bytes)
        r.run("scope vs feedback", py + [str(HERE / "scope_vs_feedback.py"), str(export_vj), str(out / "verifier.full.json"),
                                          str(a.feedback)], "scope_vs_feedback.txt", None, gate=False)
        if not r.run("scope finalize", py + [str(HERE / "scope_finalize.py"), str(export_vj), str(new_vj), str(a.feedback)],
                     "scope_finalize.txt", None, gate=True):
            return finish(a, r, out)
        vj_bytes = new_vj.read_bytes()

    # 1c. whole-rubric hardening sweep (the one-round rules); FAIL on a changed verifier needs a disposition
    history = sorted(a.rec.glob("round*/verifier.json"))
    history = [h for h in history if h.parent != out]
    sweep = py + [str(HERE / "round1_sweep.py"), str(new_vj), "--original", str(export_vj), "--out", str(out / "sweep.md")]
    if (orig_dir / "instruction.md").is_file():
        sweep += ["--instruction", str(orig_dir / "instruction.md")]
    if a.feedback:
        sweep += ["--feedback", str(a.feedback)]
    if history:
        sweep += ["--history"] + [str(h) for h in history]
    if a.dispositions:
        sweep += ["--dispositions", str(a.dispositions)]
    if not r.run("round1 sweep", sweep, "sweep.txt", r"^SWEEP: OK"):
        print("        (sweep: fix each FAIL line in sweep.md, or give a disposition line per settled hit with "
              "--dispositions; WARN lines go to NEXT_ROUND_LIST.md)")
    if a.feedback:
        # the next-round list is the product of a scoped round: unnamed edits held back plus every sweep WARN
        warns = []
        if (out / "sweep.md").is_file():
            sec = re.search(r"^## WARN.*?(?=^## |\Z)", (out / "sweep.md").read_text(encoding="utf-8"), re.M | re.S)
            warns = [ln for ln in (sec.group(0).splitlines() if sec else []) if ln.startswith("- ")]
        held = []
        if (out / "scope_finalize.txt").is_file():
            m = re.search(r"left out \(not named\): \[(.*?)\]", (out / "scope_finalize.txt").read_text(encoding="utf-8"))
            held = [x.strip().strip("'\"") for x in m.group(1).split(",") if x.strip()] if m else []
        body = ["# Next-round list (not in this upload: RL World accepts feedback-named changes only)", ""]
        body += [f"## Edits held back ({len(held)}): they stay in verifier.full.json", ""] + [f"- {x}" for x in held] + [""]
        body += [f"## Sweep warnings on unnamed verifiers ({len(warns)}): settle each before or in the next round", ""] + warns + [""]
        (out / "NEXT_ROUND_LIST.md").write_text("\n".join(body), encoding="utf-8")
        r.add("next-round list", "INFO", f"{len(held)} edits held back, {len(warns)} sweep warnings: NEXT_ROUND_LIST.md")

    # 2. validate on unpacked folders
    shutil.copytree(orig_dir, fix_dir)
    (fix_dir / "tests" / "verifier.json").write_bytes(vj_bytes)
    # keep_how reasons of this round and of every earlier round that came out READY (an abandoned round's reasons
    # must not quiet the validator); the validator compares with the export
    kept = [out / "edits.json"] + sorted(q.parent / "edits.json" for q in a.rec.glob("round*/ROUND.md")
                                         if (q.parent / "edits.json").is_file() and q.parent != out
                                         and last_line(q.read_text(encoding="utf-8")).endswith(")")
                                         and ": READY (" in last_line(q.read_text(encoding="utf-8")))
    if not r.run("validate", py + [str(HERE / "validate_verifier.py"), str(orig_dir), str(fix_dir)]
                 + (["--kept-how"] + [str(p) for p in kept] if kept else []),
                 "validate.txt", r"^VERIFIER CHECK: PASS"):
        return finish(a, r, out)

    # 3. fixed zip: the original entry by entry (names, order, dates, compression), only verifier.json replaced
    fixed_zip = out / "fixed" / a.original.name
    fixed_zip.parent.mkdir()
    target = prefix + "tests/verifier.json"
    with zipfile.ZipFile(fixed_zip, "w") as zo:
        zo.comment = oz.comment
        for info in oz.infolist():
            data = vj_bytes if info.filename == target else oz.read(info)
            # writestr rewrites the ZipInfo it is given (offset, CRC, sizes): pass a copy, or the original's index breaks
            zo.writestr(copy.copy(info), data, compress_type=info.compress_type)
    oz.close()
    oz = zipfile.ZipFile(a.original)
    with zipfile.ZipFile(fixed_zip) as fz:
        same_list = fz.namelist() == oz.namelist()
        bad = fz.testzip()
        differ = [n for n in oz.namelist() if not n.endswith("/") and oz.read(n) != fz.read(n)]
        inside = md5(fz.read(target))
    ok = same_list and bad is None and differ == [target] and inside == md5(vj_bytes)
    msg = (f"only {target} differs, its md5 {inside} = round verifier.json; zip md5 {md5(fixed_zip.read_bytes())}" if ok
           else f"entries same {same_list}, corrupt {bad}, differ {differ}, inside {inside} vs {md5(vj_bytes)}")
    (out / "fixed_zip.txt").write_text(msg + "\n", encoding="utf-8")
    r.add("fixed zip", "PASS" if ok else "FAIL", msg, "fixed_zip.txt")
    if not ok:
        return finish(a, r, out)

    # 3b. the trainer's upload zip (RL World "Upload Updated Task"): flat, task.toml as RL World's less the platform's
    # trailing [verifier.env], manifest kept, only feedback-named verifiers changed; then every item read against it
    trainer_zip = None
    if a.feedback:
        trainer_zip = out / "trainer" / (re.sub(r"\.zip$", "", a.original.name) + "_verifierfix_upload.zip")
        trainer_zip.parent.mkdir()
        if r.run("trainer zip build", py + [str(HERE / "trainer_upload.py"), "build", str(orig_dir), str(new_vj),
                                            str(a.feedback), str(trainer_zip)], "trainer_build.txt", None):
            r.run("trainer zip check", py + [str(HERE / "trainer_upload.py"), "check", str(trainer_zip), str(orig_dir),
                                             str(a.feedback)], "trainer_check.txt", r"^UPLOAD CHECK: PASS")
            res = r.run("feedback resolution", py + [str(HERE / "feedback_resolution_dump.py"), str(orig_dir),
                                                     str(trainer_zip), str(a.feedback)], "feedback_resolution.txt", None, gate=False)
            # a disposition "<verifier> RISK <reason>" (same file as the sweep's) settles a kept criterion in writing
            settled = set()
            if a.dispositions and a.dispositions.is_file():
                for ln in a.dispositions.read_text(encoding="utf-8").splitlines():
                    parts = ln.strip().split(None, 2)
                    if len(parts) == 3 and parts[1] == "RISK" and len(parts[2]) >= 15:
                        settled.add(parts[0])
            risk = [ln for ln in (out / "feedback_resolution.txt").read_text(encoding="utf-8").splitlines()
                    if "RISK" in ln and not any(f"- {s}:" in ln for s in settled)]
            r.add("items resolved", "FAIL" if risk else "PASS",
                  (f"{len(risk)} RISK line(s): a named criterion kept although the item offers deletion, or named and "
                   f"unchanged; delete it, drop the demand, or settle it with a '<verifier> RISK <evidence>' disposition "
                   f"(6eydtrq9-2-v16 'Data inconsistent')" if risk else
                   f"no open RISK line: every named criterion is deleted, reworded or settled ({len(settled)} by disposition)"),
                  "feedback_resolution.txt")

    # 4. DataOS copy: from the same scoped verifier.json the trainer uploads, so the run grades what RL World holds
    dataos_zip = out / "dataos" / a.original.name
    if a.expert:
        r.add("dataos copy", "INFO", "not made: expert mode (QC makes its own DataOS copy after your upload)")
    else:
        r.run("dataos copy", py + [str(HERE / "dataos_copy.py"), str(fixed_zip), str(dataos_zip)],
              "dataos_copy.txt", r"^DATAOS COPY: written")

    # 5. integrity and pipeline diff: the clone's checks when there is one, otherwise the bundled pipeline_lite
    if pipe:
        r.run("integrity", [a.python, "-B", "qc.py", "--no-update", "integrity", str(a.original.resolve()),
                            str(fixed_zip.resolve())], "integrity.txt", r"^INTEGRITY: PASS", cwd=pipe)
    else:
        # every integrity rule (name, files, platform files, task.toml, judges) is already decided by the fixed-zip
        # gate above (the original's entries, only tests/verifier.json replaced) and validate's config check
        r.add("integrity", "INFO", "covered by the fixed zip gate and the validator (no pipeline clone needed)")
    # NEW, WORSE or unchecked (now agentic) findings stand only with a stated reason, which the report repeats
    reason = (a.accept_diff or "").strip()
    if reason and len(reason) < 15:
        print("        (--accept-diff ignored: give the reason in a sentence, not a word)")
        reason = ""
    if not r.run("pipeline diff", py + [str(HERE / "pipeline_diff.py"), str(orig_dir), str(fix_dir)]
                 + (["--pipeline", str(pipe)] if pipe else []) + ["--python", a.python, "--out", str(out / "pdiff")],
                 "pipeline_diff.txt", r"^PIPELINE DIFF: NO NEW FINDINGS(?!.*unchecked)",
                 accept=reason or None, accept_if=r"^PIPELINE DIFF:"):
        print("        (pipeline diff: remove each NEW/WORSE finding, read each now-agentic prompt, or rebuild "
              "with --accept-diff \"<why each one stands>\")")

    # 6. readiness (information), xlsx ranges and the audit
    r.run("run readiness", py + [str(HERE / "run_readiness.py"), str(fix_dir)], "readiness.txt", None, gate=False)
    # "nothing measured" is information only when the file has no xlsx extract at all (#22 round 3); with one, it
    # means a verifier's path matches no workbook (a typo), which is a failure
    has_extract = any(((v.get("source") or {}).get("file") or {}).get("command") == "extract_xlsx"
                      for v in json.loads(vj_bytes.decode("utf-8-sig")).get("verifiers", []))
    r.run("xlsx ranges", py + [str(HERE / "xlsx_ranges.py"), str(fixed_zip)] + [str(x) for x in a.runs],
          "xlsx_ranges.txt", r"^RANGES: OK \d" if has_extract else r"^RANGES: OK",
          info_if=None if has_extract else r"^RANGES: OK \(no extract_xlsx")
    cmd = py + [str(HERE / "audit_fix.py"), "--original", str(a.original), "--fixed", str(fixed_zip)]
    if dataos_zip.is_file():
        cmd += ["--dataos", str(dataos_zip)]
    if a.runs:
        cmd += ["--runs"] + [str(x) for x in a.runs]
    if scope:
        cmd += ["--scope", str(scope)]
    r.run("audit", cmd, "audit.txt", r"^AUDIT: PASS")
    return finish(a, r, out, vj_bytes)


def finish(a, r, out, vj_bytes=None):
    failed = [s for s, st, *_ in r.rows if st == "FAIL"]
    skipped = [s for s, st, *_ in r.rows if st == "SKIPPED"]
    gates = sum(1 for _, st, *_ in r.rows if st == "PASS")
    if failed or skipped:
        verdict = f"ROUND {a.round}: NOT READY (" + "; ".join(
            x for x in (f"failed: {', '.join(failed)}" if failed else "", f"skipped: {', '.join(skipped)}" if skipped else "") if x) + ")"
    else:
        verdict = f"ROUND {a.round}: READY ({gates} gates)"
    md = [f"# Round {a.round}", "", f"Original: {a.original} (md5 {md5(a.original.read_bytes())})",
          f"Edits: {a.edits} (md5 {md5(a.edits.read_bytes())})"]
    if vj_bytes is not None:
        md.append(f"verifier.json md5 {md5(vj_bytes)}")
    for sub in ("fixed", "dataos", "trainer"):
        for z in sorted((out / sub).glob("*.zip")) if (out / sub).is_dir() else []:
            md.append(f"{sub} zip: {z} (md5 {md5(z.read_bytes())})")
    md += ["", "| Step | Result | Last line | Log |", "|---|---|---|---|"]
    md += [f"| {s} | {st} | {last.replace('|', '/')} | {log} |" for s, st, last, log in r.rows]
    trainer = sorted((out / "trainer").glob("*_verifierfix_upload.zip")) if (out / "trainer").is_dir() else []
    if trainer:
        md += ["", f"RL World upload: trainer/{trainer[0].name} is the only file for \"Upload Updated Task\" (flat, "
               "RL World's task.toml, feedback-named verifiers only). fixed/ and dataos/ never go to RL World."]
        if (out / "NEXT_ROUND_LIST.md").is_file():
            md.append("Changes the feedback does not name are listed in NEXT_ROUND_LIST.md: they ride in the DataOS "
                      "copy only if you build it from verifier.full.json on purpose; by default the DataOS copy grades "
                      "the scoped file, so the run and the upload match.")
    if a.expert:
        md += ["", "Expert mode: upload " + (f"trainer/{trainer[0].name}" if trainer else f"fixed/{a.original.name}")
               + " to RL World as the updated task. QC runs the pipeline checks and the DataOS run after that."]
        verdict = verdict.replace(" gates)", " gates, expert mode)")
    md += ["", "Not run here: the practice review (terminal tab) and the DataOS run (user's yes).", "", verdict]
    (out / "ROUND.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"summary {out / 'ROUND.md'}")
    print(verdict)
    return 0 if not failed and not skipped else 1


if __name__ == "__main__":
    sys.exit(main())
