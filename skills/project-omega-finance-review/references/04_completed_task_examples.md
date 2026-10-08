# Completed Task Examples

Completed work for calibrating design, difficulty and the review bar. Part A holds three completed golden packages: use them to judge whether a task is realistic and hard in the right way, and whether a golden earns its APPROVE. Part B holds completed review tasks from the September–October 2026 sessions: the LHF Final Review, and why six Trainer Reviews bounced between versions, each ending with the lesson that would have stopped the loop. Task keys are those in `07_failure_patterns_and_lessons.md`; accepted notes are collected in `05_real_feedback_examples.md`.

Use the examples as behavioural exemplars, not answer patterns:

- Imitate the evidence chain: source authority → recomputation → tie-out → bounded uncertainty → decision.
- Do not import their numerical thresholds into unrelated tasks.
- Do not assume every conflict is an anomaly, or that a condition the anomaly plan omits is a defect. Planned-difficulty test, before calling any source condition a defect: read the cover and notes sheets and the prompt's caveats, test every plausible convention over all periods, and ask whether a graded figure moves. If the golden and models resolve it through the authority order, it is planned difficulty: an optional note at most.

## Part A — Completed golden packages

Only task folders containing a completed Golden Solution or expert_improved output were used; in-progress folders are excluded from this ground-truth set.

### Example 1 — Riverbend Packaging Holdings: private-credit re-underwriting and regulator support

- **Source set:** original underwriting memo, SEC request packet, monthly close/sales export, and QoE/lender-model extract.
- **Golden outputs:** re-underwriting workbook, regulator response memo, continue-diligence deck.
- **Core reasoning:** rebuild LTM EBITDA from close detail; resolve the March cutoff; correct a currency-basis problem; reject unsupported add-backs; normalise duplicate debt; recompute debt, interest, liquidity, leverage and coverage.
- **Authority:** underlying close, sales and GL-style records control the numeric rebuild; the summary screen and lender model are tested, not trusted.
- **Decision:** continue diligence only on the corrected case, keeping the broader currency-basis view as a sensitivity rather than the primary result.

Golden results: corrected LTM adjusted EBITDA $24.89mm; corrected gross debt $183.99mm; net debt $166.20mm; annual cash interest $15.40mm; remaining liquidity $24.63mm; net leverage 6.68x; interest coverage 1.62x. The broader all-month currency-basis sensitivity lowers EBITDA to $21.21mm, leverage to 7.84x and coverage to 1.38x.

Why it is a strong benchmark: it does not accept the "live screen" because it looks professional. It reconstructs the record, separates a supportable primary interpretation from a broader sensitivity, and keeps source deficiencies apart from quantified credit conclusions.

Checks to imitate:

- Trace reported EBITDA to the monthly close before assessing adjustments.
- Check cutoff at invoice, shipment and delivery level.
- Normalise debt IDs before summing principal and interest.
- Separate recurring costs from genuine one-time adjustments.
- Carry every correction into leverage, coverage, liquidity and the recommendation.

### Example 2 — Arcadia Global Benefits: Q2 management close rebuild

- **Source set:** raw ledger/export, treasury FX and reporting map, close-calendar guidance, preliminary overnight close packet.
- **Golden outputs:** Q2 close review workbook and leadership readout deck.
- **Core reasoning:** rebuild from raw transactions; remove a duplicate; retranslate FX; apply the close cutoff; apply effective-dated mapping; evaluate a signed late journal under the special bridge window.
- **Authority:** the frozen extract is the baseline, not the final truth. Close-calendar timing and the current reporting map govern inclusion and classification; the overnight packet is supporting evidence, not a substitute for the rebuild.
- **Decision:** carry a management-view adjustment and do not rerun the frozen extract, because the differences are narrow, authorised and fully reconciled.

Golden results: frozen-extract operating income of $67.634m moves to final management-view operating income of $70.002m. The bridge is −$32.4k FX retranslation, +$262.8k duplicate removal, +$242.0k cutoff exclusion and +$1.895m signed-late inclusion. Final revenue is $128.2m and operating margin 54.6%.

Why it is a strong benchmark: it separates source recency from source authority. A signed late item missing from the frozen pull can still belong in the management view when the approved close rule explicitly allows it.

Checks to imitate:

