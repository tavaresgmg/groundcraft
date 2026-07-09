# Contributing

Groundcraft changes behavior, so prompt edits are code changes.

1. State the failure mode with a concrete example.
2. Add or update one focused case in `evals/cases.json`; remove overlapping coverage instead of growing the catalog by default.
3. Make the smallest rule change that addresses it.
4. Run `python3 scripts/validate.py`.
5. Run the affected regression and adjacent negative case with `scripts/run-evals.py`; repeat only when variance can change the decision.
6. Have a human or separately calibrated fresh reviewer compare the response, trace, state, and side effects with `must` and `must_not`.
7. Report both improvement and new trade-offs.

Do not add a phase, role, artifact, dependency, hook, or command without evidence that the existing method cannot handle the case. Avoid copied prompt text; cite ideas and write original instructions.

The validator enforces a 140-line kernel, 80-line reference files, and a 10-14 case catalog. Treat these as complexity budgets, not targets to fill.

Do not weaken a fixture, assertion, hidden oracle, or forbidden criterion to make a result pass. If the task or oracle is invalid, classify it as `invalid` and fix the harness before judging the agent.
