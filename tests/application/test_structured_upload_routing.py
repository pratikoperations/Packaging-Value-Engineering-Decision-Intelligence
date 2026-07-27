from __future__ import annotations

import unittest

from src.application.structured_upload import (
    STRUCTURED_CONFIRMATION_KEY,
    STRUCTURED_FINGERPRINT_KEY,
    StructuredUploadFile,
    invalidate_structured_state_on_change,
    prepare_structured_upload,
    validate_structured_batch,
)
from src.upload_routing import DetectedUpload, DetectionStatus, FileFormat, WorkflowKind
from src.uploads import UploadParseError


def detected(filename: str, file_format: FileFormat, sha256: str = "a" * 64) -> DetectedUpload:
    return DetectedUpload(
        filename=filename,
        mime_type="application/octet-stream",
        sha256=sha256,
        file_format=file_format,
        workflow=WorkflowKind.STRUCTURED_PROJECT_DATA,
        status=DetectionStatus.READY,
    )


class FakeUploadService:
    def __init__(self):
        self.calls = []

    def prepare_excel(self, **kwargs):
        self.calls.append(("xlsx", kwargs))
        return "excel-result"

    def prepare_json(self, **kwargs):
        self.calls.append(("json", kwargs))
        return "json-result"

    def prepare_csv(self, **kwargs):
        self.calls.append(("csv", kwargs))
        return "csv-result"


class StructuredUploadRoutingTests(unittest.TestCase):
    def test_xlsx_reuses_existing_prepare_excel(self):
        service = FakeUploadService()
        files = [StructuredUploadFile("input.xlsx", b"xlsx", detected("input.xlsx", FileFormat.XLSX))]
        self.assertEqual(prepare_structured_upload(service, {"project_id": "P1"}, files), "excel-result")
        self.assertEqual(service.calls[0][0], "xlsx")

    def test_json_reuses_existing_prepare_json(self):
        service = FakeUploadService()
        files = [StructuredUploadFile("input.json", b"{}", detected("input.json", FileFormat.JSON))]
        self.assertEqual(prepare_structured_upload(service, {"project_id": "P1"}, files), "json-result")
        self.assertEqual(service.calls[0][0], "json")

    def test_csv_requires_existing_two_file_contract(self):
        service = FakeUploadService()
        files = [
            StructuredUploadFile("project.csv", b"project", detected("project.csv", FileFormat.CSV, "b" * 64)),
            StructuredUploadFile("alternatives.csv", b"alternatives", detected("alternatives.csv", FileFormat.CSV, "c" * 64)),
        ]
        self.assertEqual(validate_structured_batch(files), FileFormat.CSV)
        self.assertEqual(prepare_structured_upload(service, {"project_id": "P1"}, files), "csv-result")
        self.assertEqual(set(service.calls[0][1]["files"]), {"project.csv", "alternatives.csv"})

    def test_mixed_structured_formats_are_rejected(self):
        files = [
            StructuredUploadFile("input.xlsx", b"x", detected("input.xlsx", FileFormat.XLSX)),
            StructuredUploadFile("input.json", b"{}", detected("input.json", FileFormat.JSON, "d" * 64)),
        ]
        with self.assertRaises(UploadParseError):
            validate_structured_batch(files)

    def test_file_change_invalidates_confirmation_and_result(self):
        first = [StructuredUploadFile("input.json", b"{}", detected("input.json", FileFormat.JSON))]
        state = {
            STRUCTURED_CONFIRMATION_KEY: True,
            "data_upload.structured.prepared": object(),
        }
        self.assertTrue(invalidate_structured_state_on_change(state, first))
        self.assertIn(STRUCTURED_FINGERPRINT_KEY, state)
        self.assertNotIn(STRUCTURED_CONFIRMATION_KEY, state)
        self.assertNotIn("data_upload.structured.prepared", state)
        self.assertFalse(invalidate_structured_state_on_change(state, first))


if __name__ == "__main__":
    unittest.main()
