import { mkdir, readFile, writeFile } from "node:fs/promises";
import { mkdtemp } from "node:fs/promises";
import { createServer } from "node:http";
import os from "node:os";
import path from "node:path";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { describe, expect, it } from "vitest";
import { classifySkill } from "../src/classifier.js";
import { packageSkills } from "../src/importer.js";
import { installCachedSkill, localSkillStatus, type AdapterCache } from "../src/local-installer.js";
import { MemoryRegistryStore } from "../src/memory-store.js";
import { createHandler } from "../src/worker.js";

describe("classifier", () => {
  it("classifies specific skill names deterministically", () => {
    expect(
      classifySkill({
        slug: "api-and-interface-design",
        title: "API and Interface Design",
        description: "Design APIs and contracts for agent workflows.",
        relativePath: "skills/api-and-interface-design",
        content: "# API and Interface Design"
      }).classifier
    ).toBe("API_DESIGN");

    expect(
      classifySkill({
        slug: "security-and-hardening",
        title: "Security and Hardening",
        description: "Review auth, permissions, secrets, and threat models.",
        relativePath: "skills/security-and-hardening",
        content: "# Security and Hardening"
      }).classifier
    ).toBe("SECURITY");

    expect(
      classifySkill({
        slug: "linear-thinking-coders",
        title: "linear-thinking-coders",
        description: "Orchestrates paired frontend design councils and UI specialist teams.",
        relativePath: "skills/linear-thinking-coders",
        content: "# Linear Thinking Coders"
      }).classifier
    ).toBe("FRONTEND");
  });
});

describe("importer", () => {
  it("packages multiple local skills and blocks executable files", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "skill-registry-test-"));
    await mkdir(path.join(root, "skills", "frontend-ui-engineering"), { recursive: true });
    await mkdir(path.join(root, "skills", "security-and-hardening"), { recursive: true });
    await writeFile(
      path.join(root, "skills", "frontend-ui-engineering", "SKILL.md"),
      "---\nname: Frontend UI Engineering\ndescription: Build accessible frontend UI components.\n---\n# Frontend UI Engineering\n",
      "utf8"
    );
    await writeFile(path.join(root, "skills", "frontend-ui-engineering", "example.json"), "{\"ok\":true}\n", "utf8");
    await writeFile(path.join(root, "skills", "frontend-ui-engineering", "run.js"), "console.log('blocked')\n", "utf8");
    await writeFile(
      path.join(root, "skills", "security-and-hardening", "SKILL.md"),
      "---\nname: Security and Hardening\ndescription: Review auth and secrets.\n---\n# Security\n",
      "utf8"
    );

    const report = await packageSkills({ source: root, uploadedBy: "jrice" });
    expect(report.skills).toHaveLength(2);
    expect(report.skills.map((skill) => skill.sourceOwner)).toEqual(["jrice", "jrice"]);
    expect(report.skills.find((skill) => skill.slug === "frontend-ui-engineering")?.classifier).toBe("FRONTEND");
    expect(report.rejected.some((item) => item.path.endsWith("run.js"))).toBe(true);
  });
});

