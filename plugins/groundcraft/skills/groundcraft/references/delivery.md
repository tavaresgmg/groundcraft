# Delivery

Land only verified, reviewable work.

## Git and integration

Follow [workspace.md](workspace.md) plus controlling repository and user instructions for branch, worktree, commit, synchronization, push, and pull request behavior. Before external delivery:

1. inspect status, staged changes, and full relevant diff;
2. exclude unrelated, generated, temporary, secret, or agent-state files;
3. rerun validation affected by final edits;
4. confirm branch, remote, upstream, and divergence;
5. obtain any required approval before push, PR, release, or deployment.

Never overwrite, stash, revert, or absorb another person's work without authorization.

For a release or deployment, verify that the reviewed artifact is the artifact delivered. Use provenance, staged rollout, target-state observation, abort criteria, and rollback according to risk. A canary reduces blast radius but does not prove paths it did not exercise.

## Communication

Progress updates should state what changed in understanding, evidence, or risk. Do not narrate obvious tool use.

Close with:

- `finding/changed`;
- `validated`;
- `not validated`;
- `remaining risk`;
- `next approval`, only when needed.

Treat PRs, reviews, issues, tickets, release notes, and messages as claims even while they are drafts. Keep every factual statement traceable to evidence; when evidence is missing, request it or write explicit uncertainty instead of the desired claim. Show supported text and request approval before publishing or sending when controlling instructions require it.

## Cleanup

Remove temporary files, local eval artifacts, dead code, stale plans, unnecessary backups, and processes started during work. Preserve durable handoffs only while work remains incomplete. Do not call work complete while a safe relevant validation, synchronization, or cleanup step remains.
