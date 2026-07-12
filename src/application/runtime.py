from __future__ import annotations

from pathlib import Path

from src.application.project_service import ProjectService
from src.decision_snapshots.service import DecisionSnapshotService
from src.persistence.database import Database
from src.persistence.dataset_repository import DatasetRepository
from src.persistence.decision_repository import DecisionRepository
from src.persistence.migrations import initialize_database
from src.persistence.project_repository import ProjectRepository
from src.persistence.scenario_repository import ScenarioRepository
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


def build_project_service(database_path: str | Path) -> ProjectService:
    """Create an initialized project service for Streamlit or local workflows."""
    database = _initialized_database(database_path)
    return ProjectService(ProjectRepository(database))


def build_upload_service(database_path: str | Path) -> UploadService:
    """Create an initialized upload service using the same SQLite repository boundary."""
    database = _initialized_database(database_path)
    return UploadService(DatasetRepository(database))


def build_threshold_service(database_path: str | Path) -> ThresholdService:
    """Create an initialized threshold service using immutable profile versions."""
    database = _initialized_database(database_path)
    return ThresholdService(ThresholdRepository(database))


def build_controlled_scenario_service(database_path: str | Path) -> ControlledScenarioService:
    """Create the deterministic scenario service over immutable repository records."""
    database = _initialized_database(database_path)
    return ControlledScenarioService(
        DatasetRepository(database),
        ThresholdRepository(database),
        ScenarioRepository(database),
    )


def build_decision_snapshot_service(database_path: str | Path) -> DecisionSnapshotService:
    """Create the final decision snapshot and history service."""
    database = _initialized_database(database_path)
    return DecisionSnapshotService(
        ScenarioRepository(database),
        DecisionRepository(database),
    )
