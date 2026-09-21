# Review 3 — Checkpoint 1 (35-45% complete)

## What's Good
- Open Repair: 305K real records with provenance
- DB schema: raw_blob, raw_acquisition, source_record, cursor
- 609MB DB removed from git
- Old stubs cleaned up

## P0 — Must Fix Now

### 1. raw_blob idempotency
`INSERT INTO raw_blob` fails on rerun. Use `INSERT OR IGNORE`.

### 2. Collector SQL → shared functions
Every collector hand-writes SQL. Create `insert_source_record()` that returns InsertResult.

### 3. Record count lying
`count += 1` after `INSERT OR IGNORE` counts attempts, not new records. Need: records_new, records_unchanged, records_changed, records_invalid.

### 4. ORA cursor unsafe
Row-count cursor assumes append-only order. ORA reorders/corrects. For bulk snapshots: reparse entire dataset, diff by payload_hash.

### 5. Parser replay blocked by cursor
Parser v2 can't reprocess if cursor says "done". Need: `repair reparse --parser-version`.

### 6. Source record versioning
Same source_record_id, different payload = correction. Need `source_record_version` table.

### 7. Hard-coded /home/ubuntu
Collector uses absolute paths. Must resolve from repo root.

### 8. No tests
Zero test suite. Need: idempotency, replay, resume, provenance, bad schema handling.

### 9. CLI incomplete
Docstring says backfill/verify/reparse. Actual: only init/status/sources/collect.

### 10. Storage code duplication
shared/db.py, shared/storage.py, shared/collector_contract.py all exist. Consolidate.

## P1 — Next Priority

### 11. OPSS needs real implementation
Fetch individual recall pages, not search HTML. Raw per-record provenance.

### 12. France Repairability needs real implementation
Fetch actual datasets from data.gouv.fr.

### 13. EPREL needs real implementation
Find proper API, enumerate product groups.

### 14. eBay is most urgent ephemeral source
Can't go back in time. Start small cohort: 30 GPU/miner models × 3 conditions × 6h.

### 15. Cohort configs should be data, not code
Move search panels to YAML configs.

### 16. Component distributor collectors (Mouser/DigiKey)

## P2 — After Core Works

### 17. Derived pipeline frozen until data is real
### 18. No more force-pushing main
### 19. Registry should only have Repair sources

## Required Tests

```
test_same_raw_blob_twice_is_safe
test_raw_acquisition_records_multiple_fetches
test_open_repair_backfill_is_idempotent
test_bulk_snapshot_reorder_does_not_lose_records
test_changed_source_record_is_versioned
test_parser_replay_from_raw_without_network
test_partial_backfill_resume
test_invalid_record_is_quarantined
test_source_record_has_raw_provenance
test_collect_all_runs
test_no_absolute_runtime_paths
```
