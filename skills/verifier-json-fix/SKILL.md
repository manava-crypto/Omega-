---
name: verifier-json-fix
description: Fix the grading of a benchmark task (RL World, DataOS, Harbor) from reviewer or QC feedback by editing tests/verifier.json and nothing else, since RL World requires verifier fixes there only. Use whenever someone has a task's feedback (an RL World QC feedback JSON, DataOS review findings, TFRL or manager comments, a "Task with runs" or "Dataset with runs" download) and wants verifiers, rubric criteria, weights or judge prompts fixed, checked or rebalanced; for an EKW_QC_Fix_Request sheet request end to end; to set a machine up or continue a FIX-<id> record; to build or check a trainer's "Upload Updated Task" zip; after a second DataOS round or an RL World refusal ("changes the task beyond a fix", "Data inconsistent", "Non-Harbor ZIP path", "Export manifest is missing"); and to answer "is this a verifier problem?", even when the person says rubric, criteria or grader. Needs only Python.
---

# Fix a task's verifiers, in verifier.json only

The RL World team's rule: **every verifier issue is fixed in `tests/verifier.json`, and no other file changes.** The
instruction, golden answer, data files, Dockerfile, `solve.sh`, the bundled verifier library and any Python check
scripts all stay byte for byte the same. This skill turns a list of feedback into a corrected `verifier.json`, plus a
report that says, for each feedback item, what was changed or why nothing was.

The rule matters because RL World joins its feedback, calibration grades and judge-agreement data on the verifier ids
in this file. A change made anywhere else does not reach RL World's record of the task. Some feedback cannot be fixed
inside `verifier.json`, because the real defect is in the golden answer, the prompt or a code check. That is not a
failure of the skill. Say so plainly in the report and leave those files alone.

## Start here

This skill needs only Python. It carries pinned copies of the two pipeline checks that matter for verifier edits
(`scripts/pipeline_lite/`, see its PROVENANCE.md) and of the review prompt. The team's EKW_QC_pipeline clone is
optional: when configured, its current checks are used instead, and QC's manager read needs it. Every script is in
`<skill>/scripts/`. Run them with `python -X utf8` and absolute paths, from any folder (the record folder is the
usual one). One interpreter runs every script, so it needs pydantic, jsonpath_ng and openpyxl; pypdf or pdfplumber
is needed only to grep PDFs when settling an UNASKED claim (`fix_setup.py` lists what is missing).

1. **First time on a machine:** `fix_setup.py --root <workspace> [--clone <EKW_QC_pipeline>]`. It must end
   `FIX SETUP: READY`. It lists missing packages with the pip line: ask the user before installing anything.
2. **A request from the EKW_QC_Fix_Request sheet** (claim, download, fix, DataOS proof, hand-back): follow
   `references/fix-request-flow.md` stage by stage (F0 to F6), with `fix_record.py` as the tracker. Steps 1 to 7
   below are its F2.
3. **Just a task and its feedback** (no sheet, no DataOS run asked for): steps 1 to 7 below. To split or delete a
   verifier, use the edit script's `split` and `delete` ops; never write a script of your own.
4. **A task author (expert) fixing their own task** (no DataOS, no fix sheet; QC gives them the feedback and a runs
   zip): follow `assets/START-PROMPT-EXPERT.md`: `fix_setup.py --expert`, steps 1 to 7 with the runs as evidence,
   `build_round.py --expert`, then tell them which zip to upload to RL World and what to write for each item.
5. **Someone new to fixes:** they paste `assets/START-PROMPT.md`. Before each approval, explain the question in the
   plain words of `references/what-you-will-be-asked.md`: what yes does, what it costs, the usual answer. Never
   assume they know a term: say "the golden answer", not "the oracle".
6. **The fix goes to RL World as the task's new version** (a trainer's "Upload Updated Task", or the QC team's
   updated-task zip): give `build_round.py` the version's `-external-qc-feedback.json` with `--feedback`, and hand
   over only `round<n>/trainer/<name>_verifierfix_upload.zip`. Step 8 has the rules RL World enforces.

The approval stops are fixed: claiming a row, any download, any install, each DataOS run, the DM and any sheet edit
wait for the user's yes in this chat. Sign-ins are the user's. Nothing on a fix touches RL World itself.

## Round 1 is the only round

Eleven EKW-OTS fixes in 2026-10/11 took 32 DataOS rounds: 8 of 11 tasks needed three or more. One task was approved
on its first run. Every extra round traced to a known cause, and `references/one-round-checklist.md` lists them with
the task and criterion behind each. The causes fall into six habits, and the skill now treats each as a gate rather
than advice:

1. **Harden the whole rubric, not the named clauses.** The next run's judges and reviewers read every verifier. In
   round 1 run `round1_sweep.py` on the whole file (build_round does), give every ORACLE-SPLIT, SOLVER-SPLIT and
   accepting-review side note from the snapshot its own item, and settle every hit before the first run. Hits on
   verifiers the feedback does not name go in the next-round list, never silently dropped.
2. **Settle by evidence, never by reading.** No NOT A DEFECT on a number without a recompute script; no UNASKED
   without a grep of the instruction and every named source, PDFs included; read the whole solver deliverable before
   calling a fact missing. A wrong NOT A DEFECT in round 1 reopened as a FIX in round 2 on six of the eleven tasks.
3. **Fix the class.** Replace a list with the fact the list stands for; give both twins of a figure the same carve-out
   or name one owner; grade "in any form, anywhere" unless the instruction fixes the place; state the rounding
   tolerance; put the presence gate on every absence-worded PASS; never reword the same verifier a third time, change
   the kind of fix. `references/fix-patterns.md` section 6 shows, pattern by pattern, the wording that finally held.
