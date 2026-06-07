[CmdletBinding()]
param(
    [string]$PackageRoot,
    [string]$RuntimeSkillRoot = (Join-Path $env:USERPROFILE ".agents\skills"),
    [switch]$RequireRuntime
)

$ErrorActionPreference = "Stop"
$failures = @()

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

$PackageRoot = Resolve-ScriptPackageRoot

$ExpectedMindsetQuestions = [ordered]@{
    "Operator" = "What needs to happen next?"
    "Engineer" = "How do we build it?"
    "Architect" = "How should the system fit together?"
    "Strategist" = "Where is this going, and what move creates leverage?"
    "Steward" = "Who or what must be protected as this changes?"
    "Philosopher" = "Why does this matter, and what should guide the choice?"
}

$ExpectedPairings = @(
    @("Operator", "Engineer"),
    @("Architect", "Strategist"),
    @("Steward", "Philosopher")
)

$LegacyRoles = @(
    "Product Owner",
    "Project Manager",
    "Security Engineer",
    "QA / Tester",
    "UX Designer",
    "SRE / Operations",
    "Data Analyst",
    "Compliance / Governance",
    "Customer / End User"
)

function Add-Failure {
    param([string]$Message)
    $script:failures += $Message
}

function Read-Frontmatter {
    param([string]$Path)

    $lines = Get-Content -LiteralPath $Path -TotalCount 80
    if ($lines.Count -lt 3 -or $lines[0] -ne "---") {
        return @{}
    }

    $map = @{}
    for ($i = 1; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -eq "---") {
            break
        }
        if ($lines[$i] -match "^\s*([^:]+):\s*(.*)\s*$") {
            $map[$Matches[1].Trim()] = $Matches[2].Trim().Trim('"').Trim("'")
        }
    }
    return $map
}

function Get-MetadataField {
    param(
        [string]$Content,
        [string]$Field
    )

    $pattern = "(?m)^" + [regex]::Escape($Field) + ":\s*(.+?)\s*$"
    $match = [regex]::Match($Content, $pattern)
    if ($match.Success) {
        return $match.Groups[1].Value.Trim()
    }
    return $null
}

function Test-TextContains {
    param(
        [string]$Content,
        [string]$Needle,
        [string]$Path,
        [string]$FailureCode
    )

    if ($Content -notmatch [regex]::Escape($Needle)) {
        Add-Failure "$FailureCode`t$Needle`t$Path"
    }
}

function Test-TextOmits {
    param(
        [string]$Content,
        [string]$Needle,
        [string]$Path,
        [string]$FailureCode
    )

    if ($Content -match [regex]::Escape($Needle)) {
        Add-Failure "$FailureCode`t$Needle`t$Path"
    }
}

function Test-ExpectedSkill {
    param(
        [string]$Root,
        [string]$Folder,
        [string]$Name
    )

    $skillPath = Join-Path $Root "$Folder\SKILL.md"
    if (-not (Test-Path -LiteralPath $skillPath)) {
        Add-Failure "missing-skill`t$skillPath"
        return
    }

    $frontmatter = Read-Frontmatter -Path $skillPath
    if ($frontmatter["name"] -ne $Name) {
        Add-Failure "bad-skill-name`t$skillPath"
    }
    if (-not $frontmatter["description"] -or $frontmatter["description"] -notmatch "Use when") {
        Add-Failure "bad-skill-description`t$skillPath"
    }
}

function Test-PairingMention {
    param(
        [string]$Content,
        [string]$Left,
        [string]$Right,
        [string]$Path
    )

    $left = [regex]::Escape($Left)
    $right = [regex]::Escape($Right)
    if ($Content -notmatch "$left\s*(\+|and)\s*$right") {
        Add-Failure "missing-default-pairing`t$Left + $Right`t$Path"
    }
}

