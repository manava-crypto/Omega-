# What you will be asked during a fix, and what a normal answer is

The skill stops before every act that is outward, costs money or cannot be undone. Each question below comes with
what Claude will do if you say yes. A "no", or "wait", is always safe: nothing has happened yet. Nothing on this
list needs fix experience, only attention.

| When | The question | What yes does | Cost | Usual answer |
|---|---|---|---|---|
| Setup | "Install `<package>`?" | runs `pip install --user <package>` for a package the scripts need | none | yes, if it is one of pydantic, jsonpath-ng, openpyxl |
| F0 claim | "Claim row `<n>` on the fix sheet?" | types your name in column G and In-Progress in column H, then reads the row back | none; others see the row as yours | yes, if the row is free and you were assigned it |
| F1 download | "Download the v`<N>` export and the earlier QC run?" | downloads in your Chrome, with the three dialog judges | none | yes |
| (any time) | "Please sign in to DataOS / RL World" | nothing; Claude waits | none | sign in yourself, in the tab Claude uses |
| F2 scope stop | "`SCOPE: STOP`: these findings are not verifier problems. Fix the verifier part only, or hand it back as Non-Verifier Issues?" | depends on your choice | none | ask your lead if unsure. The usual choice is to fix the verifier rows and tell the trainer the rest |
| F2 practice review | "Run this line in a terminal tab" | a rehearsal review with your own `claude`, about 10 to 20 minutes, read-only | your Claude usage, no DataOS credit | run it |
| F2 diff | "The pipeline diff shows a NEW or WORSE finding (or a verifier now agentic). Fix the wording, or keep it with this reason?" | keeps it: the round is rebuilt with `--accept-diff` and the reason goes into the report | none | fix the wording, unless the reason is clear and you agree with it |
| F3 run | "Upload round `<n>` and run the 4-reviewer pipeline on DataOS?" | uploads the DataOS copy to the master dataset and starts one run | about 3 USD | yes, once `ROUND <n>: READY` and the practice review's Majors are settled |
| F3 result | "Download the Dataset with runs of run `<id>`?" | downloads the results, to read why the run did not pass | none | yes |
| F3 retry | "Runs ended EXCEPTION at sandbox start (platform). Retry or wait?" | retries the run | about 3 USD per retry | wait, or check that another task's run starts first |
| F4 | "Download the passing run for the manager read?" | downloads it, then runs the manager read | none | yes |
| F6 | "Send this DM to `<trainer>` with the zip?" | you send it yourself; Claude only drafts it | none | read the draft, then send it |
| F6 | "Set the sheet row to Fixed?" | types Fixed in column H and reads it back | none | yes, after the DM is sent |

Things Claude never asks you to approve, because it never does them on a fix: editing the prompt, golden, data or
`task.toml`; changing the judges; uploading anything to RL World. If a message asks for one of these, say no and tell
your lead.

## Words you will see

| Word | Meaning |
|---|---|
| verifier | one grading check in `tests/verifier.json` |
| golden / oracle | the reference answer, and the run that grades it (must score 1.00) |
| No-op | the run with an empty answer (must score 0.00) |
| `ROUND <n>: READY` | every local check passed for this round; the DataOS run is the real test |
| `SCOPE: OK` / `STOP` | every finding is a verifier problem / some are not, so the fix stops for your decision |
| `4/4 valid` | all four DataOS reviews accepted the fix: the pass |
| OUTSIDE VERIFIER.JSON | a real problem in the prompt, golden or data, which the trainer must fix |
