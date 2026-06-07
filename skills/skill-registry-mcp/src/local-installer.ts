import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import type { SkillBundle, SkillFile } from "./types.js";

export interface CachedResource {
  uri: string;
  name: string;
  title: string;
  description: string;
  mimeType: string;
  text?: string;
  bundle?: SkillBundle;
}

export interface AdapterCache {
  syncedAt: string;
  resources: CachedResource[];
}

export interface LocalInstallOptions {
  root?: string;
  backupRoot?: string;
  update?: boolean;
  force?: boolean;
}

export const MCP_MANIFEST = ".skill-registry-mcp.json";

export function localSkillTools() {
  return [
    {
      name: "local_skill_status",
      description: "Report cached approved skills and whether they are installed locally.",
      inputSchema: {
        type: "object",
        properties: {
          root: { type: "string", description: "Optional local skill root. Defaults to ~/.agents/skills." }
        },
        additionalProperties: false
      }
    },
    {
      name: "install_skill",
      description: "Install one approved MCP skill bundle into the local skill root. Fails if the target exists unless force is true.",
      inputSchema: {
        type: "object",
        properties: {
          uri: { type: "string", description: "skills://CLASSIFIER/owner/slug URI." },
          slug: { type: "string", description: "Fallback lookup by slug." },
          root: { type: "string", description: "Optional local skill root. Defaults to ~/.agents/skills." },
          force: { type: "boolean", description: "Replace an existing target after backing it up." }
        },
        additionalProperties: false
      }
    },
    {
      name: "update_skill",
      description: "Update one locally installed MCP-managed skill from the cached approved bundle, backing up the existing copy first.",
      inputSchema: {
        type: "object",
        properties: {
          uri: { type: "string", description: "skills://CLASSIFIER/owner/slug URI." },
          slug: { type: "string", description: "Fallback lookup by slug." },
          root: { type: "string", description: "Optional local skill root. Defaults to ~/.agents/skills." }
        },
        additionalProperties: false
      }
    },
    {
      name: "sync_local_skills",
      description: "Update all locally installed MCP-managed skills from the cache. Optionally install missing cached skills.",
      inputSchema: {
        type: "object",
        properties: {
          root: { type: "string", description: "Optional local skill root. Defaults to ~/.agents/skills." },
          installMissing: { type: "boolean", description: "Install cached approved skills that are not present locally." }
        },
        additionalProperties: false
      }
    }
  ];
}

export function isLocalSkillTool(name: string): boolean {
  return localSkillTools().some((tool) => tool.name === name);
}

export async function localSkillStatus(cache: AdapterCache, rootInput?: string): Promise<string> {
  const root = resolveSkillRoot(rootInput);
  const rows = [];
  for (const resource of cache.resources) {
    const slug = skillSlug(resource);
    const destination = path.join(root, slug);
    const manifest = await readManifest(destination);
    rows.push({
      uri: resource.uri,
      slug,
      installed: existsSync(destination),
      managed: manifest?.uri === resource.uri,
      installedHash: manifest?.contentHash ?? null,
      cachedHash: resource.bundle?.contentHash ?? null
    });
  }
  return JSON.stringify({ root, syncedAt: cache.syncedAt, skills: rows }, null, 2);
}

export async function installCachedSkill(cache: AdapterCache, args: Record<string, unknown>, options: LocalInstallOptions = {}): Promise<string> {
  const resource = findResource(cache, args);
  if (!resource) throw new Error("cached approved skill not found; run sync_skills first");
  const bundle = resource.bundle ?? parseRenderedBundle(resource);
  const result = await writeBundle(bundle, resource.uri, {
    root: stringOrUndefined(args.root) ?? options.root,
    backupRoot: options.backupRoot,
    update: options.update,
    force: Boolean(args.force) || Boolean(options.force)
  });
  return JSON.stringify(result, null, 2);
}

export async function syncLocalSkills(cache: AdapterCache, args: Record<string, unknown>, options: LocalInstallOptions = {}): Promise<string> {
  const root = resolveSkillRoot(stringOrUndefined(args.root) ?? options.root);
  const installMissing = Boolean(args.installMissing);
  const results = [];
  for (const resource of cache.resources) {
    const destination = path.join(root, skillSlug(resource));
    const manifest = await readManifest(destination);
    if (!existsSync(destination)) {
      if (!installMissing) continue;
      results.push(JSON.parse(await installCachedSkill(cache, { uri: resource.uri, root }, { ...options, force: false })));
      continue;
    }
    if (manifest?.uri !== resource.uri) continue;
    results.push(JSON.parse(await installCachedSkill(cache, { uri: resource.uri, root }, { ...options, update: true })));
  }
  return JSON.stringify({ root, updated: results.length, results }, null, 2);
}

export function findResource(cache: AdapterCache, args: Record<string, unknown>): CachedResource | undefined {
  const uri = stringOrUndefined(args.uri);
  const slug = stringOrUndefined(args.slug)?.toLowerCase();
  if (uri) return cache.resources.find((item) => item.uri === uri);
  if (slug) return cache.resources.find((item) => skillSlug(item).toLowerCase() === slug || item.uri.toLowerCase().endsWith(`/${slug}`));
  return undefined;
}

