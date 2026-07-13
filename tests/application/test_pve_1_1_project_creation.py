from __future__ import annotations

from pathlib import Path

import pytest

from src.application import ProjectService
from src.category_registry import default_registry
from src.persistence import Database, ProjectRepository
from src.persistence.migrations import current_schema_version, initialize_database


def build_service(tmp_path: Path) -> tuple[Database, ProjectService]:
    database = Database(tmp_path / "pve.sqlite3")
    initialize_database(database)
    return database, ProjectService(ProjectRepository(database))


def test_schema_v2_is_applied_additively(tmp_path: Path):
    database, _ = build_service(tmp_path)
    assert current_schema_version(database) == 2
    with database.connect() as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(projects)")}
    assert {"objective", "change_type", "project_owner", "current_unit_cost", "expected_realization_percent"} <= columns


@pytest.mark.parametrize("category", default_registry().keys())
def test_every_category_can_create_project(tmp_path: Path, category: str):
    _, service = build_service(tmp_path)
    definition = default_registry().get(category)
    project = service.create_project(
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
    assert project["category"] == category
    assert project["objective"] == definition.objectives[0]
    assert project["change_type"] == definition.change_types[0]


def test_invalid_change_type_is_rejected(tmp_path: Path):
    _, service = build_service(tmp_path)
    with pytest.raises(ValueError, match="Unsupported change type"):
        service.create_project(
            project_code="PVE-X",
            project_name="Invalid",
            category="labels",
            objective="Cost reduction",
            change_type="Ply reduction",
            currency="INR",
            annual_volume=100,
        )


def test_legacy_corrugated_category_remains_compatible(tmp_path: Path):
    _, service = build_service(tmp_path)
    project = service.create_project(
        project_code="LEGACY-1",
        project_name="Legacy",
        category="corrugated_shipping_case",
        currency="INR",
        annual_volume=100,
    )
    assert project["category"] == "corrugated_shipping_case"
    assert project["objective"] is None


def test_archived_project_metadata_cannot_be_changed(tmp_path: Path):
    _, service = build_service(tmp_path)
    project = service.create_project(
        project_code="ARCH-1",
        project_name="Archive",
        category="glass",
        objective="Cost reduction",
        change_type="Weight reduction",
        currency="INR",
        annual_volume=100,
    )
    service.archive_project(project["project_id"])
    with pytest.raises(ValueError, match="read-only"):
        service.update_project(project["project_id"], project_owner="Changed")
