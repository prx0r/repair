# REVIEW6.md — Level 1 Completion Review

**Date:** 2026-09-21

---

This push is much closer to what Level 1 should be. The separation into `layer1/` and `layer2/` is useful, stable marketplace IDs are substantially improved, `market_observation` correctly recognizes that unchanged prices still need timestamped observations, and 21 tests is a meaningful improvement.

But **Level 1 is not finished yet**. There are a handful of structural issues that matter specifically because Level 1 is supposed to become the boring, trustworthy historical tape everything else uses.

My current assessment is:

```text
LEVEL 1 FOUNDATION       ████████░░  good
OPEN REPAIR BACKFILL     █████████░  good
MARKET TAPE MODEL        ███████░░░  concept right, plumbing incomplete
PARTS TAPE               ███░░░░░░░  not actually planted
OPSS                      ██░░░░░░░░  still misleadingly marked operational
MONITORING                █████░░░░░  designed, not fully wired
REPLAY / PROVENANCE       █████░░░░░  major raw-acquisition gap
SOURCE COVERAGE           ████░░░░░░  too few real sources running
```

The good news is I would **stop redesigning the ontology now**. The correct task is much simpler: make Level 1 eat data.

# P0 — the biggest remaining problem: "raw" isn't actually raw

This is the most important thing I found.

Take CeX.

The collector does roughly:

```text
request CeX query A
request CeX query B
request CeX query C
...
extract items from each response
combine all extracted items into Python list
json.dumps(list)
↓
BaseCollector stores THAT as raw
```

So:

```text
raw_blob
```

doesn't contain the original CeX responses.

It contains your **first transformation**.

Same problem with:

* RobotShop
* Screwfix / Toolstation
* PartsDB
* likely eBay

That violates the Level-1 rule:

> Preserve what the source actually gave us so future parsers can reconstruct history.

You currently cannot later say:

> Our parser missed EAN/SKU/stock field X in September 2026; reparse the original response.

because the original HTML/API response was thrown away.

### Correct structure

A single collector run can contain many acquisitions:

```text
collector_run
    │
    ├── acquisition 1
    │      raw blob = exact HTTP response
    │
    ├── acquisition 2
    │      raw blob = exact HTTP response
    │
    ├── acquisition 3
    │      raw blob = exact HTTP response
    │
    └── ...
```

Then:

```text
raw acquisition
      ↓
parser
      ↓
source records
```

Your aggregated JSON can still exist, but it is a **normalized batch**, not raw source evidence.

This is the single biggest Level-1 correction I'd make now.

---

# P0 — acquisition provenance only remembers the last URL

Related problem.

A CeX collection might issue 30 searches.

At the end:

```python
_last_url
_last_status
_last_final_url
```

contain only the last request.

Then BaseCollector records one `raw_acquisition`.

So the DB effectively says:

```text
this giant combined batch
came from query #30
```

when it actually came from 30 HTTP responses.

That's false provenance.

Move acquisition storage into the HTTP fetcher itself:

```python
fetch_url(...)
    ↓
HTTP response
    ↓
store exact raw blob
    ↓
store raw_acquisition
    ↓
return Acquisition object
```

Then every network request automatically becomes evidence.

Collectors should not manually remember `_last_url`.

---

# P0 — source versioning is still wrong

This code:

```sql
ORDER BY source_record_id DESC
LIMIT 1
```

does not find the latest record.

Your version IDs are now:

```text
:v<payload_hash>
```

which is good for identity.

But hashes are not chronological.

Suppose versions:

```text
:vfa0123
:v182abc
:v903def
```

Lexicographic sort tells you nothing about which came last.

So you've traded the previous bug for a subtler one.

Query:

```sql
ORDER BY retrieved_at DESC
```

instead.

Ideally the schema eventually becomes:

```text
source_entity
    stable native identity

source_record_version
    payload version
    retrieved_at
```

but you don't need a large migration immediately.

At minimum:

```sql
ORDER BY retrieved_at DESC
```

must replace ordering by ID.

---

# P0 — unchanged market observations point to old raw evidence

This is a subtle but important provenance issue.

Imagine CeX:

```text
12:00 £500
18:00 £500
```

At 18:00:

```text
insert_source_record()
→ unchanged
→ returns old source_record_id
```

Then:

```python
store_market_observation(source_record_id=old_record)
```

The time-series correctly records:

```text
18:00 £500
```

but its source record still references the **12:00 raw payload**.

The fact we're trying to prove is:

> I actually observed £500 again at 18:00.

So `market_observation` should directly reference something from the current collection:

