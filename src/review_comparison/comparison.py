"""Deterministic existing-versus-proposed review comparison."""

from __future__ import annotations

from numbers import Number
from typing import Iterable, Mapping

from src.document_intake import DocumentRole

from .models import (
    CandidateReview,
    ChangeSummary,
    ComparisonStatus,
    FieldComparison,
    FieldReviewGroup,
)
from .review_service import unresolved_reason


def _selected_by_field(
    groups: Iterable[FieldReviewGroup], role: DocumentRole
) -> tuple[Mapping[str, CandidateReview], tuple[str, ...]]:
    selected: dict[str, CandidateReview] = {}
    unresolved: list[str] = []
    for group in groups:
        if group.document_role is not role:
            continue
        reason = unresolved_reason(group)
        if reason:
            unresolved.append(f"{role.value}:{group.field_name}:{reason}")
            continue
        review = group.selected_review
        if review is not None:
            selected[group.field_name] = review
    return selected, tuple(sorted(unresolved))


def _same_value(left: object, right: object) -> bool:
    if isinstance(left, str) and isinstance(right, str):
        return left.strip().casefold() == right.strip().casefold()
    return left == right


def compare_fields(
    field_names: Iterable[str], groups: Iterable[FieldReviewGroup]
) -> tuple[FieldComparison, ...]:
    """Compare only resolved, accepted review values without technical interpretation."""

    groups = tuple(groups)
    existing, _ = _selected_by_field(groups, DocumentRole.EXISTING)
    proposed, _ = _selected_by_field(groups, DocumentRole.PROPOSED)
    comparisons: list[FieldComparison] = []

    for field_name in tuple(dict.fromkeys(field_names)):
        left = existing.get(field_name)
        right = proposed.get(field_name)
        if left is None and right is None:
            comparisons.append(FieldComparison(field_name, None, None, ComparisonStatus.BOTH_MISSING))
            continue
        if left is None:
            comparisons.append(FieldComparison(field_name, None, right, ComparisonStatus.EXISTING_MISSING))
            continue
        if right is None:
            comparisons.append(FieldComparison(field_name, left, None, ComparisonStatus.PROPOSED_MISSING))
            continue

        left_value = left.effective_value
        right_value = right.effective_value
        left_unit = left.effective_unit
        right_unit = right.effective_unit
        if left_unit and right_unit and left_unit.casefold() != right_unit.casefold():
            comparisons.append(FieldComparison(field_name, left, right, ComparisonStatus.UNIT_CONFLICT))
            continue
        if _same_value(left_value, right_value):
            comparisons.append(FieldComparison(field_name, left, right, ComparisonStatus.UNCHANGED, change=0))
            continue
        if isinstance(left_value, Number) and isinstance(right_value, Number):
            change = right_value - left_value
            change_percent = None if left_value == 0 else (change / left_value) * 100
            comparisons.append(
                FieldComparison(
                    field_name,
                    left,
                    right,
                    ComparisonStatus.CHANGED,
                    change=change,
                    change_percent=change_percent,
                )
            )
            continue
        if isinstance(left_value, str) and isinstance(right_value, str):
            comparisons.append(FieldComparison(field_name, left, right, ComparisonStatus.CHANGED))
            continue
        comparisons.append(FieldComparison(field_name, left, right, ComparisonStatus.NOT_COMPARABLE))

    return tuple(comparisons)


def build_change_summary(
    comparisons: Iterable[FieldComparison],
    groups: Iterable[FieldReviewGroup],
) -> ChangeSummary:
    comparisons = tuple(comparisons)
    groups = tuple(groups)
    unresolved = tuple(
        sorted(
            f"{group.document_role.value}:{group.field_name}:{reason}"
            for group in groups
            if (reason := unresolved_reason(group)) is not None
        )
    )
    counts = {status: 0 for status in ComparisonStatus}
    for comparison in comparisons:
        counts[comparison.status] += 1
    return ChangeSummary(
        total_fields=len(comparisons),
        changed=counts[ComparisonStatus.CHANGED],
        unchanged=counts[ComparisonStatus.UNCHANGED],
        existing_missing=counts[ComparisonStatus.EXISTING_MISSING],
        proposed_missing=counts[ComparisonStatus.PROPOSED_MISSING],
        both_missing=counts[ComparisonStatus.BOTH_MISSING],
        unit_conflicts=counts[ComparisonStatus.UNIT_CONFLICT],
        not_comparable=counts[ComparisonStatus.NOT_COMPARABLE],
        unresolved_fields=unresolved,
    )
