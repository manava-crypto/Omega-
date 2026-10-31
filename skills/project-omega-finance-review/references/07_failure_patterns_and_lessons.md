# Failure Patterns and Lessons

Read before every verdict. Each pattern is a failure from reviews of more than thirty task packs, with its rule, a self-check and one line of evidence. The evidence covers Trainer Review, Final Review, External QC, Model Output Review, one Sample Calibration and the Auto QC reworks; only the Golden Data lessons are transferred. Logs and ledgers are working notes, never output. Where a pattern and the pasted Description of a platform check disagree, the Description governs that check (09).

## Task key

- LHF: lh-finance_and_insurance-financial_and_investment_analysts-20260914-103056 (fund fee close; Final Review v24).
- SPV: as-finance_and_insurance-financial_and_investment_analysts-20260908-155621-3biepume-1-test-d4f1fec4d9dd-test-8-test-0171a01d627d-v1 (CV sell-or-roll).
- HAL: as-finance_and_insurance-financial_and_investment_analysts-20261001-173428-p98yff3p-0 (captive collateral).
- CLO: as-finance_and_insurance-financial_and_investment_analysts-20260925-144439-uswiodkk-0 (CLO coverage tests).
- ACL: as-professional_scientific_and_technical_services-accountants_and_auditors-20260927-105053-efgdteth-2 (CECL audit).
- CRW: as-finance_and_insurance-financial_and_investment_analysts-20260925-053256-p8f6vjxz-1 (fallen-angel bonds).
- REI: as-finance_and_insurance-financial_and_investment_analysts-20260925-053924-lxwjwnav-4 (reinsurance recoverables).
- ORI: as-finance_and_insurance-financial_and_investment_analysts-20261009-070551-sr6nbluy-1 (Oriole Day-100 credit integration; Source Data v1–v5).
- CAL: as-finance_and_insurance-financial_and_investment_analysts-20261009-070551-sr6nbluy-0 (Caldera new issue; Source Data v1–v5).
- ARC: as-professional_scientific_and_technical_services-accountants_and_auditors-20260909-222354 (Arcwell non-GAAP remediation; Final Review and four Auto QC reworks).
- TPX: as-professional_scientific_and_technical_services-accountants_and_auditors-20260909-222354-dr4hyy6f-3 (transfer-pricing provisioning; Final Review and Auto QC).
- KOW: as-finance_and_insurance-financial_and_investment_analysts-20260930-032951-9jv02sfa-3 (pension election; Final Review).
- NLR: as-finance_and_insurance-financial_and_investment_analysts-20260925-053924-lxwjwnav-1 (revolver renewal; Final Review).
- RKLB: as-finance_and_insurance-financial_and_investment_analysts-20260922-194729-orfzebx6-0 (principal-protected note; Final Review and Auto QC).
- VAL: as-financial_and_investment-financial_and_investment_analysts-20261013-170040-xzj1i0nw-0 (hybrid call and quarter close; Trainer Review v1–v4).
- ORN: as-financial_and_investment-financial_and_investment_analysts-20261016-095338-rtjcn29h-1 (semiconductor IG hold; Trainer Review v1–v4).
- VES: as-financial_and_investment-financial_and_investment_analysts-20261016-095338-rtjcn29h-0 (LNG force majeure, covenant and vendor renewal; Trainer Review v1–v5).
- TRS: as-finance_and_insurance-financial_and_investment_analysts-20260925-053256-p8f6vjxz-0 (trust release sizing; Final Review and two External QC rounds).
- KRD: as-finance_and_insurance-financial_and_investment_analysts-20261001-173717-ohv1n4ti-2 (leverage capacity; Final Review and two External QC rounds).
- MKT: as-finance_and_insurance-financial_and_investment_analysts-20260922-194337-jicq4o2h-1 (market alignment and remediation; Final Review and External QC).
- OPR: as-professional_scientific_and_technical_services-accountants_and_auditors-20261001-173428-p98yff3p-8 (option repricing; Final Review and External QC).
- CUS: as-professional_scientific_and_technical_services-accountants_and_auditors-20260923-033737-3m6bdh9w-3 (customs diligence; Final Review, Auto QC and External QC).
- COV, IDC, RAQ: the dr4hyy6f-0 (covenant authority briefing), dr4hyy6f-2 (idle capacity) and dr4hyy6f-4 (reverse acquisition) packs of as-professional_scientific_and_technical_services-accountants_and_auditors-20260909-222354; Final Review and External QC.
- NAV, PBM, CRR: Final Reviews of aor11i3b-1 (NAV error), nmfpvhcp-1 (prime-broker margin) and v9abvmkf-0 (REIT prepaid rent), late October.
- LQP: as-financial_and_investment-financial_and_investment_analysts-20261008-185110-fxjpir5g-5 (pricing review; Trainer Review v1–v14).
- BKS, HWI: Model Output Reviews of p98yff3p-1 (surety) and 9jv02sfa-4 (spin-off valuation), with their golden steps and one Sample Calibration.

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
- Rule: every defect note (REJECT, AGREE with a FAIL or DISAGREE with a PASS) ends with "Fix:" naming the ID, a quoted locator and the exact change, or "Fix: No change required to this file for this check; the fix belongs in <file>."
- Check: read each note pasted alone.
- Evidence: five Auto QC FAILs (HAL, ACL, REI), such as "The fixes are in the artifact verdict below".

