CREATE TABLE IF NOT EXISTS skills (
  id TEXT PRIMARY KEY,
  classifier TEXT NOT NULL,
  source_owner TEXT NOT NULL,
  slug TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  tags_json TEXT NOT NULL DEFAULT '[]',
  approved_version_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(classifier, source_owner, slug)
);

CREATE TABLE IF NOT EXISTS skill_versions (
  id TEXT PRIMARY KEY,
  skill_id TEXT NOT NULL,
  version TEXT NOT NULL,
  source_type TEXT NOT NULL,
  source_url TEXT NOT NULL DEFAULT '',
  source_commit TEXT NOT NULL DEFAULT '',
  uploaded_by TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'rejected')),
  content_hash TEXT NOT NULL,
  bundle_json TEXT NOT NULL,
  classification_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  approved_at TEXT,
  rejected_at TEXT,
  FOREIGN KEY(skill_id) REFERENCES skills(id)
);

CREATE INDEX IF NOT EXISTS idx_skills_approved ON skills(approved_version_id);
CREATE INDEX IF NOT EXISTS idx_skills_view ON skills(classifier, source_owner, slug);
CREATE INDEX IF NOT EXISTS idx_skill_versions_status ON skill_versions(status, created_at);
CREATE INDEX IF NOT EXISTS idx_skill_versions_skill ON skill_versions(skill_id, created_at);
