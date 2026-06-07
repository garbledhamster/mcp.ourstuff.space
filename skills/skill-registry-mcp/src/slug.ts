export function slugify(input: string): string {
  const slug = input
    .toLowerCase()
    .replace(/['"]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .replace(/-{2,}/g, "-");

  return slug || "skill";
}

export function stableId(parts: string[]): string {
  return parts.map(slugify).join("__");
}