function Test-ExpertDirectory {
    param([string]$Path)

    $requiredFields = @(
        "Name:",
        "Age:",
        "Domain:",
        "Role:",
        "Mindset:",
        "Primary question:",
        "Default starter:",
        "Voice:",
        "Life-defining event:",
        "Analogy style:",
        "Maintenance rules:"
    )

    $agentsPath = Join-Path $Path "AGENTS.md"
    $memoryTemplatePath = Join-Path $Path "MEMORY.template.md"

    if (-not (Test-Path -LiteralPath $agentsPath)) {
        Add-Failure "missing-expert-agents`t$agentsPath"
        return
    }
    if (-not (Test-Path -LiteralPath $memoryTemplatePath)) {
        Add-Failure "missing-expert-memory-template`t$memoryTemplatePath"
    }
    if (Test-Path -LiteralPath (Join-Path $Path "MEMORY.md")) {
        Add-Failure "tracked-memory-file`t$(Join-Path $Path "MEMORY.md")"
    }

    $content = Get-Content -Raw -LiteralPath $agentsPath
    foreach ($field in $requiredFields) {
        if ($content -notmatch [regex]::Escape($field)) {
            Add-Failure "missing-expert-field`t$field`t$agentsPath"
        }
    }

    $role = Get-MetadataField -Content $content -Field "Role"
    $mindset = Get-MetadataField -Content $content -Field "Mindset"
    $primaryQuestion = Get-MetadataField -Content $content -Field "Primary question"

    if ($role -and $mindset -and $role -ne $mindset) {
        Add-Failure "role-mindset-mismatch`t$role`t$mindset`t$agentsPath"
    }
    foreach ($value in @($role, $mindset)) {
        if ($value -and -not $script:ExpectedMindsetQuestions.Contains($value)) {
            Add-Failure "unexpected-mindset`t$value`t$agentsPath"
        }
    }
    if ($role -and $script:ExpectedMindsetQuestions.Contains($role) -and $primaryQuestion -ne $script:ExpectedMindsetQuestions[$role]) {
        Add-Failure "primary-question-mismatch`t$role`t$primaryQuestion`t$agentsPath"
    }
}

function Test-TemplateContracts {
    param([string]$TemplateRoot)

    if (-not (Test-Path -LiteralPath $TemplateRoot)) {
        Add-Failure "missing-template-root`t$TemplateRoot"
        return
    }

    $allTemplates = @(Get-ChildItem -LiteralPath $TemplateRoot -Recurse -File -ErrorAction SilentlyContinue)
    $markdownTemplates = @($allTemplates | Where-Object { $_.Name -like "*.template.md" })
    $jsonTemplates = @($allTemplates | Where-Object {
        $_.Name -like "*.template.json" -or
        $_.Name -like "*.template.jsonl" -or
        $_.Name -like "*.json.template" -or
        $_.Name -like "*.jsonl.template"
    })

    if ($markdownTemplates.Count -eq 0) {
        Add-Failure "missing-markdown-meeting-template`t$TemplateRoot"
    }
    if ($jsonTemplates.Count -eq 0) {
        Add-Failure "missing-json-meeting-template`t$TemplateRoot"
    }

    $markdownText = ($markdownTemplates | ForEach-Object { $_.Name + "`n" + (Get-Content -Raw -LiteralPath $_.FullName) }) -join "`n"
    $jsonText = ($jsonTemplates | ForEach-Object { $_.Name + "`n" + (Get-Content -Raw -LiteralPath $_.FullName) }) -join "`n"

    foreach ($needle in @(
        "Pass 1",
        "Pass 2",
        "Pass 3",
        "Pair:",
        "Working question:",
        "Proposal:",
        "Why this is the right move:",
        "What we can help implement:",
        "Memory candidates:"
    )) {
        Test-TextContains -Content $markdownText -Needle $needle -Path $TemplateRoot -FailureCode "missing-markdown-template-contract"
    }

    foreach ($needle in @(
        "meetingId",
        "timestamp",
        "pass",
        "hat",
        "speakerId",
        "speakerName",
        "pairId",
        "mindsets",
        "messageType",
        "visibility",
        "text",
        "visible",
        "internal"
    )) {
        Test-TextContains -Content $jsonText -Needle $needle -Path $TemplateRoot -FailureCode "missing-json-template-contract"
    }
}

