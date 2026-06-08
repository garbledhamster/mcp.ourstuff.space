# OpenCode Agent Backend

Use this reference when the user asks for OpenCode CLI agents, OSS/free models, OpenRouter/free models through OpenCode, or OpenCode-backed pair heads.

## Execution Contract

GPT-5.5/Blue/Logos remains the final orchestrator and instruction shaper. OpenCode is the execution system for delegated pair heads. OpenRouter is only a provider/model catalog used by OpenCode model IDs; do not describe delegated workers as "OpenRouter agents."

Fallback rule: if OpenCode fails to start, cannot use the selected model, times out, edits the wrong scope, returns unusable output, or cannot provide both pair perspectives, first try a Codex Spark lane through explicit model selection such as `codex exec --model gpt-5.3-codex-spark --cd <repoPath> "<paired ticket prompt>"`. If Spark cannot be explicitly selected, use GitHub Copilot when available, then another verified OpenCode/free fallback. Do not fall back to standard Codex as a delegated agent. GPT-5.5/Blue/Logos may continue direct orchestration or small direct implementation, but must record that no delegated fallback agent was used.

Free-only rule: when the user asks for free, free-credit, OSS/free, OpenRouter/free models, or verified agents, load `verified-opencode-agents.md` and dispatch only models through `opencode run` that pass its free-only gate. Do not use paid OpenCode aliases in that mode.

## Model Selection

OpenCode-backed helper runs must use this role model map. Treat these as the skill contract for OpenCode-backed lanes, not generic recommendations.

| OpenCode role | Required model | Use for | Reason |
| --- | --- | --- | --- |
| Researcher | MiMo-V2.5 | Reading lots of files, docs, logs, screenshots, and synthesizing findings before design or tickets | Huge context and good synthesis across broad material. |
| Builder | MiniMax M2.7 | Primary implementation, refactors, component/code generation, mechanical patch creation | Fast coding output and strong implementation throughput. |
| Reviewer | GPT-OSS 120B free | Cross-review, critique, validation, acceptance-check review, risk analysis | Verified free reviewer fallback with usable local smoke evidence. |

Resolve the exact provider/model IDs from the local OpenCode model list before dispatch. Model IDs can include OpenRouter provider prefixes, but OpenCode remains the runner. The selected ID must clearly refer to the required model family above.

For free-only runs, the role model map is a purpose map, not permission to spend paid credits. Use the verified free IDs in `verified-opencode-agents.md`; if the preferred family is not available as a verified free model, use the documented verified free fallback for that purpose or keep the lane local.

Required environment variable names, when the host wants stable IDs:

- `LINEAR_THINKING_CODERS_OPENCODE_WORKER_MODEL`: verified GPT-OSS free worker/reviewer fallback ID.
- `LINEAR_THINKING_CODERS_OPENCODE_RESEARCH_MODEL`: MiMo-V2.5 provider/model ID.
- `LINEAR_THINKING_CODERS_OPENCODE_BUILDER_MODEL`: MiniMax M2.7 provider/model ID.
- `LINEAR_THINKING_CODERS_OPENCODE_REVIEWER_MODEL`: GPT-OSS 120B free reviewer ID.

Do not use older generic env vars such as `LINEAR_THINKING_CODERS_OPENCODE_THINKING_MODEL` or `LINEAR_THINKING_CODERS_OPENCODE_CODING_MODEL` for new dispatch. If those are present, ignore them unless they resolve to one of the required role models.

Selection order:

