# Self-Critique Checklist

Use this when bootstrapping or revising `linear-thinking-coders`, and at final completion of any run that produces future skill guidance.

## Pair Enforcement

- Does every implementation ticket require a pair?
- Does every review ticket require a pair?
- Does every corrective ticket require a pair?
- Does the skill explicitly reject solo coding agents?
- Are pair roles clear enough that both members have useful responsibilities?
- Is in-pair review required before cross-review?
- Does the workflow require the coding approval gate before any worker edits?
- Is a consolidated P0-P3 tasklist created before coding dispatch?

## Blue/Logos Learning Loop

- Does Blue/Logos track where each pair/team fails?
- Are failures tied to evidence, not vague impressions?
- Does the skill distinguish code defects from process defects?
- Are repeated failures converted into future skill guidance?
- Is future guidance concrete enough to change the next ticket?
- Does final completion require reviewing the failure notes?
- Does the skill avoid burying pair failures in the final summary without updating guidance?

## Corrective Review Loop

- Are corrective tickets issued to pairs, not solo agents?
- Does each corrective ticket reference the original pair and reviewing pair?
- Does Blue/Logos check whether the correction fixed only the finding or introduced scope creep?
- Are fix pairs scoped to repair only the specific issue assigned by Blue/Logos?

## Skill Functionality

- Are triggers specific enough for future agents to invoke the skill?
- Is the default mode clear?
- Is the auto-code path explicit?
- Are required references listed in the correct order?
- Is MCP wrapper behavior clearly separated from host-agent responsibilities?
- Is OpenCode backend behavior clearly separated from GPT-5.5/Blue/Logos orchestration and GPT-5.3-Codex-Spark (`gpt-5.3-codex-spark`) coding-lane execution?
- Does OpenCode failure fall back to a Codex Spark coding lane first with `high` or `xhigh` reasoning without losing pair roles?
- Does every delegated pair record requested model, actual model when known, fallback reason, and memory destination?
- Does final Blue/Logos produce evidence-based report cards for future zero-shot improvement?
- Does each coding group produce a structured coding report with validation results?
- Is `references/coding-agent-behavior-standard.md` loaded and reflected in the workflow and templates?
- Are validation commands named?
