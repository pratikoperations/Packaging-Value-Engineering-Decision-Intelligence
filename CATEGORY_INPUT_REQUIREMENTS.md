# PVE 1.1 Category Input Requirements

## Purpose

This document summarizes the configuration-driven input model implemented in `src/category_registry/requirements.py`. The registry is authoritative for intake guidance. It does not determine final technical feasibility.

## Requirement levels

- Mandatory: required for the applicable intake or screening gate.
- Recommended: improves readiness and may become blocking when a category-specific safety, compliance, performance, or compatibility rule applies.
- Optional: useful supporting context but not required for the initial gate.

## Common governance

Every recorded value must retain a source classification: uploaded fact, manually entered fact, supplier-declared value, laboratory-tested value, predicted value, or assumption. Supplier-declared and predicted values must never be presented as laboratory-tested values.

## Category coverage

| Category | Core mandatory inputs | Key recommended inputs | Critical readiness concern |
|---|---|---|---|
| Corrugated | dimensions, ply, flute, layer GSM, board grade, packed weight | stack, storage, humidity, ECT, BCT, burst | compression evidence |
| Folding carton | dimensions, board GSM, print method, product weight | caliper, stiffness, crease, coating, compression | compression and line performance |
| Rigid plastic | weight, resin, capacity, mould reference | wall thickness, top load, drop, leak, torque, PCR | leak and compatibility |
| Flexible packaging | laminate structure, total thickness, migration compliance | layer thickness, OTR, WVTR, seal, bond, COF, puncture | barrier, migration and shelf life |
| Labels | substrate, adhesive, dimensions, migration requirement | peel, tack, temperature, durability, line speed | application and migration |
| Closures | dimensions, resin, weight, thread compatibility | torque, leakage, liner, tamper evidence, opening force | closure-container system fit |
| Glass | capacity, weight, dimensions, product compatibility | wall distribution, impact, pressure, thermal shock, tolerance | pressure, thermal shock and compatibility |
| Metal | gauge, metal type, coating, migration and product compatibility | seam, burst, corrosion | seam, coating and migration |

## Units and ranges

Units and validation ranges are stored on each `FieldDefinition`. Numerical values that represent physical quantities must be non-negative unless the field is a valid signed measurement such as temperature. Percentage fields are constrained to 0–100 where applicable.

## Available analyses

All categories may expose common commercial comparison, annual saving, realized saving, first-year net benefit, payback, material reduction, document completeness, and test-checklist outputs when required data is present.

## Unavailable analyses

PVE 1.1 does not provide final technical feasibility, engineering approval, or autonomous approval for any category.
