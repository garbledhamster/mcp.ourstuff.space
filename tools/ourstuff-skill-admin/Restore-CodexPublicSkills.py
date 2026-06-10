#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Restore archived Codex skills to active skills root.")
    parser.add_argument("--archive-path", required=True)
    parser.add_argument("--codex-skills-root", default=str(Path.home() / ".codex" / "skills"))
    parser.add_argument("--what-if", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    archive_path = Path(args.archive_path).expanduser().resolve()
    codex_skills_root = Path(args.codex_skills_root).expanduser()
    codex_skills_root.mkdir(parents=True, exist_ok=True)
    codex_skills_root = codex_skills_root.resolve()

    if not archive_path.exists():
        raise FileNotFoundError(f"Archive path not found: {archive_path}")

    items = [item for item in archive_path.iterdir() if item.is_dir()]
    for item in items:
        target = codex_skills_root / item.name
        if target.exists():
            raise FileExistsError(f"Active skill already exists, refusing overwrite: {target}")
        if not args.what_if:
            shutil.move(str(item), str(target))

    result = {
        "RestoredCount": len(items),
        "SourceArchive": str(archive_path),
        "TargetRoot": str(codex_skills_root),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
