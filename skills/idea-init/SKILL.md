---
name: idea-init
description: Maps an initialized project into PRD, Destination, and AFK-ready Vertical Slices through bounded subagent handoffs. Use when turning project context into implementation plans, running Map/Task, keeping planning contexts small, or invoking /idea-init.
---

# Idea Init

Use this wrapper after `project-init` is complete.

## Operating Model

The parent agent is an orchestrator only. Keep parent context below 160k tokens by reading minimal status, paths, and handoff summaries instead of loading source skills or large planning artifacts.

Default to subagents for the work:

1. Start a Map subagent to run or coordinate `to-prd`.
2. Receive a compact handoff from the Map subagent.
3. Start a Task subagent to run or coordinate `to-issues`.
4. Receive a compact handoff from the Task subagent.
5. Validate required files by path and update project flow status.

If subagents are unavailable, continue locally only when the same context limits can be respected. Otherwise stop and ask the user to resume with a fresh agent using the current handoff.

## Context Budget

- Hard cap every agent at 160k context.
- Treat 120k as the planning limit for new reads.
- At 140k, stop expanding context and write a handoff.
- Never paste full PRDs, Original Ideas, Vertical Slices, or source-skill bodies through parent chat when a path and handoff summary are enough.
- Prefer file paths, status JSON, and concise decisions over copied document bodies.

## Handoff Chain

Each worker subagent must use the `handoff` skill before finishing. The handoff must be concise and include:

- current phase: Map or Task
- artifacts written or changed
- decisions made
- open questions or blockers
- validation performed
- exact next agent prompt or next action

The parent reads the worker handoff, not the worker's full context. Before starting the next worker, the parent creates or forwards a short handoff prompt that includes only:

- project root
- relevant artifact paths
- current status
- previous worker handoff
- the next worker's bounded objective

## Workflow

1. Validate initialized project artifacts and project flow status.
2. Dispatch the Map subagent.
3. Map subagent coordinates `to-prd`, writes the full PRD to `/.agents/plans/000_prd.md`, writes the distilled Destination to `DESIGN_CONCEPT.md`, validates both files, and returns a handoff.
4. Parent validates Map artifact paths without loading the full PRD unless validation fails.
5. Dispatch the Task subagent with the Map handoff and artifact paths.
6. Task subagent coordinates `to-issues`, publishes approved Vertical Slices as numbered flat files in `/.agents/plans/`, validates slice format, and returns a handoff.
7. Parent validates Task artifact paths and updates status for readiness to run `/project-execute`.

## Gates

- Do not run Map or Task on an uninitialized project.
- Do not publish slices before they are approved.
- Keep Vertical Slice docs behavior-first and avoid brittle path assumptions.
- Do not let parent context become the planning workspace.
- Do not start a follow-on subagent without a handoff from the previous worker.
- If a worker approaches the 160k cap, it must stop, write a handoff, and provide the next-agent prompt.

## Public Artifacts

- `DESIGN_CONCEPT.md`
- `/.agents/plans/000_prd.md`
- `/.agents/plans/NNN_slug.md`
- `/.agents/project-flow-status.json`

## Status Updates

- Record PRD, Destination, and slice paths.
- Record the latest Map and Task handoff paths or summaries when available.
- Mark ready for `/project-execute` only after approved slices exist.

## Memory Layer

- Optional only.
- Use CLI/scripts only if available.
- Never block on missing memory tooling.
- Parent may use memory lookup for a narrow context pack, but worker subagents own deep reads.

## Companion Skills

- `to-prd`
- `to-issues`
- `handoff`
