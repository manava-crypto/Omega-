# Excel Verifier Scoping

Read this before writing, reviewing or regenerating any workbook verifier. It supplements the verifier standards in `01_consolidated_review_standards.md` and the probe battery in `07_failure_patterns_and_lessons.md`; it replaces none of the normal verifier-quality tests. Task keys (LHF, ACL, CRW, REI) are defined in 07.

## Governing principle

Scope each verifier to the most specific evidence location reasonably identifiable from the task and the artifact. The user's standard (REI): verifiers are "scoped as specifically as possible … identify the sheet name and, when possible, the specific row, column, table, range, or record". The aim is to tell the grader where to look and spare it a workbook-wide search, while preserving legitimate flexibility in how a compliant workbook is built. Never invent a locator, workbook structure, row position, table name or implementation requirement that the prompt or artifact does not support.

When writing or reviewing a workbook verifier:

1. Identify the requirement the verifier owns.
2. Decide where its evidence can reasonably be expected to appear.
3. Give the grader the narrowest useful, stable locator available.
4. State the observable evidence that decides PASS or FAIL.
5. Keep the grader out of unrelated parts of the workbook.
6. Preserve solver flexibility: the locator helps find evidence; it never imposes an unrequested implementation.
7. Keep ownership atomic and non-overlapping; a precise locator never justifies grading one property in two verifiers.
8. Scope only to evidence the declared grader can observe.

Specificity is contextual: a sheet name may be enough for one verifier, a table, labelled section, record ID, row, column or range for another. Do not force one locator format on every verifier.

## Choosing a locator

Use the most useful locator the task and artifact support, not mechanically the most granular address. Prefer stable semantic locators (a record ID, labelled section, entity, account, facility or date) over fragile coordinates where compliant workbooks may legitimately reorder rows. Cell or range references fit only where the structure makes them stable and meaningful, never merely because the deliverable is Excel. A good locator narrows the search without changing the requirement being graded.

Illustration only: if a required control is expected in a known record and instruction.md names the tab, a well-scoped verifier might say "On the Follow-up Controls sheet, verify row ECR-FU-008 includes a monitoring target, escalation threshold, status, and source/control link." This is not a template; other tasks have no stable row ID or are better scoped another way. Where that precise location exists, the weaker wording "Verify the workbook includes all required follow-up information" sends the grader through the whole workbook and grades less deterministically.

## Sheet names and tab schedules

Name a sheet only when instruction.md names that tab (ACL). Otherwise use a semantic locator; an invented tab name is a hidden structural requirement. Where you do name a sheet, add to the criterion: "If no tab carries that label, grade the sheet that plainly presents [X]; do not fail on tab naming" (REI).

Propose sheet-scoped extraction on the same condition, the user's "if the prompt mentions them", and only as an engineering escalation, because whether the extractor accepts a sheet argument is unconfirmed. ACL's instruction.md named no tabs, so the request was declined on that evidence and the extraction limit escalated. Strengthen tooling rather than weaken a rubric, but only where the prompt supports it.

When you add a tab schedule to instruction.md so verifiers can be scoped:

