# Feedback type → the fix inside verifier.json

Contents: 1. DataOS review finding types. 2. Common reviewer and TFRL comments. 3. When the defect is outside
verifier.json. 4. Examples from past rework. 5. Things that look like fixes but are not.

Settle the item first (SKILL.md step 3). This page says what to do once you know the claim is true.

## 1. DataOS Answer Check finding types

| Type | What the review says | Fix in verifier.json | Usually NOT A DEFECT when |
|---|---|---|---|
| **READINGS** | The prompt or sources allow two or more defensible readings, and the verifier accepts one | List each reading and its value in the prompt, and accept all of them. Then fix every downstream verifier that cascades from the same choice (step 4, siblings) | The prompt or a source settles the reading explicitly. Quote that line |
| **WRONG_VALUE** | The verifier's expected value is wrong against the sources | Recompute from the sources with code, then correct the value and band. Check every other verifier that quotes the same number | The reviewer used a different but wrong convention. Show the computation |
| **GOLDEN** | The golden answer is wrong, and a verifier encodes the golden's claim | Rewrite the verifier to grade the correct value from the sources, not the golden's. The golden then fails that verifier: that is OUTSIDE VERIFIER.JSON, and the report must say the oracle will drop until the golden is fixed | The golden is right. Show the source |
| **CONFLICT** | A verifier requires what another prompt sentence forbids or limits | Make the verifier agree with the governing sentence. Quote it in the report | The two sentences apply to different deliverables or cases |
| **UNASKED** | A verifier demands a deliverable, figure, label, wording or placement (a fact on one named sheet or section) the prompt never asks for | Remove the requirement from the prompt text. If it was the verifier's whole point, delete the verifier and move its weight (SKILL.md step 5) | The requirement is implied by a clear prompt sentence or by plain professional practice that the prompt invokes ("a memo the board can act on" implies a recommendation) |
| **WEAK_GRADER** | A verifier passes empty, copied or wrong answers (the NOP run scores 0.20 or more, or pass-by-absence wording) | Add the presence gate (reference §4.1). Add anti-hack wording. Narrow the PASS band. For a deterministic check that passes on nothing, add or tighten the existence condition, or pair it with a rubric | The NOP run already fails it. Show the NOP result |
| **GRADER_BUG** | The judge or code errors, times out, misreads, or fails a valid answer for a mechanical reason | Rubric: fix the source command (`extract_many`, the right path), or reword away from what the extractor cannot see. Deterministic: change arguments, path, comparison or tolerance. If the bug is inside the Python, see §3 | The failure came from the solver's file (corrupt, wrong path the prompt fixed), or from judge setup: a `gemini/` credential error (`401 ... ACCESS_TOKEN_TYPE_UNSUPPORTED`), a provider timeout, a tie left by a failed judge. Those are OUTSIDE VERIFIER.JSON (setup), whatever weight the review puts at risk |

## 2. Common reviewer and TFRL comments

