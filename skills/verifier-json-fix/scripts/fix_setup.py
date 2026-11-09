#!/usr/bin/env python3
"""Check that this machine can run a verifier fix, and write fix_config.json. Run it once, before the first fix.

    python fix_setup.py --root <workspace folder> [--clone <EKW_QC_pipeline folder>] [--name "<your name>"] [--write]

Reads only, except that it writes <root>/fix_config.json when the workspace has no config of its own (a config
found in a parent folder belongs to another workspace), or with --write, which keeps the keys the file already has. It never installs anything: a missing package is listed with the pip command,
and installing it is the user's call.

Checks, each printed as ok / MISSING / note:
  - Python 3.11 or newer (the scripts read task.toml with tomllib);
  - packages: pydantic and jsonpath_ng (the validator loads the task's own verifier library), openpyxl (the scans);
    pdfplumber is optional (PDF sources in literal_demand_scan.py);
  - the skill's bundled checks (scripts/pipeline_lite) and review prompt (assets/review-prompt): with them the skill
    needs no pipeline clone. The team's EKW_QC_pipeline clone is optional: when present, its current checks are used,
    and QC's manager read after a DataOS pass needs it;
  - the `claude` command (missing = NOT READY, except with --expert): the practice review and the manager read need
    it, signed in;
  - a workspace with room for fix records (<root>/rlworld/).
Last line: FIX SETUP: READY, or FIX SETUP: NOT READY (missing: ...).
"""
import argparse
import importlib
import json
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fix_common import DEFAULT_CONFIG, find_config  # noqa: E402

REQUIRED = {"pydantic": "pydantic", "jsonpath_ng": "jsonpath-ng", "openpyxl": "openpyxl"}
OPTIONAL = {"pdfplumber": "pdfplumber"}
LITE_FILES = ("pipeline_lite/compound_criterion_check.py", "pipeline_lite/ekw_verifier_json.py",
              "pipeline_lite/reward_signal_gate.py", "../assets/review-prompt/ekw-svc-comprehensive-review.md")
CLONE_FILES = ("qc.py", "deterministic-checks/run_all.py", "deterministic-checks/reward_signal_gate.py",
               "deterministic-checks/harbor_rubric_gate.py", "deterministic-checks/package_integrity_check.py",
               "docs/ekw-svc-comprehensive-review.md")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", type=Path, required=True, help="your workspace folder (fix records go in <root>/rlworld)")
    ap.add_argument("--clone", type=Path, help="the EKW_QC_pipeline clone (default: the config's, else <root>/EKW_QC_pipeline)")
    ap.add_argument("--name", default="", help="your name, for the records")
    ap.add_argument("--write", action="store_true", help="write <root>/fix_config.json even if a config exists")
    ap.add_argument("--expert", action="store_true",
                    help="a task author fixing their own task: no DataOS, no practice review, no claude command; the "
                         "local checks run and QC runs the rest after the upload")
    a = ap.parse_args()
    missing, notes = [], []
    root = a.root.resolve()

    v = sys.version_info
    ok = v >= (3, 11)
    print(f"{'ok     ' if ok else 'MISSING'} Python {v.major}.{v.minor} ({sys.executable})" + ("" if ok else ": need 3.11+"))
    if not ok:
        missing.append("Python 3.11+")

    for mod, pkg in {**REQUIRED, **OPTIONAL}.items():
        try:
            importlib.import_module(mod)
            print(f"ok      package {mod}")
        except Exception:
            if mod in REQUIRED:
                missing.append(mod)
                print(f"MISSING package {mod}: ask before installing, then: {sys.executable} -m pip install --user {pkg}")
            else:
                print(f"note    optional package {mod} not installed (PDF sources are skipped by literal_demand_scan.py)")

    found = find_config(root)
    # a config belongs to this workspace only when it sits in it; one found further up is another workspace's
    own = found if found and found.parent.resolve() == root else None
    saved = json.loads(own.read_text(encoding="utf-8")).get("clone") if own else None
    clone = Path(a.clone or saved or root / "EKW_QC_pipeline").resolve()
    gone = [f for f in CLONE_FILES if not (clone / f).is_file()]
    lite = [f for f in LITE_FILES if not (HERE / f).is_file()]
    if lite:
        missing.append("bundled checks")
        print(f"MISSING in this skill: {', '.join(lite)}. Unzip the skill again")
    if clone.is_dir() and not gone:
        print(f"ok      pipeline clone {clone} (used for the full checks; the skill would run without it)")
    else:
        if clone.is_dir() and gone:
            print(f"note    the clone at {clone} lacks {', '.join(gone)}: not used (update it with qc.py update)")
        clone = None
        print("ok      no pipeline clone needed: the skill runs its bundled checks (scripts/pipeline_lite)"
              + ("" if a.expert else ". Only QC's manager read after a DataOS pass (F4) needs the clone"))

    cl = shutil.which("claude")
    if a.expert:
        pass  # the practice review and the manager read are QC steps; the expert works inside Claude Code itself
    elif cl:
        print(f"ok      claude command {cl}. The practice review and the manager read use it, signed in (run `claude` "
              f"once in a terminal and log in; this check cannot see the sign-in)")
    else:
        missing.append("claude command")
        print("MISSING `claude` command: install Claude Code and sign in. The practice review (before every DataOS "
              "run) and the manager read (F4) need it")

    if not root.is_dir():
        missing.append("workspace folder")
        print(f"MISSING workspace {root}: create it first")
    else:
        print(f"ok      workspace {root}")

    target = root / "fix_config.json"
    if own and not a.write:
        rl = json.loads(own.read_text(encoding="utf-8")).get("rlworld_dir") or root / "rlworld"
        print(f"ok      config {own} (kept; pass --write to rewrite it as {target}); fix records go in {rl}")
    elif root.is_dir():
        cfg = {k: v for k, v in DEFAULT_CONFIG.items()}
        if target.is_file():
            cfg.update(json.loads(target.read_text(encoding="utf-8")))
        old_root = cfg.get("root")
        if not cfg.get("rlworld_dir") or (old_root and Path(cfg["rlworld_dir"]) == Path(old_root) / "rlworld"):
            cfg["rlworld_dir"] = str(root / "rlworld")  # follows the workspace when it moved; a custom one is kept
        cfg.update({"root": str(root), "clone": str(clone) if clone else "", "python": sys.executable,
                    "expert": bool(a.expert)})
        if a.name:
            cfg["user_name"] = a.name
        target.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
        Path(cfg["rlworld_dir"]).mkdir(parents=True, exist_ok=True)
        print(f"wrote   {target}; fix records go in {cfg['rlworld_dir']}")
        notes.append("run every fix command from inside the workspace, so the scripts find fix_config.json")

    for n in notes:
        print(f"note    {n}")
    print(("FIX SETUP: READY" + (" (expert mode)" if a.expert else "")) if not missing
          else f"FIX SETUP: NOT READY (missing: {', '.join(missing)})")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
