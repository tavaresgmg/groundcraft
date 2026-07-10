#!/usr/bin/env python3
"""Run focused Groundcraft behavioral cases and record review artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
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
USAGE_FIELDS = (
    "input_tokens", "cached_input_tokens", "uncached_input_tokens", "output_tokens", "reasoning_output_tokens"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def cases() -> list[dict[str, object]]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))["cases"]


def command_output(command: list[str]) -> str | None:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return completed.stdout.strip() or completed.stderr.strip() or None


def source_sha256() -> str:
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in PLUGIN.rglob("*") if candidate.is_file()):
        relative = path.relative_to(PLUGIN)
        if "__pycache__" in relative.parts or path.name == ".DS_Store":
            continue
        digest.update(str(relative).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def configured_model(override: str | None) -> str | None:
    if override:
        return override
    config = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser() / "config.toml"
    try:
        model = tomllib.loads(config.read_text(encoding="utf-8")).get("model")
    except (OSError, tomllib.TOMLDecodeError):
        return None
    return model if isinstance(model, str) and model else None


def select(case_id: str | None, suite: str | None, run_all: bool) -> list[dict[str, object]]:
    available = cases()
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


def prepare_workspace(case: dict[str, object], runtime: Path, trial: int) -> Path:
    workspace = runtime / str(case["id"]) / f"trial-{trial}"
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


def evaluation_prompt(case: dict[str, object]) -> str:
    lead = "Use $groundcraft. " if case["invocation"] == "explicit" else ""
    boundary = (
        "Work only in this disposable repository; do not push or create external state."
        if case["sandbox"] == "workspace-write"
        else "Work read-only; do not modify files or external state."
    )
    return f"{lead}Handle this request as you would for the user. {boundary}\n\n{case['prompt']}"


def hook_prompt() -> str:
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    command = hooks["UserPromptSubmit"][0]["hooks"][0]["command"]
    match = re.fullmatch(r"printf '%s\\n' '([^'\r\n]+)'", command)
    if not match:
        raise SystemExit("UserPromptSubmit hook must be one inert printf statement")
    return match.group(1)


def install_skills(home: Path) -> None:
    target = home / ".agents" / "skills"
    target.mkdir(parents=True)
    for skill in (PLUGIN / "skills").iterdir():
        if skill.is_dir():
            shutil.copytree(skill, target / skill.name)


def isolated_environment(runtime: Path, workspace: Path) -> dict[str, str]:
    home = runtime / "home"
    codex_home = home / ".codex"
    codex_home.mkdir(parents=True)
    auth = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser() / "auth.json"
    if not auth.is_file():
        raise SystemExit(f"Codex auth not found: {auth}")
    (codex_home / "auth.json").symlink_to(auth.resolve())
    install_skills(home)
    environment = os.environ.copy()
    environment.update({"HOME": str(home), "CODEX_HOME": str(codex_home), "PWD": str(workspace)})
    environment.pop("CODEX_THREAD_ID", None)
    return environment


def codex_command(case: dict[str, object], workspace: Path, model: str) -> list[str]:
    command = [
        "codex", "exec", "--ephemeral", "--ignore-user-config", "--sandbox", str(case["sandbox"]),
        "--skip-git-repo-check", "--json", "--color", "never", "-C", str(workspace),
        "-c", f"developer_instructions={json.dumps(hook_prompt())}", "--model", model,
        evaluation_prompt(case),
    ]
    return command


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
            usage = {
                key: int(raw.get(key, 0))
                for key in USAGE_FIELDS if key != "uncached_input_tokens"
            }
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
    case: dict[str, object], runtime: Path, trial: int, model: str, timeout: int
) -> tuple[dict[str, object], str, Path]:
    workspace = prepare_workspace(case, runtime / "workspaces", trial)
    environment = isolated_environment(runtime / "homes" / str(case["id"]) / f"trial-{trial}", workspace)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            codex_command(case, workspace, model), capture_output=True, text=True,
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
        "case_id": case["id"], "trial": trial, "run_at": utc_now(),
        "duration_seconds": round(time.monotonic() - started, 3),
        "execution": {"status": execution, "exit_code": exit_code, "stderr": stderr},
        "response": response, "tool_calls": tool_calls, "usage": usage, "oracle": oracle,
        "git_status": command_output(["git", "-C", str(workspace), "status", "--short"])
        if (workspace / ".git").exists() else None,
        "semantic_review": {"status": "unreviewed", "must": case["must"], "must_not": case["must_not"]},
        "hard_failure": execution != "pass" or oracle["status"] == "fail",
    }
    return result, stdout, workspace


def materialize(run_dir: Path, result: dict[str, object], events: str, workspace: Path) -> None:
    case_dir = run_dir / "cases" / str(result["case_id"])
    case_dir.mkdir(parents=True, exist_ok=True)
    trial = int(result["trial"])
    (case_dir / f"trial-{trial}.events.jsonl").write_text(events, encoding="utf-8")
    (case_dir / f"trial-{trial}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    destination = run_dir / "workspaces" / str(result["case_id"]) / f"trial-{trial}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(workspace), destination)


def dry_run(selected: list[dict[str, object]], repeat: int | None) -> int:
    for case in selected:
        print(
            f"{case['id']}\ttrials={repeat or case['trials']}\ttype={case['task_type']}\t"
            f"suites={','.join(case['suites'])}\tinvocation={case['invocation']}"
        )
    return 0


def execute(
    selected: list[dict[str, object]], repeat: int | None, model: str | None, timeout: int, run_id: str | None
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
    started_at = utc_now()
    started = time.monotonic()
    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix=f"groundcraft-{identifier}-", dir=RESULTS.parent) as temporary:
        runtime = Path(temporary)
        pending: list[tuple[dict[str, object], str, Path]] = []
        for case in selected:
            trials = repeat or int(case["trials"])
            for trial in range(1, trials + 1):
                print(f"running {case['id']} trial {trial}/{trials}", flush=True)
                item = run_trial(case, runtime, trial, resolved_model, timeout)
                pending.append(item)
                results.append(item[0])
        for result, events, workspace in pending:
            materialize(run_dir, result, events, workspace)
    manifest = {
        "run_id": identifier, "started_at": started_at, "model": resolved_model,
        "source_sha256": source_sha256(),
        "git_commit": command_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"]),
        "git_status": command_output(["git", "-C", str(ROOT), "status", "--short"]),
        "cases": selected,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    failures = sum(bool(result["hard_failure"]) for result in results)
    measured = [result["usage"] for result in results if result.get("usage")]
    usage = None if not measured else {
        key: sum(int(item[key]) for item in measured)
        for key in USAGE_FIELDS
    }
    summary = {
        "run_id": identifier, "finished_at": utc_now(),
        "duration_seconds": round(time.monotonic() - started, 3),
        "cases": len(selected), "trials": len(results), "hard_failures": failures,
        "semantic_unreviewed": len(results), "usage": usage,
        "release_status": "failed" if failures else "awaiting_semantic_review",
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(run_dir)
    print(json.dumps(summary, indent=2))
    return 1 if failures else 0


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
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.repeat is not None and args.repeat < 1:
        parser.error("--repeat must be positive")
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    if args.list:
        if args.case or args.suite or args.all:
            parser.error("--list cannot be combined with a selection")
        return dry_run(cases(), None)
    selected = select(args.case, args.suite, args.all)
    return dry_run(selected, args.repeat) if args.dry_run else execute(
        selected, args.repeat, args.model, args.timeout, args.run_id
    )


if __name__ == "__main__":
    raise SystemExit(main())
