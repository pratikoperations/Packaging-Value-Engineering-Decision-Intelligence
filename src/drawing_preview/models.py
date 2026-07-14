from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass
from typing import Any, Mapping
from xml.etree import ElementTree


_SUPPORTED = {"pdf", "svg", "png", "jpeg", "jpg"}
_MAX_PREVIEW_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class PreviewIssue:
    code: str
    message: str


@dataclass(frozen=True)
class PreviewDescriptor:
    available: bool
    mode: str
    mime_type: str | None
    payload: bytes | str | None
    metadata: dict[str, Any]
    limitations: tuple[str, ...]
    issues: tuple[PreviewIssue, ...]


def _metadata(record: Mapping[str, Any]) -> dict[str, Any]:
    fields = (
        "drawing_evidence_id",
        "document_type",
        "document_number",
        "title",
        "revision",
        "classification",
        "file_format",
        "source_reference",
        "source_classification",
        "validation_status",
        "approval_status",
        "sku",
        "supplier",
        "manufacturing_site",
        "specification_version",
        "issue_date",
        "effective_date",
    )
    return {field: record.get(field) for field in fields if record.get(field) not in (None, "")}


def _safe_svg(content: bytes) -> tuple[str | None, PreviewIssue | None]:
    try:
        text = content.decode("utf-8")
        root = ElementTree.fromstring(text)
    except (UnicodeDecodeError, ElementTree.ParseError):
        return None, PreviewIssue("invalid_svg", "SVG content is not valid UTF-8 XML.")

    if root.tag.split("}")[-1].lower() != "svg":
        return None, PreviewIssue("invalid_svg", "SVG root element is required.")

    for element in root.iter():
        local_name = element.tag.split("}")[-1].lower()
        if local_name in {"script", "foreignobject"}:
            return None, PreviewIssue("unsafe_svg", "Active SVG content is prohibited.")
        for key, value in element.attrib.items():
            attr = key.split("}")[-1].lower()
            lowered = str(value).strip().lower()
            if attr.startswith("on"):
                return None, PreviewIssue("unsafe_svg", "SVG event-handler attributes are prohibited.")
            if attr in {"href", "xlink:href"} and lowered.startswith(("http://", "https://", "javascript:")):
                return None, PreviewIssue("unsafe_svg", "External or executable SVG references are prohibited.")
    return text, None


def build_preview_descriptor(record: Mapping[str, Any], content: bytes | None) -> PreviewDescriptor:
    """Build a read-only preview descriptor without engineering interpretation."""
    metadata = _metadata(record)
    file_format = str(record.get("file_format") or "").lower()
    limitations = (
        "Preview is visual reference only and is not engineering validation or approval.",
        "Dimensions, geometry, cut lines, crease lines, slots and tolerances are not interpreted.",
        "DXF, DWG, AI and EPS remain governed references with no inline preview.",
    )
    issues: list[PreviewIssue] = []

    if file_format not in _SUPPORTED:
        issues.append(PreviewIssue("unsupported_preview_format", f"No inline preview is available for {file_format or 'unknown'} format."))
        return PreviewDescriptor(False, "fallback", None, None, metadata, limitations, tuple(issues))

    if content is None:
        issues.append(PreviewIssue("missing_content", "Preview content was not supplied."))
        return PreviewDescriptor(False, "fallback", None, None, metadata, limitations, tuple(issues))
    if not isinstance(content, bytes):
        issues.append(PreviewIssue("invalid_content_type", "Preview content must be bytes."))
        return PreviewDescriptor(False, "fallback", None, None, metadata, limitations, tuple(issues))
    if len(content) > _MAX_PREVIEW_BYTES:
        issues.append(PreviewIssue("preview_too_large", "Preview content exceeds the 10 MB lightweight-preview limit."))
        return PreviewDescriptor(False, "fallback", None, None, metadata, limitations, tuple(issues))

    expected_hash = str(record.get("content_hash") or "").lower()
    actual_hash = hashlib.sha256(content).hexdigest()
    if expected_hash and expected_hash != actual_hash:
        issues.append(PreviewIssue("checksum_mismatch", "Preview bytes do not match the governed evidence checksum."))
        return PreviewDescriptor(False, "fallback", None, None, metadata, limitations, tuple(issues))

    if file_format == "pdf":
        if not content.startswith(b"%PDF-"):
            issues.append(PreviewIssue("invalid_pdf_signature", "PDF signature was not found."))
            return PreviewDescriptor(False, "fallback", None, None, metadata, limitations, tuple(issues))
        encoded = base64.b64encode(content).decode("ascii")
        return PreviewDescriptor(True, "pdf_embed", "application/pdf", encoded, metadata, limitations, ())

    if file_format == "svg":
        safe_svg, issue = _safe_svg(content)
        if issue:
            return PreviewDescriptor(False, "fallback", None, None, metadata, limitations, (issue,))
        return PreviewDescriptor(True, "svg", "image/svg+xml", safe_svg, metadata, limitations, ())

    if file_format == "png":
        if not content.startswith(b"\x89PNG\r\n\x1a\n"):
            issues.append(PreviewIssue("invalid_png_signature", "PNG signature was not found."))
            return PreviewDescriptor(False, "fallback", None, None, metadata, limitations, tuple(issues))
        return PreviewDescriptor(True, "image", "image/png", content, metadata, limitations, ())

    if not content.startswith(b"\xff\xd8\xff"):
        issues.append(PreviewIssue("invalid_jpeg_signature", "JPEG signature was not found."))
        return PreviewDescriptor(False, "fallback", None, None, metadata, limitations, tuple(issues))
    return PreviewDescriptor(True, "image", "image/jpeg", content, metadata, limitations, ())
