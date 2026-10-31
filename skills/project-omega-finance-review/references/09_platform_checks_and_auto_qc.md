# Platform Checks, Auto QC and Forms

The pasted Description of each check defines what it tests. When it differs from a house test in SKILL.md, 01 or 07, answer that check by its own Description, and apply the house test only where the Description leaves room. Names and Descriptions change between packs, and two versions of the verifier checks are in use, so read the pasted text every round. Everything below was seen on the RL World screens between late September and late October 2026.

## 1. How the form works

Trainer Review sections show "LLM judge feedback — Respond to each automated check", with "The LLM judge marked this check PASSED/FAILED. Do you agree? Agree / Disagree" under each check. They also show a "File artifact feedback" field: "Approve or reject this source file" per source file, "Approve or reject the task's instructions and contract" for Task Design, and "Approve or reject the model prompt" for instruction.md. A Reject asks for "Reason — sent back for rework · required".

- A judge check takes Agree/Disagree plus a comment. Source edits go in that file's File artifact feedback reason, prompt edits in the prompt artifact, verifier edits in each verifier's note. Head every note with the field it goes in, and flag edits that must land together.
- A file can be REJECTed while every judge check on it is AGREE. Never flip a judge check to back a file REJECT.
- A DISAGREE with a FAIL opens a mandatory "Reviewer note*" field: give a standalone note for that file (why the FAIL is wrong, any earlier-version evidence, and which remediation must not be adopted).
- On a rework the previous answer is pre-filled ("LLM Judgment: Pass / Your Judgment: Fail"). Re-decide each one from the new evidence.
- Rework uploads may carry a "Changes in this version / Changes for rework feedback … Why:" changelog. Check each claim against your own diff. Regeneration often rewrites far beyond the requested edits (whole verifier sets, prompt paragraphs, moved sheets), so say which changes were requested and which were not.
- Trainer overrides do not carry across versions. A check can pass content "consistent with the trainer override" in one version and fail it in the next; re-issue the same DISAGREE, quoting the earlier pass.
- Verifier cards show the name, Description (metadata.how_justification), Source (extract_xlsx or extract_text plus the output path), Criterion, "Why this matters" (metadata.why_justification; in newer packs it opens "Grades O<n>: <obligation>") and "Your verdict on this verifier: Approve / Reject". A judge explanation that says "N checked this round, M unchanged since an earlier pass" has carried a PASS forward on the unchanged verifiers.
- Final Review warns "Rejecting any artifact ends the task — the rejection is terminal". The user has confirmed that this holds for Task Design, the sources, the prompt and the golden, while a verifier REJECT sends the verifier back for repair; tasks with verifier REJECTs at Final Review (CUS, IDC, MKT, OPR, NLR) went on to External QC. The judge checks are display-only there, shown beside a named reviewer's earlier judgment and a count ("5 passed"). The fields to answer are "Confirm … is ship-ready. Do you approve this artifact? Approve / Reject" for Task Design, each source, the prompt, each verifier ("a rejection ends the task") and each golden deliverable. Platform reviewers at that gate see the golden only; model outputs in the zip are not on their screen.
- verifier.json config runs three judge models at temperature 1. Each run re-reads and samples the package, so new findings appear every round and a PASS on sampled content proves nothing about the rest.
- Stage-close surveys ("Select all the primary bottleneck(s) causing delays in this stage") want ticks plus one line each.
- Model Output Review runs one screen per model per output file plus one Additional Feedback screen per model (two models and two files make six screens). File screens ask "List issues per axis for this output file" over six required axes; Additional Feedback has five fields and says "Issues with a single file belong in that file's feedback." Severity is Critical or Nice to have only. The golden step that follows pre-loads each issue under "Fix reported issues" for "Fixed in new golden", then asks for "Additional Issues" in one or two sentences each (06 C and D).
- Sample Calibration unlocks one verifier at a time. Per verifier: your PASS/FAIL per attempt against the LLM judge (three judges, majority wins), every disagreement resolved by agreeing with the judge or standing by your grade with a reason, then five required questions, then Coverage gaps and Redundant verifiers. After regeneration the set shows NEW, CHANGED, REMOVED and GRADE CHANGED labels (06 E).
- External QC follows Final Review: "Rework pending — review QC feedback. Review each item, then submit your verdict." Each finding card carries a category, "Review <id> · finding <n> · <x>% of the grade at risk", the reviewer type, "Why a correct answer fails", a Remediation and Agree/Disagree buttons; only verifier.json changes are in scope (10).

