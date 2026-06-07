import { CLASSIFIERS, type ClassificationResult, type Classifier } from "./types.js";

const TOKEN_WEIGHTS = [1.8, 1.25, 0.85, 0.5];

const CATEGORY_TERMS: Record<Classifier, string[]> = {
  API_DESIGN: ["api", "interface", "interfaces", "contract", "contracts", "schema", "endpoint", "endpoints"],
  FRONTEND: ["frontend", "front-end", "ui", "ux", "browser", "accessibility", "component", "components", "react", "css", "html"],
  BACKEND: ["backend", "server", "database", "db", "worker", "workers", "service", "services", "queue", "queues"],
  SECURITY: ["security", "secure", "hardening", "audit", "threat", "permission", "permissions", "auth", "credential", "credentials", "access"],
  SCRUBBERS: ["scrub", "scrubber", "scrubbers", "redact", "redaction", "pii", "secret", "secrets", "sanitize"],
  TESTING: ["test", "testing", "tests", "qa", "browser-testing", "devtools", "playwright", "vitest", "unit", "integration"],
  DEBUGGING: ["debug", "debugging", "diagnose", "diagnosis", "error", "recovery", "root", "cause", "trace", "tracing"],
  CODE_REVIEW: ["review", "reviewing", "code-review", "quality", "bugs", "bug", "find-bugs", "reviewer"],
  REFACTORING: ["refactor", "refactoring", "simplification", "simplify", "migration", "migrate", "deprecation", "legacy"],
  PERFORMANCE: ["performance", "perf", "optimization", "latency", "speed", "ttfb", "cache", "caching"],
  CI_CD: ["ci", "cd", "ci-cd", "gha", "github-actions", "workflow", "automation", "pipeline", "deploy"],
  GIT: ["git", "branch", "commit", "versioning", "pr", "pull-request", "release", "merge"],
  DOCS_ADRS: ["docs", "documentation", "adr", "adrs", "readme", "spec", "sources"],
  PLANNING: ["plan", "planning", "task", "breakdown", "roadmap", "triage", "issue", "issues", "idea", "refine"],
  SPEC_DRIVEN: ["spec", "specs", "spec-driven", "sdd", "requirements", "prd"],
  TDD: ["tdd", "test-driven", "red", "green", "refactor"],
  CONTEXT_ENGINEERING: ["context", "memory", "agent", "agents", "subagent", "subagents", "prompt", "prompts"],
  MCP: ["mcp", "model-context-protocol", "tool", "tools", "server", "servers", "resources"],
  DATA: ["data", "dataset", "spreadsheet", "csv", "json", "analytics", "query", "sql"],
  WRITING: ["writing", "blog", "copy", "article", "content", "doc-coauthoring", "coauthoring"],
  LEARNING: ["learn", "learning", "teach", "education", "educating", "tutorial", "guide", "training", "interview"],
  SHIPPING: ["ship", "shipping", "launch", "release", "deploy", "prelaunch", "handoff"],
  OTHER: []
};

const TAG_TERMS = [
  "api",
  "ui",
  "ux",
  "react",
  "css",
  "security",
  "testing",
  "debugging",
  "git",
  "ci",
  "docs",
  "adr",
  "performance",
  "mcp",
  "planning",
  "learning",
  "python",
  "typescript",
  "cloudflare",
  "d1"
];

export function tokenize(input: string): string[] {
  return input
    .toLowerCase()
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .split(/[^a-z0-9]+/g)
    .map((token) => token.trim())
    .filter(Boolean);
}

export function classifySkill(input: {
  slug: string;
  title: string;
  description: string;
  relativePath: string;
  content: string;
}): ClassificationResult {
  const slugTokens = tokenize(input.slug);
  const titleTokens = tokenize(input.title);
  const pathTokens = tokenize(input.relativePath);
  const descriptionTokens = tokenize(input.description).slice(0, 80);
  const headingTokens = tokenize(input.content.match(/^#\s+(.+)$/m)?.[1] ?? "").slice(0, 20);

  const scores: Partial<Record<Classifier, number>> = {};
  const evidence: string[] = [];

  const addEvidenceScore = (classifier: Classifier, amount: number, why: string) => {
    scores[classifier] = (scores[classifier] ?? 0) + amount;
    if (amount >= 1 && evidence.length < 8) {
      evidence.push(why);
    }
  };

  const scoreTokens = (tokens: string[], base: number, label: string) => {
    tokens.forEach((token, index) => {
      const positionWeight = TOKEN_WEIGHTS[index] ?? 0.25;
      for (const classifier of CLASSIFIERS) {
        if (classifier === "OTHER") continue;
        const terms = CATEGORY_TERMS[classifier];
        if (terms.includes(token)) {
          addEvidenceScore(classifier, base * positionWeight, `${label} token "${token}"`);
        }
      }
    });
  };

  scoreTokens(slugTokens, 1.2, "slug");
  scoreTokens(titleTokens, 1.0, "title");
  scoreTokens(pathTokens, 0.45, "path");
  scoreTokens(headingTokens, 0.55, "heading");
  scoreTokens(descriptionTokens, 0.22, "description");

  const allTextTokens = new Set([...slugTokens, ...titleTokens, ...pathTokens, ...headingTokens, ...descriptionTokens]);
  if (allTextTokens.has("frontend") && (allTextTokens.has("ui") || allTextTokens.has("design") || allTextTokens.has("redesign"))) {
    addEvidenceScore("FRONTEND", 2.5, "frontend UI/design phrase");
  }

  const ranked = CLASSIFIERS
    .filter((classifier) => classifier !== "OTHER")
    .map((classifier) => [classifier, scores[classifier] ?? 0] as const)
    .sort((a, b) => b[1] - a[1]);

  const [bestClassifier, bestScore] = ranked[0] ?? ["OTHER", 0];
  const secondScore = ranked[1]?.[1] ?? 0;
  const confidence = bestScore <= 0 ? 0 : Math.min(0.99, bestScore / (bestScore + secondScore + 2));
  const classifier = bestScore >= 1 ? bestClassifier : "OTHER";
  const tags = Array.from(
    new Set(
      [...slugTokens, ...titleTokens, ...descriptionTokens].filter((token) => TAG_TERMS.includes(token))
    )
  ).slice(0, 8);

  return {
    classifier,
    confidence: Number(confidence.toFixed(2)),
    evidence: evidence.length > 0 ? evidence : ["no deterministic classifier evidence"],
    needsReview: classifier === "OTHER" || confidence < 0.55,
    tags,
    scores
  };
}

export function isClassifier(value: string): value is Classifier {
  return (CLASSIFIERS as readonly string[]).includes(value);
}
