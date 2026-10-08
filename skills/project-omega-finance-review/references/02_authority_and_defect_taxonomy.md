# Authority Hierarchy and Defect Taxonomy

Where truth comes from, where defects belong, and how to route them.

## 1. Authority is fact-specific

The authoritative source depends on the fact being tested, not on a blanket ranking of documents. The same file can be authoritative for one field and non-authoritative for another. Start with explicit prompt rules, then choose the source that has legal, accounting, operational or temporal authority for the specific fact.

| Fact type | Usually strongest evidence | Usually weaker evidence | Reviewer test |
| --- | --- | --- | --- |
| Legal / contractual term | Executed agreement, amendment, signed election, formal policy | Summary memo, deck, email | Was it executed and effective for the relevant date / entity? |
| Actual cash / transaction | Bank value record, custodial record, GL/subledger, final transaction export | Promise log, forecast, presentation | Did cash/value actually occur, in the right entity/account, on the right date? |
| Approval / status | Signed approval, final workflow state, authoritative system log | Routed request, draft, “expected”, email intent | Does the evidence prove final authorization or only review/routing? |
| Accounting classification | Governing accounting policy + transaction evidence + effective chart/map | Management narrative or presentation label | Does classification reflect economic substance and current mapping? |
| Valuation / market input | Permitted market data under governing method and date | Dealer/internal quote not meeting method | Is the date/basis permitted, and are conventions equivalent? |
| Covenant / credit metric | Executed credit agreement + amendments + underlying financials | Compliance certificate / lender deck summary | Rebuild under the agreement definition; do not accept the certificate by default. |
| Timeline / close cutoff | Approved close calendar, effective-dated policy, timestamped approval trail | Period label or preliminary packet | Which timestamp / rule actually determines inclusion? |

## 2. Chronology and effective dates

- A definition, rate, mapping, covenant level or policy applies only within its effective window.
- A post-period document may explain a prior event, but it does not retroactively change the prior rule unless it explicitly amends or corrects it.
- Promise date ≠ cash value date. Trade date ≠ settlement date. Routed request ≠ approved commitment. Draft ≠ executed agreement.
- When a late item is allowed under a special bridge window, verify the actual approval timestamp and the authority required for that exception.
- If two records use identical labels across dates, test whether unit, compounding, denominator, population or definition changed before comparing them.
- On the first review, build a dated timeline: each document may cite only earlier events, and every contractual date gate is tested against the document dates, because a report dated outside its window can flip the governing figure (HAL).

## 3. Defect taxonomy by ownership layer

| Code | Layer | Defect | Definition | Owner | Typical severity |
| --- | --- | --- | --- | --- | --- |
| TD-01 | Task Design | Unrealistic workflow | Scenario is contrived, role/scope impossible, or timing unrealistic. | Task Design | Critical/Major |
| TD-02 | Task Design | Insufficient headroom | Generic model can solve without meaningful domain judgment. | Task Design | Major |
| SD-01 | Source Data | Chronology / cutoff error | Event, rate, approval or balance used outside valid time window. | Source file containing wrong record | Critical/Major |
| SD-02 | Source Data | Cross-file mismatch | Same fact conflicts across records without a planned reason. | Earliest incorrect source | Critical/Major |
| SD-03 | Source Data | Definition drift | Metric basis changes mid-series but appears continuous. | Source / metadata defining series | Major |
| SD-04 | Source Data | Authority inversion | Summary/draft overrides executed or system-of-record evidence. | Source / task rules | Critical/Major |
| SD-05 | Source Data | Duplicate economic event | Same event appears under variant IDs/names and is counted twice. | Source data | Major |
| SD-06 | Source Data | Unit / currency / scale mismatch | Native currency, notional, thousands, gross/net or par/carrying basis mixed. | Source data | Critical/Major |
| SD-07 | Source Data | Mechanical data error | Broken total, running balance, invalid date, missing key, impossible negative, stale formula cache. | Source data | Major |
| SD-08 | Source Data | Answer leakage | Source explicitly states supported answer / exception the solver should derive. | Source data | Major |
| SD-09 | Source Data | Anomaly telegraphed | Planted anomaly is labeled or overly obvious. | Source data | Major |
| P-01 | Prompt | Underdetermined ask | Two experts could reach materially different outputs because authority/definition/decision rule is missing. | Prompt | Critical/Major |
| P-02 | Prompt | Contract conflict | Narrative ask conflicts with strict output contract, filename, state or decision options. | Prompt | Major |
| P-03 | Prompt | Scope inflation / overconstraint | Prompt forces method or unnecessary detail that removes headroom. | Prompt | Major/Minor |
| MO-01 | Model/Golden | Computation error | Formula/arithmetic/roll-forward/bridge/waterfall is wrong. | Output artifact | Critical/Major |
| MO-02 | Model/Golden | Correct number, wrong basis | Output lands on plausible figure using invalid definition/date/authority. | Output artifact | Critical/Major |
| MO-03 | Model/Golden | Unsupported conclusion | Claim or recommendation exceeds evidence. | Output artifact | Major |
| MO-04 | Model/Golden | Cross-deliverable inconsistency | Workbook, memo, deck or reasoning disagree on a material fact/action. | All affected outputs | Major |
| MO-05 | Model/Golden | Omission | Required analysis, risk, action, source link or deliverable component is missing. | Output artifact | Major/Minor |
| V-01 | Verifier | Rubric overreach | Verifier imposes a requirement absent from prompt/source/valid professional obligation. | Verifier | Major |
| V-02 | Verifier | Composite criterion | Independent concepts bundled so partial correctness cannot be scored fairly. | Verifier | Major/Minor |
| V-03 | Verifier | Overlap / ownership collision | Same property materially graded by multiple verifiers. | Verifier set | Major |
| V-04 | Verifier | Vague threshold | Undefined “material/reasonable/appropriate” drives pass/fail. | Verifier | Major/Minor |
| V-05 | Verifier | Not self-contained | Judge lacks required values/entities/accepted alternatives. | Verifier | Major |
| V-06 | Verifier | Runtime impossible | Check needs cross-file access, formula liveness or extraction behavior runtime cannot see. | Verifier / escalation | Major |
| V-07 | Verifier | False leakage concern | Inline anchors treated as leakage even though solver never sees rubric. | Judge feedback | Reject remediation |
| V-08 | Verifier | Truncation policy error | Rubric fails solely on extraction/token truncation. | Judge feedback / verifier | Reject remediation |
| PL-01 | Pipeline | Tool/QC limitation | Issue comes from conversion, extraction, stale cached view, or impossible QC requirement. | Escalation | Not task defect |

