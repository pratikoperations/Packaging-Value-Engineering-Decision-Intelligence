from __future__ import annotations

from src.application import runtime


def test_approved_snapshot_repository_builder_uses_initialized_database(monkeypatch) -> None:
    database = object()
    captured: dict[str, object] = {}

    class Repository:
        def __init__(self, supplied_database) -> None:
            captured["database"] = supplied_database

    monkeypatch.setattr(runtime, "_initialized_database", lambda path: database)
    monkeypatch.setattr(runtime, "ApprovedSpecificationSnapshotRepository", Repository)

    result = runtime.build_approved_specification_snapshot_repository("runtime.sqlite3")

    assert isinstance(result, Repository)
    assert captured["database"] is database


def test_approved_snapshot_service_uses_one_initialized_database(monkeypatch) -> None:
    database = object()
    created: list[tuple[str, object]] = []

    def repository_type(name: str):
        class Repository:
            def __init__(self, supplied_database) -> None:
                self.database = supplied_database
                created.append((name, supplied_database))
        return Repository

    class Service:
        def __init__(self, review_repository, snapshot_repository, dataset_repository) -> None:
            self.review_repository = review_repository
            self.snapshot_repository = snapshot_repository
            self.dataset_repository = dataset_repository

    monkeypatch.setattr(runtime, "_initialized_database", lambda path: database)
    monkeypatch.setattr(runtime, "SpecificationReviewRepository", repository_type("review"))
    monkeypatch.setattr(
        runtime, "ApprovedSpecificationSnapshotRepository", repository_type("snapshot")
    )
    monkeypatch.setattr(runtime, "DatasetRepository", repository_type("dataset"))
    monkeypatch.setattr(runtime, "ApprovedSpecificationSnapshotService", Service)

    service = runtime.build_approved_specification_snapshot_service("runtime.sqlite3")

    assert [name for name, _ in created] == ["review", "snapshot", "dataset"]
    assert all(supplied is database for _, supplied in created)
    assert service.review_repository.database is database
    assert service.snapshot_repository.database is database
    assert service.dataset_repository.database is database


def test_approved_snapshot_read_model_uses_one_initialized_database(monkeypatch) -> None:
    database = object()

    class Repository:
        def __init__(self, supplied_database) -> None:
            self.database = supplied_database

    class ReadModel:
        def __init__(self, repository) -> None:
            self.repository = repository

    monkeypatch.setattr(runtime, "_initialized_database", lambda path: database)
    monkeypatch.setattr(runtime, "ApprovedSpecificationSnapshotRepository", Repository)
    monkeypatch.setattr(runtime, "ApprovedSpecificationReadModel", ReadModel)

    read_model = runtime.build_approved_specification_read_model("runtime.sqlite3")

    assert read_model.repository.database is database


def test_existing_runtime_builders_remain_available() -> None:
    expected = {
        "build_project_repository",
        "build_dataset_repository",
        "build_project_service",
        "build_upload_service",
        "build_specification_snapshot_repository",
        "build_specification_review_repository",
        "build_specification_review_read_model",
        "build_persistent_specification_review_service",
        "build_threshold_service",
        "build_controlled_scenario_service",
        "build_decision_snapshot_service",
    }

    assert expected.issubset(vars(runtime))
