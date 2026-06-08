---
name: Ourstuff Static Frontend Checks
description: Validates static frontend changes in the Ourstuff GitHub Pages app. Use when work touches C:\Github\ourstuff.space index.html, assets/js/*, assets/css/*, UI behavior, mobile layout, browser modules, dashboard shell, or Settings.
---

# Ourstuff Static Frontend Checks

## Scope

Use this for `C:\Github\ourstuff.space` frontend work. The app is a static GitHub Pages-compatible site with browser ES modules and no root build step. Start by reading `LLM.md`, then only the narrow `.llm_brain/` files relevant to the change.

Preserve unrelated dirty work, especially existing edits in `assets/js/app.js` and `assets/css/app.css`.

## Standard Path

1. Inspect the touched files and the exact user flow they affect.
2. Run syntax checks for touched JavaScript modules:

```powershell
node --check assets\js\app.js
node --check assets\js\pyxdia.js
node --check assets\js\cloud.js
```

Use the narrower touched module list when appropriate, but include `assets\js\app.js` for UI/state changes.

3. Serve from the repo root; do not double-click `index.html`:

```powershell
python -m http.server 4173
```

Open `http://localhost:4173`. If the port is busy, use a nearby port and report the exact URL.

4. Prove the real flow in a browser. Check console errors, visible state, persistence, and the specific interaction the user named.
5. For visual or layout changes, capture desktop and mobile proof. Check common mobile widths such as 360px and 390px.

## Mobile And Shell Checks

- No horizontal overflow.
- Text fits controls and cards without clipping.
- Compact date or number labels stay on their own row when that pattern applies.
- Mobile cards keep the same visual order as desktop unless the task explicitly changes it.
- Dashboard chart switchers keep stable width inside their wrapper.
- Nested scroll and header snap behavior use deliberate handoff; child scrollers should not jitter the outer shell at their boundaries.

## Reporting

Report the exact files checked, commands run, local URL, browser flow, viewport sizes, and any skipped checks with the reason. If the user asks for release readiness, switch to `ourstuff-finish-line-release`.
