from __future__ import annotations

import unittest

from src.ai_extraction import AmbiguityCode, ConfidenceBand, ExtractionCandidate
from src.document_intake import (
    DocumentRole,
    ParsedDocument,
    SourceBlock,
    SourceBlockType,
    SourceLocation,
)
from src.review_comparison import (
    ComparisonStatus,
    ReviewError,
    ReviewState,
    build_candidate_reviews,
    build_change_summary,
    compare_fields,
    confirm,
    correct_and_confirm,
    group_reviews,
    intentionally_omit,
    reject,
    resolve_candidate,
    unresolved_reason,
)


def document(role: DocumentRole, block_id: str, text: str) -> ParsedDocument:
    return ParsedDocument(
        filename=f"{role.value}.docx",
        role=role,
        sha256=role.value * 8,
        blocks=(
            SourceBlock(
                block_id=block_id,
                block_type=SourceBlockType.TABLE_CELL,
                text=text,
                location=SourceLocation(table_index=0, row_index=0, cell_index=1, section_title="Specification"),
            ),
        ),
    )


def candidate(
    field: str,
    role: DocumentRole,
    block_id: str,
    raw,
    normalized,
    unit=None,
    ambiguity=(),
):
    return ExtractionCandidate(
        field_name=field,
        document_role=role,
        raw_value=raw,
        normalized_value=normalized,
        unit=unit,
        confidence=95,
        confidence_band=ConfidenceBand.HIGH,
        source_block_id=block_id,
        source_excerpt=str(raw),
        ambiguity_codes=tuple(ambiguity),
    )


class ReviewWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.existing_doc = document(DocumentRole.EXISTING, "e1", "780")
        self.proposed_doc = document(DocumentRole.PROPOSED, "p1", "650")

    def test_builds_pending_review_with_source_location(self):
        reviews = build_candidate_reviews(
            [candidate("box_weight", DocumentRole.EXISTING, "e1", 780, 780, "g")],
            [self.existing_doc],
        )
        self.assertEqual(reviews[0].state, ReviewState.PENDING)
        self.assertEqual(reviews[0].source.location.table_index, 0)
        self.assertEqual(reviews[0].source.excerpt, "780")

    def test_rejects_unavailable_or_ungrounded_source(self):
        with self.assertRaises(ReviewError):
            build_candidate_reviews(
                [candidate("box_weight", DocumentRole.EXISTING, "missing", 780, 780, "g")],
                [self.existing_doc],
            )
        bad = candidate("box_weight", DocumentRole.EXISTING, "e1", "999", 999, "g")
        with self.assertRaises(ReviewError):
            build_candidate_reviews([bad], [self.existing_doc])

    def test_confirm_preserves_original_and_blocks_ambiguity(self):
        review = build_candidate_reviews(
            [candidate("box_weight", DocumentRole.EXISTING, "e1", 780, 780, "g")],
            [self.existing_doc],
        )[0]
        confirmed = confirm(review, reviewer_note="Verified against source")
        self.assertEqual(confirmed.state, ReviewState.CONFIRMED)
        self.assertEqual(confirmed.effective_value, 780)
        self.assertEqual(confirmed.candidate.raw_value, 780)

        blocked_candidate = candidate(
            "box_weight",
            DocumentRole.EXISTING,
            "e1",
            780,
            780,
            "g",
            [AmbiguityCode.UNIT_CONFLICT],
        )
        blocked = build_candidate_reviews([blocked_candidate], [self.existing_doc])[0]
        with self.assertRaises(ReviewError):
            confirm(blocked)

    def test_correct_omit_and_reject_require_notes(self):
        review = build_candidate_reviews(
            [candidate("box_weight", DocumentRole.EXISTING, "e1", 780, 780, "g")],
            [self.existing_doc],
        )[0]
        corrected = correct_and_confirm(review, 775, "g", reviewer_note="Corrected from table note")
        self.assertEqual(corrected.state, ReviewState.CORRECTED_CONFIRMED)
        self.assertEqual(corrected.effective_value, 775)
        self.assertEqual(corrected.candidate.raw_value, 780)
        self.assertEqual(intentionally_omit(review, reviewer_note="Not applicable").state, ReviewState.INTENTIONALLY_OMITTED)
        self.assertEqual(reject(review, reviewer_note="Wrong source").state, ReviewState.REJECTED)
        with self.assertRaises(ReviewError):
            correct_and_confirm(review, 775, "g", reviewer_note="")

    def test_duplicate_candidate_requires_explicit_resolution(self):
        doc = ParsedDocument(
            filename="existing.docx",
            role=DocumentRole.EXISTING,
            sha256="x" * 64,
            blocks=(
                SourceBlock("e1", SourceBlockType.TABLE_CELL, "780", SourceLocation(table_index=0, row_index=0, cell_index=0)),
                SourceBlock("e2", SourceBlockType.TABLE_CELL, "775", SourceLocation(table_index=0, row_index=1, cell_index=0)),
            ),
        )
        candidates = [
            candidate("box_weight", DocumentRole.EXISTING, "e1", 780, 780, "g", [AmbiguityCode.MULTIPLE_CANDIDATES]),
            candidate("box_weight", DocumentRole.EXISTING, "e2", 775, 775, "g", [AmbiguityCode.MULTIPLE_CANDIDATES]),
        ]
        reviews = list(build_candidate_reviews(candidates, [doc]))
        reviews[0] = correct_and_confirm(reviews[0], 780, "g", reviewer_note="Selected first source")
        reviews[1] = reject(reviews[1], reviewer_note="Superseded row")
        group = group_reviews(reviews)[0]
        self.assertEqual(unresolved_reason(group), "multiple_candidates_unresolved")
        resolved = resolve_candidate(group, 0)
        self.assertIsNone(unresolved_reason(resolved))
        self.assertEqual(resolved.selected_review.effective_value, 780)