### F05. Single-path anchors and bands
- Rule: run probe 1 on every anchor and band; enumerate accepted anchors rather than widening one band; where the instruction leaves a choice, grade derivation, arithmetic and rationale.
- Check: every defensible corner lands inside, every known-wrong method outside.
- Evidence: CRW wb_comparable_event_price_scaling's ±0.3pp of −2.96% failed a D−5 base (−2.6502%) by 0.0098pp.

### F06. Composites judged by the wrong test
- Rule: read which atomicity check is pasted. Ledger version: a rubric is composite only when its parts serve different O#s, and a construct tests/verifier-plan.md documents is one construct. Older version ("one atomic concept"): run probe 5; limbs are one construct only when one cannot be judged without the facts the other grades, and prompt grouping, contract stages and a shared outcome are not coupling.
- Check: name the O# of each limb (ledger), or write the output that passes one limb only (older).
- Evidence: ACL wb_directional_bias_analysis, approved as one contract stage, failed the older check at v7; SPV's and VAL's coupling REJECTs fell under the ledger check; REI's v8 split request failed Auto QC scope conformance because the plan defined the band as part of the chain construct.

### F07. Duplicate and redundant verifiers
- Rule: read which overlap check is pasted. Ledger version: overlap is two verifiers on one artifact grading the same O# and the same facts; different obligations are never overlap, even when one wrong value fails both. Older version ("non-overlapping"): run probe 4, gate each value in one verifier per artifact and merge same-value pairs and mechanical chains. Under both, consolidation is as legitimate as splitting, and different obligations sharing amounts are not overlap.
- Check: name the shared O# and fact (ledger), or the one wrong value that fails both (older).
- Evidence: LHF Model 1's Perf_Fee_Calc!C66 =SUM(S5:S16) failed workbook_performance_fee_mechanics and workbook_performance_fee_redeemed_portion for one defect (older bar); VES v3 sent 13 overlap REJECTs and VAL 9 that the ledger definition rules out; ORN DISAGREEd a double-grade PASS on value reuse across obligations.

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
- Rule: briefs quote the bar, which rejections end the task, counterexample rule, Fix: and C1–C8; re-verify each REJECT driver; relay one-to-one without stripping fixes.
- Check: relayed entries equal the form's fields.
- Evidence: LHF briefs omitted the stakes of a rejection, and 14 REJECTs came back.

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

### F27. Weights treated as a reject ground
- Rule: importance (core or secondary) is never a REJECT at any gate; a secondary verifier is still a grading home. Run probe 14 and put any relabel on the Optional line.
- Check: no REJECT cites core or secondary.
- Evidence: VES v2 and v3 rejected delivery_locked_conversion and hedge_mark_recomputation for being secondary, then withdrew both; CLO v2's wb_classification_sequence carried the whole hierarchy as secondary and was relabelled.

### F28. Conditional advice executed literally
- Rule: one definite instruction per item; name the new owner before any deletion; say which judge items must not be adopted.
- Check: each recommended deletion names its obligations' new owner.
- Evidence: CRW's fallback deletion of memo_post_day100_control_gaps was executed, orphaning the control gaps.

### F29. Convergence asserted without the text
- Rule: compute the headline under each reading and quote the band accepting it; AGREE only if all land inside with one decision, and re-run after any scope fix.
- Check: the note names each reading, its figure and the accepting phrase.
- Evidence: ACL T4 agreed on a remembered band; the real $107.5M–$113.5M low end failed a defensible 8Q+4Q range.

