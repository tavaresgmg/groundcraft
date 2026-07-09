#!/usr/bin/env python3
"""Dependency-free structural validation for Groundcraft."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "groundcraft"
SKILL = PLUGIN / "skills" / "groundcraft"


def load_json(path: Path, errors: list[str]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: {exc}")
        return None


def require_files(errors: list[str]) -> None:
    paths = [
        ROOT / ".agents" / "plugins" / "marketplace.json",
        PLUGIN / ".codex-plugin" / "plugin.json",
        PLUGIN / "hooks" / "hooks.json",
        SKILL / "SKILL.md",
        SKILL / "agents" / "openai.yaml",
        ROOT / "docs" / "methodology.md",
        ROOT / "docs" / "sources.md",
        ROOT / "evals" / "cases.json",
        ROOT / "scripts" / "run-evals.py",
    ]
    paths.extend((SKILL / "references" / name) for name in (
        "research.md",
        "decisions.md",
        "context.md",
        "engineering.md",
        "proof.md",
        "delivery.md",
    ))
    for path in paths:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")


def validate_manifest(errors: list[str]) -> None:
    data = load_json(PLUGIN / ".codex-plugin" / "plugin.json", errors)
    if not isinstance(data, dict):
        return
    if data.get("name") != "groundcraft":
        errors.append("plugin name must be groundcraft")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", str(data.get("version", ""))):
        errors.append("plugin version must be semver")
    if data.get("skills") != "./skills/":
        errors.append("plugin skills path must be ./skills/")
    if "hooks" in data:
        errors.append("omit manifest hooks field; Codex discovers hooks/hooks.json by default")


def validate_marketplace(errors: list[str]) -> None:
    data = load_json(ROOT / ".agents" / "plugins" / "marketplace.json", errors)
    if not isinstance(data, dict) or data.get("name") != "groundcraft":
        errors.append("marketplace name must be groundcraft")
        return
    entries = data.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1:
        errors.append("marketplace must contain exactly one plugin")
        return
    entry = entries[0]
    if not isinstance(entry, dict) or entry.get("name") != "groundcraft":
        errors.append("marketplace plugin must be groundcraft")
    source = entry.get("source") if isinstance(entry, dict) else None
    if not isinstance(source, dict) or source.get("path") != "./plugins/groundcraft":
        errors.append("marketplace source path must be ./plugins/groundcraft")


def validate_skill(errors: list[str]) -> None:
    path = SKILL / "SKILL.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(str(exc))
        return
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        errors.append("SKILL.md must start with YAML frontmatter")
        return
    keys = [line.split(":", 1)[0].strip() for line in match.group(1).splitlines() if ":" in line]
    if keys != ["name", "description"]:
        errors.append("SKILL.md frontmatter must contain only name and description")
    if "name: groundcraft" not in match.group(1):
        errors.append("SKILL.md name must be groundcraft")
    if len(text.splitlines()) > 220:
        errors.append("SKILL.md exceeds 220 lines")

    agent = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    expected_agent = """interface:
  display_name: \"Groundcraft\"
  short_description: \"Evidence-driven autonomous software engineering\"
  default_prompt: \"Use $groundcraft to take this software task from intent to verified delivery.\"
policy:
  allow_implicit_invocation: true
"""
    if agent != expected_agent:
        errors.append("openai.yaml differs from the validated interface contract")

    for path in sorted((SKILL / "references").glob("*.md")):
        if len(path.read_text(encoding="utf-8").splitlines()) > 180:
            errors.append(f"{path.name} exceeds 180 lines")


def validate_hooks(errors: list[str]) -> None:
    data = load_json(PLUGIN / "hooks" / "hooks.json", errors)
    hooks = data.get("hooks") if isinstance(data, dict) else None
    if not isinstance(hooks, dict):
        errors.append("hooks.json must contain hooks object")
        return
    expected_handlers = {
        "UserPromptSubmit": {
            "type": "command",
            "command": "printf '%s\\n' 'For software engineering work, apply the $groundcraft skill automatically. Do not ask the user to choose a workflow.'",
            "commandWindows": "powershell.exe -NoProfile -Command \"Write-Output 'For software engineering work, apply the $groundcraft skill automatically. Do not ask the user to choose a workflow.'\"",
            "timeout": 5,
        },
        "SubagentStart": {
            "type": "command",
            "command": "printf '%s\\n' 'Apply $groundcraft to software engineering work. Stay within the delegated scope and return evidence, not confidence.'",
            "commandWindows": "powershell.exe -NoProfile -Command \"Write-Output 'Apply $groundcraft to software engineering work. Stay within the delegated scope and return evidence, not confidence.'\"",
            "timeout": 5,
        },
    }
    for event, expected_handler in expected_handlers.items():
        groups = hooks.get(event)
        if not isinstance(groups, list) or len(groups) != 1:
            errors.append(f"hooks.json {event} must contain one matcher group")
            continue
        handlers = groups[0].get("hooks") if isinstance(groups[0], dict) else None
        if not isinstance(handlers, list) or len(handlers) != 1:
            errors.append(f"hooks.json {event} must contain one handler")
            continue
        handler = handlers[0]
        if handler != expected_handler:
            errors.append(f"hooks.json {event} handler differs from the validated contract")


def validate_evals(errors: list[str]) -> None:
    data = load_json(ROOT / "evals" / "cases.json", errors)
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        errors.append("eval schema_version must be 1")
        return
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 10:
        errors.append("evals must define at least 10 cases")
        return
    ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"eval case {index} must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"eval case {index} has invalid id")
        elif case_id in ids:
            errors.append(f"duplicate eval id {case_id}")
        else:
            ids.add(case_id)
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            errors.append(f"{case_id}: invalid prompt")
        if case.get("size") not in {"tiny", "standard", "large"}:
            errors.append(f"{case_id}: invalid size")
        if case.get("risk") not in {"routine", "guarded", "critical"}:
            errors.append(f"{case_id}: invalid risk")
        for field in ("must", "must_not"):
            value = case.get(field)
            if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
                errors.append(f"{case_id}: {field} must be a non-empty string list")
        if "cwd" in case:
            relative_cwd = Path(str(case["cwd"]))
            resolved_cwd = (ROOT / relative_cwd).resolve()
            if relative_cwd.is_absolute() or not resolved_cwd.is_relative_to(ROOT) or not resolved_cwd.is_dir():
                errors.append(f"{case_id}: cwd must be an existing directory inside the repository")
        sandbox = case.get("sandbox", "read-only")
        if sandbox not in {"read-only", "workspace-write"}:
            errors.append(f"{case_id}: invalid sandbox")
        validation = case.get("validation")
        if validation is not None and (
            not isinstance(validation, list)
            or not validation
            or not all(isinstance(part, str) and part for part in validation)
        ):
            errors.append(f"{case_id}: validation must be a non-empty string list")


def main() -> int:
    errors: list[str] = []
    require_files(errors)
    validate_manifest(errors)
    validate_marketplace(errors)
    validate_skill(errors)
    validate_hooks(errors)
    validate_evals(errors)

    for path in ROOT.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if re.search(r"\[(?:TODO|TBD|FIXME)(?::[^\]]*)?\]", text, re.IGNORECASE):
                errors.append(f"placeholder found in {path.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Groundcraft validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
