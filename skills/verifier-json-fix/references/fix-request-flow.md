# A verifier-fix request, start to finish (EKW_QC_Fix_Request sheet)

A trainer's RL World task came back from External QC with verifier findings, and the trainer asked QC to fix the
verifiers on the **EKW_QC_Fix_Request** sheet (`fix_request_sheet` in fix_config.json, tab *Request*). QC fixes the
verifiers, proves the fix on DataOS and hands the zip back; the trainer uploads it to RL World (pod call 2026-11-02).

`<skill>` is this skill's folder; `<rec>` is the fix record `fix_record.py new` makes. Run every command from inside
the workspace, so the scripts find `fix_config.json`.

## The scope, without exceptions

**You change `tests/verifier.json` and nothing else** (pod rule, 2026-11-03: "for fix we only fix verifiers, never
task or anything else").

| Never on a fix request | Instead |
|---|---|
| `instruction.md`, the golden (`solution/`), source data (`environment/`), `task.toml`, `tests/test.sh`, the verifier library, `verifier-plan.md`, any other file | mark the item OUTSIDE VERIFIER.JSON; the report and the DM say what the trainer must change |
| `config` in verifier.json (judges, temperature, samples), `qc.py judgefix` | judges come only from the RL World download dialog |
| adding, removing or renaming a file in the package | |
| QC verdicts, a feedback JSON, "Upload QC Feedback", "Upload Updated Task" | none of these belong to a fix request; the trainer uploads |
| loosening a verifier until a wrong or empty answer passes; making the task easier | each loosened verifier must still fail the wrong answer it exists to catch |

The one file that differs on the way to DataOS is the DataOS copy's `task.toml` (agent time 14400, missing judge
keys), and that copy never leaves DataOS. `audit_fix.py` checks all of this before every approval.

## Pass rule: the only meaning of "fixed" (pod rule, 2026-11-03)

On one DataOS run of the latest pipeline version:
- **Evaluations:** both oracles pass (1.00) and the No-op fails (0.00). The solvers (Terminus, Codex) can score
  anything.
- **The 4 custom reviews:** every one `valid`. One `rejected` means not fixed, whatever the other three say. There is
  no "3 of 4" pass, even when you think the rejecting review is wrong: settle it and run again.
- **Then the manager read** on that run reads 4 of 4 reviews, and every item it raises is settled (below).

Read each verdict from the review's last `overall_verdict` JSON (`task_snapshot.py` does this), never from the
PASSED badge. A run where evaluations ended EXCEPTION at sandbox start is not a round result: don't count its reviews
(`run_readiness.py` lists such runs).

## Stages and the tracker

`fix_record.py` keeps the stages and refuses "done" without the proving line. Run
`python -X utf8 <skill>/scripts/fix_record.py <name> status` at the start of every chat.

