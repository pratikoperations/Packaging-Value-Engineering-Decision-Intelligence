# Security and Access Model

## Principle
Power BI is a read-only executive reporting layer. It must not bypass PVE operational controls or create approval authority.

## Proposed Roles
- **PVE Operator** — uses Streamlit operational workflows.
- **Packaging Reviewer** — reviews technical and risk evidence.
- **Procurement Viewer** — views permitted Power BI reports.
- **Executive Viewer** — views portfolio and summary pages.
- **Reporting Administrator** — manages refresh and semantic model, without decision approval authority.

## Access Controls
- Microsoft Entra ID is the preferred identity provider for future departmental deployment.
- Power BI workspace access is separated from PVE operational permissions.
- SQL reporting access uses least privilege and approved read-only views.
- Row-level security should restrict projects or business units when real departmental data is used.
- Synthetic portfolio data must remain clearly labelled.

## Mandatory Boundaries
- engineering validation remains mandatory
- human approval remains mandatory
- autonomous approval remains prohibited
- reporting access does not grant operational write access
- project isolation and immutable evidence remain enforced by the authoritative application

## Planning Dependencies
Confirm Microsoft tenant, Power BI licence, workspace availability, SQL hosting, data classification, user population, and sharing method before implementation.