from __future__ import annotations

import hashlib
import unittest

from src.defect_taxonomy import validate_complaint_record, validate_defect_classification


class DefectComplaintTaxonomyBuild5Tests(unittest.TestCase):
    @staticmethod
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def defect_payload(self, **overrides):
        payload = {
            "project_id": "project-a",
            "taxonomy_version": "PVE-1.3-B5-v1",
            "defect_code": "STRUCT-CRUSH-001",
            "packaging_level": "secondary",
            "material_family": "corrugated",
            "defect_family": "structural",
            "defect_mode": "corner_crush",
            "description": "Corner crush observed after transport.",
            "severity": "major",
            "occurrence_stage": "transport",
            "review_status": "reviewed",
            "reviewed_by": "Packaging Quality Manager",
            "evidence_references": ["PHOTO-001", "INSPECTION-001"],
            "content_hash": self.digest("STRUCT-CRUSH-001"),
        }
        payload.update(overrides)
        return payload

    def complaint_payload(self, **overrides):
        payload = {
            "project_id": "project-a",
            "complaint_reference": "COMP-001",
            "complaint_source": "customer",
            "received_date": "2026-08-15",
            "description": "Cases arrived crushed.",
            "linked_defect_codes": ["STRUCT-CRUSH-001"],
            "affected_quantity": 24,
            "quantity_unit": "cases",
            "containment_status": "in_progress",
            "review_status": "reviewed",
            "reviewed_by": "Customer Quality Lead",
            "evidence_references": ["CUSTOMER-PHOTO-001"],
            "content_hash": self.digest("COMP-001"),
        }
        payload.update(overrides)
        return payload

    def test_reviewed_defect_classification_is_valid(self) -> None:
        self.assertTrue(validate_defect_classification(self.defect_payload()).is_valid)

    def test_reviewed_classification_requires_evidence_and_human_reviewer(self) -> None:
        result = validate_defect_classification(self.defect_payload(evidence_references=[], reviewed_by=""))
        codes = {issue.code for issue in result.issues}
        self.assertIn("missing_evidence", codes)
        self.assertIn("missing_required", codes)

    def test_complaint_quantity_requires_unit(self) -> None:
        result = validate_complaint_record(self.complaint_payload(quantity_unit=""))
        self.assertIn("missing_unit", {issue.code for issue in result.issues})

    def test_unknown_occurrence_stage_is_preserved(self) -> None:
        self.assertTrue(validate_defect_classification(self.defect_payload(occurrence_stage="unknown")).is_valid)

    def test_build6_and_later_fields_are_prohibited(self) -> None:
        defect = validate_defect_classification(
            self.defect_payload(specification_change_status="approved", root_cause="supplier process")
        )
        complaint = validate_complaint_record(
            self.complaint_payload(corrective_action_approval="approved", supplier_qualification_status="qualified")
        )
        self.assertIn("build6_data_prohibited", {issue.code for issue in defect.issues})
        self.assertIn("build6_data_prohibited", {issue.code for issue in complaint.issues})


if __name__ == "__main__":
    unittest.main()
