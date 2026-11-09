#!/usr/bin/env python3
"""A practice comprehensive review with the user's own signed-in `claude` CLI, before spending a DataOS run.

    python practice_review.py --package <fixed zip> [--runs <with-runs zip>] --out <folder> [--reviews 1] [--model claude-opus-5-5]

Builds a read-only workspace in <out>/ws: the fixed package under task_files/, and (with --runs) each earlier
evaluation's graded outputs (workspace.tar.gz -> output/) and verifier reports under evaluations/<eval>/. Then
runs the team repo's review prompt (<clone>/docs/ekw-svc-comprehensive-review.md) through
`claude -p --model <model> --allowedTools Read,Glob,Grep` (no writes, no shell) with the workspace as its folder,
writes each review to <out>/practice_review_<n>.md and reads the last overall_verdict JSON.

It is a rehearsal, not the pipeline: the DataOS reviewers use their own prompt version, sandbox and evaluations.
Its use is to catch, for the price of tokens and minutes, the kind of finding that cost #22 and #40 a 40-minute,
~3 USD DataOS round each (unasked requirements, literal pins, a verifier that passes a wrong value, judge-blind
extracts). A practice `accept`/`valid` does not prove a pass; a practice `reject` with a Major is worth settling
before the run. The evaluations in --runs were graded by the PREVIOUS verifier.json; the prompt tells the reviewer.

Run it in a terminal tab (the app refuses to launch `claude` agents through Bash). Never pass task content anywhere
else; the CLI is the user's own sign-in. Last line: PRACTICE REVIEW: <n> run, verdicts <...>, majors <...>.
"""
from __future__ import annotations

import argparse
import io
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_common import last_verdict, load_config, say  # noqa: E402

ADDENDUM = """

---

## This run (read before §0)

- The task package is in `task_files/` (RL World shape: `instruction.md`, `tests/verifier.json`, goldens in
  `solution/`, sources in `environment/`). This is a **verifier-fix round**: only `tests/verifier.json` was
  changed by QC; everything else is the trainer's and is out of scope for edits, but still evidence.
{evals}
- No deterministic-checks output, content audit, tracker history or workspace-layout skill is available here;
  skip the steps that need them and say so in one line, do not mark the whole review inconclusive for it.
- Read the files yourself; you may only read (Read, Glob, Grep).
- End with the §5 JSON object exactly once: `overall_verdict`, `major_count`, `findings[]` (each with `type`,
  `criteria`, `weight_at_risk`, `evidence`, `correct_answer_that_fails`, `fix`, `severity`).
"""
EVALS_WITH = """- Earlier evaluations are in `evaluations/<eval>/`: `output/` is what that solver or oracle produced, and
  `eval_files/` holds its grading. That grading used the PREVIOUS `verifier.json`: judge the CURRENT
  `task_files/tests/verifier.json` against these outputs. A correct output the current verifiers would fail, or a
  wrong one they would pass, is a Major."""
EVALS_WITHOUT = "- No evaluations are included; judge the verifiers against the golden and the instruction."


