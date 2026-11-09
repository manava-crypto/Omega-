"""DataOS copy of a trainer upload zip, aligned to the task.toml DataOS already ran.

usage: python -I -B -X utf8 aligned_dataos_copy.py <trainer upload zip> <previous DataOS-run zip> <out zip | --check <aligned zip>>

The trainer zip is flat (RL World's new version). The previous DataOS-run zip is wrapped in <root>/. Asserts:
- same file list; every file but tests/verifier.json and task.toml byte-identical;
- task.toml differs only by [agent] timeout_sec 600.0 -> 14400.0 plus added `KEY = "${KEY:-}"` lines / table header;
- [verifier.env] declares a key for every judge provider in config.models.
Writes <root>/<trainer files>, with task.toml taken from the DataOS-run zip. --check compares an existing aligned zip.
"""
import difflib
import hashlib
import json
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")
KEYS = {"xai": "XAI_API_KEY", "gemini": "GEMINI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}


def load(p):
    with zipfile.ZipFile(p) as z:
        d = {n: z.read(n) for n in z.namelist() if not n.endswith("/")}
    roots = {n.split("/")[0] for n in d}
    if "task.toml" not in d and len(roots) == 1:
        root = roots.pop()
        return root, {n[len(root) + 1:]: v for n, v in d.items()}
    return None, d


trainer, prev = sys.argv[1], sys.argv[2]
t_root, t = load(trainer)
p_root, p = load(prev)
assert t_root is None, "trainer zip is not flat"
assert p_root, "DataOS-run zip has no root folder"
assert sorted(t) == sorted(p), (sorted(set(t) ^ set(p)))
diff = sorted(k for k in t if t[k] != p[k])
assert set(diff) <= {"tests/verifier.json", "task.toml"}, diff
tl = t["task.toml"].decode("utf-8").splitlines()
pl = p["task.toml"].decode("utf-8").splitlines()
d = [x for x in difflib.unified_diff(tl, pl, lineterm="", n=0) if x[:1] in "+-" and not x.startswith(("+++", "---"))]
assert d[:2] == ["-timeout_sec = 600.0", "+timeout_sec = 14400.0"], d
for x in d[2:]:
    assert x.startswith("+") and (re.fullmatch(r'\+\w+_API_KEY = "\$\{\w+_API_KEY:-\}"', x) or x in ("+", "+[verifier.env]")), x
models = (json.loads(t["tests/verifier.json"]).get("config") or {}).get("models") or []
declared = set(re.findall(r"^(\w+_API_KEY)\s*=", p["task.toml"].decode("utf-8"), re.M))
need = {KEYS[m.split("/")[0]] for m in models if m.split("/")[0] in KEYS}
assert need <= declared, need - declared
out = {**t, "task.toml": p["task.toml"]}
md5 = lambda b: hashlib.md5(b).hexdigest()[:8]
print(f"root {p_root}; {len(t)} files; differ from DataOS-run zip: {diff}; models {models}")
print(f"verifier.json trainer {md5(t['tests/verifier.json'])} / DataOS-run {md5(p['tests/verifier.json'])}")
print("task.toml diff trainer -> DataOS:", d)

if sys.argv[3] == "--check":
    a_root, a = load(sys.argv[4])
    assert a_root == p_root, (a_root, p_root)
    bad = sorted(set(a) ^ set(out)) + sorted(k for k in set(a) & set(out) if a[k] != out[k])
    print("CHECK:", "IDENTICAL" if not bad else f"DIFFERS {bad}")
    sys.exit(0 if not bad else 1)

dst = sys.argv[3]
assert not os.path.exists(dst), dst
tmp = dst + ".tmp"
with zipfile.ZipFile(trainer) as zt, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
    for info in zt.infolist():
        if info.is_dir():
            continue
        data = out[info.filename]
        ni = zipfile.ZipInfo(p_root + "/" + info.filename, date_time=info.date_time)
        ni.external_attr, ni.compress_type = info.external_attr, zipfile.ZIP_DEFLATED
        zo.writestr(ni, data)
os.replace(tmp, dst)
r_root, r = load(dst)
assert r_root == p_root and r == out
print(f"WROTE {dst} md5 {md5(open(dst, 'rb').read())}; every entry checked")
