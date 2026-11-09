# The one-round checklist: every cause of a second round, and what round 1 does instead

Source: the EKW-OTS verifier fixes of 2026-10-31 to 2026-11-04 (11 tasks, 32 DataOS rounds, 12 RL World refusals),
read from each task's `VERIFIER_FIX_REPORT*.md`, the rerun verdicts and the upload notes. One task (migy8854, three
verifiers changed, all votes unanimous) passed its first run. Every other extra round is in the table below. Treat
each row as a gate for round 1; `round1_sweep.py` carries the codes in the last column.

## A. Before the first edit

| # | Cause of the extra round | Where it bit | Round 1 does this instead | Sweep code |
|---|---|---|---|---|
| A5 | A NOT A DEFECT written from reading, not recomputing | 6eydtrq9 S16 (PRT-4D78 recomputed in r2), 9dp (DRO values, debt impact, tie-outs all reopened in r2), vwr, mpp3gdze-0 ("$118 call"), jicq (`like_for_like`) | Every NOT A DEFECT on a number cites the recompute script. Every "solver miss" cites the sentence of the instruction and the search of the whole solver deliverable (every sheet, section and file). A NOT A DEFECT is provisional: list it under "watch on rerun" | - |
| A6 | An item called unasked after grepping only instruction.md | 0i4x19ri r2 removed the infection-control review; r3 restored it from the manual PDF p.7 | Grep the instruction and every named source, PDFs through pypdf or pdfplumber, before calling anything unasked | - |
| A8 | Split votes and accepting reviews' side notes not read | vwr r2 to r5 (ORACLE-SPLITs and Grok dissents on passing runs), jicq r3 (`latency_clock` 2-1 in both oracle runs), a0sbb1xd r2 | `task_snapshot.py --reasons`: every ORACLE-SPLIT, SOLVER-SPLIT and side observation is a numbered item with a disposition | - |
| A14 | The task read and the TFRL read skipped before the first upload | 083828 r1 DENY on D1 only; a0sbb1xd r1 flagged A2 in the task read | With the pipeline clone: `qc.py read --times 3` and `qc.py tfrl-read` on the fixed package before the DataOS zip | - |
| A15 | The route decided after the run: a full fix approved on DataOS, a scoped trainer zip that the run never graded | mpp3gdze-0 (35 of 46 fixes reverted), mpp3gdze-1, vwr, 6eydtrq9 (86 reverted), p8f6vjxz-0 | Decide trainer route or QC route first. For the trainer route pass `--feedback`: the round's file and the DataOS copy are scoped from the start, the rest is the next-round list | UNNAMED |
| A21 | The live version moved during the fix | vwr1nerq-2 v14 became v16 while rounds 2 to 5 ran; the approval attached to no live version | Read the version number of the RL World download before each build, and compare with the feedback's version | - |
| A23 | A golden or source defect worked as verifier work | 113904 (golden on a truncated lookback), 6eydtrq9 r4 (annex vs confirmation haircuts), jicq (golden median includes the duplicate), mpp3gdze-1 (pasted constants) | `source_range_scan.py`, recompute the golden's figures; a dissent about golden content on an oracle 2-1 is a golden item. Block the task and report; spend no round on it | - |

## B. While editing

