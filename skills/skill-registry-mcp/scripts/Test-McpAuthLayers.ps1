[CmdletBinding()]
param(
  [string]$ApiBase = $env:SKILL_REGISTRY_URL,
  [string]$ReadToken = $env:SKILL_REGISTRY_READ_TOKEN,
  [switch]$PublicRead,
  [switch]$SkipMcpClient
)

$ErrorActionPreference = "Stop"

if (-not $ApiBase) { throw "SKILL_REGISTRY_URL or -ApiBase is required." }
$ApiBase = $ApiBase.TrimEnd("/")

Write-Host "TLS/HTTPS reachability:"
$health = Invoke-WebRequest -UseBasicParsing -Method GET -Uri "$ApiBase/health"
if ($health.StatusCode -ne 200) { throw "health failed with $($health.StatusCode)" }
Write-Host "PASS health 200"

Write-Host "OAuth protected resource metadata:"
$resource = Invoke-WebRequest -UseBasicParsing -Method GET -Uri "$ApiBase/.well-known/oauth-protected-resource"
if ($resource.StatusCode -ne 200) { throw "protected resource metadata failed with $($resource.StatusCode)" }
$resourceJson = $resource.Content | ConvertFrom-Json
Write-Host ("PASS protected resource metadata oauth_implemented={0}" -f $resourceJson.mcp_auth_status.oauth_implemented)

Write-Host "OAuth authorization server metadata:"
$authorizationServer = Invoke-WebRequest -UseBasicParsing -Method GET -Uri "$ApiBase/.well-known/oauth-authorization-server"
if ($authorizationServer.StatusCode -ne 200) { throw "authorization server metadata failed with $($authorizationServer.StatusCode)" }
$authorizationServerJson = $authorizationServer.Content | ConvertFrom-Json
Write-Host ("PASS authorization metadata token_endpoint={0}" -f $(if ($authorizationServerJson.token_endpoint) { $authorizationServerJson.token_endpoint } else { "<not configured>" }))

Write-Host "MCP without token should 401 + WWW-Authenticate:"
if ($PublicRead) {
  $publicMcp = Invoke-WebRequest -UseBasicParsing -Method POST -Uri "$ApiBase/mcp" -ContentType "application/json" -Body '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
  if ($publicMcp.StatusCode -ne 200) { throw "expected public /mcp to initialize, got $($publicMcp.StatusCode)" }
  Write-Host "PASS /mcp public no-auth initialize"
}
else {
  try {
    Invoke-WebRequest -UseBasicParsing -Method POST -Uri "$ApiBase/mcp" -ContentType "application/json" -Body '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | Out-Null
    throw "expected /mcp without token to fail"
  }
  catch {
    $response = $_.Exception.Response
    if (-not $response) { throw }
    if ([int]$response.StatusCode -ne 401) { throw "expected 401, got $([int]$response.StatusCode)" }
    $challenge = $response.Headers["WWW-Authenticate"]
    if ($challenge -notmatch "oauth-protected-resource") { throw "WWW-Authenticate missing protected resource metadata pointer" }
    Write-Host "PASS /mcp 401 discovery challenge"
  }
}

if (-not $ReadToken) {
  Write-Host "SKIP bearer and MCP client checks: no SKILL_REGISTRY_READ_TOKEN"
  return
}

Write-Host "Private bearer token MCP initialize:"
$headers = @{ Authorization = "Bearer $ReadToken" }
$mcp = Invoke-WebRequest -UseBasicParsing -Method POST -Uri "$ApiBase/mcp" -Headers $headers -ContentType "application/json" -Body '{"jsonrpc":"2.0","id":2,"method":"initialize","params":{}}'
if ($mcp.StatusCode -ne 200) { throw "private bearer MCP initialize failed with $($mcp.StatusCode)" }
Write-Host "PASS private bearer MCP initialize"

if (-not $SkipMcpClient) {
  Write-Host "MCP SDK Streamable HTTP client:"
  $repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
  $previousUrl = $env:SKILL_REGISTRY_URL
  $previousReadToken = $env:SKILL_REGISTRY_READ_TOKEN
  $env:SKILL_REGISTRY_URL = $ApiBase
  $env:SKILL_REGISTRY_READ_TOKEN = $ReadToken
  Push-Location $repoRoot
  try {
    node .\scripts\mcp-client-smoke.mjs
    if ($LASTEXITCODE -ne 0) { throw "MCP SDK client smoke failed" }
  }
  finally {
    Pop-Location
    $env:SKILL_REGISTRY_URL = $previousUrl
    $env:SKILL_REGISTRY_READ_TOKEN = $previousReadToken
  }
}
