---
name: project-init
description: Guides a project from raw idea to initialized context through bounded subagent handoffs using the canonical Project Flow. Use when starting a new project, preparing project context, running Scaffold/Constitution/Align/Language, keeping initialization contexts small, or invoking /project-init.
---

# Project Init

Use this wrapper to prepare the project shape and hand off to `idea-init`.

## Operating Model

The parent agent is an orchestrator only. Keep parent context below 160k tokens by reading minimal status, paths, and handoff summaries instead of loading long project transcripts, full source-skill bodies, or large project documents.

Default to bounded subagents for the work:

1. Start a Scaffold/Constitution subagent to prepare the canonical shape, ensure `project-context/ORIGINAL_IDEA.md`, pause for `/init`, and verify `AGENTS.md`.
2. Receive a compact handoff from the Scaffold/Constitution subagent.
3. Start an Align subagent to run or coordinate `grill-with-docs` and write `AGENT_ALIGNMENT.md`.
4. Receive a compact handoff from the Align subagent.
5. Start a Language subagent to run or coordinate `ubiquitous-language` and write glossary-only `CONTEXT.md`.
6. Receive the Language handoff, validate required files by path, and update project flow status.

If subagents are unavailable, continue locally only when the same context limits can be respected. Otherwise stop and ask the user to resume with a fresh agent using the current handoff.

## Context Budget

- Hard cap every agent at 160k context.
- Treat 120k as the planning limit for new reads.
- At 140k, stop expanding context and write a handoff.
- Preserve the Smart Window by keeping the parent out of deep alignment, transcript, and glossary work.
- Never paste full Original Ideas, alignment transcripts, source-skill bodies, or large project documents through parent chat when paths and a handoff summary are enough.
- Prefer file paths, status JSON, concise decisions, and blocker summaries over copied document bodies.

## Handoff Chain

Each worker subagent must use the `handoff` skill before finishing. The handoff must be concise and include:

- current phase: Scaffold/Constitution, Align, or Language
- artifacts written or changed
- decisions made
- user-only commands completed or still required
- blockers or open questions
- validation performed
- exact next agent prompt or next action

The parent reads the worker handoff, not the worker's full context. Before starting the next worker, the parent creates or forwards a short handoff prompt that includes only:

- project root
- relevant artifact paths
- current status
- previous worker handoff
- the next worker's bounded objective

## Workflow

1. Ensure the canonical project shape exists.
2. Ensure `project-context/ORIGINAL_IDEA.md` exists.
3. If the file is missing, create it and stop.
4. If the file is empty, stop and ask the user to fill it.
5. Pause for `/init` before constitution work.
6. Resume only after `AGENTS.md` exists.
7. Dispatch an Align subagent to coordinate `grill-with-docs`, write `AGENT_ALIGNMENT.md`, validate the artifact path, and return a handoff.
8. Dispatch a Language subagent with the Align handoff to coordinate `ubiquitous-language`, keep `CONTEXT.md` glossary-only, validate the artifact path, and return a handoff.
9. Parent validates required artifact paths without loading full contents unless validation fails.
10. Update project flow status for readiness to run `/idea-init`.

## Gates

- Do not continue past an empty `ORIGINAL_IDEA.md`.
- Do not simulate `/init`.
- Do not write outside the canonical project shape.
- Do not let parent context become the initialization workspace.
- Do not start a follow-on worker without a handoff from the previous worker.
- If any worker approaches the 160k cap, it must stop, write a handoff, and provide the next-agent prompt.

## Public Artifacts

- `AGENTS.md`
- `AGENT_ALIGNMENT.md`
- `CONTEXT.md`
- `project-context/ORIGINAL_IDEA.md`
- `/.agents/project-flow-status.json`

## Status Updates

- Record phase, blocked state, next command, and written artifacts.
- Record latest Scaffold/Constitution, Align, and Language handoff paths or summaries when available.
- Mark the project ready for `/idea-init` only after all handoff files exist.

## Memory Layer

- Optional only.
- Use CLI/scripts only if available.
- Never require it for project init completion.
- Parent may use memory lookup for a narrow context pack, but worker subagents own deep reads.

## Companion Skills

- `grill-with-docs`
- `ubiquitous-language`
- `handoff`
