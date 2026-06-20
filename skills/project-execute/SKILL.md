---
name: project-execute
description: Runs approved Vertical Slices through bounded subagent execution, Smart Zone monitoring, review, and audit handoffs. Use when executing prepared project plans, running TDD batches, reviewing implementation, auditing against the Original Idea, keeping implementation contexts small, or invoking /project-execute.
---

# Project Execute

Use this wrapper to run approved slices through implementation, review, and audit.

## Operating Model

The parent agent is an orchestrator only. Keep parent context below 160k tokens by reading minimal status, paths, and handoff summaries instead of loading full PRDs, full slice bodies, large diffs, review transcripts, or audit working context.

Default to bounded subagents for the work:

1. Start an Execution Batch subagent for the approved Vertical Slices.
2. Receive a compact handoff from the Execution Batch subagent.
3. Start a Review subagent with the execution handoff and artifact paths.
4. Receive a compact handoff from the Review subagent.
5. Start an Audit subagent after Review Confidence reaches `5/5` or the user overrides.
6. Receive the audit handoff, validate artifact paths, and update project flow status.

If a batch needs multiple passes, start a fresh bounded worker for each pass. The parent passes only the latest handoff, status, paths, and objective to the next worker.

If subagents are unavailable, continue locally only when the same context limits can be respected. Otherwise stop and ask the user to resume with a fresh agent using the current handoff.

## Context Budget

- Hard cap every agent at 160k context.
- Treat 120k as the planning limit for new reads.
- At 140k, stop expanding context and write a handoff.
- Preserve the Smart Zone hard stop at 50 percent context usage when the runtime exposes context usage.
- Never paste full PRDs, Original Ideas, Vertical Slices, diffs, test logs, review transcripts, or audit notes through parent chat when paths and a handoff summary are enough.
- Prefer file paths, status JSON, concise decisions, check commands, and result summaries over copied document bodies.

## Handoff Chain

Each worker subagent must use the `handoff` skill before finishing. The handoff must be concise and include:

- current phase: Execution Batch, Review, or Audit
- active Vertical Slice paths and statuses
- files changed or artifacts written
- commands/checks run and summarized results
- decisions made
- blockers, risks, or unresolved review findings
- Review Confidence when applicable
- exact next agent prompt or next action

The parent reads the worker handoff, not the worker's full context. Before starting the next worker, the parent creates or forwards a short handoff prompt that includes only:

- project root
- relevant artifact paths
- current status
- approved batch
- previous worker handoff
- the next worker's bounded objective

## Workflow

1. Validate ready-for-execute status and load incomplete AFK slices.
2. Record model cap and reasoning cap before delegation.
3. Reject GPT-5.5 with `xhigh` reasoning.
4. Propose an execution batch, default size `3`.
5. Ask for user approval before the batch starts.
6. Dispatch an Execution Batch subagent to run TDD red-green-refactor work and return a handoff.
7. Parent validates changed artifact paths and check summaries without loading full logs unless validation fails.
8. Dispatch a Review subagent to run `review`, assess spec match, and assign Review Confidence.
9. Repeat with fresh bounded Execution or Review workers until Review Confidence is `5/5` or the user overrides.
10. Dispatch an Audit subagent to run `zoom-out`, compare against Original Idea, Destination, PRD, and completed slices, then write a durable audit file.
11. Parent validates audit artifact paths and marks execution complete.

## Gates

- Do not execute without batch approval.
- Do not continue past the Smart Zone stop.
- Do not accept GPT-5.5 `xhigh` for routine work.
- Do not finish without review and zoom-out audit evidence.
- Do not let parent context become the implementation workspace.
- Do not start a follow-on worker without a handoff from the previous worker.
- If any worker approaches the 160k cap, it must stop, write a handoff, and provide the next-agent prompt.

## Public Artifacts

- `/.agents/project-flow-status.json`
- `/.agents/audits/NNN_zoom-out-audit.md`
- `/.agents/plans/NNN_slug.md`

## Status Updates

- Record active batch, model cap, reasoning cap, review confidence, and next command.
- Record latest Execution, Review, and Audit handoff paths or summaries when available.
- Preserve `/clear` when Smart Zone is hit.

## Review Confidence

- Base the score on tests, review findings, spec match, blockers, and audit result.
- Allow user override and record it in status.

## Memory Layer

- Optional only.
- Use CLI/scripts only if available.
- Never use raw database access.
- Parent may use memory lookup for a narrow context pack, but worker subagents own deep reads.

## Companion Skills

- `tdd`
- `review`
- `zoom-out`
- `handoff`
