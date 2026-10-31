export const meta = {
  name: 'omega-external-qc',
  description: 'Project Omega External QC: two independent verdicts per finding, attack and judgment rounds until each verdict is confirmed, fix reconciliation, consistency and "are you sure" checks, then verdict-locked template H answers',
  whenToUse: 'Run from /omega-external-qc once the task pack, the pasted QC findings and the attached verifier file are saved to files.',
  phases: [
    { title: 'Inventory', detail: 'match the screen, list every finding card, diff the verifier file' },
    { title: 'Independent verdicts', detail: 'two reviewers, neither seeing the other' },
    { title: 'Attack and judge', detail: 'every verdict attacked from both sides and re-judged until confirmed' },
    { title: 'Consistency and challenge', detail: 'fix reconciliation, set consistency, then "are you sure you agree with all findings?"' },
    { title: 'Write and check', detail: 'verdict-locked template H answers and the pre-send check' },
  ],
}

// args: { pack_dir, findings_file, verifier_file, prior_verifier_file?, prior_notes_file?, scratch_dir, tracker_fields?, user_notes? }
const A = args || {}
const S = v => (v == null ? '' : typeof v === 'string' ? v : JSON.stringify(v))
const AGENT = 'project-omega-finance-review'
const MAX_ROUNDS = 3
const CTX = `Task pack directory: ${S(A.pack_dir)}. Pasted External QC findings: ${S(A.findings_file)}. Verifier file under review: ${S(A.verifier_file)}. Final Review or earlier corrected verifier file: ${A.prior_verifier_file ? S(A.prior_verifier_file) : 'not supplied'}. Final Review notes or earlier fix request: ${A.prior_notes_file ? S(A.prior_notes_file) : 'not supplied'}. Tracker fields from the user: ${A.tracker_fields ? S(A.tracker_fields) : 'none'}. Scratch directory for your working files: ${S(A.scratch_dir)}. ${A.user_notes ? 'User notes: ' + S(A.user_notes) : ''}
Before any verdict read skills/project-omega-finance-review/SKILL.md, reference 10 in full, 09 §1, 07, 08 for workbook criteria, and template H of 06. Read every file you rely on in full; recompute every figure QC cites; never write into the repository.
External QC is the last stage before TFRL. Only verifier.json changes are in scope; an agreed finding that needs a prompt, source or golden change rejects the task. Agree (true positive) only when the finding's own complaint, tested on its own example of a correct answer, holds in the current verifier file and needs a verifier change; Disagree (false positive) when it does not, including every grader or infrastructure fault (escalate those). The category tag never decides. Before agreeing that a defect lives outside verifier.json, look for a sound verifier-only cure.`

async function retry(make, tries) {
  for (let i = 0; i < (tries || 2); i++) { const r = await make(i); if (r) return r }
  return null
}

phase('Inventory')
const INVENTORY = {
  type: 'object',
  properties: {
    mismatch: { type: 'boolean' }, mismatch_reason: { type: 'string' },
    task_id: { type: 'string' }, verifier_version: { type: 'string' },
    cards: { type: 'array', description: 'every finding card in screen order', items: { type: 'object', properties: { header: { type: 'string', description: 'exact on-screen header' }, category: { type: 'string' }, criteria: { type: 'array', items: { type: 'string' } }, complaint: { type: 'string' }, example_answer: { type: 'string' }, remediation: { type: 'string' } }, required: ['header', 'criteria', 'complaint'] } },
    diff: { type: 'string', description: 'fixes agreed at Final Review or earlier rounds that are missing from this version, and changes nobody requested; or "no prior file"' },
  },
  required: ['mismatch', 'cards', 'diff'],
}
const inv = await retry(i => agent(`${CTX}

Inventory only. Match the screen (task ID, the version in the task link, the attached verifier file, the card count). List every finding card in screen order with its exact header, category, criteria, complaint, its example of a correct answer and its remediation, quoting the card. Using the prior verifier file and prior notes where supplied, list fixes agreed earlier that did not land and changes nobody requested. Give no verdicts.`, { label: `inventory#${i}`, phase: 'Inventory', agentType: AGENT, schema: INVENTORY }))
if (!inv) return { stop: true, reason: 'inventory failed' }
if (inv.mismatch) return { stop: true, reason: 'mismatch: ' + inv.mismatch_reason }
const HEADERS = inv.cards.map(c => c.header)
const HEADER = { type: 'string', enum: HEADERS }
log(`${HEADERS.length} finding cards`)

