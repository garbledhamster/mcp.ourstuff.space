# Verified OpenCode Agents

Use this reference when the user asks for verified OpenCode helper runs, OpenRouter/free models through OpenCode, free/free-credit models, or role-specific OpenCode dispatch.

## Free-Only Gate

An OpenCode model is eligible for a free-only lane only when all are true:

- The model ID contains `:free` or ends in `-free`.
- `opencode run --model "<modelId>" "Say READY."` exits successfully and returns a usable response.
- The model is assigned to the purpose listed in this file.
- Blue/Logos records the model ID and smoke evidence before dispatch.

Do not call these "OpenRouter agents." They are OpenCode helper runs using free model IDs, some of which are routed through OpenRouter. Do not use paid aliases during a free-only run, even when the paid alias better matches the requested family. If a role has no verified free model, either use the listed verified free fallback for that purpose, use Codex Spark through explicit model selection, use GitHub Copilot when available, or stop delegated helper execution.

## Current Verified Free Agents

Verified on this host with `opencode 1.16.2`.

| Purpose | Preferred role | Verified model ID | Smoke evidence | Use for |
| --- | --- | --- | --- | --- |
| Worker/search/summaries | GPT-OSS free worker fallback | `openrouter/openai/gpt-oss-120b:free` | `Say READY.` returned `READY.` | Scouting, summaries, narrow repetitive subtasks, simple smoke prompts. |
| Long-context reader | MiMo-V2.5 | `opencode/mimo-v2.5-free` | `Reply READY only.` returned `READY` | Reading large file sets, docs, logs, and synthesis before tickets. |
| Builder/code generation | MiniMax free builder | `opencode/minimax-m3-free` | `Say READY.` returned `READY.` | Implementation drafts, mechanical patches, component/code generation when MiniMax M2.5/M2.7 free IDs are unavailable. |
| Reviewer/validator fallback | GPT-OSS free reviewer | `openrouter/openai/gpt-oss-120b:free` | `Say READY.` returned `READY.` | Review, critique, acceptance-check validation, and risk analysis when Qwen free reviewer is unavailable or blocked. |

## User-Preferred IDs To Try First

Try these user-preferred IDs first only when the local OpenCode catalog accepts them and the smoke test passes:

```powershell
opencode run --model "xiaomi/mimo-v2-flash:free" "Say READY."
opencode run --model "minimax/minimax-m2.5:free" "Say READY."
opencode run --model "qwen/qwen3.6-plus:free" "Say READY."
```

Current host evidence: these shorthand IDs were not accepted by `opencode 1.15.12` during prior smoke testing. Do not hardcode them as dispatch defaults until they pass locally.

## Unverified Or Blocked Roles

- `qwen/qwen3.6-plus:free` was not found by the local OpenCode catalog.
- `openrouter/qwen/qwen3-coder:free` and `openrouter/qwen/qwen3-next-80b-a3b-instruct:free` resolved but returned a provider-side prompt-injection block during smoke tests.
- `minimax/minimax-m2.5:free` was not found by the local OpenCode catalog.
- DeepSeek models are blocked for OpenCode helper routing because they have repeatedly failed or tripped provider prompt-injection filtering.
- Paid aliases such as `opencode/qwen3.6-plus` or `opencode/minimax-m2.7` are not allowed in a free-only run.

## Dispatch Rules

- Worker/search/summaries: use the verified GPT-OSS free fallback, or another verified free worker only if Blue/Logos records why it fits the same purpose.
- Long-context reader: use MiMo-V2.5 free when verified; otherwise use another verified free long-context helper, Spark through explicit model selection, GitHub Copilot when available, or no delegated helper.
- Builder/code generation: prefer a verified MiniMax free builder. Do not use paid MiniMax M2.5/M2.7 aliases in free-only mode.
- Reviewer/validator: prefer Qwen3.6 Plus free only after it is verified. Until then, use the verified free reviewer fallback listed above, Spark through explicit model selection, GitHub Copilot when available, or no delegated helper.
- Every OpenCode prompt still uses the pair requirement from `coder-ticket-template.md`.

## CLI Notes From POC

- Use `opencode run "<message>"`; in this installed version, top-level `-p` is not the prompt flag for non-interactive work.
- In `opencode run --help`, `-p` means password.
- Attach files only when needed; for one-off proof prompts, prefer placing the full message as the positional argument.
