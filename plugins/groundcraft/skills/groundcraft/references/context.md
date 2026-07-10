# Context

Context is a working set, not an archive.

## Build the working set

Keep only what the current decision requires:

- objective and definition of done;
- controlling instructions and constraints;
- decisions and their evidence;
- relevant artifacts, data, files, sources, tests, and runtime state;
- current blocker or next action.

Prefer focused searches, symbols, diffs, and short command output. Summarize long material; do not paste entire trees, logs, documentation, or conversations without demonstrated need.

Start with no auxiliary reference. Load a module, file, source, or tool only when it resolves a current uncertainty. When evidence grows, replace raw history with the smallest decision-and-proof record that preserves safe continuation.

## Quarantine unrelated state

Match persisted context to the current objective, repository, artifact, and authority before using it. Ignore unrelated handoffs, plans, branches, memories, and pending tasks unless they create a concrete collision, dependency, or permission constraint. Do not mention them merely because they exist, and never use one task's incomplete state as evidence about another task's outcome.

## Scale

- `tiny`: no plan artifact; inspect, change, prove, close.
- `standard`: short internal plan with likely artifacts, ordered actions, proof, and material risk.
- `large`: vertical slices, checkpoints after each slice, and a compact context capsule for continuity.

Use host-native goals, plans, threads, trackers, or handoffs. Do not create repository-local Groundcraft state, specs, or plans by default. Durable project artifacts require collaboration value or an explicit request.

When a host goal or plan already exists, treat it as the active execution record and update it without mirroring it elsewhere. Never create a goal or assign a token budget unless the user explicitly requested that lifecycle.

Keep one owner for each kind of state:

- the current thread, goal, and plan own active execution;
- a handoff owns only unfinished cross-session continuity;
- long-term memory owns stable preferences and prior decisions, with date and provenance when drift matters;
- code, runtime, tests, logs, and current sources own present factual truth.

Retrieve memory only when the task depends on prior context. Treat it as a clue, preserve conflicts, and revalidate facts that may have changed. Do not duplicate the same state across these layers.

Prefer the narrowest purpose-built tool whose output directly observes the needed claim. Batch independent read-only calls; sequence mutations and verify their postcondition from canonical state. Use native subagents for independent bounded branches with material latency, specialization, noise-isolation, or review benefit; never make several agents rediscover the same context.

## Context capsule

For `large` work, update the host's durable thread, goal, plan, or tracker after each delivered slice and before compaction or interruption. Use `$groundcraft-handoff` only for explicit cross-thread export, known continuation where native persistence is unavailable, or when the user asks. If no durable mechanism exists, put the capsule in the closing response, state that continuity is not guaranteed, and create a file only with authorization and outside the repository by default.

Retain only:

```text
objective:
done:
decisions:
evidence:
changed:
validated:
open:
next:
risk:
```

On resume, read the capsule, then revalidate Git state, current diff, dependencies, external state, and any time-sensitive assumption before continuing. Never treat a capsule as current evidence merely because it persisted.

## Delegation

Default to native subagents when work has two or more independent evidence branches, a useful specialist boundary, large noisy inputs, or a justified fresh review. Give each agent a distinct question, shared output contract, and raw artifact rather than the parent's conclusion. Keep sequential dependencies and tightly coupled context with the parent; use one writer per worktree. The parent retains authority, resolves contradictions, verifies delegated claims, and synthesizes the result instead of concatenating reports.

For adversarial review, fresh context must not receive the expected answer or suspected defect. If the host cannot provide a fresh agent or thread, perform a separate self-review pass with the narrowest reconstructed context and report that independent review was not validated.
