#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import shutil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Move public Codex skills into a timestamped archive.")
    parser.add_argument("--codex-skills-root", default=str(Path.home() / ".codex" / "skills"))
    parser.add_argument("--disabled-root", default=str(Path.home() / ".codex" / "skills.disabled"))
    parser.add_argument("--archive-name", default="")
    parser.add_argument("--what-if", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    codex_skills_root = Path(args.codex_skills_root).expanduser().resolve()
    disabled_root = Path(args.disabled_root).expanduser()

    if not codex_skills_root.exists():
        raise FileNotFoundError(f"Codex skills root not found: {codex_skills_root}")

    archive_name = args.archive_name or datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_path = (disabled_root / archive_name).resolve()
    archive_path.mkdir(parents=True, exist_ok=True)

    items = [item for item in codex_skills_root.iterdir() if item.is_dir() and item.name != ".system"]
    for item in items:
        target = archive_path / item.name
        if target.exists():
            raise FileExistsError(f"Archive already contains target: {target}")
        if not args.what_if:
            shutil.move(str(item), str(target))

    result = {
        "ArchivePath": str(archive_path),
        "MovedCount": len(items),
        "Preserved": str(codex_skills_root / ".system"),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
