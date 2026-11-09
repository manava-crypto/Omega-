"""trainer_upload.py: build and check the zip a trainer uploads with RL World's "Upload Updated Task".

The uploader refuses three things (2026-11-02, migy, p8f6vjxz-0, p8f6vjxz-1; 2026-11-04, 083828):
  1. a wrapped zip ("Non-Harbor ZIP path: <folder>/instruction.md"): files must sit at the zip root;
  2. a task.toml that is not the task's own. Every RL World download appends the [verifier.env] table the platform
     serves as the file's last table; the uploader refuses it ("task.toml has a [verifier.env] table the platform
     manages. Delete the table and upload again": 2026-11-02, and vwr1nerq-2 v16 on 2026-11-04 with the download's
     table byte for byte). Any other change is refused too ("changes task.toml, which belongs to Task Design and is
     immutable": 083828 v19 on 2026-11-04, whose [verifier.env] sits mid-file, before [agent], as part of the task's
     own task.toml, and had been deleted). So only a trailing [verifier.env] table is deleted; a mid-file one stays;
  3. "changes the task beyond a fix": any change the RL World feedback for that version does not ask for, such as
     agent timeout 600 -> 14400 (our DataOS-run setting) or a verifier the feedback never names;
  4. no export manifest ("The ZIP doesn't match the task's download, or its files don't validate" / "Export manifest is
     missing - cannot verify corrected upload", p8f6vjxz-0 v8, 2026-11-04): the original task files must be an RL World
     download carrying .external-qc-manifest.json, which the zip keeps byte for byte; check validates the files against
     its expectedPaths, hashes and allowedMutablePaths. DataOS-run task_files lack it, so they can't be the original.

So the upload copy is RL World's original task files with exactly two changes:
  - task.toml: the platform's trailing [verifier.env] table removed, nothing else (agent timeout stays as RL World has
    it, and a [verifier.env] table that is not the last table is kept);
  - tests/verifier.json: only the verifiers named in the version's -external-qc-feedback.json take the fixed text;
    every other verifier keeps RL World's original text, weight and position.

  build <original task_files dir> <fixed verifier.json or zip holding it> <feedback.json> <out.zip>
  check <upload.zip> <original task_files dir> <feedback.json>      (exit 1 on any FAIL)
"""
import hashlib
import io
import json
import math
import os
import re
import sys
import zipfile

ROOT = {"environment", "instruction.md", "solution", "task.toml", "tests"}
VJ = "tests/verifier.json"
# RL World's export record (exportId, per-file SHA-256, sizes, generations, allowedMutablePaths). The uploader refuses a
# zip without it ("Export manifest is missing - cannot verify corrected upload", p8f6vjxz-0 v8, 2026-11-04). Only an
# RL World download carries it; it is copied byte for byte and never written here.
MANIFEST = ".external-qc-manifest.json"


def read_tree(d):
    out = {}
    for root, _, files in os.walk(d):
        for f in files:
            p = os.path.join(root, f)
            out[os.path.relpath(p, d).replace("\\", "/")] = open(p, "rb").read()
    return out


def platform_env_removed(text):
    """task.toml less the [verifier.env] table RL World appends to downloads: removed only when it is the last table
    (with the blank lines before it); a [verifier.env] table followed by other tables is the task's own and stays."""
    lines = text.splitlines(True)
    heads = [i for i, ln in enumerate(lines) if ln.strip().startswith("[") and ln.strip().endswith("]")]
    if not heads or lines[heads[-1]].strip() != "[verifier.env]":
        return text
    out = lines[:heads[-1]]
    while out and not out[-1].strip():
        out.pop()
    res = "".join(out)
    if text.endswith("\n") and not res.endswith("\n"):
        res += "\n"
    return res


