# Linear Thinking Agents Retrofit Plan

## Summary

Upgrade the current `linear-thinking` package from the older 12-role, one-hat flow into the new three-pass paired-agent system. Keep Git as the reusable public source, `.local` as private personal state, and `.agents` as the generated runtime install.

## Current Gaps

- Current skill docs, meeting flow, expert schema, tests, and builder script still model 12 separate roles instead of six mindsets in three paired agents.
- Meeting tracking is not explicit enough: first Blue must create and announce a meeting path before expert work starts.
- There is no dashboard-ready meeting event contract yet.
- Expert memory needs a stronger lifecycle: candidates during proposals, final Blue decides, then writes durable local memories.
- Orchestrator output needs to be more active during runs: frame the meeting, name memory candidates, explain readiness, and report memory writes.

## Target Behavior

- First Blue creates and announces `.local\meetings\<date-slug>\`.
- First Blue proposes the paired roster and pass plan, then pauses so the user can edit before experts run.
- Max live agents are orchestrator plus three paired expert agents.
- The six mindsets are mandatory:
  - Operator
  - Engineer
  - Architect
  - Strategist
  - Steward
  - Philosopher
- Default pairings:
  - Operator + Engineer
  - Architect + Strategist
  - Steward + Philosopher
- Dynamic pair overrides are allowed only when first Blue explains why.
- Pair continuity is the default after final Blue: if the user chooses to build, the same pairs become implementation or deployment lanes in the same groupings unless the user explicitly swaps them.

## Three-Pass Meeting Flow

### Pass 1: Paired Six Hats

Each pair internally runs all six hats and shows only the final paired proposal in chat. Compact internal hat checkpoints are saved to meeting files.

Visible proposal format:

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

Pairs reshuffle and review another pair's work. Each shuffled pair must:

- critique the other pair's proposal
- clarify what they think the proposal means
- append a short change proposal if they find an improvement

### Pass 3: Final Blue Table

The orchestrator brings all work together in Blue/Logos. Final Blue resolves the output into a decision, design plan, implementation plan, or final answer. Durable memory writes happen only after this pass.

If the user chooses to build after final Blue, the same expert pairs that created and reviewed the proposals become the implementation lanes. Do not hand off to unrelated coding agents by default. Preserve pair continuity so each pair implements or reviews the work connected to the proposal it shaped, unless the user explicitly swaps or recruits replacements.

## Meeting Files

Write both Markdown and JSON.

Markdown files:

```text
MEETING.md
passes\pass-1-pair-proposals.md
passes\pass-2-shuffle-review.md
passes\pass-3-final-blue.md
memory-updates.md
```

JSON files:

```text
meeting.json
pair-proposals.json
shuffle-reviews.json
final-blue.json
memory-updates.json
events.jsonl
```

`events.jsonl` is the source of truth for the future SMS-style dashboard. Each expert or pair interaction should be saved as a chat-bubble event.

Minimum event fields:

```json
{
  "meetingId": "",
  "timestamp": "",
  "pass": 1,
  "hat": "blue",
  "speakerId": "",
  "speakerName": "",
  "pairId": "",
  "mindsets": [],
  "messageType": "chat",
  "visibility": "internal",
  "text": ""
}
```

Use `visibility: "visible"` for live-chat summaries and `visibility: "internal"` for saved-only hat dialogue.

## Expert Memory Contract

- `AGENTS.md` is stable identity and voice.
- `MEMORY.template.md` is tracked starter memory structure.
- `MEMORY.md` is private durable local knowledge only.
- Meeting folders are compact short-term session history.
- Pair proposals list memory candidates only.
- Shuffle reviews may add memory candidates only if they affect future expert behavior.
- Final Blue decides what is durable and writes to local `MEMORY.md`.
- Final Blue reports exact files changed and exact memory summaries saved.
- Never write personal memory or meeting history into Git-tracked package files.

Memory-worthy means it changes how that expert should help in future sessions:

- durable user preferences
- stable system facts
- repo or tool conventions
- recurring implementation patterns
- phrasing or output preferences
- "when Joe asks X, do Y" guidance

Do not save:

- one-off brainstorm fragments
- raw secrets
- temporary meeting-only context
- long transcripts
- generic advice that will not affect future expert behavior

## Implementation Plan

### 1. Update Tests First

Update `scripts\Test-LinearThinkingSkills.ps1` so it fails on the current 12-role contract and passes only with the new paired-agent flow.

Add checks for:

- exactly six canonical mindsets
- three default pairings
- first Blue meeting path language
- three-pass meeting flow
- stable visible pair proposal template
- Markdown and JSON meeting templates
- `events.jsonl` required fields
- final Blue memory-write rules
- pair continuity from proposal work into implementation lanes
- `.local`, `MEMORY.md`, and meetings ignored by Git

### 2. Update Skill Instructions

Update `skills\linear-thinking-agents\SKILL.md` to describe:

- first Blue setup and pause
- three paired agents
- Pass 1 paired six-hat work
- Pass 2 shuffle review
- Pass 3 final Blue synthesis
- visible proposal template
- hidden internal checkpoints saved to meeting files
- final Blue memory deployment
- pair continuity when deploying experts into implementation work

Update `skills\linear-thinking-expert-builder\SKILL.md` to focus on six mindsets and local reusable experts.

### 3. Update References And Templates

Replace the 12-role `references\meeting-flow.md` with the six-mindset paired flow.

Update `references\expert-schema.md` to use:

- Operator
- Engineer
- Architect
- Strategist
- Steward
- Philosopher

Add or update templates for:

- meeting Markdown files
- summary JSON files
- `events.jsonl` event shape
- memory updates
- pair proposals
- shuffle reviews
- final Blue output

### 4. Update Expert Builder

Update `scripts\New-LinearThinkingExpert.ps1`:

- replace the 12-role `ValidateSet` with the six mindsets
- write local experts under `.local\experts`
- create `AGENTS.md`, `MEMORY.template.md`, and private `MEMORY.md`
- never overwrite existing `MEMORY.md` unless explicitly forced

### 5. Update Starter Experts

Align starter experts with the six-mindset system. Keep the starter set small and reusable. Each starter expert must have:

- name
- age
- domain
- mindset
- primary question
- default starter flag
- voice
- life-defining event
- analogy style
- maintenance rules

### 6. Update Install And Runtime Sync

Verify `scripts\Install-LinearThinkingSkills.ps1`:

- copies public skill files into `.agents`
- overlays `.local` expert memories into runtime install
- skips meeting folders unless explicitly needed
- never overwrites runtime `MEMORY.md` unless `-ForceMemory` is passed

### 7. Add Smoke Scenario

Document and test a fake topic run:

```text
Use linear thinking agents on how to deploy API keys safely in a PowerShell-heavy workflow.
```

Expected behavior:

- first Blue announces meeting path and waits
- Pass 1 shows only three compact pair proposals
- internal six-hat checkpoints are saved to files
- Pass 2 appends shuffled critique/clarify/change proposals
- final Blue produces the decision/plan
- implementation deployment reuses the same expert pairs as coding/review lanes by default
- memory-worthy API key preferences are written only to local expert memory
- JSONL contains the chat-bubble event stream

## Test-While-Building Split

- Component A, meeting contract:
  - Add tests for meeting templates, JSON schemas, event fields, and first-Blue meeting path language.
  - Update references/templates until tests pass.
- Component B, skill behavior:
  - Add tests for three-pass terms, fixed pairs, shuffle review, final Blue rules, and visible proposal shape.
  - Update skill docs until tests pass.
- Component C, expert system:
  - Add tests for six mindsets, valid pairings, local-only memory, and builder `ValidateSet`.
  - Update expert schema, starter experts, and builder script until tests pass.
- Component D, install/runtime:
  - Add tests that install sync copies templates and starter experts but does not overwrite `MEMORY.md`.
  - Update install behavior if needed.
- Component E, smoke run:
  - Run the fake topic through the installed skill.
  - Verify Markdown, JSON, JSONL, and memory updates.

## Verification Commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\linear-thinking\scripts\Test-LinearThinkingSkills.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\linear-thinking\scripts\Install-LinearThinkingSkills.ps1 -WhatIf
powershell -NoProfile -ExecutionPolicy Bypass -File .\linear-thinking\scripts\Install-LinearThinkingSkills.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\jrice\.agents\tools\skill-admin\Get-AgentSkillInventory.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\jrice\.agents\tools\skill-admin\Test-AgentSkillDrift.ps1
git -C C:\Github\skills check-ignore linear-thinking/.local/experts/example/MEMORY.md
git -C C:\Github\skills status --short
```

## Git Safety

- Do not restore or revert unrelated deleted legacy mirror files unless explicitly requested.
- Do not stage `.local`, `MEMORY.md`, meeting folders, or generated runtime installs.
- Keep this `PLAN.md` tracked as the implementation source for the retrofit.
- Before any publish, verify `git status --short` contains only intended public package files.

## Assumptions

- Source of truth is `C:\Github\skills\linear-thinking`.
- `.local` is private source state.
- `.agents` is generated runtime install.
- MCP gets portable registry metadata only.
- Current `mymcp` publication remains a later step.
