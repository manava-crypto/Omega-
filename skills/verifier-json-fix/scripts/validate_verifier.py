#!/usr/bin/env python3
"""Check an edited tests/verifier.json against the original task, and prove nothing else changed.

    python validate_verifier.py <original task folder> <edited task folder> [--allow-config-change] [--kept-how edits_r*.json]
    python validate_verifier.py <original task folder> --verifier <edited verifier.json>

A task folder holds tests/verifier.json (for a DataOS download, the rev folder's task_files/). The original is never
written to. The last line is VERIFIER CHECK: PASS or VERIFIER CHECK: FAIL (n problems); exit code 0 or 1.

PROBLEM lines fail the check:
  1. Only tests/verifier.json differs between the two folders (byte-compare of every other file).
  2. The JSON parses, and the task's own bundled verifier library accepts it (its models.py VerifierSpec). The library
     is found anywhere under tests/ (tests/verifier_lib/, tests/__verifier_lib/, RL World's
     tests/__verifier_lib/rl_world_verifiers/ or tests/rl_world_verifiers/). A task whose library cannot be found or
     loaded is a PROBLEM, because nothing else can confirm the file will run.
  3. Verifier names are unique, and weights follow the library's rule: each weight is > 0 and <= 1; when every
     verifier has a weight they sum to 1 (within 1e-6); unweighted verifiers need positive weight left over.
  4. Every source command exists in the bundled library for its file type.
  5. Every output/ path a verifier reads is a file in the golden folder (the solution/ folder solve.sh copies from:
     golden_outputs/ on EKW, output/ on RL World, files/ on SVC), and every data/ path exists in environment/data.
  6. config (judge models, temperature, effort) is unchanged unless --allow-config-change.
  7. Every rubric verifier has a prompt and expected true, and keeps the metadata fields the original verifiers carry.

WARNING lines do not fail the check, but each one names a rule the QC pipeline or RL World gates on. Read every one
and either change the edit or say in the report why it stands:
  - verifier count outside 6 to 20, when the edit changed the count;
  - estimated serial judging time (rubric verifiers x judges x 46 s) above [verifier] timeout_sec / 1.5;
  - the last deterministic verifier removed; outcome verifiers' mean weight below the process verifiers';
  - a changed verifier whose source or assertion changed but whose how/why justification did not (a NOTE instead when
    an edits file given with --kept-how states why it stays; a "*" reason covers only that file's own edits);
  - a changed rubric prompt that points at the instruction instead of carrying its own values;
  - extract_many with a data/ file before the deliverable, or a per-file text budget below 20,000 characters;
  - a new sheet, sheet_names or cell_range argument, or a range tied to a sheet (layout pin; a range alone on every
    sheet that starts at A1 and spans 10+ columns and 20+ rows is a size cap and only a NOTE); a gemini/ judge in
    config.models;
  - tests/verifier-plan.md, which now describes the old verifiers and is not this skill's to edit;
  - on every verifier, changed or not: a PASS that rests on absence ("contains no", "is limited to") with no presence
    gate, which an empty or placeholder deliverable passes.
Then it prints what changed per verifier, and the old and new weight of each changed verifier, for the fix report.
"""
import argparse
import hashlib
import importlib
import json
import re
import sys
import types
from pathlib import Path

SKIP_DIRS = {"__pycache__", ".DS_Store"}
# Loading the task's models.py must not write a __pycache__ folder into the original task.
sys.dont_write_bytecode = True

GOLDEN_DIRS = ("golden_outputs", "output", "files", "golden")  # solution/<name>, tried in this order
SECONDS_PER_JUDGE_CALL = 46.0  # measured on DataOS (deterministic-checks/timeout_headroom_check.py)
MIN_HEADROOM = 1.5
COUNT_RANGE = (6, 20)  # gdpval_qc check_verifier; RL World verifier_count_in_range
EXTRACT_BUDGET = 90000  # SourceContext.max_content_chars default, shared by every file in extract_many
ABSENCE_ONLY = re.compile(
    r"PASS (?:only )?if [^.]{0,80}?\b(?:contains? no|does not (?:contain|include|introduce|state|reproduce)|"
    r"is limited to|are limited to|has no|includes? no|avoids?)\b",
    re.I,
)
PRESENCE_GATE = re.compile(r"\b(?:missing|absent|empty|placeholder|header-only|no substantive)\b", re.I)
POINTS_AWAY = re.compile(
    r"\b(as (the )?(prompt|instructions?|task) (requires|says|specifies|asks)|per the (instructions?|prompt|task)|"
    r"as required by the (prompt|instructions?|task)|see the (instructions?|prompt))\b", re.I)


