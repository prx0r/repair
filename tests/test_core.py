"""Tests for Repair Garden — core persistence and collector contracts."""

import hashlib
import json
import os
import sys
import tempfile
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.persist import (
    get_db, store_raw, store_acquisition, insert_source_record,
    get_cursor, set_cursor, InsertResult
)


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / 'test.db'
    conn = sqlite3.connect(str(db_path))
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS raw_blob (
            sha256 TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            content_type TEXT,
            content_length INTEGER,
            storage_path TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS raw_acquisition (
            acquisition_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            dataset TEXT NOT NULL,
            retrieved_at TEXT NOT NULL,
            request_url TEXT,
            http_status INTEGER,
            etag TEXT,
            last_modified TEXT,
            content_type TEXT,
            content_length INTEGER,
            sha256 TEXT NOT NULL
        );
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
        CREATE TABLE IF NOT EXISTS source_cursor (
            source_id TEXT NOT NULL,
            dataset TEXT NOT NULL,
            cursor_type TEXT,
            cursor_value TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (source_id, dataset)
        );
    ''')
    conn.close()
    return db_path


class TestRawBlobIdempotency:
    def test_same_blob_twice_is_safe(self, temp_db, tmp_path):
        """Storing the same raw content twice should not fail."""
        os.environ['REPAIR_DB'] = str(temp_db)
        content = b'test data for idempotency'
        sha1 = store_raw(content, 'test_source')
        sha2 = store_raw(content, 'test_source')
        assert sha1 == sha2

        conn = sqlite3.connect(str(temp_db))
        count = conn.execute('SELECT COUNT(*) FROM raw_blob').fetchone()[0]
        assert count == 1  # only one blob stored
        conn.close()

    def test_different_content_different_hash(self, temp_db, tmp_path):
        """Different content should produce different hashes."""
        os.environ['REPAIR_DB'] = str(temp_db)
        sha1 = store_raw(b'content A', 'test_source')
        sha2 = store_raw(b'content B', 'test_source')
        assert sha1 != sha2

        conn = sqlite3.connect(str(temp_db))
        count = conn.execute('SELECT COUNT(*) FROM raw_blob').fetchone()[0]
        assert count == 2
        conn.close()


class TestSourceRecord:
    def test_new_record_is_inserted(self, temp_db):
        os.environ['REPAIR_DB'] = str(temp_db)
        ir = insert_source_record('test', 'dataset', 'native_1',
                                   {'key': 'value'}, 'hash1', 'parser_v1')
        assert ir.inserted is True
        assert ir.record_id == 'test:native_1'

    def test_duplicate_record_is_detected(self, temp_db):
        os.environ['REPAIR_DB'] = str(temp_db)
        ir1 = insert_source_record('test', 'dataset', 'native_1',
                                    {'key': 'value'}, 'hash1', 'parser_v1')
        ir2 = insert_source_record('test', 'dataset', 'native_1',
                                    {'key': 'value'}, 'hash1', 'parser_v1')
        assert ir1.inserted is True
        assert ir2.inserted is False
        assert ir2.duplicate_of == 'test:native_1'

    def test_changed_record_is_versioned(self, temp_db):
        os.environ['REPAIR_DB'] = str(temp_db)
        ir1 = insert_source_record('test', 'dataset', 'native_1',
                                    {'key': 'old'}, 'hash1', 'parser_v1')
        ir2 = insert_source_record('test', 'dataset', 'native_1',
                                    {'key': 'new'}, 'hash1', 'parser_v1')
        assert ir1.inserted is True
        assert ir2.inserted is True
        assert ir2.duplicate_of == 'test:native_1'  # references original

    def test_record_has_raw_provenance(self, temp_db):
        os.environ['REPAIR_DB'] = str(temp_db)
        insert_source_record('test', 'dataset', 'native_1',
                              {'key': 'value'}, 'raw_hash_abc', 'parser_v1')
        conn = sqlite3.connect(str(temp_db))
        row = conn.execute('SELECT raw_payload_hash FROM source_record WHERE source_record_id="test:native_1"').fetchone()
        assert row[0] == 'raw_hash_abc'
        conn.close()


class TestCursor:
    def test_cursor_set_and_get(self, temp_db):
        os.environ['REPAIR_DB'] = str(temp_db)
        set_cursor('test', 'dataset', '42')
        assert get_cursor('test', 'dataset') == '42'

    def test_cursor_overwrite(self, temp_db):
        os.environ['REPAIR_DB'] = str(temp_db)
        set_cursor('test', 'dataset', '10')
        set_cursor('test', 'dataset', '20')
        assert get_cursor('test', 'dataset') == '20'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