## 2. Check catalogue

### Task Design

- Scenario realism: plausible for the sector and occupation, including cognitive load and domain fit.
- Task requires expert judgment: multi-step domain reasoning, not lookup or reformatting.
- Plan does not require external lookup: no live prices, current filings or real legal citations that synthetic inputs cannot supply.
- Task can be completed entirely on a computer.
- Deliverable descriptions are contract-safe: no figure, finding, planted-item identity, input file, path or format, because the host copies these descriptions verbatim into the solver's STRICT CONTRACT.

### Source Data (per file; five checks in older packs, eight in newer)

- Synthetic data realism. Fails on [TIE], [SYNTHETIC], [AI-GENERATED] or [OMEGA] markers, and in newer packs on any accounting, legal, clinical or regulatory treatment that contradicts the governing standard and is not a declared anomaly. Seen failing: generator properties (pypdf, ReportLab, python-pptx, "Steve Canny", 2013 dates, 1 page and 0 words), static or constant balances ("fabrication tells"), hash-like IDs, uniform lifecycles (every PO open, one child per parent, constant date gaps, weekend dates), wrong market conventions (bid OAS below ask OAS), and a standards breach relabelled as entity policy.
- Input files do not contain literal expected output values (internal id input_file_anti_leak_scan): owns leaked answers, labelled final answers and deliverable-ready conclusions.
- Source data does not restate the assignment (internal id source_data_not_assignment): fails commissioning text naming the deliverables, horizon or deadline, question lists, agendas, recommendations, and policy or procedure text that prescribes the requested computation ("analytical recipes": the rate, valuation date, discount basis, day count, step order or rejected alternative). It keeps historical evidence, eligibility rules, thresholds, approval rights and dated records. Answers belong to the anti-leak check.
- Cross-file referential consistency: five kinds (same fact at the same as-of date, keys resolving in their master, records following stated rules, shared population, no event after the cutoff). "Report only the file that is actually wrong." The judge excludes only anomalies declared in the anomaly plan; any other source error fails.
- Each input file is on-topic for the task.
- Anomalies are not trivially labeled in the data: no markers, highlighted rows or comments that reveal the location without expert judgment.
- Each planted anomaly has exactly one defensible resolution, under standard practice or a one-sentence business rule.
- Source documents render cleanly: clipping, overlap, broken images, blank pages, chart faults, placeholder looks or visible markers. The judge's own LibreOffice conversion sometimes fails; render the file yourself.

The judge stamps one explanation on every file. Answer each file on its own evidence.

### Prompt (instruction.md)

- Instruction claims verifiable from prior artifacts: checked against environment/data and the Step 1–3 outputs, so task_design.json grounds named people and roles.
- Prompt aligns with Harbor task.toml (some packs): use the task_toml block inside task_design.json when no task.toml file exists.
- Two professionals would converge on the same deliverable: a stated rule for every planted conflict and a fixed as-of date.
- Instruction body reads like real workplace delegation; carries no AI assistant self-voice ("human first-person delegation voice is expected and never flagged").
- Task is completable from instruction and inputs alone; final instruction stays computer-completable; role and deliverable identity are stated.
- Source data does not contain the prompt's answer: "when one does, the fix is to rewrite the prompt so the source data is no longer a leak for it".
- Input files do not reproduce the assignment or its solution: verbatim or near-verbatim copying into the prompt.
- Instruction has a feasible path to the required deliverable: "Task difficulty or a model's failure alone is not evidence of infeasibility."

Output-path and strict-contract boilerplate, including "The output/ folder is the only location the downstream … check inspects", is template text, not a defect.

### Verifiers, ledger version (newer packs)