def wide_range(r):
    """A range that only caps the extract (from column A row 1, at least 10 columns by 20 rows), not one that points
    at a block: 'A1:AZ80' caps, 'D14' or 'C5:F9' pins."""
    m = re.fullmatch(r"\$?A\$?1:\$?([A-Z]{1,3})\$?(\d+)", str(r).strip().upper())
    if not m:
        return False
    col = 0
    for ch in m.group(1):
        col = col * 26 + ord(ch) - 64
    return col >= 10 and int(m.group(2)) >= 20


def kept_how_map(paths):
    """{verifier: reason} from edits files' keep_how. A "*" reason covers only the verifiers that file's own edits
    touched, never every verifier in the task."""
    out = {}
    for p in paths:
        spec = json.loads(Path(p).read_text(encoding="utf-8"))
        keep = spec.get("keep_how") or {}
        touched = set()
        for e in spec.get("edits") or []:
            if not isinstance(e, dict):
                continue
            if isinstance(e.get("verifier"), str):
                touched.add(e["verifier"])
            if isinstance(e.get("verifiers"), list):
                touched |= {x for x in e["verifiers"] if isinstance(x, str)}
            if isinstance(e.get("new_name"), str):
                touched.add(e["new_name"])
        for k, why in keep.items():
            for n in (touched if k == "*" else {k}):
                out.setdefault(n, why)
    return out


