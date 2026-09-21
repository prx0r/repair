# Repair Garden — ZIP Registry

All zips extracted from 408 emails, mined for data sources and architecture.

## Status Legend

| Status | Meaning |
|--------|---------|
| ✅ Mined | Fully extracted, all sources catalogued |
| ⏳ Partial | Extracted but not fully mined |
| ❌ Skipped | Not relevant to repair/pow |

---

## ZIP Inventory

### 1. ✅ ptech_garden_v0.zip
- **Email:** 1789906551360 / 1789906552846
- **Files:** 60
- **What:** PTech Garden v0.1 — earlier version of physical repair economics garden
- **Sources found:** 46 (source_registry.json)
- **Key collectors:** open_repair, dvsa_mot_bulk, companies_house_stream, octopus, pvlive, ocpi_generic, git_sources
- **Notes:** Foundation layer. Has the original source registry with 46 sources across 8 categories. All v0 sources carried forward to v0.3.

### 2. ✅ ptech_garden_v0_3_physical_repair.zip
- **Email:** 1789906550177
- **Files:** 77
- **What:** PTech Garden v0.3 — adds robot_parts, 17 canonical schemas, expanded registry
- **Sources found:** 60 (14 new vs v0)
- **New sources vs v0:** adzuna_jobs, alibaba_robotics, contracts_finder_ocds, electrical_competent_person, find_tender_ocds, mcs_installation_database, myactuator_catalog, myactuator_product_news, robotshop_uk, ros2_control, skills_england_annual, uk_apprenticeship_display_api, uk_business_population, unitree_official_shop
- **Key addition:** 17 canonical schemas (repair_opportunity, asset, repair_attempt, action_value, part, market_observation, compatibility_edge, etc.)
- **Notes:** The most complete source registry. 60 sources across 18 categories. Robot parts dataset (100 components).

### 3. ✅ POW_SYSTEMS_DEV_REFERENCE_2026-09-20.zip
- **Email:** 1789910105696
- **Files:** 75
- **What:** Cross-system dev reference — architecture, build order, shared contracts
- **Sources found:** System registry (6 systems), shared contracts (Observation, DerivedFact, EconomicEvent)
- **Key additions:** system_registry.yaml, shared/schema.sql, shared/contracts.py, cross_system/entity_edges.md
- **Notes:** Defines the pow.systems hierarchy. pow-physical is #1 priority (BUILD NOW). Shared contracts for cross-system interoperability.

### 4. ✅ pow-scarcity-lab-2026-09-20.zip
- **Email:** 1789912512779 / 1789912560804 / 1789914968450
- **Files:** 48
- **What:** POW Scarcity Lab — causal research models for scarcity migration
- **Sources found:** 29 (in pow_sources.json)
- **Key models:** diffusion, shadow prices, synergy, hazard, skills, network, lagscan, reconstruction, scenario
- **Notes:** 9 causal models. Research extension for powpowpow. Cross-domain scarcity tracking.

### 5. ✅ pow_research_kernel_2026-09-20.zip
- **Email:** 1789912560804
- **Files:** 40
- **What:** Research kernel — temporal physical-economy graph + modelling primitives
- **Sources found:** 64 (source_assets.csv)
- **Key models:** Richards diffusion, Leontief cost propagation, LP shadow prices, synergy screen, maintenance demand, labor pressure, lead/lag
- **Notes:** 64 sources across P0/P1/P2. The most comprehensive source inventory. 7 tests passing.

### 6. ✅ zip_1_WantGraph.zip
- **Email:** 1789676675521
- **Files:** 40 (8 runs)
- **What:** Consumer purchase intent from Reddit
- **Sources found:** Reddit UK subreddits (r/drivingUK, r/CarTalkUK, r/ElectricVehiclesUK, r/ukheatpumps, etc.)
- **Data collected:** 3 accepted observations (EV first-car, kitchenware, holiday)
- **Notes:** Reddit as a consumer intent source is NEW to the registry. 17 indexed results, 14 skipped for non-UK.

### 7. ✅ zip_1_marketgraph.zip
- **Email:** 1789676678733
- **Files:** 41 (8 runs + 6 prior bundles)
- **What:** UK retail product listings — EV charging cables
- **Sources found:** 40+ UK retailers (Screwfix, Toolstation, Tesco, Wickes, etc.)
- **Data collected:** 7 active_ask observations from UK EV charger merchants
- **Notes:** UK retail product scraping is entirely NEW to the registry. Tracks SKUs across retailers.

### 8. ✅ zip_1_frictiongraph_all_reports.zip
- **Email:** 1789676681132
- **Files:** 41 (8 runs)
- **What:** UK consumer friction — disputes, regulatory complaints
- **Sources found:** Reddit UK subreddits (r/HMRC, r/UKPersonalFinance, r/LegalAdviceUK, r/ukaccounting)
- **Data collected:** 6 accepted workflow observations (HMRC, deposit disputes, car rejection)
- **Notes:** Reddit for UK regulatory friction signals is NEW. Tracks resolution dates and outcomes.

### 9. ✅ zip_1_ChangeGraph.zip
- **Email:** 1789676683060
- **Files:** 5 (zip bundles only)
- **What:** Change detection across other graph types
- **Sources found:** Inside ZIPs (not extracted at top level)
- **Notes:** Contains changegraph_bundle_run14-18.zip. Change detection is a derived layer, not primary sources.

### 10. ✅ zip_1_constraint_surface.zip
- **Email:** 1789676686554
- **Files:** 44 (9 runs)
- **What:** UK government regulatory constraints
- **Sources found:** gov.uk (Environment Agency abstraction licences, Ofgem consultations, DfT EV PDR reform)
- **Data collected:** 4 observations (EA abstraction, Ofgem data-centre reform, Sea Link HVDC)
- **Notes:** gov.uk consultations are partially covered by planning_data. EA abstraction is a new specific source.

