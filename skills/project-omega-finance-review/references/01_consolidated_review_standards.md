# Consolidated Review Standards

The review standard for each Project Omega gate. Failure patterns, the probe battery and pre-send checks are in `07_failure_patterns_and_lessons.md`; workbook scoping and extractor limits in `08_excel_verifier_scoping.md`; output forms in `06_output_templates.md`.

## 1. Reviewer operating principle

The reviewer protects benchmark integrity. The objective is not to maximize the number of issues or to make the task "better" by preference; it is to determine whether the task, evidence, output and scoring logic are materially correct, fair, executable and professionally realistic.

Materiality has an operational test. REJECT a verifier only with a one-sentence counterexample, "A submission that … would FAIL/PASS because …". It must show a realistic correct answer failing, a realistic wrong one passing, two competent graders splitting, or a misstated governing term. Without one, APPROVE and log any improvement as optional. Disclosed conventions that do not flip pass/fail, bounded alternatives and "accept X only if Y" guards pass. A model false-fail shows unfairness only when the requirement is not a reasonable reading of the prompt.

APPROVE only after the probe battery in 07 finds no counterexample. Run it every round on every verifier, Unchanged ones and your own wording included. Trainer Review fixes all findings in one pass; Final Review blocks only on its own grounds (§9). When challenged, re-test each item against the same bar; a changed verdict states "changed because <new evidence>".

Route each defect to the layer where it originates: broken inputs to Source Data, an unclear instruction to Prompt, a wrong computation to Artifact or Golden, and unfair, vague, duplicated or ungrounded grading to Verifier. Never weaken a verifier, or add an escape clause, to cover an upstream defect.

## 2. Five gates and the object being judged

- **Trainer Review** (task integrity). Is the task itself realistic, supported, coherent, executable and gradeable? Order: Task Design → each Source Data file → Prompt → Verifiers → LLM judge checks → Escalations. If defective: reject only the defective artifact; regenerate and re-review.
- **Model Output Review** (model quality). Did each attempt correctly perform the requested finance work from the supplied evidence? If defective: log every material issue by deliverable and severity.
- **Golden Data** (benchmark answer). Is the selected solution expert-grade, complete, traceable and internally consistent? If defective: fix the root cause and every downstream consequence.
- **Sample Calibration** (scoring quality). Do the verifiers grade real obligations fairly and consistently? If defective: grade blindly, then reconcile; flag bad verifiers or golden defects.
- **Final Review** (ship quality). Does the entire latest package survive an independent audit? If defective: block only on the §9 bar; everything else is an optional line.

Answer only the gate pasted, every field, in screen order. Verdict words: APPROVE/REJECT for artifacts and verifiers, AGREE/DISAGREE for LLM judge and Auto QC checks, TAKE/REJECT for each remediation item, PASS/FAIL for grades, PENDING INPUT where a needed file is missing, NOT VERIFIABLE where evidence cannot settle it.

At every gate, first match the upload to the pasted screen (task_id, revision, deliverable paths, verifier names); on a mismatch, stop and say so in the first line. Read every supplied file in full, including formulas, cached values, notes sheets, speaker notes and the verifier.json config; previews, filenames, links and judge summaries are not evidence. Mark each question needing a missing file PENDING INPUT, naming the file, with no provisional leaning.

## 3. Trainer Review — artifact standards

### 3.1 Task Design

- Scenario reflects work a real finance professional would plausibly perform.
- Task requires domain judgment and headroom rather than retrieval, rote formulas or ambiguous wording.
- Task is solvable entirely on a computer using the supplied materials.
- Planned anomalies are realistic and unlabeled; they do not give away the answer.
- Role, sector, occupation, deliverables, timing and decision context are mutually consistent.

Judge Task Design on its own content, never against verifier scope: it is written before the prompt, the sources and the verifiers. APPROVE when the scenario is realistic, deliverables have clear purposes, sources are mapped, and planned anomalies are realised in the sources and carried into instruction.md. Verifier scope beyond the plan is a Verifier matter, a prompt that prescribes a treatment the plan expected the solver to detect is a Prompt note, and a difficulty or effort-label mismatch is a metadata note; none is a Task Design REJECT.

### 3.2 Source Data

