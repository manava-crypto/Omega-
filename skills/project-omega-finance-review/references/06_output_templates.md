# Output Templates

Paste-ready forms for every Project Omega gate. Fill the gate's template for every field the pasted form shows, from the files in hand, and return it inline in the chat: never a generic review essay, a file card, or review output written into the repository. Template A governs every note at every gate, B to F are the gates, and G is the escalation line. The Model Output Review, Golden Data and Sample Calibration forms carry lessons transferred from other gates, because no completed review of those gates is in the evidence.

## Reply shape

Verdict words: APPROVE/REJECT for artifacts and verifiers, AGREE/DISAGREE for LLM judge and Auto QC checks, TAKE/REJECT for each remediation item, PASS/FAIL for grades, PENDING INPUT where a needed file is missing, NOT VERIFIABLE where evidence cannot settle it.

If the upload does not match the pasted screen (task_id, revision, deliverable paths, verifier names), the first line says so and the reply stops. Otherwise a reply has up to four parts, in this order:

1. Lead, optional: one paragraph, two at most, ≤120 words, giving the verdict and the one or two findings that matter, the binding one first. A "why does it keep failing" diagnosis fits here in one paragraph.
2. Entries: one per platform field, in screen order, each headed by the on-screen name and the verdict word: "workbook_ltd_giveback_rollforward — REJECT." Fixed one-line-per-item lists (per verifier, per check, per file) are entries, not paragraphs.
3. "Optional: …", one line after the entries with at most three non-blocking items, each naming its verifier or file, or nothing. List a non-blocking fix once; when it starts propagating, it becomes a blocking note.
4. Escalation lines, template G. A Final Review reply then closes with its Overall line (template F).

A question with no form gets one paragraph, two at most. A request for names gets plain lists and nothing else; at Final Review, two lists, approved and rejected.

Working notes, never output: ownership and coverage maps, cross-file tie-outs, corner sheets, recompute tables, probe logs, the version-delta and position ledgers, the rejected-demand log, QC reconciliation, and any confidence grading of your own claims. Cut method narration, version histories, headers or bold labels inside entries, tables, code blocks, hedges and filler.

Before sending: entries equal the form's fields, every FAIL and every AGREE that takes or rejects a remediation item has a note, tallies come from the entries, no cross-reference or hedge words, no stray `|`, Fix: in every defect entry.

## A. Notes (every gate)

### Entry forms

APPROVE, or AGREE with a PASS where you found no defect: one sentence, ≤30 words, giving the evidence that settles it.

Defect entry (REJECT, DISAGREE, or AGREE with a FAIL): one paragraph, two at most, about 120 words, in this order:

- location and evidence: quoted text, sheet and cell, slide or figure;
- implication; for a verifier, the counterexample "A submission that … would FAIL/PASS because …";
- "Fix:" naming the artifact or verifier ID, a quoted locator and the exact change (what to delete, the replacement words or values, which conflicting version to keep). A verifier REJECT names its remedy, repair in place, split, merge or delete; before a merge or deletion it names the new owner of every obligation the removed text carried. The Fix closes with the ripple list: each other place the fact appears, with its replacement, or "no other occurrence (grep)".

Finding that belongs to another file: one sentence of evidence, then "Fix: No change required to this file for this check; the fix belongs in <file>."

Multi-item note: every item names its verifier ID or location and its change; with three or more separate items, bullet them. Each remediation item gets its own TAKE or REJECT, and a rejected item is named as not to be adopted: "Do not add the file-exists check proposed in item (1)."

