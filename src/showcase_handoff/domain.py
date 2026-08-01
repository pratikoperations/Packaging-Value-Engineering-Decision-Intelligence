from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class AudienceRole(str, Enum):
    EXECUTIVE = "Executive interviewer"
    PROCUREMENT = "Procurement leader"
    PACKAGING = "Packaging specialist"
    GOVERNANCE = "Technical and governance reviewer"
    HANDOFF = "New user or collaborator"


@dataclass(frozen=True)
class ShowcaseStep:
    step_number: int
    page_reference: str
    title: str
    purpose: str
    speaker_message: str
    evidence_to_show: tuple[str, ...]
    avoid_claiming: tuple[str, ...]
    expected_duration_seconds: int
    fallback_step: str = ""
    dependency: str = ""

    def __post_init__(self) -> None:
        if self.step_number < 1 or self.expected_duration_seconds < 1:
            raise ValueError("Showcase steps require positive sequence and duration.")
        required = (self.page_reference, self.title, self.purpose, self.speaker_message)
        if any(not value.strip() for value in required):
            raise ValueError("Showcase steps require page, title, purpose and speaker guidance.")
        if not self.evidence_to_show or not self.avoid_claiming:
            raise ValueError("Every showcase step requires evidence and claim limitations.")


@dataclass(frozen=True)
class ShowcaseJourney:
    journey_id: str
    title: str
    audience: AudienceRole
    target_duration_minutes: int
    business_objective: str
    opening_statement: str
    closing_statement: str
    steps: tuple[ShowcaseStep, ...]
    proof_statements: tuple[str, ...]
    limitation_statements: tuple[str, ...]
    recovery_steps: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.journey_id.strip() or not self.steps:
            raise ValueError("Journey identity and steps are required.")
        numbers = tuple(step.step_number for step in self.steps)
        if numbers != tuple(range(1, len(self.steps) + 1)):
            raise ValueError("Journey steps must be unique and contiguous.")
        if self.total_duration_seconds > self.target_duration_minutes * 60 + 30:
            raise ValueError("Journey exceeds its governed duration tolerance.")
        if not self.proof_statements or not self.limitation_statements:
            raise ValueError("Journey must separate proof from limitations.")

    @property
    def total_duration_seconds(self) -> int:
        return sum(step.expected_duration_seconds for step in self.steps)

    @property
    def page_transitions(self) -> int:
        return max(0, len(self.steps) - 1)

    def canonical_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["audience"] = self.audience.value
        return payload

    def canonical_json(self) -> str:
        return json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class HandoffChecklist:
    environment_checks: tuple[str, ...]
    repository_checks: tuple[str, ...]
    data_boundary_checks: tuple[str, ...]
    workflow_checks: tuple[str, ...]
    test_commands: tuple[str, ...]
    known_limitations: tuple[str, ...]
    recovery_guidance: tuple[str, ...]

    def canonical_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
