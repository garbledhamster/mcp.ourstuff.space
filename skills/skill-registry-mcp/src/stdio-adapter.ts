#!/usr/bin/env node
import { mkdir, readFile, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import readline from "node:readline";
import {
  installCachedSkill,
  isLocalSkillTool,
  localSkillStatus,
  localSkillTools,
  syncLocalSkills,
  type AdapterCache,
  type CachedResource
} from "./local-installer.js";

interface JsonRpcRequest {
  jsonrpc?: "2.0";
  id?: string | number | null;
  method?: string;
  params?: unknown;
}

const apiBase = (process.env.SKILL_REGISTRY_URL ?? "").replace(/\/+$/, "");
const readToken = process.env.SKILL_REGISTRY_READ_TOKEN ?? "";
const cachePath = process.env.SKILL_REGISTRY_CACHE_PATH || path.join(os.homedir(), ".skill-registry-mcp", "cache.json");
let cache: AdapterCache = { syncedAt: "", resources: [] };

async function main() {
  cache = await loadCache();
  await syncCache().catch(() => undefined);

  const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
  rl.on("line", async (line) => {
    if (!line.trim()) return;
    let request: JsonRpcRequest;
    try {
      request = JSON.parse(line) as JsonRpcRequest;
    } catch {
      write({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } });
      return;
    }

    const localToolResponse = await tryLocalTool(request);
    if (localToolResponse) {
      write(localToolResponse);
      return;
    }

    const remote = await tryRemote(request);
    if (remote) {
      await updateCacheFromRemote(request, remote);
      write(mergeLocalToolList(request, remote));
      return;
    }

    const fallback = handleFromCache(request);
    if (fallback) {
      write(fallback);
      return;
    }

    write({ jsonrpc: "2.0", id: request.id ?? null, error: { code: -32000, message: "remote MCP unavailable and cache cannot satisfy request" } });
  });
}

async function tryRemote(request: JsonRpcRequest): Promise<unknown | null> {
  if (!apiBase || !readToken) return null;
  try {
    const response = await fetch(`${apiBase}/mcp`, {
      method: "POST",
      headers: {
        authorization: `Bearer ${readToken}`,
        "content-type": "application/json"
      },
      body: JSON.stringify(request)
    });
    if (!response.ok) return null;
    const text = await response.text();
    return text ? JSON.parse(text) : null;
  } catch {
    return null;
  }
}

async function syncCache(): Promise<void> {
  if (!apiBase || !readToken) return;
  const list = (await tryRemote({ jsonrpc: "2.0", id: "cache-list", method: "resources/list", params: {} })) as
    | { result?: { resources?: CachedResource[] } }
    | null;
  const resources = list?.result?.resources ?? [];
  const withText: CachedResource[] = [];
  for (const resource of resources) {
    const read = (await tryRemote({ jsonrpc: "2.0", id: "cache-read", method: "resources/read", params: { uri: resource.uri } })) as
      | { result?: { contents?: Array<{ text?: string }> } }
      | null;
    withText.push({
      ...resource,
      text: read?.result?.contents?.[0]?.text ?? resource.text,
      bundle: await fetchBundle(resource.uri)
    });
  }
  cache = { syncedAt: new Date().toISOString(), resources: withText };
  await saveCache(cache);
}

async function fetchBundle(uri: string): Promise<CachedResource["bundle"]> {
  const response = (await tryRemote({
    jsonrpc: "2.0",
    id: "cache-bundle",
    method: "tools/call",
    params: { name: "get_skill_bundle", arguments: { uri } }
  })) as { result?: { content?: Array<{ text?: string }> } } | null;
  const text = response?.result?.content?.[0]?.text;
  if (!text) return undefined;
  try {
    return JSON.parse(text) as CachedResource["bundle"];
  } catch {
    return undefined;
  }
}

