# Agents.md — Repair Garden (honest state)

## What Actually Works

| Component | Status | Evidence |
|-----------|--------|----------|
| Open Repair 305K records | ✅ | `SELECT COUNT(*) FROM source_record WHERE source_id='open_repair'` → 305,649 |
| Derive pipeline | ✅ | 40 item types with repair success rates |
| 8 passing tests | ✅ | `REPAIR_DB=/tmp/test.db python3 -m pytest tests/ -v` |
| Shared persistence | ✅ | `insert_source_record()` returns InsertResult |
| Idempotent raw storage | ✅ | Same content → same SHA256, one blob |
| Marketplace collectors | 🔧 | Built but blocked on VPS (need non-VPS machine or Apify) |

## What's Blocked (human action needed)

1. **eBay**: Register Apify ($5/mo free), get APIFY_TOKEN
2. **OPSS**: Download ODS from GOV.UK or use Apify actor
3. **CeX**: Run from non-VPS machine
4. **Components**: Register PartsDB.io (free, instant)

## How to Run

```bash
# Tests
REPAIR_DB=/tmp/test.db python3 -m pytest tests/ -v

# Collect Open Repair
python3 collectors/open_repair_collector.py

# Check status
python3 -m repair status

# Derive facts
python3 normalize/derive_pipeline.py
```

## Five Gardens

1. ASSET — identity, composition, history
2. FAILURE — symptoms, diagnosis, recalls
3. PARTS — MPNs, substitutes, stock, price
4. MARKET — broken/working/parts listing tape
5. OUTCOME — intervention → result → survival

## File Layout

```
collectors/     — data collectors
shared/         — persist.py, db.py, contracts.py
domain/         — gardens.py (five gardens), capability.py, geography.py
tests/          — 8 passing tests
docs/           — reviews, architecture, sources
sources/        — registry.yaml
warehouse/      — SQLite (not in git)
```
