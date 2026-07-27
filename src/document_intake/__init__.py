"""PVE 2.0 deterministic Word intake boundary.

Build Group B only: no AI calls, canonical mapping, persistence, OCR, PDF, or
changes to existing PVE decision logic.
"""

from .document_models import (
    DocumentPair,
    DocumentRole,
    ParsedDocument,
    SourceBlock,
    SourceBlockType,
    SourceLocation,
    UnsupportedContent,
)
from .docx_parser import parse_validated_docx
from .file_validation import (
    DocumentValidationError,
    ValidatedDocument,
    compute_sha256,
    validate_document_pair,
    validate_docx,
)


def parse_document_pair(
    existing_filename: str,
    existing_content: bytes,
    proposed_filename: str,
    proposed_content: bytes,
) -> DocumentPair:
    """Validate and parse exactly one existing and one proposed DOCX."""

    existing = validate_docx(existing_filename, existing_content, DocumentRole.EXISTING)
    proposed = validate_docx(proposed_filename, proposed_content, DocumentRole.PROPOSED)
    existing, proposed = validate_document_pair((existing, proposed))
    return DocumentPair(
        existing=parse_validated_docx(existing),
        proposed=parse_validated_docx(proposed),
    )


__all__ = [
    "DocumentPair",
    "DocumentRole",
    "DocumentValidationError",
    "ParsedDocument",
    "SourceBlock",
    "SourceBlockType",
    "SourceLocation",
    "UnsupportedContent",
    "ValidatedDocument",
    "compute_sha256",
    "parse_document_pair",
    "parse_validated_docx",
    "validate_document_pair",
    "validate_docx",
]