### 11. ✅ pow_probe_recovery_2026-09-21.zip
- **Email:** 1789960948933
- **Files:** 6
- **What:** 21 recovered probe reports (live state, frontier, constraints, buyer actions, joins)
- **Sources found:** 18 distinct source families
- **New sources:** char.gy OCPI, Believ API, EV Smart feed, NGED Connected Data, DEFRA DWT, UK Payments Transparency Register, UK17 Compliance Notices, MCS installer directory
- **Notes:** Richest single source of new data references. Live EV state, grid constraints, procurement joins.

### 12. ⏳ postagi_worldstate_kernel_2026-09-10.zip
- **Email:** 1789128290047 / 1789129223989
- **Files:** 46
- **What:** Post-AGI world-state kernel — mispricing and obsolescence analysis
- **Sources found:** Methodology references (OpenAlex, PatentsView, EPO, supply-chain datasets)
- **Notes:** Research framework, not live collectors. Uses synthetic fixtures. References overlap with existing sources.

### 13. ⏳ uk-business-phone-agent-blueprint.zip
- **Email:** 1789139919097
- **Files:** 23
- **What:** UK business phone number selection agent
- **Sources found:** Telnyx phone number API
- **Notes:** Telephony data source is NEW but low priority for repair garden.

### 14. ❌ wantgraph_failed_delivery_backfill_all_runs.zip
- **Email:** 1789676581439
- **Files:** 5
- **What:** Backfill for failed email delivery
- **Notes:** Infrastructure artifact (FAILED_EMAIL_DISABLED). No data sources.

### 15. ❌ roastpet_checkpoint1_demo.zip
- **Email:** 1789830166706
- **Files:** 0 (invalid zip)
- **What:** Roast.pet demo checkpoint
- **Notes:** Not relevant to repair/pow.

---

## Source Deduplication Summary

| Source | Found In | Status |
|--------|----------|--------|
| Open Repair Alliance | PTech v0, v0.3, Research Kernel, Scarcity Lab | ✅ Already in registry |
| iFixit | PTech v0, v0.3, Research Kernel | ✅ Already in registry |
| Mouser | PTech v0, v0.3, Research Kernel, Scarcity Lab | ✅ Already in registry |
| DigiKey | PTech v0, v0.3, Research Kernel, Scarcity Lab | ✅ Already in registry |
| Nexar/Octopart | PTech v0, v0.3, Research Kernel, Scarcity Lab | ✅ Already in registry |
| eBay Browse | PTech v0, v0.3, Research Kernel | ✅ Already in registry |
| Companies House | PTech v0, v0.3, Research Kernel | ✅ Already in registry |
| DVSA MOT | PTech v0, v0.3, Research Kernel | ✅ Already in registry |
| Planning Data | PTech v0, v0.3, Research Kernel, Constraint Surface, Probe Recovery | ✅ Already in registry |
| NESO TEC | Research Kernel, Scarcity Lab, Probe Recovery | ✅ Already in registry |
| Elexon | PTech v0.3, Research Kernel, Probe Recovery | ✅ Already in registry |
| Find a Tender | PTech v0.3, Research Kernel, Probe Recovery | ✅ Already in registry |
| Contracts Finder | PTech v0.3, Research Kernel, Probe Recovery | ✅ Already in registry |
| Reddit (UK intent) | WantGraph, FrictionGraph | 🆕 NEW |
| UK retail scrapers (40+) | MarketGraph | 🆕 NEW |
| char.gy OCPI | Probe Recovery | 🆕 NEW |
| Believ API | Probe Recovery | 🆕 NEW |
| NGED Connected Data | Probe Recovery | 🆕 NEW |
| DEFRA DWT | Probe Recovery | 🆕 NEW |
| UK Payments Register | Probe Recovery | 🆕 NEW |
| MCS installer | Probe Recovery, PTech v0.3 | 🆕 NEW |
| element14/Farnell | PTech v0, v0.3, Research Kernel | 🆕 NEW |
| RS Components | PTech v0, v0.3 | 🆕 NEW |
| Octopus Tariffs | PTech v0, v0.3 | 🆕 NEW |
| PVGIS | PTech v0.3 | 🆕 NEW |
| OpenStreetMap | PTech v0, v0.3 | 🆕 NEW |
| Adzuna Jobs | PTech v0.3, Research Kernel | 🆕 NEW |
| Skills England | PTech v0.3, Research Kernel | 🆕 NEW |
| Blender Open Data | PTech v0, v0.3 | 🆕 NEW |
| MLPerf | PTech v0, v0.3, Research Kernel | 🆕 NEW |
| EPC England/Wales | PTech v0.3 | 🆕 NEW |
| HMRC Trade | Research Kernel, Scarcity Lab | 🆕 NEW |
| BGS Minerals | Scarcity Lab | 🆕 NEW |
| USGS Minerals | Research Kernel | 🆕 NEW |
| OpenAlex | Research Kernel | 🆕 NEW |
| PatentsView | Research Kernel | 🆕 NEW |
| SEC EDGAR | Research Kernel | 🆕 NEW |
| LCSC | Research Kernel | 🆕 NEW |
| Vast.ai | Research Kernel | 🆕 NEW |
| Akash Providers | Research Kernel | 🆕 NEW |
| Telnyx | Phone Agent | 🆕 NEW (low priority) |

## New Sources to Add to Registry: 30+
## Already in Registry: 14
## Not Relevant: 2 (roastpet, failed delivery backfill)
