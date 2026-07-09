from __future__ import annotations

import copy
import importlib.util
import json
import socket
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST_TMP = ROOT.parent / "work" / "groundcraft" / "tests"


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python3", *arguments], cwd=ROOT, capture_output=True, text=True, check=False)


class ValidationCliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        TEST_TMP.mkdir(parents=True, exist_ok=True)
        cls.validator = load_module("groundcraft_validate", "scripts/validate.py")
        cls.catalog = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))

    def validate_catalog(self, catalog: dict[str, object]) -> list[str]:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            temporary = Path(directory)
            (temporary / "evals").mkdir()
            (temporary / "evals" / "cases.json").write_text(json.dumps(catalog), encoding="utf-8")
            plugin = temporary / "plugins" / "groundcraft"
            (plugin / ".codex-plugin").mkdir(parents=True)
            (plugin / ".codex-plugin" / "plugin.json").write_text(
                json.dumps({"version": catalog["catalog_version"]}), encoding="utf-8"
            )
            original_root, original_plugin = self.validator.ROOT, self.validator.PLUGIN
            self.validator.ROOT, self.validator.PLUGIN = temporary, plugin
            try:
                errors: list[str] = []
                self.validator.validate_evals(errors)
                return errors
            finally:
                self.validator.ROOT, self.validator.PLUGIN = original_root, original_plugin

    def test_repository_contract_is_valid(self) -> None:
        completed = run("scripts/validate.py")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("validation passed", completed.stdout)

    def test_missing_required_case_field_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["cases"][0].pop("sandbox")
        self.assertTrue(any("invalid fields" in error for error in self.validate_catalog(mutated)))

    def test_catalog_bloat_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        while len(mutated["cases"]) <= 14:
            duplicate = copy.deepcopy(mutated["cases"][0])
            duplicate["id"] = f"extra-{len(mutated['cases'])}"
            mutated["cases"].append(duplicate)
        self.assertTrue(any("10-14 focused cases" in error for error in self.validate_catalog(mutated)))

    def test_effectful_hook_is_rejected(self) -> None:
        hooks = json.loads((ROOT / "plugins/groundcraft/hooks/hooks.json").read_text(encoding="utf-8"))
        hooks["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"] = "touch /tmp/owned"
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            plugin = Path(directory)
            (plugin / "hooks").mkdir()
            (plugin / "hooks" / "hooks.json").write_text(json.dumps(hooks), encoding="utf-8")
            original = self.validator.PLUGIN
            self.validator.PLUGIN = plugin
            try:
                errors: list[str] = []
                self.validator.validate_hooks(errors)
            finally:
                self.validator.PLUGIN = original
        self.assertTrue(any("inert print" in error for error in errors), errors)


class EvalCliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
        cls.runner = load_module("groundcraft_run_evals", "scripts/run-evals.py")

    def test_list_contains_every_case(self) -> None:
        completed = run("scripts/run-evals.py", "--list")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(len(completed.stdout.splitlines()), len(self.catalog["cases"]))

    def test_suite_dry_run_filters_and_overrides_trials(self) -> None:
        completed = run("scripts/run-evals.py", "--suite", "activation", "--repeat", "2", "--dry-run")
        expected = [case for case in self.catalog["cases"] if "activation" in case["suites"]]
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(len(completed.stdout.splitlines()), len(expected))
        self.assertTrue(all("trials=2" in line for line in completed.stdout.splitlines()))

    def test_event_parser_keeps_response_and_tool_count(self) -> None:
        events = "\n".join((
            json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "ok"}}),
            json.dumps({"type": "item.completed", "item": {"type": "command_execution"}}),
        ))
        self.assertEqual(self.runner.parse_events(events), ("ok", 1))

    def test_writable_fixture_is_copied_and_initialized(self) -> None:
        case = next(case for case in self.catalog["cases"] if case["id"] == "tiny-label-change")
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            workspace = self.runner.prepare_workspace(case, Path(directory), 1)
            self.assertTrue((workspace / ".git").is_dir())
            self.assertTrue((workspace / "ui.py").is_file())
            status = subprocess.run(
                ["git", "status", "--short"], cwd=workspace, capture_output=True, text=True, check=True
            )
            self.assertEqual(status.stdout, "")

    @unittest.skipUnless(hasattr(socket, "AF_UNIX"), "requires Unix sockets")
    def test_materialize_moves_git_socket(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            root = Path(directory)
            workspace = root / "workspace"
            (workspace / ".git").mkdir(parents=True)
            endpoint = workspace / ".git" / "fsmonitor.ipc"
            server = socket.socket(socket.AF_UNIX)
            server.bind(str(endpoint))
            try:
                result = {"case_id": "socket-case", "trial": 1}
                self.runner.materialize(root / "results", result, "", workspace)
            finally:
                server.close()
            self.assertTrue((root / "results" / "workspaces" / "socket-case" / "trial-1").is_dir())


if __name__ == "__main__":
    unittest.main()
