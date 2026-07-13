from __future__ import annotations

from typing import Any

from src.persistence.dataset_repository import DatasetRepository
from src.uploads.csv_parser import parse_csv_uploads
from src.uploads.excel_normalizer import normalize_excel_workbook
from src.uploads.excel_parser import parse_excel_upload
from src.uploads.excel_validation import validate_excel_workbook
from src.uploads.json_parser import parse_json_upload
from src.uploads.models import PreparedUpload
from src.uploads.normalizer import normalize_user_dataset
from src.uploads.validation import validate_user_dataset


class DuplicateDatasetError(ValueError):
    """Raised when an identical canonical dataset already exists for a project."""


class UploadService:
    def __init__(self, datasets: DatasetRepository) -> None:
        self.datasets = datasets

    def prepare_json(self, *, content: bytes, filename: str, project: dict[str, Any]) -> PreparedUpload:
        raw = parse_json_upload(content)
        canonical = normalize_user_dataset(raw, project)
        validation = validate_user_dataset(
            canonical,
            expected_project_id=project["project_id"],
            expected_category=project["category"],
            expected_currency=project["currency"],
        )
        return PreparedUpload("json", filename, canonical, validation)

    def prepare_csv(self, *, files: dict[str, bytes], project: dict[str, Any]) -> PreparedUpload:
        raw = parse_csv_uploads(files)
        canonical = normalize_user_dataset(raw, project)
        validation = validate_user_dataset(
            canonical,
            expected_project_id=project["project_id"],
            expected_category=project["category"],
            expected_currency=project["currency"],
        )
        return PreparedUpload("csv_templates", ",".join(sorted(files)), canonical, validation)

    def prepare_excel(self, *, content: bytes, filename: str, project: dict[str, Any]) -> PreparedUpload:
        raw = parse_excel_upload(content)
        canonical = normalize_excel_workbook(raw, project)
        validation = validate_excel_workbook(raw, canonical, project)
        return PreparedUpload("excel_template", filename, canonical, validation)

    def save_valid_dataset(self, *, project_id: str, prepared: PreparedUpload) -> dict[str, Any]:
        if not prepared.validation.is_valid:
            raise ValueError("Invalid uploads cannot be saved as dataset versions.")
        existing = self.datasets.find_by_content(project_id, prepared.canonical_data)
        if existing is not None:
            raise DuplicateDatasetError(
                f"This canonical dataset already exists as version {existing['version_number']}."
            )
        issues = [
            {"code": issue.code, "path": issue.path, "message": issue.message}
            for issue in prepared.validation.issues
        ]
        return self.datasets.create_version(
            project_id=project_id,
            source_type=prepared.source_type,
            canonical_data=prepared.canonical_data,
            validation_status="valid",
            validation_issues=issues,
            original_filename=prepared.original_filename,
        )