- Use timestamped close rules, not a period label, for cutoff.
- Do not double-count the preliminary packet and the raw population.
- Keep mapping-only reclasses separate from changes to total P&L.
- Bridge every correction from frozen baseline to final view once.
- Make the rerun or no-rerun recommendation follow the evidence, not instinct.

### Example 3 — AlloyWorks Motion Systems: 90-day liquidity and captive response

- **Source set:** treasury position and scheduled uses, customer collections worklist, captive information request and funding conditions, liquidity facility and covenant update.
- **Golden outputs:** 90-day liquidity model, regulator response memo, treasury committee briefing.
- **Core reasoning:** use value-dated cash; correct currency-denomination errors; fix debt amortisation; protect the lender cash floor and captive coverage; distinguish firm relief from approval- or customer-dependent relief; run fixed scenarios.
- **Authority:** bank value date and entity/account restrictions control usability; lender and captive restrictions are applied conservatively when they conflict.
- **Decision:** the captive can stay above required coverage after the opening cure, but parent liquidity remains materially short; documented bridge actions buy timing but do not eliminate the modelled residual.

Golden results: base unrestricted covenant cash first falls below the $2.75m lender floor on 14 Aug 2026, turns negative on 18 Aug and reaches −$15.56m by 12 Oct. Captive coverage opens at 1.12x, rises above the 1.15x minimum after the 16 Jul premium, and stays compliant if scheduled premiums are funded. The combined documented bridge still leaves a residual of about −$13.61m.

Why it is a strong benchmark: it separates liquidity from solvency and firm relief from contingent relief, and it says the worst tail partly reflects the finite collections-worklist horizon rather than pretending the business will collect zero cash.

Checks to imitate:

- Apply value date, cutoff and account/entity restriction before counting cash.
- Correct currency unit errors before summing receipts.
- Do not use captive assets if doing so breaks the captive coverage condition.
- Do not call a lender draw "firm" while notice, approval or borrowing-base conditions remain.
- Check whether a deferral only moves a use within the same horizon rather than curing the cumulative gap.

### Cross-example patterns

| Pattern | Riverbend | Arcadia | AlloyWorks |
| --- | --- | --- | --- |
| Do not trust the summary artifact | Original credit screen | Frozen extract / overnight packet | Promise worklist and facility summary |
| Authority is fact-specific | Close, sales and debt records | Close calendar and effective map | Value date and lender/captive restrictions |
| Chronology matters | March cutoff | 00:07 / 00:15 / 01:00 windows | Daily value date and bank cutoff |
| Definition or unit drift matters | Currency basis; recurring vs add-back | FX and mapping basis | CAD vs USD; restricted vs usable cash |
| Decision follows rebuilt evidence | Continue only on the corrected case | Carry the management adjustment | Disclose the residual; bridges insufficient |

## Part B — Completed review tasks

### LHF — Final Review, v24 (Halcyon Ridge Evergreen fee close)

**What was asked.** The package had two deliverables, output/2025_fee_close_model.xlsx and output/controller_fee_conclusion_memo.docx. The platform asks for Approve/Reject on Task Design, Source Documents, each LLM verifier and Golden Data, under the header "Confirm each verifier is ship-ready; a rejection ends the task." The user: "Run Final Review on the latest package. Verify the prior fixes yourself and give me the exact Approve/Reject answers I should enter on the platform for each - Task Design, Source Documents, verifiers, and Golden Data."

**The bar.** A verifier rejection ends the task, so block only when the rubric misstates a governing term, a realistic submission is mis-graded (shown on a supplied output or a concrete submission under an accepted reading), or the golden fails a sound verifier once you have decided which side is wrong. Stale figures that change no result, hypothetical overlap or bundling, reasonable placement or format readings, weight or difficulty labels, mechanical source slips and planned difficulty get optional lines; extractor observability gets NOT VERIFIABLE and an escalation.

**Round-by-round correction.**

