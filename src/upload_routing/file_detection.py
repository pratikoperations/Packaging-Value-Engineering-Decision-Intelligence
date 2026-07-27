from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import PurePath
from zipfile import BadZipFile, ZipFile

from pypdf import PdfReader

from .models import DetectedUpload, DetectionStatus, FileFormat, WorkflowKind


_MIME_BY_FORMAT: dict[FileFormat, set[str]] = {
    FileFormat.XLSX: {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream",
    },
    FileFormat.CSV: {"text/csv", "application/csv", "text/plain", "application/octet-stream"},
    FileFormat.JSON: {"application/json", "text/json", "text/plain", "application/octet-stream"},
    FileFormat.DOCX: {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/octet-stream",
    },
    FileFormat.PDF: {"application/pdf", "application/octet-stream"},
}


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _reject(filename: str, mime_type: str, content: bytes, code: str, detail: str) -> DetectedUpload:
    return DetectedUpload(
        filename=filename,
        mime_type=mime_type,
        sha256=_sha256(content),
        file_format=None,
        workflow=None,
        status=DetectionStatus.REJECTED,
        reason_code=code,
        detail=detail,
    )


def _validate_ooxml(content: bytes, expected_member: str) -> bool:
    try:
        with ZipFile(io.BytesIO(content)) as archive:
            names = set(archive.namelist())
            return "[Content_Types].xml" in names and expected_member in names
    except BadZipFile:
        return False


def _validate_csv(content: bytes) -> bool:
    try:
        text = content.decode("utf-8-sig")
        sample = text[:8192]
        dialect = csv.Sniffer().sniff(sample)
        rows = list(csv.reader(io.StringIO(sample), dialect))
        return len(rows) >= 2 and max((len(row) for row in rows), default=0) >= 2
    except (UnicodeDecodeError, csv.Error):
        return False


def _validate_json(content: bytes) -> bool:
    try:
        parsed = json.loads(content.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False
    return isinstance(parsed, (dict, list))


def _validate_pdf(content: bytes) -> tuple[bool, str | None, str | None]:
    if not content.startswith(b"%PDF-"):
        return False, "invalid_signature", "The file does not have a valid PDF signature."
    try:
        reader = PdfReader(io.BytesIO(content), strict=False)
        if reader.is_encrypted:
            return False, "encrypted_pdf", "Encrypted PDFs are not supported."
        extracted = "".join((page.extract_text() or "") for page in reader.pages).strip()
        if len(extracted) < 40:
            return False, "scanned_or_image_only_pdf", "The PDF does not contain enough searchable text."
    except Exception:
        return False, "malformed_pdf", "The PDF could not be parsed safely."
    return True, None, None


def detect_upload(filename: str, mime_type: str | None, content: bytes) -> DetectedUpload:
    safe_mime = (mime_type or "application/octet-stream").lower()
    extension = PurePath(filename).suffix.lower().lstrip(".")
    try:
        file_format = FileFormat(extension)
    except ValueError:
        return _reject(filename, safe_mime, content, "unsupported_format", "Supported formats are XLSX, CSV, JSON, DOCX and searchable PDF.")

    if safe_mime not in _MIME_BY_FORMAT[file_format]:
        return _reject(filename, safe_mime, content, "mime_mismatch", f"MIME type {safe_mime!r} is inconsistent with .{extension}.")

    valid = False
    code: str | None = None
    detail: str | None = None
    if file_format is FileFormat.XLSX:
        valid = _validate_ooxml(content, "xl/workbook.xml")
        code, detail = "malformed_xlsx", "The XLSX package structure is invalid."
    elif file_format is FileFormat.DOCX:
        valid = _validate_ooxml(content, "word/document.xml")
        code, detail = "malformed_docx", "The DOCX package structure is invalid."
    elif file_format is FileFormat.CSV:
        valid = _validate_csv(content)
        code, detail = "malformed_csv", "The CSV must contain a consistent table with at least two rows and two columns."
    elif file_format is FileFormat.JSON:
        valid = _validate_json(content)
        code, detail = "malformed_json", "The JSON must contain a valid object or array."
    elif file_format is FileFormat.PDF:
        valid, code, detail = _validate_pdf(content)

    if not valid:
        return _reject(filename, safe_mime, content, code or "invalid_file", detail or "The file failed structural validation.")

    workflow = (
        WorkflowKind.SPECIFICATION_COMPARISON
        if file_format in {FileFormat.DOCX, FileFormat.PDF}
        else WorkflowKind.STRUCTURED_PROJECT_DATA
    )
    status = DetectionStatus.ROLE_REQUIRED if workflow is WorkflowKind.SPECIFICATION_COMPARISON else DetectionStatus.READY
    return DetectedUpload(
        filename=filename,
        mime_type=safe_mime,
        sha256=_sha256(content),
        file_format=file_format,
        workflow=workflow,
        status=status,
    )
