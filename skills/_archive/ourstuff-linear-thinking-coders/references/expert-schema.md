# Expert Schema

Each local expert directory contains:

```text
AGENTS.md
MEMORY.template.md
MEMORY.md          # local only
meetings\          # local only
```

Tracked starter experts include only `AGENTS.md` and `MEMORY.template.md`.

## Required AGENTS.md Fields

- Name
- Age
- Domain
- Role
- Mindset
- Primary question
- Default starter
- Voice
- Life-defining event
- Analogy style
- Maintenance rules

## Roles And Mindsets

`Mindset:` is the canonical meeting perspective. `Role:` remains in the profile for current template and script compatibility, but it must match `Mindset:` exactly.

Valid values:

- Operator
- Engineer
- Architect
- Strategist
- Steward
- Philosopher

Starter experts also define `Default starter:`. There should be at most one `Default starter: Yes` profile for each canonical mindset.

## Memory Contract

- `MEMORY.template.md` is the tracked starter structure.
- `MEMORY.md` is private durable local knowledge only.
- Meeting folders are compact short-term session history.
- Pair proposals and shuffle reviews list memory candidates only.
- Only final Blue/Logos may write durable local `MEMORY.md`.
- Final Blue/Logos reports exact expert memory files changed and exact summaries saved.
- Never promote `MEMORY.md`, meeting files, or private details into tracked Git files.
