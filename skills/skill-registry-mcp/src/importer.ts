import { execFile as execFileCallback } from "node:child_process";
import { mkdtemp, readFile, readdir, rm, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import { classifySkill } from "./classifier.js";
import { parseFrontmatter } from "./frontmatter.js";
import { sha256 } from "./hash.js";
import { slugify } from "./slug.js";
import type { Classifier, ImportReport, SkillBundle, SkillFile, SkillSource } from "./types.js";

const execFile = promisify(execFileCallback);

export const ALLOWED_EXTENSIONS = new Set([".md", ".txt", ".json", ".yaml", ".yml", ".toml"]);
export const BLOCKED_DIRS = new Set([
  ".git",
  "node_modules",
  "dist",
  "build",
  ".next",
  ".wrangler",
  "coverage",
  "__pycache__"
]);

export const MAX_FILE_BYTES = 128 * 1024;
export const MAX_BUNDLE_BYTES = 512 * 1024;
export const MAX_IMPORT_BYTES = 10 * 1024 * 1024;
export const MAX_LOCAL_SCAN_BYTES = 25 * 1024 * 1024;

export interface PackageOptions {
  source: string;
  uploadedBy: string;
  sourceOwner?: string;
  keepTemp?: boolean;
}

interface PreparedSource {
  cleanup?: () => Promise<void>;
  rootDir: string;
  source: SkillSource;
}

export async function packageSkills(options: PackageOptions): Promise<ImportReport> {
  const prepared = await prepareSource(options);
  try {
    const rejected: Array<{ path: string; reason: string }> = [];
    const warnings: string[] = [];
    const scanBytes = await scanSize(prepared.rootDir, rejected);
    if (scanBytes > MAX_LOCAL_SCAN_BYTES) {
      warnings.push(`local scan size ${scanBytes} exceeds ${MAX_LOCAL_SCAN_BYTES}; importer will still only package allowed files`);
    }

    const skillFiles = await findSkillFiles(prepared.rootDir);
    if (skillFiles.length === 0) {
      warnings.push("no SKILL.md files found; no skills packaged");
    }

    const skills: SkillBundle[] = [];
    let importBytes = 0;
    const visibleSourceOwner = getVisibleSourceOwner(prepared.source, options.sourceOwner || options.uploadedBy);
    for (const skillFilePath of skillFiles) {
      const bundle = await packageSingleSkill(prepared.rootDir, skillFilePath, prepared.source, visibleSourceOwner, rejected);
      if (!bundle) continue;
      importBytes += bundle.files.reduce((sum, file) => sum + file.size, 0);
      if (importBytes > MAX_IMPORT_BYTES) {
        rejected.push({ path: path.relative(prepared.rootDir, skillFilePath), reason: "import batch upload limit exceeded" });
        continue;
      }
      skills.push(bundle);
    }

    return {
      source: prepared.source,
      uploadedBy: options.uploadedBy,
      skills,
      warnings,
      rejected
    };
  } finally {
    if (!options.keepTemp && prepared.cleanup) {
      await prepared.cleanup();
    }
  }
}

async function prepareSource(options: PackageOptions): Promise<PreparedSource> {
  const sourceInput = options.source.trim();
  const github = parseGitHubSource(sourceInput);
  if (github) {
    const tmpRoot = await mkdtemp(path.join(os.tmpdir(), "skill-registry-"));
    const checkout = path.join(tmpRoot, `${github.owner}-${github.repo}`);
    await execFile("git", ["clone", "--depth", "1", github.cloneUrl, checkout], { maxBuffer: 1024 * 1024 * 10 });
    const { stdout } = await execFile("git", ["-C", checkout, "rev-parse", "HEAD"]);
    return {
      rootDir: checkout,
      cleanup: async () => {
        await rm(tmpRoot, { recursive: true, force: true });
      },
      source: {
        type: "git",
        url: github.webUrl,
        commit: stdout.trim(),
        root: ""
      }
    };
  }

  const resolved = path.resolve(sourceInput);
  if (!existsSync(resolved)) {
    throw new Error(`source not found: ${sourceInput}`);
  }
  const sourceOwner = options.sourceOwner || options.uploadedBy || "local";
  const sourceStat = await stat(resolved);
  return {
    rootDir: sourceStat.isDirectory() ? resolved : path.dirname(resolved),
    source: {
      type: sourceStat.isDirectory() ? "local" : "file",
      url: resolved,
      commit: "",
      root: sourceStat.isDirectory() ? "" : path.basename(resolved)
    },
    cleanup: undefined
  };
}

function parseGitHubSource(input: string): { owner: string; repo: string; cloneUrl: string; webUrl: string } | null {
  const shorthand = /^([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)$/.exec(input);
  if (shorthand) {
    const owner = shorthand[1];
    const repo = shorthand[2].replace(/\.git$/, "");
    return {
      owner,
      repo,
      cloneUrl: `https://github.com/${owner}/${repo}.git`,
      webUrl: `https://github.com/${owner}/${repo}`
    };
  }

  let parsed: URL;
  try {
    parsed = new URL(input);
  } catch {
    return null;
  }

  if (!/github\.com$/i.test(parsed.hostname)) {
    return null;
  }

  const [owner, repoRaw] = parsed.pathname.replace(/^\/+/, "").split("/");
  if (!owner || !repoRaw) {
    return null;
  }

  const repo = repoRaw.replace(/\.git$/, "");
  return {
    owner,
    repo,
    cloneUrl: `https://github.com/${owner}/${repo}.git`,
    webUrl: `https://github.com/${owner}/${repo}`
  };
}

async function scanSize(rootDir: string, rejected: Array<{ path: string; reason: string }>): Promise<number> {
  let total = 0;
  await walk(rootDir, async (filePath) => {
    const info = await stat(filePath);
    total += info.size;
    if (info.size > MAX_FILE_BYTES && ALLOWED_EXTENSIONS.has(path.extname(filePath).toLowerCase())) {
      rejected.push({ path: path.relative(rootDir, filePath), reason: "allowed text file exceeds max file size" });
    }
  });
  return total;
}

async function findSkillFiles(rootDir: string): Promise<string[]> {
  const matches: string[] = [];
  await walk(rootDir, async (filePath) => {
    if (path.basename(filePath).toLowerCase() === "skill.md") {
      matches.push(filePath);
    }
  });
  return matches.sort((a, b) => normalizePath(path.relative(rootDir, a)).localeCompare(normalizePath(path.relative(rootDir, b))));
}

async function walk(dir: string, onFile: (filePath: string) => Promise<void>): Promise<void> {
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name.startsWith(".") && entry.name !== ".claude" && entry.name !== ".opencode") {
      if (entry.name !== ".github") continue;
    }
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (BLOCKED_DIRS.has(entry.name)) continue;
      await walk(fullPath, onFile);
      continue;
    }
    if (entry.isFile()) {
      await onFile(fullPath);
    }
  }
}