```text
acquisition_id
raw_hash
collector_run_id
```

Prefer:

```text
market_observation
    source_record_id
    acquisition_id
    collector_run_id
    observed_at
    price
    ...
```

Then identical states remain independently evidenced.

This is particularly important because the entire moat is the temporal tape.

---

# P0 — daemon likely cannot run several collectors

Daemon invokes:

```python
python collectors/cex_collector.py
```

But the collector contains:

```python
from .base import BaseCollector
```

Relative imports normally require execution as a package/module.

So direct script execution can fail with:

```text
attempted relative import with no known parent package
```

Your AGENTS instructions use:

```bash
python -c "from collectors.cex_collector ..."
```

which works because it's imported as a package.

The daemon needs either:

```bash
python -m collectors.cex_collector
```

or import collector classes directly.

This needs an integration test:

```text
test_daemon_can_execute_every_enabled_collector
```

Not merely test persistence helpers.

---

# P0 — daemon double-logs runs

`BaseCollector.run()` now logs its run.

Then daemon runs the subprocess and also:

```python
log_run(...)
```

So successful BaseCollector collectors can produce:

```text
collector_run #1
real metrics

collector_run #2
daemon says ok, zero metrics
```

That pollutes health/history.

Choose one.

I recommend:

```text
collector owns collector_run
daemon only schedules
```

The daemon should only create its own event if:

```text
process never starts
process crashes before collector runtime starts
timeout
```

---

# P0 — OPSS is still not Level-1 compliant

The registry now says:

```yaml
status: operational
```

But `opss_historical.py` is still the legacy collector.

It:

* does direct SQL
* bypasses `BaseCollector`
* doesn't use shared persistence
* doesn't archive exact source responses
* stores `raw_payload_hash = ''`
* doesn't fetch/parse individual recall pages properly
* doesn't exhaustively paginate history
* doesn't extract the useful recall fields

Therefore:

```yaml
status: operational
```

is wrong.

Mark it honestly:

```yaml
status: partial
```

or:

```yaml
status: needs_historical_ingest
```

until:

```text
reference
brand
model
product identifier
risk level
hazard
corrective action
publication date
documents
```

are actually harvested with provenance.

Checkpoint reports need brutally truthful statuses.

---

# P0 — PartsDB still doesn't use the API key

The collector reads:

```python
PARTSDB_API_KEY
```

but `_search_mpn()` doesn't send it.

So:

```text
status: needs_api_key
```

is partly misleading.

Even if I gave it the key today, nothing in the shown code sends the credential.

Also the MPN cohort still looks basically unchanged:

```text
STM32
ESP32
555
7805
generic passives
...
```

despite the comment now saying:

```text
repair-derived
```

It isn't repair-derived yet.

That's documentation drift.

For Level 1, either:

1. build a true repair-derived cohort, or
2. label this honestly as `electronics_baseline_v1`.

Don't pretend generic components are repair-derived.

---

# P0 — `REPAIR_DB` still isn't globally authoritative

`shared.persist` respects:

```text
REPAIR_DB
```

But `shared.db` has:

```python
DB_PATH = repo / warehouse / repair.db
```

and:

```python
init_db()
status()
get_db()
```

use that static path.

That means:

```bash
REPAIR_DB=/mnt/garden.db ...
```

can cause:

```text
collector writes → /mnt/garden.db

shared.db status → repo/warehouse/repair.db
```

This can become very confusing.

There must be one:

```python
get_db_path()
```

shared everywhere.

`shared.db` owns it.

Everything else imports it.

---

# P1 — health layer currently measures the wrong thing

In:

```python
health_from_run_result()
```

you set:

```python
records_seen = result.raw_fetched
```

So for a CeX batch containing 200 products:

```text
records_seen = 1
```

because one synthesized batch was fetched.

That field should probably be:

```text
records_seen =
new + changed + unchanged + invalid
```

while:

```text
acquisitions_seen
bytes_fetched
```

are separate metrics.

This matters because your manifest says:

```yaml
expected_min_rows: 50
```

but the health implementation would see:

```text
records_seen = 1
```

and potentially mark a successful source degraded.

---

# P1 — health exists but isn't actually wired into collection

`layer1/health.py` is a good schema.

But I don't see the collector runtime:

```text
creating health object
applying manifest expectations
persisting health
alerting on degradation
```

after every run.

So currently health is more:

```text
definition of a future system
```

than a monitoring system.

For Level 1, wire it directly:

```text
collector finishes
↓
load manifest
↓
compute health
↓
persist source_health
↓
daemon prints/report unhealthy sources
```

