---
name: Ourstuff Firebase Dotfolder
description: Guides Firebase Functions, Firestore rules, Storage rules, and Firebase deploy-config work in the Ourstuff dot-folder layout. Use when work touches .firebase, Firebase Functions, Firestore rules, Storage rules, Auth, deploy config, or backend route wiring.
---

# Ourstuff Firebase Dotfolder

## Scope

Use this in `C:\Github\ourstuff.space` for Firebase backend and rules work. Read `LLM.md`, then the narrow Firebase/security brain docs it points to.

Firebase config lives under `.firebase`, not the repo root.

## Current Layout

```text
.firebase\.firebaserc
.firebase\firebase.json
.firebase\firestore.rules
.firebase\firestore.indexes.json
.firebase\storage.rules
.firebase\storage.cors.json
.firebase\index.js
.firebase\package.json
```

`.firebase\index.js` is the Functions source of truth. Treat `functions\index.js` as a stale path warning unless current repo files prove otherwise.

## Checks

Run backend syntax after touching Functions:

```powershell
node --check .firebase\index.js
```

Inspect dependencies and scripts before changing package behavior:

```powershell
Get-Content .firebase\package.json
```

Review rules and config with the exact files involved:

```powershell
Get-Content .firebase\firestore.rules
Get-Content .firebase\storage.rules
Get-Content .firebase\firebase.json
```

If using Firebase CLI, run from a workflow that knows config is in `.firebase`, or pass the config path explicitly. Do not move config files to the repo root as a shortcut.

## Safety Rules

- Never place provider keys, service account JSON, tokens, or private user data in frontend files.
- Do not log raw prompts, note bodies, API keys, bearer tokens, payment payloads, or full profiles.
- Keep user data scoped by Firebase Auth UID and deny client writes to roles, admin flags, paid status, and entitlement truth.
- Prefer narrow rule/config diffs and report any deploy commands separately from local validation.
