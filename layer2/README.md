# Layer 2 — Analysis, Economics, Experiments

> Given Layer 1 data, what does it mean?

## Principle

Layer 2 consumes Layer 1 observations and produces derivations.
It never writes to Layer 1 tables. It never modifies raw data.
All outputs are explicitly marked as computed, not observed.

## Structure

```
layer2/
├── experiments/        # market pressure experiments
├── powlab/             # POW lab models
├── pow_research/       # POW research kernel
├── analytics/          # derived analysis
└── README.md
```

## What lives here

- RepairEconomics (fix/replace verdict)
- Margin models
- Constraint pressure
- Seesaw analysis
- Counterfactual scenarios
- Market tape analysis
- Cross-system joins

## Rule

Layer 2 code reads from Layer 1's `source_record`, `market_observation`,
and `observation` tables. It writes to `derived_fact` or its own output files.

It never touches `raw_blob`, `raw_acquisition`, or collector run history.
