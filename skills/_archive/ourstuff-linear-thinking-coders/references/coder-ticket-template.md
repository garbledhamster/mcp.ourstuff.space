# Coder Ticket Template

Use this for paired implementation and corrective tickets. Solo tickets are invalid.

Non-negotiable rule: there are always pairs. No solo implementation agents, no solo review agents, and no solo corrective agents. Blue/Logos owns coordination, failure-note capture, and conversion of recurring mistakes into future skill guidance.

## Pair Requirement

Every implementation ticket must be assigned to a pair.

Solo coding agents are not allowed.

Pair fields:

- Pair name:
- Pair roles:
- Task or ticket id:
- Memory lane:
- Requested execution system:
- Codex coding model, if Codex-backed: GPT-5.3-Codex-Spark (`gpt-5.3-codex-spark`)
- Codex reasoning effort, if Codex-backed: `high` by default; `xhigh` for complex, risky, cross-module, architecture-sensitive, or user-facing work
- Actual execution system/model, if known:
- Fallback reason, if any:
- GPT-5.5/Blue/Logos instruction brief:
- Primary implementer:
- Reviewer-in-pair:
- Cross-review pair:
- Failure notes owner: Blue/Logos

Pair operating rule:

Both members must contribute to the ticket. One may drive implementation, but the second must actively check scope, accessibility, maintainability, and design-doc alignment before the ticket is returned.

Invalid ticket:

Any ticket with only one assigned worker, one role, or no in-pair review step is invalid and must be reissued.

## Implementation Ticket

```markdown
## Ticket

Title:

Owner Pair:

Pair Roles:
- Role 1:
- Role 2:

Reviewer Pair:

Codex Coding Model:

Codex Reasoning Effort:

Memory Lane:

Requested Execution System:

Requested Model:

Actual Execution System / Model, If Known:

Fallback Reason:

GPT-5.5/Blue/Logos Instruction Brief:

Allowed Write Scope:

Forbidden Files:

Read-Only Context:

Task:

Assigned Tasklist Item:

Concrete Steps:

Acceptance Checks:
- Role 1 perspective satisfied:
- Role 2 perspective satisfied:
- Design doc compliance:
- Responsive/accessibility coverage:
- Codex model/reasoning instruction satisfied, if Codex-backed:

Verification Commands:

Stop And Report If:

Return the Coding Report format below.
```

Pair reflection:

- What did this pair miss or struggle with?
- Did the pair exceed, blur, or misunderstand scope?
- Did the pair create review burden for another team?
- What guidance should future tickets include to prevent the same failure?

## Coding Report

Use `Finding -> Implication -> Task` style where useful.

```markdown
## Coding Report

### Assigned Task

### Files Changed

### What Changed

### Why It Changed

### Validation Run

### Model Provenance

### Issues / Follow-Up

### Ready for Orchestrator Review
```

## Review Ticket

```markdown
## Pair Review Requirement

Reviews are also pair-owned. A solo reviewer may not be the only review path.

Review pair fields:
- Reviewing pair:
- Reviewer roles:
- Reviewed implementation pair:
- Cross-review target:

The reviewing pair must identify both code/design findings and process failures.

Finding:
- Finding type: implementation | accessibility | scope | maintainability | verification | pair-process
- Evidence:
- Impact:
- Required correction:
- Process failure, if any:
- Future skill guidance:
```

## Corrective Ticket

```markdown
## Review Finding

## Corrective Pair Requirement

Corrective tickets must also be assigned to a pair. Solo corrective agents are not allowed.

Corrective pair fields:
- Corrective pair:
- Roles:
- Original implementation pair:
- Reviewing pair:

Problem:

Evidence:

Required Fix:

Owner Pair:

Pair Roles:
- Role 1:
- Role 2:

Reviewer Pair:

Allowed Write Scope:

Forbidden Files:

Acceptance Checks:

Return the Fix Report format below.
```

## Fix Report

Corrective pairs repair only the specific issue assigned by Blue/Logos.

```markdown
## Fix Report

### Issue Fixed

### Files Changed

### Validation

### Remaining Risk
```

## Blue/Logos Failure Notes

Blue/Logos must keep running notes across all pairs.

For each pair/team:

- Pair:
- Ticket IDs:
- Requested model / actual model:
- Failure pattern:
- Evidence:
- Impact:
- Immediate correction:
- Future skill guidance:
- Should become permanent guidance: yes | no

Blue/Logos must convert repeated or high-impact failures into future skill guidance before final completion. Guidance should be concrete, short, and reusable.

## Report Card

Blue/Logos writes one report card for each pair and for itself as orchestrator.

```markdown
### Report Card

- `Agent or pair:`
- `Phase:`
- `Requested model:`
- `Actual model:` unknown if not exposed
- `Grade:` A | B | C | D | F
- `Evidence:`
- `Keep doing:`
- `Improve next time:`
- `Future prompt instruction:`
```

## Pair Prompt Rule

Every worker prompt must say:

```text
You are working as a pair, not a solo agent. Apply both roles before editing. If the two role perspectives disagree, report the disagreement and choose the option that best satisfies the design doc and repo constraints.
```

## Orchestrator Review Checklist

- Pair ownership named?
- Reviewer pair named?
- Write scope disjoint?
- Shared files sequenced by Blue/Logos?
- Ticket satisfies final design doc?
- Both role perspectives visible in the result?
- Model provenance recorded?
- Accessibility and responsive risks covered?
- Verification evidence credible?
- Pair failure note needed?