4. **Decide the route before the first edit.** A trainer upload may carry only feedback-named verifiers, so scope the
   round to them (`--feedback`), keep the rest as the next-round list, and build the DataOS copy from the scoped file:
   the run must grade what RL World will hold. A DataOS approval of a wider file covers nothing.
5. **Block early on golden or source defects.** When the golden carries a source error, or two readings of the source
   give different answers and the golden never mentions it, no verifier edit fixes that honestly. Report it, hand it
   back, spend no round on it.
6. **Build only from a real RL World download.** Flat zip, `task.toml` as RL World wrote it, the export manifest kept,
   weights summing to exactly 1. Every `task.toml` guess cost an upload (`references/rlworld-refusals.md`).

`build_round.py` ends `ROUND 1: READY` only when the sweep, the validator, the pipeline diff, the trainer-zip check
and the item-resolution check all pass. A FAIL you have settled in writing gets a disposition line; a FAIL you cannot
settle is the next DataOS round, found before it is paid for.

**On the trainer route, round 1 is scoped and the list is the product.** RL World accepts only feedback-named
changes, so the sweep's hits on unnamed verifiers (the garbled prefix on every agentic check, absence-only PASS
clauses, lists, placement pins) cannot ship in this upload. They are not dropped: `build_round.py --feedback` writes
every one of them, with the unnamed edits it held back, to `round<n>/NEXT_ROUND_LIST.md`, and the report carries that
list to the QC lead, who can raise them as the next feedback round or ship the full file through the QC team's
updated-task route. "One round" on this route means: every named item settled for good, every unnamed defect known
and listed before the run, nothing found by the run that round 1 could have seen.

## What you need

1. **The task.** A task folder whose `tests/verifier.json` exists. Usually it is a DataOS "Task with runs" or "Dataset
   with runs" download, where the task is `<task>/rev_<n>__<id>/task_files/`. The runs in `evaluations/` and the
   reviews in `verifications/` beside it are the best evidence you have, so prefer a download with runs over a
   bare task.
2. **The feedback.** Any of these:
   - an RL World QC feedback JSON (`{"taskId", "version", "feedback": [{"id", "category", "description",
     "explanation", "remediation", "artifacts", ...}]}`);
   - the DataOS Answer Check reviews in `verifications/*.md` (a JSON verdict with `findings[]`, each with `type`,
     `criteria`, `weight_at_risk`, `evidence`, `correct_answer_that_fails` and `fix`);
   - free-text comments from a reviewer, TFRL or a manager.

   If no feedback is given, the reviews in the download are the feedback. Tell the user you are using them.

Only a task with at least one **major** finding needs rework. When every review accepted, or raised only minors, say
so and ask before changing anything: each edit to a package that passed reopens the risk the review just closed, and
the QC team has had to restore tasks reworked by mistake. Still run the snapshot and read its split flags before
answering. An `ORACLE-SPLIT` (the golden passed only by a bare majority) is the one finding worth raising on an
accepted task, because the next run can drop the oracle below 1.0 and send the task back.

Two package layouts are common, and the scripts handle both. An EKW or DataOS task keeps its goldens in
`solution/golden_outputs/` and its library in `tests/verifier_lib/` or `tests/__verifier_lib/`. An RL World download
keeps its goldens in `solution/output/` and its library in `tests/__verifier_lib/rl_world_verifiers/` or
`tests/rl_world_verifiers/`. The golden folder is whichever one `solve.sh` copies from. Never move files to make a
layout look like the other one, and keep the download's name, `-v<N>` included: RL World matches the version in it.

If the task has no `tests/verifier.json` and is graded by `tests/reward.toml` with `deliverables_*/judge.toml`, it is
the other grader format. Stop and tell the user that this skill does not apply. Do not convert the task to the other
format.

## Workflow

### 1. Find the newest version and take a snapshot

A download can hold several versions of a task, as `rev_N__ID` folders, sometimes one folder per resubmission
(`task-v4/`, `task-v5/`). The newest is the one with the **highest number after the double underscore** (DataOS's
global id). Work only on that one. Read older versions only to see what earlier rounds changed (step 3).

```bash
python <skill>/scripts/task_snapshot.py <download or rev folder> --out snapshot.md
```

The snapshot lists every verifier with its weight, core or secondary, source command, and pass (P), fail (F) or
error (ERR) in each run: both oracles (the golden answer), the solver runs and the empty-answer (NOP) run. It flags
`ORACLE-NOT-PASS`, `ALL-SOLVERS-FAIL`, `PASSES-EMPTY` and `ERRORED`, prints each failing run's judge reasoning (every
judge's verdict and justification, for rubric and agentic verifiers alike), and lists the source commands the bundled
library supports. It also flags `ORACLE-SPLIT` and `SOLVER-SPLIT`, a run that passed by a bare majority, and prints the
dissenting judges' reasons. A pass that one more vote would have turned into a fail is evidence too. Judge reasons and
review findings are cut at 400 characters. `--reasons reasons.md` writes every judge's whole justification for each
verifier a run failed or split on, and `--only v1,v2` lists the named verifiers on every run. Use it instead of writing
your own parser, and re-run the snapshot on every round's with-runs download. The source commands it lists are the
only commands a fix may use. Libraries differ
from task to task: the pipeline's sample task has no `filesystem.extract_many` at all. The `limits` line gives the
verifier count, the judging time against the task's timeout, and how many rubric verifiers the time budget still
allows. If the snapshot says the library was not found, find it by hand before planning any change of source.

