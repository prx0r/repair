# Repair Garden — Source Registry

Every data source we collect from, what it provides, and its current status.

## Status Legend

| Status | Meaning |
|--------|---------|
| 🟢 Active | Collector built, running on schedule |
| 🟡 Ready | Collector built, needs API key or activation |
| 🔴 Planned | Source identified, collector not yet built |
| ⚫ Reference | Documentation only, not yet evaluated |

---

## Tier 1: Active Collection

### 1. eBay UK Sold Listings
- **Source ID:** `ebay_uk`
- **Status:** 🟢 Active (6-hourly)
- **Access:** Free, no API key (public search scraping)
- **What We Collect:**
  - Sold/completed listings: title, price, condition, sold date
  - Categories: phones, laptops, GPUs, cameras, power tools, robot parts, solar, batteries
  - ~50 items per category per run
- **Data Shape:** `{title, soldPrice, soldCurrency, soldDate, keyword, collected_at}`
- **Storage:** `data/resale/ebay_sold/{date}.jsonl`
- **Why It Matters:** Primary source for used electronics pricing, depreciation curves, market depth. The sold price is the closest thing to "what is this thing actually worth."

### 2. Open Repair Alliance
- **Source ID:** `open_repair`
- **Status:** 🟢 Active (daily)
- **Access:** Free, CC BY-SA 4.0 (305k+ EEE rows)
- **What We Collect:**
  - Repair attempts: item type, brand, model, fault type, repair action, outcome
  - Repair outcomes: FIXED / PARTIALLY_FIXED / NOT_FIXED / END_OF_LIFE
  - Parts used, repair time, organization, location
- **Data Shape:** `{item_id, item_type, brand, model, fault_type, repair_action, repair_outcome, parts_used, repair_time_minutes}`
- **Storage:** `data/repair_db/open_repair/{date}.jsonl`
- **Why It Matters:** The richest structured repair dataset in existence. Answers "what breaks and how often" with empirical data from real repair cafés across Europe.

### 3. France Repairability Index
- **Source ID:** `france_repairability`
- **Status:** 🟢 Active (weekly)
- **Access:** Free, open data (French government)
- **What We Collect:**
  - Repairability scores (0-10) per product
  - Sub-scores: documentation, disassembly, parts availability, parts price, software support
  - Categories: smartphones, laptops, TVs, washing machines, mowers
- **Data Shape:** `{brand, model, repairability_score, category, scoring_date, documentation_score, disassembly_score, parts_availability_score}`
- **Storage:** `data/repair_db/france_index/{date}_{category}.jsonl`
- **Why It Matters:** Government-mandated repair scores. Only structured cross-brand repairability comparison available. Predicts which products are designed to be repaired.

### 4. EPREL (EU Product Energy Register)
- **Source ID:** `eprel`
- **Status:** 🟢 Active (daily)
- **Access:** Free, EU open data
- **What We Collect:**
  - Energy efficiency ratings for solar panels, inverters, batteries, heat pumps
  - Manufacturer, model, energy class, technical specs
- **Data Shape:** `{product_id, manufacturer, model, energy_class, energy_consumption, category}`
- **Storage:** `data/hardware/eprel/{date}_{category}.jsonl`
- **Why It Matters:** Solar panel and battery identification + efficiency specs. Foundation for energy hardware repair/replace decisions.

### 5. UK Planning Data
- **Source ID:** `planning_data`
- **Status:** 🟢 Active (12-hourly)
- **Access:** Free, UK government open data
- **What We Collect:**
  - Planning applications: solar panel installs, heat pump installs, EV charger installs, extensions, renovations
  - Application details, address, postcode, decision, council
- **Data Shape:** `{application_id, description, address, postcode, decision, decision_date, council}`
- **Storage:** `data/hardware/planning/{date}.jsonl`
- **Why It Matters:** Demand signal for installation services and parts. A surge in planning applications = future parts demand.

### 6. HM Land Registry
- **Source ID:** `land_registry`
- **Status:** 🟢 Active (daily)
- **Access:** Free, UK government open data
- **What We Collect:**
  - Property transactions: price, address, date, property type
  - Price Paid Data (PPD)
- **Data Shape:** `{transaction_id, price, date_of_transfer, postcode, property_type, new_build}`
- **Storage:** `data/hardware/property/{date}.jsonl`
- **Why It Matters:** Postcode-level economics. Property value correlates with renovation activity, solar adoption, EV charger installation.

