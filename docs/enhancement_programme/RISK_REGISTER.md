# Controlled Enhancement Risk Register

| Risk | Owner | Probability | Impact | Trigger | Detection evidence | Primary control | Residual risk | Review gate | Stop condition |
|---|---|---|---|---|---|---|---|---|---|
| Evidence engine reuses primary logic | Calculation lead | Medium | High | Any prohibited import/helper reuse | Static import and dependency-boundary report | Separate modules, import prohibition, independent fixtures and mutation tests | Low–Medium | Gate 2 | Independence cannot be proven |
| Synthetic values appear commercially valid | Data-governance lead | Medium | High | Missing/ambiguous disclosure or real identity match | Manifest, export and denylist test results | Persistent disclosure, fictional suppliers and prohibited-claim tests | Low | Gates 1 and 4 | Disclosure absent or identifiable data detected |
| Browser tests become flaky | Browser-test lead | Medium | Medium | Any unexplained failure in final three-run sequence | Three-run CI history and traces | Stable selectors, readiness conditions, zero acceptance retries | Low–Medium | Gates 3 and 4 | Three consecutive clean runs cannot be achieved within scope |
| Programme exceeds 100 hours | Programme owner | Medium | High | Forecast or actual exceeds gate/cap | Time ledger and forecast report | Phase budgets and immediate scope reduction | Low | Every gate | Forecast exceeds 100 hours after mandatory scope reduction |
| Existing business outputs change | Technical lead | Low–Medium | High | Baseline snapshot difference | Regression and output-diff report | Baseline snapshots and full regression | Low | Every feature gate | Unapproved output movement |
| Test count grows without meaningful coverage | QA lead | Medium | Medium | Test lacks mapped acceptance criterion | Requirements-to-test matrix | Traceability and negative tests | Low | Every feature gate | Mandatory tests cannot map to acceptance |
| Mobile tests overstate native support | Product/governance lead | Medium | Medium | Native-mobile wording appears | Documentation and UI claim review | Android-sized browser wording only | Low | Gates 3 and 4 | Native-mobile claim remains |
| Reconciliation match creates false assurance | Governance lead | Medium | High | Match presented as validation | UI/export limitation tests | Explicit limitations and `NOT SUPPORTED` | Low–Medium | Gates 2 and 4 | Commercial/engineering validation claim appears |
| Historical frozen state becomes unclear | Programme owner | Medium | Medium | Frozen branch moves or PR #79 merge attempted | Branch comparison and PR-state evidence | Separate programme/publication branches; close PR #79 unmerged | Low | Gate 0 and 4 | Frozen branch moves |
| Dependency additions destabilize CI | Technical lead | Low–Medium | Medium | Existing regression instability | Dependency diff and CI history | Pin and isolate browser dependencies | Low–Medium | Gate 3 | Existing regression remains unstable |
| Synthetic cases are too simple | Procurement scenario owner | Medium | Medium | Cases fail to exercise trade-offs | Scenario coverage review | Contradictory, incomplete and sensitivity cases | Low | Gate 1 | Three cases do not exercise defined decisions |
| Formula scope expands uncontrollably | Calculation lead | Medium | High | Formula outside whitelist added | Registry diff and authorization check | Core whitelist and `NOT SUPPORTED` | Low | Gate 2 | Unauthorized formula remains |

## Review cadence

The programme owner reviews this register at every gate. High-impact triggers require evidence before progression. Scope reduction is preferred over contingency for optional capability. Residual risk is accepted only through explicit gate approval.
