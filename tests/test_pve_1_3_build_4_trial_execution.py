from __future__ import annotations

import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.persistence import Database, TrialExecutionRepository
from src.persistence import migrations
from src.persistence.migrations import SCHEMA_VERSION, current_schema_version, initialize_database
from src.trial_execution import validate_trial_execution


class TrialExecutionBuild4Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.temp_dir.name) / "pve.db")
        initialize_database(self.database)
        with self.database.transaction() as connection:
            connection.execute(
                "INSERT INTO projects(project_id, project_code, project_name, category, currency, annual_volume) VALUES (?, ?, ?, ?, ?, ?)",
                ("project-a", "P-A", "Project A", "corrugated", "INR", 1000),
            )
            connection.execute(
                "INSERT INTO projects(project_id, project_code, project_name, category, currency, annual_volume) VALUES (?, ?, ?, ?, ?, ?)",
                ("project-b", "P-B", "Project B", "corrugated", "INR", 1000),
            )
            for project_id, plan_id, trial_code, status, auth in (
                ("project-a", "plan-a", "TRIAL-A", "authorized", "authorized"),
                ("project-a", "plan-pending", "TRIAL-P", "ready_for_authorization", "pending"),
                ("project-b", "plan-b", "TRIAL-B", "authorized", "authorized"),
            ):
                connection.execute(
                    """
                    INSERT INTO trial_plans(
                        trial_plan_id, project_id, trial_code, title, objective, protocol,
                        owner, trial_site, planned_start_date, planned_end_date, status,
                        authorization_status, authorized_by, acceptance_criteria_json, content_hash
                    ) VALUES (?, ?, ?, 'Trial', 'Objective', 'Protocol', 'Engineer', 'Site',
                              '2026-08-01', '2026-08-02', ?, ?, 'Manager', '[]', ?)
                    """,
                    (plan_id, project_id, trial_code, status, auth, self.digest(plan_id)),
                )
        self.repository = TrialExecutionRepository(self.database)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def create_execution(self, **overrides):
        values = {
            "project_id": "project-a",
            "trial_plan_id": "plan-a",
            "execution_code": "EXEC-001",
            "started_at": "2026-08-01T09:00:00",
            "completed_at": "2026-08-01T12:00:00",
            "performed_by": "Lab Technician",
            "trial_site": "Plant A",
            "status": "completed",
            "outcome": "pass",
            "measurements": [{
                "criterion_id": "BCT-01", "result_type": "numeric",
                "value": 1250, "unit": "N", "evidence_reference": "LAB-REPORT-001",
            }],
            "evidence_references": ["LAB-REPORT-001"],
            "deviations": [],
            "reviewed_by": "Packaging Engineer",
            "content_hash": self.digest("EXEC-001"),
        }
        values.update(overrides)
        return self.repository.create(**values)

    def test_governed_schema_version_is_applied(self) -> None:
        self.assertEqual(current_schema_version(self.database), SCHEMA_VERSION)

    def test_additive_migration_from_v6_to_v7(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            database = Database(Path(tempdir) / "migration.db")
            with database.transaction() as connection:
                connection.executescript(migrations._BASE_SCHEMA)
                connection.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (1)")
                migrations._apply_v2(connection)
                migrations._apply_v3(connection)
                migrations._apply_v4(connection)
                migrations._apply_v5(connection)
                migrations._apply_v6(connection)
            self.assertEqual(current_schema_version(database), 6)
            self.assertEqual(initialize_database(database), SCHEMA_VERSION)
            self.assertEqual(current_schema_version(database), SCHEMA_VERSION)

    def test_create_and_read_project_scoped_execution(self) -> None:
        record = self.create_execution()
        self.assertEqual(record["outcome"], "pass")
        self.assertEqual(record["measurements"][0]["value"], 1250)
        self.assertEqual(self.repository.list_for_project("project-a"), [record])
        self.assertEqual(self.repository.list_for_plan("plan-a"), [record])

    def test_authorized_plan_is_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "explicitly authorized"):
            self.create_execution(trial_plan_id="plan-pending")

    def test_cross_project_plan_and_archived_project_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "same project"):
            self.create_execution(trial_plan_id="plan-b")
        with self.database.transaction() as connection:
            connection.execute("UPDATE projects SET archived_at = CURRENT_TIMESTAMP WHERE project_id = 'project-a'")
        with self.assertRaisesRegex(ValueError, "read-only"):
            self.create_execution()

    def test_execution_is_immutable_in_repository_and_database(self) -> None:
        record = self.create_execution()
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.repository.update(record["trial_execution_id"])
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE trial_executions SET outcome = 'fail' WHERE trial_execution_id = ?",
                    (record["trial_execution_id"],),
                )

    def test_measurement_evidence_reviewer_and_deviation_controls(self) -> None:
        with self.assertRaisesRegex(ValueError, "evidence_reference"):
            self.create_execution(measurements=[{
                "criterion_id": "BCT-01", "result_type": "numeric", "value": 1250, "unit": "N",
            }])
        with self.assertRaisesRegex(ValueError, "reviewed_by"):
            self.create_execution(reviewed_by="")
        record = self.create_execution(
            deviations=[{
                "deviation_id": "DEV-01", "description": "Conditioning time reduced",
                "severity": "minor", "impact_assessment": "Result remains reviewable",
                "owner": "Lab Lead", "disposition_status": "accepted",
            }]
        )
        self.assertEqual(record["deviations"][0]["deviation_id"], "DEV-01")

    def test_build5_and_later_fields_are_prohibited(self) -> None:
        result = validate_trial_execution({
            "project_id": "project-a", "trial_plan_id": "plan-a", "execution_code": "E",
            "started_at": "2026-08-01T09:00:00", "completed_at": "2026-08-01T10:00:00",
            "performed_by": "Tech", "trial_site": "Site", "status": "completed",
            "outcome": "pass", "measurements": [{
                "criterion_id": "C", "result_type": "boolean", "value": True,
                "evidence_reference": "CHECKLIST-1",
            }],
            "reviewed_by": "Reviewer", "content_hash": self.digest("E"),
            "defect_category": "crush", "supplier_qualification_status": "approved",
        })
        self.assertIn("build5_data_prohibited", {issue.code for issue in result.issues})


if __name__ == "__main__":
    unittest.main()
