from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MIN_PYTHON = (3, 10)
CANONICAL_INSTALLER_NAME = "localaibrain.py"
LAIB_CONTAINER_DIR = "localaibrain"
AGENTS_BLOCK_START = "<!-- LOCAL_AI_BRAIN_PROJECT_START -->"
AGENTS_BLOCK_END = "<!-- LOCAL_AI_BRAIN_PROJECT_END -->"
MCP_REGISTRY_NAME = "local-ai-brain-tools.json"
MCP_ADAPTER_NAME = "project_mcp.py"
DEPLOY_REGISTRY_PATH = Path.home() / ".agents" / "local-ai-brain" / "deploys.json"
LAIB_MANAGED_MARKER = "local-ai-brain-managed"
BUILTIN_SKILL_NAMES = [
    "Ourstuff LAIB Optimize Main",
    "Ourstuff LAIB Optimize Project",
    "Ourstuff LAIB Index",
]
BUILTIN_SKILL_SLUGS = {
    "Ourstuff LAIB Optimize Main": "ourstuff-laib-optimize-main",
    "Ourstuff LAIB Optimize Project": "ourstuff-laib-optimize-project",
    "Ourstuff LAIB Index": "ourstuff-laib-index",
}
WORK_FILE_PATTERN = "NNN_slug.ext"
WORK_FILE_EXAMPLE = "001_file-use-name.md"
WORK_FILE_EXCLUDED_DIRS = ("localaibrain", "scripts", "artifacts", "archive", "brain", "mcp", "meetings", "tools")
LOCAL_AI_BRAIN_ACTIONS = [
    ("doctor", "Run Local AI Brain doctor for this project.", "read_only"),
    ("context-pack", "Return a compact project Local AI Brain context pack.", "read_only"),
    ("search", "Search this project's Local AI Brain index.", "read_only"),
    ("record-artifact", "Record a project artifact through Local AI Brain capture.", "write_safe"),
    ("record-ticket", "Record a project ticket through Local AI Brain capture.", "write_safe"),
    ("record-event", "Record a project event in Local AI Brain.", "write_safe"),
    ("proof-start", "Start a project Local AI Brain proof session.", "write_safe"),
    ("proof-finish", "Finish a project Local AI Brain proof session.", "write_safe"),
    ("proof-report", "Report project Local AI Brain proof metrics.", "read_only"),
    ("rebuild-index", "Rebuild this project's Local AI Brain search index.", "write_safe"),
    ("codex-title-distill", "Run deterministic Codex title distill through this project brain.", "write_safe"),
    ("resolve-brain", "Resolve the explicit, nearest, recent, or main Local AI Brain target.", "read_only"),
    ("optimize-main", "Optimize the main Local AI Brain.", "write_safe"),
    ("optimize-project", "Optimize the nearest or selected project Local AI Brain.", "write_safe"),
    ("index", "Rebuild the selected Local AI Brain index.", "write_safe"),
]


@dataclass(frozen=True)
class ProjectInstallPlan:
    platform_name: str
    python_executable: Path
    source_package_dir: Path
    source_installer: Path
    project_root: Path
    scripts_dir: Path
    package_dir: Path
    data_dir: Path
    db_path: Path
    artifacts_dir: Path
    plans_dir: Path
    agents_file: Path
    mcp_dir: Path
    mcp_registry_path: Path
    mcp_adapter_path: Path
    brain_scope: str
    mcp_tool_prefix: str
    register_agents: bool


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    effective_argv = list(sys.argv[1:] if argv is None else argv)
    if not effective_argv:
        if sys.stdin.isatty():
            return interactive_cli(parser)
        parser.print_help()
        return 0
    command = effective_argv[0].lower()
    if command in {"help", "-h", "--help"}:
        print_commander_help(parser)
        return 0
    if command in {"deploy", "setup", "install"}:
        args = parser.parse_args(effective_argv[1:])
        return run_from_args(args)
    if command in {"install-skills", "skills"}:
        args = build_install_skills_parser().parse_args(effective_argv[1:])
        return run_install_skills_from_args(args)
    if command in {"run", "cmd", "brain"}:
        return run_local_brain_from_args(effective_argv[1:])
    if command in {"terminal", "shell"}:
        return open_terminal_from_args(effective_argv[1:])
    if command in {"ui", "gui"}:
        return open_ui_from_args(effective_argv[1:])
    if command == "rollback":
        args = build_rollback_parser().parse_args(effective_argv[1:])
        return run_rollback_from_args(args)
    if command in {"resolve-brain", "optimize-main", "optimize-project", "index"}:
        args = build_ops_parser(command).parse_args(effective_argv[1:])
        if command == "resolve-brain":
            return run_resolve_brain(args)
        if command == "optimize-main":
            return run_optimize_scope(args, force_scope="main")
        if command == "optimize-project":
            return run_optimize_scope(args, force_scope="project")
        return run_index_scope(args, force_scope="")
    if "--menu" in effective_argv:
        return interactive_cli(parser)

    args = parser.parse_args(effective_argv)
    return run_from_args(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=CANONICAL_INSTALLER_NAME,
        description=(
            "Commander for a project-local Local AI Brain. "
            "Use deploy/setup to seed the current folder, install-skills to install the optional skills, "
            "run to execute brain commands, or terminal/shell to open a configured command window."
        ),
    )
    parser.add_argument("--menu", action="store_true", help="Open the interactive terminal menu.")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root to initialize. Project installs default to the current directory; main installs default to ~/.agents/local-ai-brain.",
    )
    parser.add_argument(
        "--source-dir",
        default="",
        help="Optional source folder containing local_ai_brain, scripts/local_ai_brain, or tools/local_ai_brain.",
    )
    parser.add_argument("--what-if", action="store_true", help="Show what would happen without changing files.")
    parser.add_argument("--force", action="store_true", help="Replace scripts/local_ai_brain from --source-dir.")
    parser.add_argument("--doctor", action="store_true", help="Run doctor after init. This can require Distill.")
    parser.add_argument(
        "--brain-scope",
        choices=["main", "project"],
        default="",
        help="Install as the agents main brain or as a project brain. Interactive runs ask when omitted.",
    )
    parser.add_argument(
        "--platform",
        choices=["windows", "macos", "linux"],
        default="",
        help="Override platform detection for dry-run/testing.",
    )
    parser.add_argument("--mcp-name", default="", help="Deprecated compatibility option; MCP startup registration is disabled.")
    parser.add_argument(
        "--no-register-agents",
        action="store_true",
        help="Deprecated compatibility flag. MCP agent config registration is always skipped.",
    )
    return parser


def interactive_cli(parser: argparse.ArgumentParser) -> int:
    print("")
    print("Project Local AI Brain commander")
    print("Choose a mode. Each mode prints the exact direct command before it runs.")
    print("")
    print("Navigation: b=back | h=help | q=quit")
    print("")
    choices = {
        "1": ("Deploy or refresh this folder", ("deploy", [])),
        "2": ("Preview deploy", ("deploy", ["--what-if"])),
        "3": ("Force refresh package", ("deploy", ["--force"])),
        "4": ("Deploy and run doctor", ("deploy", ["--doctor"])),
        "5": ("Run a Local AI Brain command", "run"),
        "6": ("Open configured terminal", ("terminal", [])),
        "7": ("Open Local AI Brain UI", ("ui", [])),
        "8": ("Install/update Local AI Brain skills", ("install-skills", [])),
        "9": ("Rollback project-local files", ("rollback", [])),
        "10": ("Custom deploy builder", ("deploy", None)),
        "11": ("Show command help", "help"),
        "12": ("Quit", "quit"),
    }
    while True:
        for key, (label, _argv) in choices.items():
            print(f"{key}. {label}")
        raw_choice = read_input("Select mode [1] (b|h|q): ")
        if raw_choice is None:
            return 0
        choice = raw_choice.strip().lower() or "1"
        if choice in {"b", "back"}:
            continue
        if choice in {"h", "help"}:
            print("")
            print_commander_help(parser)
            print("")
            continue
        if choice in {"q", "quit", "12"}:
            return 0
        if choice not in choices:
            print("Unknown choice.")
            continue
        label, selected = choices[choice]
        if selected == "quit":
            return 0
        if selected == "help":
            print_commander_help(parser)
            print("")
            continue
        mode, selected_argv = selected
        argv = build_custom_argv() if selected_argv is None else list(selected_argv)
        print("")
        print(f"Mode: {label}")
        print("Direct command:")
        print(f"  python {CANONICAL_INSTALLER_NAME} {mode} {' '.join(argv)}".rstrip())
        print("")
        if not prompt_yes_no("Run this now?", default=True):
            print("")
            continue
        if mode == "terminal":
            open_terminal_from_args(argv)
            print("")
            continue
        if mode == "ui":
            open_ui_from_args(argv)
            print("")
            continue
        if mode == "install-skills":
            run_install_skills_from_args(build_install_skills_parser().parse_args(argv))
            print("")
            continue
        if mode == "run":
            interactive_run_command()
            print("")
            continue
        if mode == "rollback":
            run_rollback_from_args(build_rollback_parser().parse_args(argv))
            print("")
            continue
        run_from_args(parser.parse_args(argv))
        print("")
        continue


