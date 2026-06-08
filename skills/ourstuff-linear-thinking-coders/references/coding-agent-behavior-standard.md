# Coding Agent Behavior Standard

Use this reference when `linear-thinking-coders` moves from design synthesis into implementation. Coding agents are structured project agents under Blue/Logos, not free-roaming helpers.

## Default Flow

```text
orchestrator defines mission
agent groups inspect and plan
agent groups submit proposals
agent groups review each other
orchestrator consolidates
orchestrator approves implementation
agent groups code assigned work
agent groups report changes
orchestrator performs final review
fix agents are deployed only if needed
```

## Core Rule

Agents propose, review, and implement approved work. Blue/Logos decides the project direction. No agent may skip from discovery directly into coding unless Blue/Logos has approved that phase.

## Required Planning Outputs

### Mission Understanding

Each group first restates:

- what the system is supposed to become
- its assigned area
- files, docs, code, configs, or workflows to inspect
- assumptions to verify
- definition of done

### Inspect Before Proposing

Each group inspects existing code, docs, config, data structures, CLI commands, tests, install/setup flow, user workflow, and likely failure points before recommending changes.

### Proposal

Each proposal must include current state, target state, recommended changes, risks, dependencies, acceptance criteria, and the first safe change.

### Cross-Review

Each review must identify agreements, conflicts, missing pieces, risks introduced by other proposals, and the recommended merge decision.

## Orchestrator Consolidation

Blue/Logos distills proposals into one tasklist. The tasklist is the working source of truth and must include:

- purpose
- current state
- target state
- gap analysis
- architecture direction
- implementation roadmap
- agent group assignments
- acceptance criteria
- final review checklist

Use priorities:

```text
P0 = required for usable system
P1 = required for integration
P2 = quality / validation improvement
P3 = future enhancement
```

## Coding Approval Gate

Agents may not code until all of these are true:

- all planning groups submitted proposals
- all planning groups completed cross-review
- Blue/Logos consolidated the tasklist
- Blue/Logos approved the implementation phase
- each coding group received a specific assignment

If any condition is missing, the coding group stops and asks for orchestration approval.

## Coding Phase

When coding is approved, each pair:

1. reads the approved tasklist
2. confirms its assigned section
3. inspects the affected files
4. makes the smallest safe change
5. preserves existing behavior unless the tasklist says otherwise
6. runs relevant validation
7. reports exactly what changed

## Pairing Model

Coding groups use two hats per group:

- Storage / Schema Group: White Hat + Black Hat
- MCP / Agent Interface Group: Blue Hat + Green Hat
- Product / Install / Validation Group: Yellow Hat + Red Hat

For frontend work, these map onto the existing Build, Shape, and Guardrail pairs unless Blue/Logos explicitly assigns a different pair structure.

## Distill-As-You-Go

Agents compress their work as they proceed. Prefer:

```text
Finding -> Implication -> Task
```

Do not bury decisions inside long prose.

## Memory / Context Rule

Before searching raw files or asking the user for background, agents query the available project memory system when one exists. Use raw files only when memory is missing, stale, low-confidence, or source verification is required.

## Model Provenance Rule

Every delegated pair records how it ran:

- task or ticket id
- phase
- pair and roles
- requested execution system and model
- actual execution system and model when known
- reasoning effort when known
- fallback reason when the requested model was not used
- artifacts touched
- checks run
- compact summary

If the runtime does not expose the actual model, write `unknown`. Do not infer actual Spark usage from instructions alone.

## Output Contracts

### Planning Output

```markdown
## Current State

## Target State

## Recommended Tasks

## Risks

## Dependencies

## Acceptance Criteria
```

### Cross-Review Output

```markdown
## Agreements

## Conflicts

## Missing Pieces

## Recommended Merge Decision
```

### Coding Output

```markdown
## Files Changed

## What Changed

## Validation

## Issues

## Ready for Review
```

### Fix Output

```markdown
## Issue Fixed

## Files Changed

## Validation

## Remaining Risk
```

## Final Review

Blue/Logos checks whether the implementation matched the approved tasklist, preserved existing behavior, documented commands, ran tests or smoke checks, remained understandable, and left no unresolved blocking risks.

Fix pairs repair only the specific issue assigned by Blue/Logos. They do not reopen architecture unless Blue/Logos explicitly says so.

## Report Cards

At completion, Blue/Logos grades every pair and itself as orchestrator. Grades are evidence labels for future prompt improvement, not praise. Each report card includes grade, evidence, what to keep doing, what to improve, and one future prompt instruction.
