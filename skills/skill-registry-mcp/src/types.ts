export const CLASSIFIERS = [
  "API_DESIGN",
  "FRONTEND",
  "BACKEND",
  "SECURITY",
  "SCRUBBERS",
  "TESTING",
  "DEBUGGING",
  "CODE_REVIEW",
  "REFACTORING",
  "PERFORMANCE",
  "CI_CD",
  "GIT",
  "DOCS_ADRS",
  "PLANNING",
  "SPEC_DRIVEN",
  "TDD",
  "CONTEXT_ENGINEERING",
  "MCP",
  "DATA",
  "WRITING",
  "LEARNING",
  "SHIPPING",
  "OTHER"
] as const;

export type Classifier = (typeof CLASSIFIERS)[number];
export type SkillStatus = "pending" | "approved" | "rejected";

export interface ClassificationResult {
  classifier: Classifier;
  confidence: number;
  evidence: string[];
  needsReview: boolean;
  tags: string[];
  scores: Partial<Record<Classifier, number>>;
}

export interface SkillFile {
  path: string;
  content: string;
  size: number;
  sha256: string;
}

export interface SkillSource {
  type: "git" | "local" | "file";
  url: string;
  commit: string;
  root: string;
}

export interface SkillBundle {
  schemaVersion: 1;
  classifier: Classifier;
  sourceOwner: string;
  slug: string;
  title: string;
  description: string;
  tags: string[];
  entry: "SKILL.md";
  files: SkillFile[];
  source: SkillSource;
  contentHash: string;
  importedAt: string;
  classification: ClassificationResult;
}

export interface ImportReport {
  source: SkillSource;
  uploadedBy: string;
  skills: SkillBundle[];
  warnings: string[];
  rejected: Array<{ path: string; reason: string }>;
}

export interface SkillSummary {
  id: string;
  classifier: Classifier;
  sourceOwner: string;
  slug: string;
  title: string;
  description: string;
  tags: string[];
  approvedVersionId: string | null;
  createdAt: string;
  updatedAt: string;
  version?: SkillVersionSummary;
}

export interface SkillVersionSummary {
  id: string;
  skillId: string;
  version: string;
  sourceType: string;
  sourceUrl: string;
  sourceCommit: string;
  uploadedBy: string;
  status: SkillStatus;
  contentHash: string;
  createdAt: string;
  approvedAt: string | null;
  rejectedAt: string | null;
}

export interface SkillVersionDetail extends SkillVersionSummary {
  bundle: SkillBundle;
  classification: ClassificationResult;
}

export interface ImportRequestBody {
  skills: SkillBundle[];
  uploadedBy?: string;
  bypassApproval?: boolean;
}

export interface RegistryStore {
  importBundles(input: {
    skills: SkillBundle[];
    uploadedBy: string;
    bypassApproval: boolean;
  }): Promise<{ imported: SkillVersionDetail[] }>;
  listSkills(options?: {
    approvedOnly?: boolean;
    query?: string;
    classifier?: string;
    sourceOwner?: string;
  }): Promise<SkillSummary[]>;
  getApprovedBundleByUri(uri: string): Promise<SkillVersionDetail | null>;
  getApprovedBundle(classifier: string, sourceOwner: string, slug: string): Promise<SkillVersionDetail | null>;
  getSkill(skillId: string): Promise<SkillSummary | null>;
  listVersions(skillId: string): Promise<SkillVersionDetail[]>;
  listPending(): Promise<SkillVersionDetail[]>;
  approveVersion(skillId: string, versionId?: string): Promise<SkillVersionDetail | null>;
  rejectVersion(skillId: string, versionId?: string): Promise<SkillVersionDetail | null>;
  deleteSkill(skillId: string): Promise<boolean>;
}
