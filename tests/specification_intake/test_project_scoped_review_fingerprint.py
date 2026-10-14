from __future__ import annotations

import unittest
from types import SimpleNamespace

from src.application.specification_upload import (
    SPEC_BATCH_KEY, SPEC_REVIEWS_KEY, SPEC_CONFIRMATION_KEY,
    SpecificationUploadInput, invalidate_specification_state_on_change,
)
from src.specification_intake.models import DocumentRole
from src.upload_routing.models import FileFormat


class ReviewProjectIsolationTests(unittest.TestCase):
    @staticmethod
    def pair():
        return (
            SpecificationUploadInput(
                filename="existing.pdf", mime_type="application/pdf",
                content=b"old",
                detection=SimpleNamespace(sha256="a"*64, file_format=FileFormat.PDF),
                role=DocumentRole.EXISTING,
            ),
            SpecificationUploadInput(
                filename="proposed.pdf", mime_type="application/pdf",
                content=b"new",
                detection=SimpleNamespace(sha256="b"*64, file_format=FileFormat.PDF),
                role=DocumentRole.PROPOSED,
            ),
        )

    def test_same_files_in_new_project_clear_previous_reviews(self):
        state = {"active_project_id": "project-A"}
        self.assertTrue(invalidate_specification_state_on_change(state, self.pair()))
        first_fingerprint = state[SPEC_BATCH_KEY]
        state[SPEC_REVIEWS_KEY] = ("previous project approval",)
        state[SPEC_CONFIRMATION_KEY] = True
        state["active_project_id"] = "project-B"
        self.assertTrue(invalidate_specification_state_on_change(state, self.pair()))
        self.assertNotEqual(state[SPEC_BATCH_KEY], first_fingerprint)
        self.assertNotIn(SPEC_REVIEWS_KEY, state)
        self.assertNotIn(SPEC_CONFIRMATION_KEY, state)

    def test_same_files_same_project_preserve_review_state(self):
        state = {"active_project_id": "project-A"}
        self.assertTrue(invalidate_specification_state_on_change(state, self.pair()))
        state[SPEC_REVIEWS_KEY] = ("review",)
        self.assertFalse(invalidate_specification_state_on_change(state, self.pair()))
        self.assertEqual(state[SPEC_REVIEWS_KEY], ("review",))

    def test_empty_to_selected_project_revalidates_review_state(self):
        state = {"active_project_id": None}
        self.assertTrue(invalidate_specification_state_on_change(state, self.pair()))
        state[SPEC_REVIEWS_KEY] = ("unscoped approval",)
        state["active_project_id"] = "project-A"
        self.assertTrue(invalidate_specification_state_on_change(state, self.pair()))
        self.assertNotIn(SPEC_REVIEWS_KEY, state)


if __name__ == "__main__":
    unittest.main()
