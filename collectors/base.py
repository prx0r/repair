"""Collector Base — hardened base class for all collectors.

Uses shared/persist.py for all database operations.
Returns proper counts. No hand-written SQL.
"""

import json
import time
import requests
from datetime import datetime, timezone
from typing import Optional
from shared.persist import (
    get_db, store_raw, store_acquisition, insert_source_record,
    get_cursor, set_cursor, log_run, InsertResult, RawStoreResult, Acquisition
)


class CollectorResult:
    def __init__(self):
        self.raw_fetched = 0
        self.raw_new = 0
        self.records_new = 0
        self.records_unchanged = 0
        self.records_changed = 0
        self.records_invalid = 0
        self.errors = []
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.finished_at = None


class BaseCollector:
    SOURCE_ID = ''
    DATASET = ''
    PARSER_ID = ''
    PARSER_VERSION = '1.0.0'

    def fetch(self) -> Optional[bytes]:
        raise NotImplementedError

    def parse(self, raw_content: bytes, raw_hash: str, result: CollectorResult):
        """Parse raw content and mutate `result` with counts.

        Subclasses MUST mutate the passed-in result, NOT return a new one.
        """
        raise NotImplementedError

    def _fetch_url(self, url: str, max_retries: int = 3, timeout: int = 30,
                   headers: dict = None) -> Optional[requests.Response]:
        merged = {'User-Agent': 'RepairGarden/1.0'}
        if headers:
            merged.update(headers)
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, timeout=timeout, headers=merged)
                if resp.status_code in (200, 404, 403):
                    return resp
                if resp.status_code == 429:
                    time.sleep(min(60, 2 ** (attempt + 2)))
                else:
                    time.sleep(2 ** attempt)
            except Exception:
                time.sleep(2 ** attempt)
        return None

    def run(self) -> CollectorResult:
        result = CollectorResult()
        print(f'{self.SOURCE_ID} — {self.DATASET}')
        print('=' * 50)

        try:
            print('  Fetching...')
            raw_content = self.fetch()
            if raw_content is None:
                result.errors.append('fetch_failed')
                print('  FETCH FAILED')
                return result

            result.raw_fetched = 1

            raw_result = store_raw(raw_content, self.SOURCE_ID)
            raw_hash = raw_result.sha256
            result.raw_new = 1 if raw_result.inserted else 0

            store_acquisition(
                self.SOURCE_ID, self.DATASET,
                url=getattr(self, '_last_url', self.SOURCE_ID),
                http_status=getattr(self, '_last_status', 200),
                sha256=raw_hash,
                content_type=getattr(self, '_last_content_type', ''),
                content_length=len(raw_content),
                final_url=getattr(self, '_last_final_url', ''),
            )
            print(f'  Raw: {raw_hash[:12]}... ({len(raw_content):,} bytes)')

            print('  Parsing...')
            self.parse(raw_content, raw_hash, result)
            print(f'  New: {result.records_new} | Unchanged: {result.records_unchanged} | Changed: {result.records_changed}')

        except Exception as e:
            result.errors.append(str(e))
            print(f'  ERROR: {e}')

        finally:
            result.finished_at = datetime.now(timezone.utc).isoformat()
            log_run(
                self.SOURCE_ID,
                'ok' if not result.errors else 'error',
                result.raw_fetched, result.raw_new,
                result.records_new, result.records_unchanged, result.records_changed,
                result.records_invalid,
                json.dumps(result.errors) if result.errors else None,
                result.started_at, result.finished_at,
            )
        return result
