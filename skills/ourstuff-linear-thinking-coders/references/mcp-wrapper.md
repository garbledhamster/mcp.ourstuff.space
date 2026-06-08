# Garbledhamster MCP Wrapper Plan

Do not modify `skill-registry-mcp` for v0. It is currently an approved-skill registry and read-only MCP surface.

Non-negotiable rule: there are always pairs. No solo implementation agents, no solo review agents, and no solo corrective agents. Blue/Logos owns coordination, failure-note capture, and conversion of recurring mistakes into future skill guidance.

Design principle: the wrapper packages paired judgment. The host performs work. Blue/Logos observes pair failures and turns repeated mistakes into future guidance.

## Recommended Wrapper

Define a future garbledhamster prompt-style orchestration function named `frontend_design_council`.

This wrapper should return an orchestration packet, not directly edit files.

## Inputs

- `repoPath`: required absolute path.
- `targetSurface`: required route, page, component, or UI area.
- `mode`: optional, default `auto-code`.
- `frontendStack`: optional discovered or user-provided stack.
- `constraints`: optional user constraints.
- `verificationCommands`: optional command list.

## Output

Return a packet containing:

- discovery checklist
- paired-agent prompts
- final design-doc template
- paired coder-ticket templates
- pair failure note template
- final verification checklist
- pair requirement metadata
- Blue/Logos failure-note metadata

## Limits

- The host agent remains responsible for repo reads, subagent spawning, edits, screenshots, browser checks, and final verification.
- The wrapper must not claim to run `multi_agent_v1` itself unless the MCP server actually has that capability.
- The wrapper must preserve the pair-only rule.
- The wrapper must require Blue/Logos failure notes and future skill guidance synthesis.
- The wrapper must not generate solo coding-agent tickets.
- The wrapper must not generate solo review tickets.
- The wrapper must not treat pair review as optional.
- The wrapper must not omit Blue/Logos failure-note capture.
- The wrapper must not omit a path for converting observed pair failures into future skill guidance.

## Host Responsibilities

The host agent must:

- Enforce pair assignment for every implementation, review, and corrective ticket.
- Reject solo-agent tickets as malformed.
- Have Blue/Logos keep pair/team failure notes throughout the run.
- Convert failure notes into future skill guidance when failures are repeated, severe, or likely to recur.
- Distinguish implementation defects from process defects.

## Future Tool Schema

```json
{
  "name": "frontend_design_council",
  "description": "Create a paired frontend redesign council packet with auto-code tickets and failure-note guidance.",
  "inputSchema": {
    "type": "object",
    "required": ["repoPath", "targetSurface"],
    "properties": {
      "repoPath": { "type": "string" },
      "targetSurface": { "type": "string" },
      "mode": { "type": "string", "enum": ["auto-code", "plan-only"], "default": "auto-code" },
      "frontendStack": { "type": "string" },
      "constraints": { "type": "string" },
      "verificationCommands": {
        "type": "array",
        "items": { "type": "string" }
      }
    },
    "additionalProperties": false
  }
}
```

## Packet Shape Additions

```json
{
  "pairRequirement": {
    "soloAgentsAllowed": false,
    "appliesTo": ["implementation", "review", "corrective tickets"],
    "invalidWhen": ["single owner", "missing in-pair review", "missing cross-review pair"]
  },
  "blueLogosFailureNotes": {
    "required": true,
    "fields": [
      "pair",
      "ticketIds",
      "failurePattern",
      "evidence",
      "impact",
      "immediateCorrection",
      "futureSkillGuidance",
      "shouldBecomePermanentGuidance"
    ]
  }
}
```