### F30. Platform definition ignored
- Rule: answer each judge check by its pasted Description (09); before sending, test every REJECT against the check it falls under, named by its on-screen title, and against the Final-bar optional list.
- Check: each REJECT names the platform check whose Description it breaches.
- Evidence: VES v3 sent 22 then 16 REJECTs where the platform's own definitions supported 5 (user: "i don't understand the reason for rejects … the judge has marked all PASS"); VAL cut 17 to 8.

### F31. Verifier plan unread
- Rule: ask for tests/verifier-plan.md whenever verifiers are in play; without it, mark any split, merge, deletion or narrowing PENDING INPUT; never request a change that reverses a design the plan documents.
- Check: every structural request cites the plan or is PENDING INPUT.
- Evidence: Auto QC scope conformance failed REI's split (plan: the band is part of the chain construct), ACL's go/no-go REJECT ("it does not assume escrow lies inside every defensible range construction") and HAL's $16.1M rejection ("professional alternatives are retained").

### F32. Source fixes that create the next FAIL
- Rule: before any source addition, deletion or regeneration spec, grep verifier.json and the prompt for every figure and phrase it touches; fix a standards breach by correcting the treatment; put convergence conventions in the prompt, not in a source procedure; solve held-anchor regenerations yourself; write table rows cell by cell; set file properties as the generator's last step; name every other file holding the same fact.
- Check: each source fix carries its grep result and a ripple list naming other files.
- Evidence: ORI's v1 advice to write the coverage method into policy failed "restates the assignment" at v4, its added Note 9A published the graded 37.2%, and its held-anchor rebuild created a 98.5bn plug; CAL relabelled capitalized interest in operating cash flow as "issuer presentation policy" and failed realism at v5; HAL's re-keyed inception dates broke FX provenance and a pipe-delimited row was pasted raw; ORI's pypdf metadata came back after a rebuild.

### F33. Optional source notes never applied
- Rule: at Source Data, any defect a source check could fail is a required edit; the Optional line holds only items no check covers.
- Check: no source Optional item names something realism, consistency, labelling, rendering or metadata could fail.
- Evidence: CAL's "All 1,200 POs Open" sat in non-blocking notes from v1 and became half of the v4 realism FAIL; none of eight v3 cosmetic notes was applied.

### F34. Later rounds checked only the flagged items
- Rule: each version, re-run every source check on every changed file in full with the round-one lenses (as-of dates, market conventions, ID realism, lifecycle uniformity, classification); a judge PASS on sampled content and an unchanged checksum prove nothing about a defect present since v1.
- Check: each changed file has a full-sweep line in the working notes.
- Evidence: ORI's v3 and v4 approvals missed frozen balances, 54 font errors and a printed graded figure; CAL v1–v2 missed bid OAS below ask OAS, md5-of-integer PO IDs and a constant 37-day amend gap.

### F35. Undeclared source errors kept as difficulty
- Rule: at Trainer Review the judge excuses only anomalies declared in the anomaly plan; fix or declare every other source error, whatever the prompt's caveats.
- Check: every known source error is in a required edit or the anomaly plan.
- Evidence: HAL kept two errors as "a position to test"; v3 and v4 failed consistency ("The declared … anomalies were excluded").

### F36. Notes citing what the gate does not show
- Rule: Final Review notes cite instruction, sources, verifier.json and the golden only; write counterexamples as a described submission or a stated edit to the golden.
- Check: grep notes for "Model 1", "Model 2", "attempt".
- Evidence: RKLB, "There is only one golden solution provided in the final review gate"; NLR repeated it the same day.

### F37. Relays that re-check the fact, not the classification
- Rule: re-verifying a REJECT driver means re-running the planned-difficulty, leakage and bar tests, not confirming the quoted text exists; a brief never primes a verifier's anchor as the expected source value.
- Check: each relayed REJECT names the notes read, the controlling record counted and the graded figure moved.
- Evidence: LHF relayed a source REJECT after checking two facts; KOW rejected a premium-date conflict the instruction told solvers to resolve; ARC's severance "ambiguity" was settled by one GL posting; TPX's chart dates moved no graded figure; all four reversed on user pushback.

