import { renderSkillBundle, renderSkillList, skillUri } from "./render.js";
import type { RegistryStore, SkillSummary } from "./types.js";

const PROTOCOL_VERSION = "2025-06-18";

interface JsonRpcRequest {
  jsonrpc?: "2.0";
  id?: string | number | null;
  method?: string;
  params?: unknown;
}

export async function handleMcpRequest(request: Request, store: RegistryStore): Promise<Response> {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders() });
  }
  if (request.method !== "POST") {
    return json({ error: "MCP endpoint expects JSON-RPC POST" }, 405);
  }

  let body: JsonRpcRequest | JsonRpcRequest[];
  try {
    body = (await request.json()) as JsonRpcRequest | JsonRpcRequest[];
  } catch {
    return jsonRpcHttpError(null, -32700, "Parse error");
  }

  if (Array.isArray(body)) {
    const responses = [];
    for (const item of body) {
      const response = await dispatchMcp(item, store);
      if (response) responses.push(response);
    }
    return json(responses);
  }

  const response = await dispatchMcp(body, store);
  if (!response) {
    return new Response(null, { status: 202, headers: corsHeaders() });
  }
  return json(response);
}

async function dispatchMcp(request: JsonRpcRequest, store: RegistryStore): Promise<unknown | null> {
  const id = request.id ?? null;
  const method = request.method;
  if (!method) return jsonRpcError(id, -32600, "Invalid Request");

  try {
    switch (method) {
      case "initialize":
        return jsonRpcResult(id, {
          protocolVersion: PROTOCOL_VERSION,
          capabilities: {
            tools: {},
            resources: {}
          },
          serverInfo: {
            name: "skill-registry-mcp",
            version: "0.1.0"
          }
        });
      case "notifications/initialized":
        return null;
      case "ping":
        return jsonRpcResult(id, {});
      case "tools/list":
        return jsonRpcResult(id, { tools: toolsList() });
      case "tools/call":
        return jsonRpcResult(id, await callTool(request.params, store));
      case "resources/list":
        return jsonRpcResult(id, { resources: await listResources(store) });
      case "resources/read":
        return jsonRpcResult(id, await readResource(request.params, store));
      case "prompts/list":
        return jsonRpcResult(id, { prompts: [] });
      default:
        return jsonRpcError(id, -32601, `Method not found: ${method}`);
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return jsonRpcError(id, -32000, message);
  }
}

function toolsList() {
  return [
    {
      name: "list_skills",
      title: "List approved skills",
      description: "List approved skill registry entries in CLASSIFIER / owner / title order.",
      inputSchema: {
        type: "object",
        properties: {
          classifier: { type: "string", description: "Optional fixed classifier such as FRONTEND or SECURITY." },
          sourceOwner: { type: "string", description: "Optional GitHub owner or personal namespace." },
          query: { type: "string", description: "Optional text query." },
          format: { type: "string", enum: ["markdown", "json"], default: "markdown" }
        },
        additionalProperties: false
      },
      annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false }
    },
    {
      name: "get_skill",
      title: "Get an approved skill",
      description: "Return full approved skill instructions by URI or classifier/sourceOwner/slug.",
      inputSchema: {
        type: "object",
        properties: {
          uri: { type: "string", description: "skills://CLASSIFIER/owner/slug URI." },
          classifier: { type: "string" },
          sourceOwner: { type: "string" },
          slug: { type: "string" }
        },
        additionalProperties: false
      },
      annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false }
    },
    {
      name: "get_skill_bundle",
      title: "Get an approved skill bundle",
      description: "Return the exact approved skill bundle JSON by URI or classifier/sourceOwner/slug for local installers.",
      inputSchema: {
        type: "object",
        properties: {
          uri: { type: "string", description: "skills://CLASSIFIER/owner/slug URI." },
          classifier: { type: "string" },
          sourceOwner: { type: "string" },
          slug: { type: "string" }
        },
        additionalProperties: false
      },
      annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false }
    },
    {
      name: "search_skills",
      title: "Search approved skills",
      description: "Search approved skills by title, description, slug, owner, or classifier.",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string" },
          classifier: { type: "string" },
          sourceOwner: { type: "string" }
        },
        additionalProperties: false
      },
      annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false }
    },
    {
      name: "sync_skills",
      title: "Sync approved skills",
      description: "Return the current approved-skill manifest for client cache refresh.",
      inputSchema: {
        type: "object",
        properties: {},
        additionalProperties: false
      },
      annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false }
    }
  ];
}