1. The subagent briefs said "Be strict but do not reject on style; reject only for genuine material defects", never stated the terminal consequence, and asked of Task Design "does the prompt clearly state everything the verifiers demand". The first answer was Task Design REJECT (the anomaly plan judged against verifier scope, a $0 versus ~$659,000 give-back, "medium" against an 840-minute handling time), Source Documents REJECT (HWM Trajectory against the register in all 48 class-months, eight approver names against "Controller Mara Velez", allocation factors), Golden APPROVE, and verifiers 24 APPROVE / 14 REJECT.
2. The user: "it ahs to be independent of verifiers. First task design is created then the verifiers at last". The sources' own notes (the HWM Trajectory chronology note; Class Allocation Support's "Relative allocation factors only") and the prompt's caveat ("do not assume every total, date convention, or approval is explicit") made the source conditions planned difficulty, so Task Design and Source Documents went to APPROVE. The verifier rejects were left standing and V14 was called "stronger", although V14 rested on the source reasoning just withdrawn.
3. The user: "this was the final step where the verifiers should have been approved". Re-tested against the bar, 11 rejects fell: wrong anchors with no pass/fail effect (V15, V16, V18, V24), a hypothetical edge case or overlap (V3, V36), a workbook-wide formula check that `08_excel_verifier_scoping.md` allows (V21), and reasonable readings of the prompt (V14, V33, V35, V38). V13, V20 and V26 stood. Mechanical source slips (formulas without cached values in the Activity Register summary block, 262 against 261 rows, seven market holidays counted as valuation days) and six weights contradicting their core/secondary label stayed optional.
4. The user asked for "the names of all the verifers that are approved and reject": two plain lists.

**Round-3 answer, restated to the current note standard.** The user accepted it; the platform outcome after submission is not recorded.

Task Design — APPROVE. Judged on its own terms, since it is written before the prompt, sources and verifiers: a realistic fee-close scenario, two decision deliverables with clear purposes, the four source packages mapped, and three planned anomalies realised in the sources and carried into instruction.md. Prescribing the Class C H1 treatment in the prompt is a prompt-layer choice, not a design defect.

Source Documents — APPROVE. The HWM Trajectory note says its references are "retained for chronology; class capital-account detail and allocation components remain in the companion capital-account package", so a solver rebuilds high-water marks from that package and the register, as the golden and both models did. The approver names move no fee, HWM or give-back figure, and ACT-7B3F9D remains the only one of 136 records with a blank Controller approval and the same preparer and releaser.

Golden Data — APPROVE. It passes every verifier, and its formula-driven key figures recompute from source: management fee $5,078,354 with the add-back disclosed, $0 performance fee for every class, give-back E22 = MAX(0, $17,840,000 − $17,840,000 − 0) = $0, adjustment −$1,561,646, the $148,000 residual kept open and $215,025 shown memo-only. LibreOffice could not recalculate in the sandbox, so formulas were read against their cached values. It passes the three rejected verifiers, so their flaws lie in grading other submissions, not in the golden.

The 35 approved verifiers each took one line, "<name> — APPROVE."; the three REJECTs read:

workbook_performance_fee_mechanics — REJECT. The clause "accept a separate recorded redeemed-portion result of $0 that is formula-linked to the missing-valuation input…" and the FAIL limb "or an indicative redemption-date proxy is used to produce the recorded redeemed-portion result" grade what workbook_performance_fee_redeemed_portion already owns. Model 1's mechanics otherwise match the golden, yet it fails both verifiers for one defect: Perf_Fee_Calc!C66 =SUM(S5:S16), a month-end proxy. Fix: delete both clauses and end the criterion with "The redeemed-portion test must be computed by formula at each redemption (it may be labeled an indicative cross-check); how the recorded redeemed-portion result is derived is graded only by workbook_performance_fee_redeemed_portion."

workbook_ltd_giveback_rollforward — REJECT. The criterion applies "the 35% after-tax cap only if gross excess is positive", and reading (ii) makes the give-back "subject to the 35% cap"; Governing Documents Part V 5.3 allows the cap "only where the GP documents taxes actually paid… Without documentation of taxes paid, the required return is the gross excess", and the records hold none, so a wrongly capped give-back of about $428,000 would pass on the ~$659,000 reading and a correct gross answer could fail. Fix: replace the cap language with "treats the 35% after-tax cap as available only where the GP documents taxes actually paid (none are in the records, so any positive excess is due gross)"; make reading (ii)'s give-back due gross; add to FAIL "or the cap applied, or used to reduce or force zero, without documented taxes paid".

memo_giveback_conclusion — REJECT. The criterion accepts "the 35% after-tax cap only if gross excess is positive", but Governing Documents Part V 5.3 allows the cap only where the GP documents taxes actually paid, and the records hold none, so a memo concluding a capped give-back of about $428,000 on the ~$659,000 reading would pass. Fix: replace every statement of the cap with "treats the 35% after-tax cap as available only where the GP documents taxes actually paid (none are in the records, so any positive excess is due gross)"; add to FAIL "or the cap applied, or used to reduce or force zero, without documented taxes paid".