### F38. Notes Auto QC cannot act on or ground
- Rule: quote the exact current text and its replacement; a fix that removes a branch states the full positive PASS test; give a strict precedence where several figures could be graded; a population fix gives the count, its breakdown and one per-row test; quotes are verbatim with locators; new IDs carry file, sheet, column and row; counts name their population; no reference to a rule that exists only in your own proposed fix.
- Check: run every note against the Auto QC checks in 09 §4 before submitting.
- Evidence: RKLB's three notes failed actionability at Severity 2–3; ARC's six notes failed for describing instead of quoting; REI said paragraph seven for eight; HAL's real IDs read as "fabricated"; ACL's "The instruction names no tabs" was false.

### F39. Fields that contradict each other
- Rule: an AGREE with a FAIL on a verifier means REJECT on that verifier with the same Fix; AGREE when any cited defect is real in this version, DISAGREE only when none is; never flip a judge check to back a file REJECT; never write "Fixed" for a change not yet made; an APPROVE comment carries no defect language.
- Check: cross-tab the judge answers against the per-item verdicts before sending.
- Evidence: VES v4 agreed the self-contained FAIL on bond_position_decisions but approved it; ACL v10, "You agree with the Fail but also says Fixed?"; REI v1 agreed a leakage PASS while rejecting the leaking file; VAL offered a cross-file DISAGREE to back an intra-file REJECT.

### F40. Jargon, length and file cards
- Rule: C3, C4 and C7: plain words a non-specialist can follow, one reason sentence per reject, no file internals or tool names, inline only.
- Check: the plain-language grep in the pre-send checklist.
- Evidence: VES and ORN, "I don't understand all this … write in simple terms … It should look like a human expert reviewed it"; ORN, ARC, HAL and ACL asked for shorter notes; REI's file cards never rendered.

### F41. Repeated FAILs without a diagnosis
- Rule: after a second consecutive FAIL on one section, lead with one paragraph classifying every new FAIL from the diff: prior fix not applied, side effect of our own fix, defect we missed earlier, new judge finding, or judge tooling or unrequested regeneration.
- Check: the lead counts each class with evidence.
- Evidence: ORI, CAL and HAL users asked whether "the feedback is not thorough enough or the platform is not taking the feedback"; CAL's count was 5 missed by review, 2 wrong or optional fixes, 1 from a fix, 0 from the platform skipping a required fix.

### F42. Accepted alternatives the grader cannot check
- Rule: wherever a rubric accepts "other supported" choices under a tight tolerance, inline every input a grader needs to compute them (dates, conventions, formula), not only worked examples.
- Check: compute one unlisted alternative from the criterion text alone.
- Evidence: VES v4 bond_position_decisions accepted any reserve at 0.10 on price without the settlement, coupon and maturity dates; the judge failed it after the review approved it twice.

### F43. Fix text that names other verifiers
- Rule: scope sentences say inward what this criterion assesses and what to ignore; never name another verifier or write graded by, separately or elsewhere.
- Check: the self-contained grep in the pre-send checklist.
- Evidence: HAL v7 failed seven verifiers on self-containment, six from the reviewer's own wording.

### F44. Structure changed to hit a set size
- Rule: set size never justifies a merge, drop, split, relabel or reversed verdict; when QC says a remedy cannot be applied, change the remedy and keep the verdict.
- Check: every structural request cites atomicity, redundancy or obligation ownership.
- Evidence: CLO's rework called a composite atomic and rejected sound verifiers to restructure the set; CRW's conditional drop orphaned the control gaps; ACL's merges made for structure's sake failed atomicity.

### F45. Agreeing with every External QC finding by default
- Rule: test each finding's own complaint and its own example of a correct answer; agree only when that complaint holds in the current verifier file and needs a change.
- Check: the lead names the closest call, and every Agree survived the Pass 2 attack in reference 10.
- Evidence: the user asked "you sure you agree with all findings?" after every External QC round in the sessions (eleven); LHF finding 4 (the prompt asks how sensitive the answer "is to unresolved terms"), three MKT market findings and three KRD findings were then reversed to Disagree.

### F46. External QC fixes routed outside verifier.json
- Rule: at External QC only verifier.json changes; take a sound verifier-only cure when one exists, and say in the first sentence when an agreed finding rejects the task.
- Check: no fix request touches instruction.md, a source or the golden.
- Evidence: LHF added a decision-summary sentence and NLR a scenario date to instruction.md; the user at HAL's verifier stage: "I can't change instruction.md, I am at the verifiers stage".

