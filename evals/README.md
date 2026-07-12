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

The runner copies the selected arm into a clean Codex home and executes each case ephemerally in a disposable workspace outside the repository. It relies on native implicit skill matching and does not inject plugin hook text as developer instructions. Writable fixtures receive a fresh Git repository. Hidden reference patches, command oracles, and rubrics are not included in the prompt; rubrics appear only in the review packet after execution. Native subagent spawning is validated in a real host session rather than claimed from this ephemeral CLI harness.

Each run records the model, plugin source hash, catalog hash, Git commit and divergence, Codex version, response trace, workspace state, deterministic oracle result, and pending semantic rubric. The harness stays dependency-free and uses Codex's own sandbox rather than claiming a second security boundary.

For comparative runs, the runner uses three paired arms:

- `native` has no Groundcraft skill and receives no explicit Groundcraft invocation;
- `sham` has the same activation name but a neutral one-line body;
- `groundcraft` installs the delivered plugin skills.

Every case, trial, and arm gets a fresh home and workspace. A recorded seed randomizes execution order. Optional case-level skills are installed in every arm, so composition with a domain procedure is tested rather than assumed. `--catalog` accepts a larger external hidden catalog without making the small public contract harder to review.

For periodic overlap checks, `--extra-arm name=/path/to/skill-or-skills` adds a locally supplied competitor without downloading, vendoring, or treating it as a release dependency. The path must expose a matching skill name, and its source hash is recorded. Extra arms receive the same cases and blind review; the three built-in arms remain mandatory for a release comparison.

Native Codex sandboxing and clean workspaces reduce accidental contamination; they are not an adversarial secrecy boundary. Review packets hide arm, seed, usage, timing, and private paths, but writing style may still reveal the method. A manual case remains `unreviewed` until a fresh reviewer compares its response and side effects with the rubric. `exit 0` alone never becomes behavioral success.

## Release gate

Before release:

1. structural validation and both fail-to-pass fixture checks pass;
2. affected regression and safety cases have complete blind decisions, and Groundcraft has no hard or semantic failure;
3. native, sham, and Groundcraft candidates are all present and every repeated trial is reported;
4. the run starts from a clean commit synchronized with `origin/main`;
5. capability limits remain explicit and the reviewed source hash matches the delivered artifact.

No score compensates for an authority breach, contaminated fixture, invalid oracle, or different delivered artifact.

## Commands

```bash
python3 scripts/run-evals.py --list
python3 scripts/run-evals.py --case tiny-label-change
python3 scripts/run-evals.py --suite activation --repeat 2 --arms native sham groundcraft --seed 20260712
python3 scripts/run-evals.py --case timeout-unit-root-cause --arms native sham groundcraft superpowers --extra-arm superpowers=~/path/to/superpowers
python3 scripts/run-evals.py --all --repeat 1 --arms native sham groundcraft --dry-run
python3 scripts/run-evals.py --gate-run ~/Developer/work/groundcraft/evals/<run-id>
```

Runs are stored outside the repository under `~/Developer/work/groundcraft/evals/<run-id>/`. Set `GROUNDCRAFT_EVAL_RESULTS` to use another external workspace.

The private assignment key maps each opaque sample to its arm, case, and trial. Give a reviewer only `review/packets/`. For every packet, place a matching JSON file in `review/decisions/` with `status`, `reviewer`, `notes`, and `reviewed_at`; the packet contains the exact schema. The gate writes `gate.json` with quality comparisons and efficiency deltas. Its comparative conclusion is only `supported`, `inconclusive`, or `not_supported`; an inconclusive comparison is not evidence of superiority.
