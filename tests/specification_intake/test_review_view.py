from __future__ import annotations

import unittest

from src.review_comparison import ReviewError, ReviewState
from src.specification_intake import (
    DocumentRole,
    UnifiedSourceBlock,
    UnifiedSpecificationDocument,
    all_reviews_resolved,
    apply_review_action,
    build_common_review_views,
    build_pair,
    load_field_registry,
)
from src.upload_routing.models import FileFormat


def document(role, fmt, sha, text, location):
    block = UnifiedSourceBlock(
        block_id=f"{role.value}-{fmt.value}-1",
        document_role=role,
        document_format=fmt,
        raw_text=text,
        normalized_text=text,
        extraction_order=0,
        parser_name="test-parser",
        parser_version="v1",
        source_location=location,
    )
    return UnifiedSpecificationDocument(
        filename=f"{role.value}.{fmt.value}",
        document_role=role,
        document_format=fmt,
        sha256=sha,
        parser_name="test-parser",
        parser_version="v1",
        source_blocks=(block,),
    )


class CommonReviewViewTests(unittest.TestCase):
    def test_registry_is_governed_25_field_registry(self):
        registry = load_field_registry()
        self.assertEqual(len(registry), 25)
        self.assertIn("box_weight", registry)

    def test_builds_grounded_views_for_mixed_format_pair(self):
        existing = document(
            DocumentRole.EXISTING, FileFormat.PDF, "a" * 64,
            "Box weight: 780 g", {"type": "pdf", "page_number": 2, "block_index": 1},
        )
        proposed = document(
            DocumentRole.PROPOSED, FileFormat.DOCX, "b" * 64,
            "Box weight: 650 g", {"type": "docx", "paragraph_index": 4},
        )
        views = build_common_review_views(build_pair((existing, proposed)))
        self.assertEqual(len(views), 2)
        self.assertEqual({view.document_format for view in views}, {"pdf", "docx"})
        self.assertEqual({view.normalized_value for view in views}, {780, 650})
        self.assertTrue(all(view.source_excerpt in view.review.source.excerpt for view in views))

    def test_review_actions_and_resolution_gate(self):
        existing = document(
            DocumentRole.EXISTING, FileFormat.PDF, "a" * 64,
            "Box weight: 780 g", {"type": "pdf", "page_number": 1, "block_index": 0},
        )
        proposed = document(
            DocumentRole.PROPOSED, FileFormat.PDF, "b" * 64,
            "Box weight: 650 g", {"type": "pdf", "page_number": 1, "block_index": 0},
        )
        views = build_common_review_views(build_pair((existing, proposed)))
        self.assertFalse(all_reviews_resolved(views))
        confirmed = apply_review_action(views[0], ReviewState.CONFIRMED)
        corrected = apply_review_action(
            views[1], ReviewState.CORRECTED_CONFIRMED,
            corrected_value=655, corrected_unit="g", reviewer_note="Verified against source.",
        )
        self.assertTrue(all_reviews_resolved((confirmed, corrected)))
        self.assertEqual(corrected.review.effective_value, 655)

    def test_omit_and_reject_require_notes(self):
        existing = document(
            DocumentRole.EXISTING, FileFormat.PDF, "a" * 64,
            "Supplier: A", {"type": "pdf", "page_number": 1, "block_index": 0},
        )
        proposed = document(
            DocumentRole.PROPOSED, FileFormat.PDF, "b" * 64,
            "Supplier: B", {"type": "pdf", "page_number": 1, "block_index": 0},
        )
        view = build_common_review_views(build_pair((existing, proposed)))[0]
        with self.assertRaises(ReviewError):
            apply_review_action(view, ReviewState.INTENTIONALLY_OMITTED)
        omitted = apply_review_action(view, ReviewState.INTENTIONALLY_OMITTED, reviewer_note="Not required.")
        self.assertEqual(omitted.state, ReviewState.INTENTIONALLY_OMITTED)


if __name__ == "__main__":
    unittest.main()
