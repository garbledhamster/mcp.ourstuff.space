#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate skill frontmatter and duplicate drift.")
    parser.add_argument("--agent-root", default=str(Path.home() / ".agents"))
    parser.add_argument("--codex-root", default=str(Path.home() / ".codex"))
    parser.add_argument("--include-plugin-skills", action="store_true")
    return parser.parse_args()


def load_inventory(agent_root: str, codex_root: str, include_plugin_skills: bool) -> list[dict[str, object]]:
    inventory_script = Path(__file__).with_name("Get-AgentSkillInventory.py")
    command = [
        sys.executable,
        str(inventory_script),
        "--agent-root",
        agent_root,
        "--codex-root",
        codex_root,
        "--json",
    ]
    if include_plugin_skills:
        command.append("--include-plugin-skills")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Inventory command failed:\n{result.stderr.strip()}")
    return json.loads(result.stdout)


def main() -> int:
    args = parse_args()
    inventory = load_inventory(args.agent_root, args.codex_root, args.include_plugin_skills)

    failures: list[str] = []
    for skill in inventory:
        if not skill.get("HasFrontmatter") or not skill.get("HasName") or not skill.get("HasDescription"):
            failures.append(f"missing-frontmatter\t{skill['SkillPath']}")

    duplicate_candidates = [
        skill
        for skill in inventory
        if skill.get("SkillName") and (args.include_plugin_skills or skill.get("Origin") != "CodexPlugin")
    ]
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for skill in duplicate_candidates:
        grouped[str(skill["SkillName"])].append(skill)

    for skill_name, group in grouped.items():
        if len(group) > 1:
            paths = " | ".join(str(skill["SkillPath"]) for skill in group)
            failures.append(f"duplicate-skill\t{skill_name}\t{paths}")

    if failures:
        for failure in failures:
            print(failure)
        print(f"Agent skill drift check failed with {len(failures)} issue(s).", file=sys.stderr)
        return 1

    print("PASS agent skill drift check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