### 7. DVLA/DVSA
- **Source ID:** `dvla`
- **Status:** 🟢 Active (daily, sample fleet only)
- **Access:** Free (MOT check API), bulk needs registration
- **What We Collect:**
  - MOT status, test results, defects, mileage
  - Vehicle tax status, expiry dates
- **Data Shape:** `{registration, make, model, year, fuel_type, mot_status, mot_expiry, tax_status}`
- **Storage:** `data/hardware/vehicles/{date}.jsonl`
- **Why It Matters:** Vehicle repair demand signals. MOT failures indicate repair opportunities. Fleet age data predicts maintenance demand.

---

## Tier 2: Ready to Activate

### 8. Companies House
- **Source ID:** `companies_house`
- **Status:** 🟡 Needs API key (free)
- **Access:** Free API key from developer.company-information.service.gov.uk
- **What We Collect:**
  - Company data: repair businesses, parts suppliers, solar installers, robot manufacturers
  - Directors, filings, accounts, SIC codes, status
- **Why It Matters:** Identifies repair businesses, tracks company health (liquidation = opportunity), maps supply chain.

### 9. Electricity Maps
- **Source ID:** `electricity_maps`
- **Status:** 🟡 Needs API key (free tier)
- **Access:** Free tier from electricitymaps.com
- **What We Collect:**
  - Real-time electricity pricing by region (GB, DE, FR, NL, etc.)
  - Carbon intensity, renewable share
- **Why It Matters:** Running cost calculations for mining rigs, heat pumps, EV charging. Grid constraint signals.

### 10. Mouser Electronics
- **Source ID:** `mouser`
- **Status:** 🟡 Needs API key (free for non-commercial)
- **Access:** Free API from mouser.com/api-search
- **What We Collect:**
  - Component pricing: ICs, connectors, passives, sensors, displays, batteries
  - Stock levels, lead times, MOQ, datasheets, lifecycle status
  - Cross-references (alternative part numbers)
- **Why It Matters:** The parts pricing layer. When Mouser stock runs low, repair gets harder. Multi-distributor divergence = scarcity signal.

### 11. DigiKey
- **Source ID:** `digikey`
- **Status:** 🟡 Needs API key
- **Access:** Free API from developer.digikey.com
- **What We Collect:**
  - Same as Mouser: pricing, stock, lifecycle, cross-references
- **Why It Matters:** Cross-validation with Mouser. Divergence between distributors = meaningful signal.

### 12. Nexar/Octopart
- **Source ID:** `nexar`
- **Status:** 🟡 Needs API key
- **Access:** Free tier from nexar.com/api
- **What We Collect:**
  - Aggregated component data across multiple distributors
  - Supply chain visibility, lifecycle, alternates
- **Why It Matters:** The cross-distributor aggregation layer. One API covers multiple distributors.

### 13. iFixit
- **Source ID:** `ifixit`
- **Status:** 🟡 Ready (terms under review)
- **Access:** Public API (GET), commercial terms TBD
- **What We Collect:**
  - Device taxonomy, repair guides, step-by-step procedures
  - Parts lists, difficulty ratings, required tools
- **Why It Matters:** The knowledge layer. What tools are needed, what steps to follow, what can go wrong.

### 14. DVSA MOT Bulk
- **Source ID:** `dvsa_mot_bulk`
- **Status:** 🟡 Needs registration
- **Access:** OAuth2 + API key, bulk JSONL ~500k records
- **What We Collect:**
  - Complete MOT history per vehicle: all test results, all defects, mileage over time
  - Cars/motorcycles/vans from 2005
- **Why It Matters:** The installed base of vehicles + their failure patterns. Predicts parts demand at scale.

### 15. OPSS Product Recalls
- **Source ID:** `opss_recalls`
- **Status:** 🟡 Ready (manual or feed)
- **Access:** Free, GOV.UK
- **What We Collect:**
  - Product recall notices, safety alerts
  - Affected products, risk descriptions, remedies
- **Why It Matters:** Failure signal. A recall = known defect pattern at scale.

### 16. UK EV OCPI Feeds
- **Source ID:** `uk_ev_ocpi`
- **Status:** 🟡 Per-operator activation
- **Access:** Free data, API keys vary by CPO
- **What We Collect:**
  - Live EV charge point state: availability, tariffs, connector specs, location
  - 30-60 second granularity (ephemeral — must archive now)
