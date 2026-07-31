from __future__ import annotations

import sqlite3

import pytest

from src.domain.approved_specification import (
    ApprovedSpecificationMaterialization,
    ApprovedSpecificationSnapshot,
    ApprovedSpecificationValue,
    approved_specification_content_hash,
)
from src.persistence.approved_specification_migration import (
    APPROVED_SPECIFICATION_SCHEMA_VERSION,
)
from src.persistence.approved_specification_repository import (
    ApprovedSpecificationPersistenceError,
    ApprovedSpecificationSnapshotRepository,
)
from src.persistence.database import Database


def initialize_prerequisites(database: Database) -> None:
    with database.transaction() as connection:
        connection.executescript(
            """
            CREATE TABLE schema_migrations(
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE projects(
                project_id TEXT PRIMARY KEY,
                archived_at TEXT
            );
            CREATE TABLE project_datasets(
                dataset_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(project_id)
            );
            CREATE TABLE specification_review_revisions(
                review_revision_id TEXT PRIMARY KEY,
                review_id TEXT NOT NULL,
                revision_number INTEGER NOT NULL,
                project_id TEXT NOT NULL,
                existing_dataset_id TEXT NOT NULL,
                proposed_dataset_id TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(project_id),
                FOREIGN KEY(existing_dataset_id) REFERENCES project_datasets(dataset_id),
                FOREIGN KEY(proposed_dataset_id) REFERENCES project_datasets(dataset_id)
            );
            """
        )
        for project_id in ("project-a", "project-b"):
            connection.execute(
                "INSERT INTO projects(project_id, archived_at) VALUES (?, NULL)",
                (project_id,),
            )
        for dataset_id, project_id in (
            ("existing-a", "project-a"),
            ("proposed-a", "project-a"),
            ("existing-b", "project-b"),
            ("proposed-b", "project-b"),
        ):
            connection.execute(
                "INSERT INTO project_datasets(dataset_id, project_id) VALUES (?, ?)",
                (dataset_id, project_id),
            )
        connection.execute(
            """
            INSERT INTO specification_review_revisions(
                review_revision_id, review_id, revision_number, project_id,
                existing_dataset_id, proposed_dataset_id
            ) VALUES ('revision-a-1', 'review-a', 1, 'project-a',
                      'existing-a', 'proposed-a')
            """
        )


@pytest.fixture
def database(tmp_path) -> Database:
    database = Database(tmp_path / "approved.sqlite3")
    initialize_prerequisites(database)
    return database


@pytest.fixture
def repository(database) -> ApprovedSpecificationSnapshotRepository:
    return ApprovedSpecificationSnapshotRepository(database)


def make_snapshot(
    *,
    snapshot_id: str = "snapshot-a",
    source_revision_id: str = "revision-a-1",
    created_at: str = "2026-07-31T09:00:00Z",
) -> ApprovedSpecificationSnapshot:
    values = (
        ApprovedSpecificationValue("board.grade", "B", "accepted_proposed"),
        ApprovedSpecificationValue("dimensions.length", 120, "unchanged"),
    )
    excluded = ("optional.coating",)
    materialization = ApprovedSpecificationMaterialization(values, excluded)
    digest = approved_specification_content_hash(
        project_id="project-a",
        review_id="review-a",
        source_review_revision_id=source_revision_id,
        source_review_revision_number=1,
        existing_dataset_id="existing-a",
        proposed_dataset_id="proposed-a",
        materialization=materialization,
        snapshot_schema_version="1.0",
    )
    return ApprovedSpecificationSnapshot(
        snapshot_id=snapshot_id,
        project_id="project-a",
        review_id="review-a",
        source_review_revision_id=source_revision_id,
        source_review_revision_number=1,
        existing_dataset_id="existing-a",
        proposed_dataset_id="proposed-a",
        approved_values=values,
        excluded_fields=excluded,
        snapshot_schema_version="1.0",
        actor_reference="packaging.manager",
        approval_reason="Controlled human-authorized handoff.",
        content_hash=digest,
        created_at=created_at,
    )


def test_applies_additive_schema_version_11(database, repository):
    with database.connect() as connection:
        versions = {
            row[0]
            for row in connection.execute("SELECT version FROM schema_migrations")
        }
    assert APPROVED_SPECIFICATION_SCHEMA_VERSION == 11
    assert 11 in versions


def test_persists_and_reloads_exact_snapshot(repository):
    snapshot = make_snapshot()
    created = repository.create(snapshot)
    reloaded = ApprovedSpecificationSnapshotRepository(repository.database).get(
        snapshot.snapshot_id,
        project_id=snapshot.project_id,
    )
    assert created == snapshot
    assert reloaded == snapshot


def test_duplicate_source_revision_is_rejected(repository):
    repository.create(make_snapshot())
    with pytest.raises(ApprovedSpecificationPersistenceError) as error:
        repository.create(make_snapshot(snapshot_id="snapshot-other"))
    assert error.value.code == "duplicate_source_revision"


def test_archived_project_creation_is_rejected(database, repository):
    with database.transaction() as connection:
        connection.execute(
            "UPDATE projects SET archived_at = '2026-07-31' WHERE project_id = 'project-a'"
        )
    with pytest.raises(ApprovedSpecificationPersistenceError) as error:
        repository.create(make_snapshot())
    assert error.value.code == "archived_project"


