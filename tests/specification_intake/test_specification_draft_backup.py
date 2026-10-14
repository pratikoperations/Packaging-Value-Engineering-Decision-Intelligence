from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.application.runtime import build_project_service, build_specification_draft_repository
from src.application.specification_upload import SessionSpecificationFile
from src.application.specification_draft_backup import (
    export_specification_draft,
    import_specification_draft,
)


class PortableDraftBackupTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "backup.sqlite3"
        projects = build_project_service(path)
        self.repository = build_specification_draft_repository(path)
        self.project = projects.create_project(
            project_code="PVE-TEST-001",
            project_name="Synthetic corrugated case",
            category="corrugated", currency="INR", annual_volume=120000,
        )
        self.other = projects.create_project(
            project_code="PVE-TEST-002",
            project_name="Other case",
            category="corrugated", currency="INR", annual_volume=120000,
        )
        self.saved = self.repository.save(
            self.project["project_id"],
            SessionSpecificationFile("old.pdf", "application/pdf", b"%PDF-old"),
            SessionSpecificationFile("new.pdf", "application/pdf", b"%PDF-new"),
            ({"review_id": "existing:box_weight:block1", "state": "confirmed"},),
        )
        self.backup = export_specification_draft(self.project["project_code"], self.saved)

    def test_portable_backup_roundtrip(self):
        recovered = import_specification_draft(
            self.repository, project_id=self.project["project_id"],
            project_code=self.project["project_code"], content=self.backup,
        )
        self.assertNotEqual(recovered.draft_id, self.saved.draft_id)
        self.assertEqual(recovered.existing_content, b"%PDF-old")
        self.assertEqual(recovered.proposed_content, b"%PDF-new")
        self.assertEqual(recovered.reviews, self.saved.reviews)

    def test_different_project_code_rejected(self):
        with self.assertRaises(ValueError):
            import_specification_draft(
                self.repository, project_id=self.other["project_id"],
                project_code=self.other["project_code"], content=self.backup,
            )

    def test_tampered_backup_rejected(self):
        bundle = json.loads(self.backup)
        bundle["reviews"][0]["state"] = "corrected_confirmed"
        tampered = json.dumps(bundle).encode()
        with self.assertRaises(ValueError):
            import_specification_draft(
                self.repository, project_id=self.project["project_id"],
                project_code=self.project["project_code"], content=tampered,
            )

    def test_malformed_backup_rejected(self):
        with self.assertRaises(ValueError):
            import_specification_draft(
                self.repository, project_id=self.project["project_id"],
                project_code=self.project["project_code"], content=b"not-json",
            )


if __name__ == "__main__":
    unittest.main()
