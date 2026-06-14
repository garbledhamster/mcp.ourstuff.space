from __future__ import annotations

import os
import sys
from pathlib import Path


INSTALL_CONTAINER = Path(__file__).resolve().parents[1]
PROJECT_ROOT = INSTALL_CONTAINER.parent
SCRIPTS_DIR = INSTALL_CONTAINER / "scripts"
os.environ["PYTHONPATH"] = str(SCRIPTS_DIR) + os.pathsep + os.environ.get("PYTHONPATH", "")
os.environ["LOCAL_AI_BRAIN_HOME"] = str(INSTALL_CONTAINER / "brain")
os.environ["LOCAL_AI_BRAIN_PROJECT_ROOT"] = str(PROJECT_ROOT)
os.environ["LOCAL_AI_BRAIN_MCP_TOOL_PREFIX"] = "ouradmin.localaibrain"
os.environ["LOCAL_AI_BRAIN_MCP_SCOPE_DESCRIPTION"] = "Project-local Local AI Brain"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from local_ai_brain.project_mcp import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
