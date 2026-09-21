# POW Repair — Development Plan

> What is the highest-value next state of this physical asset?

## Evolution

> **Breadup** → "What is this physical object worth, how liquid is it, and where should it be sold?"
> **Data Garden** → "Continuously preserve transformed market state so time itself creates the moat."
> **POW Systems** → Physical-economic intelligence: hardware, labour, energy, parts, scarcity, useful life, resale and alternative uses.
> **POW Repair** → "Given a physical object and its condition/fault, is there an economically attractive path from broken → repaired → useful/resold?"

## The Canonical Chain

```
DEVICE → MODEL → FAULT → LIKELY PART → MPN → STOCK/PRICE → REPAIR PROBABILITY → BROKEN PRICE → WORKING PRICE → EXPECTED PROFIT
```

## Priority Universe (start here)

GPUs, game consoles, laptops, PC hardware, power supplies, crypto miners, homelab/server equipment.

Why: exact model identity, enthusiast repair knowledge, discrete replaceable components, online parts, online used markets, relatively high item value, technically sophisticated users, measurable performance after repair.

## 6 Priority Collectors (this week)

### 1. Open Repair Alliance — historical repair priors
- 305,649 EEE rows, CC BY-SA 4.0
- Transform into: failure distributions, success rates, repair barriers
- GOING GRANULAR: insist on model-level resolution

### 2. eBay — broken + working + parts market
- Track THREE markets: BROKEN, WORKING USED, PARTS
- Preserve distribution: broken_price_p10/p50/p90, working_price_p10/p50/p90, days_visible, listing churn
- calculate: repair_spread = working_used_value - broken_acquisition - parts - labour - selling

### 3. Keepa — retail / used / refurb reference
- Amazon product history: new/used/refurbished prices, sales rank, marketplace offers
- Join: GTIN, EAN, UPC, ASIN, manufacturer, model_number
- Calculate: used_discount, broken_discount, refurbished_premium, repair_value_uplift, price_decay

### 4. Nexar/Octopart — exact electronic-component economics
- 70M+ parts, daily supply data
- MPN → manufacturer, category, specification, stock, supplier, price_breaks, lead_time, lifecycle
- Continuously preserve: MPN × day → stock_total, supplier_count, median_price, lowest_price, lead_time, lifecycle_status

### 5. DigiKey + Mouser + TME — substitutions + independent stock/price
- DigiKey: substitutions endpoint is gold (equivalent components)
- Mouser: MPN, availability, pricing, lead time, lifecycle, replacements
- TME: stock, pricing, incoming deliveries, GB-localized

### 6. OPSS — known defect / recall / safety layer
- 1,500+ recall reports
- Capture: product, brand, model, barcode, hazard, risk_level, defect, corrective_action
- Failure precursor dataset

## Proprietary Time Series

| Metric | Meaning |
|--------|---------|
| FailureRate | What tends to break |
| Fault→Part | Which part actually fixes it |
| SubstituteSuccess | Which substitute components really work |
| RepairSuccess | Probability repair succeeds |
| RepairTime | Actual labour requirement |
| PartsScarcity | How hard the required part is becoming |
| RepairCost | Total economic repair cost |
| BrokenValue | Market value unrepaired |
| WorkingValue | Market value repaired |
| RepairSpread | Gross value created |
| ExpectedRepairEV | Spread × success probability − cost |
| Liquidity | Probability/time to resell |
| RepairabilityObserved | Actual vs manufacturer-stated repairability |
| SkillFit | Whether this person can profitably perform it |
| ToolFit | Whether their workshop supports it |
| HarvestValue | Value of dismantling for reusable parts |
| EconomicLifeRemaining | Expected useful life after repair |

## The Opportunity Formula

```
Opportunity(user, object) =
  P(success | fault, skill, model) × Value_after
  - Cost_object
  - Cost_parts
  - Cost_labour
  - Risk
```

## ASSET Actions (keep generic)

```
ASSET
  ├── BUY
  ├── REPAIR
  ├── REFURBISH
  ├── UPGRADE
  ├── PART-OUT
  ├── RESELL
  ├── RENT
  ├── DEPLOY
  ├── MINE
  └── RECYCLE
```

## Additional Sources (from research)

- GS1 — canonical product identity (300M+ products, GTIN/EAN/UPC)
- EPREL — appliance repair info, spare parts, dismantling
- France Repairability — declared vs observed repairability
- UK OPSS recalls — safety defect layer
- WEEE data — installed base, waste streams, recovery
- OSHWA — open hardware BOMs, schematics, CAD
- iFixit — procedure/skill graph (not content to republish)

## The Moat

All public sources bootstrap POW. The moat begins with:

```
RepairCaseCreated → ObjectResolved → FaultObserved → FaultDiagnosed →
PartRecommended → PartOrdered → PartDelivered → RepairStarted →
RepairCompleted → RepairFailed → RetestPassed → Relisted → Sold → Returned
```

Every real user interaction generates a receipt. The proprietary time series compound.
