# Storage reference

Recommended baseline per system:

```text
<system>/
  data/
    raw/<source>/<YYYY>/<MM>/<DD>/*.jsonl.gz
    normalized/<table>/<YYYY>/<MM>/<DD>/*.parquet
    derived/<metric>/<YYYY>/<MM>/<DD>/*.parquet
    exports/<YYYY-MM-DD>/
      entities.parquet
      aliases.parquet
      observations.parquet
      derived_facts.parquet
      events.parquet
      relationships.parquet
    state/current.duckdb
    manifests/
```

## Raw event envelope

Every raw record should retain:

```text
ingest_id
source_id
observed_at
request_url_or_channel
request_params
http_status / stream_sequence
source_cursor
source_etag / last_modified
source_version
raw_payload
payload_sha256
collector_version
```

For streaming data also store:
- connection/session ID
- sequence where provided
- reconnect/reset events
- data gaps

## Retention

- Ephemeral: raw forever if licence/storage permits.
- Canonical/backfillable: enough raw to reproduce parsing; bulk source snapshots may be referenced + hashed rather than duplicated if licence/storage dictate.
- Normalized Parquet: forever.
- Derived facts: forever, versioned.
- Current state: disposable/rebuildable.

## Compression

Prefer:
- JSONL.gz for raw envelopes
- Parquet ZSTD for normalized/derived
