export const meta = {
  name: 'omega-final-review',
  description: 'Project Omega Final Review: one shared evidence ledger, two independent reviews, judges only where verdicts are in doubt, a targeted "are you sure" pass, then verdict-locked answers checked against Auto QC',
  whenToUse: 'Run from /omega-final-review once the package, the pasted Final Review screen and any prior notes are saved to files.',
  phases: [
    { title: 'Ledger', detail: 'match the screen, list every field, build one shared evidence ledger' },
    { title: 'Review', detail: 'two independent reviews from the ledger' },
    { title: 'Judge', detail: 'judges only on contested fields; two on any task-ending verdict' },
    { title: 'Challenge', detail: 'one targeted "are you sure?" pass' },
    { title: 'Write and check', detail: 'verdict-locked template F answers and one Auto QC pre-check' },
  ],
}

// args: { pack_dir, screen_file, prior_notes_file?, scratch_dir, user_notes? }
const A = args || {}
const S = v => (v == null ? '' : typeof v === 'string' ? v : JSON.stringify(v))
const LEDGER = `${S(A.scratch_dir)}/frg_ledger.md`
const BRIEF = 'skills/project-omega-finance-review/references/11_frg_brief.md'
const CTX = `Task pack: ${S(A.pack_dir)}. Pasted Final Review screen: ${S(A.screen_file)}. Prior notes: ${A.prior_notes_file ? S(A.prior_notes_file) : 'not supplied (the fix list is inferred)'}. ${A.user_notes ? 'User notes: ' + S(A.user_notes) + '.' : ''}
Read ${BRIEF} first; it replaces the full rulebook for this job. The shared evidence ledger is ${LEDGER}: rely on it, and open a task file only to confirm or extend a fact it does not settle. Never write into the repository.`

async function retry(make) {
  for (let i = 0; i < 2; i++) { const r = await make(i); if (r) return r }
  return null
}

phase('Ledger')
const INVENTORY = {
  type: 'object',
  properties: {
    mismatch: { type: 'boolean' }, mismatch_reason: { type: 'string' },
    task_id: { type: 'string' }, revision: { type: 'string' },
    fields: { type: 'array', items: { type: 'object', properties: { field: { type: 'string' }, kind: { type: 'string', enum: ['task_design', 'source', 'prompt', 'verifier', 'golden', 'other'] } }, required: ['field', 'kind'] } },
    missing_inputs: { type: 'array', items: { type: 'string' } },
  },
  required: ['mismatch', 'fields', 'missing_inputs'],
}
const inv = await retry(i => agent(`${CTX}

You build the shared evidence ledger that every later agent will read instead of the raw package, so do the expensive reading once and well.
1. Match the upload to the pasted screen (task_id, revision, deliverable paths, verifier names, field count); report any mismatch.
2. List every field the screen asks for, in screen order, with its exact on-screen name and kind (each source file, the prompt, each verifier and each golden deliverable is its own field).
3. Write ${LEDGER} (create the directory if needed) with, in this order: the instruction's operative clauses quoted with their section; the task design's planned anomalies; per source file its cover or notes text and the facts the task turns on, with locators; the golden's key figures recomputed from source with the formula chain and cell references (say whether you recalculated or read cached values); then per verifier its criterion text verbatim, the figures and clauses it depends on, and whether the golden passes it, quoting the deciding golden cell or sentence; and the prior fixes claimed, each marked holds or does not hold.
Keep the ledger factual; give no verdicts.`, { label: `ledger#${i}`, phase: 'Ledger', schema: INVENTORY, effort: 'high' }))
if (!inv) return { stop: true, reason: 'inventory failed' }
if (inv.mismatch) return { stop: true, reason: 'mismatch: ' + inv.mismatch_reason }
const NAMES = inv.fields.map(f => f.field)
const KIND = {}
for (const f of inv.fields) KIND[f.field] = f.kind
const FIELD = { type: 'string', enum: NAMES }
const fieldList = inv.fields.map((f, i) => `${i + 1}. ${f.field} (${f.kind})`).join('\n')
log(`${NAMES.length} fields; ledger at ${LEDGER}`)

const VP = {
  field: FIELD,
  verdict: { type: 'string', enum: ['APPROVE', 'REJECT', 'PENDING INPUT'] },
  ground: { type: 'string' },
  evidence: { type: 'string' },
  counterexample: { type: 'string' },
  fix: { type: 'string' },
  optional_note: { type: 'string' },
  close_call: { type: 'boolean' },
}
const VERDICT = { type: 'object', properties: VP, required: ['field', 'verdict', 'ground', 'evidence', 'close_call'] }
const JUDGED = { type: 'object', properties: { ...VP, reason: { type: 'string' } }, required: ['field', 'verdict', 'ground', 'evidence', 'close_call', 'reason'] }
const REVIEW = {
  type: 'object',
  properties: {
    verdicts: { type: 'array', items: VERDICT },
    suspects: { type: 'array', items: { type: 'object', properties: { field: FIELD, defect: { type: 'string' } }, required: ['field', 'defect'] }, description: 'External QC-lens suspicions on fields you approved' },
    escalations: { type: 'array', items: { type: 'string' } },
  },
  required: ['verdicts', 'suspects', 'escalations'],
}

