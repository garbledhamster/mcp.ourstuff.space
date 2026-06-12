---
name: gradientfg-finish-line-release
description: Runs GradientFG repo readiness, commits and pushes approved local changes, then pulls the matching SRV01-16 web site through GitPublish when a web repo is involved.
---

# GradientFG Finish Line Release

## Scope

Use this for GradientFG repos under `D:\GIT` when work should be left ready, pushed to the remote source of truth, and, for SRV01-16 dashboard sites, pulled to live web.

Read the repo's local instructions first when present: `AGENTS.md`, `LLM.md`, `README.md`, `PLAN.md`, or `plans\*.md`. Preserve unrelated uncommitted changes. Do not claim commit, push, publish, pull, or deployment unless that action actually ran or was verified live.

## Source Of Truth

- Local edit roots live under `D:\GIT`.
- Git remote is the source of truth. Most internal web repos push to `git.is.gradientfg.com`; some tooling repos may push to GitHub.
- SRV01-16 static dashboard sites are deployed by pull, not by editing live files.
- Live SRV01-16 web roots under `D:\web\<site>` are hard mirrors of `origin/main`.

## Standard Path

From the repo root:

1. Identify the repo, branch, and remote:

```powershell
git status --short --branch
git remote -v
git branch --show-current
```

2. Inspect local instructions and choose repo-native checks before inventing new ones:

```powershell
Get-ChildItem -Force AGENTS.md,LLM.md,README.md,PLAN.md -ErrorAction SilentlyContinue
Get-ChildItem -Force .github,plans,scripts,tests -ErrorAction SilentlyContinue
```

3. Run applicable readiness checks.

For Python/uv repos:

```powershell
python -m uv run pytest
```

For plain Python repos without uv:

```powershell
python -m pytest
```

For static JavaScript dashboard repos, run syntax checks over changed JavaScript files:

```powershell
git diff --name-only --diff-filter=ACMR HEAD -- '*.js' | ForEach-Object { node --check $_ }
```

For repos with package scripts, prefer the repo scripts:

```powershell
npm test
npm run check
```

Only report a command as passed if it actually ran. If a check is not applicable because the repo has no matching files, say that.

## Commit And Push

Before committing:

- Re-run `git status --short`.
- Stage only files that belong to the task.
- Do not include unrelated dirty files.
- Use a direct commit message that names the release/check/update.

Then push the current branch:

```powershell
git add <task-files>
git commit -m "<message>"
git push origin <branch>
```

If there is nothing to commit, say so and still push only if the branch is ahead of its remote.

## SRV01-16 Web Pull

For these dashboard repos, push first, then pull live by starting the matching scheduled task on SRV01-16:

| Local repo | GitPublish site |
| --- | --- |
| `D:\GIT\automation.is.gradientfg.com` | `automation.is` |
| `D:\GIT\it.is.gradientfg.com` | `it.is` |
| `D:\GIT\is.gradientfg.com` | `is` |
| `D:\GIT\ASPX_CODING` | no SRV01-16 static pull; API/source repo only |
| any repo matching `D:\GIT\<site>.gradientfg.com` | `<site>` when a `\GFG\GitPublish\Publish-<site>` task exists |

Run the pull through the scheduled task:

```powershell
Invoke-Command -ComputerName SRV01-16 -ScriptBlock {
  param($Site)
  Start-ScheduledTask -TaskPath '\GFG\GitPublish\' -TaskName "Publish-$Site"
} -ArgumentList '<site>'
```

Then verify the GitPublish log:

```powershell
Invoke-Command -ComputerName SRV01-16 -ScriptBlock {
  param($Site)
  Get-Content "C:\GitPublish\logs\$Site.log" -Tail 80
} -ArgumentList '<site>'
```

Treat `ABORT: untracked files present` as a blocked release. Do not clean or reset live web manually unless explicitly asked.

## API And Non-Static Sites

`api.is.gradientfg.com` is SRV01-15, not SRV01-16. DPAPI-bound API changes must be deployed on-box using that repo's deployment instructions. Do not use the SRV01-16 GitPublish path for API secrets or ASPX API deployment.

`forms.is.gradientfg.com` is not part of the SRV01-16 GitPublish set unless it has been explicitly onboarded into Gitea with a publish task.

## Handoff

Summarize:

- repo, branch, and remote pushed
- commit hash or "nothing to commit"
- checks run and results
- whether SRV01-16 GitPublish was run
- GitPublish log outcome when applicable
- remaining dirty files, including unrelated files intentionally left alone
- exact next human action only when something remains blocked
