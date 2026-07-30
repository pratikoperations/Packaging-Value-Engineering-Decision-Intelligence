from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping, MutableMapping
from dataclasses import dataclass
from typing import Any, TypeVar

from src.application.specification_review_service import AssignedDataset, ReviewableField
from src.domain.specification_review import DatasetRole
from src.persistence.specification_review_repository import PersistedSpecificationReview

T = TypeVar("T")


@dataclass(frozen=True)
class ReviewActionRequest:
    action: str
    review_id: str
    revision_number: int
    field_key: str | None = None
    corrected_value: object | None = None
    reason: str | None = None


def assigned_dataset_from_record(record: Mapping[str, Any], role: DatasetRole) -> AssignedDataset:
    canonical = record["canonical_json"]
    if isinstance(canonical, str):
        canonical = json.loads(canonical)
    return AssignedDataset(
        dataset_id=str(record["dataset_id"]),
        project_id=str(record["project_id"]),
        role=role,
        canonical_data=canonical,
        validation_status=str(record["validation_status"]),
    )


def discover_reviewable_fields(*datasets: AssignedDataset) -> tuple[ReviewableField, ...]:
    paths: set[tuple[str, ...]] = set()
    for dataset in datasets:
        paths.update(_scalar_paths(dataset.canonical_data))
    return tuple(
        ReviewableField(field_key=".".join(path), path=path, mandatory=True)
        for path in sorted(paths)
    )


def _scalar_paths(value: object, prefix: tuple[str, ...] = ()) -> set[tuple[str, ...]]:
    if isinstance(value, Mapping):
        paths: set[tuple[str, ...]] = set()
        for key, child in value.items():
            paths.update(_scalar_paths(child, (*prefix, str(key))))
        return paths
    if isinstance(value, (list, tuple, set)) or not prefix:
        return set()
    return {prefix}


def action_token(request: ReviewActionRequest) -> str:
    payload = {
        "action": request.action,
        "review_id": request.review_id,
        "revision_number": request.revision_number,
        "field_key": request.field_key,
        "corrected_value": request.corrected_value,
        "reason": request.reason,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def execute_once(
    session: MutableMapping[str, Any],
    request: ReviewActionRequest,
    operation: Callable[[], T],
) -> tuple[bool, T | None]:
    token = action_token(request)
    committed_key = "specification_review_committed_action_token"
    pending_key = "specification_review_pending_action_token"
    if session.get(committed_key) == token or session.get(pending_key) == token:
        return False, None
    session[pending_key] = token
    try:
        result = operation()
    except Exception:
        session.pop(pending_key, None)
        raise
    session[committed_key] = token
    session.pop(pending_key, None)
    return True, result


def comparison_rows(review: PersistedSpecificationReview) -> list[dict[str, object]]:
    return [
        {
            "Field": item.field_key,
            "Existing": item.existing_value,
            "Proposed": item.candidate.original_value,
            "Status": item.candidate.status.value,
            "Corrected": item.candidate.corrected_value,
        }
        for item in review.state.comparisons
    ]
