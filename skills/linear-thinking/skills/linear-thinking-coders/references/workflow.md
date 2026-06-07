# Linear Thinking Coders Workflow

Default mode is `auto-code` after the coding approval gate is complete. This workflow implements `references/coding-agent-behavior-standard.md` for frontend and skill-maintenance work.

Non-negotiable rule: there are always pairs. No solo implementation agents, no solo review agents, and no solo corrective agents. Blue/Logos owns coordination, model provenance capture, failure-note capture, report cards, and conversion of recurring mistakes into future skill guidance.

## Phase 0: Self-Hosted Seed

Use when bootstrapping or revising this skill.

1. Create or update the skill files.
2. Load the local `SKILL.md` and references directly from disk.
3. Run this workflow against the skill itself.
4. Produce one critique pass focused on unclear triggers, weak phases, missing verification, ambiguous pair responsibilities, and missing team failure guidance.
5. Patch once from the critique.
6. Run skill inventory and drift checks.

## Phase 1: Mission Understanding

Each pair restates the mission before inspecting files.

Blue/Logos also chooses the active memory lane. Use Local AI Brain when available; otherwise create or reuse `.agent-memory/<repo-or-project>/`. The lane must store model provenance for every delegated pair and final report cards before completion.

Output:

```markdown
## Mission Understanding

## Assigned Area

## Files / Systems to Inspect

## Assumptions to Verify

## Definition of Done
```

## Phase 2: Inspect Before Proposing

Collect only evidence needed for the target UI/code surface. Inspect repo instructions, target files, routes, components, styles, tokens, design system, screenshots, frontend stack, package scripts, validation commands, current behavior, layout constraints, known user requirements, and failure points.

Output:

```markdown
## Current State Findings

| Area | Found | Notes |
| --- | --- | --- |
```

## Phase 3: Linear Design Council Proposals

Blue/Logos acts as orchestrator and spawns three paired design agents:

- Build Pair: Operator + Engineer, focused on interaction model, state/data flow, implementation lanes, and feasibility risks.
- Shape Pair: Architect + Strategist, focused on information architecture, layout system, component hierarchy, and visual direction.
- Guardrail Pair: Steward + Philosopher, focused on accessibility, maintainability, brand coherence, failure states, and edge cases.

Each pair returns current state, target state, recommended UI behavior, component changes, responsive rules, implementation notes, risks, dependencies, acceptance checks, and first safe change.

When OpenCode is configured as the backend, GPT-5.5/Blue/Logos remains the orchestrator and instruction shaper. OpenCode agents may serve as pair heads for the thinking lanes, but Blue/Logos must validate their output before synthesis.

## Phase 4: Shuffle Review

Each pair reviews another pair's proposal:

- Build reviews Shape.
- Shape reviews Guardrail.
- Guardrail reviews Build.

Each review must produce agreements, conflicts, missing pieces, risks added by other proposals, concrete objections, simplifications, implementation corrections, and a recommended merge decision.

## Phase 5: Blue/Logos Consolidation

Blue/Logos merges council output into one decision-complete design doc. Use `design-doc-template.md`.

The design doc must include target surface and user goal, mission understanding, current-state findings, final UI behavior, component hierarchy, layout and responsive rules, token/theme direction, accessibility requirements, state/loading/empty/error behavior, files likely to change, consolidated P0-P3 tasklist, paired implementation lanes, acceptance checks, verification commands, pair performance notes, and future skill guidance.

## Phase 6: Coding Approval Gate

Blue/Logos may not dispatch coding until all gate conditions are true:

- all planning groups submitted proposals
- all planning groups completed cross-review
- Blue/Logos consolidated the tasklist
- Blue/Logos approved the implementation phase
- each coding group received a specific assignment

If any condition is missing, stop before edits and ask for orchestration approval.

## Phase 7: Paired Coding

If the user requested OpenCode agents, load `opencode-agent-backend.md` before dispatch. In free-only mode, also load `verified-opencode-agents.md`. OpenCode failure falls back to a Codex Spark coding lane first while preserving pair roles, using GPT-5.3-Codex-Spark (`gpt-5.3-codex-spark`) with `high` or `xhigh` reasoning when selectable, with GPT-5.5/Blue/Logos retaining orchestration and review.

Blue/Logos converts the approved design doc and tasklist into paired coding tickets and dispatches paired workers or role-simulated pairs with disjoint write scopes.

Before each dispatch, Blue/Logos records the requested execution system, requested model, requested reasoning effort, pair id, phase, ticket id, and memory destination. After each pair returns, Blue/Logos records the actual execution system/model when known, fallback reason if any, artifacts, checks run, and a compact summary. If the runtime does not reveal the actual model, write `actual model: unknown`.

Rules:

- Tickets must name an `Owner Pair` and `Reviewer Pair`.
- Workers do not share write scopes.
- Shared files require orchestrator sequencing.
- Workers may read broadly but edit narrowly.
- Workers must make small reviewable patches.
- Workers must return the structured Coding Report from `coder-ticket-template.md`.
- Workers must report changed files, checks run, unresolved concerns, and both pair perspectives.
- The orchestrator integrates worker output and resolves conflicts.

Auto-code continues only after the approval gate. Pause before coding when the user requested plan-only mode, repo state makes safe edits impossible, required access is missing, destructive operations would be needed, the approval gate is incomplete, or the target surface is ambiguous enough that implementation would likely be wrong.

## Phase 8: Cross-Review And Final Review

Before final integration, pairs review each other's implementation for design doc compliance, responsive behavior, accessibility, state coverage, code maintainability, unintended file changes, missing tests, and weak verification evidence.

Blue/Logos performs the orchestrator final review from `coding-agent-behavior-standard.md`, records pair failure notes, and issues corrective tickets for blocking findings.

Blue/Logos maintains a report-card draft for each pair during review. The draft must be evidence-based and updated after corrective tickets or final verification.

## Phase 9: Focused Fix Pairs

Corrective pairs repair only the specific issue assigned by Blue/Logos. They do not reopen the whole design or architecture unless Blue/Logos explicitly approves that scope.

## Phase 10: Final Verification

Run the strongest practical verification available:

- repo-specific lint/type/test/build checks
- targeted tests for changed behavior
- browser verification for frontend UI
- screenshot checks for visual or responsive work
- finish-line checks from repo instructions or local utility scripts

For visual work, verify desktop and mobile viewports, no text overflow, no incoherent overlap, expected interaction states, and relevant loading, empty, and error states.

Final output must include changed files, verification commands and results, screenshots or browser checks performed, model provenance summary, pair report cards, pair failure notes, proposed future skill guidance, unresolved risks, and completion status.

## Report Card Format

Use this format in Local AI Brain records, repo-local memory files, and final design docs:

```markdown
### Report Card: <agent or pair>

- `Phase:`
- `Requested model:`
- `Actual model:` unknown if not exposed
- `Grade:` A | B | C | D | F
- `Evidence:`
- `Keep doing:`
- `Improve next time:`
- `Future prompt instruction:`
```
