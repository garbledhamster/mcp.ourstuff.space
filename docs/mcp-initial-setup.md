# Initial MCP Setup

This project sets up `mcp.ourstuff.space` as the public MCP/API entry point for Ourstuff agent skills and tools while keeping private planning artifacts out of Git.

## Public Runtime Shape

- GitHub Pages owns normal site pages.
- Cloudflare Workers owns only MCP/API paths.
- `skills/skill-registry-mcp` is the first MCP server package.
- `tools/local-ai-brain` remains a shareable tool package, separate from private runtime memory.

## Cloudflare Worker Routes

Route these paths to `skills/skill-registry-mcp`:

- `/mcp`
- `/tools` and `/mcp/tools`
- `/skills` and `/mcp/skills`
- `/prompts` and `/mcp/prompts`
- `/.well-known/*`
- `/health`
- `/admin/*`

Everything else should continue to fall through to the static site.

## MCP Tool Naming

Advertised MCP tool names use:

```text
{origin}.{domain}.{action}
```

Current remote skill-registry tools:

- `ourstuff.skills.list`
- `ourstuff.skills.get`
- `ourstuff.skills.get_bundle`
- `ourstuff.skills.search`
- `ourstuff.skills.sync`

The local stdio adapter also exposes local install/update tools:

- `ourstuff.skills.local_status`
- `ourstuff.skills.install`
- `ourstuff.skills.update`
- `ourstuff.skills.sync_local`

Legacy names such as `list_skills`, `get_skill_bundle`, and `sync_local_skills` remain callable for compatibility, but new clients should use the canonical names.

## Safety Rules

- Pending imports stay out of `/mcp` until approved.
- `/admin/*` requires `SKILL_REGISTRY_ADMIN_TOKEN`.
- Private `/mcp` mode requires `SKILL_REGISTRY_READ_TOKEN` or admin token.
- Public read mode publishes approved content only; it does not verify a ChatGPT email, account, workspace, or organization.
- Browser `/health` success is not MCP success. Use an MCP SDK/client smoke for real validation.

## Verification

From `skills/skill-registry-mcp`:

```powershell
npm run build
npm test
node .\scripts\mcp-client-smoke.mjs
```

Live smoke requires `SKILL_REGISTRY_URL` and either `SKILL_REGISTRY_READ_TOKEN` or `SKILL_REGISTRY_MCP_NO_AUTH=true`.

