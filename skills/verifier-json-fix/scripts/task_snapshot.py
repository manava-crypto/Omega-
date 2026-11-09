#!/usr/bin/env python3
"""Print one task's grading picture as Markdown: the verifiers, how every run scored on each, and what the bundled verifier library can do.

Reads only. Give it a task folder (the one holding tests/verifier.json), a DataOS rev folder (rev_N__ID, holding
task_files/ and evaluations/), or a download folder holding several rev folders (the newest rev of each task is used).

    python task_snapshot.py <folder> [--out snapshot.md] [--full] [--reasons reasons.md [--only v1,v2]]

--full prints every prompt, judge justification and review finding in full; by default they are cut at 400 characters.
--reasons writes every judge's whole justification, per verifier and run, for the verifiers a run failed or passed by a
split vote (with --only, the named verifiers on every run). Re-run the snapshot on every with-runs download, each round.

Flags: ORACLE-NOT-PASS, ALL-SOLVERS-FAIL, PASSES-EMPTY, ERRORED, and ORACLE-SPLIT / SOLVER-SPLIT for a run that passed
with at least one judge voting FAIL (the dissenting judges' reasons are printed under the verifier).
"""
import argparse
import json
import re
import sys
from pathlib import Path


def find_verifier_json(task_dir):
    p = task_dir / "tests" / "verifier.json"
    return p if p.is_file() else None


def rev_key(p):
    m = re.match(r"rev_(\d+)__(\d+)", p.name)
    return (int(m.group(1)), int(m.group(2))) if m else (-1, -1)


def resolve(folder):
    """Return a list of (label, task_dir, rev_dir_or_None)."""
    folder = folder.resolve()
    if find_verifier_json(folder):
        rev = folder.parent if (folder.parent / "evaluations").is_dir() else None
        return [(folder.name, folder, rev)]
    if (folder / "task_files").is_dir():
        return [(folder.parent.name + "/" + folder.name, folder / "task_files", folder)]
    out = []
    by_task = {}
    for rev in folder.rglob("rev_*__*"):
        if rev.is_dir() and (rev / "task_files").is_dir():
            by_task.setdefault(rev.parent, []).append(rev)
    for task, revs in sorted(by_task.items()):
        newest = max(revs, key=rev_key)
        older = sorted((r.name for r in revs if r != newest), key=lambda n: rev_key(Path(n)))
        label = task.name + "/" + newest.name + (f"  (older: {', '.join(older)})" if older else "")
        out.append((label, newest / "task_files", newest))
    # A download often holds each resubmission as its own folder (task-v4, task-v5). The number after the double
    # underscore is DataOS's global id, so the highest id is the newest submission across folders.
    if len(out) > 1:
        top = max(out, key=lambda o: rev_key(o[2])[1])
        out = [(("NEWEST " if o is top else "older ") + o[0], o[1], o[2]) for o in sorted(out, key=lambda o: rev_key(o[2])[1])]
    return out


GOLDEN_DIRS = ("golden_outputs", "output", "files", "golden")  # solution/<name>, tried in this order
SECONDS_PER_JUDGE_CALL = 46.0  # measured on DataOS (deterministic-checks/timeout_headroom_check.py)


def lib_dir(tests_dir):
    """The bundled verifier library: a folder under tests/ holding models.py beside a sources/ folder.

    Covers tests/verifier_lib/, tests/__verifier_lib/ and RL World's nested rl_world_verifiers/."""
    cands = []
    for m in tests_dir.rglob("models.py"):
        d = m.parent
        if "__pycache__" in d.parts or not (d / "sources").is_dir():
            continue
        has_spec = "class VerifierSpec" in m.read_text(encoding="utf-8", errors="ignore")
        cands.append((not has_spec, len(d.relative_to(tests_dir).parts), d.as_posix(), d))
    return sorted(cands)[0][3] if cands else None



def _shared_view_commands(lib):
    """{class name: command name} for the shared commands in sources/reading.py (RL World libraries)."""
    rd = lib / "sources" / "reading.py"
    if not rd.is_file():
        return {}
    out, cls = {}, None
    for line in rd.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"class (\w+)\(", line)
        if m:
            cls = m.group(1)
            continue
        m = re.match(r"""\s+name\s*(?::\s*[\w\[\]]+)?\s*=\s*["']([a-z_]+)["']""", line)
        if m and cls:
            out[cls] = m.group(1)
            cls = None
    return out

