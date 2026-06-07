import type { SkillBundle, SkillSummary } from "./types.js";

export function skillUri(summary: Pick<SkillSummary, "classifier" | "sourceOwner" | "slug">): string {
  return `skills://${encodeURIComponent(summary.classifier)}/${encodeURIComponent(summary.sourceOwner)}/${encodeURIComponent(summary.slug)}`;
}

export function renderSkillBundle(bundle: SkillBundle): string {
  const header = [
    `# ${bundle.classifier} / ${bundle.sourceOwner} / ${bundle.title}`,
    "",
    bundle.description,
    "",
    `Source: ${bundle.source.url || bundle.source.type}`,
    bundle.source.commit ? `Commit: ${bundle.source.commit}` : "",
    bundle.tags.length > 0 ? `Tags: ${bundle.tags.join(", ")}` : "",
    ""
  ].filter(Boolean);

  const files = bundle.files.map((file) => {
    return [`## ${file.path}`, "", "```text", file.content, "```", ""].join("\n");
  });

  return [...header, ...files].join("\n");
}

export function renderSkillList(skills: SkillSummary[]): string {
  if (skills.length === 0) return "No approved skills found.";
  return skills
    .map((skill) => `${skill.classifier} / ${skill.sourceOwner} / ${skill.title} (${skill.slug})`)
    .join("\n");
}
