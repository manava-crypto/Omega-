# Output Templates

Paste-ready forms for every Project Omega gate. Fill the gate's template for every field the pasted form shows, from the files in hand, and return it inline in the chat: never a generic review essay, a file card, or review output written into the repository. Template A governs every note at every gate, B to F and H are the gates (H is External QC, the stage after Final Review), and G is the escalation line. The Model Output Review and Sample Calibration forms follow the platform screens seen in late October 2026; the Golden Data form still carries lessons transferred from other gates.

## Reply shape

Verdict words: APPROVE/REJECT for artifacts and verifiers, AGREE/DISAGREE for LLM judge and Auto QC checks, TAKE/REJECT for each remediation item, PASS/FAIL for grades, PENDING INPUT where a needed file is missing, NOT VERIFIABLE where evidence cannot settle it.

If the upload does not match the pasted screen (task_id, revision, deliverable paths, verifier names), the first line says so and the reply stops. Otherwise a reply has up to four parts, in this order:

1. Lead, optional: one paragraph, two at most, ≤120 words, giving the verdict and the one or two findings that matter, the binding one first. A "why does it keep failing" diagnosis fits here in one paragraph.
2. Entries: one per platform field, in screen order, each headed by the on-screen name and the verdict word: "workbook_ltd_giveback_rollforward — REJECT." Fixed one-line-per-item lists (per verifier, per check, per file) are entries, not paragraphs. Where the form has separate tabs (judge checks, File artifact feedback, verifier notes, Reviewer note), say which field each note goes in.
3. "Optional: …", one line after the entries with at most three non-blocking items, each naming its verifier or file, or nothing. List a non-blocking fix once; when it starts propagating, it becomes a blocking note, and drop it after it has been ignored once. At Source Data the line holds only items no source check covers.
4. Escalation lines, template G. A Final Review reply then closes with its Overall line (template F).

A question with no form gets one paragraph, two at most. A request for names gets plain lists and nothing else; at Final Review, two lists, approved and rejected.

Working notes, never output: ownership and coverage maps, cross-file tie-outs, corner sheets, recompute tables, probe logs, the version-delta and position ledgers, the rejected-demand log, QC reconciliation, and any confidence grading of your own claims. Cut method narration, version histories, headers or bold labels inside entries, tables, code blocks, hedges and filler.

Before sending: entries equal the form's fields, every FAIL and every AGREE that takes or rejects a remediation item has a note, tallies come from the entries, no cross-reference or hedge words, no stray `|`, Fix: in every defect entry.

## A. Notes (every gate)

### The four situations

Every item is one of four. Decide by where your answer lands, not by which button you press: a final answer of FAIL needs proof and a fix; a final answer of PASS needs proof only. Make the button match the words, because a note that calls the file clean under a Reject (or broken under an Approve) is thrown back.

- AGREE with a PASS (it is fine, the checker is right): one line of evidence.
- DISAGREE with a FAIL (it is fine, the checker is wrong): the reason the checker's concern does not hold, the proof that clears it (file, sheet or cell, quote or figure), naming any offender the checker cited, and "No change required to this file for this check." No other Fix.
- AGREE with a FAIL (it is broken, the checker is right): the reason, the proof, the Fix.
- DISAGREE with a PASS (it is broken, the checker missed it): the defect the checker missed, the proof, the Fix.

Write every note Answer → Proof → Fix, and end with a decision and a location: never a question and never a blank "Fix:".

### Entry forms

APPROVE, or AGREE with a PASS where you found no defect: one sentence, ≤30 words, giving the evidence that settles it.

Defect entry (REJECT, AGREE with a FAIL, or DISAGREE with a PASS; at External QC an Agree uses template H instead): one paragraph, two at most, about 120 words, in this order:

- location and evidence: quoted text, sheet and cell, slide or figure;
- implication; for a verifier, the counterexample "A submission that … would FAIL/PASS because …";
- "Fix:" naming the artifact or verifier ID, a quoted locator and the exact change (what to delete, the replacement words or values, which conflicting version to keep). A verifier REJECT names its remedy, repair in place, split, merge or delete; before a merge or deletion it names the new owner of every obligation the removed text carried. The Fix closes with the ripple list: each other place the fact appears, with its replacement, or "no other occurrence (grep)".

Finding that belongs to another file: one sentence of evidence, then "Fix: No change required to this file for this check; the fix belongs in <file>."

