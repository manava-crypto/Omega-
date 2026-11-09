"""upload_fix.py <source zip or verifier.json> <edits.json> <out verifier.json>: apply exact text edits to the verifier.json
a trainer upload is built from, then rebuild with trainer_upload.py build.

edits.json: {"edit": [{"name": ..., "field": "prompt" | "how_justification" | "why_justification", "old": ..., "new": ...}],
             "append": [{"name": ..., "text": ...}],      # appended to the prompt after one space
             "delete": [name, ...]}
Every "old" must occur exactly once in its field, so a stale edit fails loudly instead of doing nothing."""
import json
import sys
import zipfile

src, edits_path, out = sys.argv[1:4]
if src.lower().endswith(".zip"):
    with zipfile.ZipFile(src) as z:
        names = [n for n in z.namelist() if n.endswith("tests/verifier.json")]
        data = json.loads(z.read(names[0]))
else:
    data = json.load(open(src, encoding="utf-8"))
edits = json.load(open(edits_path, encoding="utf-8"))
by = {v["name"]: v for v in data["verifiers"]}


def body(v):
    a = v["assertion"]
    return a["rubric"] if a["type"] == "rubric" else a["agentic"]


for e in edits.get("edit", []):
    v = by[e["name"]]
    holder, key = (body(v), "prompt") if e["field"] == "prompt" else (v["metadata"], e["field"])
    if holder[key].count(e["old"]) != 1:
        sys.exit(f"{e['name']}.{e['field']}: old text found {holder[key].count(e['old'])} times, expected 1")
    holder[key] = holder[key].replace(e["old"], e["new"])
    print(f"edited {e['name']}.{e['field']}")
for e in edits.get("append", []):
    b = body(by[e["name"]])
    if e["text"] in b["prompt"]:
        sys.exit(f"{e['name']}: text already present")
    b["prompt"] = b["prompt"].rstrip() + " " + e["text"]
    print(f"appended to {e['name']}.prompt")
for n in edits.get("delete", []):
    if n not in by:
        sys.exit(f"{n}: not found")
    data["verifiers"] = [v for v in data["verifiers"] if v["name"] != n]
    print(f"deleted {n}")
open(out, "w", encoding="utf-8").write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
