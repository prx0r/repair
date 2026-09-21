# Blockers — Updated with Alternatives

## 1. eBay — SOLVED with Apify

**Problem:** eBay blocks this VPS IP (anti-bot). UK eBay specifically is very aggressive.

**Alternatives found:**
- **Apify actors** (recommended): $5/mo free credits
  - `kestrel/ebay-search-scraper` — search + listings, 18 marketplaces
  - `scrape.badger/ebay-search-scraper` — search + browse + autocomplete
  - `webdatalabs/ebay-scraper-pro` — real-browser TLS fingerprint
- **ScrapingBee API** — send URL, get rendered HTML/JSON
- **ScraperAPI** — structured eBay data endpoint
- **Note:** eBay UK specifically returns anti-bot on 18/18 attempts per Apify. May need to use eBay.com instead.

**Human action:** Register Apify account (free $5/mo), add APIFY_TOKEN to .env

## 2. OPSS — SOLVED with Apify or GOV.UK ODS

**Problem:** GOV.UK returns HTML not data.

**Alternatives found:**
- **Apify actor** (recommended): `hamzamihaidaniel/uk-product-safety-alerts-api`
  - Uses GOV.UK Search and Content APIs
  - Returns: risk level, product category, brand, models, hazard, corrective action, documents
- **GOV.UK ODS data file** — full dataset published with annual report
  - https://www.gov.uk/government/statistics/product-safety-database-annual-reports/product-safety-database-report-2025-to-2026
- **RecallRadar API** — normalizes OPSS + EU + US recall data
  - https://recallradar.dev/
- **ProductSafer.com** — auto-updated recall alerts

**Human action:** Use Apify actor or download ODS file directly

## 3. Component Distributors — MULTIPLE FREE OPTIONS

**Problem:** No API keys for Mouser/DigiKey/Nexar.

**Alternatives found:**
- **PartsDB.io** (easiest): Free 100 requests/day, no credit card
  - https://www.partsdb.io/
  - European distributors (reichelt, Conrad)
  - REST API, EUR pricing
- **Omkar.cloud DigiKey scraper**: Free 100 queries/month
  - https://www.omkar.cloud/tools/digikey-scraper/
  - 30+ fields per component, pricing tiers, stock, datasheets
- **Nexar/Octopart**: Free evaluation (100 matched parts)
  - https://nexar.com/api
  - GraphQL, supply chain data across thousands of distributors

**Human action:** Register PartsDB.io (free, instant) for immediate component data

## 4. France Repairability — LOW PRIORITY (skip for now)

**Problem:** Data on data.gouv.fr but exact URLs unclear.

**Decision:** Skip. Not critical for checkpoint 1. Focus on eBay + OPSS + components first.

## 5. EPREL — LOW PRIORITY (skip for now)

**Problem:** API endpoint unclear.

**Decision:** Skip. Not critical for checkpoint 1.

## 6-15. Infrastructure Issues

These are code changes, not human actions:
- CLI backfill/verify/reparse commands
- Source record versioning
- Parser replay
- Test suite expansion
- Health monitoring
- Registry cleanup
