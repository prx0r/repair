# Review 2 — Checkpoint 1

> The garden itself is the product. Not schemas, not collectors, not ontologies.

## Status: Most Collectors Are Theatre

The "migrated" collectors download HTML pages and store byte counts. They do NOT collect actual data.

## What Checkpoint 1 Actually Means

> One command acquires the maximum legally accessible historical dataset for every priority source, archives immutably, normalizes into canonical records with provenance, then continuously collects incrementally.

## Priority Order

1. Fix storage semantics (INSERT OR IGNORE, not REPLACE)
2. Add source_record, raw_blob, raw_acquisition, source_cursor tables
3. Upgrade collector contract (backfill/incremental/replay)
4. Create orchestrator CLI
5. Fully implement Open Repair historical ingestion (NOT the website)
6. Fully implement OPSS historical ingestion
7. Fully implement France Repairability
8. Fully implement EPREL
9. Migrate eBay to canonical pipeline
10. Add health/status/verify commands

## Key Rules

- Raw is append-only, content-addressed
- Observations are immutable (INSERT OR IGNORE)
- Parser versioning for reparse
- Backfill must be resumable and idempotent
- No POWUK sources in Repair checkpoint
- Report: source, historical records, normalized, dates, health
