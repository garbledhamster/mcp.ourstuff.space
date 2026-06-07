[CmdletBinding()]
param(
  [Parameter(Position = 0)]
  [string]$Command,

  [Parameter(Position = 1)]
  [string]$Source,

  [string]$ApiBase = $env:SKILL_REGISTRY_URL,
  [string]$AdminToken = $env:SKILL_REGISTRY_ADMIN_TOKEN,
  [string]$ReadToken = $env:SKILL_REGISTRY_READ_TOKEN,
  [string]$UploadedBy = $(if ($env:SKILL_REGISTRY_UPLOADER) { $env:SKILL_REGISTRY_UPLOADER } else { "jrice" }),
  [switch]$BypassApproval
)

$ErrorActionPreference = "Stop"

$Script:Classifiers = @(
  "API_DESIGN",
  "FRONTEND",
  "BACKEND",
  "SECURITY",
  "SCRUBBERS",
  "TESTING",
  "DEBUGGING",
  "CODE_REVIEW",
  "REFACTORING",
  "PERFORMANCE",
  "CI_CD",
  "GIT",
  "DOCS_ADRS",
  "PLANNING",
  "SPEC_DRIVEN",
  "TDD",
  "CONTEXT_ENGINEERING",
  "MCP",
  "DATA",
  "WRITING",
  "LEARNING",
  "SHIPPING",
  "OTHER"
)

function Get-ApiBase {
  if (-not $ApiBase) {
    throw "SKILL_REGISTRY_URL is not set. Run configure or pass -ApiBase."
  }
  return $ApiBase.TrimEnd("/")
}

function Get-AdminToken {
  if (-not $AdminToken) {
    throw "SKILL_REGISTRY_ADMIN_TOKEN is not set. Run configure or pass -AdminToken."
  }
  return $AdminToken
}

function Get-ReadToken {
  if (-not $ReadToken) {
    throw "SKILL_REGISTRY_READ_TOKEN is not set. Run configure or pass -ReadToken."
  }
  return $ReadToken
}

function Invoke-RegistryJson {
  param(
    [ValidateSet("GET", "POST", "DELETE")]
    [string]$Method,
    [string]$Path,
    [string]$Token,
    [object]$Body
  )

  $headers = @{ Authorization = "Bearer $Token" }
  $uri = "$(Get-ApiBase)$Path"
  if ($PSBoundParameters.ContainsKey("Body")) {
    $json = $Body | ConvertTo-Json -Depth 100
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -ContentType "application/json" -Body $json
  }
  return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
}

function Invoke-RegistryText {
  param(
    [string]$Path,
    [string]$Token
  )

  $headers = @{ Authorization = "Bearer $Token" }
  $uri = "$(Get-ApiBase)$Path"
  return (Invoke-WebRequest -Method GET -Uri $uri -Headers $headers).Content
}

function Get-ImportCliPath {
  $path = Join-Path $PSScriptRoot "..\dist\src\import-cli.js"
  $resolved = Resolve-Path -Path $path -ErrorAction SilentlyContinue
  if (-not $resolved) {
    throw "Build output missing. Run npm install, then npm run build from the repo root."
  }
  return $resolved.Path
}

function Invoke-PackageSource {
  param([string]$InputSource)

  if (-not $InputSource) {
    $InputSource = Read-Host "Repo, URL, file, or folder path"
  }
  $tmp = Join-Path $env:TEMP ("skill-import-" + [Guid]::NewGuid().ToString("N") + ".json")
  $cli = Get-ImportCliPath
  & node $cli package $InputSource --out $tmp --uploaded-by $UploadedBy | Out-Host
  if ($LASTEXITCODE -ne 0) {
    throw "import packaging failed"
  }
  $report = Get-Content -Raw $tmp | ConvertFrom-Json
  Remove-Item -LiteralPath $tmp -Force
  return $report
}

