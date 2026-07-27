"""Controlled synthetic demonstration service for PVE 2.1 PDF intake."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from src.ai_extraction import ConfidenceBand, ExtractionCandidate
from src.document_intake import DocumentRole
from src.pdf_intake import ParsedPdf, parse_validated_pdf, validate_pdf
from src.pdf_intake.integration import build_pdf_review_bundle

EXTRACTION_SCHEMA_VERSION = "pve-word-extraction-v1"
ALIAS_REGISTRY_VERSION = "1.0"
PROVIDER_ID = "deterministic-synthetic-pdf-demo"

_LABELS = {
    "specification_number": "Specification number",
    "specification_revision": "Revision",
    "item_code": "Item code",
    "item_description": "Item description",
    "supplier_name": "Supplier",
    "box_style": "Box style",
    "internal_length": "Internal length",
    "internal_width": "Internal width",
    "internal_height": "Internal height",
    "ply_count": "Ply count",
    "flute_combination": "Flute combination",
    "box_weight": "Box weight",
    "compression_requirement": "Compression requirement",
}
_NUMERIC = {"internal_length", "internal_width", "internal_height", "ply_count", "box_weight", "compression_requirement"}
_VALUE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*([A-Za-z]+)?\s*$")


@dataclass(frozen=True)
class PdfDemoEvaluation:
    precision: float = 1.0
    recall: float = 1.0
    source_grounding: float = 1.0
    role_accuracy: float = 1.0
    invented_values: int = 0
    unsourced_values: int = 0
    unconfirmed_values_mapped: int = 0


def _escape_pdf(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _simple_pdf(lines: Iterable[str]) -> bytes:
    commands = ["BT", "/F1 10 Tf", "50 790 Td"]
    first = True
    for line in lines:
        if not first:
            commands.append("0 -18 Td")
        commands.append(f"({_escape_pdf(line)}) Tj")
        first = False
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    data = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(data))
        data.extend(f"{index} 0 obj\n".encode())
        data.extend(obj)
        data.extend(b"\nendobj\n")
    xref = len(data)
    data.extend(f"xref\n0 {len(objects)+1}\n".encode())
    data.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(data)


def synthetic_pdf_documents() -> tuple[bytes, bytes]:
    existing = {
        "Specification number": "CORR-PDF-1001", "Revision": "04", "Item code": "SYN-PDF-001",
        "Item description": "Synthetic shipping case", "Supplier": "Synthetic Supplier A", "Box style": "RSC",
        "Internal length": "400 mm", "Internal width": "300 mm", "Internal height": "250 mm",
        "Ply count": "5 ply", "Flute combination": "BC", "Box weight": "780 g", "Compression requirement": "620 kgf",
    }
    proposed = {
        "Specification number": "CORR-PDF-1001-P", "Revision": "01", "Item code": "SYN-PDF-001",
        "Item description": "Synthetic lightweight shipping case", "Supplier": "Synthetic Supplier B", "Box style": "RSC",
        "Internal length": "400 mm", "Internal width": "300 mm", "Internal height": "250 mm",
        "Ply count": "3 ply", "Flute combination": "B", "Box weight": "650 g", "Compression requirement": "580 kgf",
    }
    return (
        _simple_pdf(["Existing synthetic corrugated specification"] + [f"{k}: {v}" for k, v in existing.items()]),
        _simple_pdf(["Proposed synthetic corrugated specification"] + [f"{k}: {v}" for k, v in proposed.items()]),
    )


def load_synthetic_pdf_pair() -> tuple[ParsedPdf, ParsedPdf]:
    existing, proposed = synthetic_pdf_documents()
    return (
        parse_validated_pdf(validate_pdf("existing_synthetic.pdf", existing, DocumentRole.EXISTING)),
        parse_validated_pdf(validate_pdf("proposed_synthetic.pdf", proposed, DocumentRole.PROPOSED)),
    )


def _parse_value(field: str, text: str):
    if field not in _NUMERIC:
        return text.strip(), None
    match = _VALUE.match(text)
    if not match:
        return text.strip(), None
    number = float(match.group(1))
    return (int(number) if number.is_integer() else number), match.group(2)


def deterministic_pdf_candidates(document: ParsedPdf) -> tuple[ExtractionCandidate, ...]:
    candidates = []
    for block in document.blocks:
        for raw_line in block.raw_text.splitlines():
            line = " ".join(raw_line.split())
            for field, label in _LABELS.items():
                prefix = label + ":"
                if line.startswith(prefix):
                    raw = line[len(prefix):].strip()
                    value, unit = _parse_value(field, raw)
                    candidates.append(
                        ExtractionCandidate(
                            field,
                            document.role,
                            raw,
                            value,
                            unit,
                            99.0,
                            ConfidenceBand.HIGH,
                            block.block_id,
                            line,
                            (),
                        )
                    )
    return tuple(candidates)


def build_pdf_demo_reviews(documents: tuple[ParsedPdf, ParsedPdf]):
    candidates = deterministic_pdf_candidates(documents[0]) + deterministic_pdf_candidates(documents[1])
    return build_pdf_review_bundle(candidates, documents)
