# Groundcraft

Evidence-driven autonomous software engineering for Codex.

Groundcraft gives coding agents one adaptive operating method instead of a catalog of commands. It starts automatically, scales process to size and risk, works autonomously on safe local actions, and stops for human decisions or external consequences.

## What it optimizes

- verified outcomes, not generated code;
- autonomy proportional to reversibility;
- small coherent changes and fast feedback;
- minimal sufficient context;
- maintainable code without unnecessary ceremony.

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

Start a new Codex thread after installation. Groundcraft has no required slash commands. Its skill can be chosen implicitly, while a small plugin hook reminds Codex to apply it to software-engineering work. Codex requires you to review and trust non-managed hooks through `/hooks` before they run.

If hooks are disabled or untrusted, the implicit skill remains available and can be invoked explicitly as `$groundcraft`.

## Structure

```text
plugins/groundcraft/              installable Codex plugin
docs/methodology.md               human-readable method
docs/sources.md                   source lineage and evidence
evals/cases.json                  behavioral contract cases
scripts/validate.py               dependency-free validation
```

## Validate

```bash
python3 scripts/validate.py
```

Behavioral changes require a case in `evals/cases.json` that shows both the desired behavior and the failure mode the rule prevents.

CI validates structure and contracts deterministically. Behavioral cases require fresh-context execution and human-calibrated review; they are not declared passing merely because their JSON schema is valid. To run one case through a clean, read-only Codex session:

```bash
python3 scripts/run-evals.py --case tiny-label-change
```

The runner records the response under `.eval-results/` for review. Cases with a writable fixture run in a disposable copied repository and record its validation and Git state. Other cases remain read-only decision evaluations. The runner does not let the model grade itself.

## Status

Groundcraft is Codex-first. The methodology is host-neutral, but hook enforcement and installation currently target Codex plugins.

## License

[MIT](LICENSE). Groundcraft is an original synthesis. The projects and engineering sources that informed it are credited in [docs/sources.md](docs/sources.md).
