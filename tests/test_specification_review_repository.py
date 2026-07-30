from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.application.specification_review_service import AssignedDataset, ReviewableField, SpecificationReviewService
from src.domain.specification_review import DatasetRole
from src.persistence.database import Database
from src.persistence.migrations import initialize_database
from src.persistence.specification_review_migration import SPECIFICATION_REVIEW_SCHEMA_VERSION
from src.persistence.specification_review_repository import SpecificationReviewPersistenceError, SpecificationReviewRepository


class SpecificationReviewRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.temp.name) / "pve.db")
        initialize_database(self.database)
        with self.database.transaction() as connection:
            connection.execute(
                "INSERT INTO projects(project_id, project_code, project_name, category, currency, annual_volume) VALUES ('p1','P1','Project','packaging','INR',1)"
            )
            for dataset_id, version, value in (("existing", 1, 10), ("proposed", 2, 12)):
                connection.execute(
                    "INSERT INTO project_datasets(dataset_id, project_id, version_number, source_type, canonical_json, validation_status, content_hash) VALUES (?, 'p1', ?, 'test', ?, 'valid', ?)",
                    (dataset_id, version, '{"spec":{"weight":%d}}' % value, dataset_id),
                )
        self.repository = SpecificationReviewRepository(self.database)
        self.service = SpecificationReviewService()
        self.state = self.service.initialize_review(
            existing=AssignedDataset("existing", "p1", DatasetRole.EXISTING, {"spec": {"weight": 10}}),
            proposed=AssignedDataset("proposed", "p1", DatasetRole.PROPOSED, {"spec": {"weight": 12}}),
            fields=(ReviewableField("weight", ("spec", "weight")),),
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_schema_version_ten_is_recorded(self) -> None:
        with self.database.connect() as connection:
            version = connection.execute("SELECT MAX(version) FROM schema_migrations").fetchone()[0]
        self.assertEqual(SPECIFICATION_REVIEW_SCHEMA_VERSION, version)

    def test_create_initial_round_trip(self) -> None:
        record = self.repository.create_initial(self.state, actor_reference="user:test")
        self.assertEqual(1, record.revision_number)
        self.assertEqual("initialize", record.action_type)
        self.assertEqual(self.state, record.state)

    def test_append_preserves_history_and_parent(self) -> None:
        first = self.repository.create_initial(self.state, actor_reference="user:test")
        next_state = self.service.confirm_existing_baseline(first.state, dataset_id="existing")
        second = self.repository.append_revision(
            next_state,
            review_id=first.review_id,
            action_type="confirm_baseline",
            actor_reference="user:test",
        )
        self.assertEqual(2, second.revision_number)
        self.assertEqual(first.review_revision_id, second.parent_revision_id)
        self.assertEqual([1, 2], [item.revision_number for item in self.repository.list_revisions(first.review_id)])

    def test_reject_requires_reason(self) -> None:
        first = self.repository.create_initial(self.state, actor_reference="user:test")
        rejected = self.service.reject_candidate(first.state, field_key="weight")
        with self.assertRaisesRegex(SpecificationReviewPersistenceError, "require a reason"):
            self.repository.append_revision(
                rejected,
                review_id=first.review_id,
                action_type="reject",
                action_field_key="weight",
                actor_reference="user:test",
            )

    def test_actor_is_required(self) -> None:
        with self.assertRaisesRegex(SpecificationReviewPersistenceError, "actor"):
            self.repository.create_initial(self.state, actor_reference=" ")

    def test_update_and_delete_are_rejected(self) -> None:
        with self.assertRaises(SpecificationReviewPersistenceError):
            self.repository.update("x")
        with self.assertRaises(SpecificationReviewPersistenceError):
            self.repository.delete("x")

    def test_database_triggers_enforce_immutability(self) -> None:
        record = self.repository.create_initial(self.state, actor_reference="user:test")
        with self.assertRaises(sqlite3.DatabaseError):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE specification_review_revisions SET actor_reference='changed' WHERE review_revision_id=?",
                    (record.review_revision_id,),
                )

    def test_archived_project_is_read_only(self) -> None:
        with self.database.transaction() as connection:
            connection.execute("UPDATE projects SET archived_at='2026-01-01' WHERE project_id='p1'")
        with self.assertRaisesRegex(SpecificationReviewPersistenceError, "read-only"):
            self.repository.create_initial(self.state, actor_reference="user:test")

    def test_project_scoped_read_blocks_other_project(self) -> None:
        record = self.repository.create_initial(self.state, actor_reference="user:test")
        with self.assertRaises(SpecificationReviewPersistenceError):
            self.repository.get_latest(record.review_id, project_id="p2")


if __name__ == "__main__":
    unittest.main()
