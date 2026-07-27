from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.persistence.database import Database
from src.persistence.migrations import initialize_database
from src.persistence.specification_snapshot_repository import (
    DuplicateSpecificationSnapshotError,
    SpecificationSnapshotRepository,
)
from src.specification_intake.snapshot import (
    SnapshotDocument,
    SnapshotField,
    UnifiedSpecificationSnapshot,
)


def snapshot(project_id="P1", snapshot_id="S1", digest="h1"):
    existing = SnapshotDocument("existing", "pdf", "existing.pdf", "a" * 64, "pypdf", "v1")
    proposed = SnapshotDocument("proposed", "docx", "proposed.docx", "b" * 64, "docx-ooxml", "v1")
    field = SnapshotField(
        "box_weight", "existing", "confirmed", "780 g", 780, "g", None, None,
        780, "g", "pdf", "a" * 64, "pypdf", "v1", "block-1", "Box weight: 780 g",
        {"type": "pdf", "page_number": 1, "block_index": 0}, 99.0, "high", (), None,
    )
    return UnifiedSpecificationSnapshot(
        snapshot_id, project_id, "pdf_docx", existing, proposed, "schema-v1", "1.0",
        "deterministic", (field,), {"dataset_type": "synthetic_demo"}, (), False, digest,
    )


class SpecificationSnapshotRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.temp.name) / "test.sqlite3")
        initialize_database(self.database)
        with self.database.transaction() as connection:
            connection.execute(
                "INSERT INTO projects(project_id, project_code, project_name, category, currency, annual_volume) VALUES (?, ?, ?, ?, ?, ?)",
                ("P1", "P1", "Project 1", "corrugated", "INR", 1000),
            )
            connection.execute(
                "INSERT INTO projects(project_id, project_code, project_name, category, currency, annual_volume) VALUES (?, ?, ?, ?, ?, ?)",
                ("P2", "P2", "Project 2", "corrugated", "INR", 1000),
            )
            connection.execute(
                "INSERT INTO projects(project_id, project_code, project_name, category, currency, annual_volume, archived_at) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                ("P3", "P3", "Archived", "corrugated", "INR", 1000),
            )
        self.repository = SpecificationSnapshotRepository(self.database)

    def tearDown(self):
        self.temp.cleanup()

    def test_create_get_list_and_cross_project_protection(self):
        saved = self.repository.create(snapshot())
        self.assertEqual(saved["pair_format"], "pdf_docx")
        self.assertEqual(saved["existing_document"]["format"], "pdf")
        self.assertEqual(saved["confirmed_fields"][0]["source_location"]["page_number"], 1)
        self.assertEqual(len(self.repository.list_for_project("P1")), 1)
        with self.assertRaises(PermissionError):
            self.repository.get("S1", project_id="P2")

    def test_duplicate_update_delete_and_archived_project_rejected(self):
        self.repository.create(snapshot())
        with self.assertRaises(DuplicateSpecificationSnapshotError):
            self.repository.create(snapshot(snapshot_id="S2"))
        with self.assertRaises(ValueError):
            self.repository.update("S1", content_hash="changed")
        with self.assertRaises(ValueError):
            self.repository.delete("S1")
        with self.assertRaises(ValueError):
            self.repository.create(snapshot(project_id="P3", snapshot_id="S3", digest="h3"))

    def test_database_triggers_reject_direct_update_and_delete(self):
        self.repository.create(snapshot())
        with self.assertRaises(Exception):
            with self.database.transaction() as connection:
                connection.execute("UPDATE unified_specification_snapshots SET pair_format = 'pdf_pdf' WHERE specification_snapshot_id = 'S1'")
        with self.assertRaises(Exception):
            with self.database.transaction() as connection:
                connection.execute("DELETE FROM unified_specification_snapshots WHERE specification_snapshot_id = 'S1'")


if __name__ == "__main__":
    unittest.main()
