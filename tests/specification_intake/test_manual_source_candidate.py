from __future__ import annotations

import unittest

from src.review_comparison import ReviewError, ReviewState
from src.specification_intake.models import DocumentRole, UnifiedSourceBlock, UnifiedSpecificationDocument
from src.specification_intake.review_view import build_manual_source_candidate, apply_review_action
from src.upload_routing.models import FileFormat


class ManualSourceCandidateTests(unittest.TestCase):
    def setUp(self):
        self.block = UnifiedSourceBlock(
            block_id="proposed-pdf-block-3",
            document_role=DocumentRole.PROPOSED,
            document_format=FileFormat.PDF,
            raw_text="Requested box weight 790 g",
            normalized_text="Requested box weight 790 g",
            extraction_order=3,
            parser_name="test-parser",
            parser_version="v1",
            source_location={"type": "pdf", "page_number": 1, "block_index": 3},
        )
        self.document = UnifiedSpecificationDocument(
            filename="proposed.pdf", document_role=DocumentRole.PROPOSED,
            document_format=FileFormat.PDF, sha256="b"*64,
            parser_name="test-parser", parser_version="v1",
            source_blocks=(self.block,),
        )

    def test_literal_manual_candidate_starts_pending_and_retains_provenance(self):
        view = build_manual_source_candidate(
            document=self.document, field_name="box_weight",
            source_block_id=self.block.block_id, literal_value="790 g",
        )
        self.assertEqual(view.state, ReviewState.PENDING)
        self.assertEqual(view.normalized_value, 790)
        self.assertEqual(view.unit, "g")
        self.assertEqual(view.confidence, 0)
        self.assertEqual(view.source_block_id, self.block.block_id)
        self.assertEqual(view.source_location["page_number"], 1)
        self.assertEqual(view.review.effective_value, None)
        confirmed = apply_review_action(
            view, ReviewState.CONFIRMED, reviewer_note="Reviewed source document"
        )
        self.assertEqual(confirmed.review.effective_value, 790)

    def test_rejects_unmatched_claim(self):
        with self.assertRaises(ReviewError):
            build_manual_source_candidate(
                document=self.document, field_name="box_weight",
                source_block_id=self.block.block_id, literal_value="900 g",
            )

    def test_rejects_unknown_field_and_invalid_role_block(self):
        with self.assertRaises(ReviewError):
            build_manual_source_candidate(
                document=self.document, field_name="imaginary",
                source_block_id=self.block.block_id, literal_value="790 g",
            )
        with self.assertRaises(ReviewError):
            build_manual_source_candidate(
                document=self.document, field_name="box_weight",
                source_block_id="existing-pdf-block-3", literal_value="790 g",
            )

    def test_rejects_nonnumeric_value_for_numeric_field(self):
        with self.assertRaises(ReviewError):
            build_manual_source_candidate(
                document=self.document, field_name="box_weight",
                source_block_id=self.block.block_id, literal_value="weight",
            )


if __name__ == "__main__":
    unittest.main()
