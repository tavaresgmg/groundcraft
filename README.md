# Groundcraft

Evidence-driven autonomous work and software engineering for Codex.

Groundcraft gives Codex one adaptive operating method instead of a catalog of commands. It starts automatically for substantial software, research, analysis, decision, review, and operational work; scales process to task type, size, and risk; works autonomously on safe local actions; and stops for human decisions or external consequences.

It stays lightweight for casual conversation, simple translation or formatting, trivial stable facts, and free ideation. Domain skills remain in charge of their own procedures.

## What it optimizes

- verified outcomes, not generated code;
- autonomy proportional to reversibility;
- small coherent changes and fast feedback;
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

Start a new Codex thread after installation. Groundcraft has no required slash commands. Its skill can be chosen implicitly, while a small plugin hook reminds Codex when substantial work should use it and when trivial work should stay direct. Codex requires you to review and trust non-managed hooks through `/hooks` before they run.

If hooks are disabled or untrusted, the implicit skill remains available and can be invoked explicitly as `$groundcraft`.

The plugin also installs `$groundcraft-handoff`. On the first substantial work turn, Groundcraft checks relevant unfinished work once. When work remains incomplete, the companion skill stores a compact resume record under `~/Developer/work/handoffs/`; after completion is proven, it removes that record. Tiny completed tasks skip this path. Active handoffs never live in the repository or plugin cache.

The handoff companion currently requires a POSIX shell (macOS or Linux). Groundcraft's core skill and activation hooks remain host-neutral.

## Structure

```text
plugins/groundcraft/              installable Codex plugin
  skills/groundcraft-handoff/     durable cross-session continuity
docs/methodology.md               human-readable method
docs/sources.md                   source lineage and evidence
evals/cases.json                  behavioral contract cases
scripts/validate.py               dependency-free structural validation
scripts/validate-fixtures.py      fail-to-pass reference-oracle validation
scripts/run-evals.py              focused behavioral runner
tests/test_cli.py                 validator and harness CLI regression tests
```

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

The runner copies the current skill into a clean Codex home, uses disposable workspaces, and records the source hash, model, response trace, oracle result, Git state, and semantic rubric under `~/Developer/work/groundcraft/evals/`. It deliberately leaves `must` and `must_not` unreviewed instead of turning model self-review into a release claim.

## Status

Groundcraft is Codex-first. The methodology is host-neutral, but hook enforcement and installation currently target Codex plugins.

## License

[MIT](LICENSE). Groundcraft is an original synthesis. The projects and engineering sources that informed it are credited in [docs/sources.md](docs/sources.md).