| # | Stage | You do | Gate | Proof the tracker needs |
|---|---|---|---|---|
| F0 | Claim | Read the Request tab whole: in Chrome open `https://docs.google.com/spreadsheets/d/<sheet>/gviz/tq?tqx=out:html&gid=0`, then read the page text (the Drive connector returns only a sample of rows). Pick a free row with an RL World link and no "uploaded revised zip" note. On the user's yes, type G = their name, H = In-Progress, and read the row back. Then `fix_record.py new FIX-<short id> --row <n> --trainer "<name>"` | **user yes** | the read-back row |
| F1 | Download | On the RL World task page, newest version: copy every External QC finding into NOTES (review id, finding no., type, verifiers). Re-read the claim row. Find the earlier QC run (next section). On the user's yes: **Quality Checks -> Export & Download -> Download artifacts**, with the judges `xai/grok-4.7`, `anthropic/claude-sonnet-5-5`, `anthropic/claude-opus-5-5`. Never use the Artifacts-panel button: it skips the judge dialog. Then `fix_record.py <name> add <zip>`, which copies it to `originals/` and runs `check_judges.py` | **user yes** (one question for the export and the earlier run) | `JUDGES: OK` and the md5; the earlier run's file, or "none found" in NOTES |
| F2 | Fix | **Scope check first** (section below). Then SKILL.md steps 1 to 7 on the newest version, using the earlier run as evidence from the start. Each round is `edits_r<n>.json` plus `build_round.py` (section "Building a round" below), which must end `ROUND <n>: READY`. Then the practice review (below), in a terminal tab | | `ROUND <n>: READY` and `SCOPE: OK n verifier ...`, both quoted |
| F3 | DataOS run | On the user's yes: in Chrome open `https://data-os.turing.com/datasets/<dataos_master_dataset>` (7451, from fix_config.json), "Upload tasks", choose `<rec>/round<n>/dataos/<zip>` unrenamed (DataOS makes v2, v3 of the task for later rounds). Wait in steps of 10 s or less without leaving the page, then read the new task id from the page text (task name and id), never from a screenshot. On that task: "Run a pipeline", pick the 4-reviewer pipeline (`pipeline_name` in fix_config.json, "ManualQC automated QC pipeline 4 Reviewers") at its latest version. The run shows 9 nodes: 5 evaluations (2 oracles, Terminus, Codex, No-op) and 4 reviews. It takes about an hour: keep a background wait on the run page, or tell the user when to check back. If DataOS shows a sign-in page, stop and ask the user to sign in, in that same tab | **user yes** (about 3 USD) | dataset, task and run ids |
| F3 result | Read | All 9 nodes from the page, and reviews from JSON. Not a pass: on the user's yes, download "Task with runs" (or the dataset's "Dataset with runs") into `<rec>/in/round<n>/`. A dataset download holds every task in it: take this task out with `split_batch_zip.py <zip> <rec>/in/round<n>/x`, or unzip a single-task download into `<rec>/in/round<n>/x/`. Run `task_snapshot.py <rec>/in/round<n>/x --out <rec>/in/round<n>/snapshot.md --reasons <rec>/in/round<n>/reasons.md` (it reads folders, not zips). Settle every review finding and solver failure, then `fix_record.py <name> round --result "<run id: oracles, No-op, n/4 valid, why>"`, and go back to F2 | yes for the download | the round line |
| F4 | Pass and manager read | DataOS part of the pass rule, then the manager read (section below) | yes for the download | `4/4 valid` and `reviews read: 4 of 4` |
| F5 | Hand back | Copy the passing round's `<rec>/round<n>/fixed/<zip>` (never the `dataos/` copy) to `<rec>/for_trainer/`. Run `python -X utf8 <skill>/scripts/audit_fix.py --original <rec>/originals/<zip> --fixed <rec>/round<n>/fixed/<zip> --trainer <rec>/for_trainer/<zip>`. Write `for_trainer/SLACK_DM_DRAFT.md` (template below) | | `AUDIT: PASS (n checks)` with the trainer checks |
| F6 | DM and sheet | The user sends the DM with the zip. On their yes, set H = Fixed (and *Comment from QC* if asked). Leave *Updated on RL World* to the trainer | **user yes** for each | the read-back row |

Approvals: write the user's words into NOTES before acting on them. One yes covers one act; a yes relayed from
another chat after you already acted does not mean "do it again". Cost: one NOTES line per round
(`round n: run id, ~3 USD, hours spent`).

## Before the first fix: get the earlier QC run

The External QC findings came from a DataOS run another QC person already paid for. It has the solver workbooks (to
size every xlsx extract), every judge's vote (2-1 splits on the golden show unasked or literal requirements) and the
reviews' full findings. On #40, round 1 had only the golden, and three of the next four runs were spent finding what
that run would have shown.

1. RL World task version, External QC section: the QC feedback the other reviewer uploaded, often the
   `*-dataos-with-runs.zip`. Note its name and who uploaded it.
2. Not there: the review ids in the findings (the `900<id>` one is the manager read and carries the DataOS task id)
   lead to `https://data-os.turing.com/tasks/<id>`. Its page has "Download -> Task with runs".
3. Ask once, together with the F1 export. Put it in `<rec>/in/earlier/` and record its md5. Use it as `--runs` for
   `build_round.py` and `practice_review.py`. Unzip it into `<rec>/in/earlier/x/` (or `split_batch_zip.py` for a
   dataset download) and run `task_snapshot.py` on that folder.
