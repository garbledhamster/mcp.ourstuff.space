[CmdletBinding()]
param(
  [string]$ApiBase = $env:SKILL_REGISTRY_URL,
  [switch]$SkipTests,
  [switch]$SkipAudit,
  [switch]$SkipMigrations,
  [switch]$SkipDeploy,
  [switch]$Smoke
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

Push-Location $RepoRoot
try {
  if (-not $SkipAudit) {
    npm audit
  }
  npm run build
  if (-not $SkipTests) {
    npm test
  }
  if (-not $SkipMigrations) {
    npm run migrate:remote
  }
  if (-not $SkipDeploy) {
    npm run deploy
  }
  if ($Smoke) {
    if (-not $ApiBase) {
      throw "Set SKILL_REGISTRY_URL or pass -ApiBase before smoke checks."
    }
    & (Join-Path $PSScriptRoot "Invoke-LiveSmoke.ps1") -ApiBase $ApiBase
  }
}
finally {
  Pop-Location
}
