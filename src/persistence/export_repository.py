from __future__ import annotations

from src.persistence._utils import new_id
from src.persistence.database import Database


class ExportRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        decision_snapshot_id: str,
        export_type: str,
        filename: str,
        content_hash: str,
    ) -> dict:
        identifier = new_id("export")
        with self.database.transaction() as connection:
            connection.execute(
                """
                INSERT INTO export_records(
                    export_id, decision_snapshot_id, export_type, filename, content_hash
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (identifier, decision_snapshot_id, export_type, filename, content_hash),
            )
        return self.get(identifier)

    def get(self, export_id: str) -> dict:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM export_records WHERE export_id = ?", (export_id,)
            ).fetchone()
        if row is None:
            raise KeyError(export_id)
        return dict(row)
