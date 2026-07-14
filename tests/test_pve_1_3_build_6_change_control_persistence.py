from __future__ import annotations

import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.persistence import Database, ImplementationControlRepository, SpecificationChangeRepository
from src.persistence import migrations
from src.persistence.migrations import SCHEMA_VERSION, current_schema_version, initialize_database


class Build6ChangeControlPersistenceTests(unittest.TestCase):
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
        self.changes = SpecificationChangeRepository(self.database)
        self.implementations = ImplementationControlRepository(self.database)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def create_change(self, **overrides):
        values = {
            "project_id": "project-a",
            "change_code": "CHG-001",
            "change_type": "specification",
            "title": "Increase board strength",
            "rationale": "Validated transport damage reduction.",
            "current_specification_version": "SPEC-1",
            "proposed_specification_version": "SPEC-2",
            "review_status": "reviewed",
            "approval_status": "approved",
            "requested_by": "Packaging Engineer",
            "requested_effective_date": "2026-09-15",
            "evidence_references": ["TRIAL-REPORT-001"],
            "approved_by": "Packaging Director",
            "approval_reference": "CAB-001",
            "approved_at": "2026-09-01",
            "content_hash": self.digest("CHG-001"),
        }
        values.update(overrides)
        return self.changes.create(**values)

    def create_implementation(self, change_request_id: str, **overrides):
        values = {
            "project_id": "project-a",
            "change_request_id": change_request_id,
            "implementation_code": "IMP-001",
            "implementation_site": "Plant A",
            "implementation_owner": "Plant Packaging Lead",
            "implementation_status": "implemented",
            "planned_implementation_date": "2026-09-15",
            "actual_implementation_date": "2026-09-16",
            "verification_status": "verified",
            "evidence_references": ["LINE-TRIAL-001", "FIRST-RUN-001"],
            "authorized_by": "Operations Director",
            "authorization_reference": "AUTH-001",
            "verified_by": "Quality Manager",
            "verified_at": "2026-09-17",
            "content_hash": self.digest("IMP-001"),
        }
        values.update(overrides)
        return self.implementations.create(**values)

    def test_schema_v9_is_applied(self) -> None:
        self.assertEqual(SCHEMA_VERSION, 9)
        self.assertEqual(current_schema_version(self.database), 9)

    def test_additive_migration_from_v8_to_v9(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            database = Database(Path(tempdir) / "migration.db")
            with database.transaction() as connection:
                connection.executescript(migrations._BASE_SCHEMA)
                connection.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (1)")
                for migration in (
                    migrations._apply_v2, migrations._apply_v3, migrations._apply_v4,
                    migrations._apply_v5, migrations._apply_v6, migrations._apply_v7,
                    migrations._apply_v8,
                ):
                    migration(connection)
            self.assertEqual(current_schema_version(database), 8)
            self.assertEqual(initialize_database(database), 9)
            self.assertEqual(current_schema_version(database), 9)

    def test_create_read_and_list_preserve_versions_approval_and_effective_date(self) -> None:
        change = self.create_change()
        implementation = self.create_implementation(change["specification_change_request_id"])
        self.assertEqual(change["current_specification_version"], "SPEC-1")
        self.assertEqual(change["proposed_specification_version"], "SPEC-2")
        self.assertEqual(change["requested_effective_date"], "2026-09-15")
        self.assertEqual(change["approved_by"], "Packaging Director")
        self.assertEqual(change["evidence_references"], ["TRIAL-REPORT-001"])
        self.assertEqual(implementation["verified_by"], "Quality Manager")
        self.assertEqual(self.changes.list_for_project("project-a"), [change])
        self.assertEqual(self.implementations.list_for_project("project-a"), [implementation])

    def test_approved_change_is_required_for_implementation_authorization(self) -> None:
        pending = self.create_change(
            change_code="CHG-PENDING",
            approval_status="pending",
            approved_by=None,
            approval_reference=None,
            approved_at=None,
            content_hash=self.digest("CHG-PENDING"),
        )
        with self.assertRaisesRegex(ValueError, "approved change request"):
            self.create_implementation(
                pending["specification_change_request_id"],
                implementation_code="IMP-PENDING",
                content_hash=self.digest("IMP-PENDING"),
            )

    def test_archived_project_is_read_only(self) -> None:
        with self.database.transaction() as connection:
            connection.execute("UPDATE projects SET archived_at = CURRENT_TIMESTAMP WHERE project_id = 'project-a'")
        with self.assertRaisesRegex(ValueError, "read-only"):
            self.create_change()

    def test_cross_project_trial_defect_and_complaint_links_are_rejected(self) -> None:
        with self.database.transaction() as connection:
            connection.execute(
                "INSERT INTO defect_classifications(defect_classification_id, project_id, taxonomy_version, defect_code, packaging_level, material_family, defect_family, defect_mode, description, severity, occurrence_stage, review_status, reviewed_by, content_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("defect-b", "project-b", "1", "D-B", "secondary", "corrugated", "structural", "crush", "Crush", "major", "transport", "reviewed", "Reviewer", self.digest("defect-b")),
            )
        with self.assertRaisesRegex(ValueError, "same project"):
            self.create_change(linked_defect_classification_ids=["defect-b"])

    def test_repository_and_database_immutability(self) -> None:
        change = self.create_change()
        implementation = self.create_implementation(change["specification_change_request_id"])
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.changes.update(change["specification_change_request_id"])
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.implementations.delete(implementation["implementation_control_id"])
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE specification_change_requests SET approval_status = 'rejected' WHERE specification_change_request_id = ?",
                    (change["specification_change_request_id"],),
                )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "DELETE FROM implementation_controls WHERE implementation_control_id = ?",
                    (implementation["implementation_control_id"],),
                )

    def test_build7_supplier_and_sourcing_decisions_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Build 7"):
            self.create_change(supplier_qualification_status="qualified")
        change = self.create_change()
        with self.assertRaisesRegex(ValueError, "Build 7"):
            self.create_implementation(
                change["specification_change_request_id"],
                implementation_code="IMP-002",
                content_hash=self.digest("IMP-002"),
                sourcing_award_status="awarded",
            )


if __name__ == "__main__":
    unittest.main()