Optional: workbook_performance_fee_class_entitlement's preamble gives the Class R HWM-only excess as $139,300; it is $202,616 (17.5% × ($38,967,718 − $37,809,911)), and the pass test is still $0 for every class.

Overall REJECT, because one verifier rejection ends the task: workbook_performance_fee_mechanics, workbook_ltd_giveback_rollforward and memo_giveback_conclusion. Every submission so far concluded a $0 give-back, so the two cap REJECTs rest on a branch no submission has taken; they stand.

Lesson: set the bar and the terminal consequence before grading and quote both in every brief; judge Task Design before and apart from the verifiers; when challenged, re-test each item against the same bar instead of reversing wholesale, and state what evidence changed.

### Why six Trainer Reviews bounced

#### ACL — Kestrel Valley Bancorp CECL ACL audit (v1–v7, two Auto QC reworks)

The anchors were recomputed ("Every dollar figure, rate, loan number, property name and band is correct") but the verifiers were never probed, so judges found one design defect per round: an "at least four of these five" bar against "each data-conversion exception found", no $5.9M overall-materiality comparison, individually-evaluated spot checks sitting outside PASS, an alternative accepted "if … it produces a higher reserve", a fixed $16.0M–$19.8M overlay band beside judgmental factor scores, and the false "posted after year-end". Two verifiers both gating $70,248,785.00 and the $17.25M Riverside correction were waved through as "a shared anchor, not double grading". The agent's own wording ("equals, to the cent"; "PASS if, for each carry point present") failed later judges, the v2 regeneration silently dropped two verifiers, and Auto QC twice failed notes that pointed at "the replacement criterion above" or "the fixes above". At v7 the agent named the loop: "one judge finds a defensible answer that the hard-coded path rejects, the regenerator patches that single spot, and the patch creates a new conflict somewhere else."

Lesson: run the probe battery on every verifier every round, Unchanged ones and your own wording included, and fix every finding in one pass; where the instruction leaves a choice, grade the derivation rather than one path; keep a version-delta ledger so dropped verifiers surface.

#### REI — AS-FIN2 reinsurance recoverables (v1–v8, two Auto QC reworks)

At v8 the agent conceded: "Three of the eight FAILs are mine … I fixed each rubric in isolation and never traced what the fix did to its neighbours." The 840–1,070m band bolted onto the chain verifier failed atomicity, a residual phrase duplicated the trust rubric, and the EMBER-WEST-2026 × CAT-26-A3 exclusion produced 52.9066%, outside its own ±2pt. That EMBER source defect (USD 90,475,015 booked below a USD 1.25bn attachment) sat under Escalations at v4 and v6, was never fixed, and the verifier escape clause used to contain it cascaded into later FAILs. A note asked for a new policy clause and a repointed prompt; only the prompt changed, so v3 cited a phantom "OPTIMIZATION ORDER"; the fallback that would have prevented it, inlining the clause if the policy pack was not regenerated, had been cut when the note was shortened. N-of-M bars ("any three of four" conflicts) left the Harborstone fronting and Boreal enforceability conclusions optional; paper_references_workbook_calculations, approved at v3, failed keyword hacking at v4 and v5; and v5 arrived byte-identical to v4 on every verifier.

Lesson: before handing back wording, grep every neighbour, re-run touched bands at their corners and attach a ripple list; file a source defect as a blocking Source Data note, never only as an escalation or a verifier escape clause; align the prompt to source text that already exists; when shortening a note, never cut its fallback.

#### CRW — Crownmere fallen-angel bonds (v1–v6, submitted at v6)

Approvals were argued, not tested. The ±0.3pp band on −2.96% was approved twice until a judge showed a D−5 base (−2.6502%) and the trough (−3.2642%) failing by less than a hundredth of a point: "The rubric didn't change; my testing did." memo_post_day100_control_gaps was approved as hack-resistant by reasoning, then a fake with labels, an owner and a deadline passed "in one attempt". The agent's conditional nomination of that verifier for deletion was executed at v4, leaving the control gaps "Permitted everywhere, required nowhere". The v2 source fix of four added mandates made deck_combined_platform_standard's grace-period preamble false. Five non-blocking text fixes, the 2.24x parenthetical and the D+5 trough label among them, were repeated for three to five rounds and never applied, and the trough error was copied into a new verifier.

