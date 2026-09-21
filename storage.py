"""Repair Garden — SQLite Storage Layer.

Append-only storage for all collected data. Replaces JSONL files as the
primary query interface. JSONL stays for raw archival; SQLite for fast reads.

Tables:
- observations: raw observations from all sources
- collection_runs: when each source was collected, status, row count
- entities: device models, parts, suppliers
- market_snapshots: price/availability observations
- repair_events: fault/repair/outcome records
"""

import sqlite3
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).parent.parent / 'warehouse' / 'repair.db'


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_conn():
    conn = get_db()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create all tables if they don't exist."""
    with db_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                entity_id TEXT,
                metric TEXT NOT NULL,
                value TEXT,
                value_type TEXT DEFAULT 'text',
                event_time TEXT,
                observed_at TEXT NOT NULL DEFAULT (datetime('now')),
                raw_json TEXT,
                hash TEXT,
                UNIQUE(source_id, entity_id, metric, event_time)
            );

            CREATE TABLE IF NOT EXISTS collection_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                started_at TEXT NOT NULL DEFAULT (datetime('now')),
                finished_at TEXT,
                status TEXT DEFAULT 'running',
                rows_collected INTEGER DEFAULT 0,
                rows_inserted INTEGER DEFAULT 0,
                error TEXT,
                duration_seconds REAL
            );

            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT,
                attributes TEXT,
                first_seen TEXT DEFAULT (datetime('now')),
                last_seen TEXT DEFAULT (datetime('now')),
                status TEXT DEFAULT 'active'
            );

            CREATE TABLE IF NOT EXISTS market_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                condition TEXT,
                price_gbp REAL,
                currency TEXT DEFAULT 'GBP',
                stock_status TEXT,
                listing_url TEXT,
                observed_at TEXT NOT NULL DEFAULT (datetime('now')),
                raw_json TEXT
            );

            CREATE TABLE IF NOT EXISTS repair_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT,
                device_model TEXT,
                fault_type TEXT,
                fault_description TEXT,
                repair_action TEXT,
                repair_outcome TEXT,
                parts_cost_gbp REAL,
                labor_cost_gbp REAL,
                total_cost_gbp REAL,
                repair_time_minutes INTEGER,
                source_id TEXT,
                observed_at TEXT NOT NULL DEFAULT (datetime('now')),
                raw_json TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_obs_source ON observations(source_id);
            CREATE INDEX IF NOT EXISTS idx_obs_entity ON observations(entity_id);
            CREATE INDEX IF NOT EXISTS idx_obs_metric ON observations(metric);
            CREATE INDEX IF NOT EXISTS idx_obs_time ON observations(event_time);
            CREATE INDEX IF NOT EXISTS idx_market_entity ON market_snapshots(entity_id);
            CREATE INDEX IF NOT EXISTS idx_market_platform ON market_snapshots(platform);
            CREATE INDEX IF NOT EXISTS idx_repair_entity ON repair_events(entity_id);
            CREATE INDEX IF NOT EXISTS idx_runs_source ON collection_runs(source_id);
        """)
    print(f"Database initialized: {DB_PATH}")


def insert_observation(source_id, entity_id, metric, value, event_time=None, raw_json=None, value_type='text'):
    """Insert an observation, skip if duplicate."""
    with db_conn() as conn:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO observations (source_id, entity_id, metric, value, value_type, event_time, raw_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (source_id, entity_id, metric, str(value), value_type, event_time, raw_json)
            )
            return conn.total_changes
        except sqlite3.IntegrityError:
            return 0


def insert_observations_batch(source_id, records):
    """Insert multiple observations. Each record is a dict with at least 'metric' and 'value'."""
    inserted = 0
    with db_conn() as conn:
        for record in records:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO observations "
                    "(source_id, entity_id, metric, value, value_type, event_time, raw_json) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        source_id,
                        record.get('entity_id'),
                        record.get('metric', record.get('type', 'unknown')),
                        str(record.get('value', record.get('data', ''))),
                        record.get('value_type', 'text'),
                        record.get('event_time', record.get('observed_at')),
                        json.dumps(record, default=str),
                    )
                )
                inserted += 1
            except sqlite3.IntegrityError:
                continue
    return inserted


def start_collection_run(source_id):
    """Log the start of a collection run."""
    with db_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO collection_runs (source_id, started_at, status) VALUES (?, datetime('now'), 'running')",
            (source_id,)
        )
        return cursor.lastrowid


def finish_collection_run(run_id, rows_collected=0, rows_inserted=0, status='ok', error=None):
    """Log the end of a collection run."""
    with db_conn() as conn:
        conn.execute(
            "UPDATE collection_runs SET finished_at=datetime('now'), status=?, rows_collected=?, "
            "rows_inserted=?, error=?, "
            "duration_seconds=(julianday('now') - julianday(started_at)) * 86400 "
            "WHERE id=?",
            (status, rows_collected, rows_inserted, error, run_id)
        )


def query_observations(source_id=None, metric=None, limit=100):
    """Query observations with optional filters."""
    with db_conn() as conn:
        query = "SELECT * FROM observations WHERE 1=1"
        params = []
        if source_id:
            query += " AND source_id = ?"
            params.append(source_id)
        if metric:
            query += " AND metric = ?"
            params.append(metric)
        query += " ORDER BY observed_at DESC LIMIT ?"
        params.append(limit)
        return [dict(row) for row in conn.execute(query, params).fetchall()]


def get_collection_stats():
    """Get summary stats for all sources."""
    with db_conn() as conn:
        rows = conn.execute(
            "SELECT source_id, COUNT(*) as total, "
            "MIN(observed_at) as first_collected, MAX(observed_at) as last_collected "
            "FROM observations GROUP BY source_id ORDER BY last_collected DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_recent_runs(limit=20):
    """Get recent collection runs."""
    with db_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM collection_runs ORDER BY started_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(row) for row in rows]


if __name__ == '__main__':
    init_db()
    print("Tables created successfully.")
    stats = get_collection_stats()
    print(f"Sources with data: {len(stats)}")
