# Agents.md — Repair Garden

## What Actually Works

| Component | Status | Evidence |
|-----------|--------|----------|
| Open Repair 305K records | ✅ | 305,649 source records with full provenance |
| Shared persistence layer | ✅ | `shared/persist.py` — InsertResult, RawStoreResult, store_market_observation |
| Canonical DB schema | ✅ | `shared/db.py` — 8 tables, sole authority |
| BaseCollector runtime | ✅ | try/finally logging, parse(result) contract, 6 collectors |
| 21 passing tests | ✅ | `REPAIR_DB=/tmp/test.db python3 -m pytest tests/ -v` |
| k1 export | ✅ | 305K nodes, 233K edges, 305K evidence → k1 kernel |
| Layer 1 manifests | ✅ | Standardized source manifests for all 6 sources |
| Collector health | ✅ | `layer1/health.py` — CollectorHealth dataclass |
| CeX collector | ⚠️ | Built, runs cleanly, 403 from VPS |
| eBay 3-market | ⚠️ | Built, stable IDs, blocked on VPS |
| Trade collector | ✅ | Screwfix/Toolstation, stable IDs |
| RobotShop | ✅ | Stable IDs, JSON-LD extraction |
| PartsDB | ⚠️ | Built, needs API key (free, instant) |
| OpenAlex | ✅ | Migrated to BaseCollector |
| Canonical chain | ✅ | Fixed to write derived_fact |
| Daemon | ✅ | Fixed imports, 6 sources configured |

## What's Blocked (human action needed)

1. **eBay**: Register Apify ($5/mo free), get APIFY_TOKEN — OR run from non-VPS machine
2. **CeX**: 403 from VPS — needs non-VPS machine or residential proxy
3. **PartsDB**: Register PartsDB.io (free, instant) — 100 req/day, no credit card

## How to Run

```bash
# Tests
REPAIR_DB=/tmp/test.db python3 -m pytest tests/ -v

# Collect Open Repair
python3 -c "from collectors.open_repair_collector import OpenRepairCollector; OpenRepairCollector().run()"

# Collect CeX
python3 -c "from collectors.cex_collector import CexCollector; CexCollector().run()"

# Export to k1
python3 export_k1.py

# Run daemon (all sources on schedule)
python3 daemon.py --loop --interval 3600

# Check DB status
python3 -m shared.db status
```

## Five Gardens

1. **ASSET** — identity, composition, history
2. **FAILURE** — symptoms, diagnosis, recalls (Open Repair, OPSS)
3. **PARTS** — MPNs, substitutes, stock, price (PartsDB, Mouser, DigiKey)
4. **MARKET** — broken/working/parts listing tape (CeX, eBay, Trade, RobotShop)
5. **OUTCOME** — intervention → result → survival

## Layer Structure

```
layer1/     Core data: what_object, what_failed, what_component,
            what_intervention, what_cost, what_happened, what_worth

layer2/     Analysis: economics, experiments, constraint pressure,
            margin models, counterfactual scenarios
```

## File Layout

```
shared/           persist.py, db.py (single schema authority)
collectors/       10 collectors (6 on BaseCollector, 3 legacy fixed, 1 deleted)
domain/           gardens.py, capability.py, geography.py
core/             data models, normalize pipeline
layer1/           manifests, health schema, health tracker
layer2/           experiments, powlab, pow_research
tests/            21 passing tests
docs/             5 reviews
export_k1.py      bridge to k1 kernel
warehouse/        SQLite (not in git)
```
