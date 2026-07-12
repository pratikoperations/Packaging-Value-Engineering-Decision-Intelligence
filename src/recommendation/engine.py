from __future__ import annotations

from dataclasses import dataclass

from src.risk_engine import RiskOutcome
from src.scenario_engine import ScenarioResult
from src.technical_qualification import QualificationOutcome


_STATUS_PRIORITY = {
    "recommended": 0,
    "conditionally_recommended": 1,
    "insufficient_data": 2,
    "not_recommended": 3,
}
_RISK_PRIORITY = {"low": 0, "medium": 1, "high": 2, "critical": 3, "not_recorded": 4}


@dataclass(frozen=True)
class AlternativeRecommendation:
    alternative_id: str
    status: str
    rationale: tuple[str, ...]
    constraints: tuple[str, ...]
    validation_required: tuple[str, ...]
    annual_savings_vs_baseline: float
    material_change_percent_vs_baseline: float
    overall_risk: str
    qualification_status: str


@dataclass(frozen=True)
class RecommendationResult:
    preferred_alternative_id: str | None
    alternatives: dict[str, AlternativeRecommendation]
    selection_basis: tuple[str, ...]


def recommend_alternatives(
    dataset: dict,
    scenario: ScenarioResult,
    qualifications: dict[str, QualificationOutcome],
    risks: dict[str, RiskOutcome],
) -> RecommendationResult:
    """Create transparent, rule-based recommendations for packaging alternatives.

    The function recommends packaging designs, not suppliers. It uses no opaque score,
    does not allocate volume, and never grants autonomous technical approval.
    """
    alternatives = dataset.get("packaging_alternatives")
    if not isinstance(alternatives, list) or not alternatives:
        raise ValueError("packaging_alternatives must be a non-empty list.")

    proposed_ids = []
    for record in alternatives:
        alternative_id = record.get("alternative_id")
        if record.get("status") == "proposed":
            proposed_ids.append(alternative_id)

    outputs: dict[str, AlternativeRecommendation] = {}
    for alternative_id in proposed_ids:
        if alternative_id not in scenario.alternatives:
            raise ValueError(f"Scenario result missing for {alternative_id}.")
        if alternative_id not in qualifications:
            raise ValueError(f"Qualification outcome missing for {alternative_id}.")
        if alternative_id not in risks:
            raise ValueError(f"Risk outcome missing for {alternative_id}.")

        scenario_result = scenario.alternatives[alternative_id]
        qualification = qualifications[alternative_id]
        risk = risks[alternative_id]
        rationale: list[str] = []
        constraints: list[str] = []
        validation_required = list(qualification.validation_required) + list(risk.validation_required)

        if qualification.status == "not_qualified":
            status = "not_recommended"
            constraints.append("Technical qualification failed.")
        elif risk.overall_level == "critical":
            status = "not_recommended"
            constraints.append("Critical risk must be reduced before consideration.")
        elif qualification.status == "insufficient_data":
            status = "insufficient_data"
            constraints.append("Technical qualification basis is incomplete.")
        elif scenario_result.annual_savings_vs_baseline <= 0 and scenario_result.material_change_percent_vs_baseline >= 0:
            status = "not_recommended"
            constraints.append("No positive annual savings or material reduction versus baseline.")
        elif (
            qualification.status == "conditionally_qualified"
            or risk.overall_level == "high"
            or not risk.data_complete
            or bool(validation_required)
        ):
            status = "conditionally_recommended"
            constraints.append("Recommendation depends on completing listed validation and risk actions.")
        else:
            status = "recommended"

        if scenario_result.annual_savings_vs_baseline > 0:
            rationale.append(
                f"Annual savings versus baseline: {scenario_result.annual_savings_vs_baseline:.2f}."
            )
        else:
            rationale.append(
                f"Annual savings versus baseline are not positive: {scenario_result.annual_savings_vs_baseline:.2f}."
            )

        if scenario_result.material_change_percent_vs_baseline < 0:
            rationale.append(
                f"Material reduction versus baseline: {-scenario_result.material_change_percent_vs_baseline:.2f}%."
            )
        else:
            rationale.append(
                f"Material change versus baseline: {scenario_result.material_change_percent_vs_baseline:.2f}%."
            )

        rationale.append(f"Qualification status: {qualification.status}.")
        rationale.append(f"Overall risk: {risk.overall_level}; data complete: {risk.data_complete}.")
        rationale.extend(qualification.reasons)
        rationale.extend(risk.reasons)

        outputs[alternative_id] = AlternativeRecommendation(
            alternative_id=alternative_id,
            status=status,
            rationale=tuple(dict.fromkeys(rationale)),
            constraints=tuple(dict.fromkeys(constraints)),
            validation_required=tuple(dict.fromkeys(validation_required)),
            annual_savings_vs_baseline=scenario_result.annual_savings_vs_baseline,
            material_change_percent_vs_baseline=scenario_result.material_change_percent_vs_baseline,
            overall_risk=risk.overall_level,
            qualification_status=qualification.status,
        )

    eligible = [
        item for item in outputs.values() if item.status in {"recommended", "conditionally_recommended"}
    ]
    preferred = None
    if eligible:
        eligible.sort(
            key=lambda item: (
                _STATUS_PRIORITY[item.status],
                -item.annual_savings_vs_baseline,
                item.material_change_percent_vs_baseline,
                _RISK_PRIORITY[item.overall_risk],
                item.alternative_id,
            )
        )
        preferred = eligible[0].alternative_id

    selection_basis = (
        "Status precedence: recommended before conditionally recommended.",
        "Then higher annual savings versus baseline.",
        "Then greater material reduction versus baseline.",
        "Then lower effective risk and stable alternative identifier tie-break.",
        "No supplier ranking, allocation, or opaque weighted score is used.",
    )

    return RecommendationResult(
        preferred_alternative_id=preferred,
        alternatives=outputs,
        selection_basis=selection_basis,
    )
