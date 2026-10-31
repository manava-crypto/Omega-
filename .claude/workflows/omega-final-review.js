export const meta = {
  name: 'omega-final-review',
  description: 'Project Omega Final Review: independent reviews, adversarial adjudication rounds until each verdict is confirmed, an "are you sure" challenge, fix reconciliation, then verdict-locked answers checked against Auto QC',
  whenToUse: 'Run from /omega-final-review once the package, the pasted Final Review screen and any prior notes are saved to files.',
  phases: [
    { title: 'Inventory', detail: 'match the upload to the screen and list every field' },
    { title: 'Independent review', detail: 'two full reviews plus an External QC-lens hunter' },
    { title: 'Adjudicate', detail: 'prosecutor, defender and judges on every contested field until each verdict is confirmed' },
    { title: 'Challenge', detail: '"are you sure?" passes over every verdict' },
    { title: 'Write and check', detail: 'fix reconciliation, verdict-locked template F answers, Auto QC pre-check' },
  ],
}

// args: { pack_dir, screen_file, prior_notes_file?, scratch_dir, user_notes? }
const A = args || {}
const S = v => (v == null ? '' : typeof v === 'string' ? v : JSON.stringify(v))
const AGENT = 'project-omega-finance-review'
const MAX_ROUNDS = 3
const CTX = `Task pack directory: ${S(A.pack_dir)}. Pasted Final Review screen: ${S(A.screen_file)}. Prior review notes: ${A.prior_notes_file ? S(A.prior_notes_file) : 'not supplied (say the fix list is inferred)'}. Scratch directory for your working files: ${S(A.scratch_dir)}. ${A.user_notes ? 'User notes: ' + S(A.user_notes) : ''}
Before any verdict read skills/project-omega-finance-review/SKILL.md, references 07, 08 (workbook verifiers), 09 §1 and §4, and template F of 06. Read every file you rely on in full; recompute from source; never write into the repository.
The stakes at this gate: rejecting Task Design, a source document, the prompt or the golden ends the task; a verifier REJECT sends that verifier back for repair and the task continues. A wrong task shipped and a correct task terminated are both failures. A non-verifier artifact is rejected only for a defect a correct solver cannot work around that the sources, the authority order and the prompt do not resolve (planned difficulty is approved). A verifier is rejected only when (a) its rubric misstates a governing term, (b) a realistic submission is mis-graded, shown on a supplied output or a fully described submission under an accepted reading (any PASS condition the prompt never asks for, or a single accepted reading where the prompt and sources allow another, meets this), or (c) where verifier and golden disagree, the verifier is the one that is wrong. The golden is rejected only when it truly fails a sound verifier or recomputes wrong from source. Everything else is an optional line.`

async function retry(make, tries) {
  for (let i = 0; i < (tries || 2); i++) { const r = await make(i); if (r) return r }
  return null
}

phase('Inventory')
const INVENTORY = {
  type: 'object',
  properties: {
    mismatch: { type: 'boolean' }, mismatch_reason: { type: 'string' },
    task_id: { type: 'string' }, revision: { type: 'string' },
    fields: { type: 'array', items: { type: 'object', properties: { field: { type: 'string', description: 'exact on-screen field name' }, kind: { type: 'string', enum: ['task_design', 'source', 'prompt', 'verifier', 'golden', 'other'] } }, required: ['field', 'kind'] }, description: 'every field to answer, in screen order' },
    missing_inputs: { type: 'array', items: { type: 'string' } },
  },
  required: ['mismatch', 'fields', 'missing_inputs'],
}
const inv = await retry(i => agent(`${CTX}

Inventory only. Match the upload to the pasted screen (task_id, revision, deliverable paths, verifier names, field count). List every field the screen asks you to answer, in screen order, with its kind and its exact on-screen name (each source file, the prompt, each verifier and each golden deliverable is its own field). Count from the files and the screen, never from memory. Name any missing input (prior notes, verifier plan, a deliverable). Do not give verdicts.`, { label: `inventory#${i}`, phase: 'Inventory', agentType: AGENT, schema: INVENTORY }))
if (!inv) return { stop: true, reason: 'inventory failed' }
if (inv.mismatch) return { stop: true, reason: 'mismatch: ' + inv.mismatch_reason }
const NAMES = inv.fields.map(f => f.field)
const KIND = {}
for (const f of inv.fields) KIND[f.field] = f.kind
const FIELD = { type: 'string', enum: NAMES }
const fieldList = inv.fields.map((f, i) => `${i + 1}. ${f.field} (${f.kind})`).join('\n')
log(`${NAMES.length} fields on screen for ${inv.task_id || 'the task'}`)

