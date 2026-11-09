"""feedback_resolution_dump.py <original task_files> <upload.zip> <feedback.json>: per feedback item, the remediation and
the upload's text of every criterion it names, flagged when the remediation offers 'add to instruction.md or delete'
but the criterion was kept (reworded), the pattern RL World refused on 6eydtrq9-2-v16 (2026-11-03)."""
import json
import re
import sys
import zipfile

orig, up, fb = sys.argv[1:4]
o = {v["name"]: v for v in json.load(open(orig + "/tests/verifier.json", encoding="utf-8"))["verifiers"]}
u = {v["name"]: v for v in json.loads(zipfile.ZipFile(up).read("tests/verifier.json"))["verifiers"]}
txt = lambda v: (v["assertion"].get("rubric") or v["assertion"].get("agentic"))["prompt"]
for f in json.load(open(fb, encoding="utf-8"))["feedback"]:
    ex = f.get("explanation") or ""
    m = re.search(r"Criteria at risk \(\d+\):\*\*(.*)", ex)
    crit = re.findall(r"`([a-z0-9_]+)`", m.group(1)) if m else []
    if not crit:
        continue
    rem = f.get("remediation") or ""
    offers_delete = bool(re.search(r"\b(delete|drop|remove)\b", rem, re.I))
    print(f"### {f['id']} | {f['category']} | {f['severity']}")
    print("REMEDIATION:", rem)
    why = re.search(r"\*\*Why a correct answer fails:\*\*(.*)", ex, re.S)
    body = ex.split("**Why a correct answer fails:**")[0]
    print("CLAIM:", re.sub(r"\s+", " ", body.split("\n", 3)[-1])[:900])
    for c in crit:
        state = "DELETED" if c not in u else ("UNCHANGED" if u[c] == o.get(c) else "REWORDED")
        flag = "  <<< RISK: remediation offers deletion, criterion kept" if offers_delete and state != "DELETED" else ""
        print(f"  - {c}: {state}{flag}")
        if state != "DELETED":
            print("    UPLOAD TEXT:", re.sub(r"\s+", " ", txt(u[c])))
        if state == "REWORDED" and c in o:
            print("    RL WORLD ORIGINAL TEXT:", re.sub(r"\s+", " ", txt(o[c])))
    print()
