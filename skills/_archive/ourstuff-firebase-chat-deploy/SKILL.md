---
name: ourstuff-firebase-chat-deploy
description: Deploys secure Firebase chat/function endpoints for Ourstuff projects with fast, repeatable secret/env/deploy/verify/rollback flows. Use when creating or shipping chat APIs on Firebase for any *.ourstuff.space project, especially when you need OPENROUTER/OPENAI secrets, PROJECTS_AI_PROVIDER/MODEL env setup, and one-command deployment verification.
---

# Ourstuff Firebase Chat Deploy

## Scope

Use this skill to quickly deploy chat-capable Firebase Functions for `ourstuff.space` projects using a cross-platform Python helper.

## Quick start

```powershell
python "C:\Users\jrice\.agents\skills\ourstuff-firebase-chat-deploy\scripts\firebase_chat_deploy.py" full --project ourstuff-firebase --firebase-dir "C:\Github\ourstuff.space\.firebase" --function projectsAiApi
```

## What it does

1. Sets required provider secrets (`OPENROUTER_API_KEY`, optional `OPENAI_API_KEY`).
2. Writes `.env.<project-id>` with `PROJECTS_AI_PROVIDER` and `PROJECTS_AI_MODEL`.
3. Deploys only the target function.
4. Verifies deployment and prints expected HTTPS endpoint.
5. Provides rollback commands (delete function + restore env backup).

## Workflows

### 1) Full deploy flow (recommended)

```powershell
python "C:\Users\jrice\.agents\skills\ourstuff-firebase-chat-deploy\scripts\firebase_chat_deploy.py" full --project <firebase-project-id> --firebase-dir "<repo>\.firebase" --function <functionName>
```

### 2) Step-by-step flow

```powershell
python "...firebase_chat_deploy.py" set-secrets --project <firebase-project-id>
python "...firebase_chat_deploy.py" write-env --project <firebase-project-id> --firebase-dir "<repo>\.firebase" --provider ask
python "...firebase_chat_deploy.py" deploy --project <firebase-project-id> --firebase-dir "<repo>\.firebase" --function <functionName>
python "...firebase_chat_deploy.py" verify --project <firebase-project-id> --function <functionName>
```

### 3) Rollback flow

```powershell
python "...firebase_chat_deploy.py" rollback --project <firebase-project-id> --firebase-dir "<repo>\.firebase" --function <functionName> --restore-env
```

## Safety rules

- Never place provider keys in frontend files.
- Keep `.env.<project-id>` in `.firebase` only.
- Use `--provider ask` to enforce deploy-time provider choice.
- Use narrow deploy scope: `--only functions:<function>`.