def agent_timeout(text):
    m = re.search(r"^\[agent\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
    t = m and re.search(r"^timeout_sec\s*=\s*(\S+)", m.group(1), re.M)
    return t.group(1) if t else None


def named_in(feedback_text, name):
    return re.search(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])", feedback_text) is not None


def scope_text(fb_path):
    """What the feedback asks to change: each item's criteria at risk, plus any verifier its remediation names.
    A verifier mentioned only as evidence in an explanation is out of scope (jicq4o2h-1-v29, 2026-11-03: the build had
    kept a loosened latency_clock_corrected_reconstruction that no item lists as at risk)."""
    d = json.load(open(fb_path, encoding="utf-8"))
    parts = []
    for f in d["feedback"]:
        m = re.search(r"Criteria at risk \(\d+\):\*\*(.*)", f.get("explanation") or "")
        if m:
            parts += re.findall(r"`([A-Za-z0-9_]+)`", m.group(1))
        last = (f.get("description") or "").split("·")[-1].strip()
        if re.fullmatch(r"[a-z0-9_]+", last):
            parts.append(last)
        parts.append(f.get("remediation") or "")
    return chr(10).join(parts)


def dump_like(obj, original_text):
    """Serialise obj with the formatting that reproduces original_text exactly."""
    orig = json.loads(original_text)
    for indent in (2, 4, "\t", None):
        for nl in ("", "\n"):
            if json.dumps(orig, indent=indent, ensure_ascii=False) + nl == original_text:
                return json.dumps(obj, indent=indent, ensure_ascii=False) + nl
    sys.exit("verifier.json formatting not reproducible by json.dumps; stop and splice by hand")


def weight(v):
    return (v.get("metadata") or {}).get("weight", v.get("weight"))


def set_weight(v, w):
    v = json.loads(json.dumps(v))
    if "weight" in (v.get("metadata") or {}):
        v["metadata"]["weight"] = w
    elif "weight" in v:
        v["weight"] = w
    return v


def scoped_verifier(orig_text, fixed_text, fb_text):
    """Named verifiers take the fixed text at RL World's weight; a deleted named verifier's weight goes to the other
    named verifiers in proportion, so no verifier the feedback does not name changes, not even its weight."""
    orig, fixed = json.loads(orig_text), json.loads(fixed_text)
    fx = {v["name"]: v for v in fixed["verifiers"]}
    out, taken, kept, freed = [], [], [], 0.0
    for v in orig["verifiers"]:
        n = v["name"]
        if named_in(fb_text, n) and fx.get(n) != v:
            if n in fx:
                out.append(set_weight(fx[n], weight(v)) if weight(v) is not None else fx[n])
                taken.append(n)
            else:
                taken.append(n + " (deleted)")
                freed += weight(v) or 0.0
        else:
            out.append(v)
            if fx.get(n) != v:
                kept.append(n)
    if freed:
        pool = [i for i, v in enumerate(out) if named_in(fb_text, v["name"]) and weight(v)]
        if not pool:
            sys.exit("a named verifier was deleted and no other named verifier can take its weight; settle by hand")
        base = sum(weight(out[i]) for i in pool)
        for i in pool:
            out[i] = set_weight(out[i], weight(out[i]) * (1 + freed / base))
        # full precision, then the sum may not exceed RL World's (the library refuses a sum above 1)
        target = sum(weight(v) or 0.0 for v in orig["verifiers"])
        i = max(pool, key=lambda j: weight(out[j]))
        out[i] = set_weight(out[i], weight(out[i]) + target - sum(weight(v) or 0.0 for v in out))
        while sum(weight(v) or 0.0 for v in out) > target:
            out[i] = set_weight(out[i], math.nextafter(weight(out[i]), 0.0))
        taken.append(f"weight {freed:.6f} of deleted verifiers spread over {len(pool)} named verifiers")
    on = {v["name"] for v in orig["verifiers"]}
    added = [n for n in fx if n not in on]
    for n in added:
        if named_in(fb_text, n):
            sys.exit(f"fixed file adds named verifier {n}; place it by hand")
        kept.append(n + " (added in fix, left out)")
    res = dict(orig)
    res["verifiers"] = out
    return res, taken, kept