describe("worker and MCP", () => {
  it("keeps pending skills out of /mcp until approval", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "skill-registry-worker-"));
    await mkdir(path.join(root, "skills", "api-and-interface-design"), { recursive: true });
    await writeFile(
      path.join(root, "skills", "api-and-interface-design", "SKILL.md"),
      "---\nname: API and Interface Design\ndescription: Design API contracts.\n---\n# API Design\n",
      "utf8"
    );
    const report = await packageSkills({ source: root, uploadedBy: "jrice" });
    const store = new MemoryRegistryStore();
    const handler = createHandler(store, {
      SKILL_REGISTRY_ADMIN_TOKEN: "admin",
      SKILL_REGISTRY_READ_TOKEN: "read",
      SKILL_REGISTRY_UPLOADER: "jrice"
    });

    const importResponse = await handler(
      new Request("https://registry.test/admin/imports", {
        method: "POST",
        headers: { authorization: "Bearer admin", "content-type": "application/json" },
        body: JSON.stringify({ skills: report.skills, uploadedBy: "jrice", bypassApproval: false })
      })
    );
    expect(importResponse.status).toBe(201);

    const listPending = await handler(
      new Request("https://registry.test/mcp", {
        method: "POST",
        headers: { authorization: "Bearer read", "content-type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "resources/list", params: {} })
      })
    );
    const pendingMcp = (await listPending.json()) as { result: { resources: unknown[] } };
    expect(pendingMcp.result.resources).toHaveLength(0);

    const pendingAdmin = await handler(
      new Request("https://registry.test/admin/pending", {
        headers: { authorization: "Bearer admin" }
      })
    );
    const pendingBody = (await pendingAdmin.json()) as { pending: Array<{ skillId: string }> };
    const skillId = pendingBody.pending[0].skillId;

    const approve = await handler(
      new Request(`https://registry.test/admin/skills/${encodeURIComponent(skillId)}/approve`, {
        method: "POST",
        headers: { authorization: "Bearer admin", "content-type": "application/json" },
        body: "{}"
      })
    );
    expect(approve.status).toBe(200);

    const listApproved = await handler(
      new Request("https://registry.test/mcp", {
        method: "POST",
        headers: { authorization: "Bearer read", "content-type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", id: 2, method: "resources/list", params: {} })
      })
    );
    const approvedMcp = (await listApproved.json()) as { result: { resources: Array<{ uri: string }> } };
    expect(approvedMcp.result.resources).toHaveLength(1);
    expect(approvedMcp.result.resources[0].uri).toContain("API_DESIGN");

    const bundleResponse = await handler(
      new Request("https://registry.test/mcp", {
        method: "POST",
        headers: { authorization: "Bearer read", "content-type": "application/json" },
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: 3,
          method: "tools/call",
          params: { name: "get_skill_bundle", arguments: { uri: approvedMcp.result.resources[0].uri } }
        })
      })
    );
    const bundleMcp = (await bundleResponse.json()) as { result: { content: Array<{ text: string }> } };
    const bundle = JSON.parse(bundleMcp.result.content[0].text) as { slug: string; files: Array<{ path: string; content: string }> };
    expect(bundle.slug).toBe("api-and-interface-design");
    expect(bundle.files.find((file) => file.path === "SKILL.md")?.content).toContain("# API Design");

    const denied = await handler(new Request("https://registry.test/admin/skills"));
    expect(denied.status).toBe(401);
  });

  it("separates TLS reachability, private bearer auth, and MCP OAuth discovery", async () => {
    const store = new MemoryRegistryStore();
    const handler = createHandler(store, {
      SKILL_REGISTRY_ADMIN_TOKEN: "admin",
      SKILL_REGISTRY_READ_TOKEN: "read",
      SKILL_REGISTRY_UPLOADER: "jrice"
    });

    const tlsOnly = await handler(new Request("https://registry.test/health"));
    expect(tlsOnly.status).toBe(200);

    const protectedResource = await handler(new Request("https://registry.test/.well-known/oauth-protected-resource"));
    expect(protectedResource.status).toBe(200);
    const protectedBody = (await protectedResource.json()) as {
      resource: string;
      authorization_servers: string[];
      mcp_auth_status: { oauth_implemented: boolean; private_bearer_token_supported: boolean };
    };
    expect(protectedBody.resource).toBe("https://registry.test/mcp");
    expect(protectedBody.authorization_servers).toEqual([]);
    expect(protectedBody.mcp_auth_status.oauth_implemented).toBe(false);
    expect(protectedBody.mcp_auth_status.private_bearer_token_supported).toBe(true);

    const authorizationServer = await handler(new Request("https://registry.test/.well-known/oauth-authorization-server"));
    expect(authorizationServer.status).toBe(200);
    const authorizationBody = (await authorizationServer.json()) as {
      authorization_endpoint: string | null;
      token_endpoint: string | null;
      mcp_auth_status: { local_stdio_adapter_supported: boolean };
    };
    expect(authorizationBody.authorization_endpoint).toBeNull();
    expect(authorizationBody.token_endpoint).toBeNull();
    expect(authorizationBody.mcp_auth_status.local_stdio_adapter_supported).toBe(true);

    const missingMcpToken = await handler(
      new Request("https://registry.test/mcp", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "initialize", params: {} })
      })
    );
    expect(missingMcpToken.status).toBe(401);
    expect(missingMcpToken.headers.get("www-authenticate")).toContain("/.well-known/oauth-protected-resource");

    const privateBearer = await handler(
      new Request("https://registry.test/mcp", {
        method: "POST",
        headers: { authorization: "Bearer read", "content-type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", id: 2, method: "initialize", params: {} })
      })
    );
    expect(privateBearer.status).toBe(200);
    const mcpBody = (await privateBearer.json()) as { result: { protocolVersion: string } };
    expect(mcpBody.result.protocolVersion).toBe("2025-06-18");
  });

  it("can expose /mcp as no-auth public read while keeping admin private", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "skill-registry-public-"));
    await mkdir(path.join(root, "skills", "learning-powershell"), { recursive: true });
    await writeFile(
      path.join(root, "skills", "learning-powershell", "SKILL.md"),
      "---\nname: Learning PowerShell\ndescription: Learn PowerShell basics.\n---\n# Learning PowerShell\n",
      "utf8"
    );
    const report = await packageSkills({ source: root, uploadedBy: "jrice" });
    const store = new MemoryRegistryStore();
    await store.importBundles({ skills: report.skills, uploadedBy: "jrice", bypassApproval: true });
    const handler = createHandler(store, {
      SKILL_REGISTRY_ADMIN_TOKEN: "admin",
      SKILL_REGISTRY_READ_TOKEN: "read",
      SKILL_REGISTRY_UPLOADER: "jrice",
      SKILL_REGISTRY_MCP_PUBLIC_READ: "true"
    });

    const mcp = await handler(
      new Request("https://registry.test/mcp", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "resources/list", params: {} })
      })
    );
    expect(mcp.status).toBe(200);
    const mcpBody = (await mcp.json()) as { result: { resources: Array<{ uri: string }> } };
    expect(mcpBody.result.resources).toHaveLength(1);
    expect(mcpBody.result.resources[0].uri).toContain("LEARNING");

    const adminDenied = await handler(new Request("https://registry.test/admin/skills"));
    expect(adminDenied.status).toBe(401);

    const metadata = await handler(new Request("https://registry.test/.well-known/oauth-protected-resource"));
    const metadataBody = (await metadata.json()) as { mcp_auth_status: { public_read_enabled: boolean; identity_verification: string } };
    expect(metadataBody.mcp_auth_status.public_read_enabled).toBe(true);
    expect(metadataBody.mcp_auth_status.identity_verification).toContain("does not verify ChatGPT user email");
  });

  it("connects with the MCP SDK Streamable HTTP client using private bearer mode", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "skill-registry-sdk-"));
    await mkdir(path.join(root, "skills", "frontend-ui-engineering"), { recursive: true });
    await writeFile(
      path.join(root, "skills", "frontend-ui-engineering", "SKILL.md"),
      "---\nname: Frontend UI Engineering\ndescription: Build accessible frontend UI components.\n---\n# Frontend UI Engineering\n",
      "utf8"
    );
    const report = await packageSkills({ source: root, uploadedBy: "jrice" });
    const store = new MemoryRegistryStore();
    await store.importBundles({ skills: report.skills, uploadedBy: "jrice", bypassApproval: true });
    const handler = createHandler(store, {
      SKILL_REGISTRY_ADMIN_TOKEN: "admin",
      SKILL_REGISTRY_READ_TOKEN: "read",
      SKILL_REGISTRY_UPLOADER: "jrice"
    });
    const server = createServer(async (incoming, outgoing) => {
      const chunks: Buffer[] = [];
      for await (const chunk of incoming) {
        chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
      }
      const request = new Request(`http://127.0.0.1:${addressPort(server) || 0}${incoming.url ?? "/"}`, {
        method: incoming.method,
        headers: incoming.headers as HeadersInit,
        body: chunks.length > 0 ? Buffer.concat(chunks) : undefined
      });
      const response = await handler(request);
      outgoing.statusCode = response.status;
      response.headers.forEach((value, key) => outgoing.setHeader(key, value));
      outgoing.end(Buffer.from(await response.arrayBuffer()));
    });

    await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
    const port = addressPort(server);
    try {
      const client = new Client({ name: "skill-registry-test", version: "0.1.0" });
      const transport = new StreamableHTTPClientTransport(new URL(`http://127.0.0.1:${port}/mcp`), {
        requestInit: {
          headers: {
            Authorization: "Bearer read"
          }
        }
      });
      await client.connect(transport);
      const tools = await client.listTools();
      const resources = await client.listResources();
      expect(tools.tools.map((tool) => tool.name)).toContain("list_skills");
      expect(resources.resources.map((resource) => resource.uri)).toContain("skills://FRONTEND/jrice/frontend-ui-engineering");
      await client.close();
    } finally {
      await new Promise<void>((resolve, reject) => server.close((error) => (error ? reject(error) : resolve())));
    }
  });
});

