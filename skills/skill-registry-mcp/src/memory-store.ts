import { stableId } from "./slug.js";
import type {
  RegistryStore,
  SkillBundle,
  SkillSummary,
  SkillVersionDetail,
  SkillVersionSummary
} from "./types.js";

export class MemoryRegistryStore implements RegistryStore {
  private readonly skills = new Map<string, SkillSummary>();
  private readonly versions = new Map<string, SkillVersionDetail>();

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
      const previous = this.skills.get(skillId);
      const skill: SkillSummary = {
        id: skillId,
        classifier: bundle.classifier,
        sourceOwner: bundle.sourceOwner,
        slug: bundle.slug,
        title: bundle.title,
        description: bundle.description,
        tags: bundle.tags,
        approvedVersionId: input.bypassApproval ? versionId : previous?.approvedVersionId ?? null,
        createdAt: previous?.createdAt ?? now,
        updatedAt: now
      };
      this.skills.set(skillId, skill);

      const summary: SkillVersionSummary = {
        id: versionId,
        skillId,
        version: bundle.source.commit || bundle.importedAt,
        sourceType: bundle.source.type,
        sourceUrl: bundle.source.url,
        sourceCommit: bundle.source.commit,
        uploadedBy: input.uploadedBy,
        status,
        contentHash: bundle.contentHash,
        createdAt: now,
        approvedAt: input.bypassApproval ? now : null,
        rejectedAt: null
      };
      const detail: SkillVersionDetail = { ...summary, bundle, classification: bundle.classification };
      this.versions.set(versionId, detail);
      imported.push(detail);
    }
    return { imported };
  }

  async listSkills(options: {
    approvedOnly?: boolean;
    query?: string;
    classifier?: string;
    sourceOwner?: string;
  } = {}): Promise<SkillSummary[]> {
    const query = options.query?.toLowerCase();
    return Array.from(this.skills.values())
      .filter((skill) => !options.approvedOnly || Boolean(skill.approvedVersionId))
      .filter((skill) => !options.classifier || skill.classifier === options.classifier)
      .filter((skill) => !options.sourceOwner || skill.sourceOwner === options.sourceOwner)
      .filter((skill) => {
        if (!query) return true;
        return [skill.title, skill.description, skill.slug, skill.sourceOwner, skill.classifier].some((value) =>
          value.toLowerCase().includes(query)
        );
      })
      .sort((a, b) => `${a.classifier}/${a.sourceOwner}/${a.slug}`.localeCompare(`${b.classifier}/${b.sourceOwner}/${b.slug}`));
  }

  async getApprovedBundleByUri(uri: string): Promise<SkillVersionDetail | null> {
    const parsed = /^skills:\/\/([^/]+)\/([^/]+)\/([^/]+)$/.exec(uri);
    if (!parsed) return null;
    return this.getApprovedBundle(decodeURIComponent(parsed[1]), decodeURIComponent(parsed[2]), decodeURIComponent(parsed[3]));
  }

  async getApprovedBundle(classifier: string, sourceOwner: string, slug: string): Promise<SkillVersionDetail | null> {
    const skill = Array.from(this.skills.values()).find(
      (item) => item.classifier === classifier && item.sourceOwner === sourceOwner && item.slug === slug
    );
    if (!skill?.approvedVersionId) return null;
    return this.versions.get(skill.approvedVersionId) ?? null;
  }

  async getSkill(skillId: string): Promise<SkillSummary | null> {
    return this.skills.get(skillId) ?? null;
  }

  async listVersions(skillId: string): Promise<SkillVersionDetail[]> {
    return Array.from(this.versions.values())
      .filter((version) => version.skillId === skillId)
      .sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  }

  async listPending(): Promise<SkillVersionDetail[]> {
    return Array.from(this.versions.values())
      .filter((version) => version.status === "pending")
      .sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  }

  async approveVersion(skillId: string, versionId?: string): Promise<SkillVersionDetail | null> {
    const version = versionId ? this.versions.get(versionId) : (await this.listVersions(skillId)).find((item) => item.status === "pending");
    if (!version || version.skillId !== skillId) return null;
    const updated: SkillVersionDetail = {
      ...version,
      status: "approved",
      approvedAt: new Date().toISOString(),
      rejectedAt: null
    };
    this.versions.set(updated.id, updated);
    const skill = this.skills.get(skillId);
    if (skill) this.skills.set(skillId, { ...skill, approvedVersionId: updated.id, updatedAt: updated.approvedAt ?? skill.updatedAt });
    return updated;
  }

  async rejectVersion(skillId: string, versionId?: string): Promise<SkillVersionDetail | null> {
    const version = versionId ? this.versions.get(versionId) : (await this.listVersions(skillId)).find((item) => item.status === "pending");
    if (!version || version.skillId !== skillId) return null;
    const updated: SkillVersionDetail = {
      ...version,
      status: "rejected",
      rejectedAt: new Date().toISOString()
    };
    this.versions.set(updated.id, updated);
    return updated;
  }

  async deleteSkill(skillId: string): Promise<boolean> {
    const existed = this.skills.delete(skillId);
    for (const version of this.versions.values()) {
      if (version.skillId === skillId) this.versions.delete(version.id);
    }
    return existed;
  }
}
