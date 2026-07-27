"""Controlled validation for PVE 2.0 digital DOCX intake."""

from __future__ import annotations

import hashlib
import io
import zipfile
from dataclasses import dataclass
from pathlib import PurePath
from typing import Iterable

from .document_models import DocumentRole

MAX_DOCX_BYTES = 10 * 1024 * 1024
REQUIRED_PARTS = frozenset({"[Content_Types].xml", "word/document.xml"})


class DocumentValidationError(ValueError):
    """Raised when an uploaded document violates the controlled intake contract."""


@dataclass(frozen=True)
class ValidatedDocument:
    filename: str
    role: DocumentRole
    content: bytes
    sha256: str
    part_names: tuple[str, ...]


def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def validate_docx(
    filename: str,
    content: bytes,
    role: DocumentRole,
    *,
    max_bytes: int = MAX_DOCX_BYTES,
) -> ValidatedDocument:
    """Validate one normal digital .docx without executing embedded content."""

    if not isinstance(role, DocumentRole):
        raise DocumentValidationError("Document role must be existing or proposed.")
    if not filename or PurePath(filename).suffix.lower() != ".docx":
        raise DocumentValidationError("Only .docx files are supported.")
    if not isinstance(content, bytes) or not content:
        raise DocumentValidationError("DOCX content must be non-empty bytes.")
    if len(content) > max_bytes:
        raise DocumentValidationError(f"DOCX exceeds the {max_bytes}-byte size limit.")

    try:
        with zipfile.ZipFile(io.BytesIO(content), "r") as archive:
            bad_member = archive.testzip()
            if bad_member is not None:
                raise DocumentValidationError(f"DOCX contains a corrupt ZIP member: {bad_member}")
            names = tuple(sorted(archive.namelist()))
    except DocumentValidationError:
        raise
    except (zipfile.BadZipFile, OSError) as exc:
        raise DocumentValidationError("File is not a valid, readable DOCX package.") from exc

    missing = REQUIRED_PARTS.difference(names)
    if missing:
        raise DocumentValidationError(
            "DOCX is missing required package parts: " + ", ".join(sorted(missing))
        )

    return ValidatedDocument(
        filename=PurePath(filename).name,
        role=role,
        content=content,
        sha256=compute_sha256(content),
        part_names=names,
    )


def validate_document_pair(documents: Iterable[ValidatedDocument]) -> tuple[ValidatedDocument, ValidatedDocument]:
    """Require exactly one existing and one proposed DOCX with different hashes."""

    items = tuple(documents)
    if len(items) != 2:
        raise DocumentValidationError("Exactly two DOCX files are required.")

    by_role = {item.role: item for item in items}
    if set(by_role) != {DocumentRole.EXISTING, DocumentRole.PROPOSED}:
        raise DocumentValidationError("Exactly one existing and one proposed DOCX are required.")

    existing = by_role[DocumentRole.EXISTING]
    proposed = by_role[DocumentRole.PROPOSED]
    if existing.sha256 == proposed.sha256:
        raise DocumentValidationError("Existing and proposed DOCX files are duplicates.")

    return existing, proposed