1. Run `opencode --version`.
2. Run `opencode models` and, when supported by the local CLI, refresh the relevant provider catalog.
3. For free-only runs, load `verified-opencode-agents.md` and start from its verified free IDs.
4. Resolve each required role model from the matching role-specific env var when set, but reject it if free-only mode is active and the ID does not contain `:free` or end in `-free`.
5. If a role-specific env var is unset, resolve that role by searching the OpenCode model list for the required model name or obvious provider alias.
6. Smoke-test the selected model with a tiny neutral prompt such as `Say READY.`.
7. If the required model is unavailable, cannot be resolved, fails preflight, is provider-blocked, is not free-labeled during a free-only run, or cannot perform the lane reliably, record an OpenCode backend failure note and use the verified free fallback for that purpose when one is listed. If no verified fallback fits, return the lane to Codex Spark first through explicit model selection, with GPT-5.5/Blue/Logos retaining orchestration and review. If Spark cannot be explicitly selected, do not use standard Codex as a delegated fallback.
8. Do not silently substitute paid model families for a role. Paid fallback is forbidden in free-only mode.

## Preflight

Run from the target repo:

```powershell
opencode --version
opencode models
```

Optional smoke tests:

```powershell
opencode run --model "$env:LINEAR_THINKING_CODERS_OPENCODE_WORKER_MODEL" --dir "<repoPath>" "Say READY."
opencode run --model "$env:LINEAR_THINKING_CODERS_OPENCODE_RESEARCH_MODEL" --dir "<repoPath>" "Say READY."
opencode run --model "$env:LINEAR_THINKING_CODERS_OPENCODE_BUILDER_MODEL" --dir "<repoPath>" "Say READY."
opencode run --model "$env:LINEAR_THINKING_CODERS_OPENCODE_REVIEWER_MODEL" --dir "<repoPath>" "Say READY."
```

Treat any nonzero exit, model-not-found output, auth failure, timeout, or noisy unusable response as OpenCode failure for that model. In free-only mode, also treat missing `:free` or `-free` in the selected model ID as failure.

## Paired Dispatch Pattern

Each OpenCode run must still be pair-framed.

Prompt requirements:

- Name the `Owner Pair`.
- Define both roles.
- Include allowed write scope and forbidden files.
- Require both pair perspectives before edits.
- Require pair reflection in the output.
- Require Blue/Logos failure-note fields when the pair struggles.

Example:

```powershell
opencode run `
  --model "$env:LINEAR_THINKING_CODERS_OPENCODE_BUILDER_MODEL" `
  --dir "<repoPath>" `
  --title "linear-thinking-coders: Build Pair ticket" `
  "<paired ticket prompt>"
```

Use the model matching the prompt's role:

- Worker/search/summaries prompts use `LINEAR_THINKING_CODERS_OPENCODE_WORKER_MODEL`.
- Research prompts use `LINEAR_THINKING_CODERS_OPENCODE_RESEARCH_MODEL`.
- Builder prompts use `LINEAR_THINKING_CODERS_OPENCODE_BUILDER_MODEL`.
- Reviewer prompts use `LINEAR_THINKING_CODERS_OPENCODE_REVIEWER_MODEL`.

If the env var is empty, resolve the exact model ID from the refreshed OpenCode model list. If that fails, record failure and fall back to a Codex Spark coding lane first through explicit model selection, with GPT-5.5/Blue/Logos retaining orchestration and review. If Spark cannot be selected, do not spend standard Codex usage on a delegated agent.

## OpenCode Agent Files

Use `opencode agent create` only when a durable OpenCode subagent profile is useful. For one-off tickets, prefer `opencode run --model ... --dir ...`.

Do not grant broad permissions by default. Never use `--dangerously-skip-permissions` unless the user explicitly requested it and the repo scope is understood.

## Failure Handling

Record an OpenCode backend failure note:

```markdown
### OpenCode Backend Failure

- `Pair:`
- `Phase:`
- `Model attempted:`
- `Command shape:`
- `Failure evidence:`
- `Fallback used:` Codex Spark coding lane, GitHub Copilot, verified OpenCode/free fallback, or no delegated fallback
- `Future guidance:`
```

Then continue only with a non-standard delegated backend: Codex Spark first when explicitly selectable, then GitHub Copilot when available, then verified OpenCode/free fallback. If none is available, stop delegation and let Blue/Logos continue direct orchestration without claiming a helper-agent run.
