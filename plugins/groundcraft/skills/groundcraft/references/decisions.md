# Decisions

Use this module for material choices, not every implementation detail.

## Decision brief

1. State the decision, outcome, constraints, and non-goals.
2. Generate two or three real options. Include doing nothing, native behavior, or reuse when credible.
3. Compare effect on correctness, user value, delivery cost, risk, reversibility, maintenance, and context load.
4. Run an adversarial pass: identify how each option fails, what assumption it hides, and what evidence would falsify it.
5. Recommend one path and explain why the rejected options lose here.

Do not manufacture alternatives when one path is clearly required by evidence or repository convention.

## Human decision

- Choose autonomously when the option is safe, reversible, and does not materially alter product or architecture.
- Recommend and confirm when taste, product intent, central architecture, core dependency, cost, or blast radius changes.
- Present critical actions as `go/no-go` only after impact, evidence, and rollback or mitigation are known when applicable.

Ask at most one to three questions at once. Put the recommended option first. If an answer is useful but non-blocking, state the safe default and continue.

## Change boundary

- `narrow`: direct local change; proceed;
- `coherent expansion`: include root cause, shared contract, required proof, or obsolete-path removal; proceed and explain at close;
- `redesign`: changes central architecture, product behavior, core dependency, or blast radius; confirm first.

Brainstorming ends with a decision. Do not create a spec or plan document unless the artifact has durable coordination value or the user requests it.