| # | Cause | Where it bit | Round 1 does this instead | Sweep code |
|---|---|---|---|---|
| A1 | One more value added to a closed list | p8f6vjxz-1 `wb_comparable_event_price_scaling` (D-1 added, per-event median trough failed next), `wb_security_level_economics` labels, 0i4x19ri "FC-26B only", 9dp "Calloway Reed", jicq "Tight/Base/Wide" | Replace the list with the fact it stands for and a tolerance; keep old values as reference examples | LIST, ANCHORS |
| A2 | A twin on the other deliverable not aligned | p8f6vjxz-0 "points and dollars" vs the deck twin; 9dp funding-gap clause on the workbook only; a0sbb1xd consent date; 6eydtrq9 bridge pair contradicting | For every edited anchor, grep the whole file for the same anchor and apply the same carve-out, or declare one owner | TWIN |
| A3 | A golden literal left in an unnamed verifier; each new solver run surfaced the next one | vwr r5 `paper_opening_rec_decision` ("unit of account", 30 Sep), p8f6vjxz-0 "22 hours/week", a0sbb1xd "9 Jun 2023", 0i4x19ri "38.2°C", 6eydtrq9 "in favor of Northmere" | `literal_demand_scan.py` and the sweep on all verifiers in round 1; a written disposition per PHRASE, DATE, ID and UNIT hit | UNIT, WORDS, DATE-BAND |
| A4 | The same verifier reworded three or four times | p8f6vjxz-0 `deck_operating_model_decision` r1 to r4; mpp3gdze-1 `deck_approval_remediation`, `deck_refinancing_consistency`; 6eydtrq9 `memo_control_evidence_and_independent_review_evidence_preservation` (loosen, reword, delete) | At the first "judges still demand X": grade the fact in any form and placement, or delete and move the weight | REWORDED-3 |
| A7 | Absence-only PASS found one batch per round | 6eydtrq9 r1 gated 4, r3 another 7 (`cross_artifact_consistency_*`, a placeholder memo earned five checks), r4 one more; mpp3gdze `workbook_extraction_complete` | Sweep every PASS for absence wording and `$.truncated` guards in round 1; one presence-gate sentence on all of them | ABSENCE |
| A9 | Examples and "for example" lists read as gates | 0i4x19ri `brief_auditor_question_areas` ("for example a date, figure or record" with "no figure required"); 9dp "five figures kept as examples" | Drop per-item fact demands and example lists; never leave a golden layout or sheet name in the prompt, even as an example | EXAMPLE |
| A10 | Placement pins the instruction never makes | jicq "standards section", mpp3gdze-1 "at the rate input", 0i4x19ri "cites Chronology", vwr "slide 5", a0sbb1xd "on the stage-7 sheet" | Keep a pin only when the instruction names the location; otherwise "anywhere in the deliverable" | PLACE |
| A11 | The garbled agentic prefix "PASS only if Return only a boolean verdict." | 6eydtrq9 r2 (16 agentic checks: Grok wrote pass, recorded 0.0), jicq r2 (verdict-vs-reasoning flips) | Strip the prefix on every agentic check in round 1 | PREFIX |
| A12 | A numeric band pinned to the golden's convention or date | mpp3gdze-0 transition balance (±$0.02, then a band the ACT/365 variants still missed), p8f6vjxz-1 float-adjusted notional, 9dp DRO on one allocation, vwr one period start | Enumerate every convention the source allows, recompute each with code, grade the method first with a range that covers all, and let dependent bands follow the workbook's own upstream figure | DATE-BAND |
| A13 | The fix itself created a new ambiguity or oracle split | mpp3gdze-1 "$280.5m (normalized $276.4-276.8m)" read as a range; p8f6vjxz-1 D-1 anchor split the oracle on the spread path; jicq "every analysis total" exposed the golden median | Re-read every edited PASS sentence as a judge; a parenthetical alternative becomes its own conditional sentence; probe the golden on every edited check | PAREN-ALT |
| A24 | Cent-exact amounts in memo and deck checks | mpp3gdze-1 whole dollars failed 2-1; 6eydtrq9 "$14.064m" vs "$0.01m"; a0sbb1xd 5.7 vs 5.70 | State the rounding tolerance inside every memo or deck figure clause | CENTS |
| A25 | Named individuals or an owner per item demanded | mpp3gdze-1 `deck_transition_implications` (A7 DENY on a 0.975 codex), `memo_management_actions`; vwr "Group Controller"; 6eydtrq9 "IT lead" | Accept name, role or team unless the instruction says "named"; one owner may cover a group | OWNER |
| A26 | Exemptions joined with ", and" or ";" raised the pipeline's clause count | vwr r5, 9dp r3, 6eydtrq9 r3, mpp3gdze-1 r4 (rework inside the round) | Exemptions in parentheses without ", and" joins; `pipeline_diff.py` before the full build | (pipeline diff) |

