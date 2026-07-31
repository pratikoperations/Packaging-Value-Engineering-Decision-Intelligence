from __future__ import annotations

from src.persistence.database import Database

APPROVED_SPECIFICATION_CONSUMPTION_SCHEMA_VERSION = 12


def initialize_approved_specification_consumption_schema(database: Database) -> int:
    with database.transaction() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS approved_specification_consumption_envelopes (
                envelope_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                snapshot_id TEXT NOT NULL,
                review_id TEXT NOT NULL,
                source_review_revision_id TEXT NOT NULL,
                source_review_revision_number INTEGER NOT NULL CHECK (source_review_revision_number > 0),
                existing_dataset_id TEXT NOT NULL,
                proposed_dataset_id TEXT NOT NULL,
                snapshot_schema_version TEXT NOT NULL,
                consumption_contract_version TEXT NOT NULL,
                approved_values_json TEXT NOT NULL,
                excluded_fields_json TEXT NOT NULL,
                snapshot_content_hash TEXT NOT NULL,
                envelope_content_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(snapshot_id, consumption_contract_version),
                FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
                FOREIGN KEY (snapshot_id) REFERENCES approved_specification_snapshots(snapshot_id) ON DELETE RESTRICT,
                CHECK (existing_dataset_id <> proposed_dataset_id)
            );
            CREATE INDEX IF NOT EXISTS idx_consumption_envelopes_project
                ON approved_specification_consumption_envelopes(project_id, created_at, envelope_id);
            CREATE INDEX IF NOT EXISTS idx_consumption_envelopes_snapshot
                ON approved_specification_consumption_envelopes(project_id, snapshot_id);

            CREATE TABLE IF NOT EXISTS approved_specification_consumption_authorizations (
                authorization_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                snapshot_id TEXT NOT NULL,
                envelope_id TEXT NOT NULL,
                purpose TEXT NOT NULL CHECK (purpose IN (
                    'cost_analysis_input', 'scenario_analysis_input', 'risk_analysis_input',
                    'material_analysis_input', 'sourcing_input_preparation',
                    'recommendation_input_preparation', 'governance_demonstration'
                )),
                actor_reference TEXT NOT NULL CHECK (length(trim(actor_reference)) > 0),
                business_reason TEXT NOT NULL CHECK (length(trim(business_reason)) > 0),
                snapshot_content_hash TEXT NOT NULL,
                envelope_content_hash TEXT NOT NULL,
                authorization_schema_version TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(project_id, snapshot_id, envelope_id, purpose, actor_reference,
                       business_reason, envelope_content_hash),
                FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
                FOREIGN KEY (snapshot_id) REFERENCES approved_specification_snapshots(snapshot_id) ON DELETE RESTRICT,
                FOREIGN KEY (envelope_id) REFERENCES approved_specification_consumption_envelopes(envelope_id) ON DELETE RESTRICT
            );
            CREATE INDEX IF NOT EXISTS idx_consumption_authorizations_project
                ON approved_specification_consumption_authorizations(project_id, created_at, authorization_id);
            CREATE INDEX IF NOT EXISTS idx_consumption_authorizations_snapshot
                ON approved_specification_consumption_authorizations(project_id, snapshot_id, created_at, authorization_id);

            CREATE TRIGGER IF NOT EXISTS consumption_envelopes_immutable_update
                BEFORE UPDATE ON approved_specification_consumption_envelopes
                BEGIN SELECT RAISE(ABORT, 'approved specification consumption envelopes are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS consumption_envelopes_immutable_delete
                BEFORE DELETE ON approved_specification_consumption_envelopes
                BEGIN SELECT RAISE(ABORT, 'approved specification consumption envelopes are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS consumption_authorizations_immutable_update
                BEFORE UPDATE ON approved_specification_consumption_authorizations
                BEGIN SELECT RAISE(ABORT, 'approved specification consumption authorizations are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS consumption_authorizations_immutable_delete
                BEFORE DELETE ON approved_specification_consumption_authorizations
                BEGIN SELECT RAISE(ABORT, 'approved specification consumption authorizations are immutable'); END;
            """
        )
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)",
            (APPROVED_SPECIFICATION_CONSUMPTION_SCHEMA_VERSION,),
        )
    return APPROVED_SPECIFICATION_CONSUMPTION_SCHEMA_VERSION
