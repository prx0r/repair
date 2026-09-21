# Repair Garden — North Star

> What is the highest-value next state of this physical asset?

## What This Is

POW Repair is an **operating system for physical-object state transitions**.

Not a repair database. A system that:
1. Identifies what something is
2. Observes its current state
3. Enumerates possible next states
4. Estimates economics + feasibility
5. Routes execution
6. Observes real outcomes
7. Learns

## Five Gardens

```
1. ASSET GARDEN    — identity, model, revision, composition
2. FAILURE GARDEN  — symptoms, defects, recalls, diagnosis
3. PARTS GARDEN    — MPNs, substitutes, donors, stock, price
4. MARKET GARDEN   — broken / working / parts marketplace tape
5. OUTCOME GARDEN  — intervention → result → survival → economics
```

## The Core Graph

```
CONTEXT
   ↓
FAULT
   ↓
INTERVENTION
   ↓
OUTCOME
```

Example:
```
RTX 3090 FE
black screen, artifacting under VRAM load
Micron memory
   ↓
replace chip X
   ↓
POST success → 24h stress test pass → 180d survival
```

## Asset Passport

Not just "RTX 3090, price, faults" but:

```
identity: manufacturer, model, revision, board IDs, aliases
composition: assemblies, components, MPNs, donors
history: manufacture, failures, repairs, modifications
state: condition, faults, performance, safety
economics: working/broken/donor/parts/replacement value
transitions: repair, upgrade, sell, part-out, deploy, recycle
```

## Priority: Market + Parts (ephemeral data)

September 2026 marketplace listings and component stock states cannot be reconstructed later.

ORA/EPREL/OPSS can be backfilled later.

**First priority: eBay cohort tape + MPN distributor cohort tape. Never turn them off.**

## The Opportunity Formula

```
EV = P(success|model,revision,symptom,diagnosis,intervention,part,technician,tools)
   × Value_after
   - Acquisition
   - Parts
   - Labour
   - Logistics
   - Downtime
   - Risk
   - TransactionFriction
```

## pw.systems

```
pow.systems
├── crypto.pw.systems    ← PowPowPow
├── repair.pw.systems    ← this repo
├── grid.pw.systems      ← electricity (future)
├── ev.pw.systems        ← vehicles (future)
├── parts.pw.systems     ← components (future)
├── skills.pw.systems    ← training (future)
└── company.pw.systems   ← financials (future)
```
