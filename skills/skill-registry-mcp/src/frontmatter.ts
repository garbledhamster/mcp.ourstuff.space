export interface ParsedFrontmatter {
  metadata: Record<string, string>;
  body: string;
}

export function parseFrontmatter(content: string): ParsedFrontmatter {
  const normalized = content.replace(/^\uFEFF/, "");
  if (!normalized.startsWith("---\n") && !normalized.startsWith("---\r\n")) {
    return { metadata: {}, body: content };
  }

  const endMatch = /\r?\n---\r?\n/.exec(normalized.slice(4));
  if (!endMatch) {
    return { metadata: {}, body: content };
  }

  const frontmatterEnd = 4 + endMatch.index;
  const raw = normalized.slice(4, frontmatterEnd);
  const body = normalized.slice(frontmatterEnd + endMatch[0].length);
  const metadata: Record<string, string> = {};

  for (const line of raw.split(/\r?\n/)) {
    const match = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
    if (!match) continue;
    const value = match[2].trim().replace(/^['"]|['"]$/g, "");
    metadata[match[1]] = value;
  }

  return { metadata, body };
}
