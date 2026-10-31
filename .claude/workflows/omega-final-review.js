export const meta = {
  name: 'omega-final-review',
  description: 'Project Omega Final Review: independent reviews, adversarial adjudication rounds until stable, an "are you sure" challenge, then platform-ready answers checked against Auto QC',
  whenToUse: 'Run from /omega-final-review once the package, the pasted Final Review screen and any prior notes are saved to files.',
  phases: [
    { title: 'Inventory', detail: 'match the upload to the screen and list every field' },
    { title: 'Independent review', detail: 'two full reviews plus an External QC-lens hunter' },
    { title: 'Adjudicate', detail: 'prosecutor, defender and judge on every contested field, repeated until no verdict moves' },
    { title: 'Challenge', detail: 'an "are you sure?" pass over every verdict' },
    { title: 'Write and check', detail: 'template F answers, then the Auto QC pre-check' },
  ],
}

// args: { pack_dir, screen_file, prior_notes_file?, scratch_dir, user_notes? }
const A = args || {}
const AGENT = 'project-omega-finance-review'
const CTX = `Task pack directory: ${A.pack_dir}. Pasted Final Review screen: ${A.screen_file}. Prior review notes: ${A.prior_notes_file || 'not supplied (say the fix list is inferred)'}. Scratch directory for your working files: ${A.scratch_dir}. ${A.user_notes ? 'User notes: ' + A.user_notes : ''}
Before any verdict read skills/project-omega-finance-review/SKILL.md, references 07, 08 (workbook verifiers), 09 §1 and §4, and template F of 06. Read every file you rely on in full; recompute from source; never write into the repository.
The stakes at this gate: rejecting Task Design, a source document, the prompt or the golden ends the task; a verifier REJECT sends that verifier back for repair and the task continues. A wrong task shipped and a correct task terminated are both failures. A non-verifier artifact is rejected only for a defect a correct solver cannot work around that the sources, the authority order and the prompt do not resolve (planned difficulty is approved). A verifier is rejected only when (a) its rubric misstates a governing term, (b) a realistic submission is mis-graded, shown on a supplied output or a fully described submission under an accepted reading (any PASS condition the prompt never asks for, or a single accepted reading where the prompt and sources allow another, meets this), or (c) where verifier and golden disagree, the verifier is the one that is wrong. The golden is rejected only when it truly fails a sound verifier or recomputes wrong from source. Everything else is an optional line.`

const FIELD = {
  type: 'object',
  properties: {
    field: { type: 'string', description: 'exact on-screen field name' },
    kind: { type: 'string', enum: ['task_design', 'source', 'prompt', 'verifier', 'golden', 'other'] },
  },
  required: ['field', 'kind'],
}
const INVENTORY = {
  type: 'object',
  properties: {
    mismatch: { type: 'boolean' },
    mismatch_reason: { type: 'string' },
    task_id: { type: 'string' },
    revision: { type: 'string' },
    fields: { type: 'array', items: FIELD, description: 'every field to answer, in screen order' },
    missing_inputs: { type: 'array', items: { type: 'string' } },
  },
  required: ['mismatch', 'fields', 'missing_inputs'],
}
const VERDICT = {
  type: 'object',
  properties: {
    field: { type: 'string' },
    verdict: { type: 'string', enum: ['APPROVE', 'REJECT', 'PENDING INPUT'] },
    ground: { type: 'string', description: 'for a REJECT: a, b, c, golden or non-verifier defect; for an APPROVE: why no counterexample exists' },
    evidence: { type: 'string', description: 'quoted locators, recomputed figures' },
    counterexample: { type: 'string', description: '"A submission that … would FAIL/PASS because …" for a verifier REJECT' },
    fix: { type: 'string' },
    optional_note: { type: 'string' },
    close_call: { type: 'boolean' },
  },
  required: ['field', 'verdict', 'ground', 'evidence', 'close_call'],
}
const REVIEW = { type: 'object', properties: { verdicts: { type: 'array', items: VERDICT }, escalations: { type: 'array', items: { type: 'string' } } }, required: ['verdicts', 'escalations'] }
const HUNT = {
  type: 'object',
  properties: { candidates: { type: 'array', items: { type: 'object', properties: { field: { type: 'string' }, defect: { type: 'string' }, evidence: { type: 'string' } }, required: ['field', 'defect', 'evidence'] } } },
  required: ['candidates'],
}

