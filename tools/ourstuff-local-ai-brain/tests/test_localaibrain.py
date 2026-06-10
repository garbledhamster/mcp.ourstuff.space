from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import localaibrain


def make_plan(root: Path) -> localaibrain.ProjectInstallPlan:
    project_root = root / "workspace" / "project"
    source_package = root / "source" / "local_ai_brain"
    scripts_dir = project_root / "scripts"
    data_dir = project_root / "brain"
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
        plans_dir=project_root / "plans",
        agents_file=project_root / "agents.md",
        mcp_dir=project_root / "mcp",
        mcp_registry_path=project_root / "mcp" / "local-ai-brain-tools.json",
        mcp_adapter_path=scripts_dir / "project_mcp.py",
        brain_scope="project",
        mcp_tool_prefix="workspace.localaibrain",
        register_agents=True,
    )


class LocalAiBrainDeployTests(unittest.TestCase):
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