def _add_shared(lib, cmds, as_list):
    """A format module that imports a reading.py command class, or builds its set with unit_commands(), offers it."""
    shared = _shared_view_commands(lib)
    cmds.pop("reading", None)
    for src in (lib / "sources").glob("*.py"):
        if src.stem not in cmds:
            continue
        text = src.read_text(encoding="utf-8", errors="ignore")
        extra = {n for c, n in shared.items() if re.search(rf"\b{c}\b", text)}
        if "unit_commands" in text:
            extra |= set(shared.values()) - {"render_unit"}
        if extra:
            merged = set(cmds[src.stem]) | extra
            cmds[src.stem] = sorted(merged) if as_list else merged

def lib_commands(lib):
    """Map source type -> sorted command names found in the bundled verifier library."""
    cmds = {}
    if not lib:
        return cmds
    for src in (lib / "sources").glob("*.py"):
        if src.name.startswith("_") or src.name == "registry.py":
            continue
        names = re.findall(r"""^\s+name\s*(?::\s*[\w\[\]]+)?\s*=\s*["']([a-z_]+)["']""", src.read_text(encoding="utf-8", errors="ignore"), re.M)
        if names:
            cmds[src.stem] = sorted(set(names))
    # Shared view commands live in sources/reading.py; each format module that imports them offers them too.
    _add_shared(lib, cmds, as_list=True)
    return cmds


def golden_dir(task_dir):
    """The solution/ folder solve.sh copies from; else the first of GOLDEN_DIRS that exists."""
    sol = task_dir / "solution"
    sh = sol / "solve.sh"
    if sh.is_file():
        text = sh.read_text(encoding="utf-8", errors="replace")
        for name in GOLDEN_DIRS:
            if re.search(rf"(?<![\w-]){re.escape(name)}(?=[/\"'.\s]|$)", text) and (sol / name).is_dir():
                return sol / name
    return next((sol / n for n in GOLDEN_DIRS if (sol / n).is_dir()), None)


def verifier_timeout(task_dir):
    toml = task_dir / "task.toml"
    if not toml.is_file():
        return None
    m = re.search(r"^\[verifier\][^\[]*?^\s*timeout_sec\s*=\s*([\d.]+)", toml.read_text(encoding="utf-8", errors="ignore"), re.M | re.S)
    return float(m.group(1)) if m else None


def run_kind(name):
    n = name.lower()
    if "oracle" in n:
        return "oracle"
    if n.endswith("nop") or "__nop" in n:
        return "nop"
    return "solver"


def run_health(eval_dir):
    """(state, reason, agent seconds) for one run. NOT GRADED: no reward, because the verifier crashed (missing judge
    credentials, judge infrastructure). AGENT CUT OFF / AGENT FAILED: graded, but on unfinished work. Such runs say
    nothing about the verifiers and are left out of the flags."""
    from datetime import datetime
    state, reason, secs = "ok", "", None
    try:
        d = json.loads((eval_dir / "eval_files" / "result.json").read_text(encoding="utf-8", errors="replace"))
        a = d.get("agent_execution") or {}
        f = lambda x: datetime.fromisoformat(str(x).replace("Z", "+00:00"))
        if a.get("started_at") and a.get("finished_at"):
            secs = (f(a["finished_at"]) - f(a["started_at"])).total_seconds()
        x = d.get("exception_info") or {}
        kind, msg = x.get("exception_type") or "", " ".join(str(x.get("exception_message") or "").split())
        log = eval_dir / "eval_files" / "verifier" / "runtime.log"
        logt = log.read_text(encoding="utf-8", errors="ignore") if log.is_file() else ""
        if kind == "RewardFileNotFoundError" or "Grading did not finish" in logt:
            state = "NOT GRADED"
            reason = ("judge credentials missing" if "AuthenticationError" in logt else
                      "judge API usage limit reached (rerun later; settings are fine)" if "usage limit" in logt.lower() else
                      "judge infrastructure error" if "JudgeInfrastructureError" in logt else "no reward written")
        elif kind == "AgentTimeoutError":
            state, reason = "AGENT CUT OFF", msg[:80]
        elif kind == "ApiUsageLimitError" or "usage limit" in msg.lower():
            state, reason = "AGENT FAILED", "agent API usage limit reached (rerun later)"
        elif kind:
            state, reason = "AGENT FAILED", f"{kind}: {msg[:80]}"
    except Exception:
        pass
    return state, reason, secs


