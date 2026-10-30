---
description: Run Project Omega External QC — give a true or false positive verdict on every QC finding after the Final Review Gate
argument-hint: "[pasted QC findings and the attached verifier file, plus the task pack]"
---

Run **External QC** on: $ARGUMENTS

External QC follows the Final Review Gate and is the last stage before TFRL, so no error is tolerated. Only verifier.json changes are in scope; an agreed finding against the prompt, sources or golden rejects the task.

Delegate to the `project-omega-finance-review` agent via the Agent tool, twice, as two independent reviewers who never see each other's verdicts. Brief each one to:

- Read `skills/project-omega-finance-review/SKILL.md` and, in `references/`, `10_external_qc.md`, `07_failure_patterns_and_lessons.md`, `08_excel_verifier_scoping.md` for any workbook criterion, and template H of `06_output_templates.md` before any verdict.
- Match the screen first (task ID, the version in the task link, the attached "verifier (NN).json", the card count); on a mismatch, stop and say so in the first line. Diff the verifier file against the FRG-approved and any earlier corrected version, and report agreed edits that did not land and unrequested changes.
- For each card, read the criterion verbatim, the prompt, the sources and the golden, recompute every figure QC cites and grade the finding's own example of a correct answer against the criterion text. Agree only when that complaint holds in the current file and needs a verifier change; Disagree when it does not, including every grader or infrastructure fault, which gets "No change needed to verifier.json" and an escalation line.
- Look for a sound verifier-only cure before agreeing that a defect lives in the prompt, sources or golden, and say in the first sentence when agreeing rejects the task. TAKE or REJECT each remediation item; never adopt one that edits the prompt, sources or golden, labels the planted item, adds an unasked condition or is an escape clause.
- Re-test every verdict adversarially (Pass 2 of reference 10) and run the set-consistency and pre-send passes.
- Return a one-paragraph lead (outcome, tally, closest call), one entry per card in screen order headed exactly as on screen, and, when any verifier finding is agreed, one self-contained fix request for the tracker's Additional Comments cell. Give a corrected verifier.json only if the user asks.

Then reconcile the two reports yourself: wherever they split, re-derive the verdict from the files, never by vote, and re-check every Agree-driving figure and quote before relaying. Relay the entries in screen order, inline, under C1–C8 in SKILL.md, without stripping fixes, and list any verdict you changed in one lead line. If challenged, re-test each card against the same bar; a changed verdict states "changed because <new evidence>".