def interactive_run_command() -> int:
    print("")
    print("Examples:")
    print("  context-pack --query \"your topic\" --limit 5")
    print("  search --query \"your topic\" --limit 10")
    print("  doctor")
    while True:
        raw_command = read_input("Local AI Brain command (b/back/h/help/q/quit) [doctor]: ")
        if raw_command is None:
            return 0
        command = raw_command.strip().lower()
        if command in {"b", "back"}:
            return 0
        if command in {"h", "help"}:
            print("")
            print(
                "Enter a local AI Brain command string (for example, `context-pack --query \"your topic\" --limit 5` or `search --query \"topic\"`)."
            )
            print("")
            continue
        if command in {"q", "quit"}:
            return 0
        break
    raw_command = raw_command.strip() or "doctor"
    argv = split_command(raw_command)
    print("")
    print("Direct command:")
    print(f"  python {CANONICAL_INSTALLER_NAME} run {raw_command}".rstrip())
    print("")
    if not prompt_yes_no("Run this now?", default=True):
        return 0
    return run_local_brain_from_args(argv)


def print_commander_help(parser: argparse.ArgumentParser) -> None:
    print("Project Local AI Brain commander")
    print("")
    print("Commands:")
    print(f"  python {CANONICAL_INSTALLER_NAME} deploy [options]")
    print(f"  python {CANONICAL_INSTALLER_NAME} run <local_ai_brain command>")
    print(f"  python {CANONICAL_INSTALLER_NAME} terminal")
    print(f"  python {CANONICAL_INSTALLER_NAME} ui")
    print(f"  python {CANONICAL_INSTALLER_NAME} rollback [--what-if] [--yes]")
    print(f"  python {CANONICAL_INSTALLER_NAME} --menu")
    print("")
    print("Deploy options:")
    parser.print_help()


def build_custom_argv() -> list[str]:
    argv: list[str] = []
    project_root = prompt_text("Project root", ".")
    if project_root != ".":
        argv.extend(["--project-root", project_root])
    source_dir = prompt_text("Source dir containing local_ai_brain/scripts/local_ai_brain/tools/local_ai_brain; blank uses commander folder", "")
    if source_dir:
        argv.extend(["--source-dir", source_dir])
    brain_scope = prompt_choice("Brain scope", ["project", "main"], "project")
    argv.extend(["--brain-scope", brain_scope])
    platform_name = prompt_choice("Platform override", ["auto", "windows", "macos", "linux"], "auto")
    if platform_name != "auto":
        argv.extend(["--platform", platform_name])
    if prompt_yes_no("Preview only (--what-if)?", default=True):
        argv.append("--what-if")
    if prompt_yes_no("Replace scripts/local_ai_brain if it already exists (--force)?", default=False):
        argv.append("--force")
    if prompt_yes_no("Run doctor after init (--doctor)?", default=False):
        argv.append("--doctor")
    return argv


def prompt_text(label: str, default: str) -> str:
    suffix = f" [{default}]" if default else ""
    raw_value = read_input(f"{label}{suffix}: ")
    if raw_value is None:
        return default
    value = raw_value.strip()
    return value or default


def prompt_choice(label: str, choices: list[str], default: str) -> str:
    values = "/".join(choices)
    while True:
        raw_value = read_input(f"{label} ({values}) [{default}]: ")
        if raw_value is None:
            return default
        value = raw_value.strip() or default
        if value in choices:
            return value
        print(f"Choose one of: {values}")


def prompt_yes_no(label: str, default: bool) -> bool:
    marker = "Y/n" if default else "y/N"
    while True:
        raw_value = read_input(f"{label} [{marker}]: ")
        if raw_value is None:
            return default
        value = raw_value.strip().lower()
        if not value:
            return default
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print("Answer y or n.")


def read_input(prompt: str) -> str | None:
    try:
        return input(prompt)
    except EOFError:
        print("")
        return None


def split_command(raw_command: str) -> list[str]:
    return shlex.split(raw_command, posix=os.name != "nt")


def build_project_action_parser(program: str) -> argparse.ArgumentParser:
    command_parser = argparse.ArgumentParser(
        prog=program,
        description="Run or launch against this folder's project-local Local AI Brain.",
    )
    command_parser.add_argument("--project-root", default=".", help="Project root. Defaults to the current directory.")
    command_parser.add_argument("--source-dir", default="", help="Source folder for first-time setup. Defaults to commander folder.")
    command_parser.add_argument("--brain-scope", choices=["main", "project"], default="", help="Main brain or project brain.")
    command_parser.add_argument("--force-setup", action="store_true", help="Refresh scripts/local_ai_brain before running.")
    command_parser.add_argument("--no-setup", action="store_true", help="Do not auto-deploy if this folder has no project brain yet.")
    return command_parser


def prepare_or_require_project_plan(plan: ProjectInstallPlan, no_setup: bool, force: bool, doctor: bool) -> None:
    if no_setup:
        require_existing_project_brain(plan)
    else:
        ensure_project_ready(plan, force=force, doctor=doctor)


def run_local_brain_from_args(argv: list[str]) -> int:
    command_parser = build_project_action_parser(f"{CANONICAL_INSTALLER_NAME} run")
    command_parser.add_argument("brain_args", nargs=argparse.REMAINDER)
    args = command_parser.parse_args(argv)
    brain_args = list(args.brain_args)
    if brain_args and brain_args[0] == "--":
        brain_args = brain_args[1:]
    if not brain_args:
        command_parser.print_help()
        return 0
    misplaced_options = {"--project-root", "--source-dir", "--brain-scope", "--force-setup", "--no-setup"}
    if any(option in brain_args for option in misplaced_options):
        print(
            "ERROR: commander options for 'run' must come before the Local AI Brain command. "
            f"Example: python {CANONICAL_INSTALLER_NAME} run --project-root <folder> search --query <topic>",
            file=sys.stderr,
        )
        return 2

    try:
        require_python()
        plan = build_plan(
            argparse.Namespace(
                project_root=args.project_root,
                source_dir=args.source_dir,
                brain_scope=args.brain_scope,
                mcp_name="",
                platform="",
                what_if=False,
                force=args.force_setup,
                doctor=False,
                no_register_agents=True,
            )
        )
        prepare_or_require_project_plan(plan, args.no_setup, force=args.force_setup, doctor=False)
        return run_brain_command(plan, brain_args, check=False)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def open_terminal_from_args(argv: list[str]) -> int:
    command_parser = build_project_action_parser(f"{CANONICAL_INSTALLER_NAME} terminal")
    args = command_parser.parse_args(argv)
    try:
        require_python()
        plan = build_plan(
            argparse.Namespace(
                project_root=args.project_root,
                source_dir=args.source_dir,
                brain_scope=args.brain_scope,
                mcp_name="",
                platform="",
                what_if=False,
                force=args.force_setup,
                doctor=False,
                no_register_agents=True,
            )
        )
        prepare_or_require_project_plan(plan, args.no_setup, force=args.force_setup, doctor=False)
        return open_configured_terminal(plan)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def open_ui_from_args(argv: list[str]) -> int:
    command_parser = build_project_action_parser(f"{CANONICAL_INSTALLER_NAME} ui")
    args = command_parser.parse_args(argv)
    try:
        require_python()
        plan = build_plan(
            argparse.Namespace(
                project_root=args.project_root,
                source_dir=args.source_dir,
                brain_scope=args.brain_scope,
                mcp_name="",
                platform="",
                what_if=False,
                force=args.force_setup,
                doctor=False,
                no_register_agents=True,
            )
        )
        prepare_or_require_project_plan(plan, args.no_setup, force=args.force_setup, doctor=False)
        return open_project_ui(plan)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def open_project_ui(plan: ProjectInstallPlan) -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(plan.scripts_dir)
    env["LOCAL_AI_BRAIN_HOME"] = str(plan.data_dir)
    if plan.db_path.is_file():
        env["LOCAL_AI_BRAIN_DB"] = str(plan.db_path)
    return subprocess.run(
        [str(plan.python_executable), "-m", "local_ai_brain.ui"],
        cwd=plan.project_root,
        env=env,
        check=False,
    ).returncode


def require_existing_project_brain(plan: ProjectInstallPlan) -> None:
    if not (plan.package_dir / "__main__.py").is_file():
        raise RuntimeError(f"project brain is not deployed yet: {plan.package_dir}")
    if not plan.db_path.is_file():
        raise RuntimeError(f"project brain database is not initialized yet: {plan.db_path}")


def ensure_project_ready(plan: ProjectInstallPlan, force: bool, doctor: bool) -> None:
    migrate_old_scattered_install(plan)
    package_missing = not (plan.package_dir / "__main__.py").is_file()
    db_missing = not plan.db_path.is_file()
    agents_missing = not agents_block_exists(plan)
    if not (force or package_missing or db_missing or agents_missing or doctor):
        return
    if force or package_missing:
        print_plan(plan, what_if=False, force=force, doctor=doctor)
        install_package(plan, force=force)
    plan.data_dir.mkdir(parents=True, exist_ok=True)
    plan.plans_dir.mkdir(parents=True, exist_ok=True)
    if db_missing or force or package_missing:
        run_brain_command(plan, ["init"])
    if doctor:
        run_brain_command(plan, ["doctor"])
    if agents_missing or force or package_missing:
        write_agents_file(plan)
    record_deploy(plan)


def agents_block_exists(plan: ProjectInstallPlan) -> bool:
    if not plan.agents_file.is_file():
        return False
    content = plan.agents_file.read_text(encoding="utf-8")
    return AGENTS_BLOCK_START in content and AGENTS_BLOCK_END in content


