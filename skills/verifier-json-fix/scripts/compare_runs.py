"""compare_runs.py <old rev> <new rev>: per verifier, pass/fail and votes for oracle, terminus, codex, nop in each run."""
import sys, os, glob, json
def load(rev):
    out = {}
    for e in sorted(glob.glob(os.path.join(rev, 'evaluations', 'eval_*'))):
        tag = 'oracle' if 'oracle' in e else 'terminus' if 'terminus' in e else 'codex' if 'codex' in e else 'nop' if 'nop' in e else '?'
        rp = glob.glob(os.path.join(e, '**', 'verifier-report.json'), recursive=True)
        if not rp: continue
        r = json.load(open(rp[0], encoding='utf-8'))
        for a in r.get('assertion_results', []):
            res = a.get('result', {}); ev = res.get('evaluation') or {}
            cell = ('P' if res.get('success') else 'F') + (f"{ev.get('true_count')}/{(ev.get('true_count') or 0) + (ev.get('false_count') or 0)}" if ev.get('attempts') else '')
            out.setdefault(a['name'], {}).setdefault(tag, []).append(cell)
    return out
old, new = load(sys.argv[1]), load(sys.argv[2])
print(f"{'verifier':72s} | {'OLD oracle/terminus/codex':28s} | {'NEW oracle/terminus/codex':28s}")
for v in new:
    o = old.get(v, {}); n = new[v]
    fmt = lambda d: ' '.join(','.join(d.get(k, ['-'])) for k in ('oracle', 'terminus', 'codex'))
    print(f"{v:72s} | {fmt(o):28s} | {fmt(n):28s}")
