from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from src.exports import assemble_decision_package
from src.recommendation import recommend_alternatives
from src.risk_engine import evaluate_risks
from src.scenario_engine import ScenarioInputs, evaluate_scenario
from src.synthetic_data import build_legacy_dataset, load_governed_package
from src.technical_qualification import evaluate_technical_qualification

REQUIRED_FILES = (
    "project_summary.csv",
    "scenario_summary.csv",
    "alternative_summary.csv",
    "scenario_results.csv",
    "technical_qualification.csv",
    "risk_indicators.csv",
    "recommendations.csv",
    "assumptions.csv",
    "data_dictionary.csv",
    "export_manifest.json",
)
PRIMARY_KEYS = {
    "project_summary.csv": "project_id",
    "scenario_summary.csv": "scenario_id",
    "alternative_summary.csv": "alternative_key",
    "scenario_results.csv": "scenario_result_id",
    "technical_qualification.csv": "scenario_qualification_id",
    "risk_indicators.csv": "scenario_risk_indicator_id",
    "recommendations.csv": "scenario_recommendation_id",
    "assumptions.csv": "assumption_record_id",
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise AssertionError(f"Missing CSV header: {path.name}")
        return list(reader)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_unique(rows: list[dict[str, str]], key: str, table: str) -> None:
    values = [row.get(key, "") for row in rows]
    if any(not value for value in values):
        raise AssertionError(f"Blank mandatory primary key {key} in {table}")
    if len(values) != len(set(values)):
        raise AssertionError(f"Duplicate primary key {key} in {table}")


def _assert_subset(values: set[str], parents: set[str], label: str) -> None:
    missing = sorted(values - parents)
    if missing:
        raise AssertionError(f"Foreign-key failure for {label}: {missing}")


def _run_generator(root: Path, scenario_id: str, source_commit: str, output: Path) -> list[str]:
    command = [
        sys.executable,
        "tools/generate_portfolio_export.py",
        "--scenario-id",
        scenario_id,
        "--source-commit",
        source_commit,
        "--generated-at",
        "2026-08-01T12:00:00Z",
        "--output",
        str(output.relative_to(root)),
    ]
    subprocess.run(command, cwd=root, check=True)
    return command


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=root, text=True
    ).strip()

    governed = load_governed_package(root / "data" / "demo" / "governed_synthetic")
    scenarios = sorted(governed["scenarios"], key=lambda item: item["scenario_id"])
    if not scenarios:
        raise AssertionError("No governed scenarios found")
    selected = scenarios[0]
    scenario_id = selected["scenario_id"]
    scenario_title = selected["title"]

    work_root = root / "validation-output" / "gate4"
    export_a = work_root / "export-a"
    export_b = work_root / "export-b"
    shutil.rmtree(work_root, ignore_errors=True)
    export_a.mkdir(parents=True)
    export_b.mkdir(parents=True)

    command_a = _run_generator(root, scenario_id, source_commit, export_a)
    command_b = _run_generator(root, scenario_id, source_commit, export_b)

    actual_a = tuple(sorted(path.name for path in export_a.iterdir() if path.is_file()))
    actual_b = tuple(sorted(path.name for path in export_b.iterdir() if path.is_file()))
    expected = tuple(sorted(REQUIRED_FILES))
    if actual_a != expected or actual_b != expected:
        raise AssertionError(f"Unexpected artifact set: {actual_a} / {actual_b}")

    csv_rows = {name: _read_csv(export_a / name) for name in REQUIRED_FILES if name.endswith(".csv")}
    for table, key in PRIMARY_KEYS.items():
        _assert_unique(csv_rows[table], key, table)

    project_ids = {row["project_id"] for row in csv_rows["project_summary.csv"]}
    scenario_ids = {row["scenario_id"] for row in csv_rows["scenario_summary.csv"]}
    alternative_keys = {row["alternative_key"] for row in csv_rows["alternative_summary.csv"]}
    for table, rows in csv_rows.items():
        if table == "data_dictionary.csv":
            continue
        if rows and "project_id" in rows[0]:
            _assert_subset({row["project_id"] for row in rows}, project_ids, f"{table}.project_id")
        if rows and "scenario_id" in rows[0]:
            _assert_subset({row["scenario_id"] for row in rows}, scenario_ids, f"{table}.scenario_id")
        if rows and "alternative_key" in rows[0]:
            _assert_subset(
                {row["alternative_key"] for row in rows if row.get("alternative_key")},
                alternative_keys,
                f"{table}.alternative_key",
            )

    manifest = json.loads((export_a / "export_manifest.json").read_text(encoding="utf-8"))
    if manifest["source_commit"] != source_commit:
        raise AssertionError("Manifest source commit mismatch")
    if manifest["dataset_type"] != "synthetic_demo":
        raise AssertionError("Manifest dataset classification mismatch")
    if manifest["confidentiality_class"] != "portfolio_synthetic":
        raise AssertionError("Manifest confidentiality classification mismatch")
    controls = manifest["controls"]
    expected_controls = {
        "read_only": True,
        "synthetic_data_only": True,
        "formulas_recalculated_by_exporter": False,
        "autonomous_technical_approval": False,
        "supplier_allocation": False,
        "production_release": False,
    }
    if controls != expected_controls:
        raise AssertionError(f"Manifest controls mismatch: {controls}")

    manifest_hashes: dict[str, str] = {}
    row_counts: dict[str, int] = {}
    manifest_names = set()
    for item in manifest["files"]:
        name = item["file_name"]
        manifest_names.add(name)
        physical_hash = _sha256(export_a / name)
        if physical_hash != item["sha256"]:
            raise AssertionError(f"Manifest hash mismatch: {name}")
        physical_rows = len(csv_rows[name])
        if physical_rows != item["row_count"]:
            raise AssertionError(f"Manifest row-count mismatch: {name}")
        manifest_hashes[name] = physical_hash
        row_counts[name] = physical_rows
    if manifest_names != {name for name in REQUIRED_FILES if name.endswith(".csv")}:
        raise AssertionError("Manifest file inventory mismatch")

    dataset = build_legacy_dataset(governed, scenario_id)
    alternatives = dataset["packaging_alternatives"]
    zero_cost = {item["alternative_id"]: 0.0 for item in alternatives}
    zero_material = {item["alternative_id"]: 0.0 for item in alternatives}
    scenario = evaluate_scenario(
        dataset,
        ScenarioInputs(
            annual_volume=float(dataset["packaging_project"]["annual_volume"]),
            cost_adjustment_percent_by_alternative=zero_cost,
            material_adjustment_percent_by_alternative=zero_material,
        ),
    )
    qualifications = evaluate_technical_qualification(dataset)
    risks = evaluate_risks(dataset)
    recommendation = recommend_alternatives(dataset, scenario, qualifications, risks)
    package = assemble_decision_package(
        dataset,
        scenario,
        qualifications,
        risks,
        recommendation,
        source_commit=source_commit,
        generated_at="2026-08-01T12:00:00Z",
    )

    exported_results = {row["alternative_id"]: row for row in csv_rows["scenario_results.csv"]}
    for alternative in [package["baseline"], *package["alternatives"]]:
        row = exported_results[alternative["alternative_id"]]
        values = alternative["cost_and_material"]
        checks = {
            "unit_cost": values["unit_cost"],
            "annual_cost": values["annual_cost"],
            "annual_savings_vs_baseline": values["annual_savings_vs_baseline"],
            "case_weight_g": values["case_weight_g"],
            "annual_material_kg": values["annual_material_kg"],
            "material_change_percent_vs_baseline": values["material_change_percent_vs_baseline"],
        }
        for field, expected_value in checks.items():
            if float(row[field]) != float(expected_value):
                raise AssertionError(f"Scenario reconciliation mismatch: {alternative['alternative_id']} {field}")

    exported_recommendations = {
        row["alternative_id"]: row for row in csv_rows["recommendations.csv"]
    }
    preferred = package["executive_summary"]["preferred_alternative_id"]
    for alternative in package["alternatives"]:
        expected_rec = alternative["recommendation"]
        row = exported_recommendations[alternative["alternative_id"]]
        if row["recommendation_status"] != expected_rec["status"]:
            raise AssertionError("Recommendation status mismatch")
        if (row["is_preferred_alternative"] == "True") != (alternative["alternative_id"] == preferred):
            raise AssertionError("Preferred-alternative mismatch")
        if row["overall_risk"] != alternative["risk"]["overall_level"]:
            raise AssertionError("Recommendation risk mismatch")
        if row["qualification_status"] != alternative["technical_qualification"]["status"]:
            raise AssertionError("Recommendation qualification mismatch")

    byte_comparison = {}
    for name in REQUIRED_FILES:
        identical = (export_a / name).read_bytes() == (export_b / name).read_bytes()
        byte_comparison[name] = identical
        if not identical:
            raise AssertionError(f"Determinism failure: {name}")

    report = {
        "branch": branch,
        "source_commit": source_commit,
        "available_scenarios": [
            {"scenario_id": item["scenario_id"], "title": item["title"]}
            for item in scenarios
        ],
        "selected_scenario_id": scenario_id,
        "selected_scenario_title": scenario_title,
        "generator_command_a": command_a,
        "generator_command_b": command_b,
        "generated_files": list(expected),
        "row_counts": row_counts,
        "manifest_hashes": manifest_hashes,
        "primary_key_validation": "PASS",
        "foreign_key_validation": "PASS",
        "authoritative_scenario_reconciliation": "PASS",
        "authoritative_recommendation_reconciliation": "PASS",
        "byte_determinism": byte_comparison,
        "disposition": "PASS",
    }
    (work_root / "validation-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (work_root / "byte-comparison.txt").write_text(
        "\n".join(f"{name}: PASS" for name in REQUIRED_FILES) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
