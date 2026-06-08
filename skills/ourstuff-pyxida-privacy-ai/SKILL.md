---
name: Ourstuff PYXIDA Privacy AI
description: Guides PYXIDA, AI Brain, LLM prompt, memory, note metadata context, and backend AI route changes with Ourstuff privacy rules. Use when changing PYXIDA, AI prompts, OpenRouter calls, memory, note metadata context, PII scrubbing, AI settings, or backend AI routes.
---

# Ourstuff PYXIDA Privacy AI

## Scope

Use this in `C:\Github\ourstuff.space` for PYXIDA, AI Brain, LLM, prompt, memory, and AI gateway work. Read `LLM.md`, `.llm_brain/pyxida/PYXIDA_PENPAL_DEV.md`, and `.llm_brain/security/DATA_PII_AI_SECURITY_STANDARD.md` before editing.

## Source Files

- `.firebase\index.js`: backend AI/PYXIDA routes, PII handling, provider calls, queue processing.
- `assets/js/pyxdia.js`: frontend PYXIDA helper.
- `assets/js/app.js`: sidebar, Settings, drafts, state, and UI rendering.
- `.llm_brain/security/DATA_PII_AI_SECURITY_STANDARD.md`: privacy and secret rules.
- `.llm_brain/pyxida/PYXIDA_PENPAL_DEV.md`: product and route contract.

## Privacy Rules

- No provider keys in frontend files.
- OpenRouter and other model providers are backend-only.
- Browser code may collect drafts and selected note references, but it must not call an LLM provider directly.
- Default note context is metadata-only. Do not send raw note bodies unless the user explicitly selected that behavior and the backend minimizes it.
- Scrub inputs, block secrets/cards/tokens, rate-limit signed-in users, and scan model output before storage or display.
- Logs must not contain raw prompts, note bodies, secrets, bearer tokens, full profiles, payment payloads, or provider responses with private content.
- PYXIDA output renders as plain text with escaping and whitespace preservation, not markdown.

## Checks

```powershell
node --check .firebase\index.js
node --check assets\js\pyxdia.js
node --check assets\js\app.js
node .github\pyxdia-smoke.mjs
```

For UI changes, serve locally and prove: dashboard to sidebar/menu to PYXIDA, draft save, send or blocked send state, pending/completed state, Settings PYXIDA tab, and reset/refresh behavior.

## Review Points

- Auth token flow comes from Firebase Auth and is not logged.
- Backend route names and Firestore user scoping match the current contract.
- Missing provider config fails closed with a safe message.
- Memory compaction stores durable conclusions, not raw private transcripts.
