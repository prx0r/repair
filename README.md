# Repair Garden

Part of **pw.systems** — `repair.pw.systems`

> broken object + fault + part + labor + resale → repair margin

## What This Is

A Data Garden for physical objects: electronics, robot parts, solar panels, crypto mining hardware. Accumulates fault databases, parts pricing, repair economics, and resale curves to answer one question:

**Should I fix it, replace it, part it out, or scrap it?**

## Architecture

Same primitives as PowPowPow (Observation, Entity, Source, DerivedFact), applied to physical goods:

```
Fault Database → Part Compatibility → Repair Economics → Resale Valuation
     ↓                  ↓                    ↓                  ↓
  what breaks      what fits            what it costs      what it's worth
```

## Data Sources (Imported)

### Electronics Resale
- **801 eBay UK products** — structured pricing (title, price, brand, category)
- **eBay collectors** — free scraper (no API key) + Apify sold-listings
- **Charity shop margins** — brand-level buy/sell arbitrage data (Barbour 521%, Patagonia 550%)

### GPU / Mining Hardware
- **9 NVIDIA GPU entities** — RTX 4090, RTX 5090, A100, H100, H200, B200, B300
- **2 AMD CPU entities** — Ryzen 9 9950X, 7950X
- **Miner economics** — per-coin profitability (hashrate, power, cost, revenue, payback)
- **Chain fundamentals** — 10 PoW chains with hardware requirements

### Semiconductor Industry
- **14 company analyses** — Silvaco, Amkor, Modine (cooling), Aeluma (photonics), etc.
- **Twitter feeds** — SemiAnalysis, Photon Capital, Chips&Wafers (15K+ tweets)

### Robotics
- **Component analysis** — ALNT (motors), TKR (reducers), NOVT (encoders)
- **Bottleneck migration** — intelligence → embodiment → reliable motion thesis

### Reference Architecture
- **DataGarden core** — Observation, Entity, Source, DerivedFact, QualityGate, Storage
- **Thesis docs** — moat theory, garden patterns, formula for domain qualification

## Directory Structure

```
repair/
├── core/                    # Data Garden primitives (from datagarden)
├── schemas.py               # Repair-specific schemas (FaultRecord, PartListing, etc.)
├── collectors/              # Data collectors (eBay, etc.)
├── data/
│   ├── resale/              # eBay pricing data
│   ├── hardware/            # GPU/mining economics
│   ├── semiconductors/      # Industry analysis
│   ├── robotics/            # Component data
│   └── repair_db/           # Fault databases (to build)
├── warehouse/
│   └── knowledge/entities/  # Entity registry (GPUs, CPUs, exchanges)
├── experiments/             # Breadup market pressure experiments
├── datagarden/              # Reference docs (thesis, formula, ideology)
├── scripts/                 # Operational scripts
└── tests/                   # Test suite
```

## Schemas

- **FaultRecord** — known fault patterns (what breaks, how to fix, cost)
- **PartListing** — replacement parts with compatibility and pricing
- **RepairEconomics** — fix/replace/part-out/scrap decision analysis
- **ResaleListing** — buy/sell listings across condition grades
- **PriceHistory** — depreciation curves by device model

## Next Steps

1. **Populate GPU entity metadata** — specs, benchmarks, current resale prices
2. **Build fault database** — start with most common phone/laptop faults
3. **Run eBay collector** — populate sold pricing for target categories
4. **Connect to iFixit** — API for repair guides and parts lists
5. **Build valuation engine** — given device + fault → repair vs replace verdict

## pw.systems

- `crypto.pw.systems` — PowPowPow (PoW chain economics)
- `repair.pw.systems` — this repo (physical object repair/resale)
