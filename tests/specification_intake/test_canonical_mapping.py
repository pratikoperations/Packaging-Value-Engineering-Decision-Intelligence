from __future__ import annotations

import unittest

from src.review_comparison import ReviewError, ReviewState
from src.specification_intake import (
    DocumentRole,
    UnifiedSourceBlock,
    UnifiedSpecificationDocument,
    apply_review_action,
    build_common_review_views,
    build_pair,
    build_unified_canonical_draft,
    normalize_corrected_value,
)
from src.upload_routing import FileFormat


def document(role: DocumentRole, fmt: FileFormat, sha: str, weight: str, ply: str):
    parser = "pypdf" if fmt is FileFormat.PDF else "docx-ooxml"
    version = "pve-pdf-parser-v1" if fmt is FileFormat.PDF else "pve-docx-parser-v1"
    location = (
        {"type": "pdf", "page_number": 1, "block_index": 0}
        if fmt is FileFormat.PDF
        else {"type": "docx", "paragraph_index": 0, "section_title": "Specification"}
    )
    blocks = (
        UnifiedSourceBlock(
            block_id=f"{sha}-weight",
            document_role=role,
            document_format=fmt,
            raw_text=f"Box weight: {weight}",
            normalized_text=f"Box weight: {weight}",
            extraction_order=0,
            parser_name=parser,
            parser_version=version,
            source_location=location,
        ),
        UnifiedSourceBlock(
            block_id=f"{sha}-ply",
            document_role=role,
            document_format=fmt,
            raw_text=f"Ply count: {ply}",
            normalized_text=f"Ply count: {ply}",
            extraction_order=1,
            parser_name=parser,
            parser_version=version,
            source_location={**location, "block_index": 1} if fmt is FileFormat.PDF else {**location, "paragraph_index": 1},
        ),
    )
    return UnifiedSpecificationDocument(
        filename=f"{role.value}.{fmt.value}",
        document_role=role,
        document_format=fmt,
        sha256=sha,
        parser_name=parser,
        parser_version=version,
        source_blocks=blocks,
    )


class UnifiedCanonicalMappingTests(unittest.TestCase):
    def setUp(self):
        self.pair = build_pair((
            document(DocumentRole.EXISTING, FileFormat.PDF, "a" * 64, "780 g", "5 ply"),
            document(DocumentRole.PROPOSED, FileFormat.DOCX, "b" * 64, "650 g", "3 ply"),
        ))
        self.project = {
            "project_id": "PRJ-001",
            "project_name": "Synthetic value engineering",
            "category": "corrugated_boxes",
            "annual_volume": 100000,
            "volume_unit": "cases_per_year",
            "currency": "INR",
            "status": "active",
            "archived_at": None,
        }

    def test_maps_only_confirmed_and_corrected_confirmed_with_lineage(self):
        views = list(build_common_review_views(self.pair))
        for index, view in enumerate(views):
            if view.document_role is DocumentRole.EXISTING and view.field_name == "box_weight":
                views[index] = apply_review_action(view, ReviewState.CONFIRMED)
            elif view.document_role is DocumentRole.PROPOSED and view.field_name == "box_weight":
                views[index] = apply_review_action(
                    view,
                    ReviewState.CORRECTED_CONFIRMED,
                    corrected_value="640 g",
                    corrected_unit=None,
                    reviewer_note="Confirmed against controlled source.",
                )
            elif view.document_role is DocumentRole.EXISTING:
                views[index] = apply_review_action(
                    view, ReviewState.INTENTIONALLY_OMITTED, reviewer_note="Not required for this draft."
                )
            else:
                views[index] = apply_review_action(
                    view, ReviewState.REJECTED, reviewer_note="Source value rejected for this draft."
                )

        result = build_unified_canonical_draft(
            project=self.project,
            pair=self.pair,
            views=tuple(views),
            source_repository="example/repository",
            source_commit="draft-sha",
        )
        alternatives = {item["status"]: item for item in result.canonical_data["packaging_alternatives"]}
        self.assertEqual(alternatives["baseline"]["case_weight_g"], 780)
        self.assertEqual(alternatives["proposed"]["case_weight_g"], 640)
        self.assertNotIn("ply_count", alternatives["baseline"]["specification_intake_confirmed_fields"])
        proposed = alternatives["proposed"]["specification_intake_confirmed_fields"]["box_weight"]
        self.assertEqual(proposed["raw_value"], "650 g")
        self.assertEqual(proposed["normalized_value"], 650)
        self.assertEqual(proposed["corrected_value"], 640)
        self.assertEqual(proposed["corrected_unit"], "g")
        self.assertEqual(proposed["source_format"], "docx")
        self.assertEqual(proposed["document_sha256"], "b" * 64)
        self.assertEqual(proposed["parser_version"], "pve-docx-parser-v1")
        self.assertEqual(result.canonical_data["decision_evidence"][0]["evidence_type"], "uploaded_pdf_specification")
        self.assertEqual(result.canonical_data["decision_evidence"][1]["evidence_type"], "uploaded_docx_specification")

    def test_pending_review_blocks_mapping(self):
        with self.assertRaisesRegex(ValueError, "must be reviewed"):
            build_unified_canonical_draft(
                project=self.project,
                pair=self.pair,
                views=build_common_review_views(self.pair),
                source_repository="example/repository",
                source_commit="draft-sha",
            )

    def test_numeric_corrections_are_typed_and_invalid_text_is_rejected(self):
        self.assertEqual(normalize_corrected_value("box_weight", "640 g", None), (640, "g"))
        self.assertEqual(normalize_corrected_value("item_code", "  ABC-01  ", None), ("ABC-01", None))
        with self.assertRaises(ReviewError):
            normalize_corrected_value("box_weight", "not numeric", "g")


if __name__ == "__main__":
    unittest.main()
