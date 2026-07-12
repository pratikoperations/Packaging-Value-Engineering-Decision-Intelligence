from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.data_models.validator import ValidationResult


class UploadParseError(ValueError):
    """Raised when an uploaded file cannot be parsed safely."""


@dataclass(frozen=True)
class PreparedUpload:
    source_type: str
    original_filename: str
    canonical_data: dict[str, Any]
    validation: ValidationResult
