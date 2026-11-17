#!/usr/bin/env python3
"""RL World's upload contract, checked before any upload: named findings carried out, no loosening beyond a fix, package intact.

    python -X utf8 upload_check.py --export <export zip | verifier.json> --fixed <fixed zip | verifier.json> --plan FIX_PLAN.md
        [--out PRE_UPLOAD_CHECK.md]

What it checks (references/change-policy.md):
  package   with two zips: the same file list, every file but tests/verifier.json byte-identical; task.toml identical, or
            different only by the pod's env swap ([verifier.env] exactly GEMINI_API_KEY + OPENAI_API_KEY, [agent] timeout_sec
            600, L6); the `config` block identical; a verifier added or removed is a RISK unless an Agree finding names it;
            effective weights (unweighted verifiers share the remainder equally) sum to 1, and a lower effective weight on
            ANY verifier, named or not, is a RISK.
  tier 1    every Agree finding in the plan: each named verifier differs from the export, and the row's "Carried out as" is
            filled -> RESOLVED-CANDIDATE. A named verifier left unchanged -> NOT CHANGED (FAIL), unless the row's Verdict is
            not FIX and its Evidence quotes the user ("user: ...") -> LEFT ON THE USER'S WORD (noted, not a fail).
  extras    every changed verifier no Agree finding names is scanned for loosening: added phrases such as "not required",
            "optional", "accepted example", "rather than requirement", "accept any"; a count word that went down ("five" ->
            "four"); fewer must/required/shall; fewer FAIL clauses; a prompt shortened by a quarter; a lower weight; core ->
            secondary. Each signal is a RISK. A RISK is "reasoned" when the plan has a FIX row with Tier 2 naming that
            verifier with Evidence (section A), or a golden-ledger row ruling VERIFIER with Evidence (section B); then it is
            listed with its evidence for the user. A STRONG signal (a required count or FAIL clause dropped, "rather than
            requirement", "optional", "accepted example", a weight cut, core to secondary, a removal) is the #45 refusal
            pattern: it also needs the user's "user: ..." yes in that row. An unreasoned RISK counts in the last line.
Last line: UPLOAD CHECK: OK (n named carried out, k extras reasoned) | UPLOAD CHECK: RISK n (...) | UPLOAD CHECK: FAIL n (...).
The check is mechanical: it proves a named verifier changed, not that the change carries out the remediation. That is the
read-through's job, and the "Carried out as" cell is where you quote it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fix_plan  # noqa: E402

STRONG = re.compile(r"\b(?:rather than (?:a )?requirements?|accepted examples?|as (?:an )?examples?|optional|not mandatory|may be omitted|examples? rather than)\b", re.I)
LOOSEN = re.compile(r"\b(?:not required|need not|optional|rather than (?:a )?requirements?|accepted examples?|as (?:an )?examples?|"
                    r"illustrat\w+ (?:only|rather)|is welcome|no longer required|may be omitted|not mandatory|acceptable alternatives?|"
                    r"accept(?:s|ed)? any|any (?:equivalent|defensible|reasonable)|need not be (?:stated|shown|printed|repeated)|"
                    r"examples? rather than|are not required|is not required)\b", re.I)
MUST = re.compile(r"\b(?:must|required|requires|require|shall|mandatory)\b", re.I)
WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
COUNT = re.compile(r"\b(?:all|every|each|the|these|at least)\s+(one|two|three|four|five|six|seven|eight|nine|ten|\d{1,2})\s+(?:required\s+)?"
                   r"([a-z][a-z-]+)\b", re.I)


def load_pkg(path: Path) -> tuple[dict, dict[str, bytes] | None, str]:
    """verifier.json, the zip's files (name -> bytes) or None, and the raw verifier.json text."""
    if path.is_file() and path.suffix.lower() == ".zip":
        files = {}
        with zipfile.ZipFile(path) as zf:
            for n in zf.namelist():
                if not n.endswith("/"):
                    files[n] = zf.read(n)
        names = sorted([n for n in files if n.endswith("tests/verifier.json")], key=len)
        if not names:
            sys.exit(f"{path}: no tests/verifier.json inside")
        raw = files[names[0]].decode("utf-8-sig")
        return json.loads(raw), files, raw
    vj = fix_plan.load_verifier_json(path)
    return vj, None, ""


