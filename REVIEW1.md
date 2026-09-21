# Review 1 — Structural Fixes

> Stop adding sources. Fix the structure first.

## Critical: Rotate Keys

Both Companies House keys were committed to a public repo. **Revoke immediately.**

```bash
# Keys to revoke — see .env for current values
# REST key, Streaming key, GitHub PAT — rotate all three
```

## The Fix Sequence

1. Rotate/remove secrets, add `.env.example`
2. Define the `Capability` ontology
3. Replace universal DNO `Region` with canonical hierarchical `Geography`
4. Promote `Observation`, `DerivedFact`, `EconomicEvent`, `Relationship` as only shared persistence contracts
5. Make raw ingestion immutable and content-addressed
6. Split POWUK vs Repair/Grid/Capital sources
7. Build provider/company entity resolver
8. Implement one complete vertical end-to-end (electricians)
9. Add MCS/heat pumps, OZEV, F-gas, TrustMark
10. Keep scarcity scoring descriptive until enough historical data

## Core Thesis

> "Where is physical demand appearing faster than physical capacity can respond?"

## Four Native Economic Primitives

```
CAPABILITY  — Who can perform a physical task now?
PIPELINE    — Who is likely to become capable later?
DEMAND      — How much demand for that capability is appearing?
FRICTION    — What prevents capacity from responding?
```

Everything resolves onto: `CAPABILITY × GEOGRAPHY × TIME`

## Canonical Entities

```
Capability, Occupation, Qualification, CertificationScheme,
Provider, TrainingProvider, Company, WorkforcePopulation,
Geography, DemandEvent, PolicyEvent, ProcurementOpportunity,
TrainingFlow, CapacityObservation
```

## Relationships

```
occupation REQUIRES capability
qualification CONFERS capability
training_provider DELIVERS qualification
provider HOLDS certification
company OPERATES_AT geography
policy_event CREATES_DEMAND_FOR capability
procurement REQUIRES capability
apprenticeship TRAINS_FOR occupation
```

## Capability Ontology (electricians example)

```
electrical_domestic_installation
electrical_commercial_installation
ev_chargepoint_installation
solar_pv_installation
battery_storage_installation
heat_pump_installation
f_gas_refrigeration
retrofit_assessment
network_cabling
industrial_control_systems
hvac_maintenance
```

## Geography Hierarchy

```
country → nation → region → ITL → local_authority → ward →
postcode_area → postcode_district → postcode_sector → postcode → lat/lon
also: DNO, GSP, travel_time_isochrone
```

## Data Architecture

```
R2:          immutable evidence lake (raw payloads)
Parquet:     normalized observations/events
DuckDB:      local analytical transformations
SQLite/D1:   collector state + registry
```

## Raw Data Contract (every collector run)

```
source_id, dataset_id, retrieved_at, source_updated_at,
request_uri, request_parameters, http_status, content_type,
content_length, sha256, storage_uri, collector_version, license
```

## Timestamp Semantics (minimum 3)

```
effective_at    — when this was true in reality
published_at   — when the source published it
observed_at    — when we collected it
```

## Collection Priority Formula

```
collection_priority ∝ (future_value × ephemerality) / collection_cost
```

## Collector Architecture

```
collectors/
├── capability/     (competent_person, mcs, ozev, fgas, trustmark)
├── training/       (appar, ukrlp, apprenticeships, ofqual)
├── labour/         (ons, nomis, vacancies)
├── businesses/     (companies_house)
├── demand/         (contracts_finder, find_a_tender, planning)
├── policy/         (legislation, consultations, guidance)
└── infrastructure/ (grid, ev, solar)
```

## Vertical Test: Manchester Electricians 2026-09-21

POWUK should return:
- current registered capacity
- company capacity
- sole-trader estimate
- employment estimate
- training providers
- apprenticeship starts
- expected completions
- vacancy demand
- procurement demand
- policy events
- historical deltas
- provenance for every number

## Source Registry (YAML format)

```yaml
id: mcs_installer_register
garden: powuk
domain: capability
access:
  type: registry
  cadence: daily
temporal:
  recoverability: ephemeral
  snapshot_required: true
produces:
  - provider
  - certification
  - capability
  - geography
```

## Don't Delete

- `models/skills.py`, `lagscan.py`, `diffusion.py`, `hazard.py`, `shadow.py` — put behind `research/`
- Advanced models are conceptually aligned but ahead of data

## Key Principle

> Scarcity is a **derived fact**, not the primary storage primitive.