phase('Review')
const [revA, revB] = await parallel([
  () => retry(i => agent(`${CTX}

Independent reviewer A. Give a verdict on every field, in screen order, under the bar in the brief. Mark close_call on anything you are not certain of. Fields:
${fieldList}`, { label: `review:A#${i}`, phase: 'Review', schema: REVIEW, effort: 'high' })),
  () => retry(i => agent(`${CTX}

Independent reviewer B. Start from the golden and the verifiers, then the prompt, sources and Task Design. Give a verdict on every field. Also hunt the defects External QC kept finding after Final Review approvals (a PASS condition the prompt never asks for, a single accepted reading where another is defensible, golden wording that fails its own FAIL clause, a pass case breaching the governing standard, one defect failing two verifiers) and list any you suspect on a field you approved under suspects. Mark close_call on anything you are not certain of. Fields:
${fieldList}`, { label: `review:B#${i}`, phase: 'Review', schema: REVIEW, effort: 'high' })),
])
if (!revA && !revB) return { stop: true, reason: 'both reviews failed' }

const by = {}
for (const n of NAMES) by[n] = { a: null, b: null, suspects: [] }
for (const r of [revA, revB]) if (r) {
  for (const v of (r.verdicts || [])) if (by[v.field]) by[v.field][r === revA ? 'a' : 'b'] = v
  for (const s of (r.suspects || [])) if (by[s.field]) by[s.field].suspects.push(s)
}

const final = {}
const changes = []
const unsettled = []
const contested = []
for (const n of NAMES) {
  const x = by[n]
  const agree = x.a && x.b && x.a.verdict === x.b.verdict && !x.a.close_call && !x.b.close_call && !x.suspects.length
  if (agree && x.a.verdict === 'APPROVE') final[n] = { ...x.a, reason: 'both reviewers approved' }
  else contested.push(n)
}
log(`${contested.length} of ${NAMES.length} fields need a judge`)

const terminal = (n, r) => r && r.verdict === 'REJECT' && KIND[n] !== 'verifier'
function caseFor(n, extra) {
  const x = by[n]
  return JSON.stringify({ field: n, kind: KIND[n], reviewer_a: x.a, reviewer_b: x.b, suspects: x.suspects, current: final[n] || null, doubt: extra || null }, null, 1)
}
async function judge(n, tag, extra, note) {
  return retry(i => agent(`${CTX}

Judge (${tag}) for field "${n}". The reviewers' positions below are the two sides of the case. Decide the verdict under the bar by checking the deciding facts in the ledger (and the task file only if the ledger does not settle them). Weigh both errors: shipping a wrong task and terminating a correct one.${note ? ' ' + note : ''}

Case:
${caseFor(n, extra)}`, { label: `judge:${n}:${tag}#${i}`, phase: 'Judge', schema: JUDGED, effort: 'high' }))
}
// One judge per contested field. A second independent judge confirms any task-ending REJECT and any verdict that overturns both reviewers; a third settles a split.
async function decide(n, tag, extra) {
  const j1 = await judge(n, tag + '.1', extra)
  if (!j1) return null
  const x = by[n]
  const overturn = x.a && x.b && x.a.verdict === x.b.verdict && x.a.verdict !== j1.verdict
  const moved = final[n] && final[n].verdict !== j1.verdict
  if (!terminal(n, j1) && !overturn && !moved) return j1
  const j2 = await judge(n, tag + '.2', extra, 'Another judge has ruled; decide independently without deferring to it.')
  if (!j2) return null
  if (j2.verdict === j1.verdict) return j1
  return judge(n, tag + '.3', extra, `Two judges split. Judge 1: ${JSON.stringify(j1)}. Judge 2: ${JSON.stringify(j2)}. Settle it on the deciding fact and name that fact.`)
}
function apply(n, r, tag) {
  if (!r) { unsettled.push(n); return }
  const before = final[n] ? final[n].verdict : null
  const x = by[n]
  if (before && before !== r.verdict) changes.push(`${n}: ${before} → ${r.verdict} (${tag}): ${r.reason}`)
  else if (!before && x.a && x.b && x.a.verdict === x.b.verdict && x.a.verdict !== r.verdict) changes.push(`${n}: both reviewers ${x.a.verdict}, judged ${r.verdict}: ${r.reason}`)
  final[n] = r
}

phase('Judge')
const judged = await parallel(contested.map(n => () => decide(n, 'j').then(r => ({ n, r }))))
for (const x of judged) if (x) apply(x.n, x.r, 'judge')

