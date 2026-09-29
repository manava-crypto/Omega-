---
description: Write and review Excel/workbook verifiers so the grader is
  directed to the narrowest observable location that contains the
  required evidence. Use when creating, reviewing, or regenerating
  spreadsheet verifiers for Project Omega / RL World tasks.
name: excel-verifier-scoping
---

# Excel Verifier Scoping

## Purpose

Make Excel verifiers easy, fair, and efficient to grade by telling the
grader exactly where to look in the workbook. A verifier should be
scoped to the narrowest stable workbook location that can prove or
disprove the requirement.

This skill supplements the normal verifier standards. It does **not**
override requirements for grounding, atomicity, objectivity,
self-containment, independence, non-overlap, runtime observability, or
complete prompt coverage.

## Core rule

For each Excel verifier, identify the evidence location as specifically
as the task and workbook design reasonably allow.

Prefer, in descending order of specificity:

1.  Sheet + record/ID + field(s)
2.  Sheet + table + record/ID + field(s)
3.  Sheet + row + column(s)
4.  Sheet + cell/range
5.  Sheet + named section/table
6.  Sheet only
7.  Workbook-wide only when the requirement genuinely applies to the
    workbook as a whole

Do not ask the grader to search the entire workbook when the evidence is
expected in a known sheet, table, row, range, or record.

## Good pattern

> On the `Follow-up Controls` sheet, verify row `ECR-FU-008` includes a
> monitoring target, escalation threshold, status, and source/control
> link.

This gives the grader: - the artifact location; - the record to
inspect; - the fields/evidence to evaluate; and - a concrete pass/fail
target.

## Weak pattern

> Verify the workbook includes all required follow-up information.

This is too broad when the expected evidence has a known location. It
forces a workbook-wide search and makes grading less deterministic.

## Scoping procedure

When drafting or reviewing each workbook verifier:

1.  **Identify the owning requirement.** Trace the verifier to an
    explicit prompt/source obligation or a clearly valid task-success
    condition.
2.  **Identify the expected evidence location.** Determine where a
    compliant solver would reasonably place the evidence under the
    prompt/output contract.
3.  **Use the narrowest stable locator.** Name the sheet and, where
    possible, the row, column, table, range, record ID,
    account/facility/entity ID, or labeled section.
4.  **State the observable evidence.** Say exactly what values, fields,
    relationships, or controls must be present/correct.
5.  **Define pass/fail concretely.** Cover omission as well as incorrect
    content. Inline authoritative anchors when needed for a
    self-contained single-file grader.
6.  **Check ownership.** Do not make multiple verifiers grade the same
    property merely because they reference the same row or range.
7.  **Check runtime visibility.** Scope only to evidence the declared
    workbook grader can actually observe. Do not require invisible
    formula objects, Excel Table objects, named ranges, or other
    implementation mechanics unless the grading runtime can inspect
    them.

## Locator examples

Use whichever locator is most stable for the workbook.

**Record-based** \> On `Debt Detail`, for facility ID `TL-B`, verify the
included principal, cash-interest rate, and debt-classification fields
use the authoritative basis required by the task.

**Range-based** \> On `Liquidity Bridge`, verify cells `B12:B18` contain
the seven required bridge categories and `H12:H18` reconcile once each
into the ending liquidity total.

**Table-based** \> In the `Exceptions` table on `Close Review`, verify
the record for journal ID `JE-1047` shows the required
inclusion/exclusion decision and supporting source reference.

**Column-based population** \> On `Selected Population`, verify column
`A` contains exactly the authoritative selected IDs and no additional
IDs.

**Section-based** \> On `Executive Summary`, in the `Key Risks` section,
verify the required risk and corresponding mitigation/action are stated.

Use exact cell addresses only when they are stable and genuinely part of
the expected workbook structure. Prefer semantic locators such as record
IDs and labeled sections when row positions may legitimately vary.

## Workbook-wide verifiers