4. Not visible ("Task not found" means it sits in another DataOS team): ask its owner to share the with-runs zip. If
   that fails, write "earlier run: none found, <where you looked>" in NOTES. Go on with the golden only, size ranges
   with extra margin, and expect the first DataOS run to show more.

## Scope check before any edit (pod rule, 2026-11-03)

Before you change a byte, prove every finding is a verifier problem. `SCOPE.md` is in the record.
1. One row per External QC finding, plus every item you add from the earlier run, the sweep or a practice review.
   Each row records RL World's category, the trainer's TP/FP label, **our category** and the quoted evidence:

   | Category | Meaning | What happens |
   |---|---|---|
   | VERIFIER | the verifier is wrong | fix it in `verifier.json` |
   | NOT A DEFECT | the finding is wrong | no change |
   | GOLDEN / PROMPT / DATA | the golden, prompt or source data is wrong | never edited |
   | PLATFORM | the library, runtime, judges or `task.toml` | never edited (a verifier.json workaround, such as sizing a range, counts as VERIFIER) |
2. `python -X utf8 <skill>/scripts/scope_check.py <rec>/SCOPE.md --findings <n>`:
   - `SCOPE: OK n verifier, k not a defect`: fix the VERIFIER rows only.
   - `SCOPE: STOP m outside verifier.json`: **stop before editing.** Tell the user which findings and why. They decide:
     - **fix the verifier rows alone:** F2 is closed with the STOP line and `--approved-by-user`, and the DM lists the
       outside rows for the trainer;
     - **hand it back:** no edit at all. On the user's yes set the sheet row's H to "Non-Verifier Issues", draft a DM
       with the non-verifier check block (point 5), and note the decision in NOTES with
       `fix_record.py <name> note "handed back: Non-Verifier Issues, <rows>"`. The remaining stages stay open; the
       record ends there.

     RL World sends tasks with non-verifier issues straight to Rejected.
   - `SCOPE: INCOMPLETE`: a row, a category or the evidence is missing.
3. **A verifier tied to a GOLDEN, PROMPT or DATA row is locked.** Never reword it so a wrong golden passes. `--scope`
   on `audit_fix.py` (build_round passes it) fails if a locked verifier changed.
4. **Revalidate before it counts.** A GOLDEN, PROMPT or DATA row is a claim against the trainer's work. Recheck it on
   the untouched original in `originals/`:
   - quote the task's cell or line, and the source or instruction it contradicts;
   - recompute the numbers;
   - search every source file for the value, minute-truncated too (#38: a "golden defect" was a real order at
     23:59:51);
   - write "REVALIDATED <date> on the original: REAL ..." in the row.

   If the recheck shows a misread, reclassify the row.
5. Every report and DM carries the result:
   ```
   Non-verifier check: SCOPE: <OK|STOP ...> (<n> verifier, <k> not a defect)
   - <GOLDEN|PROMPT|DATA> <cell or line>: REAL, revalidated on the original. Task says "<quote>"; source says "<quote>". Should say: <...>
   (or: none, every finding is a verifier issue or not a defect)
   ```
6. Each later round adds its new items to `SCOPE.md` and re-runs the check.

## The trainer's list is where you start, not the whole job

Fix the named findings, then sweep the whole `verifier.json` (SKILL.md step 4): the next run's reviewers read every
verifier. On #40 the trainer counted 13 rubrics with stray paths (there were 14). On #22 the trainer named one false
positive, and the reviewers then rejected three other verifiers. Agreeing with a trainer's "false positive" also
needs your own check against the instruction.

## Building a round

```
python -X utf8 <skill>/scripts/build_round.py --original <rec>/originals/<zip> --edits <rec>/work/edits_r<n>.json \
  --rec <rec> --round <n> [--from <rec>/round<n-1>/verifier.json] --runs <with-runs zips>
```

- Round 1 starts from the export (no `--from`). Every later round needs `--from` the previous READY round's
  `verifier.json`; the export there is refused unless `--restart-from-export`.
