# Draft Issue Breakdown: Local AI Brain Install Container

Parent: `001_localaibrain-install-container-prd.md`
Status: draft-for-review

## Proposed Vertical Slices

1. **Route new deploys through the Install Container**
   - Type: AFK
   - Blocked by: None
   - User stories covered: 1, 2, 6, 7, 8, 9, 10, 11, 12, 16
   - Outcome: A fresh deploy leaves `localaibrain.py` at the project root and writes Local AI Brain-owned package code, runtime data, plans, MCP registry, and MCP adapter under `localaibrain/`. Generated instructions and host configs point to those new paths.

2. **Conservatively migrate old scattered installs**
   - Type: AFK
   - Blocked by: 1
   - User stories covered: 3, 4, 13, 14, 15
   - Outcome: Deploy can upgrade projects that already have old root-level Local AI Brain folders. Safe old folders move into the Install Container. Conflicting old/new folders produce warnings and are not merged automatically.

3. **Keep command surfaces working after the layout change**
   - Type: AFK
   - Blocked by: 1, 2
   - User stories covered: 1, 5, 6, 7, 9, 15, 16
   - Outcome: `run`, `terminal`, `ui`, `doctor`, `optimize-main`, `optimize-project`, `index`, MCP adapter execution, deploy registry resolution, and rollback continue to work with the new container paths.

4. **Prove the layout with smoke tests and docs**
   - Type: AFK
   - Blocked by: 1, 2, 3
   - User stories covered: 12, 13, 14, 17
   - Outcome: Unit tests and a temporary-project smoke deploy verify the new layout end to end. The PRD/update docs record what shipped and how it was verified.

5. **Plan Brain Issues as the next product slice**
   - Type: HITL
   - Blocked by: 1, 2, 3, 4
   - User stories covered: 18
   - Outcome: A follow-up PRD/issue set defines Brain Issues as first-class SQLite records for Local AI Brain project management. No schema or UI implementation happens in the install-container slice.

6. **Plan Brain Reviews as the approval queue slice**
   - Type: HITL
   - Blocked by: 5
   - User stories covered: 19, 20
   - Outcome: A follow-up PRD/issue set defines Brain Reviews as the top-level queue for approvals, rejections, and requested revisions. No review queue implementation happens in the install-container slice.

## Recommendation

Implement slices 1 through 4 now as the current install-container release. Keep slices 5 and 6 as explicit future product-planning slices so this pass does not drift into building the project-management system before the portable layout is proven.

## Questions For Approval

1. Does this granularity feel right, or should the smoke/docs slice be merged into the command-surface slice?
2. Are slices 5 and 6 correctly marked HITL because they need another product decision pass?
3. Should migration be its own issue, or should it be part of the first install-container issue?
