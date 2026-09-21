# Robot Parts 100

A seed panel for PTech's robotics/automation economy. It is **not a claim that every row has a verified current price**. Rows are explicitly graded:

- `verified_cross_market`: current upstream + UK reference observed
- `verified_current` / `verified_uk`: current public price evidence from one side
- `verified_identity`: manufacturer identity/spec source is confirmed; price still needs collection
- `seed_unverified`: deliberately included as a discovery target; collector must verify before publishing

The panel exists to start a clock on the categories most likely to matter for robot repair, modification, fabrication and resale.

## Daily fields we ultimately want

`manufacturer, model, revision, supplier, region, price, currency, MOQ, stock/availability, lead_time, shipping_quote, certification_claims, source_timestamp, model_status, replacement_model, interface, voltage, torque/power/spec, compatible_assets, raw_hash`

## Landed cost

Never invent landed cost. Compute from a quote:

`landed_ex_vat = unit_price + allocated_shipping + duty + broker/compliance costs`

`cash_landed = landed_ex_vat + import_vat`

Commodity code, origin, Incoterm, importer status and VAT treatment must be explicit inputs. Batteries and other regulated products require additional compliance handling.
