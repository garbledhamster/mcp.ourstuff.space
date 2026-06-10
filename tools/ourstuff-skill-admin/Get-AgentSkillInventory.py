#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List active skill inventory rows.")
    parser.add_argument("--agent-root", default=str(Path.home() / ".agents"))
    parser.add_argument("--codex-root", default=str(Path.home() / ".codex"))
    parser.add_argument("--include-plugin-skills", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit JSON rows.")
    return parser.parse_args()


def get_frontmatter_value(lines: list[str], key: str) -> str | None:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.*)\s*$")
    for line in lines:
        match = pattern.match(line)
        if match:
            return match.group(1).strip().strip('"').strip("'")
    return None


def read_skill_frontmatter(skill_path: Path) -> dict[str, object]:
    lines = skill_path.read_text(encoding="utf-8").splitlines()[:80]
    if not lines or lines[0] != "---":
        return {"name": None, "description": None, "has_frontmatter": False}

    end_index = -1
    for idx in range(1, len(lines)):
        if lines[idx] == "---":
            end_index = idx
            break
    if end_index < 0:
        return {"name": None, "description": None, "has_frontmatter": False}

    frontmatter = lines[1:end_index]
    return {
        "name": get_frontmatter_value(frontmatter, "name"),
        "description": get_frontmatter_value(frontmatter, "description"),
        "has_frontmatter": True,
    }


def get_direct_skill_rows(root: Path, origin: str) -> list[dict[str, object]]:
    if not root.exists():
        return []
    rows: list[dict[str, object]] = []
    for directory in sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: p.name.lower()):
        skill_path = directory / "SKILL.md"
        if not skill_path.exists():
            continue
        frontmatter = read_skill_frontmatter(skill_path)
        rows.append(
            {
                "SkillName": frontmatter["name"] or directory.name,
                "FolderName": directory.name,
                "Description": frontmatter["description"],
                "Origin": origin,
                "Root": str(root),
                "SkillPath": str(skill_path),
                "HasFrontmatter": bool(frontmatter["has_frontmatter"]),
                "HasName": bool(frontmatter["name"]),
                "HasDescription": bool(frontmatter["description"]),
                "IsSymlink": directory.is_symlink(),
            }
        )
    return rows


def get_plugin_skill_rows(plugin_root: Path) -> list[dict[str, object]]:
    if not plugin_root.exists():
        return []
    rows: list[dict[str, object]] = []
    for skill_path in sorted(plugin_root.rglob("SKILL.md"), key=lambda p: str(p).lower()):
        frontmatter = read_skill_frontmatter(skill_path)
        folder_name = skill_path.parent.name
        rows.append(
            {
                "SkillName": frontmatter["name"] or folder_name,
                "FolderName": folder_name,
                "Description": frontmatter["description"],
                "Origin": "CodexPlugin",
                "Root": str(plugin_root),
                "SkillPath": str(skill_path),
                "HasFrontmatter": bool(frontmatter["has_frontmatter"]),
                "HasName": bool(frontmatter["name"]),
                "HasDescription": bool(frontmatter["description"]),
                "IsSymlink": False,
            }
        )
    return rows


def format_table(rows: list[dict[str, object]]) -> str:
    columns = ["SkillName", "Origin", "SkillPath", "HasFrontmatter", "HasName", "HasDescription", "IsSymlink"]
    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(str(row[col])))
    header = "  ".join(col.ljust(widths[col]) for col in columns)
    divider = "  ".join("-" * widths[col] for col in columns)
    lines = [header, divider]
    for row in rows:
        lines.append("  ".join(str(row[col]).ljust(widths[col]) for col in columns))
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    agent_root = Path(args.agent_root).expanduser()
    codex_root = Path(args.codex_root).expanduser()

    rows: list[dict[str, object]] = []
    rows.extend(get_direct_skill_rows(agent_root / "skills", "PersonalAgents"))
    rows.extend(get_direct_skill_rows(codex_root / "skills", "CodexUser"))
    if args.include_plugin_skills:
        rows.extend(get_plugin_skill_rows(codex_root / "plugins" / "cache"))

    rows.sort(key=lambda r: (str(r["SkillName"]).lower(), str(r["Origin"]).lower(), str(r["SkillPath"]).lower()))

    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(format_table(rows) if rows else "No skills found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