function Resolve-LowConfidenceClassifiers {
  param([object]$Report)

  $auto = @($Report.skills | Where-Object { -not $_.classification.needsReview })
  $needs = @($Report.skills | Where-Object { $_.classification.needsReview })

  Write-Host ""
  Write-Host "Auto-classified: $($auto.Count)"
  foreach ($skill in $auto | Select-Object -First 25) {
    Write-Host ("  {0} / {1} / {2} ({3:P0})" -f $skill.classifier, $skill.sourceOwner, $skill.title, [double]$skill.classification.confidence)
  }
  if ($auto.Count -gt 25) {
    Write-Host "  ... $($auto.Count - 25) more"
  }

  if ($needs.Count -eq 0) {
    return $Report
  }

  Write-Host ""
  Write-Host "Needs classifier review: $($needs.Count)"
  foreach ($skill in $needs) {
    Write-Host ""
    Write-Host ("Classify: {0} / {1}" -f $skill.sourceOwner, $skill.title)
    Write-Host ("Evidence: {0}" -f (($skill.classification.evidence | Select-Object -First 3) -join "; "))
    for ($i = 0; $i -lt $Script:Classifiers.Count; $i++) {
      Write-Host ("{0}. {1}" -f ($i + 1), $Script:Classifiers[$i])
    }
    $choice = Read-Host "Select classifier [1-$($Script:Classifiers.Count)] or Enter for OTHER"
    if ($choice) {
      $index = [int]$choice - 1
      if ($index -lt 0 -or $index -ge $Script:Classifiers.Count) {
        throw "invalid classifier choice"
      }
      $skill.classifier = $Script:Classifiers[$index]
      $skill.classification.classifier = $Script:Classifiers[$index]
      $skill.classification.confidence = 1
      $skill.classification.needsReview = $false
      $skill.classification.evidence = @("manual override")
    }
  }
  return $Report
}

function Add-SkillImport {
  param([string]$InputSource)

  $report = Invoke-PackageSource -InputSource $InputSource
  $report = Resolve-LowConfidenceClassifiers -Report $report
  $body = @{
    uploadedBy = $UploadedBy
    bypassApproval = [bool]$BypassApproval
    skills = $report.skills
  }
  $response = Invoke-RegistryJson -Method POST -Path "/admin/imports" -Token (Get-AdminToken) -Body $body
  Write-Host ""
  Write-Host ("Imported versions: {0}" -f @($response.imported).Count)
  Write-Host ("Status: {0}" -f $(if ($BypassApproval) { "approved" } else { "pending" }))
}

function Show-Pending {
  $response = Invoke-RegistryJson -Method GET -Path "/admin/pending" -Token (Get-AdminToken)
  $pending = @($response.pending)
  if ($pending.Count -eq 0) {
    Write-Host "No pending skills."
    return @()
  }
  for ($i = 0; $i -lt $pending.Count; $i++) {
    $item = $pending[$i]
    $bundle = $item.bundle
    Write-Host ("{0}. {1} / {2} / {3}" -f ($i + 1), $bundle.classifier, $bundle.sourceOwner, $bundle.title)
    Write-Host ("   skillId={0}" -f $item.skillId)
    Write-Host ("   versionId={0}" -f $item.id)
  }
  return $pending
}

function Approve-Skill {
  param([string]$SkillId)

  if (-not $SkillId) {
    $pending = Show-Pending
    if (@($pending).Count -eq 0) { return }
    $choice = Read-Host "Approve which number"
    $SkillId = @($pending)[([int]$choice - 1)].skillId
  }

  $showDiff = Read-Host "Show diff before approving? [Y/n]"
  if ($showDiff -notmatch "^(n|N)") {
    Write-Host (Invoke-RegistryText -Path "/admin/skills/$SkillId/diff" -Token (Get-AdminToken))
  }

  $confirm = Read-Host "Approve pending version for $SkillId? [y/N]"
  if ($confirm -notmatch "^(y|Y)") {
    Write-Host "Skipped."
    return
  }

  $response = Invoke-RegistryJson -Method POST -Path "/admin/skills/$SkillId/approve" -Token (Get-AdminToken) -Body @{}
  Write-Host ("Approved: {0}" -f $response.approved.id)
}

function Reject-Skill {
  param([string]$SkillId)

  if (-not $SkillId) {
    $pending = Show-Pending
    if (@($pending).Count -eq 0) { return }
    $choice = Read-Host "Reject which number"
    $SkillId = @($pending)[([int]$choice - 1)].skillId
  }
  $response = Invoke-RegistryJson -Method POST -Path "/admin/skills/$SkillId/reject" -Token (Get-AdminToken) -Body @{}
  Write-Host ("Rejected: {0}" -f $response.rejected.id)
}

