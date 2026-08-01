from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from src.exports import assemble_decision_package
from src.portfolio_export import build_portfolio_export, write_portfolio_export
from src.recommendation import recommend_alternatives
from src.risk_engine import evaluate_risks
from src.scenario_engine import ScenarioInputs, evaluate_scenario
from src.synthetic_data import build_legacy_dataset, load_governed_package
from src.technical_qualification import evaluate_technical_qualification


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the governed synthetic portfolio export pack.")
    parser.add_argument("--scenario-id", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--output", default="examples/portfolio_export")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    governed = load_governed_package(root / "data" / "demo" / "governed_synthetic")
    dataset = build_legacy_dataset(governed, args.scenario_id)
    alternatives = dataset["packaging_alternatives"]
    cost_adjustments = {item["alternative_id"]: 0.0 for item in alternatives}
    material_adjustments = {item["alternative_id"]: 0.0 for item in alternatives}
    scenario = evaluate_scenario(
        dataset,
        ScenarioInputs(
            annual_volume=float(dataset["packaging_project"]["annual_volume"]),
            cost_adjustment_percent_by_alternative=cost_adjustments,
            material_adjustment_percent_by_alternative=material_adjustments,
        ),
    )
    qualifications = evaluate_technical_qualification(dataset)
    risks = evaluate_risks(dataset)
    recommendation = recommend_alternatives(dataset, scenario, qualifications, risks)
    generated_at = args.generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    package = assemble_decision_package(
        dataset,
        scenario,
        qualifications,
        risks,
        recommendation,
        source_commit=args.source_commit,
        generated_at=generated_at,
    )
    package["metadata"].update(
        {
            "dataset_id": dataset.get("dataset_id"),
            "dataset_version": dataset.get("dataset_version"),
            "synthetic_disclosure": dataset.get("synthetic_notice", "Synthetic demonstration data only."),
        }
    )
    files = build_portfolio_export(
        dataset,
        package,
        scenario_name=args.scenario_id,
        cost_adjustments=cost_adjustments,
        material_adjustments=material_adjustments,
    )
    written = write_portfolio_export(root / args.output, files)
    for name, path in written.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
