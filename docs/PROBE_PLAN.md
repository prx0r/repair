# Five POW probes

These are not five unrelated reports. They are five synchronized views of the same causal graph. Run them hourly where provider cadence/terms allow, and let slower sources contribute their most recent state.

## 1. Frontier shock probe

Inputs: OpenAlex, GitHub, EPO OPS, company product/release events.

Question: **What capability or technology state changed, and which existing dependency neighbourhood is closest to adopting it?**

Transforms: topic/repo acceleration, technology-interdependency graph, diffusion trigger, directed-innovation score.

## 2. Physical bottleneck probe

Inputs: Nexar, DigiKey, Mouser, Farnell/element14, HMRC trade, BGS/USGS minerals, energy state.

Question: **Which inputs are depleting relative to implied future load, and which have poor substitutes / long capacity response?**

Transforms: synchronized stock depletion, supplier concentration, lead-time acceleration, LP shadow prices, synergy scan.

## 3. Capacity formation probe

Inputs: NESO TEC, Planning Data, Contracts Finder, Find a Tender, Companies House / filings.

Question: **Where is supply response being built before it is visible as output?**

Transforms: project cohort survival, planned MW/capacity, procurement awards, cancellation delays, expected supply relief date.

## 4. Skill / maintenance probe

Inputs: ONS occupation job ads, salaries, skills, Skills England maps, apprenticeship ads, repair/failure datasets.

Question: **Has the bottleneck migrated from hardware into qualified human capacity or maintenance?**

Transforms: skill pressure, occupation mobility, training gap, installed-base hazard wave.

## 5. Assimilation / alpha probe

Inputs: eBay secondary markets, distributor prices, EDGAR, headlines, crypto L2 and optional IBKR L2.

Question: **Which earlier physical signal has not yet been assimilated by narrative or traded prices?**

Transforms: lag scan, PCMCI candidate edges, event study, walk-forward factor test, kill-gate check.

## Hourly output

Each probe should write machine-readable rows first, then a human report containing only:

- new state transitions since prior run
- strongest candidate causal chains
- shadow-price changes
- data-quality failures
- hypotheses to backtest
- explicit kill gates

No prose-only insight is allowed to bypass the warehouse.
