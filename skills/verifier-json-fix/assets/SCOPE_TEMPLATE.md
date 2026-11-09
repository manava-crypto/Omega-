# Scope check: is every finding a verifier problem? ({name})

Fill this BEFORE editing anything (fix path F2). One row per External QC finding (and per extra item you add from
the earlier run, the sweep or a practice review). Then run `scope_check.py SCOPE.md --findings <n>`.

Our category, one of: VERIFIER (fix in tests/verifier.json) | GOLDEN | PROMPT | DATA | PLATFORM (library, runtime,
judges, task.toml) | NOT A DEFECT. Anything but VERIFIER and NOT A DEFECT is never edited: it stops the fix and goes
to the user (who decides), then to the trainer.
Evidence: the file and line or cell, and the quoted words that decide it. Where RL World's category or the trainer's
label disagrees with ours, say why in Note.

| # | Finding (review id / no.) | Verifier(s) | RL World category | Trainer label | Our category | Evidence (file:line, "quote") | Note |
|---|---|---|---|---|---|---|---|
