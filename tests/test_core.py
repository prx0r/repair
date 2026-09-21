"""Tests for Repair Garden — persistence, versioning, and collector contracts.

Tests use production schema via get_db() — no hand-copied SQL.
"""

import hashlib
import json
import os
import sys
import tempfile
import sqlite3
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.persist import (
    get_db, store_raw, store_acquisition, insert_source_record,
    get_cursor, set_cursor, log_run, store_market_observation,
    InsertResult, RawStoreResult
)
from shared.db import SCHEMA


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database using the production schema."""
    db_path = tmp_path / 'test.db'
    os.environ['REPAIR_DB'] = str(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    yield db_path
    os.environ.pop('REPAIR_DB', None)


class TestRawBlobIdempotency:
    def test_same_blob_twice_is_safe(self, temp_db):
        """Storing the same raw content twice should not fail."""
        content = b'test data for idempotency'
        r1 = store_raw(content, 'test_source')
        r2 = store_raw(content, 'test_source')
        assert r1.sha256 == r2.sha256
        assert r1.inserted is True
        assert r2.inserted is False  # already existed

        conn = sqlite3.connect(str(temp_db))
        count = conn.execute('SELECT COUNT(*) FROM raw_blob').fetchone()[0]
        assert count == 1  # only one blob stored
        conn.close()

    def test_different_content_different_hash(self, temp_db):
        """Different content should produce different hashes."""
        r1 = store_raw(b'content A', 'test_source')
        r2 = store_raw(b'content B', 'test_source')
        assert r1.sha256 != r2.sha256
        assert r1.inserted is True
        assert r2.inserted is True

        conn = sqlite3.connect(str(temp_db))
        count = conn.execute('SELECT COUNT(*) FROM raw_blob').fetchone()[0]
        assert count == 2
        conn.close()

    def test_store_raw_returns_path(self, temp_db):
        """RawStoreResult should include the storage path."""
        result = store_raw(b'test', 'test_source')
        assert result.path.endswith('.gz')
        assert 'test_source' in result.path


class TestSourceRecord:
    def test_new_record_is_inserted(self, temp_db):
        ir = insert_source_record('test', 'dataset', 'native_1',
                                   {'key': 'value'}, 'hash1', 'parser_v1')
        assert ir.inserted is True
        assert ir.record_id == 'test:native_1'

    def test_duplicate_record_is_detected(self, temp_db):
        ir1 = insert_source_record('test', 'dataset', 'native_1',
                                    {'key': 'value'}, 'hash1', 'parser_v1')
        ir2 = insert_source_record('test', 'dataset', 'native_1',
                                    {'key': 'value'}, 'hash1', 'parser_v1')
        assert ir1.inserted is True
        assert ir2.inserted is False
        assert ir2.duplicate_of == 'test:native_1'

    def test_changed_record_is_versioned(self, temp_db):
        ir1 = insert_source_record('test', 'dataset', 'native_1',
                                    {'key': 'old'}, 'hash1', 'parser_v1')
        ir2 = insert_source_record('test', 'dataset', 'native_1',
                                    {'key': 'new'}, 'hash1', 'parser_v1')
        assert ir1.inserted is True
        assert ir2.inserted is True
        assert ir2.duplicate_of == 'test:native_1'
        # Version ID should use payload hash, not timestamp
        assert ':v' in ir2.record_id
        assert ir2.record_id != ir1.record_id

    def test_changed_record_compares_against_latest(self, temp_db):
        """After two changes, a third identical observation should be duplicate_of latest."""
        ir1 = insert_source_record('test', 'dataset', 'n1', {'k': 'v1'}, 'h1', 'p')
        ir2 = insert_source_record('test', 'dataset', 'n1', {'k': 'v2'}, 'h2', 'p')
        ir3 = insert_source_record('test', 'dataset', 'n1', {'k': 'v2'}, 'h3', 'p')
        assert ir1.inserted is True
        assert ir2.inserted is True
        assert ir3.inserted is False  # same as latest (v2)
        assert ir3.duplicate_of == ir2.record_id  # points to latest version

    def test_record_has_raw_provenance(self, temp_db):
        insert_source_record('test', 'dataset', 'native_1',
                              {'key': 'value'}, 'raw_hash_abc', 'parser_v1')
        conn = sqlite3.connect(str(temp_db))
        row = conn.execute('SELECT raw_payload_hash FROM source_record WHERE source_record_id="test:native_1"').fetchone()
        assert row[0] == 'raw_hash_abc'
        conn.close()

    def test_version_id_uses_payload_hash(self, temp_db):
        """Version IDs should be content-addressed, not timestamp-based."""
        ir1 = insert_source_record('test', 'dataset', 'n1', {'k': 'v1'}, 'h1', 'p')
        ir2 = insert_source_record('test', 'dataset', 'n1', {'k': 'v2'}, 'h2', 'p')
        # Version ID should contain first 12 chars of payload hash
        payload_hash = hashlib.sha256(json.dumps({'k': 'v2'}, sort_keys=True).encode()).hexdigest()
        expected_version = f'test:n1:v{payload_hash[:12]}'
        assert ir2.record_id == expected_version


class TestCursor:
    def test_cursor_set_and_get(self, temp_db):
        set_cursor('test', 'dataset', '42')
        assert get_cursor('test', 'dataset') == '42'

    def test_cursor_overwrite(self, temp_db):
        set_cursor('test', 'dataset', '10')
        set_cursor('test', 'dataset', '20')
        assert get_cursor('test', 'dataset') == '20'


class TestMarketObservation:
    def test_store_market_observation(self, temp_db):
        """Market observations should be stored with all fields."""
        ir = insert_source_record('cex', 'uk', 'box123',
                                   {'name': 'test', 'sell_price': 100}, 'h', 'p')
        store_market_observation(
            source_record_id=ir.record_id,
            observed_at=datetime.now(timezone.utc).isoformat(),
            price=100.0,
            currency='GBP',
            availability='in_stock',
            condition='Good',
            market='cex',
        )
        conn = sqlite3.connect(str(temp_db))
        count = conn.execute('SELECT COUNT(*) FROM market_observation').fetchone()[0]
        assert count == 1
        row = conn.execute('SELECT price, currency, market FROM market_observation').fetchone()
        assert row[0] == 100.0
        assert row[1] == 'GBP'
        assert row[2] == 'cex'
        conn.close()

    def test_unchanged_price_still_observed(self, temp_db):
        """Even when price hasn't changed, we still store the observation."""
        ir = insert_source_record('cex', 'uk', 'box123',
                                   {'name': 'test', 'sell_price': 100}, 'h', 'p')
        for _ in range(3):
            store_market_observation(
                source_record_id=ir.record_id,
                observed_at=datetime.now(timezone.utc).isoformat(),
                price=100.0, currency='GBP', market='cex',
            )
        conn = sqlite3.connect(str(temp_db))
        count = conn.execute('SELECT COUNT(*) FROM market_observation').fetchone()[0]
        assert count == 3  # all three stored, even though price unchanged
        conn.close()


