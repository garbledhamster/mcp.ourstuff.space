---
name: agent-opencode
description: Summon a local opencode Blackbox/Ollama coding subagent for focused implementation, debugging, review, or explanation tasks. Use when Codex should delegate narrow coding work to opencode while keeping the main agent responsible for review and integration.
---

# Agent Opencode

Delegate narrow coding work to `opencode`; keep the main Codex agent responsible for reviewing and integrating the result.

## Models

Use the local Blackbox/Odyssey provider through OpenCode provider `blackbox-ollama` first.

Explicit fallback rule:

- Prefer a verified local `blackbox-ollama` model when it can do the task well on the Odyssey hardware.
- If no suitable local model exists or local hardware makes the task impractical, use a non-local fallback only when the user explicitly asks for it.

Installed and verified:

- STANDARD: `blackbox-ollama/llama3.1:8b` via agent `blackbox-standard`.
  - Use for balanced text work, summaries, normal Q&A, small planning, and general chat.
  - Prompt style: concise task, exact output format, no broad context dumps.
- CODING FAST: `blackbox-ollama/qwen2.5-coder:7b` via agent `blackbox-fast-coder`.
  - Use for default coding delegation, focused edits, debugging, syntax checks, and short reviews.
  - Prompt style: exact files, exact objective, constraints, ask for changed files only.
- CODING SMALL: `blackbox-ollama/qwen2.5-coder:3b` via agent `blackbox-small-coder`.
  - Use for tiny edits, quick summaries, file triage, and cheap second opinions.
  - Prompt style: one narrow question; avoid multi-file reasoning.
- CODING SMART: `blackbox-ollama/qwen2.5-coder:14b` via agent `blackbox-coder`.
  - Use for harder coding only when 7B is insufficient.
  - Note: slower on this CPU-only box; keep prompts small.
- REASONING: `blackbox-ollama/deepseek-r1:14b` via agent `blackbox-reasoning`.
  - Use for diagnosis, tradeoff analysis, algorithm choices, and "think this through" tasks.
  - Note: slow; do not use for routine implementation.
- CHAT FAST: `blackbox-ollama/llama3.2:1b` via agent `blackbox-tiny`.
  - Use for tiny chat, labels, status text, and ultra-light classification.

Current machine fit:

- Odyssey reports CPU-only, Intel i3-10100, 8 cores, ~31GB RAM.
- Favor 1B/3B/7B models for speed.
- Use 14B models only for careful reasoning or when quality matters more than latency.

## Key

Read the session key from:

`C:\Users\jrice\.local\data\odyssey.txt`

Treat it as secret. Do not print it, log it, commit it, or mention its value.

If that file is missing or empty, fall back to `$env:OPENCODE_SESSION_KEY`.
If neither exists, report that opencode is unavailable.

## Call Pattern

PowerShell:

```powershell
$model = "blackbox-ollama/qwen2.5-coder:7b" # CODING FAST
$agent = "blackbox-fast-coder"
# $model = "blackbox-ollama/llama3.1:8b"; $agent = "blackbox-standard"
# $model = "blackbox-ollama/deepseek-r1:14b"; $agent = "blackbox-reasoning"
# $model = "blackbox-ollama/llama3.2:1b"; $agent = "blackbox-tiny"
$keyFile = "C:\Users\jrice\.local\data\odyssey.txt"
$key = if (Test-Path -LiteralPath $keyFile) { (Get-Content -LiteralPath $keyFile -Raw).Trim() } else { "" }
if (-not $key) { $key = ([string]$env:OPENCODE_SESSION_KEY).Trim() }
if (-not $key) { throw "Missing opencode session key." }

@'
Task: <focused coding task>
Context: <exact paths, symptoms, constraints>
Return: <changed files, diagnosis, patch idea, or explanation>
'@ | opencode -s $key --agent $agent --model $model
```

Interactive CLI:

```powershell
opencode -s <session-id> --agent blackbox-fast-coder --model blackbox-ollama/qwen2.5-coder:7b
```

## Delegation Rules

- Pick CODING FAST (`qwen2.5-coder:7b`) for most coding work.
- Pick CODING SMALL (`qwen2.5-coder:3b`) for tiny edits and summaries.
- Pick STANDARD (`llama3.1:8b`) for general text and balanced chat.
- Pick CHAT FAST (`llama3.2:1b`) for tiny labels/status/classification.
- Pick CODING SMART (`qwen2.5-coder:14b`) only for harder multi-file changes or stubborn bugs.
- Pick REASONING (`deepseek-r1:14b`) only for diagnosis/tradeoffs; expect slower replies.
- If a task cannot be done by a local model, or local hardware makes it impractical, ask before routing to a non-local fallback agent.
- Give opencode a focused prompt with exact file paths, the exact question, and the desired output.
- Keep prompts short. The Odyssey shim defaults to forwarding only the latest user message for speed.
- Tell opencode not to revert unrelated changes.
- Tell opencode to list changed files if it edits.
- Review opencode output before applying, trusting, or reporting it.
