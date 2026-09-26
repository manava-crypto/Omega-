Real Feedback Examples

Project tracker examples rewritten into the Omega note standard

Project Omega | Finance & Insurance reviewer knowledge pack | 25 Sep 2026

1. Source workbook appears populated but extracted values are blank

LOCATION → Source Data — 02_Rent_Roll_and_Lease_Abstracts.xlsx, H6:H17 and totals D20/H20

EVIDENCE → Annual base-rent and total cells are formulas with no cached values, so text extraction exposes blanks even though adjacent SF and rent/SF permit reconstruction.

IMPLICATION → The grader/solver may receive an incomplete source representation and different systems may reach different results.

EXACT FIX → Recalculate and save the workbook so H6:H17, D20 and H20 have current cached values; do not change the underlying lease economics.

2. Reasoning arithmetic does not support the stated multiple

LOCATION → Golden — Reasoning.docx, equity-multiple calculation

EVIDENCE → The reasoning states $27,583,126 / ($19,181,250 + $1,480,903) = 1.37x, but that division is 1.3350x. The correct positive-distribution numerator is $28,211,430, which gives about 1.37x.

IMPLICATION → The final answer happens to be right, but the audit trail is mathematically wrong and cannot support the conclusion.

EXACT FIX → Replace the numerator with $28,211,430 and show the four contributing positive distributions so the reasoning ties to the workbook.

3. Source file leaks the answer the task is supposed to derive

LOCATION → Source Data — ytd_debt_amortization_and_account_map.xlsx

EVIDENCE → The workbook includes “Supported 04/30 Balance”, an April component split, an “Unsupported Difference Flag”, and a support index that states close handling.

IMPLICATION → These fields pre-solve the reconciliation and remove the intended expert reasoning/headroom.

EXACT FIX → Remove the supported-balance, pre-solved component, exception-flag and close-handling answer fields; retain only the raw records needed to derive them.

4. General-ledger running balance is mechanically wrong

LOCATION → Source Data — april_2025_qbo_loan_liability_gl_detail.csv

EVIDENCE → The running-balance field equals each row’s amount instead of the cumulative account balance on 107/140 rows; the first observed failure shows -147.38 where the cumulative balance should be 122.09.

IMPLICATION → A real reviewer cannot rely on the record and any tie-out using the field can be corrupted.

EXACT FIX → Regenerate the running balance as a true per-account cumulative total while preserving the original transaction amounts and order.

5. Golden workbook and memo disagree on a material launch condition

LOCATION → Golden — launch-conditions workbook vs memo, Iloilo corridor

EVIDENCE → The memo requires an executed distribution-utility connection agreement before energization, but the workbook’s launch-conditions tab omits that condition.

IMPLICATION → The package gives two different operational go-live standards for the same corridor.

EXACT FIX → Add the executed connection agreement as an explicit Iloilo launch condition in the workbook, matching the memo; do not change the memo rule.

6. Verifier imposes structure absent from the prompt

LOCATION → Verifier — criterion requiring raw source tabs / owner-provenance fields

EVIDENCE → The prompt does not require those specific workbook structures, yet the verifier makes them part of pass/fail.

IMPLICATION → A faithful and materially correct answer can fail for an invented implementation requirement.

EXACT FIX → Widen the verifier to test the underlying traceability/outcome visible in the deliverable, or add the structure to the prompt only if it is genuinely required by the business task.

7. Verifier asks for something the grader cannot observe

LOCATION → Verifier — formula-liveness / Excel Table / named-range check

EVIDENCE → The scoring path sees extracted/rendered content, not formula objects, Table objects or named ranges.

IMPLICATION → The verifier can false-fail a correct workbook because the required property is outside its observation model.

EXACT FIX → Rewrite the verifier around observable evidence, or route the need to a workbook-aware check if the platform supports one; do not grade an invisible property.

8. Automated “answer-key leakage” flag is a false positive

LOCATION → LLM judge check — inlined expected values in verifier rubric

EVIDENCE → The solver receives only the prompt and source data; it does not see verifier prompts. Inlined accepted values are required to make a single-file rubric self-contained.

IMPLICATION → Removing anchors would make the verifier vague or ungradeable without reducing any real solver leakage risk.

EXACT FIX → REJECT the remediation. Keep the inlined anchors; confirm they are grounded and accept all defensible values.

9. Pipeline conversion banner is not source content

LOCATION → LLM judge check — alleged phrase in CFO_Correspondence_Q2_2025.docx

EVIDENCE → Direct case-insensitive searches of the document XML and task folder find no “degraded best-effort text extraction” phrase; the string comes from the conversion fallback.

