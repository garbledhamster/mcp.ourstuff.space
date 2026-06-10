---
name: Ourstuff LAIB Index
description: Rebuild or refresh the nearest Local AI Brain search index through MCP first, then fall back to the commander CLI.
managed_by: local-ai-brain-managed
schema: v1
---

Use this when the user asks to index, reindex, rebuild search, refresh memory search, or make recent work discoverable.

1. Resolve an explicit target first when the user gives one.
2. Otherwise prefer the nearest project brain from the current working directory.
3. Fall back to the main brain when no project brain is available.
4. Prefer the MCP `index` tool when available.
5. If MCP is unavailable, run the commander fallback:

```powershell
python localaibrain.py index
```
