from __future__ import annotations

"""Additive schema v10 for the Build 7 supplier qualification evidence register."""

from sqlite3 import Connection

from src.persistence.database import Database
from src.persistence import migrations as v9

SCHEMA_VERSION = 10


def _apply_v10(connection: Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS supplier_qualification_assessments (
            supplier_qualification_assessment_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            qualification_code TEXT NOT NULL,
            supplier_name TEXT NOT NULL,
            supplier_site TEXT NOT NULL,
            qualification_scope TEXT NOT NULL,
            assessment_type TEXT NOT NULL CHECK (assessment_type IN ('initial', 'renewal', 'scope_extension', 'corrective_reassessment', 'periodic_review')),
            assessment_date TEXT NOT NULL,
            qualification_status TEXT NOT NULL CHECK (qualification_status IN ('pending', 'conditionally_qualified', 'qualified', 'not_qualified', 'expired')),
            valid_from TEXT,
            valid_until TEXT,
            review_date TEXT,
            conditions_json TEXT NOT NULL DEFAULT '[]',
            open_actions_json TEXT NOT NULL DEFAULT '[]',
            linked_trial_execution_ids_json TEXT NOT NULL DEFAULT '[]',
            linked_defect_classification_ids_json TEXT NOT NULL DEFAULT '[]',
            linked_complaint_record_ids_json TEXT NOT NULL DEFAULT '[]',
            linked_specification_change_request_ids_json TEXT NOT NULL DEFAULT '[]',
            linked_implementation_control_ids_json TEXT NOT NULL DEFAULT '[]',
            evidence_references_json TEXT NOT NULL DEFAULT '[]',
            assessed_by TEXT NOT NULL,
            approved_by TEXT,
            approval_reference TEXT,
            approved_at TEXT,
            decision_rationale TEXT,
            metadata_json TEXT NOT NULL DEFAULT '{}',
            content_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
            UNIQUE (project_id, qualification_code),
            UNIQUE (project_id, content_hash)
        );
        CREATE INDEX IF NOT EXISTS idx_supplier_qualification_project
        ON supplier_qualification_assessments(project_id, supplier_name, supplier_site, created_at, supplier_qualification_assessment_id);
        CREATE TRIGGER IF NOT EXISTS supplier_qualification_assessments_immutable_update
        BEFORE UPDATE ON supplier_qualification_assessments
        BEGIN SELECT RAISE(ABORT, 'supplier_qualification_assessments are immutable'); END;
        CREATE TRIGGER IF NOT EXISTS supplier_qualification_assessments_immutable_delete
        BEFORE DELETE ON supplier_qualification_assessments
        BEGIN SELECT RAISE(ABORT, 'supplier_qualification_assessments are immutable'); END;
        """
    )
    connection.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (10)")


def initialize_database(database: Database) -> int:
    v9.initialize_database(database)
    with database.transaction() as connection:
        applied = {
            int(row[0])
            for row in connection.execute("SELECT version FROM schema_migrations").fetchall()
        }
        if 10 not in applied:
            _apply_v10(connection)
    return SCHEMA_VERSION


def current_schema_version(database: Database) -> int:
    with database.connect() as connection:
        row = connection.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
        return int(row[0] or 0)
