# Start a verifier fix: paste this into a new Claude Code chat

Open Claude Code in your workspace folder (the one you gave `fix_setup.py --root`). Fill in the `< >` parts and paste:

```
Use the verifier-json-fix skill to fix a verifier-fix request from the EKW_QC_Fix_Request sheet.

Task: <RL World task link, or the sheet row number>
Trainer: <trainer name, if you know it>
Files I already have (leave blank if none): <path to the RL World export zip>, <path to the earlier QC with-runs zip>

I have not done a fix before. Run the setup check first. Then take it one stage at a time (F0 to F6). Before every
step that needs my yes, tell me in plain words what you will do, what it costs, and what you expect. Fix only
tests/verifier.json. If anything is outside verifier.json, stop and tell me.
```

What happens next: Claude runs `fix_setup.py`, makes the fix record, and stops at each approval. The guide
`references/what-you-will-be-asked.md` lists every question you will get and the usual answer.

To pick up a fix another chat started, paste:

```
Use the verifier-json-fix skill. Continue the fix request <FIX-short id>: run fix_record.py <FIX-short id> status
and carry on from NEXT.
```
