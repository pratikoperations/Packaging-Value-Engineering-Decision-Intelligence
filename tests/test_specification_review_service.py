from __future__ import annotations

import unittest

from src.application.specification_review_service import (
    AssignedDataset,
    ReviewableField,
    SpecificationReviewError,
    SpecificationReviewService,
)
from src.domain.specification_review import (
    BLOCKER_EXISTING_BASELINE,
    BLOCKER_PENDING_MANDATORY,
    DatasetRole,
    ReviewStatus,
)


class SpecificationReviewServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = SpecificationReviewService()
        self.fields = (
            ReviewableField("material", ("specification", "material")),
            ReviewableField("gsm", ("specification", "gsm")),
            ReviewableField("print", ("specification", "print"), mandatory=False),
        )
        self.existing = AssignedDataset(
            dataset_id="dataset-existing",
            project_id="project-1",
            role=DatasetRole.EXISTING,
            canonical_data={
                "specification": {
                    "material": "kraft",
                    "gsm": 180,
                    "print": "one-colour",
                }
            },
        )
        self.proposed = AssignedDataset(
            dataset_id="dataset-proposed",
            project_id="project-1",
            role=DatasetRole.PROPOSED,
            canonical_data={
                "specification": {
                    "material": "recycled-kraft",
                    "gsm": 160,
                    "print": "two-colour",
                }
            },
        )

    def initialize(self):
        return self.service.initialize_review(
            existing=self.existing,
            proposed=self.proposed,
            fields=self.fields,
        )

    def test_initializes_deterministic_candidates_in_registry_order(self) -> None:
        state = self.initialize()
        self.assertEqual(
            tuple(item.field_key for item in state.comparisons),
            ("material", "gsm", "print"),
        )
        self.assertEqual(state.comparisons[0].existing_value, "kraft")
        self.assertEqual(state.comparisons[0].candidate.original_value, "recycled-kraft")

    def test_unchanged_values_do_not_create_candidates(self) -> None:
        proposed = AssignedDataset(
            dataset_id="dataset-proposed",
            project_id="project-1",
            role=DatasetRole.PROPOSED,
            canonical_data={
                "specification": {
                    "material": "kraft",
                    "gsm": 160,
                    "print": "one-colour",
                }
            },
        )
        state = self.service.initialize_review(
            existing=self.existing,
            proposed=proposed,
            fields=self.fields,
        )
        self.assertEqual(tuple(item.field_key for item in state.comparisons), ("gsm",))

    def test_missing_paths_compare_as_none(self) -> None:
        proposed = AssignedDataset(
            dataset_id="dataset-proposed",
            project_id="project-1",
            role=DatasetRole.PROPOSED,
            canonical_data={"specification": {}},
        )
        state = self.service.initialize_review(
            existing=self.existing,
            proposed=proposed,
            fields=self.fields,
        )
        self.assertIsNone(state.comparisons[0].candidate.original_value)

    def test_requires_existing_role(self) -> None:
        wrong = AssignedDataset(
            dataset_id="dataset-existing",
            project_id="project-1",
            role=DatasetRole.PROPOSED,
            canonical_data={},
        )
        with self.assertRaisesRegex(SpecificationReviewError, "Existing role"):
            self.service.initialize_review(existing=wrong, proposed=self.proposed, fields=self.fields)

    def test_requires_proposed_role(self) -> None:
        wrong = AssignedDataset(
            dataset_id="dataset-proposed",
            project_id="project-1",
            role=DatasetRole.EXISTING,
            canonical_data={},
        )
        with self.assertRaisesRegex(SpecificationReviewError, "Proposed role"):
            self.service.initialize_review(existing=self.existing, proposed=wrong, fields=self.fields)

    def test_requires_distinct_dataset_ids(self) -> None:
        proposed = AssignedDataset(
            dataset_id=self.existing.dataset_id,
            project_id="project-1",
            role=DatasetRole.PROPOSED,
            canonical_data={},
        )
        with self.assertRaisesRegex(SpecificationReviewError, "distinct datasets"):
            self.service.initialize_review(existing=self.existing, proposed=proposed, fields=self.fields)

    def test_rejects_cross_project_pair(self) -> None:
        proposed = AssignedDataset(
            dataset_id="dataset-proposed",
            project_id="project-2",
            role=DatasetRole.PROPOSED,
            canonical_data={},
        )
        with self.assertRaisesRegex(SpecificationReviewError, "same project"):
            self.service.initialize_review(existing=self.existing, proposed=proposed, fields=self.fields)

    def test_requires_valid_datasets(self) -> None:
        proposed = AssignedDataset(
            dataset_id="dataset-proposed",
            project_id="project-1",
            role=DatasetRole.PROPOSED,
            canonical_data={},
            validation_status="invalid",
        )
        with self.assertRaisesRegex(SpecificationReviewError, "Only valid datasets"):
            self.service.initialize_review(existing=self.existing, proposed=proposed, fields=self.fields)

    def test_rejects_duplicate_registry_keys(self) -> None:
        fields = (
            ReviewableField("gsm", ("specification", "gsm")),
            ReviewableField("gsm", ("other", "gsm")),
        )
        with self.assertRaisesRegex(SpecificationReviewError, "must be unique"):
            self.service.initialize_review(existing=self.existing, proposed=self.proposed, fields=fields)

    def test_initial_state_is_blocked_by_baseline_and_pending_mandatory(self) -> None:
        state = self.initialize()
        self.assertEqual(
            state.eligibility.blockers,
            (BLOCKER_EXISTING_BASELINE, BLOCKER_PENDING_MANDATORY),
        )

    def test_confirms_only_existing_dataset(self) -> None:
        state = self.initialize()
        confirmed = self.service.confirm_existing_baseline(
            state,
            dataset_id=self.existing.dataset_id,
        )
        self.assertTrue(confirmed.existing_baseline.confirmed)
        self.assertNotIn(BLOCKER_EXISTING_BASELINE, confirmed.eligibility.blockers)

    def test_rejects_proposed_dataset_as_baseline(self) -> None:
        state = self.initialize()
        with self.assertRaisesRegex(SpecificationReviewError, "Only the assigned Existing"):
            self.service.confirm_existing_baseline(state, dataset_id=self.proposed.dataset_id)

    def test_accepts_pending_candidate(self) -> None:
        state = self.service.accept_candidate(self.initialize(), field_key="material")
        self.assertEqual(state.comparisons[0].candidate.status, ReviewStatus.ACCEPTED)

    def test_rejects_pending_candidate(self) -> None:
        state = self.service.reject_candidate(self.initialize(), field_key="material")
        self.assertEqual(state.comparisons[0].candidate.status, ReviewStatus.REJECTED)
        self.assertIsNone(state.comparisons[0].candidate.final_value)

    def test_corrects_pending_candidate_and_preserves_original(self) -> None:
        state = self.service.correct_candidate(
            self.initialize(),
            field_key="material",
            corrected_value="certified-kraft",
        )
        candidate = state.comparisons[0].candidate
        self.assertEqual(candidate.status, ReviewStatus.CORRECTED)
        self.assertEqual(candidate.original_value, "recycled-kraft")
        self.assertEqual(candidate.final_value, "certified-kraft")

    def test_rejects_second_terminal_transition_with_safe_error(self) -> None:
        state = self.service.accept_candidate(self.initialize(), field_key="material")
        with self.assertRaises(SpecificationReviewError) as context:
            self.service.reject_candidate(state, field_key="material")
        self.assertEqual(context.exception.code, "invalid_review_transition")
        self.assertNotIn("pending", context.exception.message.lower())

    def test_rejects_unknown_field_with_safe_error(self) -> None:
        with self.assertRaises(SpecificationReviewError) as context:
            self.service.accept_candidate(self.initialize(), field_key="unknown")
        self.assertEqual(context.exception.code, "unknown_review_field")

    def test_optional_pending_candidate_does_not_block_eligibility(self) -> None:
        state = self.initialize()
        state = self.service.confirm_existing_baseline(state, dataset_id=self.existing.dataset_id)
        state = self.service.accept_candidate(state, field_key="material")
        state = self.service.accept_candidate(state, field_key="gsm")
        self.assertTrue(state.eligibility.eligible)
        self.assertEqual(state.comparisons[2].candidate.status, ReviewStatus.PENDING)

    def test_all_mandatory_resolutions_make_state_eligible_after_confirmation(self) -> None:
        state = self.initialize()
        state = self.service.confirm_existing_baseline(state, dataset_id=self.existing.dataset_id)
        state = self.service.accept_candidate(state, field_key="material")
        state = self.service.correct_candidate(state, field_key="gsm", corrected_value=170)
        self.assertTrue(state.eligibility.eligible)
        self.assertEqual(state.eligibility.blockers, ())

    def test_operations_return_new_state_without_mutating_prior_state(self) -> None:
        original = self.initialize()
        updated = self.service.accept_candidate(original, field_key="material")
        self.assertIsNot(original, updated)
        self.assertEqual(original.comparisons[0].candidate.status, ReviewStatus.PENDING)
        self.assertEqual(updated.comparisons[0].candidate.status, ReviewStatus.ACCEPTED)

    def test_registry_validation_rejects_empty_path(self) -> None:
        with self.assertRaisesRegex(ValueError, "path"):
            ReviewableField("gsm", ())

    def test_assigned_dataset_requires_identifiers(self) -> None:
        with self.assertRaisesRegex(ValueError, "dataset_id"):
            AssignedDataset("", "project-1", DatasetRole.EXISTING, {})
        with self.assertRaisesRegex(ValueError, "project_id"):
            AssignedDataset("dataset", "", DatasetRole.EXISTING, {})


if __name__ == "__main__":
    unittest.main()
