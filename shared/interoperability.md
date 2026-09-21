# Interoperability contract

No garden reads another garden's internal database.

Each garden publishes versioned exports.

Required export columns:

## entities
`entity_id, entity_type, canonical_name, attributes_json`

## aliases
`entity_id, namespace, alias_value, confidence, source_id, valid_from, valid_to`

## observations
shared schema from `shared/schema.sql`

## events
shared EconomicEvent

## relationships
subject/predicate/object with provenance and validity.

## Federator joins

Examples:

```text
pow-physical COMPONENT
    --manufactured_by-->
pow-capital COMPANY

pow-physical REPAIR_TASK
    --requires_occupation-->
pow-uk OCCUPATION

pow-grid SUBSTATION
    --located_in-->
pow-uk PLACE

pow-frontier HYPOTHESIS
    --predicts_pressure_on-->
pow-physical COMPONENT_FAMILY

pow-capital COMPANY
    --security-->
pow-capital SECURITY
```

Cross-garden links should be explicit relationship records, never hidden joins.
