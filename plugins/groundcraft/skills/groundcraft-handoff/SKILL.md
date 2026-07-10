---
name: groundcraft-handoff
description: "Persist or resume unfinished Groundcraft work only for explicit cross-thread handoff or when native thread continuity is unavailable. Never scan it per task or use it for completed work."
---

# Groundcraft Handoff

Preserve only the context needed to resume unfinished work without reconstructing the previous session.

## Storage

- Store handoffs only in `${CODEX_HOME:-$HOME/.codex}/groundcraft/handoffs`. Never store runtime handoffs in a repository, skill, or plugin cache, and reject a symlink at the durable directory boundary.
- Name each file `<workspace>-<slug>.md` in lowercase ASCII kebab-case. Derive `workspace` from the Git root basename when inside a repository; otherwise use the current directory basename. Normalize it to lowercase ASCII kebab-case and use `pessoal` only when normalization is empty.
- On POSIX systems, run `scripts/handoffs` without a filter to validate and list the durable directory. Pass a workspace name only to narrow the listing; validation still covers every file.
- Run `scripts/handoffs --migrate-legacy` before the first handoff operation. It safely moves a valid legacy `$HOME/Developer/work/handoffs` store when the portable store is empty, and becomes a no-op after migration. Never merge two populated stores automatically.

## Start or resume

1. When the user requests a handoff, resumes exported work, or native thread continuity is unavailable for known unfinished work, run `scripts/handoffs --migrate-legacy`. This validates and lists the portable store.
2. Read only handoffs that match the current workspace and objective. If one matches, propose resuming it before starting duplicate work.
3. Do not surface unrelated pending or stale work unless it creates a concrete collision, dependency, or authority risk.
4. Surface a relevant `ALERTA` immediately.
5. On resume, treat the handoff as context, not current evidence. Revalidate Git state, tests, dependencies, external state, and time-sensitive assumptions.

## Create or update

Create a handoff when substantial work will remain unfinished after the current session or when the user asks. Before creating one, run `scripts/handoffs` and update an existing file for the same objective instead of duplicating it.

Use every field; write `nenhum` instead of omitting an empty field:

```md
# <objective in one line>

- workspace: <absolute path>
- branch: <branch | n/a>
- criado: YYYY-MM-DD | atualizado: YYYY-MM-DD
- status: em-andamento | bloqueado(<reason>)

## Pronto quando
<observable completion criterion>

## Estado
- [x] <completed item> (validado: <evidence>)
- [ ] <open item>

## Próximo passo
<first executable action on resume>

## Bloqueios e risco
<material blockers and risk | nenhum>

## Contexto
<key files, decisions, evidence, and known traps>
```

Update the handoff in the same session whenever its work advances. Record facts and evidence, never secrets. A risk is not a blocker; use `bloqueado(<reason>)` only when progress requires an unavailable dependency or human decision.

## Close

Delete the handoff as soon as its completion criterion is proven. Completed work must not remain in the durable directory. Do not create a handoff for a tiny task that finished in the current turn.
