# Skill Registry MCP

Private Cloudflare Worker + D1 registry for curated agent skill instructions.

The registry stores approved and pending text-only skill bundles. It exposes approved skills through a remote MCP endpoint and exposes admin actions through separate locked-down routes.

## Shape

```text
/mcp
  MCP JSON-RPC transport
  no auth for public approved-read mode
  read token for private mode
  approved skills only

/admin/*
  admin token
  imports, pending review, approve, reject, diff, delete

/health
  public health only

/.well-known/oauth-protected-resource
  OAuth protected resource metadata/status

/.well-known/oauth-authorization-server
  OAuth authorization server metadata/status
```

## Auth Modes

Keep these separate:

```text
TLS success
  HTTPS cert and route are reachable.

Bearer token success
  SKILL_REGISTRY_READ_TOKEN or SKILL_REGISTRY_ADMIN_TOKEN was accepted.

MCP auth success
  The target MCP client understands the auth flow, obtains/uses credentials, and completes MCP initialize/list calls.
```

V1 supports:

```text
/mcp public read
  enabled by SKILL_REGISTRY_MCP_PUBLIC_READ = "true"
  no auth
  approved skills only
  intended for ChatGPT clients that require No Auth

/admin/*
  SKILL_REGISTRY_ADMIN_TOKEN

/mcp
  SKILL_REGISTRY_READ_TOKEN for private remote use
  SKILL_REGISTRY_ADMIN_TOKEN also accepted for owner smoke checks

local stdio adapter
  reads SKILL_REGISTRY_READ_TOKEN from environment
  proxies to /mcp
  caches approved skills
```

V1 does not claim full remote OAuth login yet. The OAuth discovery routes exist so MCP clients do not see an opaque custom API:

```text
/.well-known/oauth-protected-resource
/.well-known/oauth-authorization-server
```

When OAuth issuer/endpoints are not configured, those routes return JSON metadata/status explaining:

```text
oauth_implemented = false
private_bearer_token_supported = true
local_stdio_adapter_supported = true
```

Do not put Cloudflare Access in front of `/mcp` unless the target MCP clients can complete that specific auth flow.

`/mcp` returns `401` plus `WWW-Authenticate` with a `resource_metadata` pointer when auth is missing or invalid.

When `SKILL_REGISTRY_MCP_PUBLIC_READ = "true"`, `/mcp` does not return `401` for missing auth. It is public approved-read mode.

No-auth mode does not verify ChatGPT user email, account, workspace, or organization identity. If this needs to be restricted to a specific user such as an email address, implement full OAuth or another verifiable signed-token flow. Do not trust arbitrary email headers.

Visible skill order:

```text
CLASSIFIER / source_owner / skill_title
```

Example:

```text
API_DESIGN / addyosmani / api-and-interface-design
FRONTEND / addyosmani / frontend-ui-engineering
LEARNING / jrice / powershell-fundamentals
```

## Local Setup

```powershell
npm install
npm run build
npm test
npm run test:repos
```

`npm run test:repos` clones and packages:

```text
addyosmani/agent-skills
obra/superpowers
getsentry/skills
mattpocock/skills
```

## Cloudflare Setup

Create a D1 database:

```powershell
npx wrangler d1 create skill_registry
```

Put the returned `database_id` into `wrangler.toml`.

Set secrets:

```powershell
npx wrangler secret put SKILL_REGISTRY_ADMIN_TOKEN
npx wrangler secret put SKILL_REGISTRY_READ_TOKEN
```

Apply migrations and deploy:

```powershell
npm run migrate:remote
npm run deploy
```

Or use the reusable deploy wrapper:

```powershell
.\scripts\Deploy-Cloudflare.ps1 -Smoke
```

## PowerShell App

Menu mode:

```powershell
.\scripts\SkillRegistry.ps1
```

CLI mode:

```powershell
.\scripts\SkillRegistry.ps1 add addyosmani/agent-skills
.\scripts\SkillRegistry.ps1 pending
.\scripts\SkillRegistry.ps1 approve <skillId>
.\scripts\SkillRegistry.ps1 reject <skillId>
.\scripts\SkillRegistry.ps1 list
.\scripts\SkillRegistry.ps1 search frontend
.\scripts\SkillRegistry.ps1 test
```

Default imports are pending. Trusted manual imports can bypass approval:

```powershell
.\scripts\SkillRegistry.ps1 add mattpocock/skills -BypassApproval
```

## Stdio Adapter

Use this only for clients that need local stdio MCP instead of direct remote MCP.

```powershell
$env:SKILL_REGISTRY_URL = "https://your-worker.example.workers.dev"
$env:SKILL_REGISTRY_READ_TOKEN = "<read-token>"
node .\dist\src\stdio-adapter.js
```

The adapter syncs approved resources on startup and keeps a local cache at:

```text
~/.skill-registry-mcp/cache.json
```

The local stdio adapter also exposes install/update tools that are intentionally not available on the remote Worker:

```text
local_skill_status   show cached approved skills and local install state
install_skill        install one approved cached skill to ~/.agents/skills
update_skill         backup and replace one MCP-managed local skill
sync_local_skills    update all MCP-managed local skills from the latest cache
```

Default install root:

```text
~/.agents/skills
```

Override it with either:

```powershell
$env:AGENT_SKILLS_DIR = "C:\path\to\skills"
```

or the tool `root` argument.

Updates create backups under:

```text
~/.skill-registry-mcp/backups
```

Each installed skill receives a `.skill-registry-mcp.json` manifest. `sync_local_skills` only updates skills that have this manifest unless `installMissing` is true.

Exact local installs use the `get_skill_bundle` MCP tool, which returns approved bundle JSON. Rendered Markdown resources remain available for reading, but they are not the installer source of truth because skill files may contain nested code fences.

## Live Smoke

This repo reuses the local utility belt `api-workflow` runner for live API checks:

```powershell
.\scripts\Invoke-LiveSmoke.ps1
```

It writes reports under `%TEMP%\skill-registry-smoke` by default.

Auth-layer smoke:

```powershell
.\scripts\Test-McpAuthLayers.ps1
```

For public no-auth mode:

```powershell
.\scripts\Test-McpAuthLayers.ps1 -PublicRead
```

MCP SDK client smoke:

```powershell
node .\scripts\mcp-client-smoke.mjs
```

Do not count browser success as MCP success. Use `Test-McpAuthLayers.ps1` for curl-style HTTP checks and `mcp-client-smoke.mjs` or the actual target MCP client for MCP success.

## Content Rules

Allowed files:

```text
.md
.txt
.json
.yaml
.yml
.toml
```

Blocked:

```text
.ps1
.js
.mjs
.ts
.py
.exe
.dll
.zip
.png
.pdf
.git/
node_modules/
```

Limits:

```text
max single file: 128 KB
max skill bundle: 512 KB
max import batch uploaded: 10 MB
max local scan: 25 MB
```
