from __future__ import annotations

import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.persistence import Database, DemonstrationCaseRepository, ReleaseQAAssessmentRepository
from src.persistence import migrations_v10
from src.persistence.migrations_v11 import SCHEMA_VERSION, current_schema_version, initialize_database


class Build8ReleaseQAPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.temp_dir.name) / "pve.db")
        initialize_database(self.database)
        self.cases = DemonstrationCaseRepository(self.database)
        self.qa = ReleaseQAAssessmentRepository(self.database)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def create_case(self, **overrides):
        values = {
            "case_code": "DEMO-001",
            "title": "Synthetic governed packaging flow",
            "purpose": "Demonstrate Builds 1 through 7 with traceable evidence.",
            "data_classification": "synthetic",
            "covered_builds": [1, "2A", "2B", 3, 4, 5, 6, 7],
            "expected_outcomes": ["traceable evidence"],
            "acceptance_checks": ["records resolve"],
            "status": "ready",
            "evidence_references": ["DEMO-DATA-001"],
            "limitations": ["No deployment evidence"],
            "exceptions": [],
            "content_hash": self.digest("DEMO-001"),
        }
        values.update(overrides)
        return self.cases.create(**values)

    def create_assessment(self, case_id: str, **overrides):
        values = {
            "assessment_code": "QA-001",
            "tested_commit": "a" * 40,
            "workflow_run_id": "29330021187",
            "job_id": "87075460656",
            "test_count": 370,
            "failure_count": 0,
            "error_count": 0,
            "artifact_id": "8309564912",
            "artifact_digest": "sha256:" + self.digest("artifact"),
            "schema_version": 11,
            "demonstration_case_ids": [case_id],
            "unresolved_defects": [],
            "limitations": ["Release authorization remains separate"],
            "exceptions": [],
            "unresolved_blockers": [],
            "reviewed_by": "Release QA Lead",
            "reviewed_at": "2026-07-14",
            "recommendation": "ready_for_release_authorization",
            "recommendation_rationale": "Clean governed regression evidence.",
            "evidence_references": ["CI-29330021187"],
            "content_hash": self.digest("QA-001"),
        }
        values.update(overrides)
        return self.qa.create(**values)

    def test_schema_v11_is_applied(self) -> None:
        self.assertEqual(SCHEMA_VERSION, 11)
        self.assertEqual(current_schema_version(self.database), 11)

    def test_additive_migration_from_v10_to_v11(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            database = Database(Path(tempdir) / "migration.db")
            self.assertEqual(migrations_v10.initialize_database(database), 10)
            self.assertEqual(current_schema_version(database), 10)
            self.assertEqual(initialize_database(database), 11)
            self.assertEqual(current_schema_version(database), 11)

    def test_demonstration_case_preserves_classification_scope_and_limitations(self) -> None:
        case = self.create_case()
        self.assertEqual(case["data_classification"], "synthetic")
        self.assertEqual(case["covered_builds"], [1, "2A", "2B", 3, 4, 5, 6, 7])
        self.assertEqual(case["limitations"], ["No deployment evidence"])
        self.assertEqual(self.cases.list_all(), [case])

    def test_release_qa_preserves_exact_ci_artifact_and_review_evidence(self) -> None:
        case = self.create_case()
        assessment = self.create_assessment(case["demonstration_case_id"])
        self.assertEqual(assessment["workflow_run_id"], "29330021187")
        self.assertEqual(assessment["job_id"], "87075460656")
        self.assertEqual(assessment["test_count"], 370)
        self.assertEqual(assessment["failure_count"], 0)
        self.assertEqual(assessment["error_count"], 0)
        self.assertEqual(assessment["schema_version"], 11)
        self.assertEqual(assessment["artifact_id"], "8309564912")
        self.assertTrue(assessment["artifact_digest"].startswith("sha256:"))
        self.assertEqual(assessment["reviewed_by"], "Release QA Lead")
        self.assertEqual(self.qa.list_all(), [assessment])

    def test_unknown_demonstration_case_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            self.create_assessment("missing-case")

    def test_ready_recommendation_rejects_failures_and_blockers(self) -> None:
        case = self.create_case()
        with self.assertRaisesRegex(ValueError, "zero failures"):
            self.create_assessment(case["demonstration_case_id"], failure_count=1)
        with self.assertRaisesRegex(ValueError, "unresolved blockers"):
            self.create_assessment(case["demonstration_case_id"], unresolved_blockers=["QA-BLOCKER"])

    def test_artifact_digest_requires_sha256(self) -> None:
        case = self.create_case()
        with self.assertRaisesRegex(ValueError, "sha256"):
            self.create_assessment(case["demonstration_case_id"], artifact_digest="md5:bad")

    def test_repository_and_database_immutability(self) -> None:
        case = self.create_case()
        assessment = self.create_assessment(case["demonstration_case_id"])
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.cases.update(case["demonstration_case_id"])
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.qa.delete(assessment["release_qa_assessment_id"])
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE demonstration_cases SET status = 'passed' WHERE demonstration_case_id = ?",
                    (case["demonstration_case_id"],),
                )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "DELETE FROM release_qa_assessments WHERE release_qa_assessment_id = ?",
                    (assessment["release_qa_assessment_id"],),
                )

    def test_release_tag_completion_deployment_sourcing_and_commercial_actions_are_rejected(self) -> None:
        case = self.create_case()
        prohibited = {
            "create_release_tag": True,
            "publish_github_release": True,
            "deployment_authorization": "approved",
            "declare_release_complete": True,
            "supplier_rank": 1,
            "sourcing_award_status": "awarded",
            "sourcing_allocation_percent": 100,
            "commercial_terms_approval": "approved",
        }
        for index, (field, value) in enumerate(prohibited.items(), start=1):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "cannot perform release"):
                self.create_assessment(
                    case["demonstration_case_id"],
                    assessment_code=f"QA-{index + 1:03d}",
                    content_hash=self.digest(f"QA-{index + 1:03d}"),
                    **{field: value},
                )


if __name__ == "__main__":
    unittest.main()
