"""PVE 2.0 source-grounded AI extraction boundary."""

from .confidence_policy import classify_confidence
from .extraction_contract import (
    AmbiguityCode,
    ConfidenceBand,
    ExtractionCandidate,
    ExtractionContractError,
    ExtractionRequest,
    ExtractionResult,
)
from .extraction_service import build_request, extract_document
from .field_registry import FieldRegistry, FieldRegistryError, load_field_registry
from .prompt_safety import provider_instruction, suspicious_block_ids
from .provider_interface import ExtractionProvider

__all__ = [
    "AmbiguityCode",
    "ConfidenceBand",
    "ExtractionCandidate",
    "ExtractionContractError",
    "ExtractionProvider",
    "ExtractionRequest",
    "ExtractionResult",
    "FieldRegistry",
    "FieldRegistryError",
    "build_request",
    "classify_confidence",
    "extract_document",
    "load_field_registry",
    "provider_instruction",
    "suspicious_block_ids",
]
