from __future__ import annotations

import unittest

from src.application.specification_upload import classify_triage_source_support
from src.specification_intake.models import DocumentRole, UnifiedSourceBlock, UnifiedSpecificationDocument
from src.upload_routing.models import FileFormat


class TriageSourceSupportTests(unittest.TestCase):
    def setUp(self):
        block = UnifiedSourceBlock(
            block_id="existing:pdf:page1:block2",
            document_role=DocumentRole.EXISTING,
            document_format=FileFormat.PDF,
            raw_text="Box Weight: 790 g",
            normalized_text="Box Weight: 790 g",
            extraction_order=2,
            parser_name="synthetic",
            parser_version="v1",
            source_location={"type": "pdf", "page_number": 1, "block_index": 2},
        )
        self.document = UnifiedSpecificationDocument(
            filename="existing.pdf",
            document_role=DocumentRole.EXISTING,
            document_format=FileFormat.PDF,
            sha256="a" * 64,
            parser_name="synthetic",
            parser_version="v1",
            source_blocks=(block,),
        )

    def classify(self, source, value):
        return classify_triage_source_support(
            document=self.document, source_block_id=source, proposed_value=value
        )

    def test_exact_literal_supported(self):
        self.assertEqual(self.classify("existing:pdf:page1:block2", "790 g"), "literal_value_present")

    def test_unsupported_claim_not_verified(self):
        self.assertEqual(self.classify("existing:pdf:page1:block2", "900 g"), "source_block_requires_manual_verification")

    def test_cross_document_or_forged_reference_rejected(self):
        self.assertEqual(self.classify("proposed:pdf:page1:block2", "790 g"), "invalid_source_reference")

    def test_empty_value_not_supported(self):
        self.assertEqual(self.classify("existing:pdf:page1:block2", " "), "value_missing")


if __name__ == "__main__":
    unittest.main()
