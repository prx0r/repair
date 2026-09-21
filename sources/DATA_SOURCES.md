# Data Sources — What We Collect and Why

## Priority 1: Core Repair Data

### 1. Open Repair Alliance
- **What:** 305K+ real repair attempts from EU repair cafés
- **Why:** Empirical fault/success/failure data. The foundation.
- **Data:** product_category, brand, problem, repair_status, repair_barrier
- **Status:** ✅ 305,649 records ingested
- **URL:** https://openrepair.org/open-data/downloads/
- **Licence:** CC BY-SA 4.0
- **Cadence:** Weekly (new releases)

### 2. eBay UK 3-Market
- **What:** Broken, working, and parts market prices
- **Why:** Depreciation curves, repair spread, liquidity
- **Data:** listing_id, title, price, condition, seller, timestamps
- **Status:** ❌ Blocked on VPS (needs real machine)
- **URL:** https://www.ebay.co.uk
- **Licence:** TOS
- **Cadence:** 6-hourly

### 3. OPSS Product Recalls
- **What:** UK product safety recalls and alerts
- **Why:** Known defects, safety layer, failure precursors
- **Data:** reference, product, brand, model, hazard, risk_level, corrective_action
- **Status:** ❌ Endpoint returns HTML, needs parser
- **URL:** https://www.gov.uk/guidance/product-recalls-and-alerts
- **Licence:** OGL
- **Cadence:** Daily

### 4. France Repairability Index
- **What:** Government repair scores (0-10) per product
- **Why:** Declared vs observed repairability
- **Data:** brand, model, score, documentation_score, parts_availability_score
- **Status:** ❌ Endpoint returns HTML, needs parser
- **URL:** https://www.data.gouv.fr
- **Licence:** Open data
- **Cadence:** Weekly

### 5. EPREL (EU Product Energy Register)
- **What:** Energy efficiency ratings + repair info
- **Why:** Appliance identification, spare parts, dismantling info
- **Data:** EPREL_ID, manufacturer, model, energy_class, repair_info_urls
- **Status:** ❌ Needs proper API endpoint
- **URL:** https://eprel.ec.europa.eu
- **Licence:** EU open data
- **Cadence:** Daily

## Priority 2: Component Supply

### 6. Mouser Electronics
- **What:** Component pricing, stock, lead times
- **Why:** Parts scarcity signals, repair feasibility
- **Data:** MPN, price_breaks, stock, lead_time, lifecycle, replacements
- **Status:** 🔴 Needs API key
- **URL:** https://www.mouser.com/api-search/
- **Licence:** Commercial API
- **Cadence:** Daily

### 7. DigiKey
- **What:** Component pricing + substitution endpoint
- **Why:** Cross-validation, substitute discovery
- **Data:** MPN, price, stock, substitutions, recommended products
- **Status:** 🔴 Needs API key
- **URL:** https://developer.digikey.com
- **Licence:** Commercial API
- **Cadence:** Daily

### 8. Nexar/Octopart
- **What:** Aggregated component data across distributors
- **Why:** Cross-distributor scarcity detection
- **Data:** MPN, offers, distributors, lifecycle, cross-refs
- **Status:** 🔴 Needs API key
- **URL:** https://nexar.com/api
- **Licence:** Commercial API
- **Cadence:** Daily

## Priority 3: Reference Data

### 9. Companies House
- **What:** UK company data (SIC codes, status, officers)
- **Why:** Map repair businesses, track company health
- **Data:** company_number, name, SIC, status, address
- **Status:** ✅ 210 records
- **URL:** https://api.company-information.service.gov.uk
- **Licence:** OGL
- **Cadence:** Daily

### 10. Planning Data
- **What:** UK planning applications
- **Why:** Demand signal for solar/heat pump/EV installations
- **Data:** application_id, description, address, decision
- **Status:** ✅ 70 records
- **URL:** https://www.planning.data.gov.uk
- **Licence:** OGL
- **Cadence:** Daily

### 11. Octopus Energy
- **What:** Energy tariffs and products
- **Why:** Running cost calculations
- **Data:** product_code, tariff, unit_rate, standing_charge
- **Status:** ✅ 61 records
- **URL:** https://api.octopus.energy/v1
- **Licence:** Open API
- **Cadence:** Daily

### 12. OpenAlex
- **What:** Research papers on repair/sustainability
- **Why:** Knowledge frontier, academic grounding
- **Data:** title, authors, topics, citations, DOI
- **Status:** ✅ 20 records
- **URL:** https://api.openalex.org
- **Licence:** Open data
- **Cadence:** Weekly

## Priority 4: Future Sources

### 13. iFixit API
- **What:** Repair guides, device taxonomy, parts lists
- **Why:** Procedure/skill graph, tool requirements
- **Status:** 🔴 Needs terms review
- **URL:** https://www.ifixit.com/api/2.0/doc/

### 14. Keepa
- **What:** Amazon price history (new/used/refurb)
- **Why:** Retail reference, depreciation curves
- **Status:** 🔴 Needs API key
- **URL:** https://keepa.com/api-docs

### 15. OSHWA
- **What:** Open source hardware certified projects
- **Why:** BOMs, schematics, CAD for repair understanding
- **Status:** 🔴 Needs implementation
- **URL:** https://certificationapi.oshwa.org

### 16. DVSA MOT Bulk
- **What:** UK vehicle MOT history
- **Why:** Vehicle failure patterns, parts demand
- **Status:** 🔴 Needs OAuth2 registration
- **URL:** https://history.mot.api.gov.uk
