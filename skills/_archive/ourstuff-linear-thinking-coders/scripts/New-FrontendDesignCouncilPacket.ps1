param(
  [Parameter(Mandatory = $true)]
  [string] $RepoPath,

  [Parameter(Mandatory = $true)]
  [string] $TargetSurface,

  [ValidateSet('auto-code', 'plan-only')]
  [string] $Mode = 'auto-code',

  [bool] $FreeOnly = $true,

  [string] $FrontendStack = '',

  [string] $Constraints = '',

  [string[]] $VerificationCommands = @()
)

$verifiedAgents = [ordered]@{
  workerSearchSummaries = [ordered]@{
    purpose = 'worker/search/summaries'
    preferredRole = 'GPT-OSS free worker fallback'
    modelId = 'openrouter/openai/gpt-oss-120b:free'
    smokePrompt = 'Say READY.'
  }
  longContextReader = [ordered]@{
    purpose = 'long-context reader'
    preferredRole = 'MiMo-V2.5'
    modelId = 'opencode/mimo-v2.5-free'
    smokePrompt = 'Say READY.'
  }
  builderCodeGeneration = [ordered]@{
    purpose = 'builder/code generation'
    preferredRole = 'MiniMax free builder'
    modelId = 'opencode/minimax-m3-free'
    smokePrompt = 'Say READY.'
  }
  reviewerValidator = [ordered]@{
    purpose = 'reviewer/validator'
    preferredRole = 'Qwen3.6 Plus free when verified; current verified fallback is GPT-OSS 120B free'
    modelId = 'openrouter/openai/gpt-oss-120b:free'
    smokePrompt = 'Say READY.'
  }
}

$packet = [ordered]@{
  name = 'frontend_design_council'
  repoPath = $RepoPath
  targetSurface = $TargetSurface
  mode = $Mode
  freeOnly = $FreeOnly
  frontendStack = $FrontendStack
  constraints = $Constraints
  verificationCommands = $VerificationCommands
  pairRequirement = [ordered]@{
    soloAgentsAllowed = $false
    appliesTo = @('implementation', 'review', 'corrective tickets', 'verification')
    invalidWhen = @('single owner', 'missing in-pair review', 'missing cross-review pair', 'unverified paid OpenCode model in free-only mode')
  }
  verifiedFreeAgents = $verifiedAgents
  codexCodingLane = [ordered]@{
    orchestratorInstructionModel = 'GPT-5.5/Blue/Logos'
    firstLineCodingModel = 'gpt-5.3-codex-spark'
    defaultReasoningEffort = 'high'
    escalationReasoningEffort = 'xhigh'
    escalationWhen = @('complex', 'risky', 'cross-module', 'architecture-sensitive', 'user-facing implementation')
    usageConservationDownshiftAllowed = $false
  }
  preflightCommands = @(
    'opencode --version',
    'opencode models',
    'opencode run --model "openrouter/openai/gpt-oss-120b:free" --dir "<repoPath>" "Say READY."',
    'opencode run --model "opencode/mimo-v2.5-free" --dir "<repoPath>" "Say READY."',
    'opencode run --model "opencode/minimax-m3-free" --dir "<repoPath>" "Say READY."',
    'opencode run --model "openrouter/openai/gpt-oss-120b:free" --dir "<repoPath>" "Say READY."'
  )
  prompts = [ordered]@{
    council = @(
      'Build Pair: Operator + Engineer. Focus on behavior, state/data flow, feasibility, implementation sequencing.',
      'Shape Pair: Architect + Strategist. Focus on information architecture, layout, component hierarchy, visual direction.',
      'Guardrail Pair: Steward + Philosopher. Focus on accessibility, maintainability, coherence, failure modes, long-term fit.'
    )
    ticketRule = 'You are working as a pair, not a solo agent. Apply both roles before editing. If the two role perspectives disagree, report the disagreement and choose the option that best satisfies the design doc and repo constraints.'
  }
  blueLogosFailureNotes = [ordered]@{
    required = $true
    fields = @('pair', 'ticketIds', 'failurePattern', 'evidence', 'impact', 'immediateCorrection', 'futureSkillGuidance', 'shouldBecomePermanentGuidance')
  }
  limits = @(
    'Host agent performs repo reads, edits, screenshots, browser checks, and final verification.',
    'Wrapper packet does not claim to run multi_agent_v1 or OpenCode by itself.',
    'Codex-backed coding lanes use GPT-5.3-Codex-Spark first when selectable, with GPT-5.5/Blue/Logos shaping exact instructions.',
    'Free-only mode rejects paid aliases and unverified model IDs.'
  )
}

$packet | ConvertTo-Json -Depth 8
