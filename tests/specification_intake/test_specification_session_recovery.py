from __future__ import annotations

import unittest

from src.application.specification_upload import (
    SESSION_SPEC_CACHE,
    SessionSpecificationFile,
    restore_session_specifications,
)


class SessionRecoveryTests(unittest.TestCase):
    def test_restores_pair_and_bytes_after_sidebar_navigation(self):
        state = {"active_project_id": "project-a"}
        existing = SessionSpecificationFile("baseline.pdf", "application/pdf", b"%PDF-baseline")
        proposed = SessionSpecificationFile("candidate.pdf", "application/pdf", b"%PDF-candidate")
        first, restored = restore_session_specifications(state, existing, proposed)
        self.assertFalse(restored)
        resumed, restored = restore_session_specifications(state, None, None)
        self.assertTrue(restored)
        self.assertEqual(resumed, first)
        self.assertEqual(resumed[0].getvalue(), b"%PDF-baseline")
        self.assertEqual(resumed[1].getvalue(), b"%PDF-candidate")

    def test_does_not_leak_cached_documents_to_another_project(self):
        state = {"active_project_id": "project-a"}
        existing = SessionSpecificationFile("a.pdf", "application/pdf", b"a")
        proposed = SessionSpecificationFile("b.pdf", "application/pdf", b"b")
        restore_session_specifications(state, existing, proposed)
        state["active_project_id"] = "project-b"
        pair, restored = restore_session_specifications(state, None, None)
        self.assertIsNone(pair)
        self.assertFalse(restored)

    def test_partial_upload_does_not_mix_cached_and_new_documents(self):
        state = {"active_project_id": "project-a"}
        a = SessionSpecificationFile("a.pdf", "application/pdf", b"a")
        b = SessionSpecificationFile("b.pdf", "application/pdf", b"b")
        restore_session_specifications(state, a, b)
        result, restored = restore_session_specifications(state, a, None)
        self.assertIsNone(result)
        self.assertFalse(restored)

    def test_empty_session_has_no_pair(self):
        state = {"active_project_id": "project-a"}
        result, restored = restore_session_specifications(state, None, None)
        self.assertIsNone(result)
        self.assertFalse(restored)
        self.assertNotIn(SESSION_SPEC_CACHE, state)


if __name__ == "__main__":
    unittest.main()
