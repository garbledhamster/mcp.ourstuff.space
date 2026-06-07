import {
  authorizationServerMetadata,
  mcpAuthChallenge,
  protectedResourceMetadata,
  publicReadEnabled,
  type AuthMetadataEnv
} from "./auth-metadata.js";
import { diffBundles } from "./diff.js";
import { handleMcpRequest } from "./mcp.js";
import { D1RegistryStore, validateImportBody } from "./store.js";
import type { RegistryStore } from "./types.js";

export interface Env {
  DB: D1Database;
  SKILL_REGISTRY_ADMIN_TOKEN: string;
  SKILL_REGISTRY_READ_TOKEN: string;
  SKILL_REGISTRY_UPLOADER?: string;
  SKILL_REGISTRY_MCP_PUBLIC_READ?: string;
  SKILL_REGISTRY_OAUTH_ISSUER?: string;
  SKILL_REGISTRY_OAUTH_AUTHORIZATION_ENDPOINT?: string;
  SKILL_REGISTRY_OAUTH_TOKEN_ENDPOINT?: string;
  SKILL_REGISTRY_OAUTH_REGISTRATION_ENDPOINT?: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    return createHandler(new D1RegistryStore(env.DB), env)(request);
  }
};

export function createHandler(
  store: RegistryStore,
  env: Pick<
    Env,
    | "SKILL_REGISTRY_ADMIN_TOKEN"
    | "SKILL_REGISTRY_READ_TOKEN"
    | "SKILL_REGISTRY_UPLOADER"
    | "SKILL_REGISTRY_MCP_PUBLIC_READ"
    | "SKILL_REGISTRY_OAUTH_ISSUER"
    | "SKILL_REGISTRY_OAUTH_AUTHORIZATION_ENDPOINT"
    | "SKILL_REGISTRY_OAUTH_TOKEN_ENDPOINT"
    | "SKILL_REGISTRY_OAUTH_REGISTRATION_ENDPOINT"
  >
) {
  return async function handle(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    if (url.pathname === "/health") {
      return json({ ok: true, service: "skill-registry-mcp", time: new Date().toISOString() });
    }

    if (url.pathname === "/.well-known/oauth-protected-resource" || url.pathname === "/.well-known/oauth-protected-resource/mcp") {
      return json(protectedResourceMetadata(request, env));
    }

    if (url.pathname === "/.well-known/oauth-authorization-server") {
      return json(authorizationServerMetadata(request, env));
    }

    if (url.pathname === "/mcp") {
      if (!publicReadEnabled(env)) {
        const auth = authorizeMcp(request, env.SKILL_REGISTRY_READ_TOKEN, env.SKILL_REGISTRY_ADMIN_TOKEN);
        if (!auth.ok) return json({ error: auth.error, auth: protectedResourceMetadata(request, env).mcp_auth_status }, auth.status, auth.headers);
      }
      return handleMcpRequest(request, store);
    }

    if (url.pathname.startsWith("/admin")) {
      const auth = authorize(request, env.SKILL_REGISTRY_ADMIN_TOKEN);
      if (!auth.ok) return json({ error: auth.error }, auth.status);
      return handleAdmin(request, store, env.SKILL_REGISTRY_UPLOADER || "jrice");
    }

    return json({ error: "not found" }, 404);
  };
}