def verifier_seconds(result_json):
    """Wall time of the verifier step in one run (result.json verifier.started_at/finished_at), or None.
    Judges run in parallel on DataOS, so this is usually far below the serial estimate in the limits line."""
    from datetime import datetime
    try:
        v = json.loads(result_json.read_text(encoding="utf-8", errors="replace")).get("verifier") or {}
        f = lambda x: datetime.fromisoformat(str(x).replace("Z", "+00:00"))
        return (f(v["finished_at"]) - f(v["started_at"])).total_seconds()
    except Exception:
        return None


def load_runs(rev_dir):
    runs = []
    if not rev_dir or not (rev_dir / "evaluations").is_dir():
        return runs
    for e in sorted((rev_dir / "evaluations").iterdir()):
        rep = e / "eval_files" / "verifier" / "verifier-report.json"
        reward = e / "eval_files" / "verifier" / "reward.txt"
        res = {}
        if rep.is_file():
            try:
                d = json.loads(rep.read_text(encoding="utf-8", errors="replace"))
                for r in d.get("assertion_results", []):
                    rr = r.get("result", {})
                    ev = rr.get("evaluation") or {}
                    res[r["name"]] = {
                        "ok": rr.get("success"),
                        "error": rr.get("error"),
                        "reason": (rr.get("reason") or "")[:300],
                        # agentic and rubric judges keep their reasoning per attempt; result.reason is only
                        # "assertion failed" for them, which hides why a run lost the verifier
                        "why": [
                            f"{a.get('model', '?')} {'PASS' if a.get('verdict') else 'FAIL'}: "
                            + (a.get("justification") or a.get("error") or "")[:400]
                            for a in (ev.get("attempts") or ev.get("votes") or [])
                            if isinstance(a, dict)
                        ],
                        # judges who voted against the run's final result: on a passing run they are a near miss
                        "dissent": [
                            f"{a.get('model', '?')} {'PASS' if a.get('verdict') else 'FAIL'}: "
                            + (a.get("justification") or a.get("error") or "")[:600]
                            for a in (ev.get("attempts") or ev.get("votes") or [])
                            if isinstance(a, dict) and "verdict" in a and bool(a.get("verdict")) != bool(rr.get("success"))
                        ],
                        "votes": f"{ev.get('true_count', '')}/{(ev.get('true_count') or 0) + (ev.get('false_count') or 0)}" if ev else "",
                        # every judge's vote with its whole justification, for --full and --reasons (four fix chats
                        # wrote their own reason dumps because the 400/600-character cuts hid the deciding sentence)
                        "judges": [
                            (a.get("model", "?"),
                             "NO VERDICT" if "verdict" not in a else "PASS" if a.get("verdict") else "FAIL",
                             a.get("justification") or a.get("error") or "")
                            for a in (ev.get("attempts") or ev.get("votes") or [])
                            if isinstance(a, dict)
                        ],
                        "reason_full": rr.get("reason") or "",
                    }
            except Exception as exc:  # a broken report is itself evidence; show it
                res = {"__error__": str(exc)}
        short = re.sub(r"^eval_\d+__attempt_\d+__", "", e.name)
        runs.append({"name": short, "kind": run_kind(e.name), "reward": reward.read_text(encoding="utf-8", errors="replace").strip() if reward.is_file() else "?",
                     "res": res, "verifier_s": verifier_seconds(e / "eval_files" / "result.json"),
                     "health": run_health(e)})
    return runs


def mark(r):
    if r is None:
        return "·"
    if r.get("error"):
        return "ERR"
    return "P" if r.get("ok") else "F"


