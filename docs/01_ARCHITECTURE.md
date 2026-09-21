# Canonical architecture

## Keep each garden independent

Each system owns:
- collectors
- source registry
- raw storage
- normalized schema
- transformations
- Jev decisions
- derived metrics
- tests
- MCP/API surface
- keys/secrets
- data

Only shared contracts are synchronized.

Do not:
- import one garden's collectors into another
- query another garden's internal DB during ingestion
- share raw tables across systems
- create a global graph database as the first implementation

## Shared-export architecture

```text
powpowpow ──────┐
pow-physical ───┤
pow-uk ─────────┤     versioned exports
pow-grid ───────┼──→  POW FEDERATOR / GRAPH / BACKTEST
pow-capital ────┤
pow-frontier ───┘
```

Each system publishes only shared-contract objects:
- entities
- aliases
- observations
- derived facts
- economic events
- relationships
- hypotheses/evidence where relevant

## Per-system pipeline

```text
SOURCE
  ↓
RAW APPEND-ONLY EVENT/PAYLOAD
  ↓
DETERMINISTIC NORMALIZATION
  ↓
JEV ONLY WHERE SEMANTIC AMBIGUITY EXISTS
  ↓
ENTITY RESOLUTION
  ↓
NORMALIZED DOMAIN TABLES
  ↓
DERIVED METRICS / SIGNALS
  ↓
SHARED EXPORT CONTRACT
```

## Storage doctrine

Mirror `/powpowpow`:

```text
data/
  raw/
    <source>/<yyyy>/<mm>/<dd>/*.jsonl.gz
  normalized/
    <table>/<yyyy>/<mm>/<dd>/*.parquet
  derived/
    <metric>/<yyyy>/<mm>/<dd>/*.parquet
  state/
    current.duckdb
  manifests/
    <yyyy-mm-dd>.json
```

Suggested:
- raw source payloads: append-only
- hot streams: JSONL for 7 days
- compressed Parquet: forever
- DuckDB: local query/index layer, not source of truth
- materialized current state may be rebuilt from Parquet/raw
- source-native blobs that are huge/recoverable may use extract-and-release only if reproducibility metadata is retained

## Event time vs observation time

Always preserve both:

- `event_time`: when the thing was true in the world
- `observed_at`: when POW learned it

This distinction is mandatory for causal-latency work.

## Bitemporal future

For revised government datasets, eventually add:
- valid time: reality period
- system time: version POW received

Never silently overwrite revised values.

## Raw / normalized / derived

Raw:
- source native
- no semantic interpretation
- content hash

Normalized:
- canonical field names and units
- deterministic transformations where possible

Derived:
- versioned method
- input IDs
- limitations
- confidence
- rights inherited from parents

## Jev principle

Use deterministic code whenever exact logic can answer the question.

Use Jev for small bounded semantic transformations only.

Use a large reasoning model for:
- new hypothesis discovery
- ontology changes
- complex paper analysis
- anomaly investigation
- human-facing narrative

Never use Jev/LLM to replace:
- arithmetic
- time differences
- joins
- order-book calculations
- z-scores
- graph traversal
- backtests

## Cross-system rule

Cross-system intelligence is a **downstream consumer**.

Example:

```text
pow-physical:
  component_family=servo_motor
  replacement_scarcity=0.82

pow-uk:
  occupation=maintenance_technician
  capacity_pressure=0.73

pow-grid:
  grid_region=X
  demand_headroom=LOW

pow-capital:
  company=A
  exposure_to=servo_motor
  order_book_state=...

pow-frontier:
  hypothesis=cheap_edge_ai_increases_servo_demand
```

The federator joins them using canonical IDs and temporal windows.