### F47. Grader faults agreed as true positives
- Rule: a failure no verifier.json change cures (authentication errors, ties, a judge whose reasoning says met but scores 0, timeouts, extraction limits, import deadlocks, sandbox clock) is a Disagree with "No change needed to verifier.json" and an escalation.
- Check: every Agree names the criterion text it changes.
- Evidence: KOW round one agreed six grader findings with "No change required to verifier.json"; the user's bar, "if there are no change then its a false positive".

### F48. Unasked requirements approved at Final Review
- Rule: a PASS condition the prompt never asks for, or one accepted reading where the prompt and sources allow another, fails a correct answer and meets Final bar (b).
- Check: every literal figure, label, closed list and placement in a criterion traces to a prompt clause.
- Evidence: External QC reviews (solver runs or file reads) failed correct answers on LHF's "$6,640,000", RAQ's "405.96255m", COV's closed owner list with no Treasurer in the packet (a file-read finding), TRS's reopened reconciliation and KRD's 529.5992 EBITDA reading; each had been approved or made optional at Final Review.

### F49. Golden graded on its arithmetic, not its words
- Rule: grade the golden literally against every FAIL clause, labels and ordering included, and test each pass case against the governing standard.
- Check: each FAIL clause has been read against the golden cell or sentence it could catch.
- Evidence: IDC's golden A95 "backlog (earliest demand) > current-month demand" failed its own criterion in both oracle runs; CUS's A06/A07 labels failed workbook_sheet_assumptions; RAQ's EPS pass case breached IAS 33.36/.38.

### F50. Regenerated verifier files trusted
- Rule: diff every verifier file against the last approved or corrected version before any verdict; report lost agreed edits and unrequested changes, and escalate missing edits.
- Check: the version-delta ledger lists both.
- Evidence: CUS v43, IDC v41, TRS v45 and KRD v47 had silently lost agreed fixes and gained whole-workbook judges, a duplicated judge model or a garbled "PASS only if " prefix.

### F51. Out-of-scope extras in an External QC answer
- Rule: the fix request covers the agreed findings only; lost prior edits get one separate sentence; any other defect goes to the user in one line; a corrected file is given only on request.
- Check: every edit in the request names the finding it resolves.
- Evidence: MKT bundled five unraised Final Review fixes, a deleted verifier and re-scaled weights into a revised file; the user: "I am not gonna take your revised json, need to instruct the QC team… a single comment".

### F52. Model Output severity miscalibrated
- Rule: Critical or Nice to have only; Critical for any wrong value, unfollowed instruction, invented support or missing required content; never lower a label because the conclusion holds or the convention is disclosed.
- Check: no Nice to have entry quotes a wrong figure.
- Evidence: HWI used Critical/Major/Minor/Cosmetic until the user said "there are only two categories"; BKS's "Major, not Critical: the decline holds" and HWI's "the 252-day figure is reasonable" failed Severity Calibrated across several retries.

### F53. Button and words disagree
- Rule: clean means APPROVE, AGREE with a PASS or DISAGREE with a FAIL; broken means REJECT, AGREE with a FAIL or DISAGREE with a PASS; read each note against its button before sending.
- Check: no approve-side note carries defect words, no reject-side note says clean or unchanged.
- Evidence: the trainer-gate guide names this the cause of most re-dos; CUS's "This verifier fails a correct response… PASS test is unchanged" failed decision/note coherence as a polarity inversion, after a first failure for a bundled note.

### F54. A figure called wrong against the wrong column
- Rule: before flagging a number, confirm which column, list and population the checker means (median or top-decile, one list or another).
- Check: each "wrong figure" claim names the column and population it was compared with.
- Evidence: the trainer-gate guide's third leak; PBM's judge counted 6,134 blotter events against 6,128 because it took the last row number, header and footer included.

### F55. A Source Data Disagree that denies the judge's offender
- Rule: name every offender the judge cited, then argue scope or evidence; never claim the judge named nothing or that a named item is not a defect.
- Check: each Source Data Disagree quotes the judge's offender list.
- Evidence: LQP failed note factual groundedness because "the judge's offenders list explicitly named all three files for 'Machine-style filename'", after the section had locked.

