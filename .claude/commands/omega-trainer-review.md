---
description: Run the Project Omega Trainer Review gate on a task pack and return platform-ready answers
argument-hint: "[path to task pack, or leave blank to use attached/most recent files]"
---

Run **Trainer Review** on the task pack at: $ARGUMENTS

If no path is given, inventory the files attached or most recently referenced and confirm the pack before reviewing.

Delegate to the `project-omega-finance-review` agent via the Agent tool. Brief it to:

- Read `skills/project-omega-finance-review/SKILL.md` and, in `references/`, `07_failure_patterns_and_lessons.md`, `08_excel_verifier_scoping.md` for any workbook verifier, and template B of `06_output_templates.md` before any verdict.
- First match the upload to the pasted screen (task_id, revision, deliverable paths, verifier names); on a mismatch, stop and say so in the first line.
- Review Task Design → each Source Data file → Prompt → Verifiers → LLM judge checks → Escalations and fix every finding in one pass. Judge Task Design on its own terms, never against verifier scope.
- First review: sweep every file and run the transcription, labelling and planned-difficulty tests. Later version: before judging, diff every file (verifier.json config and task_design.json included), mark each prior finding fixed, partially fixed or not fixed, and list dropped, renamed or weakened verifiers.
- Reperform every inlined answer key and run the probe battery on every verifier, Unchanged ones and your own wording included; give every changed wording a ripple list. REJECT a verifier only with a one-sentence counterexample, "A submission that … would FAIL/PASS because …"; without one, APPROVE.
- Treat every judge verdict as unverified: recount its counts, treat a partial read as existential evidence only, answer judge text repeated across files on each file's own evidence, and decide TAKE or REJECT item by item.
- End every defect note (REJECT, DISAGREE, or AGREE with a FAIL) with "Fix:" naming the artifact or verifier ID, a quoted locator and the exact change; a finding that belongs elsewhere reads "Fix: No change required to this file for this check; the fix belongs in <file>."
- Answer only the gate pasted, inline under C1–C8 in SKILL.md: one entry per field in screen order, one paragraph per note, two at most, no cross-references, no tables.

Re-verify every finding that drives a REJECT or DISAGREE, check the entries one-to-one against the pasted form, and relay them verbatim without stripping fixes or adding anything beyond the C1 lead.
