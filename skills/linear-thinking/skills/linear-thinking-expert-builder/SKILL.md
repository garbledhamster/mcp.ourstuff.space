---
name: linear-thinking-expert-builder
description: Recruits, validates, and maintains reusable local expert profiles for six-mindset linear thinking meetings. Use when the user says "recruit expert", "create expert agent", "update expert memory", "expert profile", or needs missing expertise added to the linear thinking system.
---

# Linear Thinking Expert Builder

Use this skill to create or maintain expert profiles without leaking personal memory into Git.

## Create An Expert

1. Prefer `scripts/New-LinearThinkingExpert.ps1` from the package source.
2. Default new recruited experts to `.local\experts\<expert-id>`.
3. Create `AGENTS.md`, `MEMORY.template.md`, and private `MEMORY.md`.
4. Keep durable knowledge in local `MEMORY.md`; keep public reusable identity in `AGENTS.md`.
5. Do not create or modify meeting history in tracked package files.

## Canonical Mindsets

Every expert must use exactly one canonical mindset:

- Operator
- Engineer
- Architect
- Strategist
- Steward
- Philosopher

`Role:` is retained for current template and script compatibility. `Role:` and `Mindset:` must match exactly and must be one of the six canonical mindsets.

## Required Fields

Each expert profile must define:

- name
- age
- domain
- role
- mindset
- primary question
- default starter flag
- voice
- life-defining event
- analogy style
- maintenance rules

## Promotion Rule

Local experts can be promoted to tracked Git only after removing `MEMORY.md`, meeting history, and private details. Public promoted profiles keep `AGENTS.md` and `MEMORY.template.md` only.

There should be at most one `Default starter: Yes` profile per canonical mindset.

## Maintenance

- Pair proposals and shuffle reviews may name memory candidates.
- Add durable memory only when the final Blue/Logos pass explicitly decides it.
- Write durable memory only to local expert `MEMORY.md`.
- Report exactly what changed after a memory write.
- Reject duplicate expert ids unless the user explicitly asks to update that expert.