## C. Shipping

| # | Cause | Where it bit | Round 1 does this instead | Gate |
|---|---|---|---|---|
| A16 | "Named" read as any mention | 9dp, jicq, vwr changes to evidence-only verifiers reverted on 2026-11-03 | Named = "Criteria at risk" plus names in the remediation; `trainer_upload.py` applies it | trainer zip check |
| A17 | A named criterion reworded but still demanding | 6eydtrq9 `deck_rollback_ordered_sequence_independently_checked_live_response` ("Data inconsistent"); the same in 6 of 9 trainer zips (a0sbb1xd care-location item, 9dp indemnity base, jicq typed label, vwr 4.40x baseline, p8f6vjxz-0 week-of-30-Mar clause) | When the item says "add to instruction.md or delete", delete or drop the demand; `feedback_resolution_dump.py` RISK lines must be empty or settled by a disposition | items resolved |
| A18 | A DataOS review of a file RL World does not hold | p8f6vjxz-0/-1 "upload as is" refused ("tests/verifier.json differs") | The fixed file becomes an RL World version first (trainer zip or updated-task zip); the feedback run grades that export byte for byte; md5 check before staging | pairing rule |
| A19 | `task.toml` guessed | Wrapped zips, trailing `[verifier.env]` kept, agent 14400, a mid-file table deleted, reconstructed key blocks; three rebuilds of all ten zips on 2026-11-04 | Build only from the live RL World download; delete only the trailing platform table; change nothing else | trainer zip check |
| A20 | No export manifest | p8f6vjxz-0 v8 ("Export manifest is missing"); all ten zips built from DataOS task_files held | The original must be the RL World download carrying `.external-qc-manifest.json`; it is copied, never written | trainer zip check |
| A22 | The review format changed and broke intake tools | reviews ending with a `checks` block: rule A, the manager read, proof init and the RL World import all failed until pipeline c1b4ce46 | Check the review format at intake; `task_snapshot.py` reads the last verdict JSON | snapshot |
| A27 | Weight bookkeeping | the library refused a sum of 1.00000046; a deleted verifier's weight must go to named verifiers only | Decimal arithmetic in `trainer_upload.py`; `validate_verifier.py` weight check | validator |

## D. Judge mechanics worth remembering

- Rubric checks: three judges, majority. Agentic checks: Grok and Sonnet first, Opus only on a split, so "only 2 of 3
  votes" is an early stop, not a missing judge. A 2-1 pass is one vote from a fail, and an ORACLE-SPLIT on the golden
  in both oracle runs was the most reliable predictor of the next DENY.
- Judges grade the rubric's own words, not its disclaimers: examples, closed lists and "in exact words" become gates.
  "Not on this sheet" is a placement claim, not an absence claim.
- `reward-details.json` shows one judge's reasoning; the votes are in `verifier-report.json`.
- Infrastructure: a Grok rate limit, a Daytona gateway error or a 600 s judge deadline can fail a check or abort a run
  (`RewardFileNotFoundError`); read `verifier/runtime.log` before calling it a verifier defect. Gemini 401s were a
  platform matter, resolved on RL World's side.
- Extraction: xlsx judges truncate at about 440k tokens; `pptx.extract_text` drops speaker notes; an agentic workbook
  judge cannot open the docx; a deck judge sees only the deck. A demand the judge cannot see is unverifiable.
- The RL World `task.toml` agent limit is 600 s and solvers needed 755 to 1,400 s, so the DataOS copy sets 14400 and
  the upload keeps 600.
