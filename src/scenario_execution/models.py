from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ScenarioExecutionError(ValueError):
    """Raised when a controlled scenario cannot be evaluated safely."""


@dataclass(frozen=True)
class ControlledScenarioResult:
    project_id: str
    dataset_id: str
    threshold_profile_id: str
    scenario_name: str
    assumptions: dict[str, Any]
    results: dict[str, Any]
