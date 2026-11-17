# Fix your task's grading with Claude

_Text of verifier-fix-trainer-guide.docx, the one-page guide for task authors that ships with this skill._

A one-page guide for task authors. No technical knowledge needed.

QC tested your RL World task and found problems with how answers are graded. Claude can fix that for you, using QC's own test results. It only changes the grading checks. Your task text, your golden answer and your data files stay exactly as they are.

You need 2 files. Nothing else.

1

Your task zip

Download it from your task's page on RL World.

2

The QC zip

QC sent it to you. Its name ends in -dataos-with-runs.zip.

Claude will not need any other file, password or account from you. Before it builds the file to upload, it shows you what it changed.

A  Set up once (about 5 minutes)

1.Install the Claude desktop app from claude.ai/download and sign in. At the top, click the Code tab. (Not Chat. Not Cowork.)

2.Save the file verifier-fix-trainer-1.0.zip (QC gives it to you) in your Downloads folder. Do not unzip it.

3.In the Code tab, paste this and press Enter. Click Allow if Claude asks permission.

Copy and paste:  Unzip verifier-fix-trainer-1.0.zip from my Downloads folder into my .claude/skills folder, so that .claude/skills/verifier-fix-trainer/SKILL.md exists. Tell me when it is done.

B  Every time you fix a task

1.Make a new empty folder (for example on your Desktop). Put the 2 files in it. Do not unzip or rename them.

2.In Claude's Code tab, start a new session and choose that folder.

3.Paste this and press Enter:

Copy and paste:  Use the verifier-fix-trainer skill to fix my task's verifiers from the two zips in this folder. Do not ask me for any other file. Before you build the upload zip, show me one list of the checks you changed or added, with what each one said before and what it says now, and wait for my OK.

4.Wait a few minutes. If Claude asks permission to read files or run a step, click Allow.

5.Claude shows you one list of the grading checks it changed or added: what QC found, what the check said before, and what it says now. Read it. Reply OK, or tell it what to change.

6.Claude then gives you the name of one file to upload. Anything about your golden answer, task text or data is yours to fix.

7.On your task's page in RL World, click Upload Updated Task and choose that file. QC then tests your task again.

If something is not right

What you see

What to do

Claude says it does not know the skill

Do part A again, then start a new session.

Claude asks you for another file (a "manifest", a "config", a "setup")

Reply: "You only need the two zips in this folder."

Claude gives you the upload file without showing the list

Reply: "First show me the checks you changed or added."

Claude says a problem is in your golden answer, task text or data

That part is yours. Fix it on RL World the way you normally do.

You do not agree with a change in the list

Tell it: "Undo number 2" or "Change number 3 like this: ..."

RL World does not accept the upload

Copy the exact message and send it to your QC contact.

You do not understand something

Ask Claude: "Explain that in simple words."

Please do not: rename the zips  ·  change files inside them by hand  ·  upload any file other than the one Claude names.
