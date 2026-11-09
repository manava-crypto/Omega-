#!/usr/bin/env python3
"""Apply a list of edits to tests/verifier.json, exactly, and keep the file's format byte for byte.

    python -X utf8 apply_verifier_fix.py <in verifier.json> <edits.json> <out verifier.json>
        [--original <export verifier.json>] [--changes <changes.md>] [--check] [--overwrite] [--allow-reformat]

Replaces the hand-written apply_verifier_fix_rN.py of each round (19 of them on six fix requests, 2026-11-02/03).
The input is never written. Chain rounds by passing the last round's output as the next round's input, and keep each
round's edits_rN.json next to the report: it is the record of what changed and why.

edits.json:

    {
      "edits": [
        {"ref": "R3-1 review 398921", "verifier": "memo_fee_adjustment_conclusion", "op": "replace",
         "field": "prompt", "old": "exact text, found once", "new": "replacement"},
        {"ref": "R3-1", "verifier": "memo_fee_adjustment_conclusion", "op": "replace", "field": "how",
         "old": "...", "new": "..."},
        {"ref": "R2-4", "verifier": "deck_x", "op": "insert", "field": "prompt", "after": "anchor, found once",
         "text": " Added words."},
        {"ref": "R2-1", "verifier": "actions_x", "op": "set", "path": "source.file.arguments.range", "value": "A1:AZ80"},
        {"ref": "T1", "verifiers": "*", "op": "replace", "field": "prompt", "old": "/tmp/seed/", "new": " / ",
         "total": 46}
      ],
      "keep_how": {"actions_x": "range only: what is graded did not change"},
      "sweep": ["$148,000"]
    }

  op replace  field prompt | how | why; old must occur exactly `count` times (default 1). With `verifiers` (a list,
              or "*" for every verifier that has the field) give `total`, the exact number of matches over all of them.
  op insert   field, `after` or `before` an anchor that occurs exactly once, `text`.
  op set      `path` dotted inside the verifier (prompt, how and why are accepted as names), `value` any JSON. A
              missing key on the path is an error unless "create": true. name/id cannot be set. A weight must be a
              number in (0, 1]; prompt/how/why must stay non-empty text; how/why/importance cannot be dropped.
  op split    `new_name` (the parent's name + "_" + a suffix, e.g. v7f -> v7f_b) and, on a weighted file, `weights`
              {parent: w1, new_name: w2} summing to the parent's weight. The new verifier starts as a copy of the
              parent; give it its own prompt and how with later edits in the same list.
  op delete   removes the verifier. On a weighted file `move_weight_to` lists the verifiers that take its weight,
              shared in proportion to their own weights. Delete only what grades something the prompt never asks for.
  Each edit may only carry the keys of its op (a misspelled "verifer" is an error, never ignored).
  prompt is assertion.<type>.prompt for rubric and agentic verifiers alike; how and why are metadata.how_justification
  and metadata.why_justification.
  keep_how    {verifier or "*": reason}: why how_justification stays as it is although the grading text changed.
  sweep       extra terms to look for in every verifier after the edits (figures and IDs removed by a replace are
              looked for anyway).

PROBLEM lines stop the run and nothing is written: a verifier or text not found the expected number of times (with the
closest passage), a prompt edit on a deterministic verifier, a changed prompt, source or assertion with no how edit and
no keep_how reason, effective weights that do not sum to 1, an input whose unchanged round-trip is not byte-identical,
an output that is the input or already exists. WARNING lines do not stop it: wording the pipeline's clause counter
(G7) counts, a how/why longer than one sentence, a verifier-like name that is not in the file, a new placement pin,
backslashes or control characters in new text. The SWEEP section lists every other verifier still holding a figure or
ID that an edit changed. The last line is APPLY: OK (...) or APPLY: FAILED (n problems), nothing written; exit 0 or 1.
"""
import argparse
import copy
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FIELDS = {"how": ("metadata", "how_justification"), "why": ("metadata", "why_justification")}
COMMON_KEYS = {"ref", "op", "verifier", "verifiers"}
OP_KEYS = {"replace": {"field", "old", "new", "count", "total", "no_sweep"},
           "insert": {"field", "after", "before", "text"},
           "set": {"path", "value", "create"},
           "split": {"new_name", "weights"},
           "delete": {"move_weight_to"}}
