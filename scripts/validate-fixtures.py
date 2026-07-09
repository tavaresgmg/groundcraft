#!/usr/bin/env python3
"""Prove that command eval fixtures fail at baseline and pass the reference patch."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "evals" / "cases.json"


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, check=False, timeout=120, env=environment
    )


def main() -> int:
    cases = json.loads(CATALOG.read_text(encoding="utf-8"))["cases"]
    command_cases = [case for case in cases if case["oracle"]["kind"] == "command"]
    temporary_base = Path(
        os.environ.get("GROUNDCRAFT_TEST_TMP", ROOT.parent / "work" / "groundcraft" / "fixture-validation")
    ).expanduser().resolve()
    temporary_base.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    for case in command_cases:
        with tempfile.TemporaryDirectory(dir=temporary_base) as directory:
            workspace = Path(directory) / "fixture"
            shutil.copytree(ROOT / case["cwd"], workspace)
            command = [
                str(part).replace("{root}", str(ROOT)).replace("{workspace}", str(workspace))
                for part in case["oracle"]["command"]
            ]
            baseline = run(command, workspace)
            if baseline.returncode == 0:
                errors.append(f"{case['id']}: baseline oracle must fail")
                continue
            patch = ROOT / case["oracle"]["reference_patch"]
            applied = run(["git", "apply", "--check", str(patch)], workspace)
            if applied.returncode != 0:
                errors.append(f"{case['id']}: reference patch check failed: {applied.stderr.strip()}")
                continue
            applied = run(["git", "apply", str(patch)], workspace)
            if applied.returncode != 0:
                errors.append(f"{case['id']}: reference patch failed: {applied.stderr.strip()}")
                continue
            reference = run(command, workspace)
            if reference.returncode != 0:
                errors.append(f"{case['id']}: reference oracle failed: {reference.stderr.strip()}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Fixture validation passed: {len(command_cases)} fail-to-pass cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
