export const meta = {
  name: 'omega-external-qc',
  description: 'Project Omega External QC: one shared evidence ledger with the run snapshot, two independent verdicts per item, judges only where verdicts are in doubt, an "are you sure" pass, then verdict-locked template H answers and a fix plan for the verifier-json-fix skill',
  whenToUse: 'Run from /omega-external-qc once the fresh RL World download, the QC feedback file and the runs zip are saved.',
  phases: [
    { title: 'Ledger', detail: 'match the screen, list every item, build one shared evidence ledger' },
    { title: 'Review', detail: 'two independent verdict sets from the ledger' },
    { title: 'Judge', detail: 'judges only on contested items; two on overturns and non-verifier fixes' },
    { title: 'Challenge', detail: 'one "you sure you agree with all findings?" pass' },
    { title: 'Write and check', detail: 'verdict-locked template H answers, fix plan, pre-send check' },
  ],
}

// args: { pack_dir, findings_file, feedback_json?, runs_zip?, prior_verifier_file?, prior_notes_file?, scratch_dir, user_notes? }
const A = args || {}
const S = v => (v == null ? '' : typeof v === 'string' ? v : JSON.stringify(v))
const LEDGER = `${S(A.scratch_dir)}/xqc_ledger`
const CTX = `Task download (unzipped copy): ${S(A.pack_dir)}. External QC items as pasted: ${S(A.findings_file)}. QC feedback file: ${A.feedback_json ? S(A.feedback_json) : 'not supplied'}. Runs zip: ${A.runs_zip ? S(A.runs_zip) : 'not supplied'}. Final Review verifier file: ${A.prior_verifier_file ? S(A.prior_verifier_file) : 'not supplied'}. Final Review notes: ${A.prior_notes_file ? S(A.prior_notes_file) : 'not supplied'}. ${A.user_notes ? 'User notes: ' + S(A.user_notes) + '.' : ''}
Read §1 to §3 of skills/project-omega-finance-review/references/10_external_qc.md first; it replaces the full rulebook for this job. The shared evidence ledger is ${LEDGER}_A.md and ${LEDGER}_B.md: rely on it, and open a task file only to confirm or extend a fact it does not settle. Never write into the repository or into the download.
The test: Agree (true positive) only when the item's own complaint, tested on its own example of a correct answer, holds in the current files and needs a change; Disagree (false positive) when it does not, including every grader or infrastructure fault. The category tag never decides. Prefer a sound verifier-only cure; a prompt, golden or data change is the expert's and must pass the upload checks (same task, no removed content, grading no easier).`

async function retry(make) {
  for (let i = 0; i < 2; i++) { const r = await make(i); if (r) return r }
  return null
}

phase('Ledger')
const INVENTORY = {
  type: 'object',
  properties: {
    mismatch: { type: 'boolean' }, mismatch_reason: { type: 'string' },
    task_id: { type: 'string' }, version: { type: 'string' },
    cards: { type: 'array', items: { type: 'object', properties: { header: { type: 'string' }, category: { type: 'string' }, criteria: { type: 'array', items: { type: 'string' } }, complaint: { type: 'string' }, example_answer: { type: 'string' }, remediation: { type: 'string' } }, required: ['header', 'criteria', 'complaint'] } },
  },
  required: ['mismatch', 'cards'],
}
const inv = await retry(i => agent(`${CTX}

Inventory only. Match the screen with the files (task ID, version, item count). List every item that needs an answer, in screen order, with its exact header, category, criteria, complaint, its example of a correct answer and its remediation, quoting it; skip items marked Pass. No verdicts.`, { label: `inventory#${i}`, phase: 'Ledger', schema: INVENTORY, effort: 'low' }))
if (!inv) return { stop: true, reason: 'inventory failed' }
if (inv.mismatch) return { stop: true, reason: 'mismatch: ' + inv.mismatch_reason }
const HEADERS = inv.cards.map(c => c.header)
const HEADER = { type: 'string', enum: HEADERS }
const cardList = JSON.stringify(inv.cards, null, 1)
await parallel([
  () => retry(i => agent(`${CTX}

Build ledger part A at ${LEDGER}_A.md: for every item below, the named criteria verbatim from the current tests/verifier.json, the instruction clauses they rest on, the source and golden facts they turn on with locators, and every figure the item cites recomputed. Facts only.

Items:
${cardList}`, { label: `ledger:A#${i}`, phase: 'Ledger', effort: 'medium' })),
  () => retry(i => agent(`${CTX}

Build ledger part B at ${LEDGER}_B.md. If a runs zip is supplied, run python -X utf8 skills/verifier-json-fix/scripts/task_snapshot.py on it (unzipped into a new folder under the scratch directory) with --reasons, and record per named criterion each run's pass or fail, the judges' reasons and the oracle result. If a Final Review verifier file is supplied, diff it against the current tests/verifier.json and list agreed edits that did not land and changes nobody requested. Facts only.

Items:
${cardList}`, { label: `ledger:B#${i}`, phase: 'Ledger', effort: 'medium' })),
])
log(`${HEADERS.length} items; ledger written`)

