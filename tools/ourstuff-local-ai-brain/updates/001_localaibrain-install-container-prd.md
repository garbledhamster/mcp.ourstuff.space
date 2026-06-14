# PRD: Local AI Brain Install Container

Status: ready-for-agent

## Problem Statement

Local AI Brain currently installs its project-owned files across several root-level folders, including package code, runtime state, MCP files, and plans. That makes the project root feel cluttered and makes the brain harder to understand, move, back up, or remove as one coherent Agent Workspace.

The user wants the root-level Commander to stay simple, while the rest of the Local AI Brain payload lives inside one root-level `localaibrain` Install Container. The deeper product direction is a portable project brain that local agents can use for memory, project management, approvals, rejections, and future context without requiring extra infrastructure.

## Solution

Keep `localaibrain.py` at the installed project root as the PM User entry point. Move Local AI Brain-owned install artifacts into a project-root `localaibrain` directory. Generated host integration files remain where their host tools require them, but all generated commands, environment variables, MCP adapters, and registry files point into the Install Container.

The deploy command should conservatively migrate old scattered installs. If an old Local AI Brain-owned root folder exists and the matching new container path does not exist, move it into `localaibrain`. If both old and new paths exist, leave both alone and warn instead of guessing how to merge.

## User Stories

1. As a PM User, I want `localaibrain.py` to remain at the project root, so that I can run the brain without learning an internal folder structure.
2. As a PM User, I want Local AI Brain files grouped in a `localaibrain` folder, so that my project root stays understandable.
3. As a PM User, I want existing scattered installs to migrate automatically when safe, so that I do not need to clean up folders manually.
4. As a PM User, I want unsafe migrations to warn instead of overwriting, so that existing memory is not lost.
5. As a PM User, I want the Brain UI to remain available, so that I can inspect or correct memories when needed.
6. As a PM User, I want generated instructions to point to the new folder layout, so that agents use the correct brain without extra setup.
7. As an agent orchestrator, I want MCP registrations to point into the Install Container, so that tool calls keep working after the layout change.
8. As an agent orchestrator, I want runtime state to live under the Install Container, so that the project brain is portable.
9. As an agent model, I want a stable package path for Local AI Brain commands, so that direct Python commands and MCP commands resolve the same brain.
10. As an agent model, I want plans and artifacts grouped with the brain, so that project-management context is near the memory store.
11. As a maintainer, I want the installer layout expressed through helper functions, so that future paths do not drift back into scattered root folders.
12. As a maintainer, I want tests around generated paths, so that future edits do not silently break installed brains.
13. As a maintainer, I want tests around conservative migration, so that old installs upgrade predictably.
14. As a maintainer, I want rollback safety checks to still apply, so that the command never removes unrelated project files.
15. As a maintainer, I want the deploy registry to continue resolving old and new deployments, so that optimize and index commands keep working.
16. As a maintainer, I want generated agent skill metadata to remain where host tools expect it, so that tool discovery is not broken by the container change.
17. As a maintainer, I want flat markdown updates for this work, so that development is tracked before implementation.
18. As a future PM User, I want Brain Issues to become first-class brain records, so that project management can happen through Local AI Brain.
19. As a future PM User, I want Brain Reviews to become a top-level queue, so that approvals, rejections, and requested revisions are visible.
20. As a future agent orchestrator, I want pending Brain Reviews surfaced by command and UI, so that human approval is not hidden in chat history.

## Implementation Decisions

- The Install Container is named `localaibrain`.
- The Commander remains a root-level script named `localaibrain.py`.
- Local AI Brain-owned package files, runtime memory, MCP files, plans, and future PM state belong under the Install Container.
- Host integration files such as agent skill folders and global MCP config files stay in their host-required locations.
- Generated host integration files must point their command arguments and environment variables into the Install Container.
- Existing deploy behavior should be preserved from the PM User perspective: deploy, run, terminal, UI, doctor, optimize, index, and rollback should still be reachable through the Commander.
- Migration should be conservative. Move old root-level Local AI Brain-owned folders only when the destination does not already exist.
- If old and new paths both exist, do not merge automatically. Warn and leave both in place.
- SQLite remains the canonical Brain Memory store. Flat files are artifacts, exports, PRDs, grill docs, or inspection material.
- Brain Issues and Brain Reviews are future first-class SQLite-backed workflows, not part of this install-layout slice.

## Testing Decisions

- Test installer behavior at the existing deploy-planning and install-package seam, because that is where paths are already assembled.
- Test generated path behavior by asserting the plan points package code, runtime data, MCP registry, MCP adapter, and plans into the Install Container.
- Test conservative migration with temporary directories that simulate old scattered installs.
- Test that migration does not overwrite when both old and new paths exist.
- Test that installed package refresh still preserves destination-only files.
- Smoke test a real deploy into a temporary project directory, then run doctor or an equivalent read-only command through the root Commander.
- Avoid tests that assert internal implementation details beyond public path contracts and externally visible deploy behavior.

## Out of Scope

- Implementing Brain Issues.
- Implementing Brain Reviews.
- Implementing Gitea synchronization.
- Rebuilding the Brain UI.
- Changing the SQLite schema for project management.
- Migrating host-tool global configuration formats beyond updating generated paths.
- Creating a full flat-file memory system.

## Further Notes

This PRD intentionally keeps the current slice narrow. The install-layout change is the portability foundation. Brain Issues, Brain Reviews, approval queues, and PRD-to-brain workflows should follow as separate slices after deploy/run behavior is proven with the new container layout.