function Test-NewExpertScriptContract {
    param([string]$ScriptPath)

    if (-not (Test-Path -LiteralPath $ScriptPath)) {
        Add-Failure "missing-new-expert-script`t$ScriptPath"
        return
    }

    $scriptText = Get-Content -Raw -LiteralPath $ScriptPath
    foreach ($mindset in $script:ExpectedMindsetQuestions.Keys) {
        Test-TextContains -Content $scriptText -Needle "`"$mindset`"" -Path $ScriptPath -FailureCode "new-expert-missing-mindset"
    }
    foreach ($legacyRole in $script:LegacyRoles) {
        Test-TextOmits -Content $scriptText -Needle "`"$legacyRole`"" -Path $ScriptPath -FailureCode "new-expert-legacy-role"
    }
    Test-TextContains -Content $scriptText -Needle ".local\experts" -Path $ScriptPath -FailureCode "new-expert-local-root"

    $tempRoot = Join-Path ([IO.Path]::GetTempPath()) ("linear-thinking-new-expert-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null
    try {
        & $ScriptPath -PackageRoot $tempRoot -Id "test-strategist" -Name "Test Strategist" -Age 42 -Domain "Validation" -Role "Strategist" -Voice "Concise" -LifeDefiningEvent "Validated a package contract." -AnalogyStyle "Maps" -MaintenanceRules "Keep durable facts only." | Out-Null

        $expertRoot = Join-Path $tempRoot ".local\experts\test-strategist"
        foreach ($requiredFile in @("AGENTS.md", "MEMORY.template.md", "MEMORY.md")) {
            if (-not (Test-Path -LiteralPath (Join-Path $expertRoot $requiredFile))) {
                Add-Failure "new-expert-missing-output`t$requiredFile`t$expertRoot"
            }
        }

        $memoryPath = Join-Path $expertRoot "MEMORY.md"
        Set-Content -LiteralPath $memoryPath -Value "KEEP THIS MEMORY" -Encoding utf8

        $threw = $false
        try {
            & $ScriptPath -PackageRoot $tempRoot -Id "test-strategist" -Name "Test Strategist" -Age 42 -Domain "Validation" -Role "Strategist" -Voice "Concise" -LifeDefiningEvent "Validated a package contract." -AnalogyStyle "Maps" -MaintenanceRules "Keep durable facts only." | Out-Null
        } catch {
            $threw = $true
        }

        if (-not $threw) {
            Add-Failure "new-expert-overwrite-without-force`t$expertRoot"
        }
        if ((Get-Content -Raw -LiteralPath $memoryPath) -notmatch "KEEP THIS MEMORY") {
            Add-Failure "new-expert-memory-overwritten-without-force`t$memoryPath"
        }
    } finally {
        $resolvedTemp = (Resolve-Path -LiteralPath $tempRoot -ErrorAction SilentlyContinue).Path
        $tempBase = (Resolve-Path -LiteralPath ([IO.Path]::GetTempPath())).Path
        if ($resolvedTemp -and $resolvedTemp.StartsWith($tempBase, [StringComparison]::OrdinalIgnoreCase)) {
            Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
        }
    }
}

function Test-InstallScriptContract {
    param([string]$ScriptPath)

    if (-not (Test-Path -LiteralPath $ScriptPath)) {
        Add-Failure "missing-install-script`t$ScriptPath"
        return
    }

    $tempRoot = Join-Path ([IO.Path]::GetTempPath()) ("linear-thinking-install-" + [guid]::NewGuid().ToString("N"))
    $package = Join-Path $tempRoot "package"
    $runtime = Join-Path $tempRoot "runtime"

    New-Item -ItemType Directory -Path (Join-Path $package "skills\linear-thinking-agents\meetings") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $package "references") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $package "templates") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $package "experts\starter\starter-one\meetings") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $package ".local\experts\local-one\meetings") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $runtime "linear-thinking-agents\experts\local\local-one") -Force | Out-Null

    Set-Content -LiteralPath (Join-Path $package "skills\linear-thinking-agents\SKILL.md") -Value "---`nname: linear-thinking-agents`ndescription: Use when testing.`n---" -Encoding utf8
    Set-Content -LiteralPath (Join-Path $package "skills\linear-thinking-agents\meetings\public-session.md") -Value "public meeting" -Encoding utf8
    Set-Content -LiteralPath (Join-Path $package "references\hat-protocol.md") -Value "reference" -Encoding utf8
    Set-Content -LiteralPath (Join-Path $package "templates\meeting-note.template.md") -Value "template" -Encoding utf8
    Set-Content -LiteralPath (Join-Path $package "experts\starter\starter-one\AGENTS.md") -Value "starter" -Encoding utf8
    Set-Content -LiteralPath (Join-Path $package "experts\starter\starter-one\meetings\starter-session.md") -Value "starter meeting" -Encoding utf8
    Set-Content -LiteralPath (Join-Path $package ".local\experts\local-one\AGENTS.md") -Value "local expert" -Encoding utf8
    Set-Content -LiteralPath (Join-Path $package ".local\experts\local-one\MEMORY.md") -Value "LOCAL MEMORY" -Encoding utf8
    Set-Content -LiteralPath (Join-Path $package ".local\experts\local-one\meetings\local-session.md") -Value "local meeting" -Encoding utf8
    Set-Content -LiteralPath (Join-Path $runtime "linear-thinking-agents\experts\local\local-one\MEMORY.md") -Value "KEEP RUNTIME MEMORY" -Encoding utf8

    try {
        & $ScriptPath -PackageRoot $package -RuntimeSkillRoot $runtime | Out-Null

        foreach ($requiredPath in @(
            "linear-thinking-agents\SKILL.md",
            "linear-thinking-agents\references\hat-protocol.md",
            "linear-thinking-agents\templates\meeting-note.template.md",
            "linear-thinking-agents\experts\starter\starter-one\AGENTS.md",
            "linear-thinking-agents\experts\local\local-one\AGENTS.md"
        )) {
            if (-not (Test-Path -LiteralPath (Join-Path $runtime $requiredPath))) {
                Add-Failure "install-missing-runtime-file`t$requiredPath"
            }
        }

        foreach ($meetingPath in @(
            "linear-thinking-agents\meetings\public-session.md",
            "linear-thinking-agents\experts\starter\starter-one\meetings\starter-session.md",
            "linear-thinking-agents\experts\local\local-one\meetings\local-session.md"
        )) {
            if (Test-Path -LiteralPath (Join-Path $runtime $meetingPath)) {
                Add-Failure "install-copied-meeting-by-default`t$meetingPath"
            }
        }

        $memoryPath = Join-Path $runtime "linear-thinking-agents\experts\local\local-one\MEMORY.md"
        if ((Get-Content -Raw -LiteralPath $memoryPath) -notmatch "KEEP RUNTIME MEMORY") {
            Add-Failure "install-overwrote-memory-without-force`t$memoryPath"
        }

        & $ScriptPath -PackageRoot $package -RuntimeSkillRoot $runtime -ForceMemory | Out-Null
        if ((Get-Content -Raw -LiteralPath $memoryPath) -notmatch "LOCAL MEMORY") {
            Add-Failure "install-did-not-force-memory`t$memoryPath"
        }
    } finally {
        $resolvedTemp = (Resolve-Path -LiteralPath $tempRoot -ErrorAction SilentlyContinue).Path
        $tempBase = (Resolve-Path -LiteralPath ([IO.Path]::GetTempPath())).Path
        if ($resolvedTemp -and $resolvedTemp.StartsWith($tempBase, [StringComparison]::OrdinalIgnoreCase)) {
            Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
        }
    }
}

