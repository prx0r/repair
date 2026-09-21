# Repair Garden — North Star

> broken object + fault + part + labor + resale → repair margin

## What This Is

Repair Garden is the data layer for repairing, maintaining, modifying and economically reusing physical electronic systems. Part of **pow.systems**.

**Core question:** Given this physical electronic asset in this condition, what is worth doing with it?

**Canonical graph:**
```
ASSET → FAULT → PART → COMPATIBILITY → SUPPLY → REPAIR OUTCOME → VALUE → ACTION
```

**Proprietary primitive:** `Asset × Fault × Part × RepairOutcome × Economics × Time`

## Domains

| Domain | What We Track | Example |
|--------|--------------|---------|
| **Electronics** | Phones, laptops, GPUs, tablets, cameras | iPhone 13 Pro screen replacement economics |
| **Robot Parts** | Motors, encoders, drivers, controllers | Servo motor repair vs replace |
| **Solar/Energy** | Panels, inverters, batteries, MPPT | Solar panel degradation curves |
| **Crypto Mining** | ASICs, GPUs, PSUs, cooling | Antminer S19 repair vs resale |
| **Power Tools** | Drills, saws, vacuums | Makita motor brush replacement |
| **Appliances** | Washing machines, dishwashers, fridges | Bearing replacement economics |
| **EV/Transport** | Charge points, batteries, motors | EV battery cell-level repair |

## The Economic Loop

```
1. What is this thing?          → asset identification
2. What's wrong with it?        → fault diagnosis
3. What fixes it?               → part compatibility
4. Where do I get the part?     → supply + pricing
5. Can I fix it?                → repair feasibility
6. What does it cost to fix?    → repair economics
7. What's it worth fixed?       → resale valuation
8. Should I fix it?             → action decision
```

Every step produces an observation. The observations compound into a world model.

## What Makes This Valuable

1. **Fault accumulation** — every repair attempt teaches us what breaks and how often
2. **Parts pricing** — multi-distributor comparison creates scarcity signals
3. **Repair outcomes** — success/failure rates per device per fault per part
4. **Economic curves** — depreciation curves by device model × condition
5. **Cross-device patterns** — the same fault appearing across multiple brands = systemic issue

## Data Sources (35+ active)

### Tier 1: Active Collection (10 sources, collectors built)
- eBay UK Sold listings (6-hourly)
- Open Repair Alliance (daily)
- France Repairability Index (weekly)
- EPREL Energy Ratings (daily)
- UK Planning Data (12-hourly)
- Land Registry PPD (daily)
- DVLA/DVSA MOT (daily)
- Companies House (daily, needs API key)
- Electricity Maps (hourly, needs API key)
- Mouser/DigiKey (daily, needs API key)

### Tier 2: Ready to Activate (25+ sources in registry)
- iFixit API (repair guides + parts)
- Nexar/Octopart (component supply chain)
- DVSA MOT bulk (500k+ vehicle records)
- OPSS Product Recalls
- UK EV OCPI feeds (live charge point state)
- CEC Solar Equipment Lists
- Sheffield Solar PV_Live
- ONS Labour Demand
- Skills England Occupational Maps
- OpenAlex (research frontier)
- HMRC Trade Data
- BGS Mineral Statistics
- SEC EDGAR (company filings)
- And 12 more...

### Tier 3: Proprietary Probes (to build)
- Repair outcome probe (symptom → intervention → success/failure)
- Component basket (same MPNs across distributors hourly)
- Used equipment cohort (listing state transitions)
- 3D-printer probe (OctoPrint job/failure outcomes)

## Output Products

### Repair Opportunity Calculator
Given: `device + fault + condition`
Output: `repair_cost vs replace_cost vs part_out_value vs scrap_value` with confidence

### Fault Database
Every known fault pattern per device model:
- What breaks, how often, how to fix it
- Parts needed, cost, difficulty, time
- Success rate by repair method

### Depreciation Curves
Price tracking by device model × condition over time:
- New → Used Good → Used Fair → Broken → Parts Only
- Half-life (time to lose 50% of value)
- Liquidity score (how fast it sells)

### Scarcity Signals
When parts become scarce or expensive:
- Multi-distributor stock divergence
- Supersession chain breaks
- Listing disappearance acceleration

## Architecture

```
collectors/          → 9 data source scripts (always-on daemon)
daemon.py            → scheduler with per-source cadence
storage.py           → SQLite (append-only, WAL mode)
warehouse/repair.db  → live database
r2_sync.sh           → Cloudflare R2 permanent backup
ptech_schemas/       → 17 canonical JSON schemas
ptech_registry/      → 35+ source definitions with licensing
pow_research/        → causal models (diffusion, shadow prices, etc.)
shared/              → cross-system contracts (Observation, DerivedFact, etc.)
```

## pw.systems Hierarchy

```
pow.systems
├── crypto.pw.systems    ← PowPowPow (PoW chain economics)
├── repair.pw.systems    ← this repo (physical objects)
├── grid.pw.systems      ← electricity, energy pricing (future)
├── ev.pw.systems        ← electric vehicles (future)
├── parts.pw.systems     ← component pricing (future)
├── skills.pw.systems    ← training, apprenticeships (future)
└── company.pw.systems   ← company financials (future)
```

## Build Priority

1. **Now:** Electronics + power tools (richest fault data, easiest identification)
2. **Next:** Solar/energy hardware (clear economic loop, strong public data)
3. **Then:** Robot parts (emerging market, early mover advantage)
4. **Later:** Crypto mining hardware (bridge to PowPowPow domain)
