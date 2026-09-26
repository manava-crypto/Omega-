Finance Domain Cheat Sheet

Fast expert checks for the first Project Omega finance / insurance domains

Project Omega | Finance & Insurance reviewer knowledge pack | 25 Sep 2026

1. Universal finance checks

Define the measurement date, period and population before calculating anything.

Normalize IDs and names before deduplication; economic identity beats string identity.

Separate reported / observed values from corrected / normalized / pro forma values.

Track units explicitly: currency, scale, gross/net, par/carrying, nominal/effective rate, pre/post tax, local/reporting currency.

For every bridge, assign each difference once. A non-overlapping bridge should tie exactly from source presentation to corrected result.

For every recommendation, identify the threshold or decision rule that actually governs it; do not substitute generic finance practice for task-specific rules.

2. Credit facilities, leveraged finance and covenant analysis

3. Commercial real estate underwriting and refinancing

4. Treasury, liquidity, debt and derivative close-out

Daily liquidity: opening usable cash by entity/account + value-dated receipts - scheduled uses ± permitted transfers/draws. Promise or remittance date is not automatically a usable-cash date.

Classify relief as firm only if available without a new approval, customer action, waiver or condition. Approval-gated / customer-dependent relief is contingent or hopeful.

Keep restricted cash, tax reserves, captive assets and entity-specific cash out of general liquidity unless transfer is explicitly permitted.

For debt payoff: reconcile principal, accrued interest, breakage/fees, existing cash security, collateral interest, and wire cutoffs; avoid counting a payment both in future cash flows and accrued balance.

For derivatives: establish valid notice/termination/calculation date under governing documents; test whether quotes/market data satisfy permitted methodology; verify compounding/day-count conventions before comparing same-labeled rates across dates.

A routed authorization ticket is not necessarily an effective commitment. Trace prerequisite → approval → calculation → funding state.

5. Financial close, management P&L and consolidation

6. Valuation, M&A / QoE and private markets

Separate accounting close corrections from analytical normalizations; a valuation normalization is not automatically a journal entry.

Normalize historical marks before trend conclusions if NAV/EBITDA/revenue definitions changed over time.

For QoE, trace each adjustment to underlying transaction evidence; recurring operating costs do not become add-backs because a seller labels them “one-time.”

For continuation vehicles / waterfalls, model transaction sequence, crystallization, reset basis, fees, preferred return, catch-up, carried interest, expenses and timing of realizations in the contractual order.

Observed transaction schedules (seller proceeds, opening account, dealer statements) are terms to validate against governing provisions—not answers to copy.

Sensitivity should illuminate a disputed assumption or reversal point; it must not replace a primary conclusion.

7. Insurance underwriting, reserving and reinsurance

8. Wealth / personal financial planning

Separate spendable household cash from qualified retirement assets, restricted accounts, earmarked reserves and pending transfers.

Account ownership, registration, tax character and destination evidence matter; similar labels do not make assets interchangeable.

Expected rollover, payroll enrollment, insurance action or 529 funding is not confirmed until the supporting event/approval exists.

Funding waterfalls preserve the client-approved priority order and protect operating/tax/emergency reserves before discretionary goals.

Manual close entries require the approval evidence specified by the office control policy; “reviewed” is not necessarily “authorized.”

9. Sanity checks that catch polished mistakes

Does a ratio move in the direction implied by numerator/denominator changes?

Does a “better” liquidity outcome merely move a payment beyond the displayed horizon?

Does a cash-flow bridge double count collateral, accrued interest, prior distributions, or a receipt already included in opening cash?

Does a trend break exactly when an amendment, mapping or definition changes?

Does a suspicious number equal another nearby field (e.g., a client count mistaken for dollars)?

Can every headline figure be traced to a source or a visible derivation?

Source basis used to build this document

RL_World_Finance_Expert_Onboarding_v6: expert role, five gates, fundamentally-sound standard, verifier quality, feedback formula, common finance traps, and stage-specific review expectations.

RL World Platform Quick Reference Cheat Sheet and Platform Overview: operational review loop, full-file review, artifact vs LLM-judge separation, and gate workflow.

Project_Omega_Guide_V5: benchmark design, headroom, source-file realism, golden requirements, verifier schema and rubric-quality rules, peer-review routing, and packaging standards.

Trainer_Review_Gate_Convergence_Report (prod data through 23 Sep 2026): latest verifier-platform rules and known non-converging QC failure modes.