def test_cross_project_read_fails_closed(repository):
    snapshot = repository.create(make_snapshot())
    with pytest.raises(ApprovedSpecificationPersistenceError) as error:
        repository.get(snapshot.snapshot_id, project_id="project-b")
    assert error.value.code == "snapshot_not_found"


def test_unknown_project_read_fails_closed(repository):
    with pytest.raises(ApprovedSpecificationPersistenceError) as error:
        repository.list_for_project("missing-project")
    assert error.value.code == "unknown_project"


def test_review_lineage_mismatch_is_rejected(repository):
    snapshot = make_snapshot()
    broken = ApprovedSpecificationSnapshot(
        **{**snapshot.__dict__, "review_id": "wrong-review"}
    )
    materialization = ApprovedSpecificationMaterialization(
        broken.approved_values,
        broken.excluded_fields,
    )
    broken = ApprovedSpecificationSnapshot(
        **{
            **broken.__dict__,
            "content_hash": approved_specification_content_hash(
                project_id=broken.project_id,
                review_id=broken.review_id,
                source_review_revision_id=broken.source_review_revision_id,
                source_review_revision_number=broken.source_review_revision_number,
                existing_dataset_id=broken.existing_dataset_id,
                proposed_dataset_id=broken.proposed_dataset_id,
                materialization=materialization,
                snapshot_schema_version=broken.snapshot_schema_version,
            ),
        }
    )
    with pytest.raises(ApprovedSpecificationPersistenceError) as error:
        repository.create(broken)
    assert error.value.code == "invalid_review_lineage"


def test_content_hash_is_verified_before_create(repository):
    snapshot = make_snapshot()
    tampered = ApprovedSpecificationSnapshot(
        **{**snapshot.__dict__, "content_hash": "0" * 64}
    )
    with pytest.raises(ApprovedSpecificationPersistenceError) as error:
        repository.create(tampered)
    assert error.value.code == "content_hash_mismatch"


def test_tampered_content_fails_integrity_verification(database, repository):
    snapshot = repository.create(make_snapshot())
    with database.connect() as connection:
        connection.execute(
            "DROP TRIGGER approved_specification_snapshots_immutable_update"
        )
        connection.execute(
            """
            UPDATE approved_specification_snapshots
            SET approved_values_json = ?
            WHERE snapshot_id = ?
            """,
            (
                '[{"field_key":"board.grade","source":"accepted_proposed","value":"C"},'
                '{"field_key":"dimensions.length","source":"unchanged","value":120}]',
                snapshot.snapshot_id,
            ),
        )
        connection.commit()
    with pytest.raises(ApprovedSpecificationPersistenceError) as error:
        repository.get(snapshot.snapshot_id, project_id="project-a")
    assert error.value.code == "content_hash_mismatch"


def test_repository_update_and_delete_are_rejected(repository):
    with pytest.raises(ApprovedSpecificationPersistenceError) as update_error:
        repository.update("snapshot-a", actor_reference="other")
    with pytest.raises(ApprovedSpecificationPersistenceError) as delete_error:
        repository.delete("snapshot-a")
    assert update_error.value.code == "immutable_snapshot"
    assert delete_error.value.code == "immutable_snapshot"


def test_database_triggers_reject_update_and_delete(database, repository):
    snapshot = repository.create(make_snapshot())
    with database.connect() as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                UPDATE approved_specification_snapshots
                SET approval_reason = 'changed'
                WHERE snapshot_id = ?
                """,
                (snapshot.snapshot_id,),
            )
        connection.rollback()
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "DELETE FROM approved_specification_snapshots WHERE snapshot_id = ?",
                (snapshot.snapshot_id,),
            )


def test_project_listing_is_deterministic(repository, database):
    first = repository.create(
        make_snapshot(
            snapshot_id="snapshot-b",
            created_at="2026-07-31T10:00:00Z",
        )
    )
    with database.transaction() as connection:
        connection.execute(
            """
            INSERT INTO specification_review_revisions(
                review_revision_id, review_id, revision_number, project_id,
                existing_dataset_id, proposed_dataset_id
            ) VALUES ('revision-a-2', 'review-a-2', 1, 'project-a',
                      'existing-a', 'proposed-a')
            """
        )
    second_base = make_snapshot(
        snapshot_id="snapshot-a",
        source_revision_id="revision-a-2",
        created_at="2026-07-31T09:00:00Z",
    )
    second = ApprovedSpecificationSnapshot(
        **{**second_base.__dict__, "review_id": "review-a-2"}
    )
    materialization = ApprovedSpecificationMaterialization(
        second.approved_values,
        second.excluded_fields,
    )
    second = ApprovedSpecificationSnapshot(
        **{
            **second.__dict__,
            "content_hash": approved_specification_content_hash(
                project_id=second.project_id,
                review_id=second.review_id,
                source_review_revision_id=second.source_review_revision_id,
                source_review_revision_number=second.source_review_revision_number,
                existing_dataset_id=second.existing_dataset_id,
                proposed_dataset_id=second.proposed_dataset_id,
                materialization=materialization,
                snapshot_schema_version=second.snapshot_schema_version,
            ),
        }
    )
    repository.create(second)
    assert repository.list_for_project("project-a") == [second, first]


def test_get_for_review_is_project_scoped(repository):
    snapshot = repository.create(make_snapshot())
    assert repository.get_for_review(
        snapshot.review_id,
        project_id=snapshot.project_id,
    ) == snapshot
    assert repository.get_for_review(
        "unknown-review",
        project_id=snapshot.project_id,
    ) is None
