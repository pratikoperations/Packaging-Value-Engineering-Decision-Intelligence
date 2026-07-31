from __future__ import annotations

import math
import unittest
from dataclasses import FrozenInstanceError

from src.domain.approved_specification_consumption import (
    AUTHORIZATION_SCHEMA_VERSION,
    CONSUMPTION_CONTRACT_VERSION,
    ApprovedSpecificationConsumptionEnvelope,
    ApprovedSpecificationConsumptionError,
    ApprovedSpecificationConsumptionValue,
    AuthorizedConsumptionPurpose,
    ConsumptionAuthorization,
    GovernedConsumptionHandoff,
    approved_specification_consumption_envelope_hash,
)


class ApprovedSpecificationConsumptionDomainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.values = (
            ApprovedSpecificationConsumptionValue("board.grade", "BF-24", "accepted_proposed"),
            ApprovedSpecificationConsumptionValue("dimensions.length_mm", 400, "unchanged"),
        )
        self.excluded = ("print.special_finish",)
        self.hash = self._hash()

    def _hash(self, **changes) -> str:
        data = {
            "project_id": "project-1",
            "snapshot_id": "snapshot-1",
            "review_id": "review-1",
            "source_review_revision_id": "revision-2",
            "source_review_revision_number": 2,
            "existing_dataset_id": "dataset-existing",
            "proposed_dataset_id": "dataset-proposed",
            "snapshot_schema_version": "1.0",
            "approved_values": getattr(self, "values", (ApprovedSpecificationConsumptionValue("board.grade", "BF-24", "accepted_proposed"),)),
            "excluded_fields": getattr(self, "excluded", ()),
            "snapshot_content_hash": "snapshot-hash",
            "consumption_contract_version": CONSUMPTION_CONTRACT_VERSION,
        }
        data.update(changes)
        return approved_specification_consumption_envelope_hash(**data)

    def _envelope(self, **changes) -> ApprovedSpecificationConsumptionEnvelope:
        data = {
            "envelope_id": "envelope-1",
            "project_id": "project-1",
            "snapshot_id": "snapshot-1",
            "review_id": "review-1",
            "source_review_revision_id": "revision-2",
            "source_review_revision_number": 2,
            "existing_dataset_id": "dataset-existing",
            "proposed_dataset_id": "dataset-proposed",
            "snapshot_schema_version": "1.0",
            "consumption_contract_version": CONSUMPTION_CONTRACT_VERSION,
            "approved_values": self.values,
            "excluded_fields": self.excluded,
            "snapshot_content_hash": "snapshot-hash",
            "envelope_content_hash": self.hash,
            "created_at": "2026-07-31T10:30:00+00:00",
        }
        data.update(changes)
        return ApprovedSpecificationConsumptionEnvelope(**data)

    def _authorization(self, **changes) -> ConsumptionAuthorization:
        data = {
            "authorization_id": "authorization-1",
            "project_id": "project-1",
            "snapshot_id": "snapshot-1",
            "envelope_id": "envelope-1",
            "purpose": AuthorizedConsumptionPurpose.COST_ANALYSIS_INPUT,
            "actor_reference": "procurement.manager",
            "business_reason": "Prepare governed should-cost input.",
            "snapshot_content_hash": "snapshot-hash",
            "envelope_content_hash": self.hash,
            "authorization_schema_version": AUTHORIZATION_SCHEMA_VERSION,
            "created_at": "2026-07-31T10:31:00+00:00",
        }
        data.update(changes)
        return ConsumptionAuthorization(**data)

    def test_authorized_purposes_are_controlled(self) -> None:
        self.assertEqual(AuthorizedConsumptionPurpose.COST_ANALYSIS_INPUT.value, "cost_analysis_input")
        self.assertEqual(len(AuthorizedConsumptionPurpose), 7)

    def test_consumption_value_is_immutable(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            self.values[0].field_key = "changed"

    def test_consumption_value_requires_field_key(self) -> None:
        with self.assertRaisesRegex(ValueError, "field_key"):
            ApprovedSpecificationConsumptionValue("", 1, "unchanged")

    def test_consumption_value_rejects_invalid_source(self) -> None:
        with self.assertRaisesRegex(ValueError, "source"):
            ApprovedSpecificationConsumptionValue("field", 1, "manual")

    def test_consumption_value_rejects_non_json_value(self) -> None:
        with self.assertRaisesRegex(ValueError, "canonical JSON"):
            ApprovedSpecificationConsumptionValue("field", object(), "unchanged")

    def test_consumption_value_rejects_nan(self) -> None:
        with self.assertRaisesRegex(ValueError, "canonical JSON"):
            ApprovedSpecificationConsumptionValue("field", math.nan, "unchanged")

    def test_envelope_accepts_valid_governed_lineage(self) -> None:
        self.assertEqual(self._envelope().envelope_content_hash, self.hash)

    def test_envelope_requires_deterministic_value_order(self) -> None:
        with self.assertRaisesRegex(ValueError, "deterministic"):
            self._hash(approved_values=tuple(reversed(self.values)))

    def test_envelope_rejects_duplicate_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self._hash(approved_values=(self.values[0], self.values[0]))

    def test_envelope_requires_deterministic_exclusion_order(self) -> None:
        with self.assertRaisesRegex(ValueError, "deterministic"):
            self._hash(excluded_fields=("z", "a"))

    def test_envelope_rejects_duplicate_exclusions(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicates"):
            self._hash(excluded_fields=("a", "a"))

    def test_envelope_rejects_exclusion_overlap(self) -> None:
        with self.assertRaisesRegex(ValueError, "both approved and excluded"):
            self._hash(excluded_fields=("board.grade",))

    def test_envelope_rejects_empty_exclusion(self) -> None:
        with self.assertRaisesRegex(ValueError, "empty"):
            self._hash(excluded_fields=("",))

    def test_envelope_rejects_invalid_revision_number(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            self._hash(source_review_revision_number=0)

    def test_envelope_rejects_same_dataset_identity(self) -> None:
        with self.assertRaisesRegex(ValueError, "distinct"):
            self._hash(proposed_dataset_id="dataset-existing")

    def test_envelope_hash_is_deterministic(self) -> None:
        self.assertEqual(self.hash, self._hash())

    def test_envelope_hash_changes_with_value(self) -> None:
        changed = (ApprovedSpecificationConsumptionValue("board.grade", "BF-26", "accepted_proposed"), self.values[1])
        self.assertNotEqual(self.hash, self._hash(approved_values=changed))

    def test_envelope_hash_changes_with_lineage(self) -> None:
        self.assertNotEqual(self.hash, self._hash(snapshot_id="snapshot-2"))

    def test_envelope_hash_changes_with_contract_version(self) -> None:
        self.assertNotEqual(self.hash, self._hash(consumption_contract_version="2.0"))

    def test_envelope_rejects_hash_mismatch(self) -> None:
        with self.assertRaisesRegex(ApprovedSpecificationConsumptionError, "hash"):
            self._envelope(envelope_content_hash="wrong")

    def test_authorization_requires_supported_enum(self) -> None:
        with self.assertRaisesRegex(ApprovedSpecificationConsumptionError, "unsupported"):
            self._authorization(purpose="cost_analysis_input")

    def test_authorization_requires_actor(self) -> None:
        with self.assertRaisesRegex(ValueError, "actor_reference"):
            self._authorization(actor_reference=" ")

    def test_authorization_requires_business_reason(self) -> None:
        with self.assertRaisesRegex(ValueError, "business_reason"):
            self._authorization(business_reason="")

    def test_handoff_accepts_matching_lineage(self) -> None:
        handoff = GovernedConsumptionHandoff(self._envelope(), self._authorization())
        self.assertEqual(handoff.authorization.envelope_id, "envelope-1")

    def test_handoff_rejects_project_mismatch(self) -> None:
        with self.assertRaisesRegex(ApprovedSpecificationConsumptionError, "project"):
            GovernedConsumptionHandoff(self._envelope(), self._authorization(project_id="project-2"))

    def test_handoff_rejects_snapshot_mismatch(self) -> None:
        with self.assertRaisesRegex(ApprovedSpecificationConsumptionError, "snapshot lineage"):
            GovernedConsumptionHandoff(self._envelope(), self._authorization(snapshot_id="snapshot-2"))

    def test_handoff_rejects_envelope_identity_mismatch(self) -> None:
        with self.assertRaisesRegex(ApprovedSpecificationConsumptionError, "envelope identity"):
            GovernedConsumptionHandoff(self._envelope(), self._authorization(envelope_id="envelope-2"))

    def test_handoff_rejects_snapshot_hash_mismatch(self) -> None:
        with self.assertRaisesRegex(ApprovedSpecificationConsumptionError, "snapshot hash"):
            GovernedConsumptionHandoff(self._envelope(), self._authorization(snapshot_content_hash="other"))

    def test_handoff_rejects_envelope_hash_mismatch(self) -> None:
        with self.assertRaisesRegex(ApprovedSpecificationConsumptionError, "envelope hash"):
            GovernedConsumptionHandoff(self._envelope(), self._authorization(envelope_content_hash="other"))


if __name__ == "__main__":
    unittest.main()
