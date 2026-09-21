# REVIEW5.md — Repair Garden Deep Review

**Date:** 2026-09-21

---

The latest push is directionally much better: it cleaned old storage code, added shared persistence, added 8 tests, and—most importantly—started planting the **Market** and **Parts** gardens rather than spending everything on backfillable reference data.

But there are several P0 bugs that mean the new collectors are not yet trustworthy. The biggest theme is: **the code now looks production-shaped, but the shared collector runtime itself is currently broken in ways the tests don't exercise.**

## P0 — `BaseCollector.run()` is broken

`collectors/base.py` calls:

```python
json.dumps(result.errors)
```

but does not import `json`.

So any run reaching `log_run()` will raise `NameError`.

The current 8 tests don't instantiate/run `BaseCollector`, so they miss this entirely.

Add immediately:

```python
import json
```

and, more importantly, add:

```text
test_base_collector_success_run
test_base_collector_failed_fetch_is_logged
test_base_collector_parse_failure_is_logged
```

---

## P0 — collector statistics get erased

This is worse.

`BaseCollector.run()` starts with:

```python
result = CollectorResult()
```

then sets:

```python
result.raw_fetched = 1
result.raw_new = 1
```

but later does:

```python
result = self.parse(raw_content, raw_hash)
```

Every parser creates a **new `CollectorResult()`**.

So you lose:

```text
raw_fetched
raw_new
original started_at
```

Your run telemetry will say zero raw acquisitions even though a fetch happened.

Change the contract.

Either:

```python
parse(..., result)
```

mutates the existing result, or return a separate:

```python
ParseResult
```

and combine them centrally.

Do not let parsers own collector-run metadata.

---

## P0 — failed fetches aren't logged

This path:

```python
if raw_content is None:
    result.errors.append('fetch_failed')
    return result
```

returns **before `log_run()`**.

The most important collector failures therefore leave no run receipt.

Use a `try/finally` structure:

```text
start run
try acquisition
try parse
finally log run
```

Every invocation must create a `collector_run`:

```text
SUCCESS
EMPTY
FETCH_FAILED
PARSE_FAILED
SCHEMA_DRIFT
AUTH_FAILED
RATE_LIMITED
```

Monitoring depends on failures being persisted.

---

# P0 — changed-record versioning is still logically broken

`insert_source_record()` does:

```python
SELECT payload_hash
FROM source_record
WHERE source_record_id = base_id
```

Suppose:

```text
v1 = £100
```

then price changes:

```text
v2 = £90
```

You create:

```text
base
base:v202609...
```

Good.

But next collection still compares the new £90 record against **base £100**, not the newest version.

Therefore every subsequent £90 observation looks like another change:

```text
£100 → £90
£100 → £90
£100 → £90
...
```

and you generate versions forever.

This must become a real logical record/version model.

I recommend:

```text
source_record
    source_record_id       stable
    source_id
    native_id

source_record_version
    version_id
    source_record_id
    payload_hash
    normalized_json
    raw_hash
    parser_version
    first_observed_at
```

Then compare against:

```sql
latest version
```

not against the original.

This matters massively once you're collecting prices every six hours.

---

# P0 — version IDs can collide

Changed record version IDs use:

```python
strftime("%Y%m%d%H%M%S")
```

Two changes within the same second produce the same primary key.

Use:

```text
source_record_id + payload_hash
```

instead.

For example:

```text
cex:1234:version:a84f92...
```

Content-addressing is deterministic and avoids timing collisions.

---

# P0 — marketplace IDs currently destroy the time-series moat

This is the biggest conceptual mistake in the latest marketplace collectors.

CeX:

```python
native_id = f"{name}_{sell_price}"
```

RobotShop:

```python
native_id = f"{name}_{price}"
```

Trade:

```python
native_id = f"{site}_{name}_{price}"
```

**Price cannot be part of identity.**

If a Makita drill changes:

```text
£119 → £109
```

you currently see:

```text
product A @ £119
product B @ £109
```

rather than:

```text
same product
price changed
```

