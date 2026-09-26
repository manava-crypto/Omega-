Authority Hierarchy & Defect Taxonomy

Where truth comes from, where defects belong, and how to route them

Project Omega | Finance & Insurance reviewer knowledge pack | 25 Sep 2026

1. Authority hierarchy: use a fact-specific hierarchy, not a blanket document ranking

The authoritative source depends on the fact being tested. The same file can be authoritative for one field and non-authoritative for another. Start with explicit prompt rules, then choose the source that has legal, accounting, operational or temporal authority for the specific fact.

2. Chronology and effective-date rules

A definition, rate, mapping, covenant level or policy applies only within its effective window.

A post-period document may explain a prior event, but it does not retroactively change the prior rule unless it explicitly amends or corrects it.

Promise date ≠ cash value date. Trade date ≠ settlement date. Routed request ≠ approved commitment. Draft ≠ executed agreement.

When a late item is allowed under a special bridge window, verify the actual approval timestamp and the authority required for that exception.

If two records use identical labels across dates, test whether unit, compounding, denominator, population or definition changed before comparing them.

3. Defect taxonomy by ownership layer

4. Planned anomaly vs unintended defect

5. Routing decision tree

Is the concern real when independently checked? If no, disagree with the judge and document the evidence.

If real, what is the earliest artifact that caused it? Assign ownership there.

Does fixing it require changing task design, source data, prompt or golden? Treat it as foundational, not a verifier-only edit.

If only the scoring logic is defective, keep the underlying task/golden intact and repair or regenerate the verifier.

If the form/runtime cannot express the correct check, escalate rather than forcing an invalid workaround.

6. Quick examples from the supplied project material

Source basis used to build this document

RL_World_Finance_Expert_Onboarding_v6: expert role, five gates, fundamentally-sound standard, verifier quality, feedback formula, common finance traps, and stage-specific review expectations.

RL World Platform Quick Reference Cheat Sheet and Platform Overview: operational review loop, full-file review, artifact vs LLM-judge separation, and gate workflow.

Project_Omega_Guide_V5: benchmark design, headroom, source-file realism, golden requirements, verifier schema and rubric-quality rules, peer-review routing, and packaging standards.

Trainer_Review_Gate_Convergence_Report (prod data through 23 Sep 2026): latest verifier-platform rules and known non-converging QC failure modes.

Omega_Pod_Finance and Investment tracker: real peer-review decisions and feedback patterns.

Uploaded RL World task folders: completed and in-progress finance benchmark packages used for worked examples and evaluation cases.

V2 Addendum — Checklist / Platform Conflict Taxonomy

Precedence rule adopted for the reviewer GPT

1. Current task-specific instructions and current platform schema/runtime constraints.

2. Latest confirmed platform/verifier guidance and convergence fixes.

3. Stable Project Omega creation/review standards and pre-flight checklist.

4. Older FAQ wording or automated judge remediation when it conflicts with the above.


[Table 1]

Fact type | Usually strongest evidence | Usually weaker evidence | Reviewer test

Legal / contractual term | Executed agreement, amendment, signed election, formal policy | Summary memo, deck, email | Was it executed and effective for the relevant date / entity?

Actual cash / transaction | Bank value record, custodial record, GL/subledger, final transaction export | Promise log, forecast, presentation | Did cash/value actually occur, in the right entity/account, on the right date?

Approval / status | Signed approval, final workflow state, authoritative system log | Routed request, draft, “expected”, email intent | Does the evidence prove final authorization or only review/routing?

Accounting classification | Governing accounting policy + transaction evidence + effective chart/map | Management narrative or presentation label | Does classification reflect economic substance and current mapping?

Valuation / market input | Permitted market data under governing method and date | Dealer/internal quote not meeting method | Is the date/basis permitted, and are conventions equivalent?

Covenant / credit metric | Executed credit agreement + amendments + underlying financials | Compliance certificate / lender deck summary | Rebuild under the agreement definition; do not accept the certificate by default.

Timeline / close cutoff | Approved close calendar, effective-dated policy, timestamped approval trail | Period label or preliminary packet | Which timestamp / rule actually determines inclusion?


[Table 2]

Code | Layer | Defect | Definition | Owner | Typical severity

TD-01 | Task Design | Unrealistic workflow | Scenario is contrived, role/scope impossible, or timing unrealistic. | Task Design | Critical/Major

TD-02 | Task Design | Insufficient headroom | Generic model can solve without meaningful domain judgment. | Task Design | Major

SD-01 | Source Data | Chronology / cutoff error | Event, rate, approval or balance used outside valid time window. | Source file containing wrong record | Critical/Major

SD-02 | Source Data | Cross-file mismatch | Same fact conflicts across records without a planned reason. | Earliest incorrect source | Critical/Major

SD-03 | Source Data | Definition drift | Metric basis changes mid-series but appears continuous. | Source / metadata defining series | Major

SD-04 | Source Data | Authority inversion | Summary/draft overrides executed or system-of-record evidence. | Source / task rules | Critical/Major

SD-05 | Source Data | Duplicate economic event | Same event appears under variant IDs/names and is counted twice. | Source data | Major

SD-06 | Source Data | Unit / currency / scale mismatch | Native currency, notional, thousands, gross/net or par/carrying basis mixed. | Source data | Critical/Major

SD-07 | Source Data | Mechanical data error | Broken total, running balance, invalid date, missing key, impossible negative, stale formula cache. | Source data | Major

SD-08 | Source Data | Answer leakage | Source explicitly states supported answer / exception the solver should derive. | Source data | Major

