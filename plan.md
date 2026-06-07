# mcp.ourstuff.space Plan

## Purpose

Make `mcp.ourstuff.space` the public entry point for Ourstuff MCP tools and skills. A user should be able to visit the site and understand how to use the MCP from a CLI agent, a desktop agent, or a browser-based agent without needing to find separate GitHub repositories first.

## Migrated Source Layout

- `skills/` contains the former `C:\Github\skills` working tree content, excluding ignored generated files and local scratch state.
- `tools/` contains the former `C:\Github\tools` working tree content, excluding nested Git metadata.
- `tools/local-ai-brain` remains the shareable beta copy of Local AI Brain. The alpha working copy is still `C:\Users\jrice\.agents\tools\local-ai-brain` unless a later plan explicitly changes that release-channel model.

## Product Direction

- Build a front end at `mcp.ourstuff.space` that explains and configures the Ourstuff MCP for real users.
- Provide install paths for CLI agents, desktop agents, and browser agents.
- Keep downloadable or copyable config snippets close to the exact tool or skill they configure.
- Make the site the canonical public navigation surface for skills, tools, docs, and MCP setup.

## Migration Checklist

- [x] Create this root plan in `mcp.ourstuff.space`.
- [x] Move tracked and unignored current `C:\Github\skills` content into `skills/`.
- [x] Move tracked and unignored current `C:\Github\tools` content into `tools/`.
- [ ] Verify migrated package checks from the new paths.
- [ ] Commit and push `mcp.ourstuff.space`.
- [ ] Remove the old local `C:\Github\skills` and `C:\Github\tools` repositories after the destination push succeeds.
- [ ] Delete the old GitHub repositories after the destination push succeeds and local cleanup is complete.

## Verification Targets

- `skills/linear-thinking/scripts/Test-LinearThinkingSkills.ps1`
- `skills/skill-registry-mcp` package checks
- `tools/local-ai-brain` install or test checks
- `git status` confirms old repos are no longer needed only after the destination repo is pushed.

## Cleanup Policy

Do not delete the source repositories until the migrated content is present in `mcp.ourstuff.space`, committed, pushed, and smoke-checked from the new paths. GitHub repository deletion should only target the old `garbledhamster/skills` and `garbledhamster/tools` repositories.
