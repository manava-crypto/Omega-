# Project Omega / RL World — Finance Review

This repository is the operating framework for the Project Omega Finance Review Copilot: a Quality Authority for Finance & Insurance benchmark tasks on RL World.

## Route gate work to the agent

Whenever the user asks for Trainer Review, Model Output Review, Golden Data review, Sample Calibration, Final Review, verifier or rubric review, LLM-judge TAKE/REJECT calls, or platform-ready Approve/Reject/Agree/Disagree answers, delegate to the `project-omega-finance-review` agent (`.claude/agents/project-omega-finance-review.md`) rather than answering directly. The slash commands `/omega-trainer-review`, `/omega-model-output-review`, `/omega-golden-review`, `/omega-sample-calibration` and `/omega-final-review` each set up one gate.

## Rulebook

The standards, templates and worked examples live in `skills/project-omega-finance-review/` (symlinked into `.claude/skills/` so the skill is discoverable, and referenced by `rules/project-omega-finance-review.mdc` for Cursor). Load the reference that covers the gate in play before writing a verdict. The original `.docx` uploads are in the repository root.

## House rules for review work

Read every supplied task-pack file in full — previews, filenames, sheet names and the LLM judge's summary are not evidence. Recompute material figures instead of trusting a polished workbook or deck; keep the scratch scripts in the scratchpad directory, not here. Route each defect to the layer where it originates and never weaken a verifier to cover an upstream problem. Every REJECT and DISAGREE carries Location → Evidence → Implication → Exact Fix as a paragraph, naming the exact artifact, sheet, row, slide or verifier. Substantive output is prose, not tables or bullet grids, unless the platform form requires a fixed structure. Where evidence is missing, say PENDING INPUT or NOT VERIFIABLE rather than filling the gap.
