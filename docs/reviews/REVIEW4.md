# Review 4 — Operating System for Physical-Object State Transitions

## Core Reframe

POW Repair is not "a repair database." It's an **operating system for physical-object state transitions**.

```text
ASSET → identify → observe state → enumerate next states →
REPAIR / SELL / PART-OUT / REFURBISH / UPGRADE / DEPLOY / RENT / RECYCLE →
estimate economics → route execution → observe REAL outcome → learn
```

## Five Gardens Inside Repair

```text
1. ASSET GARDEN    — identity, model, revision, composition
2. FAILURE GARDEN  — symptoms, defects, recalls, diagnosis
3. PARTS GARDEN    — MPNs, substitutes, donors, stock, price, compatibility
4. MARKET GARDEN   — broken / working / parts / refurb marketplace tape
5. OUTCOME GARDEN  — intervention → result → survival → realized economics
```

## Key Recovered Ideas

### Asset Passport
Not just "RTX 3090, price, faults" but:
- identity (manufacturer, model, revision, board IDs)
- composition (assemblies, components, MPNs, donors)
- history (manufacture, failures, repairs, modifications)
- current state (condition, faults, performance, safety)
- economics (working/broken/donor/parts/replacement value)
- possible transitions (repair, upgrade, sell, part-out, deploy, recycle)

### Donor-Device Economy
Broken object = sum of component values minus disassembly cost.
Buy broken device A not to repair A, but because component X repairs B.

### Substitution Graph (the real moat)
OEM MPN → electrical equivalent → mechanical equivalent → firmware-compatible → salvaged → cross-model donor → 3D-printable → repairable subcomponent.
Eventually: "B successfully substituted for A 31/34 times in this device revision."

### Prediction → Realized Outcome
Store what POW believed BEFORE execution, then actual result.
Turns garden into self-calibrating economic model.

### Marketplace as State Machine
Listing lifecycle: first_seen → active → price_changed → disappeared → sold/withdrawn/unknown → possibly relisted.
Three tapes: BROKEN, WORKING, PARTS.

### Most Urgent: Market + Parts (ephemeral data that vanishes)
September 2026 marketplace listings and component stock states cannot be reconstructed later. ORA/EPREL/OPSS can be backfilled later.
