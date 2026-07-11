# Quality Assurance Protocol

## Mandatory Gates
- Scope gate: only approved build files changed
- File-placement gate: every file is in the PVE repository and correct path
- Data gate: required fields, units, defaults, and assumptions are explicit
- Calculation gate: deterministic formulas are independently validated
- Rule gate: technical and risk rules have positive and negative tests
- Regression gate: previous stable functions remain operational
- Explainability gate: recommendations trace to inputs, formulas, rules, and evidence
- Integration gate: export packages conform to the frozen contract
- Documentation gate: project status, logs, build history, version, recovery, and changelog are synchronized
- CI gate: automated checks pass or the exception is documented

## Build QA Report
Every build report records:
- Build ID and commit
- Scope and acceptance criteria
- Files changed
- Tests and checks run
- Results
- Known limitations
- CI status
- Release recommendation

## Completion Rule
No build is complete until QA evidence is committed to GitHub.