No dashboard needed.

---

# P1 — only three Level-1 manifests appear to exist

The latest commit added:

```text
open_repair.yaml
cex.yaml
trade_pricing.yaml
```

The commit message/AGENTS says manifests are standardized for all six sources.

From the change set I reviewed, I don't see manifests for:

```text
eBay
PartsDB
RobotShop
OPSS
```

Maybe they exist outside this diff, but the tree changes shown don't support the "all 6" claim.

For Level 1 every operational/planned collector should have one manifest.

The manifest should be the control plane.

---

# P1 — manifests need to stop overstating source semantics

Open Repair manifest claims it answers:

```text
what_component?
what_intervention?
what_cost?
what_was_it_worth?
```

But the current ORA normalized record is mainly:

```text
product category
brand
problem
repair status
repair barrier
event date
age
```

It does not reliably answer all those questions.

Don't describe what the whole Repair system eventually answers.

Describe what **this source actually contains**.

For Open Repair more honestly:

```text
what_object_category?
what_brand?
what_problem?
was_repair_attempted?
what_was_outcome?
what_blocked_repair?
how_old_was_object?
```

This is important because manifests should drive source-gap analysis.

If every source claims to answer everything, you can't see what data is missing.

---

# P1 — CeX is now close to a genuinely valuable Level-1 source

This part is good.

You now preserve:

```text
box_id
category_id
EAN
name
sell price
buy price
exchange price
grade
```

and stable identity.

That can give you:

```text
CeX bid
CeX ask
bid/ask spread
price movement
```

over time.

That's exactly the Breadup heritage we want.

But two improvements:

### Store three observations, not just sell price

Currently `market_observation` receives only:

```text
sell_price
```

The best CeX data is actually:

```text
SELL
CASH BUY
EXCHANGE
```

Preserve all three as first-class tape fields.

Either expand:

```text
market_observation
```

or emit metrics:

```text
cex_sell
cex_cash_bid
cex_exchange_bid
```

### Don't infer stock from price

Current:

```python
availability='in_stock' if sell_price else 'out_of_stock'
```

Price existence does not necessarily prove inventory availability.

If source doesn't give availability:

```text
availability = NULL
```

Don't infer facts at Level 1.

That's Level 2.

---

# P1 — market observation schema is still too generic for the tape

Current:

```text
price
stock TEXT
availability
condition
market
extra_json
```

This works as a prototype.

But for Level 1 I'd add:

```text
observation_type
acquisition_id
collector_run_id
source_native_id
```

and let it capture:

```text
ask_price
bid_price
exchange_price
stock_quantity
availability
shipping_price
```

without squeezing everything into one price.

You don't need a giant market ontology yet.

Just enough structure to preserve source facts faithfully.

---

# P1 — eBay identity has a questionable `+ condition`

Registry says:

```text
native_id = ebay_item_id + condition
```

The actual source identity is:

```text
ebay_item_id
```

Condition is an attribute.

If the seller changes condition classification—or parser interpretation changes—you don't want a new logical listing.

Use:

```text
native_id = ebay_item_id
```

and preserve:

```text
condition
condition_source
```

as state.

---

# P1 — eBay fallback identity must not silently collapse listings

If no eBay item ID:

```text
model + condition
```

is not safe.

Twenty RTX 3090 listings would collapse onto one identity.

If source-native identity is unavailable, either:

```text
quarantine/invalid
```

or derive a fingerprint from enough raw source fields:

```text
listing URL
seller
title
first_seen
```

with an explicit:

```text
identity_method = inferred
```

Never silently pretend model identity is listing identity.

---

# P1 — Screwfix / RobotShop are fine secondary tapes

These now fit Level 1 better because:

* price is out of identity
* market observations exist
* scope narrowed toward repair

But they're still secondary.

The Level-1 data priority should be:

```text
1. eBay
2. CeX
3. repair-linked component supply
4. Open Repair
5. OPSS
6. RobotShop / trade retail
```

because the top three create the strongest disappearing economic tape.

---

# P1 — Level 2 material is creeping back into the Level 1 push

Latest push added:

```text
domain/gardens.py        +326 lines
export_k1.py             +347 lines
canonical_chain changes
layer2 structure
K1 export
```

These may eventually be useful.

But they are **not the bottleneck right now**.

The fact that K1 export produces:

```text
305K nodes
233K edges
305K evidence
```

sounds impressive, but for Checkpoint 1 it is mostly irrelevant.

The question is:

```text
How many real external sources are continuously producing trustworthy Level-1 observations?
```

Not:

```text
How many graph edges can we derive from the one big dataset?
```

