#!/usr/bin/env python3
"""Make a reader-only copy of a rev folder so the toolkit's readers can run on an RL World package.

    python reader_copy.py <rev folder> <out rev folder> [--golden-outputs] [--fence-verdicts] [--weights]

  --golden-outputs   RL World goldens live in solution/output/; qc.py proof's golden-answer reader looks in
                     solution/golden_outputs/. The copy gets golden_outputs/ as a copy of output/.
  --fence-verdicts   manager_read.py reads a verdict only from a fenced ```json block and needs all four. For
                     each verifications/comprehensive_review_*.md (or custom_*.md): a trailing `checks` block
                     (the newer review prompt) is cut, and an unfenced closing verdict JSON is wrapped in
                     fences. The JSON text is unchanged (asserted). A review whose only JSON is the checks
                     block is left as it is.
  --weights          verifier.json checks without metadata.weight make qc.py read / manage fail with
                     KeyError 'weight'. The copy gives them the weight the runtime uses:
                     (1 - sum of explicit weights) / number of unweighted checks.
Same behaviour as the team's _manager_tools/reader_copy.py (prefer that one when present). The copy is for
reading only: never upload it, never ship it, never run integrity against it. The input is never modified.
Last line: READER COPY: <out> (<changes>).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_common import say  # noqa: E402


def fence(text: str) -> tuple[str, str]:
    dec = json.JSONDecoder()
    objs, i = [], 0
    while True:
        j = text.find("{", i)
        if j < 0:
            break
        try:
            o, k = dec.raw_decode(text, j)
            objs.append((j, k, o))
            i = k
        except ValueError:
            i = j + 1
    std = [x for x in objs if isinstance(x[2], dict) and "findings" in x[2] and "overall_verdict" in x[2]]
    if not std:
        return text, "left as is: no standard verdict"
    notes = []
    last = objs[-1]
    if isinstance(last[2], dict) and isinstance(last[2].get("checks"), list) and last[0] > std[-1][1] and not text[last[1]:].strip():
        text = text[: last[0]].rstrip() + "\n"
        notes.append("checks block cut")
    if not text.rstrip().endswith("```"):
        j, k, o = std[-1]
        if not text[k:].strip():
            text = text[:j] + "```json\n" + text[j:k] + "\n```\n"
            assert json.loads(text[text.rfind("```json\n") + 8: text.rfind("\n```")]) == o
            notes.append("verdict fenced")
    return text, ", ".join(notes) or "unchanged"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rev")
    ap.add_argument("out")
    ap.add_argument("--golden-outputs", action="store_true")
    ap.add_argument("--fence-verdicts", action="store_true")
    ap.add_argument("--weights", action="store_true")
    a = ap.parse_args()
    rev, out = Path(a.rev), Path(a.out)
    if not (rev / "task_files").is_dir():
        sys.exit("REFUSED: not a rev folder (no task_files/)")
    if out.exists():
        sys.exit(f"REFUSED: {out} exists")
    shutil.copytree(rev, out)
    changes = []
    tf = out / "task_files"
    if a.golden_outputs:
        src, dst = tf / "solution" / "output", tf / "solution" / "golden_outputs"
        if src.is_dir() and not dst.exists():
            shutil.copytree(src, dst)
            changes.append(f"golden_outputs/ = copy of output/ ({sum(1 for _ in dst.rglob('*') if _.is_file())} files)")
        else:
            changes.append("golden_outputs: nothing to do")
    if a.fence_verdicts:
        done = []
        vd = out / "verifications"
        for f in sorted(vd.glob("*.md")) if vd.is_dir() else []:
            if not re.match(r"(comprehensive_review|custom)_\d+___.*\.md$", f.name):
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            new, note = fence(text)
            if new != text:
                f.write_text(new, encoding="utf-8")
            done.append(f"{f.name[:34]}: {note}")
        changes.append("fence: " + "; ".join(done))
    if a.weights:
        vj = tf / "tests" / "verifier.json"
        if vj.is_file():
            d = json.loads(vj.read_text(encoding="utf-8"))
            vs = d.get("verifiers") or []
            un = [v for v in vs if (v.get("metadata") or {}).get("weight") is None]
            if un:
                exp = sum((v.get("metadata") or {}).get("weight") or 0 for v in vs)
                w = (1 - exp) / len(un)
                for v in un:
                    v.setdefault("metadata", {})["weight"] = w
                vj.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
                changes.append(f"weights: {len(un)} check(s) given {w:.6f} (reader copy only)")
            else:
                changes.append("weights: all present")
        else:
            changes.append("weights: no tests/verifier.json")
    (out / "READER_COPY_DO_NOT_SHIP.txt").write_text("Reader-only copy made by reader_copy.py. Never upload, ship or compare integrity against it.\n" + "\n".join(changes) + "\n", encoding="utf-8")
    say(f"READER COPY: {out} ({'; '.join(changes) or 'no changes'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
