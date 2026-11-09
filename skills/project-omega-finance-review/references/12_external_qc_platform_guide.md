# External QC: Guide for the Expert

External QC is the final check on a task. An independent QC team reviews it,
fixes small problems themselves, and sends you the issues that need your
expertise. You decide which issues are real, fix them, and submit.

You work on the External QC step's **Content** tab. In the app, you're called
the claimant or the External QC reviewer.

## Getting the task

- If you did the task's Final Review, it stays with you for External QC.
- Otherwise, claim it from **Available for Review** on your dashboard.
- It then appears under **My Tasks**. Your claim doesn't expire while the task
  is in External QC.

## The workflow

1. **Wait for the QC team.** While they review, the step shows **Awaiting
   External QC Feedback**, and there's nothing for you to do yet. If the QC
   team fixes something themselves, the task moves to a new version, and you
   work on that one.
2. **Open the feedback.** When issues come in, the status changes to **Rework
   Pending**. Open the task from **My Tasks** and go to the **Content** tab.
   Each item explains the issue, the evidence, and a suggested fix.
3. **Download the task.** Click **Download artifacts** to check each item
   against the task files.
4. **Answer every item.**
   - **Agree** if the issue is real and needs fixing.
   - **Disagree** if it isn't actually a problem, and add a note saying why.
   - Your answers save automatically. Items marked **Pass** need no answer.
5. **Fix the real issues.** If you agreed with anything, fix the task in the
   copy you downloaded, zip it, and click **Upload Updated Task**. You get one
   upload per round, so include every fix (A fix is coming to enable unlimited uploads).
6. **Submit.** Click **Submit Verdict**.

## What happens after you submit

- **You disagreed with everything:** the task is approved.
- **You agreed with anything:** your fixed task becomes a new version and goes
  back to the QC team for another review. This uses one of the task's rework
  rounds.

If the project uses automatic quality checks, AI agents review your answers,
notes, and upload before your submission goes through. The task is locked
while they run. If they find a problem, you'll see what to change, and you can
submit again.

## Checks on your upload

Your fixed task is checked automatically before it's accepted:

- Keep the same files. Don't add, remove, or rename any.
- Leave the platform's files alone: the Dockerfile, the `environment/skills/`
  folder, `solution/solve.sh`, and the files that run the tests
  (`tests/test.sh`, `tests/verifier_runtime.py`, and `tests/verifier_lib/`).
- Don't empty a file, and make sure documents still open.
- If the task has between 15 and 100 verifiers, keep it in that range.
- An AI check confirms it's still the same task. It refuses changes that remove
  content, change what the task asks for, make grading easier, contradict the
  task's data, or include notes aimed at a reviewer.

If your upload is refused, the message tells you why. Fix it and upload again.

## Good to know

- **Rework rounds are limited.** When the task has none left, it can't go back
  for another round, and it will be approved or rejected.
- **Depending on project settings,** a task with too many confirmed issues in
  one area may be rejected instead of sent back.
- **The QC team may upload a new version while you work.** You keep the task,
  but your answers on the old version don't carry over.
