# First 48 hours checklist

## Shared
- [ ] Copy shared contracts into a tiny versioned package.
- [ ] Add rights field to all source metadata.
- [ ] Add event_time + observed_at everywhere.
- [ ] Add recoverability field.
- [ ] Add raw payload SHA-256.
- [ ] Add method/version to derived facts.

## pow-capital recorder
- [ ] Define 10–30 UK securities only.
- [ ] Subscribe to correct market data.
- [ ] Store raw L2 updates.
- [ ] Handle resets explicitly.
- [ ] Mark all IBKR-derived rows INTERNAL_ONLY.
- [ ] Create gap monitoring.

## pow-physical
- [ ] Download ORA.
- [ ] Download France schemas/data.
- [ ] Seed EPREL model identities.
- [ ] Create component-family taxonomy.
- [ ] Build product aliases.
- [ ] Add one distributor snapshot.
- [ ] Add one marketplace snapshot after identity works.

## pow-uk
- [ ] Request Skills England API key.
- [ ] Load occupations + SOC + KSB.
- [ ] Load ONS labour-demand XLSX.
- [ ] Load Nomis APS218.
- [ ] Load DfE apprenticeship data.
- [ ] Load Ofqual.
- [ ] Load Find a Tender.

## pow-grid
- [ ] Backfill NESO constraints.
- [ ] Backfill Elexon system prices/generation.
- [ ] Load one DNO capacity/headroom source.
- [ ] Establish canonical asset IDs.

## pow-frontier
- [ ] Add watched entities.
- [ ] Add GitHub release polling.
- [ ] Add OpenAlex/Crossref metadata.
- [ ] Do not generate a Seesaw unless testable predictions exist.