const VERDICT_PROPS = {
  field: FIELD,
  verdict: { type: 'string', enum: ['APPROVE', 'REJECT', 'PENDING INPUT'] },
  ground: { type: 'string', description: 'for a REJECT: a, b, c, golden or non-verifier defect; for an APPROVE: why no counterexample exists' },
  evidence: { type: 'string', description: 'quoted locators and recomputed figures' },
  counterexample: { type: 'string', description: '"A submission that … would FAIL/PASS because …" for a verifier REJECT' },
  fix: { type: 'string' },
  optional_note: { type: 'string' },
  close_call: { type: 'boolean' },
}
const VERDICT = { type: 'object', properties: VERDICT_PROPS, required: ['field', 'verdict', 'ground', 'evidence', 'close_call'] }
const JUDGED = { type: 'object', properties: { ...VERDICT_PROPS, reason: { type: 'string', description: 'why this verdict survives the strongest case against it' } }, required: ['field', 'verdict', 'ground', 'evidence', 'close_call', 'reason'] }
const REVIEW = { type: 'object', properties: { verdicts: { type: 'array', items: VERDICT }, escalations: { type: 'array', items: { type: 'string' } } }, required: ['verdicts', 'escalations'] }
const HUNT = { type: 'object', properties: { candidates: { type: 'array', items: { type: 'object', properties: { field: FIELD, defect: { type: 'string' }, evidence: { type: 'string' } }, required: ['field', 'defect', 'evidence'] } } }, required: ['candidates'] }

phase('Independent review')
const [revA, revB, hunt] = await parallel([
  () => retry(i => agent(`${CTX}

You are independent reviewer A. Give a verdict on every field below: re-verify every claimed prior fix, then Task Design on its own terms, each source through the planned-difficulty test, the prompt, every verifier through the probe battery in 07, and each golden deliverable through the Golden Data test (recompute its key chains from source; grade it literally against every FAIL clause). Mark close_call true on any verdict you are not certain of.

Fields:
${fieldList}`, { label: `review:A#${i}`, phase: 'Independent review', agentType: AGENT, schema: REVIEW })),
  () => retry(i => agent(`${CTX}

You are independent reviewer B. Work in the opposite order: first recompute the golden's key figures from the sources and grade the golden literally against every verifier's PASS and FAIL text, then judge every verifier, then the prompt, the sources and Task Design. Give a verdict on every field below and mark close_call true on any verdict you are not certain of.

Fields:
${fieldList}`, { label: `review:B#${i}`, phase: 'Independent review', agentType: AGENT, schema: REVIEW })),
  () => retry(i => agent(`${CTX}

You are the External QC-lens hunter. External QC reviews later proved several Final Review approvals wrong. Hunt across every verifier and the golden for exactly those defects: a PASS condition the prompt never asks for (a literal figure or phrase, a label, a closed list, a fixed placement, a hard date the prompt never states, a provider band the prompt asks the solver to challenge); a criterion accepting one reading where the prompt and sources allow another; golden wording that fails its own FAIL clause (labels, ordering wording); a pass case that breaches the governing standard; a double penalty on one defect. Report only candidates you can evidence from the files.

Fields:
${fieldList}`, { label: `hunter#${i}`, phase: 'Independent review', agentType: AGENT, schema: HUNT })),
])
if (!revA && !revB) return { stop: true, reason: 'both independent reviews failed' }

const byField = {}
for (const n of NAMES) byField[n] = { a: null, b: null, hunt: [] }
for (const v of (revA ? revA.verdicts : [])) if (byField[v.field]) byField[v.field].a = v
for (const v of (revB ? revB.verdicts : [])) if (byField[v.field]) byField[v.field].b = v
for (const c of (hunt ? hunt.candidates : [])) if (byField[c.field]) byField[c.field].hunt.push(c)

const final = {}
const history = {}
const changeLog = []
const unsettled = new Set()
const contested = []
for (const n of NAMES) {
  const x = byField[n]
  const clean = x.a && x.b && x.a.verdict === 'APPROVE' && x.b.verdict === 'APPROVE' && !x.a.close_call && !x.b.close_call && x.hunt.length === 0
  if (clean) final[n] = { ...x.a, reason: 'both independent reviewers approved with no hunter candidate' }
  else contested.push(n)
}
log(`${contested.length} contested fields go to adjudication; ${NAMES.length - contested.length} settled by both reviewers`)

