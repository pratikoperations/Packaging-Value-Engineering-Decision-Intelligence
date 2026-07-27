"""Validated provider-neutral AI extraction adapter.

Provider responses are treated as untrusted data. No canonical mapping,
persistence, review action, engineering decision, or autonomous approval occurs.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from src.document_intake import DocumentRole, ParsedDocument

from .confidence_policy import classify_confidence
from .extraction_contract import (
    AmbiguityCode,
    ExtractionCandidate,
    ExtractionContractError,
    ExtractionRequest,
    ExtractionResult,
    require_mapping,
)
from .field_registry import FieldRegistry, load_field_registry
from .prompt_safety import suspicious_block_ids
from .provider_interface import ExtractionProvider

FORBIDDEN_TOP_LEVEL_KEYS = frozenset(
    {
        "approval",
        "approved",
        "recommendation",
        "supplier_ranking",
        "cost_assumption",
        "savings_assumption",
        "laboratory_conclusion",
    }
)
ALLOWED_TOP_LEVEL_KEYS = frozenset(
    {"schema_version", "candidates", "missing_fields", "unsupported_content"}
)
ALLOWED_CANDIDATE_KEYS = frozenset(
    {
        "field_name",
        "document_role",
        "raw_value",
        "normalized_value",
        "unit",
        "confidence",
        "source_block_id",
        "source_excerpt",
        "ambiguity_codes",
    }
)


def build_request(document: ParsedDocument, registry: FieldRegistry) -> ExtractionRequest:
    return ExtractionRequest(
        schema_version=registry.schema_version,
        allowed_fields=registry.field_names,
        blocks=document.blocks,
        document_role=document.role,
    )


def _require_string_list(value: Any, label: str, allowed: set[str] | None = None) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ExtractionContractError(f"{label} must be a list of strings.")
    result = tuple(value)
    if allowed is not None and any(item not in allowed for item in result):
        raise ExtractionContractError(f"{label} contains unsupported values.")
    return result


def _validate_candidate(
    payload: Any,
    *,
    document: ParsedDocument,
    registry: FieldRegistry,
    suspicious_ids: set[str],
) -> ExtractionCandidate:
    candidate = require_mapping(payload, "candidate")
    unknown = set(candidate).difference(ALLOWED_CANDIDATE_KEYS)
    if unknown:
        raise ExtractionContractError("candidate contains unsupported keys: " + ", ".join(sorted(unknown)))

    required = {"field_name", "document_role", "raw_value", "confidence", "source_block_id", "source_excerpt"}
    missing = required.difference(candidate)
    if missing:
        raise ExtractionContractError("candidate is missing required keys: " + ", ".join(sorted(missing)))

    field_name = candidate["field_name"]
    if field_name not in registry.field_names:
        raise ExtractionContractError(f"unsupported governed field: {field_name}")

    try:
        role = DocumentRole(candidate["document_role"])
    except (TypeError, ValueError) as exc:
        raise ExtractionContractError("candidate document_role is invalid.") from exc
    if role is not document.role:
        raise ExtractionContractError("candidate document_role does not match the parsed document.")

    raw_value = candidate["raw_value"]
    if raw_value is None or raw_value == "" or raw_value == []:
        raise ExtractionContractError("candidate raw_value cannot be missing or invented.")

    source_block_id = candidate["source_block_id"]
    source_lookup = {block.block_id: block for block in document.blocks}
    if source_block_id not in source_lookup:
        raise ExtractionContractError("candidate source_block_id is not present in approved source blocks.")
    source_block = source_lookup[source_block_id]

    excerpt = candidate["source_excerpt"]
    if not isinstance(excerpt, str) or not excerpt.strip():
        raise ExtractionContractError("candidate source_excerpt is required.")
    if excerpt.strip() not in source_block.text:
        raise ExtractionContractError("candidate source_excerpt is not grounded in the cited source block.")

    confidence = candidate["confidence"]
    band = classify_confidence(confidence)

    raw_codes = candidate.get("ambiguity_codes", [])
    if not isinstance(raw_codes, list):
        raise ExtractionContractError("ambiguity_codes must be a list.")
    try:
        codes = [AmbiguityCode(value) for value in raw_codes]
    except (TypeError, ValueError) as exc:
        raise ExtractionContractError("ambiguity_codes contains an unsupported code.") from exc
    if source_block_id in suspicious_ids and AmbiguityCode.PROMPT_INJECTION_SUSPECTED not in codes:
        codes.append(AmbiguityCode.PROMPT_INJECTION_SUSPECTED)

    unit = candidate.get("unit")
    if unit is not None and not isinstance(unit, str):
        raise ExtractionContractError("candidate unit must be a string or null.")

    return ExtractionCandidate(
        field_name=field_name,
        document_role=role,
        raw_value=raw_value,
        normalized_value=candidate.get("normalized_value"),
        unit=unit,
        confidence=float(confidence),
        confidence_band=band,
        source_block_id=source_block_id,
        source_excerpt=excerpt.strip(),
        ambiguity_codes=tuple(codes),
    )


def extract_document(
    document: ParsedDocument,
    provider: ExtractionProvider,
    registry: FieldRegistry | None = None,
) -> ExtractionResult:
    """Call a provider and reject any response outside the governed contract."""

    governed_registry = registry or load_field_registry()
    request = build_request(document, governed_registry)
    response = require_mapping(provider.extract(request), "provider response")

    forbidden = set(response).intersection(FORBIDDEN_TOP_LEVEL_KEYS)
    if forbidden:
        raise ExtractionContractError("provider response contains prohibited outputs.")
    unknown = set(response).difference(ALLOWED_TOP_LEVEL_KEYS)
    if unknown:
        raise ExtractionContractError("provider response contains unsupported top-level keys.")
    if response.get("schema_version") != governed_registry.schema_version:
        raise ExtractionContractError("provider schema_version does not match the governed registry.")

    raw_candidates = response.get("candidates")
    if not isinstance(raw_candidates, list):
        raise ExtractionContractError("candidates must be a list.")

    suspicious_ids = set(suspicious_block_ids(document.blocks))
    candidates = tuple(
        _validate_candidate(
            item,
            document=document,
            registry=governed_registry,
            suspicious_ids=suspicious_ids,
        )
        for item in raw_candidates
    )

    missing_fields = _require_string_list(
        response.get("missing_fields", []),
        "missing_fields",
        set(governed_registry.field_names),
    )
    unsupported_content = _require_string_list(
        response.get("unsupported_content", []), "unsupported_content"
    )

    returned_names = [candidate.field_name for candidate in candidates]
    if len(returned_names) != len(set(returned_names)):
        ambiguous = {
            candidate.field_name
            for candidate in candidates
            if returned_names.count(candidate.field_name) > 1
            and AmbiguityCode.MULTIPLE_CANDIDATES not in candidate.ambiguity_codes
        }
        if ambiguous:
            raise ExtractionContractError(
                "duplicate field candidates require multiple_candidates ambiguity."
            )

    return ExtractionResult(
        schema_version=governed_registry.schema_version,
        provider_id=provider.provider_id,
        candidates=candidates,
        missing_fields=missing_fields,
        unsupported_content=unsupported_content,
    )
