#!/usr/bin/env python3
"""Check that each RL World export carries the judges set in the "Configure rubric judges" dialog.

    python check_judges.py <export zip> [<export zip> ...]

Reads tests/verifier.json inside each zip (read-only) and compares its "models" list, in order, with
fix_config.json: rlworld_judges (default xai/grok-4.7, anthropic/claude-sonnet-5-5, anthropic/claude-opus-5-5).
Why: on 2026-11-02 the Artifacts-panel "Download artifacts" button skipped the dialog and exported the task's
own judges (grok-4.7, gemini-3.8-flash, sonnet-5-5); only Quality Checks -> Export & Download -> Download
artifacts opens it. Run this right after every download, before fix_record.py add or any other step.
Last line: JUDGES: OK n of n, or JUDGES: WRONG n of m (names the zips).
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_common import load_config, md5, say  # noqa: E402

DEFAULT = ["xai/grok-4.7", "anthropic/claude-sonnet-5-5", "anthropic/claude-opus-5-5"]


def models_in(zf: zipfile.ZipFile) -> list[str] | None:
    names = [n for n in zf.namelist() if n.endswith("tests/verifier.json")]
    if len(names) != 1:
        return None
    data = json.loads(zf.read(names[0]).decode("utf-8"))
    found = data.get("models") if isinstance(data, dict) else None
    if found is None and isinstance(data, dict):
        found = (data.get("config") or {}).get("models")
    return list(found) if isinstance(found, list) else None


def main() -> int:
    if {"-h", "--help"} & set(sys.argv[1:]):  # a newcomer's first try; it was read as a file name
        print(__doc__)
        return 0
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    try:
        want = load_config().get("rlworld_judges") or DEFAULT
    except Exception:
        want = DEFAULT
    bad = []
    for arg in sys.argv[1:]:
        p = Path(arg)
        with zipfile.ZipFile(p) as zf:
            got = models_in(zf)
        ok = got == want
        say(f"{'ok ' if ok else 'BAD'} {p.name}  md5 {md5(p)}  models {got}")
        if not ok:
            bad.append(p.name)
    n = len(sys.argv) - 1
    if bad:
        say(f"expected {want}; set these aside and download again via Quality Checks -> Export & Download")
        say(f"JUDGES: WRONG {len(bad)} of {n}: {', '.join(bad)}")
        return 1
    say(f"JUDGES: OK {n} of {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
