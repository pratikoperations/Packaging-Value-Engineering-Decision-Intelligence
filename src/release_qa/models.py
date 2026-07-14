from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

_PROHIBITED_RELEASE_ACTIONS = {
    "create_release_tag",
    "publish_github_release",
    "deployment_authorization",
    "production_readiness_approval",
    "autonomous_release_approval",
    "declare_release_complete",
    "supplier_rank",
    "sourcing_award_status",
    "sourcing_allocation_percent",
    "commercial_terms_approval",
}
_ALLOWED_CASE_STATUSES = {"draft", "ready", "executed", "passed", "failed", "blocked"}
_ALLOWED_RECOMMENDATIONS = {"not_ready", "ready_for_release_authorization", "blocked"}


@dataclass(frozen=True)
class ReleaseQAIssue:
    code: str
    field: str
    message: str


@dataclass(frozen=True)
class ReleaseQAValidation:
    issues: tuple[ReleaseQAIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues


def _issue(issues: list[ReleaseQAIssue], code: str, field: str, message: str) -> None:
    issues.append(ReleaseQAIssue(code, field, message))


def _required(payload: Mapping[str, Any], field: str, issues: list[ReleaseQAIssue]) -> None:
    if payload.get(field) in (None, "", [], {}):
        _issue(issues, "missing_required", field, "Required field is missing or empty.")


def _sequence(payload: Mapping[str, Any], field: str, issues: list[ReleaseQAIssue]) -> None:
    value = payload.get(field)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        _issue(issues, "invalid_type", field, f"{field} must be a sequence.")


def _reject_release_actions(payload: Mapping[str, Any], issues: list[ReleaseQAIssue]) -> None:
    for field in _PROHIBITED_RELEASE_ACTIONS.intersection(payload):
        if payload.get(field) not in (None, "", False, [], {}):
            _issue(
                issues,
                "release_action_prohibited",
                field,
                "Build 8 may record QA evidence but cannot perform release, deployment, sourcing or commercial decisions.",
            )


def validate_demonstration_case(payload: Mapping[str, Any]) -> ReleaseQAValidation:
    issues: list[ReleaseQAIssue] = []
    for field in (
        "case_id",
        "title",
        "purpose",
        "data_classification",
        "covered_builds",
        "expected_outcomes",
        "acceptance_checks",
        "status",
        "evidence_references",
    ):
        _required(payload, field, issues)
    for field in ("covered_builds", "expected_outcomes", "acceptance_checks", "evidence_references"):
        _sequence(payload, field, issues)
    if payload.get("status") not in _ALLOWED_CASE_STATUSES:
        _issue(issues, "invalid_enum", "status", "Unsupported demonstration-case status.")
    if payload.get("data_classification") not in {"synthetic", "anonymized", "real_controlled"}:
        _issue(issues, "invalid_enum", "data_classification", "Unsupported data classification.")
    _reject_release_actions(payload, issues)
    return ReleaseQAValidation(tuple(issues))


def validate_release_qa_assessment(payload: Mapping[str, Any]) -> ReleaseQAValidation:
    issues: list[ReleaseQAIssue] = []
    for field in (
        "assessment_id",
        "tested_commit",
        "workflow_run_id",
        "job_id",
        "test_count",
        "failure_count",
        "error_count",
        "artifact_id",
        "artifact_digest",
        "schema_version",
        "demonstration_case_ids",
        "unresolved_blockers",
        "reviewed_by",
        "recommendation",
        "evidence_references",
    ):
        _required(payload, field, issues)
    for field in ("demonstration_case_ids", "unresolved_blockers", "evidence_references"):
        _sequence(payload, field, issues)
    if payload.get("recommendation") not in _ALLOWED_RECOMMENDATIONS:
        _issue(issues, "invalid_enum", "recommendation", "Unsupported release-QA recommendation.")
    try:
        tests = int(payload.get("test_count", -1))
        failures = int(payload.get("failure_count", -1))
        errors = int(payload.get("error_count", -1))
        if tests <= 0 or failures < 0 or errors < 0:
            raise ValueError
        if payload.get("recommendation") == "ready_for_release_authorization":
            if failures or errors:
                _issue(issues, "tests_not_clean", "recommendation", "Ready recommendation requires zero failures and errors.")
            if payload.get("unresolved_blockers"):
                _issue(issues, "blockers_present", "unresolved_blockers", "Ready recommendation cannot contain unresolved blockers.")
    except (TypeError, ValueError):
        _issue(issues, "invalid_test_counts", "test_count", "Test counts must be valid non-negative integers and test_count must be positive.")
    _reject_release_actions(payload, issues)
    return ReleaseQAValidation(tuple(issues))
