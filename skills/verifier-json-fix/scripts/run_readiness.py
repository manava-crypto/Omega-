#!/usr/bin/env python3
"""Check that a task package can actually grade on DataOS: judge keys and agent time limit.

Reads only; it never edits any file. Give it a task folder (holding task.toml and tests/verifier.json) or a
rev folder of a download with runs; for a download the measured agent times of its runs are used as evidence.

    python run_readiness.py <folder> [--min-agent-s 14400]

It reports:
  - each judge provider in verifier.json config.models with no key declared in task.toml [verifier.env];
  - an [agent] timeout_sec below the longest agent run measured in the download (or below --min-agent-s);
  - an [environment] build_timeout_sec of 600 s or less for a heavy image (libreoffice, tesseract, many pip or npm
    packages): information, and a NOTICE only when the download shows runs lost at sandbox start;
  - runs in the download lost at sandbox start (EnvironmentStartTimeoutError, DaytonaBadGatewayError): platform.

Why: on 30 Oct 2026 a DataOS rerun of finance v12 graded nothing. DataOS passed only OPENAI_API_KEY (the 28-Oct run
also passed the xai and anthropic keys), so every judge call failed authentication. Every agent also stopped at the
package's 600 s limit, when the 28-Oct runs had needed 1146-1338 s.

This skill changes tests/verifier.json only. task.toml is never edited here: RL World refuses a package whose task.toml
differs from its export. Pass each NOTICE line to RL World (or to whoever launches the DataOS run).
"""
import argparse
import json
import re
import sys
import tomllib
from datetime import datetime
from pathlib import Path

