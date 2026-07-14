from __future__ import annotations

import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.drawing_evidence import validate_drawing_evidence
from src.persistence import Database, DrawingEvidenceRepository
from src.persistence.migrations import SCHEMA_VERSION, current_schema_version, initialize_database


class DrawingEvidenceBuild2ATests(unittest.TestCase):
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
        self.repository = DrawingEvidenceRepository(self.database)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def create_record(self, **overrides):
        values = {
            "project_id": "project-a",
            "document_type": "drawing",
            "document_number": "DRW-001",
            "title": "RSC shipping case",
            "revision": "A",
            "classification": "baseline",
            "file_format": "pdf",
            "source_reference": "controlled://drawings/DRW-001-A.pdf",
            "source_classification": "uploaded_fact",
            "validation_status": "validation_required",
            "approval_status": "approval_required",
            "content_hash": self.digest("DRW-001-A"),
            "sku": "SKU-001",
            "supplier": "Supplier A",
            "manufacturing_site": "Site A",
            "specification_version": "SPEC-1",
            "issue_date": "2026-07-01",
            "effective_date": "2026-07-10",
        }
        values.update(overrides)
        return self.repository.create(**values)

    def test_current_governed_schema_is_applied(self) -> None:
        self.assertEqual(current_schema_version(self.database), SCHEMA_VERSION)

    def test_create_and_read_governed_record(self) -> None:
        record = self.create_record()
        self.assertEqual(record["document_number"], "DRW-001")
        self.assertFalse(record["geometry_interpreted"])
        self.assertEqual(self.repository.list_for_project("project-a"), [record])

    def test_superseding_revision_becomes_current(self) -> None:
        baseline = self.create_record()
        revision_b = self.create_record(
            revision="B",
            classification="proposed",
            source_reference="controlled://drawings/DRW-001-B.pdf",
            content_hash=self.digest("DRW-001-B"),
            supersedes_id=baseline["drawing_evidence_id"],
        )
        self.assertEqual(
            self.repository.current_revision("project-a", "DRW-001")["drawing_evidence_id"],
            revision_b["drawing_evidence_id"],
        )

    def test_cross_project_supersession_is_rejected(self) -> None:
        other = self.create_record(
            project_id="project-b",
            document_number="DRW-002",
            content_hash=self.digest("project-b"),
        )
        with self.assertRaisesRegex(ValueError, "same project"):
            self.create_record(supersedes_id=other["drawing_evidence_id"])

    def test_archived_project_is_read_only(self) -> None:
        with self.database.transaction() as connection:
            connection.execute("UPDATE projects SET archived_at = CURRENT_TIMESTAMP WHERE project_id = 'project-a'")
        with self.assertRaisesRegex(ValueError, "read-only"):
            self.create_record()

    def test_records_are_immutable_in_repository_and_database(self) -> None:
        record = self.create_record()
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.repository.update(record["drawing_evidence_id"])
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE drawing_evidence SET title = 'Changed' WHERE drawing_evidence_id = ?",
                    (record["drawing_evidence_id"],),
                )

    def test_approval_requires_validation(self) -> None:
        with self.assertRaisesRegex(ValueError, "Approval requires validated status"):
            self.create_record(approval_status="approved", validation_status="validation_required")

    def test_dxf_and_dwg_geometry_interpretation_is_prohibited(self) -> None:
        result = validate_drawing_evidence(
            {
                "project_id": "project-a",
                "document_type": "cad",
                "document_number": "CAD-001",
                "title": "CAD reference",
                "revision": "A",
                "classification": "proposed",
                "file_format": "dxf",
                "source_reference": "controlled://cad/CAD-001-A.dxf",
                "source_classification": "uploaded_fact",
                "validation_status": "validation_required",
                "approval_status": "approval_required",
                "content_hash": self.digest("cad"),
                "geometry_interpreted": True,
            }
        )
        self.assertIn("cad_interpretation_prohibited", {issue.code for issue in result.issues})


if __name__ == "__main__":
    unittest.main()
