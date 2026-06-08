---
name: Ourstuff Checklist
description: Turn free-form plans into structured, status-driven execution checklists that must update at 25% checkpoints. Use when a user asks for planning, tracking, or milestone progress updates and wants explicit checklist checkpoints.
---

# Ourstuff Checklist

## Intent

Convert plan text into a real, checkable task list and show progress updates at exact 25% milestones only.

## Core Rules

- Never collapse work into arbitrary short lists. Expand the user’s full plan into task-level items.
- Use these explicit states in every checklist item:
  - `[planned]`
  - `[in-progress]` (accept `[ip-progress]` as a display alias)
  - `[error]`
  - `[done]`
- Track progress as a percentage of completed plan scope and show the percent at the end of each task label in parentheses, e.g. `(...) (25%)`.
- Emit an updated checklist only when progress reaches 25/50/75/100 percent of the current plan.
- Keep task list continuity across updates; do not reorder existing items.

## Execution Flow

1. Decompose the user plan into concrete, atomic tasks.
2. Assign each task an index and an implied step percentage:
   - `percent = round((index / total_tasks) * 100)`
3. Mark exactly one item `[in-progress]` when actively working.
4. On completion, move task to `[done]`.
5. Emit full checklist snapshots only when total completion crosses a 25% boundary.
6. If a task has a blocker, mark `[error]` with a short reason and keep percent label.

## Checklist Format

Use this exact checkbox pattern:

- [planned]  Initialize workspace state (0%)
- [in-progress]  Run required discovery commands (10%)
- [done]  Create first draft of output file (25%)
- [error]  Validate permissions and escalate with blocker note (40%)

## Milestone Update Policy

- 0–24%: update only when the request is acknowledged and the initial task list is published.
- 25% reached: publish full updated checklist once.
- 50% reached: publish full updated checklist once.
- 75% reached: publish full updated checklist once.
- 100% reached: publish final full checklist and closeout note once.

## One-Question-At-A-Time Grill Questions

When the user asks to be “grilled,” ask one planning/design question at a time and include a recommended answer.

- If user input can be clarified by existing repository context, inspect codebase first and then continue.
- Keep questions short and decision-oriented (scope, ordering, risk, rollback).

## Samples

### Sample A: Dense Task List

- [done] [1/8] Create plan skeleton (12%)
- [done] [2/8] Parse requirement constraints (25%)
- [in-progress] [3/8] Draft checklist template in SKILL.md (38%)
- [planned] [4/8] Add progress-milestone policy (50%)
- [planned] [5/8] Add status token legend (62%)
- [planned] [6/8] Add sample outputs (75%)
- [planned] [7/8] Add validation/rollover behavior (87%)
- [planned] [8/8] Publish final review note (100%)

### Sample B: Phase Grouping

- [done] Plan Setup (done/25%)  
  - [done] [1/12] Capture inputs (8%)
  - [done] [2/12] Validate success criteria (16%)
  - [done] [3/12] Estimate task count (25%)
- [in-progress] Execution (in-progress/50%)  
  - [in-progress] [4/12] Write checklist rules (33%)
  - [planned] [5/12] Add templates (41%)
- [planned] Verification (planned/75%)  
  - [planned] [6/12] Add examples (50%)
  - [planned] [7/12] Add error-handling rules (58%)
- [planned] Handoff (planned/100%)  
  - [planned] [8/12] Publish final file (66%)
  - [planned] [9/12] Record completion summary (75%)

### Sample C: Minimalist Checklist

- [in-progress] Drafting checklist skill file (25%)
- [planned] Add status legend and examples (50%)
- [planned] Add review validation steps (75%)
- [planned] Finalize and return diff summary (100%)

## Output Checklist Template

Before any work begins:

1. Publish the full tasklist.
2. Set the current task to `[in-progress]`.
3. On each milestone checkpoint, repost the full list with updated state markers.

Use the status area exactly as:
`[planned]`, `[in-progress]`, `[error]`, `[done]`.

## Anti-Patterns to Avoid

- Using only 4 tasks for every request.
- Changing the meaning of task percentages across updates.
- Emitting progress updates on every minor sub-step.
- Removing items from the list unless the user explicitly redefines scope.

## Success Criteria

- The user can see every planned task from the original plan represented.
- Percentages are stable and cumulative.
- Each status update is internally consistent with the current state.
- Full checklist is shown at 25/50/75/100.