const VERDICT_PROPS = {
  header: HEADER,
  verdict: { type: 'string', enum: ['AGREE', 'DISAGREE'] },
  layer: { type: 'string', enum: ['verifier', 'prompt', 'source', 'golden', 'infrastructure', 'none'] },
  reason: { type: 'string' },
  evidence: { type: 'string', description: 'criterion quote, prompt clause, source cell or recomputed figure' },
  remediation_calls: { type: 'string', description: 'TAKE or REJECT per remediation item' },
  fix: { type: 'string', description: 'for an Agree: quoted current text and exact replacement in verifier.json' },
  false_positive_criteria: { type: 'array', items: { type: 'string' } },
  changed_from_final_review: { type: 'string', description: 'if this reverses a Final Review APPROVE, the evidence that changed it' },
  close_call: { type: 'boolean' },
}
const VERDICT = { type: 'object', properties: VERDICT_PROPS, required: ['header', 'verdict', 'layer', 'reason', 'evidence', 'close_call'] }
const JUDGED = { type: 'object', properties: { ...VERDICT_PROPS, survives: { type: 'string', description: 'why the verdict survives the strongest attack' } }, required: ['header', 'verdict', 'layer', 'reason', 'evidence', 'close_call', 'survives'] }
const SET = { type: 'object', properties: { verdicts: { type: 'array', items: VERDICT }, escalations: { type: 'array', items: { type: 'string' } } }, required: ['verdicts', 'escalations'] }

phase('Independent verdicts')
const brief = (who, order) => `${CTX}

You are independent reviewer ${who}. ${order} For each card read the criterion verbatim in the current verifier file, the prompt clauses it rests on, the sources and the golden; recompute every figure QC cites; grade the card's own example of a correct answer against the criterion text; then give the verdict, the layer, TAKE or REJECT per remediation item, and for an Agree the exact verifier.json change. Mark close_call on anything you are not certain of.

Cards:
${JSON.stringify(inv.cards, null, 1)}`
const [rA, rB] = await parallel([
  () => retry(i => agent(brief('A', 'Work through the cards in screen order.'), { label: `verdicts:A#${i}`, phase: 'Independent verdicts', agentType: AGENT, schema: SET })),
  () => retry(i => agent(brief('B', 'Work through the cards in reverse order, and test each card against the golden and the prompt before reading QC\'s reasoning.'), { label: `verdicts:B#${i}`, phase: 'Independent verdicts', agentType: AGENT, schema: SET })),
])
if (!rA && !rB) return { stop: true, reason: 'both independent reviews failed' }
const byCard = {}
for (const c of inv.cards) byCard[c.header] = { card: c, a: null, b: null }
for (const v of (rA ? rA.verdicts : [])) if (byCard[v.header]) byCard[v.header].a = v
for (const v of (rB ? rB.verdicts : [])) if (byCard[v.header]) byCard[v.header].b = v

const final = {}
const history = {}
const changeLog = []
const unsettled = new Set()

function dossier(h, extra) {
  const x = byCard[h]
  return JSON.stringify({ card: x.card, reviewer_a: x.a, reviewer_b: x.b, current: final[h] || null, earlier_rounds: history[h] || [], challenge: extra || null, verifier_diff: inv.diff }, null, 1)
}
const taskEnding = r => r && r.verdict === 'AGREE' && ['prompt', 'source', 'golden'].includes(r.layer)

async function judgeWithConfirm(h, tag, base) {
  const j1 = await retry(i => agent(base + `\n\nYou are judge 1.`, { label: `judge1:${h}:${tag}#${i}`, phase: 'Attack and judge', agentType: AGENT, schema: JUDGED }))
  if (!j1 || !taskEnding(j1)) return j1
  const j2 = await retry(i => agent(base + `\n\nYou are judge 2. Another judge reached an Agree on the ${j1.layer} layer, which rejects the task. Decide independently, and first look for a sound verifier-only cure.`, { label: `judge2:${h}:${tag}#${i}`, phase: 'Attack and judge', agentType: AGENT, schema: JUDGED }))
  if (!j2) return null
  if (j2.verdict === j1.verdict && j2.layer === j1.layer) return j1
  return retry(i => agent(base + `\n\nYou are judge 3. Two judges split on a task-ending verdict.\nJudge 1: ${JSON.stringify(j1)}\nJudge 2: ${JSON.stringify(j2)}\nRe-derive the deciding fact from the files and settle the verdict and the layer; name the fact that decides.`, { label: `judge3:${h}:${tag}#${i}`, phase: 'Attack and judge', agentType: AGENT, schema: JUDGED }))
}

