# Source onboarding

Before writing a collector:

1. Define the economic question.
2. Define why time matters.
3. Determine if history is reconstructable.
4. Record source authority level.
5. Read/record licence and terms.
6. Decide raw vs derived publication rights.
7. Freeze raw envelope.
8. Create 3–10 fixture payloads.
9. Write deterministic parser.
10. Add Jev only if parser cannot safely resolve semantics.
11. Write normalization tests.
12. Define freshness SLA.
13. Define gap/backfill process.
14. Add source to registry.
15. Start collection before building dashboard.

## Kill test

If the data can be fetched perfectly in three years and POW performs no unique continuous transformation on it, question whether it deserves continuous collection.