TEXT_FIELDS = ("prompt", "how", "why")
SNAKE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+){2,}\b")
PINS = re.compile(
    r"\bslides? \d+(?:\s*(?:-|to|and)\s*\d+)?\b|\bon (?:the|a|its) [\w'&/ -]{1,40}? (?:sheet|tab|slide)\b|"
    r"\b(?:opening|leading|first|final|last) (?:section|slide|page|sheet|tab)\b", re.I)
MONEY = re.compile(r"\$\s?\d{1,3}(?:,\d{3})+(?:\.\d+)?|\$\s?\d{3,}(?:\.\d+)?")  # $148,000, $6675; not $0
BIGNUM = re.compile(r"(?<![\w.$-])(?:\d{1,3}(?:,\d{3})+|\d{5,})(?:\.\d+)?(?![\w-])")
IDENT = re.compile(r"\b[A-Z]{2,}[A-Z0-9]*-[A-Z0-9-]*\d[A-Z0-9-]*\b")
DATE = re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.? \d{1,2}(?:, \d{4})?\b")


def md5(b):
    return hashlib.md5(b).hexdigest()


def short(s, n=160):
    s = str(s).replace("\n", "\\n")
    return s if len(s) <= n else s[: n - 3] + "..."


class Format:
    """How the file is written: indent, newline, trailing newline, ensure_ascii, BOM."""

    def __init__(self, raw):
        self.bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw[3:].decode("utf-8") if self.bom else raw.decode("utf-8")
        self.newline = "\r\n" if "\r\n" in text else "\n"
        self.text = text.replace("\r\n", "\n")
        self.trailing = self.text.endswith("\n")
        lines = self.text.split("\n")
        second = lines[1] if len(lines) > 1 else ""
        lead = second[: len(second) - len(second.lstrip())]
        self.indent = lead if lead.startswith("\t") else (len(lead) or None)
        self.ensure_ascii = all(ord(c) < 128 for c in self.text) and "\\u" in self.text

    def dump(self, data):
        out = json.dumps(data, indent=self.indent, ensure_ascii=self.ensure_ascii) + ("\n" if self.trailing else "")
        out = out.replace("\n", self.newline)
        return (b"\xef\xbb\xbf" if self.bom else b"") + out.encode("utf-8")

    def describe(self):
        ind = "tab" if self.indent == "\t" else f"{self.indent} spaces" if self.indent else "none"
        return (f"indent {ind}, {'CRLF' if self.newline == chr(13) + chr(10) else 'LF'}, "
                f"trailing newline {'yes' if self.trailing else 'no'}, "
                f"{'ASCII escapes' if self.ensure_ascii else 'UTF-8 text'}{', BOM' if self.bom else ''}")


def vname(v):
    return v.get("name") or v.get("id")


def holder(v, field):
    """(dict, key) holding a text field, or (None, reason)."""
    if field == "prompt":
        a = v.get("assertion") or {}
        t = a.get("type")
        if t in ("rubric", "agentic") and isinstance(a.get(t), dict) and "prompt" in a[t]:
            return a[t], "prompt"
        return None, f"has no prompt (assertion type {t!r})"
    if field in FIELDS:
        sect, key = FIELDS[field]
        d = v.get(sect)
        if isinstance(d, dict) and key in d:
            return d, key
        return None, f"has no {sect}.{key}"
    return None, f"unknown field {field!r} (use prompt, how or why, or op set with a path)"


def resolve_path(v, path, create):
    """(parent dict, key) for a dotted path inside a verifier; prompt/how/why accepted as names."""
    if path in TEXT_FIELDS:
        d, k = holder(v, path)
        if d is None:
            raise KeyError(k)
        return d, k
    parts = path.split(".")
    if parts[0] in ("name", "id"):
        raise KeyError("name/id cannot be changed: RL World joins feedback and calibration on it")
    d = v
    for p in parts[:-1]:
        if not isinstance(d, dict):
            raise KeyError(f"{p!r}: parent is not an object")
        if p not in d:
            if not create:
                raise KeyError(f"no key {p!r} (keys here: {', '.join(d)}); add \"create\": true to add it")
            d[p] = {}
        d = d[p]
    if not isinstance(d, dict):
        raise KeyError(f"{parts[-1]!r}: parent is not an object")
    if parts[-1] not in d and not create:
        raise KeyError(f"no key {parts[-1]!r} (keys here: {', '.join(d)}); add \"create\": true to add it")
    return d, parts[-1]


