from __future__ import annotations

import unittest

from src.domain.approved_specification_consumption import (
    AUTHORIZATION_SCHEMA_VERSION,
    CONSUMPTION_CONTRACT_VERSION,
    ApprovedSpecificationConsumptionEnvelope,
    ApprovedSpecificationConsumptionValue,
    AuthorizedConsumptionPurpose,
    ConsumptionAuthorization,
    GovernedConsumptionHandoff,
    approved_specification_consumption_envelope_hash,
)
from src.ui.approved_specification_consumption_ui import (
    PENDING_HANDOFF_TOKEN_KEY,
    ConsumptionHandoffActionRequest,
    authorization_identity_rows,
    business_error_message,
    clear_handoff_token,
    envelope_identity_rows,
    execute_handoff_once,
    handoff_audit_rows,
    purpose_label,
    snapshot_identity_rows,
)


class DummySnapshot:
    snapshot_id = "s1"
    review_id = "r1"
    source_review_revision_id = "rr1"
    source_review_revision_number = 1
    existing_dataset_id = "d1"
    proposed_dataset_id = "d2"
    snapshot_schema_version = "1.0"
    approved_values = (object(), object())
    excluded_fields = ("optional",)


class ConsumptionUiTests(unittest.TestCase):
    def envelope(self) -> ApprovedSpecificationConsumptionEnvelope:
        values = (ApprovedSpecificationConsumptionValue("a", 1, "unchanged"),)
        digest = approved_specification_consumption_envelope_hash(
            project_id="p1",
            snapshot_id="s1",
            review_id="r1",
            source_review_revision_id="rr1",
            source_review_revision_number=1,
            existing_dataset_id="d1",
            proposed_dataset_id="d2",
            snapshot_schema_version="1.0",
            approved_values=values,
            excluded_fields=(),
            snapshot_content_hash="snapshot-hash",
        )
        return ApprovedSpecificationConsumptionEnvelope(
            envelope_id="e1",
            project_id="p1",
            snapshot_id="s1",
            review_id="r1",
            source_review_revision_id="rr1",
            source_review_revision_number=1,
            existing_dataset_id="d1",
            proposed_dataset_id="d2",
            snapshot_schema_version="1.0",
            consumption_contract_version=CONSUMPTION_CONTRACT_VERSION,
            approved_values=values,
            excluded_fields=(),
            snapshot_content_hash="snapshot-hash",
            envelope_content_hash=digest,
            created_at="2026-01-01T00:00:00+00:00",
        )

    def authorization(self) -> ConsumptionAuthorization:
        envelope = self.envelope()
        return ConsumptionAuthorization(
            authorization_id="a1",
            project_id="p1",
            snapshot_id="s1",
            envelope_id="e1",
            purpose=AuthorizedConsumptionPurpose.COST_ANALYSIS_INPUT,
            actor_reference="buyer",
            business_reason="cost input preparation",
            snapshot_content_hash=envelope.snapshot_content_hash,
            envelope_content_hash=envelope.envelope_content_hash,
            authorization_schema_version=AUTHORIZATION_SCHEMA_VERSION,
            created_at="2026-01-01T00:01:00+00:00",
        )

    def request(self) -> ConsumptionHandoffActionRequest:
        return ConsumptionHandoffActionRequest(
            project_id="p1",
            snapshot_id="s1",
            purpose=AuthorizedConsumptionPurpose.COST_ANALYSIS_INPUT,
            actor_reference="buyer",
            business_reason="cost input preparation",
        )

    def test_action_token_is_deterministic(self) -> None:
        self.assertEqual(self.request().token, self.request().token)
        self.assertIn("cost_analysis_input", self.request().token)

    def test_execute_once_blocks_duplicate_rerun(self) -> None:
        state: dict[str, object] = {}
        calls: list[str] = []
        executed, result = execute_handoff_once(
            state, self.request(), lambda: calls.append("run") or "ok"
        )
        duplicate, duplicate_result = execute_handoff_once(
            state, self.request(), lambda: calls.append("duplicate") or "bad"
        )
        self.assertTrue(executed)
        self.assertEqual(result, "ok")
        self.assertFalse(duplicate)
        self.assertIsNone(duplicate_result)
        self.assertEqual(calls, ["run"])

    def test_failed_operation_clears_pending_token(self) -> None:
        state: dict[str, object] = {}
        with self.assertRaises(RuntimeError):
            execute_handoff_once(
                state, self.request(), lambda: (_ for _ in ()).throw(RuntimeError("x"))
            )
        self.assertNotIn(PENDING_HANDOFF_TOKEN_KEY, state)

    def test_clear_handoff_token(self) -> None:
        state = {PENDING_HANDOFF_TOKEN_KEY: "x"}
        clear_handoff_token(state)
        self.assertEqual(state, {})

    def test_snapshot_rows_are_read_only_summary(self) -> None:
        rows = snapshot_identity_rows(DummySnapshot())
        labels = {row["Attribute"] for row in rows}
        self.assertIn("Snapshot ID", labels)
        self.assertNotIn("Raw JSON", labels)

    def test_envelope_rows_do_not_expose_raw_json(self) -> None:
        rows = envelope_identity_rows(self.envelope())
        self.assertNotIn("approved_values_json", str(rows))
        self.assertIn("Envelope ID", {row["Attribute"] for row in rows})

    def test_authorization_rows_include_governed_purpose(self) -> None:
        rows = authorization_identity_rows(self.authorization())
        self.assertIn("cost_analysis_input", str(rows))
        self.assertNotIn("supplier_award", str(rows))

    def test_audit_rows_keep_hashes_separate(self) -> None:
        handoff = GovernedConsumptionHandoff(self.envelope(), self.authorization())
        rows = handoff_audit_rows(handoff)
        self.assertEqual(len(rows), 3)
        self.assertIn("Snapshot content hash", {row["Attribute"] for row in rows})
        self.assertIn("Envelope content hash", {row["Attribute"] for row in rows})

    def test_purpose_label_is_business_readable(self) -> None:
        self.assertEqual(
            purpose_label(AuthorizedConsumptionPurpose.RISK_ANALYSIS_INPUT),
            "Risk Analysis Input",
        )

    def test_business_error_mapping(self) -> None:
        self.assertIn("approved specification", business_error_message("snapshot_required", "x"))
        self.assertEqual(business_error_message("unknown", "fallback"), "fallback")


if __name__ == "__main__":
    unittest.main()
