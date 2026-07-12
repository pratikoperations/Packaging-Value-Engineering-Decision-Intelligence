from __future__ import annotations

import json
from typing import Any

from src.uploads.models import UploadParseError

MAX_UPLOAD_BYTES = 2 * 1024 * 1024


def parse_json_upload(content: bytes) -> dict[str, Any]:
    if not content:
        raise UploadParseError("The uploaded JSON file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise UploadParseError("The uploaded JSON file exceeds the 2 MB limit.")
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise UploadParseError("The JSON file must use UTF-8 encoding.") from error
    try:
        parsed = json.loads(decoded)
    except json.JSONDecodeError as error:
        raise UploadParseError(
            f"Invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}."
        ) from error
    if not isinstance(parsed, dict):
        raise UploadParseError("The JSON root must be an object.")
    return parsed
