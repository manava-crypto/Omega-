#!/usr/bin/env python3
"""Does each xlsx verifier's extract fit the workbooks it will grade? Read-only, standard library only.

    python xlsx_ranges.py <package zip or folder> [<Dataset/Task with runs zip or folder> ...] [--cap 440000]

The first argument holds tests/verifier.json and the golden (solution/<path>). Every further argument is a
with-runs download (or an unpacked one): the solver workbooks are read from each evaluation's
eval_files/artifacts/workspace.tar.gz (output/<file>), or from eval_files/artifacts/workspace/output/ when the
export ships the workspace unpacked (both shapes seen on 2026-11-02). For every verifier whose source is `extract_xlsx`, and every
workbook at its `path`, it prints, sheet by sheet in tab order (only `sheet_names` when set): the sheet's used
size, whether the verifier's `range` cuts it, and the estimated tokens the extract has used by the end of that
sheet (cell text characters / 3.2, the calibration used on cnipd2jv-0; an estimate, not the library's count).
A sheet that ends past the cap is never seen by the judge.

Why: on 2026-11-02/03 cnipd2jv-0 took five DataOS runs because extracts hit the 440k cap one workbook at a time
(ISSUES-LOG rows 18, 21, 25, 27, 28). Size every range on the golden and every solver workbook before round 1.
Last line: RANGES: OK n checks, none past the cap (m with cut sheets to eyeball), or RANGES: PAST CAP n of m.
"""
from __future__ import annotations

import io
import json
import re
import sys
import tarfile
import zipfile
from pathlib import Path

CELL = re.compile(r'<c r="([A-Z]+)(\d+)"([^>]*?)(?:/>|>(.*?)</c>)', re.S)
TEXT = re.compile(r"<t[^>]*>(.*?)</t>", re.S)


def col_num(c: str) -> int:
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n


def parse_range(r: str | None) -> tuple[int, int] | None:
    if not r:
        return None
    m = re.fullmatch(r"A1:([A-Z]+)(\d+)", r.strip().upper())
    return (col_num(m.group(1)), int(m.group(2))) if m else None


def sheets(xlsx: bytes) -> list[tuple[str, list[tuple[int, int, int]]]]:
    """[(sheet name, [(col, row, chars)])] in tab order."""
    out = []
    with zipfile.ZipFile(io.BytesIO(xlsx)) as x:
        names = x.namelist()
        shared: list[str] = []
        if "xl/sharedStrings.xml" in names:
            sx = x.read("xl/sharedStrings.xml").decode("utf-8", "replace")
            shared = ["".join(TEXT.findall(si)) for si in re.findall(r"<si>(.*?)</si>", sx, re.S)]
        wb = x.read("xl/workbook.xml").decode("utf-8", "replace")
        rels = x.read("xl/_rels/workbook.xml.rels").decode("utf-8", "replace")
        target = {}
        for rel in re.findall(r"<Relationship [^>]*>", rels):
            i = re.search(r'Id="([^"]+)"', rel)
            t = re.search(r'Target="([^"]+)"', rel)
            if i and t:
                target[i.group(1)] = t.group(1)
        for tag in re.findall(r"<sheet [^>]*>", wb):
            name = re.search(r'name="([^"]*)"', tag).group(1)
            rid = re.search(r'r:id="([^"]+)"', tag).group(1)
            t = target.get(rid, "").lstrip("/")
            path = t if t.startswith("xl/") else "xl/" + t
            if path not in names:
                continue
            cells = []
            for c, r, attrs, body in CELL.findall(x.read(path).decode("utf-8", "replace")):
                body = body or ""
                if 't="s"' in attrs:
                    v = re.search(r"<v>(\d+)</v>", body)
                    s = shared[int(v.group(1))] if v and int(v.group(1)) < len(shared) else ""
                elif 't="inlineStr"' in attrs:
                    s = "".join(TEXT.findall(body))
                else:
                    v = re.search(r"<v>(.*?)</v>", body, re.S)
                    f = re.search(r"<f[^>]*>(.*?)</f>", body, re.S)
                    s = (v.group(1) if v else "") + (" =" + f.group(1) if f else "")
                if s:
                    cells.append((col_num(c), int(r), len(s) + 2))
            out.append((name.replace("&amp;", "&"), cells))
    return out


