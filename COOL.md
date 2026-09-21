# Cool Stuff Found in the Zips

Future visionary ideas, novel data types, and "we should definitely do that" moments.

---

## 1. Repair as an Economic Decision, Not a Technical One

The canonical formula:
```
EV = P(success) × working_value + P(fail) × salvage_value - acquisition - parts - labour - fees - logistics
```

The moat isn't repair knowledge — it's the cross-source join that turns scattered data into an economic decision. Every observation feeds the graph: `ASSET → FAULT → PART → COMPATIBILITY → SUPPLY → REPAIR OUTCOME → VALUE → ACTION`

---

## 2. Robot Parts Price Clock

100 robotics components tracked across markets:
- Unitree joint motor: $369 China, varies by source
- MYACTUATOR BLDC: $450 China / £390 UK
- Robotiq grippers, force/torque sensors, LiDAR, depth cameras
- Each part: manufacturer, model, interface (CAN/EtherCAT/PWM), voltage, UK+China prices
- Landed cost formula: commodity code + origin + Incoterm + VAT

**Why cool:** Living price clock for the robot economy. Import-export intelligence for the robot supply chain.

---

## 3. Shadow Prices — What's About to Become Expensive

LP dual solver answers: `λ_i = ∂ max(system economic value) / ∂ capacity_i`

Demo scenario: cheap GPU compute (-50%) → robotics adoption increases → force sensors and motors become binding constraint.

**Why cool:** Not "what's expensive now" but "what's about to become expensive" by modeling constraint rotation through a production network.

---

## 4. TechToken — Detecting Innovation Before It Happens

Measures context similarity between IPC patent technology classes before they combine. Rising cosine similarity predicts new technology combinations.

Also: technological obsolescence — tracks decline in citations to a firm's patent base.

**Why cool:** TechToken detects convergence between technologies *before* they combine. Obsolescence detects what's dying. Together: emerging formation + decaying relevance = the technology lifecycle.

---

## 5. Friction as Data

Real-world workflow failures extracted from Reddit:
- Taxpayer reconciling filed returns while penalty letters arrive with different UTR
- TUPE employer onboarding 35 employees, all 35 receiving BR tax codes due to RTI timing
- Self-employed person hit with £1,200 late penalty before any filing correspondence

**Why cool:** Not what systems are supposed to do, but where they actually fail people. Each observation is a normalized workflow chain with evidence.

---

## 6. The 5 Proprietary Probes

1. **3D-printer probe** — OctoPrint/Moonraker job/failure/maintenance outcomes (closed feedback loop)
2. **Repair outcome probe** — symptom → intervention → part → time → success/failure
3. **Component basket** — same MPNs across distributors hourly (scarcity signal)
4. **Used equipment cohort** — listing-level state transitions (active → disappeared → sold)
5. **Physical project cohort** — planning → actual completion/cancellation

**Why cool:** Public data seeds the graph; proprietary longitudinal outcomes create the moat. The 3D-printer probe is particularly clever — closed feedback loop from print job → failure → component replacement.

---

## 7. Causal Assimilation Latency

For every hypothesis, record:
```
L(X → Y) = t(first durable Y response) - t(first physical evidence X)
```

Across layers: physical evidence → distributor reaction → labor response → news → filing → financial response.

**Why cool:** Building a dataset of "how fast does information propagate from physical reality to financial markets?" Measuring the efficiency frontier of information markets.

---

## 8. Hidden Complementarity Discovery

Uses partial information decomposition to find combinations that matter together but not individually:
- `sensor + skill` — neither scarce alone, but neither matters without the other
- `GPU + power` — compute is cheap but electricity is the bottleneck
- `machine + qualified operator` — the equipment exists but no one can run it

**Why cool:** The most important constraint might be a combination, not a single input.

---

## 9. The Big Loop: Scarcity Migration

The full cycle:
```
Innovation → ΔConstraint → ΔShadowPrice → Capital Allocation → Supply Response → Constraint Relaxation → repeat
```

6 data families: adoption/demand, dependencies, buffers/capacity, labor/training, innovation response, assimilation.

**Why cool:** They're modeling the economy as a network, not independent asset series. Innovation in one domain depends on innovation rates of domains it relies on.

---

## 10. Repair-as-a-Service for AI Agents

The agent-ready API surface:
```
ptech.identify(asset_or_photo)
ptech.parts(asset)
ptech.failures(asset)
ptech.supply(part, geography)
ptech.value(asset_or_part, condition, geography)
ptech.repair_options(asset, fault, geography)
ptech.repair_economics(asset, fault, geography)
ptech.opportunities(filters)
```

**Why cool:** A personal agent could ask "what's the best economic action for this broken Unitree Go2 in Manchester?" and get a structured answer with tools, skills, capital, parts, and expected value.

---

## 11. The Seesaw Object

Tracking the full cycle of constraint migration with causal latency fields:
- first_possible_event_time
- first_observed_at
- first_confirmed_at
- company_disclosure_at
- market_response_at

**Why cool:** Formal mechanism for answering "what happened first?" across physical evidence, labor, company disclosure, and market pricing.

---

## 12. Conservative Investor Bespoke Manufacturing

From the friction graph: a company where nothing is listed, everything is bespoke, and the owner is over 70. No succession plan. The entire business depends on one person's knowledge.

**Why cool:** This is a pattern — aging craftspeople with unique knowledge, no documentation, no successors. The repair garden could detect these before they disappear.

---

## What We Should Build Next

1. **Robot parts price tracker** — start with the 100-part seed panel, add eBay sold + Alibaba + RobotShop
2. **Repair outcome probe** — simple web form: "I fixed X, it took Y hours, cost Z, here's the part"
3. **Component basket monitor** — track 10 key MPNs across Mouser/DigiKey hourly
4. **3D-printer probe** — OctoPrint plugin that reports job/failure/maintenance
5. **Depreciation curves** — eBay sold data → price decay by model × condition
6. **Constraint rotation detector** — shadow price changes across parts categories
