from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable, Mapping

from src.domain.specification_review import ReviewStatus


APPROVED_SPECIFICATION_SCHEMA_VERSION = "1.0"


class ApprovedSpecificationError(ValueError):
    """Fail-closed domain error for approved-specification materialization."""


@dataclass(frozen=True)
class GovernedSpecificationField:
    field_key: str
    existing_value: object
    proposed_value: object
    mandatory: bool = True
    status: ReviewStatus | None = None
    corrected_value: object | None = None
    intentionally_excluded: bool = False

    def __post_init__(self) -> None:
        if not self.field_key.strip():
            raise ValueError("field_key must not be empty")
        if self.status is ReviewStatus.CORRECTED and self.corrected_value is None:
            raise ValueError("corrected fields require corrected_value")
        if self.status is not ReviewStatus.CORRECTED and self.corrected_value is not None:
            raise ValueError("corrected_value is only valid for corrected fields")
        if self.intentionally_excluded and self.mandatory:
            raise ValueError("mandatory fields cannot be intentionally excluded")
        if self.intentionally_excluded and (
            self.existing_value is not None or self.proposed_value is not None
        ):
            raise ValueError("only absent optional fields can be intentionally excluded")

    @property
    def changed(self) -> bool:
        return self.existing_value != self.proposed_value


@dataclass(frozen=True)
class ApprovedSpecificationValue:
    field_key: str
    value: object
    source: str

    def __post_init__(self) -> None:
        if not self.field_key.strip():
            raise ValueError("field_key must not be empty")
        if self.source not in {"accepted_proposed", "corrected", "retained_existing", "unchanged"}:
            raise ValueError("invalid approved-value source")


@dataclass(frozen=True)
class ApprovedSpecificationMaterialization:
    approved_values: tuple[ApprovedSpecificationValue, ...]
    excluded_fields: tuple[str, ...]

    def __post_init__(self) -> None:
        value_keys = tuple(item.field_key for item in self.approved_values)
        if value_keys != tuple(sorted(value_keys)):
            raise ValueError("approved values must use deterministic field ordering")
        if len(value_keys) != len(set(value_keys)):
            raise ValueError("approved values must not contain duplicate fields")
        if self.excluded_fields != tuple(sorted(self.excluded_fields)):
            raise ValueError("excluded fields must use deterministic ordering")
        if len(self.excluded_fields) != len(set(self.excluded_fields)):
            raise ValueError("excluded fields must not contain duplicates")
        if set(value_keys).intersection(self.excluded_fields):
            raise ValueError("a field cannot be both approved and excluded")

    @property
    def approved_field_count(self) -> int:
        return len(self.approved_values)

    def count_by_source(self, source: str) -> int:
        return sum(item.source == source for item in self.approved_values)

    def as_mapping(self) -> dict[str, object]:
        return {item.field_key: item.value for item in self.approved_values}


@dataclass(frozen=True)
class ApprovedSpecificationSnapshot:
    snapshot_id: str
    project_id: str
    review_id: str
    source_review_revision_id: str
    source_review_revision_number: int
    existing_dataset_id: str
    proposed_dataset_id: str
    approved_values: tuple[ApprovedSpecificationValue, ...]
    excluded_fields: tuple[str, ...]
    snapshot_schema_version: str
    actor_reference: str
    approval_reason: str
    content_hash: str
    created_at: str

    def __post_init__(self) -> None:
        required = {
            "snapshot_id": self.snapshot_id,
            "project_id": self.project_id,
            "review_id": self.review_id,
            "source_review_revision_id": self.source_review_revision_id,
            "existing_dataset_id": self.existing_dataset_id,
            "proposed_dataset_id": self.proposed_dataset_id,
            "snapshot_schema_version": self.snapshot_schema_version,
            "actor_reference": self.actor_reference,
            "approval_reason": self.approval_reason,
            "content_hash": self.content_hash,
            "created_at": self.created_at,
        }
        for name, value in required.items():
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if self.source_review_revision_number < 1:
            raise ValueError("source_review_revision_number must be positive")
        if self.existing_dataset_id == self.proposed_dataset_id:
            raise ValueError("Existing and Proposed datasets must be distinct")
        ApprovedSpecificationMaterialization(self.approved_values, self.excluded_fields)


def materialize_approved_specification(
    fields: Iterable[GovernedSpecificationField],
    *,
    eligible: bool,
) -> ApprovedSpecificationMaterialization:
    if not eligible:
        raise ApprovedSpecificationError(
            "An approved specification cannot be materialized from an ineligible review."
        )

    ordered = sorted(tuple(fields), key=lambda item: item.field_key)
    keys = [item.field_key for item in ordered]
    if len(keys) != len(set(keys)):
        raise ApprovedSpecificationError("Governed specification field keys must be unique.")

    approved: list[ApprovedSpecificationValue] = []
    excluded: list[str] = []

    for field in ordered:
        if field.intentionally_excluded:
            excluded.append(field.field_key)
            continue

        if not field.changed:
            if field.status is not None:
                raise ApprovedSpecificationError(
                    f"Unchanged field {field.field_key} must not carry a review status."
                )
            approved.append(
                ApprovedSpecificationValue(field.field_key, field.existing_value, "unchanged")
            )
            continue

        if field.status is ReviewStatus.ACCEPTED:
            approved.append(
                ApprovedSpecificationValue(
                    field.field_key, field.proposed_value, "accepted_proposed"
                )
            )
        elif field.status is ReviewStatus.CORRECTED:
            approved.append(
                ApprovedSpecificationValue(
                    field.field_key, field.corrected_value, "corrected"
                )
            )
        elif field.status is ReviewStatus.REJECTED:
            approved.append(
                ApprovedSpecificationValue(
                    field.field_key, field.existing_value, "retained_existing"
                )
            )
        elif field.status is ReviewStatus.PENDING or field.status is None:
            raise ApprovedSpecificationError(
                f"Governed field {field.field_key} has no terminal review decision."
            )
        else:
            raise ApprovedSpecificationError(
                f"Governed field {field.field_key} has an unsupported review status."
            )

    return ApprovedSpecificationMaterialization(tuple(approved), tuple(excluded))


def approved_specification_content_hash(
    *,
    project_id: str,
    review_id: str,
    source_review_revision_id: str,
    source_review_revision_number: int,
    existing_dataset_id: str,
    proposed_dataset_id: str,
    materialization: ApprovedSpecificationMaterialization,
    snapshot_schema_version: str = APPROVED_SPECIFICATION_SCHEMA_VERSION,
) -> str:
    lineage = {
        "project_id": project_id,
        "review_id": review_id,
        "source_review_revision_id": source_review_revision_id,
        "source_review_revision_number": source_review_revision_number,
        "existing_dataset_id": existing_dataset_id,
        "proposed_dataset_id": proposed_dataset_id,
        "snapshot_schema_version": snapshot_schema_version,
    }
    for name, value in lineage.items():
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"{name} must not be empty")
    if source_review_revision_number < 1:
        raise ValueError("source_review_revision_number must be positive")
    if existing_dataset_id == proposed_dataset_id:
        raise ValueError("Existing and Proposed datasets must be distinct")

    payload: Mapping[str, object] = {
        **lineage,
        "approved_values": [
            {"field_key": item.field_key, "value": item.value, "source": item.source}
            for item in materialization.approved_values
        ],
        "excluded_fields": list(materialization.excluded_fields),
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