| Comment | Fix |
|---|---|
| "The oracle loses credit on vN" | First decide which is wrong. If the golden meets the prompt and vN fails it, vN is wrong: fix vN. If the golden really omits what vN rightly asks for, it is OUTSIDE VERIFIER.JSON (golden fix). |
| A literal the instruction never gives: an internal matter code, a record ID the deliverable need not cite, a file name, an exact phrase, a golden-only figure | Grade the concept and accept equivalents ("in any equivalent words", "named or clearly described"). Keep an ID only when the instruction asks for that record. `literal_demand_scan.py` lists the candidates |
| A fixed-size list longer than the instruction's ("all five measures", requests (1)–(6), eight controls) | Keep the items the instruction's own words require; delete the rest from the PASS line rather than marking them optional |
| Golden split (2/3) whose dissent is about the golden's own content (thin evidence, "+11 more" lists, boilerplate notes) | No wording change: it does not fix the golden, and any edit can tip the vote. Report it as golden risk, OUTSIDE VERIFIER.JSON. M3 authorization_basis went from 2/3 to 1/3 on rerun with the same golden |
| A required date falls on a weekend or holiday ("shows the 14-Nov-2026 response"; 14 Nov 2026 is a Saturday) | Accept the business-day-adjusted date ("by 14 November 2026, or the preceding business day"). The golden submitted on Fri 13 Nov and was failed for it |
| A closed list of accepted status words or sources ("PASS, FAIL, or PENDING"; "FAIL/mismatch labels"; "the deed or CAP-17") | Grade the concept: "any explicit wording that marks it as wrong", "any traceable source". Extending the list only moves the line judges reject at |
| `ORACLE-SPLIT` or `SOLVER-SPLIT`: the run passed by a bare majority | Read the dissent. If it cites rubric text the instruction does not ask for (a sheet pin, a literal phrase, golden layout or cell text quoted in the prompt, a fixed route per item), remove or loosen that text. If the dissent is right, the verifier is fine and the majority was lenient. A golden at 2/3 is the higher priority: one vote from an oracle below 1.0. |
| "vN flips between runs on the same answer" (one oracle passes, the other fails) | The prompt is not objective enough. Add concrete PASS/FAIL anchors and bands. If a bundled deterministic command measures the fact, switch to it. Task 674's v15 moved from "layout intact" wording to the `xlsx.template_contract` command. |
| "Every solver failed vN" | Read the solvers' files, all of them, not only the sheet or section vN names. If their work meets the prompt's words, vN is wrong (a Major at any weight): fix it. If they missed a clear requirement, it is NOT A DEFECT; quote the requirement. A judge's "not on this sheet" is about placement: search the rest of the deliverable before calling the fact missing. |
| "vN requires the fact on sheet/section X" (placement) | If the instruction names X and assigns that content to it, keep the pin. Otherwise accept the fact anywhere operational in the deliverable ("on this sheet or on any operational sheet such as …"), and keep the misclassification FAIL for the whole deliverable. Medical v19: PF/PO classification pinned to the source/control sheet. Name the concept, not a narrower window: #36 round 1 swapped "the opening summary slide" for "the deck's leading executive section", and the next judges read that as slides 1-2. Round 2 had to say "anywhere in the deck; an appendix alone does not count". |
| "vN demands the same reason or wording for every item" | Check each item's reason in the instruction. When the instruction gives an item its own reason (a duplicate reversed as a duplicate), accept that reason for it. Accept required wording in any audit field (rationale, evidence, assumption, shared header) unless the instruction fixes the field. Medical v19: "delivery unconfirmed" demanded of the duplicate pro-forma reversal. |
| "Compound criterion" or "independently variable facts in one pass/fail" | Split, keeping the parent's name on one part and sharing its weight. Split only facts that can independently be right or wrong and that each matter; don't shred into many tiny verifiers. |
| "Absence-only credit" or "an empty memo passes" | Presence gate, on every verifier with "does not introduce" or "does not state" wording. Task 672 and HLT-219 v5 both added it across all such verifiers. |
| "Arbitrary upper limit" or "band too narrow" | Derive the band from the sources and each defensible convention. Drop upper limits that the prompt does not imply. Task 672 replaced "16.3 to 17.1, or 17" with credit following the supported funding need. |
| "Judge cannot see the source it needs" | Switch the source to `filesystem.extract_many` with the needed `data/` files, and label which file is which in the prompt. |
| "Exact header, exact phrase or exact layout required" | Grade the concept with named synonyms. Accept a title row above the header, IDs inside longer cells, and 12- or 24-hour times. |
| "Metadata does not describe the grading" | Rewrite `how_justification` and `why_justification`. |
| "Weights do not sum to 1" or "outcome is weighted below process" | Rebalance within the affected deliverable. Keep core and secondary as they are. |
| "A verifier only checks that a file exists" | Fold the existence check into a content verifier's presence gate, and move the weight to content verifiers. Keep one deliberate `check_path_exists` or `list_unexpected` only if the prompt fixes exact file names. |
| "The judge timed out" or a run with no reward | First check it is the verifier timeout ("Verifier execution timed out after 3600.0 seconds" in the trial log), then count rubric verifiers × judges × 46 s. Don't add verifiers; merge near-duplicates or move mechanical facts to deterministic commands. The time limit itself is in `task.toml`, outside verifier.json. |
| "A formula gate fails a correct workbook" | Lower the floor to what a minimal compliant answer needs, drop a `sheet` or `cell_range` pin the prompt does not fix, or remove a formula gate from a prompt that never asks for formulas (reference §3). |
| "The workbook could be typed numbers and still pass" | Add or tighten `formula_summary` and `formula_authenticity_scan`, if the library has them and the prompt asks for a live model. A reworded rubric cannot fix this: the judge sees values. |
| "Rejects a valid alternative that a sibling verifier requires" (MKT-110: v17 rejected the /v1 and /v2 URLs that v7 required) | Make the two agree with the instruction. Check every FAIL clause against the instruction, the source headers and every sibling's PASS clause (task_24's v22 forbade the "budget" the instruction required, and failed every run including both oracles). |
| "A banned-word list catches the task's own vocabulary" | Narrow the ban to the misuse, or grade the concept instead of the word. |
| "Same fact graded on two deliverables, fixed on one" | Give the twin the same carve-out, or name one verifier as the owner of the fact and have the other grade only what is its own. |
| A deck, brief or note verifier demands workbook detail (cents, monthly splits, calculation inputs such as 744 hours, IDs, a numeric range) while the instruction keeps detail in the workbook ("Keep detail in the workbook rather than reproducing it on slides", "cite workbook evidence IDs") | Grade the deck on its conclusions at executive rounding, and accept a cited evidence ID in place of the figure. Move the precise check to the workbook verifier for the same fact. The deliverables have different contracts, so read each verifier against its own deliverable's instruction lines. EKW-OTS #35 failed three of four rounds on this (hours, HEART range, location), #36 on cents and splits, #38 on troponin values in the brief |
| Judges read an example list as closed ("e.g. falls 6.83, returns 29.2%" and a correct 2.88 fails) | For numeric anchors, give every accepted value for each basis, or state the rule that produces them. A partial list of values is read as the whole list. ("One short example at most" in SKILL.md step 5 is about wording examples, not anchor values.) #36 round 2 lost Terminus's pooled 2.88 and 72.13 this way |
| "No verifier penalises unrequested extra files or content" | Add a low-weight secondary verifier: `filesystem.list_unexpected` with the deliverables the prompt names, or a rubric on materially unsolicited content (with a presence gate). Take its weight from the secondary verifiers of the same deliverable. |

