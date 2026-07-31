from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping, MutableMapping
from dataclasses import dataclass
from typing import Any, TypeVar

from src.application.specification_review_read_model import SpecificationReviewSummary
from src.application.specification_review_service import AssignedDataset, ReviewableField
from src.domain.approved_specification import ApprovedSpecificationSnapshot
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


@dataclass(frozen=True)
class SnapshotActionRequest:
    project_id: str
    review_id: str
    source_review_revision_id: str
    actor_reference: str
    approval_reason: str

    def __post_init__(self) -> None:
        for name, value in (
            ("project_id", self.project_id),
            ("review_id", self.review_id),
            ("source_review_revision_id", self.source_review_revision_id),
            ("actor_reference", self.actor_reference),
            ("approval_reason", self.approval_reason),
        ):
            if not str(value).strip():
                raise ValueError(f"{name} must not be empty")


BLOCKER_LABELS: dict[str, str] = {
    "existing_baseline_not_confirmed": "Confirm the Existing dataset as the governed baseline.",
    "proposed_dataset_missing": "Assign a valid Proposed dataset to this review.",
    "unresolved_validation_issue": "Resolve all dataset validation issues before approval.",
    "mandatory_candidate_pending": "Complete every mandatory field review decision.",
}


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


def review_summary_label(summary: SpecificationReviewSummary) -> str:
    eligibility = "eligible" if summary.eligible else "blocked"
    return (
        f"{summary.review_id} — revision {summary.latest_revision_number} — "
        f"{eligibility} — {summary.pending_candidate_count} pending"
    )


def history_rows(history: list[PersistedSpecificationReview]) -> list[dict[str, object]]:
    return [
        {
            "Revision": item.revision_number,
            "Action": item.action_type,
            "Field": item.action_field_key,
            "Actor": item.actor_reference,
            "Rationale": item.action_reason,
            "Eligibility": (
                "eligible"
                if item.state.eligibility and item.state.eligibility.eligible
                else "blocked"
            ),
            "Created": item.created_at,
            "Parent revision": item.parent_revision_id,
            "Content hash": item.content_hash,
        }
        for item in history
    ]


def action_token(request: ReviewActionRequest) -> str:
    payload = {
        "action": request.action,
        "review_id": request.review_id,
        "revision_number": request.revision_number,
        "field_key": request.field_key,
        "corrected_value": request.corrected_value,
        "reason": request.reason,
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def snapshot_action_token(request: SnapshotActionRequest) -> str:
    payload = {
        "project_id": request.project_id,
        "review_id": request.review_id,
        "source_review_revision_id": request.source_review_revision_id,
        "actor_reference": request.actor_reference,
        "approval_reason": request.approval_reason,
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
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


def execute_snapshot_once(
    session: MutableMapping[str, Any],
    request: SnapshotActionRequest,
    operation: Callable[[], T],
) -> tuple[bool, T | None]:
    token = snapshot_action_token(request)
    committed_key = "approved_snapshot_committed_action_token"
    pending_key = "approved_snapshot_pending_action_token"
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


def business_blocker_message(blocker: str) -> str:
    return BLOCKER_LABELS.get(
        blocker,
        "A governed review condition is still unresolved. Complete the review before approval.",
    )


def snapshot_metrics(snapshot: ApprovedSpecificationSnapshot) -> dict[str, int]:
    sources = [item.source for item in snapshot.approved_values]
    return {
        "approved_field_count": len(snapshot.approved_values),
        "accepted_field_count": sources.count("accepted_proposed"),
        "corrected_field_count": sources.count("corrected"),
        "retained_baseline_count": sources.count("retained_existing"),
        "unchanged_field_count": sources.count("unchanged"),
        "optional_exclusion_count": len(snapshot.excluded_fields),
    }


def snapshot_identity_rows(
    snapshot: ApprovedSpecificationSnapshot,
) -> list[dict[str, str]]:
    return [
        {"Label": "Snapshot ID", "Value": snapshot.snapshot_id},
        {"Label": "Review ID", "Value": snapshot.review_id},
        {
            "Label": "Source revision",
            "Value": (
                f"{snapshot.source_review_revision_number} — "
                f"{snapshot.source_review_revision_id}"
            ),
        },
        {"Label": "Existing dataset", "Value": snapshot.existing_dataset_id},
        {"Label": "Proposed dataset", "Value": snapshot.proposed_dataset_id},
        {"Label": "Approval actor", "Value": snapshot.actor_reference},
        {"Label": "Created", "Value": snapshot.created_at},
    ]


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
