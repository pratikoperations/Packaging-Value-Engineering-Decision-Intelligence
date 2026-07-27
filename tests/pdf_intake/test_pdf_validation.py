from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.document_intake import DocumentRole
from src.pdf_intake import PdfEligibility, PdfValidationError, validate_pdf, validate_pdf_pair


class FakePage:
    def __init__(self, text: str):
        self.text = text

    def extract_text(self):
        return self.text


class FakeReader:
    def __init__(self, pages, *, encrypted=False):
        self.pages = pages
        self.is_encrypted = encrypted


class PdfValidationTests(unittest.TestCase):
    @patch("src.pdf_intake.file_validation.PdfReader")
    def test_accepts_searchable_pdf_and_hashes_content(self, reader_cls):
        reader_cls.return_value = FakeReader([FakePage("Specification " * 20)])
        result = validate_pdf("existing.pdf", b"%PDF-searchable", DocumentRole.EXISTING)
        self.assertEqual(result.eligibility, PdfEligibility.SEARCHABLE)
        self.assertEqual(result.page_count, 1)
        self.assertEqual(len(result.sha256), 64)

    def test_rejects_extension_mime_signature_empty_and_size(self):
        with self.assertRaises(PdfValidationError):
            validate_pdf("x.docx", b"%PDF-x", DocumentRole.EXISTING)
        with self.assertRaises(PdfValidationError):
            validate_pdf("x.pdf", b"%PDF-x", DocumentRole.EXISTING, mime_type="text/plain")
        with self.assertRaises(PdfValidationError):
            validate_pdf("x.pdf", b"not-pdf", DocumentRole.EXISTING)
        with self.assertRaises(PdfValidationError):
            validate_pdf("x.pdf", b"", DocumentRole.EXISTING)
        with self.assertRaises(PdfValidationError):
            validate_pdf("x.pdf", b"%PDF-" + b"x" * 20, DocumentRole.EXISTING, max_bytes=10)

    @patch("src.pdf_intake.file_validation.PdfReader")
    def test_rejects_encrypted_pdf(self, reader_cls):
        reader_cls.return_value = FakeReader([FakePage("Specification " * 20)], encrypted=True)
        with self.assertRaisesRegex(PdfValidationError, "Encrypted"):
            validate_pdf("x.pdf", b"%PDF-encrypted", DocumentRole.EXISTING)

    @patch("src.pdf_intake.file_validation.PdfReader")
    def test_rejects_page_limit(self, reader_cls):
        reader_cls.return_value = FakeReader([FakePage("Specification") for _ in range(3)])
        with self.assertRaisesRegex(PdfValidationError, "page limit"):
            validate_pdf("x.pdf", b"%PDF-pages", DocumentRole.EXISTING, max_pages=2)

    @patch("src.pdf_intake.file_validation.PdfReader")
    def test_rejects_image_only_and_insufficient_text(self, reader_cls):
        reader_cls.return_value = FakeReader([FakePage("")])
        with self.assertRaisesRegex(PdfValidationError, "scanned_or_image_only"):
            validate_pdf("scan.pdf", b"%PDF-scan", DocumentRole.EXISTING)
        reader_cls.return_value = FakeReader([FakePage("short")])
        with self.assertRaisesRegex(PdfValidationError, "insufficient_extractable_text"):
            validate_pdf("short.pdf", b"%PDF-short", DocumentRole.EXISTING)

    @patch("src.pdf_intake.file_validation.PdfReader")
    def test_pair_requires_roles_and_rejects_duplicates(self, reader_cls):
        reader_cls.side_effect = [
            FakeReader([FakePage("Existing specification " * 10)]),
            FakeReader([FakePage("Proposed specification " * 10)]),
        ]
        existing = validate_pdf("existing.pdf", b"%PDF-existing", DocumentRole.EXISTING)
        proposed = validate_pdf("proposed.pdf", b"%PDF-proposed", DocumentRole.PROPOSED)
        resolved = validate_pdf_pair((proposed, existing))
        self.assertEqual(resolved[0].role, DocumentRole.EXISTING)
        self.assertEqual(resolved[1].role, DocumentRole.PROPOSED)

        duplicate = SimpleNamespace(**{**proposed.__dict__, "sha256": existing.sha256})
        with self.assertRaisesRegex(PdfValidationError, "duplicates"):
            validate_pdf_pair((existing, duplicate))
        with self.assertRaisesRegex(PdfValidationError, "Exactly two"):
            validate_pdf_pair((existing,))


if __name__ == "__main__":
    unittest.main()
