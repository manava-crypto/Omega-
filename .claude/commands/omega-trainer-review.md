---
description: Run the Project Omega Trainer Review gate on a task pack and return platform-ready answers
argument-hint: "[path to task pack, or leave blank to use attached/most recent files]"
---

Run **Trainer Review** on the task pack at: $ARGUMENTS

If no path is given, inventory the files attached or most recently referenced and confirm the pack before reviewing.

Delegate to the `project-omega-finance-review` agent via the Agent tool. Brief it to:

- Read `skills/project-omega-finance-review/SKILL.md` and, in `references/`, `07_failure_patterns_and_lessons.md`, `09_platform_checks_and_auto_qc.md`, `08_excel_verifier_scoping.md` for any workbook verifier, and template B of `06_output_templates.md` before any verdict.
- Paste into the brief, verbatim, every judge check's name, Description, Explanation and Remediation from the screen, and the form's field labels. The Description defines what each check tests; overlap and atomicity are answered under the version shown (ledger O# or older).
- First match the upload to the pasted screen (task_id, revision, deliverable paths, verifier names), counting fields and verifiers from the files; on a mismatch, stop and say so in the first line. If verifiers are in play and tests/verifier-plan.md is missing, ask for it and mark structural requests PENDING INPUT.
- Review Task Design → each Source Data file → Prompt → Verifiers → LLM judge checks → Escalations and fix every finding in one pass. Judge Task Design on its own terms, never against verifier scope.
- First review: sweep every file with the round-one lenses and run the transcription, restating, labelling and planned-difficulty tests; at Trainer Review every undeclared source error is fixed or declared, and every defect a source check could fail is a required edit. Later version: before judging, diff every file (verifier.json config and task_design.json included), re-run every source check on every changed file in full, mark each prior finding fixed, partially fixed or not fixed, list dropped, renamed or weakened verifiers, and after a second consecutive FAIL classify every new FAIL from the diff.
- Reperform every inlined answer key and run the probe battery on every verifier, Unchanged ones and your own wording included; give every changed wording a ripple list. REJECT a verifier only with a one-sentence counterexample, "A submission that … would FAIL/PASS because …", and name the on-screen check whose Description it breaches; without one, APPROVE. Importance tier is never a reject ground.
- Treat every judge verdict as unverified: recount its counts, treat a partial read as existential evidence only, answer judge text repeated across files on each file's own evidence, AGREE with a FAIL when any cited defect is real in this version, and decide TAKE or REJECT item by item. An AGREE with a FAIL on a verifier goes with a REJECT on that verifier carrying the same Fix.
- End every defect note (REJECT, DISAGREE, or AGREE with a FAIL) with "Fix:" naming the artifact or verifier ID, a quoted locator and the exact change; a finding that belongs elsewhere reads "Fix: No change required to this file for this check; the fix belongs in <file>."
- Answer only the gate pasted, inline under C1–C8 in SKILL.md: one entry per field in screen order (each file's File artifact feedback included), each note naming its platform field, one paragraph per note, two at most, plain words with no file internals or tool names, no cross-references, no tables. Run every note against the Auto QC checks in 09 §4.
- In the report, list every REJECT and DISAGREE with the platform check it breaches and the evidence, so the orchestrator can re-test its classification.

Re-verify every finding that drives a REJECT or DISAGREE, re-testing its classification (planned difficulty, leakage, the bar, the platform check's Description), not only its quoted fact. Check the entries one-to-one against the pasted form, cross-check judge answers against per-item verdicts, and relay verbatim without stripping fixes or adding anything beyond the C1 lead; list any change you made to the agent's verdicts in one lead line.
