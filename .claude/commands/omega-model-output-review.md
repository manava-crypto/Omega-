---
description: Run the Project Omega Model Output Review gate over every attempt and deliverable
argument-hint: "[path to the attempts/deliverables, or blank to use attached files]"
---

Run **Model Output Review** on: $ARGUMENTS

If no path is given, inventory the attempts and deliverables the user attached or most recently referenced and confirm the set before reviewing.

Delegate to the `project-omega-finance-review` agent via the Agent tool. Brief it to:

- Read `skills/project-omega-finance-review/SKILL.md` and, in `references/`, `07_failure_patterns_and_lessons.md`, `09_platform_checks_and_auto_qc.md` where judge checks or Auto QC are in play, `08_excel_verifier_scoping.md` for any workbook, and template C of `06_output_templates.md` before any verdict.
- First match the upload to the pasted screen (task_id, revision, deliverable paths, verifier names); on a mismatch, stop and say so in the first line. Never take a task ID from an upload's file name, and never assume which model or file a screen shows; ask for any screen not pasted. Mark each question needing a missing file PENDING INPUT, naming the file.
- Review every attempt and every required deliverable in full, not a sample, and recompute the material figures rather than trusting a polished workbook or deck.
- Per output file, answer the six axes in screen order (Instruction-following, Correctness, Completeness, Deliverable / formatting compliance, Hallucination / fabrication, Data integrity); put cross-file points in the five Additional Feedback fields; record each defect once and keep analytical root causes apart from presentation.
- Use only Critical or Nice to have: Critical for any wrong value, fact, formula or check result, an unfollowed instruction, invented support, or missing or broken required content; Nice to have only when every displayed figure is correct and nothing required is missing. Never lower a severity because the conclusion holds or the convention is disclosed, make each entry's wording match its label (Auto QC "Severity Calibrated"), and after any severity change give a per-field list of the labels.
- Treat a model failing a verifier as evidence about the model unless the requirement is not a reasonable reading of the prompt; only then route it to the Verifier layer, with the counterexample "A submission that … would FAIL/PASS because …".
- End every defect entry with "Fix:" naming the deliverable, a quoted locator (sheet and cell, slide, quoted sentence) and the exact correction.
- Return entries inline under C1–C8 in SKILL.md: one entry per field in screen order, one paragraph per entry and two at most, plain words with no file internals or tool names, no cross-references, no tables.

Check the entries one-to-one against the form and relay them verbatim without stripping fixes or adding anything beyond the C1 lead.
