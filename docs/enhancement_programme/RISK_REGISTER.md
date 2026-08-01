# Controlled Enhancement Risk Register

| Risk | Probability | Impact | Primary control | Stop condition |
|---|---|---|---|---|
| Evidence engine reuses primary logic | Medium | High | Separate modules, import prohibition and deliberate mismatch tests | Independence cannot be proven |
| Synthetic values appear commercially valid | Medium | High | Persistent disclosure, fictional suppliers and prohibited-claim tests | Disclosure is absent or ambiguous |
| Browser tests become flaky | Medium | Medium | Stable selectors, explicit readiness and limited visual assertions | Reliability falls below agreed threshold |
| Programme exceeds 100 hours | Medium | High | Phase budgets, actual-hour tracking and scope reduction | Forecast exceeds cap |
| Existing business outputs change | Low–Medium | High | Baseline snapshots and full regression | Unapproved output movement |
| Test count grows without meaningful coverage | Medium | Medium | Requirements-to-test traceability and negative tests | Tests cannot be mapped to acceptance criteria |
| Mobile tests overstate native-mobile support | Medium | Medium | Describe as Android-sized browser viewport only | Native-mobile claim appears |
| Reconciliation match creates false assurance | Medium | High | Explicit limitation wording and NOT SUPPORTED state | Match is presented as commercial validation |
| Historical frozen state becomes unclear | Medium | Medium | Separate programme and publication branches | Frozen branch is moved |
| Dependency additions destabilize CI | Low–Medium | Medium | Pin versions and isolate browser dependencies | Existing regression becomes unstable |
| Synthetic cases are too simple | Medium | Medium | Contradictory, incomplete and sensitivity cases | Scenarios do not exercise decision trade-offs |
| Formula scope expands uncontrollably | Medium | High | Core calculation whitelist | Unsupported formulas are added without authorization |

## Governance response

High-impact risks require explicit evidence before acceptance. Scope reduction is preferred over consuming contingency for optional capability.
