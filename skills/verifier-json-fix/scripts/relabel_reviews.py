#!/usr/bin/env python3
"""Relabel DataOS reviews so qc.py, the converter and RL World read them: custom_<id> -> comprehensive_review_<id>.

    python relabel_reviews.py <out dir> <per-task zip or rev folder> [...]

DataOS saves the four Answer Check reviews as verifications/custom_<id>___<agent>__<model>.md with
`## type` = custom. qc.py manage / release / rlworld, manager_read.py and the RL World converter read only
comprehensive_review_<id>___*.md whose `## type` is COMPREHENSIVE_REVIEW (converter REVIEW_TYPE; the team's
relabel_with_runs.py writes the same). For each input this writes a copy into <out dir> (zip -> zip, folder
-> folder) in which only the file name and that one line change; the rest of each review is asserted
byte-identical and every other entry is copied as is. Inputs are never modified. Fallback for the team's
relabel_with_runs.py (same effect; prefer the team's when it is on the machine).
Last line: RELABEL: n file(s) in m package(s).
"""
from __future__ import annotations

import re
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_common import md5, say  # noqa: E402

CUSTOM = re.compile(r"^(?P<dir>(?:[^/]+/)*verifications/)custom_(?P<rest>\d+___[^/]*\.md)$")
TYPE = re.compile(r"\A## type(\r?\n)custom(\r?\n)")


def relabel_text(data: bytes, where: str) -> bytes:
    text = data.decode("utf-8", errors="surrogateescape")
    new, n = TYPE.subn(r"## type\1COMPREHENSIVE_REVIEW\2", text, count=1)
    if n != 1:
        sys.exit(f"REFUSED: {where} does not start with '## type' / 'custom'")
    assert new.replace("COMPREHENSIVE_REVIEW", "custom", 1) == text, where
    return new.encode("utf-8", errors="surrogateescape")


def main() -> int:
    if {"-h", "--help"} & set(sys.argv[1:]):  # a newcomer's first try; it was read as a file name
        print(__doc__)
        return 0
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    total_files = total_pkgs = 0
    for arg in sys.argv[2:]:
        src = Path(arg)
        n = 0
        if src.is_file() and src.suffix.lower() == ".zip":
            dst = out / src.name
            if dst.exists():
                sys.exit(f"REFUSED: {dst} exists")
            with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
                for info in zi.infolist():
                    data = zi.read(info.filename)
                    m = CUSTOM.match(info.filename)
                    if not m:
                        zo.writestr(info, data)
                        continue
                    zinfo = zipfile.ZipInfo(m.group("dir") + "comprehensive_review_" + m.group("rest"), date_time=info.date_time)
                    zinfo.compress_type = zipfile.ZIP_DEFLATED
                    zo.writestr(zinfo, relabel_text(data, info.filename))
                    n += 1
            say(f"{dst.name}: {n} review(s) relabelled ({md5(dst)})")
        elif src.is_dir():
            dst = out / src.name
            if dst.exists():
                sys.exit(f"REFUSED: {dst} exists; choose an empty out dir")
            shutil.copytree(src, dst)
            for f in sorted(dst.rglob("custom_*.md")):
                if f.parent.name != "verifications":
                    continue
                m = re.match(r"^custom_(\d+___.*\.md)$", f.name)
                if not m:
                    continue
                newf = f.with_name("comprehensive_review_" + m.group(1))
                newf.write_bytes(relabel_text(f.read_bytes(), str(f)))
                f.unlink()
                n += 1
            say(f"{dst.name}: {n} review(s) relabelled")
        else:
            say(f"skip {src}: not a zip or folder")
            continue
        if n != 4:
            say(f"  warn {src.name}: {n} reviews relabelled, a full run has 4")
        total_files += n
        total_pkgs += 1
    say(f"RELABEL: {total_files} file(s) in {total_pkgs} package(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
