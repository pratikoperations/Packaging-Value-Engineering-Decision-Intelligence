from __future__ import annotations

from typing import Any

from src.category_registry import default_registry
from src.persistence.project_repository import ProjectRepository

LEGACY_CATEGORY_ALIASES = {"corrugated_shipping_case": "corrugated"}


class ProjectService:
    """Application boundary for project lifecycle and dashboard operations."""

    def __init__(self, projects: ProjectRepository) -> None:
        self.projects = projects
        self.categories = default_registry()

    def create_project(
        self,
        *,
        project_code: str,
        project_name: str,
        category: str,
        currency: str,
        annual_volume: float,
        objective: str | None = None,
        change_type: str | None = None,
        **metadata: Any,
    ) -> dict[str, Any]:
        code = project_code.strip().upper()
        name = project_name.strip()
        stored_category = category.strip()
        registry_key = LEGACY_CATEGORY_ALIASES.get(stored_category, stored_category)
        normalized_currency = currency.strip().upper()
        if not code or not name:
            raise ValueError("Project code and name are required.")
        definition = self.categories.get(registry_key)
        if objective is not None and not definition.supports_objective(objective):
            raise ValueError("Unsupported project objective for this release.")
        if change_type is not None and not definition.supports_change_type(change_type):
            raise ValueError("Unsupported change type for the selected category.")
        if bool(objective) != bool(change_type):
            raise ValueError("Objective and change type must be supplied together.")
        if not normalized_currency:
            raise ValueError("Currency is required.")
        if annual_volume <= 0:
            raise ValueError("Annual volume must be greater than zero.")
        for field in ("current_unit_cost", "proposed_unit_cost", "implementation_cost", "testing_cost", "tooling_cost", "qualification_cost", "target_saving"):
            if metadata.get(field) is not None and float(metadata[field]) < 0:
                raise ValueError(f"{field} cannot be negative.")
        realization = metadata.get("expected_realization_percent")
        if realization is not None and not 0 <= float(realization) <= 100:
            raise ValueError("Expected realization percentage must be between 0 and 100.")
        return self.projects.create(
            project_code=code,
            project_name=name,
            category=stored_category,
            currency=normalized_currency,
            annual_volume=annual_volume,
            objective=objective,
            change_type=change_type,
            **metadata,
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

    def duplicate_project(self, project_id: str, *, new_project_code: str, new_project_name: str | None = None) -> dict[str, Any]:
        source = self.projects.get(project_id)
        name = new_project_name.strip() if new_project_name else f"{source['project_name']} Copy"
        copied = {key: source.get(key) for key in (
            "objective", "change_type", "product_sku", "business_unit_plant", "project_owner", "volume_unit",
            "current_unit_cost", "proposed_unit_cost", "current_supplier", "proposed_supplier", "target_saving",
            "target_completion_date", "implementation_cost", "testing_cost", "tooling_cost", "qualification_cost",
            "expected_realization_percent", "project_description", "business_justification", "sustainability_objective",
        )}
        return self.create_project(
            project_code=new_project_code,
            project_name=name,
            category=source["category"],
            currency=source["currency"],
            annual_volume=float(source["annual_volume"]),
            **copied,
        )

    def active_projects(self) -> list[dict[str, Any]]:
        return self.projects.list(archived=False)

    def archived_projects(self) -> list[dict[str, Any]]:
        return self.projects.list(archived=True)

    def portfolio_summary(self) -> dict[str, int]:
        return self.projects.portfolio_summary()

    def dashboard_projects(self, *, archived: bool = False) -> list[dict[str, Any]]:
        return self.projects.dashboard_rows(archived=archived)