## 3. When the defect is outside verifier.json

The rule forbids editing these files, so record the defect and, only where it is honest, mitigate in verifier.json.

| Real defect | In-file mitigation (only if honest) | Report as |
|---|---|---|
| Golden answer wrong or missing content | None that keeps the verifier right. Do not loosen a correct verifier to let the wrong golden pass. | OUTSIDE VERIFIER.JSON: golden fix in `solution/...`, with the exact place |
| Prompt ambiguous | Accept every defensible reading in all affected verifiers. This is a real fix, not just a mitigation. | FIX, plus a note that the prompt could also be clarified |
| A source workbook formula is wrong (for example a SUMIFS range that stops before in-window rows), and the golden and a verifier carry its figure | Grade the corrected figure. Accept the uncorrected one only where the answer discloses the source error. Remove any FAIL clause that punishes calling the source method wrong. `source_range_scan.py` finds range cases | FIX, plus OUTSIDE VERIFIER.JSON (golden rebuilt on the corrected figure); the oracle drops until it is |
| The run graded nothing: judge credentials missing, agents cut off at the time limit | None in verifier.json, and the skill does not edit task.toml. `run_readiness.py` names what the run needs | OUTSIDE VERIFIER.JSON (run setup). Rerun before settling anything |
| Verifier asks for something the prompt does not (UNASKED) | QC checklists say "add it to the prompt or drop the criterion". Only dropping or loosening is open here. | FIX (removed or loosened), plus a note if the author may prefer to add it to the prompt |
| Library defect: uncached formulas read as blank, an extraction that misses charts or content controls, truncation that drops the graded sheet | Truncation: give each `extract_xlsx` verifier its own `range` with no sheet names (short, such as `A1:AZ80`, for control or narrative sheets; tall, such as `A1:T850`, for chronologies). Size it on the golden and every solver workbook (`xlsx_ranges.py` in this skill), and do it for every extract on a multi-sheet workbook the solver writes, not only the one a review named. Never pin the golden's tab names in `sheet_names`: a solver that names its tabs differently gets an unknown-worksheet error (EKW-OTS #40, feedback item 1). Charts: switch to a command or an agentic judge that sees them. Never edit the library. | FIX where scoping helps. A layout that no single range can serve (a 700-row chronology after a big daily sheet) is OUTSIDE VERIFIER.JSON, addressed to the platform (ISSUES-LOG rows 22, 28) |
| Judge setup: a `gemini/` judge with no working key, a provider timeout | None. This skill never changes `config.models` (`qc.py judgefix` included). | OUTSIDE VERIFIER.JSON (setup) |
| `tests/verifier-plan.md` now describes the old verifiers | None. | Listed under "Not fixed here" |
| Prompt asks for something no verifier can see | Choose a source command that can see it, if the library has one | FIX, or OUTSIDE VERIFIER.JSON if no command can |
| Python check wrong (preflight gate, `formula_provenance`, custom checker) | If a verifier.json argument controls the faulty behaviour, change it. Otherwise, when the check fails valid answers, either lower its weight, or replace it with a rubric verifier on the same concept and delete the code verifier, with its weight moved. A Python gate that runs before verifier.json (`preflight.py` in `test.sh`) cannot be reached from verifier.json at all. | FIX (when replaced) or OUTSIDE VERIFIER.JSON, naming the file and function |
| Data file inconsistent | Accept both values the inconsistent data supports | FIX, plus a note on the data |

