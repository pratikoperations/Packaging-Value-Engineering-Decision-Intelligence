from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.application.runtime import (
    build_dataset_repository,
    build_persistent_specification_review_service,
    build_project_repository,
    build_specification_review_read_model,
)
from src.application.specification_review_service import SpecificationReviewError
from src.domain.specification_review import DatasetRole
from src.ui.specification_review_ui import (
    assigned_dataset_from_record,
    discover_reviewable_fields,
    history_rows,
    review_summary_label,
)


class SpecificationReviewDiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary_directory.name) / "pve.sqlite3"
        self.projects = build_project_repository(self.database_path)
        self.datasets = build_dataset_repository(self.database_path)
        self.service = build_persistent_specification_review_service(self.database_path)
        self.read_model = build_specification_review_read_model(self.database_path)
        for project_id, code in (("project-1", "PVE-001"), ("project-2", "PVE-002")):
            self.projects.create(
                project_id=project_id,
                project_code=code,
                project_name=f"Review {project_id}",
                category="corrugated",
                currency="INR",
                annual_volume=1000,
            )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _dataset(self, project_id: str, grade: str):
        return self.datasets.create_version(
            project_id=project_id,
            source_type="test",
            canonical_data={"specification": {"grade": grade}},
            validation_status="valid",
        )

    def _review(self, project_id: str, existing_grade: str = "A", proposed_grade: str = "B"):
        existing = assigned_dataset_from_record(self._dataset(project_id, existing_grade), DatasetRole.EXISTING)
        proposed = assigned_dataset_from_record(self._dataset(project_id, proposed_grade), DatasetRole.PROPOSED)
        return self.service.initialize_and_save(
            existing=existing,
            proposed=proposed,
            fields=discover_reviewable_fields(existing, proposed),
            actor_reference="creator",
        )

    def test_discovery_returns_one_latest_summary_per_review_and_project(self) -> None:
        first = self._review("project-1")
        second = self._review("project-1", "C", "D")
        self._review("project-2")
        self.service.confirm_and_save(
            first.review_id,
            dataset_id=first.state.existing_dataset_id,
            actor_reference="reviewer",
        )
        summaries = self.read_model.list_reviews_for_project("project-1")
        self.assertEqual({item.review_id for item in summaries}, {first.review_id, second.review_id})
        first_summary = next(item for item in summaries if item.review_id == first.review_id)
        self.assertEqual(first_summary.latest_revision_number, 2)
        self.assertEqual(first_summary.latest_action_type, "confirm_baseline")
        self.assertEqual(first_summary.pending_candidate_count, 1)
        self.assertEqual(first_summary.terminal_candidate_count, 0)

    def test_discovery_empty_project_is_safe(self) -> None:
        self.assertEqual(self.read_model.list_reviews_for_project("project-1"), [])

    def test_unknown_project_fails_closed(self) -> None:
        with self.assertRaises(SpecificationReviewError) as context:
            self.read_model.list_reviews_for_project("missing-project")
        self.assertEqual(context.exception.code, "unknown_project")

    def test_cross_project_latest_load_fails_closed(self) -> None:
        review = self._review("project-1")
        with self.assertRaises(SpecificationReviewError):
            self.read_model.load_latest(review.review_id, project_id="project-2")

    def test_history_is_sequential_read_only_and_resumable(self) -> None:
        review = self._review("project-1")
        self.service.confirm_and_save(
            review.review_id,
            dataset_id=review.state.existing_dataset_id,
            actor_reference="reviewer",
        )
        latest = self.service.accept_and_save(
            review.review_id,
            field_key="specification.grade",
            actor_reference="reviewer",
        )
        history = self.read_model.list_history(review.review_id, project_id="project-1")
        resumed = self.read_model.load_latest(review.review_id, project_id="project-1")
        self.assertEqual([item.revision_number for item in history], [1, 2, 3])
        self.assertEqual(resumed.review_revision_id, latest.review_revision_id)
        self.assertTrue(resumed.state.eligibility.eligible)
        rows = history_rows(history)
        self.assertEqual(rows[-1]["Action"], "accept")
        self.assertEqual(rows[-1]["Revision"], 3)
        self.assertTrue(rows[-1]["Content hash"])

    def test_summary_label_is_deterministic(self) -> None:
        review = self._review("project-1")
        summary = self.read_model.list_reviews_for_project("project-1")[0]
        self.assertEqual(review_summary_label(summary), review_summary_label(summary))
        self.assertIn(review.review_id, review_summary_label(summary))
        self.assertIn("revision 1", review_summary_label(summary))


if __name__ == "__main__":
    unittest.main()
