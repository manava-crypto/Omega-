# One-time setup: paste this into Claude Code

Open the Claude desktop app, choose the **Code** tab, start a session in any folder (your Downloads folder is fine),
and paste:

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

Claude asks before each install. Saying yes is normal. If Python will not install this way, install it yourself from
python.org (on Windows, tick "Add Python to PATH"), then paste the prompt again.