phase('Inventory')
const inv = await agent(`${CTX}

Inventory only. Match the upload to the pasted screen (task_id, revision, deliverable paths, verifier names, field count). List every field the screen asks you to answer, in screen order, with its kind. Count fields and verifiers from the files and the screen, never from memory. Name any missing input (prior notes, verifier plan, a deliverable). Do not give verdicts.`, { label: 'inventory', phase: 'Inventory', agentType: AGENT, schema: INVENTORY })
if (!inv || inv.mismatch) return { stop: true, reason: inv ? inv.mismatch_reason : 'inventory failed', inventory: inv }
const fieldList = inv.fields.map((f, i) => `${i + 1}. ${f.field} (${f.kind})`).join('\n')
log(`${inv.fields.length} fields on screen for ${inv.task_id || 'the task'}`)

phase('Independent review')
const [revA, revB, hunt] = await parallel([
  () => agent(`${CTX}

You are independent reviewer A. Give a verdict on every field below, in this order: re-verify every claimed prior fix, then Task Design on its own terms, Source Documents through the planned-difficulty test, every verifier through the probe battery in 07, and the golden through the Golden Data test (recompute its key chains from source; grade it literally against every FAIL clause). Mark close_call true on any verdict you are not certain of.

Fields:
${fieldList}`, { label: 'review:A', phase: 'Independent review', agentType: AGENT, schema: REVIEW }),
  () => agent(`${CTX}

You are independent reviewer B. Work in the opposite order from a usual pass: first recompute the golden's key figures from the sources and grade the golden literally against every verifier's PASS and FAIL text, then judge every verifier, then the prompt, sources and Task Design. Give a verdict on every field below and mark close_call true on any verdict you are not certain of.

Fields:
${fieldList}`, { label: 'review:B', phase: 'Independent review', agentType: AGENT, schema: REVIEW }),
  () => agent(`${CTX}

You are the External QC-lens hunter. External QC solver runs later proved several Final Review approvals wrong. Hunt across every verifier and the golden for exactly those defects: a PASS condition the prompt never asks for (a literal figure or phrase, a label, a closed list, a fixed placement, a hard date the prompt never states, a provider band the prompt asks the solver to challenge); a criterion accepting one reading where the prompt and sources allow another; golden wording that fails its own FAIL clause (labels, ordering wording); a pass case that breaches the governing standard; a double penalty on one defect. Report only candidates you can evidence from the files.

Fields:
${fieldList}`, { label: 'hunter', phase: 'Independent review', agentType: AGENT, schema: HUNT }),
])

const byField = {}
for (const f of inv.fields) byField[f.field] = { field: f.field, kind: f.kind, a: null, b: null, hunt: [] }
for (const v of (revA ? revA.verdicts : [])) if (byField[v.field]) byField[v.field].a = v
for (const v of (revB ? revB.verdicts : [])) if (byField[v.field]) byField[v.field].b = v
for (const c of (hunt ? hunt.candidates : [])) if (byField[c.field]) byField[c.field].hunt.push(c)

const final = {}
const contested = []
for (const f of inv.fields) {
  const x = byField[f.field]
  const agreeApprove = x.a && x.b && x.a.verdict === 'APPROVE' && x.b.verdict === 'APPROVE' && !x.a.close_call && !x.b.close_call && x.hunt.length === 0
  if (agreeApprove) final[f.field] = { ...x.a, settled_by: 'both reviewers, no hunter candidate' }
  else contested.push(f.field)
}
log(`${contested.length} contested fields go to adjudication; ${inv.fields.length - contested.length} settled`)

