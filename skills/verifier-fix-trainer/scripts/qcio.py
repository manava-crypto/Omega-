#!/usr/bin/env python3
"""One place for the small things every v4 script needs: BOM-safe reads, hashes, weights, verifier.json loading.

Before v4 these lived three times over (effective_weights in apply_verifier_fix, upload_check and audit_fix; prompt_of
in fix_plan, fairness_lint and upload_check) and three scripts crashed on a verifier.json saved with a BOM. New code
imports from here; nothing in this file writes into a download.
"""
from __future__ import annotations

import hashlib
import json
import os
import zipfile
from pathlib import Path


def read_text_any(path: Path) -> str:
    """Text of a file whatever its encoding quirks: a UTF-8 BOM is dropped, bad bytes are replaced, never raised."""
    return Path(path).read_bytes().decode("utf-8-sig", errors="replace")


def read_json_any(path: Path):
    return json.loads(read_text_any(path))


def md5_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def write_text_atomic(path: Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def write_json_atomic(path: Path, obj) -> None:
    write_text_atomic(path, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    path = Path(path)
    if not path.is_file():
        return []
    out = []
    for line in read_text_any(path).splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def load_verifier_json(path: Path) -> dict:
    """verifier.json from a file, a task folder (the shallowest tests/verifier.json under it) or a zip."""
    path = Path(path)
    if path.is_file() and path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = sorted((n for n in zf.namelist() if n.endswith("tests/verifier.json")), key=len)
            if not names:
                raise FileNotFoundError(f"{path}: no tests/verifier.json inside")
            return json.loads(zf.read(names[0]).decode("utf-8-sig"))
    if path.is_dir():
        cands = sorted(path.rglob("tests/verifier.json"), key=lambda p: len(p.parts))
        if not cands:
            raise FileNotFoundError(f"{path}: no tests/verifier.json under it")
        path = cands[0]
    return read_json_any(path)


def verifier_bytes(path: Path) -> bytes:
    """The raw bytes of tests/verifier.json from a file, folder or zip (for md5s that must match across copies)."""
    path = Path(path)
    if path.is_file() and path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = sorted((n for n in zf.namelist() if n.endswith("tests/verifier.json")), key=len)
            if not names:
                raise FileNotFoundError(f"{path}: no tests/verifier.json inside")
            return zf.read(names[0])
    if path.is_dir():
        cands = sorted(path.rglob("tests/verifier.json"), key=lambda p: len(p.parts))
        if not cands:
            raise FileNotFoundError(f"{path}: no tests/verifier.json under it")
        path = cands[0]
    return path.read_bytes()


def verifiers_hash(spec: dict) -> str:
    """A hash of the `verifiers` array alone, canonical JSON. The DataOS copy swaps config.models for the DataOS
    judges, so file md5s differ between the round's verifier.json and the one a run graded; this hash does not."""
    canon = json.dumps(spec.get("verifiers", []), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def prompt_of(v: dict) -> str:
    a = v.get("assertion", {}) or {}
    t = a.get("type")
    if t in ("rubric", "agentic"):
        return (a.get(t) or {}).get("prompt", "") or ""
    return ""


def weight_of(v: dict):
    w = (v.get("metadata") or {}).get("weight")
    return float(w) if isinstance(w, (int, float)) and not isinstance(w, bool) else None


def effective_weights(vs: list[dict]) -> dict[str, float]:
    """The verifier library's rule: explicit weights as given; unweighted verifiers share the remainder equally."""
    explicit = {v["name"]: weight_of(v) for v in vs if weight_of(v) is not None}
    rest = [v["name"] for v in vs if weight_of(v) is None]
    share = max(0.0, 1.0 - sum(explicit.values())) / len(rest) if rest else 0.0
    out = dict(explicit)
    for n in rest:
        out[n] = share
    return out


def changed_names(old: dict, new: dict) -> set[str]:
    """Names of verifiers whose definition differs between two verifier.json objects (added and removed included)."""
    o = {v["name"]: v for v in old.get("verifiers", [])}
    n = {v["name"]: v for v in new.get("verifiers", [])}
    return {k for k in set(o) | set(n) if o.get(k) != n.get(k)}


def log_dir(record: Path | None = None) -> Path:
    """Where run-time logs go: <record>/logs when a record is known, else QCFIX_LOG_DIR, else ~/.qcfix/logs.
    Never the skill folder: the installed skill must stay byte-identical to its manifest."""
    if record:
        d = Path(record) / "logs"
    elif os.environ.get("QCFIX_LOG_DIR"):
        d = Path(os.environ["QCFIX_LOG_DIR"])
    else:
        d = Path.home() / ".qcfix" / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d
