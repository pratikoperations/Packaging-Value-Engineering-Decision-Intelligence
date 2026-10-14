"""Explicit portable backup for unfinished, synthetic PVE specification drafts.

This does not provide server-side durable storage or prove evidence authenticity.
"""
from __future__ import annotations

import base64
import hashlib
import json

from src.application.specification_upload import SessionSpecificationFile
from src.persistence._utils import canonical_json

MAX_BACKUP_BYTES = 30 * 1024 * 1024
BACKUP_VERSION = 1


def _attachment(name: str, mime: str, data: bytes) -> dict:
    return {
        "filename": name,
        "mime_type": mime,
        "sha256": hashlib.sha256(data).hexdigest(),
        "base64": base64.b64encode(data).decode("ascii"),
    }


def export_specification_draft(project_code: str, draft) -> bytes:
    """Export a self-contained draft for manual download and later re-import."""
    payload = {
        "schema_version": BACKUP_VERSION,
        "project_code": project_code,
        "existing": _attachment(draft.existing_name, draft.existing_mime, draft.existing_content),
        "proposed": _attachment(draft.proposed_name, draft.proposed_mime, draft.proposed_content),
        "reviews": list(draft.reviews),
    }
    payload["bundle_sha256"] = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    result = canonical_json(payload).encode("utf-8")
    if len(result) > MAX_BACKUP_BYTES:
        raise ValueError("Draft backup exceeds maximum portable size.")
    return result


def import_specification_draft(repository, *, project_id: str, project_code: str, content: bytes):
    """Restore only to a project with the exact same project code.

    Hashes detect accidental corruption, not malicious modification. Re-review
    source evidence and engineering requirements after importing a backup.
    """
    if not 0 < len(content) <= MAX_BACKUP_BYTES:
        raise ValueError("Invalid draft backup size.")
    try:
        payload = json.loads(content)
    except (ValueError, UnicodeDecodeError) as error:
        raise ValueError("Invalid draft backup JSON.") from error
    if not isinstance(payload, dict) or payload.get("schema_version") != BACKUP_VERSION:
        raise ValueError("Unsupported draft backup schema.")
    if not project_code or payload.get("project_code") != project_code:
        raise ValueError("Draft backup belongs to a different project code.")
    claimed_hash = payload.pop("bundle_sha256", None)
    actual_hash = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    if claimed_hash != actual_hash:
        raise ValueError("Draft backup checksum mismatch.")

    def recover(role: str) -> SessionSpecificationFile:
        source = payload.get(role)
        if not isinstance(source, dict):
            raise ValueError("Missing backup document.")
        filename = source.get("filename")
        mime = source.get("mime_type")
        if not isinstance(filename, str) or not isinstance(mime, str):
            raise ValueError("Invalid backup document metadata.")
        try:
            data = base64.b64decode(source["base64"], validate=True)
        except (KeyError, ValueError) as error:
            raise ValueError("Invalid document encoding.") from error
        if hashlib.sha256(data).hexdigest() != source.get("sha256"):
            raise ValueError("Backup document checksum mismatch.")
        return SessionSpecificationFile(filename, mime, data)

    existing, proposed = recover("existing"), recover("proposed")
    reviews = payload.get("reviews")
    if not isinstance(reviews, list):
        raise ValueError("Invalid backup review collection.")
    return repository.save(project_id, existing, proposed, reviews)
