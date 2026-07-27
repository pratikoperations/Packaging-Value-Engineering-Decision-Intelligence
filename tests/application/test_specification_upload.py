from __future__ import annotations

import unittest
from unittest.mock import patch

from src.application.specification_upload import (
    SpecificationUploadInput,
    parse_specification_pair,
    source_block_rows,
)
from src.specification_intake import DocumentRole, UnifiedSourceBlock, UnifiedSpecificationDocument
from src.upload_routing.models import DetectedUpload, DetectionStatus, FileFormat, WorkflowKind


def detected(filename: str, file_format: FileFormat, sha: str) -> DetectedUpload:
    return DetectedUpload(
        filename=filename,
        mime_type="application/octet-stream",
        sha256=sha,
        file_format=file_format,
        workflow=WorkflowKind.SPECIFICATION_COMPARISON,
        status=DetectionStatus.ROLE_REQUIRED,
    )


def document(filename: str, file_format: FileFormat, role: DocumentRole, sha: str):
    location = {"type": "pdf", "page_number": 1, "block_index": 0} if file_format is FileFormat.PDF else {
        "type": "docx",
        "paragraph_index": 1,
        "table_index": None,
        "row_index": None,
        "cell_index": None,
        "section_title": "Specification",
    }
    return UnifiedSpecificationDocument(
        filename=filename,
        document_role=role,
        document_format=file_format,
        sha256=sha,
        parser_name="parser",
        parser_version="v1",
        source_blocks=(
            UnifiedSourceBlock(
                block_id=f"block-{sha}",
                document_role=role,
                document_format=file_format,
                raw_text="Box weight: 780 g",
                normalized_text="Box weight: 780 g",
                extraction_order=0,
                parser_name="parser",
                parser_version="v1",
                source_location=location,
            ),
        ),
    )


class SpecificationUploadTests(unittest.TestCase):
    def test_routes_mixed_pdf_docx_pair_and_preserves_roles(self):
        existing_detection = detected("existing.pdf", FileFormat.PDF, "a" * 64)
        proposed_detection = detected("proposed.docx", FileFormat.DOCX, "b" * 64)
        inputs = (
            SpecificationUploadInput("existing.pdf", "application/pdf", b"pdf", existing_detection, DocumentRole.EXISTING),
            SpecificationUploadInput("proposed.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", b"docx", proposed_detection, DocumentRole.PROPOSED),
        )
        outputs = [
            document("existing.pdf", FileFormat.PDF, DocumentRole.EXISTING, "a" * 64),
            document("proposed.docx", FileFormat.DOCX, DocumentRole.PROPOSED, "b" * 64),
        ]
        with patch("src.application.specification_upload.adapt_specification", side_effect=outputs):
            pair = parse_specification_pair(inputs)
        self.assertEqual(pair.existing.document_format, FileFormat.PDF)
        self.assertEqual(pair.proposed.document_format, FileFormat.DOCX)
        self.assertEqual(pair.pair_format.value, "pdf_docx")
        self.assertEqual(len(source_block_rows(pair)), 2)

    def test_rejects_non_specification_format(self):
        invalid = detected("project.json", FileFormat.JSON, "a" * 64)
        valid = detected("proposed.pdf", FileFormat.PDF, "b" * 64)
        with self.assertRaisesRegex(ValueError, "Only DOCX"):
            parse_specification_pair((
                SpecificationUploadInput("project.json", "application/json", b"{}", invalid, DocumentRole.EXISTING),
                SpecificationUploadInput("proposed.pdf", "application/pdf", b"pdf", valid, DocumentRole.PROPOSED),
            ))


if __name__ == "__main__":
    unittest.main()
