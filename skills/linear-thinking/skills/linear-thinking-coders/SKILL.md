---
name: linear-thinking-coders
description: Orchestrates paired frontend design councils that synthesize a final design doc, auto-code it with paired coding lanes, cross-review implementation work, and capture team failure notes for future skill improvement. Use when the user asks for linear thinking coders, frontend redesign agents, UI specialist teams, design doc then code, paired review, or group critique before implementation.
---

# Linear Thinking Coders

## Purpose

Use this skill to turn frontend redesign work into a paired design-and-code council. Blue/Logos orchestrates discovery, three paired reviews, final design synthesis, paired coding tickets, cross-review, and verification.

Default mode is `auto-code`: after the final design doc is complete, immediately create paired coding tickets and implement unless the user explicitly asks for plan-only mode.

## Required References

Load these in order:

1. `references/workflow.md`
2. `references/frontend-specialist-roster.md`
3. `references/design-doc-template.md`
4. `references/coder-ticket-template.md`
5. `references/self-critique-checklist.md`
6. `references/coding-agent-behavior-standard.md`

Load `references/opencode-agent-backend.md` when the user asks to deploy OpenCode agents, use OpenRouter/free models, use OSS/free models, or use OpenCode CLI as the worker backend.
Load `references/verified-opencode-agents.md` immediately after `references/opencode-agent-backend.md` when the user asks for free/free-credit OpenCode models, OpenRouter/free models through OpenCode, or verified helper agents.
Load `references/mcp-wrapper.md` only when designing or exposing a garbledhamster MCP wrapper.

## Hard Rules

- Non-negotiable rule: there are always pairs. No solo implementation agents, no solo review agents, and no solo corrective agents.
- Before beginning a non-trivial run, query Local AI Brain with `context-pack` when `C:\Users\jrice\.agents\tools\local-ai-brain` is available.
- Before dispatching paired planning, coding, review, or corrective agents, start or reference a shared memory run when Local AI Brain is available. If it is not available, create a repo-local flat-file memory lane such as `.agent-memory/<repo-or-project>/`.
- Every dispatched pair must record model provenance in the active memory lane: task/ticket id, pair, phase, requested execution system, requested model, actual execution system/model when known, reasoning effort, fallback reason, artifacts, checks run, and summary.
- If the actual model is not exposed by the runtime, record `actual model: unknown`; do not infer Spark usage from a prompt or instruction.
- Record final design docs, implementation tickets, review tickets, corrective tickets, verification evidence, pair failure notes, and future skill guidance through Local AI Brain when capture health passes.
- Record final Blue/Logos report cards for every planning pair, coding pair, review pair, corrective pair, and the orchestrator. Report cards must use evidence from outputs, diffs, checks, and review findings.
- Do not hand-write SQL for Local AI Brain. Use its CLI wrapper or Python module, and store full artifacts as files.
- Coding requires the approval gate in `references/coding-agent-behavior-standard.md`. Agents may not edit until all proposals are submitted, all cross-reviews are complete, Blue/Logos has consolidated the tasklist, Blue/Logos has approved implementation, and each coding group has a specific assignment.
- If only one callable worker is available for a lane, the ticket must explicitly simulate both roles and require both perspectives before edits.
- Blue/Logos owns orchestration, final synthesis, model provenance, team failure notes, report cards, ticket sequencing, integration, and final verification.
- GPT-5.5/Blue/Logos is the orchestrator, instruction shaper, reviewer, integration owner, and fallback executor when a delegated lane is unavailable or returns unusable output.
- GPT-5.3-Codex-Spark (`gpt-5.3-codex-spark`) is the first-line Codex coding model for implementation lanes whenever explicit model selection is available.
- Spark coding lanes use reasoning effort `high` by default. Use `xhigh` for complex, risky, cross-module, architecture-sensitive, or user-facing implementation work. Do not downshift Spark reasoning for usage conservation.
- GPT-5.5 should hand Spark exact paired-ticket instructions: owner pair, both role perspectives, write scope, forbidden files, acceptance checks, verification commands, and review criteria.
- If Spark is unavailable, unsuitable, or cannot be selected, GPT-5.5/Blue/Logos takes the lane back while preserving the pair roles.
- When OpenCode agents are used, OpenCode is the runner and OpenRouter/free is only a model/provider source. Do not describe these as "OpenRouter agents."
- OpenCode-backed runs must follow the role model map in `references/opencode-agent-backend.md`: DeepSeek V4 Flash for worker-drone throughput, MiMo-V2.5 for research, MiniMax M2.7 for building, and Qwen3.6 Plus for review.
- When the user asks for free/free-credit OpenCode agents or OpenRouter/free models, dispatch only verified free model IDs through `opencode run` from `references/verified-opencode-agents.md`. A model ID must contain `:free` or end in `-free`, pass the local smoke test, and be assigned only to its documented purpose.
- Never use paid OpenCode aliases for a free-only run. If the requested role model is unavailable, unverified, blocked, or not free-labeled, record a backend failure note and use a verified free fallback for that purpose when one is listed; otherwise keep the lane with Blue/Logos/Codex instead of spending OpenCode credits.
- Pairs may read broadly but edit narrowly.
- Shared files require orchestrator sequencing.
- The final answer must report changed files, checks run, browser or screenshot evidence where applicable, model provenance summary, pair report cards, pair failure notes, future skill guidance, remaining risks, and completion status.

