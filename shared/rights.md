# Rights propagation

Rights are data, not comments.

## Enum

- `OPEN_REPUBLISH`
- `ATTRIBUTION`
- `INTERNAL_ONLY`
- `DERIVED_INTERNAL_ONLY`
- `DERIVED_PUBLISHABLE`
- `LICENSE_REQUIRED`
- `UNKNOWN`

## Rule

A transformation may never loosen parent rights automatically.

Example:

```text
IBKR L2 (INTERNAL_ONLY)
  → order-book feature
  → INTERNAL_ONLY unless explicit licensed terms say otherwise
```

Open government data:

```text
ONS OGL
  → normalized observation
  → ATTRIBUTION / publishable subject to OGL terms
```

## Source onboarding gate

Before production:
1. save terms URL
2. save licence identifier
3. save access date
4. classify raw redistribution
5. classify transformed-data usage
6. classify commercial usage
7. preserve attribution requirements
8. flag uncertainty as `UNKNOWN` / `LICENSE_REQUIRED`

Do not infer commercial redistribution rights from “API is accessible.”

This pack is engineering guidance, not legal advice.
