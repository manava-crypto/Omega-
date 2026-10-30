---
description: Run Project Omega Sample Calibration — grade attempts against verifiers, then reconcile with the judge
argument-hint: "[path to attempts, verifiers and judge verdicts]"
---

Run **Sample Calibration** on: $ARGUMENTS

Delegate to the `project-omega-finance-review` agent via the Agent tool. Brief it to:

- Read `skills/project-omega-finance-review/SKILL.md` and, in `references/`, `07_failure_patterns_and_lessons.md`, `09_platform_checks_and_auto_qc.md` where judge checks or Auto QC are in play, `08_excel_verifier_scoping.md` for any workbook verifier, and template E of `06_output_templates.md` before any verdict.
- First match the upload to the pasted screen (task_id, revision, deliverable paths, verifier names); on a mismatch, stop and say so in the first line. If only verifier names are pasted, mark every field PENDING INPUT; never grade from a name.
- Answer in the platform's order for each verifier, never as a free-form report: grade every attempt PASS or FAIL yourself before reading the judge, then resolve each disagreement by agreeing with the judge or standing by your grade with one or two sentences of evidence. A model false-fail shows unfairness only when the requirement is not a reasonable reading of the prompt.
- Answer the five required questions with the platform's options, knowing their regeneration effect: "Not required anywhere — unfair to verify" deletes the check (use it for existence-only and cross-file checks the platform pushes); "No, several things" splits it into one check per concept listed, so split by concept, never by detail; "No, it's vague" rewords it in place, with the PASS and FAIL rule spelled out both ways; "missing information" names the exact facts or values to inline; Critical or Nice to have only sets the weight.
- Add a coverage gap only for a real obligation, with the exact wording, source, target artifact and PASS/FAIL conditions; mark redundancy only when two checks grade the same concept on the same artifact, choosing the one to keep. Run the probe battery before marking any check vague, split or redundant, and flag a defect only with a one-sentence counterexample, "A submission that … would FAIL/PASS because …".
- If the golden fails a verifier, decide which is wrong: rework a flawed verifier and leave the golden alone; fix the golden against a sound verifier, never by weakening the verifier, describe the change under "Fixed in updated Golden" and attach the updated golden; leave the golden alone where the verifier carries a being-updated note.
- After regeneration, re-review every NEW, CHANGED and GRADE CHANGED check.
- Return entries inline under C1–C8 in SKILL.md: one paragraph per note and two at most, plain words with no file internals or tool names, no cross-references, no tables.

Re-verify every finding that drives a delete, split, vague or redundancy mark, check the entries one-to-one against the form, and relay them verbatim without stripping fixes or adding anything beyond the C1 lead.
