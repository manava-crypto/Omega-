---
description: Review a Project Omega golden / expert solution for benchmark quality
argument-hint: "[path to the golden solution and its task pack]"
---

Run **Golden Data review** on: $ARGUMENTS

Delegate to the `project-omega-finance-review` agent via the Agent tool. Instruct it to:

- Verify prompt compliance, every material number and claim, cross-deliverable consistency, totals, percentages and ratios, rate-and-base matching, technical labels, chronology, causal claims and source traceability.
- Confirm the reasoning shows its logic, its intermediate values and its source linkage, and that no solver-required convention exists only in the reasoning.
- Where the golden and a verifier disagree, determine which one is wrong instead of bending the golden to satisfy a bad verifier.
- Give an APPROVE or REJECT per deliverable plus an overall verdict, with paragraph-form Location → Evidence → Implication → Exact Fix notes.

This is the one gate where correcting the artifact is in scope — but only where the golden is genuinely wrong, and say so explicitly when you change anything.
