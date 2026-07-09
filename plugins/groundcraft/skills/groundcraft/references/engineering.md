# Engineering

Optimize for the smallest correct and maintainable change, not the fewest lines.

## Trace before editing

1. Inspect Git status and relevant diffs. Preserve unrelated work.
2. Trace callers, tests, configuration, persistence, and external boundaries.
3. Reproduce the failure or establish current behavior when feasible.
4. Fix the shared root cause rather than the reported symptom.

## Design ladder

Stop at the first option that safely holds:

1. remove the need or reuse existing behavior;
2. follow an existing project pattern;
3. use the standard library or native platform;
4. use an already-installed dependency;
5. add the minimum new code or dependency justified by evidence.

Prefer deep modules with small public interfaces. Add an abstraction only when it hides a real changing decision or decouples real consumers. Do not add factories, interfaces, configuration, fallbacks, or compatibility paths for imagined futures.

## Dependencies

For a new dependency, verify maintenance, license, release history, compatibility, security posture, transitive cost, and what code it replaces. Compare that evidence with a small local implementation; recommend the lower-maintenance option, not automatically either side.

## Change boundary

Start narrow. Expand coherently when root cause, contract consistency, validation, safe migration, or obsolete-path removal requires it. Stop and confirm before redesigning central architecture, product behavior, core dependencies, or blast radius.

Keep behavior changes separate from broad formatting. Follow the repository toolchain. Update existing affected documentation when behavior changes; do not create documentation without need.

## Cleanup

Remove obsolete code, duplicate paths, temporary instrumentation, unused dependencies, stale comments, and processes started for validation. Do not hide unfinished correctness work behind a no-op, silent fallback, or TODO unless deferral is an explicit decision with visible risk.