async function packageSingleSkill(
  rootDir: string,
  skillFilePath: string,
  source: SkillSource,
  visibleSourceOwner: string,
  rejected: Array<{ path: string; reason: string }>
): Promise<SkillBundle | null> {
  const skillDir = path.dirname(skillFilePath);
  const relativeSkillDir = normalizePath(path.relative(rootDir, skillDir));
  const skillContent = await readFile(skillFilePath, "utf8");
  const parsed = parseFrontmatter(skillContent);
  const folderSlug = slugify(path.basename(skillDir));
  const title = parsed.metadata.name || path.basename(skillDir);
  const slug = slugify(title || folderSlug);
  const description = parsed.metadata.description || firstNonEmptyLine(parsed.body) || "";
  const sourceOwner = slugify(visibleSourceOwner);
  const classification = classifySkill({
    slug,
    title,
    description,
    relativePath: relativeSkillDir,
    content: skillContent
  });

  const files: SkillFile[] = [];
  let bundleBytes = 0;
  await walk(skillDir, async (filePath) => {
    const relativePath = normalizePath(path.relative(skillDir, filePath));
    const extension = path.extname(filePath).toLowerCase();
    if (!ALLOWED_EXTENSIONS.has(extension)) {
      rejected.push({ path: normalizePath(path.relative(rootDir, filePath)), reason: "file extension is not allowed" });
      return;
    }

    const info = await stat(filePath);
    if (info.size > MAX_FILE_BYTES) {
      rejected.push({ path: normalizePath(path.relative(rootDir, filePath)), reason: "file exceeds max file size" });
      return;
    }

    const content = await readFile(filePath, "utf8");
    if (content.includes("\u0000")) {
      rejected.push({ path: normalizePath(path.relative(rootDir, filePath)), reason: "binary-looking text file blocked" });
      return;
    }

    bundleBytes += Buffer.byteLength(content, "utf8");
    if (bundleBytes > MAX_BUNDLE_BYTES) {
      rejected.push({ path: normalizePath(path.relative(rootDir, filePath)), reason: "skill bundle exceeds max bundle size" });
      return;
    }

    files.push({
      path: relativePath,
      content,
      size: Buffer.byteLength(content, "utf8"),
      sha256: sha256(content)
    });
  });

  if (!files.some((file) => file.path === "SKILL.md")) {
    return null;
  }

  files.sort((a, b) => a.path.localeCompare(b.path));
  const hashInput = files.map((file) => `${file.path}\n${file.sha256}`).join("\n");
  const importedAt = new Date().toISOString();
  const sourceWithRoot: SkillSource = { ...source, root: relativeSkillDir };
  const bundle: SkillBundle = {
    schemaVersion: 1,
    classifier: classification.classifier,
    sourceOwner,
    slug,
    title,
    description,
    tags: classification.tags,
    entry: "SKILL.md",
    files,
    source: sourceWithRoot,
    contentHash: sha256(hashInput),
    importedAt,
    classification
  };

  return bundle;
}

function firstNonEmptyLine(content: string): string {
  return (
    content
      .split(/\r?\n/)
      .map((line) => line.replace(/^#+\s*/, "").trim())
      .find((line) => line.length > 0 && !line.startsWith("---")) ?? ""
  ).slice(0, 300);
}

function getVisibleSourceOwner(source: SkillSource, fallback: string): string {
  if (source.type !== "git") return fallback;
  try {
    const url = new URL(source.url);
    if (/github\.com$/i.test(url.hostname)) {
      return slugify(url.pathname.replace(/^\/+/, "").split("/")[0] ?? "local");
    }
  } catch {
    // Local paths are handled below.
  }
  return fallback;
}

function normalizePath(input: string): string {
  return input.split(path.sep).join("/");
}

export function applyClassifierOverride(bundle: SkillBundle, classifier: Classifier): SkillBundle {
  return {
    ...bundle,
    classifier,
    classification: {
      ...bundle.classification,
      classifier,
      confidence: 1,
      needsReview: false,
      evidence: ["manual override"]
    }
  };
}