- Verifiers anchored to required artifacts: each targets a path, field, value or behaviour instruction.md names or implies, and its source command can extract the evidence.
- Rubrics let competent graders agree on a concrete deliverable: "a fail needs the counterexample showing the disagreement"; a vague qualifier is a defect only when it creates a disagreement nothing bounds.
- Verifier criteria do not double-grade one obligation: "Two verifiers must not grade the same ledger obligation and the same facts on the same artifact … Verifiers serving different obligations are never overlap."
- Verifier rubrics are independently gradeable: no dependence on another verifier's pass/fail.
- Verifier coverage audit of the obligation ledger: audits tests/verifier-plan.md; fixes read "add a verifier for O#" or "map O# to <existing verifier>".
- Verifier rubrics test the named concept: no proxy, and no demand for wording, labels, structure or one reading the instruction leaves open; a fail names an expert answer that meets the instruction but fails the rubric.
- Rubric criterion is self-contained for the judge: the judge sees only the deliverable and the criterion text, so every value, list, entity and convention is inlined. It fails a rubric that names another verifier, and one that accepts "other supported choices" without the inputs a grader needs to check them.
- Verifier rubrics test one ledger obligation: "A rubric is composite only when its parts serve different ledger obligations, and the split must name the obligation the removed part needs."
- Rubric anchors and tolerances match the source data: "Sole owner of values, tolerances, and accepted alternatives", decided "with a data-location counterexample". Raise tolerance and anchor disputes here, not under convergence or overlap.

### Verifiers, older version

Verifier robustness review (reads verifier-plan.md and a "step_4 summary"); Verifier set follows rubric-first policy ("accepting zero deterministic verifiers"); Verifiers anchored to required artifacts; Expected artifacts have verifier coverage; Verifier criteria are non-overlapping ("Pairs of rubric verifiers must not grade substantively the same concept. Overlap double-penalizes a single failure"); Verifier rubrics are independently gradeable; Verifier coverage of instruction obligations; Verifier rubrics test the named concept; Verifier rubrics resist keyword-only hacking; Verifier rubrics are specific enough for judges to converge; Rubric criterion is self-contained for the judge; Verifier rubrics test one atomic concept ("Composite rubrics that chain multiple disjoint properties with AND must be split"); At least one verifier grades outcome/substance. Under this version the value-level overlap and coupling tests in SKILL.md apply.

## 3. tests/verifier-plan.md and the Obligation Ledger

