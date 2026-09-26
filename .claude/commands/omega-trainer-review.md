---
description: Run the Project Omega Trainer Review gate on a task pack and return platform-ready answers
argument-hint: "[path to task pack, or leave blank to use attached/most recent files]"
---

Run **Trainer Review** on the task pack at: $ARGUMENTS

If no path is given, inventory the files the user attached or most recently referenced and confirm the pack contents before reviewing.

Delegate the review to the `project-omega-finance-review` agent via the Agent tool. Instruct it to:

- Load `skills/project-omega-finance-review/references/06_output_templates.md` section B (Trainer Review gate) and follow that question order exactly.
- Review in dependency order: Task Design → each Source Data file individually → Prompt → Verifiers → LLM Judge Checks → Escalations.
- Read every source file in full and recompute the material figures; no sample-reading, no reliance on previews or the judge's own explanation.
- Return an explicit APPROVE or REJECT for each artifact and AGREE or DISAGREE for each automated check, with Location → Evidence → Implication → Exact Fix notes written as paragraphs.
- Run the contradiction check across all notes before output.

Relay the agent's platform-ready answers back verbatim — they are meant to be pasted into RL World.
