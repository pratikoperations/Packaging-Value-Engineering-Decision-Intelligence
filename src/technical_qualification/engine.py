from __future__ import annotations

from dataclasses import dataclass
from typing import Any


_ALLOWED_STATUSES = {
    "not_assessed",
    "qualified",
    "conditionally_qualified",
    "not_qualified",
    "insufficient_data",
}
_EVIDENCE_REQUIRED_STATUSES = {
    "qualified",
    "conditionally_qualified",
    "not_qualified",
}


@dataclass(frozen=True)
class QualificationOutcome:
    alternative_id: str
    status: str
    reasons: tuple[str, ...]
    missing_requirement_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    validation_required: tuple[str, ...]


def _require_list(value: Any, path: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{path} must be a list.")
    if not all(isinstance(item, dict) for item in value):
        raise ValueError(f"Every item in {path} must be an object.")
    return value


def _deduplicate(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def evaluate_technical_qualification(dataset: dict[str, Any]) -> dict[str, QualificationOutcome]:
    """Evaluate deterministic technical qualification for every alternative.

    This function aggregates declared qualification records only. It never approves a
    packaging design autonomously and does not calculate recommendation scores.
    """
    alternatives = _require_list(dataset.get("packaging_alternatives"), "packaging_alternatives")
    requirements = _require_list(dataset.get("technical_requirements"), "technical_requirements")
    results = _require_list(
        dataset.get("technical_qualification_results"), "technical_qualification_results"
    )
    validations = _require_list(dataset.get("validation_requirements", []), "validation_requirements")
    evidence = _require_list(dataset.get("decision_evidence", []), "decision_evidence")

    alternative_ids: set[str] = set()
    for record in alternatives:
        alternative_id = record.get("alternative_id")
        if not isinstance(alternative_id, str) or not alternative_id:
            raise ValueError("Every packaging alternative requires a non-empty alternative_id.")
        if alternative_id in alternative_ids:
            raise ValueError("Alternative identifiers must be unique.")
        alternative_ids.add(alternative_id)

    requirement_names: dict[str, str] = {}
    for record in requirements:
        requirement_id = record.get("requirement_id")
        name = record.get("name")
        if not isinstance(requirement_id, str) or not requirement_id:
            raise ValueError("Every technical requirement requires a non-empty requirement_id.")
        if requirement_id in requirement_names:
            raise ValueError("Technical requirement identifiers must be unique.")
        if not isinstance(name, str) or not name:
            raise ValueError(f"Technical requirement {requirement_id} requires a name.")
        requirement_names[requirement_id] = name

    evidence_ids = {
        record.get("evidence_id")
        for record in evidence
        if isinstance(record.get("evidence_id"), str) and record.get("evidence_id")
    }

    result_map: dict[tuple[str, str], dict[str, Any]] = {}
    for index, record in enumerate(results):
        alternative_id = record.get("alternative_id")
        requirement_id = record.get("requirement_id")
        status = record.get("status")
        if alternative_id not in alternative_ids:
            raise ValueError(f"technical_qualification_results.{index}.alternative_id is invalid.")
        if requirement_id not in requirement_names:
            raise ValueError(f"technical_qualification_results.{index}.requirement_id is invalid.")
        if status not in _ALLOWED_STATUSES:
            raise ValueError(f"technical_qualification_results.{index}.status is invalid.")
        key = (alternative_id, requirement_id)
        if key in result_map:
            raise ValueError(
                f"Duplicate technical qualification result for {alternative_id}/{requirement_id}."
            )
        result_map[key] = record

    validation_map: dict[str, list[str]] = {alternative_id: [] for alternative_id in alternative_ids}
    for index, record in enumerate(validations):
        alternative_id = record.get("alternative_id")
        activity = record.get("activity")
        status = record.get("status")
        if alternative_id not in alternative_ids:
            raise ValueError(f"validation_requirements.{index}.alternative_id is invalid.")
        if not isinstance(activity, str) or not activity:
            raise ValueError(f"validation_requirements.{index}.activity is required.")
        if status not in {"passed", "waived"}:
            validation_map[alternative_id].append(activity)

    outcomes: dict[str, QualificationOutcome] = {}
    for alternative_id in sorted(alternative_ids):
        reasons: list[str] = []
        missing_requirement_ids: list[str] = []
        collected_evidence: list[str] = []
        required_validation = list(validation_map[alternative_id])
        statuses: list[str] = []

        for requirement_id, requirement_name in requirement_names.items():
            record = result_map.get((alternative_id, requirement_id))
            if record is None:
                missing_requirement_ids.append(requirement_id)
                reasons.append(f"Missing qualification result for {requirement_id}.")
                required_validation.append(f"Assess {requirement_name}")
                statuses.append("insufficient_data")
                continue

            status = record["status"]
            evidence_id = record.get("evidence_id")
            if status in _EVIDENCE_REQUIRED_STATUSES:
                if not isinstance(evidence_id, str) or evidence_id not in evidence_ids:
                    reasons.append(
                        f"Valid evidence is required for {requirement_id} status {status}."
                    )
                    required_validation.append(f"Provide evidence for {requirement_name}")
                    statuses.append("insufficient_data")
                    continue
                collected_evidence.append(evidence_id)

            statuses.append(status)
            if status == "not_qualified":
                reasons.append(f"{requirement_id} is not qualified.")
            elif status == "conditionally_qualified":
                reasons.append(f"{requirement_id} is conditionally qualified.")
                required_validation.append(f"Close conditions for {requirement_name}")
            elif status in {"not_assessed", "insufficient_data"}:
                reasons.append(f"{requirement_id} has status {status}.")
                required_validation.append(f"Assess {requirement_name}")

        if "not_qualified" in statuses:
            overall_status = "not_qualified"
        elif any(status in {"not_assessed", "insufficient_data"} for status in statuses):
            overall_status = "insufficient_data"
        elif "conditionally_qualified" in statuses:
            overall_status = "conditionally_qualified"
        elif statuses and all(status == "qualified" for status in statuses):
            overall_status = "qualified"
        else:
            overall_status = "insufficient_data"
            reasons.append("No complete technical qualification basis is available.")

        outcomes[alternative_id] = QualificationOutcome(
            alternative_id=alternative_id,
            status=overall_status,
            reasons=_deduplicate(reasons),
            missing_requirement_ids=tuple(sorted(missing_requirement_ids)),
            evidence_ids=tuple(sorted(set(collected_evidence))),
            validation_required=_deduplicate(required_validation),
        )

    return outcomes
