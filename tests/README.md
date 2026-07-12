# Test Structure

## Implemented in PVE-0.2

`tests/data_validation/test_validator.py` covers ten canonical-data validation scenarios.

## Implemented in PVE-0.3

`tests/material_engine/test_engine.py` covers:

- Baseline material totals
- Alternative material reduction
- Missing material components
- Duplicate baseline rejection

`tests/cost_engine/test_engine.py` covers:

- Baseline cost totals
- Alternative savings
- Currency mismatch rejection
- Missing cost inputs

Expected total automated test count: 18.

Run with:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Planned Test Groups

- Business-rule tests for technical qualification and risk
- Scenario and sensitivity tests
- Export-contract compatibility tests
- End-to-end decision-flow tests

Every logic change must include or update relevant tests.
