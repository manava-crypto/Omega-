#!/usr/bin/env python3
"""Audit a verifier fix before any user gate: is it verifier.json only, and is every zip what it claims? Read-only.

    python audit_fix.py --original <RL World zip> --fixed <fixed zip>
                        [--dataos <DataOS copy zip>] [--trainer <zip for the trainer>] [--runs <with-runs zip> ...]

Checks (a wrapping root folder in a zip is ignored when comparing):
  1. original -> fixed: only tests/verifier.json differs; no file added, removed or renamed.
  2. verifier.json: `config` (judges, temperature, samples) unchanged; judges are the dialog set
     (fix_config.json rlworld_judges); weights sum to 1; verifiers removed or added are listed (a removal needs its
     weight moved, see verifier-json-fix step 5).
  3. fixed -> DataOS copy: only task.toml differs, and only by [agent] timeout_sec 600 -> 14400 and added
     KEY = "${KEY:-}" lines.
  4. trainer zip: flat (instruction.md at the root), same files and bytes as the fixed zip, task.toml and
     instruction.md byte-identical to the original, testzip clean.
  5. xlsx extracts against the golden and every solver workbook in --runs (xlsx_ranges.py): reported, never
     decides PASS; a PAST CAP line is a Major risk to settle before asking for a run.
Why: on 2026-11-02/03 the coordinator caught clipped ranges, a wrong-judge download and an overwritten round only
by checking by hand (ISSUES-LOG rows 1, 21, 26). Run this before every ask; quote its last line in the ask.
Last line: AUDIT: PASS (n checks) or AUDIT: FAIL n (names each).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_common import load_config, md5  # noqa: E402

DEFAULT_JUDGES = ["xai/grok-4.7", "anthropic/claude-sonnet-5-5", "anthropic/claude-opus-5-5"]


def entries(p: Path) -> tuple[zipfile.ZipFile, dict[str, str], dict[str, int], bool]:
    z = zipfile.ZipFile(p)
    names = [n for n in z.namelist() if not n.endswith("/")]
    roots = {n.split("/")[0] for n in names}
    wrapped = len(roots) == 1 and all("/" in n for n in names)
    real = {(n.split("/", 1)[1] if wrapped else n): n for n in names}
    return z, real, {k: z.getinfo(v).CRC for k, v in real.items()}, wrapped


def verifier(z: zipfile.ZipFile, real: dict[str, str]) -> dict:
    return json.loads(z.read(real["tests/verifier.json"]).decode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", required=True)
    ap.add_argument("--fixed", required=True)
    ap.add_argument("--dataos")
    ap.add_argument("--trainer")
    ap.add_argument("--runs", nargs="*", default=[])
    ap.add_argument("--scope", help="the record's SCOPE.md: verifiers tied to GOLDEN/PROMPT/DATA rows must be unchanged")
    a = ap.parse_args()
    try:
        want = load_config().get("rlworld_judges") or DEFAULT_JUDGES
    except (Exception, SystemExit):  # no fix_config.json: the audit still runs, with the default dialog set
        want = DEFAULT_JUDGES
    fails, n = [], 0

    def check(ok: bool, msg: str) -> None:
        nonlocal n
        n += 1
        print(("ok   " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    oz, oreal, ocrc, _ = entries(Path(a.original))
    fz, freal, fcrc, _ = entries(Path(a.fixed))
    print(f"original {md5(Path(a.original))}  fixed {md5(Path(a.fixed))}")
    changed = sorted(k for k in ocrc.keys() & fcrc.keys() if ocrc[k] != fcrc[k])
    moved = sorted(ocrc.keys() ^ fcrc.keys())
    check(changed == ["tests/verifier.json"] and not moved,
          f"original -> fixed changes only tests/verifier.json (changed {changed}, added/removed {moved})")

    ov, fv = verifier(oz, oreal), verifier(fz, freal)
    check(ov.get("config") == fv.get("config"), "verifier.json config (judges, settings) unchanged")
    models = (fv.get("config") or {}).get("models") or fv.get("models")
    # The judges come from the RL World download and are never changed by a fix (config is checked above). Whether they
    # are the dialog set is information: a task downloaded with other judges is still fixed on the judges it has.
    print(("ok   " if models == want else "note ") + f"judges {'are' if models == want else 'are not'} the dialog set {want} (found {models})")
    # Effective weights as the RL World library computes them (rl_world_verifiers/models.py): explicit weights as
    # given, and every unweighted verifier gets an equal share of (1 - explicit sum). A file with no weights at all is
    # therefore equal-weighted and valid (#35, ISSUES-LOG row 41).
    vs = fv.get("verifiers", [])
    explicit = [(x.get("metadata") or {}).get("weight", x.get("weight")) for x in vs]
    given = [float(w) for w in explicit if w is not None]
    unweighted = sum(1 for w in explicit if w is None)
    rest = 1 - sum(given)
    ok_w = (abs(rest) < 1e-6 and unweighted == 0) or (unweighted > 0 and rest > 1e-9)
    check(ok_w, f"effective verifier weights sum to 1 ({len(given)} explicit summing {sum(given):.6f}, "
                f"{unweighted} unweighted sharing {max(rest, 0):.6f})")
    ow = [(x.get("metadata") or {}).get("weight", x.get("weight")) for x in ov.get("verifiers", [])]
    if (unweighted == len(vs)) != all(w is None for w in ow):
        print("note weighting style changed from the original (weighted <-> unweighted): check it was intended")
    on = {x.get("name") or x.get("id") for x in ov.get("verifiers", [])}
    fn = {x.get("name") or x.get("id") for x in fv.get("verifiers", [])}
    if on != fn:
        print(f"note removed {sorted(on - fn)} added {sorted(fn - on)}: names must stay stable; a removal moves its weight")
    edited = sorted(x.get("name") or x.get("id") for x in fv.get("verifiers", [])
                    if x != next((y for y in ov.get("verifiers", []) if (y.get("name") or y.get("id")) == (x.get("name") or x.get("id"))), None))
    print(f"note {len(edited)} verifiers edited: {', '.join(edited)}")

    if a.scope:
        # A verifier tied to a content defect (GOLDEN / PROMPT / DATA) must not be reworded so the defect passes:
        # "don't edit a verifier to fit a wrong golden" (Anunay, 2026-11-03: "this won't suddenly start passing?").
        import re as _re
        locked = set()
        for line in Path(a.scope).read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 6 and cells[5].upper() in ("GOLDEN", "PROMPT", "DATA"):
                # every real verifier name the cell mentions, short ones (v14, v7f) included
                names = {x.get("name") or x.get("id") for x in ov.get("verifiers", [])} - {None}
                locked |= {nm for nm in names if _re.search(rf"(?<![\w-]){_re.escape(nm)}(?![\w-])", cells[2])}
        touched = sorted(locked & set(edited))
        check(not touched, f"verifiers tied to GOLDEN/PROMPT/DATA rows are unchanged ({len(locked)} locked"
                           + (f"; CHANGED: {', '.join(touched)}" if touched else "") + ")")

    if a.dataos:
        dz, dreal, dcrc, _ = entries(Path(a.dataos))
        print(f"dataos   {md5(Path(a.dataos))}")
        dchanged = sorted(k for k in fcrc.keys() & dcrc.keys() if fcrc[k] != dcrc[k])
        check(dchanged == ["task.toml"] and not (fcrc.keys() ^ dcrc.keys()),
              f"fixed -> DataOS copy changes only task.toml (changed {dchanged}, added/removed {sorted(fcrc.keys() ^ dcrc.keys())})")
        ft = fz.read(freal["task.toml"]).decode("utf-8").splitlines()
        dt_ = dz.read(dreal["task.toml"]).decode("utf-8").splitlines()
        removed = [l.strip() for l in ft if l not in dt_]
        added = [l.strip() for l in dt_ if l not in ft]
        okrem = all(l.replace(" ", "") in ("timeout_sec=600.0", "timeout_sec=600") for l in removed)
        okadd = all(l.replace(" ", "") in ("timeout_sec=14400.0", "timeout_sec=14400") or
                    (l.split("=")[0].strip().endswith("_API_KEY") and ":-}" in l) for l in added)
        check(okrem and okadd, f"task.toml diff is only agent timeout + added keys (removed {removed}, added {added})")

    if a.trainer:
        tz, treal, tcrc, twrapped = entries(Path(a.trainer))
        print(f"trainer  {md5(Path(a.trainer))}")
        check(not twrapped and "instruction.md" in tz.namelist(), "trainer zip is flat (instruction.md at the root)")
        check(tcrc == fcrc, "trainer zip has the same files and bytes as the fixed zip")
        check(tz.read(treal["task.toml"]) == oz.read(oreal["task.toml"]) and
              tz.read(treal["instruction.md"]) == oz.read(oreal["instruction.md"]),
              "task.toml and instruction.md byte-identical to RL World's")
        check(tz.testzip() is None, "trainer zip tests clean")

    print("-- xlsx extracts (information; settle any PAST CAP before asking for a run) --")
    r = subprocess.run([sys.executable, "-I", "-X", "utf8", str(Path(__file__).with_name("xlsx_ranges.py")), a.fixed, *a.runs],
                       capture_output=True, text=True, encoding="utf-8")
    lines = [l for l in r.stdout.splitlines() if l.startswith(("PAST CAP", "   never seen", "RANGES"))]
    print("\n".join(lines) or r.stdout.strip()[-400:])

    if fails:
        print(f"AUDIT: FAIL {len(fails)} of {n}: " + " | ".join(fails))
        return 1
    print(f"AUDIT: PASS ({n} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