def files_of(root):
    out = {}
    for p in root.rglob("*"):
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts):
            out[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def lib_dir(tests):
    """The bundled verifier library: a folder under tests/ holding models.py beside a sources/ folder.

    Covers tests/verifier_lib/, tests/__verifier_lib/ and RL World's nested rl_world_verifiers/. When several match, the
    one whose models.py defines VerifierSpec wins, then the shallowest."""
    cands = []
    for m in tests.rglob("models.py"):
        d = m.parent
        if any(part in SKIP_DIRS for part in d.parts) or not (d / "sources").is_dir():
            continue
        has_spec = "class VerifierSpec" in m.read_text(errors="ignore")
        cands.append((not has_spec, len(d.relative_to(tests).parts), d.as_posix(), d))
    return sorted(cands)[0][3] if cands else None



def _shared_view_commands(lib):
    """{class name: command name} for the shared commands in sources/reading.py (RL World libraries)."""
    rd = lib / "sources" / "reading.py"
    if not rd.is_file():
        return {}
    out, cls = {}, None
    for line in rd.read_text(errors="ignore").splitlines():
        m = re.match(r"class (\w+)\(", line)
        if m:
            cls = m.group(1)
            continue
        m = re.match(r"""\s+name\s*(?::\s*[\w\[\]]+)?\s*=\s*["']([a-z_]+)["']""", line)
        if m and cls:
            out[cls] = m.group(1)
            cls = None
    return out

def _add_shared(lib, cmds, as_list):
    """A format module that imports a reading.py command class, or builds its set with unit_commands(), offers it."""
    shared = _shared_view_commands(lib)
    cmds.pop("reading", None)
    for src in (lib / "sources").glob("*.py"):
        if src.stem not in cmds:
            continue
        text = src.read_text(errors="ignore")
        extra = {n for c, n in shared.items() if re.search(rf"\b{c}\b", text)}
        if "unit_commands" in text:
            extra |= set(shared.values()) - {"render_unit"}
        if extra:
            merged = set(cmds[src.stem]) | extra
            cmds[src.stem] = sorted(merged) if as_list else merged

def lib_commands(lib):
    cmds = {}
    if not lib:
        return cmds
    for src in (lib / "sources").glob("*.py"):
        if src.name.startswith("_") or src.name == "registry.py":
            continue
        names = re.findall(r"""^\s+name\s*(?::\s*[\w\[\]]+)?\s*=\s*["']([a-z_]+)["']""", src.read_text(errors="ignore"), re.M)
        if names:
            cmds[src.stem] = set(names)
    # RL World libraries define the shared view commands (get_metadata, get_outline, find_text, ...) once in
    # sources/reading.py; each format module that imports them offers them too.
    _add_shared(lib, cmds, as_list=False)
    return cmds


def golden_dir(task):
    """The solution/ folder solve.sh copies from; else the first of GOLDEN_DIRS that exists; else None."""
    sol = task / "solution"
    sh = sol / "solve.sh"
    if sh.is_file():
        text = sh.read_text(encoding="utf-8", errors="replace")
        for name in GOLDEN_DIRS:
            if re.search(rf"(?<![\w-]){re.escape(name)}(?=[/\"'.\s]|$)", text) and (sol / name).is_dir():
                return sol / name
    return next((sol / n for n in GOLDEN_DIRS if (sol / n).is_dir()), None)


def verifier_timeout(task):
    toml = task / "task.toml"
    if not toml.is_file():
        return None
    m = re.search(r"^\[verifier\][^\[]*?^\s*timeout_sec\s*=\s*([\d.]+)", toml.read_text(errors="ignore"), re.M | re.S)
    return float(m.group(1)) if m else None


def schema_check(lib, spec_text):
    """Validate with the task's own VerifierSpec. Returns (ran, error or None)."""
    if not lib:
        return False, "bundled verifier library not found under tests/"
    try:
        import jsonpath_ng.ext  # noqa: F401  (the library validates JSONPath syntax with it)
    except ImportError:
        # Without jsonpath_ng the library would reject every JSONPath. Stub the parser so the rest of the schema is
        # still checked, and say that JSONPath syntax was not.
        root, ext = types.ModuleType("jsonpath_ng"), types.ModuleType("jsonpath_ng.ext")
        root.parse = ext.parse = lambda s: s
        root.ext = ext
        sys.modules["jsonpath_ng"], sys.modules["jsonpath_ng.ext"] = root, ext
        print("NOTE: jsonpath_ng is not installed, so JSONPath syntax in deterministic checks was not validated (pip install jsonpath-ng)")
    # Import models.py as a submodule of a stand-in package, so its relative imports resolve without running the
    # library's __init__.py (which pulls in the runner, the judge and every extractor's dependencies).
    pkg_name = "_task_verifier_lib"
    pkg = types.ModuleType(pkg_name)
    pkg.__path__ = [str(lib)]
    sys.modules[pkg_name] = pkg
    try:
        mod = importlib.import_module(pkg_name + ".models")
    except Exception as exc:
        return False, f"could not load {lib}/models.py ({type(exc).__name__}: {exc}); is pydantic installed?"
    model = getattr(mod, "VerifierSpec", None)
    if model is None:
        return False, f"{lib}/models.py has no VerifierSpec"
    try:
        model.model_validate_json(spec_text) if hasattr(model, "model_validate_json") else model.parse_raw(spec_text)
        return True, None
    except Exception as exc:
        return True, str(exc)[:1500]


def paths_read(v):
    f = (v.get("source") or {}).get("file") or {}
    args = f.get("arguments") or {}
    out = []
    for val in args.values():
        if isinstance(val, str) and re.match(r"^(output|data)/", val):
            out.append(val)
        elif isinstance(val, list):
            out += [x for x in val if isinstance(x, str) and re.match(r"^(output|data)/", x)]
    return out


def weight_problems(vs, old_vs):
    """The library's weight rule (models.validate_weight_distribution), with a 1e-6 tolerance."""
    out = []
    weights = [(v.get("name"), (v.get("metadata") or {}).get("weight")) for v in vs]
    bad = [n for n, w in weights if w is not None and (not isinstance(w, (int, float)) or isinstance(w, bool) or not 0 < w <= 1)]
    if bad:
        out.append(f"weight not a number in (0, 1]: {bad}")
    explicit = [w for _, w in weights if isinstance(w, (int, float)) and not isinstance(w, bool)]
    unweighted = [n for n, w in weights if w is None]
    total = sum(explicit)
    if unweighted and all((o.get("metadata") or {}).get("weight") is not None for o in old_vs):
        out.append(f"weight missing on {unweighted} (every original verifier carries one)")
    if explicit and total > 1 + 1e-6:
        out.append(f"weights sum to {total:.8f}, more than 1")
    elif explicit and not unweighted and abs(total - 1) > 1e-6:
        out.append(f"weights sum to {total:.8f}, not 1")
    elif unweighted and explicit and total >= 1 - 1e-9:
        out.append(f"weights already sum to {total:.8f}, leaving nothing for unweighted {unweighted}")
    return out, total


def mean_weight(vs, role):
    ws = [(v.get("metadata") or {}).get("weight") for v in vs if (v.get("metadata") or {}).get("grading_role") == role]
    ws = [w for w in ws if isinstance(w, (int, float))]
    return sum(ws) / len(ws) if ws else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("original", type=Path)
    ap.add_argument("edited", type=Path, nargs="?")
    ap.add_argument("--verifier", type=Path, help="an edited verifier.json, when you did not copy the whole task")
    ap.add_argument("--allow-config-change", action="store_true")
    ap.add_argument("--kept-how", type=Path, nargs="*", default=[],
                    help="edits_rN.json files (apply_verifier_fix.py): their keep_how reasons turn the stale-justification "
                         "warning for those verifiers into a note")
    a = ap.parse_args()
    kept_how = kept_how_map(a.kept_how)
    orig = a.original.resolve()
    if (orig / "task_files").is_dir():
        orig = orig / "task_files"
    ov = orig / "tests" / "verifier.json"
    if not ov.is_file():
        sys.exit(f"{ov} not found: this skill works on tasks graded by tests/verifier.json only")
    problems, warnings, notes = [], [], []

    if a.edited:
        ed = a.edited.resolve()
        if (ed / "task_files").is_dir():
            ed = ed / "task_files"
        nv = ed / "tests" / "verifier.json"
        fo, fe = files_of(orig), files_of(ed)
        for rel in sorted(set(fo) | set(fe)):
            if rel == "tests/verifier.json":
                continue
            if rel not in fe:
                problems.append(f"file removed: {rel}")
            elif rel not in fo:
                problems.append(f"file added: {rel}")
            elif fo[rel] != fe[rel]:
                problems.append(f"file changed: {rel} (only tests/verifier.json may change)")
    elif a.verifier:
        nv = a.verifier.resolve()
        notes.append("whole-folder compare skipped (--verifier given): check by hand that no other file was touched")
    else:
        sys.exit("give the edited task folder, or --verifier <edited verifier.json>")

    text = nv.read_text(encoding="utf-8")
    try:
        new = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"PROBLEM: verifier.json does not parse: {exc}")
        print("VERIFIER CHECK: FAIL (1 problem)")
        sys.exit(1)
    old = json.loads(ov.read_text(encoding="utf-8"))
    old_vs = old.get("verifiers") or []
    vs = new.get("verifiers") or []

    lib = lib_dir(orig / "tests")
    if lib:
        notes.append(f"verifier library: {lib.relative_to(orig).as_posix()}")
    ran, err = schema_check(lib, text)
    if ran and err:
        problems.append(f"the task's own verifier library rejects the file: {err}")
    elif not ran:
        problems.append(f"schema not checked: {err}. Find the library by hand and validate the file with its VerifierSpec")

    names = [v.get("name") for v in vs]
    dup = sorted({n for n in names if names.count(n) > 1})
    if dup:
        problems.append(f"duplicate verifier names: {dup}")
    wp, total = weight_problems(vs, old_vs)
    problems += wp

    cmds = lib_commands(lib)
    if lib and not cmds:
        warnings.append(f"no command names could be read from {lib.name}/sources/: check every source command by hand")
    gdir = golden_dir(orig)
    if gdir is None:
        problems.append("no golden folder found (solution/golden_outputs, output, files or golden): output/ paths not checked")
        golden = set()
    else:
        notes.append(f"golden folder: {gdir.relative_to(orig).as_posix()} (the one solve.sh copies from)")
        golden = {re.sub(r"^(workspace/)?output/", "", p.relative_to(gdir).as_posix()) for p in gdir.rglob("*") if p.is_file()}
    data = orig / "environment" / "data"
    om = {v["name"]: v for v in old_vs if "name" in v}
    for v in vs:
        n = v.get("name")
        f = (v.get("source") or {}).get("file") or {}
        if cmds and f:
            if f.get("command") not in cmds.get(f.get("type"), set()):
                problems.append(f"{n}: command {f.get('type')}.{f.get('command')} is not in the bundled library")
        for p in paths_read(v):
            if p.startswith("output/") and gdir is not None and p[len("output/"):] not in golden:
                problems.append(f"{n}: reads {p}, which the golden answer does not produce")
            if p.startswith("data/") and data.is_dir() and not (data / p[len("data/"):]).exists():
                problems.append(f"{n}: reads {p}, which is not in environment/data")
        asr = v.get("assertion") or {}
        md = v.get("metadata") or {}
        if asr.get("type") == "rubric":
            if not (asr.get("rubric") or {}).get("prompt", "").strip():
                problems.append(f"{n}: rubric verifier with an empty prompt")
            if asr.get("expected") is not True:
                problems.append(f"{n}: rubric verifier whose expected is not true")
        for key in ("importance", "grading_role"):
            if key not in md and any(key in (o.get("metadata") or {}) for o in old_vs):
                problems.append(f"{n}: metadata.{key} missing (the original verifiers carry it)")

        # Absence-only credit is checked on every verifier, touched or not: reviews rarely raise it, and the empty-answer
        # run fails it only when the file is missing, not when an empty file exists.
        judge_prompt = ((asr.get(asr.get("type")) or {}) if asr.get("type") in ("rubric", "agentic") else {}).get("prompt") or ""
        if ABSENCE_ONLY.search(judge_prompt) and not PRESENCE_GATE.search(judge_prompt):
            warnings.append(f"{n}: PASS rests on absence ({ABSENCE_ONLY.search(judge_prompt).group(0)!r}) with no presence gate; "
                            "an empty or placeholder deliverable would pass. Add 'FAIL if <deliverable> is missing, empty, "
                            "a placeholder, or contains no substantive <content>'")

        # Warnings apply only to what this edit touched.
        o = om.get(n)
        if o == v:
            continue
        omd = (o or {}).get("metadata") or {}
        if o and (o.get("source") != v.get("source") or o.get("assertion") != v.get("assertion")):
            if md.get("how_justification") == omd.get("how_justification"):
                if n in kept_how:
                    notes.append(f"{n}: how_justification kept on purpose: {kept_how[n]}")
                else:
                    warnings.append(f"{n}: grading changed but how_justification did not; make it describe what the verifier now does")
        prompt = (asr.get("rubric") or {}).get("prompt") or ""
        if POINTS_AWAY.search(prompt):
            warnings.append(f"{n}: prompt says {POINTS_AWAY.search(prompt).group(0)!r}; the judge sees only the source text and this prompt, so inline the values")
        if f.get("command") == "extract_many":
            ps = (f.get("arguments") or {}).get("paths") or []
            first_out = next((i for i, p in enumerate(ps) if str(p).startswith("output/")), None)
            if first_out not in (None, 0):
                warnings.append(f"{n}: extract_many lists {ps[0]} before the deliverable; put the deliverable first and name each file in the prompt")
            if ps and EXTRACT_BUDGET // len(ps) < 20000:
                warnings.append(f"{n}: extract_many over {len(ps)} files leaves each about {EXTRACT_BUDGET // len(ps):,} characters of a shared {EXTRACT_BUDGET:,}; keep only the sources the criterion needs")
        new_args = (f.get("arguments") or {})
        old_args = (((o or {}).get("source") or {}).get("file") or {}).get("arguments") or {}
        sheet_keys = ("sheet", "sheet_name", "sheet_names")
        for key in sheet_keys + ("cell_range", "range"):
            if key in new_args and new_args.get(key) != old_args.get(key):
                if key == "range" and not any(k in new_args for k in sheet_keys) and wide_range(new_args[key]):
                    # a range with no sheet limits the extract on every sheet (the budget fix of #40), it pins no
                    # place; its risk is size, so it is a note, not a warning (22 warnings in #40 round 4)
                    notes.append(f"{n}: range={new_args[key]!r} on every sheet limits the extract; size it on the golden "
                                 f"and every solver workbook (xlsx_ranges.py)")
                else:
                    warnings.append(f"{n}: new {key}={new_args[key]!r} pins a layout; confirm the instruction fixes "
                                    f"that sheet or range")

    if new.get("config") != old.get("config") and not a.allow_config_change:
        problems.append(f"config changed: {old.get('config')} -> {new.get('config')} (the judge config is platform-owned; "
                        "the one sanctioned change is the opt-in Gemini replacement, qc.py judgefix, never a hand edit)")
    for k in set(old) | set(new):
        if k not in ("verifiers", "config") and old.get(k) != new.get(k):
            problems.append(f"top-level field {k!r} changed")

    models = ((new.get("config") or {}).get("models")) or []
    if any(str(m).startswith("gemini/") for m in models):
        warnings.append("config.models has a gemini/ judge, which fails on DataOS, so the other two must agree and any split "
                        "fails. That is a setup problem, not a verifier defect: do not count its failures against criteria")
    lo, hi = COUNT_RANGE
    if len(vs) != len(old_vs) and not lo <= len(vs) <= hi:
        warnings.append(f"{len(old_vs)} -> {len(vs)} verifiers, outside {lo} to {hi}; QC and RL World count gates flag this")
    # rubric and agentic verifiers are both judge calls; deterministic ones are not
    n_rubric = lambda xs: sum(1 for v in xs if (v.get("assertion") or {}).get("type") in ("rubric", "agentic"))
    timeout = verifier_timeout(orig)
    judges = max(1, len(models))
    est_new = n_rubric(vs) * judges * SECONDS_PER_JUDGE_CALL
    est_old = n_rubric(old_vs) * judges * SECONDS_PER_JUDGE_CALL
    if timeout and est_new > est_old and est_new * MIN_HEADROOM > timeout:
        warnings.append(f"about {est_new:.0f} s of serial judging ({n_rubric(vs)} rubric/agentic verifiers x {judges} judges x "
                        f"{SECONDS_PER_JUDGE_CALL:g} s) against [verifier] timeout_sec {timeout:g}, under {MIN_HEADROOM}x headroom. "
                        "A timed-out run gets no reward: avoid adding verifiers")
    n_det = lambda xs: sum(1 for v in xs if (v.get("assertion") or {}).get("type") == "deterministic")
    if n_det(old_vs) and not n_det(vs):
        warnings.append("the last deterministic verifier was removed; the EKW/DataOS Harbor gate wants at least one")
    mo, mp = mean_weight(vs, "outcome"), mean_weight(vs, "process")
    if mo is not None and mp is not None and mo < mp:
        warnings.append(f"outcome verifiers' mean weight {mo:.4f} is below process verifiers' {mp:.4f}")
    if (orig / "tests" / "verifier-plan.md").is_file() and new.get("verifiers") != old.get("verifiers"):
        warnings.append("tests/verifier-plan.md describes the old verifiers; list it under 'Not fixed here' (not this skill's to edit)")

    nm = {v["name"]: v for v in vs if "name" in v}
    print("## Changes")
    for n in sorted(set(nm) - set(om)):
        print(f"+ added {n} (w {(nm[n].get('metadata') or {}).get('weight')})")
    for n in sorted(set(om) - set(nm)):
        print(f"- removed {n} (w {(om[n].get('metadata') or {}).get('weight')})")
    for n in om:
        if n in nm and om[n] != nm[n]:
            parts = [k for k in ("metadata", "source", "assertion") if om[n].get(k) != nm[n].get(k)]
            ow, nw = (om[n].get("metadata") or {}).get("weight"), (nm[n].get("metadata") or {}).get("weight")
            print(f"~ {n}: {', '.join(parts)} changed" + (f"; weight {ow} -> {nw}" if ow != nw else ""))
    print(f"verifiers {len(om)} -> {len(nm)}; weight sum {total:.6f}")
    if timeout:
        print(f"serial judging estimate {est_old:.0f} s -> {est_new:.0f} s (timeout_sec {timeout:g})")
    for x in notes:
        print(f"NOTE: {x}")
    for x in warnings:
        print(f"WARNING: {x}")
    for x in problems:
        print(f"PROBLEM: {x}")
    if problems:
        print(f"VERIFIER CHECK: FAIL ({len(problems)} problem{'s' if len(problems) != 1 else ''})")
        sys.exit(1)
    print("VERIFIER CHECK: PASS" + (f" ({len(warnings)} warning{'s' if len(warnings) != 1 else ''} to answer in the report)" if warnings else ""))


if __name__ == "__main__":
    main()
