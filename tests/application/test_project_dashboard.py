from __future__ import annotations

import ast
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any, MutableMapping

from src.application import ProjectService
from src.application.runtime import build_project_service
from src.persistence import (
    Database,
    DatasetRepository,
    DecisionRepository,
    ProjectRepository,
    ScenarioRepository,
    ThresholdRepository,
)
from src.persistence.migrations import initialize_database

ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_PATH = ROOT / "pages" / "01_Project_Dashboard.py"


def load_workspace_selector():
    """Load only the pure workspace selector without importing Streamlit page code."""
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "select_active_workspace"
    )
    module = ast.Module(body=[function], type_ignores=[])
    namespace = {"MutableMapping": MutableMapping}
    exec(compile(module, str(DASHBOARD_PATH), "exec"), namespace)
    return namespace["select_active_workspace"]


def load_portfolio_helpers():
    """Load the pure seed-completeness and presentation helpers without Streamlit."""
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    selected = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "SEED_STAGES" for target in node.targets
        ):
            selected.append(node)
        if isinstance(node, ast.FunctionDef) and node.name in {
            "portfolio_seed_complete",
            "seed_stage_rows",
        }:
            selected.append(node)
    module = ast.Module(body=selected, type_ignores=[])
    namespace = {"Any": Any}
    exec(compile(module, str(DASHBOARD_PATH), "exec"), namespace)
    return namespace["portfolio_seed_complete"], namespace["seed_stage_rows"]


class ProjectDashboardTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.tempdir.name) / "dashboard.sqlite3"
        self.database = Database(self.database_path)
        initialize_database(self.database)
        self.projects = ProjectRepository(self.database)
        self.service = ProjectService(self.projects)
        self.datasets = DatasetRepository(self.database)
        self.thresholds = ThresholdRepository(self.database)
        self.scenarios = ScenarioRepository(self.database)
        self.decisions = DecisionRepository(self.database)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def create_project(self, code: str = "PVE-001") -> dict:
        return self.service.create_project(
            project_code=code,
            project_name="Corrugated optimization",
            category="corrugated_shipping_case",
            currency="inr",
            annual_volume=1_200_000,
        )

    def test_empty_portfolio_summary(self):
        self.assertEqual(
            self.service.portfolio_summary(),
            {
                "total_projects": 0,
                "active_projects": 0,
                "archived_projects": 0,
                "dataset_versions": 0,
                "decision_snapshots": 0,
            },
        )

    def test_create_project_normalizes_code_and_currency(self):
        project = self.service.create_project(
            project_code=" pve-001 ",
            project_name=" Project ",
            category="corrugated_shipping_case",
            currency="inr",
            annual_volume=100,
        )
        self.assertEqual(project["project_code"], "PVE-001")
        self.assertEqual(project["currency"], "INR")
        self.assertEqual(project["project_name"], "Project")

    def test_duplicate_project_copies_metadata_only(self):
        source = self.create_project()
        self.datasets.create_version(
            project_id=source["project_id"],
            source_type="json",
            canonical_data={"version": 1},
            validation_status="valid",
        )
        duplicate = self.service.duplicate_project(
            source["project_id"],
            new_project_code="PVE-002",
            new_project_name="Copy",
        )
        self.assertEqual(duplicate["category"], source["category"])
        self.assertEqual(duplicate["annual_volume"], source["annual_volume"])
        rows = self.service.dashboard_projects(archived=False)
        duplicate_row = next(row for row in rows if row["project_id"] == duplicate["project_id"])
        self.assertEqual(duplicate_row["dataset_versions"], 0)
        self.assertEqual(duplicate_row["decisions"], 0)

    def test_duplicate_project_rejects_existing_code(self):
        first = self.create_project("PVE-001")
        self.create_project("PVE-002")
        with self.assertRaises(sqlite3.IntegrityError):
            self.service.duplicate_project(first["project_id"], new_project_code="PVE-002")

    def test_archive_moves_project_to_archived_dashboard(self):
        project = self.create_project()
        self.service.archive_project(project["project_id"])
        self.assertEqual(self.service.dashboard_projects(archived=False), [])
        archived = self.service.dashboard_projects(archived=True)
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0]["status"], "archived")

    def test_dashboard_counts_related_records(self):
        project = self.create_project()
        dataset = self.datasets.create_version(
            project_id=project["project_id"],
            source_type="json",
            canonical_data={"version": 1},
            validation_status="valid",
        )
        threshold = self.thresholds.create_version(
            project_id=project["project_id"],
            profile_name="Default",
            profile={"minimum_annual_savings": 0},
        )
        scenario = self.scenarios.create(
            project_id=project["project_id"],
            dataset_id=dataset["dataset_id"],
            threshold_profile_id=threshold["threshold_profile_id"],
            scenario_name="Base",
            assumptions={"annual_volume": 100},
            results={"annual_savings": 10},
        )
        self.decisions.create_snapshot(
            project_id=project["project_id"],
            scenario_id=scenario["scenario_id"],
            dataset_id=dataset["dataset_id"],
            threshold_profile_id=threshold["threshold_profile_id"],
            status="conditionally_recommended",
            recommendation={"status": "conditionally_recommended"},
            gate_results={"engineering_validation_required": True},
            engine_version="1.0.2",
            source_commit="TEST",
        )
        row = self.service.dashboard_projects(archived=False)[0]
        self.assertEqual(row["dataset_versions"], 1)
        self.assertEqual(row["scenarios"], 1)
        self.assertEqual(row["decisions"], 1)
        self.assertEqual(row["latest_decision_status"], "conditionally_recommended")

    def test_portfolio_summary_counts_active_archived_and_evidence(self):
        active = self.create_project("PVE-001")
        archived = self.create_project("PVE-002")
        self.service.archive_project(archived["project_id"])
        self.datasets.create_version(
            project_id=active["project_id"],
            source_type="json",
            canonical_data={"version": 1},
            validation_status="valid",
        )
        summary = self.service.portfolio_summary()
        self.assertEqual(summary["total_projects"], 2)
        self.assertEqual(summary["active_projects"], 1)
        self.assertEqual(summary["archived_projects"], 1)
        self.assertEqual(summary["dataset_versions"], 1)

    def test_runtime_factory_initializes_database(self):
        path = Path(self.tempdir.name) / "nested" / "runtime.sqlite3"
        service = build_project_service(path)
        service.create_project(
            project_code="RUNTIME-1",
            project_name="Runtime",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1,
        )
        self.assertTrue(path.exists())
        self.assertEqual(service.portfolio_summary()["total_projects"], 1)

    def test_dashboard_static_contract(self):
        dashboard = DASHBOARD_PATH.read_text(encoding="utf-8")
        for marker in (
            "Packaging Value Engineering Project Dashboard",
            "Create Project",
            "Active Projects",
            "Archived Projects",
            "Select as active workspace",
            "Current active workspace",
            "Duplicate project metadata",
            "Archive selected project",
            "local SQLite demonstration persistence",
            "Portfolio Demonstration",
            "Load demonstration project",
            "seed_portfolio_demo(DATABASE_PATH)",
            "Guided workflow after loading",
            "Decision History",
        ):
            self.assertIn(marker, dashboard)

    def test_dashboard_preserves_demo_governance_warnings(self):
        dashboard = DASHBOARD_PATH.read_text(encoding="utf-8")
        for marker in (
            "synthetic data only",
            "not supplier, laboratory, production",
            "Engineering validation and documented human approval remain mandatory",
            "autonomous approval is prohibited",
            "It is not production storage",
        ):
            self.assertIn(marker, dashboard)

    def test_dashboard_does_not_claim_realized_savings(self):
        dashboard = DASHBOARD_PATH.read_text(encoding="utf-8")
        self.assertIn("do not represent realized savings", dashboard)
        self.assertNotIn("Realized Savings", dashboard)

    def test_demo_success_requires_complete_record_chain(self):
        complete, _ = load_portfolio_helpers()
        complete_result = SimpleNamespace(
            project={"project_id": "project-1"},
            dataset={"dataset_id": "dataset-1"},
            threshold_profile={"threshold_profile_id": "threshold-1"},
            scenario={"scenario_id": "scenario-1"},
            decision_snapshot={"decision_snapshot_id": "decision-1"},
        )
        self.assertTrue(complete(complete_result))
        complete_result.decision_snapshot = {}
        self.assertFalse(complete(complete_result))

    def test_demo_stage_rows_distinguish_created_and_reused_records(self):
        _, rows = load_portfolio_helpers()
        presented = rows(("project", "scenario"))
        by_name = {row["Workflow record"]: row["Load result"] for row in presented}
        self.assertEqual(by_name["Project workspace"], "Created")
        self.assertEqual(by_name["Controlled scenario"], "Created")
        self.assertEqual(by_name["Validated dataset version"], "Reused existing record")
        self.assertEqual(by_name["Immutable decision snapshot"], "Reused existing record")

    def test_dashboard_records_feedback_only_after_complete_chain_check(self):
        dashboard = DASHBOARD_PATH.read_text(encoding="utf-8")
        completion_check = dashboard.index("if not portfolio_seed_complete(result):")
        feedback_write = dashboard.index("st.session_state[SEED_FEEDBACK_KEY] =")
        self.assertLess(completion_check, feedback_write)
        self.assertIn("Demonstration project was not loaded", dashboard)

    def test_active_project_can_be_selected_explicitly(self):
        select_active_workspace = load_workspace_selector()
        session_state: dict[str, object] = {}
        selected = select_active_workspace(
            session_state,
            "project-active",
            archived=False,
        )
        self.assertTrue(selected)
        self.assertEqual(session_state["active_project_id"], "project-active")

    def test_archived_project_cannot_become_active_workspace(self):
        select_active_workspace = load_workspace_selector()
        session_state: dict[str, object] = {}
        selected = select_active_workspace(
            session_state,
            "project-archived",
            archived=True,
        )
        self.assertFalse(selected)
        self.assertNotIn("active_project_id", session_state)

    def test_archived_selection_does_not_overwrite_existing_active_workspace(self):
        select_active_workspace = load_workspace_selector()
        session_state: dict[str, object] = {"active_project_id": "project-active"}
        selected = select_active_workspace(
            session_state,
            "project-archived",
            archived=True,
        )
        self.assertFalse(selected)
        self.assertEqual(session_state["active_project_id"], "project-active")

    def test_archived_projects_remain_read_only_in_source_contract(self):
        dashboard = DASHBOARD_PATH.read_text(encoding="utf-8")
        archived_guard = dashboard.index("if archived:")
        workspace_button = dashboard.index('"Select as active workspace"')
        self.assertLess(archived_guard, workspace_button)
        self.assertIn("cannot become the active workspace", dashboard)

    def test_dashboard_scope_excludes_future_workflows(self):
        dashboard = DASHBOARD_PATH.read_text(encoding="utf-8")
        for prohibited in (
            "st.file_uploader",
            "Run scenario",
            "Configure thresholds",
        ):
            self.assertNotIn(prohibited, dashboard)


if __name__ == "__main__":
    unittest.main()
