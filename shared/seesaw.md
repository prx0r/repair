# Seesaw object

Canonical mechanism:

`Innovation → ΔConstraint → ΔShadowPrice → Capital Allocation → Supply Response → Constraint Relaxation → repeat`

## Schema

```yaml
hypothesis_id:
created_at:
status: proposed|tracking|supported|weakened|killed

innovation:
constraint_relaxed:
new_constraint:

affected_entities: []
affected_resource_families: []
affected_company_ids: []
affected_security_ids: []

predictions:
  - prediction_id:
    statement:
    metric:
    expected_direction:
    horizon:
    weight:

kill_conditions:
  - kill_id:
    statement:
    metric:
    threshold:
    duration:
    weight:

evidence_policy:
  min_source_independence:
  stale_after:
```

## Evidence update

Do not let an LLM “re-decide the thesis” from scratch each run.

Each event is mapped to:
- supports prediction?
- contradicts prediction?
- triggers kill condition?
- irrelevant?

Store each mapping and probability.

Then deterministic code updates the evidence score/posterior.

## Critical latency fields

For every prediction:
- first_possible_event_time
- first_observed_at
- first_confirmed_at
- company_disclosure_at
- market_response_at

This is how the causal-latency dataset emerges.