### F56. Identity taken from an upload
- Rule: never derive a task ID from a file name or upload ID, and never assume which screen a paste is; ask.
- Check: the task ID in every answer matches the pasted screen.
- Evidence: BKS called the upload's file ID "22d8fd8a" the task ID; HWI assumed screen 2/6 was Model 1's workbook.

### F57. Parallel drafters drifting apart
- Rule: fix one shared policy (bands, caps, anchors) before parallel drafting and reconcile centrally; re-check every relayed header and figure.
- Check: one value per shared parameter across all drafts.
- Evidence: OPR's three drafting agents set the term cap at 5.37, 5.4 and 5.25 years; NLR's subagent wrote "finding 3" for the screen's "finding 1".

### F58. Rejecting more than owns the problem
- Rule: find the one file or item that owns the defect and reject only that; preventive edits are Approve plus an Optional line, never a REJECT.
- Check: every REJECT names the realistic mis-grade it prevents.
- Evidence: the trainer-gate guide's fifth leak; LQP's "you have failed 29 verifiers, are yo usure…?" held for 12, the other 17 being preventive edits.

### F59. Reworks trusted without a spot-check
- Rule: after any rework, re-check the things that depend on what changed (totals that must still add, planted traps that must survive, neighbouring criteria that cite the same figure).
- Check: each changed item has a dependency list that was re-read.
- Evidence: the trainer-gate guide's seventh leak; F32 and F34 record the same failure at Source Data.

## Reviewer habits

- Shortening that drops load: cut explanation, never conditions, fallbacks, "do not" clauses, IDs, locators or anchors. REI's short note lost its fallback, and the phantom clause it warned of followed.
- Tally errors: compute every count from the entries, and name the exact check behind any "reversing my earlier" line. CRW wrote "six get Disagree" over eight.
- Burying the binding finding: lead with it. REI's source defect sat below seven REJECT notes.
- Process slips: answers inline in chat, never in a file card; scratch work in the scratchpad. REI wrote review output into the repository and put notes in a file card that did not render.
- Figure drift: keep one ledger of your own figures across versions, and when a figure differs from your earlier one or the plan's, state both and the basis of each. REI's rating factor moved 0.853 → 0.9013 → 0.898750 with no reconciliation.
- Context loss: reload SKILL.md and this file after a context compaction or a long gap. ACL's v9 notes, written after a compaction, broke three verifiers.
- Stale rules in long sessions: a session started before a rulebook change does not load it; re-read SKILL.md and this file before re-pasting earlier notes. HAL re-pasted wording the rulebook had banned and it caused ten FAILs.
- Counting from the brief: count verifiers and fields from the files. VES's brief said 40 verifiers against 39 and the subagent flagged a false mismatch.

## Probe battery

1. Corner sweep: every anchor and band under each defensible convention and permitted treatment; known-wrong methods outside.
2. Minimal fake: labels, owner and deadline, no case facts. If it passes, bind to a source value or case ID.
3. Obligation map: each named field and each/every/all clause → a quoted PASS/FAIL phrase.
4. One-owner diff: under the ledger check, one owner per O# per artifact; under the older check, one owner per value per artifact.
5. Coupling test on every AND: under the ledger check, a rubric is composite only when its parts serve different O#s; under the older check, split any AND whose parts can fail separately.
6. Proxy test: could a non-compliant output meet the test?
7. Governing-term quote, each condition marked met or unmet.
8. Population scan: every condition traces to the prompt or a source. For "a different X", count the qualifying rows.
9. Embedded-fact recompute: every figure, illustration, preamble fact and cross-reference.
10. Binding: spot checks sit inside PASS.
11. Degradation clause wherever formula text, cached values or formatting matter.
12. Discrimination: a shortcut hitting the graded value is a note unless it is a known-wrong method.
13. Magnitude: each headline number has a floor and a ceiling; an absurd value fails.
14. Weights: if a planned anomaly is graded only by secondaries, suggest a relabel on the Optional line; never REJECT for weight, delete or fold.

## Recurring judge demands