### Verifier codes from review evidence

The owner is the verifier concerned; severity follows the action.

| Code | Defect | Definition | Action |
| --- | --- | --- | --- |
| V-09 | Embedded anchor or fact wrong | A figure, illustration, preamble fact, "roughly" figure, cross-reference or weight in rubric text is wrong or stale. | Recompute every figure and phrase, grep all rubrics for the old one after any source, band or name change, and label illustrations "for illustration only, not a pass band". Blocks at Trainer Review if it can flip a verdict, mislead the judge or is being copied into new verifiers; optional at Final Review unless it changes a pass/fail outcome. |
| V-10 | Proxy test | A non-compliant output, or the minimal fake (labels, owner, deadline, no case facts), can meet the stated test. | Test the construct itself (a cell reference or identical stored value, not cent equality; a stated evidential basis, not "higher"), and bind the rubric to a source value or case ID when the fake passes. |
| V-11 | Governing term paraphrased without its condition | A cap, threshold, eligibility rule, exception, ranking or effective window is restated without a condition the source attaches. | Quote the clause with every condition, mark each condition met or unmet in the records, and match capitalised names and section numbers literally; this blocks even at Final Review. |
| V-12 | Subset bar against each/every | An N-of-M or "at least" threshold where the instruction says each, every or all, or where a skippable item is the sole owner of an obligation. | Require the full population enumerated from source; keep N-of-M only where no skippable item solely owns an obligation. |
| V-13 | FAIL clause punishing thoroughness | "FAIL if a different X is named" while more than one source row meets the same general test, so a correct, more thorough answer fails. | Count every qualifying source row; if there is more than one, rewrite the clause as "FAIL if <planted item> is not identified". |
| V-14 | Headline number with no magnitude band | A headline figure has no floor and ceiling, or rests on "about", "roughly" or "display rounding", so an absurd value passes. | Add an outer band computed across every defensible reading, replace vague qualifiers with explicit tolerances, grade components against their stated total, and confirm an absurd value (zero, ten times the golden) fails. |
| V-15 | Importance weight inconsistent with the share of the task | The core/secondary label does not match the share of the task the verifier carries. | Core for planned anomalies and headline figures, secondary for presentation and supporting items; fix by relabelling, never by deleting or folding verifiers; a relabel instruction at Trainer Review, an optional note at Final Review. |
| V-16 | Obligation graded only in an artifact the contract does not name | The strict output contract places an obligation or declared anomaly on one artifact, but only a verifier on another artifact grades it. | Give the obligation, and each declared anomaly, its own mandatory grading home on the artifact the contract names, never a sub-condition of a composite. |

### Judge-handling codes

