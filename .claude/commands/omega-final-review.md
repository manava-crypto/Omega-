---
description: Run an independent Project Omega Final Review audit of the latest package
argument-hint: "[path to the latest package and current QC evidence]"
---

Run **Final Review** on: $ARGUMENTS

Delegate to the `project-omega-finance-review` agent via the Agent tool, quoting this bar in the brief:

> A verifier rejection ends the task, so set the bar once and block only when: (a) the rubric misstates a governing term; (b) a realistic submission is mis-graded, shown on a supplied output or on a concrete submission under an accepted reading; (c) the golden fails a sound verifier, once you have decided which side is wrong. Everything else gets an optional line: stale figures that change no result, hypothetical overlap or bundling, reasonable placement or format readings, extractor observability (NOT VERIFIABLE plus escalation), weight or difficulty labels, mechanical source slips, and planned difficulty.

Instruct it to:

- Read `skills/project-omega-finance-review/SKILL.md` and, in `references/`, `07_failure_patterns_and_lessons.md`, `09_platform_checks_and_auto_qc.md`, `08_excel_verifier_scoping.md` for any workbook verifier, and template F of `06_output_templates.md`. Match the upload to the pasted screen first; on a mismatch, stop and say so in the first line. If the prior review notes are not supplied, say the fix list is inferred and name the missing file.
- The judge checks on the Final Review screen are display-only: answer the ship-ready Approve/Reject fields. Notes cite only what the gate shows (instruction, sources, verifier.json, golden); use model outputs privately as the test bed and write each counterexample as a fully described submission or a stated edit to the golden.
- Re-verify every claimed fix, then judge in order: Task Design, on its own terms and never against verifier scope (never frame a Task Design question in terms of what the verifiers grade); Source Documents, through the planned-difficulty test, cover and notes sheets and prompt caveats read first; each verifier; Golden, APPROVE if it passes every verifier and recomputes from source (say if cached values replaced recalculation); a golden passing a verifier you reject means the flaw is in grading other submissions.
- State in each verifier REJECT the concrete mis-grade or misstated governing term as "A submission that … would FAIL/PASS because …", and end the note with "Fix:". A requirement the prompt never asks for (a literal figure, label, closed list or fixed placement) or a single accepted reading where the prompt and sources allow another is a mis-grade under (b), not an optional placement reading; grade the golden literally against every FAIL clause and test each pass case against the governing standard. Approval sends the task to External QC, where only verifier.json can change, so the task must be final before it is approved.
- Under C1–C8 in SKILL.md, give one short paragraph each for Task Design, Source Documents and Golden, then one line per verifier, notes under REJECTs only. Close with "Overall REJECT, because one verifier rejection ends the task: <names>." or "Overall APPROVE." If a REJECT rests on a branch no submission took, say so and keep it.
- TAKE or REJECT each QC or judge finding item by item; recommend override only once corrections leave a stale or platform-limit failure. Before submitting, run every note against the five Final Review Auto QC checks in 09 §4 (cross-item consistency, groundedness, actionability, coverage completeness, decision/note coherence).

Quote the bar in every brief and pass every finding through it; label any defect hunt in the brief optional unless it shows a mis-grade. Re-verify each finding that drives a REJECT by re-running its classification (planned difficulty, leakage, the bar), not only its quoted fact, check the entries one-to-one against the form and relay them verbatim, without stripping fixes or adding anything beyond the C1 lead. If challenged, re-test each item against the same bar; a changed verdict states "changed because <new evidence>".
