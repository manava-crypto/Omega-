---
description: Run an independent Project Omega Final Review audit of the latest package
argument-hint: "[path to the latest package and current QC evidence]"
---

Run **Final Review** on: $ARGUMENTS

Delegate to the `project-omega-finance-review` agent via the Agent tool, quoting this bar in the brief:

> A verifier rejection ends the task, so set the bar once and block only when: (a) the rubric misstates a governing term; (b) a realistic submission is mis-graded, shown on a supplied output or on a concrete submission under an accepted reading; (c) the golden fails a sound verifier, once you have decided which side is wrong. Everything else gets an optional line: stale figures that change no result, hypothetical overlap or bundling, reasonable placement or format readings, extractor observability (NOT VERIFIABLE plus escalation), weight or difficulty labels, mechanical source slips, and planned difficulty.

Instruct it to:

- Read `skills/project-omega-finance-review/SKILL.md` and, in `references/`, `07_failure_patterns_and_lessons.md`, `08_excel_verifier_scoping.md` for any workbook verifier, and template F of `06_output_templates.md`. Match the upload to the pasted screen first; on a mismatch, stop and say so in the first line.
- Re-verify every claimed fix, then judge in order: Task Design, on its own terms and never against verifier scope; Source Documents, through the planned-difficulty test, cover and notes sheets and prompt caveats read first; each verifier; Golden, APPROVE if it passes every verifier and recomputes from source (say if cached values replaced recalculation); a golden passing a verifier you reject means the flaw is in grading other submissions.
- State in each verifier REJECT the concrete mis-grade or misstated governing term as "A submission that … would FAIL/PASS because …", and end the note with "Fix:".
- Under C1–C8 in SKILL.md, give one short paragraph each for Task Design, Source Documents and Golden, then one line per verifier, notes under REJECTs only. Close with "Overall REJECT, because one verifier rejection ends the task: <names>." or "Overall APPROVE." If a REJECT rests on a branch no submission took, say so and keep it.
- TAKE or REJECT each QC or judge finding item by item; recommend override only once corrections leave a stale or platform-limit failure.

Quote the bar in every brief and pass every finding through it. Re-verify each finding that drives a REJECT, check the entries one-to-one against the form and relay them verbatim, without stripping fixes or adding anything beyond the C1 lead. If challenged, re-test each item against the same bar; a changed verdict states "changed because <new evidence>".
