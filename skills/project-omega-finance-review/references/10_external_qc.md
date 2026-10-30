# External QC (XQC)

External QC is the stage immediately after the Final Review Gate (FRG) and the last check before the task goes to TFRL. Nothing downstream catches an error made here, so every verdict goes through the multi-pass review in §4 before it is sent. Sources: "SOP: External QC (XQC) Workflow for Trainers — RL World" (30 Oct 2026, draft for review) and the External QC rounds in review sessions from 20 to 30 Oct 2026 (task key in §6).

## 1. Workflow

One rule governs the stage: only verifier (JSON) changes are in scope. The prompt, the source packet and the golden are not edited at XQC.

- **FRG approval.** Approving at FRG moves the task to External QC with status QC Pending. Before approving, confirm the prompt, source packet, golden and verifier JSON are all final; anything already known to be wrong is fixed before FRG, not surfaced as rework.
- **QC Pending (with XQC).** The QC team runs the task through the Data OS pipeline and uploads its findings into the task. The reviewer takes no action and does not edit the task. When the upload lands, the status flips to Rework Pending.
- **Rework Pending (with the reviewer).** The only stage where the reviewer decides. Read every finding against the source packet, the golden and the current verifier JSON, and record agree (true positive) or disagree (false positive) on each one. Two questions, in order, settle the path:
  1. Did I agree with anything? If every finding is disagreed, with a stated reason each, the task is approved as it stands and goes to TFRL: no fix request, no tracker row.
  2. Is every agreed finding a verifier finding? Verifier findings are JSON-only fixes and stay in scope. An agreed finding against the prompt, source packet or golden rejects the task; golden issues are handled by cloning the task and re-authoring it.
