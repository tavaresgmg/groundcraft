# Proof

Define proof before the patch. Match it to the failure mode and blast radius.

Separate proof of the requested outcome from proof that execution merely completed. Inspect target state, persisted data, rendered behavior, or external observation when the task changes state.

## Proof plan

Choose the strongest affordable evidence:

1. direct reproduction or failing regression;
2. focused unit or contract check;
3. typecheck, lint, build, or broader regression suite;
4. integration, API, persisted-state, or migration verification;
5. browser interaction and visual inspection for user-facing behavior;
6. staging, telemetry, canary, reconciliation, or rollback exercise for operational risk.

Not every task needs every layer. A passing unrelated test is not proof.

For bug fixes, show that the check fails without the fix when feasible. Confirm tests assert behavior rather than implementation trivia. Never weaken a valid check to pass.

## Risk overlay

- `routine`: focused proof and final diff review;
- `guarded`: include negative or failure cases, broader regression, rollback reasoning, and fresh review when uncertainty remains;
- `critical`: test rollback or restore where applicable and feasible, verify relevant invariants/reconciliation, define abort criteria, and stop before external execution for `go/no-go`.

Security, authorization, money, data, concurrency, and migrations require boundary and partial-failure cases.

## Oracle discipline

- Validate that a test would fail for the targeted defect when feasible; a broken or circular oracle can make good work fail and bad work pass.
- Keep the agent away from hidden expected outputs when contamination would make the test meaningless, but retain an auditable reference solution and fixture owner.
- Treat self-review and model-as-judge as triage, not independent proof. Calibrate behavioral rubrics against human review and allow `unknown`.
- Record the exact task, fixture, model or agent, tools, permissions, versions, commit, run count, and relevant limits for repeatable evaluations.
- Isolate trials from shared mutable state. Use multiple runs for stochastic behavior and report variance rather than selecting the best run silently.
- A capability suite should remain challenging; a regression suite should be deterministic where possible and approach complete consistency. Move saturated capability cases into regression coverage.

Use `pass@k` only when one successful candidate among several is useful. Use all-runs consistency (`pass^k`) when any isolated failure matters. Neither compensates for an invalid task or oracle.

## Review

Review the final diff for correctness, scope, simplicity, security, data safety, tests, documentation, and collateral changes. Use a genuinely fresh read-only reviewer when residual uncertainty or blast radius justifies the cost. Verify findings before changing code. If fresh review is unavailable, run a separate self-review pass and mark independent review as not validated.

After the same failure twice, stop patching and diagnose. Report unavailable validation with its consequence; do not lower the completion standard silently.