One or two workbook-wide verifiers may be appropriate when the
requirement truly applies globally, for example: - no unrequested output
sheets; - consistent units/precision across all required output tabs; -
a workbook-wide prohibition or convention explicitly imposed by the
prompt.

Do not create many workbook-wide verifiers as a substitute for locating
evidence. If a requirement can be checked on a specific sheet or record,
scope it there.

## Prompt-design diagnostic

If most required workbook verifiers cannot be scoped more narrowly than
"somewhere in the workbook," inspect `instruction.md` before weakening
the verifiers.

This may indicate a **Prompt-layer defect** when the prompt does not
define the required deliverable structure, population, output location,
or evidence sufficiently for two competent solvers to produce gradeable
work.

Apply this rule:

-   If the business requirement permits flexible presentation but the
    substantive evidence can still be located by a stable label/record,
    keep the prompt flexible and scope the verifier semantically.
-   If the verifier is unscoped only because its author failed to
    inspect the expected workbook structure, fix the verifier.
-   If the prompt makes deterministic grading impossible because
    required evidence could appear anywhere or in materially different
    forms, revise or reject the prompt rather than inventing structure
    in the verifier.
-   Do **not** over-prescribe workbook layout merely to make grading
    convenient. Add prompt structure only when it is a genuine
    deliverable requirement or is necessary for fair, convergent
    grading.

## Review standard

Treat excessive unscoped workbook verifiers as a verifier-set quality
problem unless the root cause is the prompt.

A sound Excel verifier should normally answer all of these questions
without making the grader search:

-   **Which sheet?**
-   **Which record, row, column, table, range, or labeled section, when
    available?**
-   **What exact evidence is being checked?**
-   **What passes?**
-   **What fails?**
-   **Is this property owned by this verifier only?**
-   **Can the declared grader actually observe it?**

## Defect routing

Route the defect to its origin.

**Verifier defect:** The workbook/prompt provides a stable evidence
location, but the verifier says only "verify the workbook includes..."\
**Fix:** Rewrite the verifier with the narrowest available locator and
concrete pass/fail evidence.

**Prompt defect:** The instruction does not establish enough of the
required output/population/structure to make material requirements
fairly and consistently gradeable.\
**Fix:** Revise `instruction.md` to make the necessary requirement
discoverable and gradeable, or reject the prompt if the ambiguity is
material.

**Do not:** Patch an underdetermined prompt by making the verifier
impose a hidden workbook structure the solver was never required to
follow.

## Reviewer feedback format

When rejecting a verifier or prompt, use one natural paragraph
containing:

**Location → Evidence → Implication → Exact Fix**

Example:

> **REJECT. Location:** Verifier `v12`, follow-up-control completeness.
> **Evidence:** The criterion asks the grader to verify that the
> workbook contains all required follow-up information, but the required
> records are expected on the `Follow-up Controls` sheet and are keyed
> by ECR follow-up ID. **Implication:** The grader must search the full
> workbook and the pass/fail path is less deterministic than necessary.
> **Exact Fix:** Rewrite `v12` to name the `Follow-up Controls` sheet
> and the applicable record ID(s), and specify the required fields to
> inspect for each record; retain workbook-wide scope only for any
> requirement that genuinely applies globally.

## Final self-check

Before approving an Excel verifier set, confirm:

-   Most workbook verifiers are scoped below the workbook level.
-   Every verifier uses the narrowest reasonable stable locator.
-   Workbook-wide checks are few and justified by genuinely global
    requirements.
-   Locators do not impose unrequested implementation details.
-   Each criterion remains atomic, grounded, objective, self-contained,
    independent, non-overlapping, anti-hack, and observable from its
    declared artifact.
-   Every material prompt obligation still has exactly one scoring
    owner.
-   If broad scoping is unavoidable for many criteria, `instruction.md`
    has been reviewed for an underdetermined or ungradeable output
    contract.
