---
name: linear-thinking-agents
description: Runs three-pass linear thinking meetings with six mindsets in three paired agents. Use when the user says "linear thinking agents", "six hats", "thinking hats", "roundtable", "run the hats", or asks for a staged expert meeting.
---

# Linear Thinking Agents

Use this skill to run a staged expert meeting with one orchestrator and three paired expert agents.

## Startup

1. Load `references/hat-protocol.md` and `references/meeting-flow.md`.
2. Start every meeting with Blue/Logos as the orchestrator.
3. First Blue/Logos creates and announces `.local\meetings\<date-slug>\` before expert work starts.
4. First Blue/Logos proposes the paired roster and three-pass plan, then pauses for user edits before running paired experts.
5. Use no more than four live agents: the Blue/Logos orchestrator plus three paired agents.
6. If the topic needs expertise not represented by the six mindsets, use the expert-builder workflow to recruit a local expert under `.local` before paired work starts.
7. Create a model provenance ledger for the meeting before dispatching paired agents. Use Local AI Brain when available; otherwise write the ledger into the meeting folder.

## Mindsets And Pairs

The six canonical mindsets are:

- Operator
- Engineer
- Architect
- Strategist
- Steward
- Philosopher

Default pairs:

- Operator + Engineer
- Architect + Strategist
- Steward + Philosopher

Dynamic pair overrides are allowed only when first Blue/Logos explains why the default pairings would weaken the meeting.

## Three Passes

### Pass 1: Paired Six Hats

Each paired agent internally runs all six hats for its working question. Only the final paired proposal is visible in chat. Save compact internal hat checkpoints to the meeting files.

Each visible proposal must use this stable format:

```text
Pair:
Working question:

Proposal:

Why this is the right move:

What we can help implement:
- 
- 
- 

Memory candidates:
- 
```

### Pass 2: Shuffle Review

Shuffle the pairs so each paired agent reviews another pair's proposal. Each shuffle review must:

- critique the proposal
- clarify what the reviewers think the proposal means
- append a short change proposal if they find an improvement
- add memory candidates only when the lesson changes future expert behavior

### Pass 3: Final Blue Synthesis

Final Blue/Logos resolves the meeting into the requested artifact: decision, design plan, implementation plan, or final answer. Final Blue/Logos verifies the result against the user's request, names remaining uncertainties, decides which memory candidates are durable, writes approved local `MEMORY.md` updates, and reports exact files changed plus exact summaries saved.

Final Blue/Logos also grades each paired agent and the orchestrator with a compact report card saved to the active memory lane. Each report card must name evidence, grade the usefulness of the work, state what the agent should keep doing, state what to improve, and provide one future prompt instruction for zero-shot improvement.

If the user chooses to build after final Blue/Logos, pair continuity is the default implementation contract. The same expert pairs that created Pass 1 proposals and participated in Pass 2/Pass 3 become the implementation lanes, in the same pair groupings, with each pair owning the implementation scope that matches its proposal. Do not hand off to unrelated coding agents unless the user explicitly swaps pairs or asks for a different staffing model.

When those continuity pairs become coding lanes, GPT-5.5/Blue/Logos shapes the exact lane brief, acceptance checks, file scope, and review criteria before coding starts. Use GPT-5.3-Codex-Spark (`gpt-5.3-codex-spark`) as the first-line Codex coding model whenever explicit model selection is available.

Spark coding lanes use reasoning effort `high` by default. Use `xhigh` for complex, risky, cross-module, architecture-sensitive, or user-facing implementation work. Do not downshift Spark reasoning for usage conservation; only fall back to the active Codex orchestrator model when Spark is unavailable, unsuitable, or cannot be selected.

## Meeting Files

Every meeting folder must include Markdown, JSON, and event-stream files for future dashboard use:

```text
MEETING.md
passes\pass-1-pair-proposals.md
passes\pass-2-shuffle-review.md
passes\pass-3-final-blue.md
memory-updates.md
meeting.json
pair-proposals.json
shuffle-reviews.json
final-blue.json
memory-updates.json
events.jsonl
agent-runs.json
agent-report-cards.json
```

`events.jsonl` is the SMS-style dashboard source of truth. Use `visibility: "visible"` for live-chat summaries and `visibility: "internal"` for saved-only hat checkpoints.

## Model Provenance

Every paired agent, coding lane, review lane, and final Blue/Logos synthesis must record model provenance. Record this in Local AI Brain when available and in `agent-runs.json` plus `events.jsonl` inside the meeting folder.

Each run record must include:

- `taskId`
- `phase`
- `agentId` or `pairId`
- `role`
- `requestedExecutionSystem`
- `requestedModel`
- `requestedReasoningEffort`
- `actualExecutionSystem`
- `actualModel`
- `actualReasoningEffort`
- `fallbackReason`
- `memoryBackend`
- `memoryProjectId`
- `memoryRunId`
- `artifacts`
- `checksRun`
- `summary`

If the runtime does not expose the actual model, write `unknown`; do not infer actual Spark usage from the prompt.

## Memory Rules

- `AGENTS.md` is stable identity and voice.
- `MEMORY.template.md` is tracked starter memory structure.
- `MEMORY.md` is durable local knowledge only.
- Meeting folders are compact short-term session history.
- Pair proposals and shuffle reviews list memory candidates only.
- Only final Blue/Logos may write durable local `MEMORY.md`.
- Final Blue/Logos deploys the same pairs back into the work by default when the user chooses to build.
- Final Blue/Logos records model provenance and report cards to the active memory lane before final completion.
- If durable memory changes, report exactly which files changed and what summaries were added.
- Durable user preferences are saved to local expert memory only.
- Never write private memory or meeting history into tracked package files.
