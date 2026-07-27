from __future__ import annotations

from src.persistence.database import Database

SPECIFICATION_SNAPSHOT_SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE IF NOT EXISTS specification_snapshot_schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS unified_specification_snapshots (
    specification_snapshot_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    pair_format TEXT NOT NULL,
    existing_document_json TEXT NOT NULL,
    proposed_document_json TEXT NOT NULL,
    extraction_schema_version TEXT NOT NULL,
    alias_registry_version TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    confirmed_fields_json TEXT NOT NULL,
    canonical_dataset_draft_json TEXT NOT NULL,
    canonical_validation_issues_json TEXT NOT NULL,
    canonical_validation_valid INTEGER NOT NULL CHECK (canonical_validation_valid IN (0, 1)),
    content_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
    UNIQUE (project_id, content_hash)
);
CREATE INDEX IF NOT EXISTS idx_unified_specification_snapshots_project
ON unified_specification_snapshots(project_id, created_at, specification_snapshot_id);
CREATE TRIGGER IF NOT EXISTS unified_specification_snapshots_immutable_update
BEFORE UPDATE ON unified_specification_snapshots
BEGIN SELECT RAISE(ABORT, 'unified_specification_snapshots are immutable'); END;
CREATE TRIGGER IF NOT EXISTS unified_specification_snapshots_immutable_delete
BEFORE DELETE ON unified_specification_snapshots
BEGIN SELECT RAISE(ABORT, 'unified_specification_snapshots are immutable'); END;
"""


def initialize_specification_snapshot_schema(database: Database) -> int:
    """Apply only the additive unified specification snapshot schema."""
    with database.transaction() as connection:
        connection.executescript(_SCHEMA)
        connection.execute(
            "INSERT OR IGNORE INTO specification_snapshot_schema_migrations(version) VALUES (?)",
            (SPECIFICATION_SNAPSHOT_SCHEMA_VERSION,),
        )
    return SPECIFICATION_SNAPSHOT_SCHEMA_VERSION
