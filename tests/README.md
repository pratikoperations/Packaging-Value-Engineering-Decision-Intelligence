# Test Structure

## Implemented in PVE-0.2

`tests/data_validation/test_validator.py` covers:

- Valid complete synthetic dataset
- Missing mandatory fields
- Negative values
- Duplicate identifiers
- Unsupported units
- Invalid enum values
- Missing evidence references
- Invalid percentages
- Partial-data insufficient-data eligibility
- Currency consistency

Run with:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Planned Test Groups

- Unit tests for deterministic cost and material calculations
- Business-rule tests for technical qualification and risk
- Scenario and edge-case tests
- Export-contract compatibility tests
- End-to-end decision-flow tests

Every logic change must include or update relevant tests.
