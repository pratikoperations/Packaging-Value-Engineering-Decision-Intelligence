# Security and Access Model

## Principle
Power BI is a read-only executive reporting layer. It must not bypass PVE operational controls or create approval authority.

## Roles
- **PVE Operator** — uses Streamlit operational workflows.
- **Packaging Reviewer** — reviews technical and risk evidence.
- **Procurement Viewer** — views permitted Power BI reports.
- **Executive Viewer** — views portfolio and summary pages.
- **Reporting Administrator** — manages PostgreSQL reporting loads and Power BI refresh without decision approval authority.

## Access Boundaries
- Streamlit operational access remains separate from Power BI reporting access.
- SQLite remains private to the operational application.
- PostgreSQL reporting access follows least privilege.
- Power BI uses approved read-only PostgreSQL views only.
- Reporting access never grants operational write access.
- Microsoft Entra ID is preferred if Power BI Service sharing is later enabled.
- Row-level security is required only when real multi-user departmental data is introduced; portfolio use may use clearly labelled synthetic data without RLS.

## Mandatory Controls
- engineering validation remains mandatory
- human approval remains mandatory
- autonomous approval remains prohibited
- project isolation remains preserved
- immutable evidence remains enforced by the authoritative application
- dataset, scenario, threshold, and source identifiers remain visible for traceability

## Portfolio Sharing Decision
- Streamlit remains publicly shareable under its current link.
- Power BI Desktop is the minimum guaranteed demonstration method.
- Power BI Service sharing is optional and depends on account, tenant, workspace, and licence availability.
- Publish-to-web must not be used for confidential, personal, supplier, or company data.

## Dependencies Before Implementation
Confirm PostgreSQL hosting, network reachability, Power BI account, tenant, licence, workspace, intended sharing audience, and whether a gateway is required.

## Deferred
Enterprise identity design, production RLS administration, formal data classification, penetration testing, enterprise deployment, and operational persistence migration.