from __future__ import annotations

import unittest
from unittest.mock import patch

from src.document_intake import DocumentRole
from src.pdf_intake import (
    PDF_PARSER_VERSION,
    PdfEligibility,
    PdfLayoutWarning,
    PdfValidationError,
    ValidatedPdf,
    make_pdf_source_block_id,
    normalize_pdf_text,
    parse_validated_pdf,
)


class FakePage:
    def __init__(self, text=None, error=None):
        self.text = text
        self.error = error

    def extract_text(self):
        if self.error:
            raise self.error
        return self.text


class FakeReader:
    def __init__(self, pages):
        self.pages = pages


def validated(role=DocumentRole.EXISTING, sha="a" * 64, page_count=2):
    return ValidatedPdf(
        filename=f"{role.value}.pdf",
        role=role,
        content=b"%PDF-fake",
        sha256=sha,
        page_count=page_count,
        extracted_character_count=300,
        pages_with_meaningful_text=page_count,
        eligibility=PdfEligibility.SEARCHABLE,
    )


class PdfParserTests(unittest.TestCase):
    def test_extracts_page_blocks_in_stable_order_and_preserves_raw_text(self):
        reader = FakeReader(
            [
                FakePage("Specification\nItem code: ABC\n\nDimensions: 400 x 300 x 250 mm"),
                FakePage("Performance\nBCT requirement: 620 kgf"),
            ]
        )
        with patch("src.pdf_intake.pdf_parser.PdfReader", return_value=reader):
            parsed = parse_validated_pdf(validated())
        self.assertEqual(parsed.page_count, 2)
        self.assertEqual([block.page_number for block in parsed.blocks], [1, 1, 2])
        self.assertEqual([block.extraction_order for block in parsed.blocks], [0, 1, 2])
        self.assertEqual(parsed.blocks[0].raw_text, "Specification\nItem code: ABC")
        self.assertEqual(parsed.blocks[0].normalized_text, "Specification Item code: ABC")
        self.assertEqual(parsed.blocks[1].block_index, 1)
        self.assertEqual(parsed.blocks[2].page_number, 2)

    def test_source_ids_bind_hash_role_page_block_and_parser_version(self):
        first = make_pdf_source_block_id("a" * 64, DocumentRole.EXISTING, 1, 0, "v1")
        repeat = make_pdf_source_block_id("a" * 64, DocumentRole.EXISTING, 1, 0, "v1")
        changed_page = make_pdf_source_block_id("a" * 64, DocumentRole.EXISTING, 2, 0, "v1")
        changed_role = make_pdf_source_block_id("a" * 64, DocumentRole.PROPOSED, 1, 0, "v1")
        changed_version = make_pdf_source_block_id("a" * 64, DocumentRole.EXISTING, 1, 0, "v2")
        self.assertEqual(first, repeat)
        self.assertEqual(len({first, changed_page, changed_role, changed_version}), 4)
        self.assertTrue(first.startswith("pdfsrc_"))

    def test_parser_ids_are_stable_for_same_document_and_text(self):
        reader = FakeReader([FakePage("A\n\nB")])
        with patch("src.pdf_intake.pdf_parser.PdfReader", return_value=reader):
            first = parse_validated_pdf(validated(page_count=1))
        with patch("src.pdf_intake.pdf_parser.PdfReader", return_value=reader):
            second = parse_validated_pdf(validated(page_count=1))
        self.assertEqual([b.block_id for b in first.blocks], [b.block_id for b in second.blocks])
        self.assertEqual(first.parser_version, PDF_PARSER_VERSION)

    def test_detects_table_like_and_multi_column_warnings(self):
        text = "Field        Existing        Proposed\nWeight       780 g           650 g\nFlute        BC              B"
        with patch(
            "src.pdf_intake.pdf_parser.PdfReader",
            return_value=FakeReader([FakePage(text)]),
        ):
            parsed = parse_validated_pdf(validated(page_count=1))
        self.assertIn(PdfLayoutWarning.TABLE_LIKE_CONTENT, parsed.warnings)
        self.assertIn(PdfLayoutWarning.MULTI_COLUMN_SUSPECTED, parsed.warnings)
        self.assertIn(PdfLayoutWarning.TABLE_LIKE_CONTENT, parsed.blocks[0].warnings)

    def test_normalization_does_not_replace_raw_evidence(self):
        raw = "Box   weight:\t780 g\nRevision: 03"
        self.assertEqual(normalize_pdf_text(raw), "Box weight: 780 g Revision: 03")
        with patch(
            "src.pdf_intake.pdf_parser.PdfReader",
            return_value=FakeReader([FakePage(raw)]),
        ):
            parsed = parse_validated_pdf(validated(page_count=1))
        self.assertEqual(parsed.blocks[0].raw_text, raw)
        self.assertNotEqual(parsed.blocks[0].raw_text, parsed.blocks[0].normalized_text)

    def test_rejects_malformed_page_content(self):
        with patch(
            "src.pdf_intake.pdf_parser.PdfReader",
            return_value=FakeReader([FakePage(error=RuntimeError("broken stream"))]),
        ):
            with self.assertRaisesRegex(PdfValidationError, "page 1"):
                parse_validated_pdf(validated(page_count=1))

    def test_rejects_empty_parser_output_and_invalid_version(self):
        with patch(
            "src.pdf_intake.pdf_parser.PdfReader",
            return_value=FakeReader([FakePage("   \n")]),
        ):
            with self.assertRaisesRegex(PdfValidationError, "no extractable source blocks"):
                parse_validated_pdf(validated(page_count=1))
        with self.assertRaisesRegex(PdfValidationError, "Parser version"):
            parse_validated_pdf(validated(page_count=1), parser_version=" ")


if __name__ == "__main__":
    unittest.main()
