from __future__ import annotations

import unittest

from src.sourcemate.domain import ExplanationContext, ExplanationQuestion, SourceClassification, SourceReference
from src.ui.sourcemate_ui import render_sourcemate_page


class _Expander:
    def __enter__(self): return self
    def __exit__(self, *args): return False


class FakeStreamlit:
    def __init__(self, *, click: bool = False):
        self.click = click
        self.calls = []
    def __getattr__(self, name):
        def call(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            if name == "selectbox": return args[1][0]
            if name == "button": return self.click
            if name == "expander": return _Expander()
            return None
        return call


class SourceMateUiTests(unittest.TestCase):
    def context(self):
        return ExplanationContext(
            project_id="P-1", target_id="T-1", target_type="decision",
            revision_reference="R-1", status="BLOCKED", status_reason="Evidence missing.",
            sources=(SourceReference("evidence", None, SourceClassification.MISSING, "decision:T-1"),),
            evidence_gaps=("Evidence missing.",), blockers=("Qualification incomplete.",),
            required_validation=("Validate evidence.",), required_human_action=("Human review required.",),
            proven_claims=("Recorded status is BLOCKED.",),
            claim_limitations=("No production approval is proven.",),
            status_improvement_requirements=("Provide evidence.",), source_hash="hash",
        )

    def test_empty_state_and_limitations_render(self):
        st = FakeStreamlit()
        render_sourcemate_page(st, contexts=())
        names = [item[0] for item in st.calls]
        self.assertIn("info", names)
        self.assertIn("expander", names)

    def test_success_state_and_export_render(self):
        st = FakeStreamlit(click=True)
        render_sourcemate_page(st, contexts=(self.context(),))
        names = [item[0] for item in st.calls]
        self.assertIn("subheader", names)
        self.assertIn("download_button", names)

    def test_page_has_no_unrestricted_text_input(self):
        st = FakeStreamlit(click=False)
        render_sourcemate_page(st, contexts=(self.context(),))
        names = [item[0] for item in st.calls]
        self.assertNotIn("text_input", names)
        self.assertNotIn("chat_input", names)


if __name__ == "__main__":
    unittest.main()
