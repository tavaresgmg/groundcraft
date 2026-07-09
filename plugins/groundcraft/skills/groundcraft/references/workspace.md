# Workspace and Git

Use repository conventions first. Git isolation is a means of preventing collisions, not ceremony for every task.

## Before editing

1. Inspect status and relevant diff. Preserve unrelated changes.
2. Confirm repository root, current branch, remote, upstream, and divergence; fetch when current remote state matters.
3. Check whether the target branch already exists or is attached to another worktree.
4. Read the repository's contribution, branch, commit, ignore, and generated-file conventions.

## Branches and worktrees

- Use the current clean task branch when it is already correct.
- Create a branch for a coherent change when repository flow expects one. Follow its naming convention; do not invent a global convention over it.
- Use a separate worktree for parallel writers, long or interruptible work, risky experiments, or when isolation materially improves recovery.
- Do not create a worktree for a tiny sequential change with no collision risk.
- One writer owns a worktree at a time. Review and research agents remain read-only unless assigned an isolated worktree.
- Before resuming, revalidate branch, diff, upstream, dependencies, generated artifacts, and time-sensitive assumptions.

## Ignores, temporary files, and secrets

- Put disposable logs, eval results, downloads, and generated scratch data in the host's temporary workspace or the repository's established ignored path.
- Use `git check-ignore -v` to identify which rule applies. Respect global and repository ignore rules.
- Never ignore a real source, migration, test, or required project artifact merely to silence `git status`.
- Do not commit secrets, credentials, local agent state, private notes, editor state, or machine-specific caches.
- Before commit or delivery, inspect staged and unstaged diffs and remove temporary instrumentation, copied fixtures, and generated residue.

Never stash, reset, revert, force-update, delete, or absorb another person's work without authority. Before integration, synchronize with the target branch, resolve divergence explicitly, rerun affected proof, and confirm that the artifact reviewed is the artifact being delivered.
