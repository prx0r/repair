# Quality gates

A derived metric cannot be promoted to `LIVE` unless:

1. every required input is measured
2. input freshness thresholds pass
3. entity resolution is above required confidence
4. units are normalized
5. method/version is stored
6. source rights permit intended use
7. limitations are attached
8. a deterministic fixture exists
9. calibration/evaluation exists for any Jev decision in the path

## Truth classes

- VERIFIED: directly observed
- DERIVED: deterministic/validated calculation
- ESTIMATED: assumptions required
- HEURISTIC: useful rule, uncalibrated
- CONCEPTUAL: schema/idea only
- UNAVAILABLE: missing

Never present ESTIMATED as VERIFIED.

## Missing-data behavior

Missing inputs:
- produce UNKNOWN
- name blocker
- do not substitute made-up constants

This is copied from the strongest idea in `/powpowpow/transforms.md`: a formula graduates only with measured inputs on both sides.