def last_verdict(text):
    """The review's Answer Check verdict: the last JSON object with overall_verdict and a findings list.

    A review's ## status header always reads PASSED, and the transcript echoes the prompt's own template near the top,
    so the real verdict is a parseable object late in the file. Reviews since 2026-10-29 (custom_*.md, ## type custom)
    end with a second object, {"overall_verdict": "rejected" | "valid", "checks": [...]}, that has no findings list;
    taking the last object alone reported a 6-major rejection as 0 findings. Prefer the last object with findings, and
    fall back to the last object with overall_verdict."""
    dec = json.JSONDecoder()
    found = None
    with_findings = None
    for m in re.finditer(r'"overall_verdict"', text):
        # Walk back to each opening brace before the key until one decodes to an object holding it.
        i = m.start()
        while True:
            i = text.rfind("{", 0, i)
            if i < 0:
                break
            try:
                js, end = dec.raw_decode(text[i:])
            except ValueError:
                continue
            if isinstance(js, dict) and "overall_verdict" in js and i + end > m.start():
                found = js
                if isinstance(js.get("findings"), list):
                    with_findings = js
                break
    return with_findings or found


def review_verdicts(rev_dir):
    out = []
    if not rev_dir or not (rev_dir / "verifications").is_dir():
        return out
    for f in sorted((rev_dir / "verifications").glob("*.md")):
        text = f.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"^## status\s*\n\s*EXCEPTION", text, re.M):
            # the review crashed (for example an API usage limit); its body is only the prompt template
            out.append((f.name, "did not run (EXCEPTION)", []))
            continue
        js = last_verdict(text)
        if js is None:
            out.append((f.name, "unparsed", []))
            continue
        # v14 reviews carry findings and a later checks block; list the failed checks too, not only the findings
        ck = last_checks(text)
        items = list(js.get("findings") or [])
        if ck is not None:
            items += [{**c, "checks_item": True} for c in ck.get("checks", []) if isinstance(c, dict) and c not in items
                      and (c.get("severity") in ("major", "minor") or str(c.get("result", "")).lower() == "fail")]
        verdict = js.get("overall_verdict")
        if ck is not None and ck.get("overall_verdict") not in (None, verdict):
            verdict = f"{verdict} / {ck.get('overall_verdict')}"  # findings verdict / checks verdict (valid, rejected)
        out.append((f.name, verdict, items))
    return out


def last_checks(text):
    """The last JSON object carrying overall_verdict and a checks list (v14 reviews), or None."""
    dec = json.JSONDecoder()
    found = None
    for m in re.finditer(r'"checks"\s*:', text):
        i = m.start()
        while True:
            i = text.rfind("{", 0, i)
            if i < 0:
                break
            try:
                js, end = dec.raw_decode(text[i:])
            except ValueError:
                continue
            if isinstance(js, dict) and isinstance(js.get("checks"), list) and "overall_verdict" in js:
                found = js
            if i + end > m.start():
                break
    return found


