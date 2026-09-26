Output Templates

Copy-ready structures for every Project Omega review stage

Project Omega | Finance & Insurance reviewer knowledge pack | 25 Sep 2026

A. Universal rejection / disagreement note

One note = one repair. The note must name the target and be executable by a regenerator without needing to infer which item you meant. For LLM-judge remediation, explicitly say TAKE or REJECT and why.

B. TRAINER REVIEW GATE — REVIEW TEMPLATE

ROLE

You are the Quality Authority for an RL World benchmark task in [SECTOR / OCCUPATION]. You review and capture issues. You do not rebuild artifacts. Your judgment overrides the LLM judge in both directions. Your notes are the ONLY instruction the agent gets when it regenerates.

INPUTS I AM GIVING YOU

Task pack (prompt/instruction.md, source files, tests/verifier.json, model outputs if present)

The LLM judge checks and their PASS/FAIL verdicts, verbatim

Task metadata: sector, occupation, scenario

HOW TO WORK

Read every source file in full. Do not sample-read. Recompute material figures.

Review in order: Task Design → Source Data → Prompt → Verifiers. Later artifacts depend on earlier ones.

Dependency rule: a foundational defect is flagged on its source artifact. Never patch it by rewriting a verifier.

Tag every factual claim [Certain] (verified in a file), [Likely] (strong inference), or [Guessing]. State which file and cell/page/section supports it.

Approve what is sound. Reject only actual defects.

NOTE-WRITING RULES (every rejection and every Disagree)

Format: LOCATION → EVIDENCE → IMPLICATION → EXACT FIX.

Name the target. Never write “request the names” or “unactionable without more detail.” Identify the offenders yourself from the artifacts.

One note = one fix a regenerator can apply without reading anything else.

CONTRADICTION CHECK: no two notes may give incompatible instructions for the same artifact, clause or value. Before output, list every requirement you asked to move, split or delete, and confirm it is assigned to exactly ONE owner and deleted everywhere else.

If two automated checks demand opposite things, do not absorb the conflict. Take one, reject the other with the reason, and flag it for escalation.

OUTPUT FORMAT

1. GATE SUMMARY

Two or three lines: the single most important finding, and whether the task is fundamentally sound enough to proceed.

2. TASK DESIGN

Artifact verdict: APPROVE / REJECT + note.

3. SOURCE DATA — one block per file

For each file: realism · no literal expected outputs · cross-file consistency · on-topic · anomalies not labeled. One short paragraph per check, verdict + evidence.

Artifact verdict per file: APPROVE / REJECT + note listing each required change.

Then: CROSS-FILE TIE-OUTS — table of every shared value, ID, date and total, which files carry it, and whether it agrees. Flag any mismatch that is NOT a planned anomaly.

4. PROMPT

Checks: solvable from sources alone · aligned with task design · two experts converge · reads like a real workplace request · constraints stated · deliverables and formats named. Artifact verdict: APPROVE / REJECT + note.

5. VERIFIERS

5a. OWNERSHIP MAP — build this BEFORE judging any verifier.

Every headline number, every control, every citation rule, every gate.

5b. VERDICT TABLE — one row per verifier: name | core/secondary | APPROVE / REJECT.

5c. REJECTION NOTES — one per rejected verifier, in the note format above. Say whether the fix is: split a composite, delete a requirement another verifier owns, add a missing anchor, or widen an over-prescribed implementation.

5d. COVERAGE GAPS — obligations in the prompt with no verifier. Name the obligation and the verifier to add, including a side-effect check for unrequested files/tabs/claims.

5e. SET-LEVEL FLAGS — count, core/secondary balance, anything unbuildable under the DSL (single source path per verifier; no cross-artifact rubrics).

6. LLM JUDGE CHECKS

Answer every check. For each remediation item the check proposes, say TAKE or REJECT and why. Reject any item that contradicts another check’s requirement, and name that check.

