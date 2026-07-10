# Decisions

Use this module for material choices, not every implementation detail.

## Decision brief

1. State the decision, outcome, constraints, and non-goals.
2. Generate two or three real options. Include doing nothing, native behavior, or reuse when credible.
3. Compare effect on correctness, user value, delivery cost, risk, reversibility, maintenance, and context load.
4. Run an adversarial pass: identify how each option fails, what assumption it hides, and what evidence would falsify it.
5. Recommend one path and explain why the rejected options lose here.

When uncertainty could reverse the decision, prefer the cheapest reversible experiment that discriminates between options. Do not convert uncertainty into a weighted score whose precision the evidence cannot support.

Do not manufacture alternatives when one path is clearly required by evidence or repository convention.

For a material comparison, fix the criteria and falsifiers before favoring an option. Check whether reversing the option order changes the judgment; if it does, treat the result as a tie or unresolved bias and buy external evidence. Skip this pass for obvious, low-cost, reversible choices.

Order work by dependencies and decision value: satisfy authority gates and shared contracts first, then the cheapest observation that can invalidate the approach, then the smallest coherent value slice and its direct proof. Defer broad regression, rollout, cleanup, and polish until their prerequisites or risk make them relevant. Parallelize only independent branches. State what new evidence would reorder the queue; do not use a precise score without precise inputs.

## Human decision

- Choose autonomously when the option is safe, reversible, and does not materially alter product or architecture.
- Recommend and confirm when taste, product intent, central architecture, core dependency, cost, or blast radius changes.
- Present critical actions as `go/no-go` only after impact, evidence, and rollback or mitigation are known when applicable.

Ask at most one to three questions at once. Put the recommended option first. If an answer is useful but non-blocking, state the safe default and continue.

## Change boundary

- `narrow`: direct local change; proceed;
- `coherent expansion`: include root cause, shared contract, required proof, or obsolete-path removal; proceed and explain at close;
- `redesign`: changes central architecture, product behavior, core dependency, or blast radius; confirm first.

Brainstorm only when distinct solution shapes could change the result. Generate two or three orthogonal options, eliminate dominated ones against the constraints, and converge to a recommendation. Do not create a spec or plan document unless the artifact has durable coordination value or the user requests it.
