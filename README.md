# Groundcraft

Evidence-driven autonomous work for Codex.

Groundcraft gives Codex one adaptive operating method instead of a catalog of commands. It starts automatically for substantial software, research, analysis, planning, decision, artifact, review, and operational work; scales process to task type, size, and risk; works autonomously on safe local actions; and stops for human decisions or external consequences.

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

## Install

```bash
codex plugin marketplace add tavaresgmg/groundcraft
codex plugin add groundcraft@groundcraft
```

Start a new Codex thread after installation. Groundcraft has no required slash commands and its skill is chosen through native implicit matching. A small `SubagentStart` hook preserves scope, authority, and evidence when Codex delegates work; it adds no prompt text to ordinary user turns. Codex requires you to review and trust non-managed hooks through `/hooks` before they run.

If hooks are disabled or untrusted, the implicit skill and native subagents remain available; only the delegated-work reminder is absent. The skill can also be invoked explicitly as `$groundcraft`.

The plugin also installs `$groundcraft-handoff`. Active work stays in the host's native thread, goal, and plan; the companion skill is used only for explicit cross-thread export, known continuation when native persistence is unavailable, or when requested. It stores compact resume records under `${CODEX_HOME:-$HOME/.codex}/groundcraft/handoffs/` and removes them after completion is proven. Active handoffs never live in the repository or versioned plugin cache. Existing `~/Developer/work/handoffs/` files are migrated before the first handoff operation only when the portable store is empty; conflicting populated stores require manual resolution.

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

CI validates structure and contracts deterministically. Behavioral cases require fresh-context execution and human-calibrated review; they are not declared passing merely because their JSON schema is valid. Run one case, a suite, or the full catalog:

```bash
python3 scripts/run-evals.py --case tiny-label-change
python3 scripts/run-evals.py --suite safety --repeat 2
python3 scripts/run-evals.py --all
```

The runner copies the current skill into a clean Codex home, uses disposable workspaces, and records the source hash, model, token usage, response trace, oracle result, Git state, and semantic rubric under `~/Developer/work/groundcraft/evals/`. It deliberately leaves `must` and `must_not` unreviewed instead of turning model self-review into a release claim.

## Status

Groundcraft is Codex-first. The methodology is host-neutral, while delegated-work hooks and installation currently target Codex plugins.

## License

[MIT](LICENSE). Groundcraft is an original synthesis. The projects and engineering sources that informed it are credited in [docs/sources.md](docs/sources.md).
