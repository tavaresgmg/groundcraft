#!/usr/bin/env python3
"""Run Groundcraft behavioral prompts in fresh, read-only Codex threads."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals" / "cases.json"
RESULTS = ROOT / ".eval-results"


def cases() -> list[dict[str, object]]:
    data = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    return data["cases"]


def select(case_id: str) -> dict[str, object]:
    for case in cases():
        if case["id"] == case_id:
            return case
    raise SystemExit(f"unknown case: {case_id}")


def run(case: dict[str, object]) -> int:
    relative_cwd = Path(str(case.get("cwd", ".")))
    source_cwd = (ROOT / relative_cwd).resolve()
    if not source_cwd.is_relative_to(ROOT) or not source_cwd.is_dir():
        raise SystemExit(f"invalid eval cwd: {relative_cwd}")
    sandbox = str(case.get("sandbox", "read-only"))
    if sandbox == "workspace-write":
        cwd = RESULTS / "workspaces" / str(case["id"])
        if cwd.exists():
            shutil.rmtree(cwd)
        cwd.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_cwd, cwd)
        subprocess.run(["git", "init", "-b", "main"], cwd=cwd, capture_output=True, check=True)
        subprocess.run(["git", "add", "-A"], cwd=cwd, capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "-m", "test: initialize Groundcraft eval fixture"],
            cwd=cwd,
            capture_output=True,
            check=True,
        )
        prompt = (
            "Use $groundcraft to perform this task in the disposable evaluation repository. "
            "Do not push or create external state:\n\n" + str(case["prompt"])
        )
    else:
        cwd = source_cwd
        prompt = (
            "Use $groundcraft for this behavioral evaluation in read-only mode. "
            "Do not modify files or external state. Respond exactly as you would reason and communicate "
            "for this user request:\n\n" + str(case["prompt"])
        )
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--sandbox",
        sandbox,
        "--skip-git-repo-check",
        "--json",
        "--color",
        "never",
        "-c",
        'developer_instructions=""',
        "-C",
        str(cwd),
        prompt,
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    messages: list[str] = []
    for line in completed.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        if event.get("type") == "item.completed" and item.get("type") == "agent_message":
            messages.append(item.get("text", ""))

    RESULTS.mkdir(exist_ok=True)
    validation: dict[str, object] | None = None
    validation_command = case.get("validation")
    if isinstance(validation_command, list):
        checked = subprocess.run(
            [str(part) for part in validation_command],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        validation = {
            "command": validation_command,
            "exit_code": checked.returncode,
            "stdout": checked.stdout,
            "stderr": checked.stderr,
        }
    git_state = subprocess.run(
        ["git", "status", "--short"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    result = {
        "case": case,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "exit_code": completed.returncode,
        "response": "\n".join(messages),
        "stderr": completed.stderr,
        "source_cwd": str(relative_cwd),
        "workspace": str(cwd.relative_to(ROOT)) if cwd.is_relative_to(ROOT) else str(cwd),
        "sandbox": sandbox,
        "validation": validation,
        "git_status": git_state.stdout,
        "grading": "manual",
    }
    output = RESULTS / f"{case['id']}.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(output)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help="Run one case by id")
    parser.add_argument("--list", action="store_true", help="List case ids")
    args = parser.parse_args()
    if args.list:
        for case in cases():
            print(case["id"])
        return 0
    if not args.case:
        parser.error("use --list or --case ID")
    return run(select(args.case))


if __name__ == "__main__":
    raise SystemExit(main())
