# Local AI Brain Install Container TDD Report

Status: implemented-and-verified
Date: 2026-06-13

## Shipped

- Fresh deploy planning now keeps the Commander at project root as `localaibrain.py`.
- Local AI Brain-owned install files now live under `localaibrain/`:
  - package and adapter: `localaibrain/scripts/`
  - runtime state: `localaibrain/brain/`
  - plans: `localaibrain/plans/`
  - MCP registry: `localaibrain/mcp/`
- Generated MCP adapter and registry paths point into the Install Container.
- Generated adapter exports `LOCAL_AI_BRAIN_PROJECT_ROOT` so package MCP defaults still use the project root.
- Legacy scattered installs migrate conservatively when safe.
- Migration conflicts warn and preserve old and new paths without overwriting.
- Deploy registry resolution supports new container entries and legacy adapter/registry entries.
- Rollback removes managed MCP files without removing unrelated project files.

## Verification

- `python -B -m unittest discover -s tests`
  - Result: 18 tests, OK.
- Scratch deploy smoke with temp deploy registry:
  - `deploy_result=0`
  - all expected Commander, package, database, registry, adapter, and temp deploy-registry files existed.
- Scratch doctor smoke:
  - `doctor_result=0`
- `git diff --check` on changed files:
  - no whitespace errors; only Git line-ending warnings.

## Notes

Brain Issues and Brain Reviews remain out of scope for this slice.
