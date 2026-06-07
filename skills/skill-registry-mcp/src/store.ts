import { stableId } from "./slug.js";
import type {
  ImportRequestBody,
  RegistryStore,
  SkillBundle,
  SkillSummary,
  SkillVersionDetail,
  SkillVersionSummary
} from "./types.js";

type Row = Record<string, unknown>;

export class D1RegistryStore implements RegistryStore {
  constructor(private readonly db: D1Database) {}

  async importBundles(input: {
    skills: SkillBundle[];
    uploadedBy: string;
    bypassApproval: boolean;
  }): Promise<{ imported: SkillVersionDetail[] }> {
    const imported: SkillVersionDetail[] = [];
    const now = new Date().toISOString();

    for (const bundle of input.skills) {
      const skillId = stableId([bundle.sourceOwner, bundle.slug]);
      const versionId = stableId([skillId, bundle.contentHash.slice(0, 16)]);
      const status = input.bypassApproval ? "approved" : "pending";
      const version = bundle.source.commit || bundle.importedAt;

      await this.db
        .prepare(
          `INSERT INTO skills (
            id, classifier, source_owner, slug, title, description, tags_json, approved_version_id, created_at, updated_at
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          ON CONFLICT(id) DO UPDATE SET
            classifier = excluded.classifier,
            title = excluded.title,
            description = excluded.description,
            tags_json = excluded.tags_json,
            updated_at = excluded.updated_at`
        )
        .bind(
          skillId,
          bundle.classifier,
          bundle.sourceOwner,
          bundle.slug,
          bundle.title,
          bundle.description,
          JSON.stringify(bundle.tags),
          input.bypassApproval ? versionId : null,
          now,
          now
        )
        .run();

      await this.db
        .prepare(
          `INSERT INTO skill_versions (
            id, skill_id, version, source_type, source_url, source_commit, uploaded_by,
            status, content_hash, bundle_json, classification_json, created_at, approved_at, rejected_at
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          ON CONFLICT(id) DO UPDATE SET
            uploaded_by = excluded.uploaded_by,
            status = excluded.status,
            bundle_json = excluded.bundle_json,
            classification_json = excluded.classification_json,
            approved_at = excluded.approved_at,
            rejected_at = excluded.rejected_at`
        )
        .bind(
          versionId,
          skillId,
          version,
          bundle.source.type,
          bundle.source.url,
          bundle.source.commit,
          input.uploadedBy,
          status,
          bundle.contentHash,
          JSON.stringify(bundle),
          JSON.stringify(bundle.classification),
          now,
          input.bypassApproval ? now : null,
          null
        )
        .run();

      if (input.bypassApproval) {
        await this.db.prepare("UPDATE skills SET approved_version_id = ?, updated_at = ? WHERE id = ?").bind(versionId, now, skillId).run();
      }

      const detail = await this.getVersion(versionId);
      if (detail) imported.push(detail);
    }

    return { imported };
  }

  async listSkills(options: {
    approvedOnly?: boolean;
    query?: string;
    classifier?: string;
    sourceOwner?: string;
  } = {}): Promise<SkillSummary[]> {
    const clauses: string[] = [];
    const binds: unknown[] = [];

    if (options.approvedOnly) clauses.push("approved_version_id IS NOT NULL");
    if (options.classifier) {
      clauses.push("classifier = ?");
      binds.push(options.classifier);
    }
    if (options.sourceOwner) {
      clauses.push("source_owner = ?");
      binds.push(options.sourceOwner);
    }
    if (options.query) {
      clauses.push("(lower(title) LIKE ? OR lower(description) LIKE ? OR lower(slug) LIKE ? OR lower(source_owner) LIKE ?)");
      const query = `%${options.query.toLowerCase()}%`;
      binds.push(query, query, query, query);
    }

    const sql = `SELECT * FROM skills ${clauses.length > 0 ? `WHERE ${clauses.join(" AND ")}` : ""} ORDER BY classifier, source_owner, slug`;
    const result = await this.db.prepare(sql).bind(...binds).all<Row>();
    return (result.results ?? []).map(mapSkillRow);
  }

  async getApprovedBundleByUri(uri: string): Promise<SkillVersionDetail | null> {
    const parsed = parseSkillUri(uri);
    if (!parsed) return null;
    return this.getApprovedBundle(parsed.classifier, parsed.sourceOwner, parsed.slug);
  }

  async getApprovedBundle(classifier: string, sourceOwner: string, slug: string): Promise<SkillVersionDetail | null> {
    const row = await this.db
      .prepare(
        `SELECT v.* FROM skills s
         JOIN skill_versions v ON s.approved_version_id = v.id
         WHERE s.classifier = ? AND s.source_owner = ? AND s.slug = ? AND v.status = 'approved'`
      )
      .bind(classifier, sourceOwner, slug)
      .first<Row>();
    return row ? mapVersionRow(row) : null;
  }

  async getSkill(skillId: string): Promise<SkillSummary | null> {
    const row = await this.db.prepare("SELECT * FROM skills WHERE id = ?").bind(skillId).first<Row>();
    return row ? mapSkillRow(row) : null;
  }

