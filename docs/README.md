# POW Scarcity Lab

A drop-in research extension for `prx0r/powpowpow` that turns POW from a crypto/compute telemetry project into a **time-indexed causal market graph of physical technology**.

The core question is not “what is expensive?” It is:

> **When a technology shock changes feasible activity, where does scarcity migrate, how long does each layer take to notice, and what physical / labour / capital asset reprices next?**

The package preserves the existing POW invariant:

`source -> immutable raw observation -> normalized state -> derived transform -> hypothesis -> backtest -> outcome`

It adds six cross-domain state families:

1. **adoption** — installed base, shipments, deployments, usage, capacity
2. **dependency** — components, materials, energy, suppliers, skills, infrastructure
3. **buffer** — inventory, spare capacity, lead time, substitutes, geographic redundancy
4. **labour** — vacancies, wages, skills, training throughput, occupational mobility
5. **innovation response** — papers, patents, GitHub, new suppliers, capex, planning
6. **assimilation** — distributor prices, procurement, headlines, filings, L1/L2 market data

## Why this is POW-compatible

When copied into the root of `powpowpow`, `powlab.compat` will use the existing `core.py` archival/storage functions. Standalone mode uses its own append-only JSONL warehouse so the models and demos can be tested independently.

## Quick start

```bash
python -m pip install -e .
python -m powlab.cli sources --priority P0
python -m powlab.cli demo
python -m powlab.cli scenario examples/normal_compute_scenario.json
```

To collect a source that needs no credentials:

```bash
python -m powlab.cli probe neso_tec
python -m powlab.cli probe planning_data_recent
python -m powlab.cli probe openalex_frontier
```

Credentials are read from environment variables named in `config/source_registry.json`.

## Model kernels included

- Bayesian-style Richards/S-curve diffusion fit + demand derivative
- Leontief / production-network shock propagation
- LP shadow-price solver for binding physical constraints
- lag scanner / Granger screen for causal-assimilation latency
- PID-inspired synergy screen for complementary inputs
- installed-base cohort hazard / maintenance-demand model
- skill scarcity + training throughput model
- firm-link reconstruction baseline using gradient boosting
- scenario engine joining adoption -> component load -> bottlenecks -> skills -> maintenance

These are **research kernels**, not claims of causal truth. Every signal is designed to be backtested and falsified.

## Files to copy into current repo

Copy `powlab/`, `config/pow_sources.json`, and the docs. Do **not** replace existing `core.py`, collectors, L2 archival, or crypto models. This extension deliberately sits beside them.
