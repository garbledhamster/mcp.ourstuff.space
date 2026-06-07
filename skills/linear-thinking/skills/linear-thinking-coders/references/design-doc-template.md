# Final Design Doc Template

Use this template after paired proposal and shuffle review. The design doc must be decision-complete before coding tickets are created.

Non-negotiable rule: there are always pairs. No solo implementation agents, no solo review agents, and no solo corrective agents. Blue/Logos owns coordination, failure-note capture, and conversion of recurring mistakes into future skill guidance.

## 1. Target Surface

- `Repo:`
- `Route/page/component:`
- `User goal:`
- `Current problem:`
- `Primary action:`

## 2. Evidence Read

- `Repo instructions:`
- `Relevant files:`
- `Existing design system:`
- `Frontend stack:`
- `Available verification commands:`
- `Screenshots/browser evidence:`

## 3. Mission Understanding

For each pair, record:

- `Pair:`
- `Assigned area:`
- `Files / systems to inspect:`
- `Assumptions to verify:`
- `Definition of done:`

## 4. Current State Findings

| Pair | Area | Found | Notes |
| --- | --- | --- | --- |
|  |  |  |  |

## 5. Final UI Behavior

Describe the exact user-facing behavior to implement.

## 6. Component Hierarchy

List the intended components, ownership boundaries, and reuse expectations.

## 7. Layout And Responsive Rules

Define desktop, tablet, and mobile behavior. Include overflow, wrapping, fixed-format controls, and interaction-state constraints.

## 8. Token, Theme, And Styling Direction

State whether existing tokens, Tailwind/shadcn, Ourstuff theme adapters, or plain CSS should drive the implementation.

## 9. Accessibility Requirements

Include keyboard behavior, focus states, contrast, labels, semantics, reduced motion, and screen-reader relevant changes.

## 10. States

Define loading, empty, error, disabled, selected, hover, focus, and active states as applicable.

## 11. Accepted Pair Proposals

Summarize what Blue/Logos accepted from Build, Shape, and Guardrail, including each proposal's current state, target state, recommended changes, risks, dependencies, acceptance criteria, and first safe change.

## 12. Rejected Or Modified Proposals

Name rejected ideas and why they were not used.

## 13. Shuffle Review Resolutions

Record agreements, conflicts, missing pieces, risks added by other proposals, recommended merge decisions, and design changes made from peer review.

## 14. Consolidated Tasklist

Use priorities:

- `P0` = required for usable system
- `P1` = required for integration
- `P2` = quality / validation improvement
- `P3` = future enhancement

```markdown
- [ ] P0 
- [ ] P1 
- [ ] P2 
- [ ] P3 
```

## 15. Approval Gate Sign-Off

- `All planning groups submitted proposals:` yes | no
- `All planning groups completed cross-review:` yes | no
- `Blue/Logos consolidated the tasklist:` yes | no
- `Blue/Logos approved implementation:` yes | no
- `Each coding group has a specific assignment:` yes | no

## 16. Files Likely To Change

List likely files or directories. Keep this scoped enough to prevent accidental unrelated edits.

## 17. Shared File Sequencing

Name shared files that require orchestrator sequencing before paired implementation.

## 18. Implementation Lanes

Pairing rule:

- Every lane must have a pair owner.
- Solo implementation lanes are invalid.
- If a lane is too small for two agents, assign complementary roles anyway, such as implementer/reviewer, structure/accessibility, state/tests, or visual/responsive.

| Lane | Purpose | Owner Pair | Allowed Write Scope | Depends On |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

Backend:

- `Execution backend:` Codex only | OpenCode first, Codex fallback | multi_agent_v1 only
- `Codex orchestrator/instruction model:` GPT-5.5/Blue/Logos
- `Codex coding model:` GPT-5.3-Codex-Spark (`gpt-5.3-codex-spark`)
- `Codex coding reasoning effort:` `high` by default; `xhigh` for complex, risky, cross-module, architecture-sensitive, or user-facing implementation lanes
- `OpenCode role/model, if OpenCode-backed:`
- `Fallback rule:`

## 19. Model Provenance Ledger

Record requested and actual model information for every planning pair, coding pair, review pair, corrective pair, and Blue/Logos orchestration step. If the runtime does not expose the actual model, write `unknown`.

| Task/Ticket | Phase | Agent/Pair | Requested System | Requested Model | Actual System | Actual Model | Reasoning | Fallback Reason | Memory Destination |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  | unknown |  |  |  |

## 20. Code Ticket Synthesis

Each ticket must include:

- `Title:`
- `Owner Pair:`
- `Reviewer Pair:`
- `Allowed Write Scope:`
- `Forbidden Files:`
- `Read-Only Context:`
- `Codex Coding Model:`
- `Codex Reasoning Effort:`
- `Memory Lane:`
- `Requested Execution System:`
- `Requested Model:`
- `Actual Execution System / Model, If Known:`
- `Fallback Reason:`
- `GPT-5.5 Instruction Brief:`
- `Task:`
- `Concrete Steps:`
- `Acceptance Checks:`
- `Verification Commands:`
- `Stop And Report If:`

Pair requirement:

- Tickets must be assigned to pairs, never solo agents.
- The ticket prompt must define each role in the pair.
- Acceptance checks must require both pair perspectives to be satisfied.

## 21. Pair Performance Notes

Blue/Logos records where each pair or team struggled during design, implementation, review, and verification.

| Pair | Phase | Failure Observed | Evidence | Immediate Correction | Future Skill Guidance |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

Required categories to consider:

- Evidence gathering.
- Design specificity.
- Code-ticket clarity.
- File-scope discipline.
- Accessibility coverage.
- Responsive behavior.
- Component-system consistency.
- Review usefulness.
- Verification quality.
- Integration coordination.

## 22. Future Skill Guidance Synthesis

Convert pair performance notes into durable skill improvements.

For each guidance item:

- `Observed pattern:`
- `Skill gap:`
- `Recommended guidance text:`
- `Recommended destination:`
- `Priority:` low | medium | high

Rules:

- Guidance must be specific enough to patch into the skill later.
- Do not create guidance from unsupported impressions.
- Prefer recurring patterns over isolated misses.
- If a failure caused rework, mark it high priority.

## 23. Agent Report Cards

Blue/Logos records a report card for each pair and for itself as orchestrator. These are saved to Local AI Brain or the repo-local memory lane so future prompts can improve zero-shot behavior.

| Agent/Pair | Phase | Requested Model | Actual Model | Grade | Evidence | Keep Doing | Improve Next Time | Future Prompt Instruction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | unknown |  |  |  |  |  |

## 24. Acceptance Criteria

- Target UI behavior matches this design doc.
- The coding-agent behavior standard was loaded and applied.
- Model provenance and report cards were saved to the active memory lane.
- The consolidated tasklist exists before coding dispatch.
- The approval gate is satisfied before any worker edits.
- Responsive layout works at mobile and desktop sizes.
- Accessibility requirements are satisfied.
- Loading, empty, and error states are covered where relevant.
- Every implementation, review, and verification task was assigned to a pair.
- Blue/Logos recorded pair failure notes.
- Blue/Logos produced future skill guidance for repeated or high-impact failures.

## 23. Verification Plan

List exact commands and browser/screenshot checks to run.
