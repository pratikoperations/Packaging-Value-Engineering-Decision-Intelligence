from __future__ import annotations

import re

from .domain import SyntheticDataError

_PATTERNS = {
    "supplier": re.compile(r"^SUP-SYN-\d{3}$"),
    "specification": re.compile(r"^SPC-SYN-\d{3}$"),
    "quotation": re.compile(r"^QTE-SYN-\d{3}$"),
    "technical_result": re.compile(r"^TST-SYN-\d{3}$"),
    "risk_event": re.compile(r"^RSK-SYN-\d{3}$"),
    "scenario": re.compile(r"^SCN-SYN-\d{3}$"),
    "invalid_case": re.compile(r"^INV-SYN-\d{3}$"),
}


def validate_identifier(kind: str, value: str) -> None:
    pattern = _PATTERNS.get(kind)
    if pattern is None or not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise SyntheticDataError("INVALID_IDENTIFIER", f"Invalid {kind} identifier: {value!r}.")