class ComparisonTests(unittest.TestCase):
    def reviewed_group(self, field, role, block, raw, normalized, unit=None):
        doc = document(role, block, str(raw))
        review = build_candidate_reviews([candidate(field, role, block, raw, normalized, unit)], [doc])[0]
        return group_reviews([confirm(review)])[0]

    def test_numeric_change_and_summary(self):
        groups = [
            self.reviewed_group("box_weight", DocumentRole.EXISTING, "e1", 780, 780, "g"),
            self.reviewed_group("box_weight", DocumentRole.PROPOSED, "p1", 650, 650, "g"),
        ]
        comparisons = compare_fields(["box_weight", "box_style"], groups)
        self.assertEqual(comparisons[0].status, ComparisonStatus.CHANGED)
        self.assertEqual(comparisons[0].change, -130)
        self.assertAlmostEqual(comparisons[0].change_percent, -16.6666666, places=5)
        self.assertEqual(comparisons[1].status, ComparisonStatus.BOTH_MISSING)
        summary = build_change_summary(comparisons, groups)
        self.assertEqual(summary.changed, 1)
        self.assertEqual(summary.both_missing, 1)
        self.assertEqual(summary.total_fields, 2)

    def test_all_comparison_statuses(self):
        groups = [
            self.reviewed_group("same", DocumentRole.EXISTING, "e1", "RSC", "RSC"),
            self.reviewed_group("same", DocumentRole.PROPOSED, "p1", "rsc", "rsc"),
            self.reviewed_group("only_existing", DocumentRole.EXISTING, "e2", 1, 1),
            self.reviewed_group("only_proposed", DocumentRole.PROPOSED, "p2", 2, 2),
            self.reviewed_group("unit", DocumentRole.EXISTING, "e3", 10, 10, "g"),
            self.reviewed_group("unit", DocumentRole.PROPOSED, "p3", 0.01, 0.01, "kg"),
            self.reviewed_group("type", DocumentRole.EXISTING, "e4", 10, 10),
            self.reviewed_group("type", DocumentRole.PROPOSED, "p4", "ten", "ten"),
        ]
        results = {item.field_name: item.status for item in compare_fields(
            ["same", "only_existing", "only_proposed", "missing", "unit", "type"], groups
        )}
        self.assertEqual(results["same"], ComparisonStatus.UNCHANGED)
        self.assertEqual(results["only_existing"], ComparisonStatus.PROPOSED_MISSING)
        self.assertEqual(results["only_proposed"], ComparisonStatus.EXISTING_MISSING)
        self.assertEqual(results["missing"], ComparisonStatus.BOTH_MISSING)
        self.assertEqual(results["unit"], ComparisonStatus.UNIT_CONFLICT)
        self.assertEqual(results["type"], ComparisonStatus.NOT_COMPARABLE)

    def test_pending_review_is_reported_as_unresolved_and_not_compared(self):
        doc = document(DocumentRole.EXISTING, "e1", "780")
        review = build_candidate_reviews(
            [candidate("box_weight", DocumentRole.EXISTING, "e1", 780, 780, "g")], [doc]
        )[0]
        groups = group_reviews([review])
        comparisons = compare_fields(["box_weight"], groups)
        summary = build_change_summary(comparisons, groups)
        self.assertEqual(comparisons[0].status, ComparisonStatus.BOTH_MISSING)
        self.assertEqual(summary.unresolved_fields, ("existing:box_weight:pending_review",))


if __name__ == "__main__":
    unittest.main()
