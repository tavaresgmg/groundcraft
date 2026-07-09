# Quality contracts

Define acceptance before producing the result. Prefer observable outcomes over process compliance.

## Contract by task

- **Answer or explanation:** answer the actual question; distinguish fact, inference, and unknown; use a source or direct evidence when the claim is current, disputed, unfamiliar, or high-stakes.
- **Research:** delimit the decision; use current primary sources; cover material contradiction; connect each material claim to evidence; state scope, date, and limits.
- **Decision:** expose assumptions and constraints; compare real alternatives only when trade-offs matter; test the recommendation adversarially; choose one path and state what would falsify it.
- **Diagnosis:** reproduce or correlate the symptom; discriminate among plausible causes; identify the causal mechanism; prove the fix or finding against the original failure.
- **Change:** observe intended behavior; protect relevant existing behavior; review the final diff; remove incidental residue; update affected existing documentation.
- **Review:** inspect the actual artifact and constraints; report only evidence-backed findings, prioritized by consequence; do not invent quota findings or mutate unless asked.
- **Operation:** observe target state and side effects; make retries safe; define rollback or mitigation when relevant; gate external, destructive, or irreversible execution.

## Four proof surfaces

Use only the surfaces the task needs:

1. **Outcome:** the requested state or behavior exists.
2. **Non-regression:** relevant existing behavior still holds.
3. **Safety:** boundaries, failure paths, authority, and invariants hold.
4. **Delivery:** the reviewed artifact is the artifact integrated or released, with provenance when required.

## Completion states

- `done`: every required criterion has direct enough evidence.
- `done_with_concerns`: outcome is proven, but a non-blocking limitation remains explicit.
- `blocked`: a concrete dependency or human gate prevents the next required step.
- `failed`: execution completed without meeting a required criterion, or evidence disproved the approach.

`not validated` is a property of a claim or proof surface, not a fifth task state. If that proof is required and can still be obtained safely, continue; if an external dependency or gate prevents it, the task is `blocked`; if the attempted result missed it, the task `failed`. Do not collapse any of these into success. A proxy such as compilation, a tool exit code, agent narration, or self-review cannot compensate for a missing outcome check.

## Quality economy

Optimize for correctness, usefulness, safety, maintainability, and evidence. Treat tokens, time, tool calls, diff size, and ceremony as costs, not goals. Never reward a single metric that can be improved by weakening another required property.

Do not expose internal classification, module loading, or routine checklist narration unless it helps the user make a decision. Process compliance is not user value.