def build(orig_dir, fixed_src, fb_path, out_zip):
    files = read_tree(orig_dir)
    if fixed_src.lower().endswith(".zip"):
        with zipfile.ZipFile(fixed_src) as z:
            names = [n for n in z.namelist() if n.endswith(VJ)]
            if len(names) != 1:
                sys.exit(f"{fixed_src}: expected one {VJ}, found {names}")
            fixed_text = z.read(names[0]).decode("utf-8")
    else:
        fixed_text = open(fixed_src, encoding="utf-8").read()
    fb_text = scope_text(fb_path)
    orig_text = files[VJ].decode("utf-8")
    obj, taken, kept = scoped_verifier(orig_text, fixed_text, fb_text)
    ws = [weight(v) for v in obj["verifiers"]]
    wo = sum(weight(v) or 0.0 for v in json.loads(orig_text)["verifiers"])
    if all(w is not None for w in ws) and abs(sum(ws) - wo) > 1e-6:
        sys.exit(f"weights sum to {sum(ws)}, RL World's to {wo}; settle by hand")
    files[VJ] = dump_like(obj, orig_text).encode("utf-8")
    files["task.toml"] = platform_env_removed(files["task.toml"].decode("utf-8")).encode("utf-8")
    if MANIFEST not in files:
        print(f"WARNING: {orig_dir} has no {MANIFEST}; RL World refuses the upload. Build from the RL World download "
              "that carries it (check will FAIL)")
    tmp = out_zip + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(files):  # fixed timestamp: the same inputs always give the same md5
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.external_attr = 0o644 << 16
            z.writestr(info, files[name], compress_type=zipfile.ZIP_DEFLATED)
    os.replace(tmp, out_zip)
    print(f"built {os.path.basename(out_zip)}")
    print(f"  fixed verifiers kept (named in feedback): {len(taken)} {taken}")
    print(f"  changes left out (not named in feedback, RL World text restored): {len(kept)} {kept}")
    return taken, kept


