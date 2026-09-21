# Collector checklist

Every collector must declare:

- source_id
- source URL
- rights/licence
- expected cadence
- recoverability
- collection class: COLLECT_NOW | BACKFILL_SAFE | OPTIONAL
- rate limit
- authentication
- cursor strategy
- retry/backoff
- payload schema/version
- event-time extraction
- observed-at clock
- content hash
- dedup key
- raw storage path
- normalization version
- freshness SLA
- health signal
- gap detection

## Stream collectors additionally

- session ID
- reconnect event
- reset event
- sequence if source provides it
- local monotonic sequence otherwise
- heartbeat
- dropped-message detection where possible
