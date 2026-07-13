from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ComponentScore:
    key: str
    label: str
    weight: float
    completed: int
    total: int

    @property
    def ratio(self) -> float:
        return 1.0 if self.total == 0 else self.completed / self.total

    @property
    def weighted_score(self) -> float:
        return self.ratio * self.weight


@dataclass(frozen=True)
class OutputStatus:
    name: str
    available: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReadinessAssessment:
    project_id: str
    dataset_id: str | None
    category: str
    score_percent: float
    stage: str
    component_scores: tuple[ComponentScore, ...]
    blockers: tuple[str, ...]
    outputs: tuple[OutputStatus, ...]
    source_traceability: dict[str, int]
    approval_limitation: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "dataset_id": self.dataset_id,
            "category": self.category,
            "score_percent": self.score_percent,
            "stage": self.stage,
            "component_scores": [
                {
                    "key": item.key,
                    "label": item.label,
                    "weight": item.weight,
                    "completed": item.completed,
                    "total": item.total,
                    "ratio": item.ratio,
                    "weighted_score": item.weighted_score,
                }
                for item in self.component_scores
            ],
            "blockers": list(self.blockers),
            "outputs": [
                {"name": item.name, "available": item.available, "reasons": list(item.reasons)}
                for item in self.outputs
            ],
            "source_traceability": dict(self.source_traceability),
            "approval_limitation": self.approval_limitation,
        }