async function attackAndJudge(h, tag, extra) {
  const d = dossier(h, extra)
  const [vsAgree, vsDisagree] = await parallel([
    () => retry(i => agent(`${CTX}

${tag}, card "${h}". Attack an AGREE: show, from the files, that the card's example answer is not correct under the prompt and sources, that the criterion does not say what QC quotes, that the sources or golden settle the point, or that the failure is a grader or infrastructure fault. If no honest attack exists, say so plainly.

Dossier:
${d}`, { label: `vsAgree:${h}:${tag}#${i}`, phase: 'Attack and judge', agentType: AGENT })),
    () => retry(i => agent(`${CTX}

${tag}, card "${h}". Attack a DISAGREE: build, from the files, a realistic correct answer that fails the current criterion text (or a wrong one that passes) for the reason the card gives. If no honest attack exists, say so plainly.

Dossier:
${d}`, { label: `vsDisagree:${h}:${tag}#${i}`, phase: 'Attack and judge', agentType: AGENT })),
  ])
  return judgeWithConfirm(h, tag, `${CTX}

Judge (${tag}), card "${h}". Decide the verdict yourself by re-deriving the deciding facts from the files; the attacks are arguments, not evidence. A verdict stands only if the attack on it fails. State the layer; an Agree on a prompt, source or golden layer rejects the task, so confirm no sound verifier-only cure exists first. Give TAKE or REJECT per remediation item and, for an Agree, the exact verifier.json change; for a bundled card, name the criteria that are false positives; if this reverses a Final Review APPROVE, say what evidence changed it.

Dossier:
${d}

Attack on AGREE:
${vsAgree || 'unavailable'}

Attack on DISAGREE:
${vsDisagree || 'unavailable'}`)
}

async function finalJudge(h) {
  return judgeWithConfirm(h, 'final', `${CTX}

Final judge, card "${h}". Earlier rounds did not settle this card. Read every earlier round below, re-derive the deciding fact from the files yourself, and give the verdict and layer that survive the strongest attack. Name the fact that decides.

Dossier:
${dossier(h)}`)
}

function record(h, r, tag) { history[h] = (history[h] || []).concat([{ tag, verdict: r.verdict, layer: r.layer, reason: r.reason }]) }
function needsConfirmation(h, r) {
  const x = byCard[h]
  return r.close_call || [x.a, x.b].some(v => !v || v.verdict !== r.verdict)
}

// Every queued card must reach the same verdict in two consecutive judgments; anything still moving after MAX_ROUNDS goes to a final judge.
async function settle(headers, extras, label) {
  let queue = [...new Set(headers)]
  for (let round = 1; round <= MAX_ROUNDS && queue.length; round++) {
    const tag = `${label}${round}`
    const res = await parallel(queue.map(h => () => attackAndJudge(h, tag, extras ? extras[h] : null).then(r => ({ h, r }))))
    const next = []
    for (const x of res) {
      if (!x) continue
      if (!x.r) { unsettled.add(x.h); continue }
      record(x.h, x.r, tag)
      const prev = final[x.h]
      if (!prev) {
        final[x.h] = x.r
        const rv = byCard[x.h]
        if ([rv.a, rv.b].every(v => v && v.verdict !== x.r.verdict)) changeLog.push(`${x.h}: both reviewers said ${rv.a.verdict}, judged ${x.r.verdict} (${tag}): ${x.r.survives}`)
        if (needsConfirmation(x.h, x.r)) next.push(x.h)
        continue
      }
      if (prev.verdict !== x.r.verdict || prev.layer !== x.r.layer) { changeLog.push(`${x.h}: ${prev.verdict}/${prev.layer} → ${x.r.verdict}/${x.r.layer} (${tag}): ${x.r.survives}`); next.push(x.h) }
      final[x.h] = x.r
    }
    queue = [...new Set(next)]
    log(`${label} round ${round}: ${queue.length} cards need another judgment`)
  }
  for (const h of queue) {
    const r = await finalJudge(h)
    if (!r) { unsettled.add(h); continue }
    record(h, r, 'final')
    if (final[h] && (final[h].verdict !== r.verdict || final[h].layer !== r.layer)) changeLog.push(`${h}: ${final[h].verdict} → ${r.verdict} (final judge): ${r.survives}`)
    final[h] = r
  }
}

phase('Attack and judge')
await settle(HEADERS, null, 'r')

