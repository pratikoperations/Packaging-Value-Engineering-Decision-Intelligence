"""Deterministic decision-package assembly and rendering utilities."""

from .calculation_evidence_export import (
    CALCULATION_EVIDENCE_DISCLOSURE,
    attach_calculation_evidence,
    render_calculation_evidence_markdown,
)
from .decision_package import (
    assemble_decision_package,
    render_decision_package_json,
    render_decision_package_markdown,
    validate_decision_package,
)

__all__ = [
    "CALCULATION_EVIDENCE_DISCLOSURE",
    "assemble_decision_package",
    "attach_calculation_evidence",
    "render_calculation_evidence_markdown",
    "render_decision_package_json",
    "render_decision_package_markdown",
    "validate_decision_package",
]