$skillsRoot = Join-Path $PackageRoot "skills"
Test-ExpectedSkill -Root $skillsRoot -Folder "linear-thinking-agents" -Name "linear-thinking-agents"
Test-ExpectedSkill -Root $skillsRoot -Folder "linear-thinking-expert-builder" -Name "linear-thinking-expert-builder"
Test-ExpectedSkill -Root $skillsRoot -Folder "linear-thinking-coders" -Name "linear-thinking-coders"

$agentSkillPath = Join-Path $skillsRoot "linear-thinking-agents\SKILL.md"
$builderSkillPath = Join-Path $skillsRoot "linear-thinking-expert-builder\SKILL.md"
$coderSkillPath = Join-Path $skillsRoot "linear-thinking-coders\SKILL.md"
$coderReferenceRoot = Join-Path $skillsRoot "linear-thinking-coders\references"
$meetingFlowPath = Join-Path $PackageRoot "references\meeting-flow.md"
$expertSchemaPath = Join-Path $PackageRoot "references\expert-schema.md"
$hatProtocolPath = Join-Path $PackageRoot "references\hat-protocol.md"
$templateRoot = Join-Path $PackageRoot "templates"

foreach ($requiredFile in @(
    $agentSkillPath,
    $builderSkillPath,
    $coderSkillPath,
    (Join-Path $coderReferenceRoot "workflow.md"),
    (Join-Path $coderReferenceRoot "design-doc-template.md"),
    (Join-Path $coderReferenceRoot "coder-ticket-template.md"),
    (Join-Path $coderReferenceRoot "self-critique-checklist.md"),
    (Join-Path $coderReferenceRoot "coding-agent-behavior-standard.md"),
    (Join-Path $coderReferenceRoot "verified-opencode-agents.md"),
    (Join-Path $coderReferenceRoot "opencode-agent-backend.md"),
    $meetingFlowPath,
    $expertSchemaPath,
    $hatProtocolPath
)) {
    if (-not (Test-Path -LiteralPath $requiredFile)) {
        Add-Failure "missing-required-file`t$requiredFile"
    }
}

