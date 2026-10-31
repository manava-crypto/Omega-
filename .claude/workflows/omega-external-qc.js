export const meta = {
  name: 'omega-external-qc',
  description: 'Project Omega External QC: two independent verdicts per finding, adversarial attack and judgment rounds until stable, set consistency, an "are you sure" challenge, then template H answers',
  whenToUse: 'Run from /omega-external-qc once the task pack, the pasted QC findings and the attached verifier file are saved to files.',
  phases: [
    { title: 'Inventory', detail: 'match the screen, list every finding card, diff the verifier file' },
    { title: 'Independent verdicts', detail: 'two reviewers, neither seeing the other' },
    { title: 'Attack and judge', detail: 'every verdict attacked and re-judged until no verdict moves' },
    { title: 'Consistency and challenge', detail: 'set consistency, then "are you sure you agree with all findings?"' },
    { title: 'Write and check', detail: 'template H answers and the pre-send check' },
  ],
}

// args: { pack_dir, findings_file, verifier_file, prior_verifier_file?, scratch_dir, tracker_fields?, user_notes? }
const A = args || {}
const AGENT = 'project-omega-finance-review'
const CTX = `Task pack directory: ${A.pack_dir}. Pasted External QC findings: ${A.findings_file}. Verifier file under review: ${A.verifier_file}. Final Review or earlier corrected verifier file: ${A.prior_verifier_file || 'not supplied'}. Tracker fields from the user: ${A.tracker_fields || 'none'}. Scratch directory for your working files: ${A.scratch_dir}. ${A.user_notes ? 'User notes: ' + A.user_notes : ''}
Before any verdict read skills/project-omega-finance-review/SKILL.md, reference 10 in full, 09 §1, 07, 08 for workbook criteria, and template H of 06. Read every file you rely on in full; recompute every figure QC cites; never write into the repository.
External QC is the last stage before TFRL. Only verifier.json changes are in scope; an agreed finding that needs a prompt, source or golden change rejects the task. Agree (true positive) only when the finding's own complaint, tested on its own example of a correct answer, holds in the current verifier file and needs a verifier change; Disagree (false positive) when it does not, including every grader or infrastructure fault (escalate those). The category tag never decides. Before agreeing that a defect lives outside verifier.json, look for a sound verifier-only cure.`

const CARD = { type: 'object', properties: { header: { type: 'string', description: 'exact on-screen header' }, category: { type: 'string' }, criteria: { type: 'array', items: { type: 'string' } }, complaint: { type: 'string' }, example_answer: { type: 'string' }, remediation: { type: 'string' } }, required: ['header', 'criteria', 'complaint'] }
const INVENTORY = {
  type: 'object',
  properties: {
    mismatch: { type: 'boolean' }, mismatch_reason: { type: 'string' },
    task_id: { type: 'string' }, verifier_version: { type: 'string' },
    cards: { type: 'array', items: CARD, description: 'every finding card in screen order' },
    diff: { type: 'string', description: 'agreed edits missing from this version and unrequested changes, or "no prior file"' },
  },
  required: ['mismatch', 'cards', 'diff'],
}
const VERDICT = {
  type: 'object',
  properties: {
    header: { type: 'string' },
    verdict: { type: 'string', enum: ['AGREE', 'DISAGREE'] },
    layer: { type: 'string', enum: ['verifier', 'prompt', 'source', 'golden', 'infrastructure', 'none'] },
    reason: { type: 'string' },
    evidence: { type: 'string', description: 'criterion quote, prompt clause, source cell or recomputed figure' },
    remediation_calls: { type: 'string', description: 'TAKE or REJECT per remediation item' },
    fix: { type: 'string', description: 'for an Agree: quoted current text and exact replacement in verifier.json' },
    false_positive_criteria: { type: 'array', items: { type: 'string' }, description: 'for a bundled card: listed criteria that stay unchanged' },
    close_call: { type: 'boolean' },
  },
  required: ['header', 'verdict', 'layer', 'reason', 'evidence', 'close_call'],
}
const SET = { type: 'object', properties: { verdicts: { type: 'array', items: VERDICT }, escalations: { type: 'array', items: { type: 'string' } } }, required: ['verdicts', 'escalations'] }

phase('Inventory')
const inv = await agent(`${CTX}

Inventory only. Match the screen (task ID, the version in the task link, the attached verifier file, the card count). List every finding card in screen order with its exact header, category, criteria, complaint, its example of a correct answer and its remediation, quoting the card. Diff the verifier file against the prior one if supplied: agreed edits that did not land and changes nobody requested. Give no verdicts.`, { label: 'inventory', phase: 'Inventory', agentType: AGENT, schema: INVENTORY })
if (!inv || inv.mismatch) return { stop: true, reason: inv ? inv.mismatch_reason : 'inventory failed', inventory: inv }
const cardList = inv.cards.map((c, i) => `${i + 1}. ${c.header}`).join('\n')
log(`${inv.cards.length} finding cards`)