const JUDGED = {
  type: 'object',
  properties: { ...VERDICT.properties, reason: { type: 'string', description: 'why this verdict survives the strongest case against it' } },
  required: [...VERDICT.required, 'reason'],
}

async function adjudicate(fieldName, round, extra) {
  const x = byField[fieldName]
  const dossier = JSON.stringify({ field: fieldName, kind: x.kind, reviewer_a: x.a, reviewer_b: x.b, hunter: x.hunt, previous: final[fieldName] || null, challenge: extra || null }, null, 1)
  const [pro, con] = await parallel([
    () => agent(`${CTX}

Prosecutor, round ${round}, field "${fieldName}". Make the strongest evidence-based case that this field must be REJECTED under the stakes above. Re-derive everything from the files; cite quoted locators and recomputed figures; for a verifier give the concrete counterexample. If no honest case exists, say so plainly.

Dossier:
${dossier}`, { label: `pro:${fieldName}:r${round}`, phase: 'Adjudicate', agentType: AGENT }),
    () => agent(`${CTX}

Defender, round ${round}, field "${fieldName}". Make the strongest evidence-based case that this field must be APPROVED under the stakes above (planned difficulty, a reasonable reading the prompt supports, a defect the authority order resolves, a counterexample that is not realistic). Re-derive everything from the files. If no honest case exists, say so plainly.

Dossier:
${dossier}`, { label: `con:${fieldName}:r${round}`, phase: 'Adjudicate', agentType: AGENT }),
  ])
  const judgePrompt = (n) => `${CTX}

Judge ${n}, round ${round}, field "${fieldName}". Decide the verdict yourself by re-deriving the deciding facts from the files; the briefs below are arguments, not evidence. Weigh both errors: shipping a wrong task and terminating a correct one. A non-verifier REJECT ends the task, so it needs a defect you have confirmed yourself that no reading of the sources, authority order or prompt resolves.

Dossier:
${dossier}

Prosecutor:
${pro}

Defender:
${con}`
  const j1 = await agent(judgePrompt(1), { label: `judge1:${fieldName}:r${round}`, phase: 'Adjudicate', agentType: AGENT, schema: JUDGED })
  if (!j1) return final[fieldName] || null
  const terminal = j1.verdict === 'REJECT' && x.kind !== 'verifier'
  if (!terminal) return j1
  const j2 = await agent(judgePrompt(2) + `\n\nA first judge reached REJECT, which ends the task. Decide independently; do not defer to it.`, { label: `judge2:${fieldName}:r${round}`, phase: 'Adjudicate', agentType: AGENT, schema: JUDGED })
  if (!j2 || j2.verdict === j1.verdict) return j1
  return agent(judgePrompt(3) + `\n\nTwo judges split on a task-ending REJECT. Judge 1: ${JSON.stringify(j1)}\nJudge 2: ${JSON.stringify(j2)}\nRe-derive the deciding fact from the files and settle it; name the fact that decides.`, { label: `judge3:${fieldName}:r${round}`, phase: 'Adjudicate', agentType: AGENT, schema: JUDGED })
}

phase('Adjudicate')
let queue = contested
const changeLog = []
for (let round = 1; round <= 3 && queue.length; round++) {
  const results = await parallel(queue.map(name => () => adjudicate(name, round).then(r => ({ name, r }))))
  const next = []
  for (const res of results.filter(Boolean)) {
    if (!res.r) continue
    const prev = final[res.name]
    if (prev && prev.verdict !== res.r.verdict) { changeLog.push(`${res.name}: ${prev.verdict} → ${res.r.verdict} (round ${round}): ${res.r.reason}`); next.push(res.name) }
    else if (!prev && round > 1) next.push(res.name)
    final[res.name] = res.r
  }
  queue = round === 1 ? results.filter(Boolean).filter(x => x.r && x.r.close_call).map(x => x.name).concat(next) : next
  queue = [...new Set(queue)]
  log(`round ${round}: ${queue.length} fields still moving or close`)
}