- **Why It Matters:** True time moat — historical state not required by regulation. Archive now or lose forever.

### 17. CEC Solar Equipment Lists
- **Source ID:** `cec_solar`
- **Status:** 🟡 Ready
- **Access:** Free Excel download, updated 3x/month
- **What We Collect:**
  - Certified solar panels, inverters, batteries
  - Product specs, certifications, model numbers
- **Why It Matters:** Product identity enrichment for solar hardware.

### 18. Sheffield Solar PV_Live
- **Source ID:** `pvlive`
- **Status:** 🟡 Ready
- **Access:** Free API
- **What We Collect:**
  - Live solar PV generation data across UK
  - Panel output, degradation signals
- **Why It Matters:** Real-world performance data for solar panels.

---

## Tier 3: Planned Sources

### 19. ONS Labour Demand
- **Source ID:** `ons_labour`
- **Status:** 🔴 Planned
- **What:** Occupation-level job ad volumes, skills, salaries
- **Why:** Distinguishes "hardware shortage" from "qualified-human bottleneck"

### 20. Skills England Occupational Maps
- **Source ID:** `skills_england`
- **Status:** 🔴 Planned
- **What:** Occupation → duties → KSBs → training products
- **Why:** Maps repair skills to training pathways

### 21. OpenAlex
- **Source ID:** `openalex`
- **Status:** 🔴 Planned
- **What:** Connected graph of research works, topics, institutions
- **Why:** Technology frontier — where is effort moving after price shocks

### 22. HMRC Trade Data
- **Source ID:** `hmrc_trade`
- **Status:** 🔴 Planned
- **What:** UK imports/exports by commodity/country/month
- **Why:** Validates domestic shortage against import data

### 23. BGS Mineral Statistics
- **Source ID:** `bgs_minerals`
- **Status:** 🔴 Planned
- **What:** Global mineral production/trade (long-run)
- **Why:** Physical bottleneck detection for raw materials

### 24. SEC EDGAR
- **Source ID:** `sec_edgar`
- **Status:** 🔴 Planned
- **What:** Company filings, XBRL financials
- **Why:** Physical state can lead company narrative

### 25. Contracts Finder / Find a Tender
- **Source ID:** `contracts_finder`
- **Status:** 🔴 Planned
- **What:** UK public procurement (OCDS format)
- **Why:** Future capacity visible as procurement commitments before production

### 26. NESO TEC Register
- **Source ID:** `neso_tec`
- **Status:** 🔴 Planned
- **What:** Transmission Entry Capacity, updated twice weekly
- **Why:** Grid connection commitments = future capacity

### 27. Ofgem
- **Source ID:** `ofgem`
- **Status:** 🔴 Planned
- **What:** Energy market regulation, connection reform, constraints
- **Why:** Regulatory constraint surface

### 28. Environment Agency
- **Source ID:** `env_agency`
- **Status:** 🔴 Planned
- **What:** Abstraction licences, environmental permits
- **Why:** Physical constraint signals

---

## Proprietary Probes (to build)

### P1. Repair Outcome Probe
- **What:** Symptom → attempted intervention → part → time → success/failure
- **How:** Manual entry from own repairs + community submissions
- **Why:** First-party repair outcome data is the moat

### P2. Component Basket
- **What:** Same MPNs across Mouser/DigiKey/Farnell/TME hourly
- **How:** Multi-distributor price/stock monitor
- **Why:** Synchronized depletion = physical constraint signal

### P3. Used Equipment Cohort
- **What:** Listing-level state transitions (active → disappeared → sold)
- **How:** eBay/Gumtree/Facebook marketplace monitoring
- **Why:** Listing disappearance ≠ sold (could be relisted, delisted, or sold)

### P4. 3D-Printer Probe
- **What:** OctoPrint/Moonraker job/failure/maintenance outcomes
- **How:** Plugin-based telemetry from opted-in printers
- **Why:** Empirical failure rates for 3D printer components

---

## Source Count Summary

| Status | Count |
|--------|-------|
| 🟢 Active | 7 |
| 🟡 Ready | 11 |
| 🔴 Planned | 10 |
| Proprietary probes | 4 |
| **Total** | **32** |
