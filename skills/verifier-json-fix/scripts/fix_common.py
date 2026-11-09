#!/usr/bin/env python3
"""Shared helpers for the verifier-fix scripts: config, download layout, review verdicts, hashing.

Nothing here writes into a download. Every script imports this file from its own folder, so keep the
scripts folder outside any data folder (the team rule for untrusted downloads).

The config is fix_config.json, written by fix_setup.py. It is looked for in this order: the VJF_CONFIG environment
variable (a path that does not exist is an error, never a silent fallback), fix_config.json in the current folder or
a parent, the EKW_QC_CONFIG variable, the ekw-ots-qc skill's qc_config.json in the current folder or a parent (same
keys), then ~/.verifier_fix_config.json.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import zipfile
from pathlib import Path

CONFIG_NAMES = ("fix_config.json", "qc_config.json")
HOME_CONFIG = Path.home() / ".verifier_fix_config.json"

DEFAULT_CONFIG = {
    "root": "",                 # the workspace; fix records go in <root>/rlworld/<name>_fix_<date>/
    "clone": "",                # the team's EKW_QC_pipeline clone (qc.py, the pipeline checks, the review prompt)
    "python": sys.executable or "python",
    "user_name": "",
    "rlworld_dir": "",          # default <root>/rlworld
    "rlworld_judges": ["xai/grok-4.7", "anthropic/claude-sonnet-5-5", "anthropic/claude-opus-5-5"],
    "dataos_master_dataset": "7451",
    "pipeline_name": "ManualQC automated QC pipeline 4 Reviewers",
    "fix_request_sheet": "1I-cyCY0_7BVKF3ackmeswPlveNwXdMAf6QRdoQwDCuM",
    "agent_timeout_dataos": 14400.0,
}

PROVIDER_KEY = {
    "anthropic": "ANTHROPIC_API_KEY",
    "xai": "XAI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

RLW_NAME = re.compile(r"^(?P<task>.+?)-v(?P<version>[1-9]\d*)-dataos-harbor(?:_.*)?$")
REV_RE = re.compile(r"^rev_(\d+)__(\d+)$")


def find_config(start: Path | None = None) -> Path | None:
    """The config file, in the order the module docstring gives."""
    env = os.environ.get("VJF_CONFIG")
    if env:
        if Path(env).is_file():
            return Path(env)
        sys.exit(f"VJF_CONFIG points at {env}, which does not exist. Fix the path or unset it.")

    def up(name):
        for base in [start or Path.cwd(), Path.cwd()]:
            for d in [base, *base.parents]:
                if (d / name).is_file():
                    return d / name
        return None

    ekw = os.environ.get("EKW_QC_CONFIG")
    return (up("fix_config.json") or (Path(ekw) if ekw and Path(ekw).is_file() else None) or up("qc_config.json")
            or (HOME_CONFIG if HOME_CONFIG.is_file() else None))


def load_config(path: Path | None = None) -> dict:
    p = path or find_config()
    if not p:
        sys.exit("No fix_config.json found. Run: python <skill>/scripts/fix_setup.py --root <your workspace folder>")
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(json.loads(p.read_text(encoding="utf-8")))
    cfg["_path"] = str(p)
    return cfg


def md5(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rev_key(name: str) -> tuple[int, int]:
    m = REV_RE.match(name)
    return (int(m.group(1)), int(m.group(2))) if m else (-1, -1)


def newest_rev(task_dir: Path) -> Path | None:
    revs = [d for d in task_dir.iterdir() if d.is_dir() and REV_RE.match(d.name)]
    if not revs:
        return None
    return max(revs, key=lambda d: rev_key(d.name)[1])


def find_rev_folders(root: Path) -> list[tuple[str, Path]]:
    """(task label, newest rev folder) for a download folder, a task folder, or a rev folder."""
    root = root.resolve()
    if REV_RE.match(root.name) and (root / "task_files").is_dir():
        return [(root.parent.name, root)]
    out = []
    if any(REV_RE.match(d.name) for d in root.iterdir() if d.is_dir()):
        r = newest_rev(root)
        return [(root.name, r)] if r else []
    for d in sorted(root.iterdir()):
        if d.is_dir():
            r = newest_rev(d)
            if r:
                out.append((d.name, r))
    return out


def last_verdict(text: str) -> dict | None:
    """The last JSON object in a review transcript that carries overall_verdict. Reviews echo the prompt's
    template first ("reject" or "accept") and newer prompts append a checks block after the verdict, so a
    one-line grep is wrong both ways; this decodes real objects."""
    dec = json.JSONDecoder()
    found: list[dict] = []
    for m in re.finditer(r'"overall_verdict"', text):
        i = m.start()
        # walk back to candidate '{' positions and try to decode an object spanning past i
        j = text.rfind("{", 0, i)
        tries = 0
        while j >= 0 and tries < 40:
            try:
                obj, end = dec.raw_decode(text, j)
            except ValueError:
                obj, end = None, -1
            if isinstance(obj, dict) and "overall_verdict" in obj and end > i:
                if isinstance(obj.get("overall_verdict"), str) and " or " not in obj["overall_verdict"]:
                    if not found or found[-1] is not obj:
                        found.append(obj)
                break
            j = text.rfind("{", 0, j)
            tries += 1
    if not found:
        return None
    # The v13/v14 prompts end with a second object (verdict + `checks`, no findings). The verdict that carries
    # the findings and major_count is the last object that has them; fall back to the last object.
    with_findings = [o for o in found if "findings" in o or "major_count" in o]
    return (with_findings or found)[-1]


def review_header(text: str, field: str) -> str:
    m = re.search(rf"^## {re.escape(field)}\s*\n+([^\n]*)", text, re.M)
    return m.group(1).strip() if m else ""


def has_checks_block(text: str) -> bool:
    tail = text[-6000:]
    return bool(re.search(r'"checks"\s*:\s*\[', tail))


def verdict_class(v: str | None) -> str:
    if v is None:
        return "NO VERDICT"
    v = v.lower()
    if v in ("valid", "accept", "approve", "approved"):
        return "accept"
    if v in ("reject", "invalid", "rejected"):
        return "reject"
    if v in ("needs_revision", "needs-revision", "revise"):
        return "needs_revision"
    return v


def zip_root(zf: zipfile.ZipFile) -> str | None:
    """The single top-level folder of a zip, or None when files sit at the root or there are several."""
    roots = set()
    for n in zf.namelist():
        parts = n.split("/")
        if len(parts) < 2:
            return None
        roots.add(parts[0])
    return roots.pop() if len(roots) == 1 else None


def write_text_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def say(msg: str) -> None:
    print(msg, flush=True)
