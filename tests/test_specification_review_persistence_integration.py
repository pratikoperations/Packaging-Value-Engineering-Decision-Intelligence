from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.application.persistent_specification_review_service import PersistentSpecificationReviewService
from src.application.specification_review_service import AssignedDataset, ReviewableField, SpecificationReviewError, SpecificationReviewService
from src.domain.specification_review import DatasetRole, ReviewStatus
from src.persistence.database import Database
from src.persistence.migrations import initialize_database
from src.persistence.specification_review_repository import SpecificationReviewRepository


class SpecificationReviewPersistenceIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        database = Database(Path(self.temp.name) / "pve.db")
        initialize_database(database)
        with database.transaction() as connection:
            connection.execute(
                "INSERT INTO projects(project_id, project_code, project_name, category, currency, annual_volume) VALUES ('p1','P1','Project','packaging','INR',1)"
            )
            connection.execute(
                "INSERT INTO project_datasets(dataset_id, project_id, version_number, source_type, canonical_json, validation_status, content_hash) VALUES ('existing','p1',1,'test','{}','valid','existing')"
            )
            connection.execute(
                "INSERT INTO project_datasets(dataset_id, project_id, version_number, source_type, canonical_json, validation_status, content_hash) VALUES ('proposed','p1',2,'test','{}','valid','proposed')"
            )
        self.service = PersistentSpecificationReviewService(
            SpecificationReviewService(),
            SpecificationReviewRepository(database),
        )
        self.existing = AssignedDataset(
            "existing", "p1", DatasetRole.EXISTING,
            {"spec": {"weight": 10, "height": 20}},
        )
        self.proposed = AssignedDataset(
            "proposed", "p1", DatasetRole.PROPOSED,
            {"spec": {"weight": 12, "height": 22}},
        )
        self.fields = (
            ReviewableField("weight", ("spec", "weight")),
            ReviewableField("height", ("spec", "height")),
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_complete_governed_history_becomes_eligible(self) -> None:
        initial = self.service.initialize_and_save(
            existing=self.existing,
            proposed=self.proposed,
            fields=self.fields,
            actor_reference="user:test",
        )
        confirmed = self.service.confirm_and_save(
            initial.review_id,
            dataset_id="existing",
            actor_reference="user:test",
        )
        accepted = self.service.accept_and_save(
            initial.review_id,
            field_key="weight",
            actor_reference="user:test",
        )
        corrected = self.service.correct_and_save(
            initial.review_id,
            field_key="height",
            corrected_value=21,
            actor_reference="user:test",
            action_reason="Engineering correction",
        )
        self.assertEqual([1, 2, 3, 4], [item.revision_number for item in self.service.list_history(initial.review_id)])
        self.assertTrue(corrected.state.eligibility.eligible)
        self.assertEqual(ReviewStatus.ACCEPTED, accepted.state.comparisons[0].candidate.status)
        self.assertEqual(21, corrected.state.comparisons[1].candidate.corrected_value)
        self.assertEqual(confirmed.review_revision_id, accepted.parent_revision_id)

    def test_invalid_terminal_transition_writes_no_revision(self) -> None:
        initial = self.service.initialize_and_save(
            existing=self.existing,
            proposed=self.proposed,
            fields=self.fields,
            actor_reference="user:test",
        )
        self.service.accept_and_save(
            initial.review_id,
            field_key="weight",
            actor_reference="user:test",
        )
        with self.assertRaises(SpecificationReviewError):
            self.service.reject_and_save(
                initial.review_id,
                field_key="weight",
                actor_reference="user:test",
                action_reason="Attempt invalid transition",
            )
        self.assertEqual(2, len(self.service.list_history(initial.review_id)))

    def test_reload_from_new_service_instance_is_equivalent(self) -> None:
        initial = self.service.initialize_and_save(
            existing=self.existing,
            proposed=self.proposed,
            fields=self.fields,
            actor_reference="user:test",
        )
        loaded = self.service.load_latest(initial.review_id, project_id="p1")
        self.assertEqual(initial.state, loaded.state)
        self.assertEqual(initial.content_hash, loaded.content_hash)


if __name__ == "__main__":
    unittest.main()
