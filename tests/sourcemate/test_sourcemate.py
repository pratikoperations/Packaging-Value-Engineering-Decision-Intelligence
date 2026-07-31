from __future__ import annotations

import json
import unittest

from src.sourcemate.domain import (
    ExplanationContext,
    ExplanationError,
    ExplanationQuestion,
    ExplanationRequest,
    SourceClassification,
    SourceReference,
)
from src.sourcemate.service import ExplanationContextAssembler, SourceMateExplanationService


class SourceMateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = SourceMateExplanationService()
        self.context = ExplanationContext(
            project_id="P-1",
            target_id="ALT-1",
            target_type="decision",
            revision_reference="REV-3",
            status="CONDITIONAL",
            status_reason="Technical evidence remains incomplete.",
            sources=(
                SourceReference("unit_cost", 12.5, SourceClassification.DERIVED, "decision:ALT-1", "COST-01"),
                SourceReference("compression_test", None, SourceClassification.MISSING, "decision:ALT-1", "TECH-04"),
            ),
            assumptions=("Annual volume remains unchanged.",),
            evidence_gaps=("Compression test report is missing.",),
            blockers=("Technical qualification is incomplete.",),
            required_validation=("Complete compression testing.",),
            required_human_action=("Packaging engineer must review the test evidence.",),
            proven_claims=("The recorded should-cost calculation used the selected inputs.",),
            claim_limitations=("The record does not prove production approval.",),
            status_improvement_requirements=("Record acceptable compression-test evidence.",),
            source_hash="abc123",
        )

    def request(self, question: ExplanationQuestion) -> ExplanationRequest:
        return ExplanationRequest("P-1", "ALT-1", question, "REV-3")

    def test_exactly_nine_supported_questions(self) -> None:
        self.assertEqual(9, len(ExplanationQuestion))

    def test_all_supported_questions_return_content(self) -> None:
        for question in ExplanationQuestion:
            with self.subTest(question=question):
                response = self.service.explain(self.request(question), self.context)
                self.assertTrue(response.answer_summary)

    def test_status_reason_uses_recorded_reason(self) -> None:
        response = self.service.explain(self.request(ExplanationQuestion.STATUS_REASON), self.context)
        self.assertEqual(self.context.status_reason, response.answer_summary)

    def test_inputs_retain_classification(self) -> None:
        response = self.service.explain(self.request(ExplanationQuestion.INPUTS_AFFECTING_RESULT), self.context)
        self.assertIn("unit_cost [DERIVED]", response.answer_summary)
        self.assertIn("compression_test [MISSING]", response.answer_summary)

    def test_assumptions_remain_distinct(self) -> None:
        response = self.service.explain(self.request(ExplanationQuestion.APPLIED_ASSUMPTIONS), self.context)
        self.assertEqual(("Annual volume remains unchanged.",), response.assumptions)

    def test_blocker_precedence_is_exposed(self) -> None:
        response = self.service.explain(self.request(ExplanationQuestion.OVERRIDING_BLOCKERS), self.context)
        self.assertEqual(("Technical qualification is incomplete.",), response.blocking_controls)

    def test_required_validation_is_exposed(self) -> None:
        response = self.service.explain(self.request(ExplanationQuestion.REQUIRED_VALIDATION), self.context)
        self.assertIn("Complete compression testing.", response.answer_summary)

    def test_proven_and_unproven_claims_remain_separate(self) -> None:
        proven = self.service.explain(self.request(ExplanationQuestion.PROVEN_CLAIMS), self.context)
        unproven = self.service.explain(self.request(ExplanationQuestion.UNPROVEN_CLAIMS), self.context)
        self.assertNotEqual(proven.answer_summary, unproven.answer_summary)

    def test_status_improvement_lists_existing_requirement(self) -> None:
        response = self.service.explain(self.request(ExplanationQuestion.STATUS_IMPROVEMENT_REQUIREMENTS), self.context)
        self.assertEqual("Record acceptable compression-test evidence.", response.answer_summary)

    def test_project_scope_violation_fails_closed(self) -> None:
        with self.assertRaises(ExplanationError) as caught:
            self.service.explain(ExplanationRequest("P-2", "ALT-1", ExplanationQuestion.STATUS_REASON, "REV-3"), self.context)
        self.assertEqual("PROJECT_SCOPE_VIOLATION", caught.exception.code)

    def test_target_mismatch_fails_closed(self) -> None:
        with self.assertRaises(ExplanationError) as caught:
            self.service.explain(ExplanationRequest("P-1", "ALT-2", ExplanationQuestion.STATUS_REASON, "REV-3"), self.context)
        self.assertEqual("RECORD_NOT_FOUND", caught.exception.code)

    def test_historical_revision_is_honored(self) -> None:
        with self.assertRaises(ExplanationError):
            self.service.explain(ExplanationRequest("P-1", "ALT-1", ExplanationQuestion.STATUS_REASON, "REV-2"), self.context)

    def test_integrity_failure_fails_closed(self) -> None:
        context = self.context.__class__(**{**self.context.__dict__, "source_hash": ""})
        with self.assertRaises(ExplanationError) as caught:
            self.service.explain(self.request(ExplanationQuestion.STATUS_REASON), context)
        self.assertEqual("INTEGRITY_FAILURE", caught.exception.code)

    def test_missing_context_does_not_invent_content(self) -> None:
        context = self.context.__class__(**{**self.context.__dict__, "evidence_gaps": ()})
        with self.assertRaises(ExplanationError) as caught:
            self.service.explain(self.request(ExplanationQuestion.MISSING_EVIDENCE), context)
        self.assertEqual("INSUFFICIENT_CONTEXT", caught.exception.code)

    def test_canonical_json_is_repeatable(self) -> None:
        response = self.service.explain(self.request(ExplanationQuestion.STATUS_REASON), self.context)
        first = self.service.canonical_json(response)
        second = self.service.canonical_json(response)
        self.assertEqual(first, second)
        self.assertNotIn("timestamp", first)

    def test_json_matches_displayed_response(self) -> None:
        response = self.service.explain(self.request(ExplanationQuestion.STATUS_REASON), self.context)
        payload = json.loads(self.service.canonical_json(response))
        self.assertEqual(response.answer_summary, payload["answer_summary"])
        self.assertEqual(response.status, payload["status"])
        self.assertEqual(response.source_hash, payload["source_hash"])

    def test_canonical_source_order(self) -> None:
        response = self.service.explain(self.request(ExplanationQuestion.INPUTS_AFFECTING_RESULT), self.context)
        fields = [item.field for item in response.source_fields]
        self.assertEqual(sorted(fields), fields)

    def test_archived_context_is_visible_and_immutable(self) -> None:
        archived = self.context.__class__(**{**self.context.__dict__, "archived": True})
        before = archived
        response = self.service.explain(self.request(ExplanationQuestion.STATUS_REASON), archived)
        self.assertTrue(response.archived)
        self.assertEqual(before, archived)

    def test_context_assembler_enforces_project_scope(self) -> None:
        assembler = ExplanationContextAssembler({"decision": lambda project, target, revision: self.context})
        request = self.request(ExplanationQuestion.STATUS_REASON)
        self.assertEqual(self.context, assembler.assemble(request, "decision"))

    def test_context_assembler_rejects_cross_project_loader_result(self) -> None:
        assembler = ExplanationContextAssembler({"decision": lambda project, target, revision: self.context})
        request = ExplanationRequest("P-2", "ALT-1", ExplanationQuestion.STATUS_REASON, "REV-3")
        with self.assertRaises(ExplanationError) as caught:
            assembler.assemble(request, "decision")
        self.assertEqual("PROJECT_SCOPE_VIOLATION", caught.exception.code)

    def test_context_assembler_rejects_unknown_target_type(self) -> None:
        with self.assertRaises(ExplanationError) as caught:
            ExplanationContextAssembler({}).assemble(self.request(ExplanationQuestion.STATUS_REASON), "unknown")
        self.assertEqual("RECORD_NOT_FOUND", caught.exception.code)

    def test_service_has_no_mutation_api(self) -> None:
        prohibited = {"create", "update", "delete", "approve", "execute", "rank", "award"}
        self.assertTrue(prohibited.isdisjoint(set(dir(self.service))))


if __name__ == "__main__":
    unittest.main()
