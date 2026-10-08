---
description: Review a Project Omega golden / expert solution for benchmark quality
argument-hint: "[path to the golden solution and its task pack]"
---

Run **Golden Data review** on: $ARGUMENTS

Delegate to the `project-omega-finance-review` agent via the Agent tool. Brief it to:

- Read `skills/project-omega-finance-review/SKILL.md` and, in `references/`, `07_failure_patterns_and_lessons.md`, `08_excel_verifier_scoping.md` for any workbook, and template D of `06_output_templates.md` before any verdict.
- First match the upload to the pasted screen (task_id, revision, deliverable paths, verifier names); on a mismatch, stop and say so in the first line.
- Verify prompt compliance, every material number and claim, cross-deliverable consistency, totals, percentages and ratios, rate-and-base matching, technical labels, chronology, causal claims and source traceability. Recompute the key chains from source, not from golden cells, and say if cached values replaced recalculation.
- Confirm the reasoning shows its logic, intermediate values and source linkage, and that no convention the solver must follow lives only in the reasoning.
- Where the golden and a verifier disagree, decide which is wrong first, rejecting the verifier only with a one-sentence counterexample, "A submission that … would FAIL/PASS because …"; never bend the golden to fit a wrong verifier or weaken a verifier to pass a wrong golden. If the golden passes a verifier you reject, the flaw is in grading other submissions.
- Give APPROVE or REJECT per deliverable plus an overall verdict; APPROVE when the golden passes every verifier and recomputes from source. End every defect note with "Fix:" naming the deliverable, a quoted locator and the exact change.
- Return entries inline under C1–C8 in SKILL.md: one paragraph per note and two at most, no cross-references, no tables.

Correcting the golden is in scope here, but only where it is genuinely wrong; say explicitly what was changed. Check the entries one-to-one against the form and relay them verbatim without stripping fixes or adding anything beyond the C1 lead.
