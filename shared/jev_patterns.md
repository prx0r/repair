# Jev patterns

Jev is the fuzzy typed transistor, not the reasoning brain.

## Use Jev for

### NOUL
- does this listing describe a repairable fault?
- does this filing materially affect production capacity?
- does this tender imply incremental demand for component family X?
- does this paper actually claim a reduction in energy/compute cost?
- is this event duplicate evidence of an existing event?

### CHOICE
- fault family
- component family
- event class
- affected constraint
- relationship type
- technology domain

### SCORE
- evidence relevance
- materiality
- semantic match quality
- repair-complexity rubric
- exposure strength

## Do not use Jev for

- price arithmetic
- inventory changes
- moving averages
- z-scores
- order-book imbalance
- time lags
- joins
- exact regulatory rules
- graph traversal

## Required DecisionSpec metadata

```yaml
id:
version:
primitive:
question:
allowed_outputs:
confidence_threshold:
fallback:
consequence:
eval_set:
accuracy:
calibration:
```

## Fallback policy

LOW consequence:
- UNKNOWN or deterministic fallback

MEDIUM:
- deeper model / human review

HIGH:
- do not automate from Jev alone