async function updateCacheFromRemote(request: JsonRpcRequest, response: unknown): Promise<void> {
  const record = response && typeof response === "object" ? (response as Record<string, unknown>) : {};
  const result = record.result && typeof record.result === "object" ? (record.result as Record<string, unknown>) : {};
  if (request.method === "resources/list" && Array.isArray(result.resources)) {
    const resources = result.resources as CachedResource[];
    const byUri = new Map(cache.resources.map((item) => [item.uri, item]));
    cache = {
      syncedAt: new Date().toISOString(),
      resources: resources.map((item) => ({ ...item, text: byUri.get(item.uri)?.text }))
    };
    await saveCache(cache);
  }
  if (request.method === "resources/read") {
    const uri = String((request.params as { uri?: unknown } | undefined)?.uri ?? "");
    const contents = Array.isArray(result.contents) ? (result.contents as Array<{ text?: string }>) : [];
    const text = contents[0]?.text;
    if (uri && text) {
      const existing = cache.resources.find((item) => item.uri === uri);
      if (existing) existing.text = text;
      await saveCache(cache);
    }
  }
  if (request.method === "tools/call") {
    const params = request.params && typeof request.params === "object" ? (request.params as Record<string, unknown>) : {};
    if (params.name === "get_skill_bundle") {
      const args = params.arguments && typeof params.arguments === "object" ? (params.arguments as Record<string, unknown>) : {};
      const uri = String(args.uri ?? "");
      const content = Array.isArray(result.content) ? (result.content as Array<{ text?: string }>) : [];
      const text = content[0]?.text;
      if (uri && text) {
        const existing = cache.resources.find((item) => item.uri === uri);
        if (existing) {
          try {
            existing.bundle = JSON.parse(text) as CachedResource["bundle"];
            await saveCache(cache);
          } catch {
            // Keep text cache even if a legacy server returns non-JSON.
          }
        }
      }
    }
  }
}

function handleFromCache(request: JsonRpcRequest): unknown | null {
  const id = request.id ?? null;
  if (request.method === "initialize") {
    return {
      jsonrpc: "2.0",
      id,
      result: {
        protocolVersion: "2025-06-18",
        capabilities: { tools: {}, resources: {} },
        serverInfo: { name: "skill-registry-mcp-adapter", version: "0.1.0" }
      }
    };
  }
  if (request.method === "notifications/initialized") return null;
  if (request.method === "tools/list") {
    return {
      jsonrpc: "2.0",
      id,
      result: {
        tools: [
          {
            name: "list_skills",
            description: "List cached approved skills.",
            inputSchema: { type: "object", properties: {}, additionalProperties: true }
          },
          {
            name: "get_skill",
            description: "Get cached approved skill by URI.",
            inputSchema: { type: "object", properties: { uri: { type: "string" } }, additionalProperties: true }
          },
          {
            name: "search_skills",
            description: "Search cached approved skills.",
            inputSchema: { type: "object", properties: { query: { type: "string" } }, additionalProperties: true }
          },
          {
            name: "sync_skills",
            description: "Report cached skill sync status.",
            inputSchema: { type: "object", properties: {}, additionalProperties: false }
          },
          ...localSkillTools()
        ]
      }
    };
  }
  if (request.method === "resources/list") {
    return { jsonrpc: "2.0", id, result: { resources: cache.resources.map(({ text, ...rest }) => rest) } };
  }
  if (request.method === "resources/read") {
    const uri = String((request.params as { uri?: unknown } | undefined)?.uri ?? "");
    const resource = cache.resources.find((item) => item.uri === uri);
    if (!resource?.text) return null;
    return {
      jsonrpc: "2.0",
      id,
      result: {
        contents: [{ uri, mimeType: resource.mimeType || "text/markdown", text: resource.text }]
      }
    };
  }
  if (request.method === "tools/call") {
    return handleCachedToolCall(id, request.params);
  }
  return null;
}

