from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import localaibrain


def make_plan(root: Path) -> localaibrain.ProjectInstallPlan:
    project_root = root / "workspace" / "project"
    install_container = project_root / "localaibrain"
    source_package = root / "source" / "local_ai_brain"
    scripts_dir = install_container / "scripts"
    data_dir = install_container / "brain"
    source_package.mkdir(parents=True, exist_ok=True)
    (source_package / "__main__.py").write_text("print('source')\n", encoding="utf-8")
    return localaibrain.ProjectInstallPlan(
        platform_name="windows",
        python_executable=Path(sys.executable),
        source_package_dir=source_package,
        source_installer=root / "source" / "localaibrain.py",
        project_root=project_root,
        scripts_dir=scripts_dir,
        package_dir=scripts_dir / "local_ai_brain",
        data_dir=data_dir,
        db_path=data_dir / "brain.db",
        artifacts_dir=data_dir / "artifacts",
        plans_dir=install_container / "plans",
        agents_file=project_root / "agents.md",
        mcp_dir=install_container / "mcp",
        mcp_registry_path=install_container / "mcp" / "local-ai-brain-tools.json",
        mcp_adapter_path=scripts_dir / "project_mcp.py",
        brain_scope="project",
        mcp_tool_prefix="workspace.localaibrain",
        register_agents=True,
    )


