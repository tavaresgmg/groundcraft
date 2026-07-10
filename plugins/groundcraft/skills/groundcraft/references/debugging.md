# Debugging

Debug by reducing uncertainty, not by accumulating patches.

## Protocol

1. State the observed symptom, expected behavior, impact, and last known good state.
2. Reproduce it with the smallest faithful case, or correlate logs, traces, state, and timing when reproduction is unsafe or impractical.
3. Trace the data and control path across boundaries. Mark what is observed versus inferred.
4. Form a small set of distinct plausible hypotheses. For each, identify a discriminating observation that could disprove it.
5. Instrument the boundary with the highest information gain. Mark temporary instrumentation and remove it after use.
6. Minimize the reproducer while preserving the failure. Check configuration, versions, environment, concurrency, and partial state.
7. Fix the causal mechanism at the narrowest shared boundary. Do not stack fallbacks or patch only the first visible caller.
8. Prove fail-to-pass when feasible, pass-to-pass for relevant behavior, and negative or partial-failure cases near the risk.
9. Remove instrumentation and workaround residue; record an escaped failure as a regression case.

## Stop conditions

After the same failure twice, stop editing. Reclassify whether the failure belongs to the hypothesis, implementation, test oracle, fixture, tool protocol, environment, or unstated requirement.

Escalate or report `blocked` when the evidence required to distinguish causes is unavailable, reproduction would cross authority, or the real environment cannot be represented faithfully. State the missing observation and the cheapest way to obtain it.