def snapshot(label, task_dir, rev_dir, full):
    lines = [f"# {label}", ""]
    vj = find_verifier_json(task_dir)
    if not vj:
        lines += ["**No tests/verifier.json in this task.** This skill edits verifier.json only; stop and tell the user.", ""]
        return lines
    spec = json.loads(vj.read_text(encoding="utf-8", errors="replace"))
    vs = spec.get("verifiers", [])
    total = sum((v.get("metadata") or {}).get("weight") or 0 for v in vs)
    lines += [f"- verifier file: `{vj}`", f"- verifiers: {len(vs)}, weight sum {total:.6f}", f"- config: `{json.dumps(spec.get('config'))}`"]
    lib = lib_dir(vj.parent)
    cmds = lib_commands(lib)
    lines.append(f"- verifier library: `{lib.relative_to(task_dir).as_posix()}`" if lib else "- verifier library: **not found under tests/; find it by hand before using any source command**")
    lines.append("- source commands in the bundled library (the only ones a fix may use): " + ("; ".join(f"{k}: {', '.join(v)}" for k, v in sorted(cmds.items())) or "none could be read"))
    used = sorted({f"{(v['source'].get('file') or {}).get('type')}.{(v['source'].get('file') or {}).get('command')}" for v in vs if v.get("source", {}).get("type") == "file"})
    lines.append("- commands this verifier.json uses: " + ", ".join(used))
    gdir = golden_dir(task_dir)
    lines.append(f"- golden folder (the one solve.sh copies from): `{gdir.relative_to(task_dir).as_posix()}`" if gdir else "- golden folder: not found")
    models = (spec.get("config") or {}).get("models") or []
    # Agentic verifiers are judge calls too (one or more per judge), so they count toward the judging time.
    n_rubric = sum(1 for v in vs if (v.get("assertion") or {}).get("type") == "rubric")
    n_agentic = sum(1 for v in vs if (v.get("assertion") or {}).get("type") == "agentic")
    n_det = sum(1 for v in vs if (v.get("assertion") or {}).get("type") == "deterministic")
    timeout = verifier_timeout(task_dir)
    est = (n_rubric + n_agentic) * max(1, len(models)) * SECONDS_PER_JUDGE_CALL
    lines.append(f"- limits: {n_rubric} rubric + {n_agentic} agentic + {n_det} deterministic verifiers (QC and RL World gates want 6 to 20); "
                 f"serial judging about {est:.0f} s" + (f" against timeout_sec {timeout:g} (want 1.5x headroom: room for about "
                 f"{max(0, int((timeout / 1.5 - est) // (max(1, len(models)) * SECONDS_PER_JUDGE_CALL)))} more judged verifiers)" if timeout else ""))
    if any(str(m).startswith("gemini/") for m in models):
        lines.append("- **judge panel has a gemini/ model, which fails on DataOS: the other two must agree, and any split fails. "
                     "Read ERR and split-vote failures as setup, not verifier defects**")
    others = sorted(p.name for p in vj.parent.iterdir() if p.name not in ("verifier.json", "test.sh") and "verifier_lib" not in p.name
                    and "rl_world_verifiers" not in p.name and "verifier_runtime" not in p.name)
    if others:
        lines.append("- other files in tests/ (read-only for this skill; a defect inside them is out of scope): " + ", ".join(others))
    lines.append("")

    runs = load_runs(rev_dir)
    if runs:
        lines.append("## Runs")
        lines += [f"- {r['name']} ({r['kind']}): reward {r['reward']}"
                  + (f", agent {r['health'][2]:.0f} s" if r["health"][2] is not None else "")
                  + (f", verifier {r['verifier_s']:.0f} s measured" if r.get("verifier_s") is not None else "")
                  + (f" — **{r['health'][0]}: {r['health'][1]}**" if r["health"][0] != "ok" else "") for r in runs]
        lines.append("")
        bad = [r for r in runs if r["health"][0] != "ok"]
        if bad:
            lines.append("## Run problems (these runs are left out of the flags below)")
            lines += [f"- {r['name']}: {r['health'][0]} ({r['health'][1]})" for r in bad]
            if all(r["health"][0] == "NOT GRADED" for r in runs if r["kind"] == "oracle"):
                lines.append("- **Nothing usable graded: no oracle run has a reward. Do not settle or fix verifiers from this "
                             "download; rerun it with working judge keys (scripts/run_readiness.py).**")
            if any(r["health"][0] == "AGENT CUT OFF" for r in runs):
                lines.append("- Agent runs hit the time limit, so their failures reflect unfinished work, not the verifiers.")
            lines.append("")
    hdr = "| verifier | w | core/sec | type | source | " + " | ".join(r["name"][:18] for r in runs) + " | flag |"
    lines += ["## Verifiers (P pass, F fail, ERR judge or code error, · not in report)", "", hdr, "|" + "---|" * (6 + len(runs))]
    flags = []
    for v in vs:
        md = v.get("metadata") or {}
        f = (v.get("source") or {}).get("file") or {}
        src = f"{f.get('type')}.{f.get('command')} {json.dumps(f.get('arguments', {}))[:80]}"
        marks = [mark(r["res"].get(v["name"])) for r in runs]
        flag = []
        # usable runs only: a crashed or cut-off run says nothing about the verifier
        kinds = [r["kind"] if r["health"][0] == "ok" else "unusable" for r in runs]
        solver = [m for m, k in zip(marks, kinds) if k == "solver"]
        oracle = [m for m, k in zip(marks, kinds) if k == "oracle"]
        nop = [m for m, k in zip(marks, kinds) if k == "nop"]
        if any(m != "P" for m in oracle):
            flag.append("ORACLE-NOT-PASS")
        if solver and all(m == "F" for m in solver):
            flag.append("ALL-SOLVERS-FAIL")
        if "P" in nop:
            flag.append("PASSES-EMPTY")
        if "ERR" in marks:
            flag.append("ERRORED")
        # A bare-majority pass is one judge vote from a failure. On the golden it is a near-miss ORACLE-NOT-PASS.
        split = [r["kind"] for r in runs if (r["res"].get(v["name"]) or {}).get("ok") and (r["res"].get(v["name"]) or {}).get("dissent")]
        if "oracle" in split:
            flag.append("ORACLE-SPLIT")
        if "solver" in split:
            flag.append("SOLVER-SPLIT")
        if flag:
            flags.append((v["name"], flag))
        lines.append(f"| {v['name']} | {md.get('weight')} | {md.get('importance', '')} | {v['assertion'].get('type')} | {src} | " + " | ".join(marks) + f" | {' '.join(flag)} |")
    lines.append("")
    if flags:
        lines.append("## Look first")
        lines += [f"- {n}: {', '.join(fl)}" for n, fl in flags]
        lines.append("")

    lines.append("## Verifier text")
    for v in vs:
        a = v["assertion"]
        if a.get("type") in ("rubric", "agentic"):
            body = (a.get(a["type"]) or {}).get("prompt")
        else:
            body = json.dumps({"expected": a.get("expected"), **(a.get("deterministic") or {})})
        if not full and body and len(body) > 400:
            body = body[:400] + " ..."
        lines.append(f"- **{v['name']}** ({(v.get('metadata') or {}).get('weight')}): {body}")
        for r in runs:
            rr = r["res"].get(v["name"])
            if rr and not rr.get("ok") and r["kind"] != "nop":
                lines.append(f"  - {r['name']} {mark(rr)} {rr.get('votes', '')}: {rr.get('error') or rr.get('reason')}")
                lines += ([f"    - {m} {vd}: {flat(t)}" for m, vd, t in rr.get("judges") or []] if full
                          else [f"    - {w}" for w in rr.get("why") or []])
            elif rr and rr.get("ok") and rr.get("dissent") and r["kind"] != "nop":
                lines.append(f"  - {r['name']} P {rr.get('votes', '')} (split: passed by a bare majority; dissent below)")
                lines += ([f"    - {m} {vd}: {flat(t)}" for m, vd, t in rr.get("judges") or [] if vd == "FAIL"] if full
                          else [f"    - {w}" for w in rr["dissent"]])
    lines.append("")

    revs = review_verdicts(rev_dir)
    if rev_dir and not (rev_dir / "verifications").is_dir():
        lines += ["## DataOS reviews of this version", "- none in this download (no verifications/ folder): the Answer Check reviews have not run", ""]
    if revs:
        ran = [x for x in revs if not str(x[1]).startswith("did not run")]
        lines.append("## DataOS reviews of this version")
        if len(ran) < 4:
            lines.append(f"- **only {len(ran)} of {len(revs)} reviews ran; rule A needs four finished reviews, so rerun the reviews before approving**")
        cut = None if full else 400
        for name, verdict, items in revs:
            nf = sum(1 for x in items if "checks_item" not in x)
            nc = len(items) - nf
            lines.append(f"- {name}: {verdict}, {nf} finding(s)" + (f", {nc} failed check(s)" if nc else ""))
            lines += [f"  - {review_item(x, cut)}" for x in items]
        lines.append("")
    return lines