$agentSkillText = if (Test-Path -LiteralPath $agentSkillPath) { Get-Content -Raw -LiteralPath $agentSkillPath } else { "" }
$builderSkillText = if (Test-Path -LiteralPath $builderSkillPath) { Get-Content -Raw -LiteralPath $builderSkillPath } else { "" }
$coderSkillText = if (Test-Path -LiteralPath $coderSkillPath) { Get-Content -Raw -LiteralPath $coderSkillPath } else { "" }
$coderReferenceText = if (Test-Path -LiteralPath $coderReferenceRoot) { (Get-ChildItem -LiteralPath $coderReferenceRoot -Filter "*.md" -File | ForEach-Object { $_.Name + "`n" + (Get-Content -Raw -LiteralPath $_.FullName) }) -join "`n" } else { "" }
$meetingFlowText = if (Test-Path -LiteralPath $meetingFlowPath) { Get-Content -Raw -LiteralPath $meetingFlowPath } else { "" }
$expertSchemaText = if (Test-Path -LiteralPath $expertSchemaPath) { Get-Content -Raw -LiteralPath $expertSchemaPath } else { "" }
$contractText = $agentSkillText + "`n" + $builderSkillText + "`n" + $coderSkillText + "`n" + $coderReferenceText + "`n" + $meetingFlowText + "`n" + $expertSchemaText

foreach ($mindset in $ExpectedMindsetQuestions.Keys) {
    Test-TextContains -Content $contractText -Needle $mindset -Path "skill/reference contract" -FailureCode "missing-canonical-mindset"
}
foreach ($legacyRole in $LegacyRoles) {
    Test-TextOmits -Content $contractText -Needle $legacyRole -Path "skill/reference contract" -FailureCode "legacy-role-contract"
}
foreach ($pair in $ExpectedPairings) {
    Test-PairingMention -Content $contractText -Left $pair[0] -Right $pair[1] -Path "skill/reference contract"
}

foreach ($contract in @(
    "First Blue",
    ".local\meetings",
    "paired roster",
    "pass plan",
    "pauses",
    "three paired",
    "Pass 1",
    "Paired Six Hats",
    "Pass 2",
    "Shuffle Review",
    "Pass 3",
    "Final Blue",
    "internal hat checkpoints",
    "meeting files",
    "events.jsonl",
    "pair continuity",
    "implementation lanes",
    "same pairs",
    "swap",
    "recruit",
    "Durable memory",
    "MEMORY.md"
)) {
    Test-TextContains -Content $contractText -Needle $contract -Path "skill/reference contract" -FailureCode "missing-behavior-contract"
}

foreach ($field in @(
    "Pair:",
    "Working question:",
    "Proposal:",
    "Why this is the right move:",
    "What we can help implement:",
    "Memory candidates:"
)) {
    Test-TextContains -Content $contractText -Needle $field -Path "skill/reference contract" -FailureCode "missing-visible-proposal-field"
}

foreach ($field in @(
    "meetingId",
    "timestamp",
    "pass",
    "hat",
    "speakerId",
    "speakerName",
    "pairId",
    "mindsets",
    "messageType",
    "visibility",
    "requestedModel",
    "actualModel",
    "memoryBackend",
    "text"
)) {
    Test-TextContains -Content $contractText -Needle $field -Path "events.jsonl contract" -FailureCode "missing-event-field"
}

foreach ($contract in @(
    "coding-agent-behavior-standard.md",
    "Coding Approval Gate",
    "all planning groups submitted proposals",
    "Blue/Logos approved the implementation phase",
    "consolidated P0-P3 tasklist",
    "Coding Report",
    "Fix Report",
    "Model Provenance",
    "Report Card",
    "Finding -> Implication -> Task",
    "OpenCode is the runner",
    "OpenRouter/free is only a model/provider source",
    "verified-opencode-agents.md",
    "opencode/deepseek-v4-flash-free",
    "opencode/mimo-v2.5-free",
    "opencode/minimax-m3-free",
    "openrouter/openai/gpt-oss-120b:free"
)) {
    Test-TextContains -Content $contractText -Needle $contract -Path "linear-thinking-coders contract" -FailureCode "missing-coder-behavior-contract"
}

