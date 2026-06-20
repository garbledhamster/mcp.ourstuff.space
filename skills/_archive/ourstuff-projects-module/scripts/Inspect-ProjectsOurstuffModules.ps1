param(
  [string]$RepoPath = "C:\Github\projects.ourstuff.space"
)

$ErrorActionPreference = "Stop"

$indexPath = Join-Path $RepoPath "index.html"
if (-not (Test-Path -LiteralPath $indexPath)) {
  throw "index.html not found at $indexPath"
}

$content = Get-Content -LiteralPath $indexPath -Raw
$modulesPath = Join-Path $RepoPath "assets\js\modules"
$moduleFileContent = ""
if (Test-Path -LiteralPath $modulesPath) {
  $moduleFileContent = Get-ChildItem -LiteralPath $modulesPath -Filter "*.js" -File |
    ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw } |
    Out-String
}
$allSourceContent = "$content`n$moduleFileContent"

function Test-Pattern {
  param([string]$Pattern)
  return [regex]::IsMatch($content, $Pattern)
}

function Test-AnyPattern {
  param([string]$Pattern)
  return [regex]::IsMatch($allSourceContent, $Pattern)
}

$moduleIds = [regex]::Matches($allSourceContent, 'id:\s*"([^"]+)"') |
  ForEach-Object { $_.Groups[1].Value } |
  Where-Object {
    $_ -notin @(
      "storageBanner",
      "allProjectsButton",
      "exportButton",
      "importButton",
      "openProjectDialogButton",
      "importFile"
    )
  } |
  Select-Object -Unique

$checks = [ordered]@{
  "moduleDefinitions" = (Test-Pattern 'const\s+moduleDefinitions\s*=') -or (Test-Pattern 'getBuiltInModuleDefinitions')
  "moduleRegistry" = Test-AnyPattern 'registerBuiltInModule'
  "normalizeCustomModule" = Test-Pattern 'const\s+normalizeCustomModule\s*='
  "normalizeAppSettings" = Test-Pattern 'const\s+normalizeAppSettings\s*='
  "getModuleDefinitions" = Test-Pattern 'const\s+getModuleDefinitions\s*='
  "defaultModuleSettings" = Test-Pattern 'const\s+defaultModuleSettings\s*='
  "normalizeModules" = Test-Pattern 'const\s+normalizeModules\s*='
  "renderModuleSettings" = Test-Pattern 'const\s+renderModuleSettings\s*='
  "renderModulesPopover" = Test-Pattern 'const\s+renderModulesPopover\s*='
  "renderModulePanel" = Test-Pattern 'const\s+renderModulePanel\s*='
  "saveModuleSettingsForm" = Test-Pattern 'data-action="save-module-settings"'
  "saveModuleSettingsHandler" = Test-Pattern 'action\s*===\s*"save-module-settings"'
  "installCustomModuleForm" = Test-Pattern 'data-action="install-custom-module"'
  "installCustomModuleHandler" = Test-Pattern 'action\s*===\s*"install-custom-module"'
  "confirmModuleButton" = Test-Pattern 'data-action="confirm-module"'
  "confirmModuleHandler" = Test-Pattern 'action\s*===\s*"confirm-module"'
}

Write-Output "# projects.ourstuff.space Module System Audit"
Write-Output ""
Write-Output "- Repo: $RepoPath"
Write-Output "- Index: $indexPath"
Write-Output "- Detected possible IDs: $($moduleIds.Count)"
Write-Output ""
Write-Output "## Contract Checks"
Write-Output ""
foreach ($key in $checks.Keys) {
  $status = if ($checks[$key]) { "present" } else { "missing" }
  Write-Output "- ${key}: $status"
}

Write-Output ""
Write-Output "## Known Built-In Module IDs"
Write-Output ""
@(
  "planner",
  "calendar",
  "gantt",
  "kanban",
  "risks",
  "decisions",
  "users",
  "cloudflare",
  "firebase",
  "github",
  "stripe",
  "files",
  "mcp",
  "ourbrain"
) | ForEach-Object {
  $status = if ($moduleIds -contains $_) { "present" } else { "not detected" }
  Write-Output "- ${_}: $status"
}

Write-Output ""
Write-Output "## Implementation Notes"
Write-Output ""
if (-not $checks["saveModuleSettingsHandler"]) {
  Write-Output "- The settings form exists but no save-module-settings handler was detected."
}
if (-not $checks["installCustomModuleHandler"]) {
  Write-Output "- The custom module installer form exists but no install-custom-module handler was detected."
}
if (-not $checks["confirmModuleHandler"]) {
  Write-Output "- The confirm button exists but no confirm-module handler was detected."
}
Write-Output "- Review the findings against local source before making final claims."
