# Test Structure

## Implemented in PVE-0.2

`tests/data_validation/test_validator.py` covers ten canonical-data validation scenarios.

## Implemented in PVE-0.3

- `tests/material_engine/test_engine.py`: four material-engine scenarios
- `tests/cost_engine/test_engine.py`: four cost-engine scenarios

## Implemented in PVE-0.4

`tests/technical_qualification/test_engine.py` covers:

- Demo insufficient-data outcome
- Fully qualified outcome
- Conditional qualification
- Failure precedence
- Missing evidence
- Duplicate result rejection

`tests/risk_engine/test_engine.py` covers:

- High demo quality risk
- Explicit missing categories
- Probability escalation
- Complete low-risk set
- Invalid probability rejection
- Highest duplicate-category risk selection

Expected total automated test count: 30.

Run with:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Planned Test Groups

- Scenario and sensitivity tests
- Export-contract compatibility tests
- End-to-end decision-flow tests

Every logic change must include or update relevant tests.
