from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.application import ProjectService
from src.category_registry import default_registry
from src.persistence import Database, ProjectRepository
from src.persistence.migrations import current_schema_version, initialize_database


class PVE11ProjectCreationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.tempdir.name) / "pve.sqlite3")
        initialize_database(self.database)
        self.service = ProjectService(ProjectRepository(self.database))

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_schema_v4_is_applied_additively(self):
        self.assertEqual(current_schema_version(self.database), 4)
        with self.database.connect() as connection:
            columns = {row[1] for row in connection.execute("PRAGMA table_info(projects)")}
        self.assertTrue({"objective", "change_type", "project_owner", "current_unit_cost", "expected_realization_percent"} <= columns)

    def test_every_category_can_create_project(self):
        for category in default_registry().keys():
            with self.subTest(category=category):
                definition = default_registry().get(category)
                project = self.service.create_project(
                    project_code=f"PVE-{category}",
                    project_name=f"{definition.display_name} project",
                    category=category,
                    objective=definition.objectives[0],
                    change_type=definition.change_types[0],
                    currency="INR",
                    annual_volume=1000,
                    volume_unit="units_per_year",
                    project_owner="Owner",
                    current_unit_cost=10,
                )
                self.assertEqual(project["category"], category)
                self.assertEqual(project["objective"], definition.objectives[0])
                self.assertEqual(project["change_type"], definition.change_types[0])

    def test_invalid_change_type_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported change type"):
            self.service.create_project(
                project_code="PVE-X",
                project_name="Invalid",
                category="labels",
                objective="Cost reduction",
                change_type="Ply reduction",
                currency="INR",
                annual_volume=100,
            )

    def test_legacy_corrugated_category_remains_compatible(self):
        project = self.service.create_project(
            project_code="LEGACY-1",
            project_name="Legacy",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=100,
        )
        self.assertEqual(project["category"], "corrugated_shipping_case")
        self.assertIsNone(project["objective"])

    def test_archived_project_metadata_cannot_be_changed(self):
        project = self.service.create_project(
            project_code="ARCH-1",
            project_name="Archive",
            category="glass",
            objective="Cost reduction",
            change_type="Weight reduction",
            currency="INR",
            annual_volume=100,
        )
        self.service.archive_project(project["project_id"])
        with self.assertRaisesRegex(ValueError, "read-only"):
            self.service.update_project(project["project_id"], project_owner="Changed")


if __name__ == "__main__":
    unittest.main()
