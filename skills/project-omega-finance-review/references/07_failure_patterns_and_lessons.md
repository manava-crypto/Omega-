# Failure Patterns and Lessons

Read before every verdict. Each pattern is a failure from reviews of seven task packs, with its rule, a self-check and one line of evidence. The evidence is Trainer Review and one Final Review, so lessons for Model Output Review, Golden Data and Sample Calibration are transferred. Logs and ledgers are working notes, never output.

## Task key

- LHF: lh-finance_and_insurance-financial_and_investment_analysts-20260914-103056 (fund fee close; Final Review v24).
- SPV: as-finance_and_insurance-financial_and_investment_analysts-20260908-155621-3biepume-1-test-d4f1fec4d9dd-test-8-test-0171a01d627d-v1 (CV sell-or-roll).
- HAL: as-finance_and_insurance-financial_and_investment_analysts-20261001-173428-p98yff3p-0 (captive collateral).
- CLO: as-finance_and_insurance-financial_and_investment_analysts-20260925-144439-uswiodkk-0 (CLO coverage tests).
- ACL: as-professional_scientific_and_technical_services-accountants_and_auditors-20260927-105053-efgdteth-2 (CECL audit).
- CRW: as-finance_and_insurance-financial_and_investment_analysts-20260925-053256-p8f6vjxz-1 (fallen-angel bonds).
- REI: as-finance_and_insurance-financial_and_investment_analysts-20260925-053924-lxwjwnav-4 (reinsurance recoverables).

## Patterns

### F01. Rejecting without a counterexample
- Rule: REJECT only when a correct answer fails, a wrong one passes, graders split or a governing term is misstated; a model false-fail shows unfairness only when the requirement is not a reasonable reading of the prompt.
- Check: write "A submission that … would FAIL/PASS because …"; if you cannot, APPROVE.
- Evidence: LHF withdrew 11 of 14 verifier REJECTs; SPV wanted IRR bands though the 12% gate never flips (14.79–15.26%).

### F02. Approving without stress-testing
- Rule: APPROVE only after the probe battery, every round, Unchanged verifiers included; at Trainer Review fix all findings in one pass, at Final Review block only on its bar.
- Check: a probe log exists for each verifier you keep.
- Evidence: ACL T5 approved all but one verifier; judges then found one latent defect per round until v7.

### F03. Your fix wording breaks neighbours
- Rule: before returning wording, restate the host's construct, grep every verifier it could touch, re-run touched bands at the corners and probe it; give the change, not a full criterion, and no fixed number in a judgment area.
- Check: each fix names the neighbours it could touch, or says "no other occurrence (grep)".
- Evidence: REI v8, "Three of the eight FAILs are mine"; CLO's reviewer-written $468M–$473M endpoint became wb_acp_bridge, a double gate.

### F04. Notes that do not stand alone
- Rule: every defect note (REJECT, DISAGREE or AGREE with a FAIL) ends with "Fix:" naming the ID, a quoted locator and the exact change, or "Fix: No change required to this file for this check; the fix belongs in <file>."
- Check: read each note pasted alone.
- Evidence: five Auto QC FAILs (HAL, ACL, REI), such as "The fixes are in the artifact verdict below".

### F05. Single-path anchors and bands
- Rule: run probe 1 on every anchor and band; enumerate accepted anchors rather than widening one band; where the instruction leaves a choice, grade derivation, arithmetic and rationale.
- Check: every defensible corner lands inside, every known-wrong method outside.
- Evidence: CRW wb_comparable_event_price_scaling's ±0.3pp of −2.96% failed a D−5 base (−2.6502%) by 0.0098pp.

### F06. Composites approved as one construct
- Rule: run probe 5; limbs are one construct only when one cannot be judged without the facts the other grades, and prompt grouping, contract stages and a shared outcome are not coupling.
- Check: for each AND, write the output that passes one limb only.
- Evidence: ACL wb_directional_bias_analysis, approved as one contract stage, failed atomicity at v7.

