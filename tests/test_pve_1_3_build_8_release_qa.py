import unittest

from src.release_qa import validate_demonstration_case, validate_release_qa_assessment


class Build8ReleaseQATests(unittest.TestCase):
    def test_demonstration_case_validation(self):
        result = validate_demonstration_case({
            "case_id": "DEMO-001",
            "title": "Governed packaging flow",
            "purpose": "Demonstrate traceable evidence across Builds 1 through 7.",
            "data_classification": "synthetic",
            "covered_builds": [1, 2, 3, 4, 5, 6, 7],
            "expected_outcomes": ["traceable evidence"],
            "acceptance_checks": ["records resolve"],
            "status": "ready",
            "evidence_references": ["DEMO-DATA-001"],
        })
        self.assertTrue(result.is_valid)

    def test_ready_assessment_requires_clean_tests(self):
        payload = {
            "assessment_id": "QA-001",
            "tested_commit": "abc123",
            "workflow_run_id": "1001",
            "job_id": "2001",
            "test_count": 370,
            "failure_count": 1,
            "error_count": 0,
            "artifact_id": "3001",
            "artifact_digest": "sha256:example",
            "schema_version": 10,
            "demonstration_case_ids": ["DEMO-001"],
            "unresolved_blockers": [],
            "reviewed_by": "Release QA Lead",
            "recommendation": "ready_for_release_authorization",
            "evidence_references": ["CI-1001"],
        }
        result = validate_release_qa_assessment(payload)
        self.assertIn("tests_not_clean", {issue.code for issue in result.issues})

    def test_release_actions_are_prohibited(self):
        payload = {
            "assessment_id": "QA-002",
            "tested_commit": "abc123",
            "workflow_run_id": "1002",
            "job_id": "2002",
            "test_count": 370,
            "failure_count": 0,
            "error_count": 0,
            "artifact_id": "3002",
            "artifact_digest": "sha256:example2",
            "schema_version": 10,
            "demonstration_case_ids": ["DEMO-001"],
            "unresolved_blockers": [],
            "reviewed_by": "Release QA Lead",
            "recommendation": "ready_for_release_authorization",
            "evidence_references": ["CI-1002"],
            "create_release_tag": True,
            "declare_release_complete": True,
        }
        result = validate_release_qa_assessment(payload)
        self.assertIn("release_action_prohibited", {issue.code for issue in result.issues})


if __name__ == "__main__":
    unittest.main()