export function parseRenderedBundle(resource: CachedResource): SkillBundle {
  if (!resource.text) throw new Error(`cached skill has no bundle JSON or rendered text: ${resource.uri}`);
  const files: SkillFile[] = [];
  const pattern = /^## ([^\r\n]+)\r?\n\r?\n```text\r?\n([\s\S]*?)\r?\n```\r?$/gm;
  for (const match of resource.text.matchAll(pattern)) {
    const filePath = match[1].trim();
    const content = match[2];
    files.push({
      path: filePath,
      content,
      size: Buffer.byteLength(content, "utf8"),
      sha256: ""
    });
  }
  if (files.length === 0) {
    throw new Error("cached rendered skill could not be parsed; refresh cache with get_skill_bundle support");
  }
  const slug = skillSlug(resource);
  return {
    schemaVersion: 1,
    classifier: decodeURIComponent(resource.uri.split("/")[2] ?? "OTHER") as SkillBundle["classifier"],
    sourceOwner: decodeURIComponent(resource.uri.split("/")[3] ?? "unknown"),
    slug,
    title: resource.title || slug,
    description: resource.description || "",
    tags: [],
    entry: "SKILL.md",
    files,
    source: { type: "local", url: resource.uri, commit: "", root: "" },
    contentHash: "",
    importedAt: "",
    classification: {
      classifier: decodeURIComponent(resource.uri.split("/")[2] ?? "OTHER") as SkillBundle["classifier"],
      confidence: 0,
      evidence: [],
      needsReview: false,
      tags: [],
      scores: {}
    }
  };
}

async function writeBundle(bundle: SkillBundle, uri: string, options: LocalInstallOptions) {
  const root = resolveSkillRoot(options.root);
  const destination = safeJoin(root, bundle.slug);
  const existed = existsSync(destination);
  if (existed && !options.update && !options.force) {
    throw new Error(`local skill already exists: ${destination}`);
  }
  const backupPath = existed ? await backupExisting(destination, options.backupRoot) : null;
  if (existed) await rm(destination, { recursive: true, force: true });
  await mkdir(destination, { recursive: true });

  const written: string[] = [];
  for (const file of bundle.files) {
    const target = safeJoin(destination, file.path);
    await mkdir(path.dirname(target), { recursive: true });
    await writeFile(target, file.content, "utf8");
    written.push(path.relative(destination, target).replace(/\\/g, "/"));
  }

  await writeFile(
    path.join(destination, MCP_MANIFEST),
    JSON.stringify(
      {
        uri,
        slug: bundle.slug,
        sourceOwner: bundle.sourceOwner,
        classifier: bundle.classifier,
        title: bundle.title,
        contentHash: bundle.contentHash,
        installedAt: new Date().toISOString()
      },
      null,
      2
    ),
    "utf8"
  );

  return {
    uri,
    slug: bundle.slug,
    destination,
    action: existed ? "updated" : "installed",
    backupPath,
    filesWritten: written
  };
}

async function backupExisting(destination: string, backupRootInput?: string): Promise<string> {
  const backupRoot = path.resolve(backupRootInput || path.join(os.homedir(), ".skill-registry-mcp", "backups"));
  await mkdir(backupRoot, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const backupPath = path.join(backupRoot, `${path.basename(destination)}-${stamp}`);
  await cp(destination, backupPath, { recursive: true });
  return backupPath;
}

async function readManifest(destination: string): Promise<Record<string, string> | null> {
  try {
    return JSON.parse(await readFile(path.join(destination, MCP_MANIFEST), "utf8")) as Record<string, string>;
  } catch {
    return null;
  }
}

function resolveSkillRoot(rootInput?: string): string {
  return path.resolve(rootInput || process.env.AGENT_SKILLS_DIR || path.join(os.homedir(), ".agents", "skills"));
}

function safeJoin(root: string, relativePath: string): string {
  if (path.isAbsolute(relativePath)) throw new Error(`absolute path is not allowed in skill bundle: ${relativePath}`);
  const normalized = path.normalize(relativePath);
  if (normalized === ".." || normalized.startsWith(`..${path.sep}`)) {
    throw new Error(`path traversal is not allowed in skill bundle: ${relativePath}`);
  }
  const target = path.resolve(root, normalized);
  const resolvedRoot = path.resolve(root);
  if (target !== resolvedRoot && !target.startsWith(`${resolvedRoot}${path.sep}`)) {
    throw new Error(`path escapes skill root: ${relativePath}`);
  }
  return target;
}

function skillSlug(resource: CachedResource): string {
  const uriParts = resource.uri.split("/");
  return decodeURIComponent(uriParts[uriParts.length - 1] || resource.name.split("/").pop() || resource.title);
}

function stringOrUndefined(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() ? value : undefined;
}
