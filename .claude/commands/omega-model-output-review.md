---
description: Run the Project Omega Model Output Review gate over every attempt and deliverable
argument-hint: "[path to the attempts/deliverables, or blank to use attached files]"
---

Run **Model Output Review** on: $ARGUMENTS

If no path is given, inventory the attempts and deliverables the user attached or most recently referenced and confirm the set before reviewing.

Delegate to the `project-omega-finance-review` agent via the Agent tool. Brief it to:

- Read `skills/project-omega-finance-review/SKILL.md` and, in `references/`, `07_failure_patterns_and_lessons.md`, `08_excel_verifier_scoping.md` for any workbook, and template C of `06_output_templates.md` before any verdict.
- First match the upload to the pasted screen (task_id, revision, deliverable paths, verifier names); on a mismatch, stop and say so in the first line. Mark each question needing a missing file PENDING INPUT, naming the file.
- Review every attempt and every required deliverable in full, not a sample, and recompute the material figures rather than trusting a polished workbook or deck.
- Log instruction-following, correctness, completeness, deliverable-compliance, fabrication, data-integrity and cross-file coherence issues against the deliverable they belong to, one entry per issue with severity where the form asks, keeping analytical root causes apart from presentation.
- Treat a model failing a verifier as evidence about the model unless the requirement is not a reasonable reading of the prompt; only then route it to the Verifier layer, with the counterexample "A submission that … would FAIL/PASS because …".
- End every defect entry with "Fix:" naming the deliverable, a quoted locator (sheet and cell, slide, quoted sentence) and the exact correction.
- Return entries inline under C1–C8 in SKILL.md: one entry per field in screen order, one paragraph per entry and two at most, no cross-references, no tables.

Check the entries one-to-one against the form and relay them verbatim without stripping fixes or adding anything beyond the C1 lead.
