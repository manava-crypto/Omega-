# Real Feedback Examples

Notes in the exact form you return. Part A rewrites peer-review notes from the Omega Pod finance and investment tracker; Part B collects notes the platform, Auto QC or the user accepted or validated in the September–October 2026 sessions. Copy the shape and the evidence discipline, never the figures. Task keys (LHF, CLO, HAL, ACL, REI, CRW) are defined in `07_failure_patterns_and_lessons.md`; gate templates are in `06_output_templates.md`.

## The form

Head each entry with the on-screen name and verdict word. Every defect note (REJECT, DISAGREE, or AGREE with a FAIL) stands alone and ends with "Fix:" naming the artifact or verifier ID, a quoted locator and the exact change (what to delete, the replacement, which conflicting version to keep). Defect entry: one paragraph, two at most, about 120 words, ordered evidence with locator → counterexample → Fix:. Bullets only for three or more separate edits.

Beyond the form, the accepted notes share four habits: they prove the defect with a calculation, a quoted governing clause, a cross-file comparison or a platform rule; they state the consequence as one concrete mis-grade, without exaggeration; they repair narrowly and leave sound parts as drafted; and they route the defect to the layer where it originates (source, prompt, golden, verifier or pipeline).

Lines beginning "Reviewer:" are guidance for you and are never pasted. In Part A, v[N] and bracketed text stand for the real verifier ID and quoted sentence, which every real note must carry. Judge-check notes below open with the verdict word alone because the on-screen check name was not recorded; in a reply, head each with the check's on-screen name.

## Part A — Tracker examples

### 1. Source workbook looks populated but extracts blank (Source Data)

02_Rent_Roll_and_Lease_Abstracts.xlsx — REJECT. Annual base-rent cells H6:H17 and totals D20 and H20 are formulas with no cached values, so text extraction shows blanks even though the adjacent SF and rent/SF columns allow reconstruction; the solver and the grader may receive an incomplete source, and different systems can reach different results. Fix: recalculate and save the workbook so H6:H17, D20 and H20 carry current cached values; do not change the underlying lease economics.

Reviewer: at Final Review, formulas without cached values are a mechanical source slip and get an optional line, not a REJECT.

### 2. Reasoning arithmetic does not support the stated multiple (Golden)

Reasoning.docx — REJECT. The equity-multiple calculation states "$27,583,126 / ($19,181,250 + $1,480,903) = 1.37x", but that division gives 1.3350x; the positive-distribution numerator is $28,211,430, which gives about 1.37x. The final answer is right, but the audit trail is mathematically wrong and cannot support it. Fix: in the equity-multiple calculation, replace $27,583,126 with $28,211,430 and show the four contributing positive distributions so the reasoning ties to the workbook.

### 3. Source file hands over the answer (Source Data)

ytd_debt_amortization_and_account_map.xlsx — REJECT. The workbook carries "Supported 04/30 Balance", an April component split, an "Unsupported Difference Flag" and a support index stating close handling. These fields pre-solve the reconciliation, so a solver can copy the graded results instead of deriving them, and the intended expert reasoning and headroom disappear. Fix: delete the supported-balance, pre-solved component, exception-flag and close-handling answer fields; keep only the raw records needed to derive them.

Reviewer: if the judge's leakage check passed this file, DISAGREE with it and carry the same Fix in that note.

### 4. General-ledger running balance is mechanically wrong (Source Data)

april_2025_qbo_loan_liability_gl_detail.csv — REJECT. The running-balance field equals each row's own amount instead of the cumulative account balance on 107 of 140 rows; the first failure shows -147.38 where the cumulative balance should be 122.09. No reviewer can rely on the record, and any tie-out that uses the field is corrupted. Fix: regenerate the running balance as a true per-account cumulative total, preserving the original transaction amounts and order.

### 5. Golden workbook and memo disagree on a launch condition (Golden)