def open_configured_terminal(plan: ProjectInstallPlan) -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(plan.scripts_dir)
    env["LOCAL_AI_BRAIN_HOME"] = str(plan.data_dir)
    if plan.platform_name == "windows":
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            raise RuntimeError("PowerShell is required to open a configured terminal on Windows")
        command = "\n".join(
            [
                f"$env:PYTHONPATH = {powershell_quote(str(plan.scripts_dir))}",
                f"$env:LOCAL_AI_BRAIN_HOME = {powershell_quote(str(plan.data_dir))}",
                f"Set-Location -LiteralPath {powershell_quote(str(plan.project_root))}",
                "function localaibrain { python -m local_ai_brain @args }",
                "Write-Host 'Local AI Brain ready. Use: localaibrain doctor'",
            ]
        )
        subprocess.Popen([shell, "-NoExit", "-Command", command], cwd=plan.project_root, env=env)
        print(f"opened Local AI Brain terminal for {plan.project_root}")
        return 0

    shell = os.environ.get("SHELL") or "/bin/sh"
    print("Opening a configured subshell. Use: python -m local_ai_brain doctor")
    return subprocess.run([shell], cwd=plan.project_root, env=env, check=False).returncode


def powershell_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def run_from_args(args: argparse.Namespace) -> int:
    try:
        require_python()
        plan = build_plan(args)
        return run_plan(plan, what_if=args.what_if, force=args.force, doctor=args.doctor)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def build_install_skills_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=f"{CANONICAL_INSTALLER_NAME} install-skills",
        description="Install or refresh the Local AI Brain skills without registering an MCP startup server.",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root. Project scope defaults to the current directory; main scope defaults to ~/.agents/local-ai-brain.",
    )
    parser.add_argument("--source-dir", default="", help="Source folder for this installer. Defaults to the commander folder.")
    parser.add_argument("--brain-scope", choices=["main", "project"], default="", help="Skill target scope.")
    parser.add_argument("--mcp-name", default="", help="Deprecated compatibility option; skills use commander commands, not MCP startup.")
    parser.add_argument("--platform", choices=["windows", "macos", "linux"], default="", help="Override platform detection.")
    return parser


def run_install_skills_from_args(args: argparse.Namespace) -> int:
    try:
        require_python()
        plan = build_plan(
            argparse.Namespace(
                project_root=args.project_root,
                source_dir=args.source_dir,
                brain_scope=args.brain_scope,
                mcp_name=args.mcp_name,
                platform=args.platform,
                what_if=False,
                force=False,
                doctor=False,
                no_register_agents=True,
            )
        )
        deploy_builtin_skills(plan)
        record_deploy(plan)
        print("Installed Local AI Brain skills:")
        for target in builtin_skill_targets(plan):
            print(f"  {target}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def build_rollback_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=f"{CANONICAL_INSTALLER_NAME} rollback",
        description="Remove project-local Local AI Brain generated files.",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root. Project scope defaults to the current directory; main scope defaults to ~/.agents/local-ai-brain.",
    )
    parser.add_argument("--source-dir", default="", help="Source folder for this installer. Defaults to the commander folder.")
    parser.add_argument("--what-if", action="store_true", help="Show what would happen without removing files.")
    parser.add_argument("--yes", action="store_true", help="Confirm destructive rollback without an interactive prompt.")
    parser.add_argument("--brain-scope", choices=["main", "project"], default="", help="Rollback target scope.")
    parser.add_argument("--mcp-name", default="", help="Rollback only this MCP name when provided.")
    return parser


def build_ops_parser(command: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=f"{CANONICAL_INSTALLER_NAME} {command}")
    parser.add_argument("--project-root", default="", help="Explicit project root.")
    parser.add_argument("--brain-scope", choices=["main", "project"], default="", help="Explicit scope override.")
    parser.add_argument("--mcp-name", default="", help="Explicit MCP name override.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--apply", action="store_true", help="Apply optimizer changes where supported.")
    parser.add_argument("--what-if", action="store_true", help="Preview optimizer actions where supported.")
    parser.add_argument("--db", default="", help="Optional explicit brain.db path.")
    parser.add_argument("--lookup-event-retention-days", type=int, default=30)
    parser.add_argument("--keep-lookup-events", type=int, default=200)
    parser.add_argument("--source-file-retention-days", type=int, default=30)
    parser.add_argument("--empty-record-retention-days", type=int, default=7)
    parser.add_argument("--drop-missing-artifacts", action="store_true")
    parser.add_argument("--no-vacuum", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--main-fallback", action="store_true", help="Allow main fallback when resolving project commands.")
    return parser


def run_resolve_brain(args: argparse.Namespace) -> int:
    resolved = resolve_brain_for_operation(
        explicit_root=args.project_root,
        explicit_scope=args.brain_scope,
        explicit_mcp_name=args.mcp_name,
        require_project=False,
        allow_main_fallback=True,
    )
    payload = {
        "scope": resolved.brain_scope,
        "root": str(resolved.project_root),
        "mcp_name": resolved.mcp_tool_prefix,
        "container": str(resolved.container_dir),
        "package_dir": str(resolved.package_dir),
        "mcp_adapter": str(resolved.mcp_adapter_path),
        "mcp_registry": str(resolved.mcp_registry_path),
        "scripts_dir": str(resolved.scripts_dir),
        "data_dir": str(resolved.data_dir),
        "db_path": str(resolved.db_path),
    }
    if resolved.brain_scope == "main":
        payload["main_brain_areas"] = [str(path.resolve()) for path in user_profile_brain_areas()]
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    touch_deploy_last_used(resolved.project_root, resolved.brain_scope, resolved.mcp_tool_prefix)
    return 0


def run_optimize_scope(args: argparse.Namespace, force_scope: str) -> int:
    explicit_scope = args.brain_scope or force_scope
    allow_main = explicit_scope == "main" or bool(args.main_fallback)
    resolved = resolve_brain_for_operation(
        explicit_root=args.project_root,
        explicit_scope=explicit_scope,
        explicit_mcp_name=args.mcp_name,
        require_project=(force_scope == "project" and explicit_scope != "main"),
        allow_main_fallback=allow_main,
    )
    if force_scope == "project" and resolved.brain_scope != "project" and explicit_scope != "main":
        raise RuntimeError("No project Local AI Brain found. Re-run with --brain-scope main to target the main brain.")
    optimize_args = []
    if args.db:
        optimize_args.extend(["--db", args.db])
    else:
        optimize_args.extend(["--db", str(resolved.db_path)])
    if args.apply and not args.what_if:
        optimize_args.append("--apply")
    optimize_args.extend(["--lookup-event-retention-days", str(args.lookup_event_retention_days)])
    optimize_args.extend(["--keep-lookup-events", str(args.keep_lookup_events)])
    optimize_args.extend(["--source-file-retention-days", str(args.source_file_retention_days)])
    optimize_args.extend(["--empty-record-retention-days", str(args.empty_record_retention_days)])
    if args.drop_missing_artifacts:
        optimize_args.append("--drop-missing-artifacts")
    if args.no_vacuum:
        optimize_args.append("--no-vacuum")
    if args.no_backup:
        optimize_args.append("--no-backup")
    if args.json:
        optimize_args.append("--json")
    result = run_brain_command(resolved, ["optimize", *optimize_args], check=False)
    touch_deploy_last_used(resolved.project_root, resolved.brain_scope, resolved.mcp_tool_prefix)
    return result


def run_index_scope(args: argparse.Namespace, force_scope: str) -> int:
    explicit_scope = args.brain_scope or force_scope
    resolved = resolve_brain_for_operation(
        explicit_root=args.project_root,
        explicit_scope=explicit_scope,
        explicit_mcp_name=args.mcp_name,
        require_project=False,
        allow_main_fallback=True,
    )
    result = run_brain_command(resolved, ["rebuild-index"], check=False)
    touch_deploy_last_used(resolved.project_root, resolved.brain_scope, resolved.mcp_tool_prefix)
    return result


def run_rollback_from_args(args: argparse.Namespace) -> int:
    try:
        require_python()
        plan = build_plan(
            argparse.Namespace(
                project_root=args.project_root,
                source_dir=args.source_dir,
                brain_scope=args.brain_scope or "project",
                mcp_name=args.mcp_name,
                platform="",
                what_if=False,
                force=False,
                doctor=False,
                no_register_agents=False,
            )
        )
        return run_rollback(plan, what_if=args.what_if, yes=args.yes)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def run_rollback(plan: ProjectInstallPlan, what_if: bool, yes: bool) -> int:
    if not plan.project_root.exists():
        raise RuntimeError(f"project root does not exist: {plan.project_root}")
    remove_target = [(plan.mcp_registry_path, "MCP registration manifest"), (plan.mcp_adapter_path, "MCP adapter")]
    if not what_if and not confirm_rollback(plan, yes):
        print("Rollback cancelled.")
        return 1
    for target, label in remove_target:
        if target == plan.agents_file:
            continue
        if not is_safe_under_project(plan.project_root, target):
            raise RuntimeError(f"unsafe rollback target: {target}")
        if what_if:
            print(f"Would remove {label}: {target}")
            continue
        if target.is_file():
            print(f"Removing {label}: {target}")
            target.unlink()
        elif target.is_dir():
            print(f"Removing {label}: {target}")
            shutil.rmtree(target)
        else:
            print(f"Already absent: {target}")
    remove_agents_block(plan, what_if=what_if)
    rollback_builtin_skills(plan, what_if=what_if)
    rollback_agent_configs(plan, what_if=what_if)
    remove_deploy_record(plan, what_if=what_if)
    return 0


def confirm_rollback(plan: ProjectInstallPlan, yes: bool) -> bool:
    if yes:
        return True
    if not sys.stdin.isatty():
        raise RuntimeError("rollback is destructive; re-run with --yes to confirm")
    print("")
    print(f"Rollback will remove project-local Local AI Brain state under: {plan.project_root}")
    return (read_input("Type rollback to continue: ") or "").strip().lower() == "rollback"


def remove_agents_block(plan: ProjectInstallPlan, what_if: bool) -> None:
    path = plan.agents_file
    if not path.is_file():
        return
    if what_if:
        print(f"Would remove AGENTS managed block: {path}")
        return
    content = path.read_text(encoding="utf-8")
    if AGENTS_BLOCK_START not in content or AGENTS_BLOCK_END not in content:
        print(f"No AGENTS managed block found: {path}")
        return
    before, rest = content.split(AGENTS_BLOCK_START, 1)
    _, after = rest.split(AGENTS_BLOCK_END, 1)
    updated = before.rstrip() + "\n\n" + after.lstrip()
    path.write_text(updated, encoding="utf-8")
    print(f"Removed AGENTS managed block: {path}")


def is_safe_under_project(project_root: Path, target: Path) -> bool:
    candidate = target.resolve()
    return candidate == project_root or project_root in candidate.parents


def require_python() -> None:
    if sys.version_info < MIN_PYTHON:
        required = ".".join(str(part) for part in MIN_PYTHON)
        current = platform.python_version()
        raise RuntimeError(f"Python {required}+ is required; found {current}")


def build_plan(args: argparse.Namespace) -> ProjectInstallPlan:
    brain_scope = resolve_brain_scope(getattr(args, "brain_scope", ""))
    project_root = resolve_install_root(getattr(args, "project_root", "."), brain_scope)
    source_root = Path(args.source_dir).expanduser().resolve() if args.source_dir else Path(__file__).resolve().parent
    register_agents = False
    source_package_dir = find_source_package(source_root)
    container_dir = (project_root / LAIB_CONTAINER_DIR).resolve()
    scripts_dir = (container_dir / "scripts").resolve()
    package_dir = (scripts_dir / "local_ai_brain").resolve()
    data_dir = (container_dir / "brain").resolve()
    mcp_dir = container_dir / "mcp"
    explicit_mcp_name = str(getattr(args, "mcp_name", "") or "").strip()
    mcp_name = explicit_mcp_name or default_mcp_name(project_root, brain_scope)
    return ProjectInstallPlan(
        platform_name=args.platform or detect_platform(),
        python_executable=Path(sys.executable).resolve(),
        source_package_dir=source_package_dir,
        source_installer=(source_root / CANONICAL_INSTALLER_NAME).resolve(),
        project_root=project_root,
        scripts_dir=scripts_dir,
        package_dir=package_dir,
        data_dir=data_dir,
        db_path=data_dir / "brain.db",
        artifacts_dir=data_dir / "artifacts",
        plans_dir=container_dir / "plans",
        agents_file=find_agents_file(project_root),
        mcp_dir=mcp_dir,
        mcp_registry_path=mcp_dir / MCP_REGISTRY_NAME,
        mcp_adapter_path=scripts_dir / MCP_ADAPTER_NAME,
        brain_scope=brain_scope,
        mcp_tool_prefix=mcp_name,
        register_agents=register_agents,
    )


def migrate_old_scattered_install(plan: ProjectInstallPlan) -> None:
    moves = (
        (plan.project_root / "scripts", plan.scripts_dir, "scripts"),
        (plan.project_root / "mcp", plan.mcp_dir, "MCP directory"),
        (plan.project_root / "brain", plan.data_dir, "runtime data"),
        (plan.project_root / "plans", plan.plans_dir, "plans"),
    )
    for source, destination, label in moves:
        if not source.exists():
            continue
        if destination.exists():
            print(f"WARN: existing destination for {label}, keeping both and skipping migration: {source} -> {destination}")
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))


