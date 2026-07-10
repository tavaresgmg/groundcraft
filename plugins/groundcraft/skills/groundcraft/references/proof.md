# Proof

Define proof before producing the deliverable. Match it to the failure mode and blast radius.

Separate proof of the requested outcome from proof that execution merely completed. Inspect target state, persisted data, rendered behavior, or external observation when the task changes state.

## Proof budget

Start with the smallest direct check that can disprove the relevant claim. For every proposed check, know the claim it covers, the failure signal it can reveal, its expected latency or side effects, and which decision its result could change. Skip it when neither result would change completion or the next action.

Available proof includes source traceability, calculation or data spot-checks, constraint and scenario checks, direct reproduction, a focused unit or contract check, scoped typecheck or lint, broader regression, persisted-state verification, visual inspection, human acceptance, and operational observation. These are alternatives selected by the failure mode, not a ladder to climb or a checklist to complete.

Use changed-file or affected-scope lint and typecheck when available. Run a full suite, repository-wide lint or build only when the change crosses shared surfaces, the repository or release contract requires it, a focused check exposes wider uncertainty, or the user explicitly requests that depth. A passing unrelated test is not proof.

Long required checks should run asynchronously when possible, with useful progress updates. Asynchrony does not erase elapsed time: do not delay delivery for broader checks that add no required evidence. Stop when the requested outcome and relevant non-regression and safety claims have sufficient direct proof.

For bug fixes, show that the check fails without the fix when feasible. Confirm tests assert behavior rather than implementation trivia. Never weaken a valid check to pass.

## Risk overlay

- `routine`: focused proof and final-result inspection;
- `guarded`: include relevant negative or failure cases; add broader regression, rollback reasoning, or fresh review only where the shared surface or residual uncertainty warrants it;
- `critical`: test rollback or restore where applicable and feasible, verify relevant invariants/reconciliation, define abort criteria, and stop before external execution for `go/no-go`.

Security, authorization, money, data, concurrency, and migrations require boundary and partial-failure cases.

## Visual and human acceptance

Visual proof is for visible risk, not every user-facing file. Prefer an existing live view over a new export, inspect after the last visual-affecting change, and do not repeatedly render or export after changes that cannot alter the visual result.

Separate mechanical visual checks from taste. The agent can verify objective properties such as clipping, layout, and state transitions; the user owns subjective approval. If the user prefers to inspect the live result or artifact, perform only the cheap mechanical checks still needed, present the final state once, and leave approval explicit instead of producing repeated variants. Ask once before costly visual setup only when that choice changes the completion contract. Specialized domain instructions may still require rendering or visual inspection.

## Oracle discipline

- Validate that a test would fail for the targeted defect when feasible; a broken or circular oracle can make good work fail and bad work pass.
- Keep the agent away from hidden expected outputs when contamination would make the test meaningless, but retain an auditable reference solution and fixture owner.
- Treat self-review and model-as-judge as triage, not independent proof. Calibrate behavioral rubrics against human review and allow `unknown`.
- Record the exact task, fixture, model or agent, tools, permissions, versions, commit, run count, and relevant limits for repeatable evaluations.
- Isolate trials from shared mutable state. Use multiple runs for stochastic behavior and report variance rather than selecting the best run silently.
- A capability suite should remain challenging; a regression suite should be deterministic where possible and approach complete consistency. Move saturated capability cases into regression coverage.

Use `pass@k` only when one successful candidate among several is useful. Use all-runs consistency (`pass^k`) when any isolated failure matters. Neither compensates for an invalid task or oracle.

## Review

Inspect the final result for correctness, scope, simplicity, safety, traceability, and collateral changes. When files changed, review the actual diff and prefer the host's native diff-review surface. Use a genuinely fresh read-only reviewer only when residual uncertainty, blind review, or blast radius justifies the added context. Verify findings before revising the deliverable. If fresh review is unavailable, run a separate self-review pass and mark independent review as not validated.

After the same failure twice, stop patching and diagnose. Report unavailable validation with its consequence; do not lower the completion standard silently.
