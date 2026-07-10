# Context

Context is a working set, not an archive.

## Build the working set

Keep only what the current decision requires:

- objective and definition of done;
- controlling instructions and constraints;
- decisions and their evidence;
- relevant files, symbols, callers, tests, and runtime state;
- current blocker or next action.

Prefer focused searches, symbols, diffs, and short command output. Summarize long material; do not paste entire trees, logs, documentation, or conversations without demonstrated need.

Start with no auxiliary reference. Load a module, file, source, or tool only when it resolves a current uncertainty. When evidence grows, replace raw history with the smallest decision-and-proof record that preserves safe continuation.

## Quarantine unrelated state

Match persisted context to the current objective, repository, artifact, and authority before using it. Ignore unrelated handoffs, plans, branches, memories, and pending tasks unless they create a concrete collision, dependency, or permission constraint. Do not mention them merely because they exist, and never use one task's incomplete state as evidence about another task's outcome.

## Scale

- `tiny`: no plan artifact; inspect, change, prove, close.
- `standard`: short internal plan with likely files, ordered changes, proof, and material risk.
- `large`: vertical slices, checkpoints after each slice, and a compact context capsule for continuity.

Use host-native goals, plans, threads, trackers, or handoffs. Do not create repository-local Groundcraft state, specs, or plans by default. Durable project artifacts require collaboration value or an explicit request.

## Context capsule

For `large` work, save a capsule after each integrated slice and before compaction, interruption, handoff, or session end. Use the host's durable goal, thread, tracker, or handoff mechanism. If no durable mechanism exists, put the capsule in the closing response, state that cross-thread continuity is not guaranteed, and create a file only with authorization and outside the repository by default.

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

Delegate only independent, bounded research, discovery, or review with material benefit. Give fresh agents a concrete question and raw artifact, not the parent's conclusion. Use one writer per worktree. Prevent several agents from rediscovering the same context.

For adversarial review, fresh context must not receive the expected answer or suspected defect. If the host cannot provide a fresh agent or thread, perform a separate self-review pass with the narrowest reconstructed context and report that independent review was not validated.
