# Agents.md — How to Operate in This Repo

## What This Is

**POW Repair** — part of pw.systems. The repair garden asks:

> "Given a physical object and its condition/fault, is there an economically attractive path from broken → repaired → useful/resold?"

## What Actually Works

| Source | Records | Status |
|--------|---------|--------|
| Open Repair Alliance | 305,649 | ✅ Full historical CSV, content-addressed raw |
| Companies House | 210 | ✅ SIC→Capability mapped |
| Planning Data | 70 | ✅ UK solar apps |
| Octopus Energy | 61 | ✅ Energy products |
| OpenAlex | 20 | ✅ Research papers |
| OPSS Recalls | 0 | ❌ Endpoint returns HTML, needs parser |
| eBay | 0 | ❌ Blocked on VPS |

## How to Run

```bash
# Initialize database
python3 -m repair init

# List sources
python3 -m repair sources

# Run specific collector
python3 collectors/open_repair_historical.py

# Run derive pipeline
python3 normalize/derive_pipeline.py

# Check status
python3 -m repair status
```

## Database

SQLite at `warehouse/repair.db` (NOT in git, 600MB+).

Tables:
- `source_record` — normalized source records (305K+)
- `raw_blob` — content-addressed raw storage
- `raw_acquisition` — HTTP metadata
- `source_cursor` — resumable backfill state
- `derived_fact` — computed insights

Query:
```python
import sqlite3
conn = sqlite3.connect('warehouse/repair.db')
rows = conn.execute('SELECT * FROM source_record WHERE source_id="open_repair" LIMIT 10').fetchall()
```

## Derived Facts

The derive pipeline produces:
- Repair success rates by item type (40 categories)
- Failure distributions
- Companies mapped to capabilities via SIC codes

## Architecture

```
collectors/       — Data collectors
shared/db.py      — Database schema and helpers
normalize/        — Derive pipeline
resolve/          — SIC→Capability mapping
sources/          — Source registry
domain/           — Capability ontology (POWUK, frozen for now)
```

## API Keys

Set in `.env` (not committed):
```
COMPANIES_HOUSE_API_KEY=...
```

## What NOT to Do

- Don't commit `.env` or API keys
- Don't commit `warehouse/repair.db` (600MB+)
- Don't use `INSERT OR REPLACE` for observations (use INSERT OR IGNORE)
- Don't add collectors without testing they actually fetch data
