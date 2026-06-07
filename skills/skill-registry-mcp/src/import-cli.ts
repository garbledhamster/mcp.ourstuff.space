#!/usr/bin/env node
import { readFile, writeFile } from "node:fs/promises";
import { applyClassifierOverride, packageSkills } from "./importer.js";
import { CLASSIFIERS, type Classifier, type ImportReport } from "./types.js";

interface ParsedArgs {
  _: string[];
  [key: string]: string | string[];
}

async function main() {
  const [command, ...args] = process.argv.slice(2);
  if (!command || command === "help" || command === "--help") {
    printHelp();
    return;
  }

  if (command === "classifiers") {
    console.log(CLASSIFIERS.join("\n"));
    return;
  }

  if (command === "package") {
    const parsed = parseArgs(args);
    const source = parsed._[0] ?? stringValue(parsed.source);
    if (!source) {
      throw new Error("package requires a source path, GitHub URL, or owner/repo");
    }

    const report = await packageSkills({
      source,
      uploadedBy: stringValue(parsed["uploaded-by"]) ?? process.env.SKILL_REGISTRY_UPLOADER ?? "jrice",
      sourceOwner: stringValue(parsed["source-owner"]),
      keepTemp: parsed["keep-temp"] === "true"
    });

    const finalReport = await applyOverrideFile(report, stringValue(parsed["override-file"]));
    const json = JSON.stringify(finalReport, null, 2);
    const out = stringValue(parsed.out);
    if (out) {
      await writeFile(out, json, "utf8");
      console.log(`wrote ${out}`);
    } else {
      console.log(json);
    }
    return;
  }

  throw new Error(`unknown command: ${command}`);
}

async function applyOverrideFile(report: ImportReport, overrideFile?: string): Promise<ImportReport> {
  if (!overrideFile) return report;
  const raw = await readFile(overrideFile, "utf8");
  const overrides = JSON.parse(raw) as Record<string, Classifier>;
  return {
    ...report,
    skills: report.skills.map((skill) => {
      const override = overrides[skill.slug];
      if (!override) return skill;
      if (!CLASSIFIERS.includes(override)) {
        throw new Error(`invalid classifier override for ${skill.slug}: ${override}`);
      }
      return applyClassifierOverride(skill, override);
    })
  };
}

function parseArgs(args: string[]): ParsedArgs {
  const parsed: ParsedArgs = { _: [] };
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (!arg.startsWith("--")) {
      parsed._.push(arg);
      continue;
    }
    const key = arg.slice(2);
    const next = args[index + 1];
    if (!next || next.startsWith("--")) {
      parsed[key] = "true";
      continue;
    }
    parsed[key] = next;
    index += 1;
  }
  return parsed;
}

function stringValue(value: string | string[] | undefined): string | undefined {
  return typeof value === "string" ? value : undefined;
}

function printHelp() {
  console.log(`Skill Registry import CLI

Usage:
  node dist/src/import-cli.js package <path|github-url|owner/repo> --out import.json
  node dist/src/import-cli.js classifiers

Options:
  --uploaded-by <name>       Audit uploader name. Default: SKILL_REGISTRY_UPLOADER or jrice
  --source-owner <name>      Owner override for local sources
  --override-file <json>     Map skill slug to fixed classifier
  --keep-temp                Keep cloned GitHub checkout for debugging
`);
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
