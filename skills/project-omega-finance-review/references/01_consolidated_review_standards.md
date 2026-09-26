Consolidated Review Standards

Single source of truth for how Project Omega finance tasks are reviewed

Project Omega | Finance & Insurance reviewer knowledge pack | 25 Sep 2026

1. Reviewer operating principle

The reviewer protects benchmark integrity. The objective is not to maximize the number of issues or to make the task “better” by preference; it is to determine whether the task, evidence, output and scoring logic are materially correct, fair, executable and professionally realistic.

2. Five gates and the object being judged

3. Trainer Review — artifact standards

3.1 Task Design

Scenario reflects work a real finance professional would plausibly perform.

Task requires domain judgment / headroom rather than retrieval, rote formulas, or ambiguous wording.

Task is solvable entirely on a computer using the supplied materials.

Planned anomalies are realistic and unlabeled; they do not give away the answer.

Role, sector, occupation, deliverables, timing and decision context are mutually consistent.

3.2 Source Data

Every referenced file exists, is on-topic, and looks like the natural genre of the underlying record.

No source directly publishes the answer, expected output, exception flag, supported balance, or close handling the solver is supposed to derive.

Shared IDs, entity names, dates, totals, units, currencies and period populations reconcile unless a mismatch is the intended anomaly.

Source dates and events respect the stated cutoff; no event is silently pulled from after the measurement window.

Source files do not carry accidental duplicates, broken running balances, impossible values, invalid formulas without cached values, or missing rows required to solve the task.

The task cannot be solved correctly from one file alone when cross-file reasoning is intended.

3.3 Prompt

The ask is verifiable from supplied sources alone and aligns with the task design.

Two experts should converge on the material deliverable even if their presentation differs.

Constraints that control the decision—source authority, cutoff, exclusions, no-invention rules, output formats—are explicit enough to prevent unfair grading.

The prompt states what to determine, not a step-by-step method, unless the method itself is a business requirement.

The strict output contract agrees with the narrative body and names every required deliverable and format.

3.4 Verifiers

Each verifier has one clear owner concept and can be judged from its declared output file.

Pass/fail anchors are explicit; vague adjectives have practical boundaries.

Every requirement is grounded and fair; no accounting, covenant, business or presentation rule is invented.

Coverage spans every material prompt obligation but avoids re-grading the same property twice.

Core checks cover correctness and required outcomes; secondary checks distinguish stronger correct work from weaker correct work.

No verifier is blocked by platform limitations such as cross-file access or extraction truncation.

4. Cross-file tie-out standard

5. Recompute / cross-foot standard

Rebuild the smallest independent chain that can prove or disprove each material output. Do not rely on the same formula cell the output uses.

Tie totals in both directions when possible: detail → summary and summary → supporting population.

Check displayed rounding separately from full-precision logic; rounded components should not falsely appear to reconcile when the underlying values do not.

A material ratio must use the base its label claims. Confirm numerator, denominator, date and definition.

When a result is sensitive to a legitimate unresolved interpretation, show a primary conclusion plus bounded sensitivity rather than hiding the uncertainty.

6. Model Output Review issue axes

7. Golden Data quality standard

Every carried-forward issue is resolved in the latest version, not just mentioned as fixed.

Root-cause corrections flow through formulas, charts, tables, narrative and recommendation.

Reasoning document (when required) contains step-by-step logic, intermediate values with labels, and explicit source linkage.

No required convention exists only in Reasoning; business deliverables stand on their own.

Workbook contains auditable assumptions, checks and source traceability; no hidden hard-coded “answers” where formulas are expected.

Cross-deliverable figures, labels, recommendations, uncertainties and action timing agree.

8. Sample Calibration standard

Blind grade first. Reveal the LLM judge only after the expert verdict is recorded.

For every verifier: source of requirement, one concept, clear bar, sufficient grader evidence, criticality.

Coverage gaps add checks only for real obligations. Redundancy removes duplicate ownership.

If the golden fails a sound verifier, fix the golden; do not weaken the verifier.

If a verifier is unfair, vague, overlapping or impossible under the runtime, flag it for regeneration with precise guidance.

9. Final Review standard

Use the latest files as source of truth; old versions matter only as remediation history.

Scrutinize any prior failed check and confirm the actual fix.

A remaining material issue in any artifact is terminal for the current package.