Test-TemplateContracts -TemplateRoot $templateRoot

$starterRoot = Join-Path $PackageRoot "experts\starter"
$starterExperts = @(Get-ChildItem -LiteralPath $starterRoot -Directory -ErrorAction SilentlyContinue)
if ($starterExperts.Count -ne 6) {
    Add-Failure "starter-count`tExpected 6, found $($starterExperts.Count)"
}

$mindsetCounts = @{}
$defaultStarterCounts = @{}
foreach ($expert in $starterExperts) {
    Test-ExpertDirectory -Path $expert.FullName
    $agentsPath = Join-Path $expert.FullName "AGENTS.md"
    if (Test-Path -LiteralPath $agentsPath) {
        $content = Get-Content -Raw -LiteralPath $agentsPath
        $mindset = Get-MetadataField -Content $content -Field "Mindset"
        $defaultStarter = Get-MetadataField -Content $content -Field "Default starter"
        if ($mindset) {
            $mindsetCounts[$mindset] = 1 + [int]$mindsetCounts[$mindset]
        }
        if ($mindset -and $defaultStarter -eq "Yes") {
            $defaultStarterCounts[$mindset] = 1 + [int]$defaultStarterCounts[$mindset]
        }
    }
}

foreach ($mindset in $ExpectedMindsetQuestions.Keys) {
    if ([int]$mindsetCounts[$mindset] -ne 1) {
        Add-Failure "mindset-count`t$mindset`tExpected 1, found $([int]$mindsetCounts[$mindset])"
    }
    if ([int]$defaultStarterCounts[$mindset] -ne 1) {
        Add-Failure "default-starter-count`t$mindset`tExpected 1, found $([int]$defaultStarterCounts[$mindset])"
    }
}

$registryRoot = Join-Path $PackageRoot "registry\mymcp"
$registryPackets = @(Get-ChildItem -LiteralPath $registryRoot -Filter "*.json" -File -ErrorAction SilentlyContinue)
if ($registryPackets.Count -ne 2) {
    Add-Failure "registry-primary-count`tExpected 2 primary packets, found $($registryPackets.Count)"
}

foreach ($registryPacket in $registryPackets) {
    try {
        $json = Get-Content -Raw -LiteralPath $registryPacket.FullName | ConvertFrom-Json
        if ($json.slug -eq "linear-thinking-agents") {
            if (
                $json.id -ne "garbledhamster__linear-thinking-agents" -or
                $json.classifier -ne "PLANNING" -or
                $json.sourceOwner -ne "garbledhamster" -or
                $json.title -ne "linear-thinking-agents" -or
                $json.uri -ne "skills://PLANNING/garbledhamster/linear-thinking-agents" -or
                $json.repository -ne "https://github.com/garbledhamster/skills" -or
                $json.packagePath -ne "linear-thinking" -or
                $json.skillPath -ne "linear-thinking/skills/linear-thinking-agents"
            ) {
                Add-Failure "bad-registry-primary-packet`t$($registryPacket.FullName)"
            }
            if (-not $json.description -or $json.description -notmatch "three-pass" -or $json.description -notmatch "paired agents" -or $json.description -notmatch "JSONL" -or $json.description -notmatch "implementation lanes") {
                Add-Failure "registry-description-missing-contract`t$($registryPacket.FullName)"
            }

            $support = @($json.bundledSupport)
            if ($support.Count -ne 1 -or $support[0].slug -ne "linear-thinking-expert-builder" -or $support[0].role -ne "supporting") {
                Add-Failure "registry-supporting-builder-contract`t$($registryPacket.FullName)"
            }
        } elseif ($json.slug -eq "linear-thinking-coders") {
            if (
                $json.id -ne "garbledhamster__linear-thinking-coders" -or
                $json.classifier -ne "FRONTEND" -or
                $json.sourceOwner -ne "garbledhamster" -or
                $json.title -ne "linear-thinking-coders" -or
                $json.uri -ne "skills://FRONTEND/garbledhamster/linear-thinking-coders" -or
                $json.repository -ne "https://github.com/garbledhamster/skills" -or
                $json.packagePath -ne "linear-thinking" -or
                $json.skillPath -ne "linear-thinking/skills/linear-thinking-coders"
            ) {
                Add-Failure "bad-registry-primary-packet`t$($registryPacket.FullName)"
            }
            if (-not $json.description -or $json.description -notmatch "paired frontend" -or $json.description -notmatch "OpenCode" -or $json.description -notmatch "GPT-5.5" -or $json.description -notmatch "GPT-5.3-Codex-Spark") {
                Add-Failure "registry-description-missing-contract`t$($registryPacket.FullName)"
            }
        } else {
            Add-Failure "unexpected-registry-packet`t$($registryPacket.FullName)"
        }

        $raw = Get-Content -Raw -LiteralPath $registryPacket.FullName
        if ($raw -match "\.local|MEMORY\.md|meeting history|[\\/]\.?meetings[\\/]") {
            Add-Failure "registry-private-reference`t$($registryPacket.FullName)"
        }
    } catch {
        Add-Failure "invalid-registry-json`t$($registryPacket.FullName)`t$($_.Exception.Message)"
    }
}