The plan lists numbered obligations (O#), the construct each verifier grades, "Expected Values and Anchors" (where "professional alternatives are retained"), and cross-artifact rules. Judges cite it, and Auto QC's scope-conformance check fails any requested change that reverses a design it documents.

- Ask for the file whenever verifiers or verifier-level judge checks are on screen. Until it arrives, build the O# map from the "Grades O#" lines and from instruction.md sentence by sentence, and say which basis you used.
- Without the plan, mark any split, merge, deletion, narrowing of an accepted alternative or count-driven request PENDING INPUT, naming the file.
- When the plan documents several limbs as one construct, do not ask for a split: DISAGREE with the atomicity FAIL, quote the plan, and fix thresholds inside the verifier. The plan, not a rubric's own opening sentence, sets the construct boundary.

## 4. Auto QC on your notes

Auto QC grades the reviewer's submission, not the task. Each run can test a different dimension, and retries are limited (10 at Trainer Review, 3–5 at Final Review). Before the first submission, run every note against every check below.

Trainer Review:

- Trainer feedback — note factual groundedness. Every claim and locator is checked against verifier.json, instruction.md and the sources. Seen failing: a wrong paragraph number, a loose population ("2019 to 2025" when the batch ran to 2026), IDs with no file location (read as "fabricated"), and an overbroad claim ("The instruction names no tabs" when it numbers eight).
- Trainer feedback — note actionability. The regenerator acts on the note alone, so there is no "below" or "above", the replacement text is written out, every item names its verifier ID, and conflicting versions say which to keep.
- Trainer feedback — requested-change scope conformance. A requested change must not reverse a design documented in verifier.json or tests/verifier-plan.md, and must be applicable on the platform schema.
- Feedback coverage completeness: every field needs a note; resend the full form when several partial updates are outstanding.
- Source Data Disagree notes are checked against the judge's offender list. A note claiming the judge named nothing in this file, or that a named item "is not a defect", fails as a false claim ("the judge's offenders list explicitly named all three files for 'Machine-style filename'"). Name the offender the judge cited, then argue scope or evidence.
- A section locks once passed, yet Auto QC can fail its notes later. The edit path is Content → the section → the file → LLM judge feedback → Reviewer note; a locked section needs an unlock or override from the lead or platform support. Never paste source notes into verifier fields.

Model Output Review:

- Severity Calibrated: each issue's label is graded against its own wording, one failure per run. Seen failing as under-calls ("overstated by $0.37", "Eastfield at +$180,000 instead of a $120,000 loss", a problems table that "is a missing deliverable", inputs not "kept apart from calculations" where the prompt requires a live model) and as an over-call ("pure formatting nitpick that leaves the output usable as-is"). Recheck every entry of the same kind before resubmitting.

Final Review:

- Final review feedback – cross-item consistency: two notes whose requirements cannot both be met fail. Enumerated readings in one note must obey the rules another note sets for the same item. A malformed explanation ("result.json … does not contain the final-gate feedback record"), or a FAIL in which every pair scores severity 0, is a checker fault: resubmit once unchanged, then escalate for an override; never flip verdicts to Approve to get past it. Cross-item consistency also reads approve comments: keep them to evidence with no blocking words, put a set-level coverage gap only in the set-level and overall comments, and make every repeated figure identical and every written sum add up.
- Final review feedback – note groundedness: verbatim quotes with page, cell or clause; no cross-reference to a rule that exists only in your own proposed fix; no claims about outputs you have not opened. Every figure is checked against the golden's cells, so a counterexample figure must never read as the golden's own (a note read as claiming the golden shows $31,456,580 when Margin Bridge H88 holds $31,505,038.28 failed as a "load-bearing false claim").
- Final review feedback – actionability (Severity 2–3 per note): quote the exact current sentence and its replacement; a fix that removes a branch also states the complete positive PASS test; where a rubric must choose among several figures, give a strict precedence ("the pair labelled headline; where none, the first pair stated"); a population fix gives the count, its source breakdown and one test applied to every row.
- Final review feedback – coverage completeness: an independent re-review minus your notes. If it names a defect that does not exist, keep the verdict and put a short rebuttal with figures and locators on that artifact's entry.
- Final review feedback – decision/note coherence: open each REJECT note with the defect ("This verifier is not ship-ready because it would grade a correct … as FAIL"); an opener such as "This verifier fails a correct response" or a line like "the PASS test is unchanged" reads as approval and fails as a polarity inversion. A note that bundles corrections for several points fails as "vacuous"; give one fix per note. A REJECT not tied to a quoted task requirement or computation is "vacuous". A requirement-beyond-the-prompt REJECT quotes the governing instruction clause, shows the item is absent from the anomaly plan, and names the supplied output or fully described submission it mis-grades; a PASS condition the prompt never asks for is never a judgment call, and anything you would still call one is an Optional line.

On rework, rewrite the flagged notes and any other field whose answer would now contradict them, naming each and why. When QC forces withdrawal of one element of a REJECT, withdraw only that element and keep its other fixes. After any verdict change, tell the user to change the platform button and delete the superseded note, because QC reads the form, not the chat.

## 5. verifier.json facts for implementable remedies

- Top level: task_id, config (models, temperature, reasoning_effort) and verifiers.
- Each verifier: name; metadata (how_justification, why_justification, importance core or secondary); source.file (type xlsx, docx, pptx or pdf; command extract_xlsx or extract_text; arguments path and, for workbooks, optionally include_value); assertion (type rubric, expected true, rubric.prompt).
- One source file per verifier, so no cross-artifact rubric. Rubric-first: no file-exists, path, string-match, ROUND-function or truncation checks.
- Judges report that include_value defaults to false and that extraction can truncate on a token budget; whether formula text reaches the grader is unconfirmed (08).
- Set size is never a reason to merge, drop or split. If QC says a remedy cannot be applied, change the remedy and keep the verdict.

## 6. Engineering and process write-ups

When the user asks for a note to the engineering team or a survey answer: generic pattern, not task detail, unless asked; the general fix first, then what went wrong with version labels (v2, rework), then one sentence on why it matters; plain words with one example; "very brief" means one line per item.
