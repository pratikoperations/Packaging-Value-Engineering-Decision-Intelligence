from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.application.runtime import build_project_service, build_specification_draft_repository
from src.application.specification_upload import SessionSpecificationFile


class SpecificationDraftRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "drafts.sqlite3"
        self.projects = build_project_service(self.path)
        self.repository = build_specification_draft_repository(self.path)
        self.a = self.projects.create_project(
            project_code="DRAFT-A", project_name="Draft A", category="corrugated",
            currency="INR", annual_volume=120000,
        )
        self.b = self.projects.create_project(
            project_code="DRAFT-B", project_name="Draft B", category="corrugated",
            currency="INR", annual_volume=120000,
        )
        self.existing = SessionSpecificationFile("existing.pdf", "application/pdf", b"%PDF-existing")
        self.proposed = SessionSpecificationFile("proposed.pdf", "application/pdf", b"%PDF-proposed")

    def test_draft_round_trip_across_repository_instances(self):
        saved = self.repository.save(
            self.a["project_id"], self.existing, self.proposed,
            ({"review_id": "sample", "state": "pending"},),
        )
        fresh = build_specification_draft_repository(self.path)
        recovered = fresh.get(saved.draft_id, project_id=self.a["project_id"])
        self.assertEqual(recovered.existing_content, self.existing.content)
        self.assertEqual(recovered.proposed_content, self.proposed.content)
        self.assertEqual(recovered.reviews[0]["state"], "pending")
        self.assertEqual(len(fresh.list_for_project(self.a["project_id"])), 1)

    def test_cross_project_draft_access_rejected(self):
        saved = self.repository.save(self.a["project_id"], self.existing, self.proposed, ())
        with self.assertRaises(KeyError):
            self.repository.get(saved.draft_id, project_id=self.b["project_id"])
        self.assertEqual(self.repository.list_for_project(self.b["project_id"]), [])

    def test_archived_project_rejected(self):
        self.projects.archive_project(self.a["project_id"])
        with self.assertRaises(ValueError):
            self.repository.save(self.a["project_id"], self.existing, self.proposed, ())

    def test_drafts_are_append_only(self):
        saved = self.repository.save(self.a["project_id"], self.existing, self.proposed, ())
        with self.assertRaises(Exception):
            with self.repository.database.transaction() as connection:
                connection.execute(
                    "UPDATE specification_intake_drafts SET existing_name = ? WHERE draft_id = ?",
                    ("altered.pdf", saved.draft_id),
                )
        with self.assertRaises(Exception):
            with self.repository.database.transaction() as connection:
                connection.execute("DELETE FROM specification_intake_drafts WHERE draft_id = ?", (saved.draft_id,))

    def test_invalid_file_is_rejected(self):
        bad = SessionSpecificationFile("wrong.txt", "text/plain", b"abc")
        with self.assertRaises(ValueError):
            self.repository.save(self.a["project_id"], bad, self.proposed, ())


if __name__ == "__main__":
    unittest.main()
