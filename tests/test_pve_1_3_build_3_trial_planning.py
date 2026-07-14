from __future__ import annotations

import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.persistence import Database, TrialPlanRepository
from src.persistence.migrations import SCHEMA_VERSION, current_schema_version, initialize_database
from src.trial_planning import validate_trial_plan


class TrialPlanningBuild3Tests(unittest.TestCase):
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
            for project_id, evidence_id, number in (
                ("project-a", "drawing-a", "DRW-A"),
                ("project-b", "drawing-b", "DRW-B"),
            ):
                connection.execute(
                    """
                    INSERT INTO drawing_evidence(
                        drawing_evidence_id, project_id, document_type, document_number, title,
                        revision, classification, file_format, source_reference,
                        source_classification, validation_status, approval_status, content_hash
                    ) VALUES (?, ?, 'drawing', ?, 'Drawing', 'A', 'proposed', 'pdf', ?,
                              'uploaded_fact', 'validated', 'approval_required', ?)
                    """,
                    (evidence_id, project_id, number, f"controlled://{number}.pdf", self.digest(evidence_id)),
                )
        self.repository = TrialPlanRepository(self.database)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def create_plan(self, **overrides):
        values = {
            "project_id": "project-a",
            "trial_code": "TRIAL-001",
            "title": "Compression validation trial",
            "objective": "Validate proposed case performance against agreed requirements.",
            "protocol": "Condition samples, test compression, inspect damage, retain evidence.",
            "owner": "Packaging Engineer",
            "trial_site": "Plant A",
            "planned_start_date": "2026-08-01",
            "planned_end_date": "2026-08-02",
            "status": "ready_for_authorization",
            "authorization_status": "pending",
            "acceptance_criteria": [{
                "criterion_id": "ECT-01", "criterion_type": "numeric",
                "description": "Compression strength", "operator": ">=",
                "target": 500, "unit": "N", "evidence_required": "calibrated test report",
            }],
            "drawing_evidence_ids": ["drawing-a"],
            "specification_versions": ["SPEC-PROP-2"],
            "evidence_requirements": [{"type": "test_report", "owner": "laboratory"}],
            "prerequisites": ["approved protocol", "calibrated equipment"],
            "blockers": [],
            "content_hash": self.digest("TRIAL-001"),
        }
        values.update(overrides)
        return self.repository.create(**values)

    def test_schema_v6_is_applied(self) -> None:
        self.assertEqual(SCHEMA_VERSION, 6)
        self.assertEqual(current_schema_version(self.database), 6)

    def test_create_and_read_project_scoped_plan(self) -> None:
        plan = self.create_plan()
        self.assertEqual(plan["trial_code"], "TRIAL-001")
        self.assertEqual(plan["drawing_evidence_ids"], ["drawing-a"])
        self.assertEqual(self.repository.list_for_project("project-a"), [plan])

    def test_cross_project_drawing_evidence_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "same project"):
            self.create_plan(drawing_evidence_ids=["drawing-b"])

    def test_archived_project_is_read_only(self) -> None:
        with self.database.transaction() as connection:
            connection.execute("UPDATE projects SET archived_at = CURRENT_TIMESTAMP WHERE project_id = 'project-a'")
        with self.assertRaisesRegex(ValueError, "read-only"):
            self.create_plan()

    def test_plan_is_immutable_in_repository_and_database(self) -> None:
        plan = self.create_plan()
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.repository.update(plan["trial_plan_id"])
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE trial_plans SET title = 'Changed' WHERE trial_plan_id = ?",
                    (plan["trial_plan_id"],),
                )

    def test_human_authorization_is_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "explicit human authorization"):
            self.create_plan(status="authorized", authorization_status="pending")
        with self.assertRaisesRegex(ValueError, "Human authorizer identity"):
            self.create_plan(status="authorized", authorization_status="authorized")
        plan = self.create_plan(
            status="authorized", authorization_status="authorized",
            authorized_by="Engineering Manager", authorization_reference="AUTH-001",
        )
        self.assertEqual(plan["authorized_by"], "Engineering Manager")

    def test_measurable_acceptance_criteria_are_required(self) -> None:
        invalid = self.create_plan
        with self.assertRaisesRegex(ValueError, "Numeric criteria require a unit"):
            invalid(acceptance_criteria=[{
                "criterion_id": "C-1", "criterion_type": "numeric",
                "description": "Compression", "operator": ">=", "target": 500,
                "evidence_required": "test report",
            }])

    def test_execution_and_result_data_are_prohibited(self) -> None:
        result = validate_trial_plan({
            "project_id": "project-a", "trial_code": "T", "title": "T",
            "objective": "O", "protocol": "P", "owner": "Owner", "trial_site": "Site",
            "planned_start_date": "2026-08-01", "planned_end_date": "2026-08-02",
            "status": "draft", "authorization_status": "not_requested",
            "acceptance_criteria": [{
                "criterion_id": "C", "criterion_type": "boolean", "description": "No damage",
                "evidence_required": "inspection checklist",
            }],
            "content_hash": self.digest("T"), "results": {"passed": True},
        })
        self.assertIn("execution_data_prohibited", {issue.code for issue in result.issues})


if __name__ == "__main__":
    unittest.main()
