# Linear Thinking Coders Update Plan

## Purpose

Update `linear-thinking-coders` so coding work follows the structured path in `C:\Users\jrice\.agents\skills\linear-thinking-coders\UPDATE.md`: memory/context first, mission understanding, inspection, proposals, cross-review, Blue/Logos consolidation, approval gate, paired small patches, coding reports, final review, and focused fix pairs.

## Current State

- Source package lives in `linear-thinking\` inside this repo.
- Active runtime installs into `C:\Users\jrice\.agents\skills`.
- Existing source edits already add GPT-5.5/Blue/Logos instruction shaping and GPT-5.3-Codex-Spark coding-lane routing.
- Runtime has extra OpenCode verified-free guidance that must stay aligned with source.

## Target State

- `linear-thinking-coders` has a packaged reference for the structured coding-agent behavior standard.
- Skill workflow and templates make the coding approval gate explicit before any worker edits.
- Tickets and reports use pair-owned outputs and `Finding -> Implication -> Task` style where useful.
- Source and runtime copies match after installation.

## Implementation Roadmap

- [x] P0 Add `references\coding-agent-behavior-standard.md` from `UPDATE.md`.
- [x] P0 Update `SKILL.md` and `references\workflow.md` to require the approval-gated coding path.
- [x] P0 Update `references\design-doc-template.md` and `references\coder-ticket-template.md` with mission, inspection, proposal, cross-review, consolidated tasklist, approval, coding report, and fix report fields.
- [x] P1 Update README, registry description, and validation script checks for the new behavior standard.
- [x] P1 Backport runtime-only OpenCode/free reference files into source when missing, including `verified-opencode-agents.md`.
- [x] P1 Install source package into runtime with `Install-LinearThinkingSkills.ps1`.
- [x] P2 Record final evidence through Local AI Brain if health passes.

## Agent Group Assignments

- Build Pair: Operator + Engineer owns workflow and ticket mechanics.
- Shape Pair: Architect + Strategist owns package/reference structure and public descriptions.
- Guardrail Pair: Steward + Philosopher owns validation, drift checks, and source/runtime safety.

## Acceptance Criteria

- Coding cannot begin until proposals, cross-review, consolidated tasklist, and Blue/Logos approval are represented in the skill contract.
- `references\coding-agent-behavior-standard.md` is present in source and runtime.
- `references\verified-opencode-agents.md` is present in source and runtime.
- Every implementation, review, and corrective task stays pair-owned.
- GPT-5.5/Blue/Logos remains instruction shaper and final reviewer.
- GPT-5.3-Codex-Spark remains first-line Codex coding model with `high` or `xhigh` reasoning when selectable.
- OpenCode helper runs remain OpenCode runs, with OpenRouter/free only a provider/model source.
- Source and runtime copies pass validation and drift checks.

## Final Review Checklist

- `Test-LinearThinkingSkills.ps1 -RequireRuntime` passes.
- `Get-AgentSkillInventory.ps1` passes.
- `Test-AgentSkillDrift.ps1` passes.
- Registry JSON parses.
- Final diff contains no private `.local`, `MEMORY.md`, or meeting-history data.
