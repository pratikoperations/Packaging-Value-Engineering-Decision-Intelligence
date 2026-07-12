from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def row_to_dict(row: Any) -> dict[str, Any] | None:
    return dict(row) if row is not None else None
