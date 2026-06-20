#!/usr/bin/env python3
"""Cross-platform Firebase chat deploy helper for Ourstuff projects."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable


DEFAULT_SECRETS = ("OPENROUTER_API_KEY",)
OPTIONAL_SECRETS = ("OPENAI_API_KEY",)
DEFAULT_FUNCTION = "projectsAiApi"
DEFAULT_REGION = "us-central1"


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> int:
    printable = " ".join(cmd)
    print(f"\n$ {printable}")
    result = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    if check and result.returncode != 0:
        raise SystemExit(result.returncode)
    return result.returncode


def require_firebase_cli() -> None:
    if shutil.which("firebase") is None:
        raise SystemExit("firebase CLI not found in PATH. Install it before running this helper.")


def normalize_firebase_dir(firebase_dir: str) -> Path:
    path = Path(firebase_dir).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"firebase dir does not exist: {path}")
    config = path / "firebase.json"
    if not config.exists():
        raise SystemExit(f"firebase.json not found in: {path}")
    return path


def timestamp() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def set_secrets(project: str, secrets: Iterable[str]) -> None:
    for secret_name in secrets:
        run(["firebase", "functions:secrets:set", secret_name, "--project", project])


def provider_default_model(provider: str) -> str:
    if provider == "openai":
        return "gpt-4o-mini"
    return "openrouter/owl-alpha"


def choose_provider(provider: str) -> str:
    if provider != "ask":
        return provider
    print("\nChoose provider for this deploy:")
    print("1) openrouter")
    print("2) openai")
    choice = input("Enter 1 or 2 [1]: ").strip() or "1"
    return "openai" if choice == "2" else "openrouter"


def write_env_file(firebase_dir: Path, project: str, provider: str, model: str | None) -> Path:
    resolved_provider = choose_provider(provider)
    resolved_model = (model or "").strip() or provider_default_model(resolved_provider)
    env_path = firebase_dir / f".env.{project}"
    if env_path.exists():
        backup = env_path.with_suffix(env_path.suffix + f".bak.{timestamp()}")
        shutil.copy2(env_path, backup)
        print(f"Backed up existing env file: {backup}")
    content = (
        f"PROJECTS_AI_PROVIDER={resolved_provider}\n"
        f"PROJECTS_AI_MODEL={resolved_model}\n"
    )
    env_path.write_text(content, encoding="utf-8")
    print(f"Wrote env file: {env_path}")
    return env_path


def deploy_function(project: str, firebase_dir: Path, function_name: str) -> None:
    run(
        [
            "firebase",
            "deploy",
            "--only",
            f"functions:{function_name}",
            "--config",
            str(firebase_dir / "firebase.json"),
            "--project",
            project,
        ],
        cwd=firebase_dir,
    )


def verify_deploy(project: str, function_name: str, region: str) -> None:
    run(["firebase", "functions:list", "--project", project])
    endpoint = f"https://{region}-{project}.cloudfunctions.net/{function_name}"
    print(f"\nExpected function URL:\n{endpoint}")


def newest_env_backup(firebase_dir: Path, project: str) -> Path | None:
    target = firebase_dir / f".env.{project}"
    candidates = sorted(
        target.parent.glob(f"{target.name}.bak.*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def rollback(project: str, firebase_dir: Path, function_name: str, region: str, restore_env: bool) -> None:
    run(
        [
            "firebase",
            "functions:delete",
            function_name,
            "--region",
            region,
            "--force",
            "--project",
            project,
        ]
    )
    if restore_env:
        backup = newest_env_backup(firebase_dir, project)
        if backup is None:
            print("No env backup found to restore.")
            return
        dest = firebase_dir / f".env.{project}"
        shutil.copy2(backup, dest)
        print(f"Restored env file from backup: {backup} -> {dest}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ourstuff Firebase chat deploy helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--project", required=True, help="Firebase project id (e.g. ourstuff-firebase).")
    common.add_argument("--firebase-dir", default=".", help="Path to .firebase directory.")
    common.add_argument("--function", default=DEFAULT_FUNCTION, help=f"Function name (default: {DEFAULT_FUNCTION}).")
    common.add_argument("--region", default=DEFAULT_REGION, help=f"Function region (default: {DEFAULT_REGION}).")

    p_set = subparsers.add_parser("set-secrets", parents=[common], help="Set Firebase function secrets.")
    p_set.add_argument(
        "--include-openai-secret",
        action="store_true",
        help="Also prompt for OPENAI_API_KEY.",
    )

    p_env = subparsers.add_parser("write-env", parents=[common], help="Write .env.<project> provider settings.")
    p_env.add_argument(
        "--provider",
        choices=("ask", "openrouter", "openai"),
        default="ask",
        help="Provider selection behavior (default: ask).",
    )
    p_env.add_argument("--model", default="", help="Optional explicit model override.")

    subparsers.add_parser("deploy", parents=[common], help="Deploy one function.")
    subparsers.add_parser("verify", parents=[common], help="Verify deployed function and print URL.")

    p_roll = subparsers.add_parser("rollback", parents=[common], help="Delete function and optionally restore env backup.")
    p_roll.add_argument("--restore-env", action="store_true", help="Restore latest .env backup.")

    p_full = subparsers.add_parser("full", parents=[common], help="Run secrets + env + deploy + verify flow.")
    p_full.add_argument(
        "--include-openai-secret",
        action="store_true",
        help="Also prompt for OPENAI_API_KEY.",
    )
    p_full.add_argument(
        "--provider",
        choices=("ask", "openrouter", "openai"),
        default="ask",
        help="Provider selection behavior (default: ask).",
    )
    p_full.add_argument("--model", default="", help="Optional explicit model override.")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    require_firebase_cli()
    firebase_dir = normalize_firebase_dir(args.firebase_dir)
    cmd = args.command

    if cmd == "set-secrets":
        secrets = list(DEFAULT_SECRETS)
        if args.include_openai_secret:
            secrets.extend(OPTIONAL_SECRETS)
        set_secrets(args.project, secrets)
        return

    if cmd == "write-env":
        write_env_file(firebase_dir, args.project, args.provider, args.model)
        return

    if cmd == "deploy":
        deploy_function(args.project, firebase_dir, args.function)
        return

    if cmd == "verify":
        verify_deploy(args.project, args.function, args.region)
        return

    if cmd == "rollback":
        rollback(args.project, firebase_dir, args.function, args.region, args.restore_env)
        return

    if cmd == "full":
        secrets = list(DEFAULT_SECRETS)
        if args.include_openai_secret:
            secrets.extend(OPTIONAL_SECRETS)
        set_secrets(args.project, secrets)
        write_env_file(firebase_dir, args.project, args.provider, args.model)
        deploy_function(args.project, firebase_dir, args.function)
        verify_deploy(args.project, args.function, args.region)
        return

    raise SystemExit(f"Unsupported command: {cmd}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