PENDING INPUT: "<field> — PENDING INPUT: <file> is needed to answer this." Give no provisional leaning, and still answer the structural questions (routing, conflicts between checks, the judge's own counts). If the form forces a binary, answer it and say the basis is the judge's cited evidence.

NOT VERIFIABLE: for a truncated paste, quote the surviving fragment and ask for that check to be re-pasted. Given only a platform link, ask for the review-artifacts zip and the judge text verbatim. An extractor dependency is NOT VERIFIABLE plus an escalation line.

Changed verdict: once, in one sentence, "changed because <new evidence>", naming the exact check or verifier.

Auto QC rework: rewrite only the flagged notes and keep their verdicts unless the evidence changed.

### Wording rules

- Every note stands alone, because Auto QC grades each one in isolation and the regenerator acts on nothing else. Name the target yourself from the artifacts; never write "request the names" or "unactionable without more detail". No cross-references (above, below, earlier, last round, see the …, see chat, the fixes above) and no paragraph counts; locate text by quoting it.
- One definite instruction per item: no "consider", "optionally", "drop X if", "if the platform lets you", and no menus. A fallback whose branches are both stated may stay.
- Give the exact change, not a full replacement criterion, unless the user asks for one.
- When shortening, cut explanation, never conditions, fallbacks, scope limits, "do not" clauses, IDs, locators or anchor values.
- No two notes may conflict on the same requirement or value.

### Examples

Verifier REJECT (CRW; fix applied at v3):

> wb_exception_log_source_choices — REJECT. "FAIL … if a different lot is named as the stale-taxonomy exception" collides with Legacy Positions, where 18 rows carry an Effective Through date before 18-Sep-2026: BL-6D3A9E plus six NBAM-SM-5.0 rows and eleven NBAM-SM-5.1 rows. A submission that names every stale row would FAIL a core verifier for being thorough. Fix: repair in place; change the clause to "if BL-6D3A9E is not identified among the stale-taxonomy exceptions" and leave everything else as drafted.

Judge text stamped on the wrong file (CLO; adapted from the submitted note):

> Realism, Larkspur_2021-3_Indenture_and_Supplements.pdf — DISAGREE. The only defect the explanation cites, the 226 Daily Prices rows outside the same-row bid–ask, sits in the surveillance workbook, and the explanation confirms no defect in this PDF. Fix: No change required to this file for this check; the fix belongs in Larkspur_Collateral_Surveillance_2026-09-18.xlsx.

Missing files (HAL; the user responded by uploading):

> I can't give v2 platform answers yet: the only new file is task_design.json, and it is identical to v1. Every source-file and instruction.md check stays PENDING INPUT until the v2 files are uploaded.

## B. Trainer Review

Answer only the sub-gate pasted, every field in screen order, and fix every finding in one pass. On a later version where nothing changed, say so first and re-issue the prior notes. Name any source defect first in the lead; its note sits on the artifact where it originates, never patched by rewriting a verifier.

Task Design. One entry per judge check the form shows (scenario realism; expert judgment and headroom; no external lookup; completable on a computer; anomalies planned but not labelled), then "Task Design — APPROVE." or REJECT with its note. Judge it on its own content, never against verifier scope; a difficulty or effort-label mismatch is a metadata note, not a REJECT.

Source Data, one block per file in screen order. Answer each check (realism; no literal expected output; source does not contain the answer; cross-file consistency; on-topic; anomalies not labelled) on that file's own evidence: judge text repeated across files still gets a per-file verdict, and cross-file means between files. A leak the transcription test finds is a DISAGREE on that file's leakage check with the Fix in that note, never "AGREE as scoped". Close the block with "<filename> — APPROVE." or REJECT with every required change in its Fix; where rows are regenerated, say whether graded or determination-date rows move and whether the golden needs recomputing.

Prompt. Each check (solvable from sources alone; aligned with task design; two professionals would converge; reads like a real workplace request; constraints stated; deliverables, paths, formats and audiences named), then "instruction.md — APPROVE." or REJECT. A convergence entry names each defensible reading, its headline figure and the quoted verifier phrase that accepts it.

Verifiers. One entry per verifier in screen order. A REJECT carries its counterexample and remedy (template A); a weight change is a relabel inside that verifier's note, never a deletion or fold. A coverage gap goes in the entry for the judge's coverage check, naming the verifier to add, its artifact, core or secondary, and its PASS and FAIL conditions. Where the platform asks for pasteable wording, give one line per field, only for fields that change:

- Exact change: the quoted clause → the replacement words or values. A full criterion only if the user asks, ending with the boolean-verdict instruction if the live schema expects one.
- Description / how: the replacement text.
- Why: the replacement text.
- Importance: core or secondary.

LLM judge checks. One entry per check in screen order (coverage of instruction obligations, keyword-only hacking, one atomic concept, double-grading, rubric-first policy, anchoring, robustness and the rest the form shows). The verdict follows your own finding, and each remediation item gets its own TAKE or REJECT inside the entry; valid items survive inside a DISAGREE. A REJECT for conflict names the conflicting check and adds an escalation line. Where the judge's described work did not happen (a miscount, a partial read, a fake it claims to have graded), say so in that entry. A demand you have already rejected gets the same DISAGREE with the same instruction quote. Recommend override only once corrections leave a stale or platform-limit failure.

### Filled entries

Source Data file (CLO; validated: "source artifacts are all passing now"):

> Larkspur_Collateral_Surveillance_2026-09-18.xlsx — REJECT. Daily Prices carries 226 observations across four assets whose composite Price (%) sits outside the same-row Bid (%) and Ask (%), a generation fault in valuation inputs. Three shared Asset IDs also carry different 2026-09-18 prices in Daily Prices and Collateral Snapshot, contradicting the Read Me linkage and creating a third, undeclared anomaly. Fix: regenerate the affected rows so each Price (%) falls within its same-row bid–ask, and align the three Snapshot prices with the 2026-09-18 Daily Prices. Before regenerating, check whether any affected row is a 2026-09-18 determination-date row; if so, recompute the golden and re-tie the trustee bridge.

Clean AGREE on planted difficulty (SPV; matched the platform PASS):

> Anomalies not trivially labelled — AGREE. The duplicate JRN-4C7D92B1A8E6 and JRN-91A7C4E52B60 rows and the PEX-44 row are formatted like their neighbours; finding them needs bank trace BANK-R-C698FAEA and the GL map.

Verifier REJECT, duplicate gate (CLO; adapted from the submitted note, gate completed):

> wb_acp_bridge — REJECT. The rubric fails a bridge that "ends outside $468,000,000-$473,000,000", the same gate wb_corrected_acp_oc applies to the same workbook. A submission with one wrong ACP would FAIL both core rubrics for one defect. Fix: repair in place. Keep the $467,493,000 / 119.87% starting point, the separately labelled Excess CCC threshold and Meridian steps, and the single-unexplained-difference FAIL; end the bridge at the workbook's own corrected ACP and delete the $468M–$473M endpoint condition, because wb_corrected_acp_oc owns the value.

Judge check, finding taken and remedy rejected (REI; adopted at v6):

> Verifier rubrics resist keyword-only hacking — AGREE. paper_references_workbook_calculations passes a one-sentence paper that only names the tabs. TAKE the finding; REJECT the remedy of importing the deck's USD 840–1,070m band, which would give that value a second owner. Fix: in paper_references_workbook_calculations, PASS only if the paper ties at least two workbook references to specific conclusions the paper itself states; add to FAIL "or if the workbook references are free-standing pointers not attached to any conclusion the paper draws". Do not import the deck's USD 840–1,070m band.

## C. Model Output Review (lessons transferred)

Per attempt, in screen order:

1. Attempt summary, one paragraph: the approach, the decision or conclusion, the strongest aspect and the most material defect.
2. Per deliverable, named by its file path, one entry per axis: instruction-following, correctness, completeness, format and deliverable compliance, hallucination and fabrication, data integrity. A clean axis reads "<axis> — No issues." Each issue is its own numbered entry, with severity where the form asks (Critical, Major, Minor, Cosmetic), location, evidence, implication and a Fix: giving the exact correction, closing with the other artifacts the same error reaches. Keep analytical root causes apart from presentation.
3. Cross-file coherence: one entry per disagreement among workbook, memo, deck and reasoning, naming the authoritative value and every place it must be corrected.
4. Overall assessment, one paragraph: did the attempt answer the ask, are its conclusions sound, do its outputs cohere as one solution.

Issue numbers carry forward into the golden fix log. A model failing a verifier is evidence about the model unless the requirement is not a reasonable reading of the prompt; only then is it a Verifier note with its counterexample. When the attempts have not arrived, every entry that needs them is PENDING INPUT; the CLO review, with no files in the container, marked them so rather than inventing entries.

Example (LHF Model 1, from the Final Review evidence):

> output/2025_fee_close_model.xlsx, correctness — Issue 1. Perf_Fee_Calc!C66 =SUM(S5:S16) produces the recorded redeemed-portion result from a month-end proxy instead of a test computed at each redemption; the rest of the performance-fee mechanics match the golden. The one defect fails both workbook_performance_fee_mechanics and workbook_performance_fee_redeemed_portion. Fix: replace the proxy at Perf_Fee_Calc!C66 with a redeemed-portion test computed by formula at each redemption date; the Final Review evidence did not cover Model 1's memo, so the ripple to it is NOT VERIFIABLE.

## D. Golden Data (lessons transferred)

Entries: one per deliverable, then the overall verdict.

- APPROVE: "<deliverable path> — APPROVE." plus at most 30 words: it passes every verifier, its key chain recomputes from source, and whether cached values replaced recalculation.
- REJECT: a template A note whose Fix names the deliverable, a quoted locator (sheet and cell, section, slide) and the exact correction.
- Overall: "Golden Data — APPROVE." or REJECT naming the deliverables. Where the golden passes a verifier you reject, add "The golden passes <verifier>, so the flaw lies in grading other submissions, not in the golden."

Fix log. You correct the golden only here and in Sample Calibration E5, and only where it is genuinely wrong. One paragraph per fix, in this order: the issue it closes (carried-forward issue number, or the verifier that failed on the golden) → root cause in the source or output logic → the change (file, location, old → new) → downstream propagation (each calculation, chart, table, recommendation and narrative line updated) → independent verification (recompute, cross-foot or authority check) → regression check (what was re-read) → status: FIXED, NOT FIXED or ESCALATE.

Consistency checklist (working; also run at Sample Calibration and Final Review):

- Brief: every deliverable present, named, formatted and addressed to its audience; the Expert Solution folder holds only the solution and its reasoning file; the reasoning shows step-by-step logic, labelled intermediate values and source linkage; no required convention lives only in the reasoning; every figure and claim checked by hand.
- Internal: narrative matches tables, every superlative, comparative and percentage included; workbook, memo and deck agree; displayed totals equal their displayed parts and rounded displays still sum; each percentage or ratio is the quantity its label claims; rates sit on the matching base; technical and accounting labels are accurate; causal claims are supported; what the record does and does not disclose is treated consistently; every figure traces to a source or a shown derivation.
- Presentation: stated, consistent precision with no raw floats; no empty TOC, unpopulated heading or placeholder; no default-named, blank or working sheets; no blank trailing pages; tables, headings and sections in professional order.

Example (LHF golden, built from the Final Review evidence):

> output/2025_fee_close_model.xlsx — APPROVE. Key figures are formula-driven and recompute from source (management fee $5,078,354, give-back $0, adjustment −$1,561,646); recalculation was impossible in the sandbox, so cached values were read with the formulas.
>
> output/controller_fee_conclusion_memo.docx — APPROVE. It ties to the workbook on every key figure, including the $0 performance fee for every class.
>
> Golden Data — APPROVE.

## E. Sample Calibration (lessons transferred)

Grade every attempt against every verifier yourself, with evidence, before the judge's verdict is shown; then reconcile. Sections in order:

E1. Attempt grading, one line per attempt and verifier: "Attempt 2, <verifier_id> — FAIL. Judge PASS; DISAGREE." then the deciding cell, sentence or slide. A PASS carries at most 30 words of evidence. A FAIL or a DISAGREE carries a note: what is wrong, the correct value or element, and why the judge is wrong, or, if it is right, "changed because <new evidence>". Apply the template C model false-fail test before calling a verifier unfair.

E2. Calibration questions, five one-line answers per verifier, each choosing the platform's option and giving the reason:

1. Source: required by the prompt (quote the snippet), by the source data (name the files), implicitly required (why), or required nowhere and so unfair (why).
2. One thing: yes, or no with what to split by the coupling test.
3. Clear bar: yes, or no with the ambiguity stated as a counterexample.
4. Grader has what it needs: yes, or no with what must be inlined.
5. If it fails: critical (the answer is wrong without it) or nice to have (why).

E3. Coverage gaps, one entry per gap: the target artifact the contract names, the new verifier's PASS and FAIL conditions, where the obligation comes from (prompt quote, source file, implied), and critical or nice to have. None: "No coverage gaps identified."

E4. Redundant verifiers, one entry per overlap: the verifiers, the single wrong value that would fail both on the same artifact, and the remedy, either a merge naming the surviving owner of every obligation or an inward boundary sentence on the non-owner ("This criterion assesses only X; ignore any error in Y when scoring it."). Verifiers that share amounts but grade different obligations are not an overlap. None: "No redundant verifiers identified."

E5. Golden fixes, one template D fix-log entry per fix, opening with the verifier that failed on the golden, once you have decided whether the golden or the verifier is wrong. None: "Golden data passes all verifiers — no fixes required."

E6. Verifiers flagged for regeneration, one template A defect note per verifier: the reason (vague, overlapping, unfair, coverage gap, runtime impossible), the counterexample the probe battery found, and the Fix. A judge that flips between attempts needs a sharper anchor, not a wider band. Extraction truncation is an escalation; a population range that misses part of the business population is a defect. None: "No verifiers flagged for regeneration."

E7. Golden consistency, from the template D checklist: "Golden consistency check — PASS." or FAIL naming the failed item, with its fix logged in E5.

E8. Summary for Final Review, one line each:

- Verifiers passed by the golden: N.
- Verifiers failed by the golden, now fixed: N.
- Verifiers flagged for regeneration: N, named.
- Coverage gaps added: N.
- Redundant overlaps identified: N.
- Golden consistency check: PASS, or FAIL with the item.
- Judge panel: config.models as recorded, and any judge-panel seat change.
- Key decisions: one line per non-obvious grading or calibration call.

No calibration run is in the evidence, so this template has no filled example.

## F. Final Review

A verifier rejection ends the task, so set the bar once and block only when:

- (a) the rubric misstates a governing term;
- (b) a realistic submission is mis-graded, shown on a supplied output or on a concrete submission under an accepted reading;
- (c) the golden fails a sound verifier, once you have decided which side is wrong.

Everything else gets an optional line: stale figures that change no result, hypothetical overlap or bundling, reasonable placement or format readings, extractor observability (NOT VERIFIABLE plus escalation), weight or difficulty labels, mechanical source slips, and planned difficulty.

Re-verify every claimed fix in the current files and mark each prior failure verified fixed, false positive or still open in your working notes; a still-open item reaches the output only as a note that meets the bar. Judge in order Task Design, Source Documents, each verifier, Golden; enter them in the form's screen order:

1. Lead: one line with task_id, revision and the deliverables reviewed.
2. Task Design: one short paragraph, judged on its own terms, never against verifier scope. APPROVE when the scenario is realistic, deliverables have clear purposes, sources are mapped, and anomalies are realised and carried into instruction.md.
3. Source Documents: one short paragraph, through the planned-difficulty test, with the cover and notes sheets and the prompt's caveats read first.
4. Verifiers: one line each, "<name> — APPROVE.", with a template A defect note directly under each REJECT.
5. Golden Data: one short paragraph applying the template D APPROVE test and grading-flaw sentence.
6. The optional line and any escalation lines.
7. Close with "Overall REJECT, because one verifier rejection ends the task: <names>." or "Overall APPROVE." If a REJECT rests on a branch no submission took, say so in one sentence and keep it.

Example (LHF v24, the round-3 answer the user accepted, restated to this template; other verifier lines omitted):

> lh-finance_and_insurance-financial_and_investment_analysts-20260914-103056 v24; deliverables output/2025_fee_close_model.xlsx and output/controller_fee_conclusion_memo.docx.
>
> Task Design — APPROVE. Judged on its own terms, the design sets out a realistic fee-close scenario, names two decision deliverables with clear purposes and maps the four source packages. All three planned anomalies are realised in the sources and carried into instruction.md; prescribing the Class C H1 treatment is a prompt-layer choice, not a design defect.
>
> Source Documents — APPROVE. The HWM Trajectory sheet says its references are "retained for chronology; class capital-account detail and allocation components remain in the companion capital-account package", and the prompt accepts a NAV-package figure only if it reconciles, so solvers rebuild high-water marks from the capital package and the register, as the golden and both models did. That is planned difficulty. ACT-7B3F9D remains the only record of 136 with a blank Controller approval and the same preparer and releaser.
>
> workbook_performance_fee_class_entitlement — APPROVE.
>
> workbook_ltd_giveback_rollforward — REJECT. The criterion applies "the 35% after-tax cap only if gross excess is positive", but Governing Documents Part V 5.3 allows the cap "only where the GP documents taxes actually paid… Without documentation of taxes paid, the required return is the gross excess", and the records hold none. A submission capping the give-back at about $428,000 on the ~$659,000 reading would PASS, and a correct gross answer could FAIL. Fix: repair in place. Replace the cap language with "treats the 35% after-tax cap as available only where the GP documents taxes actually paid (none are in the records, so any positive excess is due gross)"; in reading (ii), change "subject to the 35% cap" to due gross; add to FAIL "or the cap applied, or used to reduce or force zero, without documented taxes paid". memo_giveback_conclusion carries the same cap language and takes the same replacement.
>
> Golden Data — APPROVE. The golden passes every verifier and its key chains recompute from source, give-back E22 = MAX(0, $17,840,000 − $17,840,000 − 0) = $0 included; recalculation was impossible in the sandbox, so formulas were read with their cached values. It passes all three rejected verifiers, so their flaws lie in grading other submissions, not in the golden.
>
> Optional: workbook_performance_fee_class_entitlement's preamble gives the Class R HWM-only excess as $139,300; it should read $202,616 (17.5% × ($38,967,718 − $37,809,911)), and the pass test is still $0 for every class.
>
> Overall REJECT, because one verifier rejection ends the task: workbook_performance_fee_mechanics, workbook_ltd_giveback_rollforward and memo_giveback_conclusion. Every submission so far concluded a $0 give-back, so the two cap rejections rest on a branch no submission took; they stand because the rubric misstates Part V 5.3.

## G. Escalation

One line per escalation, addressed to the pod lead or engineering; these are the only lines in any reply that contain `|`:

ESCALATE TO: <pod lead / engineering> | ISSUE: <contradictory automated checks / runtime or extractor limit / conversion bug / unclear priority> | EVIDENCE: <the check and the artifact> | WHY THE FORM CANNOT RESOLVE IT: <one sentence> | RECOMMENDED ACTION: <one sentence>

A source defect is never only an escalation: a regenerator acts on notes and an escalation needs a human, so it is a blocking note on the file that carries it.

Example (ACL; accepted):

> ESCALATE TO: engineering | ISSUE: possible extractor truncation or dropped cached values on full-workbook extraction | EVIDENCE: the 38-loan and carry-forward rubrics need every loan and stored values visible | WHY THE FORM CANNOT RESOLVE IT: instruction.md fixes no tab names, so neither rubric can be sheet-scoped without an unstated requirement | RECOMMENDED ACTION: raise the extraction size limit and include cached values for these two verifiers.
