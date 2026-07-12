# Test Structure

## Implemented in PVE-0.2
- `tests/data_validation/test_validator.py`: ten canonical-data validation scenarios

## Implemented in PVE-0.3
- `tests/material_engine/test_engine.py`: four material-engine scenarios
- `tests/cost_engine/test_engine.py`: four cost-engine scenarios

## Implemented in PVE-0.4
- `tests/technical_qualification/test_engine.py`: six technical-qualification scenarios
- `tests/risk_engine/test_engine.py`: six risk scenarios

## Implemented in PVE-0.5
- `tests/scenario_engine/test_engine.py`: six deterministic scenario scenarios
- `tests/recommendation/test_engine.py`: six explainable recommendation scenarios

## Implemented in PVE-0.6
- `tests/exports/test_decision_package.py`: ten export assembly, rendering, completeness, determinism, and validation scenarios

## Implemented in PVE-0.7
- `tests/release/test_end_to_end_release.py`: six end-to-end, export, UI smoke, documentation, control, and draft-contract release scenarios

Expected total automated test count: 58.

Run with:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Release Test Coverage
- Canonical synthetic-data validation
- Full dataset-to-decision-package flow
- Deterministic JSON and Markdown exports
- Human approval and product-boundary controls
- Static Streamlit UI smoke contract
- Final README, demo guide, and checklist completeness
- Draft integration-contract preservation

Every logic change must include or update relevant tests.
