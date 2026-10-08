# Finance Domain Cheat Sheet

Fast expert checks to run when recomputing material figures, or when testing whether a verifier band covers every defensible convention.

Project Omega | Finance & Insurance reviewer knowledge pack | 25 Sep 2026

## 1. Universal finance checks

- Define the measurement date, period and population before calculating anything.
- Normalize IDs and names before deduplication; economic identity beats string identity.
- Separate reported / observed values from corrected / normalized / pro forma values.
- Track units explicitly: currency, scale, gross/net, par/carrying, nominal/effective rate, pre/post tax, local/reporting currency.
- For every bridge, assign each difference once. A non-overlapping bridge should tie exactly from source presentation to corrected result.
- For every recommendation, identify the threshold or decision rule that actually governs it; do not substitute generic finance practice for task-specific rules.

## 2. Credit facilities, leveraged finance, covenants, CLOs and CECL allowances

| Review focus | Core check | Frequent trap |
| --- | --- | --- |
| Debt population | Normalize facility/instrument IDs; reconcile principal, drawn revolver, letters of credit, seller notes, leases or other included debt under the agreement. | Duplicate instrument under variant name/ID; par mixed with carrying value. |
| Covenant EBITDA | Start from the agreement definition and effective amendment. Rebuild allowed add-backs and exclusions from evidence. | Using management Adjusted EBITDA or applying amended add-backs to pre-amendment periods. |
| Leverage | Gross leverage = included debt / defined EBITDA. Net leverage subtracts only cash permitted by the agreement. | Subtracting restricted/trapped cash or using net debt when covenant is gross. |
| Coverage | Use the exact covenant definition; cash interest and fixed charges may differ from GAAP interest expense. | Using a generic formula because the certificate labels it “coverage.” |
| Availability / liquidity | Commitment less draws, reserves, borrowing-base constraints and LC usage; add only usable unrestricted cash. | Treating nominal commitment as immediately drawable capacity. |
| Authority | Executed credit agreement + amendments control terms; certificate/deck is evidence to test, not an answer key. | Accepting certified values without rebuilding definitions. |

- CLO collateral: each composite price sits inside its same-row bid–ask, the snapshot equals the determination-date mark, a defaulted obligation carries the indenture's lower-of value, and a threshold change with two conditions applies from the later condition date (CLO: the 10.0% CCC threshold from 2 September 2026).
- CECL: factor scores, forecast and reversion choices are judgments, so the answer is a range: low ≤ point ≤ high, each endpoint reconciled to its pooled, individually evaluated, other-segment and overlay components (ACL: F1 at 2 instead of 0 moved the overlay from $16,500,879.47 to about $19,365,651.04).

## 3. Commercial real estate underwriting and refinancing

| Metric / issue | Check | Reviewer warning |
| --- | --- | --- |
| NOI | Rebuild rent/revenue less permitted operating expenses; distinguish T-12, forward, stabilized and pro forma. | Broker pro forma used without reconciling lease/expense detail. |
| LTV | Loan amount / authoritative value; identify as-is, as-stabilized or appraised value date. | Mixing appraisal bases or using stale valuation. |
| Debt yield | NOI / loan amount on matching basis. | Using EBITDA or annualized partial-period NOI without support. |
| DSCR | NOI / debt service using the lender-required debt-service convention. | Interest-only vs amortizing debt service mixed. |
| Refi proceeds | Minimum of lender sizing constraints; deduct reserves/holdbacks/fees only once. | Using headline commitment rather than binding constraint. |
| Payoff / close costs | Payoff principal + accrued interest + fees + third-party/recording/escrow/reserve items less legitimate credits. | Double-counting accrued interest, deposits, security or escrows. |
| Closing timing | Sequence appraisal/credit approval/loan docs/title/payoff/wire cutoffs and named approvers. | Economics work but transaction cannot close before maturity. |

## 4. Treasury, liquidity, debt and derivative close-out

- Daily liquidity: opening usable cash by entity/account + value-dated receipts − scheduled uses ± permitted transfers/draws. A promise or remittance date is not automatically a usable-cash date.
- Classify relief as firm only if available without a new approval, customer action, waiver or condition. Approval-gated or customer-dependent relief is contingent or hopeful.
- Keep restricted cash, tax reserves, captive assets and entity-specific cash out of general liquidity unless transfer is explicitly permitted.
- For debt payoff, reconcile principal, accrued interest, breakage/fees, existing cash security, collateral interest and wire cutoffs; avoid counting a payment both in future cash flows and in the accrued balance.
- For derivatives, establish a valid notice/termination/calculation date under the governing documents; test whether quotes and market data satisfy the permitted methodology; verify compounding and day-count conventions before comparing same-labeled rates across dates.
- A routed authorization ticket is not necessarily an effective commitment. Trace prerequisite → approval → calculation → funding state.

## 5. Financial close, management P&L and consolidation

| Area | Expert check | Failure mode |
| --- | --- | --- |
| Population | Rebuild from raw transactions; identify duplicates, reversals and late postings. | Packet summary accepted instead of underlying population. |
| Cutoff | Use approved close calendar and timestamps; apply any late-item exception window exactly. | Period label outranks actual approval timestamp. |
| FX | Use rate table and method effective for entity/date; check transaction vs translation currency. | Wrong monthly rate or local amount stored in reporting-currency field. |
| Mapping | Use effective-dated entity/account/reporting map. | Legacy hierarchy label treated as current. |
| Consolidation | Confirm entity scope, eliminations, ownership and translation treatment. | Wrong entity included/excluded or elimination duplicated. |
| Bridge | Frozen/preliminary baseline → each correction → final management view, one difference once. | Packet vs final mixed into one unexplained variance. |

