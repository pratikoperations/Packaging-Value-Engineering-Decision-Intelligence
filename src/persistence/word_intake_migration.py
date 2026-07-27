"""Additive schema boundary for immutable PVE 2.0 Word-intake snapshots."""

from __future__ import annotations

from src.persistence.database import Database

WORD_INTAKE_SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE IF NOT EXISTS word_intake_schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS word_intake_snapshots (
    word_intake_snapshot_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    existing_filename TEXT NOT NULL,
    existing_document_hash TEXT NOT NULL,
    proposed_filename TEXT NOT NULL,
    proposed_document_hash TEXT NOT NULL,
    parser_version TEXT NOT NULL,
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
CREATE INDEX IF NOT EXISTS idx_word_intake_snapshots_project
ON word_intake_snapshots(project_id, created_at, word_intake_snapshot_id);
CREATE TRIGGER IF NOT EXISTS word_intake_snapshots_immutable_update
BEFORE UPDATE ON word_intake_snapshots
BEGIN SELECT RAISE(ABORT, 'word_intake_snapshots are immutable'); END;
CREATE TRIGGER IF NOT EXISTS word_intake_snapshots_immutable_delete
BEFORE DELETE ON word_intake_snapshots
BEGIN SELECT RAISE(ABORT, 'word_intake_snapshots are immutable'); END;
"""


def initialize_word_intake_schema(database: Database) -> int:
    """Apply the additive subsystem migration without changing legacy tables."""

    with database.transaction() as connection:
        connection.executescript(_SCHEMA)
        connection.execute(
            "INSERT OR IGNORE INTO word_intake_schema_migrations(version) VALUES (?)",
            (WORD_INTAKE_SCHEMA_VERSION,),
        )
    return WORD_INTAKE_SCHEMA_VERSION
