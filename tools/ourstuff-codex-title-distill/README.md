# Codex Title Distill

Compatibility path for the deterministic Codex title helper.

The implementation now lives with Local AI Brain:

```text
C:\Users\jrice\.agents\tools\local-ai-brain\local_ai_brain\title_distill.py
```

Prefer the Local AI Brain command:

```powershell
C:\Users\jrice\.agents\tools\local-ai-brain\local-ai-brain.ps1 codex-title-distill --date 2026-06-05
```

The old script path remains as a shim for existing calls.

It reads:

- `~/.codex/state_5.sqlite`
- each thread's `rollout_path` JSONL
- optional `~/.codex/session_index.jsonl`

It proposes titles shaped like:

```text
2026-06-05 Local AI Brain Installer
```

## Usage

Dry-run today through the compatibility shim:

```powershell
python C:\Users\jrice\.agents\tools\codex-title-distill\codex_title_distill.py
```

Dry-run a specific day:

```powershell
python C:\Users\jrice\.agents\tools\codex-title-distill\codex_title_distill.py --date 2026-06-05
```

Apply after review:

```powershell
python C:\Users\jrice\.agents\tools\codex-title-distill\codex_title_distill.py --date 2026-06-05 --apply --yes
```

Retitle chats that already have a date prefix:

```powershell
python C:\Users\jrice\.agents\tools\codex-title-distill\codex_title_distill.py --date 2026-06-05 --force-retitle --apply --yes
```

## Safety

- Dry-run is the default.
- `--apply` creates a SQLite backup through the SQLite backup API.
- `session_index.jsonl` is backed up before compatibility records are appended.
- Updates happen inside one SQLite transaction.
- Every run writes an audit JSONL under `~/.codex/title-distill-audit`.
- Already date-prefixed titles are skipped unless `--force-retitle` is set.