That destroys the very historical tape we're trying to build.

Identity should be:

```text
CeX:
boxId / product ID

RobotShop:
SKU / product URL / variant ID

Screwfix:
product code / URL

Toolstation:
product ID / URL

PartsDB:
manufacturer + MPN
```

Then price, inventory and availability become **observed states**.

This is non-negotiable.

---

# P0 — we still aren't modeling repeated market observations correctly

Even with stable identity, `source_record` alone isn't enough for an ephemeral market tape.

Example:

```text
RTX 3090
2026-09-21 12:00 £600
2026-09-21 18:00 £580
2026-09-22 00:00 £580
```

The first price change is a source version.

But the repeated £580 observation six hours later is also valuable because it tells us:

> it remained at £580.

If unchanged states are merely classified:

```text
records_unchanged += 1
```

and discarded, you can't reconstruct:

```text
duration at price
availability duration
listing visibility
stock persistence
```

For ephemeral sources you need:

```text
entity/product identity
+
snapshot observation
```

separate from source-record dedupe.

I'd introduce:

```text
market_observation

source_record_id
observed_at
price
currency
stock
availability
condition
market
```

Every scheduled market snapshot should exist even when the payload hasn't changed.

This is fundamental Data Garden logic.

---

# P0 — `raw_new` is false

`BaseCollector` does:

```python
raw_hash = store_raw(...)
...
result.raw_new = 1
```

But `store_raw()` does `INSERT OR IGNORE`.

If the same blob already exists:

```text
raw_new should = 0
```

currently:

```text
raw_new = 1
```

Again, telemetry lies.

`store_raw()` should return:

```python
RawStoreResult(
    sha256,
    inserted,
    path,
)
```

---

# P0 — acquisition provenance records the wrong URL

Current:

```python
store_acquisition(
    self.SOURCE_ID,
    self.DATASET,
    self.SOURCE_ID,
    200,
    raw_hash,
)
```

The third argument is supposed to be URL.

You store:

```text
open_repair
cex
partsdb
```

instead of the actual requested resource.

And status is hard-coded:

```text
200
```

regardless of what happened.

This nullifies much of the provenance work.

The HTTP fetching layer should return something like:

```python
Acquisition(
    content,
    requested_url,
    final_url,
    status,
    content_type,
    etag,
    last_modified,
)
```

and the base collector archives that automatically.

---

# P0 — tests are testing a fake database schema

`tests/test_core.py` manually creates:

```sql
raw_blob
raw_acquisition
source_record
source_cursor
```

rather than invoking the production database initialization.

Therefore the tests can pass while:

```text
shared/db.py
shared/persist.py
```

have incompatible schemas.

And they currently **do** each define database tables independently.

This reintroduces the schema-duplication problem.

Tests should do:

```python
REPAIR_DB=/tmp/foo.db
get_db()
```

and let production initialization create the schema.

Never copy SQL into tests.

---

# P0 — you now have two DB schema authorities again

`shared/db.py` defines a schema.

`shared/persist.py::get_db()` independently creates another partial schema.

This is precisely what we were trying to eliminate.

Make:

```text
shared/db.py
```

the sole schema/migration authority.

Then:

```python
persist.get_db()
```

imports and calls it.

Better still:

```text
db/
    schema.sql
    migrations/
```

But don't overengineer it yet.

One schema definition is enough.

---

# P1 — PartsDB collector doesn't actually use the API key

It sets:

```python
self.api_key
```

but `_search_mpn()` invokes:

```python
self._fetch_url(...)
```

without sending the key in headers or query parameters.

So `PARTSDB_API_KEY` currently changes nothing.

That collector is therefore still a stub unless their endpoint happens to be unauthenticated.

Also:

```python
price_eur = item.get('price', 0)
stock = item.get('stock', 0)
```

violates the earlier rule:

```text
unknown ≠ zero
```

Use `None`.

---

# P1 — the MPN cohort isn't actually a repair-parts cohort

Current PartsDB panel has:

```text
STM32
ESP32
ATmega
LM7805
NE555
2N2222
generic 0805
...
```