### F07. Duplicate and redundant verifiers
- Rule: run probe 4; gate each value in one verifier per artifact and merge same-value pairs and mechanical chains, since consolidation is as legitimate as splitting; different obligations sharing amounts are not overlap.
- Check: name the one wrong value that fails both, or it is not overlap.
- Evidence: LHF Model 1's Perf_Fee_Calc!C66 =SUM(S5:S16) failed workbook_performance_fee_mechanics and workbook_performance_fee_redeemed_portion for one defect.

### F08. Coverage gaps
- Rule: rebuild probe 3's map every version, per artifact; N-of-M never makes a sole owner optional.
- Check: every obligation and declared anomaly has a mandatory home on the artifact the contract names.
- Evidence: ACL accepted "at least four of these five" against "each data-conversion exception found".

### F09. Long, incomplete or not paste-ready
- Rule: answer every field inline, in screen order, under C1–C9 in SKILL.md.
- Check: the pre-send checklist.
- Evidence: ACL, "SINGLE OR MAX TWO PARAs"; REI left two FAIL checks without notes.

### F10. Leakage and labelling
- Rule: if a core verifier's conclusion can be copied from a source, REJECT the source and DISAGREE with its leakage PASS; facts the solver must still apply are not leaks; mechanism wording or a one-filter fingerprint is labelling.
- Check: grep core anchors and anomaly-plan wording across sources; sort and filter every column.
- Evidence: CLO's indenture §6.3 pre-solved a core verifier, yet the review answered "AGREE on the check as scoped".

### F11. Planned difficulty called a defect
- Rule: judge Task Design on its own content; apply the planned-difficulty test before calling a source condition a defect.
- Check: each source REJECT names the notes read, conventions tested and figure moved.
- Evidence: SPV's Preliminary Close "break" vanishes when accrued-payable credits are netted (−2150 Cr); it was the planted PEX-44 anomaly.

### F12. Judge output not audited
- Rule: treat every judge verdict as unverified: recount what it counts, treat a partial read as existential evidence only, re-run each check every round, and TAKE or REJECT item by item.
- Check: no decision covers a whole check at once.
- Evidence: CRW's keyword judge said its fakes "each one fails"; two passed at v3.

### F13. Thin first pass, unchecked deltas
- Rule: sweep every file in round one; keep the version-delta ledger on each later version, and if nothing changed say so in the first line.
- Check: the prior fake is re-graded against the revised text.
- Evidence: REI v5 matched v4 on every verifier; at CRW v4 a judge-panel seat changed unnoticed.

### F14. Fix ripple and contained source defects
- Rule: give every fix a ripple list; align prompts to source text that already exists; a source defect is a blocking Source Data note, never an escalation or verifier escape clause alone.
- Check: each fix has a ripple list or "no other occurrence (grep)".
- Evidence: REI's EMBER source defect was escalated twice, never fixed, and the escape clause containing it cascaded into v8 FAILs.

### F15. Governing terms paraphrased
- Rule: run probe 7 on every restated cap, threshold, exception or window; match names and section numbers literally.
- Check: each condition is marked met or unmet beside its source quote.
- Evidence: LHF's give-back verifiers applied the 35% cap without Part V 5.3's "documents taxes actually paid".

### F16. Wrong facts in rubric text
- Rule: run probe 9 and grep old figures after any change; at Trainer Review block when it can flip a verdict, misleads the judge or is being copied.
- Check: each figure in rubric text has a source location in your notes.
- Evidence: REI's illustration of 206,039,200 sat above its own 205m ceiling.

### F17. Pack-level judge text on every file
- Rule: answer each repeated check on that file's evidence; cross-file means between files.
- Check: no file carries a FAIL whose evidence sits in another file.
- Evidence: CLO's realism FAIL was identical on four files; the evidence sat in one workbook.

### F18. Requirements beyond the prompt
- Rule: run probe 8 and delete any condition without a basis; rewrite "FAIL if a different X" as "FAIL if <planted item> is not identified".
- Check: each condition has a quoted basis.
- Evidence: CRW wb_exception_log_source_choices failed any other stale-taxonomy lot though 18 rows were expired.

### F19. Proxies and untested hack resistance
- Rule: run probes 2 and 6; negative-scope rubrics need a substance floor, and PASS and FAIL mirror with no "if present" loophole.
- Check: no PASS clause can be met by writing less.
- Evidence: CRW's fake "account-ID normalization and duplicate detection", with an owner and a date, passed.

