# pipeline_lite: pinned copies of two EKW QC pipeline checks

Copied unchanged from turing-genai-apps/EKW_QC_pipeline, commit c1b4ce469c1c78ce1bbded976973c936b4538476 2026-11-03:

| File | From | Why it is here |
|---|---|---|
| compound_criterion_check.py | deterministic-checks/ | counts the separately checkable clauses in a criterion (the G7 counter) |
| ekw_verifier_json.py | deterministic-checks/ | the adapter compound_criterion_check reads verifier.json through |
| reward_signal_gate.py | deterministic-checks/ | flags weak reward signal, including "~N separately checkable conditions in one PASS" |
| ../../assets/review-prompt/ekw-svc-comprehensive-review.md | docs/ | the review prompt practice_review.py runs |

Why only these: across 42 saved fix rounds (2026-11-02/04), every NEW or WORSE pipeline finding a verifier.json edit
caused came from compound_criterion_check (2 new, 73 worse) or reward_signal_gate (68 worse); the other ~28 checks in
run_all.py never moved. The integrity check is covered by build_round.py's fixed-zip gate (same zip entries, only
tests/verifier.json changed) and validate_verifier.py (config unchanged).

When a pipeline clone is configured, the skill uses the clone's current checks instead of these copies. QC still runs
the full pipeline on DataOS. Do not edit these files; refresh them by copying from a newer clone and updating the
commit line above.
