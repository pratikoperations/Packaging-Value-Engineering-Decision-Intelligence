from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from src.persistence.database import Database
from src.persistence._utils import canonical_json, new_id

MAX_DOCUMENT_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class SpecificationDraft:
    draft_id: str
    project_id: str
    existing_name: str
    existing_mime: str
    existing_content: bytes
    proposed_name: str
    proposed_mime: str
    proposed_content: bytes
    reviews: tuple[dict, ...]
    created_at: str


class SpecificationDraftRepository:
    """Append-only, project-scoped unfinished intake records.

    Each Save creates a new revision. Documents are stored as binary evidence,
    with checksum validation on retrieval. These records are not approvals.
    """

    def __init__(self, database: Database):
        self.database = database
        with database.transaction() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS specification_intake_drafts (
                    draft_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    existing_name TEXT NOT NULL,
                    existing_mime TEXT NOT NULL,
                    existing_content BLOB NOT NULL,
                    existing_sha256 TEXT NOT NULL,
                    proposed_name TEXT NOT NULL,
                    proposed_mime TEXT NOT NULL,
                    proposed_content BLOB NOT NULL,
                    proposed_sha256 TEXT NOT NULL,
                    reviews_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE RESTRICT
                );
                CREATE INDEX IF NOT EXISTS idx_specification_intake_drafts_project
                ON specification_intake_drafts(project_id, created_at, draft_id);
                CREATE TRIGGER IF NOT EXISTS specification_intake_drafts_no_update
                BEFORE UPDATE ON specification_intake_drafts
                BEGIN SELECT RAISE(ABORT, 'specification drafts are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS specification_intake_drafts_no_delete
                BEFORE DELETE ON specification_intake_drafts
                BEGIN SELECT RAISE(ABORT, 'specification drafts are immutable'); END;
            """)

    def save(self, project_id: str, existing, proposed, reviews) -> SpecificationDraft:
        files = (existing, proposed)
        for item in files:
            if not item.name.lower().endswith((".pdf", ".docx")):
                raise ValueError("Only PDF and DOCX draft documents are accepted.")
            if not 0 < len(item.getvalue()) <= MAX_DOCUMENT_BYTES:
                raise ValueError("Specification draft file must be 1 byte to 10 MiB.")
        records = tuple(reviews)
        if len(records) > 100:
            raise ValueError("Too many specification review entries.")
        for record in records:
            if not isinstance(record, dict) or not isinstance(record.get("review_id"), str):
                raise ValueError("Invalid specification draft review entry.")
        draft_id = new_id("spec-draft")
        with self.database.transaction() as connection:
            project = connection.execute(
                "SELECT archived_at FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            if project is None:
                raise KeyError(project_id)
            if project["archived_at"] is not None:
                raise ValueError("Archived projects are read-only.")
            connection.execute(
                """INSERT INTO specification_intake_drafts(
                    draft_id, project_id, existing_name, existing_mime,
                    existing_content, existing_sha256, proposed_name,
                    proposed_mime, proposed_content, proposed_sha256, reviews_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (draft_id, project_id, existing.name, existing.type, existing.getvalue(),
                 hashlib.sha256(existing.getvalue()).hexdigest(), proposed.name,
                 proposed.type, proposed.getvalue(),
                 hashlib.sha256(proposed.getvalue()).hexdigest(), canonical_json(records)),
            )
        return self.get(draft_id, project_id=project_id)

    def get(self, draft_id: str, *, project_id: str) -> SpecificationDraft:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM specification_intake_drafts WHERE draft_id = ? AND project_id = ?",
                (draft_id, project_id),
            ).fetchone()
        if row is None:
            raise KeyError("Draft not found in the active project.")
        for role in ("existing", "proposed"):
            if hashlib.sha256(row[f"{role}_content"]).hexdigest() != row[f"{role}_sha256"]:
                raise ValueError("Stored specification draft checksum mismatch.")
        return SpecificationDraft(
            draft_id=row["draft_id"], project_id=row["project_id"],
            existing_name=row["existing_name"], existing_mime=row["existing_mime"],
            existing_content=row["existing_content"], proposed_name=row["proposed_name"],
            proposed_mime=row["proposed_mime"], proposed_content=row["proposed_content"],
            reviews=tuple(json.loads(row["reviews_json"])), created_at=row["created_at"],
        )

    def list_for_project(self, project_id: str) -> list[dict]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """SELECT draft_id, existing_name, proposed_name, created_at
                   FROM specification_intake_drafts WHERE project_id = ?
                   ORDER BY created_at DESC, rowid DESC""", (project_id,)
            ).fetchall()
        return [dict(row) for row in rows]
