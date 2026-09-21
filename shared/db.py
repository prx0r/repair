"""Database — canonical schema for Repair Garden.

Three layers: RAW → source_record → canonical entities/observations.
All writes are append-only. Observations are immutable.

Single authority for DB path: get_db_path() respects REPAIR_DB env var.
"""

import os
import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    """Single source of truth for database path.

    Respects REPAIR_DB env var. Every module must import this,
    never hardcode a path.
    """
    return Path(os.environ.get('REPAIR_DB', str(Path(__file__).parent.parent / 'warehouse' / 'repair.db')))


SCHEMA = """
-- Layer A: RAW blobs (content-addressed)
CREATE TABLE IF NOT EXISTS raw_blob (
    sha256 TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    content_type TEXT,
    content_length INTEGER,
    storage_path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Layer A: Raw acquisition receipts (one per HTTP response)
CREATE TABLE IF NOT EXISTS raw_acquisition (
    acquisition_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    dataset TEXT NOT NULL,
    retrieved_at TEXT NOT NULL,
    request_url TEXT,
    final_url TEXT,
    http_status INTEGER,
    etag TEXT,
    last_modified TEXT,
    content_type TEXT,
    content_length INTEGER,
    sha256 TEXT NOT NULL,
    request_params TEXT,
    FOREIGN KEY (sha256) REFERENCES raw_blob(sha256)
);

-- Layer B: Source records (normalized from raw)
CREATE TABLE IF NOT EXISTS source_record (
    source_record_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    dataset TEXT NOT NULL,
    source_native_id TEXT,
    event_time TEXT,
    retrieved_at TEXT NOT NULL,
    normalized_json TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    raw_payload_hash TEXT NOT NULL,
    acquisition_id INTEGER,
    parser_id TEXT NOT NULL,
    parser_version TEXT NOT NULL,
    valid INTEGER NOT NULL DEFAULT 1,
    validation_errors_json TEXT,
    FOREIGN KEY (acquisition_id) REFERENCES raw_acquisition(acquisition_id)
);

-- Layer C: Canonical observations
CREATE TABLE IF NOT EXISTS observation (
    observation_id TEXT PRIMARY KEY,
    source_record_id TEXT,
    source_id TEXT NOT NULL,
    entity_id TEXT,
    metric TEXT NOT NULL,
    value TEXT,
    value_type TEXT DEFAULT 'text',
    effective_at TEXT,
    published_at TEXT,
    observed_at TEXT NOT NULL DEFAULT (datetime('now')),
    truth_class TEXT DEFAULT 'observed',
    parent_observation_ids TEXT,
    raw_payload_hash TEXT,
    FOREIGN KEY (source_record_id) REFERENCES source_record(source_record_id)
);

-- Derived facts
CREATE TABLE IF NOT EXISTS derived_fact (
    derived_id TEXT PRIMARY KEY,
    source_id TEXT,
    entity_id TEXT,
    metric TEXT NOT NULL,
    value TEXT,
    method_id TEXT,
    method_version TEXT,
    input_observation_ids TEXT,
    confidence REAL,
    computed_at TEXT NOT NULL DEFAULT (datetime('now')),
    valid_from TEXT,
    valid_to TEXT
);

-- Source cursors (for resumable backfill)
CREATE TABLE IF NOT EXISTS source_cursor (
    source_id TEXT NOT NULL,
    dataset TEXT NOT NULL,
    cursor_type TEXT,
    cursor_value TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (source_id, dataset)
);

-- Collector run history
CREATE TABLE IF NOT EXISTS collector_run (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at TEXT,
    status TEXT DEFAULT 'running',
    mode TEXT DEFAULT 'incremental',
    raw_fetched INTEGER DEFAULT 0,
    raw_new INTEGER DEFAULT 0,
    source_records_new INTEGER DEFAULT 0,
    source_records_updated INTEGER DEFAULT 0,
    source_records_invalid INTEGER DEFAULT 0,
    observations_new INTEGER DEFAULT 0,
    error TEXT,
    duration_seconds REAL
);

-- Market observations (ephemeral time-series for marketplace tapes)
CREATE TABLE IF NOT EXISTS market_observation (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_record_id TEXT NOT NULL,
    acquisition_id INTEGER,
    collector_run_id INTEGER,
    source_native_id TEXT,
    observation_type TEXT DEFAULT 'price',
    observed_at TEXT NOT NULL,
    price REAL,
    bid_price REAL,
    exchange_price REAL,
    currency TEXT DEFAULT 'GBP',
    stock TEXT,
    availability TEXT,
    condition TEXT,
    market TEXT,
    extra_json TEXT,
    FOREIGN KEY (source_record_id) REFERENCES source_record(source_record_id),
    FOREIGN KEY (acquisition_id) REFERENCES raw_acquisition(acquisition_id),
    FOREIGN KEY (collector_run_id) REFERENCES collector_run(run_id)
);

-- Collector health (persisted after every run)
CREATE TABLE IF NOT EXISTS source_health (
    health_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    last_attempt TEXT,
    last_success TEXT,
    last_error TEXT,
    records_seen INTEGER DEFAULT 0,
    records_new INTEGER DEFAULT 0,
    records_changed INTEGER DEFAULT 0,
    records_unchanged INTEGER DEFAULT 0,
    records_invalid INTEGER DEFAULT 0,
    status TEXT DEFAULT 'unknown',
    status_reason TEXT,
    computed_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_source_record_source ON source_record(source_id);
CREATE INDEX IF NOT EXISTS idx_source_record_native ON source_record(source_native_id);
CREATE INDEX IF NOT EXISTS idx_source_record_retrieved ON source_record(retrieved_at);
CREATE INDEX IF NOT EXISTS idx_observation_source ON observation(source_id);
CREATE INDEX IF NOT EXISTS idx_observation_entity ON observation(entity_id);
CREATE INDEX IF NOT EXISTS idx_observation_metric ON observation(metric);
CREATE INDEX IF NOT EXISTS idx_derived_entity ON derived_fact(entity_id);
CREATE INDEX IF NOT EXISTS idx_raw_acq_source ON raw_acquisition(source_id);
CREATE INDEX IF NOT EXISTS idx_market_obs_record ON market_observation(source_record_id);
CREATE INDEX IF NOT EXISTS idx_market_obs_time ON market_observation(observed_at);
CREATE INDEX IF NOT EXISTS idx_market_obs_native ON market_observation(source_native_id);
"""