phase('Consistency and challenge')
const FIXES = { type: 'object', properties: { updates: { type: 'array', items: { type: 'object', properties: { header: HEADER, fix: { type: 'string' } }, required: ['header', 'fix'] } } }, required: ['updates'] }
async function reconcileFixes(tag) {
  const agreed = HEADERS.filter(h => final[h] && final[h].verdict === 'AGREE')
  if (!agreed.length) return
  const fx = await retry(i => agent(`${CTX}

Reconcile the fixes across every agreed card before anything is written: settle one value for every shared band, cap or anchor; duplicate cards (same criterion, same evidence) carry the same fix; no two fixes conflict; each fix stays inside verifier.json and keeps its criterion's single construct; the golden passes every changed criterion (re-grade it); a correct-value probe passes, a known-wrong probe fails and no wording has a loophole. Return only the fixes you change, with the full corrected text; never change a verdict.

${JSON.stringify(agreed.map(h => final[h]), null, 1)}`, { label: `reconcile:${tag}#${i}`, phase: 'Consistency and challenge', agentType: AGENT, schema: FIXES }))
  for (const u of ((fx && fx.updates) || [])) if (final[u.header]) final[u.header] = { ...final[u.header], fix: u.fix }
}
const PROBLEMS = { type: 'object', properties: { problems: { type: 'array', items: { type: 'object', properties: { header: HEADER, problem: { type: 'string' }, evidence: { type: 'string' } }, required: ['header', 'problem', 'evidence'] } } }, required: ['problems'] }
async function check(kind, n) {
  const prompt = kind === 'consistency'
    ? 'Set consistency. Check across all verdicts: duplicate cards carry the same verdict; bundled cards name their false-positive criteria; every Agree is routed to its layer and the task outcome follows (approved, JSON revision, or task rejected); every verdict that reverses a Final Review APPROVE says what changed it.'
    : 'You are the user asking "you sure you agree with all findings? any other finding that is a false positive? and any Disagree that should be an Agree?". Assume at least one verdict is wrong and look for it in every card.'
  const ch = await retry(i => agent(`${CTX}

${prompt} Report only problems you can evidence from the files.

Current verdicts:
${JSON.stringify(final, null, 1)}`, { label: `${kind}:${n}#${i}`, phase: 'Consistency and challenge', agentType: AGENT, schema: PROBLEMS }))
  if (!ch) { log(`${kind} ${n} failed to run`); return 0 }
  const grouped = {}
  for (const p of (ch.problems || [])) (grouped[p.header] = grouped[p.header] || []).push(p)
  const names = Object.keys(grouped)
  if (!names.length) { log(`${kind} ${n}: nothing evidenced`); return 0 }
  const before = changeLog.length
  await settle(names, grouped, `${kind[0]}${n}.`)
  const moved = changeLog.length - before
  log(`${kind} ${n}: ${names.length} cards questioned, ${moved} verdict changes`)
  return moved
}
await reconcileFixes('1')
for (let n = 1; n <= 2; n++) { if (!(await check('consistency', n))) break }
for (let n = 1; n <= 3; n++) {
  const moved = await check('challenge', n)
  if (!moved) break
  await reconcileFixes(`c${n}`)
  await check('consistency', 10 + n)
}