- **Fix request.** For agreed verifier findings, add one row per task to the EKW QC Fix Request tracker and post in ekw-ots-team-qc that a row is waiting. The reviewer fills five columns and nothing else: Trainer Name (the task claimant, not the pod lead), Email (the reviewer's Turing address, where the revised file comes back), Task ID (the full ID exactly as RL World shows it), RL-World Task Link (direct link including the version segment, e.g. /v12) and Additional Comments (the fix request itself). QC fills Claimed By, Task Status (In Progress, then Fixed), Comment from QC and Final Status (QC Approved). The QC engineer has not read the task, so everything they need is in the Additional Comments cell.
- **Upload the revised file.** QC revises the verifier JSON and returns it by DM. The reviewer opens the task in RL World, goes to the Content tab, uploads the revised file, then sets "Updated on RL World" (Column I) to Yes. That last step is not optional: QC will not run the final review until Column I reads Yes. The upload returns the task to the verdict step; RL World re-checks it and the reviewer gives fresh verdicts on whatever comes back. Nothing left to agree with means approval; new or unresolved findings mean new verdicts and, if needed, a new tracker row.
- **Approved, then TFRL.** Not yet defined in the SOP.

A task can pass through Rework Pending several times. Only two exits leave the loop: approval, or rejection on a non-verifier finding.

## 2. What a finding looks like

The screen opens "Rework pending — review QC feedback. Review each item, then submit your verdict. If any items are true positives, upload a corrected package before submitting." The verifier file under review is attached as "verifier (NN).json". Each finding card shows:

- tags: a category ("Several valid readings", "Conflicting requirement", "Unasked requirement", "Wrong golden answer", "Weak grader", "Grader bug"; some cards carry none) plus "Blocking issue" and "Needs Review";
- the header "Review <id> · finding <n> · <x>% of the grade at risk · <criterion or k criteria>";
- the reviewer: CLAUDE-CODE, which cites real solver runs (codex, terminus, oracle), or QC-MANAGER-READ, which reads the files only and tags its remediation "(Apply only after the domain expert agrees.)";
- Criteria at risk with weights, bullets for Prompt, Criterion, Source and runs, "Why a correct answer fails", "Remediation" (often a verifier fix or a prompt fix), the target file (verifier.json, sometimes also task.toml, instruction.md or a golden file) and Agree / Disagree buttons.

The same defect usually arrives in several cards from different reviews. Some cards bundle several criteria. QC's own warnings ("The quoted words were not found in that file; check them first.") are claims to check, not findings.

## 3. Deciding true positive or false positive

**True positive (Agree).** The finding names a defect that is present in the current verifier.json and needs a change: the answer it describes under "Why a correct answer fails" really is correct under the prompt and the sources, and it really fails the criterion as written (or a wrong answer really passes) for the reason the finding gives.

**False positive (Disagree).** The finding's own complaint does not hold: the answer it calls correct leaves out or contradicts something the prompt asks for; the criterion does not say what the finding quotes; the sources or golden settle the point the finding calls open; or the failure is a grader or infrastructure fault that no verifier.json change cures (judge authentication errors, ties failing pessimistically, a judge whose reasoning says met but scores 0, timeouts, extraction size limits, a document-import deadlock, a sandbox clock later than the scenario date). A grader fault is a Disagree with "No change needed to verifier.json; the fix belongs in the grading infrastructure" and an escalation line (template G). No change needed means false positive.

Rules that decide the close calls:

1. Test the finding's own complaint and its own example of a correct answer, item by item. Never agree with everything by default, and never agree because a different finding exposed a narrower defect.
2. The category tag does not decide the verdict or the layer. A "Wrong golden answer" card whose golden is right and whose criterion is wrong is a verifier finding: Agree, and say the golden is unchanged. A card whose golden is actually wrong is a non-verifier finding: agreeing rejects the task.
3. Wrong side claims (a wrong section number, "every answer fails" when the golden passes) do not make a finding false if its complaint holds; correct them inside the Agree note. A valid side point inside a finding whose complaint fails makes it an Agree only if that side point would itself mis-grade a realistic answer; otherwise Disagree and mention the side point in one sentence.
4. A bundled card gets one verdict. Agree when the complaint holds for at least one listed criterion, and name each listed criterion that is a false positive and stays unchanged.
5. Duplicate cards (same criterion, same evidence) get the same verdict and the same fix.
6. Check every factual claim QC makes against the files before agreeing. Solver-run evidence you cannot open is labelled as QC's account, and checked against the current version (judge panel, verifier version, date).
7. Before agreeing that a defect lives in the prompt, sources or golden, look for a sound verifier-only cure: accept every defensible reading the prompt and sources allow, drop a requirement the prompt never asks for, grade presence anywhere instead of a fixed placement, bound a band by the sources. Take that cure when it exists. Agree to a prompt, source or golden finding only when no verifier-only cure is sound, and say in the note's first sentence that agreeing rejects the task.
8. Decide each remediation item TAKE or REJECT, and name the items that must not be adopted. REJECT a remediation that edits the prompt, sources or golden; names or labels the planted item; adds a condition the prompt never sets; is an escape clause; removes a content floor; scores unseen or truncated evidence as a pass; or asks a text-reading judge to do what it cannot ("check the arithmetic against the stated inputs", "later than the current date").
9. Never weaken a sound verifier. Loosen a criterion by adding accepted alternatives, each anchored to a recomputed figure and its convention, and keep its content checks.
10. Reversing your own FRG approval is fine when the runs show it: write "Changed from the Final Review APPROVE because <evidence>" and say plainly that the approval was a miss.
11. If you find a blocking verifier defect QC did not raise, tell the user in one line outside the entries; it does not ride in the fix request unless the user says so.

## 4. Multi-pass review (mandatory)

Run every pass on every finding. Keep the working notes in the scratchpad; only the result is output.

- **Pass 0, identity and diff.** Match the screen: task ID, the version in the task link, the attached verifier file, the card count. Diff the verifier file against the FRG-approved version and any earlier corrected file. Report agreed edits that did not land and changes nobody requested (whole-workbook judges, a duplicated judge model, a garbled "PASS only if " prefix, a changed judge panel), and escalate missing agreed edits to the pod lead.
- **Pass 1, independent verdict.** For each card, read the criterion verbatim in the current file, the prompt clauses it rests on, the sources and the golden. Recompute every figure QC cites. Grade the finding's example answer against the criterion text yourself. Record the verdict and the deciding evidence.
- **Pass 2, adversarial re-test.** Try to break each verdict. For an Agree: show the example answer is not correct under the prompt, or that the criterion does not say what QC claims. For a Disagree: build a realistic correct answer that fails the current text. A verdict stands only if the attack fails; otherwise flip it and record why.
- **Pass 3, set consistency.** Duplicates and bundles aligned; every verdict routed to its layer; the outcome decided (approved, JSON revision or task rejected); the fix request covers every agreed finding and nothing else; no two fixes conflict; the golden passes every changed criterion; a correct-value probe passes, a known-wrong probe fails and your own wording has no loophole; any fix that makes a check stricter is flagged.
- **Pass 4, pre-send.** One entry per card in screen order, each headed exactly as the screen shows it; every button word matches its note (Agree means a defect is present, with proof and a fix in the request; Disagree means the item is clean, with the reason, the proof and "No change needed"); tallies come from the entries; no FRG field verdicts and no "Overall REJECT" line.

When the review is delegated, run two reviewers independently, neither seeing the other's verdicts, and settle every split by re-deriving it from the files, never by vote. When several agents draft fixes, fix one shared policy (bands, caps, anchors) before drafting and reconcile centrally. Expect "are you sure you agree with all findings?": answer it in advance by naming the closest call in the lead. When challenged, re-test against the same bar and change a verdict only with "changed because <new evidence>" or "changed because the bar was misapplied"; one new fact never flips unrelated findings.

## 5. Output

- **Lead**, one short paragraph: the outcome (approved, JSON revision, or task rejected and why), the tally of agrees and disagrees, and the closest call.
- **One entry per card**, in screen order, headed exactly as on screen: "Review 355969 · finding 3 — DISAGREE." An Agree is one or two sentences: the defect present now, quoted with its locator, any corrected side claim, and "Changed from the Final Review APPROVE because …" where that applies. A Disagree is one paragraph, two at most: the reason, the proof (criterion quote, prompt clause, source cell or figure), and "No change needed to verifier.json." plus an escalation line for a grader fault.
- **Fix request** for the Additional Comments cell, only when there are agreed verifier findings: self-contained for an engineer who has not read the task. Name the task ID and version; then, for each criterion, the findings it resolves, the quoted current text and its exact replacement, and any remediation item not to adopt; then one sentence that the golden passes every changed criterion. Lost prior edits go in one separate sentence ("Also restore the agreed edits missing from this version: …"). Bullets per criterion are allowed; no cross-references.
- **Escalations**, one template G line each.
- Give a corrected verifier.json only when the user asks for it. The tracker fields come from the user; mark any you do not have PENDING INPUT and never derive a task ID from an upload's file name.
- An overall note, when asked, is one short paragraph with no bullets.

## 6. Lessons from the first XQC rounds

Task key: LHF (lh-finance_and_insurance-financial_and_investment_analysts-20260914-103056) and the as-* tasks by suffix: p8f6vjxz-0, ohv1n4ti-2, jicq4o2h-1, 9jv02sfa-3, lxwjwnav-1, p98yff3p-8, 3m6bdh9w-3, dr4hyy6f-0, dr4hyy6f-2, dr4hyy6f-4.

- **FRG approvals came back as true positives.** Real solver runs failed correct answers on requirements the prompt never asks for: a literal "$6,640,000" and "total GP fee" (LHF, 14–21% of the grade), "405.96255m" and a £123.616m subtotal (dr4hyy6f-4), a closed owner list "General Counsel, the Treasurer, or the CFO" when the packet has no Treasurer and the golden's own "Treasury / CAO" fails it (dr4hyy6f-0), a single accepted reading when the prompt invites the other (reopening LW-Q3H8, p8f6vjxz-0; EBITDA 529.5992 for 4.578934x, ohv1n4ti-2), a hard 20 October cutoff with no scenario date in the prompt (lxwjwnav-1), a provider's 4.2–4.5 year band the prompt asks the solver to challenge (p98yff3p-8), golden wording that fails its own FAIL clause (A95 "backlog (earliest demand) > current-month demand", dr4hyy6f-2; A06/A07 labels, 3m6bdh9w-3) and a pass case that breaches the governing standard (IAS 33.36/.38 dilution, dr4hyy6f-4). At FRG these are blocking mis-grades, not optional placement readings.
- **Agree-all by default was reversed under challenge.** LHF finding 4 (the prompt asks how sensitive the answer "is to unresolved terms"), three market-alignment findings in jicq4o2h-1 (the cited answer would still fail correctly after any fix) and three in ohv1n4ti-2.
- **Fixes went to the prompt.** LHF added a sentence to instruction.md and lxwjwnav-1 added a scenario date. At XQC both are out of scope, and an agreed prompt finding rejects the task.
- **Grader faults were agreed with no change** (9jv02sfa-3, six findings). No verifier change means false positive: Disagree and escalate.
- **The wrong deliverable.** jicq4o2h-1 handed over a revised verifier.json; the user wanted verdicts and "a single comment" for the QC team.
- **Regeneration lost agreed edits** (3m6bdh9w-3 v43, dr4hyy6f-2 v41, p8f6vjxz-0 v45, ohv1n4ti-2 v47) and added unrequested changes. Diff first, every round.
- **Out-of-scope extras.** Unraised FRG fixes, a deleted verifier with re-scaled weights and edits outside the findings were bundled into the corrected file (jicq4o2h-1, 9jv02sfa-3, dr4hyy6f-0).
- **Subagent drift.** p98yff3p-8's three drafting agents set the term cap at 5.37, 5.4 and 5.25 years; lxwjwnav-1's subagent wrote "finding 3" for the screen's "finding 1".

## 7. Open points

The SOP refers to a fix-request template "below" that the document does not contain, marks Stage 6 (TFRL) TBD, and promises an open-questions section it does not include. The screen tells reviewers to "upload a corrected package" while the SOP has QC revise the JSON from the tracker request; the default here follows the SOP. Whether an Agree card needs a note, and whether a bundled card is a true positive when only some of its criteria are, are not stated by the SOP; the rules in §3 are the working practice from the sessions.
