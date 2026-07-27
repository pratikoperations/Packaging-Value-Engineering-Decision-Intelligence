from __future__ import annotations

import unittest

from src.application.specification_upload import (
    SPEC_BATCH_KEY,
    SPEC_CONFIRMATION_KEY,
    SPEC_REVIEWS_KEY,
    SpecificationUploadInput,
    invalidate_specification_state_on_change,
)
from src.specification_intake import DocumentRole
from src.upload_routing.models import DetectedUpload, DetectionStatus, FileFormat, WorkflowKind


def item(sha: str, role: DocumentRole, fmt: FileFormat = FileFormat.PDF):
    detection = DetectedUpload(
        filename=f"{role.value}.{fmt.value}",
        mime_type="application/pdf" if fmt is FileFormat.PDF else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        sha256=sha,
        file_format=fmt,
        workflow=WorkflowKind.SPECIFICATION_COMPARISON,
        status=DetectionStatus.ROLE_REQUIRED,
    )
    return SpecificationUploadInput(detection.filename, detection.mime_type, b"content", detection, role)


class SpecificationReviewStateTests(unittest.TestCase):
    def test_file_role_or_format_change_invalidates_downstream_state(self):
        first = (item("a" * 64, DocumentRole.EXISTING), item("b" * 64, DocumentRole.PROPOSED))
        state = {}
        self.assertTrue(invalidate_specification_state_on_change(state, first))
        state[SPEC_CONFIRMATION_KEY] = True
        state[SPEC_REVIEWS_KEY] = ("review",)
        self.assertFalse(invalidate_specification_state_on_change(state, first))
        changed_role = (item("a" * 64, DocumentRole.PROPOSED), item("b" * 64, DocumentRole.EXISTING))
        self.assertTrue(invalidate_specification_state_on_change(state, changed_role))
        self.assertNotIn(SPEC_CONFIRMATION_KEY, state)
        self.assertNotIn(SPEC_REVIEWS_KEY, state)
        self.assertIn(SPEC_BATCH_KEY, state)
        changed_format = (item("a" * 64, DocumentRole.PROPOSED, FileFormat.DOCX), item("b" * 64, DocumentRole.EXISTING))
        self.assertTrue(invalidate_specification_state_on_change(state, changed_format))


if __name__ == "__main__":
    unittest.main()