const VP = {
  header: HEADER,
  verdict: { type: 'string', enum: ['AGREE', 'DISAGREE'] },
  layer: { type: 'string', enum: ['verifier', 'prompt', 'source', 'golden', 'infrastructure', 'none'] },
  reason: { type: 'string' },
  evidence: { type: 'string' },
  remediation_calls: { type: 'string', description: 'TAKE or REJECT per remediation item' },
  fix: { type: 'string', description: 'for an Agree: the exact change, quoted current text and replacement, in the file named by layer' },
  false_positive_criteria: { type: 'array', items: { type: 'string' } },
  changed_from_final_review: { type: 'string' },
  close_call: { type: 'boolean' },
}
const VERDICT = { type: 'object', properties: VP, required: ['header', 'verdict', 'layer', 'reason', 'evidence', 'close_call'] }
const SET = { type: 'object', properties: { verdicts: { type: 'array', items: VERDICT }, escalations: { type: 'array', items: { type: 'string' } } }, required: ['verdicts', 'escalations'] }

phase('Review')
const brief = (who, how) => `${CTX}

Independent reviewer ${who}. ${how} Give every item a verdict, the layer its fix belongs in, TAKE or REJECT per remediation item and, for an Agree, the exact change. Mark close_call on anything you are not certain of.

Items:
${cardList}`
const [rA, rB] = await parallel([
  () => retry(i => agent(brief('A', 'Work in screen order from the ledger.'), { label: `review:A#${i}`, phase: 'Review', schema: SET, effort: 'medium' })),
  () => retry(i => agent(brief('B', 'Test each item first against the golden and the prompt, then read QC\'s reasoning.'), { label: `review:B#${i}`, phase: 'Review', schema: SET, effort: 'medium' })),
])
if (!rA && !rB) return { stop: true, reason: 'both reviews failed' }
const by = {}
for (const h of HEADERS) by[h] = { a: null, b: null }
for (const v of ((rA && rA.verdicts) || [])) if (by[v.header]) by[v.header].a = v
for (const v of ((rB && rB.verdicts) || [])) if (by[v.header]) by[v.header].b = v

const final = {}
const changes = []
const unsettled = []
const contested = []
for (const h of HEADERS) {
  const x = by[h]
  const agree = x.a && x.b && x.a.verdict === x.b.verdict && x.a.layer === x.b.layer && !x.a.close_call && !x.b.close_call
  if (agree) final[h] = { ...x.a, reason: x.a.reason + ' (both reviewers agree)' }
  else contested.push(h)
}
log(`${contested.length} of ${HEADERS.length} items need a judge`)

