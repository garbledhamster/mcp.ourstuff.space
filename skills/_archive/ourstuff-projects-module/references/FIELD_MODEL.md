# Projects Ourstuff Module Field Model

Use this reference to turn an external system or manual workflow into GUI fields for `projects.ourstuff.space` modules.

## Field Principles

- Prefer visible, copyable values from the target system GUI.
- Track names and URLs first, opaque IDs second.
- Separate environment, ownership, status, and verification fields.
- Store raw secrets only through the existing encrypted local secret flow.
- Keep fields optional unless the module cannot be useful without them.
- Preserve old exports by defaulting missing values to empty strings or known enum defaults.

## Baseline Fields

These fit most modules:

| Field | Type | Why it exists |
| --- | --- | --- |
| `externalName` | text | Human-readable name in the other system. |
| `externalUrl` | url | Direct admin/resource link a non-coder can paste. |
| `externalId` | text | Stable ID from the other system when visible. |
| `environment` | select | Distinguish prod/staging/dev/local/manual. |
| `owner` | text | Person or team responsible for the module data. |
| `status` | select | Not started, needs setup, active, paused, broken, retired. |
| `notes` | textarea | Manual context that does not fit structured fields. |
| `lastCheckedAt` | datetime/text | Last manual verification date. |
| `lastCheckedBy` | text | Person who checked it. |
| `sourceOfTruth` | select/text | Whether OurDashboard, external system, or manual notes are canonical. |

## System-Specific Field Candidates

### GitHub

- Repository owner/org
- Repository name
- Repository URL
- Default branch
- GitHub Pages URL
- Issues URL or project board URL
- Actions/workflow URL
- Deployment environment
- Last release/tag
- Labels or milestone convention

### Cloudflare

- Account name
- Account ID
- Zone/domain
- Zone ID
- Pages project name
- Pages project URL
- Worker name
- Worker route
- D1 database name/ID
- KV namespace name/ID
- DNS record notes

### Firebase

- Firebase project name
- Firebase project ID
- Console URL
- Hosting site/target
- Web app ID
- Auth enabled flag
- Firestore database/location
- Storage bucket
- Functions region
- Rules files or deployment notes

### Stripe

- Stripe account mode (test/live/manual)
- Product name/ID
- Price ID
- Customer portal URL
- Webhook endpoint ID/URL
- Subscription status source
- Connect account ID if relevant
- Last billing check date

### Files

- Local folder path
- Public/share path
- Artifact type
- Export filename pattern
- Backup location
- Last indexed date
- Owner
- Notes about sensitive files

### MCP

- Server name
- Server command or endpoint label
- Tool/action names
- Schema/doc URL
- Permission level
- Health status
- Last successful run
- Safe actions vs gated actions

### OurBrain

- Repo/surface key
- Context-pack query
- Memory source path
- Decision record URL/path
- Last retrieval date
- Capture status
- Scrub/sensitivity notes

### Planner / Calendar / Work Tracking

- Backend system
- Board/plan/calendar name
- Board/plan/calendar URL
- Board/plan/calendar ID
- Sync direction
- Owner/team
- Last sync/check date
- Mapping notes for phases, tasks, buckets, lanes, or milestones

### Risks / Decisions / Users

- Registry/source name
- Registry/source URL
- Owner
- Review cadence
- Severity/role/status vocabulary
- Approval or stakeholder source
- Last review date
- Notes

## Handoff Template

Use this structure when handing a module idea to another LLM or non-coder group:

```json
{
  "id": "example-system",
  "icon": "[]",
  "name": "Example System",
  "desc": "Track the Example System resources connected to this project.",
  "visibleData": "Resource names, admin links, IDs, owners, status, and last checks.",
  "controlledActions": "Record manual checks and link project records to external resources.",
  "trackingFields": [
    {
      "name": "externalUrl",
      "label": "Admin URL",
      "type": "url",
      "whereToFind": "Open the system dashboard and copy the browser URL."
    }
  ]
}
```

Current app custom module JSON may ignore `trackingFields` until the app supports schema-driven fields. Keep the field list in the handoff anyway so the next implementation pass has the manual tracking contract.
