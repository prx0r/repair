# Repair Garden — Data Sources

## Active Collectors (10 Sources)

| # | Source | Status | Cadence | API Key? | What It Collects |
|---|--------|--------|---------|----------|-----------------|
| 1 | **eBay UK Sold** | 🟢 Active | Daily | No | Sold electronics pricing — phones, laptops, GPUs, tools, parts |
| 2 | **Open Repair Alliance** | 🟢 Active | Weekly | No | Fault databases from community repair cafés across Europe |
| 3 | **France Repairability Index** | 🟢 Active | Monthly | No | Government repair scores for electronics (0-10 scale) |
| 4 | **EPREL** | 🟢 Active | Weekly | No | EU energy efficiency ratings — solar panels, inverters, batteries |
| 5 | **Planning Data** | 🟢 Active | Daily | No | UK council planning apps — solar, heat pumps, EV chargers |
| 6 | **Land Registry** | 🟢 Active | Daily | No | UK property transactions — postcode-level economics |
| 7 | **Companies House** | 🟡 Needs API Key | Daily | Yes | UK company data — repair businesses, parts suppliers |
| 8 | **DVLA/DVSA** | 🟡 Limited | Daily | No | Vehicle tax/MOT — sample fleet only (needs bulk feed) |
| 9 | **Electricity Maps** | 🟡 Needs API Key | Hourly | Yes | Real-time electricity pricing by region |
| 10 | **Mouser/DigiKey** | 🔴 Not Started | Daily | Yes | Component pricing — ICs, connectors, passives |

## How to Run

```bash
# Run all collectors
python collect.py

# Run specific source
python collect.py --source ebay

# Run in daemon mode (hourly)
python collect.py --daemon --interval 3600
```

## Data Inventory

### What We Have Now
- **801 eBay UK products** (structured pricing)
- **eBay sold collector** (free, no API key)
- **9 GPU entity stubs** (need specs populated)
- **10 chain economics files** (mining profitability)
- **14 semiconductor company analyses**
- **Robotics component analysis**
- **28-row eBay sample CSV**
- **Charity shop margins** (6 brands)

### What Collectors Will Add
- **eBay sold pricing** for 18 electronics categories
- **Open Repair fault database** (repair outcomes, parts, time)
- **France repairability scores** (phones, laptops, TVs)
- **EPREL energy ratings** (solar, batteries, heat pumps)
- **Planning applications** (solar/heat pump/EV installations)
- **Property transactions** (postcode economics)
- **UK company data** (repair businesses)
- **Vehicle MOT data** (repair demand signals)
- **Electricity pricing** (running cost calculations)

### What We Need Next
- iFixit API integration (repair guides + parts)
- eBay sold data (Apify — $5/mo free tier)
- Mouser/DigiKey API keys (free for non-commercial)
- Cloudflare R2 bucket (permanent storage)

## Source Architecture

From the POW.SYSTEMS emails, the full source hierarchy:

```
pow.systems
├── domains/
│   ├── mining/        ← powpowpow (crypto)
│   ├── repair/        ← this repo (electronics, parts, solar)
│   ├── grid/          ← electricity, energy pricing
│   ├── ev/            ← electric vehicles
│   ├── parts/         ← component pricing (mouser, digikey)
│   ├── skills/        ← training, apprenticeships
│   ├── property/      ← land registry, EPC, planning
│   └── company/       ← companies house, financials
```

## Collectors Directory

```
collectors/
├── ebay_uk_collector.py           # eBay UK sold listings (free)
├── open_repair_collector.py       # Open Repair Alliance API
├── france_repairability_collector.py  # French repair scores
├── eprel_collector.py             # EU energy ratings
├── companies_house_collector.py   # UK company data
├── land_registry_collector.py     # Property transactions
├── dvla_collector.py              # Vehicle MOT/tax
├── planning_data_collector.py     # Council planning apps
└── electricity_maps_collector.py  # Real-time energy pricing
```
