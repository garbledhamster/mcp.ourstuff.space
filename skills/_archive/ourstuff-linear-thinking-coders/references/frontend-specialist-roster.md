# Frontend Specialist Roster

Non-negotiable rule: there are always pairs. No solo implementation agents, no solo review agents, and no solo corrective agents. Blue/Logos owns coordination, failure-note capture, and conversion of recurring mistakes into future skill guidance.

## Pairing Requirement

All design, coding, review, and verification work must be assigned to a pair or team. Solo coding agents are not allowed.

Required rule:

- Every implementation ticket must name a paired owner.
- Every review ticket must name a different paired reviewer.
- Every verification pass must be assigned to a pair or to Blue/Logos plus one review pair.
- No worker may receive a ticket framed as an individual solo task.
- If only one callable worker is available, Blue/Logos must simulate the second role explicitly in the ticket prompt and require the worker to produce both role perspectives before editing.

Pair formats:

- `Build Pair`
- `Shape Pair`
- `Guardrail Pair`
- `Integration Pair`
- `Verification Pair`
- Custom two-role pair, if the design doc justifies it.

Ticket assignment format:

```text
Owner Pair: Operator + Engineer
Reviewer Pair: Steward + Philosopher
```

## Default Council

| Pair | Mindsets | Primary Responsibility |
| --- | --- | --- |
| Build Pair | Operator + Engineer | Interaction behavior, state/data flow, feasibility, implementation sequencing |
| Shape Pair | Architect + Strategist | Information architecture, page structure, visual direction, component system |
| Guardrail Pair | Steward + Philosopher | Accessibility, maintainability, coherence, failure modes, long-term fit |

## Implementation Pairs

After final synthesis, keep pair continuity by default:

- Build Pair owns behavior and wiring tickets.
- Shape Pair owns layout, component hierarchy, and design-system tickets.
- Guardrail Pair owns accessibility, responsive resilience, verification, and corrective review tickets.
- Integration Pair is Blue/Logos plus the pair whose lane touches shared files.

## Pair Failure Notes

Blue/Logos must keep running notes on where each pair or team is failing. These notes are part of the skill feedback loop and must be converted into future skill guidance.

Track failures in these categories:

- Missed repo evidence.
- Vague recommendations.
- Unclear file scope.
- Overlapping write scopes.
- Incomplete responsive rules.
- Accessibility omissions.
- Visual polish without workflow value.
- Code plans that do not match the design doc.
- Review comments that are too abstract to ticket.
- Verification claims without evidence.
- Repeated implementation mistakes.
- Pair coordination failures.

Failure note format:

```markdown
### Pair Failure Note

- `Pair:`
- `Phase:`
- `Observed failure:`
- `Evidence:`
- `Impact:`
- `Correction needed now:`
- `Future skill guidance:`
```

## Skill Feedback Loop

At the end of each run, Blue/Logos must synthesize pair failure notes into proposed improvements for the skill.

Required output:

```markdown
## Proposed Future Skill Guidance

- `Pattern observed:`
- `Why it matters:`
- `Guidance to add or revise:`
- `Where it belongs:` SKILL.md | workflow.md | frontend-specialist-roster.md | design-doc-template.md | coder-ticket-template.md
```

Rules:

- Do not bury failures in prose summaries.
- Convert repeated failures into durable guidance.
- Distinguish one-off execution mistakes from systemic skill gaps.
- Do not edit the skill unless the user asked for edits; produce implementation-ready guidance instead.
