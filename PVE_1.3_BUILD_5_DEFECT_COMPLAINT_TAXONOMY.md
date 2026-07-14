# PVE 1.3 Build 5 — Packaging Defect and Complaint Taxonomy

## Status
Build 5 implementation has started on the controlled branch. This document establishes the governed taxonomy and authority boundary before persistence and workflow integration.

## Objective
Provide a consistent, evidence-linked vocabulary for recording packaging defects and customer, plant, warehouse, transport or supplier complaints without making automatic corrective-action, specification-change, implementation or supplier decisions.

## Governed defect dimensions
- packaging level: primary, secondary, tertiary or transport;
- material family: corrugated, paperboard, flexible, rigid plastic, glass, metal, wood or other;
- defect family: dimensional, structural, material, print, artwork, closure, seal, contamination, moisture, handling, palletization, labeling or other;
- defect mode and observable description;
- severity: minor, major or critical;
- occurrence stage: incoming, conversion, packing, storage, transport, customer use or unknown;
- affected SKU, supplier, manufacturing site, batch or shipment where known;
- evidence references and source classification;
- human reviewer and review status.

## Complaint dimensions
- complaint source: customer, consumer, plant, warehouse, logistics, supplier or internal quality;
- complaint channel and received date;
- complaint reference and description;
- linked defect classifications;
- affected quantity and unit where known;
- containment status as a recorded fact only;
- evidence references;
- human reviewer and review status.

## Governance rules
- taxonomy records and complaint records are immutable snapshots;
- classification must be explicitly human-reviewed;
- uncertainty and unknown values are preserved rather than inferred;
- evidence references are mandatory for confirmed classifications;
- cross-project references are prohibited;
- archived projects are read-only;
- taxonomy versions remain identifiable and reproducible.

## Human authority boundary
Build 5 may record observed defects, complaints, severity and containment status. It does not determine root cause, approve corrective actions, approve specification or implementation changes, qualify suppliers, allocate business, or authorize production release.

## Explicit Build 6 and later exclusions
- specification-change request or approval;
- implementation-change authorization;
- effective-date control for changed specifications;
- supplier qualification or disqualification;
- sourcing award or allocation;
- automatic root-cause determination;
- automatic corrective-action approval;
- autonomous complaint disposition.

## Effort accounting
- Builds 1 through 4 governance-closed: 39 hours.
- Build 5 allocation: 8 hours.
- Build 5 implementation started; no completion hours claimed yet.
- PVE 1.3 governance-closed completion remains 39 of 69 hours, 56.5%.
- Pending planned effort remains 30 hours.
- Controlled contingency used remains 0 of 2 hours.