function handleCachedToolCall(id: string | number | null, params: unknown): unknown {
  const record = params && typeof params === "object" ? (params as Record<string, unknown>) : {};
  const name = String(record.name ?? "");
  const args = record.arguments && typeof record.arguments === "object" ? (record.arguments as Record<string, unknown>) : {};
  if (name === "sync_skills") {
    return textResult(id, JSON.stringify({ cached: true, syncedAt: cache.syncedAt, count: cache.resources.length }, null, 2));
  }
  if (name === "list_skills") {
    return textResult(id, cache.resources.map((item) => item.title).join("\n") || "No cached approved skills.");
  }
  if (name === "get_skill") {
    const uri = String(args.uri ?? "");
    const resource = cache.resources.find((item) => item.uri === uri);
    if (!resource?.text) return { jsonrpc: "2.0", id, error: { code: -32000, message: "cached skill not found" } };
    return textResult(id, resource.text);
  }
  if (name === "get_skill_bundle") {
    const uri = String(args.uri ?? "");
    const resource = cache.resources.find((item) => item.uri === uri);
    if (!resource?.bundle) return { jsonrpc: "2.0", id, error: { code: -32000, message: "cached skill bundle not found" } };
    return textResult(id, JSON.stringify(resource.bundle, null, 2));
  }
  if (name === "search_skills") {
    const query = String(args.query ?? "").toLowerCase();
    const matches = cache.resources.filter((item) =>
      [item.uri, item.name, item.title, item.description, item.text ?? ""].some((value) => value.toLowerCase().includes(query))
    );
    return textResult(id, matches.map((item) => item.title).join("\n") || "No cached approved skills found.");
  }
  return { jsonrpc: "2.0", id, error: { code: -32602, message: `unknown cached tool: ${name}` } };
}

async function tryLocalTool(request: JsonRpcRequest): Promise<unknown | null> {
  if (request.method !== "tools/call") return null;
  const record = request.params && typeof request.params === "object" ? (request.params as Record<string, unknown>) : {};
  const name = String(record.name ?? "");
  if (!isLocalSkillTool(name)) return null;
  const args = record.arguments && typeof record.arguments === "object" ? (record.arguments as Record<string, unknown>) : {};
  try {
    if (name === "local_skill_status") {
      return textResult(request.id ?? null, await localSkillStatus(cache, typeof args.root === "string" ? args.root : undefined));
    }
    if (name === "install_skill") {
      return textResult(request.id ?? null, await installCachedSkill(cache, args));
    }
    if (name === "update_skill") {
      return textResult(request.id ?? null, await installCachedSkill(cache, args, { update: true }));
    }
    if (name === "sync_local_skills") {
      await syncCache().catch(() => undefined);
      return textResult(request.id ?? null, await syncLocalSkills(cache, args));
    }
  } catch (error) {
    return { jsonrpc: "2.0", id: request.id ?? null, error: { code: -32000, message: error instanceof Error ? error.message : String(error) } };
  }
  return null;
}

function mergeLocalToolList(request: JsonRpcRequest, response: unknown): unknown {
  if (request.method !== "tools/list") return response;
  const record = response && typeof response === "object" ? (response as Record<string, unknown>) : {};
  const result = record.result && typeof record.result === "object" ? (record.result as Record<string, unknown>) : {};
  if (!Array.isArray(result.tools)) return response;
  const existingNames = new Set((result.tools as Array<{ name?: string }>).map((tool) => tool.name));
  result.tools = [...(result.tools as unknown[]), ...localSkillTools().filter((tool) => !existingNames.has(tool.name))];
  return response;
}

function textResult(id: string | number | null, text: string): unknown {
  return { jsonrpc: "2.0", id, result: { content: [{ type: "text", text }] } };
}

async function loadCache(): Promise<AdapterCache> {
  try {
    return JSON.parse(await readFile(cachePath, "utf8")) as AdapterCache;
  } catch {
    return { syncedAt: "", resources: [] };
  }
}

async function saveCache(nextCache: AdapterCache): Promise<void> {
  await mkdir(path.dirname(cachePath), { recursive: true });
  await writeFile(cachePath, JSON.stringify(nextCache, null, 2), "utf8");
}

function write(value: unknown): void {
  if (value === null) return;
  process.stdout.write(`${JSON.stringify(value)}\n`);
}

main().catch((error) => {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 1;
});
