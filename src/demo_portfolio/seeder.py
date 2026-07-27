from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.application.runtime import (
    build_controlled_scenario_service,
    build_decision_snapshot_service,
    build_project_service,
    build_threshold_service,
    build_upload_service,
)

DEMO_PROJECT_CODE = "PVE-DEMO-001"
DEMO_PROJECT_NAME = "Corrugated Shipper Value Engineering — Synthetic Demonstration"
DEMO_PROJECT_OBJECTIVE = "Cost reduction"
DEMO_PROJECT_CHANGE_TYPE = "Size optimization"
DEMO_THRESHOLD_NAME = "Portfolio Demonstration Thresholds"
DEMO_SCENARIO_NAME = "Balanced Cost and Evidence Review"
DEFAULT_SEED_PATH = Path(__file__).resolve().parents[2] / "data" / "demo" / "pve_portfolio_project.json"
DEMO_THRESHOLD_PROFILE: dict[str, Any] = {
    "minimum_annual_savings": 2_500_000.0,
    "minimum_material_reduction_percent": 5.0,
    "maximum_business_risk": "high",
    "require_positive_savings_or_material_reduction": True,
}


class PortfolioSeedConflict(ValueError):
    """Raised when an existing record conflicts with the controlled demo identity."""


@dataclass(frozen=True)
class PortfolioSeedResult:
    project: dict[str, Any]
    dataset: dict[str, Any]
    threshold_profile: dict[str, Any]
    scenario: dict[str, Any]
    decision_snapshot: dict[str, Any]
    created: tuple[str, ...]


