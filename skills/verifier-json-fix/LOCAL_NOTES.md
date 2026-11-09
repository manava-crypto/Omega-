# verifier-json-fix v2: local setup (Turing_QC_tooling)

Built 2026-11-04 by merging the other trainer's upgraded skill (`Downloads\verifier-json-fix.zip`, untouched) with our
2026-10-31 to 11-04 scripts and the lessons of the EKW-OTS fix rounds. See `CHANGES_v2.md` for what came from where.

## Where it lives
- **Source:** `C:\Turing_QC_tooling\trainer_skill\verifier-json-fix_v2\` (edit here).
- **Installed:** `C:\Users\devuser2\.claude\skills\verifier-json-fix\` (copy the folder over it after every edit).
- **Share:** `C:\Turing_QC_tooling\trainer_skill\verifier-json-fix_v2_share\` holds the zip and the expert guide
  (.md and .docx) for trainers.
- The v1 skill is kept at `trainer_skill\verifier-json-fix\` and `trainer_skill\verifier-json-fix.skill` (unchanged).

## Which Python
`build_round.py` runs every script with one interpreter, which needs pydantic, jsonpath_ng and openpyxl:
- `Task_for _Review\Other_review\_manager_tools\venv\Scripts\python.exe` has all three (no pdfplumber).
- `EKW_QC_pipeline\pipeline\.venv\Scripts\python.exe` lacks jsonpath_ng, so `validate_verifier.py` FAILs there.
Run `fix_setup.py --root <workspace>` once with the venv you will use; it writes `fix_config.json` and says what is
missing. Always `-X utf8`, absolute paths.

## House rules on top of SKILL.md
- **No judgefix, no judge changes.** `config.models` stays as the RL World download has it.
- **DataOS copy:** `dataos_copy.py` (agent 600 to 14400, missing judge keys added as `${KEY:-}` lines). Our
  `aligned_dataos_copy.py` is for the case where a trainer zip must be aligned with an earlier DataOS `task.toml`.
- **Trainer zips:** only `round<n>/trainer/*_verifierfix_upload.zip` from `build_round.py --feedback`, built from the
  live RL World download (the one with `.external-qc-manifest.json`). The trainer folder
  `Task_for _Review\Verifier Fixed task\` holds only such files.
- **practice_review.py** ships but is off our lane: DataOS is the only verdict (owner rule 2026-10-01).
- **Two flows (2026-11-04):** the QC-Feedback flow and the Verifier Fixer flow keep separate folders for the
  upload-ready task and the QC feedback (memory `feedback-two-rlworld-flows`).
- **Approvals and uploads:** ask before anything that uploads or approves on RL World or DataOS.
- **Original downloads:** never modified; work on a copy.

## Tests run on 2026-11-04 (see CHANGES_v2.md)
- `round1_sweep.py` on the original verifier.json of nine fixed tasks: flags the criteria the extra rounds were spent
  on (`cross_artifact_consistency_*` ABSENCE, `workbook_extraction_complete`, `memo_recommendation_total_uses` CENTS,
  the "PASS only if" PREFIX, `wb_security_level_economics` LIST, `deck_operating_model_decision` UNIT).
- `build_round.py --feedback` end to end on a 6eydtrq9-2 v16 test package: every gate ran; the trainer zip check
  failed on the missing manifest, as it must for a package that is not an RL World download.
