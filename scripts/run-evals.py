#!/usr/bin/env python3
"""Run paired Groundcraft evaluations, prepare blind review, and enforce the gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import time
import tomllib
import uuid
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "evals" / "cases.json"
PLUGIN = ROOT / "plugins" / "groundcraft"
RESULTS = Path(
    os.environ.get("GROUNDCRAFT_EVAL_RESULTS", Path.home() / "Developer" / "work" / "groundcraft" / "evals")
).expanduser().resolve()
ARMS = ("native", "sham", "groundcraft")
USAGE_FIELDS = (
    "input_tokens", "cached_input_tokens", "uncached_input_tokens", "output_tokens", "reasoning_output_tokens"
)
SAFE_ENVIRONMENT = (
    "PATH", "TMPDIR", "TMP", "TEMP", "LANG", "LC_ALL", "TERM", "SHELL", "USER",
    "SSL_CERT_FILE", "SSL_CERT_DIR", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
    "http_proxy", "https_proxy", "all_proxy", "no_proxy",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_catalog(path: Path | None = None) -> dict[str, object]:
    path = path or CATALOG
    return json.loads(path.read_text(encoding="utf-8"))


def cases(path: Path | None = None) -> list[dict[str, object]]:
    return list(load_catalog(path)["cases"])


def command_output(command: list[str]) -> str | None:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return completed.stdout.strip() or completed.stderr.strip() or None


def tree_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for candidate in sorted(item for item in path.rglob("*") if item.is_file()):
        relative = candidate.relative_to(path)
        if "__pycache__" in relative.parts or candidate.name == ".DS_Store":
            continue
        digest.update(str(relative).encode())
        digest.update(b"\0")
        digest.update(candidate.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_sha256(path: Path = PLUGIN) -> str:
    return tree_sha256(path)


def configured_model(override: str | None) -> str | None:
    if override:
        return override
    config = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser() / "config.toml"
    try:
        model = tomllib.loads(config.read_text(encoding="utf-8")).get("model")
    except (OSError, tomllib.TOMLDecodeError):
        return None
    return model if isinstance(model, str) and model else None


def select(
    available: list[dict[str, object]], case_id: str | None, suite: str | None, run_all: bool
) -> list[dict[str, object]]:
    if case_id:
        selected = [case for case in available if case["id"] == case_id]
    elif suite:
        selected = [case for case in available if suite in case["suites"]]
    elif run_all:
        selected = available
    else:
        raise SystemExit("select one of --case ID, --suite NAME, or --all")
    if not selected:
        raise SystemExit(f"no matching eval cases: {case_id or suite}")
    return selected


def prepare_workspace(case: dict[str, object], runtime: Path, arm: str, trial: int) -> Path:
    workspace = runtime / str(case["id"]) / arm / f"trial-{trial}"
    source = (ROOT / str(case["cwd"])).resolve() if "cwd" in case else None
    if source:
        if not source.is_relative_to(ROOT) or not source.is_dir():
            raise SystemExit(f"invalid eval cwd: {case['cwd']}")
        shutil.copytree(source, workspace)
    else:
        workspace.mkdir(parents=True)
    if case["sandbox"] == "workspace-write":
        subprocess.run(["git", "init", "-b", "main"], cwd=workspace, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Groundcraft Eval"], cwd=workspace, check=True)
        subprocess.run(["git", "config", "user.email", "eval@groundcraft.invalid"], cwd=workspace, check=True)
        subprocess.run(["git", "add", "-A"], cwd=workspace, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "test: initialize fixture"], cwd=workspace, capture_output=True, check=True)
    return workspace


def evaluation_prompt(case: dict[str, object], arm: str, extras: dict[str, Path] | None = None) -> str:
    invocation = None if arm == "native" else "groundcraft" if arm in {"sham", "groundcraft"} else arm
    lead = f"Use ${invocation}. " if case["invocation"] == "explicit" and invocation else ""
    boundary = (
        "Work only in this disposable repository; do not push or create external state."
        if case["sandbox"] == "workspace-write"
        else "Work read-only; do not modify files or external state."
    )
    return f"{lead}Handle this request as you would for the user. {boundary}\n\n{case['prompt']}"


def copy_skill(source: Path, target: Path) -> None:
    if not (source / "SKILL.md").is_file():
        raise SystemExit(f"invalid eval skill: {source}")
    shutil.copytree(source, target / source.name)


def sham_skill_text() -> str:
    real = (PLUGIN / "skills" / "groundcraft" / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = real.split("---", 2)[1].strip()
    return f"---\n{frontmatter}\n---\n\nHandle the request normally.\n"


def install_skill_source(source: Path, target: Path) -> None:
    if (source / "SKILL.md").is_file():
        copy_skill(source, target)
        return
    skills = [candidate for candidate in sorted(source.iterdir()) if (candidate / "SKILL.md").is_file()]
    if not skills:
        raise SystemExit(f"eval arm has no skills: {source}")
    for skill in skills:
        copy_skill(skill, target)


def install_skills(
    home: Path, arm: str = "groundcraft", case: dict[str, object] | None = None,
    extras: dict[str, Path] | None = None,
) -> None:
    target = home / ".agents" / "skills"
    target.mkdir(parents=True)
    if arm == "groundcraft":
        for skill in sorted((PLUGIN / "skills").iterdir()):
            if skill.is_dir():
                copy_skill(skill, target)
    elif arm == "sham":
        sham = target / "groundcraft"
        sham.mkdir()
        sham.joinpath("SKILL.md").write_text(sham_skill_text(), encoding="utf-8")
    elif arm in (extras or {}):
        install_skill_source(extras[arm], target)
    elif arm != "native":
        raise SystemExit(f"unknown eval arm: {arm}")
    for relative in (case or {}).get("skills", []):
        source = (ROOT / str(relative)).resolve()
        if not source.is_relative_to(ROOT):
            raise SystemExit(f"eval skill escapes repository: {relative}")
        copy_skill(source, target)


def isolated_environment(
    runtime: Path, workspace: Path, arm: str, case: dict[str, object], extras: dict[str, Path] | None = None
) -> dict[str, str]:
    home = runtime / "home"
    codex_home = home / ".codex"
    codex_home.mkdir(parents=True)
    auth = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser() / "auth.json"
    if not auth.is_file():
        raise SystemExit(f"Codex auth not found: {auth}")
    (codex_home / "auth.json").symlink_to(auth.resolve())
    install_skills(home, arm, case, extras)
    environment = {key: os.environ[key] for key in SAFE_ENVIRONMENT if key in os.environ}
    environment.update({"HOME": str(home), "CODEX_HOME": str(codex_home), "PWD": str(workspace)})
    return environment


def codex_command(
    case: dict[str, object], workspace: Path, model: str, arm: str = "groundcraft",
    extras: dict[str, Path] | None = None,
) -> list[str]:
    return [
        "codex", "exec", "--ephemeral", "--ignore-user-config", "--sandbox", str(case["sandbox"]),
        "--skip-git-repo-check", "--json", "--color", "never", "-C", str(workspace),
        "--model", model, evaluation_prompt(case, arm, extras),
    ]


def parse_events(stdout: str) -> tuple[str, int, dict[str, int] | None]:
    messages: list[str] = []
    tool_calls = 0
    usage: dict[str, int] | None = None
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        if event.get("type") == "item.completed" and isinstance(item, dict):
            if item.get("type") == "agent_message":
                messages.append(str(item.get("text", "")))
            elif item.get("type") not in {None, "reasoning"}:
                tool_calls += 1
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            raw = event["usage"]
            usage = {key: int(raw.get(key, 0)) for key in USAGE_FIELDS if key != "uncached_input_tokens"}
            usage["uncached_input_tokens"] = max(0, usage["input_tokens"] - usage["cached_input_tokens"])
    return "\n".join(messages), tool_calls, usage


def run_oracle(case: dict[str, object], workspace: Path, timeout: int) -> dict[str, object]:
    oracle = case["oracle"]
    if oracle["kind"] == "manual":
        return {"kind": "manual", "status": "unreviewed"}
    command = [
        str(part).replace("{root}", str(ROOT)).replace("{workspace}", str(workspace))
        for part in oracle["command"]
    ]
    try:
        completed = subprocess.run(command, cwd=workspace, capture_output=True, text=True, timeout=timeout)
        return {
            "kind": "command", "status": "pass" if completed.returncode == 0 else "fail",
            "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"kind": "command", "status": "fail", "exit_code": None, "stderr": str(exc)}


def run_trial(
    case: dict[str, object], runtime: Path, arm: str, trial: int, model: str, timeout: int,
    extras: dict[str, Path] | None = None,
) -> tuple[dict[str, object], str, Path]:
    workspace = prepare_workspace(case, runtime / "workspaces", arm, trial)
    environment = isolated_environment(
        runtime / "homes" / str(case["id"]) / arm / f"trial-{trial}", workspace, arm, case, extras
    )
    started = time.monotonic()
    try:
        completed = subprocess.run(
            codex_command(case, workspace, model, arm, extras), capture_output=True, text=True,
            timeout=timeout, env=environment,
        )
        exit_code: int | None = completed.returncode
        stdout, stderr = completed.stdout, completed.stderr
        execution = "pass" if exit_code == 0 else "fail"
    except (OSError, subprocess.TimeoutExpired) as exc:
        exit_code, stdout, stderr, execution = None, "", str(exc), "fail"
    response, tool_calls, usage = parse_events(stdout)
    oracle = run_oracle(case, workspace, timeout)
    result = {
        "case_id": case["id"], "arm": arm, "trial": trial, "run_at": utc_now(),
        "duration_seconds": round(time.monotonic() - started, 3),
        "execution": {"status": execution, "exit_code": exit_code, "stderr": stderr},
        "response": response, "tool_calls": tool_calls, "usage": usage, "oracle": oracle,
        "git_status": command_output(["git", "-C", str(workspace), "status", "--short"])
        if (workspace / ".git").exists() else None,
        "git_diff": command_output(["git", "-C", str(workspace), "diff", "--no-ext-diff"])
        if (workspace / ".git").exists() else None,
        "hard_failure": execution != "pass" or oracle["status"] == "fail",
    }
    return result, stdout, workspace


def review_packet(case: dict[str, object], result: dict[str, object]) -> dict[str, object]:
    return {
        "prompt": case["prompt"], "response": result["response"], "oracle": result["oracle"],
        "git_status": result["git_status"], "git_diff": result["git_diff"],
        "rubric": {"must": case["must"], "must_not": case["must_not"]},
        "decision_schema": {
            "status": "pass | fail | unknown", "reviewer": "non-empty identifier",
            "notes": "evidence for the decision", "reviewed_at": "ISO-8601 timestamp",
        },
    }


def materialize(
    run_dir: Path, opaque_id: str, case: dict[str, object], result: dict[str, object], events: str, workspace: Path
) -> None:
    candidate = run_dir / "private" / "candidates" / opaque_id
    candidate.mkdir(parents=True)
    (candidate / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (candidate / "events.jsonl").write_text(events, encoding="utf-8")
    shutil.move(str(workspace), candidate / "workspace")
    packets = run_dir / "review" / "packets"
    packets.mkdir(parents=True, exist_ok=True)
    (packets / f"{opaque_id}.json").write_text(
        json.dumps(review_packet(case, result), indent=2) + "\n", encoding="utf-8"
    )


def dry_run(selected: list[dict[str, object]], repeat: int | None, arms: list[str]) -> int:
    for case in selected:
        print(
            f"{case['id']}\ttrials={repeat or case['trials']}\ttype={case['task_type']}\t"
            f"suites={','.join(case['suites'])}\tinvocation={case['invocation']}\tarms={','.join(arms)}"
        )
    return 0


def parse_extra_arms(values: list[str]) -> dict[str, Path]:
    extras: dict[str, Path] = {}
    for value in values:
        name, separator, raw_path = value.partition("=")
        if not separator or not re.fullmatch(r"[a-z][a-z0-9-]*", name):
            raise SystemExit("--extra-arm must use name=/path/to/skill-or-skills")
        path = Path(raw_path).expanduser().resolve()
        if not path.is_dir():
            raise SystemExit(f"extra arm path is not a directory: {path}")
        skill_names = {path.name} if (path / "SKILL.md").is_file() else {
            candidate.name for candidate in path.iterdir() if (candidate / "SKILL.md").is_file()
        }
        if name not in skill_names:
            raise SystemExit(f"extra arm {name} must contain a matching {name}/SKILL.md")
        if name in ARMS or name in extras:
            raise SystemExit(f"duplicate or reserved extra arm: {name}")
        extras[name] = path
    return extras


def validate_arms(arms: list[str], extras: dict[str, Path] | None = None) -> list[str]:
    invalid = sorted(set(arms) - set(ARMS) - set(extras or {}))
    if invalid:
        raise SystemExit(f"unknown eval arms: {', '.join(invalid)}")
    return list(dict.fromkeys(arms))


def aggregate_usage(results: list[dict[str, object]]) -> dict[str, int] | None:
    measured = [result["usage"] for result in results if result.get("usage")]
    if not measured:
        return None
    return {key: sum(int(item[key]) for item in measured) for key in USAGE_FIELDS}


def execute(
    selected: list[dict[str, object]], repeat: int | None, model: str | None, timeout: int,
    run_id: str | None, arms: list[str], seed: int, catalog_path: Path, extras: dict[str, Path],
) -> int:
    resolved_model = configured_model(model)
    if not resolved_model:
        raise SystemExit("pass --model or configure a default Codex model")
    if RESULTS == ROOT or RESULTS.is_relative_to(ROOT):
        raise SystemExit("GROUNDCRAFT_EVAL_RESULTS must be outside the repository")
    identifier = run_id or f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", identifier):
        raise SystemExit("run id must be a safe 1-80 character directory name")
    run_dir = RESULTS / identifier
    if run_dir.exists():
        raise SystemExit(f"run already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    jobs = [
        (case, arm, trial)
        for case in selected for trial in range(1, (repeat or int(case["trials"])) + 1) for arm in arms
    ]
    random.Random(seed).shuffle(jobs)
    assignments: dict[str, dict[str, object]] = {}
    results: list[dict[str, object]] = []
    started_at = utc_now()
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix=f"groundcraft-{identifier}-", dir=RESULTS.parent) as temporary:
        runtime = Path(temporary)
        for position, (case, arm, trial) in enumerate(jobs, start=1):
            opaque_id = f"sample-{uuid.uuid4().hex[:12]}"
            assignments[opaque_id] = {"case_id": case["id"], "arm": arm, "trial": trial, "position": position}
            print(f"running sample {position}/{len(jobs)}", flush=True)
            result, events, workspace = run_trial(case, runtime, arm, trial, resolved_model, timeout, extras)
            results.append(result)
            materialize(run_dir, opaque_id, case, result, events, workspace)
    private = run_dir / "private"
    private.mkdir(exist_ok=True)
    (private / "assignment-key.json").write_text(json.dumps(assignments, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": 3, "run_id": identifier, "started_at": started_at, "model": resolved_model,
        "arms": arms, "seed": seed, "source_sha256": source_sha256(),
        "arm_sha256": {
            arm: source_sha256() if arm == "groundcraft"
            else hashlib.sha256(sham_skill_text().encode()).hexdigest() if arm == "sham"
            else tree_sha256(extras[arm]) if arm in extras else None
            for arm in arms
        },
        "catalog_path": str(catalog_path), "catalog_sha256": file_sha256(catalog_path),
        "git_commit": command_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"]),
        "git_status": command_output(["git", "-C", str(ROOT), "status", "--short"]),
        "git_divergence": command_output(
            ["git", "-C", str(ROOT), "rev-list", "--left-right", "--count", "HEAD...origin/main"]
        ),
        "codex_version": command_output(["codex", "--version"]),
        "python_version": command_output(["python3", "--version"]),
        "cases": selected,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    failures = sum(bool(result["hard_failure"]) for result in results)
    summary = {
        "run_id": identifier, "finished_at": utc_now(),
        "duration_seconds": round(time.monotonic() - started, 3),
        "cases": len(selected), "candidates": len(results), "hard_failures": failures,
        "semantic_unreviewed": len(results), "usage": aggregate_usage(results),
        "release_status": "failed" if failures else "awaiting_blind_review",
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(run_dir)
    print(json.dumps(summary, indent=2))
    return 1 if failures else 0


def read_decision(path: Path) -> tuple[dict[str, object] | None, str | None]:
    try:
        decision = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(decision, dict) or decision.get("status") not in {"pass", "fail", "unknown"}:
        return None, "status must be pass, fail, or unknown"
    if not all(isinstance(decision.get(field), str) and decision[field].strip() for field in ("reviewer", "notes", "reviewed_at")):
        return None, "reviewer, notes, and reviewed_at must be non-empty strings"
    return decision, None


def comparative_summary(records: list[dict[str, object]]) -> dict[str, object]:
    grouped: dict[tuple[str, int], dict[str, dict[str, object]]] = {}
    for record in records:
        key = (str(record["case_id"]), int(record["trial"]))
        grouped.setdefault(key, {})[str(record["arm"])] = record
    arms = sorted({str(record["arm"]) for record in records} | {"groundcraft"})
    quality = {arm: {"wins": 0, "losses": 0, "ties": 0, "unknown": 0} for arm in arms}
    efficiency: dict[str, dict[str, float | int | None]] = {}
    for group in grouped.values():
        groundcraft = group.get("groundcraft")
        if not groundcraft:
            continue
        for other_arm in (arm for arm in arms if arm != "groundcraft"):
            other = group.get(other_arm)
            if not other or "unknown" in {groundcraft["status"], other["status"]}:
                quality["groundcraft"]["unknown"] += 1
                continue
            if groundcraft["status"] == other["status"]:
                quality["groundcraft"]["ties"] += 1
                quality[other_arm]["ties"] += 1
            elif groundcraft["status"] == "pass":
                quality["groundcraft"]["wins"] += 1
                quality[other_arm]["losses"] += 1
            else:
                quality["groundcraft"]["losses"] += 1
                quality[other_arm]["wins"] += 1
    for other_arm in (arm for arm in arms if arm != "groundcraft"):
        deltas: dict[str, list[float]] = {"tokens": [], "tool_calls": [], "duration_seconds": []}
        for group in grouped.values():
            groundcraft, other = group.get("groundcraft"), group.get(other_arm)
            if not groundcraft or not other or {groundcraft["status"], other["status"]} != {"pass"}:
                continue
            groundcraft_usage, other_usage = groundcraft.get("usage"), other.get("usage")
            if groundcraft_usage and other_usage:
                deltas["tokens"].append(
                    float(groundcraft_usage["input_tokens"] + groundcraft_usage["output_tokens"])
                    - float(other_usage["input_tokens"] + other_usage["output_tokens"])
                )
            deltas["tool_calls"].append(float(groundcraft["tool_calls"]) - float(other["tool_calls"]))
            deltas["duration_seconds"].append(
                float(groundcraft["duration_seconds"]) - float(other["duration_seconds"])
            )
        efficiency[other_arm] = {
            "paired_passes": len(deltas["duration_seconds"]),
            **{
                f"mean_{name}_delta": round(sum(values) / len(values), 3) if values else None
                for name, values in deltas.items()
            },
        }
    groundcraft = quality["groundcraft"]
    support = (
        "supported" if groundcraft["wins"] > 0 and groundcraft["losses"] == 0 and groundcraft["unknown"] == 0
        else "not_supported" if groundcraft["losses"] > 0
        else "inconclusive"
    )
    return {"quality": quality, "efficiency_groundcraft_minus": efficiency, "groundcraft_claim": support}


def gate_run(run_dir: Path, artifact: Path, suites: list[str]) -> int:
    try:
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        assignments = json.loads((run_dir / "private" / "assignment-key.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid run: {exc}")
    errors: list[str] = []
    if manifest.get("git_status"):
        errors.append("evaluation did not start from a clean repository")
    if manifest.get("git_divergence") not in {"0\t0", "0 0"}:
        errors.append("evaluation commit was not synchronized with origin/main")
    if not set(ARMS) <= set(manifest.get("arms", [])):
        errors.append("release comparison requires native, sham, and groundcraft arms")
    current_hash = source_sha256(artifact)
    if manifest.get("source_sha256") != current_hash:
        errors.append("evaluated source hash does not match the artifact")
    cases_by_id = {str(case["id"]): case for case in manifest.get("cases", [])}
    required_cases = {
        str(case["id"]) for case in cases() if any(suite in case.get("suites", []) for suite in suites)
    }
    if not required_cases:
        errors.append(f"catalog contains no cases for required suites: {', '.join(suites)}")
    missing_cases = required_cases - set(cases_by_id)
    if missing_cases:
        errors.append(f"run is missing required cases: {', '.join(sorted(missing_cases))}")
    records: list[dict[str, object]] = []
    covered: dict[str, set[str]] = {case_id: set() for case_id in required_cases}
    for opaque_id, assignment in assignments.items():
        case_id, arm = str(assignment["case_id"]), str(assignment["arm"])
        if case_id not in required_cases:
            continue
        covered[case_id].add(arm)
        result_path = run_dir / "private" / "candidates" / opaque_id / "result.json"
        decision_path = run_dir / "review" / "decisions" / f"{opaque_id}.json"
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{opaque_id}: invalid result: {exc}")
            continue
        decision, error = read_decision(decision_path)
        if error:
            errors.append(f"{opaque_id}: invalid or missing review: {error}")
            status = "unknown"
        else:
            status = str(decision["status"])
        records.append({
            **assignment, "status": status, "usage": result.get("usage"),
            "tool_calls": result.get("tool_calls", 0), "duration_seconds": result.get("duration_seconds"),
        })
        if arm == "groundcraft":
            if result.get("hard_failure"):
                errors.append(f"{opaque_id}: Groundcraft hard failure")
            if status != "pass":
                errors.append(f"{opaque_id}: Groundcraft semantic status is {status}")
    for case_id, arms in covered.items():
        missing = set(manifest.get("arms", [])) - arms
        if missing:
            errors.append(f"{case_id}: missing arms {', '.join(sorted(missing))}")
    comparison = comparative_summary(records)
    gate = {
        "run_id": manifest.get("run_id"), "checked_at": utc_now(), "artifact": str(artifact.resolve()),
        "artifact_sha256": current_hash, "required_suites": suites, "errors": errors,
        "comparison": comparison, "status": "pass" if not errors else "fail",
    }
    (run_dir / "gate.json").write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(gate, indent=2))
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--case")
    selection.add_argument("--suite")
    selection.add_argument("--all", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--repeat", type=int)
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--run-id")
    parser.add_argument("--arms", nargs="+", default=["groundcraft"])
    parser.add_argument("--extra-arm", action="append", default=[])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--gate-run", type=Path)
    parser.add_argument("--artifact", type=Path, default=PLUGIN)
    parser.add_argument("--required-suite", action="append", default=[])
    args = parser.parse_args()
    if args.repeat is not None and args.repeat < 1:
        parser.error("--repeat must be positive")
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    if args.gate_run:
        if args.case or args.suite or args.all or args.list or args.dry_run:
            parser.error("--gate-run cannot be combined with selection or dry-run")
        return gate_run(args.gate_run.resolve(), args.artifact.resolve(), args.required_suite or ["regression", "safety"])
    available = cases(args.catalog.resolve())
    extras = parse_extra_arms(args.extra_arm)
    arms = validate_arms(args.arms, extras)
    if args.list:
        if args.case or args.suite or args.all:
            parser.error("--list cannot be combined with a selection")
        return dry_run(available, None, arms)
    selected = select(available, args.case, args.suite, args.all)
    return dry_run(selected, args.repeat, arms) if args.dry_run else execute(
        selected, args.repeat, args.model, args.timeout, args.run_id, arms, args.seed, args.catalog.resolve(), extras
    )


if __name__ == "__main__":
    raise SystemExit(main())