def strip_root(files: dict[str, bytes]) -> dict[str, bytes]:
    roots = {n.split("/")[0] for n in files if "/" in n}
    if len(roots) == 1 and all("/" in n for n in files):
        r = roots.pop() + "/"
        return {n[len(r):]: b for n, b in files.items()}
    return files


def prompt_of(v):
    return fix_plan.prompt_of(v)


def weight(v):
    w = (v.get("metadata") or {}).get("weight")
    return float(w) if isinstance(w, (int, float)) else None


def effective_weights(vs):
    """The library's rule: explicit weights as given; unweighted verifiers share the remainder equally."""
    explicit = {v["name"]: weight(v) for v in vs if weight(v) is not None}
    rest = [v["name"] for v in vs if weight(v) is None]
    share = max(0.0, 1.0 - sum(explicit.values())) / len(rest) if rest else 0.0
    out = dict(explicit)
    for n in rest:
        out[n] = share
    return out


def toml_env_swap_only(a: bytes, b: bytes) -> bool:
    """True when task.toml differs from the export only by the pod's upload rule: [verifier.env] = GEMINI + OPENAI keys
    and [agent] timeout_sec = 600 (L6). Anything else that differs is a FAIL."""
    import re as _re

    def norm(t):
        t = t.decode("utf-8", errors="replace").replace("\r\n", "\n")
        env = _re.search(r"\[verifier\.env\]\n(.*?)(?=\n\[|\Z)", t, _re.S)
        body = _re.sub(r"\[verifier\.env\]\n(.*?)(?=\n\[|\Z)", "[verifier.env]\n", t, flags=_re.S)
        body = _re.sub(r"(\[agent\][^\[]*?timeout_sec\s*=\s*)[\d.]+", r"\g<1>X", body, flags=_re.S)
        keys = sorted(_re.findall(r"^\s*([A-Z_]+)\s*=", env.group(1), _re.M)) if env else []
        agent = _re.search(r"\[agent\][^\[]*?timeout_sec\s*=\s*([\d.]+)", t, _re.S)
        return body, keys, float(agent.group(1)) if agent else None

    ba, ka, ta = norm(a)
    bb, kb, tb = norm(b)
    return ba == bb and kb == ["GEMINI_API_KEY", "OPENAI_API_KEY"] and tb == 600.0


def effective_sum(vs):
    explicit = [weight(v) for v in vs if weight(v) is not None]
    unweighted = len(vs) - len(explicit)
    s = sum(explicit)
    if unweighted:
        s += max(0.0, 1.0 - s)  # the library shares the remainder equally
    return s


def plan_rows(plan: Path):
    text = plan.read_text(encoding="utf-8-sig")
    tables = {h.split(".")[0].strip(): (hdr, rows) for h, hdr, rows in fix_plan.parse_md_tables(text)}
    return tables


