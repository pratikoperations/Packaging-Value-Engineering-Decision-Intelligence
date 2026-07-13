# PVE 1.1 Build Plan

Hard cap: 80 hours.

| Build | Scope | Hours | Status |
|---|---|---:|---|
| 1 | Architecture and scope lock | 6 | Complete |
| 2 | Project creation expansion | 7 | Complete |
| 3 | Category input definitions | 14 | Complete |
| 4 | Excel template generation | 10 | Complete |
| 5 | Excel upload and normalization | 10 | Complete |
| 6 | Readiness and blocking engine | 9 | Complete |
| 7 | Commercial and ROI extension | 5 | Complete |
| 8 | Streamlit UI and reports | 8 | Implemented; final CI required |
| 9 | Testing and release QA | 11 | Not authorized |
| **Total** |  | **80** | |

## Build 8 Acceptance Gate
- Guided workflow exposes all eight registry categories.
- Category/objective/change-type context is visible.
- Excel template, Excel upload, retained JSON/CSV upload, readiness, commercial, testing, document evidence, and report export are connected.
- Unavailable outputs always include reasons.
- Estimate labels, source traceability, assumptions, engineering validation, and human approval are retained.
- Complete automated test suite must pass with zero failures and errors.

## Control
Each build is delivered through controlled increments on the dedicated feature branch. Scope cannot expand without replacing an approved item within the same cap. Build 9 requires separate authorization and PR #25 remains draft and unmerged.
