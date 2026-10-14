from __future__ import annotations

import unittest
from pathlib import Path

from src.specification_intake.comparison_presentation import missing_priority_summary


class FeasibilityPriorityGateTests(unittest.TestCase):
    def test_critical_and_major_gaps_block_data_readiness(self):
        source = (Path(__file__).resolve().parents[2] / "pages" / "09_Data_Upload.py").read_text(encoding="utf-8")
        self.assertIn("priority_gaps = missing_priority_summary(comparison_rows(views))", source)
        self.assertIn("data_ready = canonical.is_valid and not priority_gaps.has_high_priority_gap", source)
        self.assertIn('disabled=priority_gaps.has_high_priority_gap', source)
        self.assertIn("Provisional triage notes do not satisfy source evidence requirements.", source)

    def test_major_incomplete_is_high_priority(self):
        summary = missing_priority_summary([{
            "Parameter": "External Length",
            "Criticality": "Major",
            "Comparison Status": "Incomplete",
        }])
        self.assertTrue(summary.has_high_priority_gap)
        self.assertEqual(summary.major, ("External Length",))

    def test_minor_incomplete_is_not_high_priority(self):
        summary = missing_priority_summary([{
            "Parameter": "Effective Date",
            "Criticality": "Minor",
            "Comparison Status": "Incomplete",
        }])
        self.assertFalse(summary.has_high_priority_gap)


if __name__ == "__main__":
    unittest.main()
