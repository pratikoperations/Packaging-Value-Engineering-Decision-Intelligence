from __future__ import annotations

from src.persistence.database import Database

APPROVED_SPECIFICATION_SCHEMA_VERSION = 11


def initialize_approved_specification_schema(database: Database) -> int:
    """Apply the additive E1.6 approved-specification snapshot schema."""
    with database.transaction() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS approved_specification_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                review_id TEXT NOT NULL,
                source_review_revision_id TEXT NOT NULL UNIQUE,
                source_review_revision_number INTEGER NOT NULL
                    CHECK (source_review_revision_number > 0),
                existing_dataset_id TEXT NOT NULL,
                proposed_dataset_id TEXT NOT NULL,
                approved_values_json TEXT NOT NULL,
                excluded_fields_json TEXT NOT NULL,
                snapshot_schema_version TEXT NOT NULL,
                actor_reference TEXT NOT NULL
                    CHECK (length(trim(actor_reference)) > 0),
                approval_reason TEXT NOT NULL
                    CHECK (length(trim(approval_reason)) > 0),
                content_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
                    ON DELETE RESTRICT,
                FOREIGN KEY (existing_dataset_id) REFERENCES project_datasets(dataset_id)
                    ON DELETE RESTRICT,
                FOREIGN KEY (proposed_dataset_id) REFERENCES project_datasets(dataset_id)
                    ON DELETE RESTRICT,
                FOREIGN KEY (source_review_revision_id)
                    REFERENCES specification_review_revisions(review_revision_id)
                    ON DELETE RESTRICT,
                CHECK (existing_dataset_id <> proposed_dataset_id)
            );
            CREATE INDEX IF NOT EXISTS idx_approved_specification_snapshots_project
                ON approved_specification_snapshots(project_id, created_at, snapshot_id);
            CREATE INDEX IF NOT EXISTS idx_approved_specification_snapshots_review
                ON approved_specification_snapshots(project_id, review_id, created_at, snapshot_id);
            CREATE TRIGGER IF NOT EXISTS approved_specification_snapshots_immutable_update
                BEFORE UPDATE ON approved_specification_snapshots
                BEGIN
                    SELECT RAISE(ABORT, 'approved_specification_snapshots are immutable');
                END;
            CREATE TRIGGER IF NOT EXISTS approved_specification_snapshots_immutable_delete
                BEFORE DELETE ON approved_specification_snapshots
                BEGIN
                    SELECT RAISE(ABORT, 'approved_specification_snapshots are immutable');
                END;
            """
        )
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)",
            (APPROVED_SPECIFICATION_SCHEMA_VERSION,),
        )
    return APPROVED_SPECIFICATION_SCHEMA_VERSION
