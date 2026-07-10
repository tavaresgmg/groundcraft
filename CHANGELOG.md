# Changelog

## 0.3.1 - 2026-07-09

- Moved durable handoffs to `${CODEX_HOME:-$HOME/.codex}/groundcraft/handoffs/` so storage no longer assumes a `~/Developer` layout.
- Added safe one-time migration from `~/Developer/work/handoffs/`, refusing invalid or conflicting stores before moving files.
- Derived handoff workspace names from the Git root or current directory instead of a machine-specific parent path.

## 0.3.0 - 2026-07-09

- Added the `groundcraft-handoff` companion skill for durable cross-session continuity.
- Integrated one-time pending-work checks into the first substantial Groundcraft turn while keeping tiny tasks direct.
- Kept active handoffs outside repositories and plugin caches under `~/Developer/work/handoffs/`.
- Added deterministic handoff validation and lifecycle regression coverage.

## 0.2.0 - 2026-07-09

- Generalized the small Groundcraft kernel to substantial research, analysis, decisions, reviews, and operations without activating it for trivial prompts.
- Added task-specific ready, done, blocked, and failed contracts plus outcome, non-regression, safety, and delivery proof surfaces.
- Added operational failure taxonomy, causal debugging protocol, and Git/worktree/ignore discipline.
- Added a focused 12-case runner with disposable workspaces, deterministic fixture oracles, repeat support, and minimal reproducibility metadata.
- Strengthened structural validation while removing brittle full-file string contracts.

## 0.1.0 - 2026-07-09

- Initial Groundcraft constitution and adaptive delivery loop.
- Automatic Codex skill with conditional research, decision, context, engineering, proof, and delivery modules.
- Minimal activation hooks for user prompts and subagents.
- Dependency-free structural validator and initial behavioral cases.
