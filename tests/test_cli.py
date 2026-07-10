from __future__ import annotations

import copy
import importlib.util
import json
import os
import socket
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST_TMP = Path(tempfile.gettempdir()) / "groundcraft-tests"
HANDOFF_SCRIPT = ROOT / "plugins" / "groundcraft" / "skills" / "groundcraft-handoff" / "scripts" / "handoffs"


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
        TEST_TMP.mkdir(parents=True, exist_ok=True)
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

    def test_eval_home_installs_every_plugin_skill(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            home = Path(directory) / "home"
            self.runner.install_skills(home)
            installed = home / ".agents" / "skills"
            self.assertTrue((installed / "groundcraft" / "SKILL.md").is_file())
            self.assertTrue((installed / "groundcraft-handoff" / "SKILL.md").is_file())

    @unittest.skipUnless(hasattr(socket, "AF_UNIX"), "requires Unix sockets")
    def test_materialize_moves_git_socket(self) -> None:
        socket_tmp = Path("/tmp") if Path("/tmp").is_dir() else TEST_TMP
        with tempfile.TemporaryDirectory(dir=socket_tmp) as directory:
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


class HandoffCliTest(unittest.TestCase):
    def handoff_store(self, home: Path) -> Path:
        return home / "Developer" / "work" / "handoffs"

    def run_handoffs(self, home: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["HOME"] = str(home)
        return subprocess.run(
            [str(HANDOFF_SCRIPT), *arguments], capture_output=True, text=True, check=False, env=environment
        )

    def write_handoff(self, directory: Path, name: str = "groundcraft-continuity") -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{name}.md"
        path.write_text(
            """# Integrate durable continuity

- workspace: /tmp/groundcraft
- branch: feature/continuity
- criado: 2026-07-09 | atualizado: 2026-07-09
- status: em-andamento

## Pronto quando
The plugin resumes verified work.

## Estado
- [ ] Validate the plugin.

## Próximo passo
Run python3 scripts/validate.py.

## Bloqueios e risco
nenhum

## Contexto
The handoff is a test fixture.
""",
            encoding="utf-8",
        )
        return path

    def test_missing_directory_is_an_empty_valid_store(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            completed = self.run_handoffs(Path(directory) / "home")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), "0 handoffs pending")

    def test_valid_handoff_lists_title_next_step_and_workspace_filter(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            home = Path(directory) / "home"
            store = self.handoff_store(home)
            path = self.write_handoff(store)
            self.write_handoff(store, "other-separate-task")
            completed = self.run_handoffs(home, "groundcraft")
            path.write_text(path.read_text(encoding="utf-8").replace(
                "Run python3 scripts/validate.py.", "Run python3 -m unittest discover -s tests."
            ), encoding="utf-8")
            updated = self.run_handoffs(home, "groundcraft")
            path.unlink()
            closed = self.run_handoffs(home, "groundcraft")
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn("groundcraft-continuity - Integrate durable continuity", completed.stdout)
        self.assertIn("next: Run python3 scripts/validate.py.", completed.stdout)
        self.assertNotIn("other-separate-task", completed.stdout)
        self.assertIn("next: Run python3 -m unittest discover -s tests.", updated.stdout)
        self.assertNotIn("groundcraft-continuity", closed.stdout)

    def test_legacy_handoff_remains_readable_during_migration(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            home = Path(directory) / "home"
            store = self.handoff_store(home)
            store.mkdir(parents=True)
            (store / "groundcraft-legacy-task.md").write_text(
                """# Resume a legacy task

- atualizado: 2026-07-09

## Pronto quando
The task is verified.

## Próximo passo
Inspect the current state.
""",
                encoding="utf-8",
            )
            completed = self.run_handoffs(home)
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn("groundcraft-legacy-task - Resume a legacy task", completed.stdout)

    def test_invalid_file_fails_the_whole_store_even_when_filtered_out(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            home = Path(directory) / "home"
            store = self.handoff_store(home)
            self.write_handoff(store)
            (store / "unrelated.txt").write_text("bad", encoding="utf-8")
            completed = self.run_handoffs(home, "groundcraft")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("ALERTA: unrelated.txt", completed.stdout)

    def test_old_handoff_is_marked_stale(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            home = Path(directory) / "home"
            path = self.write_handoff(self.handoff_store(home))
            old = path.stat().st_mtime - 8 * 86400
            os.utime(path, (old, old))
            completed = self.run_handoffs(home)
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn("[STALE 8d", completed.stdout)

    def test_symlinked_store_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as directory:
            root = Path(directory)
            home = root / "home"
            store = self.handoff_store(home)
            store.parent.mkdir(parents=True)
            target = root / "repository-state"
            target.mkdir()
            store.symlink_to(target, target_is_directory=True)
            completed = self.run_handoffs(home)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("durable handoff directory must not be a symlink", completed.stdout)


if __name__ == "__main__":
    unittest.main()
