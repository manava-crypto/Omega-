# Project Omega Finance Review Agent

Project Omega finance-review copilot for RL World. It reviews Trainer Review, Model Output Review, Golden Data, Sample Calibration and Final Review task packs, recomputes key figures, checks sources and verifiers, and returns concise, evidence-backed, platform-ready verdicts and fixes.

## Overview

The agent supports an expert reviewer across the RL World review lifecycle; it does not replace expert judgment. It treats automated QC and LLM-judge output as claims to audit, not as an answer key. The rulebook was rebuilt from failure patterns mined from review sessions on seven task packs; reference 07 records each pattern with the rule and check that prevent it.

## Review stages

**Trainer Review** runs in dependency order: Task Design → each Source Data file → Prompt → Verifiers → LLM judge checks → Escalations. It covers realism, headroom, solvability, source sufficiency, chronology, cross-file consistency, authority, leakage, prompt clarity, verifier quality, coverage and platform constraints, and raises every finding in one pass.

**Model Output Review** checks every attempt and required deliverable for analytical correctness, instruction following, completeness, fabrication, internal consistency and cross-deliverable coherence, logging each issue against its deliverable, with a severity where the form asks for one.

**Golden Data** checks that the expert solution is benchmark quality: calculations recomputed from source, traceability, reasoning, terminology, chronology, totals, rates and consistency across deliverables. Where the golden and a verifier disagree, the agent decides which is wrong before changing either.

**Sample Calibration** grades every attempt against every verifier before reading the judge's verdict, then reconciles, calibrates each verifier, maps coverage and overlap, diagnoses golden defects and hands a summary to Final Review.

**Final Review** audits the latest package independently. Prior approvals and "fixed" statuses are claims, re-verified in the current files.

The Model Output Review, Golden Data and Sample Calibration rules are transferred from Trainer Review and Final Review sessions; no complete session of those gates appears in the mined evidence.

## Core review principles

- Evidence first. The agent matches the upload to the pasted screen (task_id, revision, deliverable paths, verifier names), then reads every supplied file in full; previews, filenames, links and judge summaries are not evidence. A question that needs a missing file is marked PENDING INPUT, naming the file.
- Recompute, don't trust. Material figures are recomputed or cross-footed; a polished workbook, memo or deck is not assumed correct.
- Authority and chronology are resolved explicitly. An effective executed amendment normally governs the relevant period over a stale summary field, and a ledger or transactional record normally outweighs a presentation summarising it.
- Defects go to their origin. A source-data problem is not disguised as a verifier problem, a bad verifier does not cause a correct artifact to be rejected, and an unclear prompt is not repaired by inventing scoring rules downstream. A verifier is never weakened to cover an upstream defect.
- Counterexample discipline. A verifier is rejected only with a one-sentence counterexample, "A submission that … would FAIL/PASS because …", and approved only after the probe battery in reference 07 finds none.
- One owner per value. Redundant and duplicative verifiers are a real defect; consolidation is as legitimate as splitting.

## Output standard and the Final Review bar

Answers are paste-ready and inline: an optional lead of one paragraph, two at most, then one entry per platform field in screen order, headed by the on-screen name and verdict word, with fixed platform lists such as one line per verifier allowed. An APPROVE or clean AGREE takes one sentence; a defect entry takes one paragraph, two at most, giving evidence with a quoted locator, the counterexample, then "Fix:" with the exact change, and uses bullets only when a fix has three or more separate edits. At Final Review a verifier rejection ends the task, so the agent blocks only when a rubric misstates a governing term, a realistic submission is mis-graded (shown on a supplied output or on a concrete submission under an accepted reading), or the golden fails a sound verifier; everything else gets an optional line.

## Repository structure

```text
Omega-/
├── CLAUDE.md                  # routing and house rules
├── README.md
├── .claude/
│   ├── agents/
│   │   └── project-omega-finance-review.md
│   ├── commands/              # one slash command per gate
│   │   ├── omega-trainer-review.md
│   │   ├── omega-model-output-review.md
│   │   ├── omega-golden-review.md
│   │   ├── omega-sample-calibration.md
│   │   └── omega-final-review.md
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
            ├── 06_output_templates.md               # gate templates A–G
            ├── 07_failure_patterns_and_lessons.md   # probe battery, pre-send checks
            └── 08_excel_verifier_scoping.md         # workbook scoping, extractor limits
```

## Running the agent in Claude Code

The copilot is packaged as a Claude Code subagent, and opening this repository in Claude Code is enough to pick it up. `CLAUDE.md` routes any gate request to the agent even when no slash command is used, so "run trainer review on this pack" works as well as `/omega-trainer-review ./task-pack`.

Each command takes a path to the task pack; `/omega-trainer-review` and `/omega-model-output-review` also run without one, inventorying the files attached or last referenced and confirming the pack first.

The agent deliberately has no web access: review is closed-book against the supplied evidence, and gaps are never filled from outside knowledge. Given only a platform link, it asks for the review-artifacts zip and the judge text pasted verbatim. It handles xlsx, csv, pdf, docx, pptx, md and json, opening workbooks for both formulas and cached values, and keeps scripts and extracts in the scratchpad; review output is never written into the repository.

The knowledge pack in `skills/project-omega-finance-review/` is the single source of truth, and `rules/project-omega-finance-review.mdc` points Cursor at the same directory, so both editors read the same rulebook.
