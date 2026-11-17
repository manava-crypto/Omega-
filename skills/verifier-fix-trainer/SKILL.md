---
name: verifier-fix-trainer
version: "1.0"
description: For task authors (trainers, experts) whose RL World task came back from External QC. Fixes the task's grading checks in tests/verifier.json from the two files QC shares - the task zip from RL World and the DataOS runs zip with the reviews in it (…-dataos-with-runs.zip) - shows the author one plain list of the checks it changed or added before building the upload file, and builds the zip to upload once they say OK. Use it when a trainer says "fix my verifiers", "QC sent my task back", "here is the QC feedback zip", or drops a task zip and a with-runs zip in a folder. Needs nothing else - no setup, no config, no manifest, no QC pipeline, no DataOS or sheet access - and must never ask the user for any of those. Not for the QC team (they use verifier-fixer4).
---

# Fix my task's verifiers (for task authors)

QC ran your task on DataOS and reviewers found problems with some grading checks: the verifiers in
`tests/verifier.json` that decide whether an answer passes. This skill fixes that one file from QC's own run and
reviews, shows you what it changed, and gives you the zip to upload on RL World. Your prompt, golden answer and data
files are never touched.

## What you need: two files, nothing else

| | File | Where it comes from |
|---|---|---|
| 1 | your task zip | RL World, your task's page: Export & Download |
| 2 | the QC runs zip, named `…-dataos-with-runs.zip` | QC shares it (the DataOS run of your task with the four reviews inside) |

Put both in one folder and open Claude Code there. Their order and names do not matter: the script tells them apart.
With only file 2 it still works, because the task's files are inside it; then you get the fixed `verifier.json` to put
into your task yourself.

## Rules for Claude (read these first)

- **Never ask the user for any file or setup beyond those two files.** No manifest (`manifest.json`, `MANIFEST.md5`,
  `.external-qc-manifest.json`), no config or setup file, no labels file, no QC pipeline, no DataOS or RL World login,
  no sheet, no "export with the judges dialog", no earlier run. If a thing is absent, work without it and say in one
  line what could not be checked. The findings are in the reviews inside the QC zip; read them from there.
- **Never ask to install anything.** The scripts need only Python 3.9 or newer, no packages. If `python` is not on
  this computer, do the same steps by hand with the Read and Edit tools (unzip with whatever is at hand, read the
  reviews under `verifications/`, edit `tests/verifier.json` directly). The scripts are a convenience, not a condition.
- **Do the work without stopping at every step, then show the author once.** Do not ask about each small step or each
  finding as you go. Decide the fixes from the files and make them. Then, **before the upload file is built**, show the
  author one plain list: which checks you changed, which you added or removed, and what each one said before and says
  now. They own the task; they must know what is in their grading. Build the upload file only after they say OK.
- **Ask a question only when the files cannot answer it and their knowledge of the task can** (is this other reading
  valid in your field? did you mean one particular sheet? is this a slip in the golden answer?). Put such questions in
  the same message as the list, not one at a time along the way. Plain words, one decision per question.
- **Change only `tests/verifier.json`, and never its `config` block.** Never delete a verifier, cut a weight, or rename
  one unless a finding asks for exactly that.
- Explain in plain words. The author is an expert in the task's field, not in this tooling.

## Steps

Run every script as `python -X utf8 <this skill>/scripts/trainer_fix.py ...` from the folder that holds the two files.

### 1. Start

```bash
python -X utf8 <skill>/scripts/trainer_fix.py start
```

It finds the two files, unpacks them into `fix_<task>/` and writes:

- `FINDINGS.md`: every review finding, grouped by verifier, with the reviewer's evidence, "a correct answer that
  fails" and the suggested fix. One review of the five is QC's manager read (`900…`); treat it like the others.
- `RUNS.md`: how the golden (oracle) run, the solver runs and the empty run scored on every verifier, with each
  judge's reason where a run failed. This is the evidence: a verifier every solver failed, or one the empty answer
  passed, is worth a look even when no finding names it.
- `SWEEP.md`: other verifiers with the same kinds of problem (a sheet or slide pin, an exact wording, a check that
  can never fail). Found by pattern, not by a reviewer.
- `edits.json`: empty; you fill it in step 3.

Last line: `TRAINER FIX: STARTED …`. If it says your task zip is not the version QC ran, some findings may already be
fixed: read the current text before changing it. Tell the author in two or three plain sentences what QC found, then
carry on.

### 2. Read and decide

