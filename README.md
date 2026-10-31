# Project Omega Finance Review Agent

Project Omega finance-review copilot for RL World. It reviews Trainer Review, Model Output Review, Golden Data, Sample Calibration, Final Review and External QC work, recomputes key figures, checks sources and verifiers, and returns concise, evidence-backed, platform-ready verdicts and fixes.

## Overview

The agent supports an expert reviewer across the RL World review lifecycle; it does not replace expert judgment. It treats automated QC and LLM-judge output as claims to audit, not as an answer key. The rulebook was rebuilt from failure patterns mined from review sessions on more than thirty task packs; reference 07 records each pattern with the rule and check that prevent it, reference 09 records how the platform's judge checks and Auto QC actually define and score each question, and reference 10 covers External QC, the stage after Final Review.

## Review stages

**Trainer Review** runs in dependency order: Task Design → each Source Data file → Prompt → Verifiers → LLM judge checks → Escalations. It covers realism, headroom, solvability, source sufficiency, chronology, cross-file consistency, authority, leakage, prompt clarity, verifier quality, coverage and platform constraints, and raises every finding in one pass.

**Model Output Review** checks every attempt and required deliverable on the platform's six axes per output file, plus five Additional Feedback fields for cross-file points, logging each issue once with the form's two severities, Critical or Nice to have.

**Golden Data** checks that the expert solution is benchmark quality: calculations recomputed from source, traceability, reasoning, terminology, chronology, totals, rates and consistency across deliverables. Where the golden and a verifier disagree, the agent decides which is wrong before changing either.

**Sample Calibration** grades every attempt against every verifier before reading the judge's verdict, resolves each disagreement, then answers the platform's five questions per verifier, knowing which answers delete, split, reword or add a verifier at regeneration, and fixes the golden only against a sound verifier.

**Final Review** audits the latest package independently. Prior approvals and "fixed" statuses are claims, re-verified in the current files.

**External QC** follows Final Review and is the last stage before TFRL. The QC team uploads findings; the agent gives each one a true or false positive verdict after a mandatory four-pass review, keeps every fix inside verifier.json (an agreed prompt, source or golden finding rejects the task) and writes the fix request for the QC tracker.

The Golden Data rules are still transferred from other gates; the other stages are backed by review sessions and platform guidance.

## Core review principles

- Evidence first. The agent matches the upload to the pasted screen (task_id, revision, deliverable paths, verifier names), then reads every supplied file in full; previews, filenames, links and judge summaries are not evidence. A question that needs a missing file is marked PENDING INPUT, naming the file.
- Recompute, don't trust. Material figures are recomputed or cross-footed; a polished workbook, memo or deck is not assumed correct.
- Authority and chronology are resolved explicitly. An effective executed amendment normally governs the relevant period over a stale summary field, and a ledger or transactional record normally outweighs a presentation summarising it.
- Defects go to their origin. A source-data problem is not disguised as a verifier problem, a bad verifier does not cause a correct artifact to be rejected, and an unclear prompt is not repaired by inventing scoring rules downstream. A verifier is never weakened to cover an upstream defect.
- Counterexample discipline. A verifier is rejected only with a one-sentence counterexample, "A submission that … would FAIL/PASS because …", and approved only after the probe battery in reference 07 finds none.
- The on-screen check decides. Each judge check is answered by the Description pasted with it; overlap and atomicity follow the version of the check on screen, and a design documented in the task's verifier plan is not a defect.
- One owner per obligation. Redundant and duplicative verifiers are a real defect; consolidation is as legitimate as splitting. Importance (core or secondary) is never a reason to reject.
- Plain words. Notes read as an experienced finance reviewer would write them, with no file internals or tool names.

## Output standard and the Final Review bar

Answers are paste-ready and inline: an optional lead of one paragraph, two at most, then one entry per platform field in screen order, headed by the on-screen name and verdict word, with fixed platform lists such as one line per verifier allowed. An APPROVE or clean AGREE takes one sentence; a defect entry takes one paragraph, two at most, giving evidence with a quoted locator, the counterexample, then "Fix:" with the exact change, and uses bullets only when a fix has three or more separate edits. At Final Review, rejecting Task Design, a source, the prompt or the golden ends the task, while a verifier REJECT sends the verifier back for repair; the agent rejects a verifier only when its rubric misstates a governing term or a realistic submission is mis-graded, rejects the golden only when it truly fails a sound verifier, and gives everything else an optional line. Final Review and External QC run as multi-agent orchestrations with repeated rounds of checks, so the answers handed over are final.

## Repository structure

```text
Omega-/
├── CLAUDE.md                  # routing and house rules
├── README.md
├── .claude/
│   ├── agents/
│   │   └── project-omega-finance-review.md
│   ├── workflows/             # multi-round orchestrations for Final Review and External QC
│   │   ├── omega-final-review.js
│   │   └── omega-external-qc.js
│   ├── commands/              # one slash command per gate
│   │   ├── omega-trainer-review.md
│   │   ├── omega-model-output-review.md
│   │   ├── omega-golden-review.md
│   │   ├── omega-sample-calibration.md
│   │   ├── omega-final-review.md
│   │   └── omega-external-qc.md
│   └── skills/
│       └── project-omega-finance-review -> ../../skills/project-omega-finance-review
├── rules/
│   └── project-omega-finance-review.mdc   # Cursor rule, always applied
└── skills/
    └── project-omega-finance-review/
        ├── SKILL.md           # operative rules for every gate
        └── references/
            ├── 01_consolidated_review_standards.md
            ├── 02_authority_and_defect_taxonomy.md
            ├── 03_finance_domain_cheat_sheet.md
            ├── 04_completed_task_examples.md
            ├── 05_real_feedback_examples.md
            ├── 06_output_templates.md               # gate templates A–H
            ├── 07_failure_patterns_and_lessons.md   # probe battery, pre-send checks
            ├── 08_excel_verifier_scoping.md         # workbook scoping, extractor limits
            ├── 09_platform_checks_and_auto_qc.md    # platform check definitions, Auto QC
            └── 10_external_qc.md                    # External QC workflow, true/false positive test
```

## Running the agent in Claude Code

The copilot is packaged as a Claude Code subagent, and opening this repository in Claude Code is enough to pick it up. `CLAUDE.md` routes any gate request to the agent even when no slash command is used, so "run trainer review on this pack" works as well as `/omega-trainer-review ./task-pack`.

`/omega-final-review` and `/omega-external-qc` launch the multi-agent workflows in `.claude/workflows/` (independent reviews, adversarial adjudication rounds until no verdict moves, and an "are you sure?" challenge), so they take longer and use more agents than the other commands; if the Workflow tool is unavailable, the command runs the same rounds with subagents. Each command takes a path to the task pack; `/omega-trainer-review` and `/omega-model-output-review` also run without one, inventorying the files attached or last referenced and confirming the pack first.

The agent deliberately has no web access: review is closed-book against the supplied evidence, and gaps are never filled from outside knowledge. Given only a platform link, it asks for the review-artifacts zip and the judge text pasted verbatim. It handles xlsx, csv, pdf, docx, pptx, md and json, opening workbooks for both formulas and cached values, and keeps scripts and extracts in the scratchpad; review output is never written into the repository.

The knowledge pack in `skills/project-omega-finance-review/` is the single source of truth, and `rules/project-omega-finance-review.mdc` points Cursor at the same directory, so both editors read the same rulebook.