function List-Skills {
  param([string]$Query)

  $path = "/admin/skills"
  if ($Query) {
    $path = "${path}?q=$([Uri]::EscapeDataString($Query))"
  }
  $response = Invoke-RegistryJson -Method GET -Path $path -Token (Get-AdminToken)
  foreach ($skill in @($response.skills)) {
    $status = if ($skill.approvedVersionId) { "approved" } else { "unapproved" }
    Write-Host ("{0} / {1} / {2} [{3}]" -f $skill.classifier, $skill.sourceOwner, $skill.title, $status)
  }
}

function Search-McpSkills {
  param([string]$Query)

  if (-not $Query) { $Query = Read-Host "Search query" }
  $body = @{
    jsonrpc = "2.0"
    id = 1
    method = "tools/call"
    params = @{
      name = "search_skills"
      arguments = @{ query = $Query }
    }
  }
  $response = Invoke-RegistryJson -Method POST -Path "/mcp" -Token (Get-ReadToken) -Body $body
  Write-Host $response.result.content[0].text
}

function Test-Registry {
  Write-Host "Health:"
  Invoke-RestMethod -Method GET -Uri "$(Get-ApiBase)/health" | ConvertTo-Json -Depth 10 | Write-Host

  Write-Host "Admin list:"
  Invoke-RegistryJson -Method GET -Path "/admin/skills" -Token (Get-AdminToken) | ConvertTo-Json -Depth 4 | Write-Host

  Write-Host "MCP initialize:"
  $body = @{ jsonrpc = "2.0"; id = 1; method = "initialize"; params = @{} }
  Invoke-RegistryJson -Method POST -Path "/mcp" -Token (Get-ReadToken) -Body $body | ConvertTo-Json -Depth 10 | Write-Host
}

function Configure-Registry {
  $url = Read-Host "Registry URL"
  $admin = Read-Host "Admin token"
  $read = Read-Host "Read token"
  $scope = Read-Host "Persist to user environment? [y/N]"

  $script:ApiBase = $url
  $script:AdminToken = $admin
  $script:ReadToken = $read
  $env:SKILL_REGISTRY_URL = $url
  $env:SKILL_REGISTRY_ADMIN_TOKEN = $admin
  $env:SKILL_REGISTRY_READ_TOKEN = $read

  if ($scope -match "^(y|Y)") {
    [Environment]::SetEnvironmentVariable("SKILL_REGISTRY_URL", $url, "User")
    [Environment]::SetEnvironmentVariable("SKILL_REGISTRY_ADMIN_TOKEN", $admin, "User")
    [Environment]::SetEnvironmentVariable("SKILL_REGISTRY_READ_TOKEN", $read, "User")
    Write-Host "Saved user environment variables. New terminals will inherit them."
  } else {
    Write-Host "Set for current process only."
  }
}

function Show-Menu {
  while ($true) {
    Write-Host ""
    Write-Host "Skill Registry"
    Write-Host "1. Add skill/repo/folder"
    Write-Host "2. Review pending imports"
    Write-Host "3. Approve update/import"
    Write-Host "4. Reject pending"
    Write-Host "5. List skills"
    Write-Host "6. Search approved MCP skills"
    Write-Host "7. Show skill diff"
    Write-Host "8. Configure endpoint/tokens"
    Write-Host "9. Test connection"
    Write-Host "0. Exit"
    $choice = Read-Host "Select"
    switch ($choice) {
      "1" { Add-SkillImport }
      "2" { Show-Pending | Out-Null }
      "3" { Approve-Skill }
      "4" { Reject-Skill }
      "5" { List-Skills }
      "6" { Search-McpSkills }
      "7" {
        $id = Read-Host "Skill id"
        Write-Host (Invoke-RegistryText -Path "/admin/skills/$id/diff" -Token (Get-AdminToken))
      }
      "8" { Configure-Registry }
      "9" { Test-Registry }
      "0" { return }
      default { Write-Host "Unknown option." }
    }
  }
}

$CommandName = if ($Command) { $Command.ToLowerInvariant() } else { "" }
switch ($CommandName) {
  "" { Show-Menu }
  "add" { Add-SkillImport -InputSource $Source }
  "pending" { Show-Pending | Out-Null }
  "approve" { Approve-Skill -SkillId $Source }
  "reject" { Reject-Skill -SkillId $Source }
  "list" { List-Skills -Query $Source }
  "search" { Search-McpSkills -Query $Source }
  "configure" { Configure-Registry }
  "test" { Test-Registry }
  default {
    throw "Unknown command '$Command'. Use add, pending, approve, reject, list, search, configure, test, or no command for menu."
  }
}