7. ESCALATIONS

Anything the form cannot resolve: contradictory automated checks, DSL limits, unclear priority. One line each, addressed to the pod lead or engineering.

BEFORE YOU OUTPUT — SELF-CHECK

Does every rejection name a target and a direction?

Does any note contradict another? (Run the ownership map.)

Did I flag foundational defects on the source artifact, not the rubric?

Did I verify numbers myself rather than trusting a polished file?

Is anything marked [Guessing] that I should have checked in a file?

C. Model Output Review template

D. Golden Data fix log template

E. SAMPLE CALIBRATION STAGE — COMPLETE OUTPUT TEMPLATE

Purpose: grade each model attempt against each verifier, reconcile with the LLM judge, calibrate the verifier itself, identify coverage/overlap, repair the golden if needed, and prepare a clean handoff to Final Review.

SECTION A: Attempt-by-Attempt Verifier Grading

For each attempt (1, 2, 3…), grade every verifier PASS or FAIL. State the verdict, then cite the specific evidence from the attempt that supports it.

Attempt [N] — Verifier: [verifier_id]

My Verdict: PASS / FAIL

LLM Judge Verdict: PASS / FAIL (shown after expert submits)

Agreement: AGREE / DISAGREE

Evidence: Quote or describe the specific cell, paragraph, or slide content that drove the verdict. If FAIL, state exactly what is wrong and what the correct value/element should be.

If Disagreement: Explain why the LLM is wrong, or acknowledge the LLM is right and update your verdict.

Repeat for each verifier and each attempt.

SECTION B: Verifier Calibration Questions

For each verifier, answer all five calibration questions. These determine whether the verifier itself is sound.

Verifier: [verifier_id]

1. Where is this requirement sourced?

Explicitly required by the prompt — quote the relevant snippet

Explicitly required by the source data — name which file(s)

Implicitly required to do this work well — explain why

Not required anywhere — unfair to verify — explain why

2. Does this check test just one thing?

Yes, one thing

No, several things — describe what should be split

3. Is it clear what should pass and what should fail?

Yes, the bar is clear

No, it’s vague — explain the ambiguity

4. Does the grader have everything it needs to judge this?

Yes, it has what it needs

No, it’s missing information — explain what’s missing

5. What happens if an answer fails this check?

Critical — the answer is wrong without it — explain why

Nice to have — improves an already-correct answer — explain why

Repeat for each verifier.

SECTION C: Coverage Gaps

For each gap, specify what is missing and propose a new verifier.

Gap [N]: [short title]

Target artifact: [workbook / memo / deck]

What should be verified: [explicit pass/fail conditions]

Where this gap is coming from: [explicitly required by prompt / source data / implicitly required]

What happens if an answer fails: [critical / nice to have — explain]

If no gaps: state “No coverage gaps identified.”

SECTION D: Redundant Verifiers

Overlap [N]

Verifiers involved: [verifier_id_1, verifier_id_2, ...]

What they redundantly check: [describe the overlap]

Recommendation: [keep both as complementary / merge / drop one — explain why]

If no overlaps: state “No redundant verifiers identified.”

SECTION E: Golden Data Fixes

After all verifiers are reviewed, fix the golden data if any verifier failures revealed golden defects.

Fix [N]: [verifier_id that failed on the golden]

What was wrong: [specific description of the defect]

What was changed: [specific description of the fix — file, location, old value → new value]

File affected: [workbook / memo / deck / reasoning]

If no golden fixes needed: state “Golden data passes all verifiers — no fixes required.”

SECTION F: Verifiers Flagged for Regeneration

Verifier: [verifier_id]

Reason for flag: [vague / overlapping / unfair / coverage gap / runtime impossible]

Feedback for regeneration: [specific guidance on what the regenerated verifier should test]

If none: state “No verifiers flagged for regeneration.”

SECTION G: Final Golden Consistency Check

2.1 Compliance with the brief

