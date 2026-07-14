from __future__ import annotations

import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.persistence import Database, SupplierQualificationRepository
from src.persistence import migrations
from src.persistence.migrations_v10 import (
    SCHEMA_VERSION,
    current_schema_version,
    initialize_database,
)


class Build7SupplierQualificationPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.temp_dir.name) / "pve.db")
        initialize_database(self.database)
        with self.database.transaction() as connection:
            for project_id, code in (("project-a", "P-A"), ("project-b", "P-B")):
                connection.execute(
                    "INSERT INTO projects(project_id, project_code, project_name, category, currency, annual_volume) VALUES (?, ?, ?, ?, ?, ?)",
                    (project_id, code, project_id, "corrugated", "INR", 1000),
                )
        self.repository = SupplierQualificationRepository(self.database)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def create_assessment(self, **overrides):
        values = {
            "project_id": "project-a",
            "qualification_code": "QUAL-001",
            "supplier_name": "Supplier A",
            "supplier_site": "Plant A",
            "qualification_scope": "Corrugated shipper for SKU family A",
            "assessment_type": "initial",
            "assessment_date": "2026-10-01",
            "qualification_status": "conditionally_qualified",
            "valid_from": "2026-10-01",
            "valid_until": "2027-09-30",
            "review_date": "2027-06-30",
            "conditions": ["Close moisture-control action"],
            "open_actions": ["Submit monthly humidity records"],
            "evidence_references": ["AUDIT-001", "TRIAL-001"],
            "assessed_by": "Supplier Quality Engineer",
            "approved_by": "Procurement Quality Director",
            "approval_reference": "SQ-BOARD-001",
            "approved_at": "2026-10-02",
            "decision_rationale": "Scope-specific evidence supports conditional qualification.",
            "content_hash": self.digest("QUAL-001"),
        }
        values.update(overrides)
        return self.repository.create(**values)

    def test_schema_v10_is_applied(self) -> None:
        self.assertEqual(SCHEMA_VERSION, 10)
        self.assertEqual(current_schema_version(self.database), 10)

    def test_additive_migration_from_v9_to_v10(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            database = Database(Path(tempdir) / "migration.db")
            self.assertEqual(migrations.initialize_database(database), 9)
            self.assertEqual(current_schema_version(database), 9)
            self.assertEqual(initialize_database(database), 10)
            self.assertEqual(current_schema_version(database), 10)

    def test_create_read_and_list_preserve_scope_status_dates_conditions_and_approval(self) -> None:
        assessment = self.create_assessment()
        self.assertEqual(assessment["supplier_name"], "Supplier A")
        self.assertEqual(assessment["supplier_site"], "Plant A")
        self.assertIn("Corrugated", assessment["qualification_scope"])
        self.assertEqual(assessment["qualification_status"], "conditionally_qualified")
        self.assertEqual(assessment["valid_until"], "2027-09-30")
        self.assertEqual(assessment["conditions"], ["Close moisture-control action"])
        self.assertEqual(assessment["approved_by"], "Procurement Quality Director")
        self.assertEqual(assessment["evidence_references"], ["AUDIT-001", "TRIAL-001"])
        self.assertEqual(self.repository.list_for_project("project-a"), [assessment])

    def test_archived_project_is_read_only(self) -> None:
        with self.database.transaction() as connection:
            connection.execute("UPDATE projects SET archived_at = CURRENT_TIMESTAMP WHERE project_id = 'project-a'")
        with self.assertRaisesRegex(ValueError, "read-only"):
            self.create_assessment()

    def test_cross_project_evidence_links_are_rejected(self) -> None:
        with self.database.transaction() as connection:
            connection.execute(
                "INSERT INTO defect_classifications(defect_classification_id, project_id, taxonomy_version, defect_code, packaging_level, material_family, defect_family, defect_mode, description, severity, occurrence_stage, review_status, reviewed_by, content_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("defect-b", "project-b", "1", "D-B", "secondary", "corrugated", "structural", "crush", "Crush", "major", "transport", "reviewed", "Reviewer", self.digest("defect-b")),
            )
        with self.assertRaisesRegex(ValueError, "same project"):
            self.create_assessment(linked_defect_classification_ids=["defect-b"])

    def test_repository_and_database_immutability(self) -> None:
        assessment = self.create_assessment()
        identifier = assessment["supplier_qualification_assessment_id"]
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.repository.update(identifier)
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.repository.delete(identifier)
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE supplier_qualification_assessments SET qualification_status = 'qualified' WHERE supplier_qualification_assessment_id = ?",
                    (identifier,),
                )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "DELETE FROM supplier_qualification_assessments WHERE supplier_qualification_assessment_id = ?",
                    (identifier,),
                )

    def test_build8_release_sourcing_and_commercial_fields_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Build 8"):
            self.create_assessment(release_certification_status="certified")
        with self.assertRaisesRegex(ValueError, "Build 8"):
            self.create_assessment(
                qualification_code="QUAL-002",
                content_hash=self.digest("QUAL-002"),
                sourcing_award_status="awarded",
            )
        with self.assertRaisesRegex(ValueError, "Build 8"):
            self.create_assessment(
                qualification_code="QUAL-003",
                content_hash=self.digest("QUAL-003"),
                commercial_terms_approval="approved",
            )


if __name__ == "__main__":
    unittest.main()
