from __future__ import annotations

import unittest

from src.review_comparison import ReviewState
from src.specification_intake import (
    DocumentRole,
    UnifiedCanonicalDraft,
    UnifiedSourceBlock,
    UnifiedSpecificationDocument,
    apply_review_action,
    build_common_review_views,
    build_pair,
    build_unified_snapshot,
)
from src.upload_routing import FileFormat


def _document(role: DocumentRole, fmt: FileFormat, digest: str, value: str):
    parser_name = "pypdf" if fmt is FileFormat.PDF else "docx-ooxml"
    parser_version = "pve-pdf-parser-v1" if fmt is FileFormat.PDF else "pve-docx-parser-v1"
    location = (
        {"type": "pdf", "page_number": 1, "block_index": 0}
        if fmt is FileFormat.PDF
        else {"type": "docx", "section_title": "Specification", "paragraph_index": 0}
    )
    block = UnifiedSourceBlock(
        block_id=f"{role.value}-weight",
        document_role=role,
        document_format=fmt,
        raw_text=f"Box weight: {value}",
        normalized_text=f"Box weight: {value}",
        extraction_order=0,
        parser_name=parser_name,
        parser_version=parser_version,
        source_location=location,
    )
    return UnifiedSpecificationDocument(
        filename=f"{role.value}.{fmt.value}",
        document_role=role,
        document_format=fmt,
        sha256=digest,
        parser_name=parser_name,
        parser_version=parser_version,
        source_blocks=(block,),
    )


class UnifiedSnapshotBuilderTests(unittest.TestCase):
    def setUp(self):
        self.pair = build_pair((
            _document(DocumentRole.EXISTING, FileFormat.PDF, "a" * 64, "780 g"),
            _document(DocumentRole.PROPOSED, FileFormat.DOCX, "b" * 64, "650 g"),
        ))
        reviews = []
        for view in build_common_review_views(self.pair):
            reviews.append(apply_review_action(view, ReviewState.CONFIRMED))
        self.views = tuple(reviews)
        self.canonical = UnifiedCanonicalDraft(
            canonical_data={"dataset_type": "synthetic_demo", "packaging_alternatives": []},
            validation_issues=({"code": "example", "path": "root", "message": "controlled"},),
            is_valid=False,
        )

    def test_snapshot_preserves_pair_documents_fields_and_typed_locations(self):
        snapshot = build_unified_snapshot(
            project_id="P1",
            pair=self.pair,
            views=self.views,
            canonical=self.canonical,
            snapshot_id="SNAP-1",
        )
        self.assertEqual(snapshot.pair_format, "pdf_docx")
        self.assertEqual(snapshot.existing_document.format, "pdf")
        self.assertEqual(snapshot.proposed_document.format, "docx")
        self.assertEqual(snapshot.existing_document.sha256, "a" * 64)
        self.assertEqual(snapshot.proposed_document.sha256, "b" * 64)
        self.assertEqual(len(snapshot.confirmed_fields), 2)
        locations = {field.document_role: field.source_location for field in snapshot.confirmed_fields}
        self.assertEqual(locations["existing"]["type"], "pdf")
        self.assertEqual(locations["proposed"]["type"], "docx")
        self.assertFalse(snapshot.canonical_validation_valid)
        self.assertEqual(snapshot.snapshot_id, "SNAP-1")

    def test_content_hash_is_deterministic_and_changes_with_source_hash(self):
        first = build_unified_snapshot(
            project_id="P1", pair=self.pair, views=self.views, canonical=self.canonical
        )
        second = build_unified_snapshot(
            project_id="P1", pair=self.pair, views=self.views, canonical=self.canonical
        )
        self.assertEqual(first.content_hash, second.content_hash)

        changed_pair = build_pair((
            _document(DocumentRole.EXISTING, FileFormat.PDF, "c" * 64, "780 g"),
            self.pair.proposed,
        ))
        changed_views = tuple(
            apply_review_action(view, ReviewState.CONFIRMED)
            for view in build_common_review_views(changed_pair)
        )
        changed = build_unified_snapshot(
            project_id="P1", pair=changed_pair, views=changed_views, canonical=self.canonical
        )
        self.assertNotEqual(first.content_hash, changed.content_hash)

    def test_pending_reviews_and_empty_confirmed_set_are_rejected(self):
        pending = build_common_review_views(self.pair)
        with self.assertRaisesRegex(ValueError, "must be reviewed"):
            build_unified_snapshot(
                project_id="P1", pair=self.pair, views=pending, canonical=self.canonical
            )

        rejected = tuple(
            apply_review_action(view, ReviewState.REJECTED, reviewer_note="Not accepted")
            for view in build_common_review_views(self.pair)
        )
        with self.assertRaisesRegex(ValueError, "At least one confirmed"):
            build_unified_snapshot(
                project_id="P1", pair=self.pair, views=rejected, canonical=self.canonical
            )


if __name__ == "__main__":
    unittest.main()
