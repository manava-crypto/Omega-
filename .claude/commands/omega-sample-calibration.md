---
description: Run Project Omega Sample Calibration — grade attempts against verifiers, then reconcile with the judge
argument-hint: "[path to attempts, verifiers and judge verdicts]"
---

Run **Sample Calibration** on: $ARGUMENTS

Delegate to the `project-omega-finance-review` agent via the Agent tool. Brief it to:

- Read `skills/project-omega-finance-review/SKILL.md` and, in `references/`, `07_failure_patterns_and_lessons.md`, `08_excel_verifier_scoping.md` for any workbook verifier, and template E of `06_output_templates.md` before any verdict.
- First match the upload to the pasted screen (task_id, revision, deliverable paths, verifier names); on a mismatch, stop and say so in the first line. Record the judge panel from config.models, noting any judge-panel seat change.
- Grade every attempt against every verifier yourself first, PASS or FAIL with the evidence, before reading the judge's verdict; then reconcile and explain each disagreement. A model false-fail shows unfairness only when the requirement is not a reasonable reading of the prompt.
- Answer the template's calibration questions for each verifier and run the probe battery before flagging it for regeneration; flag a verifier only with a one-sentence counterexample, "A submission that … would FAIL/PASS because …".
- Rebuild the ownership and coverage maps. Redundant and duplicative verifiers are a real defect; consolidation is as legitimate as splitting. Before a merge or deletion, name each obligation's new owner, or repair in place.
- Fix the golden only where it is wrong, run the golden consistency check, and close with the template's summary for Final Review.
- End every regeneration or defect note with "Fix:" naming the verifier or artifact ID, a quoted locator and the exact change, and return entries inline under C1–C8 in SKILL.md: one paragraph per note and two at most, no cross-references, no tables.

Re-verify every finding that drives a regeneration flag, check the entries one-to-one against the form, and relay them verbatim without stripping fixes or adding anything beyond the C1 lead.