PROVIDER_KEY = {"anthropic": "ANTHROPIC_API_KEY", "xai": "XAI_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}


def find(folder: Path):
    for cand in (folder, folder / "task_files"):
        if (cand / "task.toml").is_file() and (cand / "tests" / "verifier.json").is_file():
            rev = cand.parent if (cand.parent / "evaluations").is_dir() else None
            return cand, rev
    sys.exit(f"no task.toml + tests/verifier.json under {folder}")


HEAVY_APT = ("libreoffice", "tesseract", "chromium", "texlive", "playwright")


def image_weight(task: Path):
    """What the Dockerfile installs that makes a cold build slow: heavy apt packages, pip and npm package counts."""
    df = task / "environment" / "Dockerfile"
    if not df.is_file():
        return None
    text = re.sub(r"\\\n", " ", df.read_text(encoding="utf-8", errors="replace"))
    heavy = sorted({h for h in HEAVY_APT if re.search(rf"\b{h}", text)})
    pip = npm = 0
    for line in text.splitlines():
        for seg in re.split(r"&&|;", line):
            m = re.search(r"\bpip3? install\b(.*)", seg)
            if m:
                toks = m.group(1).split()
                pip += sum(1 for i, t in enumerate(toks) if not t.startswith("-") and (i == 0 or toks[i - 1] not in ("-r", "--requirement")))
            m = re.search(r"\bnpm (?:install|i)\b(.*)", seg)
            if m:
                npm += sum(1 for t in m.group(1).split() if not t.startswith("-"))
    return heavy, pip, npm


def sandbox_losses(rev: Path):
    """Runs lost before the agent started: the sandbox did not come up (platform, not the package)."""
    out = []
    for r in sorted((rev / "evaluations").glob("*/eval_files/result.json")) if rev else []:
        try:
            x = json.loads(r.read_text(encoding="utf-8", errors="replace")).get("exception_info") or {}
        except Exception:
            continue
        kind, msg = x.get("exception_type") or "", str(x.get("exception_message") or "")
        if kind in ("EnvironmentStartTimeoutError", "DaytonaBadGatewayError") or "Failed to create sandbox" in msg:
            out.append((r.parts[-3], kind or "sandbox error", " ".join(msg.split())[:120]))
    return out


def agent_seconds(rev: Path):
    out = []
    for r in sorted((rev / "evaluations").glob("*/eval_files/result.json")) if rev else []:
        try:
            a = json.loads(r.read_text(encoding="utf-8", errors="replace")).get("agent_execution") or {}
            f = lambda x: datetime.fromisoformat(str(x).replace("Z", "+00:00"))
            out.append((r.parts[-3], (f(a["finished_at"]) - f(a["started_at"])).total_seconds()))
        except Exception:
            pass
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("folder", type=Path)
    ap.add_argument("--min-agent-s", type=float, default=14400.0)
    a = ap.parse_args()
    task, rev = find(a.folder)
    text = (task / "task.toml").read_text(encoding="utf-8")
    t = tomllib.loads(text)
    models = json.loads((task / "tests" / "verifier.json").read_text(encoding="utf-8")).get("config", {}).get("models", [])
    need = list(dict.fromkeys(PROVIDER_KEY[m.split("/")[0]] for m in models if m.split("/")[0] in PROVIDER_KEY))
    have = set(((t.get("verifier") or {}).get("env") or {}).keys())
    missing = [k for k in need if k not in have]
    limit = float((t.get("agent") or {}).get("timeout_sec") or 0)
    runs = agent_seconds(rev)
    longest = max((s for _, s in runs if "oracle" not in _ and "nop" not in _), default=0)
    want = max(a.min_agent_s if limit < a.min_agent_s else 0, longest * 1.5 if longest >= limit * 0.98 else 0)
    print(f"judges {models}: declared keys {sorted(have)}")
    for k in missing:
        print(f"NOTICE: [verifier.env] has no {k}; a judge in config.models needs it, so DataOS must supply it or grading fails")
    if runs:
        print("measured agent run times: " + ", ".join(f"{n.split('__')[-1][:20]} {s:.0f}s" for n, s in runs))
    if limit and longest >= limit * 0.98:
        print(f"NOTICE: agent runs hit the {limit:g} s limit ({longest:.0f} s); solvers were cut off before finishing")
    if limit < a.min_agent_s:
        print(f"NOTICE: [agent] timeout_sec {limit:g} is below {a.min_agent_s:g}; earlier DataOS solver runs needed up to ~1400 s")
    build = float((t.get("environment") or {}).get("build_timeout_sec") or 0)
    w = image_weight(task)
    print(f"timeouts: agent {limit:g} s, environment build {build:g} s" if build else f"timeouts: agent {limit:g} s, environment build not set")
    heavy_image = False
    if w:
        heavy, pip, npm = w
        heavy_image = bool(heavy) or pip >= 15 or npm >= 5
        print(f"image: apt {', '.join(heavy) or 'no heavy packages'}; {pip} pip and {npm} npm packages")
    losses = sandbox_losses(rev)
    if build and build <= 600 and heavy_image:
        # the standard RL World image is heavy and 600 s is the standard value, so this is only worth acting on after
        # runs were actually lost at sandbox start
        line = (f"build_timeout_sec {build:g} for a heavy image: a cold build (after the sandbox cache is lost) can "
                f"exceed it, and every run then ends EnvironmentStartTimeoutError. A raise is a DataOS-copy change on "
                f"the user's say-so, never in the trainer zip")
        print(("NOTICE: " if losses else "info: ") + line)
    if losses:
        print(f"NOTICE: {len(losses)} run(s) were lost at sandbox start, before the agent ran: "
              + "; ".join(f"{re.sub(r'^eval_[0-9]+__attempt_[0-9]+__', '', n)[:30]} {k}" for n, k, _ in losses)
              + ". That is the platform, not this package: do not count those runs or their reviews; on #36 a 1800 s "
                "build timeout did not help (row 55), so check another task starts before rerunning")
    ok = not missing and limit >= a.min_agent_s and not losses
    print("RUN READINESS: " + ("OK" if ok else "NOTICE (pass these to RL World; this skill does not edit task.toml)"))


if __name__ == "__main__":
    main()
