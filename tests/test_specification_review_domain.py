import unittest

from src.domain.specification_review import (
    BLOCKER_EXISTING_BASELINE,
    BLOCKER_PENDING_MANDATORY,
    BLOCKER_PROPOSED_DATASET,
    BLOCKER_VALIDATION,
    DatasetRole,
    ExistingBaselineConfirmation,
    ReviewStatus,
    SpecificationCandidate,
    evaluate_snapshot_eligibility,
)


class SpecificationReviewDomainTests(unittest.TestCase):
    def test_dataset_roles_are_stable(self):
        self.assertEqual(DatasetRole.EXISTING.value, "existing")
        self.assertEqual(DatasetRole.PROPOSED.value, "proposed")

    def test_valid_transitions(self):
        candidate = SpecificationCandidate("board_grade", "5-ply")
        self.assertEqual(candidate.transition(ReviewStatus.ACCEPTED).status, ReviewStatus.ACCEPTED)
        self.assertEqual(candidate.transition(ReviewStatus.REJECTED).status, ReviewStatus.REJECTED)
        corrected = candidate.transition(ReviewStatus.CORRECTED, corrected_value="3-ply")
        self.assertEqual(corrected.status, ReviewStatus.CORRECTED)
        self.assertEqual(corrected.final_value, "3-ply")

    def test_invalid_transition_from_terminal_state(self):
        candidate = SpecificationCandidate("board_grade", "5-ply").transition(ReviewStatus.ACCEPTED)
        with self.assertRaises(ValueError):
            candidate.transition(ReviewStatus.REJECTED)

    def test_original_value_is_preserved_after_correction(self):
        candidate = SpecificationCandidate("gsm", 180)
        corrected = candidate.transition(ReviewStatus.CORRECTED, corrected_value=200)
        self.assertEqual(corrected.original_value, 180)
        self.assertEqual(corrected.corrected_value, 200)
        self.assertEqual(corrected.final_value, 200)

    def test_mandatory_pending_blocks_snapshot(self):
        result = evaluate_snapshot_eligibility(
            existing_baseline=ExistingBaselineConfirmation("existing-1", True),
            proposed_dataset_id="proposed-1",
            candidates=[SpecificationCandidate("gsm", 180, mandatory=True)],
            has_unresolved_validation_issue=False,
        )
        self.assertFalse(result.eligible)
        self.assertEqual(result.blockers, (BLOCKER_PENDING_MANDATORY,))

    def test_optional_pending_candidate_does_not_block_snapshot(self):
        result = evaluate_snapshot_eligibility(
            existing_baseline=ExistingBaselineConfirmation("existing-1", True),
            proposed_dataset_id="proposed-1",
            candidates=[SpecificationCandidate("print_note", "blue", mandatory=False)],
            has_unresolved_validation_issue=False,
        )
        self.assertTrue(result.eligible)
        self.assertEqual(result.blockers, ())

    def test_blocker_order_is_deterministic(self):
        result = evaluate_snapshot_eligibility(
            existing_baseline=None,
            proposed_dataset_id=None,
            candidates=[SpecificationCandidate("gsm", 180, mandatory=True)],
            has_unresolved_validation_issue=True,
        )
        self.assertEqual(
            result.blockers,
            (
                BLOCKER_EXISTING_BASELINE,
                BLOCKER_PROPOSED_DATASET,
                BLOCKER_VALIDATION,
                BLOCKER_PENDING_MANDATORY,
            ),
        )

    def test_eligible_state(self):
        candidate = SpecificationCandidate("gsm", 180).transition(ReviewStatus.ACCEPTED)
        result = evaluate_snapshot_eligibility(
            existing_baseline=ExistingBaselineConfirmation("existing-1", True),
            proposed_dataset_id="proposed-1",
            candidates=[candidate],
            has_unresolved_validation_issue=False,
        )
        self.assertTrue(result.eligible)
        self.assertEqual(result.blockers, ())

    def test_correction_requires_value(self):
        candidate = SpecificationCandidate("gsm", 180)
        with self.assertRaises(ValueError):
            candidate.transition(ReviewStatus.CORRECTED)


if __name__ == "__main__":
    unittest.main()
