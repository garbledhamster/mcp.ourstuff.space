---
name: Projects Ourstuff Modules
description: Builds and reviews module tracking surfaces for C:\Github\projects.ourstuff.space. Use when adding project modules, moduleizer JSON, manual tracking fields, module settings GUIs, external-system tracking, or handoff-ready module-building instructions for non-coders.
---

# Projects Ourstuff Modules

## Quick Start

1. Work from `C:\Github\projects.ourstuff.space`.
2. Run `.\scripts\Inspect-ProjectsOurstuffModules.ps1` from this skill to map the current module system.
3. Read `references/FIELD_MODEL.md` and choose fields for the target system.
4. Implement the smallest module change that preserves local persistence, export/import, and non-coder manual entry.

## Current Module Contract

The app is currently a single-file static app in `index.html`.

- Built-in modules live in `moduleDefinitions`.
- App-level custom module metadata is stored in `state.appSettings.customModules`.
- Project-level module state lives at `project.modules[moduleId]`.
- Each module record currently stores `enabled`, `configured`, `settings`, `secretVault`, `lastConfirmed`, and `lastSettingsUpdate`.
- Current custom modules only support metadata: `id`, `icon`, `name`, `desc`, `visibleData`, and `controlledActions`.
- Current settings fields are mostly common fields (`externalName`, `externalUrl`, `externalId`) plus hardcoded Planner/Calendar settings.

Treat "add a module" as two possible jobs:

- Metadata-only module: add or generate moduleizer JSON.
- Tracking module: extend the app so the module has structured manual fields in `settings`, visible GUI controls, normalization, and saved/exported values.

## Workflow

1. Inspect first:
   - Run the audit script.
   - Search `index.html` for `moduleDefinitions`, `normalizeCustomModule`, `normalizeAppSettings`, `getModuleDefinitions`, `defaultModuleSettings`, `normalizeModules`, `renderModuleSettings`, `renderModulesPopover`, `renderModulePanel`, and form/action handlers.
2. Define the module:
   - State the external system or manual workflow being tracked.
   - Pick a stable `id`, visible name, icon, description, `visibleData`, and `controlledActions`.
   - Decide whether it is metadata-only or needs structured tracking fields.
3. Derive manual fields:
   - Prefer fields a non-coder can find in the target system UI.
   - Include enough identifiers to reconnect data later without requiring API access.
   - Do not ask users to paste raw secrets unless the app already encrypts the value and the workflow is explicitly local testing.
   - Use `references/FIELD_MODEL.md` for baseline fields and system-specific candidates.
4. Wire the app:
   - Add defaults/sanitization in `defaultModuleSettings` or a module-field schema helper.
   - Render fields in `renderModuleSettings`.
   - Save submitted values in the `save-module-settings` submit handler, adding that handler first if it is missing.
   - Keep `normalizeModules` backward compatible with old exports.
   - Preserve `project.updatedAt`, `lastSettingsUpdate`, `lastConfirmed`, import/export, and localStorage behavior.
5. Make the module handoff-ready:
   - Provide the moduleizer JSON when metadata-only is enough.
   - For tracking modules, document the GUI fields, where a non-coder finds each value, and what "confirmed working" means.
   - Avoid private paths, credentials, raw PII, and unverifiable claims.

## Verification

Run checks appropriate to the edit:

- `node --check index.html` will not work for full HTML; instead extract or inspect scripts when needed.
- Use a local static server and browser smoke for GUI changes.
- Test add project, enable module, save module settings, reload, export, import, and confirm the fields survive.
- Check desktop and narrow mobile widths for module popover/settings overflow.
- Run `git diff --check`.

## Output Format

When reporting a module review or implementation, include:

- Module system summary.
- Proposed fields grouped by purpose.
- Files and functions changed.
- Verification performed.
- Remaining risks or missing evidence.