function dossier(n, extra) {
  const x = byField[n]
  return JSON.stringify({ field: n, kind: KIND[n], reviewer_a: x.a, reviewer_b: x.b, hunter: x.hunt, current: final[n] || null, earlier_rounds: history[n] || [], challenge: extra || null }, null, 1)
}
const terminal = (n, r) => r && r.verdict === 'REJECT' && KIND[n] !== 'verifier'

async function judgeWithConfirm(n, tag, base) {
  const j1 = await retry(i => agent(base + `\n\nYou are judge 1.`, { label: `judge1:${n}:${tag}#${i}`, phase: 'Adjudicate', agentType: AGENT, schema: JUDGED }))
  if (!j1 || !terminal(n, j1)) return j1
  const j2 = await retry(i => agent(base + `\n\nYou are judge 2. Another judge reached REJECT, which ends the task. Decide independently; do not defer to it.`, { label: `judge2:${n}:${tag}#${i}`, phase: 'Adjudicate', agentType: AGENT, schema: JUDGED }))
  if (!j2) return null
  if (j2.verdict === j1.verdict) return j1
  return retry(i => agent(base + `\n\nYou are judge 3. Two judges split on a task-ending REJECT.\nJudge 1: ${JSON.stringify(j1)}\nJudge 2: ${JSON.stringify(j2)}\nRe-derive the deciding fact from the files and settle it; name the fact that decides.`, { label: `judge3:${n}:${tag}#${i}`, phase: 'Adjudicate', agentType: AGENT, schema: JUDGED }))
}

async function adjudicate(n, tag, extra) {
  const d = dossier(n, extra)
  const [pro, con] = await parallel([
    () => retry(i => agent(`${CTX}

Prosecutor (${tag}), field "${n}". Make the strongest evidence-based case that this field must be REJECTED under the stakes above. Re-derive everything from the files; cite quoted locators and recomputed figures; for a verifier give the concrete counterexample. If no honest case exists, say so plainly.

Dossier:
${d}`, { label: `pro:${n}:${tag}#${i}`, phase: 'Adjudicate', agentType: AGENT })),
    () => retry(i => agent(`${CTX}

Defender (${tag}), field "${n}". Make the strongest evidence-based case that this field must be APPROVED under the stakes above (planned difficulty, a reasonable reading the prompt supports, a defect the authority order resolves, a counterexample that is not realistic). Re-derive everything from the files. If no honest case exists, say so plainly.

Dossier:
${d}`, { label: `con:${n}:${tag}#${i}`, phase: 'Adjudicate', agentType: AGENT })),
  ])
  return judgeWithConfirm(n, tag, `${CTX}

Judge (${tag}), field "${n}". Decide the verdict yourself by re-deriving the deciding facts from the files; the briefs below are arguments, not evidence. Weigh both errors: shipping a wrong task and terminating a correct one. A non-verifier REJECT ends the task, so it needs a defect you have confirmed yourself that no reading of the sources, authority order or prompt resolves.

Dossier:
${d}

Prosecutor:
${pro || 'unavailable'}

Defender:
${con || 'unavailable'}`)
}

async function finalJudge(n) {
  return judgeWithConfirm(n, 'final', `${CTX}

Final judge, field "${n}". Earlier rounds did not settle this field. Read every earlier round below, re-derive the deciding fact from the files yourself, and give the verdict that survives the strongest case against it. Name the fact that decides.

Dossier:
${dossier(n)}`)
}

function record(n, r, tag) {
  history[n] = (history[n] || []).concat([{ tag, verdict: r.verdict, reason: r.reason }])
}
function needsConfirmation(n, r) {
  const x = byField[n]
  return r.close_call || x.hunt.length > 0 || [x.a, x.b].some(v => !v || v.verdict !== r.verdict)
}

