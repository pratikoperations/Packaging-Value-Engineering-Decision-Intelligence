from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from src.application.runtime import (
    build_dataset_repository,
    build_persistent_specification_review_service,
    build_project_repository,
)
from src.domain.specification_review import DatasetRole
from src.ui.specification_review_ui import (
    ReviewActionRequest,
    action_token,
    assigned_dataset_from_record,
    comparison_rows,
    discover_reviewable_fields,
    execute_once,
)


class SpecificationReviewUiAdapterTests(unittest.TestCase):
    def test_assigned_dataset_decodes_canonical_json(self) -> None:
        record = {
            "dataset_id": "dataset-1",
            "project_id": "project-1",
            "canonical_json": json.dumps({"specification": {"width_mm": 400}}),
            "validation_status": "valid",
        }
        dataset = assigned_dataset_from_record(record, DatasetRole.EXISTING)
        self.assertEqual(dataset.canonical_data["specification"]["width_mm"], 400)
        self.assertIs(dataset.role, DatasetRole.EXISTING)

    def test_assigned_dataset_accepts_decoded_mapping(self) -> None:
        record = {
            "dataset_id": "dataset-1",
            "project_id": "project-1",
            "canonical_json": {"grade": "A"},
            "validation_status": "valid",
        }
        dataset = assigned_dataset_from_record(record, DatasetRole.PROPOSED)
        self.assertEqual(dataset.canonical_data, {"grade": "A"})

    def test_discover_reviewable_fields_returns_sorted_scalar_paths(self) -> None:
        existing = assigned_dataset_from_record(
            {
                "dataset_id": "existing",
                "project_id": "project",
                "canonical_json": {"spec": {"width": 10, "grade": "A"}},
                "validation_status": "valid",
            },
            DatasetRole.EXISTING,
        )
        proposed = assigned_dataset_from_record(
            {
                "dataset_id": "proposed",
                "project_id": "project",
                "canonical_json": {"spec": {"width": 9, "grade": "B"}},
                "validation_status": "valid",
            },
            DatasetRole.PROPOSED,
        )
        fields = discover_reviewable_fields(existing, proposed)
        self.assertEqual([field.field_key for field in fields], ["spec.grade", "spec.width"])

    def test_discover_reviewable_fields_ignores_list_values(self) -> None:
        dataset = assigned_dataset_from_record(
            {
                "dataset_id": "dataset",
                "project_id": "project",
                "canonical_json": {"items": [{"value": 1}], "grade": "A"},
                "validation_status": "valid",
            },
            DatasetRole.EXISTING,
        )
        fields = discover_reviewable_fields(dataset)
        self.assertEqual([field.field_key for field in fields], ["grade"])

    def test_action_token_is_deterministic(self) -> None:
        request = ReviewActionRequest("accept", "review-1", 2, field_key="spec.width")
        self.assertEqual(action_token(request), action_token(request))

    def test_action_token_changes_with_revision(self) -> None:
        first = ReviewActionRequest("accept", "review-1", 2, field_key="spec.width")
        second = ReviewActionRequest("accept", "review-1", 3, field_key="spec.width")
        self.assertNotEqual(action_token(first), action_token(second))

    def test_execute_once_commits_successful_action(self) -> None:
        session: dict[str, object] = {}
        calls: list[str] = []
        request = ReviewActionRequest("accept", "review-1", 1, field_key="grade")
        executed, result = execute_once(session, request, lambda: calls.append("called") or "saved")
        self.assertTrue(executed)
        self.assertEqual(result, "saved")
        self.assertEqual(calls, ["called"])

    def test_execute_once_blocks_streamlit_rerun_duplicate(self) -> None:
        session: dict[str, object] = {}
        calls: list[str] = []
        request = ReviewActionRequest("accept", "review-1", 1, field_key="grade")
        execute_once(session, request, lambda: calls.append("called"))
        executed, result = execute_once(session, request, lambda: calls.append("duplicate"))
        self.assertFalse(executed)
        self.assertIsNone(result)
        self.assertEqual(calls, ["called"])

    def test_execute_once_releases_pending_token_after_failure(self) -> None:
        session: dict[str, object] = {}
        request = ReviewActionRequest("reject", "review-1", 1, field_key="grade", reason="invalid")
        with self.assertRaises(RuntimeError):
            execute_once(session, request, lambda: (_ for _ in ()).throw(RuntimeError("failed")))
        executed, result = execute_once(session, request, lambda: "retry-saved")
        self.assertTrue(executed)
        self.assertEqual(result, "retry-saved")

    def test_comparison_rows_are_presentation_safe(self) -> None:
        candidate = SimpleNamespace(original_value="B", status=SimpleNamespace(value="pending"), corrected_value=None)
        item = SimpleNamespace(field_key="grade", existing_value="A", candidate=candidate)
        review = SimpleNamespace(state=SimpleNamespace(comparisons=(item,)))
        self.assertEqual(
            comparison_rows(review),
            [{"Field": "grade", "Existing": "A", "Proposed": "B", "Status": "pending", "Corrected": None}],
        )


class SpecificationReviewUiRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary_directory.name) / "pve.sqlite3"
        self.projects = build_project_repository(self.database_path)
        self.datasets = build_dataset_repository(self.database_path)
        self.service = build_persistent_specification_review_service(self.database_path)
        self.projects.create(
            project_id="project-1",
            project_code="PVE-001",
            project_name="Review UI Test",
            category="corrugated",
            currency="INR",
            annual_volume=1000,
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _create_dataset(self, grade: str) -> dict[str, object]:
        return self.datasets.create_version(
            project_id="project-1",
            source_type="test",
            canonical_data={"specification": {"grade": grade}},
            validation_status="valid",
        )

    def test_runtime_builders_share_persisted_review_database(self) -> None:
        existing_record = self._create_dataset("A")
        proposed_record = self._create_dataset("B")
        existing = assigned_dataset_from_record(existing_record, DatasetRole.EXISTING)
        proposed = assigned_dataset_from_record(proposed_record, DatasetRole.PROPOSED)
        fields = discover_reviewable_fields(existing, proposed)
        review = self.service.initialize_and_save(
            existing=existing,
            proposed=proposed,
            fields=fields,
            actor_reference="tester",
        )
        loaded = build_persistent_specification_review_service(self.database_path).load_latest(review.review_id)
        self.assertEqual(loaded.review_id, review.review_id)
        self.assertEqual(loaded.revision_number, 1)

    def test_end_to_end_ui_adapter_flow_reaches_eligibility(self) -> None:
        existing_record = self._create_dataset("A")
        proposed_record = self._create_dataset("B")
        existing = assigned_dataset_from_record(existing_record, DatasetRole.EXISTING)
        proposed = assigned_dataset_from_record(proposed_record, DatasetRole.PROPOSED)
        review = self.service.initialize_and_save(
            existing=existing,
            proposed=proposed,
            fields=discover_reviewable_fields(existing, proposed),
            actor_reference="tester",
        )
        review = self.service.confirm_and_save(
            review.review_id,
            dataset_id=existing.dataset_id,
            actor_reference="tester",
        )
        review = self.service.accept_and_save(
            review.review_id,
            field_key="specification.grade",
            actor_reference="tester",
        )
        self.assertTrue(review.state.eligibility.eligible)
        self.assertEqual(review.revision_number, 3)


if __name__ == "__main__":
    unittest.main()