Golden workbook, launch-conditions tab — REJECT. For the Iloilo corridor, the memo requires an executed distribution-utility connection agreement before energization, but the workbook's launch-conditions tab omits that condition, so the package sets two different go-live standards for the same corridor. Fix: add the executed connection agreement as an explicit Iloilo launch condition on the launch-conditions tab, matching the memo; do not change the memo rule.

### 6. Verifier imposes structure the prompt never asks for (Verifier)

v[N] — REJECT. PASS requires raw source tabs and owner-provenance fields, but instruction.md asks for neither, so a faithful, materially correct workbook fails on an invented implementation requirement. Fix: delete the raw-source-tab and owner-provenance conditions and grade the underlying traceability or outcome visible in the deliverable.

Reviewer: decide the layer before writing. If the business task genuinely needs those structures, the defect is in the prompt: add them to instruction.md and leave v[N] as drafted. At Final Review, a requirement that is a reasonable reading of the prompt is not beyond it.

### 7. Verifier grades a property the judge cannot observe (Verifier)

v[N] — REJECT. The criterion requires live formulas, Excel Table objects or named ranges, but the judge scores extracted content, which carries no Table objects or named ranges and is not confirmed to expose formula strings, so a correct workbook can false-fail on a property the judge cannot observe. Fix: in v[N], delete the Table-object and named-range conditions, grade the anchored values and labels the extraction shows, and add to the formula-liveness condition "if the extraction does not expose formula strings, judge on the anchored outputs alone"; do not grade an invisible property.

Reviewer: mark the formula dependency NOT VERIFIABLE and route any genuine need for Tables or named ranges to a workbook-aware check, both through a one-line escalation to engineering. At Final Review, extractor observability is NOT VERIFIABLE plus that escalation, never a REJECT.

### 8. Inlined anchors flagged as answer-key leakage (LLM judge check)

DISAGREE. The check treats the expected values inlined in v[N] as answer-key leakage, but the solver receives only the prompt and source data and never sees verifier prompts. The inlined accepted values are what make a single-artifact rubric self-contained; removing them would leave v[N] vague or ungradeable without reducing any real leakage. Fix: REJECT the remediation and keep v[N]'s inlined anchors as written.

Reviewer: write this only after recomputing each anchor from source and confirming the rubric accepts every defensible value; a wrong or single-path anchor is a verifier defect in its own right.

### 9. Conversion banner read as source content (LLM judge check)

DISAGREE. The check cites the phrase "degraded best-effort text extraction" in CFO_Correspondence_Q2_2025.docx, but case-insensitive searches of the document XML and the task folder find no such phrase; the string comes from the conversion fallback, so failing the file would reject a sound source for a pipeline artifact. Fix: No change required to this file for this check; the banner belongs to the conversion pipeline and goes to pipeline/QC as an escalation, so make no source-file edit.

### 10. Prompt does not identify the full evidence set (Prompt)

instruction.md — REJECT. The working folder holds source documents the prompt never names or otherwise brings into the evidence set, so a solver cannot tell whether they are required evidence, optional context or stray packaging, and grading becomes unfair. Fix: name, by filename, every required source in the prompt's evidence description; remove each unrelated file from Source Documents through its own Source Data note.

Reviewer: once the source set is final, re-check verifier coverage against it and file any change as a note on the verifier concerned, since one note repairs one artifact.

### 11. Truncation flag used as a business FAIL (Verifier)

v[N] — REJECT. The extraction-range condition fails whenever the extractor reports truncated=true, without identifying a missing business record or an incomplete source population, so a correct deliverable fails on a pipeline token-budget event outside the business task. Fix: delete the truncated=true FAIL condition, and do not replace it with a file-existence, filename or format check.

Reviewer: check the business range against the full source population separately; a range that omits records is its own population defect with its own note, never a reason to keep the truncation test.

### 12. Population completeness belongs in rubric text (LLM judge remediation)

