"""Persistence — shared functions for all collectors.

Every collector uses these. No hand-written SQL inserts.
Returns InsertResult so callers know what happened.

Schema authority: shared/db.py is the single source of truth.
"""

import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from shared.db import SCHEMA


def _db_path():
    return Path(os.environ.get('REPAIR_DB', str(Path(__file__).parent.parent / 'warehouse' / 'repair.db')))


@dataclass
class InsertResult:
    """Result of inserting a record."""
    inserted: bool
    record_id: str
    duplicate_of: str = ""
    error: str = ""


@dataclass
class RawStoreResult:
    """Result of storing raw content."""
    sha256: str
    inserted: bool
    path: str


@dataclass
class Acquisition:
    """Result of an HTTP acquisition."""
    content: bytes
    requested_url: str
    final_url: str = ""
    status: int = 0
    content_type: str = ""
    etag: str = ""
    last_modified: str = ""
    content_length: int = 0
    error: str = ""


def get_db():
    """Get database connection. Creates tables from canonical schema if needed."""
    db_path = _db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def store_raw(content: bytes, source_id: str, content_type: str = 'application/octet-stream') -> RawStoreResult:
    """Store raw content immutably. Returns RawStoreResult. Idempotent."""
    sha256 = hashlib.sha256(content).hexdigest()
    raw_dir = _db_path().parent / 'raw' / source_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f'{sha256}.gz'

    inserted = not raw_path.exists()
    if inserted:
        import gzip
        with gzip.open(raw_path, 'wb') as f:
            f.write(content)

    conn = get_db()
    cursor = conn.execute(
        "INSERT OR IGNORE INTO raw_blob (sha256, source_id, content_type, content_length, storage_path) "
        "VALUES (?, ?, ?, ?, ?)",
        (sha256, source_id, content_type, len(content), str(raw_path))
    )
    # rowcount=1 means inserted, 0 means already existed
    if cursor.rowcount == 0:
        inserted = False
    conn.commit()
    conn.close()
    return RawStoreResult(sha256=sha256, inserted=inserted, path=str(raw_path))


def store_acquisition(source_id: str, dataset: str, url: str, http_status: int,
                      sha256: str, content_type: str = '', etag: str = '',
                      last_modified: str = '', content_length: int = 0,
                      final_url: str = '', request_params: str = ''):
    """Store acquisition receipt. Always appends (same blob, different fetch time)."""
    conn = get_db()
    conn.execute(
        "INSERT INTO raw_acquisition "
        "(source_id, dataset, retrieved_at, request_url, final_url, http_status, etag, last_modified, "
        "content_type, content_length, sha256, request_params) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (source_id, dataset, datetime.now(timezone.utc).isoformat(),
         url, final_url, http_status, etag, last_modified, content_type, content_length, sha256,
         request_params)
    )
    conn.commit()
    conn.close()


def insert_source_record(source_id: str, dataset: str, native_id: str,
                          normalized: dict, raw_hash: str, parser_id: str,
                          parser_version: str = '1.0.0',
                          event_time: str = '') -> InsertResult:
    """Insert a source record. Returns InsertResult with status.

    Uses INSERT OR IGNORE for idempotency.
    Detects changes by comparing payload_hash against the LATEST version.
    Version IDs use content-addressed payload_hash (no timestamp collisions).
    """
    record_id = f'{source_id}:{native_id}'
    payload_hash = hashlib.sha256(
        json.dumps(normalized, sort_keys=True, default=str).encode()
    ).hexdigest()

    conn = get_db()

    # Find the LATEST version (base or most recent version)
    existing = conn.execute(
        "SELECT source_record_id, payload_hash FROM source_record "
        "WHERE source_record_id = ? OR source_record_id LIKE ? "
        "ORDER BY source_record_id DESC LIMIT 1",
        (record_id, f'{record_id}:v%')
    ).fetchone()

    if existing:
        if existing[1] == payload_hash:
            # Unchanged from latest version
            conn.close()
            return InsertResult(inserted=False, record_id=existing[0], duplicate_of=existing[0])
        else:
            # Changed — create version with content-addressed ID
            version_id = f'{record_id}:v{payload_hash[:12]}'
            try:
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
            except sqlite3.IntegrityError:
                # Rare: same payload_hash version already exists
                conn.close()
                return InsertResult(inserted=False, record_id=version_id, duplicate_of=record_id)

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
            records_new: int = 0, records_unchanged: int = 0, records_changed: int = 0,
            records_invalid: int = 0,
            error: str = None, started_at: str = '', finished_at: str = ''):
    """Log a collector run."""
    conn = get_db()
    conn.execute(
        "INSERT INTO collector_run "
        "(source_id, started_at, finished_at, status, raw_fetched, raw_new, "
        "source_records_new, source_records_updated, source_records_invalid, error) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (source_id, started_at or datetime.now(timezone.utc).isoformat(),
         finished_at or datetime.now(timezone.utc).isoformat(),
         status, raw_fetched, raw_new, records_new, records_changed, records_invalid, error)
    )
    conn.commit()
    conn.close()


def store_market_observation(source_record_id: str, observed_at: str,
                              price: float, currency: str = 'GBP',
                              stock: str = None, availability: str = None,
                              condition: str = None, market: str = '',
                              extra_json: str = ''):
    """Store a market observation snapshot. Always appends — even unchanged prices matter.

    This captures the time dimension: duration at price, availability duration,
    listing visibility, stock persistence.
    """
    conn = get_db()
    conn.execute(
        "INSERT INTO market_observation "
        "(source_record_id, observed_at, price, currency, stock, availability, "
        "condition, market, extra_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (source_record_id, observed_at, price, currency, stock, availability,
         condition, market, extra_json)
    )
    conn.commit()
    conn.close()