Lesson: approve a band only after its corners are computed and a memo rubric only after the cheapest fake fails it; give one definite instruction per item and name the new owner of every obligation before any deletion; classify each fix once and promote a rideable to blocking as soon as it propagates.

#### CLO — Larkspur 2021-3 CLO (v1–v3)

At v1 no files had arrived, and the agent AGREED with the leakage and labelling PASSes on the judge's prose. Those PASSes hid indenture §6.3, the Schedule 9 narrative and the Table 6 certificate row stating "The later of the two SI6 condition dates is 2 September 2026 … applies the 10.0% threshold", which hands over every PASS condition of the core wb_operative_ccc_threshold, and a single Payment Status filter ("Defaulted — Past Grace") that isolates Meridian. At v2, with the leak found, the agent still answered "AGREE on the check as scoped". A whole round was lost when the REI v3 zip was reviewed against the CLO screen and the mismatch was flagged only in the last line. Judge text repeated byte-identically on all four files although the evidence sat in Larkspur_Collateral_Surveillance_2026-09-18.xlsx, and the agent's own v2 split wording, "ending between $468,000,000 and $473,000,000", became wb_acp_bridge and double-gated the ACP that wb_corrected_acp_oc owns.

Lesson: confirm pack identity in the first line and mark evidence-dependent questions PENDING INPUT rather than agreeing on a judge's prose; let each file's verdict match your own finding on that file; gate each value in exactly one verifier per artifact.

#### HAL — Halvorsen/Northbridge captive collateral (v1–v2, one Auto QC rework)

The first pass chased the judge's FAILs instead of sweeping, so v2 raised items "present in v1 and … raised here for the first time". No timeline was built: HIL-AR-2026Q2 is dated 2026-08-12, after the 2026-07-20 window end, which flips the governing reserve that V4, V7, V8 and V13 depend on. The v2 actuary-date fix missed Table 15 ("Await appointed actuary report") and treasury cells E9, A22 and A29, and the agent's own Recital B wording, "all open policy years from 2019 onward", turned 11 claims over the $1M layer ($8.85M) into a two-expert divergence. Auto QC failed seven judge notes that said what was wrong but not how to fix it ("The fixes are in the artifact verdict below"), and a provisional "lean Disagree", given when only an unchanged task_design.json had arrived, was later reversed.

Lesson: in round one, build a dated timeline, sweep every file and report everything at once; after any scope fix, recompute the headline under each defensible reading and block if it flips; end every defect note with a standalone Fix:; give no provisional leaning on a PENDING INPUT question.

#### SPV — Silverpine CV sell-or-roll (v1)

This review bounced the other way, on over-rejection. The agent rejected 11 verifiers, the workbook and the Prompt and DISAGREED with 8 judge checks; after the user's "check again, I believe all are passing", every one was reversed. It called verifiers that share amounts but grade different obligations overlapping (sale_schedule_status, roll_schedule_status, downside_liquidity), demanded IRR bands although the 12% gate never flips across conventions (14.79–15.26%), and read the guard "accept a $0.876m reclassification only if … separately supported" as unsatisfiable. It tested the Preliminary Close "break" under one convention (−6725 Dr), which breaks March only; netting accrued-payable credits instead (−2150 Cr) reproduces all seven roll-forwards, and the break was the planted PEX-44 anomaly. It also DISAGREED with a cross-file check over intra-workbook mismatches, and relayed subagent IRR ranges it had not checked. The platform judge's bar was explicit: "a fail needs the counterexample showing the disagreement."

Lesson: REJECT only with a one-sentence counterexample; run the planned-difficulty test before calling a source condition a defect; read each check's scope literally, so cross-file means between files; re-verify any finding that drives a REJECT before relaying it.

## Source basis

Part A comes from completed golden packages in the uploaded RL World task folders, read against the RL World Finance Expert Onboarding (v6), the RL World Platform Quick Reference and Platform Overview, the Project Omega Guide (V5), the Trainer Review Gate Convergence Report (production data through 23 Sep 2026) and the Omega Pod finance and investment tracker. Part B comes from the review sessions recorded in `07_failure_patterns_and_lessons.md`.
