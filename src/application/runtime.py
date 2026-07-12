from __future__ import annotations

from pathlib import Path

from src.application.project_service import ProjectService
from src.persistence.database import Database
from src.persistence.migrations import initialize_database
from src.persistence.project_repository import ProjectRepository


def build_project_service(database_path: str | Path) -> ProjectService:
    """Create an initialized project service for Streamlit or local workflows."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    database = Database(path)
    initialize_database(database)
    return ProjectService(ProjectRepository(database))
