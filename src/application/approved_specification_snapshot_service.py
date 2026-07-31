from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Mapping, Sequence

from src.application.specification_review_service import ReviewableField
from src.domain.approved_specification import (
    APPROVED_SPECIFICATION_SCHEMA_VERSION,
    ApprovedSpecificationError,
    ApprovedSpecificationMaterialization,
    ApprovedSpecificationSnapshot,
    GovernedSpecificationField,
    approved_specification_content_hash,
    materialize_approved_specification,
)
from src.domain.specification_review import evaluate_snapshot_eligibility
from src.persistence._utils import new_id
from src.persistence.approved_specification_repository import (
    ApprovedSpecificationPersistenceError,
    ApprovedSpecificationSnapshotRepository,
)
from src.persistence.dataset_repository import DatasetRepository
from src.persistence.specification_review_repository import (
    SpecificationReviewPersistenceError,
    SpecificationReviewRepository,
)


class ApprovedSpecificationSnapshotError(ValueError):
    """Presentation-safe application error for governed snapshot creation."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ApprovedSpecificationSnapshotService:
    """Create one immutable approved snapshot from the latest eligible review revision."""

    def __init__(
        self,
        review_repository: SpecificationReviewRepository,
        snapshot_repository: ApprovedSpecificationSnapshotRepository,
        dataset_repository: DatasetRepository,
    ) -> None:
        self.review_repository = review_repository
        self.snapshot_repository = snapshot_repository
        self.dataset_repository = dataset_repository

    def create_snapshot(
        self,
        *,
        project_id: str,
        review_id: str,
        source_review_revision_id: str,
        actor_reference: str,
        approval_reason: str,
        fields: Sequence[ReviewableField],
        optional_exclusions: Sequence[str] = (),
    ) -> ApprovedSpecificationSnapshot:
        project_id = self._required(project_id, "project_required", "Select a project before creating a snapshot.")
        review_id = self._required(review_id, "review_required", "Select a review before creating a snapshot.")
        source_review_revision_id = self._required(
            source_review_revision_id,
            "source_revision_required",
            "The current review revision is required.",
        )
        actor_reference = self._required(
            actor_reference,
            "actor_required",
            "A non-empty actor reference is required.",
        )
        approval_reason = self._required(
            approval_reason,
            "approval_reason_required",
            "A non-empty approval reason is required.",
        )

        try:
            latest = self.review_repository.get_latest(review_id, project_id=project_id)
        except KeyError as error:
            raise ApprovedSpecificationSnapshotError(
                "unknown_review", "The selected review does not exist."
            ) from error
        except SpecificationReviewPersistenceError as error:
            raise ApprovedSpecificationSnapshotError(error.code, error.message) from error

        if latest.review_revision_id != source_review_revision_id:
            raise ApprovedSpecificationSnapshotError(
                "historical_revision",
                "Only the latest persisted review revision can create an approved specification snapshot.",
            )

        eligibility = evaluate_snapshot_eligibility(
            existing_baseline=latest.state.existing_baseline,
            proposed_dataset_id=latest.state.proposed_dataset_id,
            candidates=(item.candidate for item in latest.state.comparisons),
            has_unresolved_validation_issue=latest.state.has_unresolved_validation_issue,
        )
        if latest.state.eligibility is not None and latest.state.eligibility != eligibility:
            raise ApprovedSpecificationSnapshotError(
                "review_integrity_error",
                "The persisted review eligibility is inconsistent with governed domain rules.",
            )
        if not eligibility.eligible:
            raise ApprovedSpecificationSnapshotError(
                "review_not_eligible",
                "The review is not eligible for an approved specification snapshot.",
            )

        existing = self._dataset(latest.state.existing_dataset_id, project_id)
        proposed = self._dataset(latest.state.proposed_dataset_id, project_id)
        governed_fields = self._governed_fields(
            fields,
            existing=self._canonical(existing),
            proposed=self._canonical(proposed),
            comparisons=latest.state.comparisons,
            optional_exclusions=optional_exclusions,
        )
        try:
            materialization = materialize_approved_specification(governed_fields, eligible=True)
        except (ApprovedSpecificationError, ValueError) as error:
            raise ApprovedSpecificationSnapshotError(
                "materialization_failed",
                "The approved specification could not be materialized from governed review data.",
            ) from error

        digest = approved_specification_content_hash(
            project_id=project_id,
            review_id=review_id,
            source_review_revision_id=latest.review_revision_id,
            source_review_revision_number=latest.revision_number,
            existing_dataset_id=latest.state.existing_dataset_id,
            proposed_dataset_id=latest.state.proposed_dataset_id,
            materialization=materialization,
        )
        candidate = ApprovedSpecificationSnapshot(
            snapshot_id=new_id("approved-specification"),
            project_id=project_id,
            review_id=review_id,
            source_review_revision_id=latest.review_revision_id,
            source_review_revision_number=latest.revision_number,
            existing_dataset_id=latest.state.existing_dataset_id,
            proposed_dataset_id=latest.state.proposed_dataset_id,
            approved_values=materialization.approved_values,
            excluded_fields=materialization.excluded_fields,
            snapshot_schema_version=APPROVED_SPECIFICATION_SCHEMA_VERSION,
            actor_reference=actor_reference,
            approval_reason=approval_reason,
            content_hash=digest,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        existing_snapshot = self._existing_snapshot(review_id, project_id)
        if existing_snapshot is not None:
            return self._resolve_retry(existing_snapshot, candidate)
        try:
            return self.snapshot_repository.create(candidate)
        except ApprovedSpecificationPersistenceError as error:
            if error.code == "duplicate_source_revision":
                existing_snapshot = self._existing_snapshot(review_id, project_id)
                if existing_snapshot is not None:
                    return self._resolve_retry(existing_snapshot, candidate)
            raise ApprovedSpecificationSnapshotError(error.code, error.message) from error

    def _existing_snapshot(
        self, review_id: str, project_id: str
    ) -> ApprovedSpecificationSnapshot | None:
        try:
            return self.snapshot_repository.get_for_review(review_id, project_id=project_id)
        except ApprovedSpecificationPersistenceError as error:
            raise ApprovedSpecificationSnapshotError(error.code, error.message) from error

    @staticmethod
    def _resolve_retry(
        existing: ApprovedSpecificationSnapshot,
        candidate: ApprovedSpecificationSnapshot,
    ) -> ApprovedSpecificationSnapshot:
        identical = (
            existing.project_id == candidate.project_id
            and existing.review_id == candidate.review_id
            and existing.source_review_revision_id == candidate.source_review_revision_id
            and existing.source_review_revision_number == candidate.source_review_revision_number
            and existing.existing_dataset_id == candidate.existing_dataset_id
            and existing.proposed_dataset_id == candidate.proposed_dataset_id
            and existing.approved_values == candidate.approved_values
            and existing.excluded_fields == candidate.excluded_fields
            and existing.snapshot_schema_version == candidate.snapshot_schema_version
            and existing.actor_reference == candidate.actor_reference
            and existing.approval_reason == candidate.approval_reason
            and existing.content_hash == candidate.content_hash
        )
        if identical:
            return existing
        raise ApprovedSpecificationSnapshotError(
            "conflicting_snapshot",
            "An approved specification snapshot already exists with conflicting authorization or content.",
        )

    def _dataset(self, dataset_id: str, project_id: str) -> Mapping[str, object]:
        try:
            record = self.dataset_repository.get(dataset_id)
        except KeyError as error:
            raise ApprovedSpecificationSnapshotError(
                "unknown_dataset", "A source dataset no longer exists."
            ) from error
        if str(record.get("project_id", "")) != project_id:
            raise ApprovedSpecificationSnapshotError(
                "invalid_dataset_lineage",
                "Source datasets must belong to the selected project.",
            )
        if str(record.get("validation_status", "")) != "valid":
            raise ApprovedSpecificationSnapshotError(
                "invalid_dataset", "Only valid source datasets can form an approved snapshot."
            )
        return record

    @staticmethod
    def _canonical(record: Mapping[str, object]) -> Mapping[str, object]:
        value = record.get("canonical_json")
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as error:
                raise ApprovedSpecificationSnapshotError(
                    "invalid_dataset_content", "Source dataset content is invalid."
                ) from error
        if not isinstance(value, Mapping):
            raise ApprovedSpecificationSnapshotError(
                "invalid_dataset_content", "Source dataset content is invalid."
            )
        return value

    @classmethod
    def _governed_fields(
        cls,
        fields: Sequence[ReviewableField],
        *,
        existing: Mapping[str, object],
        proposed: Mapping[str, object],
        comparisons,
        optional_exclusions: Sequence[str],
    ) -> tuple[GovernedSpecificationField, ...]:
        keys = [field.field_key for field in fields]
        if not keys or len(keys) != len(set(keys)):
            raise ApprovedSpecificationSnapshotError(
                "invalid_field_registry",
                "The governed field registry must be non-empty and contain unique field keys.",
            )
        registry = {field.field_key: field for field in fields}
        exclusions = {str(item).strip() for item in optional_exclusions if str(item).strip()}
        unknown_exclusions = exclusions.difference(registry)
        if unknown_exclusions or any(registry[key].mandatory for key in exclusions):
            raise ApprovedSpecificationSnapshotError(
                "invalid_optional_exclusion",
                "Only optional governed fields can be explicitly excluded.",
            )
        comparison_by_key = {item.field_key: item for item in comparisons}
        if len(comparison_by_key) != len(tuple(comparisons)):
            raise ApprovedSpecificationSnapshotError(
                "review_integrity_error", "Review comparisons contain duplicate field keys."
            )

        governed: list[GovernedSpecificationField] = []
        changed_keys: set[str] = set()
        for field in sorted(fields, key=lambda item: item.field_key):
            existing_value = cls._read_path(existing, field.path)
            proposed_value = cls._read_path(proposed, field.path)
            comparison = comparison_by_key.get(field.field_key)
            if existing_value != proposed_value:
                changed_keys.add(field.field_key)
                if comparison is None:
                    raise ApprovedSpecificationSnapshotError(
                        "review_registry_mismatch",
                        "A changed governed field is missing from the persisted review.",
                    )
                if (
                    comparison.existing_value != existing_value
                    or comparison.candidate.original_value != proposed_value
                ):
                    raise ApprovedSpecificationSnapshotError(
                        "review_source_mismatch",
                        "Persisted review values do not match the source datasets.",
                    )
                status = comparison.candidate.status
                corrected = comparison.candidate.corrected_value
            else:
                if comparison is not None:
                    raise ApprovedSpecificationSnapshotError(
                        "review_source_mismatch",
                        "An unchanged governed field is unexpectedly present in the review.",
                    )
                status = None
                corrected = None
            governed.append(
                GovernedSpecificationField(
                    field_key=field.field_key,
                    existing_value=existing_value,
                    proposed_value=proposed_value,
                    mandatory=field.mandatory,
                    status=status,
                    corrected_value=corrected,
                    intentionally_excluded=field.field_key in exclusions,
                )
            )
        if set(comparison_by_key) != changed_keys:
            raise ApprovedSpecificationSnapshotError(
                "review_registry_mismatch",
                "Persisted review fields do not match the governed field registry.",
            )
        return tuple(governed)

    @staticmethod
    def _read_path(data: Mapping[str, object], path: tuple[str, ...]) -> object:
        current: object = data
        for part in path:
            if not isinstance(current, Mapping) or part not in current:
                return None
            current = current[part]
        return current

    @staticmethod
    def _required(value: str, code: str, message: str) -> str:
        normalized = str(value).strip()
        if not normalized:
            raise ApprovedSpecificationSnapshotError(code, message)
        return normalized
