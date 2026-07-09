# Proof

Define proof before the patch. Match it to the failure mode and blast radius.

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

## Review

Review the final diff for correctness, scope, simplicity, security, data safety, tests, documentation, and collateral changes. Use a genuinely fresh read-only reviewer when residual uncertainty or blast radius justifies the cost. Verify findings before changing code. If fresh review is unavailable, run a separate self-review pass and mark independent review as not validated.

After the same failure twice, stop patching and diagnose. Report unavailable validation with its consequence; do not lower the completion standard silently.
