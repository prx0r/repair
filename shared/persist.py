"""Persistence — shared functions for all collectors.

Every collector uses these. No hand-written SQL inserts.
Returns InsertResult so callers know what happened.
"""

import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


def _db_path():
    return Path(os.environ.get('REPAIR_DB', str(Path(__file__).parent.parent / 'warehouse' / 'repair.db')))


@dataclass
class InsertResult:
    """Result of inserting a record."""
    inserted: bool
    record_id: str
    duplicate_of: str = ""
    error: str = ""


def get_db():
    """Get database connection. Creates tables if needed."""
    _db_path().parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_db_path()))
    # Ensure tables exist
    conn.execute("""CREATE TABLE IF NOT EXISTS raw_blob (
        sha256 TEXT PRIMARY KEY, source_id TEXT NOT NULL, content_type TEXT,
        content_length INTEGER, storage_path TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')))""")
    conn.execute("""CREATE TABLE IF NOT EXISTS raw_acquisition (
        acquisition_id INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT NOT NULL,
        dataset TEXT NOT NULL, retrieved_at TEXT NOT NULL, request_url TEXT,
        http_status INTEGER, etag TEXT, last_modified TEXT, content_type TEXT,
        content_length INTEGER, sha256 TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS source_record (
        source_record_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, dataset TEXT NOT NULL,
        source_native_id TEXT, event_time TEXT, retrieved_at TEXT NOT NULL,
        normalized_json TEXT NOT NULL, payload_hash TEXT NOT NULL,
        raw_payload_hash TEXT NOT NULL, parser_id TEXT NOT NULL,
        parser_version TEXT NOT NULL, valid INTEGER NOT NULL DEFAULT 1,
        validation_errors_json TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS source_cursor (
        source_id TEXT NOT NULL, dataset TEXT NOT NULL, cursor_type TEXT,
        cursor_value TEXT, updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        PRIMARY KEY (source_id, dataset))""")
    conn.execute("""CREATE TABLE IF NOT EXISTS collector_run (
        run_id INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT NOT NULL,
        started_at TEXT, finished_at TEXT, status TEXT, raw_fetched INTEGER,
        raw_new INTEGER, source_records_new INTEGER, source_records_invalid INTEGER,
        error TEXT)""")
    return conn


def store_raw(content: bytes, source_id: str, content_type: str = 'application/octet-stream') -> str:
    """Store raw content immutably. Returns SHA256. Idempotent."""
    sha256 = hashlib.sha256(content).hexdigest()
    raw_dir = _db_path().parent / 'raw' / source_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f'{sha256}.gz'

    if not raw_path.exists():
        import gzip
        with gzip.open(raw_path, 'wb') as f:
            f.write(content)

    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO raw_blob (sha256, source_id, content_type, content_length, storage_path) "
        "VALUES (?, ?, ?, ?, ?)",
        (sha256, source_id, content_type, len(content), str(raw_path))
    )
    conn.commit()
    conn.close()
    return sha256


def store_acquisition(source_id: str, dataset: str, url: str, http_status: int,
                      sha256: str, content_type: str = '', etag: str = '',
                      last_modified: str = '', content_length: int = 0):
    """Store acquisition receipt. Always appends (same blob, different fetch time)."""
    conn = get_db()
    conn.execute(
        "INSERT INTO raw_acquisition "
        "(source_id, dataset, retrieved_at, request_url, http_status, etag, last_modified, "
        "content_type, content_length, sha256) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (source_id, dataset, datetime.now(timezone.utc).isoformat(),
         url, http_status, etag, last_modified, content_type, content_length, sha256)
    )
    conn.commit()
    conn.close()


def insert_source_record(source_id: str, dataset: str, native_id: str,
                          normalized: dict, raw_hash: str, parser_id: str,
                          parser_version: str = '1.0.0',
                          event_time: str = '') -> InsertResult:
    """Insert a source record. Returns InsertResult with status.

    Uses INSERT OR IGNORE for idempotency.
    Detects changes by comparing payload_hash.
    """
    record_id = f'{source_id}:{native_id}'
    payload_hash = hashlib.sha256(
        json.dumps(normalized, sort_keys=True, default=str).encode()
    ).hexdigest()

    conn = get_db()

    # Check if exists
    existing = conn.execute(
        "SELECT payload_hash FROM source_record WHERE source_record_id=?",
        (record_id,)
    ).fetchone()

    if existing:
        if existing[0] == payload_hash:
            # Unchanged
            conn.close()
            return InsertResult(inserted=False, record_id=record_id, duplicate_of=record_id)
        else:
            # Changed — store as new version
            version_id = f'{record_id}:v{datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")}'
            conn.execute(
                "INSERT INTO source_record "
                "(source_record_id, source_id, dataset, source_native_id, event_time, "
                "retrieved_at, normalized_json, payload_hash, raw_payload_hash, "
                "parser_id, parser_version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (version_id, source_id, dataset, native_id,
                 event_time or normalized.get('event_time', ''),
                 datetime.now(timezone.utc).isoformat(),
                 json.dumps(normalized, default=str), payload_hash,
                 raw_hash, parser_id, parser_version)
            )
            conn.commit()
            conn.close()
            return InsertResult(inserted=True, record_id=version_id, duplicate_of=record_id)

    # New record
    try:
        conn.execute(
            "INSERT INTO source_record "
            "(source_record_id, source_id, dataset, source_native_id, event_time, "
            "retrieved_at, normalized_json, payload_hash, raw_payload_hash, "
            "parser_id, parser_version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (record_id, source_id, dataset, native_id,
             event_time or normalized.get('event_time', ''),
             datetime.now(timezone.utc).isoformat(),
             json.dumps(normalized, default=str), payload_hash,
             raw_hash, parser_id, parser_version)
        )
        conn.commit()
        conn.close()
        return InsertResult(inserted=True, record_id=record_id)
    except sqlite3.IntegrityError:
        conn.close()
        return InsertResult(inserted=False, record_id=record_id, duplicate_of=record_id)


def get_cursor(source_id: str, dataset: str) -> str:
    """Get cursor value."""
    conn = get_db()
    row = conn.execute(
        "SELECT cursor_value FROM source_cursor WHERE source_id=? AND dataset=?",
        (source_id, dataset)
    ).fetchone()
    conn.close()
    return row[0] if row else None


def set_cursor(source_id: str, dataset: str, cursor_value: str):
    """Set cursor value."""
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO source_cursor (source_id, dataset, cursor_type, cursor_value, updated_at) "
        "VALUES (?, ?, 'offset', ?, ?)",
        (source_id, dataset, cursor_value, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()


def log_run(source_id: str, status: str, raw_fetched: int = 0, raw_new: int = 0,
            records_new: int = 0, records_unchanged: int = 0, records_invalid: int = 0,
            error: str = None, started_at: str = '', finished_at: str = ''):
    """Log a collector run."""
    conn = get_db()
    conn.execute(
        "INSERT INTO collector_run "
        "(source_id, started_at, finished_at, status, raw_fetched, raw_new, "
        "source_records_new, source_records_invalid, error) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (source_id, started_at or datetime.now(timezone.utc).isoformat(),
         finished_at or datetime.now(timezone.utc).isoformat(),
         status, raw_fetched, raw_new, records_new, records_invalid, error)
    )
    conn.commit()
    conn.close()
