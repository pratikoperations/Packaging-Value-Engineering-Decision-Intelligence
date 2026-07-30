from __future__ import annotations

from pathlib import Path

from src.application.persistent_specification_review_service import PersistentSpecificationReviewService
from src.application.project_service import ProjectService
from src.application.specification_review_read_model import SpecificationReviewReadModel
from src.application.specification_review_service import SpecificationReviewService
from src.decision_snapshots.service import DecisionSnapshotService
from src.persistence.database import Database
from src.persistence.dataset_repository import DatasetRepository
from src.persistence.decision_repository import DecisionRepository
from src.persistence.migrations import initialize_database
from src.persistence.project_repository import ProjectRepository
from src.persistence.scenario_repository import ScenarioRepository
from src.persistence.specification_review_repository import SpecificationReviewRepository
from src.persistence.specification_snapshot_repository import SpecificationSnapshotRepository
from src.persistence.threshold_repository import ThresholdRepository
from src.scenario_execution.service import ControlledScenarioService
from src.thresholds.service import ThresholdService
from src.uploads.service import UploadService


def _initialized_database(database_path: str | Path) -> Database:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    database = Database(path)
    initialize_database(database)
    return database


def build_project_repository(database_path: str | Path) -> ProjectRepository:
    return ProjectRepository(_initialized_database(database_path))


def build_dataset_repository(database_path: str | Path) -> DatasetRepository:
    return DatasetRepository(_initialized_database(database_path))


def build_project_service(database_path: str | Path) -> ProjectService:
    database = _initialized_database(database_path)
    return ProjectService(ProjectRepository(database))


def build_upload_service(database_path: str | Path) -> UploadService:
    database = _initialized_database(database_path)
    return UploadService(DatasetRepository(database))


def build_specification_snapshot_repository(database_path: str | Path) -> SpecificationSnapshotRepository:
    """Create the additive append-only unified specification snapshot repository."""
    database = _initialized_database(database_path)
    return SpecificationSnapshotRepository(database)


def build_specification_review_repository(database_path: str | Path) -> SpecificationReviewRepository:
    """Create the additive append-only specification review repository."""
    database = _initialized_database(database_path)
    return SpecificationReviewRepository(database)


def build_specification_review_read_model(database_path: str | Path) -> SpecificationReviewReadModel:
    """Create the project-scoped read-only E1.5 review discovery boundary."""
    return SpecificationReviewReadModel(_initialized_database(database_path))


def build_persistent_specification_review_service(
    database_path: str | Path,
) -> PersistentSpecificationReviewService:
    database = _initialized_database(database_path)
    return PersistentSpecificationReviewService(
        SpecificationReviewService(),
        SpecificationReviewRepository(database),
    )


def build_threshold_service(database_path: str | Path) -> ThresholdService:
    database = _initialized_database(database_path)
    return ThresholdService(ThresholdRepository(database))


def build_controlled_scenario_service(database_path: str | Path) -> ControlledScenarioService:
    database = _initialized_database(database_path)
    return ControlledScenarioService(
        DatasetRepository(database),
        ThresholdRepository(database),
        ScenarioRepository(database),
    )


def build_decision_snapshot_service(database_path: str | Path) -> DecisionSnapshotService:
    database = _initialized_database(database_path)
    return DecisionSnapshotService(
        DatasetRepository(database),
        ScenarioRepository(database),
        DecisionRepository(database),
    )
