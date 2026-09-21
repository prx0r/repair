# Agents.md — Repair Garden

## What This Is

POW Repair — part of pw.systems. Collects data about physical objects: what breaks, what fixes it, what it costs, what it's worth.

**Core question:** Given a physical object and its condition/fault, is there an economically attractive path from broken → repaired → useful/resold?

## What Actually Works (verified)

| Source | Records | How Verified |
|--------|---------|-------------|
| Open Repair Alliance | 305,649 | Ran collector, queried source_record table |
| Companies House | 210 | Ran collector, queried source_record table |
| Planning Data | 70 | Ran collector |
| Octopus Energy | 61 | Ran collector |
| OpenAlex | 20 | Ran collector |
| Tests | 8/8 passing | `REPAIR_DB=/tmp/test.db python3 -m pytest tests/ -v` |

## What Doesn't Work (blockers)

See `BLOCKERS.md` for full list. Key items:
- eBay blocked on VPS
- No API keys for Mouser/DigiKey/Nexar
- OPSS returns HTML not data
- France/EPREL endpoints unclear

## Repository Structure

```
docs/
├── reviews/         — REVIEW1.md, REVIEW2.md, REVIEW3.md
├── architecture/    — NORTHSTAR.md, DEVPLAN.md
├── sources/         — DATA_SOURCES.md
├── BLOCKERS.md      — All blockers with human actions

collectors/          — Data collectors
├── base.py          — Hardened base class
├── open_repair_collector.py — Working (305K records)
├── opss_historical.py       — Partial (needs HTML parser)
├── ebay_3market_collector.py — Blocked on VPS
└── electricians_vertical.py  — Test case

shared/
├── persist.py       — All database operations (INSERT OR IGNORE)
├── db.py            — Database schema
└── contracts.py     — Observation/DerivedFact/EconomicEvent

domain/              — Capability ontology (POWUK, frozen)
tests/               — 8 passing tests
sources/             — registry.yaml
warehouse/           — SQLite database (not in git)
```

## How to Run

```bash
# Tests
REPAIR_DB=/tmp/test.db python3 -m pytest tests/ -v

# Collect Open Repair
python3 collectors/open_repair_collector.py

# Check status
python3 -m repair status
```

## Rules

- Every collector uses `shared/persist.py` (no hand-written SQL)
- Every source_record traces to a raw_blob (provenance)
- Observations are immutable (INSERT OR IGNORE)
- No hard-coded paths (use REPAIR_DB env var)
- Tests must pass before merge
