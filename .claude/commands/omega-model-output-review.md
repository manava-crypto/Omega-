---
description: Run the Project Omega Model Output Review gate over every attempt and deliverable
argument-hint: "[path to the attempts/deliverables, or blank to use attached files]"
---

Run **Model Output Review** on: $ARGUMENTS

If no path is given, inventory the attempts and deliverables the user attached or most recently referenced and confirm the set before reviewing.

Delegate to the `project-omega-finance-review` agent via the Agent tool. Instruct it to:

- Load the Model Output Review form-ready block in `skills/project-omega-finance-review/references/06_output_templates.md`.
- Review every attempt and every required deliverable completely — not a sample.
- Log instruction-following, correctness, completeness, deliverable-compliance, fabrication, data-integrity and cross-file coherence issues against the deliverable they belong to, with severity where the form requires it.
- Keep analytical root causes separate from presentation issues.
- Recompute the material figures rather than trusting a polished workbook or deck.

Relay the platform-ready entries back verbatim.