SD-09 | Source Data | Anomaly telegraphed | Planted anomaly is labeled or overly obvious. | Source data | Major

P-01 | Prompt | Underdetermined ask | Two experts could reach materially different outputs because authority/definition/decision rule is missing. | Prompt | Critical/Major

P-02 | Prompt | Contract conflict | Narrative ask conflicts with strict output contract, filename, state or decision options. | Prompt | Major

P-03 | Prompt | Scope inflation / overconstraint | Prompt forces method or unnecessary detail that removes headroom. | Prompt | Major/Minor

MO-01 | Model/Golden | Computation error | Formula/arithmetic/roll-forward/bridge/waterfall is wrong. | Output artifact | Critical/Major

MO-02 | Model/Golden | Correct number, wrong basis | Output lands on plausible figure using invalid definition/date/authority. | Output artifact | Critical/Major

MO-03 | Model/Golden | Unsupported conclusion | Claim or recommendation exceeds evidence. | Output artifact | Major

MO-04 | Model/Golden | Cross-deliverable inconsistency | Workbook, memo, deck or reasoning disagree on a material fact/action. | All affected outputs | Major

MO-05 | Model/Golden | Omission | Required analysis, risk, action, source link or deliverable component is missing. | Output artifact | Major/Minor

V-01 | Verifier | Rubric overreach | Verifier imposes a requirement absent from prompt/source/valid professional obligation. | Verifier | Major

V-02 | Verifier | Composite criterion | Independent concepts bundled so partial correctness cannot be scored fairly. | Verifier | Major/Minor

V-03 | Verifier | Overlap / ownership collision | Same property materially graded by multiple verifiers. | Verifier set | Major

V-04 | Verifier | Vague threshold | Undefined “material/reasonable/appropriate” drives pass/fail. | Verifier | Major/Minor

V-05 | Verifier | Not self-contained | Judge lacks required values/entities/accepted alternatives. | Verifier | Major

V-06 | Verifier | Runtime impossible | Check needs cross-file access, formula liveness or extraction behavior runtime cannot see. | Verifier / escalation | Major

V-07 | Verifier | False leakage concern | Inline anchors treated as leakage even though solver never sees rubric. | Judge feedback | Reject remediation

V-08 | Verifier | Truncation policy error | Rubric fails solely on extraction/token truncation. | Judge feedback / verifier | Reject remediation

PL-01 | Pipeline | Tool/QC limitation | Issue comes from conversion, extraction, stale cached view, or impossible QC requirement. | Escalation | Not task defect


[Table 3]

Question | Planned anomaly | Unintended defect

Is it in the anomaly plan? | Matches description, location and expected detection pattern. | Not described, or materially different from plan.

Does it preserve solvability? | Yes; enough evidence exists to detect and resolve it. | No; required evidence is missing or mutually impossible.

Is it labeled? | No. | May be accidentally signposted or directly answered.

Where to flag? | Do not flag merely because sources conflict; judge whether the intended anomaly is realistic and fair. | Flag the defective source / task design at the earliest layer.


[Table 4]

Pattern | Classification | Correct owner

Annual-rent formulas have no cached values, so extracted source looks blank. | SD-07 Mechanical data / extraction interaction | Source workbook; recalc/save cached values.

Reasoning says $27.583m / $20.662m = 1.37x when arithmetic is 1.335x. | MO-01 Golden computation support error | Reasoning document.

Source workbook contains “Supported Balance” and “Unsupported Difference Flag” that reveal the answer. | SD-08 Answer leakage | Source workbook.

Verifier asks one judge to compare workbook and memo directly, but one-source-per-verifier runtime cannot. | V-06 Runtime impossible | Verifier / escalation, not golden.

QC calls inlined expected values “answer-key leakage.” | V-07 False leakage concern | Reject remediation; solver does not see rubric.

Compliance certificate conflicts with financial statements by design and prompt instructs a rebuild from agreement definitions. | Planned anomaly / authority test | Do not reject merely for the conflict; verify it is solvable and unlabeled.


[Table 5]

Code | Pattern | Classification / action

CF-01 | Legacy verifier-count minimum vs newer no-count platform rule | Platform-policy conflict. Do not reject solely for count; require coverage/quality unless current governing spec explicitly sets a minimum.

CF-02 | Extractor reports truncated=true | Pipeline/extraction issue. Do not make it a verifier fail by itself; escalate/override only after substantive content checks are clean.

CF-03 | Verifier reads a fixed/incomplete business-data range and misses records | Real verifier/construct-validity defect. Fix the population/range logic; this is not the same as CF-02.

CF-04 | Cross-artifact equality demanded by a single-file verifier | Runtime-impossible verifier defect. Inline accepted shared anchors separately in each artifact’s owner.

CF-05 | Exact source population must be matched | Valid semantic rubric requirement when grounded. Express it in rubric PASS/FAIL text; do not invent unsupported deterministic assertion types.

CF-06 | PowerPoint spatial relationship inferred from extraction order | Potential construct-validity/runtime defect. Use reliable slide labels/observable structure or do not grade adjacency.

CF-07 | Source cross-reference to another document | Not automatically leakage. Reject only when it gives solver analytical directions/decomposition or reveals the answer; ordinary in-world references may be realistic.

CF-08 | Automated judge repeats old counts/old wording after regeneration | Stale QC result. Confirm current text, then document/override rather than rewriting already-fixed criteria.


[Table 6]

CAUTION  This precedence rule is a deliberate reconciliation for the GPT. If the live platform displays a newer explicit rule, the live rule wins and the discrepancy should be logged.
