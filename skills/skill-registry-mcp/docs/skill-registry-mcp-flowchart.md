# Skill Registry MCP Flow Chart

Endpoint: `https://skill-registry-mcp.jrice.workers.dev/mcp`

This document combines C4 context notation with BPMN-lite flow semantics. It is intentionally scoped to the current V1 Worker: public approved-read MCP, private bearer-read MCP, admin-only imports/review, and D1-backed approved skill storage.

## BPMN-Lite Legend

```text
((event))      Start/end event
[task]         Activity or service task
{gateway}      Decision
[(store)]      Data store
-- message --> Cross-boundary request/response
-. data .->    Data lookup or write
```

## C4 Context

```mermaid
flowchart LR
  user((Agent user))
  mcpClient["MCP client<br/>ChatGPT, Codex, SDK client"]
  admin["Registry admin<br/>curates skill bundles"]
  uploader["Skill source repos<br/>approved upstream bundles"]

  system["Skill Registry MCP<br/>Cloudflare Worker"]
  d1[("Cloudflare D1<br/>skill registry")]
  cache[("Local stdio cache<br/>~/.skill-registry-mcp/cache.json")]

  user -- "asks for skill discovery/read" --> mcpClient
  mcpClient -- "MCP JSON-RPC POST /mcp" --> system
  system -. "approved-only list/read/search" .-> d1
  system -- "resources/tools results" --> mcpClient

  admin -- "admin token + /admin/*" --> system
  uploader -- "packaged skills/import payload" --> admin
  system -. "pending + approved versions" .-> d1

  mcpClient -. "optional local stdio adapter" .-> cache
  cache -- "proxies/syncs via remote /mcp" --> system
```

## C4 Container View

```mermaid
flowchart TB
  subgraph client["Client Boundary"]
    remoteClient["Remote MCP client"]
    stdioAdapter["Local stdio adapter<br/>dist/src/stdio-adapter.js"]
  end

  subgraph worker["Cloudflare Worker"]
    router["HTTP router<br/>src/worker.ts"]
    authMeta["OAuth metadata routes<br/>/.well-known/*"]
    mcpAuth["MCP auth gate<br/>public-read or bearer token"]
    mcpDispatch["MCP dispatcher<br/>src/mcp.ts"]
    adminApi["Admin API<br/>/admin/*"]
  end

  subgraph data["Data Boundary"]
    d1[("D1 registry")]
  end

  remoteClient -->|"POST /mcp JSON-RPC"| router
  stdioAdapter -->|"POST /mcp JSON-RPC<br/>optional bearer token"| router
  router -->|"GET /health"| router
  router -->|"GET /.well-known/*"| authMeta
  router -->|"POST /mcp"| mcpAuth
  mcpAuth -->|"authorized or public read"| mcpDispatch
  mcpDispatch -.->|"listSkills/getApprovedBundle"| d1
  router -->|"admin token /admin/*"| adminApi
  adminApi -.->|"import/list/approve/reject/delete"| d1
```

## BPMN-Lite: MCP Read Flow

```mermaid
flowchart TB
  start((MCP client starts))
  postInit["POST /mcp<br/>JSON-RPC initialize"]
  route["Worker routes request"]
  methodCheck{HTTP method is POST?}
  publicRead{SKILL_REGISTRY_MCP_PUBLIC_READ true?}
  bearer{Valid read/admin bearer token?}
  authError["Return 401<br/>WWW-Authenticate resource metadata"]
  parse{Valid JSON-RPC?}
  dispatch["Dispatch MCP method"]
  init["initialize<br/>return protocolVersion 2025-06-18<br/>tools/resources capabilities"]
  listTools["tools/list<br/>return list_skills, get_skill,<br/>search_skills, sync_skills"]
  listResources["resources/list<br/>return skills:// resources"]
  callTool["tools/call<br/>query approved skills only"]
  readResource["resources/read<br/>return approved skill markdown"]
  d1[("D1 registry<br/>approved skills")]
  response["Return JSON-RPC result"]
  end((Client receives result))

  start --> postInit --> route --> methodCheck
  methodCheck -- "no" --> methodError["405 MCP endpoint expects JSON-RPC POST"] --> end
  methodCheck -- "yes" --> publicRead
  publicRead -- "yes" --> parse
  publicRead -- "no" --> bearer
  bearer -- "no" --> authError --> end
  bearer -- "yes" --> parse
  parse -- "no" --> parseError["JSON-RPC parse error -32700"] --> end
  parse -- "yes" --> dispatch
  dispatch --> init --> response
  dispatch --> listTools --> response
  dispatch --> listResources
  listResources -.->|"listSkills approvedOnly"| d1
  listResources --> response
  dispatch --> callTool
  callTool -.->|"list/search/get approvedOnly"| d1
  callTool --> response
  dispatch --> readResource
  readResource -.->|"getApprovedBundleByUri"| d1
  readResource --> response
  response --> end
```

## BPMN-Lite: Admin Approval Flow

```mermaid
flowchart TB
  adminStart((Admin starts))
  package["Package skill bundle"]
  import["POST /admin/imports<br/>admin bearer token"]
  adminAuth{Admin token valid?}
  validate["Validate import body"]
  pending[("D1 pending version")]
  review["GET /admin/pending<br/>GET /admin/skills/:id/diff"]
  decision{Approve?}
  approve["POST /admin/skills/:id/approve"]
  reject["POST /admin/skills/:id/reject"]
  approved[("D1 approved version")]
  rejected[("D1 rejected version")]
  visible["Visible through /mcp<br/>tools + resources"]
  adminEnd((Flow ends))

  adminStart --> package --> import --> adminAuth
  adminAuth -- "no" --> denied["401/403 admin route denied"] --> adminEnd
  adminAuth -- "yes" --> validate --> pending --> review --> decision
  decision -- "yes" --> approve --> approved --> visible --> adminEnd
  decision -- "no" --> reject --> rejected --> adminEnd
```

## Live Probe Evidence

Observed on 2026-06-03 against `https://skill-registry-mcp.jrice.workers.dev/mcp`:

```text
GET /mcp
  405 Method Not Allowed

POST /mcp initialize
  200 OK
  serverInfo.name = skill-registry-mcp
  serverInfo.version = 0.1.0
  protocolVersion = 2025-06-18
  capabilities = tools, resources

POST /mcp tools/list
  tools = list_skills, get_skill, search_skills, sync_skills

POST /mcp resources/list
  returned approved skills:// resources
```

## Design Notes

- `/mcp` is a JSON-RPC transport endpoint, not a REST browse endpoint.
- Public read mode means approved skills are public content; it does not authenticate a ChatGPT user, email, workspace, or organization.
- Pending imports and review actions stay behind `/admin/*`.
- The read surface is intentionally approved-only: `listSkills({ approvedOnly: true })`, `getApprovedBundle`, and `getApprovedBundleByUri`.
- Full OAuth login is not claimed unless issuer and authorization/token endpoints are configured and validated with a target MCP client.
