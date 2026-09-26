Worked Examples — Completed Finance Task Packages

Three real completed golden packages from the supplied RL World folder

Project Omega | Finance & Insurance reviewer knowledge pack | 25 Sep 2026

Example 1 — Riverbend Packaging Holdings: private-credit re-underwriting / regulator support

Selected golden results: corrected LTM adjusted EBITDA $24.89mm; corrected gross debt $183.99mm; net debt $166.20mm; annual cash interest $15.40mm; remaining liquidity $24.63mm; net leverage 6.68x; interest coverage 1.62x. A broader all-month currency-basis sensitivity lowers EBITDA to $21.21mm, leverage to 7.84x, and coverage to 1.38x.

Why this is a strong few-shot example: it does not accept the “live screen” because it looks professional. It reconstructs the record, distinguishes a supportable primary interpretation from a broader sensitivity, and keeps source deficiencies separate from quantified credit conclusions.

Reviewer checklist to imitate

Trace reported EBITDA to monthly close before assessing adjustments.

Check cutoff at invoice/shipment/delivery level.

Normalize debt IDs before summing principal and interest.

Separate recurring costs from genuine one-time adjustments.

Carry every correction into leverage, coverage, liquidity and the recommendation.

Example 2 — Arcadia Global Benefits: Q2 management close rebuild

Selected golden results: frozen-extract operating income $67.634m moves to final management-view operating income $70.002m. The bridge includes -$32.4k FX retranslation, +$262.8k duplicate removal, +$242.0k cutoff exclusion, and +$1.895m signed-late inclusion. Final revenue is $128.2m and operating margin 54.6%.

Why this is a strong few-shot example: it shows the difference between source recency and source authority. A signed late item missing from the frozen pull can still belong in the management view when the approved close rule explicitly allows it.

Reviewer checklist to imitate

Use timestamped close rules, not a period label, for cutoff.

Do not double-count the preliminary packet and raw population.

Keep mapping-only reclasses separate from changes to total P&L.

Bridge every correction from frozen baseline to final view once.

Make the rerun / no-rerun recommendation follow the evidence, not instinct.

Example 3 — AlloyWorks Motion Systems: 90-day liquidity / captive response

Selected golden results: base unrestricted covenant cash first falls below the $2.75m lender floor on 14 Aug 2026, turns negative 18 Aug, and reaches -$15.56m by 12 Oct. Captive coverage opens at 1.12x, rises above the 1.15x minimum after the 16 Jul premium, and remains compliant thereafter if scheduled premiums are funded. The combined documented bridge still leaves about -$13.61m residual.

Why this is a strong few-shot example: it separates liquidity from solvency and firm relief from contingent relief. It also calls out that the worst tail partly reflects the finite collections-worklist horizon rather than pretending the business will literally collect zero cash.

Reviewer checklist to imitate

Use value date, cutoff and account/entity restriction before counting cash.

Correct currency unit errors before summing receipts.

Do not use captive assets if doing so breaks the captive coverage condition.

Do not call a lender draw “firm” if notice/approval/borrowing-base conditions remain.

Check whether a deferral only moves a use within the same horizon rather than truly curing the cumulative gap.

Cross-example patterns the GPT should learn

How to use these examples in the GPT

Use them as behavioral exemplars, not hard-coded answer patterns.

Imitate the evidence chain: source authority → recomputation → tie-out → bounded uncertainty → decision.

Do not import their exact numerical thresholds into unrelated tasks.

Do not assume every conflict is an anomaly; each task must be checked against its own anomaly plan.

Source basis used to build this document

RL_World_Finance_Expert_Onboarding_v6: expert role, five gates, fundamentally-sound standard, verifier quality, feedback formula, common finance traps, and stage-specific review expectations.

RL World Platform Quick Reference Cheat Sheet and Platform Overview: operational review loop, full-file review, artifact vs LLM-judge separation, and gate workflow.

Project_Omega_Guide_V5: benchmark design, headroom, source-file realism, golden requirements, verifier schema and rubric-quality rules, peer-review routing, and packaging standards.

Trainer_Review_Gate_Convergence_Report (prod data through 23 Sep 2026): latest verifier-platform rules and known non-converging QC failure modes.

Omega_Pod_Finance and Investment tracker: real peer-review decisions and feedback patterns.

Uploaded RL World task folders: completed and in-progress finance benchmark packages used for worked examples and evaluation cases.


[Table 1]

Selection rule  Only task folders that actually contain a completed Golden Solution / expert_improved output were used as “completed” few-shot examples. Current/in-progress task folders are intentionally excluded from this ground-truth set.


[Table 2]

Element | What the completed package demonstrates

Source set | Original underwriting memo, SEC request packet, monthly close/sales export, and QoE/lender-model extract.

Golden outputs | Re-underwriting workbook, regulator response memo, continue-diligence deck.

Core reasoning | Rebuild LTM EBITDA from close detail; resolve March cutoff; correct a currency-basis problem; reject unsupported add-backs; normalize duplicate debt; recompute debt, interest, liquidity, leverage and coverage.

Authority pattern | Underlying close / sales / GL-style records control the numeric rebuild; summary screen and lender model are tested, not trusted.

Decision pattern | Continue diligence only on the corrected case; preserve a broader currency-basis sensitivity rather than presenting it as the primary result.


[Table 3]

Element | What the completed package demonstrates

Source set | Raw ledger/export, treasury FX and reporting map, close-calendar guidance, preliminary overnight close packet.

Golden outputs | Q2 close review workbook and leadership readout deck.

Core reasoning | Rebuild from raw transactions; remove a duplicate; retranslate FX; apply close cutoff; apply effective-dated mapping; evaluate a signed late journal under the special bridge window.

Authority pattern | Frozen extract is the baseline, not the final truth. Close-calendar timing and the current reporting map govern inclusion and classification; the overnight packet is supporting evidence, not a substitute for rebuild.

Decision pattern | Carry a management-view adjustment and do not rerun the frozen extract because the differences are narrow, authorized and fully reconciled.


[Table 4]

Element | What the completed package demonstrates

Source set | Treasury position and scheduled uses, customer collections worklist, captive information request/funding conditions, liquidity facility/covenant update.

Golden outputs | 90-day liquidity model, regulator response memo, treasury committee briefing.

Core reasoning | Use value-dated cash; correct currency-denomination errors; fix debt amortization; protect lender cash floor and captive coverage; distinguish firm vs approval/customer-dependent relief; run fixed scenarios.

Authority pattern | Bank value date and entity/account restrictions control usability; lender/captive restrictions are applied conservatively when they conflict.

Decision pattern | Captive can remain above required coverage after opening cure, but parent liquidity remains materially short; documented bridge actions buy timing but do not eliminate the modeled residual.


[Table 5]

Pattern | Riverbend | Arcadia | AlloyWorks

Do not trust summary artifact | Original credit screen | Frozen extract / overnight packet | Promise/worklist and facility summary

Authority is fact-specific | Close + sales + debt records | Close calendar + effective map | Value date + lender/captive restrictions

Chronology matters | March cutoff | 00:07 / 00:15 / 01:00 windows | Daily value date and bank cutoff

Definition/unit drift matters | Currency basis; recurring vs add-back | FX / mapping basis | CAD vs USD; restricted vs usable cash

Decision follows rebuilt evidence | Continue only on corrected case | Carry management adjustment | Disclose residual; bridges insufficient