For each verifier in `FINDINGS.md`, read its text in `tests/verifier.json`, the sentence of `instruction.md` it
grades, the finding's evidence and the judges' reasons in `RUNS.md`. Then one of:

- **Fix it** as the suggested fix says. This is the normal case: QC's data shows task experts agree with about 9 in
  10 of these findings, including the ones only one reviewer raised.
- **Leave it**, when the instruction itself asks for what the verifier demands (quote the sentence), or the finding
  describes an older version of the text.
- **Not a verifier problem**: the finding says the golden answer, the task text or an input file is wrong. Do not edit
  those and do not bend the verifier to hide it. That part is the author's to fix on RL World; say so in step 4.

Then look at `SWEEP.md`. When a fix is "do not insist on this sheet / this exact wording", make the same change on the
other verifiers of that family, unless the instruction requires that placement or wording for them. QC's history: fixing
one such check per round cost five rounds on one task. These extra changes are exactly what the author must see in
step 4, because QC did not name them.

How to word a fix: `references/fix-patterns.md` (by finding type) and `references/verifier-json-reference.md` (the
file's fields). The short version:

- Change as little as possible. Add or reword a clause; do not rewrite the verifier.
- Loosen to the idea, not to a longer list ("any clear wording that marks it as overdue", not three more labels).
- Accept a value wherever it sits in the deliverable, unless the instruction names the place.
- Where the instruction allows more than one reading, accept each with its own value, or grade the answer on the
  basis it states.
- Never loosen until an empty or wrong answer would pass: keep the "FAIL if missing" part. Never paste the golden's
  figure as the only accepted value when another reading is valid.
- Keep the golden answer passing. If the golden itself fails a check, that is a golden question for the author.
- Update `how_justification` in one plain sentence when what is graded changes.

### 3. Write the edits and apply

Fill `fix_<task>/edits.json` (format at the top of `scripts/apply_verifier_fix.py`: `replace`, `insert`, `set`; each
edit names the verifier and, in `ref`, the finding it answers in a few plain words), then:

```bash
python -X utf8 <skill>/scripts/trainer_fix.py apply
```

`old` and `after` texts must match the verifier exactly, once; the message says which edit did not. Last line
`TRAINER FIX: APPLIED (n verifiers changed …)`.

### 4. Show the author what changes (once, before the upload file exists)

```bash
python -X utf8 <skill>/scripts/trainer_fix.py finish
```

It checks that only `tests/verifier.json` differs and that `config`, names and weights are intact, then writes
`SUMMARY_FOR_AUTHOR.md` and stops with `TRAINER FIX: WAITING FOR THE AUTHOR`. No upload file is built yet. A `STOP:`
line means something must be put right first (step 3 again).

Now tell the author, in one message and in plain words:

- **The checks you changed**, numbered: for each, what QC found in one sentence, what the check said, and what it says
  now. ("Check 2, the pay comparison: QC found it fails a correct report that states the pay basis in the methods
  section. It used to require the basis inside the pay section, in exact words. Now it accepts the basis anywhere in
  the report, in any clear wording. A report that never states it still fails.")
- **The checks you changed that QC did not name**, and why (they have the same problem as one QC did name).
- **Any check you added or removed.** These need their attention most.
- **What you left as it is**, and why; and **anything that is theirs to fix** (golden answer, task text, data).
- Any `check:` line the script printed, in plain words.
- Any question only they can answer (see the rules above).

Then ask once: **"These are the changes to your grading. OK to build the upload file, or do you want anything
changed?"** If they want something changed, go back to step 3 and show the new list. Do not build the file on silence.

### 5. Build the upload file

```bash
python -X utf8 <skill>/scripts/trainer_fix.py finish --confirmed "<the author's own words>"
```

Last line `TRAINER FIX: READY <fix_…/fixed/your task zip> (…)`, plus `FIX_REPORT.md`. Their OK is kept in
`DECISIONS.md` and quoted in the report.

### 6. Tell the author what to do next

- which file to upload: `fix_<task>/fixed/<the same zip name>` on RL World, your task's page, "Upload Updated Task";
- that QC will run the new version again: a fix is confirmed only by that run;
- anything that is theirs to fix before or after that upload.

## What this skill does not do

It does not run DataOS, upload anything, read RL World, or judge the golden answer. It does not need or use the QC
team's trackers. If the author has no QC runs zip at all, say so in one line and offer the pattern list in `SWEEP.md`
as the only thing that can be checked without it.