def flat(s, cut=None):
    s = " ".join(str(s or "").split())
    return s if cut is None or len(s) <= cut else s[:cut] + " ..."


def review_item(x, cut):
    """One review finding or failed check, whichever of the three shapes it has: Answer Check findings (type,
    criteria, evidence, fix), v14 checks (id, name, result, justification, failure_severity, fix_options) or v14
    findings (name, severity, justification, fix_options)."""
    sev = x.get("severity") or x.get("failure_severity") or ""
    kind = x.get("type") or x.get("name") or f"check {x.get('id', '?')}"
    crit = x.get("criteria")
    crit = ", ".join(crit) if isinstance(crit, list) else (crit or "")
    head = " ".join(p for p in (str(sev), str(kind), crit, f"(weight at risk {x['weight_at_risk']})"
                                if x.get("weight_at_risk") is not None else "") if p)
    body = x.get("evidence") or x.get("justification") or ""
    fix = x.get("fix") or x.get("suggested_fix") or "; ".join(
        f"{o.get('id', '')}) {o.get('title', '')}".strip() for o in x.get("fix_options") or [] if isinstance(o, dict))
    out = head + (f": {flat(body, cut)}" if body else "")
    if x.get("correct_answer_that_fails"):
        out += f" | correct answer that fails: {flat(x['correct_answer_that_fails'], cut)}"
    return out + (f" | fix: {flat(fix, cut)}" if fix else "")


