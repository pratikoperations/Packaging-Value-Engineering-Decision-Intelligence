from __future__ import annotations

import hashlib
import unittest

from src.drawing_preview import build_preview_descriptor


class DrawingPreviewBuild2BTests(unittest.TestCase):
    @staticmethod
    def record(file_format: str, content: bytes, **overrides):
        value = {
            "drawing_evidence_id": "drawing-evidence-1",
            "document_type": "drawing",
            "document_number": "DRW-001",
            "title": "Shipping case",
            "revision": "B",
            "classification": "proposed",
            "file_format": file_format,
            "source_reference": f"controlled://drawings/DRW-001-B.{file_format}",
            "source_classification": "uploaded_fact",
            "validation_status": "validated",
            "approval_status": "approval_required",
            "content_hash": hashlib.sha256(content).hexdigest(),
        }
        value.update(overrides)
        return value

    def test_png_preview_and_metadata(self):
        content = b"\x89PNG\r\n\x1a\npreview"
        descriptor = build_preview_descriptor(self.record("png", content), content)
        self.assertTrue(descriptor.available)
        self.assertEqual(descriptor.mode, "image")
        self.assertEqual(descriptor.mime_type, "image/png")
        self.assertEqual(descriptor.metadata["classification"], "proposed")

    def test_jpeg_preview(self):
        content = b"\xff\xd8\xffpreview"
        descriptor = build_preview_descriptor(self.record("jpeg", content), content)
        self.assertTrue(descriptor.available)
        self.assertEqual(descriptor.mime_type, "image/jpeg")

    def test_pdf_is_embedded_without_parsing(self):
        content = b"%PDF-1.7\nsynthetic preview"
        descriptor = build_preview_descriptor(self.record("pdf", content), content)
        self.assertTrue(descriptor.available)
        self.assertEqual(descriptor.mode, "pdf_embed")
        self.assertIsInstance(descriptor.payload, str)
        self.assertIn("not interpreted", " ".join(descriptor.limitations))

    def test_safe_svg_preview(self):
        content = b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10"/></svg>'
        descriptor = build_preview_descriptor(self.record("svg", content), content)
        self.assertTrue(descriptor.available)
        self.assertEqual(descriptor.mode, "svg")

    def test_active_svg_is_rejected(self):
        content = b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
        descriptor = build_preview_descriptor(self.record("svg", content), content)
        self.assertFalse(descriptor.available)
        self.assertEqual(descriptor.issues[0].code, "unsafe_svg")

    def test_checksum_mismatch_blocks_preview(self):
        content = b"\x89PNG\r\n\x1a\npreview"
        record = self.record("png", content, content_hash="0" * 64)
        descriptor = build_preview_descriptor(record, content)
        self.assertFalse(descriptor.available)
        self.assertEqual(descriptor.issues[0].code, "checksum_mismatch")

    def test_dxf_and_dwg_use_explicit_fallback(self):
        for file_format in ("dxf", "dwg"):
            with self.subTest(file_format=file_format):
                content = b"reference only"
                descriptor = build_preview_descriptor(self.record(file_format, content), content)
                self.assertFalse(descriptor.available)
                self.assertEqual(descriptor.mode, "fallback")
                self.assertEqual(descriptor.issues[0].code, "unsupported_preview_format")

    def test_invalid_signatures_and_large_content_are_rejected(self):
        invalid = build_preview_descriptor(self.record("pdf", b"not-pdf"), b"not-pdf")
        self.assertEqual(invalid.issues[0].code, "invalid_pdf_signature")
        too_large = b"x" * (10 * 1024 * 1024 + 1)
        descriptor = build_preview_descriptor(self.record("png", too_large), too_large)
        self.assertFalse(descriptor.available)
        self.assertEqual(descriptor.issues[0].code, "preview_too_large")


if __name__ == "__main__":
    unittest.main()
