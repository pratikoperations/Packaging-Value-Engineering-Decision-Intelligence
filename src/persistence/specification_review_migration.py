from __future__ import annotations

from src.persistence.database import Database

SPECIFICATION_REVIEW_SCHEMA_VERSION = 10


def initialize_specification_review_schema(database: Database) -> int:
    """Apply the additive E1.3 specification-review persistence schema."""
    with database.transaction() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS specification_review_revisions (
                review_revision_id TEXT PRIMARY KEY,
                review_id TEXT NOT NULL,
                revision_number INTEGER NOT NULL CHECK (revision_number > 0),
                state_schema_version TEXT NOT NULL,
                project_id TEXT NOT NULL,
                existing_dataset_id TEXT NOT NULL,
                proposed_dataset_id TEXT NOT NULL,
                existing_baseline_confirmed INTEGER NOT NULL CHECK (existing_baseline_confirmed IN (0, 1)),
                existing_baseline_dataset_id TEXT,
                comparisons_json TEXT NOT NULL,
                has_unresolved_validation_issue INTEGER NOT NULL CHECK (has_unresolved_validation_issue IN (0, 1)),
                eligibility_json TEXT NOT NULL,
                action_type TEXT NOT NULL CHECK (action_type IN ('initialize', 'confirm_baseline', 'accept', 'reject', 'correct')),
                action_field_key TEXT,
                actor_reference TEXT NOT NULL,
                action_reason TEXT,
                parent_revision_id TEXT,
                content_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
                FOREIGN KEY (existing_dataset_id) REFERENCES project_datasets(dataset_id) ON DELETE RESTRICT,
                FOREIGN KEY (proposed_dataset_id) REFERENCES project_datasets(dataset_id) ON DELETE RESTRICT,
                FOREIGN KEY (parent_revision_id) REFERENCES specification_review_revisions(review_revision_id) ON DELETE RESTRICT,
                UNIQUE (review_id, revision_number),
                UNIQUE (review_id, content_hash),
                CHECK (existing_dataset_id <> proposed_dataset_id),
                CHECK (
                    (revision_number = 1 AND parent_revision_id IS NULL AND action_type = 'initialize')
                    OR (revision_number > 1 AND parent_revision_id IS NOT NULL AND action_type <> 'initialize')
                ),
                CHECK (
                    action_type NOT IN ('accept', 'reject', 'correct')
                    OR (action_field_key IS NOT NULL AND length(trim(action_field_key)) > 0)
                ),
                CHECK (
                    action_type NOT IN ('reject', 'correct')
                    OR (action_reason IS NOT NULL AND length(trim(action_reason)) > 0)
                ),
                CHECK (length(trim(actor_reference)) > 0)
            );
            CREATE INDEX IF NOT EXISTS idx_specification_review_revisions_review
                ON specification_review_revisions(review_id, revision_number);
            CREATE INDEX IF NOT EXISTS idx_specification_review_revisions_project
                ON specification_review_revisions(project_id, created_at, review_revision_id);
            CREATE TRIGGER IF NOT EXISTS specification_review_revisions_immutable_update
                BEFORE UPDATE ON specification_review_revisions
                BEGIN SELECT RAISE(ABORT, 'specification_review_revisions are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS specification_review_revisions_immutable_delete
                BEFORE DELETE ON specification_review_revisions
                BEGIN SELECT RAISE(ABORT, 'specification_review_revisions are immutable'); END;
            """
        )
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)",
            (SPECIFICATION_REVIEW_SCHEMA_VERSION,),
        )
    return SPECIFICATION_REVIEW_SCHEMA_VERSION