Never disguise one of these as fixed. RL World reviewers re-run the task, and a hidden golden defect comes back as an
oracle below 1.0.

## 4. Examples from past rework (the 16 downloads of 2026-10-30, then the EKW QC pipeline's records)

- **HLT-219, rev_3 → v4 → v5 (verifier.json).** The rev_3 reviews raised two minors: v7f graded amlodipine and
  metoprolol in one 0.009-weight pass/fail, and its metadata claimed separate credit. v4 split v7f into `v7f_amlo` and
  `v7f_meto` at 0.0045 each, and split v1 into v1a (0.06) and v1b (0.04), going from 43 to 53 verifiers. v5 then
  merged everything back into 18 verifiers (v1 at 0.10) and replaced each "FIRST: if the memo is absent ... FAIL" line
  with one standard presence-gate sentence. Lesson: settle the granularity once, with a reason, and say in the report
  why you chose it.
- **674, rev_6.** Two oracle-side problems. First, v15 template layout flipped between the two oracle runs on the same
  workbook, so its grading moved to the deterministic `template_contract` command. Second, v25 failed the golden in
  all three judge votes because the golden omitted required qualifications. Under the verifier-only rule the v15
  change is in scope. The v25 golden fix is not: it would be OUTSIDE VERIFIER.JSON.
- **672, rev_4.** v12 and v13 gave credit for absence: a presence gate was added. The funding criteria rejected
  reasonable larger support ("16.3 to 17.1, or 17"): the credit now follows the supported funding need. The golden's
  cash sweep did not match its forecast: a golden fix, outside verifier.json.
- **HLT-159, v3 to v7 (reward-kit format, shown for the defect pattern only).** Each round, a Python preflight gate
  zeroed the whole task for a layout detail: an exact header row, a literal phrase such as 'pa-independent', a
  patient ID inside a longer cell, a "1:03 PM" timestamp. Every review gave the same fix: leave layout to the judge
  criteria instead of a hard gate. Under the verifier-only rule a gate in Python cannot be edited, so the report must
  say so, and the verifier.json side must not contain the same literal-match habit.
- **462 and 538 (reward-kit format, shown for the pattern only).** A `formula_provenance` code check failed fully
  live workbooks: it did not support IF(OR(...)), did not trace VLOOKUP chains, and took integer index columns for
  typed figures. The verifier-side options are to lower its weight or to grade the formula chain with a rubric. The
  checker's own bug is outside verifier.json.
- **Medical & health services v19, rounds 1 and 2 (2026-10-30).** Round 1 fixed the GL vs non-GL treatment that four
  reviews named in `finance_balanced_proposed_journals` and `finance_journal_audit_metadata`. It kept a second clause
  of the audit-metadata verifier that the round-1 judges had also failed both solvers on: every action's
  rationale/evidence must say delivery by 30 September is unconfirmed. It also called `finance_source_control_provenance`
  NOT A DEFECT, because "codex never classifies the PO", reading the judge's "not on this sheet" as "nowhere". All
  four round-2 reviews rejected the task for exactly those two verifiers. The same round-2 sweep found two boundary
  verifiers ("PASS if the handover contains no ledger amounts") with no presence gate, which no review had raised.
  Lessons: settle every clause a judge failed, search the whole deliverable before NOT A DEFECT, and sweep the file
  for the absence-only and placement patterns (SKILL.md steps 3 and 4).
  Round 3 then scored 1.0 everywhere and all four reviews accepted, but 8 verdicts passed only 2/3:
  - The golden passed `finance_episode_reconciliation_and_links` by a bare majority in both oracle runs; its 16-link register sat on the Source Control sheet.
  - One judge failed both solvers on `clinical_time_ordered_deterioration` for missing "the specified Table 2 cell text", golden layout that the prompt quoted as a hint.
  - Others failed solvers on a fixed route per evidence type, and on equivalent wording ("no delivery by cutoff was evidenced").
  Only the dissenting votes showed these. Lesson: read the split flags even on an accepted task.
