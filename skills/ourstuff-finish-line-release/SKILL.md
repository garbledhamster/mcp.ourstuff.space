---
name: Ourstuff Finish Line Release
description: Runs and interprets the Ourstuff ready, publish, release, and handoff checks. Use when the user asks to check, publish, release, hand off, leave ourstuff.space ready, or verify final readiness.
---

# Ourstuff Finish Line Release

## Scope

Use this in `C:\Github\ourstuff.space` when work should be left ready for GitHub Pages or handed off. Read `LLM.md` first and preserve unrelated uncommitted changes.

Do not claim commit, push, publish, or deployment unless that action actually ran or was verified live.

## Standard Path

From the repo root, run the repo-local ready script:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\.github\github-ready.ps1
```

For a fast syntax smoke while debugging only:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\.github\github-ready.ps1 -SkipUtilityChecks
```

The full ready path should cover:

- `node --check .firebase\index.js`
- `node --check assets\js\pyxdia.js`
- `node --check assets\js\app.js`
- `node .github\pyxdia-smoke.mjs`
- `.obsidian\obsidian-plugin` `npm test` and `npm run check`
- utility-belt `static-site-ready`
- utility-belt `github-release-handoff`

## Utility Belt Fallback

If the ready script cannot run the utility checks, inspect or run the tools directly from:

```text
C:\Codex\codex_utility_belt\utility-belt\scripts\static-site-ready.ps1
C:\Codex\codex_utility_belt\utility-belt\scripts\github-release-handoff.ps1
```

Use artifacts under `artifacts\utility-belt\` as evidence, not vibes.

## Known Stale Path Guard

`.firebase\index.js` is the Firebase Functions source of truth. If older docs, scripts, or comments mention `functions\index.js`, treat that as a stale path or mismatch warning and report it instead of silently validating the wrong file.

## Handoff

Summarize the final state with command results, generated artifact paths, dirty files, and the exact next human action. If Git is missing from PATH, use GitHub Desktop's embedded Git or file/artifact evidence, and say which path was used.
