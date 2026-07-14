from __future__ import annotations

import hashlib
import unittest

from src.change_control import validate_implementation_control, validate_specification_change


class ChangeControlBuild6Tests(unittest.TestCase):
    @staticmethod
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def change_payload(self, **overrides):
        payload = {
            "project_id": "project-a",
            "change_code": "CHG-001",
            "change_type": "specification",
            "title": "Increase board grade",
            "rationale": "Improve transport performance.",
            "current_specification_version": "SPEC-1.0",
            "proposed_specification_version": "SPEC-1.1",
            "review_status": "reviewed",
            "approval_status": "approved",
            "requested_by": "Packaging Engineer",
            "approved_by": "Packaging Manager",
            "approval_reference": "CAB-2026-001",
            "approved_at": "2026-08-20",
            "requested_effective_date": "2026-09-01",
            "evidence_references": ["TRIAL-EXEC-001", "DEFECT-REPORT-001"],
            "linked_trial_execution_ids": ["trial-exec-001"],
            "linked_defect_classification_ids": ["defect-001"],
            "linked_complaint_record_ids": ["complaint-001"],
            "content_hash": self.digest("CHG-001"),
        }
        payload.update(overrides)
        return payload

    def implementation_payload(self, **overrides):
        payload = {
            "project_id": "project-a",
            "change_request_id": "change-001",
            "implementation_code": "IMP-001",
            "implementation_site": "Plant A",
            "implementation_owner": "Plant Packaging Lead",
            "implementation_status": "implemented",
            "verification_status": "verified",
            "planned_implementation_date": "2026-09-01",
            "actual_implementation_date": "2026-09-02",
            "authorized_by": "Operations Manager",
            "authorization_reference": "AUTH-001",
            "verified_by": "Quality Manager",
            "verified_at": "2026-09-03",
            "evidence_references": ["LINE-TRIAL-001", "STARTUP-CHECK-001"],
            "content_hash": self.digest("IMP-001"),
        }
        payload.update(overrides)
        return payload

    def test_approved_specification_change_is_valid(self) -> None:
        self.assertTrue(validate_specification_change(self.change_payload()).is_valid)

    def test_approval_requires_human_authority_reference_and_evidence(self) -> None:
        result = validate_specification_change(
            self.change_payload(approved_by="", approval_reference="", evidence_references=[])
        )
        codes = {issue.code for issue in result.issues}
        self.assertIn("missing_required", codes)
        self.assertIn("missing_evidence", codes)

    def test_proposed_version_must_change(self) -> None:
        result = validate_specification_change(
            self.change_payload(proposed_specification_version="SPEC-1.0")
        )
        self.assertIn("version_not_changed", {issue.code for issue in result.issues})

    def test_implemented_and_verified_control_requires_authority_and_evidence(self) -> None:
        self.assertTrue(validate_implementation_control(self.implementation_payload()).is_valid)
        result = validate_implementation_control(
            self.implementation_payload(authorized_by="", verified_by="", evidence_references=[])
        )
        codes = {issue.code for issue in result.issues}
        self.assertIn("missing_required", codes)
        self.assertIn("missing_evidence", codes)

    def test_build7_and_later_fields_are_prohibited(self) -> None:
        change = validate_specification_change(
            self.change_payload(supplier_qualification_status="qualified", supplier_rank=1)
        )
        implementation = validate_implementation_control(
            self.implementation_payload(sourcing_award_status="awarded")
        )
        self.assertIn("build7_data_prohibited", {issue.code for issue in change.issues})
        self.assertIn("build7_data_prohibited", {issue.code for issue in implementation.issues})


if __name__ == "__main__":
    unittest.main()
