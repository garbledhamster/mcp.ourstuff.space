---
name: Ourstuff Theme Adapter
description: Maintains or ports the Ourstuff theme engine, named themes, tokens, accessibility color adapters, and planned YAML theme-adapter workflows. Use when changing APP_THEMES, themeSystem.js, theme-contract.css, colorblind mode, theme tokens, Settings theme switching, scanning themed UI surfaces, or copying the theme engine into another app.
---

# Ourstuff Theme Adapter

## Scope

Use this for theme work in `C:\Github\ourstuff.space` or when copying its theme engine elsewhere. Read `LLM.md` and `.llm_brain/dev reference/THEMING_DEV.md` first.

## Source Files

- `assets/js/themeSystem.js`: portable engine.
- `assets/js/app.js`: Ourstuff `APP_THEMES`, `THEME_FONT_SETS`, Settings wiring, and app-specific theme calls.
- `assets/css/theme-contract.css`: portable token contract helpers.
- `assets/css/app.css`: Ourstuff selector adapter.
- `.github/theme-adapter-coverage.mjs`: self-updating adapter coverage checker.
- `.llm_brain/dev reference/THEME_ADAPTER_COVERAGE.json`: generated component coverage inventory.
- `references/theme-adapter-yaml-v1.md`: planned portable YAML interface for scanning UI surfaces and applying theme adapters.

## Rules

- Add or edit named Ourstuff themes in `APP_THEMES`.
- Keep app selectors pointed at tokens instead of hardcoded colors when touching themed UI.
- Use `themePreviewStyle(theme)` for chooser swatches.
- Keep colorblind mode as the `ourstuff.colorMode.v1` adapter with `.theme-accessibility-colorblind` hooks.
- Add app surfaces to the generic theme selector groups before creating special-case theme CSS.
- Use `:root.theme-consolas` only for console-theme behavior the generic tokens cannot express.
- Avoid one-note palette regressions; the app should not collapse into one dominant hue family after a theme change.
- Run the coverage checker before and after adapter work. Use its `requiredMissing` and `highConfidenceMissing` lists as the work queue.
- Do not manually edit `.llm_brain/dev reference/THEME_ADAPTER_COVERAGE.json`; update CSS, then regenerate it.
- The checker should skip rewriting the generated JSON when coverage content is unchanged, so repeated ready checks stay clean.
- Preserve dynamic per-item colors such as theme previews, picker swatches, chart segments, identity colors, and thought/card colors. Exempt them in the checker only when they intentionally render data or candidate-theme colors.

## Coverage Flow

1. Run `node .\.github\theme-adapter-coverage.mjs --update --strict`.
2. Open `.llm_brain/dev reference/THEME_ADAPTER_COVERAGE.json`.
3. For each required missing class, either point the base rule at existing tokens or add the selector to the generic palette/consolas adapter groups.
4. Use `:root.theme-consolas` only when Consolas needs separate contrast, outline, or terminal behavior.
5. Rerun the checker until `requiredMissingCount` and `highConfidenceMissingCount` are `0`.

## Porting Flow

1. Copy `assets/js/themeSystem.js`.
2. Optionally copy `assets/css/theme-contract.css`.
3. Create a local theme catalog shaped like `APP_THEMES`.
4. Replace literal surface, card, field, tab, selected-row, and hover colors with theme tokens.
5. Wire startup and Settings changes through `loadTheme`, `saveTheme`, and `applyThemeVariables` or `createThemeController`.

## YAML Adapter Flow

Use this only when the user asks to generalize the Ourstuff theme adapter, scan UI elements, or apply themes with simple YAML.

1. Read `references/theme-adapter-yaml-v1.md`.
2. Treat `C:\Github\ourstuff.space` as the reference implementation for a good theme.
3. Planned command sequence:
   - `Scan-ThemeSurfaces.ps1 -RepoPath <path> -OutFile <json>`
   - `New-ThemeAdapterYaml.ps1 -ScanPath <json> -OutFile <yaml>`
   - `Apply-ThemeAdapter.ps1 -RepoPath <path> -ThemeYaml <yaml>`
4. Scanner output should capture selector role, size band, nesting depth, theme-token coverage, and likely exemptions.
5. YAML should stay simple: tokens, surface groups, selector adapters, exemptions, and verification commands.

## Verify

```powershell
node .\.github\theme-adapter-coverage.mjs --update --strict
node --check .\assets\js\themeSystem.js
node --check .\assets\js\app.js
python -m http.server 4173
```

In Settings, switch through changed themes and colorblind mode. Check dashboard controls, cards, forms, selected states, hover states, swatches, text contrast, and the Consolas theme.
