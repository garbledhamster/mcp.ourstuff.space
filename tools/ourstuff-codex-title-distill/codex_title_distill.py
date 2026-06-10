#!/usr/bin/env python3
"""Compatibility launcher for Local AI Brain's Codex title distill command."""

from __future__ import annotations

from pathlib import Path
import sys


LOCAL_AI_BRAIN_ROOT = Path(__file__).resolve().parents[1] / "local-ai-brain"
if str(LOCAL_AI_BRAIN_ROOT) not in sys.path:
    sys.path.insert(0, str(LOCAL_AI_BRAIN_ROOT))

from local_ai_brain.title_distill import main


if __name__ == "__main__":
    raise SystemExit(main())
