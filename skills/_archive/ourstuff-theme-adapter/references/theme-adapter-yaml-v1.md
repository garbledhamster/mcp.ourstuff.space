# Theme Adapter YAML V1

This is the planned portable interface for scanning a UI, drafting a theme adapter, and applying token-based themes.

## Commands

`Scan-ThemeSurfaces.ps1 -RepoPath <path> -OutFile <json>`

- Inventories UI surfaces, selectors, size bands, nesting depth, and current token coverage.
- Reads source files only; it should not modify the target repo.
- Emits JSON grouped by component role and selector confidence.

`New-ThemeAdapterYaml.ps1 -ScanPath <json> -OutFile <yaml>`

- Drafts a simple YAML adapter from a scan.
- Keeps exemptions explicit so data-driven colors, swatches, previews, charts, and identity colors are not themed accidentally.

`Apply-ThemeAdapter.ps1 -RepoPath <path> -ThemeYaml <yaml>`

- Applies token and selector-adapter changes from YAML.
- Must produce a reviewable diff and leave verification commands for the repo.

## YAML Shape

```yaml
theme:
  name: example-theme
  source: ourstuff.space

tokens:
  surface: "#ffffff"
  surfaceRaised: "#f7f8fa"
  text: "#1f2937"
  textMuted: "#64748b"
  accent: "#2563eb"
  border: "#d8dee9"

surfaceGroups:
  cards:
    role: container
    size: medium
    nestingMax: 2
    tokens:
      background: surfaceRaised
      color: text
      borderColor: border

selectorAdapters:
  ".card, .panel":
    group: cards
    confidence: high

exemptions:
  ".theme-preview-swatch":
    reason: candidate theme color preview

verification:
  commands:
    - node .\.github\theme-adapter-coverage.mjs --update --strict
    - node --check .\assets\js\themeSystem.js
```

## Reference Behavior

Use `C:\Github\ourstuff.space` as the reference implementation for:

- `assets\js\themeSystem.js`
- `assets\css\theme-contract.css`
- named theme catalogs shaped like `APP_THEMES`
- colorblind mode and accessibility selector adapters
- coverage checks for missing or hardcoded themed surfaces