Trainer overrides do not carry across versions: when a check re-fails content an earlier version passed, re-issue the same DISAGREE quoting the earlier pass (ORN). A FAIL caused by the judge's own tooling (no OCR data, a failed render, a read-only workspace) gets your own inspection and a DISAGREE with no change requested (HAL v5, passed by Auto QC). Log every rejected demand and answer each repeat with the same short DISAGREE and instruction quote; after a second flag on one point, re-derive from source and hold only on a quoted basis. REI turned away a seven-labelled-tabs demand four times by quoting "Prefixes or suffixes on those labels are fine". REJECT on sight: file-exists checks against the rubric-first policy (CLO, CRW, REI), ROUND-function string checks (CRW), anchors called leakage (ACL), another artifact's anchors (REI), cross-artifact rubrics, facts the pack lacks (REI competing claims, ACL partner name), tab labels as a test (REI), and remedies that hand over the answer or remove the work (REI's 2027 market schedule, ACL's F4 anchoring). When two checks conflict, TAKE one, REJECT the other by name and escalate (CLO v3).

## Final Review bar and the LHF case

Rejecting Task Design, a source, the prompt or the golden ends the task; a verifier REJECT sends that verifier back for repair. Block a verifier only when (a) the rubric misstates a governing term; (b) a realistic submission is mis-graded, shown on a supplied output or on a concrete submission under an accepted reading; or (c) the golden fails a sound verifier, once you have decided which side is wrong. Everything else gets an optional line: stale figures that change no result, hypothetical overlap or bundling, reasonable placement or format readings, extractor observability (NOT VERIFIABLE plus escalation), weight or difficulty labels, mechanical source slips, and planned difficulty.

LHF round one rejected Task Design against verifier scope, Source Documents over conditions their own notes explain, and 14 verifiers. Against the bar both layers went to APPROVE and 11 REJECTs fell: wrong anchors that changed no result (V15, V16, V18, V24), hypothetical overlap or edge cases (V3, V36), a workbook-wide check that `08_excel_verifier_scoping.md` allows (V21), and reasonable readings of the prompt (V14, V33, V35, V38). Three stood: a double penalty shown on a supplied output (workbook_performance_fee_mechanics), and a 35% cap missing Part V 5.3's documented-taxes condition (workbook_ltd_giveback_rollforward, memo_giveback_conclusion). The golden passed all three, so the flaws lie in grading other submissions. The closing line, as the bar requires it:

Overall: verifier REJECTs only — workbook_performance_fee_mechanics, workbook_ltd_giveback_rollforward and memo_giveback_conclusion go back for repair; the task continues. Every submission so far concluded a $0 give-back, so the two cap REJECTs rest on a branch no submission has taken; they stand.

The full answer is in `04_completed_task_examples.md`. Two cautions. V14 and V35 were approved without quoting a prompt basis although both supplied outputs failed V14; under F01 an approval like that now needs the prompt or anomaly-plan quote that makes the item a reasonable reading. And External QC later showed correct solver runs failing LHF criteria approved here as "strict but defensible" placement and literal-figure readings ("$6,640,000", "total GP fee"): a PASS condition the prompt never asks for meets (b) and is not an optional placement reading (F48).

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
10. Platform check: each REJECT names the on-screen check whose Description it breaches; overlap and atomicity are answered under the pasted version (ledger or older).
11. Cross-field: each AGREE with a FAIL on a verifier matches a REJECT on that verifier with the same Fix; each judge answer matches the per-file verdict; every finding lands on a field or the Optional line; no APPROVE comment carries defect language.
12. Plain-language grep: `docProps|app\.xml|core\.xml|python-|openpyxl|reportlab|pypdf|XML part|formula field`; say it in the author's terms (File > Info, sheet and cell, page and section).
13. Rubric-text grep inside your proposed wording: any verifier ID, and `graded (only )?by|graded separately|graded elsewhere|separate criterion`.
14. Tense grep in AGREE notes: `Fixed\.|now (does|grades|reads)|is removed`; an unmade change reads "Required change".
15. Field headings: each note names the platform field it goes in; source edits sit in that file's File artifact feedback, never in a judge-check comment alone.
16. Gate visibility: at Final Review, no note names a model output.
17. Button match: every note's words match its button (F53), and every note ends with a decision and a location, never a question or a blank "Fix:".
18. Right column: every "wrong figure" claim names the column, list and population it was compared with (F54).
19. One place, every place: when you change your mind on an item, search its name and fix every place it appears before sending.
20. Rule check: no fix breaks a stated platform rule or the verifier.json schema; if it would, change the fix, never the verdict.
21. External QC: one entry per card with its exact screen header; the fix request covers only agreed verifier findings plus one sentence on missing earlier fixes; no Final Review field verdicts or Overall line (reference 10).
22. Model Output Review: severity is Critical or Nice to have, and each entry's wording matches its label (F52).
