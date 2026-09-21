# Source notes verified during reference build — 2026-09-20

These notes capture important current implementation facts. Re-check terms/rates before production.

## eBay Browse / Feed
- Browse supports searches by keyword, category, GTIN, product and compatibility and condition/aspect filters.
- Product feed fields include listing ID, title, availability, condition, price/currency, GTIN, MPN, brand, category, delivery/returns/shipping fields.
- Great Britain (`EBAY_GB`) is supported by the Buy API surface, but individual Buy APIs have marketplace/access limitations.
- Some Buy APIs are limited-release; do not assume production access to every feed.
- Active listing disappearance is not proof of sale.
Sources:
- https://developer.ebay.com/develop/api/buy
- https://developer.ebay.com/api-docs/buy/api-browse.html
- https://developer.ebay.com/api-docs/buy/feed/v1/schema/product_feed

## EPREL
- Public EU energy-label registry has over 2 million registered products as of July 2026.
- Product groups can expose detailed characteristics and, for newer legislation, links/fields around spare parts, indicative costs, repair instructions and dismantling.
- Researchers can export results.
Source:
- https://energy-efficient-products.ec.europa.eu/eprel_en

## OPSS
- GOV.UK exposes Product Safety Alerts, Reports and Recalls with alert type, risk level, category, measure and date.
- Treat as safety signal, not a population failure-rate denominator.
Source:
- https://www.gov.uk/product-safety-alerts-reports-recalls

## Skills England
- Public API requires an API key request.
- Can expose occupations, SOC mappings, job titles, duties, KSBs, routes, green themes and technical education products.
- API data can inform external products subject to OGL and stated Skills England attribution/branding conditions.
Source:
- https://occupational-maps.skillsengland.education.gov.uk/public-api/

## ONS Labour Demand
- Current dataset contains online job adverts split by local authority and SOC2020 occupation.
- August 21 2026 release exposes January 2017–July 2026 edition.
- Preserve revisions/source caveats.
Source:
- https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/labourdemandvolumesbystandardoccupationclassificationsoc2020uk

## Nomis APS218
- Current latest reference period: Apr 2025–Mar 2026.
- 552 SOC2020 occupation categories.
- Employee/self-employed dimension available.
Source:
- https://www.nomisweb.co.uk/datasets/aps218

## DfE apprenticeships
- 2025/26 release published July 16 2026.
- Regional/LAD datasets expose starts, achievements and related breakdowns.
Source:
- https://explore-education-statistics.service.gov.uk/find-statistics/apprenticeships/2025-26/explore

## Find a Tender
- Notice data available under OGL.
- OCDS release/record package APIs use OCDS 1.1.5 mappings.
Source:
- https://www.find-tender.service.gov.uk/Developer/Documentation

## UK Trade Info
- Open REST/OData API, no Authorization header.
- 60 requests/minute.
- Commodity endpoint supports CN/HS; trade data exposes value/net mass and geographic/flow dimensions.
Source:
- https://www.uktradeinfo.com/api-documentation

## Elexon Insights
- Public REST API, no API key.
- OpenAPI definitions available.
- Dataset endpoints preserve publication-time access patterns useful for revisions/backfills.
Source:
- https://developer.data.elexon.co.uk/

## NESO
- CKAN API supports datastore_search / SQL.
- Thermal constraint cost files and constraint breakdown (inertia/voltage/thermal) are available; current 2026–27 files exist.
- NESO Open Data Licence applies to relevant portal datasets.
Source:
- https://www.neso.energy/data-portal

## UK Power Networks
- Open Data Portal includes historical power flows, import/export capacity/headroom and near-real-time network operational data.
Source:
- https://ukpowernetworks.opendatasoft.com/

## IBKR L2
- TWS API `reqMktDepth()` returns deep-book updates.
- fields include position, operation, side, price, size, marketMaker, isSmartDepth.
- IBKR says depth is sent without L1-style sampling/filtering but cannot guarantee every quote and odd lots are excluded.
- reset error 317 requires clearing the book before applying further updates.
- current published market-data pricing lists LSE UK L2 at GBP 7 for non-professional users; professional column shown N/A on that page.
- Treat rights conservatively; do not assume external commercial redistribution.
Sources:
- https://www.interactivebrokers.com/docs/tws-api/doc/market-data-live/market-depth-l-2/introduction
- https://www.interactivebrokers.com/docs/tws-api/doc/market-data-live/market-depth-l-2/request-market-depth
- https://www.interactivebrokers.com/en/pricing/market-data-pricing.php

## OpenFIGI
- current API is v3.
- public/free API with higher free rate using API key.
- maps identifiers and returns FIGI/security metadata.
Source:
- https://www.openfigi.com/api/documentation

## FCA NSM
- official system for UK regulated issuer disclosures.
- search by company/LEI/date/keywords.
- free document download/search-result CSV export.
- Annual Financial Reports can be viewed as iXBRL and downloaded in JSON/CSV where available.
- related issuer LEIs/correction handling improved from Nov 2025.
Source:
- https://www.fca.org.uk/markets/primary-markets/regulatory-disclosures/national-storage-mechanism

## OpenAlex
- API covers works, authors, institutions, sources/topics etc.
- basic access free to start; heavier usage has budget/pricing mechanics.
- current docs describe `from_created_date` / `from_updated_date` sync filters as premium.
Source:
- https://help.openalex.org/api/

## Crossref
- REST API public access requires no signup.
- polite use identifies via email/agent.
- rate limits differ by public/polite/Plus and may change; obey returned headers.
Source:
- https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/

## EPO OPS
- free threshold up to 4GB/week under current fair-use terms.
- terms permit inclusion of OPS data in own machine-readable products/services but prohibit making the raw data “as such” publicly available.
Sources:
- https://www.epo.org/en/searching-for-patents/data/web-services/ops
- https://www.epo.org/en/service-support/ordering/terms-and-conditions/ops-terms-and-conditions

## GitHub
- authenticated REST primary limit is generally 5,000 requests/hour for normal authenticated users; search and secondary limits differ.
Source:
- https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