def open_tree(p: Path):
    """Yield (relative name, bytes reader) for a zip or a folder."""
    if p.is_dir():
        for f in p.rglob("*"):
            if f.is_file():
                yield f.relative_to(p).as_posix(), f.read_bytes
    else:
        z = zipfile.ZipFile(p)
        for n in z.namelist():
            if not n.endswith("/"):
                yield n, (lambda n=n: z.read(n))


def find_package(p: Path) -> tuple[dict, dict[str, bytes]]:
    verifier, golden = None, {}
    for name, read in open_tree(p):
        if name.endswith("tests/verifier.json") and verifier is None:
            verifier = json.loads(read().decode("utf-8"))
        elif "solution/" in name and name.lower().endswith(".xlsx"):
            golden[name.split("solution/", 1)[1]] = read()
    if verifier is None:
        sys.exit(f"no tests/verifier.json in {p}")
    return verifier, golden


def run_workbooks(p: Path) -> list[tuple[str, str, bytes]]:
    out = []
    for name, read in open_tree(p):
        if "artifacts/workspace/output/" in name and name.lower().endswith(".xlsx"):
            # unpacked export shape: eval_files/artifacts/workspace/output/<file>
            m = re.search(r"evaluations/(eval_[^/]+)/", name)
            out.append((m.group(1) if m else name, "output/" + name.split("artifacts/workspace/output/", 1)[1], read()))
            continue
        if not name.endswith("workspace.tar.gz"):
            continue
        m = re.search(r"evaluations/(eval_[^/]+)/", name)
        label = m.group(1) if m else name
        with tarfile.open(fileobj=io.BytesIO(read()), mode="r:gz") as t:
            for mem in t.getmembers():
                if mem.isfile() and mem.name.lower().endswith(".xlsx") and "/output/" in "/" + mem.name:
                    rel = "output/" + mem.name.split("output/", 1)[1]
                    out.append((label, rel, t.extractfile(mem).read()))
    return out


def main() -> int:
    if {"-h", "--help"} & set(sys.argv[1:]):  # a newcomer's first try; it was read as a file name
        print(__doc__)
        return 0
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cap = 440000
    if "--cap" in sys.argv:
        cap = int(sys.argv[sys.argv.index("--cap") + 1])
        args = [a for a in args if a != str(cap)]
    if not args:
        sys.exit(__doc__)
    verifier, golden = find_package(Path(args[0]))
    books = [("golden", rel, data) for rel, data in golden.items()]
    for extra in args[1:]:
        books += run_workbooks(Path(extra))
    parsed: dict[int, list] = {}
    review, checks, cuts = [], 0, 0
    for v in verifier.get("verifiers", []):
        src = (v.get("source") or {}).get("file") or {}
        if src.get("command") != "extract_xlsx":
            continue
        a = src.get("arguments") or {}
        path, rng, only = a.get("path", ""), parse_range(a.get("range")), a.get("sheet_names")
        vid = v.get("name") or v.get("id")
        for label, rel, data in books:
            if Path(rel).name != Path(path).name:
                continue
            checks += 1
            sh = parsed.setdefault(id(data), sheets(data))
            used, cut, past = 0, [], []
            for name, cells in sh:
                if only and name not in only:
                    continue
                if not cells:
                    continue
                mc = max(c for c, _, _ in cells)
                mr = max(r for _, r, _ in cells)
                inside = [n for c, r, n in cells if rng is None or (c <= rng[0] and r <= rng[1])]
                used += sum(inside) / 3.2
                if rng and (mc > rng[0] or mr > rng[1]):
                    cut.append(f"{name} ({mc} cols x {mr} rows)")
                if used > cap:
                    past.append(f"{name} (~{int(used/1000)}k)")
            line = f"{vid} | {label} {rel} | range {a.get('range') or 'whole'} | ~{int(used/1000)}k tokens"
            if past:
                review.append(line)
                print("PAST CAP " + line)
                print("   never seen by the judge: " + "; ".join(past))
            else:
                print("ok       " + line)
            if cut:
                cuts += 1
                print("   cut by range (fine unless this verifier grades rows/cols past it): " + "; ".join(cut))
    if not checks:
        print("RANGES: OK (no extract_xlsx verifier matched a workbook)")
        return 0
    print("Check each PAST CAP sheet and each cut sheet the verifier grades: if it holds evidence, resize the range.")
    if review:
        print(f"RANGES: PAST CAP {len(review)} of {checks} ({cuts} with cut sheets)")
        return 1
    print(f"RANGES: OK {checks} checks, none past the cap ({cuts} with cut sheets to eyeball)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
