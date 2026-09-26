---
description: Run Project Omega Sample Calibration — grade attempts against verifiers, then reconcile with the judge
argument-hint: "[path to attempts, verifiers and judge verdicts]"
---

Run **Sample Calibration** on: $ARGUMENTS

Delegate to the `project-omega-finance-review` agent via the Agent tool. Instruct it to:

- Load the Sample Calibration template and added calibration checks in `skills/project-omega-finance-review/references/06_output_templates.md`.
- Grade every attempt against every verifier independently first — PASS or FAIL with the evidence — before looking at the LLM judge verdict, then reconcile and explain each disagreement.
- For each verifier, state the source of the requirement, whether it covers one concept or several, whether pass/fail is unambiguous, whether the judge sees enough to score it from the declared artifact alone, and whether failure is critical or secondary.
- Build the ownership map and call out coverage gaps and overlaps; flag vague, unfair or unbuildable verifiers for regeneration.
- Fix golden defects only where the golden is actually wrong, run the golden consistency check, and close with the Final Review summary.

Relay the calibrated, paste-ready output back verbatim.