async function callTool(params: unknown, store: RegistryStore): Promise<unknown> {
  const toolParams = asRecord(params);
  const name = String(toolParams.name ?? "");
  const args = asRecord(toolParams.arguments ?? {});

  if (name === "list_skills") {
    const skills = await store.listSkills({
      approvedOnly: true,
      query: stringOrUndefined(args.query),
      classifier: stringOrUndefined(args.classifier),
      sourceOwner: stringOrUndefined(args.sourceOwner)
    });
    const format = args.format === "json" ? "json" : "markdown";
    return textContent(format === "json" ? JSON.stringify(skills, null, 2) : renderSkillList(skills));
  }

  if (name === "get_skill") {
    const detail = args.uri
      ? await store.getApprovedBundleByUri(String(args.uri))
      : await store.getApprovedBundle(String(args.classifier ?? ""), String(args.sourceOwner ?? ""), String(args.slug ?? ""));
    if (!detail) throw new Error("approved skill not found");
    return textContent(renderSkillBundle(detail.bundle));
  }

  if (name === "get_skill_bundle") {
    const detail = args.uri
      ? await store.getApprovedBundleByUri(String(args.uri))
      : await store.getApprovedBundle(String(args.classifier ?? ""), String(args.sourceOwner ?? ""), String(args.slug ?? ""));
    if (!detail) throw new Error("approved skill not found");
    return textContent(JSON.stringify(detail.bundle, null, 2));
  }

  if (name === "search_skills") {
    const skills = await store.listSkills({
      approvedOnly: true,
      query: stringOrUndefined(args.query),
      classifier: stringOrUndefined(args.classifier),
      sourceOwner: stringOrUndefined(args.sourceOwner)
    });
    return textContent(renderSkillList(skills));
  }

  if (name === "sync_skills") {
    const skills = await store.listSkills({ approvedOnly: true });
    return textContent(JSON.stringify({ syncedAt: new Date().toISOString(), count: skills.length, skills }, null, 2));
  }

  throw new Error(`unknown tool: ${name}`);
}

async function listResources(store: RegistryStore): Promise<unknown[]> {
  const skills = await store.listSkills({ approvedOnly: true });
  return skills.map((skill) => ({
    uri: skillUri(skill),
    name: `${skill.classifier}/${skill.sourceOwner}/${skill.slug}`,
    title: `${skill.classifier} / ${skill.sourceOwner} / ${skill.title}`,
    description: skill.description,
    mimeType: "text/markdown"
  }));
}

async function readResource(params: unknown, store: RegistryStore): Promise<unknown> {
  const record = asRecord(params);
  const uri = String(record.uri ?? "");
  const detail = await store.getApprovedBundleByUri(uri);
  if (!detail) throw new Error("approved resource not found");
  return {
    contents: [
      {
        uri,
        mimeType: "text/markdown",
        text: renderSkillBundle(detail.bundle)
      }
    ]
  };
}

function textContent(text: string): unknown {
  return {
    content: [
      {
        type: "text",
        text
      }
    ]
  };
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

function stringOrUndefined(value: unknown): string | undefined {
  if (typeof value !== "string" || value.trim() === "") return undefined;
  return value;
}

function jsonRpcResult(id: string | number | null, result: unknown): unknown {
  return { jsonrpc: "2.0", id, result };
}

function jsonRpcError(id: string | number | null, code: number, message: string): unknown {
  return { jsonrpc: "2.0", id, error: { code, message } };
}

function jsonRpcHttpError(id: string | number | null, code: number, message: string): Response {
  return json(jsonRpcError(id, code, message), 400);
}

function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value, null, 2), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      ...corsHeaders()
    }
  });
}

function corsHeaders(): HeadersInit {
  return {
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET, POST, DELETE, OPTIONS",
    "access-control-allow-headers": "authorization, content-type, mcp-protocol-version",
    "access-control-expose-headers": "www-authenticate"
  };
}