Read each review's verdict from the snapshot, not from the review file's `## status` header, which reads PASSED
whatever the review decided. The snapshot takes the last JSON object carrying `overall_verdict`, because the transcript
also echoes the prompt's template. A review whose header reads `## status EXCEPTION` did not run (its body is only the
prompt template; an API usage limit did this to 7 of 20 reviews in one batch). The snapshot lists it as "did not run",
and says when fewer than four reviews ran. Treat the task as unreviewed, not as accepted. Any script that prepares
reviews for other tools should reuse `task_snapshot.last_verdict` rather than grepping one line, because verdict JSON
often spans several lines.

If the EKW QC pipeline is to hand, `deterministic-checks/eval_evidence_sweep.py --root <dir> --out <dir>` also flags
runs that scored 0 from a fatal error rather than from the answer. It only scans folders named `task_*`, so for an RL
World download link the task folder under such a name first (`ln -s <download>/<task> <dir>/task_<short>`); otherwise
it writes an empty summary without saying so. It does not show split votes, or read `custom_*` reviews, so the
snapshot stays the main view.

**Check that the runs graded anything.** The snapshot's `Runs` list marks each run NOT GRADED (no reward: the
verifier crashed, usually on missing judge credentials), AGENT CUT OFF (the agent hit the time limit) or AGENT FAILED.
It leaves those runs out of the flags. If it says nothing usable graded, stop: do not settle or fix verifiers from that
download. Run `python <skill>/scripts/run_readiness.py <rev folder>`, which names the missing judge keys and the agent
time the runs needed. Ask for a rerun with working settings. (The 30-Oct finance v12 rerun had no xai or anthropic key
and a 600 s agent limit, and every one of its 23 verifiers looked like a golden failure.)

**Golden first.** When the golden is below 1.0 in both oracle runs and two or more reviews call the golden wrong, decide
that before polishing verifiers. Verifier edits cannot raise an oracle whose answer is wrong. Settle each golden claim,
fix only the verifier text that is wrong in its own right, and report the task as needing a golden fix. Order clerks v48
went through 48 versions with its golden still releasing lines its routing evidence did not clear.

Then make a working copy, and never edit the original:

```bash
cp -R <rev folder>/task_files <work>/<task>_verifierfix
```

### 2. Turn the feedback into numbered items

Give each distinct complaint its own number. Four reviews often report the same defect four times; merge those into
one item and list all four sources. For each item record the verifiers it names, the weight at risk, and the claim in
one sentence ("a correct answer that writes 12.3 million fails v14").

**Triage order on a large file** (95 verifiers and 38 snapshot flags is normal): the feedback-named items first, then
ORACLE-NOT-PASS and ORACLE-SPLIT, then SOLVER-SPLIT, then ALL-SOLVERS-FAIL, then the sweep's WARN lines. An item
that goes to the next-round list needs one line of evidence and its sweep code; an item you settle as NOT A DEFECT
needs the full evidence of step 3. A manager-read item that says "The quoted words were not found in that file;
check them first" is a feedback-generator note, not a finding: check the quote against the live `verifier.json`.

### 3. Settle each item against the files before you change anything

Feedback is a claim, not a fact. Reviews are wrong fairly often: they misread a criterion, miss that another
criterion already accepts the alternative, or call a hard criterion broken. For each item, open what it cites:
`instruction.md`, the source files in `environment/data/`, the golden answer in `solution/`, the verifier text, and
the runs. A solver's actual deliverable is in `evaluations/<run>/eval_files/artifacts/workspace/output/`, or, in
newer downloads, inside `eval_files/artifacts/workspace.tar.gz` (extract it with Python's `tarfile`, since Windows
tar rejects `C:/` paths), and the
judge's per-verifier reasoning is in `eval_files/verifier/verifier-report.json`. Recompute every number with code,
not by eye.

Give each item exactly one verdict:

| Verdict | Meaning | What you do |
|---|---|---|
| **FIX** | The defect is in `verifier.json`: a criterion's text, tolerance, scope, source, weight or assertion | Fix it (steps 4 to 6) |
| **NOT A DEFECT** | The files show the verifier is right (the criterion is hard, the solver missed a clear requirement, or another criterion already covers the alternative) | No change. Write the evidence in one or two sentences with file and line |
| **OUTSIDE VERIFIER.JSON** | The real defect is in the prompt, golden answer, data or a Python check | No change to that file. Name the file and the needed change. Apply a verifier-side mitigation only if it is honest (see the reference) |
| **CANNOT SETTLE** | The evidence cannot decide it (for example, no runs, or the source is ambiguous in a way only the author can resolve) | No change. State the question the author must answer |

The decisive question for FIX: **would a materially correct answer that follows the instruction lose this verifier's
credit, or would an empty, hollow or wrong answer earn it?** If yes, it is a defect at any weight. Do not rate it minor
and move on, and do not reason a predicted failure away ("it will probably fail for another, legitimate reason"). In
a blind test, QC reviewers found the exact verifiers that were later rejected, rated them Minor, and would have shipped
them. For each verifier the feedback names, answer four questions with the prompt line or source cell:

1. Does the instruction ask for exactly what this verifier checks (the figure, row, caveat, section or item)? "The
   golden has it" is not a reason.
2. Does it accept every reading the sources support?
3. Does its expected value re-derive from the sources, by your own computation?
4. Does it respect every restriction in the instruction (records only, scope fences, length or layout freedom)?

