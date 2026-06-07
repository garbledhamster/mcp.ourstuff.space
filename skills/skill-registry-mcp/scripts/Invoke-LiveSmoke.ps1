[CmdletBinding()]
param(
  [string]$ApiBase = $env:SKILL_REGISTRY_URL,
  [string]$ReadToken = $env:SKILL_REGISTRY_READ_TOKEN,
  [string]$AdminToken = $env:SKILL_REGISTRY_ADMIN_TOKEN,
  [string]$OutputRoot = $(Join-Path $env:TEMP "skill-registry-smoke")
)

$ErrorActionPreference = "Stop"

if (-not $ApiBase) { throw "SKILL_REGISTRY_URL or -ApiBase is required." }
if (-not $ReadToken) { throw "SKILL_REGISTRY_READ_TOKEN or -ReadToken is required." }
if (-not $AdminToken) { throw "SKILL_REGISTRY_ADMIN_TOKEN or -AdminToken is required." }

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$UtilityBelt = "C:\Codex\codex_utility_belt\utility-belt\use-utility-belt.ps1"
New-Item -ItemType Directory -Force $OutputRoot | Out-Null

$env:API_BASE = $ApiBase.TrimEnd("/")
$env:WORKFLOW_PATH = Join-Path $RepoRoot "workflows\read-mcp-smoke.json"
$env:JSON_OUT = Join-Path $OutputRoot "read-mcp-smoke.json"
$env:API_TOKEN = $ReadToken
& $UtilityBelt -Run api-workflow
if ($LASTEXITCODE -ne 0) { throw "read MCP smoke failed" }

$env:WORKFLOW_PATH = Join-Path $RepoRoot "workflows\admin-smoke.json"
$env:JSON_OUT = Join-Path $OutputRoot "admin-smoke.json"
$env:API_TOKEN = $AdminToken
& $UtilityBelt -Run api-workflow
if ($LASTEXITCODE -ne 0) { throw "admin smoke failed" }

$publicRead = $env:SKILL_REGISTRY_MCP_PUBLIC_READ -eq "true"
if ($publicRead) {
  & (Join-Path $PSScriptRoot "Test-McpAuthLayers.ps1") -ApiBase $ApiBase -ReadToken $ReadToken -PublicRead
}
else {
  & (Join-Path $PSScriptRoot "Test-McpAuthLayers.ps1") -ApiBase $ApiBase -ReadToken $ReadToken
}

Write-Host "Smoke reports:"
Write-Host (Join-Path $OutputRoot "read-mcp-smoke.json")
Write-Host (Join-Path $OutputRoot "admin-smoke.json")
