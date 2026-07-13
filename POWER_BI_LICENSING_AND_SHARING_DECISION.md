# Power BI Licensing and Sharing Decision

## Initial Decision
Use Power BI Desktop as the guaranteed development and interview-demonstration environment. Power BI Service publishing and sharing are optional and must be confirmed against the available Microsoft account, tenant, workspace, and licence before implementation.

## Portfolio Sharing Model
- Streamlit remains the active public operational demonstration.
- GitHub remains the canonical source repository.
- Power BI Desktop provides the guaranteed executive-reporting demonstration.
- A `.pbix` file may be demonstrated locally or by screen sharing.
- Power BI Service may be added only after account and licence validation.

## Service Sharing Preconditions
Before publishing, confirm:
- access to the correct Microsoft account
- Power BI Service entitlement
- tenant and workspace availability
- ability to invite intended viewers
- whether viewers require their own licences
- whether the PostgreSQL host is directly reachable from the service
- whether an on-premises data gateway is required

## Data Protection Rule
Publish-to-web must not be used for confidential, supplier, personal, commercial, or company data. It may be considered only for synthetic portfolio data after explicit review.

## Initial Technical Position
- connection mode: Import
- source: approved PostgreSQL reporting views
- refresh: on demand
- gateway: deferred unless service-to-database connectivity requires it
- row-level security: deferred for synthetic portfolio data; required before real departmental multi-user data is shared

## Fallback
If Power BI Service sharing is unavailable, the project remains fully demonstrable through:
1. the existing Streamlit public link
2. GitHub documentation
3. Power BI Desktop or recorded dashboard walkthrough

## Scope Boundary
Licensing procurement, enterprise tenant administration, capacity planning, formal production distribution, and enterprise deployment are excluded from this edition.