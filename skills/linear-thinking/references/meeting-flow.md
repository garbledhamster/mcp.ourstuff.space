# Meeting Flow

## Mindsets

Default meetings use six canonical mindsets in three paired agents.

| Mindset | Primary Question |
| --- | --- |
| Operator | What needs to happen next? |
| Engineer | How do we build it? |
| Architect | How should the system fit together? |
| Strategist | Why this direction, and what tradeoffs does it create? |
| Steward | What must be protected, maintained, or made sustainable? |
| Philosopher | What assumptions, meanings, or values are shaping the decision? |

## Default Pairs

Use these pairs unless first Blue/Logos explains why a dynamic override is better for the topic.

| Pair | Mindsets | Default Working Question |
| --- | --- | --- |
| Build Pair | Operator + Engineer | What should be done next, and how can it be implemented cleanly? |
| Shape Pair | Architect + Strategist | What structure and direction should guide the work? |
| Guardrail Pair | Steward + Philosopher | What must remain true for the decision to be responsible and coherent? |

## First Blue/Logos

First Blue/Logos must:

1. Create and announce `.local\meetings\<date-slug>\`.
2. Name the live-agent limit: orchestrator plus three paired agents.
3. Propose the paired roster, working questions, and three-pass plan.
4. Explain any dynamic pair override.
5. Pause for user edits before expert work starts.

## Pass 1: Paired Six Hats

Each pair internally runs Blue, White, Red, Black, Yellow, and Green against its working question. Only the final pair proposal is visible.

Visible proposal format:

```text
Pair:
Working question:

Proposal:

Why this is the right move:

What we can help implement:
- 
- 
- 

Memory candidates:
- 
```

## Pass 2: Shuffle Review

Shuffle the six mindsets across review pairs. Each shuffled pair reviews another pair's proposal and writes:

- critique
- clarification of what the proposal means
- appended change proposal, if useful
- memory candidates, only if future expert behavior should change

## Pass 3: Final Blue Synthesis

Final Blue/Logos synthesizes the meeting into the user's requested output, verifies it against the request, names remaining uncertainties, decides which memory candidates are durable, writes approved local `MEMORY.md` changes, and reports exact files and summaries.

## Pair Continuity After Final Blue

If the user chooses to build, final Blue/Logos deploys the same pairs back into the work. The Pass 1 pairs remain the default implementation lanes, and each pair owns the implementation scope matching its proposal:

- Operator + Engineer owns the build lane.
- Architect + Strategist owns the shape and integration lane.
- Steward + Philosopher owns the guardrail and coherence lane.

The user can explicitly swap pairs or change ownership, but continuity is the default. Do not describe final Blue/Logos as handing off to unrelated coding agents.

## Meeting Files

Each meeting path contains Markdown summaries plus JSON files and `events.jsonl` for the future SMS-style dashboard.

```text
MEETING.md
passes\pass-1-pair-proposals.md
passes\pass-2-shuffle-review.md
passes\pass-3-final-blue.md
memory-updates.md
meeting.json
pair-proposals.json
shuffle-reviews.json
final-blue.json
memory-updates.json
events.jsonl
```

Minimum event shape:

```json
{
  "meetingId": "",
  "timestamp": "",
  "pass": 1,
  "hat": "blue",
  "speakerId": "",
  "speakerName": "",
  "pairId": "",
  "mindsets": [],
  "messageType": "chat",
  "visibility": "internal",
  "text": ""
}
```

Use `visibility: "visible"` for live-chat summaries and `visibility: "internal"` for saved-only hat dialogue.