Those are useful electronics components, but this doesn't yet connect to the Repair graph.

We want the cohort to emerge from:

```text
devices we're tracking
↓
common failed components
↓
repair BOMs
↓
MPNs
```

Example:

```text
RTX 3090
Antminer S19
PS5
MacBook
Dyson
Makita
```

→ actual MOSFETs/controllers/fans/connectors/PSUs/chips used in repairs.

Otherwise we are building a generic electronics-price garden rather than a **Repair Parts Garden**.

Generic parts can remain as control/baseline cohorts.

---

# P1 — CeX is a strong addition, but needs exact source IDs

CeX is actually an excellent source for Breadup/Repair because it gives something eBay doesn't:

```text
retail sell price
cash buy price
exchange value
```

That directly exposes market-maker spread:

$$
spread = sell - buy
$$

and gives a liquidity/value anchor.

This is one of the better additions in this push.

But the collector discards whatever CeX-native product identifier exists and uses:

```text
name + price
```

Fix that immediately.

Preserve every source field that might identify:

```text
boxId
categoryId
EAN
product code
grade/condition
```

Even if you don't use them yet.

---

# P1 — CeX should become a longitudinal **quote tape**

Don't merely collect products.

Track:

```text
CeX product
× timestamp
× sell price
× cash-buy price
× exchange price
× availability
```

Then derive:

```text
dealer spread
price revisions
buy-side liquidity proxy
retail-refurb ceiling
```

This is exactly inherited Breadup intelligence.

---

# P1 — RobotShop is good strategically, low checkpoint priority

RobotShop is interesting because robot components are the future-facing Repair branch.

But for Checkpoint 1 it is less urgent than:

```text
eBay
CeX
parts distributors
```

because those complete the immediate economic loop.

Keep it running if it works cheaply.

Don't invest much engineering time into scraping it yet.

---

# P1 — Screwfix/Toolstation is drifting toward POWUK again

Trade pricing is useful.

But entries like:

```text
consumer unit
EV charger
solar panel
heat pump
```

are more:

```text
POWUK / installation economics
```

than Repair.

For Repair, I'd narrow this collector to replacement/repair-relevant goods:

```text
power tool batteries
motors
switches
brushes
chargers
electrical consumables
repair tools
```

Don't let `repair` become the entire UK physical economy again.

---

# P1 — marketplace query scope is too broad

Examples:

```text
makita
bosch
apple-iphones
thinkpad
```

are too broad for a long-term cohort.

You need:

```text
exact physical identities
```

Example:

```text
Makita DHP482
Makita DHP486
ThinkPad T480
ThinkPad X1 Carbon Gen 9
RTX 3090 FE
Antminer S19 Pro
PS5 CFI-1216A
```

Stable cohorts are where the time moat comes from.

Broad keyword searches are useful for discovery but shouldn't constitute the permanent tape.

---

# P1 — registry cleanup was only partial

`registry.yaml` still includes:

```text
Companies House
Planning Data
Octopus
OpenAlex
```

under Repair.

We've now discussed this repeatedly.

Those can absolutely feed POW later, but they're not one of Repair's five native gardens:

```text
ASSET
FAILURE
PARTS
MARKET
OUTCOME
```

Move them to cross-system/reference registry or remove them from Repair's operational health definition.

Otherwise checkpoint reporting remains noisy.

---

# P1 — marketplace source inventory is useful, but don't build 21 collectors

`MARKETPLACES.md` is good research.

But it creates a temptation to implement:

```text
CeX
Back Market
Cash Converters
MusicMagpie
RobotShop
Screwfix
Toolstation
BidSpotter
Saleroom
...
```

before the tape model itself is right.

Don't.

First prove three complementary tapes:

```text
eBay
→ peer-to-peer / actual market

CeX
→ dealer bid/ask

parts distributor
→ repair input costs
```

That's enough to create a powerful first economic loop.

Everything else can plug into the same primitive later.

---

# P1 — don't solve eBay by immediately paying a scraper unless necessary