### F20. Source sweep gaps
- Rule: round one covers a dated timeline, generator text, back-solved values, intra-file invariants and undeclared anomalies; block what moves a graded figure or gate, contradicts the design or breaks the fiction.
- Check: a timeline and a marker grep exist per file.
- Evidence: HAL's HIL-AR-2026Q2, dated after the window end, flipped the governing reserve.

### F21. Briefs and relays
- Rule: briefs quote the bar, terminal consequence, counterexample rule, Fix: and C1–C8; re-verify each REJECT driver; relay one-to-one without stripping fixes.
- Check: relayed entries equal the form's fields.
- Evidence: LHF briefs omitted the terminal consequence, and 14 REJECTs came back.

### F22. Verdicts without evidence, wrong pack
- Rule: match the upload to the screen first; mark PENDING INPUT per question, naming the file, with no provisional leaning; quote a truncated paste, mark it NOT VERIFIABLE and ask for a re-paste.
- Check: every PENDING INPUT names the file that would settle it.
- Evidence: CLO reviewed the REI zip against the CLO screen ("A whole round was lost").

### F23. Flip-flopping
- Rule: fix the bar before grading; when challenged, re-test each item against that bar.
- Check: each changed verdict says "changed because <new evidence>".
- Evidence: LHF V14 went REJECT, "stronger", then APPROVE.

### F24. Unconfirmed extractor behaviour
- Rule: where a rubric needs formula text, cached values or formatting, run probe 11, mark it NOT VERIFIABLE and escalate in one line; truncation is never a FAIL.
- Check: each such rubric has a degradation clause or an escalation.
- Evidence: CRW's core `$.truncated equals false` check was deleted.

### F25. Optional fixes that never land
- Rule: classify each fix once; a non-blocking one gets one "Optional:" line, promoted when it spreads.
- Check: one severity per fix across the steps of one review.
- Evidence: CRW repeated five text fixes "now for the third round", the trough error spread into a new verifier, and one FAIL clause was rideable at Source Data but a REJECT at the verifier step.

### F26. Headline numbers with no band
- Rule: run probe 13, even for a wide band; replace "about" with a tolerance.
- Check: an absurd value (zero, ten times the golden) fails.
- Evidence: REI v3 model_economic_value_shortfall passed both 1,286,347,919 and 400,000,000.

### F27. Weights misstating share
- Rule: run probe 14; at Trainer Review put the relabel in the verifier's note.
- Check: no planned anomaly is graded only by secondaries.
- Evidence: CLO v2's wb_classification_sequence was secondary while carrying the whole hierarchy.

### F28. Conditional advice executed literally
- Rule: one definite instruction per item; name the new owner before any deletion; say which judge items must not be adopted.
- Check: each recommended deletion names its obligations' new owner.
- Evidence: CRW's fallback deletion of memo_post_day100_control_gaps was executed, orphaning the control gaps.

### F29. Convergence asserted without the text
- Rule: compute the headline under each reading and quote the band accepting it; AGREE only if all land inside with one decision, and re-run after any scope fix.
- Check: the note names each reading, its figure and the accepting phrase.
- Evidence: ACL T4 agreed on a remembered band; the real $107.5M–$113.5M low end failed a defensible 8Q+4Q range.

## Reviewer habits

- Shortening that drops load: cut explanation, never conditions, fallbacks, "do not" clauses, IDs, locators or anchors. REI's short note lost its fallback, and the phantom clause it warned of followed.
- Tally errors: compute every count from the entries, and name the exact check behind any "reversing my earlier" line. CRW wrote "six get Disagree" over eight.
- Burying the binding finding: lead with it. REI's source defect sat below seven REJECT notes.
- Process slips: answers inline in chat, never in a file card; scratch work in the scratchpad. REI wrote review output into the repository and put notes in a file card that did not render.

## Probe battery

