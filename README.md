# mcp.ourstuff.space

Public home for Ourstuff MCP tools, skills, and installation guidance.

The site should help users connect the MCP from three practical surfaces:

- CLI agents and terminal workflows
- Desktop agents that consume MCP server configuration
- Browser-based agents and web MCP clients

The migrated source now lives under:

- `skills/` - personal agent skills and the skill registry MCP work
- `tools/` - shareable MCP-capable tools, starting with Local AI Brain

## Domain routing

`mcp.ourstuff.space` can keep GitHub Pages as the frontend origin while Cloudflare Workers handles only MCP/API paths.

Cloudflare should route these paths to `skills/skill-registry-mcp`:

- `/mcp` - real MCP Streamable HTTP JSON-RPC endpoint
- `/tools` and `/mcp/tools` - JSON discovery for MCP tools
- `/skills` and `/mcp/skills` - JSON discovery for approved skill resources
- `/prompts` and `/mcp/prompts` - JSON discovery for MCP prompts
- `/.well-known/*` - MCP auth metadata
- `/health` - Worker health
- `/admin/*` - token-protected registry admin routes

Everything else on `mcp.ourstuff.space` should continue to fall through to GitHub Pages for the frontend.

Cloudflare note: the hostname must be proxied through Cloudflare for Worker route interception. A DNS-only CNAME to GitHub Pages bypasses Workers entirely.
