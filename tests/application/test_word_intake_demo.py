from __future__ import annotations

import unittest
from pathlib import Path

from src.application.word_intake_demo import (
    build_demo_reviews,
    demo_comparisons,
    demo_groups,
    deterministic_demo_candidates,
    load_synthetic_pair,
    synthetic_demo_documents,
)
from src.review_comparison import confirm


class WordIntakeDemoTests(unittest.TestCase):
    def test_synthetic_documents_parse_as_exact_pair(self):
        existing, proposed = synthetic_demo_documents()
        self.assertNotEqual(existing, proposed)
        pair = load_synthetic_pair()
        self.assertEqual(pair.existing.role.value, "existing")
        self.assertEqual(pair.proposed.role.value, "proposed")
        self.assertGreater(len(pair.existing.blocks), 20)
        self.assertGreater(len(pair.proposed.blocks), 20)

    def test_deterministic_mock_extraction_is_source_grounded(self):
        pair = load_synthetic_pair()
        existing = deterministic_demo_candidates(pair.existing)
        proposed = deterministic_demo_candidates(pair.proposed)
        self.assertEqual(len(existing), 13)
        self.assertEqual(len(proposed), 13)
        block_ids = {block.block_id for block in pair.existing.blocks}
        self.assertTrue(all(candidate.source_block_id in block_ids for candidate in existing))
        self.assertTrue(all(candidate.confidence == 99.0 for candidate in existing))
        self.assertEqual(
            next(candidate for candidate in existing if candidate.field_name == "box_weight").normalized_value,
            780,
        )

    def test_confirmed_reviews_generate_changed_comparison(self):
        pair = load_synthetic_pair()
        reviews = tuple(confirm(review) for review in build_demo_reviews(pair))
        comparisons = {item.field_name: item for item in demo_comparisons(demo_groups(reviews))}
        self.assertEqual(comparisons["box_style"].status.value, "unchanged")
        self.assertEqual(comparisons["box_weight"].status.value, "changed")
        self.assertEqual(comparisons["box_weight"].change, -130)

    def test_page_contains_required_governance_and_workflow_sections(self):
        content = Path("pages/07_PVE_2_0_AI_Word_Intake.py").read_text()
        for required in (
            "Synthetic portfolio demonstration only",
            "No external model or provider call is made",
            "Human review",
            "Existing versus proposed comparison",
            "Confirmed-only canonical dataset draft",
            "Immutable in-memory confirmed snapshot created",
            "Engineering validation and documented human approval remain mandatory",
        ):
            self.assertIn(required, content)


if __name__ == "__main__":
    unittest.main()