Do not reject for cosmetic or pipeline-only issues that do not impair correctness, usability, fairness or gradeability.

10. Severity guide

11. Pre-submit checklist

I read the prompt and every source file in full.

The task is inside the intended finance expertise.

I independently judged the artifact rather than echoing the LLM judge.

I checked material calculations, chronology, definitions, units, currencies and cross-file tie-outs.

I approved sound items and rejected only actual defects.

Every rejection gives location, evidence, implication and exact fix.

Verifier checks are objective, grounded, non-overlapping and executable.

I have resolved or escalated contradictory automated feedback.

No action item is left undecided.

Source basis used to build this document

RL_World_Finance_Expert_Onboarding_v6: expert role, five gates, fundamentally-sound standard, verifier quality, feedback formula, common finance traps, and stage-specific review expectations.

RL World Platform Quick Reference Cheat Sheet and Platform Overview: operational review loop, full-file review, artifact vs LLM-judge separation, and gate workflow.

Project_Omega_Guide_V5: benchmark design, headroom, source-file realism, golden requirements, verifier schema and rubric-quality rules, peer-review routing, and packaging standards.

Trainer_Review_Gate_Convergence_Report (prod data through 23 Sep 2026): latest verifier-platform rules and known non-converging QC failure modes.

Omega_Pod_Finance and Investment tracker: real peer-review decisions and feedback patterns.

Uploaded RL World task folders: completed and in-progress finance benchmark packages used for worked examples and evaluation cases.

V2 Addendum — Pre-Flight Standards

A. Prompt and source-document pre-flight

B. Golden pre-flight

C. Verifier pre-flight

D. Approval / override hygiene

Diff regenerated verifier text against the last reviewed version; detect missing/reverted text before judging new QC findings.

Classify remaining automated fails as substantive fix, policy/platform limitation, or stale result.

Batch substantive fixes rather than resubmitting a half-fixed set.

Override only when substantive defects are clean and the remaining fail is demonstrably stale/incorrect/platform-level; document affected verifier(s) and evidence.

Never use override merely because regeneration is frustrating.


[Table 1]

Gate | Primary object | Core question | Default action if defective

Trainer Review | Task integrity | Is the task itself realistic, supported, coherent, executable and gradeable? | Reject only the defective artifact; regenerate and re-review.

Model Output Review | Model quality | Did each attempt correctly perform the requested finance work from the supplied evidence? | Log every material issue by deliverable and severity.

Golden Data | Benchmark answer | Is the selected solution expert-grade, complete, traceable and internally consistent? | Fix root cause and every downstream consequence.

Sample Calibration | Scoring quality | Do the verifiers grade real obligations fairly and consistently? | Grade blindly, then reconcile; flag bad verifiers or golden defects.

Final Review | Ship quality | Does the entire latest package survive an independent audit? | Any material defect blocks ship.


[Table 2]

Tie-out family | What to compare | Typical failure

Identity | Entity IDs, facility IDs, account numbers, invoice IDs, instrument IDs, customer/vendor names | Same economic item carried twice because formatting differs; missing master key.

Time | Measurement date, effective date, approval timestamp, value date, cutoff, maturity | New rate applied to old period; promise date treated as usable cash date.

Amounts | Detail-to-summary totals, balances, cash, debt, reserves, consideration, expenses | Summary differs from underlying detail; correct number used on wrong basis.

Definitions | EBITDA, leverage, liquidity, NAV, earned premium, reserve, coverage, “available cash” | Definition changes mid-series but trend is presented as comparable.

Units / currency | USD vs local currency, thousands vs full units, gross vs net, par vs carrying value | Native currency carried into USD field; gross notional treated as cash.

Status / approval | Draft vs approved, routed vs committed, review vs final authorization | Downstream work advances from a request that never became effective.


[Table 3]

Axis | Reject / log when

Instruction-following | The output answers a different question, ignores an explicit constraint, or omits a required deliverable / audience.

Correctness | A fact, formula, tie-out, timing conclusion, authority call, classification or recommendation is materially wrong.

Completeness | Required analysis, decision support, risk, bridge, sensitivity, owner/action, source linkage, or section is missing.

Format / deliverable compliance | Required structure/file format is violated in a way that affects use or grading.

Hallucination / fabrication | The output invents a source fact, approval, rule, number, event or citation.

Data integrity | Amounts are internally inconsistent, malformed, duplicated, stale, or cannot reconcile.

