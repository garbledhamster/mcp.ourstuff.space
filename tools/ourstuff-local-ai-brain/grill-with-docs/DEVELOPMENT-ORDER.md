# Development Order

## Current slice

Update the Local AI Brain deploy script so the root-level commander stays at `localaibrain.py`, while Local AI Brain-owned install files live under a root-level `localaibrain/` install container.

## Order

1. Keep `localaibrain.py` at the installed project root for a simple PM-user entry point.
2. Put Local AI Brain package code, runtime state, MCP files, plans, and future project-management state under `localaibrain/`.
3. Keep external host integration files where the host tools require them, but point their commands and environment variables into `localaibrain/`.
4. Add conservative migration from the old scattered layout into the install container.
5. Verify with unit tests plus a smoke deploy/run/doctor check before pushing.

## Later slices

1. Add Brain Issues as first-class SQLite records for agent project management.
2. Add Brain Reviews as a top-level approval/rejection queue.
3. Adapt PRD and issue-generation workflows to write to Local AI Brain instead of Git-only issue files.
