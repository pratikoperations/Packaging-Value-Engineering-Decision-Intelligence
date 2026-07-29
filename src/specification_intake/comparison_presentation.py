from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from src.review_comparison import ReviewState

from .models import DocumentRole


class ParameterCriticality(str, Enum):
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"


FIELD_CRITICALITY: dict[str, ParameterCriticality] = {
    "specification_number": ParameterCriticality.MAJOR,
    "specification_revision": ParameterCriticality.MAJOR,
    "item_code": ParameterCriticality.MAJOR,
    "item_description": ParameterCriticality.MAJOR,
    "supplier_name": ParameterCriticality.MINOR,
    "effective_date": ParameterCriticality.MINOR,
    "box_style": ParameterCriticality.CRITICAL,
    "internal_length": ParameterCriticality.CRITICAL,
    "internal_width": ParameterCriticality.CRITICAL,
    "internal_height": ParameterCriticality.CRITICAL,
    "external_length": ParameterCriticality.MAJOR,
    "external_width": ParameterCriticality.MAJOR,
    "external_height": ParameterCriticality.MAJOR,
    "dimension_unit": ParameterCriticality.CRITICAL,
    "joint_type": ParameterCriticality.MAJOR,
    "closure_method": ParameterCriticality.MAJOR,
    "ply_count": ParameterCriticality.CRITICAL,
    "flute_combination": ParameterCriticality.CRITICAL,
    "liner_gsm": ParameterCriticality.MAJOR,
    "medium_gsm": ParameterCriticality.MAJOR,
    "total_board_gsm": ParameterCriticality.CRITICAL,
    "paper_grade": ParameterCriticality.CRITICAL,
    "box_weight": ParameterCriticality.CRITICAL,
    "box_weight_unit": ParameterCriticality.CRITICAL,
    "compression_requirement": ParameterCriticality.CRITICAL,
}

COMPARISON_STATUSES = ("Changed", "Unchanged", "Incomplete")
CRITICALITY_LEVELS = tuple(level.value for level in ParameterCriticality)


@dataclass(frozen=True)
class MissingPrioritySummary:
    critical: tuple[str, ...]
    major: tuple[str, ...]
    minor: tuple[str, ...]

    @property
    def has_high_priority_gap(self) -> bool:
        return bool(self.critical or self.major)


def display_value(value: Any, unit: str | None = None) -> str:
    if value is None or value == "":
        return "Not provided"
    rendered = str(value)
    return f"{rendered} {unit}".strip() if unit else rendered


def effective_display(view: Any) -> str:
    review = view.review
    if review.state is ReviewState.CORRECTED_CONFIRMED:
        return display_value(review.corrected_value, review.corrected_unit)
    return display_value(view.normalized_value, view.unit)


def comparison_rows(views: Iterable[Any]) -> list[dict[str, str]]:
    by_field: dict[str, dict[str, Any]] = {}
    for view in views:
        by_field.setdefault(view.field_name, {})[view.document_role.value] = view

    rows: list[dict[str, str]] = []
    for field_name in sorted(FIELD_CRITICALITY):
        pair = by_field.get(field_name, {})
        existing = pair.get(DocumentRole.EXISTING.value)
        proposed = pair.get(DocumentRole.PROPOSED.value)
        existing_value = effective_display(existing) if existing else "Not provided"
        proposed_value = effective_display(proposed) if proposed else "Not provided"
        if existing is None or proposed is None:
            status = "Incomplete"
        elif existing_value == proposed_value:
            status = "Unchanged"
        else:
            status = "Changed"
        rows.append({
            "Parameter": field_name.replace("_", " ").title(),
            "Criticality": FIELD_CRITICALITY[field_name].value,
            "Existing": existing_value,
            "Proposed": proposed_value,
            "Comparison Status": status,
        })
    return rows


def filter_comparison_rows(
    rows: Iterable[dict[str, str]],
    *,
    statuses: Iterable[str],
    criticalities: Iterable[str],
) -> list[dict[str, str]]:
    allowed_statuses = set(statuses)
    allowed_criticalities = set(criticalities)
    return [
        row for row in rows
        if row["Comparison Status"] in allowed_statuses
        and row["Criticality"] in allowed_criticalities
    ]


def missing_priority_summary(rows: Iterable[dict[str, str]]) -> MissingPrioritySummary:
    grouped: dict[str, list[str]] = {level: [] for level in CRITICALITY_LEVELS}
    for row in rows:
        if row["Comparison Status"] == "Incomplete":
            grouped[row["Criticality"]].append(row["Parameter"])
    return MissingPrioritySummary(
        critical=tuple(grouped[ParameterCriticality.CRITICAL.value]),
        major=tuple(grouped[ParameterCriticality.MAJOR.value]),
        minor=tuple(grouped[ParameterCriticality.MINOR.value]),
    )