- keep it minimal, and allow prefixes, suffixes, continuation sheets and extra sheets;
- never grade tab labels: they are format-only, and a test met by labels alone fails keyword hacking (ACL's tab-order rubric);
- say in the note that each scheduled tab's content is covered by the verifiers scoped to it, not by a tab-presence check;
- expect coverage judges to keep demanding a tab-presence verifier, and DISAGREE each time with the same note quoting the schedule's paragraph, logged as a rejected demand (REI, four rounds).

A tab sequence that instruction.md itself requires still needs an owner (ACL failed a coverage check when its tab-layout verifier was dropped), and that owner tests the content each step must carry, not the labels.

Model note, written only after confirming every scheduled tab's content has a scoped owner:

> Verifier coverage of instruction obligations — DISAGREE. The remedy asks for a verifier that the workbook carries the scheduled tabs, but instruction.md says "Prefixes or suffixes on those labels are fine, as are continuation sheets and any extra sheets you find useful", so the labels are presentation and each scheduled tab's content is already graded by the verifiers scoped to it. Fix: REJECT the remediation; add no tab-presence or tab-label verifier.

## Workbook-wide verifiers

Workbook-wide scope is right when the requirement genuinely applies to the whole workbook. In the user's words, "One or two workbook-wide verifiers may be okay if the requirement truly applies to the entire workbook"; the task's genuinely global obligations decide how many. A workbook-wide formula check can be one of them (LHF V21 was withdrawn from the Final Review rejects on this basis). A workbook-wide check that grades only the global property, and not any value's correctness, does not overlap the verifiers that own those values. If it depends on formula text, it carries the degradation clause. Do not use workbook-wide wording because it is easier to draft when the evidence can be localised, and do not manufacture artificial locations when the requirement is genuinely global.

## Extractor observability

Whether extract_xlsx returns formula strings, cached values or formatting, with or without include_value, and when it truncates, is unconfirmed; never assume either way.

- Wherever a rubric depends on formula text, cached values or formatting, require a degradation clause such as "if the extraction does not expose formula strings, judge on the anchored outputs alone", and mark the dependency NOT VERIFIABLE with a one-line engineering escalation. At Trainer Review a dependent limb without the clause fails the probe battery, because a correct workbook fails whenever the extraction hides that property: REJECT with the clause as the Fix (CRW: wb_scenario_controls_live's FAIL limb needed formula strings, and the clause, carried as a non-blocking fix, went unapplied for five rounds). At Final Review it is never a REJECT: LHF's workbook verifiers grading text and formulas, and V22's legend clause, which needs formatting, were marked NOT VERIFIABLE and escalated.
- Never presume how the extractor represents a formula, as in "cells that contain formulas show a formula field (text beginning with '=')" (REI).
- Never grade a property the extraction cannot show, such as Excel Table objects or named ranges; grade the anchored values and labels it does show, and keep any formula-liveness condition only with the degradation clause (V-06; `05_real_feedback_examples.md` example 7).
- Truncation never decides a verdict. CRW's v1 deterministic `$.truncated equals false` core check failed a perfect workbook whenever the extractor truncated; delete such a condition and replace it with no file-exists, filename or format check (V-08, CF-02).
- Diff the extractor arguments in verifier.json on every version: CRW's regeneration dropped include_value from the source args.
- A source workbook whose formulas carry no cached values extracts as blanks. At Trainer Review that is SD-07 on the source when it hides a needed figure (05 example 1); at Final Review, a minor optional note (LHF Activity Register summary block).

The accepted escalation form (ACL):

> ESCALATE TO: engineering | ISSUE: possible extractor truncation or dropped cached values on full-workbook extraction | EVIDENCE: the 38-loan and carry-forward rubrics need every loan and stored values visible | WHY THE FORM CANNOT RESOLVE IT: instruction.md fixes no tab names, so neither rubric can be sheet-scoped without an unstated requirement | RECOMMENDED ACTION: raise the extraction size limit and include cached values for these two verifiers.

## Population ranges are not truncation

A verifier that reads a fixed or incomplete business-data range and misses records has a real defect (CF-03): fix the range or population logic so the rubric covers the complete source population, which each, every and all always mean. Truncation is a pipeline event that goes to an escalation; a short range is a verifier defect with its own note. State the population in rubric text: inline the authoritative ID set and FAIL any omission or spurious ID, with no path, string or count check (CF-05; 05 example 12). When the full population may exceed what the extractor returns, keep it whole in the rubric and escalate the extraction limit; never shrink the population to fit the extractor.

## Prompt-design diagnostic and routing

If most material workbook verifiers cannot be scoped beyond "somewhere in the workbook", read instruction.md to find out why. In the user's words: "If the prompt is written in a way that makes most verifiers impossible to scope, that may mean the prompt (instruction.md) itself needs to be revised or rejected." Route the issue to its origin rather than weakening downstream grading:

- The prompt and artifact give a reasonable evidence location but the verifier does not name it: a Verifier defect. Fix: rewrite it with the most useful supported locator and concrete observable PASS/FAIL evidence.
- Flexible presentation is legitimate and the evidence can be found through a stable semantic label, record, entity or section: keep the flexibility and scope semantically.
- The prompt leaves the required output, population, organisation or evidence so underdetermined that materially different workbooks are equally compliant but cannot be graded fairly or consistently: a Prompt defect. Fix: revise instruction.md so the obligation is discoverable and gradeable, or REJECT the prompt if the ambiguity is material.
- Never repair an underdetermined prompt with verifier-only structure the solver was never told to provide.
- Never over-prescribe layout for grader convenience; add prompt structure only when it is a genuine deliverable requirement or necessary for fair, convergent grading, and then follow the tab-schedule rules in this file.

## Scoping verdicts and notes

REJECT for scope only with a counterexample: two competent graders would split, a wrong workbook passes on content found elsewhere, or a correct workbook fails on a locator that imposes structure the prompt never asked for (05 example 6). Without one, APPROVE with the narrower locator as an optional line; at Final Review, scope that changes no grade is always optional. Model note (illustrative):

> v12 — REJECT. The criterion reads "Verify the workbook includes all required follow-up information", although instruction.md names the Follow-up Controls tab and the artifact records the control as row ECR-FU-008. A workbook that mentions a monitoring target only in a free-text notes tab, with row ECR-FU-008 incomplete, would PASS with one grader and FAIL with another. Fix: replace that sentence with "On the Follow-up Controls sheet, verify row ECR-FU-008 includes a monitoring target, escalation threshold, status, and source/control link; if no tab carries that label, grade the sheet that plainly presents the follow-up controls; do not fail on tab naming", add to FAIL "or any of the four items is missing", and impose no row position or range.

## Final check on a workbook verifier set

Before approving, confirm that:

- each verifier is scoped as specifically as its requirement reasonably allows, and the grader is not repeatedly sent through the whole workbook when narrower locations exist;
- workbook-wide checks match genuinely workbook-wide obligations;
- locators are useful and stable rather than artificially granular, and impose no unrequested structure;
- sheet names appear only where instruction.md names the tab, with the fallback sentence; no tab label is graded; degradation clauses stand wherever extraction visibility matters; nothing fails on truncation; every population range is complete;
- each verifier still traces to a real prompt or source obligation, tests one owner concept, has concrete PASS/FAIL conditions covering silent omission, is self-contained for its declared grader, overlaps no other verifier, invents no business or presentation requirement, is hack-resistant and relies only on evidence the runtime can observe; an excellent locator does not rescue a vague, composite, overlapping, ungrounded, unfair or runtime-impossible verifier;
- every material prompt obligation has a scoring owner;
- widespread inability to scope material verifiers has triggered a review of instruction.md, not silent acceptance or hidden verifier requirements.
