from __future__ import annotations

import unittest
from pathlib import Path

PAGE = Path(__file__).resolve().parents[2] / "pages" / "09_Data_Upload.py"


class SpecificationComparisonPresentationTests(unittest.TestCase):
    def test_side_by_side_comparison_has_filters(self):
        source = PAGE.read_text(encoding="utf-8")
        self.assertIn('st.subheader("Specification comparison")', source)
        self.assertIn('"Filter by comparison status"', source)
        self.assertIn('"Filter by parameter criticality"', source)
        self.assertIn("st.dataframe(filtered_rows", source)

    def test_raw_json_is_not_rendered(self):
        source = PAGE.read_text(encoding="utf-8")
        self.assertNotIn("st.json(", source)
        self.assertIn('with st.expander("Technical source evidence")', source)
        self.assertIn("format_source_location", source)

    def test_missing_priority_messages_exist(self):
        source = PAGE.read_text(encoding="utf-8")
        self.assertIn("Critical parameters missing", source)
        self.assertIn("Major parameters missing", source)
        self.assertIn("Only minor parameters are incomplete", source)
        self.assertIn("presentation-only review aid", source)

    def test_source_document_rows_are_collapsed(self):
        source = PAGE.read_text(encoding="utf-8")
        self.assertIn('with st.expander("Source document evidence")', source)


if __name__ == "__main__":
    unittest.main()
