# Existing repository notes

## `prx0r/powpowpow`

Use as the engineering exemplar.

Observed design strengths:
- immutable raw data doctrine
- JSONL hot streams + permanent Parquet
- explicit `Recoverability`
- source registry
- universal schemas
- real-time L2/trades
- transformation registry
- blockers named rather than faked
- formulas graduate only when both sides are measured
- daily state materialization
- independently deployable MCP/API/site

Useful existing concepts to copy:
- `Observation`
- `TruthClass`
- `Recoverability`
- `Source`
- `DerivedFact`
- `DecisionSpec`
- source registry
- warehouse/manifest patterns

## `prx0r/datagarden`

Important architectural precedent:
- collectors/data/API keys stay garden-specific
- shared primitives stay garden-agnostic
- no cross-import of garden collectors
- each garden independently deployable
- Jev acts as fuzzy typed decision layer
- QP-lite concepts protect provenance/history

This reference pack deliberately preserves those ideas while restructuring objective UK/physical data under POW.