phase('Challenge')
const CHALLENGE = { type: 'object', properties: { doubts: { type: 'array', items: { type: 'object', properties: { field: { type: 'string' }, claim: { type: 'string' }, evidence: { type: 'string' } }, required: ['field', 'claim', 'evidence'] } } }, required: ['doubts'] }
for (let c = 1; c <= 2; c++) {
  const ch = await agent(`${CTX}

You are the user asking "are you sure every verdict is right?". Assume at least one is wrong and look for it: every APPROVE for a missed mis-grade (especially the External QC-lens defects), every REJECT for a false defect or one that a reading of the prompt or sources resolves, and every golden and non-verifier verdict twice, since those REJECTs end the task. Report only doubts you can evidence from the files.

Current verdicts:
${JSON.stringify(final, null, 1)}`, { label: `challenge:${c}`, phase: 'Challenge', agentType: AGENT, schema: CHALLENGE })
  const doubts = ch ? ch.doubts.filter(d => final[d.field]) : []
  if (!doubts.length) { log(`challenge ${c}: no evidenced doubt`); break }
  const res = await parallel(doubts.map(d => () => adjudicate(d.field, 3 + c, d).then(r => ({ name: d.field, r }))))
  let moved = 0
  for (const x of res.filter(Boolean)) {
    if (!x.r) continue
    if (final[x.name].verdict !== x.r.verdict) { moved++; changeLog.push(`${x.name}: ${final[x.name].verdict} → ${x.r.verdict} (challenge ${c}): ${x.r.reason}`) }
    final[x.name] = x.r
  }
  log(`challenge ${c}: ${doubts.length} doubts, ${moved} verdicts moved`)
  if (!moved) break
}

phase('Write and check')
const ordered = inv.fields.map(f => final[f.field] || { field: f.field, verdict: 'PENDING INPUT', ground: 'not adjudicated', evidence: '', close_call: true })
let answers = await agent(`${CTX}

Write the platform-ready Final Review answers from these settled verdicts, in screen order, using template F of 06 and C1–C8 of SKILL.md: a one-line lead (task_id, revision, deliverables), one short paragraph each for Task Design, Source Documents and Golden, one line per verifier with a template A note under each REJECT (reason, evidence with quoted locator, counterexample, "Fix:" with the exact change), one "Optional:" line, escalation lines, then the Overall line as SKILL.md specifies. Do not change any verdict; if you believe one is wrong, write it as given and add a final line "WRITER DOUBT: <field> — <reason>".

Settled verdicts:
${JSON.stringify(ordered, null, 1)}

Escalations raised: ${JSON.stringify([...(revA ? revA.escalations : []), ...(revB ? revB.escalations : [])])}
Missing inputs: ${JSON.stringify(inv.missing_inputs)}`, { label: 'writer', phase: 'Write and check', agentType: AGENT })

const QC = { type: 'object', properties: { pass: { type: 'boolean' }, problems: { type: 'array', items: { type: 'string' } } }, required: ['pass', 'problems'] }
for (let k = 1; k <= 2; k++) {
  const qc = await agent(`${CTX}

Auto QC pre-check. Run these answers against the five Final Review Auto QC checks in 09 §4 (cross-item consistency, note groundedness against the files, actionability, coverage completeness, decision/note coherence including polarity) and the pre-send checklist in 07. Check every quote and figure against the files. List each concrete problem with the field and the exact change; pass is true only if there are none.

Answers:
${answers}`, { label: `autoqc:${k}`, phase: 'Write and check', agentType: AGENT, schema: QC })
  if (!qc || qc.pass) break
  answers = await agent(`${CTX}

Revise these Final Review answers to fix every problem listed, changing wording only, never a verdict. Return the full corrected answers.

Problems:
${qc.problems.join('\n')}

Answers:
${answers}`, { label: `revise:${k}`, phase: 'Write and check', agentType: AGENT })
}

return { answers, changes: changeLog, settled_without_adjudication: inv.fields.length - contested.length, adjudicated: contested.length }