Multi-item note: every item names its verifier ID or location and its change; with three or more separate items, bullet them. Each remediation item gets its own TAKE or REJECT, and a rejected item is named as not to be adopted: "Do not add the file-exists check proposed in item (1)."

PENDING INPUT: "<field> — PENDING INPUT: <file> is needed to answer this." Give no provisional leaning, and still answer the structural questions (routing, conflicts between checks, the judge's own counts). If the form forces a binary, answer it and say the basis is the judge's cited evidence.

NOT VERIFIABLE: for a truncated paste, quote the surviving fragment and ask for that check to be re-pasted. Given only a platform link, ask for the review-artifacts zip and the judge text verbatim. An extractor dependency is NOT VERIFIABLE plus an escalation line.

Changed verdict: once, in one sentence, "changed because <new evidence>", naming the exact check or verifier.

Auto QC rework: rewrite the flagged notes and keep their verdicts unless the evidence changed; also rewrite any other field whose answer would now contradict them, naming it and why. When QC forces withdrawal of one element of a REJECT, keep its other fixes. When several partial updates are outstanding, resend the full form. After any verdict change, remind the user to change the platform button and delete the superseded note.

### Wording rules

- Every note stands alone, because Auto QC grades each one in isolation and the regenerator acts on nothing else. Name the target yourself from the artifacts; never write "request the names" or "unactionable without more detail". No cross-references (above, below, earlier, last round, see the …, see chat, the fixes above) and no paragraph counts; locate text by quoting it.
- One definite instruction per item: no "consider", "optionally", "drop X if", "if the platform lets you", and no menus. A fallback whose branches are both stated may stay.
- Give the exact change, not a full replacement criterion, unless the user asks for one: quote the current sentence and give the replacement sentence. A fix that removes a branch also states the complete positive PASS test; where several figures could be graded, give a strict precedence; a population fix gives the count, its breakdown and one per-row test.
- Plain words a non-specialist can follow: no file internals, XML part names, library or tool names. Say "the file's properties (File > Info) show 1 page and 0 words; re-save it from Word".
- An AGREE with a FAIL states the defect present now and the "Required change"; never "Fixed" for a change not yet made.
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

Task Design. One entry per judge check the form shows (scenario realism; task requires expert judgment; plan does not require external lookup; completable entirely on a computer; deliverable descriptions are contract-safe), then the File artifact feedback entry, "Task Design — APPROVE." or REJECT with its note. Judge it on its own content, never against verifier scope; a difficulty or effort-label mismatch is a metadata note, not a REJECT.

Source Data, one block per file in screen order. Answer each check the form shows (synthetic data realism; input files do not contain literal expected output values; source data does not restate the assignment; cross-file referential consistency; on-topic; anomalies not trivially labeled; each planted anomaly has exactly one defensible resolution; source documents render cleanly) on that file's own evidence: judge text repeated across files still gets a per-file verdict, and cross-file means between files. A leak the transcription test finds is a DISAGREE on that file's leakage check with the Fix in that note, never "AGREE as scoped". A DISAGREE with a FAIL also gets its own Reviewer note. Close the block with the File artifact feedback entry, "<filename> — APPROVE." or REJECT with every required change in its Fix (judge-check comments cannot carry the fix on their own), and "Also change <file> <locator>" for every other file holding the same fact; where rows are regenerated, say whether graded or determination-date rows move and whether the golden needs recomputing.

Prompt. Each check the form shows (claims verifiable from prior artifacts, task_design.json included; two professionals would converge; real workplace delegation; no AI self-voice; completable from instruction and inputs; source data does not contain the prompt's answer; computer-completable; role and deliverable identity; inputs do not reproduce the assignment; feasible path; task.toml alignment where shown, against the task_toml block), then "instruction.md — APPROVE." or REJECT. A convergence entry names each defensible reading, its headline figure and the quoted verifier phrase that accepts it.

Verifiers. One entry per verifier in screen order. A REJECT carries its counterexample and remedy (template A); a weight change is a relabel inside that verifier's note, never a deletion or fold. A coverage gap goes in the entry for the judge's coverage check, phrased "add a verifier for O#" or "map O# to <existing verifier>" where the ledger check is shown, naming its artifact and its PASS and FAIL conditions. Never REJECT for weight; a relabel is an Optional item. Where the platform asks for pasteable wording, give one line per field, only for fields that change:

- Exact change: the quoted clause → the replacement words or values. A full criterion only if the user asks, ending with the boolean-verdict instruction if the live schema expects one.
- Description / how: the replacement text.
- Why: the replacement text.
- Importance: core or secondary.

LLM judge checks. One entry per check in screen order (coverage of instruction obligations, keyword-only hacking, one atomic concept, double-grading, rubric-first policy, anchoring, robustness and the rest the form shows). Answer overlap and atomicity under the version the form shows: the ledger version judges by obligation (O#), the older version by value and coupling (SKILL.md). AGREE with a FAIL when at least one cited defect is real in this version, DISAGREE only when none holds; each remediation item gets its own TAKE or REJECT inside the entry, and an AGREE with a FAIL on a verifier goes with a REJECT on that verifier carrying the same Fix. A REJECT for conflict names the conflicting check and adds an escalation line. Where the judge's described work did not happen (a miscount, a partial read, a fake it claims to have graded), say so in that entry. A demand you have already rejected gets the same DISAGREE with the same instruction quote. Recommend override only once corrections leave a stale or platform-limit failure.

### Filled entries

Source Data file (CLO; validated: "source artifacts are all passing now"):

> Larkspur_Collateral_Surveillance_2026-09-18.xlsx — REJECT. Daily Prices carries 226 observations across four assets whose composite Price (%) sits outside the same-row Bid (%) and Ask (%), a generation fault in valuation inputs. Three shared Asset IDs also carry different 2026-09-18 prices in Daily Prices and Collateral Snapshot, contradicting the Read Me linkage and creating a third, undeclared anomaly. Fix: regenerate the affected rows so each Price (%) falls within its same-row bid–ask, and align the three Snapshot prices with the 2026-09-18 Daily Prices. Before regenerating, check whether any affected row is a 2026-09-18 determination-date row; if so, recompute the golden and re-tie the trustee bridge.

Clean AGREE on planted difficulty (SPV; matched the platform PASS):

> Anomalies not trivially labelled — AGREE. The duplicate JRN-4C7D92B1A8E6 and JRN-91A7C4E52B60 rows and the PEX-44 row are formatted like their neighbours; finding them needs bank trace BANK-R-C698FAEA and the GL map.

Verifier REJECT, duplicate gate (CLO; adapted from the submitted note, gate completed):

> wb_acp_bridge — REJECT. The rubric fails a bridge that "ends outside $468,000,000-$473,000,000", the same gate wb_corrected_acp_oc applies to the same workbook. A submission with one wrong ACP would FAIL both core rubrics for one defect. Fix: repair in place. Keep the $467,493,000 / 119.87% starting point, the separately labelled Excess CCC threshold and Meridian steps, and the single-unexplained-difference FAIL; end the bridge at the workbook's own corrected ACP and delete the $468M–$473M endpoint condition, because wb_corrected_acp_oc owns the value.

Judge check, finding taken and remedy rejected (REI; adopted at v6):

> Verifier rubrics resist keyword-only hacking — AGREE. paper_references_workbook_calculations passes a one-sentence paper that only names the tabs. TAKE the finding; REJECT the remedy of importing the deck's USD 840–1,070m band, which would give that value a second owner. Fix: in paper_references_workbook_calculations, PASS only if the paper ties at least two workbook references to specific conclusions the paper itself states; add to FAIL "or if the workbook references are free-standing pointers not attached to any conclusion the paper draws". Do not import the deck's USD 840–1,070m band.

## C. Model Output Review

The screens typically run per model and per file: with two models and two output files, 1/6 is Model 1's memo, 2/6 Model 1's workbook, 3/6 Model 1's Additional Feedback, and 4/6 to 6/6 repeat for Model 2. Never assume which screen is which; ask for any screen not pasted, and never derive the task ID from an upload's file name.

1. Per output file ("List issues per axis for this output file"), one entry per axis in screen order: Instruction-following, Correctness, Completeness, Deliverable / formatting compliance, Hallucination / fabrication, Data integrity. A clean axis reads "<axis> — No issues." plus one reason and no severity. Each issue is its own entry: severity, location, evidence and the exact correction.
2. Additional Feedback, five fields: Approach & direction, Task understanding & scope, Reasoning & assumptions, Cross-file data consistency, Coherence & integration. "Issues with a single file belong in that file's feedback"; cross-file disagreements go here, naming the authoritative value and every place it must change.
3. Record each defect once, in one field, and keep every "No issues" line consistent with the other entries.

Severity has two values only: Critical and Nice to have, never Major, Minor or Cosmetic. Auto QC ("Severity Calibrated") grades the label against the entry's own wording, one failure per run, so recheck every entry of the same kind before resubmitting.

- Critical: a wrong value, fact, formula, check result or pass/fail status; a prompt instruction not followed; invented support; missing or broken required content, including a latent formula feeding a required output and inputs that do not flow through where the prompt asks for a live model; anything left over from a Critical fix.
- Nice to have: only when every displayed figure is correct and nothing required is missing (file properties, spacing, a shifted header, paragraph placement, an added sensitivity or explanation). Its wording says so and never quotes a wrong figure; split an entry that mixes a wrong value with a presentation point.
- Never lower a severity because the conclusion still holds, the convention is disclosed or the figure looks reasonable. An over-call is also a failure: a "pure formatting nitpick that leaves the output usable as-is" is Nice to have.

After a severity change, give the user a per-field list of the labels, because the platform field keeps the old one until it is changed. Issue IDs (e.g. issue-30-i7xjas) carry forward into the golden step.

A model failing a verifier is evidence about the model unless the requirement is not a reasonable reading of the prompt; only then is it a Verifier note with its counterexample. When the attempts have not arrived, every entry that needs them is PENDING INPUT; the CLO review, with no files in the container, marked them so rather than inventing entries.

Example (LHF Model 1, from the Final Review evidence):

> output/2025_fee_close_model.xlsx, Correctness — Critical. Perf_Fee_Calc!C66 =SUM(S5:S16) produces the recorded redeemed-portion result from a month-end proxy instead of a test computed at each redemption; the rest of the performance-fee mechanics match the golden. The one defect fails both workbook_performance_fee_mechanics and workbook_performance_fee_redeemed_portion. Fix: replace the proxy at Perf_Fee_Calc!C66 with a redeemed-portion test computed by formula at each redemption date; the Final Review evidence did not cover Model 1's memo, so the ripple to it is NOT VERIFIABLE.

## D. Golden Data

Entries: one per deliverable, then the overall verdict.

- APPROVE: "<deliverable path> — APPROVE." plus at most 30 words: it passes every verifier, its key chain recomputes from source, and whether cached values replaced recalculation.
- REJECT: a template A note whose Fix names the deliverable, a quoted locator (sheet and cell, section, slide) and the exact correction.
- Overall: "Golden Data — APPROVE." or REJECT naming the deliverables. Where the golden passes a verifier you reject, add "The golden passes <verifier>, so the flaw lies in grading other submissions, not in the golden."

Golden step after Model Output Review. The user picks a base model; each golden file then shows "Fix reported issues Required 0 / N", pre-loaded with the MOR issues as severity plus category (cross-file items appear in both files' lists), each needing "Fixed in new golden", followed by "Additional Issues", one or two sentences per issue you found and how you fixed it, per golden file. Classify each Additional Issue Critical or Nice to have by the template C test. The pre-loaded text drops multiplication signs from formulas ("=Valuation!B9Valuation!B10"), so re-supply exact formulas.

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

## E. Sample Calibration

The panel unlocks one verifier at a time. An orange circle needs a response before you can move on; a green check means a field is filled, not approved; an LLM verifier is graded by three judges, majority wins; a triangle warning marks a row where your grade and the judge's differ, and every one must be resolved before the verifier closes. Answer in the platform's order for each verifier; never substitute a free-form report for these fields.

E1. Grade each attempt yourself, PASS or FAIL, before reading the judge: "Attempt 2 — FAIL." with the deciding cell, sentence or slide in at most 30 words. Then resolve each triangle: open the attempt, read "Why the Judge Marked Attempt N Pass/Fail", and either agree with the judge (no further action) or stand by your grade with one or two sentences of evidence. Apply the template C model false-fail test before calling a verifier unfair.

E2. The five required questions, each choosing the platform's option and giving the reason in one line:

1. "Where is this requirement sourced?" Explicitly required by the prompt (quote the snippet); Explicitly required by the source data (name the file); Implicitly required to do this work well (why a competent professional would do it); or Not required anywhere — unfair to verify (why). That last option deletes the verifier at the next regeneration; use it for checks nobody asked for, including existence-only and cross-file checks the platform pushes.
2. "Does this check test just one thing?" Yes, or No listing the separate concepts. Split by concept, not by detail: "Team A includes Persons 1–4" is one question; "includes Persons 1–4 and finished first" is two. Keep it one check if it can be phrased as one yes/no question or its details add up to one answer (a roster, one calculation, one table); split only when an "and" joins different ideas that could pass or fail independently. Every concept you list comes back as its own verifier, so ten checks marked as testing three things return about thirty.
3. "Is it clear what should pass and what should fail?" Yes, or No with the rule spelled out both ways ("Passes if the memo states a dollar variance and a one-sentence cause; fails if either is missing"). No rewords the check in place; it never deletes or adds one, so use it for any change you want short of deletion.
4. "Does the grader have everything it needs to judge this?" Yes, or No naming the exact facts or values to inline ("the prior-quarter net income of 1,240,131"), not just where they come from.
5. "What happens if an answer fails this check?" Critical (the answer is wrong without it, a hard requirement) or Nice to have (it improves an already-correct answer). The label only sets the weight; Nice to have never deletes a check. Importance is never a reason to reject.

E3. Coverage gaps: "Add gap" with the exact wording of the new check, where it is sourced, the artifact it targets and its PASS and FAIL conditions, or "No gaps". This is one of only two ways a verifier is added.

E4. Redundant verifiers: when two or more checks grade the same concept against the same artifact, select them, describe what they redundantly check, and choose the one to keep; the rest are deleted. To change a check rather than delete one, mark it vague (E2.3) instead.

E5. Golden failing a verifier: first decide whether the verifier or the golden is wrong. A flawed verifier is reworked and the golden left alone; a sound verifier the golden truly fails is fixed in the golden, never by weakening the verifier. To fix the golden, download it from File Preview, edit it offline, click "Fixed in updated Golden" and describe what was wrong and what changed, then "Attach updated golden". Do this for every verifier the golden fails, except those carrying a note that the verifier is being updated: leave the golden alone for those. Log each fix in the template D form.

E6. After regeneration, re-review by label. NEW checks come from a split or a gap; CHANGED ones usually from a vague mark; REMOVED ones from "Not required anywhere" or a redundancy choice, and nothing else adds or deletes a verifier. GRADE CHANGED means the check is unchanged but an automated grade flipped between runs (grading varies run to run, and an updated golden can change results): accept the new grade or stand by yours, which feeds the disagreement into the next regeneration. No label means unchanged; no re-review is needed.

E7. Set check before submitting: every outcome a correct solution must reach is graded by at least one check that a wrong answer fails, and each required file has a primary-correctness check; checks separate the golden from a plausible-but-wrong attempt (drop default-pass checks); the hardest analytical steps are graded, not only surface checks, and mandatory cautions and exclusions are covered; no two checks grade the same condition on the same artifact; each check is gradeable on its own; at least one check penalises unsolicited additions, naming the specific forbidden artifacts (extra files or content the prompt excludes, never more thorough correct analysis); no existence-only, filename-only or format-restating checks.

When only verifier names are pasted, every field is PENDING INPUT; never grade from a name. Hold the line: approve what is sound, reject what is defective, keep feedback atomic and anchored to something observable (vague feedback comes back as a vague verifier), and fix the golden or the check, never weaken a sound verifier to make the golden pass.

## F. Final Review

A verifier rejection ends the task, so set the bar once and block only when:

- (a) the rubric misstates a governing term;
- (b) a realistic submission is mis-graded, shown on a supplied output or on a concrete submission under an accepted reading;
- (c) the golden fails a sound verifier, once you have decided which side is wrong.

Everything else gets an optional line: stale figures that change no result, hypothetical overlap or bundling, reasonable placement or format readings, extractor observability (NOT VERIFIABLE plus escalation), weight or difficulty labels, mechanical source slips, and planned difficulty.

A placement or format reading is optional only when the prompt supports it. A PASS condition the prompt never asks for (a literal figure or phrase, a label, a closed list, a fixed placement, a provider band the prompt asks the solver to challenge) or a criterion that accepts one reading where the prompt and sources allow another fails a correct answer, so it meets (b); External QC reviews (solver runs or file reads) showed several such Final Review approvals to be true positives. Grade the golden literally against every FAIL clause, labels and ordering wording included, and test each pass case against the governing standard, not only the arithmetic. Approval sends the task to External QC, where only verifier.json can change, so the task must be final before you approve: anything already known to be wrong is fixed before Final Review, not left for rework.

The judge checks on the Final Review screen are display-only; answer the ship-ready Approve/Reject fields. Notes cite only what the gate shows (instruction, sources, verifier.json, golden); model outputs are a private test bed, so write a counterexample as a fully described submission or a stated edit to the golden. If the prior notes are absent, say the fix list is inferred and name the missing file. Re-verify every claimed fix in the current files and mark each prior failure verified fixed, false positive or still open in your working notes; a still-open item reaches the output only as a note that meets the bar. Judge in order Task Design, Source Documents, each verifier, Golden; enter them in the form's screen order:

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
> Source Documents — APPROVE. The HWM Trajectory sheet says its references are "retained for chronology; class capital-account detail and allocation components remain in the companion capital-account package", and the prompt accepts a NAV-package figure only if it reconciles, so solvers rebuild high-water marks from the capital package and the register, as the golden does. That is planned difficulty. ACT-7B3F9D remains the only record of 136 with a blank Controller approval and the same preparer and releaser.
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

## H. External QC

The stage after Final Review and the last before TFRL; reference 10 holds the workflow, the true or false positive test and the mandatory multi-pass review. Only verifier.json changes are in scope.

1. Lead, one short paragraph: the outcome (approved: every finding disagreed; JSON revision: every agreed finding is a verifier finding; or task rejected: an agreed finding needs a prompt, source or golden change), the tally, and the closest call.
2. One entry per finding card, in screen order, headed exactly as on screen: "Review 900309453 · finding 1 — AGREE." An Agree is one or two sentences giving the defect present now with its quoted locator, correcting any wrong side claim, and "Changed from the Final Review APPROVE because …" where that applies. A Disagree is one paragraph, two at most: why the finding's own complaint does not hold, the proof (criterion quote, prompt clause, source cell or figure) and "No change needed to verifier.json."; a grader or infrastructure fault adds "the fix belongs in the grading infrastructure" and a template G line. A bundled card names each listed criterion that is a false positive.
3. Fix request for the tracker's Additional Comments cell, only when a verifier finding is agreed: task ID and version, then per criterion the findings it resolves, the quoted current text, the exact replacement and any remediation item not to adopt, then "The golden passes every changed criterion." once you have re-graded it. Fixes agreed at Final Review or in an earlier External QC round that are missing from this version go in one separate sentence; any other defect QC did not raise goes to the user in one line, not into the request. Written for an engineer who has not read the task: no cross-references.
4. The tracker row's other reviewer fields, each PENDING INPUT if the user has not given it: Trainer Name (the task claimant), Email (the Turing address), Task ID (full, exactly as RL World shows it) and RL-World Task Link (with its version segment). Close with one line: once QC returns the file, upload it on the Content tab, set "Updated on RL World" to Yes, then give fresh verdicts on whatever comes back.
5. Escalation lines, then nothing else: no Final Review field verdicts and no Overall line. A corrected verifier.json only on request.

Example (lxwjwnav-1, an illustrative restatement: the quotes and dates come from the session, the replacement wording is illustrative, and the submitted answer also added a scenario date to instruction.md, which is out of scope at External QC):

> AGREE on all three findings: one verifier defect, a JSON revision. The closest call is that the runs QC cites dated actions from a sandbox clock reading 28 October, an infrastructure fault escalated below; the Agree rests on the criterion's fixed cutoff, which the prompt never states and which also fails a plan dated from the source Close Calendar.
>
> Review 355952 · finding 1 — AGREE. deck_close_action_plan requires "each with a specific calendar date on or before 20 October 2026", a date the prompt never states, and the source Close Calendar itself schedules "Distribute final close book" on 21 October, so a correct plan dated from the calendar fails.
>
> Additional Comments: Task as-finance_and_insurance-financial_and_investment_analysts-20260925-053924-lxwjwnav-1, version <NN> (PENDING INPUT). deck_close_action_plan (resolves Review 355952 finding 1, Review 355954 finding 1, Review 900309453 finding 1): replace "each with a specific calendar date on or before 20 October 2026" with "each with a specific calendar date, in the Close Calendar's order, with pre-certification actions dated before post-certification steps such as distributing the final close book". Do not adopt "accept later actions when the deck says certification has passed". The golden passes the changed criterion.
>
> ESCALATE TO: engineering | ISSUE: sandbox clock later than the scenario date | EVIDENCE: the cited solver runs dated actions from 28 October 2026 | WHY THE FORM CANNOT RESOLVE IT: the clock is environment state, not task content | RECOMMENDED ACTION: pin the sandbox date to the scenario date.
