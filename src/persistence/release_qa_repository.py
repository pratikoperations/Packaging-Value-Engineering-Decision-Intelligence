from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from src.persistence._utils import new_id
from src.persistence.database import Database
from src.release_qa import validate_demonstration_case, validate_release_qa_assessment


class DemonstrationCaseRepository:
    """Immutable Build 8 demonstration-case manifests."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        case_code: str,
        title: str,
        purpose: str,
        data_classification: str,
        covered_builds: Sequence[Any],
        expected_outcomes: Sequence[str],
        acceptance_checks: Sequence[str],
        status: str,
        evidence_references: Sequence[str],
        content_hash: str,
        limitations: Sequence[str] = (),
        exceptions: Sequence[str] = (),
        **prohibited_fields: Any,
    ) -> dict[str, Any]:
        payload = {
            "case_id": case_code,
            "title": title,
            "purpose": purpose,
            "data_classification": data_classification,
            "covered_builds": list(covered_builds),
            "expected_outcomes": list(expected_outcomes),
            "acceptance_checks": list(acceptance_checks),
            "status": status,
            "evidence_references": list(evidence_references),
            **prohibited_fields,
        }
        validation = validate_demonstration_case(payload)
        if not validation.is_valid:
            raise ValueError("; ".join(f"{i.field}: {i.message}" for i in validation.issues))
        identifier = new_id("demonstration-case")
        with self.database.transaction() as connection:
            connection.execute(
                """INSERT INTO demonstration_cases(
                    demonstration_case_id, case_code, title, purpose, data_classification,
                    covered_builds_json, expected_outcomes_json, acceptance_checks_json,
                    status, evidence_references_json, limitations_json, exceptions_json, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    identifier, case_code, title, purpose, data_classification,
                    json.dumps(list(covered_builds), sort_keys=True),
                    json.dumps(list(expected_outcomes), sort_keys=True),
                    json.dumps(list(acceptance_checks), sort_keys=True),
                    status, json.dumps(list(evidence_references), sort_keys=True),
                    json.dumps(list(limitations), sort_keys=True),
                    json.dumps(list(exceptions), sort_keys=True), content_hash.lower(),
                ),
            )
        return self.get(identifier)

    def get(self, identifier: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM demonstration_cases WHERE demonstration_case_id = ?", (identifier,)
            ).fetchone()
        if row is None:
            raise KeyError(identifier)
        result = dict(row)
        for column, key in (
            ("covered_builds_json", "covered_builds"),
            ("expected_outcomes_json", "expected_outcomes"),
            ("acceptance_checks_json", "acceptance_checks"),
            ("evidence_references_json", "evidence_references"),
            ("limitations_json", "limitations"),
            ("exceptions_json", "exceptions"),
        ):
            result[key] = json.loads(result.pop(column))
        return result

    def list_all(self) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT demonstration_case_id FROM demonstration_cases ORDER BY created_at, demonstration_case_id"
            ).fetchall()
        return [self.get(row[0]) for row in rows]

    def update(self, *_: Any, **__: Any) -> None:
        raise ValueError("Demonstration cases are immutable; create a new manifest.")

    def delete(self, *_: Any, **__: Any) -> None:
        raise ValueError("Demonstration cases are immutable.")


class ReleaseQAAssessmentRepository:
    """Immutable release-QA evidence; never performs release actions."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        assessment_code: str,
        tested_commit: str,
        workflow_run_id: str,
        job_id: str,
        test_count: int,
        failure_count: int,
        error_count: int,
        artifact_id: str,
        artifact_digest: str,
        schema_version: int,
        demonstration_case_ids: Sequence[str],
        reviewed_by: str,
        reviewed_at: str,
        recommendation: str,
        recommendation_rationale: str,
        evidence_references: Sequence[str],
        content_hash: str,
        unresolved_defects: Sequence[str] = (),
        limitations: Sequence[str] = (),
        exceptions: Sequence[str] = (),
        unresolved_blockers: Sequence[str] = (),
        **prohibited_fields: Any,
    ) -> dict[str, Any]:
        payload = {
            "assessment_id": assessment_code,
            "tested_commit": tested_commit,
            "workflow_run_id": workflow_run_id,
            "job_id": job_id,
            "test_count": test_count,
            "failure_count": failure_count,
            "error_count": error_count,
            "artifact_id": artifact_id,
            "artifact_digest": artifact_digest,
            "schema_version": schema_version,
            "demonstration_case_ids": list(demonstration_case_ids),
            "unresolved_blockers": list(unresolved_blockers),
            "reviewed_by": reviewed_by,
            "recommendation": recommendation,
            "evidence_references": list(evidence_references),
            **prohibited_fields,
        }
        validation = validate_release_qa_assessment(payload)
        if not validation.is_valid:
            raise ValueError("; ".join(f"{i.field}: {i.message}" for i in validation.issues))
        if not artifact_digest.startswith("sha256:"):
            raise ValueError("artifact_digest must use sha256.")
        identifier = new_id("release-qa")
        with self.database.transaction() as connection:
            for case_id in demonstration_case_ids:
                row = connection.execute(
                    "SELECT demonstration_case_id FROM demonstration_cases WHERE demonstration_case_id = ?", (case_id,)
                ).fetchone()
                if row is None:
                    raise KeyError(case_id)
            connection.execute(
                """INSERT INTO release_qa_assessments(
                    release_qa_assessment_id, assessment_code, tested_commit, workflow_run_id,
                    job_id, test_count, failure_count, error_count, schema_version, artifact_id,
                    artifact_digest, demonstration_case_ids_json, unresolved_defects_json,
                    limitations_json, exceptions_json, unresolved_blockers_json, reviewed_by,
                    reviewed_at, recommendation, recommendation_rationale,
                    evidence_references_json, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    identifier, assessment_code, tested_commit, workflow_run_id, job_id,
                    test_count, failure_count, error_count, schema_version, artifact_id,
                    artifact_digest, json.dumps(list(demonstration_case_ids), sort_keys=True),
                    json.dumps(list(unresolved_defects), sort_keys=True),
                    json.dumps(list(limitations), sort_keys=True),
                    json.dumps(list(exceptions), sort_keys=True),
                    json.dumps(list(unresolved_blockers), sort_keys=True), reviewed_by,
                    reviewed_at, recommendation, recommendation_rationale,
                    json.dumps(list(evidence_references), sort_keys=True), content_hash.lower(),
                ),
            )
        return self.get(identifier)

    def get(self, identifier: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM release_qa_assessments WHERE release_qa_assessment_id = ?", (identifier,)
            ).fetchone()
        if row is None:
            raise KeyError(identifier)
        result = dict(row)
        for column, key in (
            ("demonstration_case_ids_json", "demonstration_case_ids"),
            ("unresolved_defects_json", "unresolved_defects"),
            ("limitations_json", "limitations"),
            ("exceptions_json", "exceptions"),
            ("unresolved_blockers_json", "unresolved_blockers"),
            ("evidence_references_json", "evidence_references"),
        ):
            result[key] = json.loads(result.pop(column))
        return result

    def list_all(self) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT release_qa_assessment_id FROM release_qa_assessments ORDER BY created_at, release_qa_assessment_id"
            ).fetchall()
        return [self.get(row[0]) for row in rows]

    def update(self, *_: Any, **__: Any) -> None:
        raise ValueError("Release-QA assessments are immutable; create a new assessment.")

    def delete(self, *_: Any, **__: Any) -> None:
        raise ValueError("Release-QA assessments are immutable.")