- `ROUND <n>: NOT READY`: open the failed step's log in `<rec>/round<n>/` (`apply.txt`, `validate.txt`,
  `pipeline_diff.txt` ...), fix the edits file, and build again under a new name, `--round <n>b`, with the same
  `--from`. A failed round folder is never reused or deleted.
- `PIPELINE DIFF: NEW FINDINGS` or `WORSE FINDINGS`, or verifiers now agentic: remove each NEW or WORSE finding (the
  usual cause is an added sentence, ';' or 'and' before FAIL), and read every now-agentic prompt yourself. If one
  must stand, rebuild with `--accept-diff "<why each one stands>"` and give the same reason in the report.
- With a pipeline clone configured, the integrity check and the pipeline diff run `qc.py` and the clone's checks (if
  Bash refuses them, run build_round in a terminal tab). Without one, the zip gate covers integrity and the bundled
  pipeline_lite runs the diff.

## Before each DataOS run: the practice review

It runs the team's comprehensive review prompt on the fixed package with the user's own signed-in `claude`, so it
costs tokens instead of a DataOS run. The app refuses to launch it through Bash, so give the user this line to run
in a terminal tab (or run it there yourself):

```
python -X utf8 <skill>/scripts/practice_review.py --package <rec>/round<n>/fixed/<zip> --runs <latest with-runs zip> --out <rec>/practice/round<n>
```

It ends `PRACTICE REVIEW: ... verdicts ..., majors ...`. Settle every Major like a review finding before asking for
the run, and quote the last line in the ask. It is a rehearsal: a practice `accept` does not replace the DataOS
reviews.

## After DataOS passes: the manager read

1. Ask once for the "Dataset with runs" download of the passing run. Put it in `<rec>/in/round<n>/` and record its
   md5. A combined export of several tasks: `split_batch_zip.py`.
2. Relabel the reviews:
   ```
   python -X utf8 <skill>/scripts/relabel_reviews.py <rec>/in_relabelled/round<n> <with-runs zip>
   ```
   It ends `RELABEL:`.
3. Inside the pipeline clone, in a terminal tab:
   ```
   python qc.py manage "<rec>/in_relabelled/round<n>/<zip>" --out "<rec>/qc_manage_out/round<n>"
   ```
   `manager/<DataOS task id>/manager_read_report.md` must read **"Answer Check reviews read (the 4 automated DataOS
   pipeline reviews of this task): 4 of 4"**. If it reads fewer, build a
   reader copy and run the manager read on it:
   ```
   reader_copy.py <rev> <out> --fence-verdicts [--weights]
   python <clone>/automation/manager-read/manager_read.py <reader copy> --out ...
   ```
   Add `--weights` for an unweighted verifier.json. If the reader answers in prose instead of JSON, read its raw
   answer by hand and quote it.
4. Settle every item in writing, with the quoted line:
   - A **Major** inside `verifier.json` (a correct answer loses credit, or a wrong one gains it) means not fixed: run
     `fix_record.py round` and go back to F2.
   - An item outside `verifier.json` goes to the trainer.
   - Anything else is NOT A DEFECT, with the reason.
5. Mark F4 done:
   ```
   --proof "run #<id>: oracles 1.00/1.00, No-op 0.00, 4/4 valid; manager read: Answer Check reviews read (the 4 automated DataOS pipeline reviews of this task): 4 of 4, <n> items, all settled"
   ```

## In every report

- One line for the judges (`tests/verifier.json` `config.models`) and one for the judge API keys (`task.toml`
  `[verifier.env]`, left as RL World wrote it). They are different things.
- The non-verifier check block from the scope section.
- Each round's `ROUND.md` last line and run result.

## Slack DM (F5), in the user's voice

```
hey <trainer>, fixed the verifier issues on <task short id> (v<N>), zip attached. only tests/verifier.json changed, prompt/golden/data untouched

<one line: what changed, in plain words>

dataos run passes now, all 4 reviews valid, oracles 1.00, noop 0. can you verify on your side and upload it as the updated task?
```

Add one line for anything OUTSIDE VERIFIER.JSON the trainer must decide (a golden defect, a library limit).
