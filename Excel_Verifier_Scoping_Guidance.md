# Excel Verifier Scoping Guidance

## Purpose

Use this document as supplemental guidance when creating, reviewing, or
regenerating Excel/workbook verifiers. It complements the broader
Project Omega verifier standards; it is not a standalone workflow and
does not replace the requirements for grounding, atomicity, objectivity,
self-containment, independence, non-overlap, runtime observability, and
complete prompt coverage.

## Governing principle

Scope each verifier to the most specific evidence location that is
reasonably identifiable from the task and artifact.

For Excel workbooks, identify the relevant sheet and, where useful and
available, the applicable table, section, record, row, column, range,
cell, label, ID, or other stable locator. The appropriate locator will
vary by task and workbook.

The goal is to make it easy for the grader to know where to look and to
minimize unnecessary workbook-wide searching, while preserving
legitimate flexibility in how a compliant workbook may be structured.

Do not invent a locator, workbook structure, row position, table name,
or implementation requirement that the prompt or artifact does not
support.

## How to apply the principle

When writing or reviewing a workbook verifier:

1.  Identify the requirement the verifier owns.
2.  Determine where the evidence for that requirement can reasonably be
    expected to appear.
3.  Give the grader the narrowest useful and stable locator available.
4.  State the specific observable evidence that determines pass or fail.
5.  Avoid making the grader search unrelated portions of the workbook.
6.  Preserve legitimate solver flexibility. Specificity should help
    locate evidence, not impose an unrequested implementation.
7.  Keep ownership atomic and non-overlapping. A precise locator does
    not justify grading the same property in multiple verifiers.
8.  Scope only to evidence the declared grader can observe.

Specificity is contextual. A sheet name alone may be sufficient in one
workbook. Another verifier may reasonably identify a table, labeled
section, record ID, row, column, or range. Do not force every verifier
into the same locator format.

## Illustration only

If a required control is expected in a known record, a well-scoped
verifier **might** say:

> "On the Follow-up Controls sheet, verify row ECR-FU-008 includes a
> monitoring target, escalation threshold, status, and source/control
> link."

This is only an example of the scoping principle. It is **not** a
required verifier template. Other tasks may have no stable row ID, may
organize evidence differently, or may be better scoped using a table,
section, account, facility, entity, date, column, range, or another
locator.

The principle is the important part: direct the grader to the relevant
evidence as specifically as the task reasonably permits.

A weaker verifier, when a more precise location is available, would be:

> "Verify the workbook includes all required follow-up information."

That wording unnecessarily asks the grader to search the entire workbook
and provides less deterministic grading.

## Workbook-wide verifiers

Workbook-wide scope is appropriate when the requirement genuinely
applies to the workbook as a whole.

One or two workbook-wide verifiers may therefore be reasonable for
genuinely global requirements. There is no arbitrary permitted count;
the number should follow the actual obligations of the task.

Do not use workbook-wide wording merely because it is easier to draft.
If the evidence can reasonably be localized, scope the verifier
accordingly.

Conversely, do not manufacture artificial locations just to avoid
workbook-wide scope when the underlying requirement is genuinely global.

## Choosing a locator

Use the most useful locator supported by the task and artifact, not
mechanically the most granular possible address.

Prefer stable semantic locators over fragile coordinates when
appropriate. For example, a record ID or labeled section may be more
robust than a fixed row number if compliant workbooks can legitimately
reorder rows.

Cell or range references can be appropriate when the workbook structure
makes those locations stable and meaningful. They should not be required
simply because the deliverable is Excel.

A good locator should reduce the grader's search space without changing
the substantive requirement being graded.

## Prompt-design diagnostic

If most material workbook verifiers cannot be scoped beyond "somewhere
in the workbook," review `instruction.md` to determine why.

The problem may be at the **Prompt layer** if the prompt leaves the
required output, population, organization, or evidence so
underdetermined that materially different workbook structures are
equally compliant but cannot be graded fairly or consistently.

Use the following distinction:

-   If the prompt and artifact provide a reasonable evidence location
    but the verifier fails to name it, fix the **verifier**.
-   If flexible presentation is legitimate and the evidence can still be
    located through a stable semantic label, record, entity, or section,
    preserve that flexibility and scope the verifier semantically.
-   If deterministic grading is impossible because the prompt does not
    make the required evidence sufficiently discoverable, revise or
    reject the **prompt**.
-   Do not repair an underdetermined prompt by adding hidden structural
    requirements only in the verifier.
-   Do not over-prescribe workbook layout merely for grader convenience.
    Prompt structure should be added only when it reflects a genuine
    deliverable requirement or is necessary for fair, convergent
    grading.

## Relationship to other verifier standards

Scoping does not replace the normal verifier-quality tests.

A well-scoped verifier must still:

-   trace to a real prompt/source obligation or valid task-success
    condition;
-   test one clear owner concept;
-   define concrete pass/fail conditions;
-   cover silent omission where relevant;
-   be self-contained for its declared grader;
-   avoid overlap with other verifiers;
-   avoid invented business or presentation requirements;
-   rely only on evidence the grading runtime can observe; and
-   contribute to complete coverage of the material prompt obligations.

A verifier can have an excellent locator and still be defective because
it is vague, composite, overlapping, ungrounded, unfair, or
runtime-impossible.

## Defect routing

Route the issue to its origin rather than weakening downstream grading.

**Verifier defect:** A sufficiently specific evidence location is
available, but the verifier unnecessarily asks the grader to search
broadly.

**Fix:** Rewrite the verifier using the most useful supported locator
and concrete observable pass/fail evidence.

**Prompt defect:** The instruction leaves a material requirement so
underdetermined that the expected evidence cannot be located or graded
consistently.

**Fix:** Revise `instruction.md` so the necessary obligation is
discoverable and gradeable, or reject the prompt if the ambiguity is
material.

**Do not:** Invent workbook structure in the verifier that the solver
was never instructed to provide.

## Reviewer feedback

When the scoping issue warrants rejection, use the normal Project Omega
feedback structure:

**Location → Evidence → Implication → Exact Fix**

For example:

> **REJECT. Location:** Verifier `v12`, follow-up-control completeness.
> **Evidence:** The criterion asks the grader to search the workbook for
> all required follow-up information even though the expected evidence
> is localized on the `Follow-up Controls` sheet and can be identified
> more narrowly from the artifact. **Implication:** The grader must
> search unrelated workbook content, making the check less efficient and
> less deterministic than necessary. **Exact Fix:** Rewrite `v12` to
> identify the relevant sheet and the narrowest stable locator supported
> by this task, then state the specific observable evidence required for
> PASS; do not impose a row, range, or structure that the
> prompt/artifact does not support.

## Final review check

Before approving an Excel verifier set, confirm that:

-   verifiers are scoped as specifically as their individual
    requirements reasonably allow;
-   the grader is not repeatedly asked to search the entire workbook
    when narrower evidence locations are available;
-   workbook-wide checks correspond to genuinely workbook-wide
    obligations;
-   locators are useful and stable rather than artificially granular;
-   locator wording does not impose unrequested workbook structure;
-   each verifier remains grounded, atomic, objective, self-contained,
    independent, non-overlapping, anti-hack, and observable;
-   every material prompt obligation has an appropriate scoring owner;
    and
-   widespread inability to scope material verifiers has triggered a
    review of `instruction.md` rather than being silently accepted or
    patched through hidden verifier requirements.