  async listVersions(skillId: string): Promise<SkillVersionDetail[]> {
    const result = await this.db
      .prepare("SELECT * FROM skill_versions WHERE skill_id = ? ORDER BY created_at DESC")
      .bind(skillId)
      .all<Row>();
    return (result.results ?? []).map(mapVersionRow);
  }

  async listPending(): Promise<SkillVersionDetail[]> {
    const result = await this.db
      .prepare("SELECT * FROM skill_versions WHERE status = 'pending' ORDER BY created_at DESC")
      .all<Row>();
    return (result.results ?? []).map(mapVersionRow);
  }

  async approveVersion(skillId: string, versionId?: string): Promise<SkillVersionDetail | null> {
    const version = versionId ? await this.getVersion(versionId) : await this.getLatestPending(skillId);
    if (!version || version.skillId !== skillId) return null;
    const now = new Date().toISOString();
    await this.db
      .prepare("UPDATE skill_versions SET status = 'approved', approved_at = ?, rejected_at = NULL WHERE id = ?")
      .bind(now, version.id)
      .run();
    await this.db.prepare("UPDATE skills SET approved_version_id = ?, updated_at = ? WHERE id = ?").bind(version.id, now, skillId).run();
    return this.getVersion(version.id);
  }

  async rejectVersion(skillId: string, versionId?: string): Promise<SkillVersionDetail | null> {
    const version = versionId ? await this.getVersion(versionId) : await this.getLatestPending(skillId);
    if (!version || version.skillId !== skillId) return null;
    const now = new Date().toISOString();
    await this.db
      .prepare("UPDATE skill_versions SET status = 'rejected', rejected_at = ? WHERE id = ?")
      .bind(now, version.id)
      .run();
    return this.getVersion(version.id);
  }

  async deleteSkill(skillId: string): Promise<boolean> {
    await this.db.prepare("DELETE FROM skill_versions WHERE skill_id = ?").bind(skillId).run();
    const result = await this.db.prepare("DELETE FROM skills WHERE id = ?").bind(skillId).run();
    return (result.meta?.changes ?? 0) > 0;
  }

  private async getVersion(versionId: string): Promise<SkillVersionDetail | null> {
    const row = await this.db.prepare("SELECT * FROM skill_versions WHERE id = ?").bind(versionId).first<Row>();
    return row ? mapVersionRow(row) : null;
  }

  private async getLatestPending(skillId: string): Promise<SkillVersionDetail | null> {
    const row = await this.db
      .prepare("SELECT * FROM skill_versions WHERE skill_id = ? AND status = 'pending' ORDER BY created_at DESC LIMIT 1")
      .bind(skillId)
      .first<Row>();
    return row ? mapVersionRow(row) : null;
  }
}

export function validateImportBody(value: unknown): ImportRequestBody {
  if (!value || typeof value !== "object") {
    throw new Error("expected JSON object body");
  }
  const body = value as ImportRequestBody;
  if (!Array.isArray(body.skills)) {
    throw new Error("body.skills must be an array");
  }
  for (const skill of body.skills) {
    if (!skill || skill.schemaVersion !== 1 || !skill.slug || !skill.classifier || !Array.isArray(skill.files)) {
      throw new Error("invalid skill bundle shape");
    }
  }
  return body;
}

function mapSkillRow(row: Row): SkillSummary {
  return {
    id: String(row.id),
    classifier: row.classifier as SkillSummary["classifier"],
    sourceOwner: String(row.source_owner),
    slug: String(row.slug),
    title: String(row.title),
    description: String(row.description ?? ""),
    tags: parseJsonArray(row.tags_json),
    approvedVersionId: row.approved_version_id ? String(row.approved_version_id) : null,
    createdAt: String(row.created_at),
    updatedAt: String(row.updated_at)
  };
}

function mapVersionRow(row: Row): SkillVersionDetail {
  const summary: SkillVersionSummary = {
    id: String(row.id),
    skillId: String(row.skill_id),
    version: String(row.version),
    sourceType: String(row.source_type),
    sourceUrl: String(row.source_url ?? ""),
    sourceCommit: String(row.source_commit ?? ""),
    uploadedBy: String(row.uploaded_by),
    status: row.status as SkillVersionSummary["status"],
    contentHash: String(row.content_hash),
    createdAt: String(row.created_at),
    approvedAt: row.approved_at ? String(row.approved_at) : null,
    rejectedAt: row.rejected_at ? String(row.rejected_at) : null
  };

  return {
    ...summary,
    bundle: JSON.parse(String(row.bundle_json)) as SkillBundle,
    classification: JSON.parse(String(row.classification_json || "{}"))
  };
}

function parseJsonArray(value: unknown): string[] {
  try {
    const parsed = JSON.parse(String(value ?? "[]"));
    return Array.isArray(parsed) ? parsed.map(String) : [];
  } catch {
    return [];
  }
}

function parseSkillUri(uri: string): { classifier: string; sourceOwner: string; slug: string } | null {
  const match = /^skills:\/\/([^/]+)\/([^/]+)\/([^/]+)$/.exec(uri);
  if (!match) return null;
  return {
    classifier: decodeURIComponent(match[1]),
    sourceOwner: decodeURIComponent(match[2]),
    slug: decodeURIComponent(match[3])
  };
}
