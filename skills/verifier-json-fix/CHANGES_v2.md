# verifier-json-fix v2 (2026-11-04): what changed and where it came from

Goal: a verifier fix that lands in one DataOS round and one RL World upload. v1 (2026-10-31) averaged three rounds on
the EKW-OTS fixes (11 tasks, 32 rounds, 12 refusals).

## Sources merged
| Piece | From | Note |
|---|---|---|
| SKILL.md base, Start here, edit-list workflow (`apply_verifier_fix.py`), `build_round.py`, `fix_setup.py`, `fix_record.py`, `scope_check.py`, `audit_fix.py`, `xlsx_ranges.py`, `check_judges.py`, `dataos_copy.py`, `practice_review.py`, `reader_copy.py`, `relabel_reviews.py`, `split_batch_zip.py`, `fix_common.py`, `pipeline_lite/`, the expert mode assets, `references/fix-request-flow.md`, `references/what-you-will-be-asked.md`, improved `task_snapshot.py` (`--reasons`, `--only`, checks-block parsing), `validate_verifier.py` (`--kept-how`), `pipeline_diff.py` (WORSE, UNCHECKED, Windows copy fallback), `run_readiness.py` (sandbox losses, build timeout) | the other trainer's fork (`Downloads\verifier-json-fix.zip`, 2026-11-04) | taken as-is unless listed below |
| `trainer_upload.py` (flat zip, task.toml rule, manifest, feedback scope, Decimal weights), `feedback_resolution_dump.py`, `scope_vs_feedback.py`, `scope_finalize.py`, `aligned_dataos_copy.py`, `compare_runs.py`, `upload_fix.py` | our `Task_for _Review\Verifier_fix\_tools` (2026-11-02 to 11-04) | the RL World upload rules the fork lacked |
| SKILL.md step 8, the step-4 RL World paragraph, "rewording an unasked requirement" | our v1 SKILL.md | re-inserted; the fork had dropped them |

## New in v2
- **`scripts/round1_sweep.py`:** the whole-rubric hardening scan (PREFIX, ABSENCE, PAREN-ALT, REWORDED-3, EXAMPLE,
  LIST, ANCHORS, PLACE, OWNER, CENTS, UNIT, WORDS, TWIN, DATE-BAND, UNNAMED, RISK). FAIL on a changed verifier, WARN
  elsewhere, dispositions file for settled hits. Every code is a cause of an extra round in the history.
- **`build_round.py --feedback`:** keeps the full edit as `verifier.full.json`, scopes the round to feedback-named
  verifiers (`scope_finalize.py`), writes `NEXT_ROUND_LIST.md`, runs the sweep, builds and checks the trainer zip
  (`trainer_upload.py`), reads every item against it (`feedback_resolution_dump.py`, RISK lines gate), builds the
  DataOS copy from the scoped file, lists the trainer zip in ROUND.md as the only upload file.
  `--instruction-sweep-dispositions` settles sweep and RISK FAILs in writing.
- **`audit_fix.py`:** the dialog-judges check is a note, not a FAIL (judges come from the download and are never
  changed); runs without `fix_config.json`.
- **SKILL.md:** "Round 1 is the only round" (six habits as gates), step 8 rewritten around the ten refusals, the
  description names the refusal messages so the skill triggers on them.
- **References:** `one-round-checklist.md` (every cause of a second round, A1-A27, with the task and criterion),
  `rlworld-refusals.md` (eleven refusal texts and the rule each implies), `fix-patterns.md` section 6 (wording judges
  turned into gates and the fix that held), four new "looks like a fix" bullets in section 5.
- **Assets:** `EXPERT-GUIDE.md` and `START-PROMPT-EXPERT.md` rewritten for the feedback file, the fresh download with
  its manifest, the `trainer/` upload file and the next-round list.

## Tests (2026-11-04)
- Baseline (RED): the history itself. v1 on these tasks: 6eydtrq9 4 rounds + 1 refusal, vwr1nerq 5 + 3 refusals,
  p8f6vjxz-0 4, p8f6vjxz-1 3 + 2 refusals, 9dp 4, jicq 3, a0sbb1xd 4, mpp3gdze-0 3, mpp3gdze-1 4 + 1 refusal,
  0i4x19ri 3 (open), migy 1 + 2 refusals.
- `round1_sweep.py` on the nine original verifier.json files: flags the criteria those rounds were spent on
  (6eydtrq9 `cross_artifact_consistency_*` ABSENCE and 16 PREFIX; mpp3gdze-1 `workbook_extraction_complete` and
  `memo_recommendation_total_uses` CENTS; p8f6vjxz-1 `wb_security_level_economics` LIST; p8f6vjxz-0
  `deck_operating_model_decision` UNIT).
- `build_round.py --feedback` on a 6eydtrq9 v16 test package (export-like zip, 6 edits, dispositions): all gates ran;
  scope finalize kept 6 named changes and listed 1 unnamed one; trainer zip check FAILed on the missing manifest only;
  items-resolved and sweep FAILed on the 4 named criteria the test left untouched (correct); audit PASS.
- GREEN: a fresh agent given only the v2 skill, the 6eydtrq9-2 v16 RL World files, the round-1 DataOS run and the
  batch-1 feedback produced in one pass what the real fix reached after four DataOS rounds and one RL World refusal:
  the five deletions (`deck_run_timing_lineage`, `memo_notice_pre_cutoff_dispute_basis`,
  `deck_rollback_ordered_sequence_independently_checked_live_response`,
  `memo_control_evidence_and_independent_review_independent_review`,
  `deck_regate_population_integrity_agreement_account_identifiers`), the four loosened named checks with presence
  gates, a disposition per kept named criterion, and a next-round list of 57 unnamed hits plus 9 snapshot items
  (including the golden bridge line it could not settle). Its 12 remarks on the skill were applied the same day
  (tarball deliverables, NEXT_ROUND_LIST always written, `--restart-from-export`, `--runs` folders, one
  `--dispositions` file, the triage order, the trainer-route scope statement, the dry-run manifest note).

## Known limits
- `trainer_upload.py` needs the RL World download with `.external-qc-manifest.json`; none of the DataOS-run task_files
  on disk has one, so every historical package fails that one line.
- Splits (`<parent>_<suffix>`) cannot ship through the feedback scope; RL World has not been tested with one.
- The QC team's updated-task route (`qc.py rlworld` STEP 1) keeps every fixed verifier; whether RL World applies the
  "beyond a fix" rule there is unknown.
- `fix_setup.py` wants one interpreter with pydantic, jsonpath_ng and openpyxl.
