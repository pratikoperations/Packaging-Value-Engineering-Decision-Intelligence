from __future__ import annotations

"""Additive schema v11 for Build 8 demonstration cases and release-QA evidence."""

from sqlite3 import Connection

from src.persistence.database import Database
from src.persistence import migrations_v10 as v10

SCHEMA_VERSION = 11


def _apply_v11(connection: Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS demonstration_cases (
            demonstration_case_id TEXT PRIMARY KEY,
            case_code TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            purpose TEXT NOT NULL,
            data_classification TEXT NOT NULL CHECK (data_classification IN ('synthetic', 'anonymized', 'real_controlled')),
            covered_builds_json TEXT NOT NULL DEFAULT '[]',
            expected_outcomes_json TEXT NOT NULL DEFAULT '[]',
            acceptance_checks_json TEXT NOT NULL DEFAULT '[]',
            status TEXT NOT NULL CHECK (status IN ('draft', 'ready', 'executed', 'passed', 'failed', 'blocked')),
            evidence_references_json TEXT NOT NULL DEFAULT '[]',
            limitations_json TEXT NOT NULL DEFAULT '[]',
            exceptions_json TEXT NOT NULL DEFAULT '[]',
            content_hash TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS release_qa_assessments (
            release_qa_assessment_id TEXT PRIMARY KEY,
            assessment_code TEXT NOT NULL UNIQUE,
            tested_commit TEXT NOT NULL,
            workflow_run_id TEXT NOT NULL,
            job_id TEXT NOT NULL,
            test_count INTEGER NOT NULL CHECK (test_count > 0),
            failure_count INTEGER NOT NULL CHECK (failure_count >= 0),
            error_count INTEGER NOT NULL CHECK (error_count >= 0),
            schema_version INTEGER NOT NULL CHECK (schema_version > 0),
            artifact_id TEXT NOT NULL,
            artifact_digest TEXT NOT NULL,
            demonstration_case_ids_json TEXT NOT NULL DEFAULT '[]',
            unresolved_defects_json TEXT NOT NULL DEFAULT '[]',
            limitations_json TEXT NOT NULL DEFAULT '[]',
            exceptions_json TEXT NOT NULL DEFAULT '[]',
            unresolved_blockers_json TEXT NOT NULL DEFAULT '[]',
            reviewed_by TEXT NOT NULL,
            reviewed_at TEXT NOT NULL,
            recommendation TEXT NOT NULL CHECK (recommendation IN ('not_ready', 'ready_for_release_authorization', 'blocked')),
            recommendation_rationale TEXT NOT NULL,
            evidence_references_json TEXT NOT NULL DEFAULT '[]',
            content_hash TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_demo_cases_status ON demonstration_cases(status, created_at, demonstration_case_id);
        CREATE INDEX IF NOT EXISTS idx_release_qa_commit ON release_qa_assessments(tested_commit, created_at, release_qa_assessment_id);
        CREATE TRIGGER IF NOT EXISTS demonstration_cases_immutable_update
        BEFORE UPDATE ON demonstration_cases BEGIN SELECT RAISE(ABORT, 'demonstration_cases are immutable'); END;
        CREATE TRIGGER IF NOT EXISTS demonstration_cases_immutable_delete
        BEFORE DELETE ON demonstration_cases BEGIN SELECT RAISE(ABORT, 'demonstration_cases are immutable'); END;
        CREATE TRIGGER IF NOT EXISTS release_qa_assessments_immutable_update
        BEFORE UPDATE ON release_qa_assessments BEGIN SELECT RAISE(ABORT, 'release_qa_assessments are immutable'); END;
        CREATE TRIGGER IF NOT EXISTS release_qa_assessments_immutable_delete
        BEFORE DELETE ON release_qa_assessments BEGIN SELECT RAISE(ABORT, 'release_qa_assessments are immutable'); END;
        """
    )
    connection.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (11)")


def initialize_database(database: Database) -> int:
    v10.initialize_database(database)
    with database.transaction() as connection:
        applied = {int(row[0]) for row in connection.execute("SELECT version FROM schema_migrations").fetchall()}
        if 11 not in applied:
            _apply_v11(connection)
    return SCHEMA_VERSION


def current_schema_version(database: Database) -> int:
    with database.connect() as connection:
        row = connection.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
        return int(row[0] or 0)