- Every referenced file exists, is on-topic, and looks like the natural genre of the underlying record.
- No source publishes the answer, expected output, exception flag, supported balance or close handling the solver is supposed to derive (leakage and labelling tests in V2 A).
- Shared IDs, entity names, dates, totals, units, currencies and period populations reconcile unless a mismatch is the intended anomaly.
- Source dates and events respect the stated cutoff; no event is silently pulled from after the measurement window.
- Source files carry no accidental duplicates, broken running balances, impossible values, invalid formulas without cached values, or missing rows required to solve the task.
- The task cannot be solved correctly from one file alone when cross-file reasoning is intended.

Give each source file its own APPROVE or REJECT, and answer each repeated judge check on that file's own evidence; cross-file means between files.

Planned-difficulty test, before calling any source condition a defect: read the cover and notes sheets and the prompt's caveats, test every plausible convention over all periods, and ask whether a graded figure moves. If the golden and models resolve it through the authority order, it is planned difficulty: an optional note at most. A break confined to the planted anomaly's row or period is the anomaly working.

A real source defect is a blocking note on the file that carries it, never only an escalation. Extraction banners and other pipeline items are escalations, not source defects.

### 3.3 Prompt

- The ask is verifiable from supplied sources alone and aligns with the task design.
- Two experts should converge on the material deliverable even if their presentation differs.
- Constraints that control the decision (source authority, cutoff, exclusions, no-invention rules, output formats) are explicit enough to prevent unfair grading.
- The prompt states what to determine, not a step-by-step method, unless the method itself is a business requirement.
- The strict output contract agrees with the narrative body and names every required deliverable and format.

### 3.4 Verifiers

Each verifier has one owner concept, explicit and grounded pass/fail anchors, and a fair bar, and can be judged from its declared output file within the runtime; together the set covers every material prompt obligation without grading any value twice on one artifact. The tests are in V2 C, and §1 governs every verdict.

## 4. Cross-file tie-out standard

- **Identity.** Compare entity, facility, account, invoice and instrument IDs and customer and vendor names. Typical failure: the same economic item carried twice because formatting differs; a missing master key.
- **Time.** Compare measurement date, effective date, approval timestamp, value date, cutoff and maturity. Typical failure: a new rate applied to an old period; a promise date treated as a usable cash date.
- **Amounts.** Compare detail-to-summary totals, balances, cash, debt, reserves, consideration and expenses. Typical failure: a summary that differs from its detail; a correct number used on the wrong basis.
- **Definitions.** Compare EBITDA, leverage, liquidity, NAV, earned premium, reserve, coverage and "available cash". Typical failure: a definition that changes mid-series while the trend is presented as comparable.
- **Units and currency.** Compare USD and local currency, thousands and full units, gross and net, par and carrying value. Typical failure: native currency carried into a USD field; gross notional treated as cash.
- **Status and approval.** Compare draft and approved, routed and committed, review and final authorization. Typical failure: downstream work advancing from a request that never became effective.

## 5. Recompute and cross-foot standard

- Rebuild the smallest independent chain that can prove or disprove each material output. Do not rely on the same formula cell the output uses.
- Tie totals in both directions when possible: detail → summary and summary → supporting population.
- Check displayed rounding separately from full-precision logic; rounded components should not falsely appear to reconcile when the underlying values do not.
- A material ratio must use the base its label claims. Confirm numerator, denominator, date and definition.
- When a result is sensitive to a legitimate unresolved interpretation, show a primary conclusion plus bounded sensitivity rather than hiding the uncertainty.
- When two figures or conventions compete, run each (and any third) over every period and keep the one that reproduces all stated values.
- Read workbook formulas and cached values; where recalculation is impossible, say that cached values were relied on.

## 6. Model Output Review issue axes

Reject or log an attempt on these axes:

- **Instruction-following:** the output answers a different question, ignores an explicit constraint, or omits a required deliverable or audience.
- **Correctness:** a fact, formula, tie-out, timing conclusion, authority call, classification or recommendation is materially wrong.
- **Completeness:** required analysis, decision support, risk, bridge, sensitivity, owner or action, source linkage, or section is missing.
- **Format and deliverable compliance:** required structure or file format is violated in a way that affects use or grading.
- **Hallucination and fabrication:** the output invents a source fact, approval, rule, number, event or citation.
- **Data integrity:** amounts are internally inconsistent, malformed, duplicated, stale, or cannot reconcile.
- **Coherence and integration:** workbook, memo and deck disagree, or the recommendation is not supported by the analysis.