def init_db():
    """Initialize database with canonical schema."""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    conn.commit()
    print(f'Database initialized: {db_path}')
    return conn


def get_db():
    """Get database connection."""
    return sqlite3.connect(str(get_db_path()))


def status():
    """Print database status."""
    conn = get_db()
    tables = ['raw_blob', 'raw_acquisition', 'source_record', 'observation',
              'derived_fact', 'source_cursor', 'collector_run', 'market_observation']
    print('=== DATABASE STATUS ===')
    for t in tables:
        try:
            c = conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
            print(f'  {t:25s} {c:>10,}')
        except:
            print(f'  {t:25s} {"MISSING":>10}')

    # By source
    print('\n=== BY SOURCE ===')
    try:
        rows = conn.execute('''
            SELECT source_id, COUNT(*) as total,
                   MIN(retrieved_at) as first, MAX(retrieved_at) as last
            FROM source_record GROUP BY source_id ORDER BY total DESC
        ''').fetchall()
        for r in rows:
            print(f'  {r[0]:25s} {r[1]:>10,}  {r[2][:10] if r[2] else "?"} → {r[3][:10] if r[3] else "?"}')
    except:
        print('  No source_record data yet')

    # Market observations
    print('\n=== MARKET OBSERVATIONS ===')
    try:
        rows = conn.execute('''
            SELECT source_native_id, COUNT(*) as n, MIN(observed_at), MAX(observed_at)
            FROM market_observation GROUP BY source_native_id ORDER BY n DESC LIMIT 10
        ''').fetchall()
        for r in rows:
            print(f'  {r[0][:40]:40s} {r[1]:>6}  {r[2][:10] if r[2] else "?"} → {r[3][:10] if r[3] else "?"}')
    except:
        print('  No market observations yet')

    conn.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        status()
    else:
        init_db()
