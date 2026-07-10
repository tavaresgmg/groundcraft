#!/usr/bin/env python3
"""Validate the small public and evaluation contracts of Groundcraft."""

from __future__ import annotations

import json
import re
import stat
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "groundcraft"
SKILL = PLUGIN / "skills" / "groundcraft"
HANDOFF = PLUGIN / "skills" / "groundcraft-handoff"
SEMVER = re.compile(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?")


def load_json(path: Path, errors: list[str]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: {exc}")
        return None


def require_files(errors: list[str]) -> None:
    paths = [
        ROOT / ".agents" / "plugins" / "marketplace.json",
        ROOT / ".gitattributes",
        ROOT / "CHANGELOG.md",
        ROOT / "README.md",
        ROOT / "docs" / "methodology.md",
        ROOT / "docs" / "sources.md",
        ROOT / "evals" / "cases.json",
        ROOT / "evals" / "README.md",
        ROOT / "scripts" / "run-evals.py",
        ROOT / "scripts" / "install-local.py",
        ROOT / "scripts" / "validate-fixtures.py",
        ROOT / "tests" / "test_cli.py",
        PLUGIN / ".codex-plugin" / "plugin.json",
        PLUGIN / "hooks" / "hooks.json",
        SKILL / "SKILL.md",
        SKILL / "agents" / "openai.yaml",
        HANDOFF / "SKILL.md",
        HANDOFF / "agents" / "openai.yaml",
        HANDOFF / "scripts" / "handoffs",
    ]
    paths.extend((SKILL / "references" / name) for name in (
        "context.md", "debugging.md", "decisions.md", "delivery.md", "engineering.md",
        "failure-modes.md", "proof.md", "quality.md", "research.md", "workspace.md",
    ))
    for path in paths:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")


def validate_manifest(errors: list[str]) -> None:
    manifest = load_json(PLUGIN / ".codex-plugin" / "plugin.json", errors)
    if not isinstance(manifest, dict):
        return
    if manifest.get("name") != "groundcraft":
        errors.append("plugin name must be groundcraft")
    version = str(manifest.get("version", ""))
    if not SEMVER.fullmatch(version):
        errors.append("plugin version must be semver")
    if manifest.get("skills") != "./skills/":
        errors.append("plugin skills path must be ./skills/")
    if manifest.get("hooks") != "./hooks/hooks.json":
        errors.append("plugin hooks path must be ./hooks/hooks.json")
    try:
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"CHANGELOG.md: {exc}")
    else:
        if f"## {version} -" not in changelog:
            errors.append("plugin version must have a changelog entry")

    marketplace = load_json(ROOT / ".agents" / "plugins" / "marketplace.json", errors)
    entries = marketplace.get("plugins") if isinstance(marketplace, dict) else None
    matches = [entry for entry in entries or [] if isinstance(entry, dict) and entry.get("name") == "groundcraft"]
    source = matches[0].get("source") if len(matches) == 1 else None
    if not isinstance(source, dict) or source.get("path") != "./plugins/groundcraft":
        errors.append("marketplace must contain one local groundcraft entry")


def validate_skill(errors: list[str]) -> None:
    try:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"SKILL.md: {exc}")
        return
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not frontmatter or set(re.findall(r"(?m)^([a-z_]+):", frontmatter.group(1))) != {"name", "description"}:
        errors.append("SKILL.md frontmatter must contain only name and description")
    if frontmatter and "name: groundcraft" not in frontmatter.group(1):
        errors.append("SKILL.md name must be groundcraft")
    if len(text.splitlines()) > 140:
        errors.append("SKILL.md exceeds the 140-line kernel budget")
    for path in (SKILL / "references").glob("*.md"):
        if len(path.read_text(encoding="utf-8").splitlines()) > 80:
            errors.append(f"{path.name} exceeds the 80-line reference budget")

    try:
        agent = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"openai.yaml: {exc}")
        return
    for pattern in (
        r"(?m)^interface:\s*$", r"(?m)^\s+display_name:\s*['\"]Groundcraft['\"]\s*$",
        r"(?m)^\s+default_prompt:\s*['\"].*\$groundcraft.*['\"]\s*$",
        r"(?m)^\s+allow_implicit_invocation:\s*true\s*$",
    ):
        if not re.search(pattern, agent):
            errors.append(f"openai.yaml missing contract: {pattern}")


