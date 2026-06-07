# Changelog

Notable Local AI Brain changes are recorded here for users and future agents.

## 2026-06-05 - Local AI Brain V0

### Added

- Created the first portable Local AI Brain kit: a local-first memory utility for coding agents where files remain the source of truth and SQLite is a rebuildable index.
- Added a Python package and CLI with commands for initialization, health checks, run tracking, artifact and ticket recording, event recording, search, context-pack generation, index rebuilds, Codex session audit, and Codex title distillation.
- Added a deterministic capture pipeline: raw input is scrubbed, distilled, classified, stored as a file artifact, and indexed through SQLite.
- Added SQLite FTS5-backed local search without requiring an external `sqlite3` executable.
- Added cross-platform install support through `install.py`, including dry-run installation with `--what-if`, forced refresh with `--force`, and `--no-doctor` for environments where Distill is not ready yet.
- Added thin Windows and macOS/Linux wrapper scripts while keeping Python as the primary interface.
- Added a dependency-free stdio MCP server that wraps the CLI for agent hosts that can install or call local MCP tools.
- Added Codex chat title distillation. It reads local Codex thread metadata and rollout logs, proposes concise dated titles, and can apply title updates with backups and audit logs.
- Added tests for core capture/index behavior, installer planning, MCP command behavior, and Codex title distillation.

### Packaging

- Added a local publish script for preparing a shareable Git copy of the kit.
- Kept runtime memory data outside the shipped tool folder so upgrades do not overwrite a user's local memories.
- Excluded local-only files and generated data from the shareable copy, including private publishing notes, deploy helpers, `.opencode`, `.git`, `__pycache__`, `.pytest_cache`, and compiled Python files.
- Added public README and MCP setup documentation aimed at users installing the kit from a copied folder, Git checkout, or MCP-assisted setup.

### Product Direction

- Chose a deliberately simple V0 direction: no cloud, no required server, no vector database, and no hidden agent runtime.
- Kept SQLite as the local index/cache rather than the source of truth.
- Kept memory records inspectable and file-backed so users can see where their memory is stored.
- Preferred a small CLI contract and context-pack retrieval over more complex automatic memory systems.

### Planned

- Add a deterministic `sync-context` importer that can scan a user's existing safe local context and load missing records into Local AI Brain without runtime LLM usage.
- Keep raw Codex rollout ingestion opt-in and quarantine scrub warnings before indexing.
- Use small LLM passes only after scripted evidence collection, mainly to turn verified evidence into readable summaries.

### Verified

- Unit tests passed for the core package and installer behavior.
- Python compile checks passed for the package and tests.
- Windows and macOS installer dry-runs passed.
- Local doctor checks passed in the development environment.
- The shareable Git copy and ZIP package were scanned to confirm that private deploy helpers, generated caches, local-only notes, and personal path markers were not included.
