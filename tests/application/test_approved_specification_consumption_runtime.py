from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.application.approved_specification_consumption_read_model import (
    ApprovedSpecificationConsumptionReadModel,
)
from src.application.approved_specification_consumption_service import (
    ApprovedSpecificationConsumptionError,
    ApprovedSpecificationConsumptionService,
)
from src.application.approved_specification_read_model import ApprovedSpecificationReadModel
from src.application.runtime import (
    build_approved_specification_consumption_read_model,
    build_approved_specification_consumption_repository,
    build_approved_specification_consumption_service,
)
from src.persistence.approved_specification_consumption_migration import (
    APPROVED_SPECIFICATION_CONSUMPTION_SCHEMA_VERSION,
)
from src.persistence.approved_specification_consumption_repository import (
    ApprovedSpecificationConsumptionRepository,
)


class ApprovedSpecificationConsumptionRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp.name) / "runtime.sqlite"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_repository_builder_initializes_schema_version_12(self) -> None:
        repository = build_approved_specification_consumption_repository(
            self.database_path
        )
        self.assertIsInstance(
            repository, ApprovedSpecificationConsumptionRepository
        )
        with repository.database.connect() as connection:
            migration = connection.execute(
                "SELECT 1 FROM schema_migrations WHERE version = ?",
                (APPROVED_SPECIFICATION_CONSUMPTION_SCHEMA_VERSION,),
            ).fetchone()
            envelope_table = connection.execute(
                "SELECT 1 FROM sqlite_master "
                "WHERE type = 'table' "
                "AND name = 'approved_specification_consumption_envelopes'"
            ).fetchone()
            authorization_table = connection.execute(
                "SELECT 1 FROM sqlite_master "
                "WHERE type = 'table' "
                "AND name = 'approved_specification_consumption_authorizations'"
            ).fetchone()
        self.assertIsNotNone(migration)
        self.assertIsNotNone(envelope_table)
        self.assertIsNotNone(authorization_table)

    def test_service_builder_composes_one_database_and_e1_6_read_boundary(self) -> None:
        service = build_approved_specification_consumption_service(
            self.database_path
        )
        self.assertIsInstance(service, ApprovedSpecificationConsumptionService)
        self.assertIsInstance(
            service.snapshot_read_model, ApprovedSpecificationReadModel
        )
        self.assertEqual(
            service.snapshot_read_model.repository.database.path,
            service.repository.database.path,
        )
        self.assertFalse(hasattr(service, "dataset_repository"))
        self.assertFalse(hasattr(service, "review_repository"))

    def test_read_model_builder_uses_consumption_repository(self) -> None:
        read_model = build_approved_specification_consumption_read_model(
            self.database_path
        )
        self.assertIsInstance(
            read_model, ApprovedSpecificationConsumptionReadModel
        )
        self.assertIsInstance(
            read_model.repository, ApprovedSpecificationConsumptionRepository
        )

    def test_read_model_preserves_project_scope(self) -> None:
        read_model = build_approved_specification_consumption_read_model(
            self.database_path
        )
        with self.assertRaises(ApprovedSpecificationConsumptionError) as captured:
            read_model.list_envelopes_for_project("")
        self.assertEqual(captured.exception.code, "project_required")


if __name__ == "__main__":
    unittest.main()
