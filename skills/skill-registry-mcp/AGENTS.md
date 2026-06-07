# Agent Guidance

## Auth Layers

Keep these layers separate in code, docs, and validation:

- TLS success: HTTPS certificate and route are reachable.
- Bearer token success: private `SKILL_REGISTRY_ADMIN_TOKEN` or `SKILL_REGISTRY_READ_TOKEN` was accepted.
- MCP auth success: the target MCP client completed MCP-compatible auth discovery/login and then connected.

Do not treat browser success or `/health` success as MCP success.

## Endpoint Rules

- `/admin/*` stays protected by `SKILL_REGISTRY_ADMIN_TOKEN`.
- `/mcp` stays approved-only.
- `/mcp` may run in public read mode only when `SKILL_REGISTRY_MCP_PUBLIC_READ = "true"`.
- Public read mode means no-auth clients can read approved skills; it does not verify ChatGPT user email, account, workspace, or organization identity.
- Pending imports and review actions stay under `/admin/*`; never expose pending skills through `/mcp`.
- Private/local reads may use `SKILL_REGISTRY_READ_TOKEN`.
- `/mcp` must remain a valid MCP JSON-RPC transport endpoint, not a custom REST-only API.
- In private bearer mode, missing or invalid `/mcp` auth should return `401` with a `WWW-Authenticate` header that points to `/.well-known/oauth-protected-resource`.

## OAuth Readiness

The v1 remote auth mode is private bearer token plus local stdio adapter. Full remote OAuth login is not implemented unless the OAuth issuer and endpoints are configured and validated with the target MCP client.

For ChatGPT no-auth compatibility, public read mode can be enabled. Treat it as public approved-content publishing, not user authentication. If the user wants to restrict by email/account such as a ChatGPT email, implement real OAuth or another verifiable signed-token flow; never trust an arbitrary header or claimed email string.

Keep these routes present:

- `/.well-known/oauth-protected-resource`
- `/.well-known/oauth-authorization-server`

If full OAuth is not configured, they must return clear JSON metadata/status saying v1 supports private bearer-token mode and local stdio adapter mode, not full remote OAuth login yet.

Do not put Cloudflare Access in front of `/mcp` unless the chosen MCP clients can actually complete that auth flow.

## Validation

Use tests and scripts that prove each layer:

- `npm test`
- `npm run test:repos`
- `.\scripts\Test-McpAuthLayers.ps1`
- `node .\scripts\mcp-client-smoke.mjs`

Live MCP success requires a target MCP client or MCP SDK client, not just a browser or `curl` health check.
