# Practical build order

## First 48 hours

1. Freeze shared contracts from `shared/`.
2. Create five independent repo/folder skeletons.
3. Start `pow-capital` L2 recorder for a deliberately small UK watch universe.
4. Seed `pow-physical` with:
   - French repairability/durability datasets
   - Open Repair Alliance
   - EPREL exports where accessible
5. Build exact product/model/component identity tables.
6. Add one distributor snapshot source.
7. Add eBay active-market snapshots only after canonical identity works.
8. Import Skills England into `pow-uk`.
9. Import ONS labour-demand SOC×local-authority time series.
10. Start Elexon/NESO backfills for `pow-grid`.
11. Add a thin `pow-frontier` watcher for watched projects/research domains.

## Week 1

### pow-physical
Goal: canonical device and component graph exists.

Definition of done:
- 1,000+ canonical models
- aliases resolve deterministically or with explicit confidence
- component family taxonomy exists
- repair events map to product category/brand
- source provenance preserved

### pow-uk
Goal: canonical task/occupation/skill graph exists.

Definition of done:
- Skills England occupations/KSBs ingested
- SOC codes canonicalized
- Nomis supply joins to SOC
- ONS demand joins to SOC×LAD
- apprenticeship flows imported
- one `capacity_pressure` metric implemented

### pow-grid
Goal: first UK power constraint surface exists.

Definition of done:
- Elexon system price/frequency/generation series
- NESO constraint cost/volume
- at least one DNO headroom dataset
- canonical grid region/site IDs
- one `constraint_pressure` metric

### pow-capital
Goal: record, do not overbuild.

Definition of done:
- security master
- UK watch universe
- raw L2 event stream
- reconstructable book state
- minute features
- internal-only rights enforced

### pow-frontier
Goal: hypotheses enter graph cleanly.

Definition of done:
- watched entities
- GitHub/research/patent events
- event dedup
- Jev event classification
- structured Seesaw object generation
- no automatic trading conclusion

## Weeks 2–4

Only after raw history is growing:
- repair spread
- replacement scarcity
- local capacity pressure
- grid constraint pressure
- company exposure mapping
- event propagation studies
- hypothesis evidence updates

Avoid building polished dashboards before collectors and identity resolution are stable.