// Every queued field must reach the same verdict in two consecutive judgments; anything still moving after MAX_ROUNDS goes to a final judge.
async function settle(names, extras, label) {
  let queue = [...new Set(names)]
  for (let round = 1; round <= MAX_ROUNDS && queue.length; round++) {
    const tag = `${label}${round}`
    const res = await parallel(queue.map(n => () => adjudicate(n, tag, extras ? extras[n] : null).then(r => ({ n, r }))))
    const next = []
    for (const x of res) {
      if (!x) continue
      if (!x.r) { unsettled.add(x.n); continue }
      record(x.n, x.r, tag)
      const prev = final[x.n]
      if (!prev) {
        final[x.n] = x.r
        const rv = byField[x.n]
        if ([rv.a, rv.b].every(v => v && v.verdict !== x.r.verdict)) changeLog.push(`${x.n}: both reviewers said ${rv.a.verdict}, judged ${x.r.verdict} (${tag}): ${x.r.reason}`)
        if (needsConfirmation(x.n, x.r)) next.push(x.n)
        continue
      }
      if (prev.verdict !== x.r.verdict) { changeLog.push(`${x.n}: ${prev.verdict} → ${x.r.verdict} (${tag}): ${x.r.reason}`); next.push(x.n) }
      final[x.n] = x.r
    }
    queue = [...new Set(next)]
    log(`${label} round ${round}: ${queue.length} fields need another judgment`)
  }
  for (const n of queue) {
    const r = await finalJudge(n)
    if (!r) { unsettled.add(n); continue }
    record(n, r, 'final')
    if (final[n] && final[n].verdict !== r.verdict) changeLog.push(`${n}: ${final[n].verdict} → ${r.verdict} (final judge): ${r.reason}`)
    final[n] = r
  }
}

phase('Adjudicate')
await settle(contested, null, 'r')

phase('Challenge')
const CHALLENGE = { type: 'object', properties: { doubts: { type: 'array', items: { type: 'object', properties: { field: FIELD, claim: { type: 'string' }, evidence: { type: 'string' } }, required: ['field', 'claim', 'evidence'] } } }, required: ['doubts'] }
for (let c = 1; c <= 3; c++) {
  const ch = await retry(i => agent(`${CTX}

You are the user asking "are you sure every verdict is right?". Assume at least one is wrong and look for it: every APPROVE for a missed mis-grade (especially the External QC-lens defects), every REJECT for a false defect or one that a reading of the prompt or sources resolves, and every golden and non-verifier verdict twice, since those REJECTs end the task. Report only doubts you can evidence from the files.

Current verdicts:
${JSON.stringify(final, null, 1)}`, { label: `challenge:${c}#${i}`, phase: 'Challenge', agentType: AGENT, schema: CHALLENGE }))
  if (!ch) { log(`challenge ${c} failed to run`); break }
  const grouped = {}
  for (const d of (ch.doubts || [])) (grouped[d.field] = grouped[d.field] || []).push(d)
  const names = Object.keys(grouped)
  if (!names.length) { log(`challenge ${c}: no evidenced doubt`); break }
  const before = changeLog.length
  await settle(names, grouped, `c${c}.`)
  log(`challenge ${c}: ${names.length} fields doubted, ${changeLog.length - before} verdict changes`)
  if (changeLog.length === before) break
}

phase('Write and check')
const FIXES = { type: 'object', properties: { updates: { type: 'array', items: { type: 'object', properties: { field: FIELD, fix: { type: 'string' } }, required: ['field', 'fix'] } }, notes: { type: 'string' } }, required: ['updates'] }
const rejects = NAMES.filter(n => final[n] && final[n].verdict === 'REJECT')
if (rejects.length > 1) {
  const fx = await retry(i => agent(`${CTX}

Reconcile the fixes across these REJECT verdicts before anything is written: no two fixes may conflict, every figure, band or anchor that appears in more than one fix must be identical, each fix keeps its verifier's single construct, and the golden must still pass every changed criterion. Re-derive from the files. Return only the fixes you change, with the full corrected fix text; never change a verdict.

${JSON.stringify(rejects.map(n => final[n]), null, 1)}`, { label: `reconcile-fixes#${i}`, phase: 'Write and check', agentType: AGENT, schema: FIXES }))
  for (const u of ((fx && fx.updates) || [])) if (final[u.field]) final[u.field] = { ...final[u.field], fix: u.fix }
}