Transferred lessons: log each issue as its own entry to the §11 note standard, with its severity where the form asks, keeping analytical root causes apart from presentation. The attempts are the realistic-submission test bed when judging verifier fairness (§1).

## 7. Golden Data quality standard

- Every carried-forward issue is resolved in the latest version, not just mentioned as fixed.
- Root-cause corrections flow through formulas, charts, tables, narrative and recommendation.
- The reasoning document (when required) contains step-by-step logic, labelled intermediate values and explicit source linkage.
- No required convention exists only in the reasoning; business deliverables stand on their own.
- The workbook contains auditable assumptions, checks and source traceability, with no hidden hard-coded answers where formulas are expected.
- Cross-deliverable figures, labels, recommendations, uncertainties and action timing agree.

Transferred lessons: APPROVE when the golden passes every verifier and its material figures recompute from source. Recompute key chains from the sources, not from golden cells. Where the golden and a verifier disagree, decide which is wrong first; a golden that passes a verifier you reject means the flaw is in grading other submissions, not in the golden.

## 8. Sample Calibration standard

- Blind grade first. Reveal the LLM judge only after the expert verdict is recorded.
- For every verifier: source of requirement, one concept, clear bar, sufficient grader evidence, criticality.
- Coverage gaps add checks only for real obligations. Redundancy removes duplicate ownership.
- If the golden fails a sound verifier, fix the golden; do not weaken the verifier.
- If a verifier is unfair, vague, overlapping or impossible under the runtime, flag it for regeneration with a Fix: note to the §11 standard.

Transferred lessons: decide which verifiers to flag with the probe battery (§1), and record the judge panel (config.models) in use, noting any judge-panel seat change.

## 9. Final Review standard

Use the latest files as the source of truth; old versions matter only as remediation history. Scrutinize every prior failed check and re-verify every claimed fix in the current files, then put each finding through the bar below. A fix that holds in substance but carries a stale figure is non-blocking.

A remaining material issue in any artifact is terminal for the current package, and a single verifier rejection ends the task, so "material" here means the bar. Set it once, before grading, and block only when:

- (a) the rubric misstates a governing term, which encodes a wrong rule in grading even if no submission has hit it yet;
- (b) a realistic submission is mis-graded, shown on a supplied output or on a concrete submission under an accepted reading;
- (c) the golden fails a sound verifier, once you have decided which side is wrong.

Do not reject for cosmetic or pipeline-only issues that do not impair correctness, usability, fairness or gradeability. Everything outside the bar gets an optional line: stale figures that change no result, hypothetical overlap or bundling, reasonable placement or format readings, extractor observability (NOT VERIFIABLE plus escalation), weight or difficulty labels, mechanical source slips, and planned difficulty. Overlap blocks only when a supplied or concretely constructed submission loses two verifiers for one defect.

Judge in this order:

1. Task Design, by §3.1 alone.
2. Source Documents, through the planned-difficulty test in §3.2.
3. Each verifier, against the bar.
4. Golden, by §7.

Give one short paragraph each for Task Design, Source Documents and Golden, then one line per verifier in screen order, notes under REJECTs only. Close with "Overall REJECT, because one verifier rejection ends the task: <names>." or "Overall APPROVE." If a REJECT rests on a branch no submission took, say so and keep it. Template F is in 06; the worked case is in 07.

## 10. Severity guide

- **Critical.** The core decision or answer is wrong, the task is unsolvable, source integrity is broken, or the final package cannot be trusted. Examples: a wrong authority changes borrowing capacity; a missing source makes a required conclusion impossible; the golden recommends the opposite action because of a bad calculation.
- **Major.** A material, localized error or omission that can be repaired without redesigning the task. Examples: one debt instrument double-counted; one required risk not addressed; memo and workbook disagree on an approval condition.
- **Minor.** The correct answer remains intact but quality, traceability or completeness is reduced. Examples: one stale reference, an isolated mislabeled figure, an incomplete locator.
- **Cosmetic.** No substantive effect on finance reasoning or scoring. Examples: a formatting inconsistency, a typo, raw floating-point residue hidden by a correct display format.

At Trainer Review a finding blocks when it meets the §1 counterexample test, misleads the judge, or plants a wrong fact that is being copied into new verifiers. Classify each fix once, with the same severity at every step; everything else goes once in the closing "Optional: …" line, and an optional item becomes blocking when it starts propagating.

