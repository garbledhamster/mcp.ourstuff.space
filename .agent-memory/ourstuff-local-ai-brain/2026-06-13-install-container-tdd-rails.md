# Local AI Brain Install Container TDD Rails

Date: 2026-06-13

## Target Surface

- Repo: `C:\Github\mcp.ourstuff.space`
- Tool: `tools/ourstuff-local-ai-brain`
- Goal: keep the root Commander at `localaibrain.py`, move Local AI Brain-owned install files into `project_root/localaibrain/`, preserve conservative migration, and keep command/MCP surfaces working.

## Consolidated Tasklist

- [x] P0 Route fresh deploy plans through `project_root/localaibrain/{scripts,brain,plans,mcp}` while leaving the Commander at `project_root/localaibrain.py`.
- [x] P0 Generate MCP registry, adapter, server specs, and agent instructions with container paths.
- [x] P0 Conservatively migrate old scattered root install artifacts when the destination is absent.
- [x] P0 Warn and preserve both sides when old and new migration paths conflict.
- [x] P1 Keep registry resolution compatible with new container entries and legacy adapter/registry entries.
- [x] P1 Keep package MCP repo defaults pointed at the project root while runtime state stays container-local.
- [x] P2 Add unit coverage for layout, migration, rollback safety, registry resolution, adapter source, and package MCP path behavior.
- [x] P2 Run scratch deploy plus doctor smoke with deploy registry redirected to a temp file.

## Model Provenance

| Task | Phase | Pair | Requested System | Requested Model | Actual Model | Reasoning | Fallback |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Rail 1 | coding | Build Pair: Operator + Engineer | multi_agent_v1 worker | gpt-5.3-codex-spark | unknown | high | none |
| Rail 2 | coding | Guardrail Pair: Steward + Philosopher | multi_agent_v1 worker | gpt-5.3-codex-spark | unknown | high | none |
| Rail 3 | coding | Shape Pair: Architect + Strategist | multi_agent_v1 worker | gpt-5.3-codex-spark | unknown | high | none |
| Blue/Logos | orchestration/integration | Blue/Logos | Codex | GPT-5.5 | unknown | not exposed | direct integration |

## Verification

- `python -B -m unittest discover -s tests`: 18 tests, OK.
- Scratch deploy smoke through `localaibrain.run_plan` with `DEPLOY_REGISTRY_PATH` mocked to temp: `deploy_result=0`, no expected files missing.
- Scratch doctor smoke through `localaibrain.run_brain_command(plan, ["doctor"])`: `doctor_result=0`.
- `git diff --check` on changed files: no whitespace errors; Git reported line-ending normalization warnings only.

## Report Cards

### Report Card: Build Pair

- `Phase:` coding
- `Requested model:` gpt-5.3-codex-spark
- `Actual model:` unknown
- `Grade:` A
- `Evidence:` delivered container path contract, adapter source, registry references, and passing tests.
- `Keep doing:` tie tests to deploy-visible path behavior.
- `Improve next time:` avoid overlapping edits while orchestrator is integrating.
- `Future prompt instruction:` return patch intent plus exact write scope before editing shared files.

### Report Card: Guardrail Pair

- `Phase:` coding
- `Requested model:` gpt-5.3-codex-spark
- `Actual model:` unknown
- `Grade:` A-
- `Evidence:` delivered migration conflict behavior and rollback safety tests.
- `Keep doing:` preserve user data by warning instead of merging.
- `Improve next time:` create all fixture parent directories in tests.
- `Future prompt instruction:` when writing path fixtures, create the immediate parent for every generated file.

### Report Card: Shape Pair

- `Phase:` coding
- `Requested model:` gpt-5.3-codex-spark
- `Actual model:` unknown
- `Grade:` A-
- `Evidence:` delivered registry/candidate compatibility for new and legacy entries.
- `Keep doing:` store explicit path fields in registry records.
- `Improve next time:` call out legacy path inference rules in the report.
- `Future prompt instruction:` document whether a path helper returns project root, install container, or host-required folder.

### Report Card: Blue/Logos

- `Phase:` orchestration, integration, verification
- `Requested model:` GPT-5.5
- `Actual model:` unknown
- `Grade:` B+
- `Evidence:` integrated three rails, added package MCP regression, ran unit and smoke verification.
- `Keep doing:` run scratch smoke with global deploy registry redirected.
- `Improve next time:` pause worker editing earlier when shared files are unavoidable.
- `Future prompt instruction:` for shared-file rails, assign workers to forked patches or planning reports unless write sequencing is explicit.

## Pair Failure Notes

### Pair Failure Note

- `Pair:` all implementation rails
- `Phase:` coding
- `Observed failure:` write scopes overlapped on `localaibrain.py` and `tests/test_localaibrain.py`.
- `Evidence:` orchestrator observed shared workspace changes while integrating.
- `Impact:` required extra diff review and duplicate patch checks.
- `Correction needed now:` integration review completed; no blocking defects remain.
- `Future skill guidance:` for backend rails with shared files, use planning/explorer rails first or require patch files instead of direct concurrent edits.

## Future Skill Guidance

- `Observed pattern:` frontend-oriented rail workflow was used for a backend installer slice with highly shared files.
- `Skill gap:` the skill does not distinguish direct parallel edits from parallel planning when shared files dominate.
- `Recommended guidance text:` For backend/tooling work where all rails need the same implementation files, run parallel planning or patch-proposal rails first, then let Blue/Logos sequence the actual TDD edits.
- `Recommended destination:` workflow.md
- `Priority:` medium