describe("local installer", () => {
  it("installs and updates exact cached skill bundles with backups", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "skill-registry-install-root-"));
    const source = await mkdtemp(path.join(os.tmpdir(), "skill-registry-install-source-"));
    await mkdir(path.join(source, "skills", "linear-thinking-coders", "references"), { recursive: true });
    await writeFile(
      path.join(source, "skills", "linear-thinking-coders", "SKILL.md"),
      "---\nname: linear-thinking-coders\ndescription: Use when paired frontend coders are needed.\n---\n# Linear Thinking Coders\n",
      "utf8"
    );
    await writeFile(
      path.join(source, "skills", "linear-thinking-coders", "references", "workflow.md"),
      "# Workflow\n\n```text\nnested fences stay inside bundle content\n```\n",
      "utf8"
    );
    const report = await packageSkills({ source, uploadedBy: "jrice", sourceOwner: "garbledhamster" });
    const bundle = report.skills[0];
    const cache: AdapterCache = {
      syncedAt: new Date().toISOString(),
      resources: [
        {
          uri: `skills://${bundle.classifier}/${bundle.sourceOwner}/${bundle.slug}`,
          name: `${bundle.classifier}/${bundle.sourceOwner}/${bundle.slug}`,
          title: bundle.title,
          description: bundle.description,
          mimeType: "text/markdown",
          bundle
        }
      ]
    };

    const install = JSON.parse(await installCachedSkill(cache, { uri: cache.resources[0].uri, root })) as { destination: string; action: string };
    expect(install.action).toBe("installed");
    expect(await readFile(path.join(install.destination, "references", "workflow.md"), "utf8")).toContain("nested fences");
    const status = JSON.parse(await localSkillStatus(cache, root)) as { skills: Array<{ installed: boolean; managed: boolean }> };
    expect(status.skills[0]).toMatchObject({ installed: true, managed: true });

    const updated = {
      ...bundle,
      contentHash: `${bundle.contentHash}-next`,
      files: bundle.files.map((file) => (file.path === "SKILL.md" ? { ...file, content: `${file.content}\nUpdated.\n` } : file))
    };
    cache.resources[0].bundle = updated;
    const update = JSON.parse(await installCachedSkill(cache, { uri: cache.resources[0].uri, root }, { update: true })) as {
      action: string;
      backupPath: string | null;
      destination: string;
    };
    expect(update.action).toBe("updated");
    expect(update.backupPath).toBeTruthy();
    expect(await readFile(path.join(update.destination, "SKILL.md"), "utf8")).toContain("Updated.");
  });
});

function addressPort(server: ReturnType<typeof createServer>): number {
  const address = server.address();
  if (!address || typeof address === "string") return 0;
  return address.port;
}
