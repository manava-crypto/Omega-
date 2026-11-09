# Fix your task's grading with Claude: a one-page guide for task experts

**What this is.** QC sent your RL World task back with notes on its grading: the checks in `tests/verifier.json`
that decide whether an answer passes. A Claude skill called **verifier-json-fix** reads those notes, fixes that one
file, checks the fix against every rule RL World enforces, and tells you exactly what to upload. It never touches
your prompt, golden answer or data files. If a note is really about those, it tells you, and you fix them yourself as
usual.

**Why this version.** The first version of this skill got most tasks through in three or four tries: each new test
run found something the first fix had missed, or RL World refused the zip. Version 2 runs those lessons as checks
before you upload (every one of them cost a real task a round), so the goal is one upload and one QC run.

## Which Claude? Use Claude Code

The Claude desktop app has three tabs. This only works in **Code**.

| Tab | What it is | Use it for this? |
|---|---|---|
| **Chat** | Talk to Claude, like a chat window | No |
| **Cowork** | Claude works on documents and tasks for you | No |
| **Code** | Claude works with files and runs small programs on your computer | **Yes** |

## One-time setup (about 10 minutes: Claude does most of it)

1. **Install the Claude desktop app** from claude.ai/download and sign in with your work account. Open the **Code** tab.
2. **Save the skill zip.** Put `verifier-json-fix.zip` (from your pod lead) in your Downloads folder. Don't unzip it.
3. **Let Claude set it up.** In the Code tab, start a session in your Downloads folder and paste this:

   ```
   Set up the verifier-json-fix skill on this computer for me. I am not technical: before each step, tell me in one plain sentence what you will do, and ask me before you install anything.
   1. Find verifier-json-fix.zip in my Downloads folder. If it is not there, ask me where it is.
   2. Check that Python 3.11 or newer works here. If it does not, offer to install it (winget on Windows, Homebrew or the python.org installer on Mac) and wait for my yes.
   3. Unzip the skill so that this file exists: <my home folder>/.claude/skills/verifier-json-fix/SKILL.md. If that folder already exists, ask me before replacing it.
   4. Make a work folder called "fixes" in my home folder, unless it already exists.
   5. Install the Python packages pydantic, jsonpath-ng and openpyxl for my user (pip install --user), after my yes.
   6. Run the skill's setup check on the work folder in expert mode: python -X utf8 <skill folder>/scripts/fix_setup.py --root <the fixes folder> --expert. Fix anything it lists until its last line is "FIX SETUP: READY (expert mode)".
   7. Finish by telling me the full path of my fixes folder, and that I should now open a new Code session in that folder.
   ```

   Claude installs Python and what the skill needs, asking you first each time. It ends with
   `FIX SETUP: READY (expert mode)` and the path of your new **fixes** folder.
4. **Open a new Code session in that fixes folder.** You work from there from now on.

## Each time you fix a task

1. **Download your task from RL World, fresh.** On your task's page: **Quality Checks → Export & Download → Download
   artifacts**. In the judges box keep exactly these three: `xai/grok-4.7`, `anthropic/claude-sonnet-5-5`,
   `anthropic/claude-opus-5-5`. Put the zip in your fixes folder. **Don't rename it**: the version number in the name
   matters, and this download carries a record (`.external-qc-manifest.json`) that RL World checks on upload. A copy
   from somewhere else, or an older download, is refused.
2. **Get QC's feedback and runs.** QC sends you two things: the **feedback file** (`...-external-qc-feedback.json`,
   what is wrong with the grading) and a **runs zip** (how earlier test answers were graded). Put both in your fixes
   folder. Don't unzip anything: Claude does that.
3. **Start Claude.** In the Code tab, with your fixes folder open, paste this and fill in the `< >` parts:

   ```
   Use the verifier-json-fix skill in expert mode to fix the verifiers of my own RL World task.
   My task zip: <file name>
   The feedback file QC sent: <file name>
   The runs zip QC sent: <file name>
   I have not done this before. Explain each step in plain words before you do it.
   ```
4. **Answer its questions.** Claude stops and asks before anything that changes your computer, such as installing a
   Python package it needs. Saying yes is normal. Saying "wait" is always safe. It may also ask you about your task:
   whether a figure can be read two ways, or whether your golden answer has a slip. Answer from your own knowledge of
   the task; Claude cannot change the golden or the prompt, so these questions decide what you fix yourself.
5. **Wait until Claude says** `ROUND 1: READY`. It then tells you:
   - **the file to upload,** always `round1\trainer\<your zip name>_verifierfix_upload.zip`;
   - **one line for each QC note:** what was fixed, or why the note needs no change;
   - **anything it could not fix,** because it is in your prompt, golden answer or data;
   - **a next-round list,** if it found grading problems QC's notes did not mention. RL World only accepts changes
     the notes ask for, so these wait for the next round of notes. Keep the list.
6. **Upload.** On your task's page in RL World, click **Upload Updated Task** and choose that exact file. Paste the
   lines Claude gave you where RL World asks what you changed, or send them to your QC contact. QC then re-runs your
   task: that run is the real test.

## If something goes wrong

| You see | Do this |
|---|---|
| Claude doesn't know the skill | Check that `SKILL.md` sits at `.claude\skills\verifier-json-fix\`, then start a new Code session |
| `FIX SETUP: NOT READY (missing: ...)` | Let Claude fix what it names. If Python won't install, get it from python.org (on Windows tick "Add Python to PATH"), then paste the setup prompt again |
| `ROUND 1: NOT READY` | Normal: tell Claude "fix it and build again". It makes `round1b`, then you upload that one. It will not call a round READY while any check fails |
| `UPLOAD CHECK: FAIL ... manifest missing` | Your task zip is not a fresh RL World download. Download it again (step 1) and tell Claude the new file name |
| "This note is outside verifier.json" | Fix that part of your task yourself, the way you usually would |
| RL World refuses the upload | Copy the exact message to Claude and to your pod lead. The known messages and their causes are in the skill (`references/rlworld-refusals.md`) |
| Anything you don't understand | Ask Claude "explain that in simple words". If you are still stuck, ask your pod lead |

**Never do these:** rename the zip, edit files inside it by hand, change the judges, change `task.toml`, or upload
anything other than the file Claude names. You need nothing else: no extra tools, accounts or test runs. QC runs the
task again after you upload.