phase('Write and check')
const ordered = HEADERS.map(h => final[h] || null)
const WRITE = {
  type: 'object',
  properties: {
    lead: { type: 'string' },
    entries: { type: 'array', items: { type: 'object', properties: { header: HEADER, verdict: { type: 'string', enum: ['AGREE', 'DISAGREE'] }, text: { type: 'string', description: 'the complete paste-ready entry, starting "<header> — <VERDICT>."' } }, required: ['header', 'verdict', 'text'] } },
    fix_request: { type: 'string', description: 'the Additional Comments text, or empty when nothing is agreed' },
    tracker_fields: { type: 'string' },
    reminder: { type: 'string' },
    escalations: { type: 'array', items: { type: 'string' } },
    doubts: { type: 'array', items: { type: 'object', properties: { header: HEADER, reason: { type: 'string' } }, required: ['header', 'reason'] } },
  },
  required: ['lead', 'entries', 'fix_request', 'doubts'],
}
const writerBrief = `Write the platform-ready External QC answers from the settled verdicts using template H of 06 and C1–C8 of SKILL.md: a one-paragraph lead (outcome, tally, closest call); one entry per card in this exact order, headed exactly as on screen; when any verifier finding is agreed, the self-contained fix request for the tracker's Additional Comments cell (with one separate sentence for fixes agreed earlier that are missing, from the verifier diff), the tracker's reviewer fields (PENDING INPUT where not given) and the upload-and-Column-I reminder; and escalation lines. Copy each verdict exactly; if you believe one is wrong, keep it and add the card to doubts.`
function codeCheck(w) {
  const problems = []
  const seen = {}
  for (const e of (w.entries || [])) {
    if (seen[e.header]) problems.push(`${e.header}: entry written twice`)
    seen[e.header] = e
    if (final[e.header] && e.verdict !== final[e.header].verdict) problems.push(`${e.header}: entry says ${e.verdict} but the settled verdict is ${final[e.header].verdict}`)
  }
  for (const h of HEADERS) if (!seen[h]) problems.push(`${h}: no entry`)
  const agreedVerifier = HEADERS.some(h => final[h] && final[h].verdict === 'AGREE' && final[h].layer === 'verifier')
  if (agreedVerifier && !w.fix_request) problems.push('a verifier finding is agreed but there is no fix request')
  return problems
}
function compose(w) {
  const byH = {}
  for (const e of (w.entries || [])) byH[e.header] = e.text
  return [w.lead, ...HEADERS.map(h => byH[h]), w.fix_request ? 'Additional Comments: ' + w.fix_request : '', w.tracker_fields, w.reminder, ...(w.escalations || [])].filter(Boolean).join('\n\n')
}
const material = `Settled verdicts:\n${JSON.stringify(ordered, null, 1)}\n\nVerifier diff: ${inv.diff}\nEscalations raised: ${JSON.stringify([...(rA ? rA.escalations : []), ...(rB ? rB.escalations : [])])}`
let w = await retry(i => agent(`${CTX}\n\n${writerBrief}\n\n${material}`, { label: `writer#${i}`, phase: 'Write and check', agentType: AGENT, schema: WRITE }))
if (!w) return { stop: true, reason: 'writer failed', verdicts: ordered, changes: changeLog }
if (w.doubts && w.doubts.length) {
  const grouped = {}
  for (const d of w.doubts) (grouped[d.header] = grouped[d.header] || []).push(d)
  const before = changeLog.length
  await settle(Object.keys(grouped), grouped, 'w')
  if (changeLog.length > before) { await reconcileFixes('w'); await check('consistency', 20) }
  w = (await retry(i => agent(`${CTX}\n\n${writerBrief}\n\nSettled verdicts:\n${JSON.stringify(HEADERS.map(h => final[h] || null), null, 1)}\n\nVerifier diff: ${inv.diff}`, { label: `writer2#${i}`, phase: 'Write and check', agentType: AGENT, schema: WRITE }))) || w
}

const QC = { type: 'object', properties: { pass: { type: 'boolean' }, problems: { type: 'array', items: { type: 'string' } } }, required: ['pass', 'problems'] }
let qcProblems = []
for (let k = 1; k <= 3; k++) {
  const codeProblems = codeCheck(w)
  const qc = await retry(i => agent(`${CTX}

Pre-send check (Pass 4 of reference 10 and the 07 pre-send checklist). Check every quote and figure against the files, that each entry's header matches the screen exactly, that every button word matches its note, that the fix request covers only agreed verifier findings plus the one missing-fixes sentence and is self-contained for an engineer who has not read the task, that tallies come from the entries, and that there are no Final Review field verdicts or Overall line. List each concrete problem with the exact change; pass is true only if there are none.

Answers:
${compose(w)}`, { label: `presend:${k}#${i}`, phase: 'Write and check', agentType: AGENT, schema: QC }))
  qcProblems = [...codeProblems, ...(qc ? (qc.problems || []) : ['pre-send check failed to run'])]
  if (!qcProblems.length) break
  if (k === 3) break
  const rev = await retry(i => agent(`${CTX}

Revise these External QC answers to fix every problem listed. Change wording only; every verdict must stay exactly as settled. Return every entry.

Problems:
${qcProblems.join('\n')}

Settled verdicts:
${JSON.stringify(HEADERS.map(h => ({ header: h, verdict: final[h] ? final[h].verdict : null })))}

Current answers (structured):
${JSON.stringify(w, null, 1)}`, { label: `revise:${k}#${i}`, phase: 'Write and check', agentType: AGENT, schema: WRITE }))
  if (rev) w = rev
}

return {
  answers: compose(w),
  changes: changeLog,
  unsettled: [...unsettled, ...HEADERS.filter(h => !final[h])],
  qc_problems: qcProblems,
  cards: HEADERS.length,
}
