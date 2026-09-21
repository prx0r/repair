# Blockers — What's Stopping Progress

## Critical (blocks data collection)

### 1. eBay blocked on this VPS
- **What:** eBay blocks all HTTP requests from this IP (anti-bot)
- **Impact:** Can't collect broken/working/parts market data (most ephemeral source)
- **Fix:** Run collector from a different machine, or use eBay Browse API with OAuth
- **Link:** https://developer.ebay.com/api-docs/buy/browse/overview.html
- **Human action:** Register eBay developer account, get OAuth credentials

### 2. No API keys for component distributors
- **What:** Mouser, DigiKey, Nexar/Octopart all need API keys
- **Impact:** Can't collect parts pricing/scarcity data
- **Fix:** Register for free API access
- **Links:**
  - Mouser: https://www.mouser.com/api-search/ (free, 1000 calls/day)
  - DigiKey: https://developer.digikey.com/ (free for non-commercial)
  - Nexar: https://nexar.com/api (free tier available)
- **Human action:** Register at each, get API keys, add to .env

### 3. OPSS endpoint returns HTML not data
- **What:** GOV.UK product recalls page serves HTML, not JSON/API
- **Impact:** Can't collect product recall data
- **Fix:** Need to parse HTML or find alternative endpoint
- **Link:** https://www.gov.uk/guidance/product-recalls-and-alerts
- **Human action:** Research if OPSS has a machine-readable feed or API

### 4. France Repairability datasets need discovery
- **What:** Data is on data.gouv.fr but exact download URLs unknown
- **Impact:** Can't collect repairability scores
- **Fix:** Find actual dataset download URLs
- **Link:** https://www.data.gouv.fr/datasets/?q=indice+reparabilite
- **Human action:** Browse data.gouv.fr, find CSV/JSON download links

### 5. EPREL API endpoint unclear
- **What:** EU energy register has data but API access path unclear
- **Impact:** Can't collect appliance repair info
- **Fix:** Find official API documentation
- **Link:** https://eprel.ec.europa.eu/
- **Human action:** Check EPREL API docs, find product search endpoint

## Moderate (blocks completeness)

### 6. No 'repair backfill' CLI command
- **What:** CLI only has init/status/sources/collect
- **Impact:** Can't easily trigger historical data collection
- **Fix:** Implement backfill subcommand

### 7. No 'repair verify' CLI command
- **What:** No way to verify data integrity
- **Impact:** Can't check if source records trace to raw blobs
- **Fix:** Implement verify subcommand

### 8. No 'repair reparse' CLI command
- **What:** Can't reprocess data with new parser version
- **Impact:** Parser upgrades can't reprocess historical data
- **Fix:** Implement reparse subcommand

### 9. OPSS collector has no raw provenance
- **What:** OPSS inserts source_records with empty raw_payload_hash
- **Impact:** Violates invariant that every record traces to raw evidence
- **Fix:** Fetch individual recall pages, archive each

### 10. No test suite for collectors
- **What:** Only 8 core persistence tests, no collector-specific tests
- **Impact:** Can't verify collectors work correctly
- **Fix:** Add fixture-based tests for each collector

## Low (improvements)

### 11. No health monitoring
- **What:** No way to check if sources are stale/broken
- **Impact:** Can't detect silent failures
- **Fix:** Add health/status checks per source

### 12. No cohort configs (YAML)
- **What:** eBay search terms are hardcoded in Python
- **Impact:** Hard to change search panel without code changes
- **Fix:** Move to YAML config files

### 13. Shared/db.py vs shared/persist.py overlap
- **What:** Two database modules exist
- **Impact:** Confusion about which to use
- **Fix:** Consolidate into one

### 14. Old collectors still in tree
- **What:** Multiple old collector files exist alongside new ones
- **Impact:** Confusion about which to use
- **Fix:** Remove old collectors

### 15. Registry has POWUK sources mixed with Repair
- **What:** Companies House, Planning Data are POWUK concerns
- **Impact:** Blurs garden boundaries
- **Fix:** Separate registries