def _load_seed(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("dataset_type") != "synthetic_demo":
        raise PortfolioSeedConflict("Portfolio seed must be explicitly classified as synthetic_demo.")
    project = payload.get("packaging_project")
    if not isinstance(project, dict) or project.get("project_id") != DEMO_PROJECT_CODE:
        raise PortfolioSeedConflict("Portfolio seed project identity is invalid.")
    return payload


def _get_existing_project(project_service) -> dict[str, Any] | None:
    try:
        return project_service.projects.get_by_code(DEMO_PROJECT_CODE)
    except KeyError:
        return None


def _validate_and_repair_existing_project(project_service, project: dict[str, Any]) -> dict[str, Any]:
    if project.get("archived_at") is not None:
        raise PortfolioSeedConflict("The controlled demonstration project is archived and cannot be reseeded.")

    expected_identity = {
        "project_name": DEMO_PROJECT_NAME,
        "category": "corrugated_shipping_case",
        "currency": "INR",
        "annual_volume": 1_200_000.0,
    }
    identity_conflicts = [
        field
        for field, value in expected_identity.items()
        if project.get(field) != value
    ]
    if identity_conflicts:
        raise PortfolioSeedConflict(
            "Project code PVE-DEMO-001 already exists with conflicting fields: "
            + ", ".join(sorted(identity_conflicts))
        )

    governed_metadata = {
        "objective": DEMO_PROJECT_OBJECTIVE,
        "change_type": DEMO_PROJECT_CHANGE_TYPE,
    }
    metadata_conflicts = [
        field
        for field, expected in governed_metadata.items()
        if project.get(field) not in (None, "", expected)
    ]
    if metadata_conflicts:
        raise PortfolioSeedConflict(
            "Project code PVE-DEMO-001 already exists with conflicting governed metadata: "
            + ", ".join(sorted(metadata_conflicts))
        )

    missing = {
        field: expected
        for field, expected in governed_metadata.items()
        if project.get(field) in (None, "")
    }
    if missing:
        project = project_service.update_project(project["project_id"], **missing)
    return project


def _find_threshold(threshold_service, project_id: str) -> dict[str, Any] | None:
    for record in threshold_service.available_profiles(project_id):
        if record["project_id"] == project_id and record["profile_name"] == DEMO_THRESHOLD_NAME:
            if record["profile"] != DEMO_THRESHOLD_PROFILE:
                raise PortfolioSeedConflict("Existing portfolio threshold profile has conflicting content.")
            return record
    return None


def _find_scenario(scenario_service, project_id: str, dataset_id: str, threshold_id: str) -> dict[str, Any] | None:
    for record in scenario_service.scenarios.list_for_project(project_id):
        if record["scenario_name"] != DEMO_SCENARIO_NAME:
            continue
        if record["dataset_id"] != dataset_id or record["threshold_profile_id"] != threshold_id:
            raise PortfolioSeedConflict("Existing portfolio scenario has conflicting record references.")
        return record
    return None


def _find_decision(decision_service, project_id: str, scenario_id: str) -> dict[str, Any] | None:
    for record in decision_service.history(project_id):
        if record["scenario_id"] == scenario_id:
            return record
    return None


def seed_portfolio_demo(
    database_path: str | Path,
    *,
    seed_path: str | Path = DEFAULT_SEED_PATH,
) -> PortfolioSeedResult:
    """Create or resume one linked synthetic demonstration record chain.

    The operation is intentionally idempotent. Existing immutable records are reused
    only when their controlled identities and references match the seed definition.
    It never updates, archives, unarchives, or overwrites existing immutable records.
    The only permitted metadata repair is to populate missing governed objective and
    change type values on the active controlled demonstration project.
    """

    payload = _load_seed(seed_path)
    project_service = build_project_service(database_path)
    upload_service = build_upload_service(database_path)
    threshold_service = build_threshold_service(database_path)
    scenario_service = build_controlled_scenario_service(database_path)
    decision_service = build_decision_snapshot_service(database_path)
    created: list[str] = []

    project = _get_existing_project(project_service)
    if project is None:
        project = project_service.create_project(
            project_code=DEMO_PROJECT_CODE,
            project_name=DEMO_PROJECT_NAME,
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1_200_000.0,
            objective=DEMO_PROJECT_OBJECTIVE,
            change_type=DEMO_PROJECT_CHANGE_TYPE,
            product_sku="SYNTHETIC-FMCG-CASE-12X1L",
            business_unit_plant="Synthetic Western India Plant",
            project_owner="Demonstration Procurement Owner",
            volume_unit="cases_per_year",
            current_unit_cost=52.4,
            current_supplier="Synthetic Supplier Alpha",
            project_description=(
                "Synthetic portfolio case for deterministic packaging value-engineering "
                "decision support. It is not supplier, laboratory, production, or commercial evidence."
            ),
            business_justification="Demonstrate controlled cost, material, evidence, and approval gates.",
            sustainability_objective="Demonstrate material-reduction analysis without claiming realized impact.",
        )
        created.append("project")
    else:
        project = _validate_and_repair_existing_project(project_service, project)

    prepared = upload_service.prepare_json(
        content=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        filename="pve_portfolio_project.json",
        project=project,
    )
    if not prepared.validation.is_valid:
        messages = "; ".join(issue.message for issue in prepared.validation.issues)
        raise PortfolioSeedConflict(f"Synthetic portfolio dataset failed validation: {messages}")
    dataset = upload_service.datasets.find_by_content(project["project_id"], prepared.canonical_data)
    if dataset is None:
        dataset = upload_service.save_valid_dataset(project_id=project["project_id"], prepared=prepared)
        created.append("dataset")

    threshold = _find_threshold(threshold_service, project["project_id"])
    if threshold is None:
        threshold = threshold_service.create_project_profile(
            project_id=project["project_id"],
            profile_name=DEMO_THRESHOLD_NAME,
            profile=DEMO_THRESHOLD_PROFILE,
        )
        created.append("threshold_profile")

    scenario = _find_scenario(
        scenario_service,
        project["project_id"],
        dataset["dataset_id"],
        threshold["threshold_profile_id"],
    )
    if scenario is None:
        alternatives = json.loads(dataset["canonical_json"])["packaging_alternatives"]
        adjustments = {item["alternative_id"]: 0.0 for item in alternatives}
        evaluated = scenario_service.evaluate(
            project_id=project["project_id"],
            dataset_id=dataset["dataset_id"],
            threshold_profile_id=threshold["threshold_profile_id"],
            scenario_name=DEMO_SCENARIO_NAME,
            annual_volume=float(project["annual_volume"]),
            cost_adjustments=adjustments,
            material_adjustments=adjustments,
        )
        scenario = scenario_service.save(evaluated)
        created.append("scenario")

    decision = _find_decision(decision_service, project["project_id"], scenario["scenario_id"])
    if decision is None:
        prepared_decision = decision_service.prepare(
            project_id=project["project_id"],
            scenario_id=scenario["scenario_id"],
        )
        decision = decision_service.save(prepared_decision)
        created.append("decision_snapshot")

    return PortfolioSeedResult(
        project=project,
        dataset=dataset,
        threshold_profile=threshold,
        scenario=scenario,
        decision_snapshot=decision,
        created=tuple(created),
    )
