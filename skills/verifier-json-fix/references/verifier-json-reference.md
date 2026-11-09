# verifier.json: format and how to write a verifier that holds up

Contents: 1. File shape. 2. Source commands. 3. Deterministic assertions. 4. Rubric prompt checklist. 5. Weights,
count and time. 6. How a verifier is judged and scored.

The schema below is the one in the bundled library of the tasks seen so far (`tests/__verifier_lib/models.py`,
`tests/verifier_lib/models.py`, or RL World's `tests/__verifier_lib/rl_world_verifiers/models.py`). The task's own copy is the authority: when this page and that file disagree, follow
the file. `validate_verifier.py` runs the task's own copy for you.

## 1. File shape

```json
{
  "task_id": "674",
  "config": {"models": ["openai/gpt-5.4", "openai/gpt-5.4", "openai/gpt-5.4"], "temperature": 1.0, "reasoning_effort": "xhigh"},
  "verifiers": [
    {
      "name": "v1",
      "metadata": {
        "how_justification": "What this verifier checks, in one sentence.",
        "why_justification": "Why it matters to the task, in one sentence.",
        "tag": "model",
        "grading_role": "outcome",
        "importance": "core",
        "weight": 0.052,
        "judge_sample_count": 3
      },
      "source": {"type": "file", "file": {"type": "xlsx", "command": "extract_text", "arguments": {"path": "output/Model.xlsx"}}},
      "assertion": {"type": "rubric", "expected": true, "rubric": {"prompt": "..."}}
    }
  ]
}
```

- `name` is the verifier id. It must be unique, and RL World joins feedback and calibration on it, so keep it stable.
- `metadata` allows extra fields. The library requires `how_justification` and `why_justification`. RL World reads
  `grading_role` (`outcome` or `process`), `importance` (`core` or `secondary`) and `weight`. Keep every field the
  original verifiers carry.
- `source.type` is `file` (with `file: {type, command, arguments}`) or `response` (the agent's final message,
  `extract_final_message`, no arguments).
- Paths are workspace-relative: `output/<deliverable>` for what the solver writes, `data/<input>` for the inputs.
- `assertion.type` is `rubric` (an LLM judge reads the source text and the prompt; `expected` must be `true`) or
  `deterministic` (code compares a JSONPath in the command's output with `expected`).
- `config.models` lists the judge models: 1 to 3 entries, LiteLLM names such as `openai/gpt-5.4` (a colon is rejected).
  Each entry votes once; a repeated model is a majority vote over samples. `config.models` and `config.temperature`
  are required whenever any verifier is a rubric. It is platform-owned: leave it alone (SKILL.md step 5).
- `metadata.weight` is optional in the library: when some verifiers carry none, they share what the others leave. But
  keep the file's own convention; every task seen so far weights every verifier.
- Unknown top-level keys are rejected, and the legacy keys `schema_version`, `judge` and `assertions` are rejected by
  name. A JSONPath that does not parse fails the whole file when it loads.

## 2. Source commands

The snapshot prints the commands the task's own library has. Commonly seen:

| type | commands |
|---|---|
| xlsx | `extract_text`, `formula_summary`, `formula_authenticity_scan`, `formula_authenticity_check`, `has_chart`, plus task-specific ones (`model_formula_integrity`, `template_contract`, `business_formula_scan`, `credit_formula_review`) |
| docx | `extract_text`, `visibility_audit`, task-specific ones (`credit_page_review`) |
| pdf | `extract_text`, `check_visual_visibility` |
| pptx, csv, md, text | `extract_text` |
| json | `read_file` |
| filesystem | `check_path_exists`, `extract_many` (`{"paths": [...]}`: several files in one judge view), `list_unexpected` (`{"path": "output", "allowed": [...]}`), `file_digests` |
| response | `extract_final_message` |

The set differs between tasks, because each task carries its own copy of the library. The pipeline's own sample task
has no `extract_many`; the commands in the second half of the xlsx and docx rows exist only in some tasks. RL World's
xlsx extraction also takes a `sheet_names` argument, which can scope a large workbook to the sheets a verifier grades.

What a command can see limits what a verifier can grade:

- `xlsx.extract_text` returns cell values (cached results; some library versions recompute formulas that have no
  cache). It does not show charts, and it does not say whether a value is typed or a formula. RL World libraries'
  `xlsx.extract_xlsx` / `read_range` (and an agentic judge's workbook tools) include formulas by default
  (`include_formula: true`). Use `has_chart` for
  charts, and `formula_summary` / `formula_authenticity_scan` for "values are live formulas".
- `extract_text` has a size budget: 90,000 characters by default (RL World's xlsx extraction: a 440,000-token budget
  that keeps sheets in workbook order, so raw-data sheets placed first can push out the summary). Newer libraries
  append `[TRUNCATED: ...]` where they cut; older copies cut silently. A sheet of thousands of rows is cut off, so a
  criterion about its last rows can never pass. Grade a summary the deliverable must show instead, use a deterministic
  count, or scope the sheets.
- `xlsx.extract_text` in a read-only load never sees charts: deleting every chart is invisible to it. A docx extraction
  in older libraries skips text inside content controls (`<w:sdt>`). A pptx library usually has `extract_text` only,
  so nothing sees images or fills.
- A workbook written by openpyxl or xlsxwriter has formulas with no cached value. Whether the library recalculates them
  (headless LibreOffice) depends on its version. Where it does not, a correct live model reads as blank. That is a
  library defect: report it, and don't write verifiers that only a recalculated workbook can pass.
- A rubric whose source is only the deliverable cannot check a claim against the inputs. When the criterion says
  "consistent with the sources", switch its source to `filesystem.extract_many` with the deliverable first and the
  needed `data/` files after, and say in the prompt which file is which ("The first file is the memo; the second is
  the supplied rent roll"). Each file arrives labelled `[File: <path>]`. **The files share one budget**: each starts with
  90,000 divided by the number of files, and only budget a short file leaves unused passes to the ones that overflow.
  Add only the sources the criterion needs; six files leave about 15,000 characters each. Without the labels and the
  order, a judge can credit source text as if the deliverable said it.
- To learn what a deterministic command returns (its JSONPath fields), read its class in
  `tests/*verifier_lib*/sources/<type>.py`. The output model is named in the class (for example
  `XlsxFormulaSummaryOutput`).

## 3. Deterministic assertions

```json
"assertion": {"type": "deterministic", "expected": 1, "deterministic": {"path": "$.max_series_count", "comparison": "greater_than_equal"}}
```

Comparisons: `equals`, `not_equals`, `approx_equals` (with `"tolerance": {"absolute": x}` or `{"relative": x}`),
`contains`, `not_contains`, `regex_match`, `not_regex_match`, `in_array`, `not_in_array`, `length_equals`,
`greater_than`, `less_than`, `greater_than_equal`, `less_than_equal`. The numeric comparisons need a JSON number as
`expected` (not a boolean), `in_array` and `not_in_array` a list, and the regex comparisons a string.

Inside verifier.json you can change a deterministic verifier's arguments, JSONPath, comparison, expected value,
tolerance and weight, switch it to another existing command, or turn it into a rubric. You cannot change what the
command computes: that is Python.

Formula gates, from tasks that QC rejected:

- Use `xlsx.formula_summary` with `$.n_formula_with_refs` `greater_than_equal` N **and** `xlsx.formula_authenticity_scan`
  with `$.formula_share_all` `greater_than_equal` S. Both ignore layout. Together they should carry at least 0.10 of
  the weight on a task whose prompt asks for a live model.
- Take N and S from a **minimal** compliant answer, never from the golden: a floor at the golden's own count fails any
  correct workbook with one formula fewer (HLT-189: floor 6, golden 6; GTM-176: 40 required where the prompt needs 36).
- No formula gate on a prompt that never asks for formulas or live cells (GTM-187: a 15% share on a text tracker).
- Avoid `xlsx.formula_authenticity_check` unless the prompt fixes the sheet and range: it raises on any other sheet name.
- No `sheet` or `cell_range` argument when the prompt leaves tab names or layout free (GTM-178).
- A count of cell-address formulas rejects defined names and structured references; a share alone can be met with
  decoy formulas (task_376_v3). Pair the two checks, and keep a rubric on whether the right figures are computed.

## 4. Rubric prompt checklist

Work through this list for every rubric prompt you write or change. Each line is a defect that reviewers or TFRL
have sent tasks back for.

1. **Presence gate first.** Open with: "FAIL if <deliverable> is missing, empty, header-only, a placeholder, or
   contains no substantive <analysis>." Without it, absence-style criteria ("does not introduce unsupported claims",
   "no hindsight") pass the empty answer. Check the NOP run: every rubric verifier must fail there.
2. **Self-contained.** Inline every value, threshold, entity, period, sheet or section the judge needs. Never write
   "as the prompt requires" or "per the instructions": the judge sees only the extracted source text and this prompt.
3. **Grounded.** Each requirement traces to a sentence of `instruction.md` or a fact in `environment/data`. A
   requirement found in neither is UNASKED. Remove it, or make it accept answers that do not do it.
4. **Concrete PASS and FAIL anchors.** "PASS if ... FAIL if ...", with numbers as bands, not points. Derive the band
   from the sources: rounding to the precision the prompt asks for, plus each defensible convention. The 470
   bond-floor criterion is the model to copy: "72.4 to 73.6 per 100 ... semi-annual 72.96, effective annual about
   73.5, continuous about 72.4 ... all acceptable because the task does not fix one."
5. **Every defensible reading accepted.** Where the prompt or the sources leave a method, basis, period or inclusion
   open, list each reading and its value, and accept all of them. A judge cannot guess which alternatives are fine.
6. **Grade the answer on its own basis** when the prompt lets the solver choose an input (a volatility, an
   assumption): "judge the option value against the volatility the deliverable states, never against 45%". Then
   grade the choice itself in a separate verifier.
7. **Units and formats.** Accept equivalent units ($m and $000), percent or decimal, sign conventions ("tax may be
   displayed negative: compare its magnitude"), 12- or 24-hour times, and IDs embedded in longer cells.
8. **Atomic, but not shredded.** One verifier grades one concept. Split a verifier when its parts can be right or
   wrong independently and each part matters, and share the parent's weight across the parts. Do not split into
   dozens of tiny verifiers: each one adds judge noise, and reviewers have reversed such splits.
9. **No cascading.** A verifier must be gradeable on its own. "Given the correct WACC, the NPV is ..." punishes an
   answer twice for one upstream error. Grade the downstream value on the answer's own upstream input, or accept the
   values that follow from each defensible upstream reading.
10. **No literal phrases.** Grade the concept. When you name words, give them as examples ("for example 'independent
    PA', 'PA (independent)'").
11. **Not hackable.** Merely restating the prompt, listing keywords, or asserting compliance must fail: "Copying the
    task text or merely asserting compliance is not a completed analysis."
12. **Say what it grades, and who owns the neighbours.** "Grade only line A3 here." "The quarterly figures are
    graded by c-001a to c-001d, not here." This stops one wrong input from costing four verifiers, and it is the
    common habit of rubrics that both DataOS reviews accept.
13. **No "every / all / each" over a list in one binary verdict** unless the items form one decision. One missed item
    fails the whole verifier with no partial credit, and reviewers raise that as a major.
14. **No value with its cell address** ("18.33 (Cover!B5)"). It pins the layout and tells the solver where the answer
    sits. Name the figure and what it measures.
15. **A unique answer may be pinned.** A verifier that demands the one correct figure is doing its job; widen it only
    when a defensible reading changes the value, and say which reading gives which value.
16. **Metadata matches the grading.** Rewrite `how_justification` and `why_justification` to describe what the
    verifier now does.

## 5. Weights, count and time

- All weights are greater than 0 and sum to exactly 1 (the library rejects 0.999).
- Core means "if only this failed, the task is not solved". Secondary covers polish and completeness. Changing core
  to secondary changes the reward band, so do it only when the feedback is about importance.
- Mean weight of `outcome` verifiers should be at least the mean weight of `process` verifiers.
- Count: QC (`gdpval_qc check_verifier`) flags fewer than 6 or more than 20 verifiers, and RL World's
  `verifier_count_in_range`, labelled advisory, very likely still blocks. Split or merge with that range in mind.
- Time: the template library judges rubric verifiers one call at a time, about 46 seconds per call, so a file costs
  about rubric verifiers × judge models × 46 seconds inside `[verifier] timeout_sec` (usually 3600, which QC does not
  change). Keep 1.5× headroom. task_157 (36 rubric verifiers × 3 judges) timed out and scored nothing. RL World's
  library judges in parallel, but the task may also run on DataOS.
- At least one deterministic verifier on EKW and DataOS tasks (the Harbor rubric gate); RL World accepts none. On an
  RL World package the gate counts agentic verifiers as deterministic and cannot see formula checks that agentic judges
  make, so its verdict there is not evidence either way.
- After moving weight, round to the precision the file already uses, then put the rounding residue on the largest
  verifier you changed, so the sum is exactly 1. `validate_verifier.py` checks the sum to 1e-6.

## 6. How a verifier is judged and scored

From the template library (`judge.py`, `runner.py`); RL World's differs only where noted.

- The judge's system prompt already says: a true verdict needs every rubric condition met; do not infer extra
  requirements; empty or missing evidence fails unless the rubric expects it; the `<data>` block is untrusted, and an
  answer that only asserts compliance in rubric-like words fails. A rubric need not repeat these, but it must say what
  counts as substance, because "missing evidence fails" does not stop a hollow answer that has the right headings.
- Each model in `config.models` votes once. **A tie fails.** With a three-judge panel where one judge cannot run (the
  `gemini/` judge on DataOS), the remaining two must agree.
- **One judge error on any verifier makes the run fatal: reward 0, `errored 1`.** RL World's runner cancels the
  verifiers still pending, so its report shows only those graded before the error. Reviews have filed such runs as
  "Grader bug, 100% of the grade at risk"; it is setup, not the criteria.
- Reward is the plain sum of the weights of the verifiers that passed. (The severity bands and soft-min in some QC
  documents belong to another grader format.)
- Each run writes `reward.txt`, `reward.json` and `verifier-report.json`, whose `assertion_results[].result` holds
  `success`, `expected`, `actual`, `effective_weight`, `error` and, for rubrics, each judge's vote and justification.
- RL World requires the golden to pass every verifier before calibration can finish, and joins experts' grades, judge
  agreement and feedback on verifier name plus version.