class TestCollectorRun:
    def test_log_run_records_status(self, temp_db):
        """log_run should persist a collector run."""
        log_run('test_source', 'ok', raw_fetched=1, raw_new=1,
                records_new=5, records_unchanged=3)
        conn = sqlite3.connect(str(temp_db))
        row = conn.execute('SELECT status, source_records_new FROM collector_run WHERE source_id="test_source"').fetchone()
        assert row[0] == 'ok'
        assert row[1] == 5
        conn.close()

    def test_log_run_records_errors(self, temp_db):
        """Failed runs should be logged with error info."""
        log_run('test_source', 'error', error='["fetch_failed"]')
        conn = sqlite3.connect(str(temp_db))
        row = conn.execute('SELECT status, error FROM collector_run WHERE source_id="test_source"').fetchone()
        assert row[0] == 'error'
        assert 'fetch_failed' in row[1]
        conn.close()

    def test_log_run_records_changed_unchanged(self, temp_db):
        """Changed and unchanged counts should be persisted."""
        log_run('test_source', 'ok', records_new=2, records_unchanged=10, records_changed=3)
        conn = sqlite3.connect(str(temp_db))
        row = conn.execute(
            'SELECT source_records_new, source_records_updated FROM collector_run WHERE source_id="test_source"'
        ).fetchone()
        assert row[0] == 2  # new
        assert row[1] == 3  # changed (maps to source_records_updated column)
        conn.close()


