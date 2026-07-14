from __future__ import annotations

"""Ordered, additive SQLite schema migrations for PVE."""

from sqlite3 import Connection

from src.persistence.database import Database

SCHEMA_VERSION = 4

_BASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    project_code TEXT NOT NULL UNIQUE,
    project_name TEXT NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    currency TEXT NOT NULL,
    annual_volume REAL NOT NULL CHECK (annual_volume > 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    archived_at TEXT
);
CREATE TABLE IF NOT EXISTS project_datasets (
    dataset_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    version_number INTEGER NOT NULL CHECK (version_number > 0),
    source_type TEXT NOT NULL,
    original_filename TEXT,
    canonical_json TEXT NOT NULL,
    validation_status TEXT NOT NULL,
    validation_issues_json TEXT NOT NULL DEFAULT '[]',
    content_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
    UNIQUE (project_id, version_number),
    UNIQUE (project_id, content_hash)
);
CREATE TABLE IF NOT EXISTS threshold_profiles (
    threshold_profile_id TEXT PRIMARY KEY,
    project_id TEXT,
    profile_name TEXT NOT NULL,
    version_number INTEGER NOT NULL CHECK (version_number > 0),
    profile_json TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
    UNIQUE (project_id, profile_name, version_number)
);
CREATE TABLE IF NOT EXISTS scenarios (
    scenario_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    dataset_id TEXT NOT NULL,
    threshold_profile_id TEXT,
    scenario_name TEXT NOT NULL,
    assumptions_json TEXT NOT NULL,
    results_json TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
    FOREIGN KEY (dataset_id) REFERENCES project_datasets(dataset_id) ON DELETE RESTRICT,
    FOREIGN KEY (threshold_profile_id) REFERENCES threshold_profiles(threshold_profile_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS decision_snapshots (
    decision_snapshot_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    dataset_id TEXT NOT NULL,
    threshold_profile_id TEXT,
    status TEXT NOT NULL,
    preferred_alternative_id TEXT,
    recommendation_json TEXT NOT NULL,
    gate_results_json TEXT NOT NULL,
    engine_version TEXT NOT NULL,
    source_commit TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE RESTRICT,
    FOREIGN KEY (dataset_id) REFERENCES project_datasets(dataset_id) ON DELETE RESTRICT,
    FOREIGN KEY (threshold_profile_id) REFERENCES threshold_profiles(threshold_profile_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS export_records (
    export_id TEXT PRIMARY KEY,
    decision_snapshot_id TEXT NOT NULL,
    export_type TEXT NOT NULL,
    filename TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    generated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (decision_snapshot_id) REFERENCES decision_snapshots(decision_snapshot_id) ON DELETE RESTRICT
);
CREATE TRIGGER IF NOT EXISTS project_datasets_immutable_update BEFORE UPDATE ON project_datasets BEGIN SELECT RAISE(ABORT, 'project_datasets are immutable'); END;
CREATE TRIGGER IF NOT EXISTS project_datasets_immutable_delete BEFORE DELETE ON project_datasets BEGIN SELECT RAISE(ABORT, 'project_datasets are immutable'); END;
CREATE TRIGGER IF NOT EXISTS threshold_profiles_immutable_update BEFORE UPDATE ON threshold_profiles BEGIN SELECT RAISE(ABORT, 'threshold_profiles are immutable'); END;
CREATE TRIGGER IF NOT EXISTS threshold_profiles_immutable_delete BEFORE DELETE ON threshold_profiles BEGIN SELECT RAISE(ABORT, 'threshold_profiles are immutable'); END;
CREATE TRIGGER IF NOT EXISTS scenarios_immutable_update BEFORE UPDATE ON scenarios BEGIN SELECT RAISE(ABORT, 'scenarios are immutable'); END;
CREATE TRIGGER IF NOT EXISTS scenarios_immutable_delete BEFORE DELETE ON scenarios BEGIN SELECT RAISE(ABORT, 'scenarios are immutable'); END;
CREATE TRIGGER IF NOT EXISTS decision_snapshots_immutable_update BEFORE UPDATE ON decision_snapshots BEGIN SELECT RAISE(ABORT, 'decision_snapshots are immutable'); END;
CREATE TRIGGER IF NOT EXISTS decision_snapshots_immutable_delete BEFORE DELETE ON decision_snapshots BEGIN SELECT RAISE(ABORT, 'decision_snapshots are immutable'); END;
"""

_PROJECT_V2_COLUMNS: dict[str, str] = {
    "objective": "TEXT", "change_type": "TEXT", "product_sku": "TEXT",
    "business_unit_plant": "TEXT", "project_owner": "TEXT", "volume_unit": "TEXT",
    "current_unit_cost": "REAL", "proposed_unit_cost": "REAL",
    "current_supplier": "TEXT", "proposed_supplier": "TEXT", "target_saving": "REAL",
    "target_completion_date": "TEXT", "implementation_cost": "REAL", "testing_cost": "REAL",
    "tooling_cost": "REAL", "qualification_cost": "REAL",
    "expected_realization_percent": "REAL", "project_description": "TEXT",
    "business_justification": "TEXT", "sustainability_objective": "TEXT",
}


def _column_names(connection: Connection, table: str) -> set[str]:
    return {str(row[1]) for row in connection.execute(f"PRAGMA table_info({table})")}


def _apply_v2(connection: Connection) -> None:
    existing = _column_names(connection, "projects")
    for name, declaration in _PROJECT_V2_COLUMNS.items():
        if name not in existing:
            connection.execute(f"ALTER TABLE projects ADD COLUMN {name} {declaration}")
    connection.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (2)")


def _apply_v3(connection: Connection) -> None:
    connection.executescript("""
    CREATE TABLE IF NOT EXISTS readiness_assessments (
        readiness_assessment_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        dataset_id TEXT,
        score_percent REAL NOT NULL CHECK (score_percent >= 0 AND score_percent <= 100),
        stage TEXT NOT NULL,
        assessment_json TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
        FOREIGN KEY (dataset_id) REFERENCES project_datasets(dataset_id) ON DELETE RESTRICT
    );
    CREATE TRIGGER IF NOT EXISTS readiness_assessments_immutable_update
    BEFORE UPDATE ON readiness_assessments BEGIN SELECT RAISE(ABORT, 'readiness_assessments are immutable'); END;
    CREATE TRIGGER IF NOT EXISTS readiness_assessments_immutable_delete
    BEFORE DELETE ON readiness_assessments BEGIN SELECT RAISE(ABORT, 'readiness_assessments are immutable'); END;
    """)
    connection.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (3)")


def _apply_v4(connection: Connection) -> None:
    connection.executescript("""
    CREATE TABLE IF NOT EXISTS technical_assessments (
        technical_assessment_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        readiness_assessment_id TEXT,
        dataset_id TEXT NOT NULL,
        dataset_version INTEGER NOT NULL CHECK (dataset_version > 0),
        baseline_specification_version TEXT NOT NULL,
        proposed_specification_version TEXT NOT NULL,
        rule_set_version TEXT NOT NULL,
        threshold_profile_id TEXT,
        threshold_references_json TEXT NOT NULL DEFAULT '[]',
        evidence_references_json TEXT NOT NULL DEFAULT '[]',
        formula_inputs_json TEXT NOT NULL DEFAULT '{}',
        assumptions_json TEXT NOT NULL DEFAULT '[]',
        technical_outcomes_json TEXT NOT NULL DEFAULT '{}',
        commercial_outcomes_json TEXT NOT NULL DEFAULT '{}',
        blockers_json TEXT NOT NULL DEFAULT '[]',
        required_trials_json TEXT NOT NULL DEFAULT '[]',
        evidence_confidence_status TEXT NOT NULL,
        recommendation_outcome TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
        FOREIGN KEY (readiness_assessment_id) REFERENCES readiness_assessments(readiness_assessment_id) ON DELETE RESTRICT,
        FOREIGN KEY (dataset_id) REFERENCES project_datasets(dataset_id) ON DELETE RESTRICT,
        FOREIGN KEY (threshold_profile_id) REFERENCES threshold_profiles(threshold_profile_id) ON DELETE RESTRICT
    );
    CREATE INDEX IF NOT EXISTS idx_technical_assessments_project
    ON technical_assessments(project_id, created_at, technical_assessment_id);
    CREATE TRIGGER IF NOT EXISTS technical_assessments_immutable_update
    BEFORE UPDATE ON technical_assessments BEGIN SELECT RAISE(ABORT, 'technical_assessments are immutable'); END;
    CREATE TRIGGER IF NOT EXISTS technical_assessments_immutable_delete
    BEFORE DELETE ON technical_assessments BEGIN SELECT RAISE(ABORT, 'technical_assessments are immutable'); END;
    """)
    connection.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (4)")


def initialize_database(database: Database) -> int:
    with database.transaction() as connection:
        connection.executescript(_BASE_SCHEMA)
        connection.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (1)")
        applied = {int(row[0]) for row in connection.execute("SELECT version FROM schema_migrations").fetchall()}
        if 2 not in applied:
            _apply_v2(connection)
        if 3 not in applied:
            _apply_v3(connection)
        if 4 not in applied:
            _apply_v4(connection)
    return SCHEMA_VERSION


def current_schema_version(database: Database) -> int:
    with database.connect() as connection:
        row = connection.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
        return int(row[0] or 0)
