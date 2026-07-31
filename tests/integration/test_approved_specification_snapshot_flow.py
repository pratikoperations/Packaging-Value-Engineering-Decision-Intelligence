from __future__ import annotations

import pytest

from src.application.approved_specification_snapshot_service import (
    ApprovedSpecificationSnapshotError,
)
from src.application.runtime import (
    build_approved_specification_read_model,
    build_approved_specification_snapshot_repository,
    build_approved_specification_snapshot_service,
    build_dataset_repository,
    build_persistent_specification_review_service,
    build_project_repository,
)
from src.application.specification_review_service import AssignedDataset, ReviewableField
from src.domain.approved_specification import (
    ApprovedSpecificationMaterialization,
    approved_specification_content_hash,
)
from src.domain.specification_review import DatasetRole


def test_full_approved_specification_snapshot_flow(tmp_path) -> None:
    database_path = tmp_path / "approved-specification-flow.sqlite3"

    projects = build_project_repository(database_path)
    project = projects.create(
        project_id="project-e1-6",
        project_code="E1-6-INTEGRATION",
        project_name="Approved specification integration",
        category="corrugated",
        currency="INR",
        annual_volume=100000,
        status="active",
    )
    project_id = str(project["project_id"])

    datasets = build_dataset_repository(database_path)
    existing_record = datasets.create_version(
        project_id=project_id,
        source_type="integration-existing",
        canonical_data={
            "gsm": 120,
            "caliper": 1.0,
            "burst_strength": 8.0,
            "flute": "B",
            "coating": None,
        },
        validation_status="valid",
    )
    proposed_record = datasets.create_version(
        project_id=project_id,
        source_type="integration-proposed",
        canonical_data={
            "gsm": 140,
            "caliper": 0.8,
            "burst_strength": 7.0,
            "flute": "B",
            "coating": None,
        },
        validation_status="valid",
    )

    existing = AssignedDataset(
        dataset_id=str(existing_record["dataset_id"]),
        project_id=project_id,
        role=DatasetRole.EXISTING,
        canonical_data={
            "gsm": 120,
            "caliper": 1.0,
            "burst_strength": 8.0,
            "flute": "B",
            "coating": None,
        },
    )
    proposed = AssignedDataset(
        dataset_id=str(proposed_record["dataset_id"]),
        project_id=project_id,
        role=DatasetRole.PROPOSED,
        canonical_data={
            "gsm": 140,
            "caliper": 0.8,
            "burst_strength": 7.0,
            "flute": "B",
            "coating": None,
        },
    )
    fields = (
        ReviewableField("burst_strength", ("burst_strength",)),
        ReviewableField("caliper", ("caliper",)),
        ReviewableField("coating", ("coating",), mandatory=False),
        ReviewableField("flute", ("flute",)),
        ReviewableField("gsm", ("gsm",)),
    )

    review_service = build_persistent_specification_review_service(database_path)
    review = review_service.initialize_and_save(
        existing=existing,
        proposed=proposed,
        fields=fields,
        actor_reference="integration-reviewer",
    )
    review = review_service.confirm_and_save(
        review.review_id,
        dataset_id=existing.dataset_id,
        actor_reference="integration-reviewer",
    )
    review = review_service.accept_and_save(
        review.review_id,
        field_key="gsm",
        actor_reference="integration-reviewer",
    )
    review = review_service.correct_and_save(
        review.review_id,
        field_key="caliper",
        corrected_value=0.9,
        actor_reference="integration-reviewer",
        action_reason="Use the validated intermediate caliper.",
    )
    review = review_service.reject_and_save(
        review.review_id,
        field_key="burst_strength",
        actor_reference="integration-reviewer",
        action_reason="Retain the governed Existing baseline strength.",
    )

    assert review.revision_number == 5
    assert review.state.eligibility is not None
    assert review.state.eligibility.eligible is True

    snapshot_service = build_approved_specification_snapshot_service(database_path)
    snapshot = snapshot_service.create_snapshot(
        project_id=project_id,
        review_id=review.review_id,
        source_review_revision_id=review.review_revision_id,
        actor_reference="integration-approver",
        approval_reason="Freeze the fully reviewed specification for controlled handoff.",
        fields=fields,
        optional_exclusions=("coating",),
    )

    recreated_service = build_approved_specification_snapshot_service(database_path)
    recreated_read_model = build_approved_specification_read_model(database_path)
    reloaded = recreated_read_model.get_snapshot(
        snapshot.snapshot_id,
        project_id=project_id,
    )

    assert reloaded.snapshot_id == snapshot.snapshot_id
    assert reloaded.review_id == review.review_id
    assert reloaded.source_review_revision_id == review.review_revision_id
    assert reloaded.source_review_revision_number == review.revision_number
    assert reloaded.project_id == project_id
    assert reloaded.existing_dataset_id == existing.dataset_id
    assert reloaded.proposed_dataset_id == proposed.dataset_id
    assert reloaded.excluded_fields == ("coating",)
    assert {item.field_key: item.value for item in reloaded.approved_values} == {
        "burst_strength": 8.0,
        "caliper": 0.9,
        "flute": "B",
        "gsm": 140,
    }
    assert {item.field_key: item.source for item in reloaded.approved_values} == {
        "burst_strength": "retained_existing",
        "caliper": "corrected",
        "flute": "unchanged",
        "gsm": "accepted_proposed",
    }

    expected_hash = approved_specification_content_hash(
        project_id=project_id,
        review_id=review.review_id,
        source_review_revision_id=review.review_revision_id,
        source_review_revision_number=review.revision_number,
        existing_dataset_id=existing.dataset_id,
        proposed_dataset_id=proposed.dataset_id,
        materialization=ApprovedSpecificationMaterialization(
            reloaded.approved_values,
            reloaded.excluded_fields,
        ),
        snapshot_schema_version=reloaded.snapshot_schema_version,
    )
    assert reloaded.content_hash == expected_hash

    identical_retry = recreated_service.create_snapshot(
        project_id=project_id,
        review_id=review.review_id,
        source_review_revision_id=review.review_revision_id,
        actor_reference="integration-approver",
        approval_reason="Freeze the fully reviewed specification for controlled handoff.",
        fields=fields,
        optional_exclusions=("coating",),
    )
    assert identical_retry.snapshot_id == snapshot.snapshot_id

    snapshot_repository = build_approved_specification_snapshot_repository(database_path)
    persisted = snapshot_repository.list_for_project(project_id)
    assert [item.snapshot_id for item in persisted] == [snapshot.snapshot_id]

    with pytest.raises(ApprovedSpecificationSnapshotError) as conflict:
        recreated_service.create_snapshot(
            project_id=project_id,
            review_id=review.review_id,
            source_review_revision_id=review.review_revision_id,
            actor_reference="integration-approver",
            approval_reason="A conflicting authorization rationale.",
            fields=fields,
            optional_exclusions=("coating",),
        )
    assert conflict.value.code == "conflicting_snapshot"
    assert len(snapshot_repository.list_for_project(project_id)) == 1
