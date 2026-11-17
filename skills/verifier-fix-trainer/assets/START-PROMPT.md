# Fix my task's verifiers: what to do

The one-page guide for task authors is `verifier-fix-trainer-guide.docx` (sent with this skill). This file is the same
thing in short.

## One time

1. Install the Claude desktop app and open the **Code** tab.
2. Save `verifier-fix-trainer-1.0.zip` in your Downloads folder, then paste this to Claude in any folder:

```
Unzip verifier-fix-trainer-1.0.zip from my Downloads folder into my .claude/skills folder, so that .claude/skills/verifier-fix-trainer/SKILL.md exists. Tell me when it is done.
```

That is all. No Python packages, no setup script, no account beyond Claude.

## Each task

1. Make a folder. Put two files in it:
   - your task zip, downloaded from your task's page on RL World;
   - the zip QC shared with you, named `…-dataos-with-runs.zip`.
2. Open Claude Code in that folder and paste:

```
Use the verifier-fix-trainer skill to fix my task's verifiers from the two zips in this folder. Do not ask me for any other file. Before you build the upload zip, show me one list of the checks you changed or added, with what each one said before and what it says now, and wait for my OK.
```

Claude reads QC's findings from the zip and does the fixing without stopping at every step. Before it builds the file
to upload, it shows you **one list**: the checks it changed (what QC found, what the check said, what it says now), any
check it changed that QC did not name, any check it added or removed, and anything that is yours to fix (golden answer,
task text, data). Read it, then say OK or tell it what to change.

It will not ask you for any other file. If it does, reply: "You only need the two zips in this folder."

It ends with the file to upload. Upload it on RL World with "Upload Updated Task". QC then tests your task again.