Freeze K1/export work.

Freeze graph transformation.

Freeze derived economics.

Level 1 needs collectors.

---

# What Level 1 should actually contain

I think the project is cleaner if we define Level 1 as only four things:

```text
LEVEL 1
│
├── 1. SOURCE
│      what exists?
│      rights/access/cadence
│
├── 2. ACQUISITION
│      exact bytes received
│      URL/API call
│      timestamp/status/hash
│
├── 3. SOURCE RECORD
│      faithful parsing
│      native identity
│      source timestamp
│
└── 4. TIME OBSERVATION
       repeated state
       price/stock/status/etc
```

Then Level 2 handles:

```text
entity resolution
cross-source joins
normalization
derived graphs
repair probabilities
market curves
economics
```

There may be light normalization in Level 1, obviously, but don't force intelligence into acquisition.

This boundary would make the whole system much easier to reason about.

---

# The source coverage we're actually aiming for

For Repair Level 1 I would now explicitly build toward these source families.

| Garden  | Source type           | Examples                 | Why now?          |
| ------- | --------------------- | ------------------------ | ----------------- |
| Failure | Repair outcomes       | ORA                      | historical prior  |
| Failure | Recalls/defects       | OPSS, EU Safety Gate     | systematic faults |
| Market  | Peer market           | eBay                     | **ephemeral**     |
| Market  | Dealer bid/ask        | CeX                      | **ephemeral**     |
| Market  | Refurb market         | Back Market etc.         | value ceiling     |
| Parts   | Distributor inventory | Mouser/DigiKey/Nexar/TME | **ephemeral**     |
| Parts   | aftermarket           | AliExpress/eBay parts    | **ephemeral**     |
| Asset   | product identity      | GS1/EPREL/manufacturer   | joins             |
| Asset   | BOM/teardown          | OSHWA/iFixit/repair data | composition       |
| Outcome | repair receipts       | eventually proprietary   | moat              |

You don't have to implement every one before declaring an initial Level 1.

But **each category needs at least one real source running** where possible.

Right now:

```text
Failure: ✅ ORA
Market:  ⚠ mostly blocked/not proven continuously
Parts:   ❌ not planted yet
Asset:   ❌ weak
Outcome: ❌ future proprietary
```

So that's where effort should go.

---

# Exact next coding instructions

I would give the coding agent this order and tell it **not to add any new Level-2 functionality**:

1. Make raw storage operate per HTTP/API acquisition, not per synthesized collector batch.
2. Make every acquisition retain exact bytes + URL + status + headers + hash.
3. Link source records to the exact acquisition/raw blob that created them.
4. Fix source-version lookup to use `retrieved_at`, not lexicographic hash IDs.
5. Add acquisition/run references to `market_observation`.
6. Fix `REPAIR_DB` so every module resolves the identical DB.
7. Fix daemon module execution.
8. Remove daemon's duplicate successful-run logging.
9. Persist and wire actual `CollectorHealth`.
10. Correct `records_seen`.
11. Add manifests for every Level-1 source.
12. Make manifests describe only fields the source actually provides.
13. Downgrade OPSS from `operational` until it uses the clean pipeline and stores raw evidence.
14. Finish proper OPSS historical ingestion.
15. Fix PartsDB authentication.
16. Replace/rename generic component cohort, then create first repair-derived MPN cohort.
17. Get PartsDB or another distributor actually returning records.
18. Get CeX running from a viable worker.
19. Get eBay running from a viable acquisition route.
20. Run eBay + CeX + component source repeatedly for at least several cycles and verify timestamp continuity.
21. Add an asset-identity source after the ephemeral tapes are planted.
22. Freeze `export_k1`, `canonical_chain`, and new Level-2 work until these pass.

Then the checkpoint report should contain almost nothing architectural. It should look like:

```text
SOURCE          RAW ACQ   SOURCE RECORDS   OBSERVATIONS   EARLIEST      LATEST        HEALTH
Open Repair     3         305,649          —              2010/...      2026/...       OK
CeX             28,144    7,202            21,330         Sep 22 ...    Sep 25 ...     OK
eBay            96,000    14,183           81,223         Sep 22 ...    Sep 25 ...     OK
Parts           4,200     840              2,520          Sep 22 ...    Sep 25 ...     OK
OPSS            ...       ...              —              ...           ...            OK
```

**That table is Level 1.**

Once that table is real and growing every day, you have the garden. Everything clever — K1 graph, repair economics, Seesaw signals, prediction models, donor-device logic — is Level 2/3 transformation on top of an asset you have already started compounding.
