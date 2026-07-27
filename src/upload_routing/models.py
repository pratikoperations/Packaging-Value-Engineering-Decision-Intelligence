from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FileFormat(str, Enum):
    XLSX = "xlsx"
    CSV = "csv"
    JSON = "json"
    DOCX = "docx"
    PDF = "pdf"


class WorkflowKind(str, Enum):
    STRUCTURED_PROJECT_DATA = "structured_project_data"
    SPECIFICATION_COMPARISON = "specification_comparison"


class DetectionStatus(str, Enum):
    READY = "ready"
    ROLE_REQUIRED = "role_required"
    REJECTED = "rejected"


@dataclass(frozen=True)
class DetectedUpload:
    filename: str
    mime_type: str
    sha256: str
    file_format: FileFormat | None
    workflow: WorkflowKind | None
    status: DetectionStatus
    reason_code: str | None = None
    detail: str | None = None

    @property
    def requires_document_role(self) -> bool:
        return self.workflow is WorkflowKind.SPECIFICATION_COMPARISON and self.status is not DetectionStatus.REJECTED
