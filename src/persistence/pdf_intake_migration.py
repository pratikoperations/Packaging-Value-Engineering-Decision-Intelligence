"""Additive schema for immutable PVE 2.1 PDF intake snapshots."""

from __future__ import annotations

from src.persistence.database import Database

PDF_INTAKE_SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE IF NOT EXISTS pdf_intake_schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS pdf_intake_snapshots (
    pdf_intake_snapshot_id TEXT PRIMARY KEY,
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
    canonical_validation_valid INTEGER NOT NULL CHECK (canonical_validation_valid IN (0,1)),
    content_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
    UNIQUE (project_id, content_hash)
);
CREATE INDEX IF NOT EXISTS idx_pdf_intake_snapshots_project
ON pdf_intake_snapshots(project_id, created_at, pdf_intake_snapshot_id);
CREATE TRIGGER IF NOT EXISTS pdf_intake_snapshots_immutable_update
BEFORE UPDATE ON pdf_intake_snapshots
BEGIN SELECT RAISE(ABORT, 'pdf_intake_snapshots are immutable'); END;
CREATE TRIGGER IF NOT EXISTS pdf_intake_snapshots_immutable_delete
BEFORE DELETE ON pdf_intake_snapshots
BEGIN SELECT RAISE(ABORT, 'pdf_intake_snapshots are immutable'); END;
"""


def initialize_pdf_intake_schema(database: Database) -> int:
    with database.transaction() as connection:
        connection.executescript(_SCHEMA)
        connection.execute(
            "INSERT OR IGNORE INTO pdf_intake_schema_migrations(version) VALUES (?)",
            (PDF_INTAKE_SCHEMA_VERSION,),
        )
    return PDF_INTAKE_SCHEMA_VERSION
