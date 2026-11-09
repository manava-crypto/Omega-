"""scope_finalize.py <original verifier.json> <fixed verifier.json> <feedback.json>: rewrite the fixed verifier.json in
place as trainer_upload.py's scoped result (named verifiers take the fixed text, a deleted named verifier's weight goes
to the other named verifiers with trainer_upload's own rounding), so the DataOS-run copy grades byte for byte what the
trainer upload will carry. config comes from the original given here (the DataOS copy keeps the DataOS config).
Prints whether anything changed and every change left out."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trainer_upload as tu  # noqa: E402

orig_path, fixed_path, fb_path = sys.argv[1:4]
orig_text = open(orig_path, encoding="utf-8").read()
fixed_text = open(fixed_path, encoding="utf-8").read()
obj, taken, kept = tu.scoped_verifier(orig_text, fixed_text, tu.scope_text(fb_path))
out = tu.dump_like(obj, orig_text)
changed = out != fixed_text
with open(fixed_path, "w", encoding="utf-8", newline="") as f:
    f.write(out)
print(f"scoped: {len(taken)} named changes kept; left out (not named): {kept}; file rewritten: {changed}")
print(f"weight sum {sum(v['metadata']['weight'] for v in obj['verifiers'])!r}, verifiers {len(obj['verifiers'])}")
