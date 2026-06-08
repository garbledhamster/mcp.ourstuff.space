---
name: Ourstuff Obsidian Sync
description: Validates and changes the Ourstuff Obsidian compendium sync plugin and related live sync checks. Use when changing .obsidian, obsidian-plugin, compendium sync, sync-core behavior, install helpers, active edit protection, or Obsidian live smoke checks.
---

# Ourstuff Obsidian Sync

## Scope

Use this in `C:\Github\ourstuff.space` for Obsidian plugin, compendium sync, install helpers, and sync smoke work. Read `LLM.md` and `.llm_brain/obsidian/OBSIDIAN_SYNC.md` before editing.

## Current Layout

```text
.obsidian\obsidian-plugin\main-source.cjs
.obsidian\obsidian-plugin\sync-core.cjs
.obsidian\obsidian-plugin\main.js
.obsidian\obsidian-plugin\manifest.json
.obsidian\obsidian-plugin\package.json
.obsidian\obsidian-plugin\tests\
.obsidian\check-obsidian-sync.ps1
.obsidian\obsidian-sync-smoke.ps1
.obsidian\install-obsidian-plugin.ps1
.obsidian\obsidian-sync-ready.ps1
```

Edit `main-source.cjs` and `sync-core.cjs`; `main.js` is the generated bundle.

## Local Checks

```powershell
Push-Location .\.obsidian\obsidian-plugin
npm test
npm run check
Pop-Location
```

`npm run check` should build, syntax-check `main.js`, `main-source.cjs`, and `sync-core.cjs`, then run bundle and load smoke tests.

For broader sync readiness:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\.obsidian\obsidian-sync-ready.ps1
```

## Live And Install Checks

Use live smoke only when the user provides or already has a local API key:

```powershell
$env:OURSTUFF_OBSIDIAN_API_KEY = "<local key>"
powershell -NoProfile -ExecutionPolicy Bypass -File .\.obsidian\obsidian-sync-smoke.ps1
Remove-Item Env:\OURSTUFF_OBSIDIAN_API_KEY
```

Install through the repo helper or utility-belt path; after reinstall, Obsidian may need plugin disable/enable or restart to load the new bundle.

## Behavioral Guards

- Preserve active edit protection: pull sync must not overwrite the currently edited note during the protection window.
- Treat plain Markdown files inside synced compendium folders as section candidates.
- Keep backend sync behavior client-agnostic; do not make server rules Obsidian-only.
- Do not log API keys, bearer tokens, note bodies, or long private values.