def build_ws(pkg: Path, runs: Path | None, ws: Path) -> int:
    (ws / "task_files").mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(pkg) as z:
        names = [n for n in z.namelist() if not n.endswith("/")]
        roots = {n.split("/")[0] for n in names}
        strip = len(roots) == 1 and all("/" in n for n in names)
        root = (ws / "task_files").resolve()
        for n in names:
            rel = n.split("/", 1)[1] if strip else n
            dst = ws / "task_files" / rel
            if not str(dst.resolve()).startswith(str(root)):
                sys.exit(f"zip member escapes the folder: {n}")
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(z.read(n))
    evals = 0
    if runs:
        with zipfile.ZipFile(runs) as z:
            for n in z.namelist():
                if "/evaluations/" not in n or n.endswith("/"):
                    continue
                label = n.split("/evaluations/", 1)[1].split("/", 1)[0]
                rest = n.split(f"/evaluations/{label}/", 1)[1]
                base = ws / "evaluations" / label
                if rest.endswith("workspace.tar.gz"):
                    evals += 1
                    with tarfile.open(fileobj=io.BytesIO(z.read(n)), mode="r:gz") as t:
                        for m in t.getmembers():
                            if m.isfile() and "output/" in m.name:
                                out = base / ("output/" + m.name.split("output/", 1)[1])
                                if ".." in out.parts:
                                    continue
                                out.parent.mkdir(parents=True, exist_ok=True)
                                out.write_bytes(t.extractfile(m).read())
                elif "/artifacts/workspace/output/" in "/" + rest:
                    # unpacked export shape: eval_files/artifacts/workspace/output/<file>
                    out = base / ("output/" + rest.split("artifacts/workspace/output/", 1)[1])
                    if ".." in out.parts:
                        continue
                    if not (base / "output").exists():
                        evals += 1
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(z.read(n))
                elif "/artifacts/" not in rest:
                    out = base / rest
                    if ".." in out.parts:
                        continue
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(z.read(n))
    return evals


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True)
    ap.add_argument("--runs")
    ap.add_argument("--out", required=True)
    ap.add_argument("--reviews", type=int, default=1)
    ap.add_argument("--model", default="claude-opus-5-5")
    a = ap.parse_args()
    cfg = load_config()
    prompt_src = Path(cfg["clone"]) / "docs" / "ekw-svc-comprehensive-review.md" if cfg.get("clone") else None
    if not prompt_src or not prompt_src.is_file():
        # no clone: the copy bundled with the skill (assets/review-prompt, pinned; see scripts/pipeline_lite/PROVENANCE.md)
        prompt_src = Path(__file__).resolve().parent.parent / "assets" / "review-prompt" / "ekw-svc-comprehensive-review.md"
    if not prompt_src.is_file():
        sys.exit(f"review prompt not found: {prompt_src}")
    claude = shutil.which("claude")
    if not claude:
        sys.exit("the claude CLI is not on PATH")
    out = Path(a.out)
    ws = out / "ws"
    if ws.exists() and any(ws.iterdir()):
        sys.exit(f"{ws} is not empty; use a new --out folder (each round its own)")
    n_evals = build_ws(Path(a.package), Path(a.runs) if a.runs else None, ws)
    prompt = prompt_src.read_text(encoding="utf-8") + ADDENDUM.format(evals=EVALS_WITH if n_evals else EVALS_WITHOUT)
    (out / "prompt.md").write_text(prompt, encoding="utf-8")
    say(f"workspace {ws}: task_files + {n_evals} evaluation outputs; prompt {out / 'prompt.md'}")
    verdicts, majors = [], []
    for i in range(1, a.reviews + 1):
        say(f"review {i}/{a.reviews}: claude -p --model {a.model} (read-only tools), this takes minutes ...")
        r = subprocess.run([claude, "-p", "--model", a.model, "--output-format", "text",
                            "--allowedTools", "Read,Glob,Grep", "--disallowedTools", "Bash,Write,Edit,NotebookEdit,WebFetch,WebSearch"],
                           input=prompt, capture_output=True, text=True, encoding="utf-8", cwd=str(ws))
        text = r.stdout or ""
        (out / f"practice_review_{i}.md").write_text(text + ("\n\n[stderr]\n" + r.stderr if r.stderr else ""), encoding="utf-8")
        v = last_verdict(text)
        verdicts.append((v or {}).get("overall_verdict", "NO VERDICT"))
        majors.append(str((v or {}).get("major_count", "?")))
        for f in (v or {}).get("findings", [])[:20]:
            say(f"   [{f.get('severity')}] {f.get('type')}: {f.get('criteria')} -- {str(f.get('evidence'))[:160]}")
        say(f"   saved {out / f'practice_review_{i}.md'}")
    say(f"PRACTICE REVIEW: {a.reviews} run, verdicts {', '.join(verdicts)}, majors {', '.join(majors)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