AGREE. TAKE the population requirement; REJECT the instrument. The task requires the complete source population, but the proposed remediation adds a filename/path check or a deterministic count check instead of grading the selected IDs visible in the deliverable, so v[N] could pass or fail on mechanics unrelated to whether the population is right. Fix: rewrite v[N] so it PASSes only when the deliverable's selected ID set equals the inlined authoritative set and FAILs on any omission or spurious ID; do not add the path, string or count check.

### 13. Prompt quantifier and rubric disagree (Prompt)

instruction.md — REJECT. "[quoted sentence]" asks for "one" exception per entity, while v[N] requires every exception in the population, so an obedient solver satisfies the prompt and still fails the rubric. Fix: in that sentence, change "one" to "each applicable"; v[N] already requires every exception and stays as drafted.

Reviewer: decide the intended scope at the prompt layer before writing. If the task wants a single item per entity, the note goes on v[N] instead: narrow it to the stated single-item obligation and leave the prompt unchanged.

### 14. Slide adjacency inferred from extraction order (Verifier)

v[N] — REJECT. The slide-layout criterion infers that two text boxes are adjacent from extraction order, but the runtime does not guarantee that extracted text order preserves visual proximity, so a visually correct slide can false-fail and a visually wrong one can pass. Fix: replace the adjacency condition with a test of the slide-specific labels and content the extraction shows; do not infer adjacency from text order.

Reviewer: route any genuine layout requirement to a renderer- or layout-aware check through a one-line escalation.

## Part B — Accepted notes, September–October 2026

Verbatim or near-verbatim from submitted turns, adjusted only to the current note form (length, entry heading, quoted locators); no condition was removed. Each heading gives the task key and what happened to the note.

### Final Review

#### 15. Double penalty shown on a real output (LHF v24; accepted)

workbook_performance_fee_mechanics — REJECT. The clauses "accept a separate recorded redeemed-portion result of $0 that is formula-linked to the missing-valuation input…" and the FAIL limb "or an indicative redemption-date proxy is used to produce the recorded redeemed-portion result" grade what workbook_performance_fee_redeemed_portion already owns. Model 1's mechanics otherwise match the golden, yet it fails both verifiers for one defect: Perf_Fee_Calc!C66 =SUM(S5:S16), a month-end proxy. Fix: delete both clauses and end the criterion with "The redeemed-portion test must be computed by formula at each redemption (it may be labeled an indicative cross-check); how the recorded redeemed-portion result is derived is graded only by workbook_performance_fee_redeemed_portion."

#### 16. Governing term misstated (LHF v24; accepted)

workbook_ltd_giveback_rollforward — REJECT. The criterion applies "the 35% after-tax cap only if gross excess is positive", and reading (ii) makes the give-back "subject to the 35% cap", but Governing Documents Part V 5.3 allows the cap "only where the GP documents taxes actually paid… Without documentation of taxes paid, the required return is the gross excess". No tax documents exist, so a wrongly capped give-back of about $428,000 passes on the ~$659,000 reading and a correct gross answer can fail. Fix: replace the cap language with "treats the 35% after-tax cap as available only where the GP documents taxes actually paid (none are in the records, so any positive excess is due gross)"; make reading (ii)'s give-back due gross; add to FAIL "or the cap applied, or used to reduce or force zero, without documented taxes paid".

Reviewer: memo_giveback_conclusion carried the same defect and was also rejected; its entry carries this Fix written out in full, never "the same fix applies", because each entry is pasted alone.

### Trainer Review — Source Data

#### 17. File REJECT with the defect on its carrier (CLO; validated: "source artifacts are all passing now")

Larkspur_Collateral_Surveillance_2026-09-18.xlsx — REJECT. Daily Prices carries 226 observations across four assets whose composite Price (%) sits outside the same-row Bid (%) and Ask (%), a generation fault in valuation inputs. Three shared Asset IDs also carry different 2026-09-18 prices in Daily Prices and Collateral Snapshot, contradicting the Read Me linkage and creating a third, undeclared anomaly. Fix: regenerate the affected rows so each Price (%) falls within its same-row bid–ask, and align the three Snapshot prices with the 2026-09-18 Daily Prices. Before regenerating, check whether any affected row is a 2026-09-18 determination-date row; if so, recompute the golden and re-tie the trustee bridge.