| Code | Defect | Definition | Action |
| --- | --- | --- | --- |
| JD-01 | Pack-level text replicated per file | One judge verdict and explanation are stamped on every file while the evidence sits in one, or a "cross-file" finding is intra-file. | Answer each file on its own evidence; where the finding lives elsewhere, DISAGREE with "Fix: No change required to this file for this check; the fix belongs in <file>."; cross-file means between files. |
| JD-02 | Judge miscount or partial read | The judge's counts do not match the files, it declares a cut-off or partial read, or it claims work (a fake submission, an every-pair check) that did not happen. | Recount what it counts and spot-check every "every" claim, treat a partial read as existential evidence only, and re-run the check yourself over the full set whatever the verdict. |
| JD-03 | Conflicting remediation across checks | Two checks demand incompatible changes, such as a robustness check asking for file-exists checks against the rubric-first policy. | TAKE one, REJECT the other by name, and escalate in one line. |
| JD-04 | Recurring demand already rejected with an instruction citation | A judge repeats a demand previously rejected on a quoted instruction or source basis. | Log it and answer each repeat with the same short DISAGREE and the instruction quote; after a second flag on the same point, re-derive from source before holding the line. |

## 4. Planned anomaly or unintended defect

Run the first test before calling any source condition a defect; a yes makes it planned difficulty, and only the labelling test still applies.

| Question | Planned anomaly | Unintended defect |
| --- | --- | --- |
| Do the sources' own cover or notes sheets, or the prompt's caveats, explain the condition, and do the golden and models resolve it through the stated authority order? Test every plausible convention across all periods and ask whether a graded figure moves. | Yes: planned difficulty, an optional note at most. A break confined to the planted anomaly's row or period is the anomaly working. | Not explained, or it moves a graded figure the authority order does not resolve: apply the remaining tests. |
| Is it in the anomaly plan? | Matches description, location and expected detection pattern. | Not described, or materially different from plan. |
| Does it preserve solvability? | Yes; enough evidence exists to detect and resolve it. | No; required evidence is missing or mutually impossible. |
| Is it labeled? | No; finding it needs the intended join or test. A disclosed fact the solver must still apply, an observed term to validate, or one-step arithmetic on a disclosed line where the graded skill remains is not leakage. | Text names the planted mechanism or reuses the anomaly plan's wording, or one sort, filter or round-number fingerprint isolates the rows (SD-09); a worker could copy a core verifier's graded conclusion from the source (SD-08). REJECT that source and DISAGREE with its leakage PASS: delete the conclusory text or pre-solved cells and keep the raw dated evidence. |
| Where to flag? | Do not flag merely because sources conflict; judge whether the intended anomaly is realistic and fair. | Flag the defective source / task design at the earliest layer. |

Anomaly-plan completeness is never tested against verifier scope. Task Design is judged on its own terms, since it is written before the prompt, sources and verifiers; a verifier grading a condition the plan never mentions is a Verifier-layer question (V-01 where the condition has no prompt or source basis). A difficulty or effort-label mismatch is a metadata note, and a prompt that prescribes a treatment the plan expected the solver to detect is a Prompt-layer note; neither is a Task Design defect.

## 5. Routing decision tree

1. Is the concern real when independently checked (for a source condition, after the section 4 tests)? If no, DISAGREE with the judge and document the evidence.
2. If real, what is the earliest artifact that caused it? Assign ownership there.
3. Does fixing it require changing task design, source data, prompt or golden? Treat it as foundational, not a verifier-only edit. Never weaken a verifier, or add an escape clause, to cover an upstream defect.
4. A source defect is a blocking note, never only an escalation. If the source would not be fixed this cycle, still file it as a blocking Source Data note on the file that carries it, because a regenerator acts on notes and escalations need a human. Align the prompt or verifier to source text that exists; never point a prompt at a clause not yet written.
5. If only the scoring logic is defective, keep the underlying task and golden intact and repair or regenerate the verifier.
6. If the form or runtime cannot express the correct check, escalate rather than forcing an invalid workaround.

## 6. Worked classifications

Task keys in parentheses are those used in `07_failure_patterns_and_lessons.md`.

