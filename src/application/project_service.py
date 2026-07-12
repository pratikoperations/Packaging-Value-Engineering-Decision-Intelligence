from __future__ import annotations

from typing import Any

from src.persistence.project_repository import ProjectRepository


class ProjectService:
    """Application boundary for project lifecycle operations."""

    def __init__(self, projects: ProjectRepository) -> None:
        self.projects = projects

    def create_project(
        self,
        *,
        project_code: str,
        project_name: str,
        category: str,
        currency: str,
        annual_volume: float,
    ) -> dict[str, Any]:
        if not project_code.strip() or not project_name.strip():
            raise ValueError("Project code and name are required.")
        if annual_volume <= 0:
            raise ValueError("Annual volume must be greater than zero.")
        return self.projects.create(
            project_code=project_code.strip(),
            project_name=project_name.strip(),
            category=category.strip(),
            currency=currency.strip().upper(),
            annual_volume=annual_volume,
        )

    def update_project(self, project_id: str, **changes: Any) -> dict[str, Any]:
        return self.projects.update_metadata(project_id, **changes)

    def archive_project(self, project_id: str) -> dict[str, Any]:
        return self.projects.archive(project_id)

    def active_projects(self) -> list[dict[str, Any]]:
        return self.projects.list(archived=False)

    def archived_projects(self) -> list[dict[str, Any]]:
        return self.projects.list(archived=True)
