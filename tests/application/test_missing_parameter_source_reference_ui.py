from __future__ import annotations

import unittest
from pathlib import Path


class MissingSourceReferenceUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (
            Path(__file__).resolve().parents[2] / "pages" / "09_Data_Upload.py"
        ).read_text(encoding="utf-8")

    def test_missing_value_has_source_block_inspection(self):
        self.assertIn("def render_missing_field_triage(rows, pair)", self.source)
        self.assertIn("document = pair.existing if role", self.source)
        self.assertIn("block.block_id, block.normalized_text, block.source_location", self.source)
        self.assertIn("Attach source block reference", self.source)
        self.assertIn("reviewer verification required", self.source)

    def test_source_reference_is_note_not_canonical_candidate(self):
        self.assertIn("on_click=attach_triage_source_reference", self.source)
        self.assertIn("def render_reviews(views, pair)", self.source)
        self.assertIn("render_missing_field_triage(rows, pair)", self.source)
        self.assertIn("triage_evidence_", self.source)


if __name__ == "__main__":
    unittest.main()
