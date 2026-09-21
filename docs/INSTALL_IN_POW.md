# Install into `prx0r/powpowpow`

## 1. Copy files

At repo root:

```text
powlab/
config/pow_sources.json
POW_CAUSAL_RESEARCH.md
POW_DATA_GARDENS.md
```

The adapter in `powlab/compat.py` detects the repo's `core.py` and uses:

- `core.fetch_json`
- `core._archive_raw`
- `core.store_normalized`
- `core.utcnow`

No migration of existing chain data is required.

## 2. Add dependencies

Append to the existing `pyproject.toml` dependencies:

```toml
"numpy>=2.0",
"scipy>=1.12",
"scikit-learn>=1.4",
"networkx>=3.2",
"statsmodels>=0.14",
```

Pandas already exists in POW.

## 3. Preserve old namespace

Do **not** rename `chain_id` immediately. Existing data and code depend on it. `powlab.compat.store_observation()` writes a generalized `entity_id` inside normalized rows while using a synthetic `chain_id` / domain partition externally.

Recommended gradual migration:

```text
network_id / chain_id   -> partition / compatibility key
entity_id               -> canonical heterogeneous graph node
entity_type             -> technology | component | firm | skill | location | instrument | material
metric                   -> observed variable
```

## 4. First cron/probe set

Start irreversible series first:

```text
*/15 * * * *  neso/elexon state where relevant
0 * * * *     selected distributor component baskets
15 * * * *    market / eBay / job / procurement deltas
30 * * * *    GitHub / OpenAlex / patent frontier deltas
45 * * * *    graph transforms and signal scan
```

Do not poll sources more frequently than their terms/rate limits permit. The registry's cadence is a **POW desired cadence**, not permission to violate provider rules.

## 5. Core new normalized table

Use `causal_observation` as the universal long-form state table:

```json
{
  "entity_id": "component:STM32H743VIT6",
  "entity_type": "component",
  "metric": "stock_units",
  "value": 18420,
  "unit": "unit",
  "event_time": "...",
  "source_id": "mouser",
  "dimensions": {"supplier":"mouser","region":"uk"}
}
```

Edges live in `causal_edge` and can be time-varying:

```json
{
  "src": "technology:humanoid_robot",
  "dst": "component:torque_sensor",
  "relation": "requires",
  "weight": 6.0,
  "confidence": 0.72,
  "valid_from": "...",
  "evidence_ids": ["..."]
}
```

## 6. Never flatten away provenance

A discovered relationship is not truth. Store:

- method
- training window
- lag
- p-value / score
- feature set
- source observations
- model version
- out-of-sample result

The graph must distinguish `observed`, `inferred`, `simulated`, and `hypothesized` edges.
