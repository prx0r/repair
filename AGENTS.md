# Agents.md — How to Operate in This Repo

## What This Is

**POW Repair** — part of pw.systems. The repair garden asks:

> "Given a physical object and its condition/fault, is there an economically attractive path from broken → repaired → useful/resold?"

Core thesis: **"Where is physical demand appearing faster than physical capacity can respond?"**

## Architecture

```
domain/           — Capability ontology, Geography, Contracts, Entities
collectors/       — Data collectors (eBay, Open Repair, Companies House, etc.)
normalize/        — Raw storage (immutable), derive pipeline (observations → facts)
resolve/          — Entity resolver, SIC→Capability mapping
sources/          — Source registry (YAML)
shared/           — Cross-system contracts (from POW dev reference)
core/             — Data Garden primitives (from datagarden)
powlab/           — Causal models (research, not production yet)
pow_research/     — Research kernel (64 sources, 9 models)
ptech_*/          — PTech v0.3 schemas and collectors (reference)
data/             — Collected data (eBay products, robot parts, chain economics)
warehouse/        — SQLite database, raw storage
docs/             — Architecture docs from zips
datagarden/       — Thesis, formula, ideology docs
```

## How to Run

```bash
# Run all collectors
python3 collect.py

# Run specific collector
python3 collectors/open_repair_v2.py

# Run derive pipeline (observations → derived facts)
python3 normalize/derive_pipeline.py

# Run electricians vertical test
python3 collectors/electricians_vertical.py

# Run daemon (scheduled collection)
python3 daemon.py --loop --interval 3600
```

## Database

SQLite at `warehouse/repair.db` (not in git).

Tables:
- `observations` — raw observations from all sources
- `entities` — device models, parts, suppliers
- `market_snapshots` — price/availability
- `repair_events` — fault/repair/outcome
- `collection_runs` — when each source was collected

Query:
```python
import sqlite3
conn = sqlite3.connect('warehouse/repair.db')
rows = conn.execute('SELECT * FROM observations WHERE source_id="open_repair" LIMIT 10').fetchall()
```

## Data Sources (what's actually working)

| Source | Status | Rows | What |
|--------|--------|------|------|
| Open Repair Alliance | ✅ | 306,149 | Repair faults from EU cafés |
| Companies House | ✅ | 210 | Company searches + profiles |
| Planning Data | ✅ | 70 | UK solar planning apps |
| Octopus Energy | ✅ | 61 | Energy products |
| eBay UK | ⚠️ | 100 | Existing data (scraping blocked on VPS) |
| Robot Parts | ✅ | 100 | 100 components with prices |
| OpenAlex | ✅ | 20 | Research papers |
| GitHub | ✅ | 15 | Software releases |

## Derived Facts

The derive pipeline (`normalize/derive_pipeline.py`) produces:
- Repair success rates by item type (40 categories)
- Failure distributions by item type
- Companies mapped to capabilities via SIC codes

## Key Domain Concepts

### Capability (the heart of POWUK)
```
electrical_domestic_installation
ev_chargepoint_installation
solar_pv_installation
heat_pump_installation
f_gas_refrigeration
battery_storage_installation
retrofit_assessment
electronics_repair
```

### Geography Hierarchy
```
country → nation → region → LAD → postcode area → postcode
Also: DNO, GSP, isochrone
```

### The Canonical Chain
```
DEVICE → MODEL → FAULT → PART → MPN → STOCK/PRICE → REPAIR PROBABILITY → VALUE
```

## Adding a New Collector

1. Create `collectors/your_collector.py`
2. Use `normalize/raw_store.py` for immutable storage
3. Store observations in SQLite via `INSERT INTO observations`
4. Add source to `sources/registry.yaml`
5. Run `python3 normalize/derive_pipeline.py` to produce derived facts

## API Keys

Set in `.env` (not committed):
```
COMPANIES_HOUSE_API_KEY=...
ELECTRICITY_MAPS_TOKEN=...
MOUSER_API_KEY=...
```

## What NOT to Do

- Don't commit `.env` or API keys
- Don't overwrite raw data files (append-only)
- Don't add collectors without adding to registry.yaml
- Don't use `datetime.now()` for timestamps (use UTC)
- Don't catch bare `except:` (use specific exceptions)

## File Naming

- Collectors: `{source}_collector.py` or `{source}_v2.py`
- Derived data: `derive_{thing}.py`
- Schemas: `{thing}.schema.json`
- Source manifests: `source.yaml`
