---
description: Run an independent Project Omega Final Review audit of the latest package
argument-hint: "[path to the latest package and current QC evidence]"
---

Run **Final Review** on: $ARGUMENTS

Delegate to the `project-omega-finance-review` agent via the Agent tool. Instruct it to:

- Audit the latest package independently against the current QC evidence. A prior approval or a "fixed" status is a claim, not proof — re-verify each one in the current files and say which ones actually hold.
- Determine whether any material task, source, golden or verifier defect remains.
- Treat automated QC and LLM-judge findings as evidence: TAKE a genuine supported defect, REJECT one that is unsupported, stale, impossible under platform limits, in conflict with a higher-priority rule, or likely to introduce a new defect. Recommend override only after the required correction attempts and only where the remaining failure is demonstrably stale, immaterial, or a platform or schema limitation.
- Give artifact-level verdicts plus an overall verdict, in the exact Approve/Reject form the platform expects.

Relay the answers back verbatim for pasting into RL World.
