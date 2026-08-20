from __future__ import annotations

import json
from pathlib import Path

from src.recommendation import recommend_alternatives
from src.risk_engine import evaluate_risks
from src.scenario_engine import ScenarioInputs, evaluate_scenario
from src.technical_qualification import evaluate_technical_qualification


ROOT = Path(__file__).resolve().parents[1]
DEMO_PATH = ROOT / "data" / "demo" / "corrugated_shipping_cases.json"


def test_live_demo_has_one_governed_preferred_alternative() -> None:
    dataset = json.loads(DEMO_PATH.read_text(encoding="utf-8"))
    adjustments = {
        item["alternative_id"]: 0.0
        for item in dataset["packaging_alternatives"]
    }
    scenario = evaluate_scenario(
        dataset,
        ScenarioInputs(
            annual_volume=float(dataset["packaging_project"]["annual_volume"]),
            cost_adjustment_percent_by_alternative=adjustments,
            material_adjustment_percent_by_alternative=adjustments,
        ),
    )
    qualifications = evaluate_technical_qualification(dataset)
    risks = evaluate_risks(dataset)
    recommendation = recommend_alternatives(dataset, scenario, qualifications, risks)

    assert qualifications["ALT-BASE"].status == "qualified"
    assert risks["ALT-BASE"].data_complete is True

    assert qualifications["ALT-A"].status == "conditionally_qualified"
    assert risks["ALT-A"].data_complete is True
    assert recommendation.alternatives["ALT-A"].status == "conditionally_recommended"
    assert recommendation.preferred_alternative_id == "ALT-A"

    assert recommendation.alternatives["ALT-B"].status == "insufficient_data"
    assert recommendation.alternatives["ALT-C"].status == "insufficient_data"