#### 18. Label that states the outcome (HAL; literal-output check, not flagged by Auto QC)

DISAGREE. Carrier Demand Build A26/E26 and Data Dictionary B45 label the $44.0M input "Corrected legacy case", which states the outcome of the reconciliation the solver must establish. Fix: change A26 and B45 to "Appointed actuary case reserve", E26 to "Source: HIL-AR-2026Q2; case reserve at 2026-06-30", and C45 to "Separately sourced actuarial case reserve"; leave the value at $44.0M.

#### 19. Anomaly mechanism named in the source (HAL; labelling check, trimmed)

AGREE. In the PDF, Exhibit I uses the task design's own phrase, "claim records re-keyed during migration"; Exhibit F singles out "currency treatment or any duplicated record" on 2026-08-29, before the full RMIS run existed (2026-09-02); and Schedule A §2.1 names "a policy-inception rate", the exact wrong rate used for B-0718-B. Fix:
- In Exhibit F, replace that sentence with "HIL does not concede that any loss-run field is a reliable basis for a collateral calculation until it has been reconciled to the TPA run and the actuarial record".
- In Exhibit I, replace the phrase with "the claim-level support has been reconciled to the legacy TPA loss run".
- In Schedule A §2.1, replace the rate sentence with "No other rate or rate date may be substituted".
- Keep every other WM/Reuters statement.

#### 20. Cross-file conflict, naming the version to keep (HAL; post-Auto QC form)

DISAGREE. Table 15 shows the actuary report still awaited on 2026-08-05, while PDF Exhibit E records HIL-AR-2026Q2 delivered on 2026-07-20. Fix: keep the PDF's date and change the three cells of the docx Table 15 row to "Appointed actuary report", "HIL-AR-2026Q2 issued 2026-07-16, valuation 2026-06-30" and "Provided with response"; do not change the PDF.

### Trainer Review — Prompt

#### 21. Named artifact absent from the source (REI; accepted, instruction.md then passed)

instruction.md — REJECT. The prompt directs the solver to "the OPTIMIZATION ORDER in §9.4", but §9.4 ("Initiative prioritization and deferral") closes with a callout headed OPTIMIZATION RULE: a single unranked objective with three unordered criteria. There is no order to apply. Fix: change "OPTIMIZATION ORDER in §9.4" to "OPTIMIZATION RULE in §9.4", and replace "do not introduce personal weights or substitute a different preference" with "do not substitute a different objective; where the rule's criteria conflict, state the trade-off applied and why."

### Trainer Review — Verifiers

#### 22. FAIL clause that punishes a thorough answer (CRW; fix applied verbatim at v3)

wb_exception_log_source_choices — REJECT. "FAIL … if a different lot is named as the stale-taxonomy exception" collides with Legacy Positions, where 18 rows carry an Effective Through date before 18-Sep-2026: BL-6D3A9E plus six NBAM-SM-5.0 rows and eleven NBAM-SM-5.1 rows. A correct, thorough answer can therefore fail a core verifier. Fix: change the clause to "if BL-6D3A9E is not identified among the stale-taxonomy exceptions" and leave everything else as drafted.

#### 23. Source fix that broke a verifier fact (CRW; fix applied at v3)

deck_combined_platform_standard — REJECT. The preamble "Northlake 0/5/10 days; Bellwether 5/10/20 days" was true only of the eight-row v1 Mandate Register. On the twelve-row v2 register both firms span {0, 5, 10, 15, 20}, so a solver who reads the whole register fails. Fix: scope the preamble to the six Crownmere-holding accounts (NL-IG-1047 0, NL-INS-7731 5, NL-LDI-2208 10; BW-OPP-4180 5, BW-LONG-0622 10, BW-CORE-0315 20). Rubric text only; keep the four added mandates.

