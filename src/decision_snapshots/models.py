from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class DecisionSnapshotError(ValueError):
    """Raised when a decision snapshot cannot be created safely."""


@dataclass(frozen=True)
class PreparedDecisionSnapshot:
    project_id: str
    scenario_id: str
    dataset_id: str
    threshold_profile_id: str | None
    status: str
    preferred_alternative_id: str | None
    recommendation: dict[str, Any]
    gate_results: dict[str, Any]
