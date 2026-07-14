from __future__ import annotations

import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.persistence import ComplaintRecordRepository, Database, DefectClassificationRepository
from src.persistence import migrations
from src.persistence.migrations import SCHEMA_VERSION, current_schema_version, initialize_database


class Build5TaxonomyPersistenceTests(unittest.TestCase):
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
        self.defects = DefectClassificationRepository(self.database)
        self.complaints = ComplaintRecordRepository(self.database)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def create_defect(self, **overrides):
        values = {
            "project_id": "project-a",
            "taxonomy_version": "PVE-DEFECT-1.0",
            "defect_code": "CORR-STRUCT-CRUSH",
            "packaging_level": "transport",
            "material_family": "corrugated",
            "defect_family": "structural",
            "defect_mode": "edge_crush",
            "description": "Case edge is visibly crushed.",
            "severity": "major",
            "occurrence_stage": "transport",
            "review_status": "reviewed",
            "reviewed_by": "Packaging Quality Manager",
            "evidence_references": ["PHOTO-001"],
            "content_hash": self.digest("DEFECT-001"),
        }
        values.update(overrides)
        return self.defects.create(**values)

    def create_complaint(self, **overrides):
        values = {
            "project_id": "project-a",
            "complaint_reference": "COMP-001",
            "complaint_source": "customer",
            "received_date": "2026-08-10",
            "description": "Customer reported crushed transport cases.",
            "containment_status": "in_progress",
            "review_status": "reviewed",
            "reviewed_by": "Customer Quality Manager",
            "taxonomy_version": "PVE-DEFECT-1.0",
            "evidence_references": ["CUSTOMER-PHOTO-001"],
            "content_hash": self.digest("COMP-001"),
        }
        values.update(overrides)
        return self.complaints.create(**values)

    def test_schema_v8_remains_present_under_governed_schema(self) -> None:
        self.assertGreaterEqual(SCHEMA_VERSION, 8)
        self.assertEqual(current_schema_version(self.database), SCHEMA_VERSION)

    def test_additive_migration_from_v7_to_v8(self) -> None:
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
                migrations._apply_v7(connection)
            self.assertEqual(current_schema_version(database), 7)
            with database.transaction() as connection:
                migrations._apply_v8(connection)
            self.assertEqual(current_schema_version(database), 8)

    def test_create_read_and_list_preserve_taxonomy_evidence_and_review(self) -> None:
        defect = self.create_defect()
        complaint = self.create_complaint(
            linked_defect_classification_ids=[defect["defect_classification_id"]]
        )
        self.assertEqual(defect["taxonomy_version"], "PVE-DEFECT-1.0")
        self.assertEqual(defect["evidence_references"], ["PHOTO-001"])
        self.assertEqual(defect["reviewed_by"], "Packaging Quality Manager")
        self.assertEqual(
            complaint["linked_defect_classification_ids"],
            [defect["defect_classification_id"]],
        )
        self.assertEqual(self.defects.list_for_project("project-a"), [defect])
        self.assertEqual(self.complaints.list_for_project("project-a"), [complaint])

    def test_archived_project_is_read_only(self) -> None:
        with self.database.transaction() as connection:
            connection.execute("UPDATE projects SET archived_at = CURRENT_TIMESTAMP WHERE project_id = 'project-a'")
        with self.assertRaisesRegex(ValueError, "read-only"):
            self.create_defect()
        with self.assertRaisesRegex(ValueError, "read-only"):
            self.create_complaint()

    def test_cross_project_defect_link_is_rejected(self) -> None:
        defect = self.create_defect(
            project_id="project-b",
            defect_code="CORR-STRUCT-B",
            content_hash=self.digest("DEFECT-B"),
        )
        with self.assertRaisesRegex(ValueError, "same project"):
            self.create_complaint(
                linked_defect_classification_ids=[defect["defect_classification_id"]]
            )

    def test_repository_and_database_immutability(self) -> None:
        defect = self.create_defect()
        complaint = self.create_complaint()
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.defects.update(defect["defect_classification_id"])
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.complaints.delete(complaint["complaint_record_id"])
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE defect_classifications SET severity = 'minor' WHERE defect_classification_id = ?",
                    (defect["defect_classification_id"],),
                )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "DELETE FROM complaint_records WHERE complaint_record_id = ?",
                    (complaint["complaint_record_id"],),
                )

    def test_reviewed_records_require_evidence_and_human_review(self) -> None:
        with self.assertRaisesRegex(ValueError, "evidence"):
            self.create_defect(evidence_references=[])
        with self.assertRaisesRegex(ValueError, "reviewed_by"):
            self.create_complaint(reviewed_by="")

    def test_build6_and_later_decisions_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Build 6"):
            self.create_defect(specification_change_status="approved")
        with self.assertRaisesRegex(ValueError, "Build 6"):
            self.create_complaint(supplier_qualification_status="approved")


if __name__ == "__main__":
    unittest.main()