#### 24. Duplicate value gate (CLO; submitted, gate completed)

wb_acp_bridge — REJECT. The rubric fails a bridge that "ends outside $468,000,000-$473,000,000", the same gate wb_corrected_acp_oc applies to the same workbook, so one wrong ACP fails two core rubrics. Fix: keep the $467,493,000 / 119.87% starting point, the separately labelled Excess CCC threshold and Meridian steps, and the single-unexplained-difference FAIL. End the bridge at the workbook's own corrected ACP and delete the $468M–$473M endpoint condition; wb_corrected_acp_oc owns the value.

#### 25. One owner per value (ACL; Auto QC validated)

wb_exceptions_log_all_exceptions — REJECT. It re-grades the FX restatement to $70,248,785.00 and the Riverside correction to $17,250,000, both owned by wb_gl_reconciliation_fx_restatement. Fix: keep the full correctness test for Hollis (rating 7), Linden ($21,400,000) and the v2024.2→v2025.1 switch. For FX and Riverside, require only documentation (wrong value, corrected value, source reference), and state inside the criterion that this criterion assesses documentation only for those two items.

#### 26. Enumerated anchors instead of a wider band (CRW; applied at v5)

wb_comparable_event_price_scaling — REJECT. ±0.3pp of −2.96% fails defensible readings on knife edges: a D−5 base gives −2.6502% (outside by 0.0098pp), and the trough gives −3.2642% from D−10 (outside by 0.0034pp). Fix: accept a D+5 change within ±0.3pp of −2.96% (pre-event), −2.79% (D−10 base) or −2.65% (D−5 base), or a trough-anchored −3.26% (D−10 = 100), and keep excluding a D0 baseline (−1.34%). Correct the preamble to "97.21 at D+5, with the trough at 96.74 on D+8".

### LLM judge checks

#### 27. Agree with the finding, reject the remedy (REI; adopted at v6)

AGREE with the finding, REJECT the remediation. paper_references_workbook_calculations passes a one-sentence pointer to the tabs. Importing the deck's USD 840–1,070m band would duplicate ownership. Fix: PASS only if the paper ties at least two workbook references to specific conclusions the paper itself states; add to FAIL "or if the workbook references are free-standing pointers not attached to any conclusion the paper draws".

#### 28. Take the substance, reject the instrument (CRW v6; package approved)

AGREE. Taking the substance, rejecting the instrument: the real defect in wb_buyer_capacity_imbalance is a branch gap, not band width. PASS lists three totals while FAIL says "differ … without explanation", so an explained unlisted total satisfies neither. Fix: add to PASS "or a different total the workbook derives from the Buyer Eligibility inputs and explicitly justifies, with the derivation shown", and keep ±0.01. For memo_execution_governance_scope, replace "more than about 150 words" with "a dedicated heading or three or more consecutive paragraphs on an out-of-scope theme fails".

#### 29. Refusing to invent facts (REI v8)

DISAGREE on the competing-claims limb. The pack's three trusts (TR-USD-61KF, TR-CAD-774Q, TR-USD-92MP) carry no disclosed competing claim, so "any competing claims" is a condition to check and find absent. A verifier demanding the analysis would force the solver to invent one. Fix: REJECT this limb; no change.

### Escalation

#### 30. Extraction limit the form cannot resolve (ACL; accepted)

ESCALATE TO: engineering | ISSUE: possible extractor truncation or dropped cached values on full-workbook extraction | EVIDENCE: the 38-loan and carry-forward rubrics need every loan and stored values visible | WHY THE FORM CANNOT RESOLVE IT: instruction.md fixes no tab names, so neither rubric can be sheet-scoped without an unstated requirement | RECOMMENDED ACTION: raise the extraction size limit and include cached values for these two verifiers.
