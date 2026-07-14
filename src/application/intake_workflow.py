from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.commercial import calculate_commercial_analysis
from src.persistence import Database, DatasetRepository, ProjectRepository
from src.persistence.migrations import initialize_database
from src.validation_readiness import assess_readiness


def load_active_context(database_path: str | Path, project_id: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    database = Database(database_path)
    initialize_database(database)
    project = ProjectRepository(database).get(project_id)
    versions = DatasetRepository(database).list_for_project(project_id)
    if not versions:
        raise ValueError("No validated dataset version is available for this project.")
    latest = versions[-1]
    canonical = json.loads(latest["canonical_json"])
    assessment = assess_readiness(project=project, canonical_data=canonical, dataset_id=latest["dataset_id"])
    return project, latest, {"canonical": canonical, "assessment": assessment}


def commercial_from_context(project: dict[str, Any], canonical: dict[str, Any]):
    values = {
        row.get("field_key"): row.get("value")
        for row in canonical.get("intake_values", [])
        if row.get("context") == "commercial"
    }
    required = {
        "current_unit_cost": values.get("current_unit_cost") or project.get("current_unit_cost"),
        "proposed_unit_cost": values.get("proposed_unit_cost") or project.get("proposed_unit_cost"),
        "annual_volume": values.get("annual_volume") or project.get("annual_volume"),
    }
    missing = [key for key, value in required.items() if value in (None, "")]
    if missing:
        return None, tuple(f"Missing required commercial input: {key}" for key in missing)
    try:
        return calculate_commercial_analysis(
            current_unit_cost=float(required["current_unit_cost"]),
            proposed_unit_cost=float(required["proposed_unit_cost"]),
            annual_volume=float(required["annual_volume"]),
            realization_percent=float(values.get("realization_percent") or project.get("expected_realization_percent") or 100),
            testing_cost=float(values.get("testing_cost") or project.get("testing_cost") or 0),
            tooling_cost=float(values.get("tooling_cost") or project.get("tooling_cost") or 0),
            implementation_cost=float(values.get("implementation_cost") or project.get("implementation_cost") or 0),
            qualification_cost=float(values.get("qualification_cost") or project.get("qualification_cost") or 0),
            assumptions=tuple(str(k) for k, v in values.items() if v not in (None, "")),
        ), ()
    except (TypeError, ValueError) as error:
        return None, (str(error),)