def closest(text, old):
    """Where `old` probably drifted: the best-matching passage of `text`, with the matching ratio."""
    if not text or not old:
        return None
    n = len(old)
    step = max(1, n // 6)
    best = (0.0, 0)
    for i in range(0, max(1, len(text) - n + 1), step):
        sm = difflib.SequenceMatcher(None, old, text[i:i + n], autojunk=False)
        if sm.real_quick_ratio() <= best[0] or sm.quick_ratio() <= best[0]:
            continue
        r = sm.ratio()
        if r > best[0]:
            best = (r, i)
    r, i = best
    for j in range(max(0, i - step), min(len(text) - n, i + step) + 1):
        rr = difflib.SequenceMatcher(None, old, text[j:j + n], autojunk=False).ratio()
        if rr > r:
            r, i = rr, j
    window = text[i:i + n]
    k = next((x for x in range(min(len(old), len(window))) if old[x] != window[x]), min(len(old), len(window)))
    return r, window, k


def sentences_before_fail(prompt):
    pre = prompt.split("FAIL", 1)[0]
    return pre.count(";"), len(re.findall(r"\band\b", pre)), len(re.findall(r"[.!?](?:\s|$)", pre))


def effective_weights(vs):
    """(ok, text) by the RL World library rule: unweighted verifiers share 1 - explicit sum equally."""
    ws = [(x.get("metadata") or {}).get("weight", x.get("weight")) for x in vs]
    given = [float(w) for w in ws if isinstance(w, (int, float)) and not isinstance(w, bool)]
    unweighted = sum(1 for w in ws if w is None)
    rest = 1 - sum(given)
    bad = [w for w in given if not 0 < w <= 1]
    ok = not bad and ((abs(rest) < 1e-6 and unweighted == 0) or (unweighted > 0 and rest > 1e-9))
    return ok, (f"{len(given)} explicit summing {sum(given):.6f}, {unweighted} unweighted sharing {max(rest, 0):.6f}"
                + (f", out of range {bad}" if bad else ""))


def weight_of(v):
    return (v.get("metadata") or {}).get("weight", v.get("weight"))


def removed_tokens(old, new):
    toks = []
    for rx in (MONEY, BIGNUM, IDENT, DATE):
        for m in rx.findall(old):
            m = m.strip()
            if m and m not in new and m not in toks:
                toks.append(m)
    return toks


def all_text(v):
    out = []
    for f in TEXT_FIELDS:
        d, k = holder(v, f)
        if d is not None and isinstance(d[k], str):
            out.append(d[k])
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("input", type=Path, help="verifier.json to start from (the export, or the last round's output)")
    ap.add_argument("edits", type=Path, help="edits.json (format in this script's docstring)")
    ap.add_argument("output", type=Path, help="where to write the edited verifier.json (a new file)")
    ap.add_argument("--original", type=Path, help="the export's verifier.json, to count changes against it")
    ap.add_argument("--changes", type=Path, help="write a markdown change table for the fix report here")
    ap.add_argument("--check", action="store_true", help="do everything except writing files")
    ap.add_argument("--overwrite", action="store_true", help="replace an existing output file")
    ap.add_argument("--allow-reformat", action="store_true",
                    help="write even though the input does not round-trip byte for byte (it will be reformatted)")
    a = ap.parse_args()

    problems, warnings, log, rows = [], [], [], []

    raw = a.input.read_bytes()
    fmt = Format(raw)
    data = json.loads(fmt.text)
    if fmt.dump(data) != raw:
        redo = fmt.dump(data).decode("utf-8-sig").split(fmt.newline)
        have = raw.decode("utf-8-sig").split(fmt.newline)
        i = next((i for i, (x, y) in enumerate(zip(redo, have)) if x != y), min(len(redo), len(have)))
        msg = (f"input does not round-trip byte for byte (first difference at line {i + 1}: file "
               f"{short(have[i] if i < len(have) else '<end>', 100)!r}, rewritten "
               f"{short(redo[i] if i < len(redo) else '<end>', 100)!r})")
        (warnings if a.allow_reformat else problems).append(
            msg + ("" if a.allow_reformat else "; pass --allow-reformat only if a reformatted file is acceptable"))
    if a.changes:
        cr = a.changes.resolve()
        if cr in (a.input.resolve(), a.output.resolve(), a.edits.resolve()):
            problems.append(f"--changes {a.changes} is the input, the output or the edits file")
        elif a.changes.exists() and not a.overwrite and not a.check:
            problems.append(f"{a.changes} exists: pass --overwrite, or name this round's change table differently")
    if a.output.resolve() == a.input.resolve():
        problems.append("output is the input: write each round to a new file and keep the old one")
    elif a.output.exists() and not a.overwrite and not a.check:
        problems.append(f"{a.output} exists: pass --overwrite, or write this round to a new file")

    spec = json.loads(a.edits.read_text(encoding="utf-8"))
    edits = spec.get("edits") if isinstance(spec, dict) else None
    if not isinstance(edits, list) or not edits:
        problems.append("edits.json needs a non-empty \"edits\" list")
        edits = []
    keep_how = spec.get("keep_how", {}) if isinstance(spec, dict) else {}
    sweep_terms = list(spec.get("sweep", [])) if isinstance(spec, dict) else []

    before = copy.deepcopy(data)
    vs = data.get("verifiers", [])
    all_names = [vname(v) for v in vs]
    if any(n is None for n in all_names):
        problems.append(f"{sum(1 for n in all_names if n is None)} verifier(s) in the input have no name: an edit "
                        f"cannot target them safely")
    dups = sorted({n for n in all_names if n is not None and all_names.count(n) > 1})
    if dups:
        problems.append(f"duplicate verifier names in the input: {', '.join(dups)} (RL World joins on the name)")
    by = {vname(v): v for v in vs if vname(v) is not None}
    names = list(by)
    touched = {}  # verifier name -> set of changed areas
    added, deleted = [], []

    def targets(e, field):
        if "verifiers" in e:
            sel = e["verifiers"]
            if sel == "*":
                return [n for n in names if field is None or holder(by[n], field)[0] is not None], True
            if not isinstance(sel, list) or not sel:
                return None, True
            return list(sel), True
        return [e.get("verifier")], False

    for idx, e in enumerate(edits, 1):
        if not isinstance(e, dict):
            problems.append(f"[edit {idx}] is not an object")
            continue
        ref = e.get("ref") or f"edit {idx}"
        op = e.get("op", "replace")
        field = e.get("field", "prompt") if op in ("replace", "insert") else None
        tag = f"[{ref}]"
        extra = set(e) - COMMON_KEYS - OP_KEYS.get(op, set())
        if extra or op not in OP_KEYS:
            problems.append(f"{tag} " + (f"unknown op {op!r} (replace, insert, set, split or delete)" if op not in OP_KEYS
                                         else f"unknown key(s) {', '.join(sorted(extra))} for op {op} "
                                              f"(allowed: {', '.join(sorted(COMMON_KEYS | OP_KEYS[op]))})"))
            continue
        if ("verifier" in e) == ("verifiers" in e):
            problems.append(f"{tag} give exactly one of \"verifier\" (one name) or \"verifiers\" (a list, or \"*\")")
            continue
        if op in ("insert", "split", "delete") and "verifiers" in e:
            problems.append(f"{tag} {op} works on one \"verifier\"")
            continue
        tlist, multi = targets(e, field)
        if tlist is None:
            problems.append(f"{tag} \"verifiers\" must be a non-empty list of names, or \"*\"")
            continue
        unknown = [n for n in tlist if n not in by]
        if unknown:
            for n in unknown:
                near = difflib.get_close_matches(str(n), names, n=3, cutoff=0.5)
                problems.append(f"{tag} no verifier named {n!r}" + (f" (closest: {', '.join(near)})" if near else ""))
            continue

        if op == "replace":
            old, new = e.get("old"), e.get("new")
            if not isinstance(old, str) or not old or not isinstance(new, str):
                problems.append(f"{tag} replace needs non-empty \"old\" and a string \"new\"")
                continue
            if old == new:
                problems.append(f"{tag} old and new are the same")
                continue
            found = {}
            for n in tlist:
                d, k = holder(by[n], field)
                if d is None:
                    problems.append(f"{tag} {n} {k}")  # "*" lists only verifiers that have the field
                    continue
                found[n] = (d, k, d[k].count(old))
            if not found:
                problems.append(f"{tag} no target verifier has a {field}")
                continue
            total = sum(c for _, _, c in found.values())
            want = e.get("total") if multi else e.get("count", 1)
            if multi and want is None:
                problems.append(f"{tag} an edit over several verifiers needs \"total\" (found {total} matches in "
                                f"{sum(1 for *_, c in found.values() if c)} verifiers)")
                continue
            if not isinstance(want, int) or isinstance(want, bool) or want < 1:
                problems.append(f"{tag} {'total' if multi else 'count'} must be a whole number of 1 or more (got {want!r})")
                continue
            if total != want:
                msg = f"{tag} {field} text found {total} times, expected {want}: {short(old, 120)!r}"
                if total == 0 and not multi:
                    n = tlist[0]
                    d, k, _ = found[n]
                    if " ".join(old.split()) in " ".join(d[k].split()):
                        msg += "\n    it matches only with whitespace collapsed: copy the exact spacing from the file"
                    else:
                        c = closest(d[k], old)
                        if c:
                            r, window, at = c
                            msg += (f"\n    closest passage ({r:.0%} alike, differs from character {at}): "
                                    f"{short(window, 220)!r}")
                    elsewhere = [f"{m}.{f}" for m in names for f in TEXT_FIELDS
                                 if (m, f) != (n, field) and holder(by[m], f)[0] is not None
                                 and old in holder(by[m], f)[0][holder(by[m], f)[1]]]
                    if elsewhere:
                        msg += f"\n    the exact text is in: {', '.join(elsewhere[:5])}"
                elif total > want and not multi:
                    msg += " (lengthen old until it is unique, or give \"count\")"
                problems.append(msg)
                continue
            for n, (d, k, c) in found.items():
                if c:
                    d[k] = d[k].replace(old, new)
                    # a how edit made with "*" is cosmetic: it does not count as updating a verifier's justification
                    touched.setdefault(n, set()).add("how*" if field == "how" and e.get("verifiers") == "*" else field)
                    rows.append((ref, n, field, f"{short(old, 300)} → {short(new, 300)}"))
            hit = [n for n, (*_, c) in found.items() if c]
            log.append(f"APPLIED {tag} replace {field} in {', '.join(hit) if len(hit) <= 3 else f'{len(hit)} verifiers'}"
                       f" ({total} match{'es' if total != 1 else ''})")
            if not e.get("no_sweep"):
                for t in removed_tokens(old, new):
                    if t not in sweep_terms:
                        sweep_terms.append(t)

        elif op == "insert":
            text = e.get("text")
            if ("after" in e) == ("before" in e):
                problems.append(f"{tag} insert needs exactly one of \"after\" or \"before\"")
                continue
            anchor, where = (e["after"], "after") if "after" in e else (e.get("before"), "before")
            if not isinstance(text, str) or not text or not isinstance(anchor, str) or not anchor or multi:
                problems.append(f"{tag} insert needs one \"verifier\", \"after\" or \"before\", and \"text\"")
                continue
            n = tlist[0]
            d, k = holder(by[n], field)
            if d is None:
                problems.append(f"{tag} {n} {k}")
                continue
            c = d[k].count(anchor)
            if c != 1:
                msg = f"{tag} anchor found {c} times in {n}.{field}, expected 1: {short(anchor, 120)!r}"
                if c == 0:
                    cl = closest(d[k], anchor)
                    if cl:
                        msg += f"\n    closest passage ({cl[0]:.0%} alike): {short(cl[1], 220)!r}"
                problems.append(msg)
                continue
            i = d[k].index(anchor) + (len(anchor) if where == "after" else 0)
            d[k] = d[k][:i] + text + d[k][i:]
            touched.setdefault(n, set()).add(field)
            rows.append((ref, n, field, f"+ {short(text, 400)} ({where} {short(anchor, 60)!r})"))
            log.append(f"APPLIED {tag} insert into {n}.{field} {where} the anchor")

        elif op == "set":
            path = e.get("path")
            if not path or "value" not in e:
                problems.append(f"{tag} set needs \"path\" and \"value\"")
                continue
            for n in tlist:
                try:
                    d, k = resolve_path(by[n], path, e.get("create", False))
                except KeyError as exc:
                    problems.append(f"{tag} {n}: path {path!r}: {exc.args[0]}")
                    continue
                oldv = d.get(k, "<absent>")
                if oldv == e["value"]:
                    problems.append(f"{tag} {n}.{path} already has that value")
                    continue
                d[k] = copy.deepcopy(e["value"])
                head = path.split(".")[0]
                area = path if path in TEXT_FIELDS else {"metadata": "metadata", "source": "source",
                                                          "assertion": "assertion"}.get(head, head)
                if path == "metadata.how_justification":
                    area = "how"
                elif path == "metadata.why_justification":
                    area = "why"
                elif path == "metadata.weight":
                    area = "weight"
                touched.setdefault(n, set()).add(area)
                rows.append((ref, n, path, f"{short(json.dumps(oldv, ensure_ascii=False), 200)} → "
                                           f"{short(json.dumps(e['value'], ensure_ascii=False), 200)}"))
                log.append(f"APPLIED {tag} set {n}.{path}")
        elif op == "split":
            n, new_name = tlist[0], e.get("new_name")
            parent = by[n]
            if not isinstance(new_name, str) or not new_name.startswith(n + "_") or len(new_name) <= len(n) + 1:
                problems.append(f"{tag} split needs \"new_name\" = {n}_<suffix> (ids stay stable: the parent keeps "
                                f"its name, the new part shares its stem)")
                continue
            if new_name in by:
                problems.append(f"{tag} {new_name} already exists")
                continue
            pw = weight_of(parent)
            ws = e.get("weights")
            if pw is not None:
                if (not isinstance(ws, dict) or set(ws) != {n, new_name}
                        or not all(isinstance(x, (int, float)) and not isinstance(x, bool) and 0 < x <= 1 for x in ws.values())
                        or abs(sum(ws.values()) - float(pw)) > 1e-9):
                    problems.append(f"{tag} split of a weighted verifier needs \"weights\": {{{n!r}: w1, {new_name!r}: "
                                    f"w2}} with w1 + w2 = its weight {pw}")
                    continue
            elif ws:
                problems.append(f"{tag} {n} has no weight (equal shares): leave out \"weights\"")
                continue
            child = copy.deepcopy(parent)
            child["name" if "name" in child else "id"] = new_name
            if pw is not None:
                parent["metadata"]["weight"], child["metadata"]["weight"] = ws[n], ws[new_name]
            vs.insert(vs.index(parent) + 1, child)
            by[new_name] = child
            names.insert(names.index(n) + 1, new_name)
            added.append(new_name)
            touched.setdefault(n, set()).add("weight" if pw is not None else "split")
            touched.setdefault(new_name, set()).add("added")
            rows.append((ref, n, "split", f"-> {n} + {new_name}" + (f" (weights {ws[n]} + {ws[new_name]})" if pw is not None else "")))
            log.append(f"APPLIED {tag} split {n} -> {n}, {new_name}")

        elif op == "delete":
            n = tlist[0]
            v = by[n]
            w = weight_of(v)
            to = e.get("move_weight_to") or []
            if w is not None:
                bad = [m for m in to if m not in by or m == n or weight_of(by[m]) is None]
                if not to or bad:
                    problems.append(f"{tag} deleting weighted {n} needs \"move_weight_to\": other weighted verifiers "
                                    f"of the same deliverable" + (f" (not usable: {', '.join(map(str, bad))})" if bad else ""))
                    continue
                share = sum(float(weight_of(by[m])) for m in to)
                for m in to:
                    by[m]["metadata"]["weight"] = float(weight_of(by[m])) + float(w) * float(weight_of(by[m])) / share
                    touched.setdefault(m, set()).add("weight")
            elif to:
                problems.append(f"{tag} {n} has no weight (equal shares): leave out \"move_weight_to\"")
                continue
            vs.remove(v)
            del by[n]
            names.remove(n)
            deleted.append(n)
            touched.pop(n, None)
            rows.append((ref, n, "delete", "removed" + (f"; weight {w} moved to {', '.join(to)}" if w is not None else "")))
            log.append(f"APPLIED {tag} delete {n}")

    # Grading changed but how_justification did not: the QC pipeline grades it as the agentic criterion text, and the
    # validator flags it, so decide it here (12 warnings on #38, 10 on #17).
    for n, areas in touched.items():
        grading = areas & {"prompt", "source", "assertion"}
        if n in added and grading and "how" not in areas:
            problems.append(f"{n}: a split part needs its own how_justification (field how), not the parent's")
            continue
        if grading and "how" not in areas and n not in keep_how and "*" not in keep_how:
            problems.append(f"{n}: {', '.join(sorted(grading))} changed but how_justification did not; edit it "
                            f"(field how) or give a reason in keep_how")
    for n in keep_how:
        if n != "*" and n not in by:
            problems.append(f"keep_how names {n!r}, which is not a verifier")

    old_by = {vname(v): v for v in before.get("verifiers", [])}
    for n in touched:
        v, ov = by.get(n), old_by.get(n)
        if v is None:
            continue
        md, omd = v.get("metadata") or {}, (ov or {}).get("metadata") or {}
        for key in ("how_justification", "why_justification", "importance", "grading_role"):
            if key in omd and key not in md:
                problems.append(f"{n}: metadata.{key} was removed (set the field itself, not the whole metadata object)")
        w = md.get("weight", v.get("weight"))
        if w is not None and (isinstance(w, bool) or not isinstance(w, (int, float))):
            problems.append(f"{n}: weight {w!r} is not a number")
        for f in TEXT_FIELDS:
            d, k = holder(v, f)
            if d is not None and (not isinstance(d[k], str) or not d[k].strip()):
                problems.append(f"{n}: {f} must stay non-empty text (got {d[k]!r})")
    if any("weight is not a number" in x for x in problems):
        ok_b, txt_b, ok_a, txt_a = True, "(not computed)", True, "(not computed: a weight is not a number)"
    else:
        ok_b, txt_b = effective_weights(before.get("verifiers", []))
        ok_a, txt_a = effective_weights(vs)
    if not ok_a:
        (problems if any("weight" in s for s in touched.values()) or ok_b else warnings).append(
            f"effective weights do not sum to 1 after the edits ({txt_a})" + ("" if ok_b else "; the input already did not"))

    # Warnings on added text
    prefixes = {str(n).split("_")[0] for n in names}
    for n in touched:
        v, ov = by.get(n), old_by.get(n)
        if v is None:
            continue
        ov = ov or {"metadata": {}, "assertion": {}}  # a split part: every word of it is new
        d, k = holder(v, "prompt")
        od, ok_ = holder(ov, "prompt")
        if d is not None and od is not None and d[k] != od[ok_]:
            sb, ab, nb = sentences_before_fail(od[ok_])
            sa, aa, na = sentences_before_fail(d[k])
            bits = []
            if sa > sb:
                bits.append(f"';' {sb}->{sa}")
            if aa > ab:
                bits.append(f"'and' {ab}->{aa}")
            if na > nb:
                bits.append(f"sentences {nb}->{na}")
            if bits:
                warnings.append(f"{n}: before the first FAIL, {', '.join(bits)}; the clause counter (G7) may count "
                                f"more requirements: fold added words into an existing sentence, without ';' or 'and'")
            pins = len(PINS.findall(d[k])) - len(PINS.findall(od[ok_]))
            if pins > 0:
                warnings.append(f"{n}: {pins} new placement wording(s) "
                                f"({', '.join(sorted(set(PINS.findall(d[k])) - set(PINS.findall(od[ok_]))))[:120]}): "
                                f"pin a place only when the instruction fixes it")
        for f in TEXT_FIELDS:
            d, k = holder(v, f)
            od, ok_ = holder(ov, f)
            if d is None or not isinstance(d[k], str) or (od is not None and d[k] == od[ok_]):
                continue
            newtxt, oldtxt = d[k], (od[ok_] if od is not None and isinstance(od[ok_], str) else "")
            if f in ("how", "why") and (";" in newtxt or len(re.findall(r"[.!?](?:\s|$)", newtxt.strip())) > 1):
                warnings.append(f"{n}.{f}: keep a justification to one plain sentence with no ';' (the pipeline reads "
                                f"how_justification as an agentic verifier's criterion text)")
            # only tokens shaped like this file's names (same first word: memo_, workbook_, deck_ ...), so data
            # column names such as component_risk_score are not reported
            ghosts = sorted({t for t in SNAKE.findall(newtxt) if t not in by and t not in oldtxt
                             and t.split("_")[0] in prefixes})
            if ghosts:
                warnings.append(f"{n}.{f}: names {', '.join(ghosts)}, not a verifier in this file (a reference to a "
                                f"verifier that does not exist confuses judges and reviewers)")
            if newtxt.count("\\") > oldtxt.count("\\") or re.search(r"[\x00-\x08\x0b-\x1f]", newtxt):
                warnings.append(f"{n}.{f}: new text has a backslash or control character; check for an escape slip")

    # Sweep: the same figure or ID in verifiers this run did not edit (#22's $148,000, #36's workbook twin)
    sweep_lines = []
    for t in sweep_terms:
        hits = [n for n in names if t in all_text(by[n])]
        if not hits:
            continue
        rest = [n for n in hits if n not in touched]
        still = [n for n in hits if n in touched]
        line = f"  {t!r}: " + (f"not edited: {', '.join(rest)}" if rest else "")
        if still:
            line += ("; " if rest else "") + f"edited, still has it: {', '.join(still)}"
        sweep_lines.append(line)

    print(f"input  {a.input}  md5 {md5(raw)}  ({fmt.describe()}, {len(vs)} verifiers)")
    for line in log:
        print(line)
    if touched:
        print(f"\n## Changed verifiers ({len(touched)})")
        for n in deleted:
            print(f"- {n}: deleted")
        for n in names:
            if n not in touched:
                continue
            if n in added:
                print(f"+ {n}: added (split)")
                continue
            ov, v = old_by[n], by[n]
            parts = []
            for f in TEXT_FIELDS:
                d, k = holder(v, f)
                od, ok_ = holder(ov, f)
                if d is not None and od is not None and d[k] != od[ok_]:
                    parts.append(f"{f} {len(str(od[ok_] or ''))}->{len(str(d[k] or ''))} chars")
            for area in sorted(touched[n] - set(TEXT_FIELDS) - {"weight", "how*"}):
                parts.append(f"{area} changed")
            if weight_of(ov) != weight_of(v):
                parts.append(f"weight {weight_of(ov)} -> {weight_of(v)}")
            kh = keep_how.get(n) or (keep_how.get("*") if "how" not in touched[n] else None)
            if kh and "how" not in touched[n]:
                parts.append(f"how kept: {kh}")
            print(f"~ {n}: {'; '.join(parts)}")
    if a.original:
        orig = {vname(v): v for v in json.loads(a.original.read_text(encoding="utf-8-sig")).get("verifiers", [])}
        diff = [n for n in names if by.get(n) != orig.get(n)]
        gone = [n for n in orig if n not in by]
        print(f"\nagainst the original export: {len(diff)} of {len(names)} verifiers differ"
              + (f"; missing from this file: {', '.join(gone)}" if gone else ""))
    print(f"weights: before {txt_b}; after {txt_a}")
    if sweep_lines:
        print("\n## SWEEP: figures and IDs from the edits, where they still appear (settle each one)")
        print("\n".join(sweep_lines))
    for w in warnings:
        print(f"WARNING: {w}")
    for p in problems:
        print(f"PROBLEM: {p}")

    if problems:
        print(f"APPLY: FAILED ({len(problems)} problem{'s' if len(problems) != 1 else ''}), nothing written")
        return 1
    out = fmt.dump(data)
    if a.check:
        print(f"output (not written, --check) md5 {md5(out)}")
    else:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_bytes(out)
        print(f"output {a.output}  md5 {md5(out)}")
        if a.changes:
            md = [f"Edits: {a.edits.name}. Input md5 {md5(raw)}, output md5 {md5(out)}.", "",
                  "| Ref | Verifier | Field | Change |", "|---|---|---|---|"]
            md += [f"| {r} | {n} | {f} | {c.replace('|', '/')} |" for r, n, f, c in rows]
            kept = [f"- {n}: how_justification kept: {r}" for n, r in keep_how.items()]
            a.changes.write_text("\n".join(md + ([""] + kept if kept else [])) + "\n", encoding="utf-8")
            print(f"changes table {a.changes}")
    print(f"APPLY: OK ({len(edits)} edit{'s' if len(edits) != 1 else ''}, {len(touched)} verifier"
          f"{'s' if len(touched) != 1 else ''} changed{f', {len(warnings)} warnings' if warnings else ''})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