- Ledger roll-forwards: test every netting convention over all periods before calling a break; a break confined to one period may be the planted item (SPV: −6725 Dr broke March only, while netting accrued-payable credits, −2150 Cr, tied all seven roll-forwards; the break was the planted PEX-44).

## 6. Valuation, M&A / QoE, private markets and event studies

- Separate accounting close corrections from analytical normalizations; a valuation normalization is not automatically a journal entry.
- Normalize historical marks before trend conclusions if NAV/EBITDA/revenue definitions changed over time.
- For QoE, trace each adjustment to underlying transaction evidence; recurring operating costs do not become add-backs because a seller labels them “one-time.”
- For continuation vehicles and waterfalls, model transaction sequence, crystallization, reset basis, fees, preferred return, catch-up, carried interest, expenses and timing of realizations in the contractual order.
- Observed transaction schedules (seller proceeds, opening account, dealer statements) are terms to validate against governing provisions, not answers to copy.
- Sensitivity should illuminate a disputed assumption or reversal point; it must not replace a primary conclusion.
- Performance fees: the high-water mark is the crystallised, flow-adjusted peak from the capital-account package, not an uncrystallised monthly step-up on a trajectory sheet; test the hurdle and the HWM separately, since either can bind (LHF).
- Give-back and clawback caps are often conditional on documentation: quote the clause and test each condition (LHF Part V 5.3 allows the 35% after-tax cap "only where the GP documents taxes actually paid"; with no tax documents the give-back is the gross excess).
- IRR: before demanding a band, check whether any defensible fee convention flips the decision gate (SPV: 14.79–15.26% across conventions against a 12% gate, so any disclosed, coherent convention passes).
- Event studies: the baseline changes the statistic, so accept every defensible baseline as its own anchor and exclude only known-wrong ones (CRW D+5 move: −2.96% pre-event, −2.79% D−10, −2.65% D−5, −3.26% trough-anchored; D0, −1.34%, excluded).

## 7. Insurance underwriting, reserving, reinsurance and captives

| Subdomain | Core checks | Common definition drift / trap |
| --- | --- | --- |
| Underwriting | Exposure, policy period, attachment/limit/deductible, pricing basis, exclusions, loss history, rate change and capacity. | Written premium treated as earned; quote treated as bound policy; exposure base changes unnoticed. |
| P&C reserving / IBNR | Paid, case outstanding, incurred = paid + case, IBNR = selected ultimate − reported/incurred as defined; accident/report/calendar period; development age; gross/net. | Mixing accident year with calendar year; gross and net triangles mixed; case reserve changes treated as cash. |
| Loss ratios | Use the premium denominator matching the loss basis and period (earned vs written). | Incurred losses / written premium labeled as earned loss ratio. |
| Reinsurance | Attachment, limit, occurrence vs aggregate, reinstatement terms, hours clause, ceded recovery, counterparty and collateral. | Gross loss compared directly to net retention; reinstatement premium omitted; layer exhaust/aggregate confused. |
| Captive liquidity | Eligible liquid assets / required liabilities or coverage denominator, premium funding, related-party receivables, restricted assets. | Captive assets used as parent liquidity despite coverage restriction. |
| Claims operations | Claim status, authority, payment timing, reserve vs paid, recoverable evidence. | Pending/review item estimated as finalized payment. |

- Reinsurance recoverables: test the hours-clause event loss against the attachment before booking a recoverable (REI booked USD 90,475,015 on EMBER-WEST-2026 × CAT-26-A3 with an hours-clause loss of 1,033,600,000 below a USD 1.25bn attachment). A trust asset the eligibility table does not map is escalated, never haircut into eligibility (REI policy Table 9).
- Concentration percentages move with the weighting basis (unweighted, limit-weighted, exposure-weighted); accept the basis the submission states (REI: the 55.5–56.5% top-four band came from an unweighted average, while limit-weighting gives exactly 55.0000%).
- Captive collateral: apply per-claim layer limits claim by claim before aggregating (HAL: 11 open legacy claims carried $8.85M of case above the $1M layer, the difference between posting $8.0M and posting nothing), and test each date gate, such as a 90-day window, against the document's own date (HIL-AR-2026Q2, dated 2026-08-12 after the 2026-07-20 window end, flips the governing reserve).

## 8. Wealth and personal financial planning

- Separate spendable household cash from qualified retirement assets, restricted accounts, earmarked reserves and pending transfers.
- Account ownership, registration, tax character and destination evidence matter; similar labels do not make assets interchangeable.
- An expected rollover, payroll enrollment, insurance action or 529 funding is not confirmed until the supporting event or approval exists.
- Funding waterfalls preserve the client-approved priority order and protect operating, tax and emergency reserves before discretionary goals.
- Manual close entries require the approval evidence specified by the office control policy; “reviewed” is not necessarily “authorized.”

## 9. Sanity checks that catch polished mistakes

- Does a ratio move in the direction implied by the numerator and denominator changes?
- Does a “better” liquidity outcome merely move a payment beyond the displayed horizon?
- Does a cash-flow bridge double count collateral, accrued interest, prior distributions, or a receipt already included in opening cash?
- Does a trend break exactly when an amendment, mapping or definition changes?
- Does a suspicious number equal another nearby field (e.g., a client count mistaken for dollars)?
- Can every headline figure be traced to a source or a visible derivation?

## Source basis

The untagged checks come from the RL World Finance Expert Onboarding (v6), the RL World Platform Quick Reference and Platform Overview, the Project Omega Guide (V5), the Trainer Review Gate Convergence Report (production data through 23 Sep 2026), the Omega Pod finance and investment tracker and the uploaded RL World task folders. Traps tagged LHF, SPV, HAL, CLO, ACL, CRW or REI come from the review sessions recorded in `07_failure_patterns_and_lessons.md`.