def resolve_install_root(value: str, brain_scope: str) -> Path:
    text = str(value or "").strip()
    if brain_scope == "main" and text in {"", "."}:
        return (Path.home() / ".agents" / "local-ai-brain").resolve()
    return Path(text or ".").expanduser().resolve()


def resolve_brain_scope(value: str) -> str:
    if value:
        return value
    if sys.stdin.isatty():
        return prompt_choice("Install as", ["project", "main"], "project")
    return "project"


def find_source_package(source_root: Path) -> Path:
    candidates = [
        source_root / "local_ai_brain",
        source_root / "scripts" / "local_ai_brain",
        source_root / "tools" / "local_ai_brain",
        source_root / "tools" / "local-ai-brain" / "local_ai_brain",
    ]
    for candidate in candidates:
        if (candidate / "__main__.py").is_file():
            return candidate.resolve()
    raise RuntimeError(f"source is missing local_ai_brain package: {source_root}")


def find_agents_file(project_root: Path) -> Path:
    for name in ("agents.md", "AGENTS.md"):
        candidate = project_root / name
        if candidate.exists():
            return candidate.resolve()
    return (project_root / "agents.md").resolve()


def detect_platform() -> str:
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    if system == "darwin":
        return "macos"
    return "linux"


def run_plan(plan: ProjectInstallPlan, what_if: bool, force: bool, doctor: bool) -> int:
    print_plan(plan, what_if=what_if, force=force, doctor=doctor)
    if what_if:
        print("SKIP MCP agent config registration; Local AI Brain is skill/CLI only by default.")
        print(f'WOULD allow explicit skill install with: python "{plan.project_root / CANONICAL_INSTALLER_NAME}" install-skills')
        return 0

    plan.project_root.mkdir(parents=True, exist_ok=True)
    migrate_old_scattered_install(plan)
    install_package(plan, force=force)
    plan.data_dir.mkdir(parents=True, exist_ok=True)
    plan.plans_dir.mkdir(parents=True, exist_ok=True)
    run_brain_command(plan, ["init"])
    if doctor:
        run_brain_command(plan, ["doctor"])
    write_agents_file(plan)
    record_deploy(plan)
    print_next_steps(plan)
    return 0


def print_plan(plan: ProjectInstallPlan, what_if: bool, force: bool, doctor: bool) -> None:
    mode = "WhatIf" if what_if else "Install"
    scope_description = "main brain" if plan.brain_scope == "main" else "project brain"
    print(f"{mode}: {plan.brain_scope} Local AI Brain")
    print(f"platform: {plan.platform_name}")
    print(f"python: {plan.python_executable}")
    print(f"brain_scope: {plan.brain_scope}")
    print(f"project: {plan.project_root}")
    print(f"source_package: {plan.source_package_dir}")
    print(f"scripts: {plan.scripts_dir}")
    print(f"package: {plan.package_dir}")
    print(f"data: {plan.data_dir}")
    print(f"database: {plan.db_path}")
    print(f"plans: {plan.plans_dir}")
    print(f"work_file_naming: {WORK_FILE_PATTERN} (example: {WORK_FILE_EXAMPLE})")
    print(f"agents_file: {plan.agents_file}")
    if plan.brain_scope == "main":
        for path in user_profile_brain_areas():
            status = "present" if path.exists() else "candidate"
            print(f"main_brain_area: {path.resolve()} ({status})")
    print("register_agents: false (MCP startup registration disabled)")
    print(f"force: {force}")
    print(f"doctor: {doctor}")
    operations = [
        "ensure scripts/local_ai_brain exists",
        f"create {scope_description} runtime folder",
        f"run python -m local_ai_brain init with LOCAL_AI_BRAIN_HOME set to the {scope_description} folder",
        f"ensure plans folder exists and document readable work filenames like {WORK_FILE_EXAMPLE}",
        "append or refresh one Local AI Brain CLI block in agents.md",
        "leave MCP startup configs untouched",
    ]
    if not same_path(plan.source_package_dir, plan.package_dir):
        operations[0] = "copy local_ai_brain package into scripts/local_ai_brain"
    if doctor:
        operations.append("run python -m local_ai_brain doctor")
    for operation in operations:
        prefix = "WOULD" if what_if else "DO"
        print(f"{prefix} {operation}")


def install_package(plan: ProjectInstallPlan, force: bool) -> None:
    validate_source_package(plan.source_package_dir)
    if same_path(plan.source_package_dir, plan.package_dir):
        return
    if plan.package_dir.exists():
        assert_safe_package_destination(plan)
        if force:
            if plan.package_dir.is_dir():
                shutil.rmtree(plan.package_dir)
            else:
                plan.package_dir.unlink()
        elif not plan.package_dir.is_dir():
            raise RuntimeError(f"package destination is not a directory; re-run with --force to replace: {plan.package_dir}")
        else:
            copy_package_tree(plan.source_package_dir, plan.package_dir)
    if not plan.package_dir.exists():
        plan.package_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(plan.source_package_dir, plan.package_dir, ignore=copy_ignore)
    installer_destination = plan.project_root / CANONICAL_INSTALLER_NAME
    if plan.source_installer.is_file() and not same_path(plan.source_installer, installer_destination):
        shutil.copy2(plan.source_installer, installer_destination)


def validate_source_package(source_package_dir: Path) -> None:
    if not (source_package_dir / "__main__.py").is_file():
        raise RuntimeError(f"source package is missing __main__.py: {source_package_dir}")


