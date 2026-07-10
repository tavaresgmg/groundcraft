# Evaluation contract

Groundcraft evaluates outcomes and failure prevention, not whether an agent repeats the method.

## Cases

The catalog stays between 10 and 14 cases. Each case must cover a distinct failure surface and declares:

- task type, size, risk, authority, sandbox, and invocation mode;
- expected direct or full behavior;
- a small semantic `must` and `must_not` rubric;
- either a deterministic command oracle or manual review;
- one to three trials, with repetition reserved for stochastic or high-risk behavior.

The four suites have separate jobs: `regression` protects known behavior, `capability` probes harder behavior, `safety` checks authority and state boundaries, and `activation` checks when Groundcraft should stay direct or become active.

## Runner

The runner copies the current skills into a clean Codex home and executes each case ephemerally in a disposable workspace outside the repository. It relies on native implicit skill matching and does not inject plugin hook text as developer instructions. Writable fixtures receive a fresh Git repository. Hidden reference patches and command oracles are not included in the prompt, and rubrics are written only after execution. Native subagent spawning is validated in a real host session rather than claimed from this ephemeral CLI harness.

Each run records the model, plugin source hash, Git commit and status, response trace, workspace state, deterministic oracle result, and pending semantic rubric. This is enough to identify what ran without maintaining a second plugin installer, cross-platform sandbox layer, control experiment, or telemetry system.

Native Codex sandboxing and clean workspaces reduce accidental contamination; they are not an adversarial secrecy boundary. A manual case remains `unreviewed` until a fresh reviewer compares its response and side effects with the rubric. `exit 0` alone never becomes behavioral success.

## Release gate

Before release:

1. structural validation and both fail-to-pass fixture checks pass;
2. affected regression and safety cases have no hard or semantic failure;
3. repeated trials report every result, not the best one;
4. capability limits and unreviewed surfaces remain explicit;
5. the reviewed source hash matches the delivered artifact.

No score compensates for an authority breach, contaminated fixture, invalid oracle, or different delivered artifact.

## Commands

```bash
python3 scripts/run-evals.py --list
python3 scripts/run-evals.py --case tiny-label-change
python3 scripts/run-evals.py --suite activation --repeat 2
python3 scripts/run-evals.py --all --repeat 1 --dry-run
```

Runs are stored outside the repository under `~/Developer/work/groundcraft/evals/<run-id>/`. Set `GROUNDCRAFT_EVAL_RESULTS` to use another external workspace.