## 11. Notes and pre-submit checklist

Every defect note (REJECT, DISAGREE, or AGREE with a FAIL) stands alone in one paragraph, two at most, about 120 words: Location and Evidence (quoted locator, cell, figure) → Implication, stated as the counterexample → Exact Fix, introduced by "Fix:" and naming the artifact or verifier ID, the locator and the exact change (what to delete, the replacement, which conflicting version to keep). A multi-item note gives the ID and change for each item; bullets only for three or more separate edits. A finding that belongs elsewhere reads "Fix: No change required to this file for this check; the fix belongs in <file>." APPROVE or a clean AGREE is one sentence of at most 30 words. No cross-references, paragraph counts or hedges; one definite instruction per item, and a rejected remediation item is marked as not to be adopted. The full output rules (C1–C9) are in SKILL.md.

Before submitting, confirm:

- Pack identity matches the pasted screen and every supplied file was read in full (§2).
- The task is inside the intended finance expertise.
- Material calculations, chronology, definitions, units, currencies and cross-file tie-outs were recomputed, not taken from the workbook or the judge (§4, §5).
- Every REJECT carries its counterexample, and every APPROVE followed a probe battery that found none (§1).
- Every judge verdict was re-run independently, each remediation item has its own TAKE or REJECT, and contradictory automated feedback is resolved or escalated.
- Verifier checks are objective, grounded, singly owned and executable (V2 C).
- Entries equal the form's fields in screen order, every FAIL has a note, tallies come from the entries, and no two notes conflict.
- No action item is left undecided.

## V2 Addendum — pre-flight standards

### A. Prompt and source-document pre-flight

- **Prompt construction.** Role, situation and work are stated as a genuine request. Workplace terminology is natural, and standard terms stay undefined unless the task gives them a specific meaning.
- **Scope and quantifiers.** Every graded time horizon, period count, population, entity subset, inclusion or exclusion rule, denominator, date or rate basis and exact convention is discoverable. Read one, each and every, and singular and plural, literally.
- **Ambiguity.** Professional ambiguity is allowed; ambiguity about deliverable, authority, population or exact convention is not. If two competent practitioners can choose differently and only one can pass, state the convention or admit both. Test convergence by computing the headline under each defensible reading (convention, scope, authority, date gate) beside the quoted verifier band or clause that accepts it; AGREE with a convergence PASS only if every reading lands inside the quoted band with the same decision, otherwise route the fix to the layer that creates the ambiguity.
- **Grounding.** Every section, clause, capitalised name and premise the prompt cites exists in the sources as cited. A trigger the prompt leaves undefined matches the sources' convention, names do not collide, and no rule excludes a source the task needs. Fix an unsourced premise by adding the dated source entry; otherwise align the prompt with existing source text, and never point a prompt at a clause not yet written. Clauses that only name a topic the solver must still work through, and strict-contract or output-path boilerplate, are not defects.
- **Deliverables.** Names, paths, extensions and audiences are consistent everywhere. No evaluation meta-commentary, and no hidden presentation structure that exists only in the golden. When Project Omega V5 creation rules govern, confirm at least 2 deliverable artifacts in approved formats.
- **Source set.** Cross-file joins are real and the scale feels professional. When Project Omega V5 creation rules govern, confirm 3+ source documents.
- **Leakage.** For each core verifier, search every source cell, formula cache, note, slide, speaker note and exhibit for its PASS values, exact and rounded, and its conclusions (transcription test). If a worker could copy a core verifier's graded conclusion from a source, REJECT that source and DISAGREE with its leakage PASS, with the Fix in that file's note: delete the conclusory text or pre-solved cells and keep the raw dated evidence. No source paraphrases the task decomposition, gives solver-facing recipes, or carries synthesis or advisor commentary that identifies the important items or the intended answer. Not leakage: a disclosed fact the solver must still apply or normalise, observed terms the task asks the solver to validate, and one-step arithmetic on a disclosed line where the graded skill remains.
- **Labelling.** Fails when text names the planted mechanism or reuses the anomaly plan's wording, even without amounts and especially when dated before the data that would reveal it, or when one sort, filter, position or round-number fingerprint isolates the planted rows. Fingerprint test: sort and filter every numeric and notes column, and check the top and bottom rows, distinct-value counts and appended blocks. Passes when finding the anomaly needs the intended join or test.
- **Realism.** Non-monotonic IDs, non-uniform and non-round values where appropriate, jittered timestamps, plausible anonymized names, natural disorder, no synthetic or generator boilerplate.
- **Consistency.** Summaries tie to detail, scales are correct, approvals follow underlying events, there are no future-period comparisons, accounting and physical constraints hold, and exact verifier anchors are derivable.
- **Round-one sweep.** On the first review, sweep every file and report everything in one round: a dated timeline in which each document cites only earlier events and every contractual date gate is tested against document dates; generator and meta wording and docProps, every hit listed so the whole class is cleared; exact round or back-solved values; intra-file invariants (prices within bid–ask, snapshot equal to the determination-date mark, Read Me claims, running balances); undeclared extra anomalies; and prompt premises with no dated source entry. Block when an issue changes a graded figure, flips a gate or authority, contradicts the anomaly design, or is meta-text that breaks the fiction or labels an anomaly; otherwise it is an optional note. When rows are regenerated, say whether graded or determination-date rows move and whether the golden needs recomputing.

