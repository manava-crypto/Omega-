# Project Omega Finance Review Agent
Project Omega finance-review copilot for RL World. Reviews Trainer Review, Model Output, Golden, Sample Calibration and Final Review task packs; recomputes key figures, checks sources and verifiers, and returns evidence-backed, platform-ready verdicts and fixes.

## Overview

This repository contains the operating framework, review standards, templates, examples, and evaluation materials used to build the Project Omega Finance Review Agent for RL World.

The agent is designed to support Finance & Insurance task review across the full RL World review lifecycle. Its purpose is to help an expert reviewer inspect task packages, verify calculations and source authority, identify defects at the correct layer, assess verifiers, reconcile automated judge findings, and produce concise, platform-ready review comments.

The agent is a review copilot, not a replacement for expert judgment. It should independently inspect the supplied evidence, recompute material figures, and make its own assessment rather than treating automated QC or LLM judge outputs as authoritative.

---

## Primary Use Cases

The agent supports the following review stages:

### Trainer Review

Reviews the task in dependency order:

Task Design → Source Data → Prompt → Verifiers → Automated Judge Checks → Escalations.

The review covers realism, headroom, solvability, source sufficiency, chronology, cross-file consistency, authority, leakage, prompt clarity, verifier quality, coverage, and platform constraints.

### Model Output Review

Reviews every model attempt and required deliverable for analytical correctness, instruction following, completeness, fabrication, formatting requirements, internal consistency, and cross-deliverable coherence.

Issues should be assigned to the correct deliverable, given an appropriate severity, and written in a form that can be entered directly into the RL World platform.

### Golden Data Review

Checks whether the expert solution is genuinely benchmark quality.

The review verifies calculations, source traceability, reasoning, internal consistency, prompt compliance, terminology, chronology, totals, percentages, ratios, rates, and consistency across every deliverable.

A verifier should never be weakened simply to make an incorrect golden pass.

### Sample Calibration

Grades each model attempt against each verifier independently before considering the automated judge result.

The agent then reconciles disagreements, evaluates whether each verifier is fair and well specified, identifies coverage gaps and overlap, diagnoses golden defects, and prepares the calibrated package for Final Review.

### Final Review

Performs an independent final audit of the latest task package.

Prior approvals, fixes, and automated QC results are treated as evidence rather than proof. The current files must independently support the final decision.

---

## Core Review Principles

The review standard is evidence first.

The agent should read the complete files whenever available, rather than relying on previews, filenames, summaries, or automated judge explanations.

Material calculations should be independently recomputed or cross-footed. A polished workbook, memo, or presentation is not assumed to be correct.

Source authority and chronology must be resolved explicitly. For example, an effective executed amendment normally governs the relevant period over a stale summary field. A ledger or transactional record normally carries more evidentiary weight than a presentation summarizing it.

Defects must be assigned to the layer where they originate. A source-data problem should not be disguised as a verifier problem. A bad verifier should not cause a correct artifact to be rejected. An unclear prompt should not be repaired by inventing scoring rules downstream.

Review comments should identify the location, evidence, implication, and exact correction required.

---

## Repository Structure

A recommended repository structure is:

```text
project-omega-review-agent/
│
├── README.md
│
├── agent/
│   ├── instructions.md
│   ├── description.md
│   └── conversation_starters.md
│
├── standards/
│   ├── consolidated_review_standards.md
│   ├── authority_hierarchy.md
│   ├── defect_taxonomy.md
│   ├── verifier_standard.md
│   └── feedback_writing_standard.md
│
├── domains/
│   ├── finance_domain_cheat_sheet.md
│   ├── credit_and_covenants.md
│   ├── insurance_underwriting.md
│   ├── reserving_and_ibnr.md
│   ├── treasury_and_liquidity.md
│   ├── close_and_consolidation.md
│   ├── valuation_and_ma.md
│   └── investment_analysis.md
│
├── workflows/
│   ├── trainer_review.md
│   ├── model_output_review.md
│   ├── golden_data_review.md
│   ├── sample_calibration.md
│   └── final_review.md
│
├── templates/
│   ├── trainer_review_template.md
│   ├── model_output_review_template.md
│   ├── golden_review_template.md
│   ├── sample_calibration_template.md
│   ├── final_review_template.md
│   └── feedback_template.md
│
├── examples/
│   ├── completed_tasks/
│   ├── accepted_feedback/
│   ├── rejected_examples/
│   └── verifier_examples/
│
├── evaluation/
│   ├── evaluation_cases.md
│   ├── expected_results.md
│   └── regression_tests.md
│
├── platform/
│   ├── verifier_runtime_rules.md
│   ├── override_guidance.md
│   ├── qc_interpretation.md
│   └── troubleshooting.md
│
└── source_guides/
    ├── project_omega_guide/
    ├── rl_world_onboarding/
    ├── platform_overview/
    ├── faq/
    └── historical_guidance/