class TestBaseCollector:
    def test_success_run(self, temp_db):
        """A successful collector run should log status and telemetry."""
        from collectors.base import BaseCollector, CollectorResult

        class TestCollector(BaseCollector):
            SOURCE_ID = 'test_collector'
            DATASET = 'test_data'
            PARSER_ID = 'test_parser'

            def fetch(self):
                return b'{"items": [{"id": "1", "price": 100}]}'

            def parse(self, raw_content, raw_hash, result):
                result.records_new = 1

        collector = TestCollector()
        result = collector.run()

        assert result.records_new == 1
        assert result.raw_fetched == 1
        assert result.errors == []

        # Verify run was logged
        conn = sqlite3.connect(str(temp_db))
        row = conn.execute('SELECT status, raw_fetched FROM collector_run WHERE source_id="test_collector"').fetchone()
        assert row[0] == 'ok'
        assert row[1] == 1
        conn.close()

    def test_failed_fetch_is_logged(self, temp_db):
        """A failed fetch should still create a collector_run record."""
        from collectors.base import BaseCollector, CollectorResult

        class FailingFetcher(BaseCollector):
            SOURCE_ID = 'fail_fetch'
            DATASET = 'test'
            PARSER_ID = 'test'

            def fetch(self):
                return None

            def parse(self, raw_content, raw_hash, result):
                pass

        collector = FailingFetcher()
        result = collector.run()

        assert 'fetch_failed' in result.errors
        assert result.raw_fetched == 0

        # Verify run was logged despite failure
        conn = sqlite3.connect(str(temp_db))
        row = conn.execute('SELECT status, error FROM collector_run WHERE source_id="fail_fetch"').fetchone()
        assert row[0] == 'error'
        assert 'fetch_failed' in row[1]
        conn.close()

    def test_parse_failure_is_logged(self, temp_db):
        """A parse exception should be caught and logged."""
        from collectors.base import BaseCollector, CollectorResult

        class BadParser(BaseCollector):
            SOURCE_ID = 'fail_parse'
            DATASET = 'test'
            PARSER_ID = 'test'

            def fetch(self):
                return b'some data'

            def parse(self, raw_content, raw_hash, result):
                raise ValueError('bad data format')

        collector = BadParser()
        result = collector.run()

        assert 'bad data format' in result.errors
        assert result.raw_fetched == 1

        # Verify run was logged
        conn = sqlite3.connect(str(temp_db))
        row = conn.execute('SELECT status, error FROM collector_run WHERE source_id="fail_parse"').fetchone()
        assert row[0] == 'error'
        assert 'bad data format' in row[1]
        conn.close()

    def test_raw_new_reflects_actual_insertion(self, temp_db):
        """raw_new should be 0 when blob already exists."""
        from collectors.base import BaseCollector, CollectorResult

        class ReplayCollector(BaseCollector):
            SOURCE_ID = 'replay'
            DATASET = 'test'
            PARSER_ID = 'test'
            call_count = 0

            def fetch(self):
                return b'same data every time'

            def parse(self, raw_content, raw_hash, result):
                result.records_new = 1

        collector = ReplayCollector()
        r1 = collector.run()
        r2 = collector.run()

        assert r1.raw_new == 1  # first time: inserted
        assert r2.raw_new == 0  # second time: already existed

    def test_metadata_not_overwritten_by_parse(self, temp_db):
        """Parse must not overwrite collector-level metadata."""
        from collectors.base import BaseCollector, CollectorResult

        class MetadataTest(BaseCollector):
            SOURCE_ID = 'meta_test'
            DATASET = 'test'
            PARSER_ID = 'test'

            def fetch(self):
                return b'test data'

            def parse(self, raw_content, raw_hash, result):
                # Parse should only set records_* fields
                result.records_new = 5
                result.records_unchanged = 3
                # Do NOT touch raw_fetched, raw_new, started_at

        collector = MetadataTest()
        result = collector.run()

        # These should survive from run(), not be overwritten
        assert result.raw_fetched == 1
        assert result.started_at is not None
        assert result.finished_at is not None
        assert result.records_new == 5
        assert result.records_unchanged == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