The `BLOCKERS.md` reasoning is reasonable, but the key is not "we need Apify."

The key is:

> we need a reliable legally compliant source of repeated marketplace observations.

Options can include:

```text
official eBay APIs
another residential/non-datacenter worker
allowed third-party service
Apify
```

Whichever one wins should produce the same canonical tape.

Keep provider-specific logic behind:

```text
EbayAcquisitionAdapter
```

so changing provider doesn't alter the garden schema.

---

# P2 — `CollectorResult.records_changed` isn't logged

The result object has:

```python
records_changed
```

but `collector_run` and `log_run()` don't persist it.

So a key health metric disappears.

Add:

```text
source_records_changed
source_records_unchanged
```

to `collector_run`.

For a recurring source these matter more than total "new."

---

# P2 — health needs `EMPTY_SUCCESS` vs success

Several new scrapers can legally return:

```json
[]
```

because parsing broke.

`BaseCollector` will consider that success.

That's dangerous.

Each source needs sanity bounds:

```yaml
sanity:
  expected_min_records: 10
  required_fields:
    - name
    - price
```

If yesterday:

```text
CeX = 180 records
```

and today:

```text
CeX = 0
```

status should become:

```text
DEGRADED / PARSER_FAILURE
```

not green.

---

# P2 — imports and unused code need linting

Several collectors import:

```text
requests
re
HEADERS
```

without using them directly.

Not serious, but `ruff` should run in CI.

More importantly, running:

```bash
python -m pytest
ruff check .
```

would have caught some structural mistakes.

`BaseCollector`'s missing `json` is exactly the sort of thing a linter would catch immediately.

---

# The big strategic assessment

This push **did respond to the most important conceptual correction from our prior chats**:

Previously:

```text
backfillable public dataset
backfillable public dataset
backfillable public dataset
```

Now:

```text
Open Repair history
+
CeX tape
+
component tape
+
robot/trade prices
```

That's much closer to an actual Data Garden.

But the latest code still treats market collection too much like:

> scrape current page → dedupe records

instead of:

> continuously observe stable physical entities → preserve market state through time.

That is the next conceptual correction.

The core architecture should now crystallize around:

```text
                    ASSET ID
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
   FAILURE          PARTS            MARKET
       │               │                │
       │          part offers       observations
       │          stock/price       broken
       │          substitutes       working
       │                            parts
       │                            refurb
       └───────────────┬────────────────┘
                       ▼
                   OUTCOME
```

and every market collector should answer:

```text
WHAT stable thing did I observe?
WHAT was its state?
WHEN did I observe it?
WHERE?
WHAT raw evidence proves it?
```

not:

```text
can I avoid inserting the same JSON twice?
```

## Exact instructions for the next coding pass

1. Fix `BaseCollector` missing `json`.
2. Fix result metadata being overwritten by parser results.
3. Guarantee failed runs are logged.
4. Make raw storage return whether blob is actually new.
5. Record real acquisition URL/status/headers.
6. Consolidate DB schema authority between `db.py` and `persist.py`.
7. Replace changed-record implementation with proper latest-version semantics.
8. Use payload hash rather than timestamps for version IDs.
9. **Remove price from marketplace native IDs.**
10. Extract stable CeX/RobotShop/Screwfix product IDs.
11. Introduce first-class timestamped `market_observation`.
12. Persist unchanged observations for ephemeral market tapes.
13. Add `records_changed` and `records_unchanged` to run telemetry.
14. Fix PartsDB authentication and null semantics.
15. Replace generic MPN panel with a repair-derived MPN cohort.
16. Add exact model versioned cohorts for marketplace collection.
17. Add tests around the collector runtime—not merely persistence helpers.
18. Get **CeX + one component source + eBay** running repeatedly.
19. Run three consecutive collection cycles and prove state continuity.
20. Do not add marketplace #22 until this works.

The biggest positive change is that **the repo is finally moving into data that becomes more valuable each day it remains running**. The biggest remaining error is that its identity/observation model still doesn't properly preserve that time dimension. Fix that before expanding source count.