| Pattern | Classification | Correct owner |
| --- | --- | --- |
| Annual-rent formulas have no cached values, so extracted source looks blank. | SD-07 Mechanical data / extraction interaction | Source workbook; recalc/save cached values (an optional note at Final Review). |
| Reasoning says $27.583m / $20.662m = 1.37x when arithmetic is 1.335x. | MO-01 Golden computation support error | Reasoning document. |
| Source workbook contains “Supported Balance” and “Unsupported Difference Flag” that reveal the answer. | SD-08 Answer leakage | Source workbook. |
| Verifier asks one judge to compare workbook and memo directly, but one-source-per-verifier runtime cannot. | V-06 Runtime impossible | Verifier / escalation, not golden. |
| QC calls inlined expected values “answer-key leakage.” | V-07 False leakage concern | Reject remediation; solver does not see rubric. |
| Compliance certificate conflicts with financial statements by design and prompt instructs a rebuild from agreement definitions. | Planned anomaly / authority test | Do not reject merely for the conflict; verify it is solvable and unlabeled. |
| The HWM Trajectory note says it is "retained for chronology; class capital-account detail and allocation components remain in the companion capital-account package", and the golden and both models rebuild from that package (LHF). | Planned difficulty | No defect; Source Documents APPROVE, optional note at most. |
| A rubric applies "the 35% after-tax cap only if gross excess is positive", but Governing Documents Part V 5.3 allows the cap "only where the GP documents taxes actually paid", and the records hold none (LHF). | V-11 Governing term paraphrased | workbook_ltd_giveback_rollforward and memo_giveback_conclusion. |
| "FAIL … if a different lot is named as the stale-taxonomy exception" while 18 Legacy Positions rows are expired (CRW). | V-13 FAIL clause punishing thoroughness | Verifier; FAIL only "if BL-6D3A9E is not identified among the stale-taxonomy exceptions". |
| "At least four of these five" exceptions against an instruction covering "each data-conversion exception found" (ACL). | V-12 Subset bar against each/every | Verifier; require each exception, enumerated from source. |
| An economic-value shortfall rubric requires only that value sit below booked, the parts sum and the base match, so an economic value of 400,000,000 passes (REI). | V-14 No magnitude band | Verifier; add a floor and ceiling computed across the defensible readings. |
| Realism and cross-file FAILs carry byte-identical text on all four files, but the evidence sits only in Larkspur_Collateral_Surveillance_2026-09-18.xlsx (CLO). | JD-01 Replicated pack-level text | REJECT the surveillance workbook; DISAGREE on the other three files. |
| EMBER-WEST-2026 × CAT-26-A3 carries USD 90,475,015 booked below a USD 1.25bn attachment (hours-clause loss 1,033,600,000); it was escalated twice and contained with a verifier escape clause that later cascaded into verifier FAILs (REI). | Source defect left as an escalation | Blocking Source Data note on the carrying file; no verifier escape clause. |

## 7. Guidance conflicts and platform-policy codes

On conflicting guidance, task and platform instructions win, then Omega standards, runtime limits, examples; flag what stays unresolved. Platform instructions include the latest confirmed verifier guidance and convergence fixes. Older FAQ wording and automated-judge remediation give way to all of these when they conflict. This order is a deliberate reconciliation: if the live platform shows a newer explicit rule, the live rule wins and the discrepancy is logged.

| Code | Pattern | Classification / action |
| --- | --- | --- |
| CF-02 | Extractor reports truncated=true | Pipeline/extraction issue. Do not make it a verifier fail by itself; escalate/override only after substantive content checks are clean. |
| CF-03 | Verifier reads a fixed/incomplete business-data range and misses records | Real verifier/construct-validity defect. Fix the population/range logic; this is not the same as CF-02. |
| CF-04 | Cross-artifact equality demanded by a single-file verifier | Runtime-impossible verifier defect. Inline accepted shared anchors separately in each artifact’s owner. |
| CF-05 | Exact source population must be matched | Valid semantic rubric requirement when grounded. Express it in rubric PASS/FAIL text; do not invent unsupported deterministic assertion types. |
| CF-06 | PowerPoint spatial relationship inferred from extraction order | Potential construct-validity/runtime defect. Use reliable slide labels/observable structure or do not grade adjacency. |
| CF-07 | Source cross-reference to another document | Not automatically leakage. Reject only when it gives solver analytical directions/decomposition or reveals the answer; ordinary in-world references may be realistic. |
| CF-08 | Automated judge repeats old counts/old wording after regeneration | Stale QC result. Confirm current text, then document/override rather than rewriting already-fixed criteria. |

## Basis

The authority table, the first five chronology rules, codes TD to V-08, PL and CF, and the unkeyed classifications come from the RL World Finance Expert Onboarding (v6), the RL World Platform Quick Reference and Platform Overview, the Project Omega Guide (V5), the Trainer Review Gate Convergence Report (production data through 23 Sep 2026), the Omega Pod finance and investment tracker and the uploaded RL World task folders. Everything else, including codes V-09 to V-16 and JD-01 to JD-04, the first planned-difficulty test and the routing rule for source defects, comes from the review sessions recorded in `07_failure_patterns_and_lessons.md`.
