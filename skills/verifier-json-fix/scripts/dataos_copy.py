#!/usr/bin/env python3
"""Make the DataOS copy of an RL World download: task.toml changes, nothing else (team guide 2026-11-02, stage 1).

    python dataos_copy.py <in: qc_rlworld_prep_out/*_dataos_ready.zip or the RL World zip> <out zip> [--agent-timeout 14400] [--no-keys]

Changes, in task.toml only:
  [agent] timeout_sec        raised to --agent-timeout (default 14400.0) when lower; never lowered
  [verifier.env]             for every judge provider in tests/verifier.json config.models whose documented key
                             (ANTHROPIC_API_KEY, XAI_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY) is not declared,
                             one line  KEY = "${KEY:-}"  is appended to the section (created if absent).
                             Lines RL World wrote itself are never touched.
Everything else is byte-identical; the script asserts that (same entry list, same bytes except task.toml) and
prints the task.toml diff. The output keeps the input's root folder name (<task>-v<N>-dataos-harbor): RL World
reads the version from it. The input is never modified. Keep the original: qc.py rlworld --download <original>
--publish-as-download restores this task.toml before anything goes back to RL World.

Why: on 2026-10-30 a DataOS rerun graded nothing because DataOS passed only OPENAI_API_KEY and every agent
stopped at the package's 600 s limit. Last line: DATAOS COPY: written <out> or REFUSED.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import tomllib
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_common import PROVIDER_KEY, RLW_NAME, md5, say, zip_root  # noqa: E402


def edit_toml(text: str, judges: list[str], agent_timeout: float, add_keys: bool) -> tuple[str, list[str]]:
    notes = []
    data = tomllib.loads(text)
    lines = text.splitlines(keepends=True)

    # 1. agent timeout
    cur = float((data.get("agent") or {}).get("timeout_sec") or 0)
    if cur < agent_timeout:
        in_agent = False
        done = False
        for i, ln in enumerate(lines):
            s = ln.strip()
            if s.startswith("["):
                in_agent = s == "[agent]"
                continue
            if in_agent and re.match(r"^timeout_sec\s*=", s):
                lines[i] = re.sub(r"=\s*[0-9.]+", f"= {agent_timeout:.1f}", ln, count=1)
                done = True
                break
        if not done:
            sys.exit("REFUSED: [agent] timeout_sec line not found in task.toml")
        notes.append(f"[agent] timeout_sec {cur:g} -> {agent_timeout:.1f}")
    else:
        notes.append(f"[agent] timeout_sec {cur:g} kept")

    # 2. judge keys: at the TOP of [verifier.env], XAI before ANTHROPIC before GEMINI before OPENAI, the order the
    #    team's dataos_copy_addkeys.py and the 2026-10-30 prep used (rebuild_refs_noenv.py relies on it)
    if add_keys:
        env = (data.get("verifier") or {}).get("env") or {}
        declared = set(re.findall(r"^(\w+_API_KEY)\s*=", text, re.M)) | set(env)
        needed = {PROVIDER_KEY[j.split("/", 1)[0].lower()] for j in judges if j.split("/", 1)[0].lower() in PROVIDER_KEY}
        need = [k for k in ("XAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY") if k in needed - declared]
        if need:
            text2 = "".join(lines)
            if "[verifier.env]" in text2:
                idx = next(i for i, ln in enumerate(lines) if ln.strip() == "[verifier.env]")
                ins = idx + 1
                for k in need:
                    lines.insert(ins, f'{k} = "${{{k}:-}}"\n')
                    ins += 1
            else:
                vi = next((i for i, ln in enumerate(lines) if ln.strip() == "[verifier]"), None)
                if vi is None:
                    sys.exit("REFUSED: no [verifier] section to attach [verifier.env] to")
                end = vi + 1
                while end < len(lines) and not lines[end].strip().startswith("["):
                    end += 1
                block = ["\n", "[verifier.env]\n"] + [f'{k} = "${{{k}:-}}"\n' for k in need] + ["\n"]
                lines[end:end] = block
                notes.append("NOTE: the download had no [verifier.env]; a new table was added (the team's script stops here: 'decide by hand'). Keep the original; rebuild_refs_noenv.py expects this shape")
            notes.append("added judge keys: " + ", ".join(need))
        else:
            notes.append("judge keys: all declared")
    new = "".join(lines)
    tomllib.loads(new)  # must still parse
    return new, notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--agent-timeout", type=float, default=14400.0)
    ap.add_argument("--no-keys", action="store_true")
    a = ap.parse_args()
    src, dst = Path(a.src), Path(a.dst)
    if dst.exists():
        sys.exit(f"REFUSED: {dst} exists")
    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as zi:
        if zi.testzip():
            sys.exit("REFUSED: corrupt input zip")
        root = zip_root(zi)
        names = zi.namelist()
        if root is None and "task.toml" in names:
            # RL World's own export is flat (instruction.md, task.toml, environment/, solution/, tests/ at the root);
            # the version then comes from the zip's file name
            if not RLW_NAME.match(src.stem):
                sys.exit(f"REFUSED: flat zip whose file name is not <task>-v<N>-dataos-harbor.zip ({src.name}); download it again from RL World")
            prefix = ""
        elif root and RLW_NAME.match(root):
            prefix = root + "/"
        else:
            sys.exit(f"REFUSED: expected RL World's flat export or qc.py rlworld-prep's one-folder copy named <task>-v<N>-dataos-harbor (got root {root!r})")
        toml_name = f"{prefix}task.toml"
        vj_name = f"{prefix}tests/verifier.json"
        if toml_name not in names:
            sys.exit("REFUSED: task.toml not at the package root")
        judges = []
        if vj_name in names:
            try:
                judges = list((json.loads(zi.read(vj_name)).get("config") or {}).get("models") or [])
            except ValueError:
                say("warn tests/verifier.json did not parse; no keys added")
        old = zi.read(toml_name).decode("utf-8")
        new, notes = edit_toml(old, judges, a.agent_timeout, not a.no_keys)
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
            for info in zi.infolist():
                data = zi.read(info)
                if info.filename == toml_name:
                    zo.writestr(info, new.encode("utf-8"))
                else:
                    zo.writestr(info, data)
    # assert
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst) as zo:
        if zi.namelist() != zo.namelist():
            dst.unlink()
            sys.exit("REFUSED: entry list changed (internal error)")
        changed = [n for n in zi.namelist() if not n.endswith("/") and zi.read(n) != zo.read(n)]
        if changed != [toml_name]:
            dst.unlink()
            sys.exit(f"REFUSED: files other than task.toml differ: {changed}")
    for n in notes:
        say("  " + n)
    diff = difflib.unified_diff(old.splitlines(), new.splitlines(), "task.toml (RL World)", "task.toml (DataOS copy)", lineterm="", n=1)
    say("\n".join(diff))
    say(f"judges: {judges}")
    say(f"DATAOS COPY: written {dst} ({md5(dst)}); only task.toml differs from {src.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
