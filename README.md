# Groundcraft

Evidence-driven autonomous work for Codex.

Groundcraft gives Codex one adaptive operating method instead of a catalog of commands. Codex can select its skill implicitly when substantial software, research, analysis, planning, decision, artifact, review, or operational work matches the description. The method scales to task type, size, and risk, acts autonomously on safe local work, and stops for human decisions or external consequences.

It stays lightweight for casual conversation, simple translation or formatting, trivial stable facts, and free ideation. Domain skills remain in charge of their own procedures.

## What it optimizes

- verified outcomes and useful deliverables, not generated volume;
- autonomy proportional to reversibility;
- small coherent changes and evidence worth the user's wait;
- minimal sufficient context;
- maintainable code without unnecessary ceremony;
- useful research and decisions without pretending every prompt is a software project.

The operating loop is:

```text
Ground -> Trace -> Shape -> Build -> Prove -> Land
```

See [the methodology](docs/methodology.md) for the constitution, classifiers, authority model, and completion contract.

## When to use it

Groundcraft is the cross-cutting option when one task must move from uncertain intent to a verified outcome while respecting authority. More specialized systems remain better fits for their own lane:

| Need | Better fit |
| --- | --- |
| Adaptive work across software, research, analysis, decisions, review, and operations | Groundcraft |
| Small task already governed by repository or domain instructions | Native Codex only |
| Strict test-driven software workflow | Superpowers |
| Shared specification artifacts and change proposals | OpenSpec or Spec Kit |
| Long, phase-heavy project execution | GSD |
| Browser-heavy QA and release operations | gstack |
| Reusable engineering knowledge and workflow catalog | Compound Engineering |

Groundcraft composes with domain skills instead of replacing them. It is not a spec store, project manager, browser suite, or command catalog.

The reason to keep a separate system is narrow: Codex already supplies skills, plans, goals, subagents, and task continuity; Groundcraft adds one small policy layer for when to use them, what authority exists, which context matters, and what evidence permits completion across domains. That distinction is now tested against native Codex and a neutral sham. Until reviewed comparisons discriminate outcomes, Groundcraft makes no superiority claim.

## Install

```bash
codex plugin marketplace add tavaresgmg/groundcraft
codex plugin add groundcraft@groundcraft
```

Start a new Codex thread after installation. Groundcraft has no required slash commands; Codex may choose its skill through native implicit matching. A small `SubagentStart` hook adds a reminder about scope, authority, and evidence when delegation starts. Its output is injected only on that event. Codex requires you to review and trust non-managed hooks through `/hooks` before they run.

If hooks are disabled or untrusted, the implicit skill and native subagents remain available; only the delegated-work reminder is absent. The skill can also be invoked explicitly as `$groundcraft`.

The plugin also installs `$groundcraft-handoff`. Active work stays in the host's native task, goal, and plan. Use the companion only for an explicit portable export when the original task cannot be resumed, or when the user asks for it. The skill uses compact records under `${CODEX_HOME:-$HOME/.codex}/groundcraft/handoffs/`; its helper validates, lists, and safely migrates them. Active handoffs never live in the repository or versioned plugin cache. Existing `~/Developer/work/handoffs/` files are migrated only when the portable store is empty; conflicting populated stores require manual resolution.

The handoff companion currently requires a POSIX shell (macOS or Linux). Groundcraft's core skill and subagent hook remain host-neutral.

## Structure

```text
plugins/groundcraft/              installable Codex plugin
  hooks/hooks.json                delegated-work boundary
  skills/groundcraft-handoff/     explicit cross-thread continuity
docs/methodology.md               human-readable method
docs/sources.md                   source lineage and evidence
evals/cases.json                  behavioral contract cases
scripts/validate.py               dependency-free structural validation
scripts/validate-fixtures.py      fail-to-pass reference-oracle validation
scripts/run-evals.py              focused behavioral runner
scripts/check-sources.py          informational upstream-version check
scripts/install-local.py          clean local development install
tests/test_cli.py                 validator and harness CLI regression tests
```

## Local development

Every validated `main` change receives the smallest truthful pre-1.0 release; `1.0.0` remains an explicit product decision. During active development and after publishing, keep the current source installed through the generated local marketplace:

```bash
python3 scripts/install-local.py
```

The command validates the source, copies only the plugin and marketplace metadata to `${CODEX_HOME:-$HOME/.codex}/groundcraft/dev-marketplace`, applies a local cachebuster there, and reinstalls `groundcraft@groundcraft`. The repository manifest stays unchanged. Start a new Codex thread after each reinstall.

## Validate

```bash
python3 scripts/validate.py
```

Behavioral changes require a case in `evals/cases.json` that identifies task type, suite, authority, desired behavior, and the failure mode the rule prevents.

CI validates structure and contracts deterministically. Behavioral cases require fresh-context execution and independent calibrated review; they are not declared passing merely because their JSON schema is valid. Run one case, a suite, or the full catalog:

```bash
python3 scripts/run-evals.py --case tiny-label-change
python3 scripts/run-evals.py --all --repeat 1 --arms native sham groundcraft --seed 20260712
python3 scripts/run-evals.py --gate-run ~/Developer/work/groundcraft/evals/<run-id>
```

The paired run randomizes native Codex, a neutral sham skill, and Groundcraft across isolated homes and workspaces. It records provenance privately and emits label-blind review packets under `~/Developer/work/groundcraft/evals/`. The release gate requires complete independent decisions for affected regression and safety cases, a clean synchronized evaluation commit, and an exact source-hash match. A comparative result may remain `inconclusive`; the gate does not turn binary rubrics into a superiority claim.

Periodic competitor checks use `--extra-arm name=/path/to/skill-or-skills`; the runner records the local source hash but never downloads or vendors another framework.

Before a release, `python3 scripts/check-sources.py` reports drift in mutable upstream version references. It is intentionally informative rather than a network-dependent CI gate.

## Status

Groundcraft is Codex-first. The methodology is host-neutral, while delegated-work hooks and installation currently target Codex plugins.

## License

[MIT](LICENSE). Groundcraft is an original synthesis. The projects and engineering sources that informed it are credited in [docs/sources.md](docs/sources.md).
