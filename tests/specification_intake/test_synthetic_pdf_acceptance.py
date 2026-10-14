from __future__ import annotations

import io
import unittest

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from src.review_comparison import ReviewState
from src.specification_intake import (
    DocumentRole, adapt_pdf, build_pair, build_common_review_views, apply_review_action,
)
from src.specification_intake.comparison_presentation import comparison_rows, missing_priority_summary


COMMON = {
    "Specification Number": "PVE-CORR-DEMO",
    "Specification Revision": "1",
    "Item Code": "CASE-001",
    "Item Description": "Synthetic corrugated shipper",
    "Box Style": "FEFCO 0201",
    "Internal Length": "400",
    "Internal Width": "300",
    "Internal Height": "250",
    "External Length": "414",
    "External Width": "314",
    "External Height": "264",
    "Dimension Unit": "mm",
    "Joint Type": "Glued",
    "Closure Method": "BOPP tape",
    "Ply Count": "5",
    "Flute Combination": "BC",
    "Liner GSM": "180",
    "Medium GSM": "150",
    "Paper Grade": "Kraft mix",
    "Box Weight Unit": "kg",
    "Compression Requirement": "3800",
    "Total Board GSM": "810",
    "Box Weight": "0.92",
}


def synthetic_searchable_pdf(fields: dict[str, str]) -> bytes:
    """Create a real searchable PDF with alternating row labels/values."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})
    })
    lines = ["Parameter", "Value / requirement"]
    for label, value in fields.items():
        lines.extend((label, value))
    escaped = [
        "(" + line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ") Tj"
        for line in lines
    ]
    commands = "BT /F1 10 Tf 40 740 Td " + " 0 -13 Td ".join(escaped) + " ET"
    stream = DecodedStreamObject()
    stream.set_data(commands.encode("ascii"))
    page[NameObject("/Contents")] = writer._add_object(stream)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


class SyntheticPdfWorkflowAcceptanceTests(unittest.TestCase):
    def test_complete_25_parameter_specifications_compare_with_no_missing_fields(self):
        existing = dict(COMMON)
        existing.update({
            "Supplier Name": "Synthetic Packaging Supplier A",
            "Effective Date": "2026-10-01",
        })
        proposed = dict(existing)
        proposed.update({
            "Specification Revision": "2",
            "Supplier Name": "Synthetic Packaging Supplier B",
            "Effective Date": "2026-10-14",
            "External Length": "412",
            "External Width": "312",
            "External Height": "262",
            "Liner GSM": "160",
            "Medium GSM": "130",
            "Total Board GSM": "700",
            "Box Weight": "0.79",
            "Compression Requirement": "3400",
        })
        pair = build_pair((
            adapt_pdf("existing_complete.pdf", synthetic_searchable_pdf(existing), DocumentRole.EXISTING),
            adapt_pdf("proposed_complete.pdf", synthetic_searchable_pdf(proposed), DocumentRole.PROPOSED),
        ))
        views = build_common_review_views(pair)
        self.assertEqual(len(views), 50, "All 25 governed fields should be extracted from each PDF")
        self.assertEqual(len({(view.document_role, view.field_name) for view in views}), 50)
        self.assertTrue(all(view.source_block_id and view.source_excerpt for view in views))
        reviewed = tuple(
            apply_review_action(view, ReviewState.CONFIRMED, reviewer_note="Synthetic-only reviewer acceptance")
            for view in views
        )
        rows = comparison_rows(reviewed)
        self.assertEqual(len(rows), 25)
        self.assertFalse(any(row["Comparison Status"] == "Incomplete" for row in rows))
        self.assertFalse(missing_priority_summary(rows).has_high_priority_gap)
        by_name = {row["Parameter"]: row for row in rows}
        self.assertEqual(by_name["Internal Length"]["Comparison Status"], "Unchanged")
        self.assertEqual(by_name["External Length"]["Comparison Status"], "Changed")
        self.assertEqual(by_name["Box Weight"]["Existing"], "0.92")
        self.assertEqual(by_name["Box Weight"]["Proposed"], "0.79")
        self.assertEqual(by_name["Compression Requirement"]["Proposed"], "3400")

    def test_existing_proposed_pdf_parse_review_and_priority_readiness(self):
        old = dict(COMMON)
        proposed = dict(COMMON, **{"Box Weight": "0.79", "Compression Requirement": "3400", "Total Board GSM": "675"})
        documents = (
            adapt_pdf("existing.pdf", synthetic_searchable_pdf(old), DocumentRole.EXISTING),
            adapt_pdf("proposed.pdf", synthetic_searchable_pdf(proposed), DocumentRole.PROPOSED),
        )
        pair = build_pair(documents)
        views = build_common_review_views(pair)
        self.assertEqual(len(views), len(COMMON) * 2)
        pending_rows = comparison_rows(views)
        self.assertIn("Box Weight", missing_priority_summary(pending_rows).critical)
        reviewed = tuple(
            apply_review_action(view, ReviewState.CONFIRMED, reviewer_note="Synthetic test confirmation")
            for view in views
        )
        rows = comparison_rows(reviewed)
        gaps = missing_priority_summary(rows)
        self.assertFalse(gaps.has_high_priority_gap)
        self.assertEqual(gaps.minor, ("Effective Date", "Supplier Name"))
        by_field = {row["Parameter"]: row for row in rows}
        self.assertEqual(by_field["Box Weight"]["Existing"], "0.92")
        self.assertEqual(by_field["Box Weight"]["Proposed"], "0.79")
        self.assertEqual(by_field["Compression Requirement"]["Proposed"], "3400")
        self.assertEqual(by_field["Box Weight"]["Comparison Status"], "Changed")
        self.assertTrue(all(view.source_block_id and view.source_location for view in views))


if __name__ == "__main__":
    unittest.main()