const JUDGED = { type: 'object', properties: { ...VP, survives: { type: 'string' } }, required: ['header', 'verdict', 'layer', 'reason', 'evidence', 'close_call', 'survives'] }
const JUDGED_SET = { type: 'object', properties: { verdicts: { type: 'array', items: JUDGED } }, required: ['verdicts'] }
const BATCH = 4
const outsideVerifier = r => r && r.verdict === 'AGREE' && ['prompt', 'source', 'golden'].includes(r.layer)
function caseFor(h, extra) { const x = by[h]; return JSON.stringify({ item: inv.cards.find(c => c.header === h), reviewer_a: x.a, reviewer_b: x.b, current: final[h] || null, doubt: extra || null }, null, 1) }
async function judgeBatch(hs, tag, extras, note) {
  const r = await retry(i => agent(`${CTX}

Judge (${tag}). For each item below, the reviewers' positions are the two sides. Decide each verdict and layer yourself from the ledger (and a task file only if the ledger does not settle it); a verdict stands only if the strongest case against it fails. For an Agree outside verifier.json, confirm no sound verifier-only cure exists and that the change passes the upload checks.${note ? ' ' + note : ''}

Cases:
${hs.map(h => caseFor(h, extras ? extras[h] : null)).join('\n\n')}`, { label: `judge:${tag}:${hs[0]}#${i}`, phase: 'Judge', schema: JUDGED_SET, effort: 'high' }))
  const out = {}
  for (const v of ((r && r.verdicts) || [])) if (hs.includes(v.header)) out[v.header] = v
  return out
}
function chunks(list) { const c = []; for (let i = 0; i < list.length; i += BATCH) c.push(list.slice(i, i + BATCH)); return c }
async function decideAll(hs, tag, extras) {
  const first = {}
  for (const p of await parallel(chunks(hs).map(c => () => judgeBatch(c, tag + '.1', extras)))) Object.assign(first, p || {})
  const need = hs.filter(h => {
    const j = first[h]; if (!j) return false
    const x = by[h]
    const overturn = x.a && x.b && x.a.verdict === x.b.verdict && x.a.verdict !== j.verdict
    const moved = final[h] && (final[h].verdict !== j.verdict || final[h].layer !== j.layer)
    return outsideVerifier(j) || overturn || moved
  })
  const second = {}
  for (const p of await parallel(chunks(need).map(c => () => judgeBatch(c, tag + '.2', extras, 'Another judge has ruled on these; decide independently.')))) Object.assign(second, p || {})
  const split = need.filter(h => second[h] && (second[h].verdict !== first[h].verdict || second[h].layer !== first[h].layer))
  const third = {}
  for (const p of await parallel(chunks(split).map(c => () => judgeBatch(c, tag + '.3', extras, 'Two judges split: ' + JSON.stringify(c.map(h => ({ item: h, judge1: first[h], judge2: second[h] }))) + '. Settle each on the deciding fact and name it.')))) Object.assign(third, p || {})
  const res = {}
  for (const h of hs) res[h] = !first[h] ? null : !need.includes(h) ? first[h] : !second[h] ? null : split.includes(h) ? (third[h] || null) : first[h]
  return res
}
function apply(h, r, tag) {
  if (!r) { unsettled.push(h); return }
  const prev = final[h]
  if (prev && (prev.verdict !== r.verdict || prev.layer !== r.layer)) changes.push(`${h}: ${prev.verdict}/${prev.layer} → ${r.verdict}/${r.layer} (${tag}): ${r.survives}`)
  else if (!prev && by[h].a && by[h].b && by[h].a.verdict === by[h].b.verdict && by[h].a.verdict !== r.verdict) changes.push(`${h}: both reviewers ${by[h].a.verdict}, judged ${r.verdict}: ${r.survives}`)
  final[h] = r
}

phase('Judge')
const judged = await decideAll(contested, 'j')
for (const h of contested) apply(h, judged[h], 'judge')

phase('Challenge')
const DOUBTS = { type: 'object', properties: { doubts: { type: 'array', items: { type: 'object', properties: { header: HEADER, claim: { type: 'string' }, evidence: { type: 'string' } }, required: ['header', 'claim', 'evidence'] } } }, required: ['doubts'] }
const ch = await retry(i => agent(`${CTX}

You are the user asking "you sure you agree with all findings? any other finding that is a false positive? and any Disagree that should be an Agree?". Check every verdict against the ledger, and also that duplicate items carry the same verdict and fix, bundled items name their false-positive criteria, and no two fixes conflict. Report only doubts backed by a fact the verdicts missed.

Verdicts:
${JSON.stringify(HEADERS.map(h => final[h] || { header: h, verdict: 'unsettled' }), null, 1)}`, { label: `challenge#${i}`, phase: 'Challenge', schema: DOUBTS, effort: 'high' }))
const grouped = {}
for (const d of ((ch && ch.doubts) || [])) (grouped[d.header] = grouped[d.header] || []).push(d)
const doubted = Object.keys(grouped)
log(`challenge raised ${doubted.length} evidenced doubts`)
if (doubted.length) { const r = await decideAll(doubted, 'c', grouped); for (const h of doubted) apply(h, r[h], 'challenge') }