IMPLICATION → Treating the banner as source content would incorrectly reject a sound task for a pipeline artifact.

EXACT FIX → DISAGREE with the judge and route the conversion banner to pipeline/QC escalation; make no source-file edit.

10. Prompt fails to identify the full evidence set

LOCATION → Prompt — source-file references

EVIDENCE → The working folder contains source documents that the prompt never names or otherwise incorporates into the evidence set.

IMPLICATION → A solver cannot know whether those files are required evidence, optional context, or stray packaging, so grading can become unfair.

EXACT FIX → Either reference every required source in the prompt/evidence description or remove unrelated files from Source Documents; then align verifier coverage to the final source set.

What strong feedback has in common

It names the artifact and the exact offender.

It proves the issue with a calculation, locator, cross-file comparison or platform rule.

It explains materiality without exaggeration.

It gives a narrow repair and does not redesign sound parts of the task.

It distinguishes task/golden defects from verifier defects and pipeline false positives.

Source basis used to build this document

RL_World_Finance_Expert_Onboarding_v6: expert role, five gates, fundamentally-sound standard, verifier quality, feedback formula, common finance traps, and stage-specific review expectations.

RL World Platform Quick Reference Cheat Sheet and Platform Overview: operational review loop, full-file review, artifact vs LLM-judge separation, and gate workflow.

Project_Omega_Guide_V5: benchmark design, headroom, source-file realism, golden requirements, verifier schema and rubric-quality rules, peer-review routing, and packaging standards.

Trainer_Review_Gate_Convergence_Report (prod data through 23 Sep 2026): latest verifier-platform rules and known non-converging QC failure modes.

Omega_Pod_Finance and Investment tracker: real peer-review decisions and feedback patterns.

Uploaded RL World task folders: completed and in-progress finance benchmark packages used for worked examples and evaluation cases.

V2 Additional Feedback Examples

11. Legacy verifier-count check conflicts with current platform rule

LOCATION → LLM judge / verifier-set check — requested minimum verifier count.

EVIDENCE → The current verifier platform guidance removes count targeting and directs reviewers to add/merge/split only for coverage and quality; the set already maps every prompt obligation to a unique owner.

IMPLICATION → Adding filler criteria only to reach a number can create overlap and non-atomicity without improving scoring.

EXACT FIX → REJECT the count-only remediation. Keep the current set size unless a specific uncovered obligation is identified.

12. Truncation: pipeline flag versus real incomplete range

LOCATION → Verifier v[N] — extraction/range condition.

EVIDENCE → The criterion fails merely when the extractor reports truncated=true; it does not identify a missing business record or an incomplete source population.

IMPLICATION → A correct deliverable can fail because of a pipeline token-budget event outside the business task.

EXACT FIX → Remove the truncated=true fail condition. If the actual business range omits records, repair that separate population defect instead.

13. Population completeness belongs in rubric text, not a filler mechanism

LOCATION → Verifier v[N] — population-selection criterion.

EVIDENCE → The task requires the complete source population, but the proposed remediation adds a filename/path or deterministic-count check rather than grading the selected IDs visible in the deliverable.

IMPLICATION → The check can pass/fail on mechanics unrelated to whether the substantive population is correct.

EXACT FIX → Keep a rubric verifier that PASSes only when the deliverable’s selected ID set equals the inlined authoritative set and FAILs on any omission or spurious ID; do not add a path/string-only check.

14. Prompt quantifier and rubric disagree

LOCATION → Prompt [sentence] and verifier v[N].

EVIDENCE → The prompt asks for “one” exception per entity while v[N] requires every exception in the population.

IMPLICATION → An obedient solver can satisfy the prompt and still fail the rubric.

EXACT FIX → Decide the intended scope at the prompt layer. If full-population coverage is required, change “one” to “each/all applicable” in the prompt and then align v[N]; otherwise narrow v[N] to the stated single-item obligation.

15. PowerPoint adjacency is not reliably visible to the text judge

LOCATION → Verifier v[N] — slide-layout/adjoining-text requirement.

EVIDENCE → The criterion infers that two text boxes are adjacent from extraction order, but the runtime does not guarantee that extracted text order preserves visual proximity.

IMPLICATION → A visually correct slide can false-fail, or a visually wrong slide can pass.

EXACT FIX → Rewrite the criterion around observable slide-specific labels/content or route the requirement to a renderer/layout-aware check; do not infer adjacency from text order.


[Table 1]

How these were prepared  The cases below come from real peer-review notes in the supplied Omega tracker. Long narrative notes were compressed into one-fix regeneration notes so the GPT learns the desired LOCATION → EVIDENCE → IMPLICATION → EXACT FIX structure.