phase('Independent verdicts')
const brief = (who, order) => `${CTX}

You are independent reviewer ${who}. ${order} For each card read the criterion verbatim in the current verifier file, the prompt clauses it rests on, the sources and the golden; recompute every figure QC cites; grade the card's own example of a correct answer against the criterion text; then give the verdict, the layer, TAKE or REJECT per remediation item, and for an Agree the exact verifier.json change. Mark close_call on anything you are not certain of.

Cards (full text in the inventory below):
${JSON.stringify(inv.cards, null, 1)}`
const [rA, rB] = await parallel([
  () => agent(brief('A', 'Work through the cards in screen order.'), { label: 'verdicts:A', phase: 'Independent verdicts', agentType: AGENT, schema: SET }),
  () => agent(brief('B', 'Work through the cards in reverse order, and test each card first against the golden and the prompt before reading QC\'s reasoning.'), { label: 'verdicts:B', phase: 'Independent verdicts', agentType: AGENT, schema: SET }),
])
const byCard = {}
for (const c of inv.cards) byCard[c.header] = { card: c, a: null, b: null }
for (const v of (rA ? rA.verdicts : [])) if (byCard[v.header]) byCard[v.header].a = v
for (const v of (rB ? rB.verdicts : [])) if (byCard[v.header]) byCard[v.header].b = v

const JUDGED = { type: 'object', properties: { ...VERDICT.properties, survives: { type: 'string', description: 'why the verdict survives the strongest attack' } }, required: [...VERDICT.required, 'survives'] }
const final = {}
async function attackAndJudge(header, round, extra) {
  const x = byCard[header]
  const dossier = JSON.stringify({ card: x.card, reviewer_a: x.a, reviewer_b: x.b, current: final[header] || null, challenge: extra || null }, null, 1)
  const [attackAgree, attackDisagree] = await parallel([
    () => agent(`${CTX}

Round ${round}, card "${header}". Attack an AGREE: show, from the files, that the card's example answer is not correct under the prompt and sources, that the criterion does not say what QC quotes, that the sources or golden settle the point, or that the failure is a grader or infrastructure fault. If no honest attack exists, say so plainly.

Dossier:
${dossier}`, { label: `vsAgree:${header}:r${round}`, phase: 'Attack and judge', agentType: AGENT }),
    () => agent(`${CTX}

Round ${round}, card "${header}". Attack a DISAGREE: build, from the files, a realistic correct answer that fails the current criterion text (or a wrong one that passes) for the reason the card gives. If no honest attack exists, say so plainly.

Dossier:
${dossier}`, { label: `vsDisagree:${header}:r${round}`, phase: 'Attack and judge', agentType: AGENT }),
  ])
  return agent(`${CTX}

Judge, round ${round}, card "${header}". Decide the verdict yourself by re-deriving the deciding facts from the files; the attacks are arguments, not evidence. A verdict stands only if the attack on it fails. State the layer; an Agree on a prompt, source or golden layer rejects the task, so confirm no sound verifier-only cure exists first. Give TAKE or REJECT per remediation item and, for an Agree, the exact verifier.json change; for a bundled card, name the criteria that are false positives.

Dossier:
${dossier}

Attack on AGREE:
${attackAgree}

Attack on DISAGREE:
${attackDisagree}`, { label: `judge:${header}:r${round}`, phase: 'Attack and judge', agentType: AGENT, schema: JUDGED })
}

phase('Attack and judge')
const changeLog = []
let queue = inv.cards.map(c => c.header)
for (let round = 1; round <= 3 && queue.length; round++) {
  const res = await parallel(queue.map(h => () => attackAndJudge(h, round).then(r => ({ h, r }))))
  const next = []
  for (const x of res.filter(Boolean)) {
    if (!x.r) continue
    const prev = final[x.h]
    if (prev && prev.verdict !== x.r.verdict) { changeLog.push(`${x.h}: ${prev.verdict} → ${x.r.verdict} (round ${round}): ${x.r.survives}`); next.push(x.h) }
    const ab = byCard[x.h]
    const split = ab.a && ab.b && ab.a.verdict !== ab.b.verdict
    if (round === 1 && (x.r.close_call || split || (ab.a && ab.a.verdict !== x.r.verdict) || (ab.b && ab.b.verdict !== x.r.verdict))) next.push(x.h)
    final[x.h] = x.r
  }
  queue = [...new Set(next)]
  log(`round ${round}: ${queue.length} cards still moving or contested`)
}

