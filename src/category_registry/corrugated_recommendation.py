from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

RECOMMENDATION_OUTCOMES = (
    "criteria met for engineering review",
    "criteria not met",
    "laboratory validation required",
    "packing-line trial required",
    "transport trial required",
    "evidence conflict",
    "insufficient technical data",
    "engineering review required",
)

@dataclass(frozen=True)
class EngineeringRecommendation:
    outcome: str
    evidence_confidence: str
    rationale: tuple[str, ...]
    blockers: tuple[str, ...]
    required_trials: tuple[str, ...]
    technical_outcomes: Mapping[str, Any]
    commercial_outcomes: Mapping[str, Any]
    limitations: tuple[str, ...]


def build_engineering_recommendation(
    *,
    screening_outcome: str,
    technical_blockers: Sequence[str] = (),
    required_trials: Sequence[str] = (),
    evidence_confidence: str,
    material_logistics: Mapping[str, Any] | None = None,
    economics: Mapping[str, Any] | None = None,
) -> EngineeringRecommendation:
    """Aggregate prior-build outputs without generating approval or success probability."""
    blockers = tuple(dict.fromkeys(str(v) for v in technical_blockers if str(v)))
    trials = tuple(dict.fromkeys(str(v) for v in required_trials if str(v)))
    rationale: list[str] = []

    if screening_outcome == "evidence conflict":
        outcome = "evidence conflict"
    elif blockers:
        outcome = "criteria not met"
    elif any("packing-line" in value.lower() for value in trials):
        outcome = "packing-line trial required"
    elif any("transport" in value.lower() for value in trials):
        outcome = "transport trial required"
    elif any("laboratory" in value.lower() for value in trials):
        outcome = "laboratory validation required"
    elif screening_outcome in {"validation required", "insufficient technical data"}:
        outcome = "insufficient technical data"
    elif screening_outcome == "criteria met":
        outcome = "criteria met for engineering review"
    else:
        outcome = "engineering review required"

    if blockers:
        rationale.append("Technical or evidence blockers override commercial attractiveness.")
    if evidence_confidence:
        rationale.append(f"Evidence confidence is recorded separately as: {evidence_confidence}.")
    if economics:
        rationale.append("Economic outputs are decision support only and cannot authorize the proposal.")

    return EngineeringRecommendation(
        outcome=outcome,
        evidence_confidence=evidence_confidence,
        rationale=tuple(rationale),
        blockers=blockers,
        required_trials=trials,
        technical_outcomes={"screening_outcome": screening_outcome, **dict(material_logistics or {})},
        commercial_outcomes=dict(economics or {}),
        limitations=(
            "This is an engineering recommendation for review, not an approval decision.",
            "Evidence confidence is not probability of technical success.",
            "Explicit human engineering validation remains mandatory.",
        ),
    )