A "no" to question 1 or 4 can only be fixed here by removing or loosening the requirement. Adding it to the prompt is
outside verifier.json.

**Ask the four questions of every clause of the verifier, not only the clause the feedback names.** Reviews quote the
loudest defect. When you edit a verifier, list every reason a judge gave for failing it in any run, and settle each
one as its own item. A clause you leave in place while predicting "this run will still fail on it" is an unsettled
item, not a NOT A DEFECT. The medical v19 round shows the cost: round 1 fixed the treatment clause that four reviews
named, noted that the judges also failed both solvers because the £18,750 rationale lacked "delivery unconfirmed"
wording, and kept that clause. The instruction gives the duplicate entry as that action's reason, so all four
round-2 reviews rejected the task for the clause round 1 had already seen.

**Read the dissents on passing runs.** Settle an `ORACLE-SPLIT` like an `ORACLE-NOT-PASS`: decide whether the
dissenting judge is right about the golden (a golden defect, outside verifier.json) or is reading a requirement the
instruction does not make (a verifier defect). Settle a `SOLVER-SPLIT` with the four questions applied to the dissent's
reason. When the dissent rests on rubric text the instruction does not ask for (a placement, a literal phrase, a quoted
golden layout, a fixed route per item), that text is a defect even though the run passed. When the dissent is right and
the majority was lenient, it is NOT A DEFECT. Medical v19 round 3 had all four reviews accept, yet the golden passed
`finance_episode_reconciliation_and_links` 2/3 in every oracle run that split. The dissenting judges rejected its
16-link register because it sat on the Source Control sheet, and the instruction names no sheet for the links.

**Test the verifier against the instruction, not the solver against the verifier.** "The solver has no status column"
or "the solver never names X" only settles an item when the instruction asks for that column or that X there. Before
NOT A DEFECT on a verifier the solvers failed, open each solver's deliverable and search **all** of it (every sheet,
section and file) for the fact the judge said was missing. Judges scope their reasons to what the rubric pins: "not
classified on this sheet" is a placement claim, not an absence claim. Medical v19 round 1 read "PO-NM-26-1847-L3 is not
named on this sheet" as "codex never classifies the PO". Codex classified it on its Cross-File Links sheet. If the
instruction does not fix where a fact goes, a verifier that pins it to one sheet or section is UNASKED placement.

**Two scans give a first candidate list. They are not verdicts.**

```bash
python <skill>/scripts/literal_demand_scan.py <rev folder>
python <skill>/scripts/source_range_scan.py <rev folder>
```

