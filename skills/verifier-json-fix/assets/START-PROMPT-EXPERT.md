# Fix my own task's verifiers: paste this into Claude Code

For a task author (expert) fixing the grading of their own RL World task after External QC feedback. QC sends the
feedback file together with a **runs zip** (the earlier runs of the task: solver answers and every judge's vote).
Open the Claude desktop app, choose the **Code** tab, pick your work folder, fill in the `< >` parts and paste:

```
Use the verifier-json-fix skill in expert mode to fix the verifiers of my own RL World task.

My task zip (downloaded from RL World): <file name, in this folder>
The feedback file QC sent: <file name, in this folder; or paste the feedback text>
The runs zip QC sent: <file name, in this folder>

I am the task author and I have not done this before. Explain each step in plain words before you do it.
First run the setup check in expert mode. Then fix only tests/verifier.json, build the round in expert mode with
the feedback file, and tell me exactly which file to upload to RL World and what to write for each feedback item.
If a finding is about my prompt, golden answer or data instead, tell me plainly and leave it for me.
```

## What Claude does with it (instructions for Claude)

1. `fix_setup.py --root . --expert` until `FIX SETUP: READY (expert mode)`. Ask before installing any package. No
   pipeline clone, DataOS or `claude` command is needed.
2. Check the inputs before anything else:
   - the task zip is flat and carries `.external-qc-manifest.json` (a real RL World download). Without it the trainer
     zip check fails and RL World refuses the upload: ask for a fresh download, don't work around it;
   - the feedback is the version's `-external-qc-feedback.json` (if the author pasted text, save it as that file and
     say the item ids may be missing);
   - the runs zip is unzipped into `<task folder>/in/runs/` (a dataset download with several tasks:
     `split_batch_zip.py`), then `task_snapshot.py <that folder> --out ... --reasons ...`.

   With no runs zip, say so and settle each item on the instruction, the sources and the golden alone.
3. SKILL.md: read "Round 1 is the only round", then steps 1 to 7 on the task. Every ORACLE-SPLIT, SOLVER-SPLIT and
   side note from the snapshot is an item. Settle numbers by recomputing, unasked claims by searching every named
   source. No fix sheet, no `fix_record.py`, no DataOS, no practice review.
4. Each round, which must end `ROUND <n>: READY (... expert mode)`:

   ```
   build_round.py --original <zip> --edits edits_r<n>.json --rec <task folder> --round <n> --runs <runs zip> \
       --feedback <feedback file> --expert [--dispositions SWEEP_OK.txt]
   ```

   Later rounds add `--from <task folder>/round<n-1>/verifier.json`. The sweep, the trainer zip check and the
   item-resolution check are gates: fix each FAIL, or settle it with a disposition line the report repeats. The
   pipeline diff runs the bundled checks; a NEW or WORSE finding is fixed, or kept only with the author's agreement
   through `--accept-diff`.
5. Hand back in plain words:
   - the file to upload: `<task folder>/round<n>/trainer/<zip name>_verifierfix_upload.zip` (never rename it; never
     the `fixed/` copy);
   - where: the task's page on RL World, "Upload Updated Task";
   - one line per feedback item, from the report's `RL World remediation lines`;
   - the items outside verifier.json, for the author to fix themselves;
   - the next-round list (`NEXT_ROUND_LIST.md` and the sweep's WARN lines), explained as "real problems the notes
     did not name; RL World takes only what the notes ask for, so these wait for the next notes".

   Say that QC re-runs the task after the upload: the local checks are not the final test.
