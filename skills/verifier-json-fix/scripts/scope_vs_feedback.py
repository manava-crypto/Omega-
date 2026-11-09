"""scope_vs_feedback.py <original verifier.json> <fixed verifier.json> <feedback.json>: list changed verifiers and whether the feedback names each."""
import json
import sys

orig, fixed, fb = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:4])
o = {v["name"]: v for v in orig["verifiers"]}
f = {v["name"]: v for v in fixed["verifiers"]}
named = json.dumps(fb)
changed = sorted(n for n in set(o) | set(f) if o.get(n) != f.get(n))
print("feedback items:", len(fb.get("feedback", [])), "| changed verifiers:", len(changed))
for n in changed:
    state = "removed" if n not in f else "added" if n not in o else "changed"
    print(f"  {'IN FEEDBACK ' if n in named else 'NOT IN FEEDBACK'} {state:8} {n}")
print("config changed:", orig.get("config") != fixed.get("config"))
