from __future__ import annotations

import unittest

from src.specification_intake import (
    DocumentRole,
    PairFormat,
    UnifiedSpecificationDocument,
    build_pair,
    classify_pair,
)
from src.upload_routing import FileFormat


def _document(role: DocumentRole, file_format: FileFormat, sha256: str) -> UnifiedSpecificationDocument:
    return UnifiedSpecificationDocument(
        filename=f"{role.value}.{file_format.value}",
        document_role=role,
        document_format=file_format,
        sha256=sha256,
        parser_name=f"{file_format.value}-parser",
        parser_version="v1",
    )


class PairingTests(unittest.TestCase):
    def test_all_approved_pair_formats(self) -> None:
        self.assertEqual(PairFormat.PDF_PDF, classify_pair(FileFormat.PDF, FileFormat.PDF))
        self.assertEqual(PairFormat.DOCX_DOCX, classify_pair(FileFormat.DOCX, FileFormat.DOCX))
        self.assertEqual(PairFormat.PDF_DOCX, classify_pair(FileFormat.PDF, FileFormat.DOCX))
        self.assertEqual(PairFormat.DOCX_PDF, classify_pair(FileFormat.DOCX, FileFormat.PDF))

    def test_builds_mixed_pair(self) -> None:
        pair = build_pair(
            (
                _document(DocumentRole.EXISTING, FileFormat.PDF, "a" * 64),
                _document(DocumentRole.PROPOSED, FileFormat.DOCX, "b" * 64),
            )
        )
        self.assertEqual(PairFormat.PDF_DOCX, pair.pair_format)

    def test_rejects_duplicate_content(self) -> None:
        documents = (
            _document(DocumentRole.EXISTING, FileFormat.PDF, "a" * 64),
            _document(DocumentRole.PROPOSED, FileFormat.DOCX, "a" * 64),
        )
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            build_pair(documents)

    def test_rejects_duplicate_role(self) -> None:
        documents = (
            _document(DocumentRole.EXISTING, FileFormat.PDF, "a" * 64),
            _document(DocumentRole.EXISTING, FileFormat.DOCX, "b" * 64),
        )
        with self.assertRaisesRegex(ValueError, "Exactly one existing"):
            build_pair(documents)


if __name__ == "__main__":
    unittest.main()