def copy_package_tree(source: Path, destination: Path) -> None:
    for current_dir, dirnames, filenames in os.walk(source):
        current = Path(current_dir)
        ignored = copy_ignore(str(current), [*dirnames, *filenames])
        dirnames[:] = [name for name in dirnames if name not in ignored]
        relative = current.relative_to(source)
        target_dir = destination / relative
        target_dir.mkdir(parents=True, exist_ok=True)
        for filename in filenames:
            if filename in ignored:
                continue
            shutil.copy2(current / filename, target_dir / filename)


def same_path(left: Path, right: Path) -> bool:
    try:
        return left.samefile(right)
    except FileNotFoundError:
        return left.resolve() == right.resolve()


def copy_ignore(directory: str, names: list[str]) -> set[str]:
    ignored = {"__pycache__", ".pytest_cache", ".opencode", ".git"}
    ignored.update(name for name in names if name.endswith(".pyc") or name.endswith(".pyo"))
    return ignored


def assert_safe_package_destination(plan: ProjectInstallPlan) -> None:
    scripts_dir = plan.scripts_dir.resolve()
    package_dir = plan.package_dir.resolve()
    if package_dir == scripts_dir or scripts_dir not in package_dir.parents:
        raise RuntimeError(f"refusing to remove unsafe package destination: {package_dir}")


def run_brain_command(plan: ProjectInstallPlan, args: list[str], check: bool = True) -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(plan.scripts_dir)
    env["LOCAL_AI_BRAIN_HOME"] = str(plan.data_dir)
    result = subprocess.run(
        [str(plan.python_executable), "-m", "local_ai_brain", *args],
        cwd=plan.project_root,
        env=env,
        check=check,
    )
    return result.returncode


def write_mcp_registration(plan: ProjectInstallPlan) -> None:
    plan.mcp_dir.mkdir(parents=True, exist_ok=True)
    plan.mcp_adapter_path.parent.mkdir(parents=True, exist_ok=True)
    plan.mcp_adapter_path.write_text(mcp_adapter_source(plan), encoding="utf-8")
    plan.mcp_registry_path.write_text(json.dumps(mcp_registry(plan), indent=2) + "\n", encoding="utf-8")


def mcp_registry(plan: ProjectInstallPlan) -> dict[str, object]:
    return {
        "schema": f"ourstuff.local-mcp.{plan.brain_scope}-localaibrain.v1",
        "brain_scope": plan.brain_scope,
        "project": plan.project_root.name,
        "project_root": str(plan.project_root),
        "plan_naming": {
            "directory": str(plan.plans_dir),
            "pattern": WORK_FILE_PATTERN,
            "example": WORK_FILE_EXAMPLE,
            "rule": "Use the next 3-digit number, an underscore, and a short lowercase hyphenated slug. Preserve the file extension.",
        },
        "work_file_naming": {
            "pattern": WORK_FILE_PATTERN,
            "example": WORK_FILE_EXAMPLE,
            "excluded_directories": list(WORK_FILE_EXCLUDED_DIRS),
        },
        "server": {
            "name": plan.mcp_tool_prefix,
            "transport": "stdio",
            "command": str(plan.python_executable),
            "args": [str(plan.mcp_adapter_path)],
            "cwd": str(plan.project_root),
            "env": {
                "PYTHONPATH": str(plan.scripts_dir),
                "LOCAL_AI_BRAIN_HOME": str(plan.data_dir),
            },
        },
        "tools": [
            {
                "name": mcp_tool_name(plan, action),
                "action": action,
                "description": description,
                "permission": permission,
                "project_root": str(plan.project_root),
                "pythonpath": str(plan.scripts_dir),
                "local_ai_brain_home": str(plan.data_dir),
                "database": str(plan.db_path),
            }
            for action, description, permission in LOCAL_AI_BRAIN_ACTIONS
        ],
    }


def mcp_tool_name(plan: ProjectInstallPlan, action: str) -> str:
    return f"{plan.mcp_tool_prefix}.{action}"


def mcp_tool_prefix(project_root: Path, brain_scope: str) -> str:
    return default_mcp_name(project_root, brain_scope)


def default_mcp_name(project_root: Path, brain_scope: str) -> str:
    if brain_scope == "main":
        return "localaibrain"
    parent = project_tool_prefix(project_root.parent)
    child = project_tool_prefix(project_root)
    base = f"{parent}.localaibrain"
    deploys = load_deploy_registry().get("deploys", [])
    for entry in deploys:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("scope", "")) != "project":
            continue
        if str(entry.get("mcp_name", "")) != base:
            continue
        entry_root = str(entry.get("root", ""))
        if entry_root and Path(entry_root).expanduser().resolve() != project_root.resolve():
            return f"{parent}-{child}.localaibrain"
    return base


def project_tool_prefix(project_root: Path) -> str:
    name = project_root.name.strip() or "project"
    return re.sub(r"[^A-Za-z0-9_-]+", "-", name).strip("-") or "project"


def write_agents_file(plan: ProjectInstallPlan) -> None:
    plan.agents_file.parent.mkdir(parents=True, exist_ok=True)
    existing = plan.agents_file.read_text(encoding="utf-8") if plan.agents_file.exists() else "# Agent Instructions\n"
    block = agents_block(plan)
    if AGENTS_BLOCK_START in existing and AGENTS_BLOCK_END in existing:
        before, rest = existing.split(AGENTS_BLOCK_START, 1)
        _old, after = rest.split(AGENTS_BLOCK_END, 1)
        updated = before.rstrip() + "\n\n" + block + "\n" + after.lstrip()
        print(f"agents.md Local AI Brain instructions refreshed: {plan.agents_file}")
    elif AGENTS_BLOCK_START in existing:
        print(f"agents.md already contains an incomplete Local AI Brain marker; leaving file unchanged: {plan.agents_file}")
        return
    else:
        updated = existing.rstrip() + "\n\n" + block + "\n"
    plan.agents_file.write_text(updated, encoding="utf-8")


def agents_block(plan: ProjectInstallPlan) -> str:
    project = command_path(plan.project_root)
    commander = command_path(plan.project_root / CANONICAL_INSTALLER_NAME)
    scripts = command_path(plan.scripts_dir)
    package = command_path(plan.package_dir)
    data = command_path(plan.data_dir)
    database = command_path(plan.db_path)
    artifacts = command_path(plan.artifacts_dir)
    plans = command_path(plan.plans_dir)
    main_brain_areas = main_brain_areas_block(plan)
    scope_label = "Main" if plan.brain_scope == "main" else "Project"
    scope_sentence = (
        "This is the agents main Local AI Brain. Use the Local AI Brain skills or commander CLI."
        if plan.brain_scope == "main"
        else "This project has its own Local AI Brain. Use the Local AI Brain skills or commander CLI."
    )
    return f"""{AGENTS_BLOCK_START}
## {scope_label} Local AI Brain

{scope_sentence}
Use it before non-trivial repo, debugging, UI, deployment, planning, or multi-agent work that may depend on relevant history.

- Project root: `{project}`
- Brain scope: `{plan.brain_scope}`
- Commander: `{commander}`
- Python module path: `{scripts}`
- Local AI Brain package: `{package}`
- Runtime data path: `{data}`
- SQLite database path: `{database}`
- Artifact path: `{artifacts}`
- Plans path: `{plans}`
{main_brain_areas}

Use Python only. Do not write SQLite directly.

Agent software and model allocation:

- Keep a clear divide between model roles. Operator and Engineer lanes are lightweight coding agents for repo reads, local edits, tests, terminal work, MCP calls, and linear implementation. Larger architecture models such as GPT-5.5 are for innovation, system design, product architecture, strategy, and reviewing the shape of major decisions.
- Do not spend large architecture models on routine coding work when Copilot CLI, OpenCode, Codex coding lanes, or Claude Code can execute the task through their tools.
- When orchestrating multiple agents, assign linear implementation tickets to Operator/Engineer agents first, then escalate only the design question, architecture tradeoff, or unresolved blocker to a larger architecture model.
- Local AI Brain MCP startup registration is intentionally disabled. Use the skills or commander CLI below.

Full access command labels for agent software:

```yaml
full_access_commands:
  copilot: "copilot --allow-all"
  copilot_tools_only: "copilot --allow-all-tools"
  opencode: "opencode --dangerously-skip-permissions"
  codex: "codex --dangerously-bypass-approvals-and-sandbox"
  claude: "claude --permission-mode bypassPermissions"
  claude_alt: "claude --dangerously-skip-permissions"
one_shot_commands:
  copilot: "copilot -p \"<task>\" --allow-all"
  opencode: "opencode run --dir \"{project}\" --dangerously-skip-permissions \"<task>\""
  codex: "codex exec --cd \"{project}\" --dangerously-bypass-approvals-and-sandbox \"<task>\""
  claude: "cd \"{project}\"; claude -p \"<task>\" --permission-mode bypassPermissions"
```

Project commander:

```powershell
python "{commander}" deploy --brain-scope {plan.brain_scope}
python "{commander}" install-skills --brain-scope {plan.brain_scope}
python "{commander}" run --brain-scope {plan.brain_scope} context-pack --repo "{project}" --query "<topic>" --limit 5
python "{commander}" run --brain-scope {plan.brain_scope} search --repo "{project}" --query "<topic>" --limit 10
python "{commander}" run --brain-scope {plan.brain_scope} doctor
python "{commander}" terminal --brain-scope {plan.brain_scope}
```

Project work file naming:

- Keep project plans in `{plans}`.
- Name plan, phase, task, milestone, and similar work-tracking files as `{WORK_FILE_PATTERN}`, for example `{WORK_FILE_EXAMPLE}`.
- Use the next available 3-digit number, an underscore, and a short lowercase hyphenated slug that reads like the file topic.
- Preserve the file extension, such as `.md` or `.txt`.
- Do not apply this naming rule inside `{", ".join(WORK_FILE_EXCLUDED_DIRS)}`.

PowerShell:

```powershell
$env:PYTHONPATH = "{scripts}"
$env:LOCAL_AI_BRAIN_HOME = "{data}"
python -m local_ai_brain context-pack --repo "{project}" --query "<topic>" --limit 5
python -m local_ai_brain search --repo "{project}" --query "<topic>" --limit 10
python -m local_ai_brain proof-start --repo "{project}" --surface "<surface>" --summary "<scrubbed task>" --json
python -m local_ai_brain proof-finish --session "<proof-session-uid>" --json-file ".local\\proof-finish.json"
python -m local_ai_brain proof-report --repo "{project}" --json
python -m local_ai_brain optimize --apply
```

macOS/Linux:

```sh
PYTHONPATH="{scripts}" LOCAL_AI_BRAIN_HOME="{data}" python -m local_ai_brain context-pack --repo "{project}" --query "<topic>" --limit 5
PYTHONPATH="{scripts}" LOCAL_AI_BRAIN_HOME="{data}" python -m local_ai_brain search --repo "{project}" --query "<topic>" --limit 10
PYTHONPATH="{scripts}" LOCAL_AI_BRAIN_HOME="{data}" python -m local_ai_brain proof-start --repo "{project}" --surface "<surface>" --summary "<scrubbed task>" --json
PYTHONPATH="{scripts}" LOCAL_AI_BRAIN_HOME="{data}" python -m local_ai_brain proof-finish --session "<proof-session-uid>" --json-file ".local/proof-finish.json"
PYTHONPATH="{scripts}" LOCAL_AI_BRAIN_HOME="{data}" python -m local_ai_brain proof-report --repo "{project}" --json
PYTHONPATH="{scripts}" LOCAL_AI_BRAIN_HOME="{data}" python -m local_ai_brain optimize --apply
```

For token conservation, prefer `context-pack --limit 5` with a specific `--query` and `--surface` before broad scans. Use `search --limit 10` when you need more matches.
For proof that the brain helped, start a proof session before the first lookup, set `LOCAL_AI_BRAIN_PROOF_SESSION` to the returned id, classify useful/stale/irrelevant hits in `proof-finish`, and check `proof-report` before making speed or token-savings claims.
For deterministic maintenance, run `python -m local_ai_brain optimize --apply`; it finds the project `brain.db`, backs it up, removes transient cleanup candidates, rebuilds FTS, and compacts SQLite.

{AGENTS_BLOCK_END}"""