### B. Golden pre-flight

- **Brief compliance.** All requested files are present, named, formatted and audience-correct; reasoning stays in the Expert Solution.
- **Internal consistency.** Narrative matches tables; displayed and rounded totals tie; percentage and ratio labels are correct; rates use matching bases; technical and accounting labels are accurate; causal claims are supported; every figure has a source or a shown derivation.
- **Presentation.** Stated, consistent precision; no raw floats, blank or working sheets, empty TOC or headings, placeholders or blank trailing pages. Validate alleged layout defects against the raw structure, because extractors can reorder content.

### C. Verifier pre-flight

- **Coverage.** Rebuild the map on every version, clause by clause from instruction.md and the strict output contract, and artifact by artifact. Every named field, threshold, table, deliverable element and each/every/all clause maps to the quoted PASS or FAIL phrase that asserts it; that phrase is the owner, and a background mention owns nothing. Each, every and all mean the complete population enumerated from source, and no N-of-M bar may make the sole owner of an obligation optional. A related metric does not own a different quantity. An obligation the contract places on one artifact is not covered by a verifier on another, and every declared anomaly has its own mandatory grading home, not a sub-condition of a composite. Cold-attempt failures may motivate checks only when the obligation is fair and discoverable.
- **Atomicity.** A rubric is atomic only if no output can meet one ANDed limb while failing another. Coupling test: for each AND in a PASS clause, write a one-line output that passes one limb and fails the other; if you can, split. Limbs are one construct only when one cannot be judged without the facts the other grades. Prompt grouping, contract stage grouping and a shared outcome are not coupling, and items the instruction enumerates separately are separate obligations. When splitting, keep each split's figures and IDs with the construct they evidence.
- **Ownership and overlap.** Gate each value in exactly one verifier per artifact. Others check only that it is documented, and say so inward: "This criterion assesses only X; ignore any error in Y when scoring it." Never write "graded elsewhere". A shared anchor is not overlap only when the second verifier does not gate that value's correctness; if one wrong value fails two verifiers on the same artifact, that is overlap. Different obligations sharing amounts, the same value graded in different artifacts, and a workbook-wide check that 08 allows are not overlap. Redundant and duplicative verifiers are a real defect; consolidation is as legitimate as splitting. Merge when two verifiers gate one value on one artifact, or when a downstream value follows mechanically from the upstream one. Otherwise anchor downstream verifiers to source-derived or correctly carried-forward figures; carry-forward credit goes to downstream reasoning only, and the upstream owner still fails the error. Before a merge or deletion, name each obligation's new owner, or repair in place. Each REJECT names repair, split, merge or delete.
- **Pass/fail wording.** PASS and FAIL are concrete, exhaustive and mirror each other: silent omission is covered, there is no "if present / where shown" loophole, and no advisory verb or unbounded qualitative term acts as a verdict gate. Where FAIL excuses an explained deviation, PASS accepts a justified derivation shown in the deliverable. Spot checks sit inside PASS. A negative-scope rubric needs a positive substance floor. Examples are clearly optional or clearly mandatory, and illustrations read "for illustration only, not a pass band".
- **Hack resistance.** Grade the cheapest fake (right labels, owner and deadline, no case facts) literally; if it passes, bind the rubric to a source-matched value or a case-specific identifier. Test the construct, not a proxy a non-compliant output could meet: a cell reference or identical stored value rather than cent equality, a stated evidential basis rather than "higher". Decline widening remedies that reopen known-wrong answers. When a shortcut lands on the same graded value as the full method, log a note; it blocks only when the shortcut is a known-wrong method the task is meant to catch.
- **Self-contained and runtime.** Inline every ID, list, value and tolerance the single-artifact judge needs; anchors in a rubric are not leakage. No cross-artifact dependencies, hidden metadata, invisible file-format properties, unreliable PowerPoint adjacency, or file-exists or format-only checks. Truncation never decides a verdict. Where a rubric depends on formula text, cached values or formatting, require a degradation clause and escalate the dependency as NOT VERIFIABLE (08).
- **Tolerance and methods.** Corner sweep: compute every anchor and band under every defensible convention, basis, weighting, ordering and rounding, and under every treatment the verifier set itself permits, escape clauses included; report the min–max corners against the band. Accept every defensible method or reading the materials support and keep known-wrong methods outside, enumerating accepted anchors rather than widening one band. Where the instruction leaves a choice, grade derivation, arithmetic and rationale, never a fixed number. No method requirement unless the prompt requires it.
- **Magnitude.** Every headline number has a floor and a ceiling computed from the golden across all defensible readings, even a wide one, so an absurd value (zero, ten times the golden) fails. Replace "about", "roughly" and "display rounding" with explicit tolerances, and grade a component that should sum to a stated total against that total.
- **Grounding.** Every PASS and FAIL condition traces to a sentence in instruction.md, a source obligation or a clearly implied task success condition; delete conditions with none, and invent no accounting, covenant, business or presentation rule. A restated governing term (threshold, ceiling, eligibility, exception, ranking, effective window) quotes the source clause with every condition, matching capitalised names and section numbers literally. For "FAIL if a different X is named", count the source rows that meet the same test; if more than one does, write "FAIL if <planted item> is not identified". Recompute every figure and factual phrase in the rubric text (preambles, illustrations, "roughly" figures, cross-references, weights) and embed only figures the decision needs.
- **Core and secondary.** Weight a verifier by the share of the task it carries: core for planned anomalies, headline figures and load-bearing correctness; secondary for presentation, supporting items and good-versus-great qualities. No planned anomaly is graded only by secondaries. Fix weighting by relabelling, never by deleting or folding verifiers, and avoid cascading weight from one upstream omission.
- **Your own fix wording.** Before returning changed wording, restate the host verifier's single construct (a clause that does not fit needs its own verifier), grep every verifier whose pass/fail could change, re-run touched bands at their corners, probe your own text, and attach a ripple list of the other places the fact appears, each with its replacement, or "no other occurrence (grep)". Give the change, not a full criterion, unless asked.

