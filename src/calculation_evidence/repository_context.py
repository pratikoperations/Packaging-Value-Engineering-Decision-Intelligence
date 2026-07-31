from __future__ import annotations

from pathlib import Path

from src.application.runtime import build_project_repository
from src.persistence.database import Database
from src.persistence.migrations import initialize_database
from src.persistence.scenario_repository import ScenarioRepository

from .domain import CalculationEvidenceError


class CalculationEvidenceRepositoryContext:
    """Read-only project-scoped access to persisted scenario evidence."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        database = Database(self.database_path)
        initialize_database(database)
        self.projects = build_project_repository(self.database_path)
        self.scenarios = ScenarioRepository(database)

    def list_projects(self) -> tuple[dict, ...]:
        return tuple(self.projects.list(archived=None))

    def list_scenarios(self, project_id: str) -> tuple[dict, ...]:
        self._project(project_id)
        return tuple(self.scenarios.list_for_project(project_id))

    def get_scenario(self, project_id: str, scenario_id: str) -> tuple[dict, bool]:
        project = self._project(project_id)
        try:
            scenario = self.scenarios.get(scenario_id)
        except KeyError as exc:
            raise CalculationEvidenceError("RECORD_NOT_FOUND", "The requested scenario was not found.") from exc
        if scenario.get("project_id") != project_id:
            raise CalculationEvidenceError("PROJECT_SCOPE_VIOLATION", "The requested scenario does not belong to the selected project.")
        return scenario, project.get("archived_at") is not None

    def _project(self, project_id: str) -> dict:
        for project in self.projects.list(archived=None):
            if project.get("project_id") == project_id:
                return project
        raise CalculationEvidenceError("RECORD_NOT_FOUND", "The requested project was not found.")