Every requested deliverable present, correctly named, in required format, addressed to stated audience

Expert Solution folder contains only the solution and its reasoning file

Reasoning file complete: step-by-step logic, intermediate values with clear labels, explicit source linkage

No required convention exists only in the reasoning file

Every figure and claim has been checked by hand

2.2 Internal consistency

Narrative matches tables (every superlative, comparative, percentage checked against numbers)

Claims consistent across all deliverables (workbook ↔ memo ↔ deck)

Every displayed total equals the sum of its displayed parts

Rounded displays still sum to their stated total

Every stated percentage or ratio is the quantity its label claims

Rates applied to the matching base

Every labelled technical or accounting term actually is that term

Causal claims supported

Consistent treatment of what the record does and does not disclose

Every figure traces to a source document or to a derivation shown in the reasoning file

2.3 Presentation

Figures rounded to a stated, consistent precision — no raw unrounded floats

No empty TOC, unpopulated headings, or placeholder text

No stray default-named, blank, or working worksheets

No blank trailing pages

Tables, headings, and sections in professional order

If any item fails: fix and document under Section E.

SECTION H: Summary Output for Downstream (Final Review)

Total verifiers: [N]

Verifiers passed by golden: [N]

Verifiers failed by golden (now fixed): [N]

Verifiers flagged for regeneration: [N]

Coverage gaps added: [N]

Redundant verifiers identified: [N]

Golden consistency check: PASS / FAIL (with details if FAIL)

Key decisions made during calibration: [brief list of any non-obvious grading or calibration choices]

F. Final Review template

G. Escalation template

ESCALATE TO: [pod lead / engineering] | ISSUE: [contradictory automated checks / DSL limit / conversion bug / unclear priority] | EVIDENCE: [specific check + artifact] | WHY THE FORM CANNOT RESOLVE IT: [one sentence] | RECOMMENDED RULE / ACTION: [one sentence].

Source basis used to build this document

User-provided Trainer Review Gate review template.

User-provided Sample Calibration Stage complete output template.

RL_World_Finance_Expert_Onboarding_v6 and RL World Platform Quick Reference Cheat Sheet.

Project_Omega_Guide_V5 and Trainer_Review_Gate_Convergence_Report.

V2 — Platform-Ready Starter Mode

Trainer Review — added platform questions/checks

Trainer Review — remediation decision block

Verifier rejection — replacement-text block

Use this when the platform expects pasteable replacement wording, not just diagnosis:

Model Output Review — form-ready block

For each attempt and each deliverable, answer every platform axis: instruction-following, correctness, completeness, format/deliverable compliance, hallucination/fabrication, data integrity.

Then add cross-file coherence and overall attempt assessment.

Every issue includes severity + location + evidence + implication + exact fix + impacted artifacts.

Sample Calibration — added calibration checks

For each verifier, also check: accepted alternatives/tolerance; silent omission; exhaustive PASS/FAIL; runtime observability; hidden conventions; one-owner overlap; whether a flipping judge needs a sharper anchor rather than a wider band.

Distinguish pipeline extraction truncation from a real incomplete source/data range.

When the golden fails, decide first whether the golden or verifier is wrong; fix only the defective side.

Carry forward a short round log for non-obvious verifier changes/overrides.

Final Review — added golden consistency checks

Recheck prompt quantifiers/conventions against latest golden and verifiers.

Recheck narrative superlatives/percentages against tables; cross-deliverable values; rounded totals; ratio labels; rate/base matching; technical terminology; causal claims; source/derivation traceability.

Treat green QC as evidence, not authority.

Missing-input behavior

If the task pack lacks an item needed only for one section (for example LLM judge verdicts), write “PENDING INPUT — [item]” for that section and complete every independent section. Ask a clarifying question only when the missing item prevents any meaningful review.


[Table 1]

FORMAT  LOCATION → EVIDENCE → IMPLICATION → EXACT FIX.