def validate_handoff_skill(errors: list[str]) -> None:
    try:
        text = (HANDOFF / "SKILL.md").read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"groundcraft-handoff/SKILL.md: {exc}")
        return
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not frontmatter or set(re.findall(r"(?m)^([a-z_]+):", frontmatter.group(1))) != {"name", "description"}:
        errors.append("groundcraft-handoff frontmatter must contain only name and description")
    if frontmatter and "name: groundcraft-handoff" not in frontmatter.group(1):
        errors.append("groundcraft-handoff skill name must match its directory")
    if len(text.splitlines()) > 100:
        errors.append("groundcraft-handoff/SKILL.md exceeds the 100-line budget")
    if "${CODEX_HOME:-$HOME/.codex}/groundcraft/handoffs" not in text or "Never store runtime handoffs in a repository" not in text:
        errors.append("groundcraft-handoff must keep durable state outside repositories and plugin caches")
    if "scripts/handoffs --migrate-legacy" not in text or "Never merge two populated stores automatically" not in text:
        errors.append("groundcraft-handoff must require safe one-time legacy migration")

    try:
        agent = (HANDOFF / "agents" / "openai.yaml").read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"groundcraft-handoff/openai.yaml: {exc}")
    else:
        for pattern in (
            r"(?m)^interface:\s*$",
            r"(?m)^\s+display_name:\s*['\"]Groundcraft Handoff['\"]\s*$",
            r"(?m)^\s+default_prompt:\s*['\"].*\$groundcraft-handoff.*['\"]\s*$",
            r"(?m)^\s+allow_implicit_invocation:\s*true\s*$",
        ):
            if not re.search(pattern, agent):
                errors.append(f"groundcraft-handoff/openai.yaml missing contract: {pattern}")

    script = HANDOFF / "scripts" / "handoffs"
    try:
        mode = script.stat().st_mode
        script_text = script.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"groundcraft-handoff/scripts/handoffs: {exc}")
    else:
        if not mode & stat.S_IXUSR:
            errors.append("groundcraft-handoff/scripts/handoffs must be executable")
        if 'CODEX_ROOT="${CODEX_HOME:-$HOME/.codex}"' not in script_text or 'DIR="$CODEX_ROOT/groundcraft/handoffs"' not in script_text:
            errors.append("handoffs script must use the portable Codex state root")
        if 'LEGACY_DIR="$HOME/Developer/work/handoffs"' not in script_text or "--migrate-legacy" not in script_text:
            errors.append("handoffs script must support legacy migration")
        if 'if [ -L "$DIR" ]' not in script_text:
            errors.append("handoffs script must enforce the durable root and reject a symlink boundary")
        if 'mkdir "$LOCK_DIR"' not in script_text or "set -C" not in script_text or '"$store"/..?*' not in script_text:
            errors.append("handoffs migration must serialize, avoid clobbering, and validate double-dot entries")


def validate_hooks(errors: list[str]) -> None:
    data = load_json(PLUGIN / "hooks" / "hooks.json", errors)
    hooks = data.get("hooks") if isinstance(data, dict) else None
    if not isinstance(hooks, dict) or set(hooks) != {"UserPromptSubmit", "SubagentStart"}:
        errors.append("hooks.json must contain only UserPromptSubmit and SubagentStart")
        return
    messages: dict[str, str] = {}
    for event, groups in hooks.items():
        if not isinstance(groups, list) or len(groups) != 1:
            errors.append(f"{event} must contain one matcher group")
            continue
        handlers = groups[0].get("hooks") if isinstance(groups[0], dict) else None
        if not isinstance(handlers, list) or len(handlers) != 1:
            errors.append(f"{event} must contain one handler")
            continue
        handler = handlers[0]
        if not isinstance(handler, dict) or set(handler) != {"type", "command", "commandWindows", "timeout"}:
            errors.append(f"{event} has an invalid handler shape")
            continue
        unix = re.fullmatch(r"printf '%s\\n' '([^'\r\n]+)'", str(handler.get("command", "")))
        windows = re.fullmatch(
            r'powershell\.exe -NoProfile -Command "Write-Output \'([^\'\r\n]+)\'"',
            str(handler.get("commandWindows", "")),
        )
        if handler.get("type") != "command" or not unix or not windows:
            errors.append(f"{event} must use inert print commands")
            continue
        if unix.group(1) != windows.group(1) or "$groundcraft" not in unix.group(1):
            errors.append(f"{event} hook messages must match and mention $groundcraft")
        if not isinstance(handler.get("timeout"), int) or not 1 <= handler["timeout"] <= 10:
            errors.append(f"{event} timeout must be 1-10 seconds")
        messages[event] = unix.group(1)
    prompt = messages.get("UserPromptSubmit", "")
    if not all(word in prompt for word in ("substantial", "tiny", "casual", "translation")):
        errors.append("UserPromptSubmit must define the activation boundary")
    if (
        "$groundcraft-handoff" not in prompt
        or "unfinished cross-session work" not in prompt
        or "never per task" not in prompt
        or "describing a sequence of steps" not in prompt
    ):
        errors.append("UserPromptSubmit must keep handoff continuity demand-driven")


