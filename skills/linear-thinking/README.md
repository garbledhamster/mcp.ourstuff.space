# Linear Thinking

Package-style skill family for three-pass linear thinking meetings with six mindsets in three paired agents.

## Contract

- First Blue/Logos creates and announces `.local\meetings\<date-slug>\`, proposes the pair roster and pass plan, then pauses for user edits.
- Maximum live agents: orchestrator plus three paired agents.
- Canonical mindsets: Operator, Engineer, Architect, Strategist, Steward, Philosopher.
- Default pairs: Operator + Engineer, Architect + Strategist, Steward + Philosopher.
- Pass 1 runs paired internal six-hat work and shows only final pair proposals.
- Pass 2 shuffles pairs for critique, clarification, and appended change proposals.
- Pass 3 is final Blue/Logos synthesis plus durable local memory deployment.
- If the user chooses to build, final Blue/Logos deploys the same pairs as implementation or deployment lanes by default.
- Meeting folders include Markdown, JSON, `events.jsonl`, agent run provenance, and report cards for future dashboard and memory playback.

## myMCP And Cross-LLM Install

The myMCP registry packets publish two primary discoverable skills:

```text
PLANNING / garbledhamster / linear-thinking-agents
FRONTEND / garbledhamster / linear-thinking-coders
```

`linear-thinking-expert-builder` stays bundled as supporting package capability. It is installed with the package so agents can recruit or maintain local experts when the primary meeting runner needs that support, but it is not a separate primary registry entry.

`linear-thinking-coders` extends the paired meeting protocol into frontend design-doc synthesis, approval-gated pair-only implementation tickets, OpenCode CLI optional worker heads, GPT-5.5/Blue/Logos instruction shaping, GPT-5.3-Codex-Spark coding lanes using `high` or `xhigh` reasoning, structured coding reports, model provenance ledgers, final agent report cards, focused fix pairs, and Blue/Logos failure-note learning loops.

Cross-LLM installers should pull the package from:

```text
https://github.com/garbledhamster/skills
```

using package path:

```text
linear-thinking
```

The primary skill entrypoint is:

```text
linear-thinking/skills/linear-thinking-agents
```

The frontend coding skill entrypoint is:

```text
linear-thinking/skills/linear-thinking-coders
```

Supporting skill files, references, templates, starter experts, and scripts are part of the same package. Registry packets must stay portable and must not include private runtime state, local durable memory, or meeting transcripts.

## Layout

```text
skills\linear-thinking-agents\          meeting runner skill
skills\linear-thinking-coders\          frontend design council and paired coder skill
skills\linear-thinking-expert-builder\  expert recruiting and maintenance skill
experts\starter\                        tracked reusable starter experts
templates\                              local expert and meeting templates
references\                             shared protocols and schemas
scripts\                                install, create, and validation scripts
tests\                                  fixtures and test notes
registry\mymcp\                         local MCP registry packet
.local\                                 ignored private expert memory and meetings
```

Runtime install target:

```text
C:\Users\jrice\.agents\skills
```

Use `scripts\Install-LinearThinkingSkills.ps1 -WhatIf` before a real install.
