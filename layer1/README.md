# Layer 1 — Core Repair Data

> What object? What failed? What component? What intervention?
> What did it cost? What happened afterwards? What was it worth?

## Principle

Layer 1 preserves the raw temporal tape. No analysis, no economics,
no verdicts. Just the observations, append-only, with provenance.

## Structure

```
layer1/
├── manifests/          # source manifests (standardized YAML)
├── health_schema.yaml  # collector health contract
├── collectors/         # Layer 1 collectors only
├── shared/             # persistence, DB schema
├── domain/             # five gardens data model
├── schemas/            # JSON Schema definitions
├── warehouse/          # SQLite (not in git)
└── tests/              # Layer 1 tests
```

## Source Manifest

Every source has a manifest answering:

| Field | Meaning |
|-------|---------|
| `id` | unique source ID |
| `layer` | 1 = core data, 2 = analysis |
| `answers` | which Layer 1 questions this feeds |
| `source.authority` | who publishes this |
| `collection.cadence` | how often |
| `storage.raw` | preserve raw blobs |
| `storage.append_only` | never rewrite |
| `health.expected_min_rows` | sanity floor |
| `health.max_staleness_hours` | freshness SLA |

## Collector Health

Every collector emits after each run:

```
last_attempt, last_success, last_error
records_seen, records_new, records_changed, records_unchanged, records_invalid
bytes_fetched, bytes_stored
schema_hash, parser_id, parser_version
source_timestamp, staleness_hours
status: ok | degraded | error | blocked
```

## Sources

| Source | Status | Records | Answers |
|--------|--------|---------|---------|
| Open Repair | ✅ operational | 305,649 | what_object, what_failed, what_intervention |
| CeX | ⚠️ blocked_vps | — | what_was_it_worth |
| Trade pricing | ✅ operational | — | what_cost |
| RobotShop | ✅ operational | — | what_cost |
| PartsDB | ⚠️ needs_api_key | — | what_component |
| OPSS recalls | ✅ operational | — | what_failed |
