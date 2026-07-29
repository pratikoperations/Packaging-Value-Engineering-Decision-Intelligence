from __future__ import annotations

import unittest
from types import SimpleNamespace

from src.review_comparison import ReviewState
from src.specification_intake.comparison_presentation import FIELD_CRITICALITY, comparison_rows, filter_comparison_rows, missing_priority_summary
from src.specification_intake.models import DocumentRole


def make_view(field_name, role, value, unit=None, state=ReviewState.PENDING, corrected=None, corrected_unit=None):
    return SimpleNamespace(
        field_name=field_name,
        document_role=role,
        normalized_value=value,
        unit=unit,
        review=SimpleNamespace(state=state, corrected_value=corrected, corrected_unit=corrected_unit),
    )


class ComparisonPresentationTests(unittest.TestCase):
    def test_all_fields_have_priority(self):
        self.assertEqual(len(FIELD_CRITICALITY), 25)
        self.assertEqual(FIELD_CRITICALITY["box_weight"].value, "Critical")
        self.assertEqual(FIELD_CRITICALITY["item_code"].value, "Major")
        self.assertEqual(FIELD_CRITICALITY["supplier_name"].value, "Minor")

    def test_rows_use_corrected_value(self):
        rows = comparison_rows((
            make_view("box_weight", DocumentRole.EXISTING, 980, "g"),
            make_view("box_weight", DocumentRole.PROPOSED, 820, "g", ReviewState.CORRECTED_CONFIRMED, 815, "g"),
        ))
        row = next(item for item in rows if item["Parameter"] == "Box Weight")
        self.assertEqual(row["Existing"], "980 g")
        self.assertEqual(row["Proposed"], "815 g")
        self.assertEqual(row["Comparison Status"], "Changed")
        self.assertEqual(row["Criticality"], "Critical")

    def test_filters_apply_status_and_priority(self):
        rows = comparison_rows((
            make_view("box_weight", DocumentRole.EXISTING, 980, "g"),
            make_view("box_weight", DocumentRole.PROPOSED, 820, "g"),
            make_view("supplier_name", DocumentRole.EXISTING, "A"),
            make_view("supplier_name", DocumentRole.PROPOSED, "A"),
        ))
        filtered = filter_comparison_rows(rows, statuses=("Changed",), criticalities=("Critical",))
        self.assertEqual([row["Parameter"] for row in filtered], ["Box Weight"])

    def test_missing_summary_groups_priority(self):
        rows = comparison_rows((
            make_view("box_weight", DocumentRole.EXISTING, 980, "g"),
            make_view("item_code", DocumentRole.EXISTING, "CASE-1"),
            make_view("supplier_name", DocumentRole.EXISTING, "Supplier A"),
        ))
        gaps = missing_priority_summary(rows)
        self.assertIn("Box Weight", gaps.critical)
        self.assertIn("Item Code", gaps.major)
        self.assertIn("Supplier Name", gaps.minor)
        self.assertTrue(gaps.has_high_priority_gap)


if __name__ == "__main__":
    unittest.main()
