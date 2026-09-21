"""Collector Base — hardened base class for all data collectors.

Every collector inherits from this. Handles:
- Retry with backoff
- Raw storage (content-addressed)
- Source record storage (append-only)
- Cursor management (resumable)
- Manifest logging
- Health tracking
"""

import hashlib
import json
import gzip
import time
import sqlite3
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class CollectorResult:
    """Result of a collector run."""
    def __init__(self):
        self.raw_fetched = 0
        self.raw_new = 0
        self.source_records_new = 0
        self.source_records_duplicate = 0
        self.source_records_invalid = 0
        self.errors = []
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.finished_at = None

    def to_dict(self):
        return {
            'raw_fetched': self.raw_fetched,
            'raw_new': self.raw_new,
            'source_records_new': self.source_records_new,
            'source_records_duplicate': self.source_records_duplicate,
            'source_records_invalid': self.source_records_invalid,
            'errors': self.errors,
            'started_at': self.started_at,
            'finished_at': self.finished_at,
        }


class BaseCollector:
    """Hardened base class for all collectors."""

    SOURCE_ID = ''               # override in subclass
    DATASET = ''                 # override in subclass
    PARSER_ID = ''               # override in subclass
    PARSER_VERSION = '1.0.0'

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / 'warehouse' / 'repair.db')
        self.db_path = db_path
        self.raw_dir = Path(__file__).parent.parent / 'warehouse' / 'raw' / self.SOURCE_ID

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _get_cursor(self, conn):
        """Get last cursor value for resumable backfill."""
        row = conn.execute(
            "SELECT cursor_value FROM source_cursor WHERE source_id=? AND dataset=?",
            (self.SOURCE_ID, self.DATASET)
        ).fetchone()
        return row[0] if row else None

    def _set_cursor(self, conn, cursor_value):
        """Update cursor after successful processing."""
        conn.execute(
            "INSERT OR REPLACE INTO source_cursor (source_id, dataset, cursor_type, cursor_value, updated_at) "
            "VALUES (?, ?, 'offset', ?, ?)",
            (self.SOURCE_ID, self.DATASET, str(cursor_value), datetime.now(timezone.utc).isoformat())
        )
        conn.commit()

    def _store_raw(self, content: bytes, content_type: str = 'application/octet-stream') -> str:
        """Store raw content immutably. Returns SHA256."""
        sha256 = hashlib.sha256(content).hexdigest()
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = self.raw_dir / f'{sha256}.gz'

        if not raw_path.exists():
            with gzip.open(raw_path, 'wb') as f:
                f.write(content)

        conn = self._conn()
        conn.execute(
            "INSERT OR IGNORE INTO raw_blob (sha256, source_id, content_type, content_length, storage_path) "
            "VALUES (?, ?, ?, ?, ?)",
            (sha256, self.SOURCE_ID, content_type, len(content), str(raw_path))
        )
        conn.commit()
        conn.close()
        return sha256

    def _store_raw_with_acquisition(self, content: bytes, url: str, http_status: int,
                                     content_type: str = 'application/octet-stream',
                                     etag: str = '', last_modified: str = '') -> str:
        """Store raw with full acquisition metadata."""
        sha256 = self._store_raw(content, content_type)
        conn = self._conn()
        conn.execute(
            "INSERT INTO raw_acquisition "
            "(source_id, dataset, retrieved_at, request_url, http_status, etag, last_modified, "
            "content_type, content_length, sha256) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (self.SOURCE_ID, self.DATASET, datetime.now(timezone.utc).isoformat(),
             url, http_status, etag, last_modified, content_type, len(content), sha256)
        )
        conn.commit()
        conn.close()
        return sha256

    def _store_source_record(self, native_id: str, normalized: dict, raw_hash: str) -> bool:
        """Store a normalized source record. Returns True if new, False if duplicate."""
        record_id = f'{self.SOURCE_ID}:{native_id}'
        payload_hash = hashlib.sha256(
            json.dumps(normalized, sort_keys=True, default=str).encode()
        ).hexdigest()

        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO source_record "
                "(source_record_id, source_id, dataset, source_native_id, event_time, "
                "retrieved_at, normalized_json, payload_hash, raw_payload_hash, "
                "parser_id, parser_version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (record_id, self.SOURCE_ID, self.DATASET, native_id,
                 normalized.get('event_time', ''), datetime.now(timezone.utc).isoformat(),
                 json.dumps(normalized, default=str), payload_hash,
                 raw_hash, self.PARSER_ID, self.PARSER_VERSION)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def _fetch_url(self, url: str, max_retries: int = 3, timeout: int = 30) -> Optional[requests.Response]:
        """Fetch URL with retry and backoff."""
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, timeout=timeout, headers={
                    'User-Agent': 'RepairGarden/1.0 (data collection)',
                    'Accept': '*/*',
                })
                if resp.status_code == 200:
                    return resp
                elif resp.status_code == 429:
                    wait = min(60, 2 ** (attempt + 2))
                    print(f'    Rate limited, waiting {wait}s...')
                    time.sleep(wait)
                elif resp.status_code >= 500:
                    time.sleep(2 ** attempt)
                else:
                    return resp  # return non-200 for caller to handle
            except requests.exceptions.Timeout:
                time.sleep(2 ** attempt)
            except requests.exceptions.ConnectionError:
                time.sleep(2 ** attempt)
        return None

    def fetch(self) -> Optional[bytes]:
        """Fetch raw data from source. Override in subclass."""
        raise NotImplementedError

    def parse(self, raw_content: bytes, raw_hash: str) -> int:
        """Parse raw content into source records. Override in subclass."""
        raise NotImplementedError

    def run(self, backfill: bool = False) -> CollectorResult:
        """Run the collector."""
        result = CollectorResult()
        print(f'{self.SOURCE_ID} — {self.DATASET}')
        print('=' * 50)

        try:
            # Fetch
            print('  Fetching...')
            raw_content = self.fetch()
            if raw_content is None:
                result.errors.append('fetch_failed')
                print('  FETCH FAILED')
                return result

            result.raw_fetched = 1

            # Store raw
            raw_hash = self._store_raw_with_acquisition(
                raw_content, url=self.SOURCE_ID, http_status=200
            )
            result.raw_new = 1
            print(f'  Raw stored: {raw_hash[:12]}... ({len(raw_content):,} bytes)')

            # Parse
            print('  Parsing...')
            count = self.parse(raw_content, raw_hash)
            result.source_records_new = count
            print(f'  Stored {count:,} source records')

        except Exception as e:
            result.errors.append(str(e))
            print(f'  ERROR: {e}')

        result.finished_at = datetime.now(timezone.utc).isoformat()

        # Log run
        conn = self._conn()
        conn.execute(
            "INSERT INTO collector_run "
            "(source_id, started_at, finished_at, status, raw_fetched, raw_new, "
            "source_records_new, source_records_duplicate, error) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (self.SOURCE_ID, result.started_at, result.finished_at,
             'ok' if not result.errors else 'error',
             result.raw_fetched, result.raw_new,
             result.source_records_new, result.source_records_duplicate,
             json.dumps(result.errors) if result.errors else None)
        )
        conn.commit()
        conn.close()

        return result
