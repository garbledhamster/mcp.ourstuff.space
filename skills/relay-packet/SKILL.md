---
name: relay-packet
description: Relay a concise whole context packet to the next agent to resume work.
---

VARIABLES:

GOAL = RELAY YOUR WORK TO THE NEXT AGENT VIA TEMP.
REQUEST = THE ORIGINAL REQUEST THE FIRST AGENT WAS GIVEN. NOT THE RELAY PACKET INSTRUCTION.
REQUEST_ID = <short-goal-slug>-<first-created-YYYYMMDD-HHMMSS>
FILENAME = relay-packet-<YYYYMMDD-HHMMSS>-<short-goal-slug>.md
CURRENT_PACKET = Windows: %TEMP%\.agents\relay\current\REQUEST_ID.md or Linux: /tmp/.agents/relay/current/REQUEST_ID.md or Mac: /tmp/.agents/relay/current/REQUEST_ID.md
ARCHIVE_PACKET = Windows: %TEMP%\.agents\relay\archive\REQUEST_ID\FILENAME or Linux: /tmp/.agents/relay/archive/REQUEST_ID/FILENAME or Mac: /tmp/.agents/relay/archive/REQUEST_ID/FILENAME
LOCKFILE = CURRENT_PACKET.lock
TEMP = Windows: %TEMP%\.agents\relay or Linux: /tmp/.agents/relay or Mac: /tmp/.agents/relay
PACKET = CONTEXT PACKET TO BE RELAYED TO THE NEXT AGENT WITH THE CURRENT_PACKET PATH FROM ABOVE
CATEGORIES = Original Request, Checklist, Skills Used, Changelog

Work through (creating, updating, appending the PACKET) a collaborative PACKET in TEMP to take advantage of the "memento effect".

STATE IDENTITY:
- Use REQUEST_ID to identify which packet belongs to this work.
- REQUEST_ID must be generated from the short-goal-slug and the timestamp of the first created packet.
- Do not change REQUEST_ID after the packet is created.
- Use CURRENT_PACKET as the stable handoff path for future agents.
- Use ARCHIVE_PACKET only as an optional timestamped snapshot.
- Future agents must resume from CURRENT_PACKET first.

PACKET DISCOVERY:
- Before creating a new packet, search TEMP/relay/current for an existing packet with the same REQUEST_ID or short-goal-slug.
- If one matching CURRENT_PACKET is found, update that packet.
- If multiple packets match the same request, use the most recently modified packet and note the ambiguity in Changelog.
- If no packet exists, create one.
- If a packet exists for the same request, update Checklist statuses and append Changelog entries.
- Do not erase prior Changelog entries.

WRITE SAFETY:
- Before writing, create LOCKFILE when possible.
- If LOCKFILE already exists, re-read CURRENT_PACKET before writing and append after existing changes.
- Remove LOCKFILE after writing when possible.
- If the write fails, output the error and do not claim the relay succeeded.
- Do not overwrite existing packet content unless preserving prior Changelog entries.

Collaborate with another agent on these CATEGORIES:
 - Original REQUEST you were given.
   - Include REQUEST_ID.
   - Include Created timestamp.
   - Include Last Updated timestamp.
   - Include the original request text.
 - Checklist of **ALL** the planned work you have.
   - Mark each item in the list with the labels `[plan]`, `[active]`, `[err]`, and `[done]`.
   - Each item should be filled in with your own results.
   - Each item should include concise Result and Next details when useful.
 - Any skills you have used with a colon and a 10 words or less description of how you used it.
 - An agent maintained, concise Changelog of work done in this REQUEST.

CHECKLIST STATUS RULES:
- Use only these Checklist labels: `[plan]`, `[active]`, `[err]`, `[done]`.
- There must be at most one `[active]` item.
- `[plan]` means intended but not started.
- `[active]` means current next work item.
- `[err]` means blocked, failed, uncertain, or needs attention.
- `[done]` means completed and verified as far as possible.
- If the current item is incomplete, keep it `[active]`.
- If it failed or is blocked, mark it `[err]`.
- Only mark it `[done]` when completed.
- Do not mark work `[done]` just because it was attempted.

VALIDATION BEFORE OUTPUT:
- Confirm all required CATEGORIES exist.
- Confirm Original Request is not the relay packet instruction.
- Confirm Checklist uses only `[plan]`, `[active]`, `[err]`, `[done]`.
- Confirm there is at most one `[active]` item.
- Confirm Changelog has at least one entry.
- Confirm unknown information is marked `Unknown` or `None yet`.
- Confirm no secrets, credentials, tokens, private keys, session cookies, or sensitive data are included.
- If validation fails, repair the packet before outputting the path.

RECOVERY:
- If an existing packet is malformed, do not delete it.
- Preserve recoverable content.
- Create or update a repaired CURRENT_PACKET.
- Note the repair in Changelog.
- If multiple packets appear to contain useful history, preserve the most recent one as CURRENT_PACKET and summarize recoverable unique history in Changelog.
- If the task is blocked, mark the relevant Checklist item `[err]` and explain the blocker concisely.

COMPACTION:
- Keep the packet concise.
- Do not turn the packet into a full transcript.
- If the packet becomes too large, compact older Changelog entries into concise summary entries.
- Preserve all `[active]` and `[err]` Checklist items.
- Preserve the Original Request.
- Preserve recent Changelog entries that explain the current state.

SECURITY:
- Do not include secrets, tokens, credentials, private keys, session cookies, API keys, passwords, or sensitive personal data.
- If sensitive data appears necessary, write `[REDACTED]` and describe the dependency without revealing the value.

Do not rely on chat/session memory as the durable handoff.
Do not make any CATEGORIES up use what I have to pass between agents.
Do not leave artifacts or traces of this work outside of the PACKET in TEMP, when possible.
If a required category has no known content, write `Unknown` or `None yet`. Do not guess.

Store it in CURRENT_PACKET where the next agent will continue the work.
Optionally store a timestamped copy in ARCHIVE_PACKET when useful.

Future agents will be able to use this to continue your work.
Your final output if the PACKET is built must be the path to CURRENT_PACKET in TEMP for the next agent to use.
If the PACKET cannot be built, your final output must be the failure reason and the attempted path.

EXAMPLE```
# Relay Packet

## Original Request
REQUEST_ID: ...
Created: ...
Last Updated: ...

...

## Checklist
- [done] ... Result: ... Next: ...
- [active] ... Result: ... Next: ...
- [plan] ... Result: None yet. Next: ...
- [err] ... Result: ... Next: ...

## Skills Used
- skill-name: under 10 words

## Changelog
- timestamp — agent — action