---
name: Ourstuff LAIB Optimize Main
description: Optimize the main Local AI Brain by using the configured MCP server first, then falling back to the commander CLI.
managed_by: local-ai-brain-managed
schema: v1
---

Use this when the user asks to optimize, compact, clean, or maintain the main Local AI Brain.

1. Prefer the `localaibrain.optimize-main` MCP tool when it is available.
2. If MCP is unavailable, run the commander fallback from the installed Local AI Brain folder:

```powershell
python localaibrain.py optimize-main
```

Use `--apply` only when the user asked to apply maintenance, not for a dry-run preview.