async function handleAdmin(request: Request, store: RegistryStore, defaultUploader: string): Promise<Response> {
  const url = new URL(request.url);
  const path = url.pathname;

  if (request.method === "POST" && path === "/admin/imports") {
    const body = validateImportBody(await request.json());
    const result = await store.importBundles({
      skills: body.skills,
      uploadedBy: body.uploadedBy || defaultUploader,
      bypassApproval: Boolean(body.bypassApproval)
    });
    return json(result, 201);
  }

  if (request.method === "GET" && path === "/admin/pending") {
    return json({ pending: await store.listPending() });
  }

  if (request.method === "GET" && path === "/admin/skills") {
    return json({
      skills: await store.listSkills({
        query: url.searchParams.get("q") ?? undefined,
        classifier: url.searchParams.get("classifier") ?? undefined,
        sourceOwner: url.searchParams.get("sourceOwner") ?? undefined
      })
    });
  }

  const skillMatch = /^\/admin\/skills\/([^/]+)(?:\/([^/]+))?$/.exec(path);
  if (skillMatch) {
    const skillId = decodeURIComponent(skillMatch[1]);
    const action = skillMatch[2];

    if (!action && request.method === "GET") {
      const skill = await store.getSkill(skillId);
      if (!skill) return json({ error: "skill not found" }, 404);
      return json({ skill, versions: await store.listVersions(skillId) });
    }

    if (action === "diff" && request.method === "GET") {
      const versions = await store.listVersions(skillId);
      const pending = versions.find((version) => version.status === "pending");
      if (!pending) return json({ error: "pending version not found" }, 404);
      const skill = await store.getSkill(skillId);
      const current = skill?.approvedVersionId ? versions.find((version) => version.id === skill.approvedVersionId) : null;
      return text(diffBundles(current?.bundle ?? null, pending.bundle));
    }

    if (action === "approve" && request.method === "POST") {
      const body = await optionalJson(request);
      const approved = await store.approveVersion(skillId, typeof body.versionId === "string" ? body.versionId : undefined);
      if (!approved) return json({ error: "pending version not found" }, 404);
      return json({ approved });
    }

    if (action === "reject" && request.method === "POST") {
      const body = await optionalJson(request);
      const rejected = await store.rejectVersion(skillId, typeof body.versionId === "string" ? body.versionId : undefined);
      if (!rejected) return json({ error: "pending version not found" }, 404);
      return json({ rejected });
    }

    if (!action && request.method === "DELETE") {
      const deleted = await store.deleteSkill(skillId);
      return json({ deleted });
    }
  }

  if (request.method === "POST" && path === "/admin/tokens/rotate") {
    return json(
      {
        error: "token rotation is intentionally manual",
        nextStep: "Use wrangler secret put SKILL_REGISTRY_ADMIN_TOKEN or SKILL_REGISTRY_READ_TOKEN, then redeploy/restart."
      },
      501
    );
  }

  return json({ error: "admin route not found" }, 404);
}

async function optionalJson(request: Request): Promise<Record<string, unknown>> {
  try {
    return (await request.json()) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function authorize(request: Request, ...tokens: Array<string | undefined>): { ok: true } | { ok: false; status: number; error: string } {
  const header = request.headers.get("authorization") ?? "";
  const token = /^Bearer\s+(.+)$/i.exec(header)?.[1] ?? "";
  const allowed = tokens.filter(Boolean);
  if (allowed.length === 0) return { ok: false, status: 500, error: "server token is not configured" };
  if (!token) return { ok: false, status: 401, error: "missing bearer token" };
  if (!allowed.includes(token)) return { ok: false, status: 403, error: "invalid bearer token" };
  return { ok: true };
}

function authorizeMcp(
  request: Request,
  ...tokens: Array<string | undefined>
): { ok: true } | { ok: false; status: number; error: string; headers: HeadersInit } {
  const auth = authorize(request, ...tokens);
  if (auth.ok) return auth;
  return {
    ok: false,
    status: auth.status === 500 ? 500 : 401,
    error: auth.error,
    headers: {
      "www-authenticate": mcpAuthChallenge(request)
    }
  };
}

function json(value: unknown, status = 200, extraHeaders: HeadersInit = {}): Response {
  return new Response(JSON.stringify(value, null, 2), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      ...corsHeaders(),
      ...extraHeaders
    }
  });
}

function text(value: string, status = 200): Response {
  return new Response(value, {
    status,
    headers: {
      "content-type": "text/plain; charset=utf-8",
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