def loosening_signals(old: dict, new: dict) -> list[str]:
    sig = []
    op, np_ = prompt_of(old), prompt_of(new)
    if op != np_:
        added = {x.lower() for x in LOOSEN.findall(np_)} - {x.lower() for x in LOOSEN.findall(op)}
        if added:
            sig.append("loosening words added: " + ", ".join(sorted(added)))
        oc = {m.group(2).lower(): WORDNUM.get(m.group(1).lower(), int(m.group(1)) if m.group(1).isdigit() else 0) for m in COUNT.finditer(op)}
        nc = {m.group(2).lower(): WORDNUM.get(m.group(1).lower(), int(m.group(1)) if m.group(1).isdigit() else 0) for m in COUNT.finditer(np_)}
        for noun, n_old in oc.items():
            n_new = nc.get(noun)
            if n_new is not None and n_new < n_old:
                sig.append(f"count of required {noun} dropped {n_old} -> {n_new}")
            elif n_new is None and n_old >= 2:
                sig.append(f"'{n_old} {noun}' requirement no longer stated")
        om, nm = len(MUST.findall(op)), len(MUST.findall(np_))
        if nm < om:
            sig.append(f"must/required words {om} -> {nm}")
        of, nf = len(re.findall(r"\bFAIL\b", op)), len(re.findall(r"\bFAIL\b", np_))
        if nf < of:
            sig.append(f"FAIL clauses {of} -> {nf}")
        if len(np_) < 0.75 * len(op):
            sig.append(f"prompt shortened {len(op)} -> {len(np_)} characters")
    ow, nw = weight(old), weight(new)
    if ow is not None and nw is not None and nw < ow - 1e-9:
        sig.append(f"weight {ow:.4f} -> {nw:.4f}")
    oi, ni = (old.get("metadata") or {}).get("importance"), (new.get("metadata") or {}).get("importance")
    if oi == "core" and ni == "secondary":
        sig.append("importance core -> secondary")
    if old.get("assertion", {}).get("type") != new.get("assertion", {}).get("type"):
        sig.append(f"assertion type {old.get('assertion', {}).get('type')} -> {new.get('assertion', {}).get('type')}")
    return sig


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--export", required=True)
    ap.add_argument("--fixed", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    ex, exf, _ = load_pkg(Path(a.export))
    fx, fxf, _ = load_pkg(Path(a.fixed))
    lines: list[str] = []
    fails: list[str] = []
    risks: list[tuple[str, str, str]] = []  # verifier, signal, reason or ""
    notes: list[str] = []

    def say(s=""):
        lines.append(s)

    say(f"# Pre-upload check: {Path(a.fixed).name} against {Path(a.export).name}")
    say("")
    # package
    say("## Package")
    say("")
    if exf is not None and fxf is not None:
        exf, fxf = strip_root(exf), strip_root(fxf)
        only_ex = sorted(set(exf) - set(fxf))
        only_fx = sorted(set(fxf) - set(exf))
        if only_ex or only_fx:
            fails.append(f"file list differs: missing {only_ex[:5]}, added {only_fx[:5]}")
        diff = [n for n in sorted(set(exf) & set(fxf)) if exf[n] != fxf[n]]
        bad = [n for n in diff if not n.endswith("tests/verifier.json")]
        toml = [n for n in bad if n.endswith("task.toml")]
        toml_note = "identical"
        if toml:
            if toml_env_swap_only(exf[toml[0]], fxf[toml[0]]):
                bad = [n for n in bad if n not in toml]
                toml_note = "differs by the pod's env swap only ([verifier.env] GEMINI + OPENAI, agent 600; L6)"
                notes.append("task.toml carries the pod's env swap (L6); record the before and after in NOTES")
            else:
                toml_note = "DIFFERS beyond the env swap (FAIL)"
        if bad:
            fails.append("files other than tests/verifier.json differ: " + ", ".join(bad[:8]))
        say(f"- files: {len(fxf)} (export {len(exf)}); differing: {diff or 'none'}")
        say(f"- task.toml: {toml_note}")
        say(f"- fixed zip md5: {hashlib.md5(Path(a.fixed).read_bytes()).hexdigest()}")
    else:
        say("- verifier.json files compared only (give zips to compare the whole package)")
    if ex.get("config") != fx.get("config"):
        fails.append(f"config block differs: export {ex.get('config')} vs fixed {fx.get('config')} (the upload keeps the export's judges)")
    say(f"- config identical: {'yes' if ex.get('config') == fx.get('config') else 'NO'}")
    exv = {v["name"]: v for v in ex.get("verifiers", [])}
    fxv = {v["name"]: v for v in fx.get("verifiers", [])}
    added, removed = sorted(set(fxv) - set(exv)), sorted(set(exv) - set(fxv))
    ew_ex, ew_fx = effective_weights(ex.get("verifiers", [])), effective_weights(fx.get("verifiers", []))
    s = effective_sum(fx.get("verifiers", []))
    if abs(s - 1.0) > 1e-6:
        fails.append(f"effective weights sum to {s:.6f}, not 1")
    say(f"- verifiers: {len(fxv)} (export {len(exv)}); added {added or 'none'}; removed {removed or 'none'}; weight sum {s:.6f}")
    changed = sorted(n for n in exv if n in fxv and exv[n] != fxv[n])
    say(f"- changed verifiers: {len(changed)}: {', '.join(changed) or 'none'}")
    say("")
    # plan
    tables = plan_rows(Path(a.plan))
    hdrA, rowsA = tables.get("A", ([], []))
    hdrB, rowsB = tables.get("B", ([], []))
    lowA = [h.lower() for h in hdrA]

    def cellA(r, key):
        for k, h in enumerate(lowA):
            if key in h:
                return r[k].strip()
        return ""

    agree_named: dict[str, list[str]] = {}
    agree_evid: dict[str, str] = {}        # verifier -> the Evidence cells of the Agree rows naming it
    disagree_named: dict[str, list[str]] = {}
    disagree_evid: dict[str, str] = {}
    tier2: dict[str, str] = {}
    plan_named: set[str] = set()
    say("## Named findings (tier 1)")
    say("")
    say("| # | Label | Verifiers | Verdict | Status | Carried out as |")
    say("|---|---|---|---|---|---|")
    n_named_ok = 0
    for r in rowsA:
        if not r or r[0].startswith("("):
            continue
        rid, label, verdict = r[0], cellA(r, "label").lower(), cellA(r, "verdict").upper()
        vs = [x.strip() for x in re.split(r"[,;]\s*", cellA(r, "verifiers")) if x.strip() and (x.strip() in exv or x.strip() in fxv)]
        plan_named.update(vs)
        tier, carried, evid = cellA(r, "tier"), cellA(r, "carried"), cellA(r, "evidence")
        if verdict == "FIX" and tier == "2":
            for n in vs:
                tier2[n] = evid or "(evidence missing in the plan)"
        if label.startswith("disagree"):
            for n in vs:
                disagree_named.setdefault(n, []).append(rid)
                disagree_evid[n] = (disagree_evid.get(n, "") + " " + evid).strip()
        if not label.startswith("agree"):
            continue
        for n in vs:
            agree_named.setdefault(n, []).append(rid)
            agree_evid[n] = (agree_evid.get(n, "") + " " + evid).strip()
        if verdict != "FIX":
            if "user:" in evid.lower():
                status = "LEFT ON THE USER'S WORD"
                notes.append(f"Agree #{rid} left unfixed on the user's word: {evid[:120]}")
            elif not verdict:
                changed_here = [n for n in vs if n in changed]
                status = "NOT RECORDED (FAIL): fill Verdict, Tier and 'Carried out as' in FIX_PLAN.md" + (f" (its verifiers did change: {', '.join(changed_here)})" if changed_here else "")
                fails.append(f"Agree finding #{rid}: the plan row has no Verdict yet (write FIX, Tier 1 and what you changed in 'Carried out as')")
            else:
                status = "NOT FIXED (FAIL)"
                fails.append(f"Agree finding #{rid} is {verdict} but not FIX: an Agree item stays unfixed only with the user's words in Evidence ('user: ...')")
        else:
            unchanged = [n for n in vs if n not in changed and n not in removed]
            if not vs:
                status = "NO VERIFIER RESOLVED (FAIL)"
                fails.append(f"Agree finding #{rid}: no verifier name from the plan matches the file")
            elif unchanged:
                status = f"NOT CHANGED: {', '.join(unchanged)} (FAIL)"
                fails.append(f"Agree finding #{rid}: named verifier(s) unchanged: {', '.join(unchanged)}")
            elif not carried:
                status = "CHANGED, 'Carried out as' empty (FAIL)"
                fails.append(f"Agree finding #{rid}: 'Carried out as' is empty in the plan")
            else:
                status = "RESOLVED-CANDIDATE"
                n_named_ok += 1
        say(f"| {rid} | {label} | {', '.join(vs) or cellA(r, 'verifiers')} | {verdict} | {status} | {carried[:140].replace('|', '/')} |")
    say("")
    # golden ledger rulings as tier-2 reasons
    lowB = [h.lower() for h in hdrB]
    for r in rowsB:
        if not r or r[0].startswith("("):
            continue
        ruling = next((r[k] for k, h in enumerate(lowB) if h.startswith("ruling")), "").strip().upper()
        evid = next((r[k] for k, h in enumerate(lowB) if "evidence" in h), "").strip()
        if ruling == "VERIFIER" and r[0].strip() in exv:
            tier2.setdefault(r[0].strip(), f"golden ledger: {evid}")
    # extras
    # effective-weight cuts on any verifier, named or not (the library shares the remainder over unweighted ones)
    for n in sorted(set(exv) & set(fxv)):
        if ew_fx.get(n, 0) < ew_ex.get(n, 0) - 1e-9:
            reason = tier2.get(n, "")
            risks.append((n, f"effective weight {ew_ex[n]:.4f} -> {ew_fx[n]:.4f}", reason if "user:" in reason.lower() else ""))
    for n in added:
        if n in plan_named:
            notes.append(f"verifier added: {n} (named in the plan; RL World joins on names, a new name carries no calibration)")
        else:
            risks.append((n, "verifier added (not named in the plan)", ""))
    say("## Changed verifiers no Agree finding names (tier 2 or 3)")
    say("")
    say("| Verifier | Loosening signals | Plan evidence | Status |")
    say("|---|---|---|---|")
    n_extra_reasoned = 0
    for n in changed:
        if n in agree_named:
            continue
        sig = loosening_signals(exv[n], fxv[n])
        reason = tier2.get(n, "")
        if sig:
            strong = bool(STRONG.search(prompt_of(fxv[n]))) and not STRONG.search(prompt_of(exv[n])) or any(
                s.startswith(("count of required", "FAIL clauses", "weight", "importance")) or "no longer stated" in s for s in sig)
            if reason and (not strong or "user:" in reason.lower()):
                status = "RISK (reasoned)" if not strong else "RISK (strong signal, user's yes quoted)"
                n_extra_reasoned += 1
            elif reason and strong:
                status = "RISK (STRONG signal: the #45 refusal pattern; needs 'user: ...' in the tier-2 row)"
                reason = ""
            else:
                status = "RISK (STRONG signal: the #45 refusal pattern; no tier-2 row with evidence)" if strong else "RISK (no tier-2 row with evidence)"
            risks.append((n, "; ".join(sig), reason))
        else:
            status = "tightening or neutral" + (" (tier 2)" if reason else " (no plan row)")
            if reason:
                n_extra_reasoned += 1
            else:
                notes.append(f"{n} changed with no loosening signal and no plan row: add a tier-2 row or revert it")
        say(f"| {n} | {('; '.join(sig) or 'none').replace('|', '/')} | {reason[:140].replace('|', '/')} | {status} |")
    # A removed verifier is the strongest loosening there is (change-policy tier 3). It passes only with the user's
    # quoted yes ("user: ...") in a plan row that names it, whether or not an Agree finding asks for the removal.
    for n in removed:
        why = (agree_evid.get(n, "") + " " + tier2.get(n, "")).strip()
        quoted = "user:" in why.lower()
        risks.append((n, "verifier removed" + (f" (named by Agree #{', '.join(agree_named[n])})" if n in agree_named else ""),
                      why if quoted else ""))
        say(f"| {n} | REMOVED | {why[:140].replace('|', '/')} | {'RISK (removal, the user yes quoted)' if quoted else 'RISK (removal needs user: ... in its plan row)'} |")
    # A verifier only Disagree findings name stays as exported; a change to it is refused by RL World (#22, a false-positive label).
    for n in changed:
        if n in disagree_named and n not in agree_named:
            why = (disagree_evid.get(n, "") + " " + tier2.get(n, "")).strip()
            quoted = "user:" in why.lower()
            risks.append((n, f"changed although only Disagree finding(s) #{', '.join(disagree_named[n])} name it", why if quoted else ""))
            say(f"| {n} | CHANGED UNDER A DISAGREE LABEL | {why[:140].replace('|', '/')} | {'RISK (the user yes quoted)' if quoted else 'RISK (revert it, or quote the user)'} |")
    say("")
    unreasoned = [r for r in risks if not r[2]]
    say("## Result")
    say("")
    for f in fails:
        say(f"- FAIL: {f}")
    for n, sig, reason in risks:
        say(f"- RISK {n}: {sig}" + (f" | evidence: {reason}" if reason else " | NO EVIDENCE: revert, or add a tier-2 row with evidence and ask the user"))
    for x in notes:
        say(f"- note: {x}")
    if fails:
        last = f"UPLOAD CHECK: FAIL {len(fails)} ({n_named_ok} named carried out, {len(risks)} risks)"
    elif unreasoned:
        last = f"UPLOAD CHECK: RISK {len(unreasoned)} ({n_named_ok} named carried out, {len(risks) - len(unreasoned)} risks reasoned)"
    else:
        last = f"UPLOAD CHECK: OK ({n_named_ok} named carried out, {n_extra_reasoned} extras reasoned" + (f", {len(risks)} reasoned risks for the user" if risks else "") + ")"
    say("")
    say(last)
    text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text if not a.out else f"wrote {a.out}")
    print(last) if a.out else None
    return 0 if last.startswith("UPLOAD CHECK: OK") else 1


if __name__ == "__main__":
    sys.exit(main())
