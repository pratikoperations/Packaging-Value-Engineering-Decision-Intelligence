"""Provider-neutral boundary for AI-assisted extraction."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from .extraction_contract import ExtractionRequest


class ExtractionProvider(Protocol):
    provider_id: str

    def extract(self, request: ExtractionRequest) -> Mapping[str, Any]:
        """Return schema-shaped data; validation is performed by the service."""
        ...
