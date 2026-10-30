# Project Omega / RL World — Finance Review

This repository is the operating framework for the Project Omega Finance Review Copilot: a Quality Authority for Finance & Insurance benchmark tasks on RL World.

## Route gate work to the agent

Whenever the user asks for Trainer Review, Model Output Review, Golden Data review, Sample Calibration, Final Review, External QC (true or false positive verdicts on QC findings after Final Review), verifier or rubric review, LLM-judge TAKE/REJECT calls, or platform-ready Approve/Reject/Agree/Disagree answers, delegate to the `project-omega-finance-review` agent (`.claude/agents/project-omega-finance-review.md`) rather than answering directly. The slash commands `/omega-trainer-review`, `/omega-model-output-review`, `/omega-golden-review`, `/omega-sample-calibration`, `/omega-final-review` and `/omega-external-qc` each set up one gate.

## Rulebook

The standards, templates and worked examples live in `skills/project-omega-finance-review/` (symlinked into `.claude/skills/` so the skill is discoverable, and referenced by `rules/project-omega-finance-review.mdc` for Cursor). Before any verdict, load `SKILL.md`, the gate's template in `references/06_output_templates.md`, `references/07_failure_patterns_and_lessons.md`, `references/08_excel_verifier_scoping.md` for any workbook verifier, and `references/10_external_qc.md` for any External QC finding.

## House rules for review work

First match the upload to the pasted screen (task_id, revision, deliverable paths, verifier names), then read every supplied task-pack file in full; previews, filenames, links and the LLM judge's summary are not evidence. Recompute material figures instead of trusting a polished workbook or deck. Route each defect to the layer where it originates and never weaken a verifier, or add an escape clause, to cover an upstream defect. Where evidence is missing, say PENDING INPUT or NOT VERIFIABLE rather than filling the gap. Answer each judge check by the Description pasted with it, and read tests/verifier-plan.md before asking for any split, merge or deletion; importance (core or secondary) is never a reason to reject.

REJECT a verifier only with a one-sentence counterexample, "A submission that … would FAIL/PASS because …". At Final Review a verifier rejection ends the task, so block only on a misstated governing term, a realistic submission shown to be mis-graded, or a golden failing a sound verifier; everything else gets an optional line, but a requirement the prompt never asks for is a mis-grade, not an optional reading. External QC is the last stage: only verifier.json changes are in scope, an agreed prompt, source or golden finding rejects the task, a finding is a true positive only when its own complaint holds in the current verifier file and needs a change, and every verdict passes the four-pass review in reference 10 before it is sent.

Every defect note (REJECT, AGREE with a FAIL, or DISAGREE with a PASS) stands alone and ends with "Fix:" naming the artifact or verifier ID, a quoted locator and the exact change; a note that clears an item gives the reason and proof and ends "No change required to this file for this check." The button always matches the words. Answers are concise and inline: an optional lead of one paragraph, two at most; one entry per platform field in screen order; one paragraph per note, two at most, with bullets only for three or more separate edits; full replacement criteria only on request; prose, not tables, unless the form fixes the structure. Write in plain words an experienced finance reviewer would use, with no file internals or tool names.

Delegation briefs quote the bar, the terminal consequence, the counterexample rule, Fix: and C1–C8 (the output rules in SKILL.md). Re-verify any finding that drives a REJECT, re-test that it breaches the on-screen check it is filed under, test rival figures over every period, and relay one-to-one without stripping fixes.

Keep scratch scripts, extracts and ledgers in the scratchpad directory, and never write review output into the repository.
