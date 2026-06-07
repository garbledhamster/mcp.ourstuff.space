import type { SkillBundle } from "./types.js";

export function diffBundles(current: SkillBundle | null, pending: SkillBundle): string {
  const currentFiles = new Map((current?.files ?? []).map((file) => [file.path, file.content]));
  const pendingFiles = new Map(pending.files.map((file) => [file.path, file.content]));
  const paths = Array.from(new Set([...currentFiles.keys(), ...pendingFiles.keys()])).sort();
  const chunks: string[] = [];

  for (const filePath of paths) {
    const before = currentFiles.get(filePath);
    const after = pendingFiles.get(filePath);
    if (before === after) continue;
    chunks.push(diffText(filePath, before ?? "", after ?? "", before === undefined, after === undefined));
  }

  return chunks.length > 0 ? chunks.join("\n") : "No text changes.";
}

function diffText(filePath: string, before: string, after: string, added: boolean, deleted: boolean): string {
  const beforeLines = before.split(/\r?\n/);
  const afterLines = after.split(/\r?\n/);
  const output = [
    `diff -- ${filePath}`,
    `--- ${deleted ? "/dev/null" : `a/${filePath}`}`,
    `+++ ${added ? "/dev/null" : `b/${filePath}`}`
  ];

  const max = Math.max(beforeLines.length, afterLines.length);
  for (let index = 0; index < max; index += 1) {
    const oldLine = beforeLines[index];
    const newLine = afterLines[index];
    if (oldLine === newLine) {
      if (oldLine !== undefined) output.push(` ${oldLine}`);
      continue;
    }
    if (oldLine !== undefined) output.push(`-${oldLine}`);
    if (newLine !== undefined) output.push(`+${newLine}`);
  }

  return output.join("\n");
}
