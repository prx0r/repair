"""Database — canonical schema for Repair Garden.

Three layers: RAW → source_record → canonical entities/observations.
All writes are append-only. Observations are immutable.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path('/home/ubuntu/warehouse/repair.db')

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

-- Layer A: Raw acquisition receipts
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
    parser_id TEXT NOT NULL,
    parser_version TEXT NOT NULL,
    valid INTEGER NOT NULL DEFAULT 1,
    validation_errors_json TEXT
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_source_record_source ON source_record(source_id);
CREATE INDEX IF NOT EXISTS idx_source_record_native ON source_record(source_native_id);
CREATE INDEX IF NOT EXISTS idx_observation_source ON observation(source_id);
CREATE INDEX IF NOT EXISTS idx_observation_entity ON observation(entity_id);
CREATE INDEX IF NOT EXISTS idx_observation_metric ON observation(metric);
CREATE INDEX IF NOT EXISTS idx_derived_entity ON derived_fact(entity_id);
CREATE INDEX IF NOT EXISTS idx_raw_acq_source ON raw_acquisition(source_id);
"""


def init_db():
    """Initialize database with canonical schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript(SCHEMA)
    conn.commit()
    print(f'Database initialized: {DB_PATH}')
    return conn


def get_db():
    """Get database connection."""
    return sqlite3.connect(str(DB_PATH))


def status():
    """Print database status."""
    conn = get_db()
    tables = ['raw_blob', 'raw_acquisition', 'source_record', 'observation', 'derived_fact', 'source_cursor', 'collector_run']
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

    conn.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        status()
    else:
        init_db()
