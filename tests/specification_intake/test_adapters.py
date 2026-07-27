from __future__ import annotations

import io
import unittest
import zipfile
from unittest.mock import patch

from src.document_intake import DocumentRole as LegacyDocumentRole
from src.pdf_intake.models import ParsedPdf, PdfLayoutWarning, PdfSourceBlock, ValidatedPdf, PdfEligibility
from src.specification_intake import DocumentRole, adapt_docx, adapt_pdf
from src.upload_routing.models import FileFormat

CONTENT_TYPES = b'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''


def make_docx() -> bytes:
    document_xml = b'''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Specification</w:t></w:r></w:p>
    <w:p><w:r><w:t>Box weight: 780 g</w:t></w:r></w:p>
  </w:body>
</w:document>'''
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("word/document.xml", document_xml)
    return buffer.getvalue()


class SpecificationAdapterTests(unittest.TestCase):
    def test_docx_adapter_preserves_hash_role_parser_and_source_location(self):
        document = adapt_docx("existing.docx", make_docx(), DocumentRole.EXISTING)
        self.assertEqual(document.document_format, FileFormat.DOCX)
        self.assertEqual(document.document_role, DocumentRole.EXISTING)
        self.assertEqual(len(document.sha256), 64)
        self.assertEqual(document.parser_version, "pve-docx-parser-v1")
        self.assertEqual(document.source_blocks[0].source_location["type"], "docx")
        self.assertEqual(document.source_blocks[0].source_location["section_title"], "Specification")

    def test_pdf_adapter_preserves_page_lineage_and_warnings(self):
        validated = ValidatedPdf(
            filename="proposed.pdf",
            role=LegacyDocumentRole.PROPOSED,
            content=b"%PDF-fake",
            sha256="b" * 64,
            page_count=1,
            extracted_character_count=200,
            pages_with_meaningful_text=1,
            eligibility=PdfEligibility.SEARCHABLE,
        )
        parsed = ParsedPdf(
            filename="proposed.pdf",
            role=LegacyDocumentRole.PROPOSED,
            sha256="b" * 64,
            page_count=1,
            parser_version="pve-pdf-parser-v1",
            blocks=(
                PdfSourceBlock(
                    block_id="pdfsrc_1",
                    page_number=2,
                    block_index=3,
                    extraction_order=0,
                    raw_text="Box weight: 650 g",
                    normalized_text="Box weight: 650 g",
                    parser_version="pve-pdf-parser-v1",
                    warnings=(PdfLayoutWarning.TABLE_LIKE_CONTENT,),
                ),
            ),
            warnings=(PdfLayoutWarning.TABLE_LIKE_CONTENT,),
        )
        with patch("src.specification_intake.adapters.validate_pdf", return_value=validated), patch(
            "src.specification_intake.adapters.parse_validated_pdf", return_value=parsed
        ):
            document = adapt_pdf("proposed.pdf", b"%PDF-fake", DocumentRole.PROPOSED)
        self.assertEqual(document.document_format, FileFormat.PDF)
        self.assertEqual(document.document_role, DocumentRole.PROPOSED)
        self.assertEqual(document.parser_name, "pypdf")
        self.assertEqual(document.source_blocks[0].source_location, {"type": "pdf", "page_number": 2, "block_index": 3})
        self.assertEqual(document.source_blocks[0].warnings, ("table_like_content",))


if __name__ == "__main__":
    unittest.main()
