from __future__ import annotations

import hashlib
import unittest

from src.supplier_qualification import validate_supplier_qualification


class SupplierQualificationBuild7Tests(unittest.TestCase):
    @staticmethod
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def payload(self, **overrides):
        payload = {
            "project_id": "project-a",
            "qualification_code": "SQ-001",
            "supplier_name": "Supplier A",
            "supplier_site": "Plant 1",
            "qualification_scope": "Corrugated shipper for SKU family A",
            "assessment_type": "initial",
            "assessment_date": "2026-09-01",
            "qualification_status": "qualified",
            "assessed_by": "Supplier Quality Engineer",
            "approved_by": "Procurement Quality Director",
            "approval_reference": "SQA-2026-001",
            "approved_at": "2026-09-05",
            "decision_rationale": "Trials, audit and quality evidence met the approved scope.",
            "valid_from": "2026-09-05",
            "valid_until": "2027-09-04",
            "review_date": "2027-06-01",
            "evidence_references": ["AUDIT-001", "TRIAL-001"],
            "linked_trial_execution_ids": [],
            "linked_defect_classification_ids": [],
            "linked_complaint_record_ids": [],
            "linked_specification_change_request_ids": [],
            "linked_implementation_control_ids": [],
            "conditions": [],
            "open_actions": [],
            "content_hash": self.digest("SQ-001"),
        }
        payload.update(overrides)
        return payload

    def test_qualified_supplier_assessment_is_valid(self) -> None:
        self.assertTrue(validate_supplier_qualification(self.payload()).is_valid)

    def test_qualification_requires_human_approval_and_evidence(self) -> None:
        result = validate_supplier_qualification(
            self.payload(approved_by="", approval_reference="", evidence_references=[])
        )
        codes = {issue.code for issue in result.issues}
        self.assertIn("missing_required", codes)
        self.assertIn("missing_evidence", codes)

    def test_conditional_qualification_requires_conditions(self) -> None:
        result = validate_supplier_qualification(
            self.payload(qualification_status="conditionally_qualified", conditions=[])
        )
        self.assertIn("conditions_required", {issue.code for issue in result.issues})

    def test_validity_dates_must_be_ordered(self) -> None:
        result = validate_supplier_qualification(
            self.payload(valid_from="2027-01-01", valid_until="2026-12-31")
        )
        self.assertIn("invalid_date_order", {issue.code for issue in result.issues})

    def test_build8_release_and_sourcing_fields_are_prohibited(self) -> None:
        result = validate_supplier_qualification(
            self.payload(release_certification_status="approved", sourcing_award_status="awarded")
        )
        self.assertIn("build8_data_prohibited", {issue.code for issue in result.issues})


if __name__ == "__main__":
    unittest.main()
