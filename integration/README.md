# Integration Structure

- `contracts/` — versioned schemas and compatibility rules
- `exports/` — generated decision packages; production outputs are not committed
- `samples/` — synthetic contract examples

PVE exports read-only decision packages. AI Procurement Copilot consumes them through its own adapter. No cross-repository source modification is allowed.