1. Corner sweep: every anchor and band under each defensible convention and permitted treatment; known-wrong methods outside.
2. Minimal fake: labels, owner and deadline, no case facts. If it passes, bind to a source value or case ID.
3. Obligation map: each named field and each/every/all clause → a quoted PASS/FAIL phrase.
4. One-owner diff.
5. Coupling test on every AND.
6. Proxy test: could a non-compliant output meet the test?
7. Governing-term quote, each condition marked met or unmet.
8. Population scan: every condition traces to the prompt or a source. For "a different X", count the qualifying rows.
9. Embedded-fact recompute: every figure, illustration, preamble fact and cross-reference.
10. Binding: spot checks sit inside PASS.
11. Degradation clause wherever formula text, cached values or formatting matter.
12. Discrimination: a shortcut hitting the graded value is a note unless it is a known-wrong method.
13. Magnitude: each headline number has a floor and a ceiling; an absurd value fails.
14. Weights: core for anomalies and headline figures. Relabel; never delete or fold.

## Recurring judge demands

Log every rejected demand and answer each repeat with the same short DISAGREE and instruction quote; after a second flag on one point, re-derive from source and hold only on a quoted basis. REI turned away a seven-labelled-tabs demand four times by quoting "Prefixes or suffixes on those labels are fine". REJECT on sight: file-exists checks against the rubric-first policy (CLO, CRW, REI), ROUND-function string checks (CRW), anchors called leakage (ACL), another artifact's anchors (REI), cross-artifact rubrics, facts the pack lacks (REI competing claims, ACL partner name), tab labels as a test (REI), and remedies that hand over the answer or remove the work (REI's 2027 market schedule, ACL's F4 anchoring). When two checks conflict, TAKE one, REJECT the other by name and escalate (CLO v3).

## Final Review bar and the LHF case

A verifier rejection ends the task, so block only when (a) the rubric misstates a governing term; (b) a realistic submission is mis-graded, shown on a supplied output or on a concrete submission under an accepted reading; or (c) the golden fails a sound verifier, once you have decided which side is wrong. Everything else gets an optional line: stale figures that change no result, hypothetical overlap or bundling, reasonable placement or format readings, extractor observability (NOT VERIFIABLE plus escalation), weight or difficulty labels, mechanical source slips, and planned difficulty.

LHF round one rejected Task Design against verifier scope, Source Documents over conditions their own notes explain, and 14 verifiers. Against the bar both layers went to APPROVE and 11 REJECTs fell: wrong anchors that changed no result (V15, V16, V18, V24), hypothetical overlap or edge cases (V3, V36), a workbook-wide check that `08_excel_verifier_scoping.md` allows (V21), and reasonable readings of the prompt (V14, V33, V35, V38). Three stood: a double penalty shown on a supplied output (workbook_performance_fee_mechanics), and a 35% cap missing Part V 5.3's documented-taxes condition (workbook_ltd_giveback_rollforward, memo_giveback_conclusion). The golden passed all three, so the flaws lie in grading other submissions. The closing line, as the bar requires it:

Overall REJECT, because one verifier rejection ends the task: workbook_performance_fee_mechanics, workbook_ltd_giveback_rollforward and memo_giveback_conclusion. Every submission so far concluded a $0 give-back, so the two cap REJECTs rest on a branch no submission has taken; they stand.

The full answer is in `04_completed_task_examples.md`.

## Pre-send checklist

1. Identity: the upload matches the pasted screen (task_id, revision, deliverable paths, verifier names), or the first line flags the mismatch.
2. Ledger: on a later version, each prior finding is marked fixed, partially fixed or not fixed.
3. Completeness: entries equal the form's fields in screen order; every FAIL, and every AGREE that takes or rejects part of a remediation, has a note.
4. Length: lead ≤2 paragraphs, ≤120 words; a reply with no form ≤2 paragraphs; a request for names gets plain lists; APPROVE or clean AGREE ≤30 words; defect entry ≤2 paragraphs, about 120 words; bullets only for three or more edits; one "Optional:" line of up to three items.
5. Fix: in every defect entry, in the F04 form.
6. Self-containment grep: `above|below|last round|earlier|see the|see chat|as before|paragraph (one|two|three|four|five|six|seven|eight|nine)`; reword each hit that points at other text.
7. Hedge grep: `consider|optionally|if you|if the|could also`; make each hit definite unless it is a fallback with both branches stated.
8. Format: no `|` outside escalation lines; no tables, code blocks, headers, bold labels or confidence tags.
9. Consistency: tallies come from the entries, and no two notes conflict.
