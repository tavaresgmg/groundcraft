---
name: groundcraft-handoff
description: "Persist and resume unfinished Groundcraft work across Codex sessions. Use on the first substantial work turn to check relevant pending work; before pausing incomplete work; when resuming prior work; or when asked to create, update, list, or close a handoff. Do not use for tiny completed tasks."
---

# Groundcraft Handoff

Preserve only the context needed to resume unfinished work without reconstructing the previous session.

## Storage

- Store handoffs only in `$HOME/Developer/work/handoffs`. Never store runtime handoffs in a repository, skill, or plugin cache, and reject a symlink at the durable directory boundary.
- Name each file `<workspace>-<slug>.md` in lowercase ASCII kebab-case. Derive `workspace` from the first directory below `~/Developer` that contains the current working directory; use `pessoal` outside that tree.
- On POSIX systems, run `scripts/handoffs` without a filter to validate and list the durable directory. Pass a workspace name only to narrow the listing; validation still covers every file.

## Start or resume

1. Run `scripts/handoffs` once on the first substantial work turn in a thread.
2. Read handoffs that match the current workspace. If one matches the requested objective, propose resuming it before starting duplicate work.
3. If the user requested a different objective, mention a current-workspace handoff in one line and continue with the requested work.
4. Surface `ALERTA` immediately. Surface unrelated `STALE` entries only to decide whether to continue, update, or delete them.
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
