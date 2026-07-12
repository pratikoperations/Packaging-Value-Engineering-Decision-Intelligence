from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from src.persistence.dataset_repository import DatasetRepository
from src.persistence.scenario_repository import ScenarioRepository
from src.persistence.threshold_repository import ThresholdRepository
from src.risk_engine import evaluate_risks
from src.scenario_engine import ScenarioInputs, evaluate_scenario
from src.scenario_execution.models import ControlledScenarioResult, ScenarioExecutionError
from src.technical_qualification import evaluate_technical_qualification
from src.thresholds import MANDATORY_ENGINEERING_CONTROLS
from src.thresholds.policy import business_thresholds_pass


class ControlledScenarioService:
    def __init__(
        self,
        datasets: DatasetRepository,
        thresholds: ThresholdRepository,
        scenarios: ScenarioRepository,
    ) -> None:
        self.datasets = datasets
        self.thresholds = thresholds
        self.scenarios = scenarios

    def available_datasets(self, project_id: str) -> list[dict[str, Any]]:
        return self.datasets.list_for_project(project_id)

    def available_thresholds(self, project_id: str) -> list[dict[str, Any]]:
        return self.thresholds.list_available(project_id)

    def evaluate(
        self,
        *,
        project_id: str,
        dataset_id: str,
        threshold_profile_id: str,
        scenario_name: str,
        annual_volume: float,
        cost_adjustments: dict[str, float],
        material_adjustments: dict[str, float],
    ) -> ControlledScenarioResult:
        clean_name = scenario_name.strip()
        if not clean_name:
            raise ScenarioExecutionError("Scenario name is required.")

        dataset_record = self.datasets.get(dataset_id)
        if dataset_record["project_id"] != project_id:
            raise ScenarioExecutionError("Dataset must belong to the active project.")

        threshold_record = self.thresholds.get(threshold_profile_id)
        if threshold_record["project_id"] not in (None, project_id):
            raise ScenarioExecutionError(
                "Threshold profile must be global or belong to the active project."
            )

        dataset = json.loads(dataset_record["canonical_json"])
        inputs = ScenarioInputs(
            annual_volume=annual_volume,
            cost_adjustment_percent_by_alternative=cost_adjustments,
            material_adjustment_percent_by_alternative=material_adjustments,
        )
        scenario = evaluate_scenario(dataset, inputs)
        technical = evaluate_technical_qualification(dataset)
        risks = evaluate_risks(dataset)

        alternatives: dict[str, Any] = {}
        for alternative_id, outcome in scenario.alternatives.items():
            qualification = technical[alternative_id]
            risk = risks[alternative_id]
            business_passed, business_reasons = business_thresholds_pass(
                profile=threshold_record["profile"],
                annual_savings=outcome.annual_savings_vs_baseline,
                material_change_percent=outcome.material_change_percent_vs_baseline,
                overall_risk=risk.overall_level,
            )

            control_reasons: list[str] = []
            if qualification.status == "not_qualified":
                control_reasons.append("Technical qualification status is not_qualified.")
            if qualification.status == "insufficient_data":
                control_reasons.append("Technical evidence is insufficient.")
            if risk.overall_level == "critical":
                control_reasons.append("Critical risk is blocking.")
            if not risk.data_complete:
                control_reasons.append("Required risk categories are incomplete.")

            if qualification.status == "not_qualified" or risk.overall_level == "critical":
                control_status = "blocked"
            elif qualification.status == "insufficient_data" or not risk.data_complete:
                control_status = "insufficient_data"
            elif not business_passed:
                control_status = "business_threshold_failed"
            elif qualification.status == "conditionally_qualified":
                control_status = "conditionally_eligible_for_review"
            else:
                control_status = "eligible_for_engineering_review"

            alternatives[alternative_id] = {
                **asdict(outcome),
                "technical_status": qualification.status,
                "technical_reasons": list(qualification.reasons),
                "technical_validation_required": list(qualification.validation_required),
                "risk_level": risk.overall_level,
                "risk_data_complete": risk.data_complete,
                "risk_reasons": list(risk.reasons),
                "risk_validation_required": list(risk.validation_required),
                "business_thresholds_passed": business_passed,
                "business_threshold_reasons": list(business_reasons),
                "control_status": control_status,
                "control_reasons": control_reasons,
                "engineering_validation_required": MANDATORY_ENGINEERING_CONTROLS[
                    "engineering_validation_required"
                ],
                "autonomous_approval_allowed": MANDATORY_ENGINEERING_CONTROLS[
                    "autonomous_approval_allowed"
                ],
            }

        assumptions = {
            "annual_volume": float(annual_volume),
            "cost_adjustment_percent_by_alternative": dict(cost_adjustments),
            "material_adjustment_percent_by_alternative": dict(material_adjustments),
        }
        results = {
            "annual_volume": scenario.annual_volume,
            "threshold_profile": {
                "threshold_profile_id": threshold_record["threshold_profile_id"],
                "profile_name": threshold_record["profile_name"],
                "version_number": threshold_record["version_number"],
                "profile": threshold_record["profile"],
            },
            "mandatory_engineering_controls": dict(MANDATORY_ENGINEERING_CONTROLS),
            "alternatives": alternatives,
            "decision_boundary": (
                "Scenario outputs are decision-support evidence only. Engineering validation "
                "and human approval remain mandatory."
            ),
        }
        return ControlledScenarioResult(
            project_id=project_id,
            dataset_id=dataset_id,
            threshold_profile_id=threshold_profile_id,
            scenario_name=clean_name,
            assumptions=assumptions,
            results=results,
        )

    def save(self, evaluated: ControlledScenarioResult) -> dict[str, Any]:
        return self.scenarios.create(
            project_id=evaluated.project_id,
            dataset_id=evaluated.dataset_id,
            threshold_profile_id=evaluated.threshold_profile_id,
            scenario_name=evaluated.scenario_name,
            assumptions=evaluated.assumptions,
            results=evaluated.results,
        )
