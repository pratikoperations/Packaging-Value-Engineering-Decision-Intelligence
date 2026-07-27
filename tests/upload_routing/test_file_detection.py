from __future__ import annotations

import io
import json
import unittest
from zipfile import ZipFile

from src.upload_routing import DetectionStatus, FileFormat, WorkflowKind, detect_upload


def _ooxml(member: str) -> bytes:
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr(member, "content")
    return buffer.getvalue()


class UploadDetectionTests(unittest.TestCase):
    def test_detects_xlsx_as_structured_data(self) -> None:
        result = detect_upload(
            "project.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            _ooxml("xl/workbook.xml"),
        )
        self.assertEqual(FileFormat.XLSX, result.file_format)
        self.assertEqual(WorkflowKind.STRUCTURED_PROJECT_DATA, result.workflow)
        self.assertEqual(DetectionStatus.READY, result.status)

    def test_detects_docx_as_specification(self) -> None:
        result = detect_upload(
            "existing.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            _ooxml("word/document.xml"),
        )
        self.assertEqual(FileFormat.DOCX, result.file_format)
        self.assertEqual(WorkflowKind.SPECIFICATION_COMPARISON, result.workflow)
        self.assertTrue(result.requires_document_role)

    def test_detects_json(self) -> None:
        result = detect_upload("project.json", "application/json", json.dumps({"project": 1}).encode())
        self.assertEqual(FileFormat.JSON, result.file_format)
        self.assertEqual(DetectionStatus.READY, result.status)

    def test_rejects_mime_mismatch(self) -> None:
        result = detect_upload("project.json", "application/pdf", b"{}")
        self.assertEqual(DetectionStatus.REJECTED, result.status)
        self.assertEqual("mime_mismatch", result.reason_code)

    def test_rejects_malformed_docx(self) -> None:
        result = detect_upload(
            "existing.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            b"not a package",
        )
        self.assertEqual(DetectionStatus.REJECTED, result.status)
        self.assertEqual("malformed_docx", result.reason_code)

    def test_rejects_unsupported_extension(self) -> None:
        result = detect_upload("drawing.dwg", "application/octet-stream", b"data")
        self.assertEqual(DetectionStatus.REJECTED, result.status)
        self.assertEqual("unsupported_format", result.reason_code)


if __name__ == "__main__":
    unittest.main()