$repoRoot = Split-Path $PackageRoot -Parent
$gitignorePath = Join-Path $repoRoot ".gitignore"
if (-not (Test-Path -LiteralPath $gitignorePath)) {
    Add-Failure "missing-gitignore`t$gitignorePath"
} else {
    $gitignore = Get-Content -Raw -LiteralPath $gitignorePath
    foreach ($pattern in @("linear-thinking/.local/", "**/MEMORY.md", "**/meetings/")) {
        if ($gitignore -notmatch [regex]::Escape($pattern)) {
            Add-Failure "missing-gitignore-pattern`t$pattern"
        }
    }
}

if (Get-Command git -ErrorAction SilentlyContinue) {
    foreach ($ignoredPath in @(
        "linear-thinking/.local/experts/example/MEMORY.md",
        "linear-thinking/.local/meetings/example/MEETING.md",
        "linear-thinking/.local/meetings/example/events.jsonl",
        "linear-thinking/experts/starter/example/MEMORY.md",
        "linear-thinking/experts/starter/example/meetings/session.md"
    )) {
        & git -C $repoRoot check-ignore -q -- $ignoredPath
        if ($LASTEXITCODE -ne 0) {
            Add-Failure "git-ignore-miss`t$ignoredPath"
        }
    }
}

Test-NewExpertScriptContract -ScriptPath (Join-Path $PackageRoot "scripts\New-LinearThinkingExpert.ps1")
Test-InstallScriptContract -ScriptPath (Join-Path $PackageRoot "scripts\Install-LinearThinkingSkills.ps1")

$runtimeSkillNames = @("linear-thinking-agents", "linear-thinking-expert-builder", "linear-thinking-coders")
$runtimeExists = $runtimeSkillNames | Where-Object { Test-Path -LiteralPath (Join-Path $RuntimeSkillRoot $_) }
if ($RequireRuntime -or $runtimeExists.Count -gt 0) {
    foreach ($skillName in $runtimeSkillNames) {
        $target = Join-Path $RuntimeSkillRoot $skillName
        if (-not (Test-Path -LiteralPath (Join-Path $target "SKILL.md"))) {
            Add-Failure "runtime-missing-skill`t$target"
        }
        if (-not (Test-Path -LiteralPath (Join-Path $target "references\hat-protocol.md"))) {
            Add-Failure "runtime-missing-reference`t$target"
        }
        if (-not (Test-Path -LiteralPath (Join-Path $target "experts\starter"))) {
            Add-Failure "runtime-missing-starter-experts`t$target"
        }
        if ($skillName -eq "linear-thinking-coders") {
            foreach ($requiredRuntimeReference in @(
                "references\coding-agent-behavior-standard.md",
                "references\verified-opencode-agents.md",
                "references\opencode-agent-backend.md"
            )) {
                if (-not (Test-Path -LiteralPath (Join-Path $target $requiredRuntimeReference))) {
                    Add-Failure "runtime-missing-coder-reference`t$target`t$requiredRuntimeReference"
                }
            }
        }
        $runtimeStarterCount = @(Get-ChildItem -LiteralPath (Join-Path $target "experts\starter") -Directory -ErrorAction SilentlyContinue).Count
        if ($runtimeStarterCount -ne 6) {
            Add-Failure "runtime-starter-count`t$target`tExpected 6, found $runtimeStarterCount"
        }
    }
}

if ($failures.Count -gt 0) {
    $failures
    Write-Error "Linear thinking skill validation failed with $($failures.Count) issue(s)."
    exit 1
}

"PASS linear thinking skill validation"