Coherence / integration | Workbook, memo and deck disagree or the recommendation is not supported by the analysis.


[Table 4]

Severity | Definition | Examples

Critical | Core decision / answer is wrong, task is unsolvable, source integrity is broken, or final package cannot be trusted. | Wrong authority changes borrowing capacity; missing source makes required conclusion impossible; golden recommends opposite action due to bad calculation.

Major | Material localized error or omission that can be repaired without redesigning the task. | One debt instrument double-counted; one required risk not addressed; memo/workbook disagree on an approval condition.

Minor | Correct answer remains intact but quality, traceability or completeness is reduced. | One stale reference, isolated mislabeled figure, incomplete locator.

Cosmetic | No substantive effect on finance reasoning or scoring. | Formatting inconsistency, typo, raw floating-point residue hidden by correct display format.


[Table 5]

Area | Reviewer standard

Prompt construction | Role/situation/work stated as a genuine request. Ask what to determine, not how. Do not prescribe formula/method/sequence. Keep workplace terminology natural and standard terms undefined unless task-specific meaning differs.

Scope / quantifiers | Every graded time horizon, period count, population, entity subset, inclusion/exclusion rule, denominator, date/rate basis and exact convention is discoverable. Read one/each/every and singular/plural literally.

Ambiguity | Professional ambiguity is allowed; ambiguity about deliverable, authority, population or exact convention is not. If two competent practitioners can choose differently and only one can pass, state the convention or admit both.

Deliverables | Names/paths/extensions/audiences are consistent everywhere. No evaluation meta-commentary. No hidden presentation structure that only exists in the golden. When Project Omega V5 creation rules govern, confirm at least 2 deliverable artifacts in approved formats.

Source set | All required files present/referenced; cross-file joins real; genre/format appropriate; enough scale to feel professional; task not solvable from one file when multi-file reasoning is intended. When Project Omega V5 creation rules govern, confirm 3+ source documents.

Leakage | No pre-solved values/flags; no source section that paraphrases task decomposition; no solver-facing recipes; no synthesis/advisor commentary that identifies important items or intended answer.

Realism | Non-monotonic IDs, non-uniform/non-round values where appropriate, jittered timestamps, plausible anonymized names, natural disorder, no synthetic/model boilerplate.

Consistency | IDs resolve; summaries tie to detail; units/scales correct; chronology/cutoffs valid; approvals follow underlying events; no future-period comparisons; accounting/physical constraints hold; exact verifier anchors derivable.


[Table 6]

Area | Reviewer standard

Brief compliance | All requested files present/named/formatted/audience-correct. Reasoning stays in Expert Solution; it contains step-by-step logic, intermediates and source linkage. No solver-needed convention exists only in reasoning.

Internal consistency | Narrative matches tables; deliverables agree; displayed totals/rounded totals tie; percentage/ratio labels are correct; rates use matching bases; technical/accounting labels are accurate; causal claims supported; every figure has source or shown derivation.

Presentation | Stated/consistent precision, no raw floats, blank/working sheets, empty TOC/headings, placeholders or blank trailing pages. Validate alleged layout defects against raw structure because extractors can reorder content.


[Table 7]

Area | Reviewer standard

Coverage | Map prompt clause by clause. Every explicit obligation has an owner; every verifier traces to prompt/source/clearly implied task success condition. Cold-attempt failures may motivate checks only when the obligation is fair and discoverable.

Atomicity / ownership | One tightly coupled construct per verifier; split only when independent pass/fail is possible. One scoring owner per property; shared anchors do not equal overlap.

Pass/fail wording | Concrete exhaustive PASS/FAIL, silent omission covered, no advisory verbs or unbounded qualitative terms as verdict gates. Examples are clearly optional or clearly mandatory.

Self-contained / runtime | Inline everything the single-file judge needs. No cross-file dependencies, hidden metadata, invisible file-format properties or unreliable PowerPoint adjacency.

Tolerance / methods | Accept every defensible method/reading supported by materials; keep known wrong methods outside accepted band. No method requirement unless prompt requires it.

Core/secondary | Core only for load-bearing correctness; secondary for good-vs-great qualities. Avoid cascading weight from one upstream omission.

Count | Do not target verifier count for its own sake. Coverage and quality control count. A count requirement applies only if the current governing task/platform spec explicitly says so.