[Table 2]

Check | LLM | Mine | Note if disagree

Scenario realism |  |  | 

Requires expert judgment (headroom) |  |  | 

No external lookup |  |  | 

Completable on a computer |  |  | 

Anomalies planned but not labeled |  |  | 


[Table 3]

Requirement / value / control | Owning verifier | Also appears in (must be deleted)

 |  | 


[Table 4]

Check | LLM verdict | Mine | Reviewer note

 |  |  | 


[Table 5]

Section | Required output

Attempt summary | Overall approach, decision/conclusion, strongest aspect, most material defect.

Per deliverable | File name; Instruction-following; Correctness; Completeness; Deliverable/format compliance; Hallucination/fabrication; Data integrity. State “No issues” where clean.

Issue log | Issue ID | severity | axis | artifact/location | evidence | implication | exact fix | other artifacts impacted.

Additional / cross-file feedback | Any disagreement across workbook/memo/deck/reasoning and the authoritative value/action.

Overall assessment | Did the attempt actually answer the ask? Are conclusions sound? Do all outputs cohere as one solution?


[Table 6]

Field | Template

Issue ID / severity | [carried-forward issue]

Root cause | [source/output logic that caused the defect]

What was changed | [file + location + old state → new state]

Downstream propagation | [other calculations, analysis, charts, tables, recommendations and narrative updated]

Independent verification | [recomputation / cross-foot / authority check]

Regression check | [what was re-read to confirm the repair did not break anything else]

Status | FIXED / NOT FIXED / ESCALATE


[Table 7]

Section | What to record

Package summary | Task ID, domain, latest artifact versions, prior material issues reviewed.

Task Design | APPROVE / REJECT + material reason only.

Source Data | APPROVE / REJECT per source; unresolved cross-file mismatch / chronology / leaked answer.

Prompt | APPROVE / REJECT; solvability, authority, output contract.

Golden | APPROVE / REJECT per deliverable; correctness, completeness, cross-deliverable tie.

Verifiers | APPROVE / REJECT set; fairness, coverage, ownership, runtime executability.

QC reconciliation | For prior failures: verified fixed / false positive / still open.

Final verdict | APPROVE only if no material issue remains; otherwise REJECT and name the blocking artifact.


[Table 8]

DEFAULT BEHAVIOR  When the user invokes a stage starter, fill the relevant template completely from the uploaded task pack. Do not return a generic review essay.


[Table 9]

Artifact | Additional checks to answer explicitly

Task Design | Realistic expert work; genuine headroom; computer-only; no external lookup; anomaly fair/unlabeled; role/occupation/scenario coherent.

Source Data | File-set completeness; cross-file dependency; single-file solvability; leakage beyond literal answers; realism/scale/genre; IDs/names/dates/totals/units/currency/population/chronology; exact anchors derivable.

Prompt | Role/situation/work; what-not-how; authority/conflict rules; scope/quantifiers; exact conventions; ambiguity; deliverable names/paths/formats/audiences; no prompt-vs-rubric punishment.

Verifiers | Ownership map; coverage map; atomicity; objective/exhaustive PASS/FAIL; self-contained; runtime-visible; non-overlap; accepted-method/tolerance fairness; core/secondary; side effects; no count-only remediation.


[Table 10]

Automated remediation item | Decision | Reason / conflict | Platform-ready action

[paste judge item] | TAKE / REJECT | [evidence + any conflicting check] | [exact change or override/escalation text]


[Table 11]

Field | Platform-ready text

Verifier | [vN / name]

Verdict | REJECT

Reason | LOCATION → EVIDENCE → IMPLICATION → EXACT FIX

Replacement criterion | [full self-contained PASS/FAIL criterion; end with a boolean-verdict instruction if the live schema expects it]

Description / how | [pasteable replacement]

Why | [pasteable replacement]

Importance / weight | [only if a change is needed]
