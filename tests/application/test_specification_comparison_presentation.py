from __future__ import annotations

import unittest
from pathlib import Path


PAGE = Path(__file__).resolve().parents[2] / "pages" / "09_Data_Upload.py"


class SpecificationComparisonPresentationTests(unittest.TestCase):
    def test_side_by_side_comparison_has_four_business_columns(self):
        source = PAGE.read_text(encoding="utf-8")
        self.assertIn('"Parameter":', source)
        self.assertIn('"Existing":', source)
        self.assertIn('"Proposed":', source)
        self.assertIn('"Comparison Status":', source)
        self.assertIn('st.subheader("Specification comparison")', source)

    def test_raw_json_is_not_rendered_in_data_upload(self):
        source = PAGE.read_text(encoding="utf-8")
        self.assertNotIn("st.json(", source)
        self.assertIn('with st.expander("Technical source evidence")', source)
        self.assertIn("_format_source_location", source)

    def test_comparison_status_supports_changed_unchanged_and_incomplete(self):
        source = PAGE.read_text(encoding="utf-8")
        self.assertIn('status = "Changed"', source)
        self.assertIn('status = "Unchanged"', source)
        self.assertIn('status = "Incomplete"', source)

    def test_source_document_rows_are_collapsed_by_default(self):
        source = PAGE.read_text(encoding="utf-8")
        self.assertIn('with st.expander("Source document evidence")', source)


if __name__ == "__main__":
    unittest.main()