phase('Consistency and challenge')
const CONS = { type: 'object', properties: { problems: { type: 'array', items: { type: 'object', properties: { header: { type: 'string' }, problem: { type: 'string' }, evidence: { type: 'string' } }, required: ['header', 'problem', 'evidence'] } } }, required: ['problems'] }
for (let c = 1; c <= 3; c++) {
  const prompt = c === 1
    ? `Set consistency. Check across all verdicts: duplicate cards (same criterion, same evidence) carry the same verdict and fix; bundled cards name their false-positive criteria; every Agree is routed to its layer and the task outcome follows (approved, JSON revision, or task rejected); no two fixes conflict; the golden passes every changed criterion (re-grade it); a correct-value probe passes, a known-wrong probe fails and no proposed wording has a loophole; any fix that makes a check stricter is flagged.`
    : `You are the user asking "you sure you agree with all findings? any other finding that is a false positive? and any Disagree that should be an Agree?". Assume at least one verdict is wrong and look for it in every card.`
  const ch = await agent(`${CTX}

${prompt} Report only problems you can evidence from the files.

Current verdicts:
${JSON.stringify(final, null, 1)}

Verifier diff: ${inv.diff}`, { label: c === 1 ? 'consistency' : `challenge:${c - 1}`, phase: 'Consistency and challenge', agentType: AGENT, schema: CONS })
  const probs = ch ? ch.problems.filter(p => byCard[p.header]) : []
  if (!probs.length) { log(`${c === 1 ? 'consistency' : 'challenge'}: nothing evidenced`); if (c > 1) break; else continue }
  const res = await parallel(probs.map(p => () => attackAndJudge(p.header, 3 + c, p).then(r => ({ h: p.header, r }))))
  let moved = 0
  for (const x of res.filter(Boolean)) {
    if (!x.r) continue
    if (final[x.h].verdict !== x.r.verdict) { moved++; changeLog.push(`${x.h}: ${final[x.h].verdict} → ${x.r.verdict} (${c === 1 ? 'consistency' : 'challenge'}): ${x.r.survives}`) }
    final[x.h] = x.r
  }
  log(`${c === 1 ? 'consistency' : 'challenge'}: ${probs.length} problems, ${moved} verdicts moved`)
  if (c > 1 && !moved) break
}

phase('Write and check')
const ordered = inv.cards.map(c => final[c.header])
let answers = await agent(`${CTX}

Write the platform-ready External QC answers from these settled verdicts using template H of 06 and C1–C8 of SKILL.md: a one-paragraph lead (outcome, tally, closest call), one entry per card in screen order headed exactly as on screen, then, when any verifier finding is agreed, the self-contained fix request for the tracker's Additional Comments cell (with one separate sentence for missing earlier fixes from the diff), the tracker's reviewer fields (PENDING INPUT where not given), the upload-and-Column-I reminder, and escalation lines. Do not change any verdict; if you believe one is wrong, write it as given and add a final line "WRITER DOUBT: <header> — <reason>".

Settled verdicts:
${JSON.stringify(ordered, null, 1)}

Verifier diff: ${inv.diff}
Escalations raised: ${JSON.stringify([...(rA ? rA.escalations : []), ...(rB ? rB.escalations : [])])}`, { label: 'writer', phase: 'Write and check', agentType: AGENT })

const QC = { type: 'object', properties: { pass: { type: 'boolean' }, problems: { type: 'array', items: { type: 'string' } } }, required: ['pass', 'problems'] }
for (let k = 1; k <= 2; k++) {
  const qc = await agent(`${CTX}

Pre-send check (Pass 4 of reference 10 and the 07 pre-send checklist). Check every quote and figure against the files, that each entry's header matches the screen exactly, that every button word matches its note, that the fix request covers only agreed verifier findings plus the one missing-fixes sentence, that tallies come from the entries, and that there are no Final Review field verdicts or Overall line. List each concrete problem with the exact change; pass is true only if there are none.

Answers:
${answers}`, { label: `presend:${k}`, phase: 'Write and check', agentType: AGENT, schema: QC })
  if (!qc || qc.pass) break
  answers = await agent(`${CTX}

Revise these External QC answers to fix every problem listed, changing wording only, never a verdict. Return the full corrected answers.

Problems:
${qc.problems.join('\n')}

Answers:
${answers}`, { label: `revise:${k}`, phase: 'Write and check', agentType: AGENT })
}

return { answers, changes: changeLog, cards: inv.cards.length }