def check(zip_path, orig_dir, fb_path):
    fails = []
    files = read_tree(orig_dir)
    fb_text = scope_text(fb_path)
    with zipfile.ZipFile(zip_path) as z:
        if z.testzip() is not None:
            fails.append("zip test failed")
        infos = z.infolist()
        up = {i.filename: z.read(i.filename) for i in infos if not i.filename.endswith("/")}
    roots = {n.split("/")[0] for n in up} - {MANIFEST}
    if roots != ROOT:
        fails.append(f"zip root is {sorted(roots)}, must be exactly {sorted(ROOT)} plus {MANIFEST} (flat, no top folder)")
        if len(roots) == 1:
            up = {n.split("/", 1)[1]: b for n, b in up.items() if "/" in n}
    if any(n.startswith(("/", "\\")) or "\\" in n or ".." in n.split("/") for n in up):
        fails.append("unsafe or backslash paths in zip")
    junk = [n for n in up if "__pycache__" in n or n.endswith((".pyc", ".DS_Store")) or "/__MACOSX" in n]
    if junk:
        fails.append(f"junk files: {junk[:5]}")
    if set(up) != set(files):
        fails.append(f"file list differs from RL World's: only zip {sorted(set(up) - set(files))[:5]}, "
                     f"only original {sorted(set(files) - set(up))[:5]}")
    differ = sorted(n for n in set(up) & set(files) if up[n] != files[n])
    extra = [n for n in differ if n not in ("task.toml", VJ)]
    if extra:
        fails.append(f"files other than task.toml and verifier.json changed: {extra}")
    t_up, t_or = up.get("task.toml", b"").decode("utf-8"), files["task.toml"].decode("utf-8")
    if MANIFEST not in up:
        fails.append(f"{MANIFEST} missing (RL World: 'Export manifest is missing'); the original task files must be an "
                     "RL World download that carries it")
    elif up[MANIFEST] != files.get(MANIFEST):
        fails.append(f"{MANIFEST} differs from the original's: it must be RL World's, byte for byte")
    else:
        m = json.loads(up[MANIFEST])
        paths = {n for n in up if n != MANIFEST}
        if paths != set(m.get("expectedPaths") or []):
            fails.append(f"files differ from the manifest's expectedPaths: only zip {sorted(paths - set(m['expectedPaths']))[:5]}, "
                         f"only manifest {sorted(set(m['expectedPaths']) - paths)[:5]}")
        changed = [n for n in paths if hashlib.sha256(up[n]).hexdigest() != (m.get("hashes") or {}).get(n)]
        frozen = [n for n in changed if n not in set(m.get("allowedMutablePaths") or [])]
        if frozen:
            fails.append(f"changed files the manifest does not allow to change: {frozen}")
    if platform_env_removed(t_up) != t_up:
        fails.append("task.toml still ends with the [verifier.env] table the platform manages")
    if t_up != platform_env_removed(t_or):
        fails.append("task.toml differs from RL World's by more than the platform's trailing [verifier.env] table "
                     "(a mid-file [verifier.env] is the task's own and must stay)")
    if agent_timeout(t_up) != agent_timeout(t_or):
        fails.append(f"agent timeout {agent_timeout(t_up)} != RL World's {agent_timeout(t_or)}")
    vo, vu = json.loads(files[VJ]), json.loads(up[VJ])
    if vo.get("config") != vu.get("config"):
        fails.append("verifier.json config changed")
    if {k for k in vo if k != "verifiers"} != {k for k in vu if k != "verifiers"} or any(
            vo[k] != vu[k] for k in vo if k != "verifiers"):
        fails.append("verifier.json top-level fields other than verifiers changed")
    o = {v["name"]: v for v in vo["verifiers"]}
    u = {v["name"]: v for v in vu["verifiers"]}
    changed = sorted(n for n in set(o) | set(u) if o.get(n) != u.get(n))
    unasked = [n for n in changed if not named_in(fb_text, n)]
    if unasked:
        fails.append(f"verifiers changed that no feedback item lists as at risk or names in its remediation: {unasked}")
    if [v["name"] for v in vo["verifiers"] if v["name"] in u] != [v["name"] for v in vu["verifiers"] if v["name"] in o]:
        fails.append("verifier order changed")
    ws = [weight(v) for v in vu["verifiers"]]
    wo = sum(weight(v) or 0.0 for v in vo["verifiers"])
    if all(w is not None for w in ws) and (abs(sum(ws) - wo) > 1e-6 or sum(ws) > max(wo, 1.0)):
        fails.append(f"weights sum to {sum(ws)!r}, RL World's to {wo!r} (the library refuses a sum above 1)")
    if up[VJ] != files[VJ] and json.dumps(vu, ensure_ascii=False) == json.dumps(vo, ensure_ascii=False):
        fails.append("verifier.json differs only in formatting")
    md5 = hashlib.md5(open(zip_path, "rb").read()).hexdigest()
    print(f"{os.path.basename(zip_path)} | files {len(up)} | md5 {md5}")
    print(f"  changed files: {differ} | changed verifiers (all named in feedback): {changed}")
    for f in fails:
        print("  FAIL:", f)
    print("UPLOAD CHECK:", "FAIL" if fails else "PASS")
    return not fails


if __name__ == "__main__":
    if len(sys.argv) == 6 and sys.argv[1] == "build":
        build(*sys.argv[2:6])
    elif len(sys.argv) == 5 and sys.argv[1] == "check":
        sys.exit(0 if check(*sys.argv[2:5]) else 1)
    else:
        sys.exit(__doc__)
