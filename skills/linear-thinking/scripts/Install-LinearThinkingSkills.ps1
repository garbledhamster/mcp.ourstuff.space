[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$PackageRoot,
    [string]$RuntimeSkillRoot = (Join-Path $env:USERPROFILE ".agents\skills"),
    [switch]$ForceMemory,
    [switch]$IncludeMeetings
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

function Copy-FileTree {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination,
        [bool]$SkipMeetings = $true,
        [bool]$ForceMemoryFiles = $false
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        return
    }

    Get-ChildItem -LiteralPath $Source -Recurse -File -Force | ForEach-Object {
        $relativePath = $_.FullName.Substring((Resolve-Path -LiteralPath $Source).Path.Length).TrimStart("\", "/")
        $parts = $relativePath -split "[\\/]"

        if ($SkipMeetings -and ($parts -contains "meetings")) {
            return
        }

        $targetPath = Join-Path $Destination $relativePath
        $targetDir = Split-Path $targetPath -Parent

        if ($_.Name -eq "MEMORY.md" -and (Test-Path -LiteralPath $targetPath) -and -not $ForceMemoryFiles) {
            Write-Output "SKIP memory exists: $targetPath"
            return
        }

        if ($PSCmdlet.ShouldProcess($targetPath, "Copy $($_.FullName)")) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            Copy-Item -LiteralPath $_.FullName -Destination $targetPath -Force
        }
    }
}

function Sync-DirectorySet {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        return
    }
    if (-not (Test-Path -LiteralPath $Destination)) {
        return
    }

    $sourceNames = @{}
    Get-ChildItem -LiteralPath $Source -Directory -Force | ForEach-Object {
        $sourceNames[$_.Name] = $true
    }

    Get-ChildItem -LiteralPath $Destination -Directory -Force | ForEach-Object {
        if (-not $sourceNames.ContainsKey($_.Name)) {
            if ($PSCmdlet.ShouldProcess($_.FullName, "Remove stale generated directory")) {
                Remove-Item -LiteralPath $_.FullName -Recurse -Force
            }
        }
    }
}

$PackageRoot = Resolve-ScriptPackageRoot
$skipMeetings = -not $IncludeMeetings

$skillsRoot = Join-Path $PackageRoot "skills"
$sharedRoots = @("references", "templates")
$starterExperts = Join-Path $PackageRoot "experts\starter"
$localExperts = Join-Path $PackageRoot ".local\experts"

if (-not (Test-Path -LiteralPath $skillsRoot)) {
    throw "Missing package skills root: $skillsRoot"
}

New-Item -ItemType Directory -Path $RuntimeSkillRoot -Force | Out-Null

Get-ChildItem -LiteralPath $skillsRoot -Directory | ForEach-Object {
    $skillPath = Join-Path $_.FullName "SKILL.md"
    if (-not (Test-Path -LiteralPath $skillPath)) {
        return
    }

    $targetSkill = Join-Path $RuntimeSkillRoot $_.Name
    Copy-FileTree -Source $_.FullName -Destination $targetSkill -SkipMeetings $skipMeetings -ForceMemoryFiles $ForceMemory

    foreach ($sharedRoot in $sharedRoots) {
        $sourceShared = Join-Path $PackageRoot $sharedRoot
        $targetShared = Join-Path $targetSkill $sharedRoot
        Copy-FileTree -Source $sourceShared -Destination $targetShared -SkipMeetings $skipMeetings -ForceMemoryFiles $ForceMemory
    }

    if (Test-Path -LiteralPath $starterExperts) {
        $targetStarterExperts = Join-Path $targetSkill "experts\starter"
        Sync-DirectorySet -Source $starterExperts -Destination $targetStarterExperts
        Copy-FileTree -Source $starterExperts -Destination $targetStarterExperts -SkipMeetings $skipMeetings -ForceMemoryFiles $ForceMemory
    }

    if (Test-Path -LiteralPath $localExperts) {
        Copy-FileTree -Source $localExperts -Destination (Join-Path $targetSkill "experts\local") -SkipMeetings $skipMeetings -ForceMemoryFiles $ForceMemory
    }
}

if ($WhatIfPreference) {
    Write-Output "Evaluated linear thinking skill install plan for $RuntimeSkillRoot"
} else {
    Write-Output "Installed linear thinking skills to $RuntimeSkillRoot"
}
