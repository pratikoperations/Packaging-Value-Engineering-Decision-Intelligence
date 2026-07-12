from __future__ import annotations

import csv
import io
from typing import Any

from src.uploads.models import UploadParseError

MAX_UPLOAD_BYTES = 1 * 1024 * 1024
MAX_ROWS = 500
REQUIRED_FILES = {"project.csv", "alternatives.csv"}

PROJECT_COLUMNS = {"project_name", "category", "annual_volume", "currency"}
ALTERNATIVE_COLUMNS = {
    "alternative_id",
    "name",
    "status",
    "length_mm",
    "width_mm",
    "height_mm",
    "case_weight_g",
    "board_grade",
}


def _parse_csv(content: bytes, filename: str, required_columns: set[str]) -> list[dict[str, str]]:
    if not content:
        raise UploadParseError(f"{filename} is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise UploadParseError(f"{filename} exceeds the 1 MB limit.")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise UploadParseError(f"{filename} must use UTF-8 encoding.") from error
    reader = csv.DictReader(io.StringIO(text))
    fieldnames = set(reader.fieldnames or [])
    missing = sorted(required_columns - fieldnames)
    if missing:
        raise UploadParseError(f"{filename} is missing required columns: {', '.join(missing)}.")
    rows: list[dict[str, str]] = []
    for index, row in enumerate(reader, start=2):
        if index - 1 > MAX_ROWS:
            raise UploadParseError(f"{filename} exceeds the {MAX_ROWS}-row limit.")
        normalized = {str(key).strip(): (value or "").strip() for key, value in row.items()}
        if any(normalized.values()):
            rows.append(normalized)
    return rows


def parse_csv_uploads(files: dict[str, bytes]) -> dict[str, Any]:
    normalized_files = {name.lower(): content for name, content in files.items()}
    missing_files = sorted(REQUIRED_FILES - normalized_files.keys())
    if missing_files:
        raise UploadParseError(
            "CSV upload requires exactly the documented templates: "
            + ", ".join(sorted(REQUIRED_FILES))
            + f". Missing: {', '.join(missing_files)}."
        )
    unsupported = sorted(set(normalized_files) - REQUIRED_FILES)
    if unsupported:
        raise UploadParseError(
            "Unsupported CSV file(s): " + ", ".join(unsupported) + ". Only project.csv and alternatives.csv are accepted."
        )
    project_rows = _parse_csv(normalized_files["project.csv"], "project.csv", PROJECT_COLUMNS)
    if len(project_rows) != 1:
        raise UploadParseError("project.csv must contain exactly one data row.")
    alternative_rows = _parse_csv(
        normalized_files["alternatives.csv"],
        "alternatives.csv",
        ALTERNATIVE_COLUMNS,
    )
    if not alternative_rows:
        raise UploadParseError("alternatives.csv must contain at least one data row.")
    return {
        "packaging_project": project_rows[0],
        "packaging_alternatives": alternative_rows,
    }
