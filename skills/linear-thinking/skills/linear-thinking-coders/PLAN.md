# Build `linear-thinking-coders`

## Summary

Create a new local skill at `C:\Users\jrice\.agents\skills\linear-thinking-coders` that bootstraps itself: it defines a frontend UI specialist workflow, then immediately uses that workflow to review and refine its own skill design before it is considered done.

The skill will synthesize `linear-thinking-agents`, `spark-worker-orchestrator`, `impeccable`, `design-review`, `tailwind-design-system`, and product UI skills into one repeatable design-to-code protocol.

Best MCP type: skill-first orchestration with an MCP prompt/tool wrapper plan, not a direct side-effectful MCP tool in v0. The host agent must own repo reads, subagent spawning, file edits, screenshots, and final verification.

## Key Changes

- Add `linear-thinking-coders/SKILL.md` with triggers for "frontend redesign council," "linear thinking coders," "UI specialist agents," "design doc then code," and "review each other then implement."
- Add references:
  - `references/workflow.md`: end-to-end protocol.
  - `references/frontend-specialist-roster.md`: paired design/coding lanes.
  - `references/design-doc-template.md`: final synthesized design doc.
  - `references/coder-ticket-template.md`: exact worker ticket and review-ticket format.
  - `references/mcp-wrapper.md`: future garbledhamster MCP function spec.
- Add `agents/openai.yaml` with a short display name, default prompt, and `multi_agent_v1` dependency metadata.

## Workflow To Encode

- Phase 0, self-hosted seed: create the initial skill files, then load the just-created skill directly from disk and run its own protocol against itself.
- Phase 1, discovery: inspect repo instructions, current UI files, design tokens, screenshots/dev server if available, frontend stack, and validation commands.
- Phase 2, linear design council: Blue/Logos orchestrator runs three paired agents:
  - Build Pair: Operator + Engineer, interaction model, code feasibility, implementation lanes.
  - Shape Pair: Architect + Strategist, information architecture, visual direction, component system.
  - Guardrail Pair: Steward + Philosopher, accessibility, maintainability, brand coherence, risk.
- Phase 3, shuffle review: each pair critiques another pair's proposal, clarifies it, and adds concrete recommendations.
- Phase 4, final design doc: Blue/Logos produces a single decision-complete design doc with target UI behavior, component hierarchy, token/theme direction, responsive rules, acceptance checks, and implementation lanes.
- Phase 5, auto-code: because the chosen default is Auto-code, Blue/Logos immediately converts the design doc into exact tickets and dispatches coding pairs/workers with disjoint write scopes.
- Phase 6, cross-review: pairs review each other's work before integration; the orchestrator issues corrective tickets where needed.
- Phase 7, final verification: orchestrator runs local checks, browser/screenshot checks when applicable, and repo-specific finish-line checks.

## MCP Wrapper Plan

- Do not modify `skill-registry-mcp` for v0; it is currently an approved-skill registry and read-only MCP surface.
- Define the future garbledhamster MCP wrapper as a prompt-style orchestration function named `frontend_design_council`.
- Inputs: `repoPath`, `targetSurface`, `mode` default `auto-code`, `frontendStack` optional, `constraints` optional, `verificationCommands` optional.
- Output: an orchestration packet containing discovery checklist, paired-agent prompts, design-doc template, coder-ticket templates, and final verification checklist.
- Host agent remains responsible for calling `multi_agent_v1.spawn_agent`, applying edits, and verifying results.

## Test Plan

- Validate skill structure with `Get-AgentSkillInventory.ps1` and `Test-AgentSkillDrift.ps1`.
- Confirm `SKILL.md` has valid frontmatter, concise trigger description, and no duplicate active skill name.
- Dry-run the self-host protocol on `linear-thinking-coders` itself:
  - produce a design/review note for the skill,
  - identify missing workflow clarity,
  - patch the skill once based on its own critique,
  - rerun drift checks.
- Optional forward test on a frontend repo: invoke the skill against one known UI surface and confirm it creates a design doc plus disjoint coding tickets before editing.

## Assumptions

- Canonical install path is `C:\Users\jrice\.agents\skills\linear-thinking-coders`.
- The skill is framework-neutral by default and loads Tailwind/shadcn guidance only when the target repo uses it.
- Auto-code is the default after final design synthesis; no approval pause unless the user asks for one.
- The current `multi_agent_v1` tool does not expose explicit model selection, so the skill will describe roles and prompt quality rather than requiring specific model parameters.
