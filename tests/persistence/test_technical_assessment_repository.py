from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.category_registry import build_engineering_recommendation
from src.persistence import (
    Database,
    DatasetRepository,
    ProjectRepository,
    ReadinessRepository,
    TechnicalAssessmentRepository,
)
from src.persistence.migrations import current_schema_version, initialize_database


class TechnicalAssessmentRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.tempdir.name) / "pve.sqlite3")
        initialize_database(self.database)
        self.projects = ProjectRepository(self.database)
        self.datasets = DatasetRepository(self.database)
        self.readiness = ReadinessRepository(self.database)
        self.assessments = TechnicalAssessmentRepository(self.database)
        self.project = self.projects.create(
            project_code="PVE-1", project_name="Corrugated", category="corrugated",
            currency="INR", annual_volume=100000,
        )
        self.other_project = self.projects.create(
            project_code="PVE-2", project_name="Other", category="corrugated",
            currency="INR", annual_volume=50000,
        )
        self.dataset = self.datasets.create_version(
            project_id=self.project["project_id"], source_type="json",
            canonical_data={"version": 1}, validation_status="valid",
        )
        self.other_dataset = self.datasets.create_version(
            project_id=self.other_project["project_id"], source_type="json",
            canonical_data={"version": 1}, validation_status="valid",
        )
        self.readiness_record = self.readiness.create(
            project_id=self.project["project_id"], dataset_id=self.dataset["dataset_id"],
            assessment={"score_percent": 90, "stage": "validation_ready"},
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def create_assessment(self, **overrides):
        values = {
            "project_id": self.project["project_id"],
            "readiness_assessment_id": self.readiness_record["readiness_assessment_id"],
            "dataset_id": self.dataset["dataset_id"],
            "baseline_specification_version": "BASE-1",
            "proposed_specification_version": "PROP-1",
            "rule_set_version": "PVE-1.2-B7",
            "threshold_profile_id": None,
            "threshold_references": ["REQ-BCT-1"],
            "evidence_references": [{"evidence_id": "EV-1", "project_id": self.project["project_id"]}],
            "formula_inputs": {"bct_n": 4200},
            "assumptions": ["No hidden defaults."],
            "technical_outcomes": {"screening": "criteria met"},
            "commercial_outcomes": {"risk_adjusted_benefit": 250000},
            "blockers": [],
            "required_trials": [],
            "evidence_confidence_status": "High evidence confidence",
            "recommendation_outcome": "criteria met for engineering review",
        }
        values.update(overrides)
        return self.assessments.create(**values)

    def test_schema_version_four_and_append_only_create(self):
        self.assertEqual(current_schema_version(self.database), 4)
        created = self.create_assessment()
        self.assertEqual(created["dataset_version"], 1)
        self.assertEqual(created["recommendation_outcome"], "criteria met for engineering review")
        self.assertEqual(len(self.assessments.list_for_project(self.project["project_id"])), 1)

    def test_repository_update_and_delete_are_rejected(self):
        created = self.create_assessment()
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.assessments.update(created["technical_assessment_id"])
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.assessments.delete(created["technical_assessment_id"])

    def test_database_update_and_delete_triggers_are_rejected(self):
        created = self.create_assessment()
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE technical_assessments SET recommendation_outcome = 'changed' WHERE technical_assessment_id = ?",
                    (created["technical_assessment_id"],),
                )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "DELETE FROM technical_assessments WHERE technical_assessment_id = ?",
                    (created["technical_assessment_id"],),
                )

    def test_archived_project_write_is_rejected(self):
        self.projects.archive(self.project["project_id"])
        with self.assertRaisesRegex(ValueError, "read-only"):
            self.create_assessment()

    def test_cross_project_dataset_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "same project"):
            self.create_assessment(dataset_id=self.other_dataset["dataset_id"])

    def test_cross_project_evidence_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Evidence references"):
            self.create_assessment(
                evidence_references=[{"evidence_id": "EV-X", "project_id": self.other_project["project_id"]}]
            )

    def test_historical_dataset_and_readiness_remain_unchanged(self):
        before_dataset = self.datasets.get(self.dataset["dataset_id"])
        before_readiness = self.readiness.get(self.readiness_record["readiness_assessment_id"])
        self.create_assessment()
        self.assertEqual(self.datasets.get(self.dataset["dataset_id"]), before_dataset)
        self.assertEqual(self.readiness.get(self.readiness_record["readiness_assessment_id"]), before_readiness)


class EngineeringRecommendationTestCase(unittest.TestCase):
    def test_evidence_conflict_has_highest_precedence(self):
        result = build_engineering_recommendation(
            screening_outcome="evidence conflict", technical_blockers=("BCT below requirement",),
            evidence_confidence="Low evidence confidence", economics={"benefit": 1000000},
        )
        self.assertEqual(result.outcome, "evidence conflict")

    def test_high_saving_cannot_override_technical_blocker(self):
        result = build_engineering_recommendation(
            screening_outcome="criteria met", technical_blockers=("BCT below requirement",),
            evidence_confidence="High evidence confidence", economics={"benefit": 1000000},
        )
        self.assertEqual(result.outcome, "criteria not met")
        self.assertIn("override commercial attractiveness", result.rationale[0])

    def test_trial_precedence_and_confidence_separation(self):
        result = build_engineering_recommendation(
            screening_outcome="criteria met", required_trials=("Packing-line trial required",),
            evidence_confidence="Moderate evidence confidence",
        )
        self.assertEqual(result.outcome, "packing-line trial required")
        self.assertEqual(result.evidence_confidence, "Moderate evidence confidence")
        self.assertIn("not probability", result.limitations[1])

    def test_criteria_met_remains_review_only(self):
        result = build_engineering_recommendation(
            screening_outcome="criteria met", evidence_confidence="High evidence confidence",
        )
        self.assertEqual(result.outcome, "criteria met for engineering review")
        self.assertNotIn(result.outcome, {"Approved", "Rejected", "Conditional"})


if __name__ == "__main__":
    unittest.main()
