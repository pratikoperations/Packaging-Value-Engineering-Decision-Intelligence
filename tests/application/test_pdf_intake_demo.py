from __future__ import annotations

import unittest

from src.application.pdf_intake_demo import (
    build_pdf_demo_reviews,
    deterministic_pdf_candidates,
    load_synthetic_pdf_pair,
    synthetic_pdf_documents,
)
from src.document_intake import DocumentRole
from src.pdf_intake import compare_pdf_review_groups
from src.review_comparison import confirm, group_reviews


class PdfIntakeDemoTests(unittest.TestCase):
    def test_synthetic_files_are_searchable_pdf_documents(self):
        existing_bytes, proposed_bytes = synthetic_pdf_documents()
        self.assertTrue(existing_bytes.startswith(b"%PDF-"))
        self.assertTrue(proposed_bytes.startswith(b"%PDF-"))
        existing, proposed = load_synthetic_pdf_pair()
        self.assertEqual(existing.role, DocumentRole.EXISTING)
        self.assertEqual(proposed.role, DocumentRole.PROPOSED)
        self.assertGreaterEqual(len(existing.blocks), 1)
        self.assertGreaterEqual(len(proposed.blocks), 1)
        self.assertEqual(existing.page_count, 1)
        self.assertEqual(proposed.page_count, 1)

    def test_deterministic_extraction_is_grounded_and_uses_expected_values(self):
        existing, proposed = load_synthetic_pdf_pair()
        existing_candidates = deterministic_pdf_candidates(existing)
        proposed_candidates = deterministic_pdf_candidates(proposed)
        self.assertEqual(len(existing_candidates), 13)
        self.assertEqual(len(proposed_candidates), 13)
        existing_weight = next(c for c in existing_candidates if c.field_name == "box_weight")
        proposed_weight = next(c for c in proposed_candidates if c.field_name == "box_weight")
        self.assertEqual(existing_weight.normalized_value, 780)
        self.assertEqual(proposed_weight.normalized_value, 650)
        self.assertEqual(existing_weight.unit, "g")
        source = next(b.normalized_text for b in existing.blocks if b.block_id == existing_weight.source_block_id)
        self.assertIn(existing_weight.source_excerpt, source)

    def test_review_and_comparison_reuse(self):
        documents = load_synthetic_pdf_pair()
        bundle = build_pdf_demo_reviews(documents)
        confirmed = tuple(confirm(item.review) for item in bundle.reviews)
        groups = group_reviews(confirmed)
        comparisons, summary = compare_pdf_review_groups(groups, ["box_weight", "box_style"])
        weight = next(item for item in comparisons if item.field_name == "box_weight")
        style = next(item for item in comparisons if item.field_name == "box_style")
        self.assertEqual(weight.change, -130)
        self.assertEqual(style.status.value, "unchanged")
        self.assertEqual(summary.unresolved_fields, ())


if __name__ == "__main__":
    unittest.main()