def main_brain_areas_block(plan: ProjectInstallPlan) -> str:
    if plan.brain_scope != "main":
        return ""
    lines = ["", "Main brain areas detected under the user profile:"]
    for path in user_profile_brain_areas():
        status = "present" if path.exists() else "candidate"
        lines.append(f"- `{command_path(path)}` ({status})")
    return "\n".join(lines)


def user_profile_brain_areas() -> list[Path]:
    home = Path.home()
    return [home / ".agents", home / ".codex", home / ".claude"]


def command_path(path: Path) -> str:
    return str(path.resolve())


def print_next_steps(plan: ProjectInstallPlan) -> None:
    print("")
    print("Next:")
    print(f"  commander: {plan.project_root / CANONICAL_INSTALLER_NAME}")
    print(f"  agents.md: {plan.agents_file}")
    print(f"  database: {plan.db_path}")
    print(f'  skills: python "{plan.project_root / CANONICAL_INSTALLER_NAME}" install-skills')
    print("")
    print("Commander:")
    print(f'  python "{plan.project_root / CANONICAL_INSTALLER_NAME}" run context-pack --query "your topic"')
    print(f'  python "{plan.project_root / CANONICAL_INSTALLER_NAME}" terminal')
    print("")
    print("Direct Python:")
    if plan.platform_name == "windows":
        print(f'  $env:PYTHONPATH = "{plan.scripts_dir}"')
        print(f'  $env:LOCAL_AI_BRAIN_HOME = "{plan.data_dir}"')
        print(f'  python -m local_ai_brain context-pack --repo "{plan.project_root}" --query "your topic"')
    else:
        print(
            f'  PYTHONPATH="{plan.scripts_dir}" LOCAL_AI_BRAIN_HOME="{plan.data_dir}" '
            f'python -m local_ai_brain context-pack --repo "{plan.project_root}" --query "your topic"'
        )


def mcp_adapter_source(plan: ProjectInstallPlan) -> str:
    tool_prefix = json.dumps(plan.mcp_tool_prefix)
    scope_description = "Main Local AI Brain" if plan.brain_scope == "main" else "Project-local Local AI Brain"
    scope_description_literal = json.dumps(scope_description)
    template = r'''from __future__ import annotations

import os
import sys
from pathlib import Path


INSTALL_CONTAINER = Path(__file__).resolve().parents[1]
PROJECT_ROOT = INSTALL_CONTAINER.parent
SCRIPTS_DIR = INSTALL_CONTAINER / "scripts"
os.environ["PYTHONPATH"] = str(SCRIPTS_DIR) + os.pathsep + os.environ.get("PYTHONPATH", "")
os.environ["LOCAL_AI_BRAIN_HOME"] = str(INSTALL_CONTAINER / "brain")
os.environ["LOCAL_AI_BRAIN_PROJECT_ROOT"] = str(PROJECT_ROOT)
os.environ["LOCAL_AI_BRAIN_MCP_TOOL_PREFIX"] = __TOOL_PREFIX__
os.environ["LOCAL_AI_BRAIN_MCP_SCOPE_DESCRIPTION"] = __SCOPE_DESCRIPTION__
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from local_ai_brain.project_mcp import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
'''
    return template.replace("__TOOL_PREFIX__", tool_prefix).replace("__SCOPE_DESCRIPTION__", scope_description_literal)


@dataclass(frozen=True)
class ResolvedBrain:
    project_root: Path
    brain_scope: str
    mcp_tool_prefix: str
    scripts_dir: Path
    data_dir: Path
    package_dir: Path
    container_dir: Path
    mcp_adapter_path: Path
    mcp_registry_path: Path
    db_path: Path
    python_executable: Path


def now_iso_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def deploy_registry_path() -> Path:
    return DEPLOY_REGISTRY_PATH.expanduser().resolve()


def load_deploy_registry() -> dict[str, Any]:
    path = deploy_registry_path()
    if not path.is_file():
        return {"deploys": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"deploys": []}
    deploys = data.get("deploys", [])
    if not isinstance(deploys, list):
        deploys = []
    return {"deploys": deploys}


def save_deploy_registry(registry: dict[str, Any]) -> None:
    path = deploy_registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"deploys": registry.get("deploys", [])}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def record_deploy(plan: ProjectInstallPlan) -> None:
    container_dir = plan.project_root / LAIB_CONTAINER_DIR
    registry = load_deploy_registry()
    deploys = [entry for entry in registry.get("deploys", []) if isinstance(entry, dict)]
    now = now_iso_utc()
    deployed_skills = [str(path) for path in builtin_skill_targets(plan)]
    entry = {
        "scope": plan.brain_scope,
        "root": str(plan.project_root),
        "mcp_name": plan.mcp_tool_prefix,
        "container": str(container_dir),
        "package": str(plan.package_dir),
        "adapter": str(plan.mcp_adapter_path),
        "registry": str(plan.mcp_registry_path),
        "deployed_skills": deployed_skills,
        "last_deployed": now,
        "last_used": now,
    }
    if plan.brain_scope == "main":
        entry["main_brain_areas"] = [str(path.resolve()) for path in user_profile_brain_areas()]
    updated = False
    for index, current in enumerate(deploys):
        if (
            str(current.get("scope", "")) == plan.brain_scope
            and str(current.get("root", "")) == str(plan.project_root)
            and str(current.get("mcp_name", "")) == plan.mcp_tool_prefix
        ):
            deploys[index] = entry
            updated = True
            break
    if not updated:
        deploys.append(entry)
    registry["deploys"] = deploys
    save_deploy_registry(registry)


def touch_deploy_last_used(project_root: Path, brain_scope: str, mcp_name: str) -> None:
    registry = load_deploy_registry()
    changed = False
    for entry in registry.get("deploys", []):
        if not isinstance(entry, dict):
            continue
        if (
            str(entry.get("root", "")) == str(project_root)
            and str(entry.get("scope", "")) == brain_scope
            and str(entry.get("mcp_name", "")) == mcp_name
        ):
            entry["last_used"] = now_iso_utc()
            changed = True
            break
    if changed:
        save_deploy_registry(registry)


def remove_deploy_record(plan: ProjectInstallPlan, what_if: bool) -> None:
    registry = load_deploy_registry()
    deploys = [entry for entry in registry.get("deploys", []) if isinstance(entry, dict)]
    kept = []
    removed = 0
    for entry in deploys:
        if (
            str(entry.get("root", "")) == str(plan.project_root)
            and str(entry.get("scope", "")) == plan.brain_scope
            and (not getattr(plan, "mcp_tool_prefix", "") or str(entry.get("mcp_name", "")) == plan.mcp_tool_prefix)
        ):
            removed += 1
            continue
        kept.append(entry)
    if what_if:
        print(f"Would remove deploy registry entries: {removed}")
        return
    registry["deploys"] = kept
    save_deploy_registry(registry)


