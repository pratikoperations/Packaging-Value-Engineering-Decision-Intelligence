from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping, MutableMapping, Sequence

from src.upload_routing import DetectedUpload, DetectionStatus, FileFormat, WorkflowKind
from src.uploads import UploadParseError

STRUCTURED_STATE_PREFIX = "data_upload.structured."
STRUCTURED_FINGERPRINT_KEY = f"{STRUCTURED_STATE_PREFIX}fingerprint"
STRUCTURED_CONFIRMATION_KEY = f"{STRUCTURED_STATE_PREFIX}confirmed"
STRUCTURED_RESULT_KEY = f"{STRUCTURED_STATE_PREFIX}prepared"


@dataclass(frozen=True)
class StructuredUploadFile:
    filename: str
    content: bytes
    detection: DetectedUpload


def structured_batch_fingerprint(files: Sequence[StructuredUploadFile]) -> str:
    payload = "|".join(sorted(f"{item.detection.sha256}:{item.filename}" for item in files))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def invalidate_structured_state_on_change(
    session_state: MutableMapping[str, object],
    files: Sequence[StructuredUploadFile],
) -> bool:
    fingerprint = structured_batch_fingerprint(files)
    previous = session_state.get(STRUCTURED_FINGERPRINT_KEY)
    if previous == fingerprint:
        return False
    for key in list(session_state):
        if key.startswith(STRUCTURED_STATE_PREFIX):
            session_state.pop(key, None)
    session_state[STRUCTURED_FINGERPRINT_KEY] = fingerprint
    return True


def validate_structured_batch(files: Sequence[StructuredUploadFile]) -> FileFormat:
    if not files:
        raise UploadParseError("No structured project-data files were supplied.")
    for item in files:
        if item.detection.status is DetectionStatus.REJECTED:
            raise UploadParseError(f"{item.filename}: {item.detection.detail or item.detection.reason_code}")
        if item.detection.workflow is not WorkflowKind.STRUCTURED_PROJECT_DATA:
            raise UploadParseError("The structured route accepts XLSX, CSV or JSON project-data files only.")
    formats = {item.detection.file_format for item in files}
    if len(formats) != 1:
        raise UploadParseError("Process one structured file format at a time.")
    file_format = next(iter(formats))
    if file_format in {FileFormat.XLSX, FileFormat.JSON} and len(files) != 1:
        raise UploadParseError(f"Upload exactly one {file_format.value.upper()} file.")
    if file_format is FileFormat.CSV:
        names = {item.filename.lower() for item in files}
        if names != {"project.csv", "alternatives.csv"}:
            raise UploadParseError("CSV intake requires exactly project.csv and alternatives.csv.")
    assert file_format is not None
    return file_format


def prepare_structured_upload(upload_service, project: Mapping[str, object], files: Sequence[StructuredUploadFile]):
    file_format = validate_structured_batch(files)
    if file_format is FileFormat.XLSX:
        item = files[0]
        return upload_service.prepare_excel(content=item.content, filename=item.filename, project=project)
    if file_format is FileFormat.JSON:
        item = files[0]
        return upload_service.prepare_json(content=item.content, filename=item.filename, project=project)
    if file_format is FileFormat.CSV:
        return upload_service.prepare_csv(files={item.filename: item.content for item in files}, project=project)
    raise UploadParseError("Unsupported structured project-data format.")