phase('Write and check')
const WRITE = {
  type: 'object',
  properties: {
    lead: { type: 'string' },
    entries: { type: 'array', items: { type: 'object', properties: { header: HEADER, verdict: { type: 'string', enum: ['AGREE', 'DISAGREE'] }, text: { type: 'string' } }, required: ['header', 'verdict', 'text'] } },
    fix_plan: { type: 'string', description: 'verifier items for the verifier-json-fix skill, then prompt, golden or data changes for the expert; empty when nothing is agreed' },
    escalations: { type: 'array', items: { type: 'string' } },
  },
  required: ['lead', 'entries', 'fix_plan'],
}
const writeBrief = `Write the External QC answers from the settled verdicts using template H of skills/project-omega-finance-review/references/06_output_templates.md and rules C1–C8 in SKILL.md (read only those sections): a one-paragraph lead (outcome, tally, closest call); one entry per item in this order, headed exactly as on screen; the fix plan (verifier items as the brief for the verifier-json-fix skill, with the agreed change per item; prompt, golden or data items as exact changes for the expert, each checked against the upload rules); escalation lines. Copy every verdict exactly.`
function codeCheck(w) {
  const p = [], seen = {}
  for (const e of (w.entries || [])) { if (seen[e.header]) p.push(`${e.header}: written twice`); seen[e.header] = 1; if (final[e.header] && e.verdict !== final[e.header].verdict) p.push(`${e.header}: says ${e.verdict}, settled verdict is ${final[e.header].verdict}`) }
  for (const h of HEADERS) if (!seen[h]) p.push(`${h}: no entry`)
  if (HEADERS.some(h => final[h] && final[h].verdict === 'AGREE') && !w.fix_plan) p.push('an item is agreed but there is no fix plan')
  return p
}
function compose(w) { const t = {}; for (const e of (w.entries || [])) t[e.header] = e.text; return [w.lead, ...HEADERS.map(h => t[h]), w.fix_plan ? 'Fix plan: ' + w.fix_plan : '', ...(w.escalations || [])].filter(Boolean).join('\n\n') }
let w = await retry(i => agent(`${CTX}

${writeBrief}

Settled verdicts:
${JSON.stringify(HEADERS.map(h => final[h] || null), null, 1)}
Escalations: ${JSON.stringify([...((rA && rA.escalations) || []), ...((rB && rB.escalations) || [])])}`, { label: `writer#${i}`, phase: 'Write and check', schema: WRITE, effort: 'medium' }))
if (!w) return { stop: true, reason: 'writer failed', verdicts: HEADERS.map(h => final[h] || null), changes }
const QC = { type: 'object', properties: { problems: { type: 'array', items: { type: 'string' } } }, required: ['problems'] }
const qc = await retry(i => agent(`${CTX}

Pre-send check (Pass 4 of reference 10). Check every quote and figure against the ledger, each header against the screen, that every button word matches its note, that verifier changes touch only feedback-named verifiers and every other change passes the upload checks, and that there are no Final Review field verdicts or Overall line. List each concrete problem with the exact change, or none.

Answers:
${compose(w)}`, { label: `presend#${i}`, phase: 'Write and check', schema: QC, effort: 'medium' }))
let problems = [...codeCheck(w), ...((qc && qc.problems) || (qc ? [] : ['pre-send check failed to run']))]
if (problems.length) {
  const rev = await retry(i => agent(`${CTX}

Fix every problem below in these External QC answers, changing wording only; every verdict stays as settled. Return every entry.

Problems:
${problems.join('\n')}

Settled verdicts: ${JSON.stringify(HEADERS.map(h => [h, final[h] ? final[h].verdict : null]))}

Answers:
${JSON.stringify(w)}`, { label: `revise#${i}`, phase: 'Write and check', schema: WRITE, effort: 'medium' }))
  if (rev) w = rev
  problems = codeCheck(w)
}
const agreedVerifier = HEADERS.filter(h => final[h] && final[h].verdict === 'AGREE' && final[h].layer === 'verifier').map(h => ({ item: h, fix: final[h].fix }))
const agreedOther = HEADERS.filter(h => outsideVerifier(final[h])).map(h => ({ item: h, layer: final[h].layer, fix: final[h].fix }))
return { answers: compose(w), verifier_fixes: agreedVerifier, other_fixes: agreedOther, changes, unsettled: [...unsettled, ...HEADERS.filter(h => !final[h])], qc_problems: problems, judged: contested.length }
