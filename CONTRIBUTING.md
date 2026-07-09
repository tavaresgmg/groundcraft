# Contributing

Groundcraft changes behavior, so prompt edits are code changes.

1. State the failure mode with a concrete example.
2. Add or update a case in `evals/cases.json`.
3. Make the smallest rule change that addresses it.
4. Run `python3 scripts/validate.py`.
5. Run the affected case with `scripts/run-evals.py` or an equivalent isolated fixture.
6. Have a human or separately calibrated reviewer compare the artifact with `must` and `must_not`.
7. Report both improvement and new trade-offs.

Do not add a phase, role, artifact, dependency, hook, or command without evidence that the existing method cannot handle the case. Avoid copied prompt text; cite ideas and write original instructions.
