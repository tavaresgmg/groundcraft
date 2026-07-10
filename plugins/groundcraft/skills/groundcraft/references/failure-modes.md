# Failure modes

Classify failures by where they originated and where they escaped. Use the class to choose the next observation; do not add a generic rule for every incident.

## Taxonomy

- **Intent:** ambiguous outcome, hidden stakeholder, wrong scope, or a human decision silently assumed.
- **Context:** stale or cross-task state, omitted constraint, fabricated fact, weak source, or relevant evidence lost among distractors.
- **Reasoning:** premature hypothesis, symptom mistaken for cause, incompatible assumptions, or risk-blind plan.
- **Tool protocol:** wrong tool or arguments, truncated output, timeout, partial response, or error treated as success.
- **State and side effect:** transcript claims success while target state differs; retry duplicates work; operation is partially applied.
- **Implementation:** functional, security, data, performance, concurrency, compatibility, or maintainability defect.
- **Oracle:** test does not represent intent, fixture is unsolvable, parser is brittle, grader is biased, or reference result is wrong.
- **Gaming or contamination:** assertion, grader, or safeguard weakened; hidden answer leaked; behavior specialized to the benchmark.
- **Environment:** dependency, version, resource, permission, network, clock, or shared-state difference invalidates the result.
- **Verification:** proxy mistaken for outcome, only happy path tested, self-review repeats author bias, or uncertainty is concealed.
- **Authority:** external, destructive, secret, financial, production, or product decision executed without a real gate.
- **Delivery:** reviewed artifact differs from landed artifact; provenance, rollout observation, rollback, or cleanup is missing.

## Recovery

1. Preserve the smallest useful failure artifact: input, state, versions, trace, and observed output.
2. Identify the originating class and the control that should have caught it earlier.
3. Prefer a direct oracle, boundary check, or environment fix over more prompt text.
4. Add a deterministic regression when feasible; otherwise add a calibrated behavioral case with known limits.
5. Re-run the nearest affected suite and one adjacent negative case.

`Unknown` is valid when evidence is insufficient. Confident guessing, false completion, and silent gate bypass are failures even when the final output appears plausible.