Omega_Pod_Finance and Investment tracker: real peer-review decisions and feedback patterns.

Uploaded RL World task folders: completed and in-progress finance benchmark packages used for worked examples and evaluation cases.


[Table 1]

Review focus | Core check | Frequent trap

Debt population | Normalize facility/instrument IDs; reconcile principal, drawn revolver, letters of credit, seller notes, leases or other included debt under the agreement. | Duplicate instrument under variant name/ID; par mixed with carrying value.

Covenant EBITDA | Start from the agreement definition and effective amendment. Rebuild allowed add-backs and exclusions from evidence. | Using management Adjusted EBITDA or applying amended add-backs to pre-amendment periods.

Leverage | Gross leverage = included debt / defined EBITDA. Net leverage subtracts only cash permitted by the agreement. | Subtracting restricted/trapped cash or using net debt when covenant is gross.

Coverage | Use the exact covenant definition; cash interest and fixed charges may differ from GAAP interest expense. | Using a generic formula because the certificate labels it “coverage.”

Availability / liquidity | Commitment less draws, reserves, borrowing-base constraints and LC usage; add only usable unrestricted cash. | Treating nominal commitment as immediately drawable capacity.

Authority | Executed credit agreement + amendments control terms; certificate/deck is evidence to test, not an answer key. | Accepting certified values without rebuilding definitions.


[Table 2]

Metric / issue | Check | Reviewer warning

NOI | Rebuild rent/revenue less permitted operating expenses; distinguish T-12, forward, stabilized and pro forma. | Broker pro forma used without reconciling lease/expense detail.

LTV | Loan amount / authoritative value; identify as-is, as-stabilized or appraised value date. | Mixing appraisal bases or using stale valuation.

Debt yield | NOI / loan amount on matching basis. | Using EBITDA or annualized partial-period NOI without support.

DSCR | NOI / debt service using the lender-required debt-service convention. | Interest-only vs amortizing debt service mixed.

Refi proceeds | Minimum of lender sizing constraints; deduct reserves/holdbacks/fees only once. | Using headline commitment rather than binding constraint.

Payoff / close costs | Payoff principal + accrued interest + fees + third-party/recording/escrow/reserve items less legitimate credits. | Double-counting accrued interest, deposits, security or escrows.

Closing timing | Sequence appraisal/credit approval/loan docs/title/payoff/wire cutoffs and named approvers. | Economics work but transaction cannot close before maturity.


[Table 3]

Area | Expert check | Failure mode

Population | Rebuild from raw transactions; identify duplicates, reversals and late postings. | Packet summary accepted instead of underlying population.

Cutoff | Use approved close calendar and timestamps; apply any late-item exception window exactly. | Period label outranks actual approval timestamp.

FX | Use rate table and method effective for entity/date; check transaction vs translation currency. | Wrong monthly rate or local amount stored in reporting-currency field.

Mapping | Use effective-dated entity/account/reporting map. | Legacy hierarchy label treated as current.

Consolidation | Confirm entity scope, eliminations, ownership and translation treatment. | Wrong entity included/excluded or elimination duplicated.

Bridge | Frozen/preliminary baseline → each correction → final management view, one difference once. | Packet vs final mixed into one unexplained variance.


[Table 4]

Subdomain | Core checks | Common definition drift / trap

Underwriting | Exposure, policy period, attachment/limit/deductible, pricing basis, exclusions, loss history, rate change and capacity. | Written premium treated as earned; quote treated as bound policy; exposure base changes unnoticed.

P&C reserving / IBNR | Paid, case outstanding, incurred = paid + case, IBNR = selected ultimate - reported/incurred as defined; accident/report/calendar period; development age; gross/net. | Mixing accident year with calendar year; gross and net triangles mixed; case reserve changes treated as cash.

Loss ratios | Use the premium denominator matching the loss basis and period (earned vs written). | Incurred losses / written premium labeled as earned loss ratio.

Reinsurance | Attachment, limit, occurrence vs aggregate, reinstatement terms, hours clause, ceded recovery, counterparty and collateral. | Gross loss compared directly to net retention; reinstatement premium omitted; layer exhaust/aggregate confused.

Captive liquidity | Eligible liquid assets / required liabilities or coverage denominator, premium funding, related-party receivables, restricted assets. | Captive assets used as parent liquidity despite coverage restriction.

Claims operations | Claim status, authority, payment timing, reserve vs paid, recoverable evidence. | Pending/review item estimated as finalized payment.
