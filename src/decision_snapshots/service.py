from __future__ import annotations

import json
from typing import Any

from src.decision_snapshots.models import DecisionSnapshotError, PreparedDecisionSnapshot
from src.persistence.dataset_repository import DatasetRepository
from src.persistence.decision_repository import DecisionRepository
from src.persistence.scenario_repository import ScenarioRepository

ENGINE_VERSION = "PVE-1.0.6"
SOURCE_COMMIT = "FINAL-RELEASE-CLOSURE"

_ELIGIBLE = {
    "eligible_for_engineering_review": 3,
    "conditionally_eligible_for_review": 2,
    "business_threshold_failed": 1,
    "insufficient_data": 0,
    "blocked": -1,
}


class DecisionSnapshotService:
    def __init__(
        self,
        datasets: DatasetRepository,
        scenarios: ScenarioRepository,
        decisions: DecisionRepository,
    ) -> None:
        self.datasets = datasets
        self.scenarios = scenarios
        self.decisions = decisions

    def available_scenarios(self, project_id: str) -> list[dict[str, Any]]:
        return self.scenarios.list_for_project(project_id)

    def prepare(self, *, project_id: str, scenario_id: str) -> PreparedDecisionSnapshot:
        scenario = self.scenarios.get(scenario_id)
        if scenario["project_id"] != project_id:
            raise DecisionSnapshotError("Scenario must belong to the active project.")

        dataset_record = self.datasets.get(scenario["dataset_id"])
        if dataset_record["project_id"] != project_id:
            raise DecisionSnapshotError("Scenario dataset must belong to the active project.")
        dataset = json.loads(dataset_record["canonical_json"])
        baseline = dataset.get("baseline_specification")
        baseline_id = baseline.get("alternative_id") if isinstance(baseline, dict) else None
        if not baseline_id:
            baseline_id = next(
                (
                    record.get("alternative_id")
                    for record in dataset.get("packaging_alternatives", [])
                    if isinstance(record, dict) and record.get("status") == "baseline"
                ),
                None,
            )
        if not baseline_id:
            raise DecisionSnapshotError("Dataset does not identify a baseline alternative.")

        results = json.loads(scenario["results_json"])
        alternatives = results.get("alternatives")
        if not isinstance(alternatives, dict) or not alternatives:
            raise DecisionSnapshotError("Scenario results do not contain alternatives.")

        proposed = [
            (alternative_id, record)
            for alternative_id, record in alternatives.items()
            if isinstance(record, dict) and alternative_id != baseline_id
        ]
        if not proposed:
            raise DecisionSnapshotError("Scenario does not contain a proposed alternative.")

        ranked = sorted(
            proposed,
            key=lambda item: (
                _ELIGIBLE.get(str(item[1].get("control_status")), -2),
                float(item[1].get("annual_savings_vs_baseline", 0.0)),
                -float(item[1].get("material_change_percent_vs_baseline", 0.0)),
                item[0],
            ),
            reverse=True,
        )
        preferred_id, preferred = ranked[0]
        control_status = str(preferred.get("control_status"))

        if control_status == "eligible_for_engineering_review":
            status = "recommended_for_engineering_review"
            summary = "Preferred alternative is recommended for engineering review, not approval."
        elif control_status == "conditionally_eligible_for_review":
            status = "conditionally_recommended_for_engineering_review"
            summary = "Preferred alternative is conditionally recommended for engineering review."
        elif control_status == "business_threshold_failed":
            status = "not_recommended_business_threshold_failed"
            summary = "No proposed alternative passes the configured business thresholds."
            preferred_id = None
        elif control_status == "insufficient_data":
            status = "insufficient_data"
            summary = "No recommendation can be issued because technical or risk evidence is incomplete."
            preferred_id = None
        else:
            status = "blocked"
            summary = "No recommendation can be issued because mandatory controls are blocking."
            preferred_id = None

        recommendation = {
            "status": status,
            "preferred_alternative_id": preferred_id,
            "summary": summary,
            "autonomous_approval": False,
            "engineering_validation_required": True,
            "human_approval_required": True,
            "decision_boundary": (
                "This snapshot records deterministic decision support only. It does not approve "
                "a packaging design or authorize supplier allocation."
            ),
        }
        gate_results = {
            "scenario_name": scenario["scenario_name"],
            "scenario_created_at": scenario["created_at"],
            "baseline_alternative_id": baseline_id,
            "threshold_profile": results.get("threshold_profile", {}),
            "mandatory_engineering_controls": results.get(
                "mandatory_engineering_controls", {}
            ),
            "alternatives": alternatives,
            "selected_control_status": control_status,
            "selected_technical_status": preferred.get("technical_status"),
            "selected_risk_level": preferred.get("risk_level"),
            "selected_business_thresholds_passed": preferred.get(
                "business_thresholds_passed"
            ),
            "selected_business_threshold_reasons": preferred.get(
                "business_threshold_reasons", []
            ),
            "selected_control_reasons": preferred.get("control_reasons", []),
        }
        return PreparedDecisionSnapshot(
            project_id=project_id,
            scenario_id=scenario_id,
            dataset_id=scenario["dataset_id"],
            threshold_profile_id=scenario["threshold_profile_id"],
            status=status,
            preferred_alternative_id=preferred_id,
            recommendation=recommendation,
            gate_results=gate_results,
        )

    def save(self, prepared: PreparedDecisionSnapshot) -> dict[str, Any]:
        return self.decisions.create_snapshot(
            project_id=prepared.project_id,
            scenario_id=prepared.scenario_id,
            dataset_id=prepared.dataset_id,
            threshold_profile_id=prepared.threshold_profile_id,
            status=prepared.status,
            preferred_alternative_id=prepared.preferred_alternative_id,
            recommendation=prepared.recommendation,
            gate_results=prepared.gate_results,
            engine_version=ENGINE_VERSION,
            source_commit=SOURCE_COMMIT,
        )

    def history(self, project_id: str) -> list[dict[str, Any]]:
        records = self.decisions.list_for_project(project_id)
        for record in records:
            record["recommendation"] = json.loads(record["recommendation_json"])
            record["gate_results"] = json.loads(record["gate_results_json"])
        return records
