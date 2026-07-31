from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.domain.approved_specification_consumption import (
    AUTHORIZATION_SCHEMA_VERSION,
    CONSUMPTION_CONTRACT_VERSION,
    ApprovedSpecificationConsumptionEnvelope,
    ApprovedSpecificationConsumptionValue,
    AuthorizedConsumptionPurpose,
    ConsumptionAuthorization,
    approved_specification_consumption_envelope_hash,
)
from src.persistence.approved_specification_consumption_migration import (
    APPROVED_SPECIFICATION_CONSUMPTION_SCHEMA_VERSION,
)
from src.persistence.approved_specification_consumption_repository import (
    ApprovedSpecificationConsumptionPersistenceError,
    ApprovedSpecificationConsumptionRepository,
)
from src.persistence.database import Database


class ConsumptionRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.temp.name) / "test.sqlite")
        with self.database.transaction() as connection:
            connection.executescript(
                """
                CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY);
                CREATE TABLE projects(project_id TEXT PRIMARY KEY, archived_at TEXT);
                CREATE TABLE approved_specification_snapshots(
                    snapshot_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    review_id TEXT NOT NULL,
                    source_review_revision_id TEXT NOT NULL,
                    source_review_revision_number INTEGER NOT NULL,
                    existing_dataset_id TEXT NOT NULL,
                    proposed_dataset_id TEXT NOT NULL,
                    snapshot_schema_version TEXT NOT NULL,
                    content_hash TEXT NOT NULL
                );
                """
            )
            connection.execute("INSERT INTO projects VALUES ('p1', NULL)")
            connection.execute("INSERT INTO projects VALUES ('p2', NULL)")
            connection.execute("INSERT INTO projects VALUES ('archived', '2026-01-01')")
            connection.execute(
                "INSERT INTO approved_specification_snapshots VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ('s1', 'p1', 'r1', 'rr1', 1, 'd1', 'd2', '1.0', 'snapshot-hash'),
            )
        self.repository = ApprovedSpecificationConsumptionRepository(self.database)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def envelope(self, **changes) -> ApprovedSpecificationConsumptionEnvelope:
        values = (ApprovedSpecificationConsumptionValue('a', 1, 'unchanged'),)
        data = dict(
            envelope_id='e1', project_id='p1', snapshot_id='s1', review_id='r1',
            source_review_revision_id='rr1', source_review_revision_number=1,
            existing_dataset_id='d1', proposed_dataset_id='d2',
            snapshot_schema_version='1.0', consumption_contract_version=CONSUMPTION_CONTRACT_VERSION,
            approved_values=values, excluded_fields=(), snapshot_content_hash='snapshot-hash',
            created_at='2026-01-01T00:00:00+00:00',
        )
        data.update(changes)
        data['envelope_content_hash'] = approved_specification_consumption_envelope_hash(
            project_id=data['project_id'], snapshot_id=data['snapshot_id'], review_id=data['review_id'],
            source_review_revision_id=data['source_review_revision_id'],
            source_review_revision_number=data['source_review_revision_number'],
            existing_dataset_id=data['existing_dataset_id'], proposed_dataset_id=data['proposed_dataset_id'],
            snapshot_schema_version=data['snapshot_schema_version'], approved_values=data['approved_values'],
            excluded_fields=data['excluded_fields'], snapshot_content_hash=data['snapshot_content_hash'],
            consumption_contract_version=data['consumption_contract_version'],
        )
        return ApprovedSpecificationConsumptionEnvelope(**data)

    def authorization(self, **changes) -> ConsumptionAuthorization:
        data = dict(
            authorization_id='a1', project_id='p1', snapshot_id='s1', envelope_id='e1',
            purpose=AuthorizedConsumptionPurpose.COST_ANALYSIS_INPUT,
            actor_reference='buyer', business_reason='cost review',
            snapshot_content_hash='snapshot-hash',
            envelope_content_hash=self.envelope().envelope_content_hash,
            authorization_schema_version=AUTHORIZATION_SCHEMA_VERSION,
            created_at='2026-01-01T00:01:00+00:00',
        )
        data.update(changes)
        return ConsumptionAuthorization(**data)

    def test_schema_version_and_tables(self) -> None:
        with self.database.connect() as connection:
            self.assertIsNotNone(connection.execute(
                "SELECT 1 FROM schema_migrations WHERE version = ?",
                (APPROVED_SPECIFICATION_CONSUMPTION_SCHEMA_VERSION,),
            ).fetchone())
            names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertIn('approved_specification_consumption_envelopes', names)
        self.assertIn('approved_specification_consumption_authorizations', names)

    def test_create_and_reload_envelope(self) -> None:
        self.assertEqual(self.repository.create_envelope(self.envelope()), self.envelope())

    def test_duplicate_envelope_rejected(self) -> None:
        self.repository.create_envelope(self.envelope())
        with self.assertRaises(ApprovedSpecificationConsumptionPersistenceError):
            self.repository.create_envelope(self.envelope(envelope_id='e2'))

    def test_multiple_purpose_authorizations(self) -> None:
        self.repository.create_envelope(self.envelope())
        self.repository.create_authorization(self.authorization())
        self.repository.create_authorization(self.authorization(
            authorization_id='a2', purpose=AuthorizedConsumptionPurpose.RISK_ANALYSIS_INPUT,
        ))
        self.assertEqual(len(self.repository.list_authorizations_for_snapshot('s1', project_id='p1')), 2)

    def test_duplicate_authorization_rejected(self) -> None:
        self.repository.create_envelope(self.envelope())
        self.repository.create_authorization(self.authorization())
        with self.assertRaises(ApprovedSpecificationConsumptionPersistenceError):
            self.repository.create_authorization(self.authorization(authorization_id='a2'))

    def test_cross_project_envelope_read_rejected(self) -> None:
        self.repository.create_envelope(self.envelope())
        with self.assertRaises(ApprovedSpecificationConsumptionPersistenceError):
            self.repository.get_envelope('e1', project_id='p2')

    def test_cross_project_authorization_read_rejected(self) -> None:
        self.repository.create_envelope(self.envelope())
        self.repository.create_authorization(self.authorization())
        with self.assertRaises(ApprovedSpecificationConsumptionPersistenceError):
            self.repository.get_authorization('a1', project_id='p2')

    def test_archived_project_envelope_creation_rejected(self) -> None:
        with self.database.transaction() as connection:
            connection.execute(
                "INSERT INTO approved_specification_snapshots VALUES ('sa','archived','ra','rra',1,'d1','d2','1.0','h')"
            )
        with self.assertRaisesRegex(ApprovedSpecificationConsumptionPersistenceError, 'read-only'):
            self.repository.create_envelope(self.envelope(
                project_id='archived', snapshot_id='sa', review_id='ra',
                source_review_revision_id='rra', snapshot_content_hash='h',
            ))

    def test_invalid_snapshot_lineage_rejected(self) -> None:
        with self.assertRaises(ApprovedSpecificationConsumptionPersistenceError):
            self.repository.create_envelope(self.envelope(review_id='wrong'))

    def test_authorization_lineage_rejected(self) -> None:
        self.repository.create_envelope(self.envelope())
        with self.assertRaises(ApprovedSpecificationConsumptionPersistenceError):
            self.repository.create_authorization(self.authorization(snapshot_content_hash='wrong'))

    def test_repository_immutability(self) -> None:
        operations = (
            lambda: self.repository.update_envelope('e1'),
            lambda: self.repository.delete_envelope('e1'),
            lambda: self.repository.update_authorization('a1'),
            lambda: self.repository.delete_authorization('a1'),
        )
        for operation in operations:
            with self.subTest(operation=operation):
                with self.assertRaises(ApprovedSpecificationConsumptionPersistenceError):
                    operation()

    def test_database_envelope_triggers(self) -> None:
        self.repository.create_envelope(self.envelope())
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute("UPDATE approved_specification_consumption_envelopes SET review_id='x' WHERE envelope_id='e1'")
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute("DELETE FROM approved_specification_consumption_envelopes WHERE envelope_id='e1'")

    def test_database_authorization_triggers(self) -> None:
        self.repository.create_envelope(self.envelope())
        self.repository.create_authorization(self.authorization())
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute("UPDATE approved_specification_consumption_authorizations SET business_reason='x' WHERE authorization_id='a1'")
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute("DELETE FROM approved_specification_consumption_authorizations WHERE authorization_id='a1'")

    def test_tampered_envelope_detected(self) -> None:
        self.repository.create_envelope(self.envelope())
        with self.database.transaction() as connection:
            connection.execute("DROP TRIGGER consumption_envelopes_immutable_update")
            connection.execute("UPDATE approved_specification_consumption_envelopes SET approved_values_json='[]' WHERE envelope_id='e1'")
        with self.assertRaises(ApprovedSpecificationConsumptionPersistenceError):
            self.repository.get_envelope('e1', project_id='p1')

    def test_project_lists_are_deterministic(self) -> None:
        self.repository.create_envelope(self.envelope())
        self.assertEqual(
            [item.envelope_id for item in self.repository.list_envelopes_for_project('p1')],
            ['e1'],
        )

    def test_get_envelope_for_snapshot(self) -> None:
        self.repository.create_envelope(self.envelope())
        envelope = self.repository.get_envelope_for_snapshot(
            's1', project_id='p1', consumption_contract_version='1.0',
        )
        self.assertIsNotNone(envelope)
        self.assertEqual(envelope.envelope_id, 'e1')


if __name__ == '__main__':
    unittest.main()
