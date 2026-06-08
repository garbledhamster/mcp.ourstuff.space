---
name: skill-to-simple-instruction
description: Converts agent skills, workflows, or long local instructions into simple paste-ready instructions for ChatGPT, Custom GPTs, other assistants, myMCP registry descriptions, or human sharing. Use when the user wants a skill turned into a concise prompt, "simple instruction", GUI-ready ChatGPT instruction, portable custom instruction, or shareable version that preserves behavior without Codex-only mechanics.
---

# Skill To Simple Instruction

Turn skills and agent workflows into portable instructions a normal person can paste, install, or share.

## Workflow

1. Identify the source.
   - If the user names a skill, read that skill's `SKILL.md`.
   - If the user pasted text, use that text.
   - If multiple skills apply, merge only the overlapping behavior unless the user asks for a full bundle.
   - If the source is unclear, ask one concise question.
2. Extract the useful behavior:
   - trigger intent
   - default workflow
   - output format
   - quality gates
   - constraints, no-go rules, and anti-patterns
   - user preferences worth preserving
3. Remove agent-only machinery:
   - local paths, shell commands, MCP routing, helper-agent dispatch, hidden tool calls, and repo checks
   - references to Codex-specific skill loading unless the target is another coding agent
   - private memory, machine details, secrets, or PII
4. Translate missing capabilities:
   - "read files" -> "ask me to paste or upload the relevant material"
   - "run checks" -> "tell me what checks to run or ask for results"
   - "use tools" -> "use available evidence and say what evidence is missing"
5. Produce the requested form.
   - Default: full paste prompt, quick prompt, and usage notes.
   - For ChatGPT Custom Instructions: write stable "Always..." behavior.
   - For Custom GPTs: write role, behavior, constraints, and conversation starters.
   - For myMCP/registry: write title, short description, tags, triggers, and concise behavior summary.
   - For sharing with other people: write a plain-language instruction they can reuse without local context.

## Output Contract

Default output:

```text
Full paste instruction:
<complete instruction>

Quick version:
<short prompt>

How to use it:
<1-3 usage notes>
```

For "always" instructions:

```text
Always do this when I ask for <topic>:
<stable instruction>
```

For registry text:

```text
Title:
<short title>

Description:
<1-3 sentence description>

Tags:
<comma-separated tags>

Triggers:
<phrases that should invoke it>
```

## Writing Rules

- Keep the result self-contained.
- Prefer concrete instructions over philosophy.
- Preserve the source skill's most important quality gate.
- Say when evidence is missing; do not invent missing facts.
- Include a quick version unless the user asks for only one artifact.
- Use normal ChatGPT language, not Codex internals.
- Keep most outputs between 150 and 900 words.
- Keep the skill itself under 500 lines.

## Quality Gate

Before returning, check:

- A normal ChatGPT user could paste the instruction without local files.
- The source skill's core behavior survived.
- Local-only mechanics were removed or translated.
- The instruction is simple enough to share.
- The output format matches the target surface.