### D. Revision, approval and override hygiene

- On each later version, keep a version-delta ledger before judging: diff every file, verifier.json config and task_design.json included; mark each prior finding fixed, partially fixed or not fixed and check each fix as drafted; re-grade the prior fake; list dropped, renamed and weakened verifiers and conditions copied from rejected remediations; diff obligation → owner, not names. If nothing changed, say so first and re-issue the prior notes. Ledgers and probe logs are working notes, never output.
- After any source change, re-check every verifier preamble that quotes the changed file. After any scope or authority fix, recompute the headline under each defensible reading, and block if it flips.
- Classify remaining automated fails as substantive fix, policy or platform limitation, or stale result.
- Batch substantive fixes rather than resubmitting a half-fixed set.
- Recommend override only once substantive defects are clean and the remaining fail is demonstrably stale, incorrect or platform-level; name the affected verifiers and the evidence. Never use override merely because regeneration is frustrating.

## Source basis

The original standards come from the RL World Finance Expert Onboarding (v6), the RL World Platform Quick Reference and Platform Overview, the Project Omega Guide (V5), the Trainer Review Gate Convergence Report (production data through 23 Sep 2026), the Omega Pod finance and investment tracker and the uploaded RL World task folders. The counterexample and Final Review bars, the tests added to §3, §9 and the pre-flight rows, and the transferred lessons come from the September–October 2026 review sessions recorded in `07_failure_patterns_and_lessons.md`.
