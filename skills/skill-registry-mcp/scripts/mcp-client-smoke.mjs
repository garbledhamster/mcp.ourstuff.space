import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const apiBase = (process.env.SKILL_REGISTRY_URL || "").replace(/\/+$/, "");
const readToken = process.env.SKILL_REGISTRY_READ_TOKEN || "";
const noAuth = process.env.SKILL_REGISTRY_MCP_NO_AUTH === "true";

if (!apiBase) {
  throw new Error("SKILL_REGISTRY_URL is required.");
}
if (!readToken && !noAuth) {
  throw new Error("SKILL_REGISTRY_READ_TOKEN is required.");
}

const requestInit = readToken
  ? {
      headers: {
        Authorization: `Bearer ${readToken}`
      }
    }
  : undefined;

const transport = new StreamableHTTPClientTransport(new URL(`${apiBase}/mcp`), {
  requestInit
});

const client = new Client({
  name: "skill-registry-smoke",
  version: "0.1.0"
});

try {
  await client.connect(transport);
  const tools = await client.listTools();
  const resources = await client.listResources();
  console.log(
    JSON.stringify(
      {
        ok: true,
        transport: "streamable-http",
        auth: readToken ? "bearer" : "none",
        tools: tools.tools.map((tool) => tool.name),
        resourceCount: resources.resources.length
      },
      null,
      2
    )
  );
} finally {
  await client.close();
}
