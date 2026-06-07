# Linear Thinking Tests

Run from the package root:

```powershell
.\scripts\Test-LinearThinkingSkills.ps1
```

After install:

```powershell
.\scripts\Test-LinearThinkingSkills.ps1 -RequireRuntime
```

## Contract Checks

Lightweight validation should cover:

- exactly six canonical mindsets
- default pairs: Operator + Engineer, Architect + Strategist, Steward + Philosopher
- first Blue/Logos meeting path language and pause for user edits
- max live agents: orchestrator plus three paired agents
- three-pass flow: paired six hats, shuffle review, final Blue synthesis
- pair continuity after final Blue when the user chooses to build
- stable visible proposal format
- Markdown, JSON, and `events.jsonl` meeting artifacts
- final Blue/Logos as the only durable local `MEMORY.md` write point
- myMCP registry has exactly one primary `PLANNING / garbledhamster / linear-thinking-agents` packet, with `linear-thinking-expert-builder` only as bundled support