def reasons_report(label, task_dir, rev_dir, only):
    """Every judge's full justification, per verifier and run: failures and splits first, then (with --only) passes."""
    vj = find_verifier_json(task_dir)
    runs = load_runs(rev_dir)
    lines = [f"# Judge reasons: {label}", "",
             "Every judge vote with its whole justification. A verifier is listed when a usable run failed it or passed "
             "it by a split vote; with --only, the named verifiers are listed with every run.", ""]
    if not vj or not runs:
        return lines + ["(no runs in this folder: give a DataOS rev folder or a with-runs download)"]
    names = [v["name"] for v in json.loads(vj.read_text(encoding="utf-8", errors="replace")).get("verifiers", [])]
    if only:
        missing = [n for n in only if n not in names]
        if missing:
            lines.append(f"**not in verifier.json: {', '.join(missing)}**")
        names = [n for n in names if n in only]
    for n in names:
        rows = []
        for r in runs:
            rr = r["res"].get(n)
            if not rr:
                continue
            split = rr.get("ok") and any(vd == "FAIL" for _, vd, _ in rr.get("judges") or [])
            if not only and (rr.get("ok") and not split or r["health"][0] != "ok"):
                continue
            state = "ERR" if rr.get("error") else "PASS (split)" if split else "PASS" if rr.get("ok") else "FAIL"
            note = "" if r["health"][0] == "ok" else f" — {r['health'][0]}: {r['health'][1]}"
            rows.append(f"### {r['name']} ({r['kind']}): {state} {rr.get('votes', '')}{note}")
            if rr.get("error") or (rr.get("reason_full") and not rr.get("judges")):
                rows.append(flat(rr.get("error") or rr.get("reason_full")))
            rows += [f"- **{m} {vd}**: {flat(t)}" for m, vd, t in rr.get("judges") or []]
            rows.append("")
        if rows:
            lines += [f"## {n}", ""] + rows
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--reasons", type=Path, help="also write every judge's full justification per verifier and run here")
    ap.add_argument("--only", default="", help="comma-separated verifier names for --reasons (then every run is listed)")
    a = ap.parse_args()
    if a.only and not a.reasons:
        sys.exit("--only works with --reasons <file>")
    if a.folder.is_file() and a.folder.suffix.lower() == ".zip":
        sys.exit(f"{a.folder} is a zip: unzip it into a folder first (e.g. <record>/in/round<n>/x/) and give that folder. "
                 f"A Dataset with runs from a shared dataset holds many tasks: split_batch_zip.py takes this task out")
    items = resolve(a.folder)
    if not items:
        sys.exit(f"no task found under {a.folder} (need tests/verifier.json, or rev_N__ID/task_files)")
    if a.reasons:
        only = [x.strip() for x in a.only.split(",") if x.strip()]
        a.reasons.write_text("\n".join(l for it in items for l in reasons_report(*it, only)) + "\n", encoding="utf-8")
        print(f"[snapshot] wrote judge reasons to {a.reasons}")
    text = "\n".join(l for it in items for l in snapshot(*it, a.full))
    if a.out:
        a.out.write_text(text, encoding="utf-8")
        print(f"[snapshot] wrote {a.out} ({len(items)} task(s))")
    else:
        print(text)


if __name__ == "__main__":
    main()