- `literal_demand_scan.py` lists what each judged verifier demands literally that the instruction never states:
  identifiers, file names, quoted phrases, placement pins (one sheet, section, slide, row or labelled block) and
  fixed-size lists ("all five", items (1)–(8)). Each is marked `instr`, `data` (a fact found only in the inputs) or `NONE`
  (in neither: an internal code or the golden's own value, the strongest UNASKED candidate). About 40 of 90 fixes on 13
  tasks were of these kinds. It also marks `check` for closed lists of accepted status words (LABELS) and for required
  dates that fall on a weekend (DATE).
- `source_range_scan.py` flags formulas in the input workbooks whose range stops before more rows of the same data.
  For each hit, check whether the cut-off rows meet the formula's criteria. If they do, the source figure is wrong, and
  a golden or verifier that carries it is wrong too. R2047 v9's lookback dropped $17,800 of transfer/ED charges this way.

Call a finding confirmed only when you can name the verifier **and** the run whose recorded verdict shows it (or, with
no run behind it, the concrete answer you built). Reviewers are wrong often enough, of both models, that neither one's
word settles a finding. Agreement of two reviews on one root cause is strong evidence; one review's story about why a
run failed is not, until the run's `verifier-report.json` says the same.

Judge failures that are setup, not verifier defects: a `gemini/` judge erroring on DataOS (a credential the platform
lacks), a provider timeout, a split vote caused by a failed judge. One judge error makes the whole run fatal, so a
reward of 0 with `errored 1` is usually this. Report it as OUTSIDE VERIFIER.JSON (setup), not as a defect in the
criteria it happened to hit.

Some feedback has no run behind it ("v20 would pass a document that just copies the instruction"). Settle it by
building the answer it describes: write out the copied text, the 12-hour timestamps or the alternative reading, and
read the verifier against it as the judge would. Remember the judge sees only what the source command extracts. A
rubric whose source is the deliverable alone cannot compare it with the instruction or the inputs. Call it FIX only if
that concrete answer would get the wrong result. Otherwise it is NOT A DEFECT, and the report shows the answer you
tried.

Look at older versions when they exist. If an earlier round already changed the same verifier, read what changed and
why, so the fix does not undo it. When this is the second round on a task you fixed, reopen every NOT A DEFECT of the
first round that the new runs or reviews touch, and test it again against the new runs. Do not carry the old verdict
forward. HLT-219 is the cautionary case: v4 split compound criteria into 53 verifiers, then
v5 merged them back into 18. Each round reversed the one before.

**A verifier reworded twice that still fails real judges needs a different kind of fix**, not a third wording tweak.
Your own reading of a new wording passes every time; that is why the first two tweaks shipped. Either restructure it
to grade only the underlying facts, accepting any presentation, or move it to a deterministic source command that
measures the fact (reference §2), or say in the report that it has resisted two rounds and needs a rewrite by the
author.

Read `references/fix-patterns.md` for the feedback type you are settling. It maps each review finding type (READINGS,
WRONG_VALUE, GOLDEN, CONFLICT, UNASKED, WEAK_GRADER, GRADER_BUG), and the common TFRL comments, to the fix that stays
inside `verifier.json`, with real examples from past rework.

### 4. Check the siblings

A defect rarely lives in one criterion. When one criterion has the wrong tolerance, or lacks an empty-deliverable
clause, or accepts only the golden's convention, other criteria written the same way usually share the gap. Search the
whole file for the same pattern, then fix all of them or note why each one differs. Reviewers send tasks back for the
sibling that was missed. A review quotes a sample of instances, not the full list.

Then sweep the whole file once for the patterns reviews rarely mention, whatever this round's feedback covered. These
are: absence-only wording with no presence gate ("PASS if it contains no …", "PASS if X is limited to …"), facts
pinned to a sheet or section the instruction does not fix, a reason or wording demanded of every item when the
instruction gives some items a different reason, and golden layout or cell text quoted in a prompt. Settle each hit
like a feedback item. An empty-answer run that fails only because the file is missing does not prove a presence gate:
read the verifier against an empty or placeholder file that exists.

Look especially at the twin of a fixed verifier on another deliverable: when the memo-side verifier now accepts a
citation style, the workbook-side verifier grading the same fact must accept it too (task_48). And re-read every
verifier against the golden, not only the ones the feedback names: a verifier the golden fails is a finding (in the
verifier or in the golden, settled as in step 3) whether or not this round's review noticed it.

**For an RL World upload, only the verifiers the feedback names can change** (step 8). The uploader refuses any other
changed verifier as "changes the task beyond a fix". Settle every sibling and sweep hit as above, but put the ones the
feedback does not name in the report as next-round items, not in this version's upload. `build_round.py --feedback`
does the split for you: the full edit stays in `verifier.full.json` and `NEXT_ROUND_LIST.md`, the round's file and
the DataOS copy carry the named changes only. A DataOS rerun of our fixed version is not RL World feedback either:
what it finds in an unnamed verifier waits for the next round.

### 5. Edit verifier.json, and only verifier.json

Write the edits as a list in `edits_r<n>.json` next to the report, one exact replace, insert, set, split or delete per change with
its `ref` (review id or item number), and apply it with the skill's script rather than a script of your own:

```bash
python -X utf8 <skill>/scripts/apply_verifier_fix.py <in verifier.json> edits_r<n>.json <work>/r<n>/verifier.json \
  --original <export verifier.json> --changes changes_r<n>.md
```

The edit-list format is in the script's docstring. It covers rubric and agentic prompts, `how`/`why`, and any path such
as `source.file.arguments.range`. Each text must match exactly as often as stated, and on a miss the script shows the
closest passage. It keeps the file's format byte for byte (indent, LF or CRLF, key order) and refuses an edit that
changes grading with no `how` edit or `keep_how` reason. It never writes over its input or an earlier round's output.
Read its WARNING lines (clause-counter wording, new placement pins, how/why longer than one sentence, unknown verifier
names) and its SWEEP list, which shows every other verifier that still holds a figure or ID you changed. Settle each
one before the build. Round n+1 starts from round n's output, and the edits files and change tables are the record
the reviewer reruns.

Make the smallest change that fixes the defect. Add a clause to a rubric rather than rewriting it, and keep the PASS
and FAIL text that already works. To loosen a requirement, delete it or say "X is not required". Don't add "X, or Y, or Z;
W is welcome but not required". Every added alternative or example reads as another condition to the pipeline's clause
counter, which turned warnings into fails in batch 3. One short example, at most.

**Loosen to the concept, not to a longer list.** When the defect is a closed list of accepted labels, sources or
wordings, replace the list with what it stands for: "any explicit wording that marks the configured value as wrong",
"any traceable effective source". A list such as "FAIL/mismatch/requires-correction labels pass" was still the line
judges used to reject "superseded" and "not appropriate" one round later (N1, d3 runs). `literal_demand_scan.py` flags
these as LABELS.

**Exempt by scope, not by describing an artifact.** "An auxiliary summary that shows annual totals does not fail"
did not help, because the judges decided the golden's investor-HWM sheet was an HWM schedule, not a summary (M4).
Name what is graded ("grade the dated ledger and the class-level fee and HWM schedules"). If the golden's artifact
really breaks the rule, report it as a golden defect rather than writing around it.

Don't paste long passages of the instruction or sources into a prompt. A short quote
or one named example anchors the judge, while a paragraph of pasted text buries the criterion. Put text shared by
several verifiers in each of them, since every verifier is judged alone, but keep that text to a sentence or two.

Rules that keep the file valid and the change reviewable:

- **Keep verifier ids stable.** RL World joins feedback and calibration on `name`. Change the text of an existing
  verifier rather than deleting it and adding a new one. When you split a verifier, keep the original name on one part
  and give the others the same stem with a suffix (`v7f` → `v7f`, `v7f_b`).
- **Keep the total weight at 1**, and move weight as little as possible. A split shares the parent's weight. When you
  delete a verifier, give its weight to the verifiers that now grade that concept, or spread it in proportion over
  verifiers of the same deliverable. Keep `importance` (core or secondary) and `grading_role` unless the feedback is
  about them.
- **Update `how_justification` and `why_justification`** whenever the grading changes, so they describe what the
  verifier now does. A stale justification is a finding in its own right. Keep each one a single plain sentence, with
  no semicolons and no lists of conditions. The judge never sees it: the runtime copies `how_justification` into
  `reward-details.json` as the criterion description. But the QC pipeline grades it as the criterion text of every
  **agentic** verifier (its adapter reads only `rubric.prompt`), so "…; it accepts X, Y and Z" raises compound
  warnings that the prompt itself never caused.
- **Use only source commands the bundled library has.** The snapshot lists them. Adding a command means changing
  Python, which is out of scope.
- **Prefer a deterministic command to a reworded rubric** when the verifier is about a mechanical fact: a chart exists
  (`xlsx.has_chart`), values are live formulas (`xlsx.formula_summary`, `xlsx.formula_authenticity_scan`), a count, a
  file exists. A judge reading extracted text cannot see charts or tell a formula from a typed number, so no wording
  fixes that. Keep rubrics for reasoning, completeness, tone and consistency. Exception: RL World libraries'
  xlsx reading commands (`extract_xlsx`, `read_range`, and the agentic judge's tools) return formulas by default
  (`include_formula: true`), so an agentic or rubric verifier there *can* tell live formulas from typed values, and a
  library with no `formula_*` command has no deterministic route to offer.
- **Mind the count and the clock before splitting.** QC and RL World gates flag fewer than 6 or more than 20
  verifiers. Rubric verifiers are judged one call at a time, about 46 seconds per judge model each, inside
  `[verifier] timeout_sec` (usually 3600), and a run that times out gets no reward at all. Agentic verifiers are judge
  calls too and count the same. The snapshot's `limits` line gives this serial upper bound and how many more judged
  verifiers fit, and its `Runs` list gives each run's measured verifier time (judges run in parallel on DataOS, so the
  measured time is usually far lower). Split only facts that are independently right or wrong and each
  matter; a binary "every / all / each item" over a list is the bundle reviewers reject, while one cohesive decision
  with several parts is not.
- **Keep at least one deterministic verifier** on an EKW or DataOS task: the Harbor rubric gate wants one, and a
  formula-based source on every xlsx deliverable whose golden uses live formulas. (RL World itself accepts rubric-only
  files.) On an RL World package the gate misreads both: it counts every non-`rubric` assertion, agentic included, as
  deterministic, and it looks for `formula` in a command name, which the RL World library does not have. An
  `anti_cheat_robustness` fail there is not a verifier.json defect; report it as platform, do not add verifiers for it.
- **Leave `config` alone** (judge models, temperature, effort, `judge_sample_count`). It is a platform file: RL World
  refused uploads whose judges had been changed. This skill never changes judges, `qc.py judgefix` included: the
  judges come from the RL World download dialog. A Gemini or other judge failure is reported as setup.
- **Don't edit the golden to fit a verifier, or a verifier to fit a wrong golden.** When the golden fails a correct
  verifier, the golden is the defect, and it is OUTSIDE VERIFIER.JSON.
- **Don't make the task easier than the defect requires.** Fix ambiguity, misalignment and brittleness; keep genuine
  difficulty. Resolving an open choice by telling the judge to accept only the easier reading, or loosening a band
  beyond what the sources support, trades one defect for another.
- **Files beside verifier.json are not yours to change.** If `tests/verifier-plan.md` exists, it now describes the
  old verifiers: list it under "Not fixed here". Notes the QC pipeline expects (`reports/<task>_TRACE.json`) live
  beside the package, never inside it.

How to write a rubric prompt that holds up is in `references/verifier-json-reference.md`: the schema, the assertion
types and comparisons, and a checklist for rubric text.

### 6. Validate, then re-grade by reading

For a package built from an RL World export zip, one command runs this whole step except the read-through, and writes
it all into a new `<rec>/round<n>/` folder (it refuses an existing one, so earlier rounds stay on disk):

```bash
python -X utf8 <skill>/scripts/build_round.py --original <RL World download zip> --edits edits_r<n>.json --rec <record> \
  --round <n> [--from <rec>/round<n-1>/verifier.json] --runs <with-runs zips> [--pipeline <EKW_QC_pipeline root>] \
  [--feedback <version>-external-qc-feedback.json] [--dispositions SWEEP_OK.txt]
```

It applies the edit list. With `--feedback` it then keeps the full edit as `verifier.full.json`, scopes the round's
`verifier.json` to the feedback-named verifiers (`scope_finalize.py`) and writes the unnamed changes to
`NEXT_ROUND_LIST.md`. It runs `round1_sweep.py` on the whole file (the one-round rules: FAIL on a changed verifier,
WARN elsewhere), then the validator. It builds the fixed zip from the original entry by entry and checks that the
`verifier.json` inside matches the round's file. With `--feedback` it builds the trainer's upload zip
(`trainer_upload.py build`, then `check`: `UPLOAD CHECK: PASS`) and reads every feedback item against it
(`feedback_resolution_dump.py`: a named criterion kept although the item offers deletion, or named and unchanged, is
an open RISK line). It makes the DataOS copy from that same scoped file, then the integrity check (`qc.py integrity`
with a clone, otherwise covered by the zip gate), the pipeline diff (the clone's checks, otherwise the bundled
pipeline_lite), `run_readiness`, `xlsx_ranges` and `audit_fix`. It ends `ROUND <n>: READY` only when every gate
passes, with each step's last line in `ROUND.md`. It takes several minutes, so run it in the background. Read each log
it names before the read-through below. The commands it wraps are described next, for running one check on its own.

A sweep or RISK FAIL you have settled gets one line in the dispositions file (`--dispositions SWEEP_OK.txt`, one file
for both), `<verifier> <CODE> <reason of 15+ characters>` (`deck_x RISK NOT A DEFECT: instruction.md:14 asks for the
owner by name`), and the reason goes into the report. The items-resolved gate raises RISK for **every named criterion
you kept** when its item offers deletion, so each kept-and-reworded named criterion needs a line saying which demand
is gone and which instruction line asks for what remains. That line is the sentence RL World reads when it decides
"Data inconsistent", so write it before the build, not after. Never silence a FAIL you have not settled against the
files.

The round folder holds: `edits.json`, `verifier.json` (scoped when `--feedback`), `verifier.full.json`, `changes.md`,
`sweep.md`, `NEXT_ROUND_LIST.md` (always written with `--feedback`: unnamed edits held back plus every sweep WARN),
`fixed/`, `dataos/`, `trainer/`, one `.txt` log per step and `ROUND.md`. `--runs` takes with-runs zips or unpacked
`rev_*` folders. A second try of the same round is a new name (`--round 1b`); `--restart-from-export` lets a round
start from the export although earlier rounds exist. On a dry run from DataOS task_files (no
`.external-qc-manifest.json`) the trainer-zip check is the one FAIL to expect; it cannot be settled by disposition,
and the real build needs the RL World download.

```bash
python <skill>/scripts/validate_verifier.py <rev folder or original task_files> <work>/<task>_verifierfix
```

It confirms that no file other than `tests/verifier.json` changed. It also runs the task's own bundled schema on the
file, and checks for unique names, weights that follow the library's rule, commands that exist, paths the golden
folder actually holds, and an unchanged `config`. It prints a per-verifier change list for the report. Fix every
`PROBLEM` line and run it again until it ends `VERIFIER CHECK: PASS`. Pass every round's edits file with
`--kept-how edits_r*.json`, so a stated `keep_how` reason becomes a NOTE instead of a stale-justification warning
(build_round.py does this). A library it cannot find is a PROBLEM, not a
note: without it nothing confirms the file will run.

`WARNING` lines do not fail the check, but each names a rule a QC or RL World gate acts on: the verifier count, the
judging time against the timeout, the last deterministic verifier, outcome weight below process weight, a
justification left stale, a prompt that points at the instruction, an `extract_many` that lists sources before the
deliverable or splits the budget thin, a new sheet or range pin, a `gemini/` judge, a stale `verifier-plan.md`, and, on
every verifier whether you changed it or not, a PASS that rests on absence with no presence gate. Change the edit, or say
in the report why the warning stands.

If the QC pipeline is to hand, also run `python qc.py integrity <download> <fixed package>`: RL World refuses an
upload that it fails. Then run the pipeline's own checks on both packages and read only the difference:

```bash
python <skill>/scripts/pipeline_diff.py <original task_files> <work>/<task>_verifierfix --pipeline <EKW_QC_pipeline root>
```

It runs `run_all.py`, `reward_signal_gate.py` and `harbor_rubric_gate.py` (read-only) on the original and the fixed
package. It prints NEW, CHANGED (marked WORSE when a severity or a clause count rises) and GONE findings. It ends
`PIPELINE DIFF: NO NEW FINDINGS`, `NEW FINDINGS` or `WORSE FINDINGS`. A fix must not add findings or make one worse.
Remove each NEW or WORSE one, or say in the report why it stands. Findings on a verifier you switched to agentic are
listed as UNCHECKED, not GONE: the pipeline stopped reading it, so read that prompt yourself. On Windows it copies the
packages when it cannot make a symlink. Use the QC venv (Python 3.11+). Findings present in both packages are the task's existing state, not this
fix's: don't chase them unless the feedback raised them. A clean result says nothing about agentic prompts, because
the pipeline never reads them (see the `how_justification` rule in step 5).

Before handing over a zip to run, check that it can grade:

```bash
python <skill>/scripts/run_readiness.py <work>/<task>_verifierfix
```

- **Judge keys and time limits.** It flags any judge provider in `config.models` with no key in `task.toml`
  `[verifier.env]`, and an `[agent] timeout_sec` below what solver runs need (default floor 14400 s). It also flags an
  `[environment] build_timeout_sec` of 600 s or less on a heavy image (libreoffice, tesseract, many packages), and
  runs in the download lost at sandbox start. Those are platform failures: don't count those runs or their reviews.
- **Report only.** This skill never edits `task.toml` (RL World refuses a package whose `task.toml` differs from its
  export). Put the NOTICE lines in the report for RL World and for whoever launches the DataOS run.

The validator cannot tell whether the new wording grades correctly. For every verifier you changed, read it as the
judge would and check it against five answers. Use real files from the download where you can:

1. **The golden** (`solution/`): it must still pass.
2. **Each solver run** that the feedback said was wrongly failed, and each solver run that failed a verifier you
   changed: it must now pass when its work meets the prompt. "It may still fail for another reason" is not a result.
   Either quote the instruction sentence the remaining failure rests on, or treat that reason as a clause to fix.
3. **The empty answer**: a missing, empty, header-only or placeholder deliverable must fail.
4. **A plausible wrong answer**: think of the specific mistake the verifier exists to catch (the wrong discount rate,
   the stale figure). It must still fail. Include a hollow one: the right headings and file names with typed numbers,
   an empty section or a renamed column.
5. **A different correct answer**: one that differs from the golden where the prompt leaves a choice open (layout,
   sequencing, wording, rounding, units). It must pass. The golden passes its own conventions by definition, so only a
   genuinely different answer tests brittleness. Build it to contain **everything the instruction requires**, then read
   it past **every FAIL clause** of the verifier, not only the clause you changed. In N1 the instruction requires a
   communications step, while the rubric said the CUT-38 baseline has none and failed any departure left unlabelled.
   The fix removed the approval-route clause, and the next run failed both solvers for adding communications without
   calling it a departure. Check required dates the same way: a deadline that falls on a weekend may be met on the
   business day before it (`literal_demand_scan.py` flags such DATEs).

If any of the five comes out wrong, the edit is not finished. Write in the report which check you ran on which file.
These are your readings, not new judge runs. The real test is the next DataOS or RL World run, and the report must say
so.

### 7. Write the report

Save `VERIFIER_FIX_REPORT.md` next to the working copy and show it to the user. Use this structure:

```markdown
# <task name> (<rev folder>): verifier.json fix

Input: <download name>, newest version <rev_N__ID>. Feedback: <source(s)>. Only tests/verifier.json changed
(validate_verifier.py: VERIFIER CHECK: PASS).

| # | Feedback (source) | Verdict | Verifiers | Change, or why none | Evidence |
|---|---|---|---|---|---|
| 1 | v14 rejects 12.3 million (review 355008, RL World item ...-2) | FIX | v14, v15 (sibling) | Accept any unit scale; band 12.25-12.35 m | instruction.md:12; golden Summary!C4 = 12,301,442 |
| 2 | ... | OUTSIDE VERIFIER.JSON | v25 | Golden memo omits the two required qualifications; the verifier is right. Needs a golden fix | solution/golden_outputs/memo.docx p.2 |

## Changes
<validate_verifier.py change list, then one line per changed verifier: old -> new behaviour, old -> new weight>

## Read-through checks
<per changed verifier: golden passes / solver run X now passes / empty fails / wrong answer fails / alternative
correct answer passes, with file>

## Validator warnings
<each WARNING line from validate_verifier.py, and what you did about it or why it stands>

## Not fixed here
<every OUTSIDE VERIFIER.JSON and CANNOT SETTLE item: the file, the change needed, who decides>

## Next step
Re-run the task (DataOS pipeline, or RL World's own run) on the fixed verifier.json; the read-through checks above are
not judge runs.
```

For an RL World upload, the person usually also wants one short remediation line per feedback item. Add a section
`## RL World remediation lines` with one line per feedback `id`: `<id>: FIXED in v14, v15 - accepts any unit scale.` or
`<id>: not a verifier defect - <reason>.`

Add `## Next-round list` whenever `NEXT_ROUND_LIST.md` or the sweep's WARN lines are not empty: the verifier, the
defect, and the fix held back because the feedback does not name it. The next feedback round starts from that list.

### 8. The zip RL World accepts ("Upload Updated Task")

Whoever uploads (the trainer, or the QC team's updated-task route), the file is `round<n>/trainer/<download
name>_verifierfix_upload.zip`, built by `trainer_upload.py` inside `build_round.py --feedback`. Never zip by hand,
never hand over the `fixed/` or `dataos/` copy. RL World refused ten different things in 2026-10/11
(`references/rlworld-refusals.md` has each message); the builder and `check` enforce all of them:

1. **Flat.** `instruction.md`, `task.toml`, `environment/`, `solution/`, `tests/` and `.external-qc-manifest.json`
   at the zip root. "Non-Harbor ZIP path: <folder>/instruction.md" otherwise.
2. **`task.toml` as RL World wrote it,** less only the trailing `[verifier.env]` table the platform appends to every
   download. A `[verifier.env]` that other tables follow is the task's own and stays ("immutable under the active
   External QC threshold policy" when it was deleted). Agent timeout stays as RL World has it; the DataOS copy's
   14400 is "beyond a fix".
3. **Built from the live RL World download,** never from a DataOS copy: only the download carries the export
   manifest, and the uploader refuses a zip without it ("Export manifest is missing"). Check the download's version
   first: a task can move on while a fix runs (vwr1nerq-2 went v14 to v16 during five rounds).
4. **Only feedback-named verifiers change.** "Named" = each item's "Criteria at risk" plus any verifier its
   remediation names; a verifier mentioned only as evidence is out of scope. A deleted named verifier's weight goes to
   the other named verifiers, so nothing else moves; weights sum to exactly 1 (the library refused 1.00000046).
5. **Every item is resolved by the upload itself.** When the remediation says "add it to instruction.md or delete the
   criterion", instruction.md cannot change, so delete the criterion or drop the demand in every wording. A softer
   wording that still demands the unasked thing ("any second-person control" for "a different reviewer") was refused
   as "Data inconsistent". A named criterion left unchanged is an unaddressed item: settle it in the report or fix it.
6. **The DataOS run grades the scoped file.** RL World pairs the feedback with the version's export: "DataOS review was
   run on a different package than this version's export: tests/verifier.json differs" otherwise. The DataOS copy in
   the round is built from the scoped `verifier.json` for that reason; a run of the full edit proves nothing about the
   upload.

The three checks, when run on their own:

```bash
python -X utf8 <skill>/scripts/trainer_upload.py build <RL World task_files> <fixed verifier.json or zip> <feedback.json> <out.zip>
python -X utf8 <skill>/scripts/trainer_upload.py check <out.zip> <RL World task_files> <feedback.json>    # UPLOAD CHECK: PASS
python -X utf8 <skill>/scripts/feedback_resolution_dump.py <RL World task_files> <out.zip> <feedback.json>   # read every item
```

## Things that look like fixes but are not

Deleting a verifier every solver failed, loosening until the empty answer passes, pasting the golden's numbers,
literal phrases, a third rewording, rewording an unasked requirement in softer words, wholesale `extract_many`,
judge-setup failures, golden layout pins: each is explained in `references/fix-patterns.md` section 5. Read it before
the first edit of a round.
