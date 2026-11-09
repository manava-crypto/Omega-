#!/usr/bin/env python3
"""Run the EKW QC pipeline's deterministic checks on the original and the fixed task, and print only what changed.

A verifier.json fix must not add pipeline findings. This script runs, unmodified and read-only, the pipeline's
`deterministic-checks/run_all.py`, `reward_signal_gate.py` and `harbor_rubric_gate.py` on both packages and lists
every finding that is NEW in the fixed package, CHANGED (same finding, different severity, count or evidence, marked
WORSE when the severity or a count rises) or GONE from it. Findings on a verifier switched to agentic are listed as
UNCHECKED, not GONE. Findings identical in both are the task's existing state and are only counted. The last line is
PIPELINE DIFF: NO NEW FINDINGS, NEW FINDINGS or WORSE FINDINGS.

    python pipeline_diff.py <original task_files> <fixed task_files> [--pipeline <EKW_QC_pipeline root>] [--out DIR]

Without --pipeline it runs the skill's bundled pipeline_lite: compound_criterion_check and reward_signal_gate, the
two checks behind every NEW or WORSE finding in 42 saved fix rounds (pipeline_lite/PROVENANCE.md).

Needs Python 3.11+ with the pipeline's dependencies (the QC venv); pass --python to choose the interpreter that runs
the checks. Exit 0 when nothing is NEW or WORSE, 1 when something is (explain or remove each one), 2 on a setup error.

Known blind spot (read before trusting a clean result): the pipeline's verifier.json adapter reads
`assertion.rubric.prompt` only. For an `agentic` verifier it grades `metadata.how_justification` as the criterion text,
so its text checks (compound, groundedness, G1-G7) never see an agentic prompt, and the Harbor gate counts agentic
verifiers as deterministic. A NEW finding on an agentic verifier therefore usually comes from its how_justification.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ID_KEYS = ("where", "criterion", "name", "id", "check", "lint")
STATE_KEYS = ("severity", "status", "clause_count", "strength")
# A CHANGED finding is WORSE when its severity rises or a count (clause_count ...) grows: #40 round 4 printed
# NO NEW FINDINGS while exceptions_authority_reasoning went from clause_count=4 to 13.
SEVERITY_RANK = {"pass": 0, "ok": 0, "info": 1, "note": 1, "low": 1, "warn": 2, "warning": 2, "minor": 2,
                 "medium": 3, "fail": 4, "major": 4, "high": 4, "error": 5, "critical": 5}


def direction(before, after):
    """WORSE, BETTER or CHANGED for one finding's state strings ('severity=fail clause_count=10 | severity=warn ...').

    Each ' | ' part is read on its own, keyed by its severity, so a warn count that rises is not hidden by a fail
    count that drops. Counts are *count* keys and the number that opens a short evidence text ('~7 separately
    checkable conditions': reward_signal_gate keeps its count only there)."""
    def parse(s):
        parts = {}
        for seg in s.split(" | "):
            sev, nums = 0, {}
            for k, v in re.findall(r"(\w+)=([^\s|]+)", seg):
                if k in ("severity", "status"):
                    sev = max(sev, SEVERITY_RANK.get(v.lower(), 0))
                elif "count" in k and re.fullmatch(r"-?\d+(?:\.\d+)?", v):
                    nums[k] = float(v)
                elif k == "evidence":
                    m = re.match(r"~?(\d+(?:\.\d+)?)\b", v)
                    if m:
                        nums["evidence"] = float(m.group(1))
            have = parts.setdefault(sev, {})
            for k, x in nums.items():
                have[k] = max(have.get(k, float("-inf")), x)
        return parts
    b, a = parse(before), parse(after)
    up = max(a, default=0) > max(b, default=0)
    down = max(a, default=0) < max(b, default=0)
    for sev in a.keys() & b.keys():
        for k in a[sev].keys() & b[sev].keys():
            up |= a[sev][k] > b[sev][k]
            down |= a[sev][k] < b[sev][k]
    return "WORSE" if up else "BETTER" if down else "CHANGED"


def assertion_types(pkg):
    try:
        spec = json.loads((pkg / "tests" / "verifier.json").read_text(encoding="utf-8"))
        return {v.get("name"): (v.get("assertion") or {}).get("type") for v in spec.get("verifiers", [])}
    except (OSError, ValueError):
        return {}


def run(cmd, log):
    # PYTHONUTF8: the checks read task files in cp1252 on Windows otherwise (UnicodeDecodeError, ISSUES-LOG row 15)
    with open(log, "w", encoding="utf-8") as fh:
        return subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONUTF8": "1"}).returncode


def signatures(obj, check, root_strs):
    """{finding identity: state} for each finding-like dict in a check's JSON report. The identity is the check, the
    report path and the criterion-like keys; the state is severity, status, counts and short evidence."""
    out = {}

    def clean(s):
        s = str(s)
        for r in root_strs:
            s = s.replace(r, "<root>")
        return s

    def walk(x, path):
        if isinstance(x, dict):
            ids = [f"{k}={clean(x[k])}" for k in ID_KEYS if k in x and isinstance(x[k], (str, int))]
            state = [f"{k}={clean(x[k])}" for k in STATE_KEYS if k in x and isinstance(x[k], (str, int, float))]
            ev = x.get("evidence")
            if isinstance(ev, str) and len(ev) <= 120:
                state.append(f"evidence={clean(ev)}")
            if ids and state:
                # compound_fail[] and compound_warn[] hold the same finding at two severities; key them together so a
                # fail that drops to a warn reads as CHANGED, not as one NEW and one GONE
                key = f"{check} {re.sub(r'_(fail|warn)(?=\[\])', '_*', path)} " + " ".join(ids)
                out[key] = " | ".join(sorted({*out.get(key, "").split(" | "), " ".join(state)} - {""}))
            for k, v in x.items():
                # reports key tasks by folder name (task_x, task_files, the working copy's name): drop that level
                keep = not (path.endswith("/tasks") or re.fullmatch(r"task_\w+|<root>.*", str(k)))
                walk(v, f"{path}/{k}" if keep else path)
        elif isinstance(x, list):
            for v in x:
                walk(v, path + "[]")

    walk(obj, "")
    return out


def collect(out_dir, root_strs):
    sigs = {}
    for f in sorted(Path(out_dir).rglob("*.json")):
        if f.name == "summary.json":
            continue
        try:
            for k, v in signatures(json.loads(f.read_text(encoding="utf-8")), f.stem, root_strs).items():
                sigs[k] = " | ".join(sorted({*sigs.get(k, "").split(" | "), v} - {""}))
        except Exception as exc:
            sigs[f"{f.stem} unreadable report"] = str(exc)
    return sigs


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("original", type=Path, help="original task_files (the package the review graded)")
    ap.add_argument("fixed", type=Path, help="fixed task_files (your working copy)")
    ap.add_argument("--pipeline", type=Path, help="EKW QC pipeline root (holds deterministic-checks/); without it the "
                                                  "skill's bundled pipeline_lite checks run")
    ap.add_argument("--python", default=sys.executable, help="interpreter for the checks (3.11+, the QC venv)")
    ap.add_argument("--out", type=Path, default=None, help="keep the raw reports here (default: a temp folder)")
    a = ap.parse_args()

    lite = a.pipeline is None
    # pipeline_lite: the two checks that produced every NEW or WORSE finding in 42 saved rounds (PROVENANCE.md)
    dc = Path(__file__).resolve().parent / "pipeline_lite" if lite else a.pipeline / "deterministic-checks"
    need = [dc / n for n in (("compound_criterion_check.py", "ekw_verifier_json.py", "reward_signal_gate.py") if lite
                             else ("run_all.py", "reward_signal_gate.py", "harbor_rubric_gate.py"))]
    missing = [p.name for p in need if not p.is_file()]
    if lite:
        print("checks: pipeline_lite (compound_criterion_check, reward_signal_gate; bundled copies, see "
              "pipeline_lite/PROVENANCE.md)")
    if missing:
        print(f"setup: {dc} lacks {', '.join(missing)}", file=sys.stderr)
        return 2
    for p in (a.original, a.fixed):
        if not (p / "tests" / "verifier.json").is_file():
            print(f"setup: {p} has no tests/verifier.json", file=sys.stderr)
            return 2

    base = a.out or Path(tempfile.mkdtemp(prefix="pipeline_diff_"))
    sigs = {}
    for side, pkg in (("original", a.original), ("fixed", a.fixed)):
        # The pipeline discovers task folders named task_*; link the package under one such name.
        root = base / side / "root"
        root.mkdir(parents=True, exist_ok=True)
        link = root / "task_x"
        if link.is_symlink():
            link.unlink()
        if link.exists():
            print(f"setup: {link} exists; pass a fresh --out folder", file=sys.stderr)
            return 2
        try:
            link.symlink_to(pkg.resolve(), target_is_directory=True)
        except OSError:
            # Windows without the symlink privilege (WinError 1314): copy instead. Never a junction, so deleting
            # --out later cannot reach the package's own files (ISSUES-LOG rows 15, 20).
            shutil.copytree(pkg.resolve(), link)
        out = base / side / "reports"
        out.mkdir(parents=True, exist_ok=True)
        if lite:
            # report paths as run_all.py writes them, so findings carry the same names as a full-pipeline diff
            (out / "run_all").mkdir(exist_ok=True)
            rcs = [
                run([a.python, str(dc / "compound_criterion_check.py"), str(link), "--json",
                     str(out / "run_all" / "compound_criterion_check.json")], out / "compound_criterion_check.log"),
                run([a.python, str(dc / "reward_signal_gate.py"), "--root", str(link), "--out", str(out / "reward_signal_gate.json")], out / "reward_signal_gate.log"),
            ]
        else:
            rcs = [
                run([a.python, str(dc / "run_all.py"), "--all", "--root", str(root), "--out-dir", str(out / "run_all")], out / "run_all.log"),
                run([a.python, str(dc / "reward_signal_gate.py"), "--root", str(link), "--out", str(out / "reward_signal_gate.json")], out / "reward_signal_gate.log"),
                run([a.python, str(dc / "harbor_rubric_gate.py"), "--root", str(root), "--out", str(out / "harbor_rubric_gate.json")], out / "harbor_rubric_gate.log"),
            ]
        if not any((out / "run_all").glob("*.json")):
            print(f"setup: run_all.py wrote no reports for the {side} package; see {out / 'run_all.log'}", file=sys.stderr)
            return 2
        sigs[side] = collect(out, [str(root), str(link), str(pkg.resolve()), str(pkg)])
        print(f"{side}: {len(sigs[side])} findings (check exit codes {rcs}; nonzero only means the check found something)")
    return report(sigs["original"], sigs["fixed"], base, a.original, a.fixed)


def report(o, f, base, original, fixed):
    """Print NEW / CHANGED / GONE / UNCHECKED and the verdict line; return the exit code."""
    new = sorted(k for k in f if k not in o)
    gone = sorted(k for k in o if k not in f)
    changed = sorted(k for k in f if k in o and f[k] != o[k])
    dirs = {k: direction(o[k], f[k]) for k in changed}
    worse = [k for k in changed if dirs[k] == "WORSE"]
    # A verifier switched to agentic leaves the pipeline's view (its adapter reads only rubric prompts), so its
    # findings vanish without being fixed: list them apart from GONE (#36 round 2: 8 GONE + NO NEW FINDINGS)
    to, tf = assertion_types(original), assertion_types(fixed)
    switched = sorted(n for n, t in tf.items() if t == "agentic" and to.get(n) not in (None, "agentic"))
    # the whole name only, after '=' or '/' (where=deck_x/deck_x, criterion=deck_x), so deck_census_authority is not
    # taken for census_authority
    unchecked = [k for k in gone if any(re.search(rf"(?<=[=/]){re.escape(n)}(?=$|[\s/])", k) for n in switched)]
    gone = [k for k in gone if k not in unchecked]
    print(f"\n## NEW in the fixed package ({len(new)})")
    print("\n".join(f"+ {k}  [{f[k]}]" for k in new) or "(none)")
    print(f"\n## CHANGED: present before and after, different severity, count or evidence ({len(changed)}, "
          f"{len(worse)} worse)")
    print("\n".join(f"~ {dirs[k]:7} {k}  [{o[k]}] -> [{f[k]}]" for k in sorted(changed, key=lambda k: dirs[k] != "WORSE"))
          or "(none)")
    print(f"\n## GONE from the fixed package ({len(gone)})")
    print("\n".join(f"- {k}  [{o[k]}]" for k in gone) or "(none)")
    if switched:
        print(f"\n## UNCHECKED: verifiers now agentic, which the pipeline does not read ({', '.join(switched)})")
        print("\n".join(f"? {k}  [{o[k]}]" for k in unchecked) or "(no earlier findings on them)")
        print("These are not fixed, only out of the pipeline's sight: read each agentic prompt yourself.")
    print(f"\nunchanged: {sum(1 for k in f if k in o and f[k] == o[k])} findings identical before and after (the task's existing state)")
    print(f"raw reports: {base}")
    if new:
        verdict = "NEW FINDINGS (explain or remove each one)" + (f"; {len(worse)} worse" if worse else "")
    elif worse:
        verdict = f"WORSE FINDINGS ({len(worse)} got worse: explain or fix each one)"
    else:
        verdict = "NO NEW FINDINGS" + (f"; {len(changed)} changed, none worse" if changed else "")
    print("PIPELINE DIFF: " + verdict + (f"; {len(switched)} verifier(s) now agentic, unchecked" if switched else ""))
    return 1 if new or worse else 0


if __name__ == "__main__":
    sys.exit(main())
