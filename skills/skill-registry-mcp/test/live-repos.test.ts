import { describe, expect, it } from "vitest";
import { packageSkills } from "../src/importer.js";

const repos = [
  { repo: "addyosmani/agent-skills", minSkills: 20, owner: "addyosmani", sampleSlug: "api-and-interface-design" },
  { repo: "obra/superpowers", minSkills: 8, owner: "obra", sampleSlug: "systematic-debugging" },
  { repo: "getsentry/skills", minSkills: 10, owner: "getsentry", sampleSlug: "code-review" },
  { repo: "mattpocock/skills", minSkills: 10, owner: "mattpocock", sampleSlug: "tdd" }
];

describe.sequential("live GitHub repo imports", () => {
  it.each(repos)("packages $repo", async ({ repo, minSkills, owner, sampleSlug }) => {
    const report = await packageSkills({ source: repo, uploadedBy: "jrice" });
    expect(report.skills.length).toBeGreaterThanOrEqual(minSkills);
    expect(new Set(report.skills.map((skill) => skill.sourceOwner))).toEqual(new Set([owner]));
    expect(report.skills.some((skill) => skill.slug === sampleSlug)).toBe(true);
    expect(report.skills.every((skill) => skill.files.some((file) => file.path === "SKILL.md"))).toBe(true);
    expect(report.skills.every((skill) => skill.files.every((file) => /\.(md|txt|json|ya?ml|toml)$/i.test(file.path)))).toBe(true);
  });
});