def resolve_brain_for_operation(
    explicit_root: str,
    explicit_scope: str,
    explicit_mcp_name: str,
    require_project: bool,
    allow_main_fallback: bool,
) -> ResolvedBrain:
    registry = load_deploy_registry()
    deploys = [entry for entry in registry.get("deploys", []) if isinstance(entry, dict)]
    candidate = resolve_explicit_candidate(deploys, explicit_root, explicit_scope, explicit_mcp_name)
    if candidate is None:
        candidate = resolve_nearest_project_candidate(deploys, Path.cwd().resolve())
    if candidate is None:
        candidate = resolve_recent_project_candidate(deploys)
    if candidate is None and allow_main_fallback:
        candidate = resolve_recent_main_candidate(deploys)
    if candidate is None:
        if require_project:
            raise RuntimeError("No project Local AI Brain deployment is available.")
        raise RuntimeError("No Local AI Brain deployment is available. Run deploy first.")
    if require_project and candidate.brain_scope != "project":
        raise RuntimeError("No project Local AI Brain deployment is available.")
    return candidate


def resolve_explicit_candidate(
    deploys: list[dict[str, Any]],
    explicit_root: str,
    explicit_scope: str,
    explicit_mcp_name: str,
) -> ResolvedBrain | None:
    root = explicit_root.strip()
    scope = explicit_scope.strip()
    mcp_name = explicit_mcp_name.strip()
    if not (root or scope or mcp_name):
        return None
    root_path = Path(root).expanduser().resolve() if root else None
    for entry in deploys:
        entry_root = Path(str(entry.get("root", "."))).expanduser().resolve()
        entry_scope = str(entry.get("scope", ""))
        entry_name = str(entry.get("mcp_name", ""))
        if root_path is not None and entry_root != root_path:
            continue
        if scope and entry_scope != scope:
            continue
        if mcp_name and entry_name != mcp_name:
            continue
        return candidate_from_registry(entry)
    if root_path is not None:
        guessed_scope = scope or "project"
        return guessed_candidate(root_path, guessed_scope, mcp_name or default_mcp_name(root_path, guessed_scope))
    if scope == "main":
        fallback_root = Path.cwd().resolve()
        return guessed_candidate(fallback_root, "main", mcp_name or "localaibrain")
    return None


def resolve_nearest_project_candidate(deploys: list[dict[str, Any]], cwd: Path) -> ResolvedBrain | None:
    candidates: list[tuple[int, ResolvedBrain]] = []
    for entry in deploys:
        if str(entry.get("scope", "")) != "project":
            continue
        root = Path(str(entry.get("root", "."))).expanduser().resolve()
        if cwd == root or root in cwd.parents:
            candidates.append((len(str(root)), candidate_from_registry(entry)))
    if not candidates:
        return None
    candidates.sort(key=lambda pair: pair[0], reverse=True)
    return candidates[0][1]


def resolve_recent_project_candidate(deploys: list[dict[str, Any]]) -> ResolvedBrain | None:
    projects = [entry for entry in deploys if str(entry.get("scope", "")) == "project"]
    if not projects:
        return None
    projects.sort(key=lambda entry: str(entry.get("last_used", "")) or str(entry.get("last_deployed", "")), reverse=True)
    return candidate_from_registry(projects[0])


def resolve_recent_main_candidate(deploys: list[dict[str, Any]]) -> ResolvedBrain | None:
    mains = [entry for entry in deploys if str(entry.get("scope", "")) == "main"]
    if not mains:
        return None
    mains.sort(key=lambda entry: str(entry.get("last_used", "")) or str(entry.get("last_deployed", "")), reverse=True)
    return candidate_from_registry(mains[0])


def _coerce_entry_path(value: Any, project_root: Path) -> Path | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    candidate = Path(text).expanduser()
    if candidate.is_absolute():
        return candidate
    return project_root / candidate


def _container_from_entry(root: Path, entry: dict[str, Any]) -> Path:
    container = _coerce_entry_path(entry.get("container"), root)
    if container is not None:
        return container
    registry = _coerce_entry_path(entry.get("registry"), root)
    if registry is not None:
        if registry.name == MCP_REGISTRY_NAME:
            if registry.parent.name == "mcp":
                return registry.parent.parent
            return registry.parent
    adapter = _coerce_entry_path(entry.get("adapter"), root)
    if adapter is not None:
        if adapter.name == MCP_ADAPTER_NAME:
            adapter_parent = adapter.parent
            if adapter_parent.name == "scripts":
                return adapter_parent.parent
        return adapter.parent
    return root


def candidate_from_registry(entry: dict[str, Any]) -> ResolvedBrain:
    root = Path(str(entry.get("root", "."))).expanduser().resolve()
    scope = str(entry.get("scope", "project"))
    name = str(entry.get("mcp_name", default_mcp_name(root, scope)))
    container_dir = _container_from_entry(root, entry)
    scripts_dir = container_dir / "scripts"
    data_dir = container_dir / "brain"
    return ResolvedBrain(
        project_root=root,
        brain_scope=scope,
        mcp_tool_prefix=name,
        scripts_dir=scripts_dir,
        package_dir=scripts_dir / "local_ai_brain",
        container_dir=container_dir,
        mcp_adapter_path=container_dir / "scripts" / MCP_ADAPTER_NAME,
        mcp_registry_path=container_dir / "mcp" / MCP_REGISTRY_NAME,
        data_dir=data_dir,
        db_path=data_dir / "brain.db",
        python_executable=Path(sys.executable).resolve(),
    )


def guessed_candidate(root: Path, scope: str, mcp_name: str) -> ResolvedBrain:
    container_dir = root / LAIB_CONTAINER_DIR
    scripts_dir = container_dir / "scripts"
    data_dir = container_dir / "brain"
    return ResolvedBrain(
        project_root=root,
        brain_scope=scope,
        mcp_tool_prefix=mcp_name,
        scripts_dir=scripts_dir,
        package_dir=scripts_dir / "local_ai_brain",
        container_dir=container_dir,
        mcp_adapter_path=scripts_dir / MCP_ADAPTER_NAME,
        mcp_registry_path=container_dir / "mcp" / MCP_REGISTRY_NAME,
        data_dir=data_dir,
        db_path=data_dir / "brain.db",
        python_executable=Path(sys.executable).resolve(),
    )


def skill_template_source(skill_name: str, plan: ProjectInstallPlan) -> str:
    if skill_name == "Ourstuff LAIB Optimize Main":
        action = "optimize-main"
        description = "Optimize the main Local AI Brain through the commander CLI."
    elif skill_name == "Ourstuff LAIB Optimize Project":
        action = "optimize-project"
        description = "Optimize the nearest or most relevant project Local AI Brain through the commander CLI."
    else:
        action = "index"
        description = "Rebuild the nearest Local AI Brain index through the commander CLI."
    return (
        "---\n"
        f"name: {skill_name}\n"
        f"description: {description}\n"
        "managed_by: local-ai-brain-managed\n"
        "schema: v1\n"
        "---\n\n"
        f"Use `python \"{plan.project_root / CANONICAL_INSTALLER_NAME}\" {action}` for this Local AI Brain deployment.\n"
    )


def skill_scope_roots(plan: ProjectInstallPlan) -> list[Path]:
    if plan.brain_scope == "main":
        return [Path.home()]
    return [plan.project_root]


def builtin_skill_targets(plan: ProjectInstallPlan) -> list[Path]:
    targets: list[Path] = []
    for root in skill_scope_roots(plan):
        for base in (root / ".agents" / "skills", root / ".claude" / "skills"):
            for skill in BUILTIN_SKILL_NAMES:
                targets.append(base / BUILTIN_SKILL_SLUGS[skill] / "SKILL.md")
    return targets


def deploy_builtin_skills(plan: ProjectInstallPlan) -> None:
    templates_root = Path(__file__).resolve().parent / "templates" / "skills"
    for skill_name in BUILTIN_SKILL_NAMES:
        slug = BUILTIN_SKILL_SLUGS[skill_name]
        template_path = templates_root / slug / "SKILL.md"
        if template_path.is_file():
            body = template_path.read_text(encoding="utf-8")
        else:
            body = skill_template_source(skill_name, plan)
        for root in skill_scope_roots(plan):
            for base in (root / ".agents" / "skills", root / ".claude" / "skills"):
                target = base / slug / "SKILL.md"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(body, encoding="utf-8")
                openai_yaml = target.parent / "agents" / "openai.yaml"
                openai_yaml.parent.mkdir(parents=True, exist_ok=True)
                openai_yaml.write_text(skill_openai_yaml(skill_name, plan), encoding="utf-8")


def rollback_builtin_skills(plan: ProjectInstallPlan, what_if: bool) -> None:
    for target in builtin_skill_targets(plan):
        if not target.is_file():
            continue
        content = target.read_text(encoding="utf-8")
        if LAIB_MANAGED_MARKER not in content:
            continue
        skill_dir = target.parent
        if what_if:
            print(f"Would remove managed skill: {skill_dir}")
            continue
        shutil.rmtree(skill_dir, ignore_errors=True)
        print(f"Removed managed skill: {skill_dir}")


