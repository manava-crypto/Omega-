#!/usr/bin/env python3
"""Split one combined DataOS "Dataset with runs" export into one zip per task.

    python split_batch_zip.py <combined zip> <out dir>

A combined export holds several task folders at its root, each with rev_<n>__<id>/ inside. Each task
becomes <out dir>/<task folder name>_with_runs.zip (the team's naming) holding that folder and nothing
else, bytes unchanged. A zip that holds one task (a single root folder with rev_* inside) is copied as is.
The input is never modified. Fallback for the team's split_batch_zip.py.
Last line: SPLIT: n zip(s) written.
"""
from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_common import REV_RE, md5, say  # noqa: E402


def main() -> int:
    if {"-h", "--help"} & set(sys.argv[1:]):  # a newcomer's first try; it was read as a file name
        print(__doc__)
        return 0
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as zf:
        bad = zf.testzip()
        if bad:
            sys.exit(f"corrupt zip entry: {bad}")
        names = zf.namelist()
        roots: dict[str, list[str]] = {}
        for n in names:
            parts = n.split("/")
            if len(parts) >= 2 and parts[0]:
                roots.setdefault(parts[0], []).append(n)
        task_roots = {r: ns for r, ns in roots.items() if any(REV_RE.match(n.split("/")[1]) for n in ns if len(n.split("/")) > 2)}
        if not task_roots:
            # maybe <root>/<task>/rev_*: one level deeper
            deeper: dict[str, list[str]] = {}
            for n in names:
                parts = n.split("/")
                if len(parts) >= 3 and REV_RE.match(parts[2]):
                    deeper.setdefault(parts[1], []).append(n)
            if not deeper:
                sys.exit("no task folders with rev_<n>__<id> inside found")
            written = 0
            for task, ns in deeper.items():
                dst = out / f"{task}_with_runs.zip"
                with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
                    for n in ns:
                        info = zf.getinfo(n)
                        zo.writestr(n.split("/", 1)[1], zf.read(n), compress_type=info.compress_type)
                say(f"wrote {dst.name} ({len(ns)} entries, {md5(dst)})")
                written += 1
            say(f"SPLIT: {written} zip(s) written")
            return 0
        if len(task_roots) == 1:
            dst = out / f"{next(iter(task_roots))}_with_runs.zip"
            shutil.copy2(src, dst)
            say(f"one task only: copied as {dst.name} ({md5(dst)})")
            say("SPLIT: 1 zip(s) written")
            return 0
        written = 0
        for task, ns in task_roots.items():
            dst = out / f"{task}_with_runs.zip"
            with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
                for n in ns:
                    info = zf.getinfo(n)
                    zo.writestr(info, zf.read(n))
            say(f"wrote {dst.name} ({len(ns)} entries, {md5(dst)})")
            written += 1
    say(f"SPLIT: {written} zip(s) written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