- **EKW QC pipeline cases (2026-09 to 2026-10).** task_157 and LGL-160: oracle runs died at the 3600 s verifier
  timeout (108 and 66 serial judge calls) and wrote no reward; adding verifiers would have made it worse. as-finance
  v13: the Gemini judge failed on every verifier, ties then failed, and the oracle scored 0.949; reviews filed it as a
  grader bug, but the fix was the judge's key. HLT-189 and GTM-176: formula floors at or above the golden's count
  failed correct workbooks. GTM-187: a formula-share gate on a text tracker the prompt never asked to compute. FIN-117:
  a hidden floor of 10 loans per sheet zeroed a correct split layout. task_28: two rounds of wording fixes to one
  verifier passed the fixer's own reading and still failed the next real review panel, which is why SKILL.md step 3
  asks for a different kind of fix after two rewordings.
- **EKW-OTS fix requests (2026-11-02/03, six tasks; full rows in the pod's issues log, section 2).**
  - #40 took five DataOS runs, and three of the four extra ones were extract truncation found one workbook at a time.
    Scope every extract in round 1.
  - #22's round 2 loosened a fee verifier to "arithmetic only", and it then passed a $68,379 performance fee where
    the answer is $0. Run the reverse check on every loosened verifier.
  - #22 and #36 found a sibling holding the same figure or demand one practice pass late ($148,000; "formula-driven"
    in five workbook verifiers). Use the SWEEP list from `apply_verifier_fix.py`.
  - #35's lower-case anchors needed three rounds, one reading at a time. Before round 1, enumerate every reading the
    governing rules allow, as a matrix.

## 5. Things that look like fixes but are not

- **Deleting or zero-weighting a verifier because every solver failed it.** A hard criterion that the prompt clearly
  asks for is working as intended. Remove it only when it grades something the prompt does not ask for, or cannot be
  passed by any correct answer.
- **Loosening a criterion until the empty answer passes.** Every rubric must still fail a missing or empty
  deliverable. Check the NOP run before and after.
- **Pasting the golden's numbers as the only accepted answer.** When the sources allow two defensible readings, the
  verifier accepts both and names each one's value.
- **Literal-phrase matching.** "Must contain the words 'shift-level summary'" fails correct answers written in other
  words. Grade the concept and name synonyms where they help.
- **A third rewording of the same verifier.** See step 3: change the kind of fix instead.
- **Moving a criterion's sources into `extract_many` wholesale.** All files share one 90,000-character budget, so each
  added source cuts the deliverable's share. Add only the sources the verifier needs, deliverable first, and name
  each file in the prompt.
- **Calling a judge-setup failure a verifier defect.** A Gemini credential error, a provider timeout or a split vote
  from a failed judge says nothing about the criterion's wording. Report it as setup.
- **Pinning the golden's layout.** A deterministic `sheet` or `cell_range` argument, or a formula-count floor at the
  golden's own count, fails correct workbooks laid out differently. Pin a layout only when the prompt fixes it, and take
  floors from a minimal compliant answer.
- **Fixing the reviewer's sentence instead of the defect.** A review that says "v12 is too strict" may be pointing at
  a source the judge cannot see. Read the source command before you reword the prompt.
- **Rewording an unasked requirement.** When the instruction does not ask for X, a criterion that still demands X in
  softer words ("any second-person control" for "a different reviewer") is not fixed. RL World refused 6eydtrq9-2-v16
  for exactly this ("Data inconsistent"), and the 2026-11-03 audit found the same in 6 of 9 trainer zips. Delete the
  criterion, or drop X outright ("may also appear but is not required").
- **Adding one more accepted value to a closed list.** The next solver produces the value after that one
  (p8f6vjxz-1 `wb_comparable_event_price_scaling`: D-1 added in round 1, per-event median trough failed in round 2).
  State the rule that produces the values and a tolerance; keep the old values as reference examples only.
- **A conditional alternative in parentheses beside the golden figure.** "$280.5m (normalized $276.4-276.8m)" was read
  as a range and split the oracle 2-1 (mpp3gdze-1). Write the alternative as its own sentence with its own condition.

