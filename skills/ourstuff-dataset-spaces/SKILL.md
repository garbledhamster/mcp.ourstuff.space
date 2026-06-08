---
name: Ourstuff Dataset Spaces
description: Adds or updates Ourstuff dataset spaces with scoped local/cloud storage, defaults, sharing roles, Settings controls, and validation. Use when adding Personal/Work/Family/Couples/Friends/Coworkers-style spaces in `C:\Github\ourstuff.space`.
---

# Ourstuff Dataset Spaces

Use this in `C:\Github\ourstuff.space` when adding or changing a dataset space.

## Required Reads

- `LLM.md` first.
- App wording and storage vocabulary: `.llm_brain/dev reference/APP_LINGO.md`.
- Cloud paths and app ids: `.llm_brain/ourstuff.space/OURSTUFF_CLOUD_CONTEXT.md`.
- If sharing, roles, Auth, rules, Functions, media, Trash, or Cloud access changes: `.llm_brain/core systems/FIREBASE_MCP_CODEX.md`, `.llm_brain/security/DATA_PII_AI_SECURITY_STANDARD.md`, `.firebase/firestore.rules`, `.firebase/storage.rules`, `.firebase/index.js`.
- If PYXIDA changes: `.llm_brain/pyxida/PYXIDA_PENPAL_DEV.md`.
- If Obsidian behavior changes: `.llm_brain/obsidian/OBSIDIAN_SYNC.md`.

## Space Registry Checklist

For each space, define or verify:

- `id`: stable local key segment such as `personal`, `work`, or `family`.
- `label`: visible dataset name.
- `cloudAppId`: Firebase app dataset id such as `ourstuff-main-family`.
- Dashboard display labels for internal areas `Mind`, `Body`, `Spirit`, `Life`.
- Default thought orbs, goal orbs, dashboard identity, and empty artifact/log state.
- Sharing flag and role model: owner, editor, reader, or local-only.
- PYXIDA behavior: local-only, owner-scoped, shared, author attribution, reader/editor gates.
- Shared messaging behavior: direct one-to-one Pen Pal letters only, with no group chat, CC, or BCC.
- Obsidian behavior: disabled, owner-only, shared, or unchanged.

## Implementation Checklist

- Add the space to a single registry rather than branching on one named space.
- Scope local storage keys, last-sync markers, demo state, Space PIN, and IndexedDB/media databases by space id.
- Keep Personal migration compatible with legacy unscoped keys.
- Route Cloud metadata, artifact docs, media paths, Trash, and PYXIDA docs through the active space's `cloudAppId` and owner uid.
- For shared messaging, reuse `pyxdiaThreads` and `pyxdiaLetters` with `recipientType`:
  - `pyxdia` keeps the AI queue/provider path.
  - `family`/future shared-space people use `fromUid/fromLabel`, `toUid/toLabel`, `participantUids`, `readBy`, and immediate `delivered` state.
- Add or preserve unread summary behavior by space id so `dashboardSpaceSwitcherHtml()` can show an unread bubble for the affected space.
- Keep the editor recipient UI as a radio choice between PYXIDA and the current shared-space type, with people inside a dropdown. If no people exist, show space-specific invite copy and link to the invite controls.
- Add Functions allowlist entries for new Cloud app ids.
- Update Firestore and Storage rules for same-owner access and any shared member access.
- Add Settings controls for create, restore/load, sync, import, export, clear, delete, PIN, and sharing/member management.
- Gate UI actions by role: owner can manage defaults/members/cloud delete/import/trash hard delete; editor can edit/sync/upload/soft-delete/restore; reader can read/export only.
- Ensure import/export excludes local-only PIN hashes and unlock sessions.
- Keep clear/delete copy and confirmation text specific to the active space.

## Validation Checklist

- Verify this skill exists and has valid frontmatter/description.
- Run syntax checks for touched browser modules and `.firebase/index.js`.
- Browser smoke Personal migration, existing Work isolation, the new space defaults/labels, PIN, import/export, clear/load/sync/delete copy, and role-disabled controls.
- Role smoke owner/editor/reader access, removed-member loss of access, and local joined-cache clearing.
- Media smoke Cloud paths under `/users/{ownerUid}/apps/{cloudAppId}/media/...`.
- PYXIDA/shared messaging smoke if changed: draft/send/retry/settings, reader read-only, author attribution, owner/admin entitlement check, acting-user rate limits, direct-letter From/To labels, unread summary/bubble, participant-only read filtering, and thread-read behavior.
- Final check:
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\.github\github-ready.ps1`
