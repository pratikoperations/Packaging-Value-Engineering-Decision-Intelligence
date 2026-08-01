from __future__ import annotations

from typing import Any


CALCULATION_EVIDENCE_DISCLOSURE = (
    "Independent arithmetic reconciliation over synthetic demonstration data. "
    "A match is not supplier, engineering, regulatory, production or realized-savings validation."
)


def attach_calculation_evidence(package: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(package, dict):
        raise ValueError("Decision package must be an object.")
    if not isinstance(evidence, dict) or not isinstance(evidence.get("results"), list):
        raise ValueError("Calculation evidence must contain a results list.")
    package["calculation_evidence"] = {
        "registry_version": evidence.get("registry_version"),
        "catalogue_count": evidence.get("catalogue_count"),
        "summary": evidence.get("summary", {}),
        "rule_lineage": evidence.get("rule_lineage", {}),
        "assumptions": evidence.get("assumptions", {}),
        "results": evidence["results"],
        "disclosure": CALCULATION_EVIDENCE_DISCLOSURE,
    }
    return package


def render_calculation_evidence_markdown(evidence: dict[str, Any]) -> str:
    summary = evidence.get("summary", {})
    lines = [
        "## Independent Calculation Evidence",
        "",
        CALCULATION_EVIDENCE_DISCLOSURE,
        "",
        f"- Formula registry version: {evidence.get('registry_version', 'unknown')}",
        f"- Numeric formula count: {evidence.get('catalogue_count', 0)}",
        f"- Matched: {summary.get('matched', 0)}",
        f"- Matched within tolerance: {summary.get('matched_within_tolerance', 0)}",
        f"- Mismatch: {summary.get('mismatch', 0)}",
        f"- Insufficient evidence: {summary.get('insufficient_evidence', 0)}",
        f"- Unsupported: {summary.get('unsupported', 0)}",
        "",
        "### Reconciliation Results",
        "",
    ]
    for result in evidence.get("results", []):
        lines.extend(
            [
                f"- `{result['calculation_id']}` / `{result['alternative_id']}`: **{result['state']}**",
                f"  - Primary: {result.get('primary_result')} {result.get('unit', '')}".rstrip(),
                f"  - Independent: {result.get('independent_result')} {result.get('unit', '')}".rstrip(),
                f"  - Absolute variance: {result.get('absolute_variance')}",
                f"  - Tolerance policy: {result.get('tolerance_policy_id')}",
            ]
        )
        if result.get("issue_code"):
            lines.append(f"  - Issue: {result['issue_code']} — {result.get('issue_message', '')}")
    lines.extend(
        [
            "",
            "### Rule Lineage",
            "",
        ]
    )
    for rule_id, name in sorted(evidence.get("rule_lineage", {}).items()):
        lines.append(f"- `{rule_id}` — {name}")
    return "\n".join(lines) + "\n"