## Workflow

1. Query Local AI Brain when available, start or reference the active memory lane, then inspect repo instructions, target UI files, frontend stack, design tokens, screenshots/dev server availability, and validation commands.
2. Run Mission Understanding for each pair: assigned area, files/systems to inspect, assumptions to verify, and definition of done.
3. Run Inspect Before Proposing for each pair and record current-state findings.
4. Run the linear design council:
   - Build Pair: Operator + Engineer
   - Shape Pair: Architect + Strategist
   - Guardrail Pair: Steward + Philosopher
5. Each pair produces a proposal with current state, target state, recommended changes, risks, dependencies, acceptance criteria, and first safe change.
6. Run shuffle review:
   - Build reviews Shape
   - Shape reviews Guardrail
   - Guardrail reviews Build
7. Blue/Logos records pair failure notes throughout the run.
8. Blue/Logos synthesizes one final design doc and consolidated tasklist with P0-P3 priorities, target behavior, component hierarchy, responsive rules, theme/token direction, accessibility requirements, implementation lanes, acceptance checks, and verification commands.
9. Blue/Logos checks the coding approval gate before dispatch.
10. After approval, convert the design doc into paired coding tickets with disjoint write scopes.
11. Dispatch paired coding workers, OpenCode-backed pairs, or role-simulated pairs for small reviewable patches.
12. Require each pair to return a structured coding report, then cross-review worker output before integration.
13. Issue focused corrective tickets only for blocking review findings; fix pairs repair the specific issue and do not reopen the whole design.
14. Run final verification with repo checks, browser checks, mobile/desktop screenshots for UI work, and repo-specific finish-line checks.
15. Create final report cards for every pair and the orchestrator, then save them to Local AI Brain or the repo-local memory lane.
16. Convert repeated or high-impact pair failures into proposed future skill guidance and record them in Local AI Brain when capture health passes.

Auto-code remains the default after the approval gate is satisfied. Pause before implementation when the user requested plan-only mode, required access is missing, destructive operations would be needed, the approval gate is incomplete, or the target surface is too ambiguous to edit safely.

## Self-Hosted Bootstrap

When building or revising this skill, run the workflow against the skill itself:

1. Create or update the skill files.
2. Read the local `SKILL.md` and references from disk.
3. Run the paired critique on the skill's own clarity, triggers, ticket rules, pair invariants, and verification path.
4. Patch once from the critique.
5. Run `C:\Users\jrice\.agents\tools\skill-admin\Get-AgentSkillInventory.ps1`.
6. Run `C:\Users\jrice\.agents\tools\skill-admin\Test-AgentSkillDrift.ps1`.
