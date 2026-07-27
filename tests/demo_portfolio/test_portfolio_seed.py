from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.application.runtime import (
    build_controlled_scenario_service,
    build_decision_snapshot_service,
    build_project_service,
)
from src.demo_portfolio import DEMO_PROJECT_CODE, PortfolioSeedConflict, seed_portfolio_demo
from src.demo_portfolio.seeder import (
    DEMO_PROJECT_CHANGE_TYPE,
    DEMO_PROJECT_NAME,
    DEMO_PROJECT_OBJECTIVE,
)


class PortfolioSeedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.tempdir.name) / "portfolio.sqlite3"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_clean_seed_creates_complete_linked_record_chain(self) -> None:
        result = seed_portfolio_demo(self.database_path)

        self.assertEqual(
            result.created,
            ("project", "dataset", "threshold_profile", "scenario", "decision_snapshot"),
        )
        self.assertEqual(result.project["project_code"], DEMO_PROJECT_CODE)
        self.assertEqual(result.project["objective"], DEMO_PROJECT_OBJECTIVE)
        self.assertEqual(result.project["change_type"], DEMO_PROJECT_CHANGE_TYPE)
        self.assertEqual(result.dataset["project_id"], result.project["project_id"])
        self.assertEqual(result.threshold_profile["project_id"], result.project["project_id"])
        self.assertEqual(result.scenario["project_id"], result.project["project_id"])
        self.assertEqual(result.scenario["dataset_id"], result.dataset["dataset_id"])
        self.assertEqual(
            result.scenario["threshold_profile_id"],
            result.threshold_profile["threshold_profile_id"],
        )
        self.assertEqual(result.decision_snapshot["project_id"], result.project["project_id"])
        self.assertEqual(result.decision_snapshot["scenario_id"], result.scenario["scenario_id"])
        self.assertEqual(result.decision_snapshot["dataset_id"], result.dataset["dataset_id"])
        self.assertEqual(
            result.decision_snapshot["threshold_profile_id"],
            result.threshold_profile["threshold_profile_id"],
        )

        summary = build_project_service(self.database_path).portfolio_summary()
        self.assertEqual(summary["total_projects"], 1)
        self.assertEqual(summary["active_projects"], 1)
        self.assertEqual(summary["dataset_versions"], 1)
        self.assertEqual(summary["decision_snapshots"], 1)
        self.assertEqual(
            len(build_controlled_scenario_service(self.database_path).available_datasets(result.project["project_id"])),
            1,
        )
        self.assertEqual(
            len(build_decision_snapshot_service(self.database_path).history(result.project["project_id"])),
            1,
        )

    def test_repeated_seed_is_idempotent(self) -> None:
        first = seed_portfolio_demo(self.database_path)
        second = seed_portfolio_demo(self.database_path)

        self.assertEqual(second.created, ())
        self.assertEqual(second.project["project_id"], first.project["project_id"])
        self.assertEqual(second.dataset["dataset_id"], first.dataset["dataset_id"])
        self.assertEqual(
            second.threshold_profile["threshold_profile_id"],
            first.threshold_profile["threshold_profile_id"],
        )
        self.assertEqual(second.scenario["scenario_id"], first.scenario["scenario_id"])
        self.assertEqual(
            second.decision_snapshot["decision_snapshot_id"],
            first.decision_snapshot["decision_snapshot_id"],
        )

        summary = build_project_service(self.database_path).portfolio_summary()
        self.assertEqual(summary["total_projects"], 1)
        self.assertEqual(summary["dataset_versions"], 1)
        self.assertEqual(summary["decision_snapshots"], 1)
        self.assertEqual(
            len(build_controlled_scenario_service(self.database_path).available_datasets(first.project["project_id"])),
            1,
        )
        self.assertEqual(
            len(build_controlled_scenario_service(self.database_path).scenarios.list_for_project(first.project["project_id"])),
            1,
        )

    def test_existing_demo_with_missing_governed_metadata_is_repaired(self) -> None:
        service = build_project_service(self.database_path)
        existing = service.create_project(
            project_code=DEMO_PROJECT_CODE,
            project_name=DEMO_PROJECT_NAME,
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1_200_000.0,
        )

        result = seed_portfolio_demo(self.database_path)

        self.assertEqual(result.project["project_id"], existing["project_id"])
        self.assertEqual(result.project["objective"], DEMO_PROJECT_OBJECTIVE)
        self.assertEqual(result.project["change_type"], DEMO_PROJECT_CHANGE_TYPE)
        self.assertNotIn("project", result.created)
        self.assertEqual(service.portfolio_summary()["total_projects"], 1)

        repeated = seed_portfolio_demo(self.database_path)
        self.assertEqual(repeated.created, ())
        self.assertEqual(repeated.project["project_id"], existing["project_id"])

    def test_conflicting_governed_metadata_stops_without_overwrite(self) -> None:
        service = build_project_service(self.database_path)
        conflicting = service.create_project(
            project_code=DEMO_PROJECT_CODE,
            project_name=DEMO_PROJECT_NAME,
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1_200_000.0,
            objective="Material reduction",
            change_type="Ply reduction",
        )

        with self.assertRaisesRegex(PortfolioSeedConflict, "conflicting governed metadata"):
            seed_portfolio_demo(self.database_path)

        preserved = service.get_project(conflicting["project_id"])
        self.assertEqual(preserved["objective"], "Material reduction")
        self.assertEqual(preserved["change_type"], "Ply reduction")
        self.assertEqual(service.portfolio_summary()["dataset_versions"], 0)

    def test_seed_preserves_human_approval_and_non_autonomy_boundaries(self) -> None:
        result = seed_portfolio_demo(self.database_path)
        decision = build_decision_snapshot_service(self.database_path).history(result.project["project_id"])[0]
        recommendation = decision["recommendation"]

        self.assertFalse(recommendation["autonomous_approval"])
        self.assertTrue(recommendation["engineering_validation_required"])
        self.assertTrue(recommendation["human_approval_required"])
        self.assertNotIn("approved", recommendation["status"])
        self.assertIn(
            recommendation["status"],
            {
                "recommended_for_engineering_review",
                "conditionally_recommended_for_engineering_review",
                "not_recommended_business_threshold_failed",
                "insufficient_data",
                "blocked",
            },
        )

    def test_conflicting_project_code_stops_without_overwrite(self) -> None:
        service = build_project_service(self.database_path)
        conflicting = service.create_project(
            project_code=DEMO_PROJECT_CODE,
            project_name="Conflicting Project",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1_200_000.0,
        )

        with self.assertRaisesRegex(PortfolioSeedConflict, "conflicting fields"):
            seed_portfolio_demo(self.database_path)

        preserved = service.get_project(conflicting["project_id"])
        self.assertEqual(preserved["project_name"], "Conflicting Project")
        self.assertEqual(service.portfolio_summary()["dataset_versions"], 0)

    def test_archived_demo_project_is_not_reactivated_or_modified(self) -> None:
        first = seed_portfolio_demo(self.database_path)
        service = build_project_service(self.database_path)
        service.archive_project(first.project["project_id"])

        with self.assertRaisesRegex(PortfolioSeedConflict, "archived"):
            seed_portfolio_demo(self.database_path)

        archived = service.get_project(first.project["project_id"])
        self.assertIsNotNone(archived["archived_at"])
        self.assertEqual(service.portfolio_summary()["active_projects"], 0)
        self.assertEqual(service.portfolio_summary()["archived_projects"], 1)


if __name__ == "__main__":
    unittest.main()
