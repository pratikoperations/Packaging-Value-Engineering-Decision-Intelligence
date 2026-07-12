from __future__ import annotations

from typing import Any

from src.persistence.project_repository import ProjectRepository


class ProjectService:
    """Application boundary for project lifecycle and dashboard operations."""

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
        code = project_code.strip().upper()
        name = project_name.strip()
        normalized_category = category.strip()
        normalized_currency = currency.strip().upper()
        if not code or not name:
            raise ValueError("Project code and name are required.")
        if not normalized_category:
            raise ValueError("Packaging category is required.")
        if not normalized_currency:
            raise ValueError("Currency is required.")
        if annual_volume <= 0:
            raise ValueError("Annual volume must be greater than zero.")
        return self.projects.create(
            project_code=code,
            project_name=name,
            category=normalized_category,
            currency=normalized_currency,
            annual_volume=annual_volume,
        )

    def get_project(self, project_id: str) -> dict[str, Any]:
        return self.projects.get(project_id)

    def update_project(self, project_id: str, **changes: Any) -> dict[str, Any]:
        if "annual_volume" in changes and float(changes["annual_volume"]) <= 0:
            raise ValueError("Annual volume must be greater than zero.")
        if "currency" in changes:
            changes["currency"] = str(changes["currency"]).strip().upper()
        if "project_name" in changes:
            changes["project_name"] = str(changes["project_name"]).strip()
        return self.projects.update_metadata(project_id, **changes)

    def archive_project(self, project_id: str) -> dict[str, Any]:
        return self.projects.archive(project_id)

    def duplicate_project(
        self,
        project_id: str,
        *,
        new_project_code: str,
        new_project_name: str | None = None,
    ) -> dict[str, Any]:
        source = self.projects.get(project_id)
        name = new_project_name.strip() if new_project_name else f"{source['project_name']} Copy"
        return self.create_project(
            project_code=new_project_code,
            project_name=name,
            category=source["category"],
            currency=source["currency"],
            annual_volume=float(source["annual_volume"]),
        )

    def active_projects(self) -> list[dict[str, Any]]:
        return self.projects.list(archived=False)

    def archived_projects(self) -> list[dict[str, Any]]:
        return self.projects.list(archived=True)

    def portfolio_summary(self) -> dict[str, int]:
        return self.projects.portfolio_summary()

    def dashboard_projects(self, *, archived: bool = False) -> list[dict[str, Any]]:
        return self.projects.dashboard_rows(archived=archived)
