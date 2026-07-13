from __future__ import annotations

from .excel_schema import CONTEXT_VALUES, REQUIREMENT_LEVELS, SOURCE_CLASSIFICATIONS, VALIDATION_STATUSES

DROPDOWNS = {
    "source_classification": SOURCE_CLASSIFICATIONS,
    "validation_status": VALIDATION_STATUSES,
    "requirement": REQUIREMENT_LEVELS,
    "context": CONTEXT_VALUES,
    "upload_status": ("uploaded", "missing", "not_applicable"),
    "verification_status": ("not_reviewed", "verified", "rejected", "expired"),
}
