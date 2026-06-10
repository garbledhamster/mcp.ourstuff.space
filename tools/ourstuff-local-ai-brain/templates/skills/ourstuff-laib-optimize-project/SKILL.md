---
name: Ourstuff LAIB Optimize Project
description: Optimize the nearest or most relevant project Local AI Brain by using MCP first, then falling back to the commander CLI.
managed_by: local-ai-brain-managed
schema: v1
---

Use this when the user asks to optimize, compact, clean, or maintain a project Local AI Brain.

1. Resolve an explicit project first when the user gives one.
2. Otherwise use the nearest project brain from the current working directory.
3. Otherwise use the most recently used project brain.
4. Prefer the project MCP `optimize-project` tool when available.
5. If MCP is unavailable, run the commander fallback:

```powershell
python localaibrain.py optimize-project
```

Do not silently optimize the main brain unless the user explicitly asks for main or passes a main fallback.