def validate_evals(errors: list[str]) -> None:
    data = load_json(ROOT / "evals" / "cases.json", errors)
    manifest = load_json(PLUGIN / ".codex-plugin" / "plugin.json", errors)
    if not isinstance(data, dict) or data.get("schema_version") != 2:
        errors.append("eval schema_version must be 2")
        return
    if not isinstance(manifest, dict) or data.get("catalog_version") != manifest.get("version"):
        errors.append("eval catalog version must match the plugin version")
    cases = data.get("cases")
    if not isinstance(cases, list) or not 10 <= len(cases) <= 14:
        errors.append("eval catalog must contain 10-14 focused cases")
        return

    task_types = {"answer", "research", "decision", "diagnosis", "change", "review", "operation"}
    suite_types = {"activation", "capability", "regression", "safety"}
    allowed = {
        "id", "task_type", "suites", "prompt", "cwd", "sandbox", "authority", "invocation",
        "expected_mode", "trials", "oracle", "size", "risk", "must", "must_not",
    }
    required = allowed - {"cwd"}
    ids: set[str] = set()
    prompts: set[str] = set()
    covered_tasks: set[str] = set()
    covered_suites: set[str] = set()
    command_oracles = 0
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"eval case {index} must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", case_id):
            errors.append(f"eval case {index} has invalid id")
            continue
        if case_id in ids:
            errors.append(f"duplicate eval id {case_id}")
        ids.add(case_id)
        if set(case) - allowed or required - set(case):
            errors.append(f"{case_id}: invalid fields")
        if case.get("task_type") not in task_types:
            errors.append(f"{case_id}: invalid task_type")
        else:
            covered_tasks.add(case["task_type"])
        suites = case.get("suites")
        if not isinstance(suites, list) or not suites or not set(suites) <= suite_types:
            errors.append(f"{case_id}: invalid suites")
        else:
            covered_suites.update(suites)
        if case.get("invocation") == "implicit" and "activation" not in (suites or []):
            errors.append(f"{case_id}: implicit cases must be in activation")
        if case.get("sandbox") not in {"read-only", "workspace-write"}:
            errors.append(f"{case_id}: invalid sandbox")
        if case.get("authority") not in {"inspect-only", "local-write", "external-gated"}:
            errors.append(f"{case_id}: invalid authority")
        if case.get("expected_mode") not in {"full", "direct"}:
            errors.append(f"{case_id}: invalid expected_mode")
        if case.get("size") not in {"tiny", "standard", "large"} or case.get("risk") not in {"routine", "guarded", "critical"}:
            errors.append(f"{case_id}: invalid size or risk")
        if case.get("risk") == "critical" and case.get("authority") != "external-gated":
            errors.append(f"{case_id}: critical cases require external-gated authority")
        if case.get("sandbox") == "workspace-write" and ("cwd" not in case or case.get("authority") != "local-write"):
            errors.append(f"{case_id}: writable cases require a fixture and local-write authority")
        if not isinstance(case.get("trials"), int) or not 1 <= case["trials"] <= 3:
            errors.append(f"{case_id}: trials must be 1-3")
        for field in ("prompt", "must", "must_not"):
            value = case.get(field)
            if field == "prompt" and (not isinstance(value, str) or not value.strip()):
                errors.append(f"{case_id}: invalid prompt")
            if field != "prompt" and (not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value)):
                errors.append(f"{case_id}: invalid {field}")
        prompt = case.get("prompt")
        if isinstance(prompt, str) and prompt in prompts:
            errors.append(f"{case_id}: duplicate prompt")
        elif isinstance(prompt, str):
            prompts.add(prompt)
        if "cwd" in case:
            cwd = (ROOT / str(case["cwd"])).resolve()
            if not cwd.is_relative_to(ROOT) or not cwd.is_dir():
                errors.append(f"{case_id}: cwd must be an existing repository directory")
        oracle = case.get("oracle")
        if not isinstance(oracle, dict) or oracle.get("kind") not in {"manual", "command"}:
            errors.append(f"{case_id}: invalid oracle")
        elif oracle["kind"] == "manual" and set(oracle) != {"kind"}:
            errors.append(f"{case_id}: manual oracle has extra fields")
        elif oracle["kind"] == "command":
            command_oracles += 1
            if set(oracle) != {"kind", "command", "reference_patch"}:
                errors.append(f"{case_id}: invalid command oracle fields")
            command = oracle.get("command")
            if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
                errors.append(f"{case_id}: invalid command oracle")
            patch = (ROOT / str(oracle.get("reference_patch", ""))).resolve()
            if not patch.is_relative_to(ROOT) or not patch.is_file():
                errors.append(f"{case_id}: missing reference patch")

    if covered_tasks != task_types:
        errors.append(f"missing task types: {', '.join(sorted(task_types - covered_tasks))}")
    if covered_suites != suite_types:
        errors.append(f"missing suites: {', '.join(sorted(suite_types - covered_suites))}")
    if command_oracles < 2:
        errors.append("eval catalog requires two deterministic command oracles")


def main() -> int:
    errors: list[str] = []
    require_files(errors)
    validate_manifest(errors)
    validate_skill(errors)
    validate_handoff_skill(errors)
    validate_hooks(errors)
    validate_evals(errors)
    for path in ROOT.rglob("*"):
        if not path.is_file() or {".git", "__pycache__"} & set(path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "[TO" + "DO:" in text:
            errors.append(f"placeholder in {path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Groundcraft validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