const ordered = NAMES.map(n => final[n] || { field: n, verdict: 'PENDING INPUT', ground: 'not settled', evidence: '', close_call: true })
const WRITE = {
  type: 'object',
  properties: {
    lead: { type: 'string' },
    entries: { type: 'array', items: { type: 'object', properties: { field: FIELD, verdict: { type: 'string', enum: ['APPROVE', 'REJECT', 'PENDING INPUT'] }, text: { type: 'string', description: 'the complete paste-ready entry, starting "<field> — <VERDICT>."' } }, required: ['field', 'verdict', 'text'] } },
    optional_line: { type: 'string' },
    escalations: { type: 'array', items: { type: 'string' } },
    overall: { type: 'string' },
    doubts: { type: 'array', items: { type: 'object', properties: { field: FIELD, reason: { type: 'string' } }, required: ['field', 'reason'] } },
  },
  required: ['lead', 'entries', 'overall', 'doubts'],
}
const writerBrief = `Write the platform-ready Final Review answers from the settled verdicts, using template F of 06 and C1–C8 of SKILL.md: a one-line lead (task_id, revision, deliverables); one entry per field below, in this exact order, each a short paragraph for Task Design, each source, the prompt and each golden deliverable, and one line per verifier with a template A note under each REJECT (reason, evidence with quoted locator, counterexample, "Fix:" with the exact change); one "Optional:" line; escalation lines; and the Overall line as SKILL.md specifies. Copy each verdict exactly; if you believe one is wrong, keep it and add the field to doubts.`
function codeCheck(w) {
  const problems = []
  const seen = {}
  for (const e of (w.entries || [])) {
    if (seen[e.field]) problems.push(`${e.field}: entry written twice`)
    seen[e.field] = e
    if (final[e.field] && e.verdict !== final[e.field].verdict) problems.push(`${e.field}: entry says ${e.verdict} but the settled verdict is ${final[e.field].verdict}`)
  }
  for (const n of NAMES) if (!seen[n]) problems.push(`${n}: no entry`)
  return problems
}
function compose(w) {
  const byF = {}
  for (const e of (w.entries || [])) byF[e.field] = e.text
  return [w.lead, ...NAMES.map(n => byF[n]), w.optional_line, ...(w.escalations || []), w.overall].filter(Boolean).join('\n\n')
}
const material = `Settled verdicts:\n${JSON.stringify(ordered, null, 1)}\n\nEscalations raised: ${JSON.stringify([...(revA ? revA.escalations : []), ...(revB ? revB.escalations : [])])}\nMissing inputs: ${JSON.stringify(inv.missing_inputs)}`
let w = await retry(i => agent(`${CTX}\n\n${writerBrief}\n\n${material}`, { label: `writer#${i}`, phase: 'Write and check', agentType: AGENT, schema: WRITE }))
if (!w) return { stop: true, reason: 'writer failed', verdicts: ordered, changes: changeLog }
if (w.doubts && w.doubts.length) {
  const grouped = {}
  for (const d of w.doubts) (grouped[d.field] = grouped[d.field] || []).push(d)
  await settle(Object.keys(grouped), grouped, 'w')
  const ordered2 = NAMES.map(n => final[n] || { field: n, verdict: 'PENDING INPUT', ground: 'not settled', evidence: '', close_call: true })
  w = (await retry(i => agent(`${CTX}\n\n${writerBrief}\n\nSettled verdicts:\n${JSON.stringify(ordered2, null, 1)}`, { label: `writer2#${i}`, phase: 'Write and check', agentType: AGENT, schema: WRITE }))) || w
}

const QC = { type: 'object', properties: { pass: { type: 'boolean' }, problems: { type: 'array', items: { type: 'string' } } }, required: ['pass', 'problems'] }
let qcProblems = []
for (let k = 1; k <= 3; k++) {
  const codeProblems = codeCheck(w)
  const qc = await retry(i => agent(`${CTX}

Auto QC pre-check. Run these answers against the five Final Review Auto QC checks in 09 §4 (cross-item consistency, note groundedness against the files, actionability, coverage completeness, decision/note coherence including polarity) and the pre-send checklist in 07, and check the Overall line against SKILL.md. Check every quote and figure against the files. List each concrete problem with the field and the exact change; pass is true only if there are none.

Answers:
${compose(w)}`, { label: `autoqc:${k}#${i}`, phase: 'Write and check', agentType: AGENT, schema: QC }))
  qcProblems = [...codeProblems, ...(qc ? (qc.problems || []) : ['Auto QC pre-check failed to run'])]
  if (!qcProblems.length) break
  if (k === 3) break
  const rev = await retry(i => agent(`${CTX}

Revise these Final Review answers to fix every problem listed. Change wording only; every verdict must stay exactly as settled. Return every entry.

Problems:
${qcProblems.join('\n')}

Settled verdicts:
${JSON.stringify(NAMES.map(n => ({ field: n, verdict: final[n] ? final[n].verdict : 'PENDING INPUT' })))}

Current answers (structured):
${JSON.stringify(w, null, 1)}`, { label: `revise:${k}#${i}`, phase: 'Write and check', agentType: AGENT, schema: WRITE }))
  if (rev) w = rev
}

return {
  answers: compose(w),
  changes: changeLog,
  unsettled: [...unsettled],
  qc_problems: qcProblems,
  settled_by_both_reviewers: NAMES.length - contested.length,
  adjudicated: contested.length,
}