class LocalAiBrainDeployTests(unittest.TestCase):
    def test_build_plan_routes_owned_paths_through_install_container(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_root = root / "workspace" / "project"
            source_root = root / "source"
            source_package = source_root / "local_ai_brain"
            source_package.mkdir(parents=True)
            (source_package / "__main__.py").write_text("print('source')\n", encoding="utf-8")
            args = mock.Mock(
                project_root=str(project_root),
                source_dir=str(source_root),
                brain_scope="project",
                no_register_agents=False,
                mcp_name="workspace.localaibrain",
                platform="windows",
            )

            plan = localaibrain.build_plan(args)

            install_container = project_root / "localaibrain"
            self.assertEqual(plan.project_root, project_root.resolve())
            self.assertEqual(plan.source_installer, (source_root / "localaibrain.py").resolve())
            self.assertEqual(plan.scripts_dir, (install_container / "scripts").resolve())
            self.assertEqual(plan.package_dir, (install_container / "scripts" / "local_ai_brain").resolve())
            self.assertEqual(plan.data_dir, (install_container / "brain").resolve())
            self.assertEqual(plan.plans_dir, (install_container / "plans").resolve())
            self.assertEqual(plan.mcp_dir, (install_container / "mcp").resolve())
            self.assertEqual(plan.mcp_adapter_path, (install_container / "scripts" / "project_mcp.py").resolve())
            self.assertEqual(
                plan.mcp_registry_path,
                (install_container / "mcp" / "local-ai-brain-tools.json").resolve(),
            )

            server = localaibrain.server_spec(plan)
            self.assertEqual(server["args"], [str(plan.mcp_adapter_path)])
            self.assertEqual(server["env"]["PYTHONPATH"], str(plan.scripts_dir))
            self.assertEqual(server["env"]["LOCAL_AI_BRAIN_HOME"], str(plan.data_dir))
            self.assertEqual(server["cwd"], str(plan.project_root))

            registry = localaibrain.mcp_registry(plan)
            self.assertEqual(registry["server"]["args"], [str(plan.mcp_adapter_path)])
            self.assertEqual(registry["server"]["env"]["PYTHONPATH"], str(plan.scripts_dir))
            self.assertEqual(registry["server"]["env"]["LOCAL_AI_BRAIN_HOME"], str(plan.data_dir))
            self.assertEqual(registry["plan_naming"]["directory"], str(plan.plans_dir))

            block = localaibrain.agents_block(plan)
            self.assertIn(str(plan.mcp_registry_path), block)
            self.assertIn(str(plan.mcp_adapter_path), block)
            self.assertIn(str(plan.scripts_dir), block)
            self.assertIn(str(plan.data_dir), block)
            self.assertIn(str(plan.plans_dir), block)

    def test_main_brain_default_install_uses_user_profile_brain_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_root = root / "source"
            source_package = source_root / "local_ai_brain"
            source_package.mkdir(parents=True)
            (source_package / "__main__.py").write_text("print('source')\n", encoding="utf-8")
            home = root / "home"
            args = mock.Mock(
                project_root=".",
                source_dir=str(source_root),
                brain_scope="main",
                no_register_agents=False,
                mcp_name="",
                platform="windows",
            )

            with mock.patch.object(localaibrain.Path, "home", return_value=home):
                plan = localaibrain.build_plan(args)

            expected_root = home / ".agents" / "local-ai-brain"
            self.assertEqual(plan.project_root, expected_root.resolve())
            self.assertEqual(plan.brain_scope, "main")
            self.assertEqual(plan.mcp_tool_prefix, "localaibrain")
            self.assertEqual(plan.data_dir, (expected_root / "localaibrain" / "brain").resolve())

    def test_main_brain_agents_block_lists_user_profile_brain_areas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            plan = make_plan(Path(tmp))
            plan = localaibrain.ProjectInstallPlan(
                **{
                    **plan.__dict__,
                    "project_root": home / ".agents" / "local-ai-brain",
                    "brain_scope": "main",
                    "mcp_tool_prefix": "localaibrain",
                }
            )

            with mock.patch.object(localaibrain.Path, "home", return_value=home):
                block = localaibrain.agents_block(plan)

            self.assertIn("Main brain areas", block)
            self.assertIn(str(home / ".agents"), block)
            self.assertIn(str(home / ".codex"), block)
            self.assertIn(str(home / ".claude"), block)

    def test_main_brain_plan_preview_prints_user_profile_brain_areas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            plan = make_plan(Path(tmp))
            plan = localaibrain.ProjectInstallPlan(
                **{
                    **plan.__dict__,
                    "project_root": home / ".agents" / "local-ai-brain",
                    "brain_scope": "main",
                    "mcp_tool_prefix": "localaibrain",
                }
            )

            with (
                mock.patch.object(localaibrain.Path, "home", return_value=home),
                mock.patch("builtins.print") as print_mock,
            ):
                localaibrain.print_plan(plan, what_if=True, force=False, doctor=False)

            printed = "\n".join(str(call.args[0]) for call in print_mock.call_args_list)
            self.assertIn(f"main_brain_area: {home / '.agents'}", printed)
            self.assertIn(f"main_brain_area: {home / '.codex'}", printed)
            self.assertIn(f"main_brain_area: {home / '.claude'}", printed)

    def test_mcp_adapter_source_uses_install_container_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = make_plan(Path(tmp))

            source = localaibrain.mcp_adapter_source(plan)

            self.assertIn('INSTALL_CONTAINER = Path(__file__).resolve().parents[1]', source)
            self.assertIn('PROJECT_ROOT = INSTALL_CONTAINER.parent', source)
            self.assertIn('SCRIPTS_DIR = INSTALL_CONTAINER / "scripts"', source)
            self.assertIn('os.environ["LOCAL_AI_BRAIN_HOME"] = str(INSTALL_CONTAINER / "brain")', source)
            self.assertIn('os.environ["LOCAL_AI_BRAIN_PROJECT_ROOT"] = str(PROJECT_ROOT)', source)
            self.assertIn('os.environ["PYTHONPATH"] = str(SCRIPTS_DIR)', source)
            self.assertIn(str(plan.mcp_tool_prefix), source)

    def test_project_mcp_uses_env_project_root_and_container_runtime_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "workspace" / "project"
            scripts_root = Path(localaibrain.__file__).resolve().parent / "scripts"
            sys.path.insert(0, str(scripts_root))
            try:
                with mock.patch.dict(os.environ, {"LOCAL_AI_BRAIN_PROJECT_ROOT": str(project_root)}, clear=True):
                    module = importlib.import_module("local_ai_brain.project_mcp")
                    module = importlib.reload(module)

                    self.assertEqual(module.PROJECT_ROOT, project_root.resolve())
                    self.assertEqual(module.SCRIPTS_DIR, module.INSTALL_CONTAINER / "scripts")
                    self.assertEqual(os.environ["LOCAL_AI_BRAIN_HOME"], str(module.INSTALL_CONTAINER / "brain"))
            finally:
                sys.path.remove(str(scripts_root))

    def test_migrate_old_scattered_install_moves_scattered_folders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = make_plan(Path(tmp))
            old_package = plan.project_root / "scripts" / "local_ai_brain"
            old_package.mkdir(parents=True)
            (old_package / "__main__.py").write_text("print('old package')\n", encoding="utf-8")
            old_adapter = plan.project_root / "scripts" / "project_mcp.py"
            old_adapter.write_text("# old adapter", encoding="utf-8")
            for name in ("brain", "mcp", "plans"):
                old_dir = plan.project_root / name
                old_dir.mkdir(parents=True)
                (old_dir / f"{name}.txt").write_text(name, encoding="utf-8")

            localaibrain.migrate_old_scattered_install(plan)

            self.assertFalse(old_package.exists())
            self.assertFalse(old_adapter.exists())
            self.assertTrue((plan.package_dir / "__main__.py").is_file())
            self.assertTrue(plan.mcp_adapter_path.is_file())
            self.assertTrue((plan.data_dir / "brain.txt").is_file())
            self.assertTrue((plan.mcp_dir / "mcp.txt").is_file())
            self.assertTrue((plan.plans_dir / "plans.txt").is_file())

    def test_migrate_old_scattered_install_warns_and_keeps_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = make_plan(Path(tmp))
            old_brain = plan.project_root / "brain"
            old_brain.mkdir(parents=True)
            (old_brain / "old.txt").write_text("old", encoding="utf-8")
            plan.data_dir.mkdir(parents=True)
            (plan.data_dir / "new.txt").write_text("new", encoding="utf-8")

            with mock.patch("builtins.print") as print_mock:
                localaibrain.migrate_old_scattered_install(plan)

            self.assertTrue((old_brain / "old.txt").is_file())
            self.assertTrue((plan.data_dir / "new.txt").is_file())
            printed = "\n".join(str(call.args[0]) for call in print_mock.call_args_list)
            self.assertIn("WARN", printed)
            self.assertIn(str(old_brain), printed)

    def test_run_rollback_preserves_unrelated_project_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = make_plan(Path(tmp))
            plan.project_root.mkdir(parents=True, exist_ok=True)
            plan.mcp_dir.mkdir(parents=True, exist_ok=True)
            plan.mcp_registry_path.write_text("{}", encoding="utf-8")
            plan.mcp_adapter_path.parent.mkdir(parents=True, exist_ok=True)
            plan.mcp_adapter_path.write_text("# adapter", encoding="utf-8")
            keep_file = plan.project_root / "notes.txt"
            keep_file.write_text("keep", encoding="utf-8")
            keep_container_file = plan.project_root / "keep" / "notes.txt"
            keep_container_file.parent.mkdir(parents=True, exist_ok=True)
            keep_container_file.write_text("keep", encoding="utf-8")

            with (
                mock.patch.object(localaibrain, "rollback_agent_configs"),
                mock.patch.object(localaibrain, "rollback_builtin_skills"),
                mock.patch.object(localaibrain, "remove_deploy_record"),
            ):
                result = localaibrain.run_rollback(plan, what_if=False, yes=True)

            self.assertEqual(result, 0)
            self.assertFalse(plan.mcp_registry_path.exists())
            self.assertFalse(plan.mcp_adapter_path.exists())
            self.assertTrue(keep_file.is_file())
            self.assertTrue(keep_container_file.is_file())

    def test_record_deploy_stores_container_and_registry_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = make_plan(Path(tmp))
            with mock.patch.object(localaibrain, "DEPLOY_REGISTRY_PATH", plan.project_root / "deploys.json"):
                localaibrain.record_deploy(plan)
            registry = json.loads((plan.project_root / "deploys.json").read_text(encoding="utf-8"))
            entry = registry["deploys"][0]
            self.assertEqual(entry["container"], str(plan.project_root / "localaibrain"))
            self.assertEqual(entry["adapter"], str(plan.mcp_adapter_path))
            self.assertEqual(entry["registry"], str(plan.mcp_registry_path))

    def test_record_deploy_stores_main_brain_profile_areas_for_main_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            plan = make_plan(Path(tmp))
            plan = localaibrain.ProjectInstallPlan(
                **{
                    **plan.__dict__,
                    "project_root": home / ".agents" / "local-ai-brain",
                    "brain_scope": "main",
                    "mcp_tool_prefix": "localaibrain",
                }
            )

            with (
                mock.patch.object(localaibrain.Path, "home", return_value=home),
                mock.patch.object(localaibrain, "DEPLOY_REGISTRY_PATH", Path(tmp) / "deploys.json"),
            ):
                localaibrain.record_deploy(plan)

            registry = json.loads((Path(tmp) / "deploys.json").read_text(encoding="utf-8"))
            entry = registry["deploys"][0]
            self.assertEqual(
                entry["main_brain_areas"],
                [str(home / ".agents"), str(home / ".codex"), str(home / ".claude")],
            )

    def test_resolve_brain_json_reports_main_brain_profile_areas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            registry = Path(tmp) / "deploys.json"
            registry.write_text(
                json.dumps(
                    {
                        "deploys": [
                            {
                                "scope": "main",
                                "root": str(home / ".agents" / "local-ai-brain"),
                                "mcp_name": "localaibrain",
                                "last_used": "2026-06-13T00:00:00+00:00",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            args = mock.Mock(project_root="", brain_scope="main", mcp_name="", json=True)

            with (
                mock.patch.object(localaibrain.Path, "home", return_value=home),
                mock.patch.object(localaibrain, "DEPLOY_REGISTRY_PATH", registry),
                mock.patch("builtins.print") as print_mock,
            ):
                result = localaibrain.run_resolve_brain(args)

            self.assertEqual(result, 0)
            payload = json.loads(print_mock.call_args_list[0].args[0])
            self.assertEqual(
                payload["main_brain_areas"],
                [str(home / ".agents"), str(home / ".codex"), str(home / ".claude")],
            )

    def test_candidate_from_entry_and_guessed_candidate_resolve_container_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_root = root / "project"
            project_root.mkdir(parents=True)
            candidate_new_entry = {
                "scope": "project",
                "root": str(project_root),
                "mcp_name": "workspace.localaibrain",
                "container": str(project_root / "localaibrain"),
                "adapter": str(project_root / "localaibrain" / "scripts" / "project_mcp.py"),
                "registry": str(project_root / "localaibrain" / "mcp" / "local-ai-brain-tools.json"),
            }
            candidate = localaibrain.candidate_from_registry(candidate_new_entry)
            self.assertEqual(candidate.container_dir, (project_root / "localaibrain").resolve())
            self.assertEqual(candidate.package_dir, (project_root / "localaibrain" / "scripts" / "local_ai_brain").resolve())
            self.assertEqual(candidate.data_dir, (project_root / "localaibrain" / "brain").resolve())
            self.assertEqual(candidate.mcp_adapter_path, (project_root / "localaibrain" / "scripts" / "project_mcp.py").resolve())
            self.assertEqual(candidate.mcp_registry_path, (project_root / "localaibrain" / "mcp" / "local-ai-brain-tools.json").resolve())

            legacy_entry = {
                "scope": "project",
                "root": str(project_root),
                "mcp_name": "workspace.localaibrain",
                "adapter": str(project_root / "scripts" / "project_mcp.py"),
                "registry": str(project_root / "mcp" / "local-ai-brain-tools.json"),
            }
            candidate_legacy = localaibrain.candidate_from_registry(legacy_entry)
            self.assertEqual(candidate_legacy.scripts_dir, (project_root / "scripts").resolve())
            self.assertEqual(candidate_legacy.data_dir, (project_root / "brain").resolve())
            self.assertEqual(candidate_legacy.mcp_adapter_path, (project_root / "scripts" / "project_mcp.py").resolve())
            self.assertEqual(candidate_legacy.mcp_registry_path, (project_root / "mcp" / "local-ai-brain-tools.json").resolve())

            guessed = localaibrain.guessed_candidate(project_root, "project", "workspace.localaibrain")
            self.assertEqual(guessed.container_dir, (project_root / "localaibrain").resolve())

    def test_default_project_mcp_name_uses_parent_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "parent-folder" / "project-folder"
            root.mkdir(parents=True)
            with mock.patch.object(localaibrain, "DEPLOY_REGISTRY_PATH", Path(tmp) / "deploys.json"):
                name = localaibrain.default_mcp_name(root, "project")
            self.assertEqual(name, "parent-folder.localaibrain")

    def test_default_project_mcp_name_collision_uses_parent_and_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            registry = Path(tmp) / "deploys.json"
            registry.write_text(
                json.dumps(
                    {
                        "deploys": [
                            {
                                "scope": "project",
                                "root": str(Path(tmp) / "other-parent" / "other-project"),
                                "mcp_name": "parent-folder.localaibrain",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            root = Path(tmp) / "parent-folder" / "project-folder"
            root.mkdir(parents=True)
            with mock.patch.object(localaibrain, "DEPLOY_REGISTRY_PATH", registry):
                name = localaibrain.default_mcp_name(root, "project")
            self.assertEqual(name, "parent-folder-project-folder.localaibrain")

    def test_resolve_prefers_nearest_project_from_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outer = Path(tmp) / "workspace" / "repo"
            inner = outer / "sub" / "pkg"
            inner.mkdir(parents=True)
            deploys = [
                {"scope": "project", "root": str(outer), "mcp_name": "workspace.localaibrain"},
                {"scope": "project", "root": str(inner), "mcp_name": "repo.localaibrain"},
                {"scope": "main", "root": str(Path(tmp) / "main"), "mcp_name": "localaibrain"},
            ]
            candidate = localaibrain.resolve_nearest_project_candidate(deploys, inner / "src")
            self.assertIsNotNone(candidate)
            self.assertEqual(candidate.project_root, inner)
            self.assertEqual(candidate.mcp_tool_prefix, "repo.localaibrain")

    def test_strip_codex_managed_block(self) -> None:
        original = (
            'other = "value"\n'
            "# LOCAL_AI_BRAIN_MANAGED_START abc.localaibrain\n"
            '[mcp_servers."abc.localaibrain"]\n'
            'command = "python"\n'
            "# LOCAL_AI_BRAIN_MANAGED_END abc.localaibrain\n"
        )
        updated = localaibrain.strip_codex_managed_block(original, "abc.localaibrain")
        self.assertNotIn("LOCAL_AI_BRAIN_MANAGED_START", updated)
        self.assertIn('other = "value"', updated)

    def test_normal_install_refresh_preserves_destination_only_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = make_plan(Path(tmp))
            plan.package_dir.mkdir(parents=True)
            (plan.package_dir / "__main__.py").write_text("print('old')\n", encoding="utf-8")
            (plan.package_dir / "destination_only.py").write_text("keep\n", encoding="utf-8")
            (plan.source_package_dir / "feature.py").write_text("new\n", encoding="utf-8")

            localaibrain.install_package(plan, force=False)

            self.assertEqual((plan.package_dir / "__main__.py").read_text(encoding="utf-8"), "print('source')\n")
            self.assertEqual((plan.package_dir / "feature.py").read_text(encoding="utf-8"), "new\n")
            self.assertTrue((plan.package_dir / "destination_only.py").is_file())

    def test_builtin_skill_targets_use_slug_folders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = make_plan(Path(tmp))
            targets = [path.as_posix() for path in localaibrain.builtin_skill_targets(plan)]

            self.assertTrue(any("ourstuff-laib-optimize-main/SKILL.md" in path for path in targets))
            self.assertFalse(any("Ourstuff LAIB Optimize Main/SKILL.md" in path for path in targets))

    def test_deploy_builtin_skills_writes_skill_and_openai_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = make_plan(Path(tmp))

            localaibrain.deploy_builtin_skills(plan)

            skill = plan.project_root / ".agents" / "skills" / "ourstuff-laib-index" / "SKILL.md"
            metadata = skill.parent / "agents" / "openai.yaml"
            self.assertTrue(skill.is_file())
            self.assertTrue(metadata.is_file())
            self.assertIn("name: Ourstuff LAIB Index", skill.read_text(encoding="utf-8"))
            self.assertIn("description:", skill.read_text(encoding="utf-8"))
            self.assertIn("value: \"workspace.localaibrain\"", metadata.read_text(encoding="utf-8"))

    def test_write_json_config_uses_requested_server_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = make_plan(Path(tmp))
            opencode = Path(tmp) / "opencode.jsonc"
            opencode.write_text('{"model":"x", "mcp": {"other": {"type":"local"}}}', encoding="utf-8")

            localaibrain.write_json_config(
                opencode,
                plan,
                allow_jsonc=True,
                server_key="mcp",
                spec=localaibrain.opencode_server_spec(plan),
            )

            data = json.loads(opencode.read_text(encoding="utf-8"))
            self.assertIn("other", data["mcp"])
            self.assertEqual(data["mcp"]["workspace.localaibrain"]["type"], "local")
            self.assertNotIn("mcpServers", data)

    def test_parse_jsonc_handles_comments_and_trailing_commas(self) -> None:
        parsed = localaibrain.parse_jsonc(
            """
            {
              // keep comments
              "mcp": {
                "x": {"url": "https://example.test/path"},
              },
            }
            """
        )
        self.assertEqual(parsed["mcp"]["x"]["url"], "https://example.test/path")

    def test_toml_string_escapes_windows_backslashes(self) -> None:
        encoded = localaibrain.toml_string(r"C:\Users\jrice\brain")
        self.assertEqual(encoded, r'"C:\\Users\\jrice\\brain"')


if __name__ == "__main__":
    unittest.main()