def skill_openai_yaml(skill_name: str, plan: ProjectInstallPlan) -> str:
    display_name = skill_name
    short_description = {
        "Ourstuff LAIB Optimize Main": "Optimize the main Local AI Brain.",
        "Ourstuff LAIB Optimize Project": "Optimize the nearest project Local AI Brain.",
        "Ourstuff LAIB Index": "Rebuild the nearest Local AI Brain index.",
    }.get(skill_name, "Use Local AI Brain maintenance tools.")
    return f"""interface:
  display_name: "{display_name}"
  short_description: "{short_description}"
  default_prompt: "Use {skill_name}."
policy:
  allow_implicit_invocation: true
dependencies:
  tools: []
metadata:
  managed_by: "{LAIB_MANAGED_MARKER}"
"""


def register_agent_configs(plan: ProjectInstallPlan) -> None:
    for name, func in (
        ("Codex", register_codex_config),
        ("Copilot CLI", register_copilot_config),
        ("OpenCode", register_opencode_config),
        ("Claude Code", register_claude_config),
    ):
        try:
            func(plan)
        except Exception as exc:
            print(f"WARN: unable to register {name} MCP config: {exc}")


def rollback_agent_configs(plan: ProjectInstallPlan, what_if: bool) -> None:
    for func in (
        lambda: rollback_codex_config(plan, what_if),
        lambda: rollback_json_config(Path.home() / ".copilot" / "mcp-config.json", plan, what_if, server_key="mcpServers"),
        lambda: rollback_json_config(Path.home() / ".config" / "opencode" / "opencode.jsonc", plan, what_if, server_key="mcp"),
        lambda: rollback_json_config(claude_fallback_config_path(plan), plan, what_if, server_key="mcpServers"),
    ):
        try:
            func()
        except Exception as exc:
            print(f"WARN: unable to rollback managed MCP config entry: {exc}")


def server_spec(plan: ProjectInstallPlan) -> dict[str, Any]:
    return {
        "command": str(plan.python_executable),
        "args": [str(plan.mcp_adapter_path)],
        "cwd": str(plan.project_root),
        "env": {
            "PYTHONPATH": str(plan.scripts_dir),
            "LOCAL_AI_BRAIN_HOME": str(plan.data_dir),
        },
        "managedBy": LAIB_MANAGED_MARKER,
        "scope": plan.brain_scope,
        "root": str(plan.project_root),
    }


def opencode_server_spec(plan: ProjectInstallPlan) -> dict[str, Any]:
    return {
        "type": "local",
        "command": [str(plan.python_executable), str(plan.mcp_adapter_path)],
        "enabled": True,
        "environment": {
            "PYTHONPATH": str(plan.scripts_dir),
            "LOCAL_AI_BRAIN_HOME": str(plan.data_dir),
        },
        "managedBy": LAIB_MANAGED_MARKER,
        "scope": plan.brain_scope,
        "root": str(plan.project_root),
    }


def register_codex_config(plan: ProjectInstallPlan) -> None:
    path = Path.home() / ".codex" / "config.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    marker_start = f"# LOCAL_AI_BRAIN_MANAGED_START {plan.mcp_tool_prefix}"
    marker_end = f"# LOCAL_AI_BRAIN_MANAGED_END {plan.mcp_tool_prefix}"
    quoted_name = plan.mcp_tool_prefix.replace('"', '\\"')
    block = (
        f"{marker_start}\n"
        f'[mcp_servers."{quoted_name}"]\n'
        f"command = {toml_string(str(plan.python_executable))}\n"
        f"args = [{toml_string(str(plan.mcp_adapter_path))}]\n"
        f"cwd = {toml_string(str(plan.project_root))}\n"
        "startup_timeout_sec = 10\n"
        f'[mcp_servers."{quoted_name}".env]\n'
        f"PYTHONPATH = {toml_string(str(plan.scripts_dir))}\n"
        f"LOCAL_AI_BRAIN_HOME = {toml_string(str(plan.data_dir))}\n"
        f"managed_by = {toml_string(LAIB_MANAGED_MARKER)}\n"
        f"{marker_end}\n"
    )
    updated = strip_codex_managed_block(existing, plan.mcp_tool_prefix).rstrip()
    if updated:
        updated += "\n\n"
    updated += block
    backup_file(path)
    path.write_text(updated + ("\n" if not updated.endswith("\n") else ""), encoding="utf-8")


def rollback_codex_config(plan: ProjectInstallPlan, what_if: bool) -> None:
    path = Path.home() / ".codex" / "config.toml"
    if not path.is_file():
        return
    existing = path.read_text(encoding="utf-8")
    updated = strip_codex_managed_block(existing, plan.mcp_tool_prefix)
    if updated == existing:
        return
    if what_if:
        print(f"Would remove managed Codex MCP block: {path}")
        return
    backup_file(path)
    path.write_text(updated, encoding="utf-8")
    print(f"Removed managed Codex MCP block: {path}")


def strip_codex_managed_block(content: str, mcp_name: str) -> str:
    pattern = re.compile(
        re.escape(f"# LOCAL_AI_BRAIN_MANAGED_START {mcp_name}")
        + r".*?"
        + re.escape(f"# LOCAL_AI_BRAIN_MANAGED_END {mcp_name}")
        + r"\n?",
        re.DOTALL,
    )
    return pattern.sub("", content)


def register_copilot_config(plan: ProjectInstallPlan) -> None:
    write_json_config(Path.home() / ".copilot" / "mcp-config.json", plan, allow_jsonc=False, server_key="mcpServers", spec=server_spec(plan))


def register_opencode_config(plan: ProjectInstallPlan) -> None:
    write_json_config(Path.home() / ".config" / "opencode" / "opencode.jsonc", plan, allow_jsonc=True, server_key="mcp", spec=opencode_server_spec(plan))


def register_claude_config(plan: ProjectInstallPlan) -> None:
    claude_cli = shutil.which("claude")
    if claude_cli:
        try:
            result = subprocess.run(
                [
                    claude_cli,
                    "mcp",
                    "add",
                    "--scope",
                    "user" if plan.brain_scope == "main" else "project",
                    plan.mcp_tool_prefix,
                    "--",
                    str(plan.python_executable),
                    str(plan.mcp_adapter_path),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(plan.project_root),
            )
            if result.returncode == 0:
                return
            print(f"WARN: Claude CLI MCP registration failed: {result.stderr.strip() or result.stdout.strip()}")
        except Exception:
            print("WARN: Claude CLI MCP registration failed; writing .mcp.json fallback.")
    write_json_config(claude_fallback_config_path(plan), plan, allow_jsonc=False, server_key="mcpServers", spec=server_spec(plan))


def claude_fallback_config_path(plan: ProjectInstallPlan) -> Path:
    if plan.brain_scope == "project":
        return plan.project_root / ".mcp.json"
    return Path.home() / ".mcp.json"


def parse_jsonc(text: str) -> dict[str, Any]:
    cleaned = strip_jsonc_comments(text)
    cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
    stripped = cleaned.strip()
    if not stripped:
        return {}
    parsed = json.loads(stripped)
    if not isinstance(parsed, dict):
        return {}
    return parsed


def strip_jsonc_comments(text: str) -> str:
    output: list[str] = []
    index = 0
    in_string = False
    escape = False
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if in_string:
            output.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            output.append(char)
            index += 1
            continue
        if char == "/" and nxt == "/":
            index += 2
            while index < len(text) and text[index] not in "\r\n":
                index += 1
            continue
        if char == "/" and nxt == "*":
            index += 2
            while index + 1 < len(text) and not (text[index] == "*" and text[index + 1] == "/"):
                index += 1
            index += 2
            continue
        output.append(char)
        index += 1
    return "".join(output)


def toml_string(value: str) -> str:
    return json.dumps(value)


def write_json_config(path: Path, plan: ProjectInstallPlan, allow_jsonc: bool, server_key: str, spec: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        raw = path.read_text(encoding="utf-8")
        try:
            data = parse_jsonc(raw) if allow_jsonc else json.loads(raw)
        except Exception:
            print(f"WARN: could not parse existing config, skipping update: {path}")
            return
        if not isinstance(data, dict):
            print(f"WARN: unexpected config shape, skipping update: {path}")
            return
    else:
        data = {}
    servers = data.get(server_key)
    if not isinstance(servers, dict):
        servers = {}
    servers[plan.mcp_tool_prefix] = spec
    data[server_key] = servers
    backup_file(path)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def rollback_json_config(path: Path, plan: ProjectInstallPlan, what_if: bool, server_key: str) -> None:
    if not path.is_file():
        return
    raw = path.read_text(encoding="utf-8")
    try:
        data = parse_jsonc(raw)
    except Exception:
        return
    changed = False
    servers = data.get(server_key)
    if isinstance(servers, dict):
        current = servers.get(plan.mcp_tool_prefix)
        if isinstance(current, dict) and str(current.get("managedBy", "")) == LAIB_MANAGED_MARKER:
            del servers[plan.mcp_tool_prefix]
            changed = True
    if not changed:
        return
    if what_if:
        print(f"Would remove managed MCP entry: {path}")
        return
    backup_file(path)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Removed managed MCP entry: {path}")


def backup_file(path: Path) -> None:
    if not path.is_file():
        return
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = path.with_name(f"{path.name}.bak-{stamp}")
    shutil.copy2(path, backup_path)


if __name__ == "__main__":
    raise SystemExit(main())
