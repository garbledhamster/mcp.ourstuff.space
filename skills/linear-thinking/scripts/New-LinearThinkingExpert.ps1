[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$PackageRoot,
    [string]$Id,
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][int]$Age,
    [Parameter(Mandatory = $true)][string]$Domain,
    [Parameter(Mandatory = $true)]
    [Alias("Mindset")]
    [ValidateSet("Operator", "Engineer", "Architect", "Strategist", "Steward", "Philosopher")]
    [string]$Role,
    [Parameter(Mandatory = $true)][string]$Voice,
    [Parameter(Mandatory = $true)][string]$LifeDefiningEvent,
    [Parameter(Mandatory = $true)][string]$AnalogyStyle,
    [Parameter(Mandatory = $true)][string]$MaintenanceRules,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Resolve-ScriptPackageRoot {
    if ($PackageRoot) {
        return (Resolve-Path -LiteralPath $PackageRoot).Path
    }

    $scriptRoot = $PSScriptRoot
    if (-not $scriptRoot -and $PSCommandPath) {
        $scriptRoot = Split-Path -Parent $PSCommandPath
    }
    if (-not $scriptRoot) {
        throw "Unable to resolve script root. Pass -PackageRoot explicitly."
    }

    return (Resolve-Path -LiteralPath (Split-Path -Parent $scriptRoot)).Path
}

function ConvertTo-ExpertId {
    param([string]$Value)

    $slug = $Value.ToLowerInvariant() -replace "[^a-z0-9]+", "-"
    $slug = $slug.Trim("-")
    if (-not $slug) {
        throw "Expert id cannot be empty."
    }
    return $slug
}

$primaryQuestions = @{
    "Operator" = "What needs to happen next?"
    "Engineer" = "How do we build it?"
    "Architect" = "How should the system fit together?"
    "Strategist" = "Where is this going, and what move creates leverage?"
    "Steward" = "Who or what must be protected as this changes?"
    "Philosopher" = "Why does this matter, and what should guide the choice?"
}

$PackageRoot = Resolve-ScriptPackageRoot
$Mindset = $Role
$PrimaryQuestion = $primaryQuestions[$Role]

if (-not $Id) {
    $Id = ConvertTo-ExpertId -Value $Name
} else {
    $Id = ConvertTo-ExpertId -Value $Id
}

$expertRoot = Join-Path $PackageRoot ".local\experts\$Id"
if ((Test-Path -LiteralPath $expertRoot) -and -not $Force) {
    throw "Expert already exists: $expertRoot. Use -Force to update generated identity files."
}

$agentsContent = @"
# $Name

Name: $Name
Age: $Age
Domain: $Domain
Role: $Role
Mindset: $Mindset
Primary question: $PrimaryQuestion
Default starter: No
Voice: $Voice
Life-defining event: $LifeDefiningEvent
Analogy style: $AnalogyStyle
Maintenance rules: $MaintenanceRules

## Operating Notes

- Speak from the assigned mindset before personal style.
- Keep claims grounded in available evidence.
- Distinguish durable lessons from meeting-local context.
"@

$memoryTemplateContent = @"
# $Name Memory

Durable local knowledge for $Name. Keep this file private unless explicitly promoted after review.

## Durable Preferences

- None yet.

## Durable Lessons

- None yet.
"@

$memoryContent = @"
# $Name Memory

Private durable memory for local roundtable use.

## Durable Preferences

- None yet.

## Durable Lessons

- None yet.

## Last Reviewed

- Created locally by New-LinearThinkingExpert.ps1.
"@

if ($PSCmdlet.ShouldProcess($expertRoot, "Create local expert profile")) {
    New-Item -ItemType Directory -Path $expertRoot -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $expertRoot "meetings") -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $expertRoot "AGENTS.md") -Value $agentsContent -Encoding utf8
    Set-Content -LiteralPath (Join-Path $expertRoot "MEMORY.template.md") -Value $memoryTemplateContent -Encoding utf8

    $memoryPath = Join-Path $expertRoot "MEMORY.md"
    if (-not (Test-Path -LiteralPath $memoryPath) -or $Force) {
        Set-Content -LiteralPath $memoryPath -Value $memoryContent -Encoding utf8
    } else {
        Write-Output "SKIP memory exists: $memoryPath"
    }
}

[pscustomobject]@{
    Id = $Id
    Path = $expertRoot
    Role = $Role
    Mindset = $Mindset
    PrimaryQuestion = $PrimaryQuestion
}