## 6. Wording judges turned into gates, and the fix that held

Each row cost at least one DataOS round in 2026-10/11. `round1_sweep.py` flags the pattern; this table says what to
write instead.

| Pattern in the check text | What the judges did | Fix that held |
|---|---|---|
| "tied to a concrete fact (for example a date, figure or record)" plus "no figure required" | Demanded a figure beside every item (0i4x19ri `brief_auditor_question_areas`, 3 of 3 judges) | Grade coverage of the areas; drop per-item fact demands and the example list; let one item cover several areas |
| Golden figures or sheet names "kept as examples", "Schedule 1 optional" | Still searched for the Schedule 1 table and side-by-side pairs (9dp `numeric_tieouts`, 3 UNASKED majors) | Remove every golden pointer; grade "input totals and the bridge are tied, with a visible result, traceable figures and source lineage"; accept a cited record or packet page as lineage |
| Closed list of accepted statistics or anchors | Rejected a correct statistic not on the list (p8f6vjxz-1) | "any median or mean of the comparable events' price or spread move through the window, from a pre-event base, consistent with the event data (±0.3 pp)"; old anchors as reference values; the explicit FAILs kept |
| Closed label list ("Sell, Hold, or Add"; "like-for-like"; "netting set") | Failed when no cell or sentence equals the word | "Sell and retain amounts per block count as the conclusion"; "any explicit wording, anywhere"; "the words are not required" plus a description of the fact |
| Unit literal ("Central has 22 hours/week") | Three rewordings still failed cumulative exhibits (p8f6vjxz-0, rounds 1 to 4) | Grade the fact "in any unit against the roster's reference values of 7 hours/week for Pods and 22 for Central, so that 21 h pooled by the paper week is the Pods figure" |
| "in points **and** in dollars"; "both proxy totals"; "the $2.3m difference written out" | Required every derived figure | "points or dollars"; "the cost of a later window and its sponsor-cash effect, relative to the memo's own base"; derived deltas "need not be written out" |
| "explicitly flags ... as open"; "states ... in exact words" | Wanted the word "open" or "unresolved" | "shows ... as an open or residual question in substance (a committee decision or a pending confirmation also counts)" |
| Reading B must rebut reading A; "distinct clocks" when both coincide | Asymmetric burden on the non-golden reading (0i4x19ri) | "Under B the qualifying-combination basis suffices"; "separate clocks only under A"; "elapsed time in any exact unit" |
| A band pinned to one convention or date ("$31,558,062.60 ±$0.02"; "10/23 only") | A defensible alternative convention fell outside (mpp3gdze-0, 9dp, vwr) | Method first, then a sanity range that covers every convention the source allows; dependent bands recomputed; "either reading, each with its own figures" |
| Placement pin ("in the standards section", "on the decision sheet", "cites Chronology") | The fact elsewhere in the deliverable failed (jicq, mpp3gdze-1, 0i4x19ri) | "stated once anywhere in the memo, provided the memo recommends them as the standard"; "counts anywhere in the workbook, tied to the coupon"; "on any slide" |
| Owner or name demand ("a named independent backup", "owner per gate", "Group Controller") | Roles, teams and pooled owners failed (mpp3gdze-1 A7 DENY on a 0.975 codex) | "owners may be roles or teams; naming individuals is not required"; "one owner may cover a group" |
| Reworded-but-still-demanding ("any second-person control") | RL World refused the upload; judges kept failing | Delete the criterion (weight to the named siblings) or drop the demand outright |
| Absence-only PASS ("PASS if the memo omits this figure"; `$.truncated == false`) | An empty or placeholder deliverable earned the weight (6eydtrq9 `cross_artifact_consistency_*`; mpp3gdze `workbook_extraction_complete`) | "FAIL also if the deliverable is missing, empty or a placeholder with no substantive content"; delete the truncation guard and spread its weight |
| Cent-exact amounts in memo or deck checks | Whole-dollar rounding failed 2-1 (mpp3gdze-1) | "(rounding to whole dollars or $0.01 million is fine)" inside the PASS sentence; workbook checks keep exact arithmetic |
| Exemptions joined with ", and" or ";" | The pipeline gate counted them as new conditions | Exemptions in parentheses without ", and" joins |

The restructure that held most often: grade the two or three underlying facts in any form or placement; FAIL = exact
negation, or missing/empty; no owner, date, label, figure or section required unless the instruction names it.
