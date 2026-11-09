# RL World refusals seen on verifier fixes (2026-10-31 to 2026-11-04), and the rule each one implies

`trainer_upload.py build` and `check` enforce the rows marked "builder". The others are process rules the report and
the hand-over must follow.

| # | Refusal text (as RL World shows it) | When | Rule | Enforced by |
|---|---|---|---|---|
| 1 | "DataOS review was run on a different package than this version's export: tests/verifier.json differs" | 2026-10-31, p8f6vjxz-0 v8 and -1 v13 feedback uploaded for a fixed file | The fixed verifier.json must first become the task's own RL World version (trainer upload or the QC team's updated-task zip). Feedback is uploaded only for a run whose verifier.json is byte-identical to that version's export | md5 check before staging; `build_round.py --feedback` builds the DataOS copy from the scoped file |
| 2 | "Non-Harbor ZIP path: <folder>/instruction.md" | 2026-11-02, migy8854-2 v4 (then jicq4o2h-1, p8f6vjxz-1) | The upload zip is flat: `environment`, `instruction.md`, `solution`, `task.toml`, `tests` and the manifest at the root | builder |
| 3 | "task.toml has a [verifier.env] table the platform manages. Delete the table and upload again." | 2026-11-02 (three zips); 2026-11-04 mpp3gdze-1 v23 with the download's trailing table kept byte for byte | Delete the trailing `[verifier.env]` table RL World appends to every download, with the blank line before it, and nothing else | builder |
| 4 | "changes the task beyond a fix" (goal changed / verification weakened) | 2026-11-02, p8f6vjxz-1 v13: agent 600 to 14400, and `wb_comparable_event_price_scaling`, a verifier the five-item feedback never names | Only verifiers named in that version's feedback (Criteria at risk plus remediation names) may change; the agent timeout stays 600 | builder |
| 5 | "changes the task beyond a fix ... Data inconsistent: the changed <criterion> still fails ..." | 2026-11-03, 6eydtrq9-2 v16: `deck_rollback_ordered_sequence_independently_checked_live_response` reworded to "any second-person control" when the item said "add to instruction.md or delete" | Every item is resolved by the upload itself; a reworded criterion that still demands the unasked thing is unresolved. Delete it or drop the demand | `feedback_resolution_dump.py` RISK lines (items resolved gate) |
| 6 | "Comprehensive review uses DataOS's retired ten-check format; review the task again in DataOS and import the new export" | 2026-11-03, vwr1nerq-2 v14; 2026-10-30 ljx6y9pt-1; 2026-11-02 all of EKW-OTS-02112026 | Reviews that end with a `checks` block are rewritten by the pipeline's `qc.py rlworld` (c1b4ce46) before upload; converters that only strip the block do not help | pipeline |
| 7 | "DataOS review was run on a different package than this version's export: task.toml has a [verifier.env] table other than the block this version's DataOS package added" | 2026-11-04, vwr1nerq-2 v14 feedback zips r1 and r2; earlier 1zzovduc-2 v7 | Never reconstruct or strip RL World's own key block in a feedback package; use the real download of the live version as the reference | process |
| 8 | "Updated task changes task.toml, which belongs to Task Design and is immutable under the active External QC threshold policy" | 2026-11-04, 083828 v19: its mid-file `[verifier.env]` (before `[agent]`) had been deleted | A `[verifier.env]` that other tables follow is the task's own: keep it byte for byte. Position decides | builder |
| 9 | "Export manifest is missing - cannot verify corrected upload" (also "The ZIP doesn't match the task's download, or its files don't validate") | 2026-11-04, p8f6vjxz-0 v8 trainer zip | The original must be an RL World download carrying `.external-qc-manifest.json` (exportId, expectedPaths, hashes, allowedMutablePaths), kept unchanged at the root. DataOS-run task_files never have it; never write one | builder |
| 10 | "DataOS export exceeded 100 MB" | earlier batches | Slim `workspace/work/` tarballs before upload | pipeline |
| 11 | Library: a weight sum of 1.00000046 refused | 2026-11 | Weights sum to exactly 1, Decimal arithmetic | builder, validator |

Routes as of 2026-11-04: the trainer route (`trainer_upload.py`) is scoped to named verifiers and needs the manifest.
The QC team's route (`qc.py rlworld`, pipeline c1b4ce46, STEP 1 `-updated-task.zip` on vN, then the feedback on
vN+1) keeps every fixed verifier; `trainer_upload.py check` FAILs that zip on the unnamed verifiers, and whether the
QC upload path applies the "beyond a fix" rule is still unknown. Say which route a round is built for in the report.