phase('Challenge')
const CHALLENGE = { type: 'object', properties: { doubts: { type: 'array', items: { type: 'object', properties: { field: FIELD, claim: { type: 'string' }, evidence: { type: 'string' } }, required: ['field', 'claim', 'evidence'] } } }, required: ['doubts'] }
const focus = NAMES.filter(n => contested.includes(n) || (final[n] && final[n].verdict === 'REJECT'))
if (focus.length) {
  const ch = await retry(i => agent(`${CTX}

You are the user asking "are you sure?". Check these verdicts, especially every REJECT (a false defect terminates a correct task when it is not a verifier) and every close call, against the ledger. Report only doubts backed by a fact the judges missed; restating an argument already in the case is not a doubt.

Verdicts:
${JSON.stringify(focus.map(n => final[n] || { field: n, verdict: 'unsettled' }), null, 1)}`, { label: `challenge#${i}`, phase: 'Challenge', schema: CHALLENGE, effort: 'high' }))
  const grouped = {}
  for (const d of ((ch && ch.doubts) || [])) (grouped[d.field] = grouped[d.field] || []).push(d)
  const names = Object.keys(grouped)
  log(`challenge raised ${names.length} evidenced doubts`)
  const res = await parallel(names.map(n => () => decide(n, 'c', grouped[n]).then(r => ({ n, r }))))
  for (const x of res) if (x) apply(x.n, x.r, 'challenge')
}

phase('Write and check')
const ordered = NAMES.map(n => final[n] || { field: n, verdict: 'PENDING INPUT', ground: 'not settled', evidence: '', close_call: true })
const WRITE = {
  type: 'object',
  properties: {
    lead: { type: 'string' },
    entries: { type: 'array', items: { type: 'object', properties: { field: FIELD, verdict: { type: 'string', enum: ['APPROVE', 'REJECT', 'PENDING INPUT'] }, text: { type: 'string' } }, required: ['field', 'verdict', 'text'] } },
    optional_line: { type: 'string' },
    escalations: { type: 'array', items: { type: 'string' } },
    overall: { type: 'string' },
  },
  required: ['lead', 'entries', 'overall'],
}
const writeBrief = `Write the platform-ready Final Review answers from the settled verdicts, using template F of skills/project-omega-finance-review/references/06_output_templates.md and rules C1–C8 in SKILL.md (read only those sections): a one-line lead; one entry per field in this order, each starting "<field> — <VERDICT>."; a short paragraph for Task Design, each source, the prompt and each golden deliverable; one line per verifier, with a note under each REJECT (the defect, evidence with a quoted locator, the counterexample, "Fix:" with the exact change; make fixes that touch the same figure agree); one "Optional:" line; escalation lines; the Overall line. Copy every verdict exactly.`
function codeCheck(w) {
  const p = [], seen = {}
  for (const e of (w.entries || [])) {
    if (seen[e.field]) p.push(`${e.field}: entry written twice`)
    seen[e.field] = 1
    if (final[e.field] && e.verdict !== final[e.field].verdict) p.push(`${e.field}: says ${e.verdict}, settled verdict is ${final[e.field].verdict}`)
  }
  for (const n of NAMES) if (!seen[n]) p.push(`${n}: no entry`)
  return p
}
function compose(w) {
  const t = {}
  for (const e of (w.entries || [])) t[e.field] = e.text
  return [w.lead, ...NAMES.map(n => t[n]), w.optional_line, ...(w.escalations || []), w.overall].filter(Boolean).join('\n\n')
}
let w = await retry(i => agent(`${CTX}

${writeBrief}

Settled verdicts:
${JSON.stringify(ordered, null, 1)}
Escalations: ${JSON.stringify([...((revA && revA.escalations) || []), ...((revB && revB.escalations) || [])])}
Missing inputs: ${JSON.stringify(inv.missing_inputs)}`, { label: `writer#${i}`, phase: 'Write and check', schema: WRITE, effort: 'medium' }))
if (!w) return { stop: true, reason: 'writer failed', verdicts: ordered, changes }

const QC = { type: 'object', properties: { problems: { type: 'array', items: { type: 'string' } } }, required: ['problems'] }
let problems = []
for (let k = 1; k <= 2; k++) {
  const qc = await retry(i => agent(`${CTX}

Auto QC pre-check. Test these answers against the five Final Review Auto QC checks in section 4 of skills/project-omega-finance-review/references/09_platform_checks_and_auto_qc.md (cross-item consistency, groundedness, actionability, coverage completeness, decision/note coherence). Check quotes and figures against the ledger. List each concrete problem with the field and the exact change, or none.

Answers:
${compose(w)}`, { label: `autoqc:${k}#${i}`, phase: 'Write and check', schema: QC, effort: 'medium' }))
  problems = [...codeCheck(w), ...((qc && qc.problems) || (qc ? [] : ['pre-check failed to run']))]
  if (!problems.length || k === 2) break
  const rev = await retry(i => agent(`${CTX}

Fix every problem below in these Final Review answers, changing wording only; every verdict stays as settled. Return every entry.

Problems:
${problems.join('\n')}

Settled verdicts: ${JSON.stringify(NAMES.map(n => [n, final[n] ? final[n].verdict : 'PENDING INPUT']))}

Answers:
${JSON.stringify(w)}`, { label: `revise#${i}`, phase: 'Write and check', schema: WRITE, effort: 'medium' }))
  if (rev) w = rev
}

return { answers: compose(w), changes, unsettled, qc_problems: problems, judged: contested.length, settled_by_both_reviewers: NAMES.length - contested.length }
